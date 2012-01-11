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

#import pdb
from numpy import *
from copy import *
import re

AREA=0
LINE=1
POINT=2

rf6headerstring = "yx01,0100nnny0200,1xy\r\n"

class defaultspec(object):
    def __init__(self,use,offsetx,offsety,maxmag,mag,c2c,l2l,
                 dwell,dose, dosetype):
        self.layer = (use,(offsetx,offsety),maxmag,mag,c2c,l2l)
        self.color = (dwell,dose, dosetype)

class layerspec(object):
    def __init__(self, layernumber=-1, use='s', 
                 offset=(0,0), maxmag=1, mag=1, 
                 c2c=100, l2l=100, lcolors=None):
        self.layernumber = layernumber
        self.use = use
        self.offset = offset
        self.maxmag = maxmag
        self.mag = mag
        self.c2c = c2c
        self.l2l = l2l
        if lcolors is None:
            self.colorlist = {}
        else:
            self.colorlist = lcolors
        self.configparameter = 1
        self.current = 10.0

    def specstring(self):
        s = ("lev %d %s    %d,%d    %d    %d    %.10g    %.10g    %d    %.1f\r\n" %
             ((self.layernumber, self.use)+ self.offset+ (self.maxmag, self.mag,
             self.c2c, self.l2l, self.configparameter, self.current)) )
        return s

class colorspec(object):
    def __init__(self, colornumber=-1, rgb=(0,0,0), dwell=0, dose=0, dosetype=AREA):
        self.colornumber = colornumber
        self.rgb = rgb
        self.dwell = dwell
        self.dose = dose
        self.dosetype = dosetype

    def specstring(self, colornum=1):
        t = (self.colornumber,) + self.rgb + (self.dwell, self.dose, self.dosetype)
        #print t
        s = ("col -%03d %03d %03d %03d %.3f %.2f %d\r\n" % t)
        return s

def moveOnlyString(x,y):
     s = 'MoveOnly M\r\n%d,%d\r\n' % (x,y)
     return s

        
# need to:
    # find each layer and the colors used on each layer
def dc2parse(rf6fileName,defaults={}):
    dcf = open(rf6fileName)
    dcfdat = dcf.read()
    lines = dcfdat.split('\r\n')

    currentlayer = -1
    layers = {}

    currentcolors = {}

    for line in lines:
        fields = line.split()
        if len(fields) == 6 and fields[0] == '21':
            currentlayer = int(fields[1])
            #print currentlayer
            if currentlayer not in layers.keys():
                if currentlayer in defaults.keys():
                    layers[currentlayer] = layerspec(
                            currentlayer, *(defaults[currentlayer].layer))
                elif -1 in defaults.keys():
                    layers[currentlayer] = layerspec(
                            currentlayer, *(defaults[-1].layer))
                else:
                    layers[currentlayer] = layerspec(currentlayer)
                #foo = layerspec(currentlayer)
            clspec = layers[currentlayer]
            #layers[currentlayer].colorlist[currentlayer] = (currentlayer)
            #print currentlayer
            #print foo
            
        if currentlayer == -1:
            continue # don't have much to do until we find a layer

        # this is an entity
        if len(fields) in [12,14]:
            color = tuple(map(int, fields[9:12]))
            if color not in clspec.colorlist.keys():
                if currentlayer in defaults.keys():
                    d = (len(clspec.colorlist) + 1,color)+ (defaults[currentlayer].color)
                    clspec.colorlist[color] = colorspec(*d)
                elif -1 in defaults.keys():
                    d = (len(clspec.colorlist) + 1,color)+ (defaults[-1].color)
                    clspec.colorlist[color] = colorspec(*d)
                else:
                    clspec.colorlist[color] = colorspec(
                        len(clspec.colorlist)+1,color)

    return layers

def genPatternData(ldict):
    pd = ""
    lkeys = sorted( ldict.keys() )
    for k in lkeys:
        if k > 19:
            continue
        l = ldict[k]
        pd += l.specstring()
        ckeys = sorted(l.colorlist.keys(),key=lambda x: l.colorlist[x].colornumber)
        for ck in ckeys:
            c = l.colorlist[ck]
            pd += c.specstring()

    pd += "*\r\n"
    return pd


