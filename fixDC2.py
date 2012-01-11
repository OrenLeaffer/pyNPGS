#! /usr/bin/python 
""" fixDC2.py: depends on rf6 tools --- fixes colors in a DC2 file to be a
    single color to each layer as specified in colorlist and also breaks up 
    self-intersecting lines into multiple pieces ... this is mostly critical 
    for making the number 8 work in alignment files """

__author__ = 'Oren Leaffer'
__email__ = 'oren.leaffer@gmail.com'
__date__ = 'September 2011'
__license__ = '''
pyNPGS - some scripts to manipulate NPGS files from python
Copyright (C) 2011 Oren Leaffer

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
'''
__disclaimer__ = '''
THESE MATERIALS SHOULD _NEVER_ BE LOADED ONTO A SYSTEM WHICH
IS INVOLVED, DIRECTLY OR INDIRECTLY, WITH ON-LINE CONTROL
EQUIPMENT IN HAZARDOUS ENVIRONMENTS REQUIRING FAIL-SAFE
PERFORMANCE, SUCH AS IN THE OPERATION OF NUCLEAR FACILITIES,
AIRCRAFT NAVIGATION OR COMMUNICATIONS SYSTEMS, AIR TRAFFIC
CONTROL, DIRECT LIFE SUPPORT MACHINES, FOREIGN OR
EXTRATERRESTRIAL LANGUAGE TRANSLATION, OR WEAPONS SYSTEMS, IN
WHICH THE FAILURE OF THE SYSTEM OR THESE MATERIALS COULD LEAD
TO DEATH, PERSONAL INJURY OR THE DESTRUCTION OF THE EARTH. 
'''

import rf6tools
import re
import os

import sys

def main():
    if(len(sys.argv) != 4):
        print "usage: " + sys.argv[0] + " colorlist infile.dc2 outfile.dc2"
        return 0

    (colorListFileName, infileName, outfileName) = sys.argv[1:]

    #print colorListFileName + infileName + outfileName
    layerList = rf6tools.parseColorListFile(colorListFileName)

    rf6tools.fixupDC2file(layerList, infileName, outfileName)

if __name__ == "__main__":
    main()
