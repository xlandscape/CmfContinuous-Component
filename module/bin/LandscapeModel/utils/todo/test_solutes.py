# -*- coding: utf-8 -*-
"""
Created on Tue May 14 07:47:23 2019

@author: smh
"""

# import library
import cmf
from datetime import datetime
import pandas as pd
from matplotlib.dates import DateFormatter
import matplotlib.pylab as plt
import numpy as np
import numba
from numba import jit

def simulate_separated(timestep,ts,printres=True):
    """
    Creates a small cathcment with eight storages and ann outlet. Inflow is
    constant and a compound is applied at a fixed date.
    
    :param timestep: Timestep.
    :type timestep; cmf.time
    :param period: Timperiod.
    :type drift: float.
    :param ts: Concentrations and flows from full simulation.
    :type ts: pandas.DataFra,e
    :param ts_conc: List with conc per teimestep (mg/m3).
    :type ts_conc: List
    :param printres: Print res.
    :type printres; bool 
    
    """
    
    # calc timeseries
    conc1 = ts.r11_conc
    flow1 = ts.r11_r2
    conc2 = ts.r21_conc
    flow2 = ts.r21_r2
    load1 = conc1 * flow1
    load2 = conc2 * flow2
    ts_flow = flow1+flow2
    ts_conc = (load1+load2) / ts_flow

    
    # create a new container for all CMF objects
    p = cmf.project("cmpB")
    cmpB, = p.solutes 
    
    # create outlet
    outlet = p.NewStorage("outlet",x=400,y=400,z=40) 
    
    # create reaches with fixed shape
    shape=cmf.TriangularReach(100,0.2)
    shape.set_nManning(0.035)
    r1 = p.NewReach(x=500,y=400,z=45,shape=shape)
    r2 = p.NewReach(x=500,y=500,z=50,shape=shape)
    # create NBC for r13 and r23
    r2_nbc = cmf.NeumannBoundary.create(r2)
    # connect reaches
    r1.set_outlet(outlet)
    r2.set_downstream(r1)
    
    # set initial conditions
    reaches = [r1,r2]
    for reach in reaches:
        reach.depth = 0.
    
    # create inflow
    r2_nbc.flux = cmf.timeseries.from_sequence(start,timestep,ts_flow)  
    r2_nbc.concentration[cmpB] = cmf.timeseries.from_sequence(start ,timestep,ts_conc) 
    
    
    
    # create a numerical solver and set number of threads
    cmf.set_parallel_threads(1)
    solver = cmf.CVodeIntegrator(p,1e-9)
    res = []
    # run the model for a certain timeperiod
    if printres: print("flow m3/day r13  r23  r2 conc mg/m3 r13  r23  r2")
    for t in solver.run(start,end,step=timestep):
        
        # get flow
        r2_r1 = r2.flux_to(r1,t)
        # get conc
        r2_conc = r2.conc(t,cmpB)  
        # get loads
        r2_load = r2.Solute(cmpB).state
        # get outlet
        out_load = outlet.Solute(cmpB).state
        
        res.append((t.AsPython(),r2_r1,r2_conc,r2_load,out_load))
    
    # make dataframe
    res = pd.DataFrame(res,columns=["time","r2_r1","r2_conc","r2_load","out_load"])
    res.set_index("time",inplace=True)
    
    print (timestep,t,"sum outlet %.3f"%(res.out_load.max()))
    print()
    
    #return time snippet
    return res#res.loc[datetime(2007,5,2,9):datetime(2007,5,2,13)]


