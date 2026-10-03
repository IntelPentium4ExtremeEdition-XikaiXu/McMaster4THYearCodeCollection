#ifndef _SIMPARAMETERS_H_
#define _SIMPARAMETERS_H_

/* Part 4 traffic source rates, packets per second. */
#define ARRIVAL_RATE_1 750.0
#define ARRIVAL_RATE_2 500.0
#define ARRIVAL_RATE_3 500.0

/* All packets and links use these values. */
#define PACKET_LENGTH 500.0
#define LINK_BIT_RATE 1000000.0
#define PACKET_XMT_TIME ((double)PACKET_LENGTH / LINK_BIT_RATE)

/* Total completed packets from all three sources per run. */
#define RUNLENGTH 1000000L
#define RANDOM_SEED_LIST 400440917, 400473040
#define BLIPRATE (RUNLENGTH / 1000)

#endif
