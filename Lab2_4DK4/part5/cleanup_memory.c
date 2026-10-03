#include "main.h"
#include "cleanup_memory.h"

void cleanup_memory(Simulation_Run_Ptr simulation_run)
{
  Simulation_Run_Data_Ptr data;

  data = (Simulation_Run_Data_Ptr)simulation_run_data(simulation_run);

  if (server_state(data->link) == BUSY)
    xfree(server_get(data->link));
  xfree(data->link);

  while (fifoqueue_size(data->buffer) > 0)
    xfree(fifoqueue_get(data->buffer));
  xfree(data->buffer);

  simulation_run_free_memory(simulation_run);
}
