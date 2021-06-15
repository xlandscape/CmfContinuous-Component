# -*- coding: utf-8 -*-
"""
Created on Tue Apr 24 07:53:53 2018

@author: smh
"""
from LandscapeModel.pySteps.Structs import SubstanceApplication

import shapefile as shp
from simplekml import (Kml, OverlayXY, ScreenXY, Units, RotationXY,
                       AltitudeMode, Camera)

import numpy.ma as ma
from netCDF4 import Dataset, date2index, num2date
#from mpl_toolkits.basemap import Basemap

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import pandas as pd
from datetime import datetime

def plotshape():
    sf = shp.Reader(r"c:\0_work\bcs_catchmentmodelling\BEL_pome\GIS\pome2.shp")
    records = []
    shapes = []
    for i,j in zip(sf.records(),sf.shapeRecords()):
        records.append(i)
        shapes.append(j)
    
    
    fig, ax = gearth_fig(llcrnrlon=sf.bbox[0],
                         llcrnrlat=sf.bbox[1],
                         urcrnrlon=sf.bbox[2],
                         urcrnrlat=sf.bbox[3],
                         pixels=2048)
    
     
    
    for rec,shape in zip(records,shapes):
        xy = [[i[0],i[1]] for i in shape.shape.points]
        ax.fill([i[0] for i in xy], [i[1] for i in xy], lw=0.2, edgecolor='white',color="magenta",alpha=.5)
        
    ax.set_axis_off()    
    fig.savefig('landuse.png', transparent=True, format='png')  # Change transparent to True if your colorbar is not on space :)


def plotLine(ax,x1,x2,y1,y2,color="b",alpha=1,width=5): 
#    xs = [x1+width,x2+width,x2-width,x1-width]
#    ys = [y1,y2,y2,y1]
#    zs = [z1,z2,z2,z1] 
#    plotPoly(ax,xs,ys,zs,color=color,alpha=alpha)
    ax.plot([x1,x2],[y1,y2],alpha=alpha,linewidth=width,color=color)


   
def make_kml(fpath,llcrnrlon, llcrnrlat, urcrnrlon, urcrnrlat,
             figs,times, colorbar=None, **kw):
    """TODO: LatLon bbox, list of figs, optional colorbar figure,
    and several simplekml kw..."""

    kml = Kml()
    altitude = kw.pop('altitude', 2e4)
    roll = kw.pop('roll', 0)
    tilt = kw.pop('tilt', 0)
    altitudemode = kw.pop('altitudemode', AltitudeMode.relativetoground)
    camera = Camera(latitude=np.mean([urcrnrlat, llcrnrlat]),
                    longitude=np.mean([urcrnrlon, llcrnrlon]),
                    altitude=altitude, roll=roll, tilt=tilt,
                    altitudemode=altitudemode)

    kml.document.camera = camera
    draworder = 0
    for fig,time in zip(figs,times):  # NOTE: Overlays are limited to the same bbox.
        draworder += 1
        ground = kml.newgroundoverlay(name='GroundOverlay')
        ground.draworder = draworder
        ground.visibility = kw.pop('visibility', 1)
        ground.name = kw.pop('name', 'overlay')
        ground.color = kw.pop('color', '9effffff')
        ground.atomauthor = kw.pop('author', 'ocefpaf')
        ground.latlonbox.rotation = kw.pop('rotation', 0)
        ground.description = kw.pop('description', 'Matplotlib figure')
        ground.gxaltitudemode = kw.pop('gxaltitudemode',
                                       'clampToSeaFloor')
        ground.icon.href = fig
        ground.latlonbox.east = llcrnrlon
        ground.latlonbox.south = llcrnrlat
        ground.latlonbox.north = urcrnrlat
        ground.latlonbox.west = urcrnrlon
               
        ground.timespan.begin = time[0]#"2004-01-01" '2007-01-01T10:00+02:00'#  
        ground.timespan.end = time[1]#"2004-01-31"

    if colorbar:  # Options for colorbar are hard-coded (to avoid a big mess).
        screen = kml.newscreenoverlay(name='ScreenOverlay')
        screen.icon.href = colorbar
        screen.overlayxy = OverlayXY(x=0, y=0,
                                     xunits=Units.fraction,
                                     yunits=Units.fraction)
        screen.screenxy = ScreenXY(x=0.015, y=0.075,
                                   xunits=Units.fraction,
                                   yunits=Units.fraction)
        screen.rotationXY = RotationXY(x=0.5, y=0.5,
                                       xunits=Units.fraction,
                                       yunits=Units.fraction)
        screen.size.x = 0
        screen.size.y = 0
        screen.size.xunits = Units.fraction
        screen.size.yunits = Units.fraction
        screen.visibility = 1

    kmzfile = kw.pop('kmzfile', fpath+ 'overlay.kmz')
    kml.savekmz(kmzfile)

