#include "main.h"
#include "cleanup_memory.h"

static void clean_server(Server_Ptr link)
{
  if (server_state(link) == BUSY)
    xfree(server_get(link));
  xfree(link);
}

static void clean_queue(Fifoqueue_Ptr buffer)
{
  while (fifoqueue_size(buffer) > 0)
    xfree(fifoqueue_get(buffer));
  xfree(buffer);
}

void cleanup_memory(Simulation_Run_Ptr simulation_run)
{
  Simulation_Run_Data_Ptr data;
  data = (Simulation_Run_Data_Ptr)simulation_run_data(simulation_run);

  clean_server(data->link1);
  clean_server(data->link2);
  clean_server(data->link3);
  clean_queue(data->buffer1);
  clean_queue(data->buffer2);
  clean_queue(data->buffer3);
  simulation_run_free_memory(simulation_run);
}
