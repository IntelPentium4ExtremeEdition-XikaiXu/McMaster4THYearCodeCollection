/*
 * One discrete-event simulator for three ARQ protocols.
 *
 *   Wr == 1 && Ws == 1   Stop-and-Wait
 *   Wr == 1 && Ws  > 1   Go-Back-N
 *   Wr  > 1              Selective Repeat
 *
 * Time unit is milliseconds.
 *   data packet transmission time = 1000 bit / 1 Mbps = 1 ms
 *   one-way propagation            = 5 ms
 *   ACK transmission time          = 0  (neglected, per the lab)
 *   ACK of a packet that starts at t returns at t + 1 + 5 + 5 = t + 11 ms
 *   so the pipe holds about 11 packets; Ws >= 11 fills the link when pd = pa = 0
 *
 * Assumptions (state these in the report):
 *   - sequence numbers are unbounded integers (no modulo window)
 *   - a lost data packet produces no ACK
 *   - ACK loss is decided independently, only after the data packet is kept
 *   - GBN/S&W ACK is cumulative; SR ACK is selective (one seq)
 *   - on a GBN/S&W discard of an out-of-order packet, the receiver repeats
 *     the last cumulative ACK (ACK tx time is still 0)
 *   - only the forward data channel is busy; packets are serialized 1 ms apart
 *   - a timeout is measured from the start of that packet's latest transmission
 */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

#define PKT_BITS            1000
#define LINK_RATE_BPS       1000000
#define TX_MS               1.0     /* PKT_BITS / LINK_RATE_BPS * 1000 */
#define PROP_MS             5.0     /* one way; RTT propagation is 10 ms */
#define DEFAULT_TIMEOUT_MS  15.0

#define SEED1 230411341234134134ULL
#define SEED2 400440917ULL
#define SEED3 400460804ULL

typedef enum {
    EV_PKT_ARRIVE = 1,
    EV_ACK_ARRIVE = 2,
    EV_TIMEOUT    = 3
} EventType;

typedef struct Event {
    double time;
    int type;
    int seq;
    unsigned gen;          /* ignore the event when gen != packet's current gen */
    unsigned long ord;
} Event;

typedef struct {
    int acked;
    int buffered;          /* receiver has a good copy */
    unsigned gen;          /* bumped on every (re)transmission */
    int tx_count;
} Packet;

typedef struct {
    int Ws;
    int Wr;
    double pd;             /* data packet loss probability */
    double pa;             /* ACK loss probability, given the packet arrived */
    double timeout_ms;
    int N;                 /* finite transfer size; 0 means continuously backlogged */
    long deliver_limit;   /* stop after this many deliveries when N == 0 */
    uint64_t seed_data;
    uint64_t seed_ack;
} Config;

typedef struct {
    double now;
    double channel_free_at; /* next time the forward channel can start a packet */
    double timeout_ms;

    double pd, pa;
    int Ws, Wr;
    int N;                 /* 0 => infinite backlog */
    long deliver_limit;

    int send_base;         /* oldest unacked seq */
    int next_seq;          /* next new seq that may be sent */
    int rcv_base;          /* next in-order seq the receiver still needs */

    Packet *pkts;          /* index by sequence number; grown as needed */
    int pkts_cap;

    Event *heap;
    int heap_n, heap_cap;
    unsigned long next_ord;
    uint64_t rng_data;
    uint64_t rng_ack;

    long delivered;
    long tx_attempts;
    int trace;
} Sim;