def simulate(timestep,inflow,drift,printres=True):
    """
    Creates a small cathcment with eight storages and ann outlet. Inflow is
    constant and a compound is applied at a fixed date.
    
    :param timestep: Timestep.
    :type timestep; cmf.time
    :param inflow: Timeseries of inflow.
    :type period: some kind of array
    :param drift: drift rate.
    :type drift: float.
    :param printres: Print res.
    :type printres; bool 
    
    """
    # create a new container for all CMF objects
    p = cmf.project("cmpB")
    cmpB, = p.solutes 
    
    # create outlet
    outlet = p.NewStorage("outlet",x=400,y=400,z=40) 
    
    # create reaches with fixed shape
    shape=cmf.TriangularReach(100.12492197250393,0.2)
    shape.set_nManning(0.035)
    r1 = p.NewReach(x=500,y=400,z=45,shape=shape)
    r2 = p.NewReach(x=500,y=500,z=50,shape=shape)
    r11 = p.NewReach(x=600,y=500,z=55,shape=shape)
    r12 = p.NewReach(x=700,y=500,z=60,shape=shape)
    r13 = p.NewReach(x=800,y=500,z=65,shape=shape)
    r21 = p.NewReach(x=500,y=600,z=55,shape=shape)
    r22 = p.NewReach(x=500,y=700,z=60,shape=shape)
    r23 = p.NewReach(x=500,y=800,z=65,shape=shape)
    
    # create NBC for r13 and r23
    r13_nbc = cmf.NeumannBoundary.create(r13)
    r23_nbc = cmf.NeumannBoundary.create(r23)
    
    # connect reaches
    r1.set_outlet(outlet)
    r2.set_downstream(r1)
    r23.set_downstream(r22)
    r22.set_downstream(r21)
    r21.set_downstream(r2)
    r13.set_downstream(r12)
    r12.set_downstream(r11)
    r11.set_downstream(r2)
    
    # set initial conditions
    reaches = [r1,r2,r11,r12,r13,r21,r22,r23]
    for reach in reaches:
        reach.depth = 0.
    
    # create inflow
    r13_nbc.flux = cmf.timeseries.from_sequence(start,timestep,inflow)  
    r23_nbc.flux = cmf.timeseries.from_sequence(start,timestep,inflow) 
    
    # create a numerical solver and set number of threads
    cmf.set_parallel_threads(1)

    solver = cmf.CVodeIntegrator(p,1e-9)
    
    res = []
    # run the model for a certain timeperiod
    if printres: print("flow m3/day r13  r23  r2 conc mg/m3 r13  r23  r2")
    for t in solver.run(start,end,step=timestep):
        
        # apply compound
        if t.day==2 and t.hour==10 and t.minute==0:
            r23.Solute(cmpB).state = drift * r23.wet_area() # mg
            r13.Solute(cmpB).state = drift * r13.wet_area()
            print("Application of cmpB: ",timestep,t)
            print("r13 Vol %.2fm3 Area %.2fm2"%(r13.volume,r13.wet_area()))
            print("r23 Vol %.2fm3 Area %.2fm2"%(r23.volume,r23.wet_area()))
            print("sum drift %.2f"%(( drift * r13.wet_area())+( drift * r23.wet_area())))
            
            solver.reset()
        
        # get flow
        r11_r2 = r11.flux_to(r2,t)
        r21_r2 = r21.flux_to(r2,t)
        r2_r1 = r2.flux_to(r1,t)
        # get conc
        r11_conc = r11.conc(t,cmpB)
        r21_conc = r21.conc(t,cmpB)
        r2_conc = r2.conc(t,cmpB)  
        # get loads
        r11_load = r11.Solute(cmpB).state
        r21_load = r21.Solute(cmpB).state
        r2_load = r2.Solute(cmpB).state
        # get outlet
        out_load = outlet.Solute(cmpB).state
        
        
        res.append((t.AsPython(),r11_r2,r21_r2,r2_r1,r11_conc,r21_conc,
                    r2_conc,r11_load,r21_load,r2_load,out_load))
    
        # print res
        if printres: print(t,"%.4f  %.4f  %.4f  %.4f  %.4f  %.4f"%(r11_r2,r21_r2,r2_r1,r11_conc,r21_conc,r2_conc))
    
    # make dataframe
    res = pd.DataFrame(res,columns=["time","r11_r2","r21_r2","r2_r1","r11_conc","r21_conc","r2_conc","r11_load","r21_load","r2_load","out_load"])
    res.set_index("time",inplace=True)
    
    print (timestep,t,"sum outlet %.3f"%(res.out_load.max()))
    print()
    
    #return time snippet
    return res#res.loc[datetime(2007,5,2,9):datetime(2007,5,2,13)]


