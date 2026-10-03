#ifndef _MAIN_H_
#define _MAIN_H_

#include "simlib.h"
#include "simparameters.h"

typedef struct _simulation_run_data_
{
  Fifoqueue_Ptr buffer1;
  Fifoqueue_Ptr buffer2;
  Fifoqueue_Ptr buffer3;

  Server_Ptr link1;
  Server_Ptr link2;
  Server_Ptr link3;

  long int blip_counter;
  long int arrival_count[3];
  long int number_of_packets_processed[3];
  double accumulated_delay[3];

  double p12;
  unsigned random_seed;
} Simulation_Run_Data, *Simulation_Run_Data_Ptr;

typedef enum {XMTTING, WAITING} Packet_Status;

typedef struct _packet_
{
  double arrive_time;
  double service_time;
  int source_id;
  int destination_id;
  Packet_Status status;
} Packet, *Packet_Ptr;

int main(void);

#endif
