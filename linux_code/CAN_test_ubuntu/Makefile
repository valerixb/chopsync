LIBS = -lm
CFLAGS = -g0 -Wall
LDFLAGS = -Wall
TARGETS = MECOS_hz_setpoint_write MECOS_hz_setpoint_read MECOS_hz_actual_read prova_txbuf

all: $(TARGETS)
default: all

%.o: %.c
	gcc $(CFLAGS) -c $< -o $@

$(TARGETS): %: %.o
	gcc $^ $(LDFLAGS) $(LIBS) -o $@
	rm $^

clean:
	-rm -f *.o
	-rm -f $(TARGETS)