def plot(res_hours,res_minutes,name=""):
    """
    """
    # plot concentration
    fig = plt.figure()
    ax = fig.add_subplot(111)
    # plot res_minutes
    ax.plot(res_minutes.index,res_minutes["r11_conc"],label="minutes r11",color="b",linestyle="--",alpha=.5)
    ax.plot(res_minutes.index,res_minutes["r21_conc"],label="minutes r21",color="b",linestyle=":",alpha=.5)
    ax.plot(res_minutes.index,res_minutes["r2_conc"],label="minutes r2",color="b",linestyle="-",alpha=.5)
    # plot res_hours
    ax.plot(res_hours.index,res_hours["r11_conc"],label="hours r11",color="r",linestyle="--",alpha=.5)
    ax.plot(res_hours.index,res_hours["r21_conc"],label="hours r21",color="r",linestyle=":",alpha=.5)
    ax.plot(res_hours.index,res_hours["r2_conc"],label="hours r2",color="r",linestyle="-",alpha=.5)
    ax.legend(loc=0)
    ax.set_ylabel("concentration mg/m3")
    ax.legend(loc=0)
    ax.grid(True)
    myFmt = DateFormatter("%Y-%m-%d %H:%M")
    ax.xaxis.set_major_formatter(myFmt)
    ax.xaxis.set_tick_params(rotation=90)
    plt.tight_layout()
    fig.savefig(name+"_concentrations.png",dpi=300)
    
    # plot flow
    fig = plt.figure()
    ax = fig.add_subplot(111)
    # plot res_minutes
    ax.plot(res_minutes.index,res_minutes["r11_load"],label="minutes r11",color="b",linestyle="--",alpha=.5)
    ax.plot(res_minutes.index,res_minutes["r21_load"],label="minutes r21",color="b",linestyle=":",alpha=.5)
    ax.plot(res_minutes.index,res_minutes["r2_load"],label="minutes r2",color="b",linestyle="-",alpha=.5)
    # plot res_hours
    ax.plot(res_hours.index,res_hours["r11_load"],label="hours r11",color="r",linestyle="--",alpha=.5)
    ax.plot(res_hours.index,res_hours["r21_load"],label="hours r21",color="r",linestyle=":",alpha=.5)
    ax.plot(res_hours.index,res_hours["r2_load"],label="hours r2",color="r",linestyle="-",alpha=.5)
    ax.legend(loc=0)
    ax.set_ylabel("load mg")
    ax.legend(loc=0)
    ax.grid(True)
    myFmt = DateFormatter("%Y-%m-%d %H:%M")
    ax.xaxis.set_major_formatter(myFmt)
    ax.xaxis.set_tick_params(rotation=90)
    plt.tight_layout()
    fig.savefig(name+"_loads.png",dpi=300)
    
    # plot flow
    fig = plt.figure()
    ax = fig.add_subplot(111)
    # plot res_minutes
    ax.plot(res_minutes.index,res_minutes["r11_r2"],label="minutes r11",color="b",linestyle="--",alpha=.5)
    ax.plot(res_minutes.index,res_minutes["r21_r2"],label="minutes r21",color="b",linestyle=":",alpha=.5)
    ax.plot(res_minutes.index,res_minutes["r2_r1"],label="minutes r2",color="b",linestyle="-",alpha=.5)
    # plot res_hours
    ax.plot(res_hours.index,res_hours["r11_r2"],label="hours r11",color="r",linestyle="--",alpha=.5)
    ax.plot(res_hours.index,res_hours["r21_r2"],label="hours r21",color="r",linestyle=":",alpha=.5)
    ax.plot(res_hours.index,res_hours["r2_r1"],label="hours r2",color="r",linestyle="-",alpha=.5)
    ax.legend(loc=0)
    ax.set_ylabel("flow m3/day")
    ax.legend(loc=0)
    ax.grid(True)
    myFmt = DateFormatter("%Y-%m-%d %H:%M")
    ax.xaxis.set_major_formatter(myFmt)
    ax.xaxis.set_tick_params(rotation=90)
    plt.tight_layout()
    fig.savefig(name+"_flows.png",dpi=300)

if __name__ == "__main__":
    # simulation time
    start = datetime(2007,5,2,0)
    end = datetime(2007,5,2,23)

    # drift rate
    drift = 1 #mg
    
    # pick results by hour
#    inflow = np.random.triangular(0,5,50, len(pd.date_range(start,end,freq="1H")))
    inflow = [15 if i.hour%3==0 else 15  for i in pd.date_range(start,end,freq="1H")]
    res_hours = simulate(cmf.h, inflow,drift,False)
    res_hours.to_csv(r"c:\LandscapeModel2019\bin\LandscapeModel\utils\todo\res_hours.csv")#
        
    # pick resutls by minute 