class segment(object):

    ### start and end should be array-like ###
    def __init__(self, start, end):
        self.start = array(start)
        self.end = array(end)

    def __str__(self):
        return "(%s --> %s)" % (str(self.start.transpose()), str(self.end.transpose()))

    def length(self):
        return  linalg.norm(self.end-self.start)

    @classmethod
    def xtest(cls, a, b):
        return cls._xtest0(a,b) and cls._xtest0(b,a)
    
    @classmethod
    def _xtest0(cls, a, b):
        r1 = a.end - a.start
        r2a = b.end - a.end
        r2b = b.start - a.end
        
        x1 = cross(r1[:,0], r2a[:,0])
        x2 = cross(r1[:,0], r2b[:,0])

        if(shape(x1) == ()):
            return sign(x1) != sign(x2)
        else: 
            return (sign(x1[2]) != sign(x2[2]))

    def top(self):
        return max(self.start[1],self.end[1])

    def bottom(self):
        return min(self.start[1],self.end[1])

    def right(self):
        return max(self.start[0],self.end[0])

    def left(self):
        return min(self.start[0],self.end[0])

""" take a list of strings of x y z and turns into segments """
def plist2seglist(plist):
    if len(plist) < 2:
        return None
    alist = map(lambda x: array(map(lambda y: [float(y)],x.split())), plist)

    slist = [s for s in map(segment, alist[0:-1], alist[1:]) if s.length() > 0]

    return slist

    
""" takes a dc2 file that's been read into a list of lines and returns a 
list of tuples of the form (linenumber, linestring,[list of segments])"""
def getsegs(dat):
    if len(dat[1]) == 1:
        lines = dat.split('\r\n')
    else:
        lines = dat

    entitylines =  [(i,l) for i,l in enumerate(lines) if len(l) > 0 and l.split()[0] == '1']

    seglist = []
    for (i,l) in entitylines:
        if not (len(l.split()) == 14 or len(l.split()) == 12) :
            #14 is our magic length 
            # or 12 ... ?
            continue
        
        #print (i,l)
        c = int(l.split()[1])
        if c > 0:
            segs = plist2seglist(lines[i + 1: i + 1 + c])
            seglist += [(i,l, segs)]

    return seglist


def findSegIntersect(s1, s2):
    r1 = (s1.end - s1.start)[0:2]
    r2 = (s2.end - s2.start)[0:2]

    # (r2 -r1) * (m n) = (a b)
    A = append(r2, -r1, 1)

    b = (s1.start - s2.start)[0:2]

    fs = linalg.solve(A,b)

    if max(fs) > 1+1e-8 or min(fs) < -1e-8:
        #print "segments don't really intersect fs: ", fs
        #print fs[3]
        return False

    return s1.start[0:2] + fs[1]*r1

""" takes a tuple of (line#, linespec, seglist) and returns a list of text
lines to go in a dc2 file - also ensures that linespec's field[1] is correct
for the number of segments"""
def segtuple2lines(st):
    (linenumber, linespec, seglist) = st
    s = []

    if len(seglist) < 1:
        return s

    for seg in seglist:
        s += ["%.10g %.10g 0" % (seg.start[0], seg.start[1])]

    seg = seglist[-1]
    s += ["%.10g %.10g 0" % (seg.end[0], seg.end[1])]

    fields = linespec.split()
    fields[1] = str(len(s))

    s0 = reduce(lambda x,y: x + " " + y, fields)
    
    return [s0] + s

def findIntersections(seglist):
    c = len(seglist)
    
    its = []
    for i in range(0,c):
        a = seglist[i]
        # search backwards to make life easier
        for j in reversed(range(i + 2, c)):
            b = seglist[j]
            if segment.xtest(a,b):
                if i == 0 and j == len(seglist)-1 and all(a.start == b.end):
                    continue
                its += [(i,j)]
    return its

def findFirstIntersection(seglist):
    c = len(seglist)
    
    it = ()
    for i in range(0,c):
        a = seglist[i]
        # search backwards to make life easier
        for j in reversed(range(i + 2, c)):
            b = seglist[j]
            if segment.xtest(a,b):
                if i == 0 and j == len(seglist)-1 and all(a.start == b.end):
                    continue
                #if i==0:
                    #print a,b
                return (i,j)
    return it

