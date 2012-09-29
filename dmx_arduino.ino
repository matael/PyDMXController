/*
 *   File: dmx_arduino.ino
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

#define MIN 0x40
#define MAX 0xFF
#define DELAY 100
/*#define MIN 0x35*/
/*#define MAX 0x89*/


void setup()
{
	int colors[6] = {0xFF, 0, 0, 0, 0, 0};
	/*int colors[6] = {0x09, 0, 0xFF, 0, 0, 0};*/
	int i;
	for (i = 0; i < 6; i++) {
		DmxSimple.write(i+1, colors[i]);
	}
}



void loop()
{
	/*
 	int colors[3][6] = {
		{0xFF, 0x35, 0, 0, 0, 0},
		{0xFF, 0x67, 0, 0, 0, 0},
		{0xFF, 0x89, 0, 0, 0, 0}
	};

	int i, j;
	for (i = 0; i < 3; i++) {
		for (j = 0; j < 6; j++) {
			DmxSimple.write(j+1, colors[i][j]);
		}
		delay(500);
	}
	*/
	int i = MIN;
	while (i < MAX) {
		DmxSimple.write(2, i);
		i++;
		delay(DELAY);
	}
	while (i > MIN) {
		DmxSimple.write(2, i);
		i--;
		delay(DELAY);
	}
}
