
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

#include <stdio.h>
#include "simparameters.h"
#include "main.h"
#include "output.h"

/*******************************************************************************/

void
output_blip_to_screen(Simulation_Run_Ptr simulation_run)
{
  double percentagedone;
  Simulation_Run_Data_Ptr data;

  data = (Simulation_Run_Data_Ptr) simulation_run_data(simulation_run);

  data->blip_counter++;

  if((data->blip_counter >= BLIPRATE)
     ||
     (data->number_of_packets_processed >= data->runlength_target)) {

    data->blip_counter = 0;

    percentagedone =
      100 * (double) data->number_of_packets_processed/data->runlength_target;

    printf("%3.0f%% ", percentagedone);

    printf("Successfully Xmtted Pkts  = %ld (Arrived Pkts = %ld) \r", 
	   data->number_of_packets_processed, 
	   data->arrival_count);

    fflush(stdout);
  }
}

/**********************************************************************/

void output_results(Simulation_Run_Ptr this_simulation_run)
{
  int i;
  double xmtted_fraction;
  double finish_time;
  double system_throughput;
  double other_delay_sum = 0.0;
  long int other_packet_count = 0;
  Simulation_Run_Data_Ptr sim_data;

  sim_data = (Simulation_Run_Data_Ptr) simulation_run_data(this_simulation_run);
  finish_time = simulation_run_get_time(this_simulation_run);
  system_throughput =
    (double) sim_data->number_of_packets_processed / finish_time;

  printf("\n");
  printf("Random Seed = %d \n", sim_data->random_seed);
  printf("Pkt Arrivals = %ld \n", sim_data->arrival_count);

  xmtted_fraction = (double) sim_data->number_of_packets_processed /
    sim_data->arrival_count;

  printf("Xmtted Pkts  = %ld (Service Fraction = %.5f)\n",
	 sim_data->number_of_packets_processed, xmtted_fraction);

  printf("Mean Delay   = %.1f \n",
	 sim_data->accumulated_delay/sim_data->number_of_packets_processed);

  printf("System Throughput (S) = %.6f packets/Tx time\n", system_throughput);

  printf("Mean collisions per packet = %.3f\n",
	 (double) sim_data->number_of_collisions / 
	 sim_data->number_of_packets_processed);

  printf("Aggregate load G = %.6f (transmission attempts per Tx time)\n",
	 (double) sim_data->number_of_transmission_attempts / finish_time);

  if(sim_data->persistent_station_id < 0) {
    printf("\n\n");
    return;
  }

  printf("Persistent station = %d (BEB elsewhere)\n",
	 sim_data->persistent_station_id);
  printf("\nPer-station results (delay in Tx times, throughput in pkts/Tx time):\n");

  for(i=0; i<sim_data->number_of_stations; i++) {
    double stn_delay =
      (sim_data->stations+i)->accumulated_delay /
      (sim_data->stations+i)->packet_count;
    double stn_throughput =
      (double) (sim_data->stations+i)->packet_count / finish_time;

    printf("Station %2i Mean Delay = %8.1f  Throughput = %.6f%s\n", i,
	   stn_delay, stn_throughput,
	   (i == sim_data->persistent_station_id) ? "  [persistent]" : "");

    if(i != sim_data->persistent_station_id) {
      other_delay_sum += (sim_data->stations+i)->accumulated_delay;
      other_packet_count += (sim_data->stations+i)->packet_count;
    }
  }

  if(other_packet_count > 0) {
    int other_stations = sim_data->number_of_stations - 1;
    double other_mean_delay = other_delay_sum / other_packet_count;
    double other_mean_throughput =
      (double) other_packet_count / other_stations / finish_time;
    double persist_delay =
      (sim_data->stations+sim_data->persistent_station_id)->accumulated_delay /
      (sim_data->stations+sim_data->persistent_station_id)->packet_count;
    double persist_throughput =
      (double) (sim_data->stations+sim_data->persistent_station_id)->packet_count /
      finish_time;

    printf("\nOther stations average: Mean Delay = %.1f  Throughput = %.6f\n",
	   other_mean_delay, other_mean_throughput);
    printf("Persistent vs others — delay ratio = %.3f  throughput ratio = %.3f\n",
	   persist_delay / other_mean_delay,
	   persist_throughput / other_mean_throughput);
  }
  printf("\n\n");
}



