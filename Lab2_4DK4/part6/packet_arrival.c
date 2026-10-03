#include "main.h"
#include "packet_arrival.h"
#include "packet_transmission.h"

static long int schedule_arrival_event(
  Simulation_Run_Ptr simulation_run,
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

long int schedule_voice_packet_arrival_event(
  Simulation_Run_Ptr simulation_run,
  double event_time)
{
  return schedule_arrival_event(
    simulation_run, event_time,
    voice_packet_arrival_event, "Voice Packet Arrival");
}

long int schedule_data_packet_arrival_event(
  Simulation_Run_Ptr simulation_run,
  double event_time)
{
  return schedule_arrival_event(
    simulation_run, event_time,
    data_packet_arrival_event, "Data Packet Arrival");
}

static void start_or_enqueue(
  Simulation_Run_Ptr simulation_run,
  Simulation_Run_Data_Ptr data,
  Packet_Ptr packet,
  Fifoqueue_Ptr destination_buffer)
{
  if (server_state(data->link) == FREE)
    start_transmission_on_link(simulation_run, packet, data->link);
  else
    fifoqueue_put(destination_buffer, packet);
}

void voice_packet_arrival_event(
  Simulation_Run_Ptr simulation_run,
  void *unused)
{
  Simulation_Run_Data_Ptr data;
  Packet_Ptr packet;
  (void)unused;

  data = (Simulation_Run_Data_Ptr)simulation_run_data(simulation_run);
  data->voice_arrival_count++;

  packet = (Packet_Ptr)xmalloc(sizeof(Packet));
  packet->arrive_time = simulation_run_get_time(simulation_run);
  packet->service_time = VOICE_SERVICE_TIME;
  packet->type = VOICE_PACKET;
  packet->status = WAITING;

  start_or_enqueue(simulation_run, data, packet, data->voice_buffer);

  schedule_voice_packet_arrival_event(
    simulation_run,
    simulation_run_get_time(simulation_run) + VOICE_INTERARRIVAL_TIME);
}

void data_packet_arrival_event(
  Simulation_Run_Ptr simulation_run,
  void *unused)
{
  Simulation_Run_Data_Ptr data;
  Packet_Ptr packet;
  (void)unused;

  data = (Simulation_Run_Data_Ptr)simulation_run_data(simulation_run);
  data->data_arrival_count++;

  packet = (Packet_Ptr)xmalloc(sizeof(Packet));
  packet->arrive_time = simulation_run_get_time(simulation_run);
  packet->service_time = exponential_generator(DATA_MEAN_SERVICE_TIME);
  packet->type = DATA_PACKET;
  packet->status = WAITING;

  start_or_enqueue(simulation_run, data, packet, data->data_buffer);

  schedule_data_packet_arrival_event(
    simulation_run,
    simulation_run_get_time(simulation_run) +
      exponential_generator(1.0 / data->data_arrival_rate));
}
