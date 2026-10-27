#include <stdlib.h>
#include "sim_run.h"
#include "simparameters.h"
#include "cleanup.h"
#include "packet_arrival.h"
#include "packet_transmission.h"
#include "output.h"

void
aloha_run_simulation(const Aloha_Run_Config *cfg, Aloha_Run_Result *result)
{
  Simulation_Run_Ptr simulation_run;
  Simulation_Run_Data data;
  int i;

  random_generator_initialize(cfg->random_seed);

  simulation_run = (Simulation_Run_Ptr) simulation_run_new();
  simulation_run_set_data(simulation_run, (void *) &data);

  data.number_of_stations = cfg->number_of_stations;
  data.packet_arrival_rate = cfg->packet_arrival_rate;
  data.mean_backoff_duration = cfg->mean_backoff_duration;
  data.use_binary_exponential_backoff = cfg->use_binary_exponential_backoff;
  data.persistent_station_id = cfg->persistent_station_id;
  data.runlength_target = cfg->runlength;
  data.random_seed = cfg->random_seed;
  data.print_results = cfg->print_results;

  data.stations = (Station_Ptr) xcalloc((unsigned int) MAX_STATIONS,
					sizeof(Station));

  data.blip_counter = 0;
  data.arrival_count = 0;
  data.number_of_packets_processed = 0;
  data.number_of_collisions = 0;
  data.number_of_transmission_attempts = 0;
  data.accumulated_delay = 0.0;
  data.channel = channel_new();

  for(i = 0; i < cfg->number_of_stations; i++) {
    (data.stations+i)->id = i;
    (data.stations+i)->buffer = fifoqueue_new();
    (data.stations+i)->packet_count = 0;
    (data.stations+i)->accumulated_delay = 0.0;
    (data.stations+i)->mean_delay = 0;
  }

  schedule_packet_arrival_event(simulation_run,
				simulation_run_get_time(simulation_run) +
				exponential_generator((double)
						      1/cfg->packet_arrival_rate));

  while(data.number_of_packets_processed < cfg->runlength) {
    simulation_run_execute_event(simulation_run);
  }

  if(cfg->print_results) {
    output_results(simulation_run);
  }

  result->arrivals = data.arrival_count;
  result->successes = data.number_of_packets_processed;
  result->collision_count_sum = data.number_of_collisions;
  result->transmission_attempts = data.number_of_transmission_attempts;
  result->delay_sum = data.accumulated_delay;
  result->finish_time = simulation_run_get_time(simulation_run);
  result->throughput =
    (double) result->successes / result->finish_time;
  result->mean_delay = result->delay_sum / result->successes;
  result->collisions_per_success =
    (double) result->collision_count_sum / result->successes;
  /* G: total channel transmission-attempt rate (packet-times per Tx time). */
  result->aggregate_load_G =
    (double) result->transmission_attempts / result->finish_time;

  cleanup(simulation_run);
}