/* -------------------------------------------------------------------------- */
/*  Algorithm                                                                  */
/*                                                                             */
/*  run(cfg):                                                                   */
/*      init send_base = next_seq = rcv_base = 0, channel_free_at = 0          */
/*      fill_window()                         # pipeline a full window at t=0 */
/*      while not finished:                                                    */
/*          e = pop earliest event                                              */
/*          now = e.time                                                        */
/*          if e is PKT_ARRIVE:  on_pkt(e.seq)                                  */
/*          if e is ACK_ARRIVE:  on_ack(e.seq)                                  */
/*          if e is TIMEOUT:     on_timeout(e.seq, e.gen)                       */
/*      efficiency      = acked * TX_MS / now                                   */
/*      attempts/packet = (tx count of acked packets) / acked                   */
/*      finished when N > 0 and send_base == N, else send_base == limit         */
/*      completion time = now of the ACK that delivers the last packet          */
/*                                                                             */
/*  transmit(seq):                          # book the forward channel         */
/*      start = max(now, channel_free_at)                                       */
/*      channel_free_at = start + TX_MS                                         */
/*      pkts[seq].gen++                                                         */
/*      pkts[seq].tx_count++ ; tx_attempts++                                    */
/*      schedule PKT_ARRIVE(seq) at start + TX_MS + PROP_MS                     */
/*      schedule TIMEOUT(seq, gen) at start + timeout_ms                        */
/*                                                                             */
/*  fill_window():                                                              */
/*      while next_seq < send_base + Ws                                        */
/*            and (N == 0 or next_seq < N):                                    */
/*          transmit(next_seq)                                                  */
/*          next_seq++                                                          */
/*                                                                             */
/*  on_pkt(seq):                             # receiver                        */
/*      if rand_data() < pd: return           # loss, no ACK                    */
/*      if Wr == 1:                          # S&W and GBN                      */
/*          if seq == rcv_base:                                                 */
/*              rcv_base++ ; delivered++                                        */
/*          schedule ACK_ARRIVE(rcv_base - 1) at now + PROP_MS                  */
/*          # cumulative ACK; also repeated when seq is discarded               */
/*      else:                                # SR                               */
/*          if rcv_base <= seq < rcv_base + Wr:                                 */
/*              if not buffered[seq]: buffer it; if seq == some new in-order    */
/*                  delivery, count it when it extends rcv_base                 */
/*              while buffered[rcv_base]: clear it; rcv_base++; delivered++     */
/*              schedule ACK_ARRIVE(seq) at now + PROP_MS   # selective ACK     */
/*                                                                             */
/*  on_ack(seq):                             # sender                           */
/*      if rand_ack() < pa: return                                            */
/*      if Wr == 1:                          # cumulative                       */
/*          if seq >= send_base:                                                */
/*              send_base = seq + 1                                             */
/*              fill_window()   # old TIMEOUTs die because seq < send_base     */
/*      else:                                # selective                        */
/*          if send_base <= seq < next_seq and not acked[seq]:                  */
/*              acked[seq] = 1                                                  */
/*              while send_base < next_seq and acked[send_base]: send_base++   */
/*              fill_window()                                                   */
/*                                                                             */
/*  on_timeout(seq, gen):                                                       */
/*      if gen != pkts[seq].gen: return      # stale timer                      */
/*      if seq < send_base or acked[seq]: return                                */
/*      if Wr == 1:                          # GBN / S&W: only base timer acts  */
/*          if seq != send_base: return                                        */
/*          for s in send_base .. next_seq-1:                                  */
/*              transmit(s)                  # serialised on the channel       */
/*      else:                                # SR: retransmit that seq only    */
/*          transmit(seq)                                                       */
/*                                                                             */
/*  finished when send_base reaches N (finite) or deliver_limit (backlogged).  */
/*                                                                             */
/*  Same-time tie break: pop ACK before PKT before TIMEOUT.                    */
/*  Trace mode prints "t  event  seq" for the short traces in experiment 1.    */
/* -------------------------------------------------------------------------- */

static uint64_t rng_next(uint64_t *state)
{
    /* Numerical Recipes LCG; one stream for data loss, one for ACK loss. */
    *state = (*state) * 1664525ULL + 1013904223ULL;
    return *state;
}

static double rng_uniform(uint64_t *state)
{
    return (rng_next(state) >> 11) * (1.0 / 9007199254740992.0);
}

static int event_rank(int type)
{
    if (type == EV_ACK_ARRIVE) return 0;
    if (type == EV_PKT_ARRIVE) return 1;
    return 2;
}

static int comes_first(const Event *a, const Event *b)
{
    if (a->time < b->time) return 1;
    if (a->time > b->time) return 0;
    int ra = event_rank(a->type);
    int rb = event_rank(b->type);
    if (ra != rb) return ra < rb;
    return a->ord < b->ord;
}

static void heap_swap(Event *a, Event *b)
{
    Event t = *a;
    *a = *b;
    *b = t;
}

static void sift_up(Event *a, int i)
{
    while (i > 0) {
        int p = (i - 1) / 2;
        if (!comes_first(&a[i], &a[p]))
            break;
        heap_swap(&a[i], &a[p]);
        i = p;
    }
}

