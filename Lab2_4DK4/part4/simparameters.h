#ifndef _SIMPARAMETERS_H_
#define _SIMPARAMETERS_H_

/* Part 4 traffic source rates, packets per second. */
#define ARRIVAL_RATE_1 750.0
#define ARRIVAL_RATE_2 500.0
#define ARRIVAL_RATE_3 500.0

/* Part 4: all packets are 1000 bits. */
#define PACKET_LENGTH 1000.0

/* Link 1 = 2 Mbps, Link 2 and Link 3 = 1 Mbps. */
#define LINK1_BIT_RATE 2000000.0
#define LINK2_BIT_RATE 1000000.0
#define LINK3_BIT_RATE 1000000.0

/* Per-link transmission times (seconds). */
#define PACKET_XMT_TIME_LINK1 ((double)PACKET_LENGTH / LINK1_BIT_RATE)  /* 0.5 ms */
#define PACKET_XMT_TIME_LINK2 ((double)PACKET_LENGTH / LINK2_BIT_RATE)  /* 1.0 ms */
#define PACKET_XMT_TIME_LINK3 ((double)PACKET_LENGTH / LINK3_BIT_RATE)  /* 1.0 ms */

/* Total completed packets from all three sources per run. */
#define RUNLENGTH 10000000L
#define RANDOM_SEED_LIST 400440917, 400473040
#define BLIPRATE (RUNLENGTH / 1000)

#endif
