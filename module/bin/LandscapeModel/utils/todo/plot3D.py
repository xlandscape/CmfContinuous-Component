# library
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import matplotlib 
from mpl_toolkits.axes_grid1 import make_axes_locatable
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import matplotlib.lines as mlines
import matplotlib.patches as mpatches

fontsize = 16

params = {
 'axes.labelsize': fontsize,
 'axes.titlesize':fontsize,
 'xtick.labelsize':fontsize,
 'ytick.labelsize':fontsize}
plt.rcParams.update(params)

def makeFigure(size=[0.05,0.05,0.9,0.7]):
    fig = plt.figure(figsize=(15, 10))
    ax = fig.add_axes(size,projection='3d') # x,y, lenght, height
    return ax

def makeLayout(ax,xlim,ylim,zlim):
    ax.view_init(65, 45)
    ax.set_zlim3d([zlim[0],zlim[1]])
    ax.set_xlabel("\n\nX [m]")
    ax.set_ylabel("\n\nY [m]")
    ax.set_zlabel("\nElevation [m]")
 
    
    
    ax.grid(True)
    ax.xaxis.pane.set_edgecolor('black')
    ax.yaxis.pane.set_edgecolor('black')
    ax.xaxis.pane.fill = False
    ax.yaxis.pane.fill = False
    ax.zaxis.pane.fill = False
    ax.set_xlim(xlim[0],xlim[1])   
    ax.set_ylim(ylim[0],ylim[1])   
    ax.set_zlim(zlim[0],zlim[1]) 
    
    ax.set_xticks(range(xlim[0],xlim[1],500))   
    
    ################################################################################
    #plot colorbar
    ax = fig.add_axes([0.825,0.2,0.1,0.5]) # x,y, lenght, height
    ax.axis("off")
    #create colorbar
    divider = make_axes_locatable(ax)
    cax = divider.append_axes('right', size='20%', pad=0.05)
    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm._A = []
    sm
    cb=fig.colorbar(sm,cax=cax, orientation='vertical')
    cb.set_label("PEC$_{sw}$ [µg L$^{-1}$]")
    cb.set_clim(0,0.2)
    
    ###############################################################################
    # plot legend
    ax5  = fig.add_axes([0.8,0.0,0.2,0.2])
    ax5.axis('off')
    legend_agr = mpatches.Patch(color='burlywood', label='Agriculture',alpha=.75,linewidth=0)
    legend_gra = mpatches.Patch(color='olive', label='Grass, wood',alpha=.75,linewidth=0)
    legend_urb = mpatches.Patch(color='violet', label='Urban',alpha=.75,linewidth=0)
    legend_riv = mpatches.Patch(color='lightblue', label='River',alpha=.75,linewidth=0)
    plt.legend(handles=[legend_agr,legend_gra,legend_urb,legend_riv],ncol=1, loc="center", fontsize=fontsize,fancybox=True, framealpha=0.5)

def plotPoly(ax,xs,ys,zs,color="g",alpha=0.8):
    poly3d = [(x,y,z) for x,y,z in zip(xs,ys,zs)]
    collection = Poly3DCollection([poly3d], linewidths=0, alpha=alpha)
    collection.set_facecolor(color)
    ax.add_collection3d(collection)

def plotLine(ax,x1,x2,y1,y2,z1,z2,color="b",alpha=1,width=5): 
#    xs = [x1+width,x2+width,x2-width,x1-width]
#    ys = [y1,y2,y2,y1]
#    zs = [z1,z2,z2,z1] 
#    plotPoly(ax,xs,ys,zs,color=color,alpha=alpha)
    ax.plot([x1,x2],[y1,y2],[z1,z2],alpha=1,linewidth=width,color=color)

def plotSurf(ax,xvals, yvals, zvals,alpha=1):    
    tri = ax.plot_trisurf(xvals, yvals, zvals,color="w", linewidth=0,alpha=alpha,antialiased = False)


