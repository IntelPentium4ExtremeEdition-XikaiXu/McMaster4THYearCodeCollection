#ifndef _PART1_APPENDIX_A_H_
#define _PART1_APPENDIX_A_H_

/*
 * Part 1 only.
 * Fixed arrival rate. Four seeds (2 student IDs + 114514, 1919810).
 * Six (stations, backoff) pairs:
 *   N=10 with backoff 5, 10, 20
 *   N=5  with backoff 3, 5, 7
 * Runs = 4 seeds x 6 configs = 24.
 */

#include "lab_seeds.h"

#define PART1_USE_APPENDIX_A 1

#define APPENDIX_A_MODEL_NAME           "M/D/1, FCFS"
#define APPENDIX_A_PACKET_LENGTH_BITS   500
#define APPENDIX_A_LINK_BIT_RATE_BPS    1000000.0
#define APPENDIX_A_PACKET_TX_TIME_SEC   (APPENDIX_A_PACKET_LENGTH_BITS / APPENDIX_A_LINK_BIT_RATE_BPS)
#define APPENDIX_A_PACKET_TX_TIME_MS    0.5

/* One arrival rate for every Part 1 run (packets per packet-Tx-time). */
#define APPENDIX_A_ARRIVAL_RATE  0.10

#define APPENDIX_A_NUM_SEEDS     LAB_NUM_SEEDS
#define APPENDIX_A_NUM_CONFIGS   6
#define APPENDIX_A_NUM_RUNS      (APPENDIX_A_NUM_SEEDS * APPENDIX_A_NUM_CONFIGS)

#define appendix_a_seeds lab_seeds

/* {number of stations, mean backoff duration} */
static const int appendix_a_configs[APPENDIX_A_NUM_CONFIGS][2] = {
  {10, 5}, {10, 10}, {10, 20},
  {5, 3}, {5, 5}, {5, 7}
};

#define APPENDIX_A_LAMBDA_PACKETS_PER_SEC(lambda_normalized) \
  ((lambda_normalized) / (APPENDIX_A_PACKET_TX_TIME_SEC))

#endif /* part1_appendix_a.h */