def makeDC2(lines, seglist):
    cpos = 0
    nls = []
    nsegl = []

    for s in seglist:
        i = s[0]
        nls += lines[cpos:i]

        r = breakupselfxs(s)
        nsegl += r
        for s1 in r:
            nls += segtuple2lines(s1)

        fakelength = int(s[1].split()[1])

        cpos = i + fakelength + 1

    return (nls, nsegl)

""" takes a segment tuple and then breaks it up based on a list of intersecting
pairs ... doesn't need the list anymore - returns a list of segtuples """
def breakupselfxs(segtuple):
    (lnum, linespec, segs) = segtuple

    if len(segs) == 0:
        return []
    
    xs = findFirstIntersection(segs)


    if len(xs) == 0:# or len(segs) < 28:
        return [segtuple] # nothing to do

    (i,j) = xs
    ni = findSegIntersect(segs[i],segs[j])

    if ni is False:
        #print "oh crap, I hoped this wouldn't happen"
        #print (i,j)
        #print segs[i], segs[j], len(segs)
        return [segtuple]
    
    #print "xs: ", xs

    head = deepcopy(segs[:i+1])
    body = deepcopy(segs[i:j+1])
    tail = deepcopy(segs[j:])
    
    #pdb.set_trace()


    head[-1].end[0:2] = ni[0:2]
    tail[0].start[0:2] = ni[0:2]

    if head[-1].length() < 1e-6:
        head = head[:-1]

    if tail[0].length() < 1e-6:
        tail = tail[1:]

    body[0].start[0:2] = ni[0:2]
    body[-1].end[0:2] = ni[0:2]

    if body[0].length() < 1e-6:
        body = body[1:]

    if body[-1].length() < 1e-6:
        body = body[:-1]

    #if len(head) == 0:
        #head = body
        #body = []

    bodytuple = (lnum, linespec, body)
    tailtuple = (lnum, linespec, tail)

    bt = breakupselfxs(bodytuple)
    tt = breakupselfxs(tailtuple)

    sts = [(lnum, linespec, head)] + bt + tt

    return sts

def lines2file(filename, lines):
    f = open(filename, 'w')

    for l in lines:
        f.write(l)
        f.write('\r\n')

    f.close()

# uncomment this to use rftools.qplot to plot some segments
# (useful for debugging)
#from pylab import *
def qplot(stl, *oa):
    for st in stl:
        for s in st[2]:
            plot((s.start[0],s.end[0]),(s.start[1],s.end[1]),*oa)


def recolorDC2dat(layerList, infiledata):
    outfiledata = []
    currentlayer = -1
    rgblist = ["255", "255", "255"]

    c = 0
    for line in infiledata:
        #print line.rstrip()
        c = c + 1
        fields = line.rstrip().split()

        if len(fields) == 6 and fields[0] == "21":
            #print line.rstrip()
            currentlayerString = fields[1]
            #print "layer is now: " + currentlayerString
            currentlayer = int(currentlayerString)
            if currentlayer not in layerList.keys():
                if 0 in layerList.keys():
                    #print "substituting color 0"
                    currentlayer = 0
                else:
                    #print "not going to change layer " + currentlayer
                    currentlayer = -1

            if currentlayer != -1:
                cld = layerList[currentlayer]
                rgblist = map(str, [cld['R'], cld['G'], cld['B']])

                #print ["rgblist",  rgblist]

        if len(fields) in [12,14] and currentlayer != -1:
            #print line.rstrip()
           
            fixedline = reduce(lambda x,y: x + " " + y,
                               fields[0:9] + rgblist + fields[12:]) + '\r\n'
            #print fixedline.rstrip()
        else:
            fixedline = line
        
        outfiledata += [fixedline]

    return outfiledata

def parseColorListFile(colorListFileName):
    clf = open(colorListFileName)

        

    ps = r"^(?:[0-9]+\s+){3}[0-9]+$"

    layerList = {}

    for line in clf:
        if not re.match(ps, line):
            continue
        (layer, r, g, b) = map(int, line.split())

        layerList[layer] = {'R': r, 'G': g, 'B': b}

    return layerList

def fixupDC2file(layerList, infilename, outfilename):
    infile = open(infilename)
    dat = infile.read()

    lines = dat.split('\r\n')

    rclines = recolorDC2dat(layerList, lines)
    segs = getsegs(rclines)

    (nls, nsegs) = makeDC2(rclines, segs)

    lines2file(outfilename, nls)