#################################################################################
###read data
#reaches = pd.read_csv("C:/0_work/bcs_catchmentmodelling/GKB_video/Reaches.csv")
#lu = pd.read_csv("C:/0_work/bcs_catchmentmodelling/GKB_video/gkb2points.csv")
#lu_classes = pd.read_csv("C:/0_work/bcs_catchmentmodelling/GKB_video/GKB2_nodes.csv")
#concs = pd.read_csv("C:/0_work/bcs_catchmentmodelling/GKB_video/GKB2_reaches.csv")
#concs["time"] = pd.to_datetime(concs["time"])
#xls = pd.ExcelFile("C:/0_work/bcs_catchmentmodelling/GKB_video/hourly_climate.xlsx")
#rain = xls.parse("Sheet1")
#rain["Date"] = pd.to_datetime(rain["Date"])
#rain.set_index("Date",inplace=True)
##load observed data
#obs = pd.read_excel("C:/0_work/bcs_catchmentmodelling/GKB_video/obs_FLU.xlsx",sheetname="obs")
#obs.set_index("Date",inplace=True)
##get conc data of monitoring sites
#monitor_names = ["r126","r140"]
#monitor_data = []
#monitor_coords = []
#for name in monitor_names:
#    c = concs[["time","conc"]][concs["name"]==name]
#    c.set_index("time",inplace=True)
#    monitor_data.append(c)
#    reach = reaches[reaches["name"]==name]
#    monitor_coords.append([reach["x"].values[0],reach["y"].values[0],reach["z"].values[0]])
#
#
##resample: 1H to 6H
#resample = "6H"
#
## get time window
#start = "2010-11-22"
#end ="2010-12-02"
##get time period
#
#conc_time=concs[concs["name"]=="r9"]
#conc_time.set_index("time",inplace=True)
#conc_time=conc_time.resample(resample).mean()
#conc_time.reset_index(inplace=True)
#
#timestamps = pd.DataFrame(conc_time["time"],columns=["time"])
#period = (timestamps["time"] >= pd.Timestamp(start)) & (timestamps["time"] <= pd.Timestamp(end))
#timestamps=timestamps[period]
#times = timestamps["time"].apply(lambda x: x.strftime('%Y-%m-%d %H:%M'))
#
#concs.set_index("time",inplace=True)
#concs=concs.groupby("name").resample(resample).mean()
#concs.reset_index(inplace=True)
#
#ind=0


for ind in range(len(times)):
    ###############################################################################
    # get values for actual time step
    actual_time = times.iloc[ind]
    t = pd.Timestamp(actual_time)
    conc = concs[concs["time"]==t]
    
    print(t, str(ind))
    ################################################################################ 
    ## Make the plot
    fig = plt.figure(figsize=(16, 10))
    
    ############################################################################
    # plot rainfall
    #select rainfall data in time series
    r = rain[(rain.index >= pd.Timestamp(start)) & (rain.index <= pd.Timestamp(end))]
    r=r.resample(resample).sum()
    #plot rainfall
    ax1 = fig.add_axes([0.08,0.77,0.85,0.18]) # x,y, lenght, height
    ax1.bar(r.index.to_pydatetime(), r['Precipitation'].values, width=0.05,color="b",edgecolor="w",align='center', alpha=0.5)
    ax1.bar([t.to_datetime()],[20], width=0.1,color="r",edgecolor="w",align='center', alpha=0.25)
    ax1.invert_yaxis()
    ax1.xaxis.tick_top()
    ax1.xaxis.set_ticks_position('both') 
    ax1.xaxis_date()
    ax1.grid(True)
    ax1.spines['bottom'].set_color('none')
    ax1.xaxis.set_ticks_position('top')
    
    

    ax1.set_yticks([5,10,15,20])
    ax1.set_yticklabels(["5","10","15",""])
    ax1.set_ylabel("Rain\n[mm "+resample+"$^{-1}$]")
    ax1.set_xlim(pd.Timestamp(start),pd.Timestamp(end))
    
    
    ax1.text(.01,-.1,"Timestep: "+resample+"\n"+actual_time, fontsize="small",horizontalalignment='left', transform=ax1.transAxes,fontweight="bold")

    
    #create axis
#    ax2 = fig.add_axes([0.05,0.76,0.9,0.09]) # x,y, lenght, height
    
