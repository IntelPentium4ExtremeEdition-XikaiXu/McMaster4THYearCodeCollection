
/*
 * Simulation_Run of the ALOHA Protocol
 * 
 * Copyright (C) 2014 Terence D. Todd Hamilton, Ontario, CANADA
 * todd@mcmaster.ca
 * 
 * This program is free software; you can redistribute it and/or modify it
 * under the terms of the GNU General Public License as published by the Free
 * Software Foundation; either version 3 of the License, or (at your option)
 * any later version.
 * 
 * This program is distributed in the hope that it will be useful, but WITHOUT
 * ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
 * FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
 * more details.
 * 
 * You should have received a copy of the GNU General Public License along with
 * this program.  If not, see <http://www.gnu.org/licenses/>.
 * 
 */

/*******************************************************************************/

#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include "output.h"
#include "trace.h"
#include "simparameters.h"
#include "cleanup.h"
#include "packet_arrival.h"
#include "packet_transmission.h"
#include "main.h"

/*******************************************************************************/

/* logspace(0.01, 1.00, 15): dense near 0, then stretches to 1 */
static const double arrival_rates[] = {
  0.0100, 0.0139, 0.0193, 0.0268, 0.0373,
  0.0518, 0.0720, 0.1000, 0.1389, 0.1931,
  0.2683, 0.3728, 0.5179, 0.7197, 1.0000
};

static int
save_results(FILE *file, Simulation_Run_Ptr simulation_run)
{
  Simulation_Run_Data_Ptr data;
  double finish_time;
  double mean_delay;
  double throughput;
  double aggregate_load_G;
  double persistent_delay;
  double persistent_throughput;
  double other_delay_sum;
  double other_successes;
  int other_stations;
  int i;
  Station_Ptr persistent;

  data = (Simulation_Run_Data_Ptr) simulation_run_data(simulation_run);
  finish_time = simulation_run_get_time(simulation_run);
  mean_delay = 0.0;
  throughput = 0.0;
  aggregate_load_G = 0.0;
  if (data->number_of_packets_processed > 0) {
    mean_delay = data->accumulated_delay / data->number_of_packets_processed;
  }
  if (finish_time > 0.0) {
    throughput = (double) data->number_of_packets_processed / finish_time;
    aggregate_load_G =
      (double) data->number_of_transmission_attempts / finish_time;
  }

  persistent = data->stations + data->persistent_station_id;
  persistent_delay = 0.0;
  persistent_throughput = 0.0;
  if(persistent->packet_count > 0) {
    persistent_delay = persistent->accumulated_delay / persistent->packet_count;
    persistent_throughput = (double) persistent->packet_count / finish_time;
  }

  other_delay_sum = 0.0;
  other_successes = 0.0;
  other_stations = 0;
  for(i = 0; i < data->number_of_stations; i++) {
    if(i == data->persistent_station_id) {
      continue;
    }
    other_delay_sum += (data->stations+i)->accumulated_delay;
    other_successes += (data->stations+i)->packet_count;
    other_stations++;
  }

  if (fprintf(file,
	      "%d,%d,%.4f,%u,%ld,%ld,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%ld\n",
	      data->number_of_stations,
	      data->persistent_station_id,
	      data->packet_arrival_rate,
	      data->random_seed,
	      data->arrival_count,
	      data->number_of_packets_processed,
	      mean_delay,
	      throughput,
	      aggregate_load_G,
	      persistent_delay,
	      persistent_throughput,
	      other_successes > 0.0 ? other_delay_sum / other_successes : 0.0,
	      other_stations > 0
		? (other_successes / other_stations) / finish_time
		: 0.0,
	      finish_time,
	      data->arrival_count - data->number_of_packets_processed) < 0) {
    return 1;
  }
  fflush(file);

  printf("N=%d lambda=%.4f seed=%u persist D=%.3f S=%.4f  others D=%.3f S=%.4f\n",
	 data->number_of_stations,
	 data->packet_arrival_rate,
	 data->random_seed,
	 persistent_delay,
	 persistent_throughput,
	 other_successes > 0.0 ? other_delay_sum / other_successes : 0.0,
	 other_stations > 0
	   ? (other_successes / other_stations) / finish_time
	   : 0.0);
  return 0;
}