static void sift_down(Event *a, int n, int i)
{
    for (;;) {
        int l = 2 * i + 1;
        int r = l + 1;
        int s = i;
        if (l < n && comes_first(&a[l], &a[s])) s = l;
        if (r < n && comes_first(&a[r], &a[s])) s = r;
        if (s == i) break;
        heap_swap(&a[i], &a[s]);
        i = s;
    }
}

static void schedule(Sim *sim, double time, int type, int seq, unsigned gen)
{
    Event e;
    int i;
    if (sim->heap_n == sim->heap_cap) {
        sim->heap_cap = sim->heap_cap ? sim->heap_cap * 2 : 1024;
        sim->heap = realloc(sim->heap, (size_t)sim->heap_cap * sizeof(Event));
        if (!sim->heap) {
            perror("realloc");
            exit(1);
        }
    }
    e.time = time;
    e.type = type;
    e.seq = seq;
    e.gen = gen;
    e.ord = sim->next_ord++;
    i = sim->heap_n++;
    sim->heap[i] = e;
    sift_up(sim->heap, i);
}

static int pop_event(Sim *sim, Event *out)
{
    if (sim->heap_n == 0)
        return 0;
    *out = sim->heap[0];
    sim->heap_n--;
    if (sim->heap_n > 0) {
        sim->heap[0] = sim->heap[sim->heap_n];
        sift_down(sim->heap, sim->heap_n, 0);
    }
    return 1;
}

static void ensure_pkt(Sim *sim, int seq)
{
    if (seq < sim->pkts_cap)
        return;
    int cap = sim->pkts_cap ? sim->pkts_cap : 16;
    while (cap <= seq)
        cap *= 2;
    sim->pkts = realloc(sim->pkts, (size_t)cap * sizeof(Packet));
    if (!sim->pkts) {
        perror("realloc");
        exit(1);
    }
    memset(sim->pkts + sim->pkts_cap, 0, (size_t)(cap - sim->pkts_cap) * sizeof(Packet));
    sim->pkts_cap = cap;
}

static int finished(const Sim *sim)
{
    if (sim->N > 0)
        return sim->send_base >= sim->N;
    return sim->send_base >= sim->deliver_limit;
}

static void trace_at(const Sim *sim, double time, const char *name, int seq)
{
    if (sim->trace)
        printf("TRACE %.6f %s %d\n", time, name, seq);
}

/* Book the forward channel and arm arrival + timeout for this seq. */
static void transmit(Sim *sim, int seq)
{
    double start;
    unsigned gen;

    ensure_pkt(sim, seq);
    start = sim->now > sim->channel_free_at ? sim->now : sim->channel_free_at;
    sim->channel_free_at = start + TX_MS;

    gen = ++sim->pkts[seq].gen;
    sim->pkts[seq].tx_count++;
    sim->tx_attempts++;

    schedule(sim, start + TX_MS + PROP_MS, EV_PKT_ARRIVE, seq, gen);
    schedule(sim, start + sim->timeout_ms, EV_TIMEOUT, seq, gen);
    trace_at(sim, start, sim->pkts[seq].tx_count > 1 ? "RETX" : "TX", seq);
}

/* Send new sequence numbers until the send window or the finite file is full. */
static void fill_window(Sim *sim)
{
    while (sim->next_seq < sim->send_base + sim->Ws &&
           (sim->N == 0 || sim->next_seq < sim->N)) {
        transmit(sim, sim->next_seq);
        sim->next_seq++;
    }
}

static void send_ack(Sim *sim, int ack_seq)
{
    if (ack_seq < 0)
        return;
    schedule(sim, sim->now + PROP_MS, EV_ACK_ARRIVE, ack_seq, 0);
    trace_at(sim, sim->now, "ACK_SENT", ack_seq);
}

