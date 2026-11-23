/*
 * Lab 5 — two links, ARQ + reservation MAC, one discrete-event run.
 *
 * Time unit: millisecond.
 *   data frame            D = 1 ms          (1000 bit at 1 Mbps)
 *   one-way propagation   tau = 5 ms
 *   ACK transmission      0                 (dedicated reverse channel, no contention)
 *   ACK returns at        tx_start + D + 2*tau = tx_start + 11 ms
 *
 * Reservation channel is separate from the shared forward data channel.
 *   minislot              0.5 ms            (2 minislots per data-frame time)
 *   request feedback      2*tau = 10 ms     (request goes, grant comes back)
 *   one successful grant  = one data frame, then the reservation expires
 *
 * MAC:
 *   sched  even minislots belong to link 0, odd minislots to link 1
 *   aloha  a backlogged link requests in a minislot with probability p
 *          (p = 0.5). Two requests in one minislot collide and both fail.
 *
 * ARQ timer:
 *   tx     starts when the data frame actually begins transmission
 *   ready  starts when the frame becomes eligible, so MAC wait sits inside the timer
 *
 * A timeout that fires while the frame is still waiting for a grant does not
 * create a second copy. The timer is restarted. A timeout that fires after
 * transmission follows GBN (go-back of the window) or SR (that frame only).
 * Retransmissions are chosen before new frames when a grant is consumed.
 */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

#define NLINKS 2
#define TX_MS  1.0
#define PROP_MS 5.0
#define DEFAULT_TIMEOUT_MS 15.0
#define DEFAULT_TMINI 0.5
#define DEFAULT_P 0.5
#define DEFAULT_TEND 50000.0
#define FINITE_SAFETY_MS 1.0e8

#define SEED1 230411341234134134ULL
#define SEED2 400440917ULL
#define SEED3 400460804ULL

enum {
    MAC_SCHED = 0,
    MAC_ALOHA = 1
};

enum {
    TIMER_TX = 0,
    TIMER_READY = 1
};

enum {
    ST_EMPTY = 0,
    ST_READY = 1,
    ST_FLY = 2,
    ST_ACKED = 3
};

enum {
    EV_ACK = 1,
    EV_PKT = 2,
    EV_TIMEOUT = 3,
    EV_GRANT = 4,
    EV_FAIL = 5,
    EV_MINI = 6
};

typedef struct Event {
    double time;
    int type;
    int link;
    int seq;
    unsigned gen;
    unsigned long ord;
} Event;

typedef struct {
    int state;
    int buffered;
    unsigned gen;
    int tx_count;
    double ready_at;
} Pkt;

typedef struct {
    int id;
    int Ws, Wr;
    int send_base;
    int next_seq;
    int rcv_base;
    int pending;
    int unused;
    int n_req;
    long tx_attempts;
    double access_sum;
    long access_n;
    double t_comp;
    int comp_set;
    Pkt *pkts;
    int pkts_cap;
    uint64_t rng_data;
    uint64_t rng_ack;
} Link;

typedef struct {
    int mac;
    int timer_mode;
    double p;
    double t_mini;
    double timeout_ms;
    double t_end;
    int continuous;
    int N;
    double pd, pa;
    uint64_t seed_data, seed_ack, seed_mac;
} Config;

typedef struct {
    double now;
    double t_end;
    double timeout_ms;
    double t_mini;
    double p;
    double pd, pa;
    double channel_free;
    double busy;
    int mac;
    int timer_mode;
    int continuous;
    int N;
    int trace;
    long long slot_index;
    long n_grant;
    long n_coll;
    uint64_t rng_mac;
    Link links[NLINKS];
    Event *heap;
    int heap_n, heap_cap;
    unsigned long next_ord;
} Sim;

static uint64_t rng_next(uint64_t *state)
{
    *state = (*state) * 1664525ULL + 1013904223ULL;
    return *state;
}

static double rng_uniform(uint64_t *state)
{
    return (rng_next(state) >> 11) * (1.0 / 9007199254740992.0);
}