int
main(void)
{
  /* Get the list of random number generator seeds defined in simparameters.h */
  unsigned random_seed;
  unsigned RANDOM_SEEDS[] = {RANDOM_SEED_LIST, 0};

  Simulation_Run_Ptr simulation_run;
  Simulation_Run_Data data;
  FILE *results;
  int config, station, seed_index, lambda_step;

  results = fopen("part4_results.csv", "w");
  if (results == NULL) {
    perror("part4_results.csv");
    return 1;
  }
  fprintf(results,
	  "stations,persistent_station_id,lambda,seed,arrivals,successes,mean_delay,throughput,aggregate_load_G,persistent_delay,persistent_throughput,other_mean_delay,other_mean_throughput,finish_time,live_packets\n");

  int station_counts[2] = {10, 5};
  for (config = 0 ; config < 2; config++) {
    int number_of_stations = station_counts[config];

    for (lambda_step = 0;
         lambda_step < (int) (sizeof arrival_rates / sizeof arrival_rates[0]);
         lambda_step++) {
      double packet_arrival_rate = arrival_rates[lambda_step];

    /* Do a new simulation_run for each random number generator seed. */
    seed_index = 0;
    while ((random_seed = RANDOM_SEEDS[seed_index++]) != 0) {

      /* Set the random generator seed. */
      random_generator_initialize(random_seed);

      /* Create a new simulation_run. This gives a clock and
        eventlist. Clock time is set to zero. */
      simulation_run = (Simulation_Run_Ptr) simulation_run_new();

      /* Add our data definitions to the simulation_run. */
      simulation_run_set_data(simulation_run, (void *) & data);

      /* Create and initalize the stations. */
      data.stations = (Station_Ptr) xcalloc((unsigned int) number_of_stations,
              sizeof(Station));

      /* Initialize various simulation_run variables. */
      data.blip_counter = 0;
      data.arrival_count = 0;
      data.number_of_packets_processed = 0;
      data.number_of_collisions = 0;
      data.number_of_transmission_attempts = 0;
      data.accumulated_delay = 0.0;
      data.random_seed = random_seed;
      data.number_of_stations = number_of_stations;
      data.persistent_station_id = PERSISTENT_STATION_ID;
      data.mean_backoff_duration = 0.0;
      data.packet_arrival_rate = packet_arrival_rate;
      
      /* Initialize the stations. */
      for(station=0; station<number_of_stations; station++) {
        (data.stations+station)->id = station;
        (data.stations+station)->buffer = fifoqueue_new();
        (data.stations+station)->packet_count = 0;
        (data.stations+station)->accumulated_delay = 0.0;
        (data.stations+station)->mean_delay = 0;
      }

      /* Create and initialize the channel. */
      data.channel = channel_new();

      /* Schedule initial packet arrival. */
      schedule_packet_arrival_event(simulation_run, 
          simulation_run_get_time(simulation_run) +
          exponential_generator((double) 1/packet_arrival_rate));

      /* Execute events until we are finished. */
      while(data.number_of_packets_processed < RUNLENGTH &&
            data.arrival_count - data.number_of_packets_processed
              < MAX_LIVE_PACKETS) {
        simulation_run_execute_event(simulation_run);
      }
      if (data.arrival_count - data.number_of_packets_processed
            >= MAX_LIVE_PACKETS) {
        printf("\nStopped early: %ld packets still queued "
               "(successes %ld / %d).\n",
               data.arrival_count - data.number_of_packets_processed,
               data.number_of_packets_processed,
               RUNLENGTH);
      }

      /* Print out some results. */
      output_results(simulation_run);
      if (save_results(results, simulation_run) != 0) {
        perror("part4_results.csv");
        fclose(results);
        cleanup(simulation_run);
        return 1;
      }

      /* Clean up memory. */
      cleanup(simulation_run);
    }
    }
  }

  fclose(results);

  /* Pause before finishing. */
  getchar();

  return 0;
}












