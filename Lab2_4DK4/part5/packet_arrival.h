#ifndef _PACKET_ARRIVAL_H_
#define _PACKET_ARRIVAL_H_

#include "simlib.h"

long int schedule_voice_packet_arrival_event(Simulation_Run_Ptr, double);
long int schedule_data_packet_arrival_event(Simulation_Run_Ptr, double);
void voice_packet_arrival_event(Simulation_Run_Ptr, void *);
void data_packet_arrival_event(Simulation_Run_Ptr, void *);

#endif