/* Receiver. A lost data packet produces no ACK. */
static void on_pkt(Sim *sim, int seq)
{
    if (rng_uniform(&sim->rng_data) < sim->pd) {
        trace_at(sim, sim->now, "DROP", seq);
        return;
    }
    trace_at(sim, sim->now, "RECV", seq);

    if (sim->Wr == 1) {
        /* S&W and GBN: in-order only, cumulative ACK. Duplicates and
         * gaps both repeat ACK(rcv_base-1) so a lost ACK can still recover. */
        if (seq == sim->rcv_base) {
            sim->rcv_base++;
            sim->delivered++;
        }
        if (sim->rcv_base > 0)
            send_ack(sim, sim->rcv_base - 1);
        return;
    }

    /* SR: selective ACK. Duplicates below the window are ACKed again. */
    if (seq < sim->rcv_base) {
        send_ack(sim, seq);
        return;
    }
    if (seq >= sim->rcv_base + sim->Wr)
        return;

    ensure_pkt(sim, seq);
    sim->pkts[seq].buffered = 1;
    while (sim->rcv_base < sim->pkts_cap && sim->pkts[sim->rcv_base].buffered) {
        sim->pkts[sim->rcv_base].buffered = 0;
        sim->rcv_base++;
        sim->delivered++;
    }
    send_ack(sim, seq);
}

/* Sender. ACK loss is independent of data-packet loss. */
static void on_ack(Sim *sim, int seq)
{
    if (rng_uniform(&sim->rng_ack) < sim->pa) {
        trace_at(sim, sim->now, "ACK_LOST", seq);
        return;
    }
    trace_at(sim, sim->now, "ACK_OK", seq);

    if (sim->Wr == 1) {
        if (seq >= sim->send_base)
            sim->send_base = seq + 1;
    } else if (seq >= sim->send_base && seq < sim->next_seq) {
        ensure_pkt(sim, seq);
        sim->pkts[seq].acked = 1;
        while (sim->send_base < sim->next_seq && sim->pkts[sim->send_base].acked)
            sim->send_base++;
    }
    if (!finished(sim))
        fill_window(sim);
}

/* Stale timers (gen mismatch) are leftovers of an earlier transmission. */
static void on_timeout(Sim *sim, int seq, unsigned gen)
{
    int s;

    if (seq < 0 || seq >= sim->pkts_cap)
        return;
    if (gen != sim->pkts[seq].gen)
        return;
    if (seq < sim->send_base)
        return;
    if (sim->Wr > 1 && sim->pkts[seq].acked)
        return;

    if (sim->Wr == 1) {
        if (seq != sim->send_base)
            return;
        trace_at(sim, sim->now, "TIMEOUT", seq);
        for (s = sim->send_base; s < sim->next_seq; s++)
            transmit(sim, s);
        return;
    }

    trace_at(sim, sim->now, "TIMEOUT", seq);
    transmit(sim, seq);
}

static void sim_init(Sim *sim, const Config *cfg)
{
    memset(sim, 0, sizeof(*sim));
    sim->Ws = cfg->Ws > 0 ? cfg->Ws : 1;
    sim->Wr = cfg->Wr > 0 ? cfg->Wr : 1;
    sim->N = cfg->N;
    sim->pd = cfg->pd;
    sim->pa = cfg->pa;
    sim->deliver_limit = cfg->deliver_limit > 0 ? cfg->deliver_limit : 100000;
    sim->timeout_ms = cfg->timeout_ms > 0 ? cfg->timeout_ms : DEFAULT_TIMEOUT_MS;
    sim->rng_data = cfg->seed_data ? cfg->seed_data : SEED2;
    sim->rng_ack = cfg->seed_ack ? cfg->seed_ack : SEED3;
    if (sim->pd < 0) sim->pd = 0;
    if (sim->pa < 0) sim->pa = 0;
    if (sim->pd > 1) sim->pd = 1;
    if (sim->pa > 1) sim->pa = 1;
}

static void sim_free(Sim *sim)
{
    free(sim->heap);
    free(sim->pkts);
    sim->heap = NULL;
    sim->pkts = NULL;
}

static long acked_transmissions(const Sim *sim)
{
    long tx = 0;
    int i;
    for (i = 0; i < sim->send_base && i < sim->pkts_cap; i++)
        tx += sim->pkts[i].tx_count;
    return tx;
}

