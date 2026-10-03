#ifndef _MAIN_H_
#define _MAIN_H_

#include "simlib.h"
#include "simparameters.h"

typedef enum {
  VOICE_PACKET,
  DATA_PACKET
} Packet_Type;

typedef enum {
  XMTTING,
  WAITING
} Packet_Status;

typedef struct _packet_
{
  double arrive_time;
  double service_time;
  Packet_Type type;
  Packet_Status status;
} Packet, *Packet_Ptr;

typedef struct _simulation_run_data_
{
  Fifoqueue_Ptr voice_buffer;
  Fifoqueue_Ptr data_buffer;
  Server_Ptr link;

  long int blip_counter;
  long int voice_arrival_count;
  long int data_arrival_count;
  long int voice_processed_count;
  long int data_processed_count;

  double voice_accumulated_delay;
  double data_accumulated_delay;
  double data_arrival_rate;

  unsigned random_seed;
} Simulation_Run_Data, *Simulation_Run_Data_Ptr;

int main(void);

#endif
