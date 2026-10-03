#ifndef _PACKET_ARRIVAL_H_
#define _PACKET_ARRIVAL_H_

#include "simlib.h"

long int schedule_packet_arrival_1_event(Simulation_Run_Ptr, double);
long int schedule_packet_arrival_2_event(Simulation_Run_Ptr, double);
long int schedule_packet_arrival_3_event(Simulation_Run_Ptr, double);

void packet_arrival_1_event(Simulation_Run_Ptr, void *);
void packet_arrival_2_event(Simulation_Run_Ptr, void *);
void packet_arrival_3_event(Simulation_Run_Ptr, void *);

#endif
