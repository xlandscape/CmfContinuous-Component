# -*- coding: utf-8 -*-
"""
Created on Mon Jan 14 13:18:57 2019

@author: smh
"""

def plot_coords(ax, ob):
    x, y = ob.xy
    ax.plot(x, y, 'o', color='green', zorder=1)

def plot_line(ax, ob):
    x, y = ob.xy
    ax.plot(x, y, color="r", alpha=0.7, linewidth=3, solid_capstyle='round', zorder=2)

def make_map(line,point,buffer,intersection):
    fig = plt.figure()
    ax=fig.add_subplot(111)
    x, y = point.xy
    ax.plot(x, y, 'o', color='green', zorder=1,label="Start")
    ring_patch = PolygonPatch(buffer,color="g",alpha=.25,label="Buffer")
    ax.add_patch(ring_patch)
    x, y = line.xy
    ax.plot(x, y, color="b", alpha=0.7, linewidth=3, 
            solid_capstyle='round', zorder=2,label="Stream")
    x, y = intersection.xy
    ax.plot(x, y, 'o', color='r', zorder=1,label="Intersection")    
    xrange = [0,100]
    yrange = [0,100]
    ax.set_xlim(*xrange)
    ax.set_ylim(*yrange)
#    ax.set_yticks(list(range(*yrange)) + [yrange[-1]])
    ax.set_aspect(1)
    ax.grid(True)
    ax.legend(loc=0)


def intersect(buffer,stream):
    lring = LinearRing(list(buffer.exterior.coords))
    return (lring.intersection(stream))

import matplotlib.pylab as plt
from shapely.geometry import Point, LineString, Polygon,shape
from shapely.geometry.polygon import LinearRing
from descartes import PolygonPatch
from shapely.ops import split

stream = LineString([(10,20),(20,40),(40,50),(50,70)])
distance = 10
# list for resulting reaches
reaches = []

def split_stream(stream,outlet,distance,reaches):
    """
    """
    # create first buffer
    buffer = outlet.buffer(distance=distance)
    # get point at intersection
    intersection = intersect(buffer,stream)
    if intersection.wkt=='GEOMETRYCOLLECTION EMPTY':
        return None,None,None,None
    else:
        # split line by points
        segment,stream1 = split(stream, intersection)
        return segment,stream1,buffer,intersection
    # add segment 
    reaches.append(("r"+str(len(reaches)),segment))

#
#stream1 = stream
#last_segment=False
#while not last_segment:
#    
#    
#    stream_t0=stream1
#    x,y=stream1.xy
#    print(x[0],y[0])
#    start_point = Point((x[0],y[0]))
#    
#    # create first buffer
#    buffer = start_point.buffer(distance=distance)
#    # get point at intersection
#    intersection = intersect(buffer,stream1)
#
#    
#    
#    if not intersection.wkt=='GEOMETRYCOLLECTION EMPTY':
#        # split line by points
#        stream1 = split(stream1, intersection)
#        if len(stream1)>1:
#            print("dsfdsf")
#            stream1=stream1[1]
#        else:
#            stream1=stream1[-1]
#    
#    make_map(stream1,start_point,buffer,intersection) 
#    
#    
    
#    
##    start_point = Point((x[0],y[0]))
##    segment,stream1,buffer1,intersection1=split_stream(stream1,start_point,distance,reaches)
#    reaches.append(("r"+str(len(reaches)),segment))
#    make_map(stream_t0,start_point,buffer,intersection)
#    if segment==None:
#        last_segment=True

stream1 = stream
x,y=stream1.xy
print("##1##",x[0],y[0])
start_point1 = Point((x[0],y[0]))
segment2,stream2,buffer2,intersection2=split_stream(stream1,start_point1,distance,reaches)
#make_map(stream1,start_point1,buffer2,intersection2) 


stream1=stream2
x,y=stream2.xy
print("##2##",x[0],y[0])
start_point1 = Point((x[0],y[0]))
segment2,stream2,buffer2,intersection2=split_stream(stream2,start_point1,distance,reaches)
#make_map(stream1,start_point1,buffer2,intersection2) 

stream1 = stream2
x,y=stream1.xy
print("##3##",x[0],y[0])
start_point1 = Point((x[0],y[0]))
#segment2,stream2,buffer2,intersection2=split_stream(stream1,start_point1,distance,reaches)
# create first buffer
buffer = start_point1.buffer(distance=distance)
intersection = intersect(buffer,stream1)
stream2 = split(stream1, intersection)[0]
#stream2=stream2[0]
#make_map(stream2,start_point1,buffer,intersection2) 



stream1 = stream2
x,y=stream1.xy
print("##4##",x[0],y[0])
start_point1 = Point((x[0],y[0]))
##segment2,stream2,buffer2,intersection2=split_stream(stream1,start_point1,distance,reaches)
## create first buffer
#buffer = start_point1.buffer(distance=distance)
#intersection = intersect(buffer,stream1)
#stream2 = split(stream1, intersection)
#stream2=stream2[0]
#make_map(stream2,start_point1,buffer,intersection2) 

#
#
#stream1 = stream2
#x,y=stream1.xy
#print("##3##",x[0],y[0])
#start_point1 = Point((x[0],y[0]))
##segment2,stream2,buffer2,intersection2=split_stream(stream1,start_point1,distance,reaches)
## create first buffer
#buffer = start_point1.buffer(distance=distance)
#intersection = intersect(buffer,stream1)
#stream2 = split(stream1, intersection)
#stream2=stream2[0]
#make_map(stream2,start_point1,buffer,intersection2) 
#
#
#
#
#








