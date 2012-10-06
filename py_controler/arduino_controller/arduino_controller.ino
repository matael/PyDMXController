/*
 *   File: arduino_controller.ino
 *   Author : Mathieu (matael) Gaborit
 *   Year : 2012
 *   Licence : WTFPL
 *   Licence Terms :
 *
 *           DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
 *                   Version 2, December 2004
 *
 *   Copyright (C) 2004 Sam Hocevar <sam@hocevar.net>
 *
 *   Everyone is permitted to copy and distribute verbatim or modified
 *   copies of this license document, and changing it is allowed as long
 *   as the name is changed.
 *
 *           DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
 *   TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION
 *
 *   0. You just DO WHAT THE FUCK YOU WANT TO.
 *
 *   This program is free software. It comes without any warranty, to
 *   the extent permitted by applicable law. You can redistribute it
 *   and/or modify it under the terms of the Do What The Fuck You Want
 *   To Public License, Version 2, as published by Sam Hocevar. See
 *   http://sam.zoy.org/wtfpl/COPYING for more details.
 *
 */

#include <DmxSimple.h>
#define CHAN_RED 1
#define CHAN_GREEN CHAN_RED+1
#define CHAN_BLUE CHAN_RED+2

void setup()
{
	int i;

	// first, be sure all 6 channels are set to 0x00
	for (i=1; i<3; i++) {
		DmxSimple.write(i, 0x00);
	}

	// initialize Serial connection
	Serial.begin(9600);
}

byte r, g, b;

void loop()
{
	if (Serial.available() >= 3) {
		DmxSimple.write(CHAN_RED, Serial.read());
		DmxSimple.write(CHAN_GREEN, Serial.read());
		DmxSimple.write(CHAN_BLUE, Serial.read());
	}
	delay(2);
}
