NAME=$(shell pwd | tr '/' '\n' | tail -n 1)
all:
	scons

upload:
	avrdude -F -V -c arduino -p m328p -P /dev/ttyACM0 -U flash:w:$(NAME).hex

clean:
	rm -rf build/ *.hex *.elf

