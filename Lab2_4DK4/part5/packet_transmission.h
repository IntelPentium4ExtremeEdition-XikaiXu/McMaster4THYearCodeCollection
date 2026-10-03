#ifndef _PACKET_TRANSMISSION_H_
#define _PACKET_TRANSMISSION_H_

#include "main.h"

long int schedule_end_packet_transmission_event(
  Simulation_Run_Ptr, double, Server_Ptr);
void start_transmission_on_link(
  Simulation_Run_Ptr, Packet_Ptr, Server_Ptr);
void end_packet_transmission_event(Simulation_Run_Ptr, void *);

#endif
