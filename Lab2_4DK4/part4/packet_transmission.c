#include "trace.h"
#include "main.h"
#include "output.h"
#include "packet_transmission.h"

long int schedule_end_packet_transmission_event(
  Simulation_Run_Ptr simulation_run,
  double event_time,
  Server_Ptr link)
{
  Event event;
  event.description = "Packet Xmt End";
  event.function = end_packet_transmission_event;
  event.attachment = (void *)link;
  return simulation_run_schedule_event(simulation_run, event, event_time);
}

static void start_next_waiting_packet(Simulation_Run_Ptr simulation_run,
                                      Fifoqueue_Ptr buffer,
                                      Server_Ptr link)
{
  Packet_Ptr next_packet;
  if (fifoqueue_size(buffer) > 0) {
    next_packet = (Packet_Ptr)fifoqueue_get(buffer);
    start_transmission_on_link(simulation_run, next_packet, link);
  }
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

static void complete_network_packet(Simulation_Run_Ptr simulation_run,
                                    Simulation_Run_Data_Ptr data,
                                    Packet_Ptr packet)
{
  int source_index = packet->source_id - 1;
  data->number_of_packets_processed[source_index]++;
  data->accumulated_delay[source_index] +=
    simulation_run_get_time(simulation_run) - packet->arrive_time;
  xfree(packet);
  output_progress_msg_to_screen(simulation_run);
}

void end_packet_transmission_event(Simulation_Run_Ptr simulation_run, void *ptr)
{
  Simulation_Run_Data_Ptr data;
  Server_Ptr completed_link = (Server_Ptr)ptr;
  Packet_Ptr packet;

  data = (Simulation_Run_Data_Ptr)simulation_run_data(simulation_run);
  packet = (Packet_Ptr)server_get(completed_link);

  if (completed_link == data->link1) {
    /* Keep Link 1 busy with its next queued packet before forwarding. */
    start_next_waiting_packet(simulation_run, data->buffer1, data->link1);

    /* Forwarding over Link 2 or Link 3 uses a 1 ms service time. */
    if (uniform_generator() < data->p12) {
      packet->destination_id = 2;
      packet->service_time = PACKET_XMT_TIME_LINK2;
      send_or_queue(simulation_run, packet, data->link2, data->buffer2);
    } else {
      packet->destination_id = 3;
      packet->service_time = PACKET_XMT_TIME_LINK3;
      send_or_queue(simulation_run, packet, data->link3, data->buffer3);
    }
    return;
  }

  if (completed_link == data->link2) {
    complete_network_packet(simulation_run, data, packet);
    start_next_waiting_packet(simulation_run, data->buffer2, data->link2);
    return;
  }

  if (completed_link == data->link3) {
    complete_network_packet(simulation_run, data, packet);
    start_next_waiting_packet(simulation_run, data->buffer3, data->link3);
    return;
  }
}

void start_transmission_on_link(Simulation_Run_Ptr simulation_run,
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

double get_packet_transmission_time(void)
{
  return PACKET_XMT_TIME_LINK1;
}
