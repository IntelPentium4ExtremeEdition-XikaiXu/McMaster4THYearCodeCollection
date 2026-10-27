
#ifndef _SIMPARAMETERS_H_
#define _SIMPARAMETERS_H_

#include "lab_seeds.h"

#define MAX_STATIONS 10
#define NUMBER_OF_STATIONS 10
#define MEAN_PACKET_DURATION 1
#define PACKET_ARRIVAL_RATE 0.1
#define MEAN_BACKOFF_DURATION 10
#define RUNLENGTH 70000000
#define SWEEP_RUNLENGTH 1000000
#define BLIPRATE 100000

#define USE_BINARY_EXPONENTIAL_BACKOFF 1
#define MAX_BEB_COLLISION_COUNT 10

/* Part 4: persistent station; use -1 for parts 1–3. */
#define PERSISTENT_STATION_ID 0

#endif /* simparameters.h */