static int event_rank(int type)
{
    switch (type) {
    case EV_ACK: return 0;
    case EV_PKT: return 1;
    case EV_TIMEOUT: return 2;
    case EV_GRANT: return 3;
    case EV_FAIL: return 4;
    default: return 5;
    }
}

static int comes_first(const Event *a, const Event *b)
{
    int ra, rb;
    if (a->time < b->time) return 1;
    if (a->time > b->time) return 0;
    ra = event_rank(a->type);
    rb = event_rank(b->type);
    if (ra != rb) return ra < rb;
    if (a->link != b->link) return a->link < b->link;
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

static void schedule(Sim *sim, double time, int type, int link, int seq, unsigned gen)
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
    e.link = link;
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

static void ensure_pkt(Link *L, int seq)
{
    int cap;
    if (seq < L->pkts_cap)
        return;
    cap = L->pkts_cap ? L->pkts_cap : 16;
    while (cap <= seq)
        cap *= 2;
    L->pkts = realloc(L->pkts, (size_t)cap * sizeof(Pkt));
    if (!L->pkts) {
        perror("realloc");
        exit(1);
    }
    memset(L->pkts + L->pkts_cap, 0, (size_t)(cap - L->pkts_cap) * sizeof(Pkt));
    L->pkts_cap = cap;
}

static void trace_at(const Sim *sim, double time, int link, const char *name, int seq)
{
    if (sim->trace)
        printf("TRACE %.6f L%d %s %d\n", time, link, name, seq);
}

static int link_done(const Sim *sim, const Link *L)
{
    return !sim->continuous && L->send_base >= sim->N;
}

static void note_complete(Sim *sim, Link *L)
{
    if (sim->continuous || L->comp_set)
        return;
    if (L->send_base >= sim->N) {
        L->comp_set = 1;
        L->t_comp = sim->now;
    }
}

static void become_ready(Sim *sim, Link *L, int seq)
{
    Pkt *p;
    ensure_pkt(L, seq);
    p = &L->pkts[seq];
    if (p->state == ST_ACKED || p->state == ST_READY)
        return;
    p->state = ST_READY;
    p->ready_at = sim->now;
    p->gen += 1;
    if (sim->timer_mode == TIMER_READY)
        schedule(sim, sim->now + sim->timeout_ms, EV_TIMEOUT, L->id, seq, p->gen);
}

static void fill_window(Sim *sim, Link *L)
{
    int limit;
    if (link_done(sim, L))
        return;
    limit = L->send_base + L->Ws;
    while (L->next_seq < limit && (sim->continuous || L->next_seq < sim->N)) {
        int seq = L->next_seq++;
        become_ready(sim, L, seq);
    }
}

static int pick_ready(const Link *L)
{
    int s;
    for (s = L->send_base; s < L->next_seq; s++) {
        if (L->pkts[s].state == ST_READY)
            return s;
    }
    return -1;
}

static int count_ready(const Link *L)
{
    int s, n = 0;
    for (s = L->send_base; s < L->next_seq; s++) {
        if (L->pkts[s].state == ST_READY)
            n++;
    }
    return n;
}

static int demand(const Link *L)
{
    int ready = count_ready(L);
    int pipe = L->pending + L->unused;
    if (ready > pipe)
        return ready - pipe;
    return 0;
}

static void transmit(Sim *sim, Link *L, int seq, double start)
{
    Pkt *p = &L->pkts[seq];
    double end = start + TX_MS;

    p->state = ST_FLY;
    p->tx_count++;
    L->tx_attempts++;
    L->access_sum += start - p->ready_at;
    L->access_n++;

    if (sim->continuous) {
        double b = end;
        if (start < sim->t_end) {
            if (b > sim->t_end)
                b = sim->t_end;
            sim->busy += b - start;
        }
    } else {
        sim->busy += TX_MS;
    }

    schedule(sim, start + TX_MS + PROP_MS, EV_PKT, L->id, seq, p->gen);
    if (sim->timer_mode == TIMER_TX)
        schedule(sim, start + sim->timeout_ms, EV_TIMEOUT, L->id, seq, p->gen);
    trace_at(sim, start, L->id, p->tx_count > 1 ? "RETX" : "TX", seq);
}

static void pump(Sim *sim, Link *L)
{
    while (L->unused > 0) {
        int seq = pick_ready(L);
        double start;
        if (seq < 0)
            break;
        start = sim->now > sim->channel_free ? sim->now : sim->channel_free;
        sim->channel_free = start + TX_MS;
        L->unused--;
        transmit(sim, L, seq, start);
    }
}

static void send_ack(Sim *sim, Link *L, int ack_seq)
{
    if (ack_seq < 0)
        return;
    schedule(sim, sim->now + PROP_MS, EV_ACK, L->id, ack_seq, 0);
    trace_at(sim, sim->now, L->id, "ACK_SENT", ack_seq);
}

static void on_pkt(Sim *sim, Link *L, int seq)
{
    int s;
    if (rng_uniform(&L->rng_data) < sim->pd) {
        trace_at(sim, sim->now, L->id, "DROP", seq);
        return;
    }
    trace_at(sim, sim->now, L->id, "RECV", seq);

    if (L->Wr == 1) {
        if (seq == L->rcv_base)
            L->rcv_base++;
        if (L->rcv_base > 0)
            send_ack(sim, L, L->rcv_base - 1);
        return;
    }

    if (seq < L->rcv_base) {
        send_ack(sim, L, seq);
        return;
    }
    if (seq >= L->rcv_base + L->Wr)
        return;

    ensure_pkt(L, seq);
    L->pkts[seq].buffered = 1;
    s = L->rcv_base;
    while (s < L->pkts_cap && L->pkts[s].buffered) {
        L->pkts[s].buffered = 0;
        s++;
    }
    L->rcv_base = s;
    send_ack(sim, L, seq);
}

static void on_ack(Sim *sim, Link *L, int seq)
{
    int s;
    int nb;

    if (rng_uniform(&L->rng_ack) < sim->pa) {
        trace_at(sim, sim->now, L->id, "ACK_LOST", seq);
        return;
    }
    trace_at(sim, sim->now, L->id, "ACK_OK", seq);

    if (L->Wr == 1) {
        nb = seq + 1;
        if (nb > L->next_seq)
            nb = L->next_seq;
        if (nb > L->send_base) {
            for (s = L->send_base; s < nb; s++)
                L->pkts[s].state = ST_ACKED;
            L->send_base = nb;
        }
    } else if (seq >= L->send_base && seq < L->next_seq) {
        ensure_pkt(L, seq);
        L->pkts[seq].state = ST_ACKED;
        while (L->send_base < L->next_seq &&
               L->pkts[L->send_base].state == ST_ACKED)
            L->send_base++;
    }

    note_complete(sim, L);
    if (!link_done(sim, L))
        fill_window(sim, L);
    pump(sim, L);
}

static void go_back(Sim *sim, Link *L)
{
    int s;
    for (s = L->send_base; s < L->next_seq; s++) {
        if (L->pkts[s].state == ST_FLY)
            become_ready(sim, L, s);
    }
}

static void on_timeout(Sim *sim, Link *L, int seq, unsigned gen)
{
    Pkt *p;
    if (seq < L->send_base || seq >= L->next_seq || seq >= L->pkts_cap)
        return;
    p = &L->pkts[seq];
    if (gen != p->gen)
        return;
    if (L->Wr > 1 && p->state == ST_ACKED)
        return;

    if (p->state == ST_READY) {
        /* Still waiting for a reservation or a data slot. Keep a single copy. */
        if (sim->timer_mode == TIMER_READY)
            schedule(sim, sim->now + sim->timeout_ms, EV_TIMEOUT, L->id, seq, gen);
        trace_at(sim, sim->now, L->id, "WAIT_TIMEOUT", seq);
        return;
    }
    if (p->state != ST_FLY)
        return;
    if (L->Wr == 1 && seq != L->send_base)
        return;

    trace_at(sim, sim->now, L->id, "TIMEOUT", seq);
    if (L->Wr == 1)
        go_back(sim, L);
    else
        become_ready(sim, L, seq);
    pump(sim, L);
}

static void on_grant(Sim *sim, Link *L)
{
    if (L->pending > 0)
        L->pending--;
    sim->n_grant++;
    L->unused++;
    trace_at(sim, sim->now, L->id, "GRANT", L->unused);
    pump(sim, L);
}

static void on_fail(Sim *sim, Link *L)
{
    if (L->pending > 0)
        L->pending--;
    trace_at(sim, sim->now, L->id, "COLLISION", 0);
}

static void on_minislot(Sim *sim)
{
    int want[NLINKS];
    int i, n = 0;
    long long slot = sim->slot_index;

    for (i = 0; i < NLINKS; i++) {
        Link *L = &sim->links[i];
        int eligible = demand(L) > 0;
        want[i] = 0;
        if (!eligible)
            continue;
        if (sim->mac == MAC_SCHED) {
            want[i] = ((slot % 2) == i);
        } else if (rng_uniform(&sim->rng_mac) < sim->p) {
            want[i] = 1;
        }
        if (want[i]) {
            L->pending++;
            L->n_req++;
            trace_at(sim, sim->now, L->id, "REQ", L->pending);
            n++;
        }
    }

    if (n == 1) {
        for (i = 0; i < NLINKS; i++) {
            if (want[i])
                schedule(sim, sim->now + 2.0 * PROP_MS, EV_GRANT, i, 0, 0);
        }
    } else if (n == 2) {
        sim->n_coll++;
        for (i = 0; i < NLINKS; i++)
            schedule(sim, sim->now + 2.0 * PROP_MS, EV_FAIL, i, 0, 0);
    }

    sim->slot_index++;
    schedule(sim, sim->slot_index * sim->t_mini, EV_MINI, -1, 0, 0);
}

static int both_done(const Sim *sim)
{
    return link_done(sim, &sim->links[0]) && link_done(sim, &sim->links[1]);
}

static void sim_init(Sim *sim, const Config *cfg)
{
    int i;
    memset(sim, 0, sizeof(*sim));
    sim->mac = cfg->mac;
    sim->timer_mode = cfg->timer_mode;
    sim->p = cfg->p;
    sim->t_mini = cfg->t_mini;
    sim->timeout_ms = cfg->timeout_ms;
    sim->t_end = cfg->t_end;
    sim->continuous = cfg->continuous;
    sim->N = cfg->N;
    sim->pd = cfg->pd;
    sim->pa = cfg->pa;
    sim->rng_mac = cfg->seed_mac ? cfg->seed_mac : SEED1;
    sim->channel_free = 0.0;

    for (i = 0; i < NLINKS; i++) {
        Link *L = &sim->links[i];
        uint64_t mix = (uint64_t)(i + 1) * 0x9E3779B97F4A7C15ULL;
        L->id = i;
        L->Ws = 1;
        L->Wr = 1;
        L->t_comp = -1.0;
        L->rng_data = (cfg->seed_data ? cfg->seed_data : SEED2) ^ mix;
        L->rng_ack = (cfg->seed_ack ? cfg->seed_ack : SEED3) ^ (mix << 1);
        if (L->rng_data == 0)
            L->rng_data = 1;
        if (L->rng_ack == 0)
            L->rng_ack = 1;
    }
}

static void link_config(Link *L, int Ws, int Wr)
{
    L->Ws = Ws > 0 ? Ws : 1;
    L->Wr = Wr > 0 ? Wr : 1;
}

static void sim_free(Sim *sim)
{
    int i;
    free(sim->heap);
    sim->heap = NULL;
    for (i = 0; i < NLINKS; i++) {
        free(sim->links[i].pkts);
        sim->links[i].pkts = NULL;
    }
}

static long acked_tx(const Link *L)
{
    long tx = 0;
    int s;
    int n = L->send_base < L->pkts_cap ? L->send_base : L->pkts_cap;
    for (s = 0; s < n; s++)
        tx += L->pkts[s].tx_count;
    return tx;
}

static int sim_run(Sim *sim)
{
    long long steps = 0;
    int i;

    for (i = 0; i < NLINKS; i++)
        fill_window(sim, &sim->links[i]);
    schedule(sim, 0.0, EV_MINI, -1, 0, 0);

    while (!both_done(sim)) {
        Event e;
        if (!pop_event(sim, &e))
            return 1;
        if (e.time > sim->t_end) {
            if (sim->continuous)
                break;
            return 2;
        }
        if (++steps > 50000000LL)
            return 3;
        sim->now = e.time;
        if (e.type == EV_MINI)
            on_minislot(sim);
        else if (e.link < 0 || e.link >= NLINKS)
            return 4;
        else if (e.type == EV_PKT)
            on_pkt(sim, &sim->links[e.link], e.seq);
        else if (e.type == EV_ACK)
            on_ack(sim, &sim->links[e.link], e.seq);
        else if (e.type == EV_TIMEOUT)
            on_timeout(sim, &sim->links[e.link], e.seq, e.gen);
        else if (e.type == EV_GRANT)
            on_grant(sim, &sim->links[e.link]);
        else if (e.type == EV_FAIL)
            on_fail(sim, &sim->links[e.link]);
        else
            return 4;
    }
    return 0;
}

static void print_result(const Sim *sim)
{
    double T, S[2], att[2], ad[2];
    int i;
    T = sim->continuous ? sim->t_end : sim->now;
    if (T <= 0.0)
        T = 1e-12;
    for (i = 0; i < NLINKS; i++) {
        const Link *L = &sim->links[i];
        long tx = acked_tx(L);
        S[i] = L->rcv_base * TX_MS / T;
        att[i] = (L->send_base > 0) ? (double)tx / (double)L->send_base : 0.0;
        ad[i] = (L->access_n > 0) ? L->access_sum / (double)L->access_n : 0.0;
    }
    printf("RESULT S0=%.8f S1=%.8f Seff=%.8f occ=%.8f att0=%.6f att1=%.6f "
           "ad0=%.6f ad1=%.6f T=%.6f del0=%d del1=%d tx0=%ld tx1=%ld "
           "tc0=%.6f tc1=%.6f req=%d grant=%ld coll=%ld base0=%d base1=%d\n",
           S[0], S[1], S[0] + S[1], sim->busy / T, att[0], att[1],
           ad[0], ad[1], T, sim->links[0].rcv_base, sim->links[1].rcv_base,
           sim->links[0].tx_attempts, sim->links[1].tx_attempts,
           sim->links[0].t_comp, sim->links[1].t_comp,
           sim->links[0].n_req + sim->links[1].n_req, sim->n_grant, sim->n_coll,
           sim->links[0].send_base, sim->links[1].send_base);
    fflush(stdout);
}

static void usage(const char *argv0)
{
    fprintf(stderr,
            "Usage: %s --ws N --wr N --pd P --pa P --timeout MS --n N --tend MS\n"
            "          --mac sched|aloha --timer tx|ready --p P --tmini MS\n"
            "          --seed-data U --seed-ack U --seed-mac U --trace 0|1\n",
            argv0);
}

static int parse_args(int argc, char **argv, Config *cfg, int *Ws, int *Wr, int *trace)
{
    int i;
    memset(cfg, 0, sizeof(*cfg));
    cfg->mac = MAC_SCHED;
    cfg->timer_mode = TIMER_TX;
    cfg->p = DEFAULT_P;
    cfg->t_mini = DEFAULT_TMINI;
    cfg->timeout_ms = DEFAULT_TIMEOUT_MS;
    cfg->t_end = 0.0;
    cfg->seed_data = SEED2;
    cfg->seed_ack = SEED3;
    cfg->seed_mac = SEED1;
    *Ws = 1;
    *Wr = 1;
    *trace = 0;

    for (i = 1; i < argc; i++) {
        const char *a = argv[i];
        if (i + 1 >= argc) {
            usage(argv[0]);
            return 1;
        }
        if (strcmp(a, "--ws") == 0) *Ws = atoi(argv[++i]);
        else if (strcmp(a, "--wr") == 0) *Wr = atoi(argv[++i]);
        else if (strcmp(a, "--pd") == 0) cfg->pd = atof(argv[++i]);
        else if (strcmp(a, "--pa") == 0) cfg->pa = atof(argv[++i]);
        else if (strcmp(a, "--timeout") == 0) cfg->timeout_ms = atof(argv[++i]);
        else if (strcmp(a, "--n") == 0) cfg->N = atoi(argv[++i]);
        else if (strcmp(a, "--tend") == 0) cfg->t_end = atof(argv[++i]);
        else if (strcmp(a, "--p") == 0) cfg->p = atof(argv[++i]);
        else if (strcmp(a, "--tmini") == 0) cfg->t_mini = atof(argv[++i]);
        else if (strcmp(a, "--seed-data") == 0) cfg->seed_data = strtoull(argv[++i], NULL, 10);
        else if (strcmp(a, "--seed-ack") == 0) cfg->seed_ack = strtoull(argv[++i], NULL, 10);
        else if (strcmp(a, "--seed-mac") == 0) cfg->seed_mac = strtoull(argv[++i], NULL, 10);
        else if (strcmp(a, "--trace") == 0) *trace = atoi(argv[++i]);
        else if (strcmp(a, "--mac") == 0) {
            const char *m = argv[++i];
            if (strcmp(m, "sched") == 0) cfg->mac = MAC_SCHED;
            else if (strcmp(m, "aloha") == 0) cfg->mac = MAC_ALOHA;
            else return 1;
        } else if (strcmp(a, "--timer") == 0) {
            const char *m = argv[++i];
            if (strcmp(m, "tx") == 0) cfg->timer_mode = TIMER_TX;
            else if (strcmp(m, "ready") == 0) cfg->timer_mode = TIMER_READY;
            else return 1;
        } else {
            usage(argv[0]);
            return 1;
        }
    }
    if (*Ws < 1 || *Wr < 1 || cfg->timeout_ms <= 0 || cfg->t_mini <= 0 ||
        cfg->p < 0 || cfg->p > 1) {
        fprintf(stderr, "bad ws/wr/timeout/tmini/p\n");
        return 1;
    }
    if (cfg->pd < 0) cfg->pd = 0;
    if (cfg->pa < 0) cfg->pa = 0;
    if (cfg->pd > 1) cfg->pd = 1;
    if (cfg->pa > 1) cfg->pa = 1;
    if (cfg->N > 0) {
        cfg->continuous = 0;
        if (cfg->t_end <= 0)
            cfg->t_end = FINITE_SAFETY_MS;
    } else {
        cfg->continuous = 1;
        cfg->N = 0;
        if (cfg->t_end <= 0)
            cfg->t_end = DEFAULT_TEND;
    }
    return 0;
}

int main(int argc, char **argv)
{
    Config cfg;
    Sim sim;
    int Ws = 1, Wr = 1, trace = 0, rc, i;

    if (parse_args(argc, argv, &cfg, &Ws, &Wr, &trace))
        return 1;
    sim_init(&sim, &cfg);
    for (i = 0; i < NLINKS; i++)
        link_config(&sim.links[i], Ws, Wr);
    sim.trace = trace;
    if (trace) {
        printf("TRACE_HEADER mac=%s timer=%s ws=%d wr=%d pd=%.4f pa=%.4f timeout=%.3f "
               "n=%d tend=%.3f p=%.3f tmini=%.3f\n",
               sim.mac == MAC_SCHED ? "sched" : "aloha",
               sim.timer_mode == TIMER_TX ? "tx" : "ready",
               Ws, Wr, sim.pd, sim.pa, sim.timeout_ms, sim.N, sim.t_end, sim.p, sim.t_mini);
    }
    rc = sim_run(&sim);
    if (rc != 0) {
        fprintf(stderr, "simulation stopped early (code %d)\n", rc);
        print_result(&sim);
        sim_free(&sim);
        return rc;
    }
    print_result(&sim);
    sim_free(&sim);
    return 0;
}
