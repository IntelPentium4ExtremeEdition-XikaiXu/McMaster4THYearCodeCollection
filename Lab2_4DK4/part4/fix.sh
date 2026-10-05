#!/bin/bash
# fix_part4.sh — 自动写入 Part 4 所需的所有正确源文件

cat >simparameters.h <<'EOF'
#ifndef _SIMPARAMETERS_H_
#define _SIMPARAMETERS_H_

/* Part 4 traffic source rates, packets per second. */
#define ARRIVAL_RATE_1 750.0
#define ARRIVAL_RATE_2 500.0
#define ARRIVAL_RATE_3 500.0

/* Part 4: all packets are 1000 bits. */
#define PACKET_LENGTH 1000.0

/* Link 1 = 2 Mbps, Link 2 and Link 3 = 1 Mbps. */
#define LINK1_BIT_RATE 2000000.0
#define LINK2_BIT_RATE 1000000.0
#define LINK3_BIT_RATE 1000000.0

/* Per-link transmission times (seconds). */
#define PACKET_XMT_TIME_LINK1 ((double)PACKET_LENGTH / LINK1_BIT_RATE)  /* 0.5 ms */
#define PACKET_XMT_TIME_LINK2 ((double)PACKET_LENGTH / LINK2_BIT_RATE)  /* 1.0 ms */
#define PACKET_XMT_TIME_LINK3 ((double)PACKET_LENGTH / LINK3_BIT_RATE)  /* 1.0 ms */

/* Total completed packets from all three sources per run. */
#define RUNLENGTH 10000000L
#define RANDOM_SEED_LIST 400440917, 400473040
#define BLIPRATE (RUNLENGTH / 1000)

#endif
EOF

cat >packet_arrival.h <<'EOF'
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
EOF

cat >packet_transmission.h <<'EOF'
#ifndef _PACKET_TRANSMISSION_H_
#define _PACKET_TRANSMISSION_H_

#include "main.h"

long int schedule_end_packet_transmission_event(
  Simulation_Run_Ptr, double, Server_Ptr);
void start_transmission_on_link(
  Simulation_Run_Ptr, Packet_Ptr, Server_Ptr);
void end_packet_transmission_event(Simulation_Run_Ptr, void *);
double get_packet_transmission_time(void);

#endif
EOF

cat >packet_arrival.c <<'EOF'
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
EOF

cat >packet_transmission.c <<'EOF'
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
EOF

echo "所有文件已写入。现在请编译："
echo "gcc -O2 -Wall -o part4 main.c packet_arrival.c packet_transmission.c output.c cleanup_memory.c simlib.c -lm"