def gearth_fig(llcrnrlon, llcrnrlat, urcrnrlon, urcrnrlat, pixels=1024):
    """Return a Matplotlib `fig` and `ax` handles for a Google-Earth Image."""
    aspect = np.cos(np.mean([llcrnrlat, urcrnrlat]) * np.pi/180.0)
    xsize = np.ptp([urcrnrlon, llcrnrlon]) * aspect
    ysize = np.ptp([urcrnrlat, llcrnrlat])
    aspect = ysize / xsize

    if aspect > 1.0:
        figsize = (10.0 / aspect, 10.0)
    else:
        figsize = (10.0, 10.0 * aspect)

    if False:
        plt.ioff()  # Make `True` to prevent the KML components from poping-up.
    fig = plt.figure(figsize=figsize,
                     frameon=False,
                     dpi=pixels//10)
    # KML friendly image.  If using basemap try: `fix_aspect=False`.
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(llcrnrlon, urcrnrlon)
    ax.set_ylim(llcrnrlat, urcrnrlat)
    return fig, ax

def plotRiver(fpath,i,river):
    llcrnrlon = river.lon.min()
    llcrnrlat = river.lat.min()
    urcrnrlon = river.lon.max()
    urcrnrlat = river.lat.max()
    fig, ax = gearth_fig(llcrnrlon=llcrnrlon,
                         llcrnrlat=llcrnrlat,
                         urcrnrlon=urcrnrlon,
                         urcrnrlat=urcrnrlat,
                         pixels=2048)
    pc=ax.scatter(river.lon,river.lat,edgecolor="None",c=river.z*np.random.uniform(0,1),s=10,cmap=plt.cm.jet,vmin=0,vmax=50)
    ax.set_axis_off()
    fig.savefig(fpath+'river'+str(i)+'.png', transparent=True, format='png')
    return fpath+'river'+str(i)+'.png'

def plot_conc(fpath,results,t):
    # get concentration at current time for al lreaches
    conc = results[results.index==t]

    # create geart-figure
    fig, ax = gearth_fig(llcrnrlon=llcrnrlon,
                             llcrnrlat=llcrnrlat,
                             urcrnrlon=urcrnrlon,
                             urcrnrlat=urcrnrlat,
                             pixels=2048)
    
    # create colormap
    norm = matplotlib.colors.LogNorm(vmin=results.PEC_SW[results.PEC_SW!=0].quantile(0.05), vmax=results.PEC_SW[results.PEC_SW!=0].quantile(0.95))
    cmap = matplotlib.cm.get_cmap('autumn_r')
    for i in range(len(reaches)):
        # get current reach
        reach = reaches.iloc[i]
        x1 = reach["lon"] 
        y1 = reach["lat"] 
        if reach["downstream"]!="Outlet":
            next_reach = reaches[reaches["name"]==reach["downstream"]]
            x2 = next_reach["lon"] 
            y2 = next_reach["lat"]          
            value  = conc["conc"][conc["name"]==reach["name"]].values[0]
            if value>0:
                plotLine(ax,x1,x2,y1,y2,color=cmap(norm(value)),alpha=1,width=5)
            else:
                plotLine(ax,x1,x2,y1,y2,color="lightblue",alpha=1,width=5)
    # save figure for each timestep
    ax.set_axis_off()
    plt.close("all")
    path = fpath+'conc_'+str(t.dayofyear) + "_" + str(t.hour) +'h.png'
    fig.savefig(path, transparent=True, format='png')
    del fig
    return path


fpath = "c:/0_work/bcs_catchmentmodelling/BEL_pome/BEL_pome_modelruns/MelsterbeekField1/"


# reach reaches geometries
reaches = pd.read_csv(fpath + "/Reaches.csv")

# get bounding box
llcrnrlon = reaches.lon.min()
llcrnrlat = reaches.lat.min()
urcrnrlon = reaches.lon.max()
urcrnrlat = reaches.lat.max()
    
# read PEC results
results = pd.read_csv(fpath + "/MelsterbeekField1_reaches.csv")
results["time"] = pd.to_datetime(results["time"])
results.set_index("time",inplace = True)

# create timeperiod to plot
begin = [pd.Timestamp(i) for i in pd.date_range("2007-05-02 06:00","2007-05-3 06:00",freq="H")]
end =  [pd.Timestamp(i) for i in pd.date_range("2007-05-02 07:00","2007-05-3 07:00",freq="H")]

# create plots and timestamps
figs = [plot_conc(fpath,results,t) for t in begin]
times = [[b.strftime("%Y-%m-%dT%H:00+02:00"),e.strftime("%Y-%m-%dT%H:00+02:00")] for b,e in  zip(begin,end)]

# create kml files    
make_kml(fpath,llcrnrlon, llcrnrlat, urcrnrlon, urcrnrlat,figs,times, colorbar=None,)


# plot applications
AppRates=[SubstanceApplication("CMP_A",reach, datetime(i,5,2,10),0.2698) for i in range(2006,2019,1) for reach in ["r277","r279","r280","r281","r282","r276","r139"]]# 259 ug/m² = 0.2698mg/m²









## create colormap
#fig = plt.figure(figsize=(5, 8.0), facecolor="w", frameon=True)
#ax = fig.add_axes([0.8, 0.08, 0.1, 0.2])
#pc=ax.scatter([],[],edgecolor="None",c=[],s=10,cmap=plt.cm.jet,vmin=0,vmax=50)
#cb = fig.colorbar(pc, cax=ax,vmin=0,vmax=50)
#cb.set_ticks(range(40,100,5))
#cb.set_label('Elevation [m]', rotation=-90, color='w', labelpad=20)
#fig.savefig(fpath+'legend.png', transparent=True, format='png')  # Change transparent to True if your colorbar is not on space :)


# 
#    
##    
    
    

    
    
    
    
    
    