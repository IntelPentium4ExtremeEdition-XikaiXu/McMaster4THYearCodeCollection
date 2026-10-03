#include "main.h"
#include "output.h"
#include "packet_transmission.h"

long int schedule_end_packet_transmission_event(
  Simulation_Run_Ptr simulation_run,
  double event_time,
  Server_Ptr link)
{
  Event event;
  event.description = "Packet Transmission End";
  event.function = end_packet_transmission_event;
  event.attachment = (void *)link;
  return simulation_run_schedule_event(simulation_run, event, event_time);
}

void end_packet_transmission_event(
  Simulation_Run_Ptr simulation_run,
  void *link_ptr)
{
  Simulation_Run_Data_Ptr data;
  Server_Ptr link;
  Packet_Ptr packet;
  Packet_Ptr next_packet;
  double packet_delay;

  data = (Simulation_Run_Data_Ptr)simulation_run_data(simulation_run);
  link = (Server_Ptr)link_ptr;
  packet = (Packet_Ptr)server_get(link);

  packet_delay = simulation_run_get_time(simulation_run) - packet->arrive_time;

  if (packet->type == VOICE_PACKET) {
    data->voice_processed_count++;
    data->voice_accumulated_delay += packet_delay;
  } else {
    data->data_processed_count++;
    data->data_accumulated_delay += packet_delay;
  }

  xfree(packet);
  output_progress_msg_to_screen(simulation_run);

  /* Part 5 is strict FCFS: always take the front packet, regardless of type. */
  if (fifoqueue_size(data->buffer) > 0) {
    next_packet = (Packet_Ptr)fifoqueue_get(data->buffer);
    start_transmission_on_link(simulation_run, next_packet, link);
  }
}

void start_transmission_on_link(
  Simulation_Run_Ptr simulation_run,
  Packet_Ptr packet,
  Server_Ptr link)
{
  server_put(link, packet);
  packet->status = XMTTING;
  schedule_end_packet_transmission_event(
    simulation_run,
    simulation_run_get_time(simulation_run) + packet->service_time,
    link);
}