/* Returns 0 on a normal stop, 1 if the event list drains, 2 if the safety cap hits. */
static int sim_run(Sim *sim)
{
    long long steps = 0;
    long long cap_pkts = sim->N > 0 ? (long long)sim->N : (long long)sim->deliver_limit;
    long long cap = cap_pkts * 200000LL;
    if (cap < 1000000)
        cap = 1000000;

    fill_window(sim);
    while (!finished(sim)) {
        Event e;
        if (!pop_event(sim, &e))
            return 1;
        if (++steps > cap)
            return 2;
        sim->now = e.time;
        if (e.type == EV_PKT_ARRIVE)
            on_pkt(sim, e.seq);
        else if (e.type == EV_ACK_ARRIVE)
            on_ack(sim, e.seq);
        else
            on_timeout(sim, e.seq, e.gen);
    }
    return 0;
}

static void print_result(const Sim *sim)
{
    long tx = acked_transmissions(sim);
    double eff = 0.0;
    double att = 0.0;
    if (sim->now > 0.0 && sim->send_base > 0) {
        eff = sim->send_base * TX_MS / sim->now;
        att = (double)tx / (double)sim->send_base;
    }
    printf("RESULT %.10f %.10f %.6f %d %ld\n",
           eff, att, sim->now, sim->send_base, tx);
    fflush(stdout);
}

static void usage(const char *argv0)
{
    fprintf(stderr,
            "Usage: %s --ws N --wr N --pd P --pa P --timeout MS --n N --limit N "
            "--seed-data U --seed-ack U --trace 0|1\n",
            argv0);
}

static int parse_args(int argc, char **argv, Config *cfg, int *trace)
{
    int i;
    memset(cfg, 0, sizeof(*cfg));
    cfg->Ws = 1;
    cfg->Wr = 1;
    cfg->timeout_ms = DEFAULT_TIMEOUT_MS;
    cfg->deliver_limit = 100000;
    cfg->seed_data = SEED2;
    cfg->seed_ack = SEED3;
    *trace = 0;

    for (i = 1; i < argc; i++) {
        const char *a = argv[i];
        if (i + 1 >= argc) {
            usage(argv[0]);
            return 1;
        }
        if (strcmp(a, "--ws") == 0) cfg->Ws = atoi(argv[++i]);
        else if (strcmp(a, "--wr") == 0) cfg->Wr = atoi(argv[++i]);
        else if (strcmp(a, "--pd") == 0) cfg->pd = atof(argv[++i]);
        else if (strcmp(a, "--pa") == 0) cfg->pa = atof(argv[++i]);
        else if (strcmp(a, "--timeout") == 0) cfg->timeout_ms = atof(argv[++i]);
        else if (strcmp(a, "--n") == 0) cfg->N = atoi(argv[++i]);
        else if (strcmp(a, "--limit") == 0) cfg->deliver_limit = atol(argv[++i]);
        else if (strcmp(a, "--seed-data") == 0) cfg->seed_data = strtoull(argv[++i], NULL, 10);
        else if (strcmp(a, "--seed-ack") == 0) cfg->seed_ack = strtoull(argv[++i], NULL, 10);
        else if (strcmp(a, "--trace") == 0) *trace = atoi(argv[++i]);
        else {
            usage(argv[0]);
            return 1;
        }
    }
    if (cfg->Ws < 1 || cfg->Wr < 1 || cfg->timeout_ms <= 0) {
        fprintf(stderr, "Ws, Wr and timeout must be positive\n");
        return 1;
    }
    return 0;
}

int main(int argc, char **argv)
{
    Config cfg;
    Sim sim;
    int trace = 0;
    int rc;

    if (parse_args(argc, argv, &cfg, &trace))
        return 1;
    sim_init(&sim, &cfg);
    sim.trace = trace;
    if (trace) {
        printf("TRACE_HEADER ws=%d wr=%d pd=%.4f pa=%.4f timeout=%.3f n=%d limit=%ld seed_data=%llu seed_ack=%llu\n",
               sim.Ws, sim.Wr, sim.pd, sim.pa, sim.timeout_ms, sim.N, sim.deliver_limit,
               (unsigned long long)sim.rng_data, (unsigned long long)sim.rng_ack);
    }
    rc = sim_run(&sim);
    if (rc != 0) {
        fprintf(stderr, "simulation stopped early (code %d) ws=%d wr=%d pd=%g pa=%g timeout=%g n=%d\n",
                rc, sim.Ws, sim.Wr, sim.pd, sim.pa, sim.timeout_ms, sim.N);
        sim_free(&sim);
        return rc;
    }
    print_result(&sim);
    sim_free(&sim);
    return 0;
}
