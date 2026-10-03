#ifndef _SIMPARAMETERS_H_
#define _SIMPARAMETERS_H_

/* Voice: G.711, 64 kbit/s, 20 ms packetization, 62-byte header. */
#define VOICE_INTERARRIVAL_TIME 0.020
#define VOICE_PACKET_LENGTH 1776.0

/* One shared 1 Mbit/s output link. */
#define LINK_BIT_RATE 1000000.0
#define VOICE_SERVICE_TIME (VOICE_PACKET_LENGTH / LINK_BIT_RATE)

/* Data packet transmission time is exponential with 40 ms mean. */
#define DATA_MEAN_SERVICE_TIME 0.040

/* Total completed Voice + Data packets in each run. */
#define RUNLENGTH 1000000L
#define RANDOM_SEED_LIST 400440917, 400473040
#define BLIPRATE (RUNLENGTH / 1000)

#endif
