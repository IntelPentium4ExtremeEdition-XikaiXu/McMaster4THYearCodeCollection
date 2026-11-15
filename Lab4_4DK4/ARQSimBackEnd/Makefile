CC = gcc
CFLAGS = -O2 -Wall -Wextra -std=c11

.PHONY: all clean

all: arq_sim

arq_sim: ARQBackEnd.c
	$(CC) $(CFLAGS) -o arq_sim ARQBackEnd.c

clean:
	rm -f arq_sim
