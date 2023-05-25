# Recipe lines (for example 'rm -f...' below) MUST begin with a tab
# character.  See https://www.gnu.org/software/make/manual/html_node/Rule-Introduction.html

CC = gcc
CFLAGS += -g -Wall

all: gosh

clean:
	rm -f gosh

gosh: gosh.c
	$(CC) $(CFLAGS) -o gosh gosh.c
