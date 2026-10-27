CC ?= gcc
CFLAGS ?= -O2 -Wall -Wextra
LDLIBS = -lm

SRCS = main.c sim_run.c channel.c cleanup.c output.c packet_arrival.c \
       packet_duration.c packet_transmission.c simlib.c
OBJS = $(SRCS:.c=.o)

all: aloha

aloha: $(OBJS)
	$(CC) $(CFLAGS) -o $@ $(OBJS) $(LDLIBS)

clean:
	rm -f aloha $(OBJS)

.PHONY: all clean