#    #select conc data in time series and plot
#    for name,data in zip(monitor_names,monitor_data):
#        data_period = data[(data.index >= pd.Timestamp(start)) & (data.index <= pd.Timestamp(end))]
#        data_period = data_period.resample(resample).mean()
#        ax2.plot(data_period.index, data_period['conc'].values,label=name)
#
#    # plot observed data
#    obs_period = obs[(obs.index >= pd.Timestamp(start)) & (obs.index <= pd.Timestamp(end))]
#    obs_period = obs_period.resample(resample).mean()
#    ax2.plot(obs_period.index, obs_period['FLU conc [mg/m3]'].values,label="Observed",color="k",linestyle="-",alpha=.5,linewidth=3)
#    
#    #plot time bar
#    ax2.bar([t.to_datetime()],[0.25], width=0.1,color="r",edgecolor="w",align='center', alpha=0.25)
#    #format axis
#    ax2.xaxis_date()
#    ax2.grid(True)
#    ax2.spines['top'].set_color('none')
#    ax2.xaxis.set_ticks_position('bottom')
#    ax2.set_xticklabels("")
#    ax2.set_yticks([0.05,0.1,0.15,0.2])
#    ax2.set_yticklabels(["0.05","0.1","0.15","0.2"])
##    ax2.set_ylabel("Conc\n[µg L$^{-1}$]")
##    ax2.legend(loc=1,fontsize=fontsize)
#    ax2.text(0.015,-0.65,"Timestep: "+resample+"\n"+actual_time, fontsize="small",horizontalalignment='left', transform=ax2.transAxes,fontweight="bold")
#    ax2.set_xlim(pd.Timestamp(start),pd.Timestamp(end))
##    
    ###########################################################################
    #  plot map
    ax = fig.add_axes([0.05,0.05,0.9,0.7],projection='3d') # x,y, lenght, height
    
    ###########################################################################
    #  plot surface map
    plotSurf(ax,lu['x'], lu['y'], lu['DEM'],alpha=0.25)
    
    ###############################################################################
    #plot landuse classes
    
    #create colors dict 
    lu_types = ['agriculture', 'Park', 'grass', 'Urban', 'wood', 'farmyard', 'urban']
    colors = ["burlywood","olive","olive","violet","olive","violet","violet"]
    lu_colors = dict(zip(lu_types,colors))
    #
    #plot lu
    for OBJECTID in pd.unique(lu_classes["OBJECTID"]):
        poly = lu_classes[lu_classes["OBJECTID"]==OBJECTID]    
        c = lu_colors[poly["LULCType"].iloc[0]]
        xs = list(poly["x"])
        ys = list(poly["y"])
        zs = list(poly["z"]) #TODO remove adjustment factor
        plotPoly(ax,xs,ys,zs,color=c,alpha=.25)
        
    ###############################################################################
    # plot reaches
    width_maxt=8
    wet_area_max=10
    norm = matplotlib.colors.Normalize(vmin=min(reaches["conc_max"]), vmax=max(reaches["conc_max"]))
    cmap = matplotlib.cm.get_cmap('gnuplot_r')
    for i in range(len(reaches)):
        reach = reaches.iloc[i]
        x1 = reach["x"] 
        y1 = reach["y"] 
        z1 = reach["z"] #TODO_:cahnge
        if reach["downstream"]!="Outlet":
            next_reach = reaches[reaches["name"]==reach["downstream"]]
            x2 = next_reach["x"] 
            y2 = next_reach["y"] 
            z2 = next_reach["z"] #TODO_:cahnge
            wet_area  = conc["area"][conc["name"]==reach["name"]].values[0]       
    #        flowwidth = np.sqrt((x2-x1)**2 + (y2-y1)**2 + (z2-z1)**2).values[0]       
            width = 5#min(wet_area,wet_area_max)/wet_area_max*width_maxt
            value  = conc["conc"][conc["name"]==reach["name"]].values[0]
            if value>0:
                plotLine(ax,x1,x2,y1,y2,z1,z2,color=cmap(norm(value)),alpha=1,width=max(width,1))
            else:
                plotLine(ax,x1,x2,y1,y2,z1,z2,color="lightblue",alpha=1,width=max(width,1))
            
    
    ###############################################################################
    # make layout
    makeLayout(ax,(40400,43000)  ,(164000,167000),(0,130))
    
    ##############################################################################
    # save figure
    fig.savefig("C:/0_work/bcs_catchmentmodelling/GKB_video/final/" + str(ind) +  ".png",dpi=300)
        



#
#



















