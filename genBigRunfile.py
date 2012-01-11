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
import math
import sys

def calcCoord(xblock,yblock,n=None):
    if n is None:
        x0 = 200
        y0 = 200
    else:
        x0 = 20 + ((n - 1) % 10) * 40
        y0 = 20 + (9 - math.floor( (n-1)/10.0)) * 40

    X = x0 + (xblock - 1) * 450
    Y = y0 + (yblock - 1) * 450 

    return (X,Y)

def name2coord(name):
   m = re.match('(\d+)_(\d+)-(\d+)center.dc2', name)
   if not m:
       m = re.match('(\d+)_(\d+)big.dc2',name)
   c0 = map(int, m.groups())
   return calcCoord(*c0)

mydefaultsPattern = {}
mydefaultsAlign = {}

defaultsBiggerPattern = {}
defaultsBiggerAlign = {}

defaultsHugePattern = {}
defaultsHugeAlign = {}

mydefaultsPattern[-1] = rf6tools.defaultspec(
                         's',0,0,355,350,248.50,497.001,323.05,1.30,1)

mydefaultsPattern[12] = rf6tools.defaultspec(
                        #'w',0,0,5893,2000,217.438, 217.438,
                        'w',0,0,5893,2000,152.206,152.206,
                        104.25,450.00,0)

 
mydefaultsAlign[-1] = rf6tools.defaultspec('s',0,0,355,350,248.50,248.50,
                                            323,1.30,1)

mydefaultsAlign[5] = rf6tools.defaultspec('p',0,0,5132,2000,2000.4,2000.4,
                                           3,0.00001,1)
mydefaultsAlign[6] = rf6tools.defaultspec('w',0,0,5132,2000,2000.4,2000.4,
                                           3,0.00001,1)
mydefaultsAlign[7] = rf6tools.defaultspec('w',0,0,5132,2000,2000.4,2000.4,
                                           3,0.00001,1)
mydefaultsAlign[8] = rf6tools.defaultspec('w',0,0,5132,2000,2000.4,2000.4,
                                           3,0.00001,1)

defaultsBiggerAlign[-1] = rf6tools.defaultspec('s',0,0,355,350,248.50,248.50,
                                            323,1.30,1)
defaultsBiggerAlign[5] = rf6tools.defaultspec('p',0,0,5132,1200,1993.2,1993.2,
                                           3,0.00001,1)
defaultsBiggerAlign[6] = rf6tools.defaultspec('w',0,0,5132,1200,1993.2,1993.2,
                                           3,0.00001,1)
defaultsBiggerAlign[7] = rf6tools.defaultspec('w',0,0,5132,1200,1993.2,1993.2,
                                           3,0.00001,1)
defaultsBiggerAlign[8] = rf6tools.defaultspec('w',0,0,5132,1200,1993.2,1993.2,
                                           3,0.00001,1)

defaultsBiggerPattern[-1] = rf6tools.defaultspec(
                         's',0,0,355,350,248.50,497.001,323.05,1.30,1)
defaultsBiggerPattern[11] = rf6tools.defaultspec('w',0,0,1500,1200,145.0,145.0,
                        94.56,450.00,0)

defaultsHugePattern[-1] = rf6tools.defaultspec(
                         's',0,0,355,350,248.50,497.001,323.05,1.30,1)
defaultsHugePattern[14] = rf6tools.defaultspec('w', 0,0,486,300,546.57,546.57,
                                               1344.300,450.000,0)
defaultsHugePattern[18] = rf6tools.defaultspec('w', 0,0,486,300,546.57,546.57,
                                               1344.300,450.000,0)

defaultsHugeAlign[-1] = rf6tools.defaultspec(
                         's',0,0,355,300,248.50,497.001,323.05,1.30,1)
defaultsHugeAlign[1] = rf6tools.defaultspec('p',0,0,339,300,4044.62,4044.62,
                                           6,0.00001,1)
defaultsHugeAlign[2] = rf6tools.defaultspec('w',0,0,339,300,4044.62,4044.62,
                                           6,0.00001,1)
defaultsHugeAlign[3] = rf6tools.defaultspec('w',0,0,339,300,4044.62,4044.62,
                                           6,0.00001,1)
def main():
    if len(sys.argv) != 3:
        print "usage: %s filelist outfile" % sys.argv[0]
        return
    filelistname = sys.argv[1]
    outfilename = sys.argv[2]
    commands = ""
    patterndata = ""
    flist = open(filelistname)
    count = 0
    cpos = (0,0)
    for line in flist:
        lastpos = cpos
        name = line.rstrip()
        sname = name[:-4]

        cpos = name2coord(name)
        deltapos = map(lambda x,y: x-y, cpos, lastpos)

        commands += rf6tools.moveOnlyString(*deltapos)
        commands += '%s AL\r\n1\r\n0,0\r\n' % sname
        commands += '%s\r\n1\r\n0,0\r\n' % sname

        if '12_1-100' in sname:
            alayers = rf6tools.dc2parse(name,defaultsBiggerAlign)
            players = rf6tools.dc2parse(name,defaultsBiggerPattern)
        elif 'big' in sname: 
            alayers = rf6tools.dc2parse(name,defaultsHugeAlign)
            players = rf6tools.dc2parse(name,defaultsHugePattern)
        else:
            alayers = rf6tools.dc2parse(name,mydefaultsAlign)
            players = rf6tools.dc2parse(name,mydefaultsPattern)

        if (5 not in alayers.keys()) and (1 not in alayers.keys()):
            noAstart = True
            for lnum in (6,7,8):
                if lnum in alayers.keys():
                    alayers[lnum].use = 'p'
                    noAstart = False
                    break
            if noAstart:
                print "!Pattern %s doesn't start alignment, NPGS is gonna be mad!" % sname

        patterndata += rf6tools.genPatternData(alayers)
        patterndata += rf6tools.genPatternData(players)

        count = count + 3

    head = rf6tools.rf6headerstring + ("%d\r\n" % count)
    g = open(outfilename, 'w')
    g.write(head + commands + patterndata)

if __name__ == "__main__":
    main()
