CC = gcc
CFLAGS = -O2 -Wall -Wextra -std=c11

.PHONY: all clean

all: src/cross_layer

src/cross_layer: src/cross_layer.c
	$(CC) $(CFLAGS) -o src/cross_layer src/cross_layer.c

clean:
	rm -f src/cross_layer
