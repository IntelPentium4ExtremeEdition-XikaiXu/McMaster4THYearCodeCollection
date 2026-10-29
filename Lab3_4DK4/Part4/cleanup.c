
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

#include <malloc.h>
#include "simlib.h"
#include "main.h"
#include "simparameters.h"
#include "cleanup.h"

/*******************************************************************************/

void
cleanup (Simulation_Run_Ptr simulation_run)
{
  Simulation_Run_Data_Ptr data;
  int i;

  data = (Simulation_Run_Data_Ptr) simulation_run_data(simulation_run);

  /* Clean out the stations. */
  for(i=0; i<data->number_of_stations; i++) {
    Buffer_Ptr buffer;

    buffer = (data->stations+i)->buffer;
    while (fifoqueue_size(buffer) > 0) {
      xfree(fifoqueue_get(buffer));
    }
    xfree(buffer);
  }
  xfree(data->stations);

  /* Clean out the channel. */
  xfree(data->channel);

  /* Clean up the simulation_run. */
  simulation_run_free_memory(simulation_run);

  /* Return the freed heap pages to the OS before the next run. */
  malloc_trim(0);
}



