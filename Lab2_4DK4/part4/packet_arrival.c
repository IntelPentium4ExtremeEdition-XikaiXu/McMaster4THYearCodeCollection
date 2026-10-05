#include "main.h"
#include "packet_arrival.h"
#include "packet_transmission.h"

static long int schedule_arrival_event(Simulation_Run_Ptr simulation_run,
                                       double event_time,
                                       void (*function)(Simulation_Run_Ptr, void *),
                                       const char *description)
{
  Event event;
  event.description = description;
  event.function = function;
  event.attachment = NULL;
  return simulation_run_schedule_event(simulation_run, event, event_time);
}

long int schedule_packet_arrival_1_event(Simulation_Run_Ptr simulation_run,
                                         double event_time)
{
  return schedule_arrival_event(simulation_run, event_time,
                                packet_arrival_1_event, "Source 1 Arrival");
}

long int schedule_packet_arrival_2_event(Simulation_Run_Ptr simulation_run,
                                         double event_time)
{
  return schedule_arrival_event(simulation_run, event_time,
                                packet_arrival_2_event, "Source 2 Arrival");
}

long int schedule_packet_arrival_3_event(Simulation_Run_Ptr simulation_run,
                                         double event_time)
{
  return schedule_arrival_event(simulation_run, event_time,
                                packet_arrival_3_event, "Source 3 Arrival");
}

static Packet_Ptr create_packet(Simulation_Run_Ptr simulation_run, int source_id)
{
  Packet_Ptr packet = (Packet_Ptr)xmalloc(sizeof(Packet));
  packet->arrive_time = simulation_run_get_time(simulation_run);
  if (source_id == 1)
    packet->service_time = PACKET_XMT_TIME_LINK1;   /* 0.5 ms */
  else
    packet->service_time = PACKET_XMT_TIME_LINK2;   /* 1.0 ms, Link 3 same */
  packet->source_id = source_id;
  packet->destination_id = 0;
  packet->status = WAITING;
  return packet;
}

static void send_or_queue(Simulation_Run_Ptr simulation_run,
                          Packet_Ptr packet,
                          Server_Ptr link,
                          Fifoqueue_Ptr buffer)
{
  if (server_state(link) == FREE)
    start_transmission_on_link(simulation_run, packet, link);
  else
    fifoqueue_put(buffer, packet);
}

void packet_arrival_1_event(Simulation_Run_Ptr simulation_run, void *unused)
{
  Simulation_Run_Data_Ptr data;
  Packet_Ptr packet;
  (void)unused;
  data = (Simulation_Run_Data_Ptr)simulation_run_data(simulation_run);
  data->arrival_count[0]++;
  packet = create_packet(simulation_run, 1);
  send_or_queue(simulation_run, packet, data->link1, data->buffer1);
  schedule_packet_arrival_1_event(
    simulation_run,
    simulation_run_get_time(simulation_run) +
      exponential_generator(1.0 / ARRIVAL_RATE_1));
}

void packet_arrival_2_event(Simulation_Run_Ptr simulation_run, void *unused)
{
  Simulation_Run_Data_Ptr data;
  Packet_Ptr packet;
  (void)unused;
  data = (Simulation_Run_Data_Ptr)simulation_run_data(simulation_run);
  data->arrival_count[1]++;
  packet = create_packet(simulation_run, 2);
  send_or_queue(simulation_run, packet, data->link2, data->buffer2);
  schedule_packet_arrival_2_event(
    simulation_run,
    simulation_run_get_time(simulation_run) +
      exponential_generator(1.0 / ARRIVAL_RATE_2));
}

void packet_arrival_3_event(Simulation_Run_Ptr simulation_run, void *unused)
{
  Simulation_Run_Data_Ptr data;
  Packet_Ptr packet;
  (void)unused;
  data = (Simulation_Run_Data_Ptr)simulation_run_data(simulation_run);
  data->arrival_count[2]++;
  packet = create_packet(simulation_run, 3);
  send_or_queue(simulation_run, packet, data->link3, data->buffer3);
  schedule_packet_arrival_3_event(
    simulation_run,
    simulation_run_get_time(simulation_run) +
      exponential_generator(1.0 / ARRIVAL_RATE_3));
}