#    inflow = np.random.triangular(0,5,50, len(pd.date_range(start,end,freq="1min")))
    inflow = [15 if i.hour%3==0 else 15 for i in pd.date_range(start,end,freq="1min")]
    res_minutes = simulate(cmf.min, inflow,drift,False)
    res_minutes.to_csv(r"c:\LandscapeModel2019\bin\LandscapeModel\utils\todo\res_minutes.csv")
    
    # make plot
    plot(res_hours,res_minutes,"")

    # pick results by hour
    res_hours_sep = simulate_separated(cmf.h,res_hours,printres=True)
    
    # pick results by minutes
    res_minutes_sep = simulate_separated(cmf.min,res_minutes,printres=True)
    res_minutes_sep.to_csv(r"c:\LandscapeModel2019\bin\LandscapeModel\utils\todo\res_minutes_sep.csv")

    def mix_water(flows,concs):
        """
        Mixes fluxes (water+solutes) from two or more timeseries.
        
        :param flows: List with timeseries of flows.
        :param flows: list 
        :param concs: List with timeseries of flows.
        :param concs: list
        
        :returns: Three arrays with mixed laods,flows and concs.
        :rtype: np.array
        """
        # calc loads
        mix_loads = np.multiply(flows,concs)
        mix_loads = np.sum(mix_loads,axis=0)
        # sum up flows
        mix_flows = np.sum(flows,axis=0)
        # calc concs
        mix_concs = np.divide(mix_loads,mix_flows)
        return mix_loads,mix_flows,mix_concs
    
    
    start = datetime.now()
    # calc timeseries
    ts=res_minutes
    conc1 = ts.r11_conc
    flow1 = ts.r11_r2
    conc2 = ts.r21_conc
    flow2 = ts.r21_r2
    load1 = conc1 * flow1
    load2 = conc2 * flow2
    ts_flow = flow1+flow2
    ts_load = load1+load2
    ts_conc = ts_load / ts_flow
    print(datetime.now()-start)
    
    
    ts = pd.DataFrame(list(zip(flow1,flow1,load1,load2,conc1,conc2,ts_flow,ts_load,ts_conc)),
                      columns=["flow1","flow2","load1","load2","conc1","conc2","ts_flow","ts_load","ts_conc"],
                      index = res_minutes.index)
    ts.to_csv(r"c:\LandscapeModel2019\bin\LandscapeModel\utils\todo\res_minutes_TS.csv")#
    
    
    flows = [flow1,flow2]
    concs = [conc1,conc2]  
    start = datetime.now()
    mix_loads,mix_flows,mix_concs = mix_water(flows,concs)
    print(datetime.now()-start)

     # plot concentration
    fig = plt.figure()
    ax = fig.add_subplot(111)
    # plot res_minutes
    ax.plot(res_hours.index,res_hours_sep["r2_conc"],label="sep hours r2",color="r",linestyle="--",alpha=.5)
    ax.plot(res_hours.index,res_hours["r2_conc"],label="hours r2",color="r",linestyle="-",alpha=.5)
    ax.legend(loc=0)
    ax.set_ylabel("concentration mg/m3")
    ax.legend(loc=0)
    ax.grid(True)
    myFmt = DateFormatter("%Y-%m-%d %H:%M")
    ax.xaxis.set_major_formatter(myFmt)
    ax.xaxis.set_tick_params(rotation=90)
    plt.tight_layout()
    fig.savefig("comparison_hours"+"_concentrations.png",dpi=300)
    
     # plot concentration
    fig = plt.figure()
    ax = fig.add_subplot(111)
    # plot res_minutes
    ax.plot(res_minutes.index,res_minutes_sep["r2_conc"],label="sep minutes r2",color="b",linestyle="--",alpha=.5)
    ax.plot(res_minutes.index,res_minutes["r2_conc"],label="minutes r2",color="b",linestyle="-",alpha=.5)
#    ax.plot(res_minutes.index,ts_conc,label="minutes ts",color="orange",linestyle="-.",alpha=.5)
    ax.legend(loc=0)
    ax.set_ylabel("concentration mg/m3")
    ax.legend(loc=0)
    ax.grid(True)
    myFmt = DateFormatter("%Y-%m-%d %H:%M")
    ax.xaxis.set_major_formatter(myFmt)
    ax.xaxis.set_tick_params(rotation=90)
    plt.tight_layout()
    fig.savefig("comparison_hours_minutes"+"_concentrations.png",dpi=300)    


     # plot concentration
    fig = plt.figure()
    ax = fig.add_subplot(111)
    # plot res_minutes
    ax.plot(res_minutes.index,res_minutes_sep["r2_r1"],label="sep minutes r2",color="b",linestyle="--",alpha=.5)
    ax.plot(res_minutes.index,res_minutes["r2_r1"],label="minutes r2",color="b",linestyle="-",alpha=.5)
#    ax.plot(res_minutes.index,ts_flow,label="minutes ts",color="b",linestyle="-.",alpha=.5)
    ax.legend(loc=0)
    ax.set_ylabel("flow m3/day")
    ax.legend(loc=0)
    ax.grid(True)
    myFmt = DateFormatter("%Y-%m-%d %H:%M")
    ax.xaxis.set_major_formatter(myFmt)
    ax.xaxis.set_tick_params(rotation=90)
    plt.tight_layout()
    fig.savefig("comparison_hours_minutes"+"_flow.png",dpi=300)    

     # plot concentration
    fig = plt.figure()
    ax = fig.add_subplot(111)
    # plot res_minutes
    ax.plot(res_minutes.index,res_minutes["r2_conc"],label="minutes r2",color="b",linestyle="-",alpha=.5)
    ax.plot(res_hours.index,res_hours["r2_conc"],label="hours r2",color="r",linestyle="-",alpha=.5)
    ax.legend(loc=0)
    ax.set_ylabel("concentration mg/m3")
    ax.legend(loc=0)
    ax.grid(True)
    myFmt = DateFormatter("%Y-%m-%d %H:%M")
    ax.xaxis.set_major_formatter(myFmt)
    ax.xaxis.set_tick_params(rotation=90)
    plt.tight_layout()
    fig.savefig("comparison_minutes_hours.png",dpi=300)
    