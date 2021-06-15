# -*- coding: utf-8 -*-
"""
Created on Thu Apr 11 11:33:24 2019

@author: smh
"""

# python native
import os
from calendar import monthrange
from datetime import timedelta
import shutil
import copy
import math

# other
import pandas as pd
import numpy as np

# plotting
import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
from mpl_toolkits.mplot3d import Axes3D
import mpl_toolkits.axisartist as AA
from mpl_toolkits.axes_grid1 import host_subplot
from mpl_toolkits.axes_grid.parasite_axes import SubplotHost

# own
from .Parameter import ParameterList
from .Tools import TimeSeries,IO,Plots
from .Signatures import Signatures

class AreaYieldCatchment(TimeSeries,IO,Plots,Signatures):
    
    def __init__(self,catchment):
        """
        """
        
        # implement parent classes
        TimeSeries.__init__(self)
        IO.__init__(self)
        Plots.__init__(self)
        Signatures.__init__(self)
        
        # set catchment project
        print("Process ", catchment.modelrun.key )
        self.catchment = catchment
        self.inpData = catchment.inpData
        self.fpath = catchment.fpath
        self.fname = catchment.modelrun.key 
        self.filetype = catchment.database.ext
        self.time_format = catchment.database.date_format
        self.start_date = catchment.modelrun.begin + timedelta(hours=1) 
        
        # TODO: check
        self.end_date = catchment.modelrun.end

        # set format and header fo hdf5-file
        self.fmt = catchment.database.fmt_ts_reaches
        self.header =  catchment.database.columns_ts_reaches
        self.dtype =catchment.database.dtype_ts_reaches

        # load observed data
        fpath_obs =  os.path.join(self.fpath,"observation.csv")
        if os.path.isfile(fpath_obs):
            print("load", fpath_obs)
            self.observed = pd.read_csv(fpath_obs)
            self.observed ["time"]=pd.to_datetime(self.observed ["time"],format=self.time_format)
            self.observed.set_index(["time","key"],inplace=True)
                    
            # get gauging station
            self.gaugingstation = self.observed.index.levels[1][0]
        else:
            print("file not exists",fpath_obs)
            self.observed = None
            self.gaugingstation = None
        
        # load simulated data
        fpath_sim = os.path.join(self.fpath,self.fname + "_reaches."+self.filetype)
        print("load", fpath_sim)
        if self.filetype == "hdf":
            # read hdf5
            self.simulated =self.read_hdf_to_pandas(fname=fpath_sim,
                                                    keys=["time","key"], 
                                                    dset="reaches",
                                                    time_key="time",
                                                    time_format="%Y-%m-%dT%H:%M",
                                                    convert_byte=["time","key"])
        elif self.filetype == "csv":
            #read csv
            self.simulated = self.read_csv_to_pandas(fname=fpath_sim,
                                                     keys=["time","key"],
                                                     time_key="time",
                                                     time_format="%Y-%m-%dT%H:%M")
        
        # load spraydrif list
        self.spraydrift = pd.read_csv(os.path.join(self.fpath,"SprayDriftList.csv"))
            
        # climfile
        self.clim_file = pd.read_csv(os.path.join(self.fpath,"%s.csv" % ([row.key for row in self.catchment.inpData.ClimateList][0])))
        self.clim_file["time"]=pd.to_datetime(self.clim_file["key"],format=self.time_format)
        self.clim_file.set_index(["time"],inplace=True) 


    def calc_signatures(self):
        
        results_path = os.path.join(self.fpath,"Signatures")
        Signatures.createFolder(self, results_path) 

        try:
            # checks if observation period covers simulation period (years)
            pct = Signatures.check_data_inputs(self, self.simulated, self.observed)
            
            if pct == 100:            
                results_path = os.path.join(self.fpath,"Signatures")
                Signatures.createFolder(self, results_path) 
                print('Folder Signatures created')
                Signatures.calc_signatures(self, self.simulated, self.observed, self.gaugingstation, self.fname, results_path, self.clim_file)
                print('Signatures for complete timeseries calculated')
                Signatures.calc_yearly_TS(self, self.simulated, self.observed, self.gaugingstation, self.fname, results_path)
                print('Signatures for yearly timeseries calculated')
                print('### DONE ###')
            else:
                print('simulation period not in observation period')
                Signatures.calc_signatures_sim_only(self, self.simulated, self.gaugingstation, self.fname, results_path, self.clim_file)
        except:
            Signatures.calc_signatures_sim_only(self, self.simulated, self.gaugingstation, self.fname, results_path, self.clim_file)
            

    
    
    def performance(self,var):
        """
        makes a timeseries plot of observed and simulated values.
        """
        
        # get observed and simulated values
        obs = self.observed.xs(self.gaugingstation ,level=1)[var] 
        sim = self.simulated.xs(self.gaugingstation ,level=1)[var]  
        time = self.simulated.index.levels[0]
        
        # make plot
        fname = os.path.join(self.fpath,var+"_"+self.gaugingstation +".png")
        self.figure_performance(time,obs,sim,
                                "Flow [m$^3$ sec$^{-1}]$","%b", fname)
    
    
    def catchment_hydrology(self):
        """
        Creates several histograms of hydrology related to compound application.
        """
        
        # get time
        time = self.simulated.index.get_level_values(0)
        key = self.simulated.index.get_level_values(1)
        
        # select values from reaches which receive drift at the day of application
        cond1 = ( key.isin(self.spraydrift.key.tolist()))
        cond2 = (time.day == 10) & (time.month == 5) & ( key.isin(self.spraydrift.key.tolist()))
        
        # get flowdiwidths of reaches
        flowwidth = pd.DataFrame(self.catchment.get_flowwidths(),columns=["key","flowwith"])
        flowwidth.set_index("key",inplace=True)
        
        # make join between flowwidth and simulations and normalise volume and area
        join = self.simulated.join(flowwidth,how="left")
        volume = join.volume / join.flowwith
        area = join.area / join.flowwith
        
        # make plot
        fig = plt.figure(figsize=(10, 8))
        
        # plot water depth
        ax = fig.add_subplot(221)
        ax.grid(True,alpha=.2,color="k")
        self.ax_hist(ax,data=[self.simulated.depth[cond1],self.simulated.depth[cond2]],
             colors=["k","orange"],labels=["Catchment","Appl. day"],
             xlabel="Depth [m]",text="(a)",alpha=.5,normed=True)
        
        # plot volume  
        ax = fig.add_subplot(222)
        ax.grid(True,alpha=.2,color="k")
        self.ax_hist(ax,data=[volume[cond1],volume[cond2]],
             colors=["k","orange"],labels=["Catchment","Appl. day"],
             xlabel="Volume [m$^3$ m$^{-1}$]",text="(b)",alpha=.5,normed=True)    
    
        # plot wet area  
        ax = fig.add_subplot(223)
        ax.grid(True,alpha=.2,color="k")
        self.ax_hist(ax,data=[area[cond1],area[cond2]],
             colors=["k","orange"],labels=["Catchment","Appl. day"],
             xlabel="Wet area [m$^2$ m$^{-1}$]",text="(c)",alpha=.5,normed=True)    
    
          # plot wet area  
        ax = fig.add_subplot(224)
        ax.grid(True,alpha=.2,color="k")
        self.ax_hist(ax,data=[self.simulated.flow[cond1],self.simulated.flow[cond2]],
             colors=["k","orange"],labels=["Catchment","Appl. day"],
             xlabel="Flow [m$^3$ day$^{-1}$]",text="(d)",alpha=.5,normed=True)  
        
        # save 
        fname = os.path.join(self.fpath,"catchment_hydrology.png")
        fig.savefig(fname,dpi=300)
        fig.clf()
    
    def catchment_efate(self,day,intervals,maxSW=1,maxSED=1):
        """
        Creates several histograms of efate related to compound application.
        """
        
        # get time
        time = self.simulated.index.get_level_values(0)
        key = self.simulated.index.get_level_values(1)
        
        conds = []
        for intv in intervals:
            conds += [(time==(day+timedelta(seconds=3600*intv))) & ( key.isin(self.spraydrift.key.tolist()))]
        
        # make plot
        fig = plt.figure(figsize=(10, 8))
        
        # create colors
        cmap = plt.cm.get_cmap("jet", len(intervals)+1)
        colors = [cmap(i) for i in range(len(intervals))]
        
        # create labels
        labels = ["app.time + %ih"%i for i in intervals]
        
        # plot water depth
        ax = fig.add_subplot(211)
        ax.grid(True,alpha=.2,color="k")

        self.ax_hist(ax,data= [self.simulated.PEC_SW[cond] for cond in conds],
             colors=colors,labels=labels,
             xlabel="PEC$_{SW}$ [$\mu$g L$^{-1}$]",text="(a)",alpha=.5,normed=True,
              histtype='step', cumulative=-1)
        ax.set_xlim(0, maxSW)
        
        # plot maximum vaulue
        ax.text(0.8, 0.98, "max:%.3f"%(self.simulated.PEC_SW.max()) + " $\mu$g L$^{-1}$", 
                  horizontalalignment='left', 
                  verticalalignment='top', transform=ax.transAxes,
                  fontsize=10,fontweight="bold")
        
        # plot volume  
        ax = fig.add_subplot(212)
        ax.grid(True,alpha=.2,color="k")
        self.ax_hist(ax,data= [self.simulated.PEC_SED[cond] for cond in conds],
             colors=colors,labels=labels,
             xlabel="PEC$_{SED}$ [$\mu$g L$^{-1}$]",text="(b)",alpha=.5,normed=True,
              histtype='step', cumulative=-1)  
        ax.set_xlim(0, maxSED)
        
        # plot maximum value
        ax.text(0.8, 0.98, "max:%.3f"%( self.simulated.PEC_SED.max()) + " $\mu$g L$^{-1}$", 
                  horizontalalignment='left', 
                  verticalalignment='top', transform=ax.transAxes,
                  fontsize=10,fontweight="bold")
   
        # save 
        fname = os.path.join(self.fpath,"catchment_efate.png")
        fig.savefig(fname,dpi=300)
        fig.clf()

    def reach_getTimeseries(self,reach,variable=None,tstart=None,tend=None):
        """
        Return the timeseries of a specific reach. tstart/tend are optional
        to set a time snippet.
        
        :param reach: Name of reach.
        :type reach: str
        :param variable: Name of variable.
        :type variable: str
        :param tstart: Start time.
        :type tstart: datetime
        :param tend: End time.
        :type tend: datetime  
        
        :returns: Timeseries
        :rtype: pandas.TimeSeries 
        """
        if tstart == None:
            dat =  self.simulated.xs(reach,level=1)
        else:
            dat = self.simulated.xs(reach,level=1).loc[tstart:tend]
        
        if variable != None:
            return dat[variable]
        else: return dat
        


    def branch_hydrology_and_efate(self,par1,lab1,par2,lab2,
                                   reach_start,reach_end,
                                   tstart,tend,tintverval,
                                   timescale="daily",
                                   vmin=None,vmax=None,fname=""):
        """
        Plot 3D bar chart with with reaches on x-axis, time on y-axis and par1
        on z-axis as well as par2 as color of the bars.
        
        :param par1: Parameter to be plotted on z-axis
        :type par1: float
        :param lab1: Axis label of first parameter.
        :type lab1: str
        :param par1: Parameter to be plotted as color of bars
        :type par1: float   
        :param par2: Axis label of second parameter.
        :type lab2: str
        :param reach_start: Reach at the start of branch.
        :type reach_start: str
        :param reach_end: Reach at the end of branch.
        :type reach_end: str    
        :param tstart: Start time.
        :type tstart: datetime
        :param tend: End time.
        :type tend: datetime  
        :param tintverval: Invervall of time axis.
        :type tintverval: int
        :param vmin: Minimum value colormap par2.
        :type vmin: float
        :param vmax:  Maximum value colormap par2.
        :type vmax: float            
        
        :returns: -
        :rtype: -
        """

        # get reaches
        rList = self.inpData.ReachList
        
        # find reaches between start and end
        reaches = [reach_start]                     
        complete = False
        while not complete:
            # get current reach
            reach = reaches[-1]
            # get downstream storage
            downstream = rList[reach][0].__dict__["downstream"]
            # stop at outlet
            if downstream == "Outlet":
                complete = True
            else:
                # stop at end reach
                if downstream == reach_end:
                    reaches.append(downstream)
                    complete = True
                # go on when not outlet and not end
                else:
                    # get next reach
                    reaches.append(downstream)

        # get flowwidth
        flowwidths = dict(self.catchment.get_flowwidths())
        flowwidths = [flowwidths[reach] for reach in reaches]
        flowwidths_cumulative = np.cumsum(flowwidths)
    
    	# get data snippet for timeperiod of par1 and par2
        dat1 = pd.DataFrame([self.simulated.xs(reach,level=1).loc[tstart:tend][par1].values for reach in reaches])
        dat2 = pd.DataFrame([self.simulated.xs(reach,level=1).loc[tstart:tend][par2].values for reach in reaches])


        # format dat1 for plotting
        xpos=np.arange(dat1.shape[0])
        ypos=np.arange(dat1.shape[1])
        yposM, xposM = np.meshgrid(ypos+0.5, xpos+0.5)
        zpos=np.zeros(dat1.shape).flatten()
        dx = 0.25 * np.ones_like(zpos)
        dy= 0.5 * np.ones_like(zpos)
        dz=dat1.values.ravel()
    
        # format dat2 for plotting
        if vmin == None:
            vmin=0
        if vmax == None:
            vmax = np.percentile(dat2,95)
            
        norm = matplotlib.colors.Normalize(vmin=vmin, vmax=vmax)
        cmap = matplotlib.cm.get_cmap('jet')
        colors = cmap(norm(dat2.values.ravel()))

        # create figure
        fig = plt.figure(figsize=[14,8])
        ax1 = fig.add_subplot(111, projection='3d')
        
        # make plot
        ax1.grid(True)
        ax1.bar3d(xposM.ravel(),yposM.ravel(),zpos,dx,dy,dz,color=colors,alpha=0.5,edgecolor="None")
        ax1.xaxis.pane.fill = False
        ax1.yaxis.pane.fill = False
        ax1.zaxis.pane.fill = False
        ax1.set_xticks(np.arange(dat1.shape[0])+0.5)
        ax1.set_xticklabels(["%i"%(fw) if (i*100)%200 == 0 else "" for i,fw in zip(range(dat1.shape[0]),flowwidths_cumulative)],rotation=90)  
        ax1.set_yticks(np.arange(dat1.shape[1])+0.5)
        
        # create y-axis ticks
        yticklabels =    pd.date_range(tstart,tend,freq="H")
        if timescale=="hourly":
            ax1.set_yticklabels(["","",""]+[t.strftime("%d %b %y %Hh") if t.hour%tintverval == 0 else "" for t in yticklabels])
        elif timescale=="daily":
            ax1.set_yticklabels(["","",""]+[t.strftime("%d %b %y") if t.day%tintverval == 0 else "" for t in yticklabels])
        elif timescale=="monthly":
            ax1.set_yticklabels(["","",""]+[t.strftime("%b %y") if t.month%tintverval == 0 else "" for t in yticklabels])
        elif timescale=="weekly":
            ax1.set_yticklabels(["","",""]+[t.strftime("%b %y") if t.week%tintverval == 0 else "" for t in yticklabels])

        # set labels of axis
        ax1.set_xlabel("River head --> Outlet [m]", labelpad=20,fontweight='bold')
        ax1.set_ylabel("Time", labelpad=20,fontweight='bold')
        ax1.set_zlabel(lab1,fontweight='bold')        
        ax1.set_title("%s --> %s"%(reach_start,reach_end))
        
        # create colorbar
        ax = fig.add_axes([0.01,0.2,0.1,0.5]) # x,y, lenght, height
        ax.axis("off")
        divider = make_axes_locatable(ax)
        cax = divider.append_axes('right', size='20%', pad=0.05)
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        sm._A = []
        sm
        cb=fig.colorbar(sm,cax=cax, orientation='vertical',extend="max")
        cb.set_label(lab2,fontweight="bold")
        cb.set_clim(vmin=vmin, vmax=vmax)
    
        # save
        
        fname = os.path.join(self.fpath,"branch_efate_and_hydrology_"+fname+".png")
        fig.savefig(fname,dpi=300)      
        
        del fig,dat1,dat2


    def reach_hydrology_and_efate(self,reach,tstart=None,tend=None,
                                  ymax=[0.15,4,0.5,20],maxconc=0.,maxload=0.):
        """
        Plot hydrological and efate state variables of a single reach.
        
        :param reach: name of reach.
        :type reach: str
        :param tstart: Start time.
        :type tstart: datetime
        :param tend: End time.
        :type tend: datetime 
            
        :returns: -
        :rtype: -
        """

        # get simulated data
        res =  self.reach_getTimeseries(reach,variable=None,
                                        tstart=tstart,
                                        tend=tend)
        
       # some plot params
        params=["flow","volume","depth","area"]
        ylabels=["Discharge [m$^3$ sec$^{-1}$]","Volume [m$^3$]","Depth [m]","Wet area [m$^{3}$]"]
        names=["Discharge","Volume","Depth","Wet area"]
        styles=["--","-",":","-."]

        #plot mass balance
        fig = plt.figure(figsize=[12,6])
        host = host_subplot(111, axes_class=AA.Axes)
        plt.subplots_adjust(right=0.75)
       
        # plot subplots right
        offset=0
        for p,l,n,s,ym in zip(params,ylabels,names,styles,ymax):
            par = host.twinx()
            new_fixed_axis = par.get_grid_helper().new_fixed_axis
            par.axis["right"] = new_fixed_axis(loc="right", axes=par,
                                                    offset=(offset, 0))
            par.plot(res.index, res[p], label=l,color="k",linestyle=s)
            offset+=60
            par.set_ylim(0,ym)
            par.set_ylabel(l)
            
        # plot mass flux
        p1, = host.plot(res.index,res["MASS_SW"],color="b",linewidth=3,alpha=.5)
        p1, = host.plot(res.index,res["MASS_SED"],color="orange",linewidth=3,alpha=.5)
        p1, = host.plot(res.index,res["MASS_SED_DEEP"],color="red",linewidth=3,alpha=.5)        
        host.set_xlabel("Time")
        host.set_ylabel("Load [mg]") 
        host.set_ylim(0,maxload)
        #make legend
        plt.legend(loc=0)
        host.axis["bottom"].major_ticklabels.set_rotation(30)
        host.axis["bottom"].major_ticklabels.set_ha("right")
        host.axis["bottom"].label.set_pad(30)
        #save figure
        fname = os.path.join(self.fpath,"reach_hydrology_and_efate_load_"+reach+".png")
        fig.savefig(fname,dpi=300)         
    
        #plot concentration
        fig = plt.figure(figsize=[12,6])
        host = host_subplot(111, axes_class=AA.Axes)
        plt.subplots_adjust(right=0.75)
       
        # plot subplots right
        offset=0
        for p,l,n,s,ym in zip(params,ylabels,names,styles,ymax):
            par = host.twinx()
            new_fixed_axis = par.get_grid_helper().new_fixed_axis
            par.axis["right"] = new_fixed_axis(loc="right", axes=par,
                                                    offset=(offset, 0))
            par.plot(res.index, res[p], label=l,color="k",linestyle=s)
            offset+=60
            par.set_ylim(0,ym)
            par.set_ylabel(l)
    
        # plot mass flux
        p1, = host.plot(res.index,res["PEC_SW"],color="b",linewidth=3,alpha=.5)
        p1, = host.plot(res.index,res["PEC_SED"],color="orange",linewidth=3,alpha=.5)    
        host.set_ylim(0,maxconc)
        host.set_xlabel("Time")
        host.set_ylabel("PEC [$\mu$g L$^{-1}$]")
        host.set_title(reach)
        #make legend
        plt.legend(loc=0)
        host.axis["bottom"].major_ticklabels.set_rotation(30)
        host.axis["bottom"].major_ticklabels.set_ha("right")
        host.axis["bottom"].label.set_pad(30)
        # save figure
        fname = os.path.join(self.fpath,"reach_hydrology_and_efate_conc_"+reach+".png")
        fig.savefig(fname,dpi=300)       
  
    