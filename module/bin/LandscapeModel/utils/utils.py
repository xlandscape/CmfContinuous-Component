# -*- coding: utf-8 -*-
"""
Created on Mon Nov  6 10:32:24 2017

@author: smh
"""
import os
import numpy as np
#import pandas as pd
import matplotlib.pylab as plt
from matplotlib.lines import Line2D
import matplotlib.patches as mpatches
from collections import Counter
import sys
from datetime import datetime

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
    


def export_reach(fpath,name,reachname):
    dat = pd.read_csv(os.sep.join([fpath,name+"_reaches.csv"]) )
    d=dat[dat["name"]=="r184"]
    d.set_index("name",inplace=True)
    d.to_csv(os.sep.join([fpath,name+"_"+reachname+"_reaches.csv"]) )

def convert_Koc_to_Kd(Koc,foc):
    """
    Function to convert Koc to Kd.
    
    Koc (double):   Koc of substance in (kg/L)
    foc (double):   organic mattewr in [-]
    """
    return Koc*foc

def calc_Q10FAC(T,Tbase,QFAC=2.2):
    """
    Calculate temperature dependent degradation based on a Q10 
    equation.
    
    T (double):       Temperature [°C]
    Tbase (double):   Base tempeature [°C]
    QFAC (double):    factor for rate increase when temperatur increases by
                        10°C (default value being 2.2 (FOCUS, 1996).
    """
    return QFAC**(T-Tbase)/10.

def calc_FOCUS_degradationfactor_depth(depth):
    """
    the rate of pesticide degradation decreases with depth in the soil profile, 
    following the same rate of decline assumed in the development of the FOCUS 
    groundwater scenarios.
    
    depth (double):     soil depth   
    """
    if depth <0.3:
        degradation_factor=1.0
    elif depth>=0.3:
        degradation_factor = 0.5
    elif depth >= 0.6 and depth <=1.0:
        degradation_factor = 0.3
    else:
        degradation_factor = 0
    return degradation_factor

def calc_FOCUS_degradationfactor_theta(theta,theta_ref,B=0.7):
    """
    The B value is used in both PRZM and MACRO and is derived from the Walker 
    equation (f = (/REF)B, Walker, 1974). The recommended default value 
    is 0.7, which is the geo-metric mean of a number of values found in the 
    literature (Gottesbüren, 1991). This cor-rection factor is appropriate
    for laboratory data but is generally not needed for degrada-tion data 
    obtained from field studies. It is not recommended to change the default
    values, unless scientifically justified.
    
    theta (double):      water content
    theta_ref (double): reference theta at pF 2.0
    B double:           correction factor, usally 0.7
    """
    return (theta / theta_ref)**B

def calc_Q10FAC(T,Tbase,QFAC=2.2):
    """
    Calculate temperature dependent degradation based on a Q10 
    equation.
    
    T (double):       Temperature [°C]
    Tbase (double):   Base tempeature [°C]
    QFAC (double):    factor for rate increase when temperatur increases by
                        10°C (default value being 2.2 (FOCUS, 1996).
    """
    return QFAC**(T-Tbase)/10.

def calc_LinearSoilTemperature(tmp_surface,tmp_profile,depth,depth_profile):
    """
    Calculates the soil temprature at depth based on a linear interpolation
    between the surface temperature and the temprature at the lower bottom
    of the soil profile. The latter one can be estimated from the average 
    annula surface temperature.
    tmp_surface (double):       Surface temperature (°C)
    tmp_profile (double):       Temerpature at lower soil boundary  (°C)
    depth (double):             depth of acutal soil layer (m)
    depth_profile (double):     depth of lower boundasry of soil profile (m)
    """
    x = [0.,depth_profile]
    y = [tmp_surface,tmp_profile]
    xvals = [depth]
    return np.interp(xvals, x, y)[0]




###############################################################################
# utils
def readCSV(fpath,dtype,delimiter=","):
    """reads csv file and covnerts to numpy.recarray"""
    f = open(fpath,"r")
    f = f.read()
    f = f.split("\n")[1:]
    
    if f[-1] == "": f=f[:-1]
    
    f = [tuple(i.split(",")) for i in  f]
    return np.array(f,dtype=dtype)

def writeCSV(np_file,fpath,delimiter=","):
    """reads csv file and covnerts to numpy.recarray"""
    f = open(fpath,"w")
    #write header
    header = delimiter.join(np_file.dtype.names)+"\n"
    f.write(header)
    s = "\n".join([",".join([str(col) for col in row]) for row in np_file])
    f.write(s)
    f.close()




def readInputData(fpath):
    inputdata_types = dict()
    
    
    inputdata_types["ClimateStationList"] = [('Name', 'U100'), 
                   ('x', '<f8'), ('y', '<f8'),  ('z', '<f8'),('lat', '<f8'),('lon', '<f8')]
    inputdata_types["OutletList"] = [('name', 'U100'), ('x', '<f8'), ('y', '<f8'),
                   ('z', '<f8'), ('downstream', 'U100') ]
    inputdata_types["SubbasinList"] = [('name', 'U100'),('component', 'U100'), ('x', '<f8'), ('y', '<f8'),
                   ('z', '<f8'), ('downstream', 'U100'),('residencetime', '<f8') ]
    inputdata_types["ReachList"] = [('name', 'U100'), ('x', '<f8'), ('y', '<f8'), 
                   ('z', '<f8'),('downstream', 'U100'),
                   ('initial_depth', '<f8'),('manning_n', '<f8'), ('bankslope', '<f8'),
                   ('width', '<f8'), ('shape', '<U20'),
                   ('dens', '<f8'),('porosity', '<f8'), ('oc', '<f8'),
                   ('depth_sed', '<f8'), ('depth_sed_deep', '<f8')]
    inputdata_types["FieldList"] = [('name', 'U100'), ('reach', 'U100'),
                   ('reach_connection', 'U100'),('adjacent_field', 'U100'),
                   ('field_connection', 'U100'),
                   ('x', '<f8'), ('y', '<f8'),   ('z', '<f8'), ('latitude', '<f8'),('gw_depth', '<f8'),
                   ('residencetime_gw_river', '<f8'),
                   ('residencetime_drainage_river', '<f8'),
                   ('puddledepth','<f8'),
                   ('saturated_depth','<f8'), 
                   ('evap_depth','<f8'), ('area', '<f8'),
                   ('deep_gw', '<U10'),('deep_gw_rt', '<f8'),
                   ('drainage_depth', '<f8'),('drainage_suction_limit', '<f8'),('drainage_t_ret', '<f8'),
                   ('flowwdith_sw', '<f8'),('slope_sw', '<f8'),('nManning', '<f8'),
                   ('hasDrainage', 'U100'),
                   ('meteostation', 'U100'), ('rainstation', 'U100'),
                   ('soil', 'U100'),('plantmodel', 'U100'),
                   ('unit_traveltime', 'U100'),('soilwaterflux', 'U100')]
    inputdata_types["SoilLayerList"] = [('field', 'U100'), ('depth', '<f8'),
                   ('Ksat', '<f8'), ('Phi', '<f8'),   ('alpha', '<f8'),
                   ('n', '<f8'),('m', '<f8'),('Corg', '<f8'),('residual_wetness', '<f8')]
    inputdata_types["CropCoefficientList"] = [('name', '<U100'), 
                   ('GLAImin', '<f8'), ('GLAImax', '<f8'), ('GLAIharv', '<f8'), 
                   ('rootinit', '<f8'), ('rootmax', '<f8'), 
                   ('heightinit', '<f8'), ('heightmax', '<f8'),
                   ('rpin', '<f8'), 
                   ('Dmin', '<f8'), ('Dstart', '<f8'), ('Dmax', '<f8'), 
                   ('Dharv', '<f8'), ('cform', '<f8'), ('dform', '<f8'), 
                   ('feddes1', '<f8'), ('feddes2', '<f8'), ('feddes3', '<f8'), 
                   ('feddes4', '<f8'), ('croptype', '<U100'), ('wintercrop', '<U100')]
    inputdata_types["ManagementList"] = [('field', 'U100'),('date', 'U100'), ('task', 'U100'),
                   ('description', 'U100'), ('value', 'U100')]
    
    #read climate stations
    ClimateStationList = readCSV(os.path.join(fpath , "ClimateList.csv"),
                                 inputdata_types["ClimateStationList"])
    #read list of  fields
    FieldList = readCSV(os.path.join(fpath,"CellList.csv"),
                        inputdata_types["FieldList"]) 
#    #read properties of subbasin
    SubbasinList =  readCSV(os.path.join(fpath,"CatchmentList.csv"),
                         inputdata_types["SubbasinList"])     

    ###########################################################################
    # read reaches
    error_ReachList=False
    try:
        ReachList = readCSV(os.path.join(fpath,"ReachList.csv"),
                            inputdata_types["ReachList"])
    except BaseException as e:
        print("ERROR in Reaches.csv: " + str(e))
        error_ReachList = True
        sys.exit()
        

    #  check reaches fo repeated names, because name is unique
    c=Counter(ReachList["name"])
    replicates = [name for name in ReachList["name"] if c[name]>1]
    if len(replicates) > 0:
        print("ERROR: name repeated in Reaches.csv: " + str(replicates))
        error_ReachList = True
        sys.exit()

    # check if each conenction is existing
    not_existing = []
    for reach in ReachList:
        if not reach["downstream"] == "Outlet":
            if not len(ReachList[ReachList["name"]==reach["downstream"]])>0:
                not_existing.append([reach["name"]+ " --> " +reach["downstream"]])
    if len(not_existing)>0:
        print("ERROR: Non existing connection in Reaches.csv: " + str(not_existing))
        error_ReachList = True
        sys.exit()

    #check slope   
    reaches_slope = []
    for reach in ReachList:
        z1 = reach["z"]
        if not reach["downstream"] == "Outlet":
            reach_downstream = ReachList[ReachList["name"]==reach["downstream"]][0]
            z2 = reach_downstream["z"]           
            if not (z1-z2)>0:
                reaches_slope.append(reach["name"]+ " z=%.4fm"%(z1)+ " --> " +reach["downstream"]+" z=%.4fm"%(z2))
    if len(reaches_slope)>0:
        print("ERROR: Upwards flow in  Reaches.csv: " + str(reaches_slope))
        error_ReachList = True
        sys.exit()

    #check flowwidth
    flowwidths = []
    for reach in ReachList:
        # get coords
        x1 = reach["x"]
        y1 = reach["y"]
        z1 = reach["z"]
        if reach["downstream"] != "Outlet":
            x2 = ReachList["x"][ReachList["name"]==reach["downstream"]][0]
            y2 = ReachList["y"][ReachList["name"]==reach["downstream"]][0]
            z2 = ReachList["z"][ReachList["name"]==reach["downstream"]][0]
        #   calculate flow width
            flowwidth = np.sqrt((x2-x1)**2 + (y2-y1)**2 + (z2-z1)**2)
            if not flowwidth >= 0:
                flowwidths.append([reach["name"] + " --> " + reach["downstream"]+ ": %.4fm"%(flowwidth)])

    if len(flowwidths)>0:
        print("ERROR: Lenght of channel lower than 0 in Reaches.csv: " + str(flowwidths))
        error_ReachList = True
        sys.exit()
    
    if error_ReachList:  
        ReachList = None
        sys.exit()
             
    # read soil layer list
    SoilLayerList = readCSV(os.path.join(fpath,"SoilList.csv"),
                            inputdata_types["SoilLayerList"])
    # read subatance info
    SubstanceList = readCSV(os.path.join(fpath,"SubstanceList.csv"),
                            dtype=[('name', 'U100'),('molarmass', '<f8'),
                                   ('DT50sw', '<f8'),('DT50sed', '<f8'),
                                   ('KOC', '<f8'),('Temp0', '<f8'),('Q10', '<f8'),
                                   ('plantuptake', '<f8'),  ('QFAC', '<f8')])
        
    # read crop coefficients
    CropCoefficientList = readCSV(os.path.join(fpath,"CropcoefficientList.csv"),
                                  dtype = inputdata_types["CropCoefficientList"])
    # read management list
    ManagementList = readCSV(os.path.join(fpath,"CropManagementList.csv"),
                             dtype = inputdata_types["ManagementList"])  

    return ClimateStationList,FieldList,SubbasinList,ReachList,SoilLayerList,SubstanceList,CropCoefficientList,ManagementList








def repair_ReachList(fpath):
    """
    """
    ReachList = readCSV(os.path.join(fpath,"Reaches.csv"),
                         [('name', 'U100'), ('x', '<f8'), ('y', '<f8'), 
                   ('z', '<f8'),('downstream', 'U100'),
                   ('initial_depth', '<f8'),('manning_n', '<f8'), ('bankslope', '<f8'),
                   ('width', '<f8'), ('shape', '<U20'),
                   ('dens', '<f8'),('porosity', '<f8'), ('oc', '<f8'),
                   ('depth_sed', '<f8'), ('depth_sed_deep', '<f8'),])

    #make copy of original file
    writeCSV(ReachList,os.path.join(fpath,"Reaches_copy_original.csv"),delimiter=",")
    # adjust elevation in reach list until valid stream network
    correct = False
    counter=0
    while not correct:
        counter+=1
        reaches_slope = []
        for r,reach in enumerate(ReachList):
            z1 = reach["z"]
            if not reach["downstream"] == "Outlet":
                reach_downstream = ReachList[ReachList["name"]==reach["downstream"]][0]
                z2 = reach_downstream["z"] 
                # if not valid adjust elevation of actual and donwstream reach
                if not (z1-z2)>0:
                    reaches_slope.append(reach["name"]+ " z=%.4fm"%(z1)+ " --> " +reach["downstream"]+" z=%.4fm"%(z2))
                    mid = (z1+z2) / 2
                    ReachList[list(ReachList["name"]).index(reach["downstream"])]["z"] =mid-0.01
                    ReachList[r]["z"] =  mid+0.01
        if not len(reaches_slope)>0:
            correct=True
        print(counter)
    #save adjusted reach list
    writeCSV(ReachList,os.path.join(fpath,"Reaches.csv"),delimiter=",")













def stats_readCSV2(fpath,dtype,delimiter=","):
    """reads csv file and covnerts to numpy.recarray"""
    f = open(fpath,"r")
    f = f.read()
    f = f.split("\n")[1:]
    if f[-1] == "": f=f[:-1]
    f = [tuple(i.split(",")) for i in  f]
    return np.array(f,dtype=dtype)

def stats_calc_stats(dat_observed,dat_simulated):
    #clc r2
    r_squared = np.corrcoef(dat_observed,dat_simulated)[0][1]**2

    #calc NSE
    def calc_NSE(obs,sim):
        avg_obs = np.mean(obs)
        return  1 - (sum((obs-sim)**2)/sum((obs-avg_obs)**2))
    NSE = calc_NSE(dat_observed,dat_simulated)
    #plot data
    return r_squared,NSE

def stats_plot_timeseries(fpath,fname,compartment,dat_observed,dat_simulated,r_squared,NSE):
    fig = plt.figure(figsize=(5,3))
    ax=dat_simulated.plot(legend=True,label="Simulated",color="r",linewidth=3,alpha=.5)
    dat_observed.plot(legend=True,label="Measured",color="b",linewidth=3,alpha=.5)
    ax.set_xlim(pd.Timestamp('2010-06-01'), pd.Timestamp('2010-12-31'))
    ax.set_ylim(0,np.max([dat_observed,dat_simulated]))
    ax.grid(True)
    ax.set_ylabel('[m$^3$ sec$^{-1}$]')
    ax.text(0.1, 0.5, "r$^2$: "+"%.2f NSE: %.2f"%(r_squared,NSE),
            verticalalignment='bottom', horizontalalignment='left',
            transform=ax.transAxes,
            color='k', fontsize=9, 
            bbox=dict(facecolor='0.7', edgecolor='None', boxstyle='round,pad=.5',alpha=.5))
    fig.savefig(os.sep.join([fpath,fname+"_"+compartment+"_timeseries.png"]),dpi=300,transparent=True) 
    
def stats_process_data(fpath,fname,compartment):
    ###########################################################################
    # convert data
    if compartment == "outlets":
        dtype= [('Name', 'U100'), ('time', 'U100'),
                      ('volume', '<f8') , ('conc', '<f8'),  ('load', '<f8'), ('flow', '<f8')]
    elif compartment == "reaches":
        dtype= [('Name', 'U100'), ('time', 'U100'), ('depth', 'U100'),
             ('conc', '<f8'),  ('load', '<f8'), ('artificialflux', '<f8'),
              ('volume', '<f8'), ('flow', '<f8')]
    dat = stats_readCSV2(os.sep.join([fpath,fname+"_" + compartment + ".csv"]),dtype,delimiter=",")
    # convert datatime
    f = open(os.sep.join([fpath,fname+"_" + compartment + "_converted.csv"]),"w")
    f.write("name,time,year,month,day,hour,flow,volume\n")
    for i, _ in enumerate(dat):
        name = dat[i]["Name"]
        time = dat[i]["time"]
        time = time.split(" ")
        date = time[0]
        date = date.split(".")
        year = date[2]
        month = date[1]
        day = date[0]
        if time[1] == "":
            hour = "00"
        else: 
            hour = time[1]
        flow = str(dat[i]["flow"])
        volume = str(dat[i]["volume"])
        f.write(name+","+ year+"-"+month+"-"+day +","+year+","+month+","+day+","+hour+","+flow+","+volume+"\n")
    f.close()

def stats_calc_daily(fpath,fname,compartment,reach=""):

    #################################################################################
    ### average all models of one 
    res = pd.read_csv(os.sep.join([fpath,fname+"_"+compartment+"_converted.csv"]))
    if compartment == "outlets":
        res = res.groupby(["name","time"]).mean()
    elif compartment == "reaches":
        res = res[res["name"]==reach].groupby(["name","time"]).mean()
    res.reset_index(level=0,inplace=True)
    res.reset_index(level=1,inplace=True)
    res.time = pd.to_datetime(res['time'], format='%Y-%m-%d')
    res.flow = res.flow/86400.
    res.volume= res.volume.diff()/86400.
    res.to_csv(os.sep.join([fpath,fname+"_"+compartment+"_eval.csv"]))
    res.set_index(['time'],inplace=True)
    return res


def stats_eval_flow(fpath,fname,reaches):

    ###############################################################################
    # read observed data
    obs = pd.read_csv(os.sep.join([fpath,fname+"_observed.csv"]))
    obs.time =  pd.to_datetime(obs.time, format='%Y-%m-%d')
    obs.set_index(['time'],inplace=True)
    
    ##############################################################################
    # eval results of outlet
    # get data
    stats_process_data(fpath,fname,"outlets")
    res = stats_calc_daily(fpath,fname,"outlets",reach="")
    #read observed values
    obs = pd.read_csv(os.sep.join([fpath,fname+"_observed.csv"]))
    obs.time =  pd.to_datetime(obs.time, format='%Y-%m-%d')
    obs.set_index(['time'],inplace=True)
    dat_observed = obs["flow"][(obs.index >= pd.Timestamp('2010-06-01')) & (obs.index <= pd.Timestamp('2010-12-31'))]
    dat_simulated = res["volume"][(res.index >= pd.Timestamp('2010-06-01')) & (res.index <= pd.Timestamp('2010-12-31'))]
    #calc stats
    r_squared,NSE=stats_calc_stats(dat_observed,dat_simulated)
    #plot data
    stats_plot_timeseries(fpath,fname,"outlets",dat_observed,dat_simulated,r_squared,NSE)
    
    #############################################################################
    # eval results of reaches
    # get data
    stats_process_data(fpath,fname,"reaches")
    for reach in reaches:
        res = stats_calc_daily(fpath,fname,"reaches",reach=reach)
        dat_observed = obs["flow"][(obs.index >= pd.Timestamp('2010-06-01')) & (obs.index <= pd.Timestamp('2010-12-31'))]
        dat_simulated = res["flow"][(res.index >= pd.Timestamp('2010-06-01')) & (res.index <= pd.Timestamp('2010-12-31'))]
        #calc stats
        r_squared,NSE=stats_calc_stats(dat_observed,dat_simulated)
        #plot data
        stats_plot_timeseries(fpath,fname,reach,dat_observed,dat_simulated,r_squared,NSE)

def stats_FieldData_makeDaily_flows(fpath,fname):
    #read dataset
    res_hourly = pd.read_csv(os.sep.join([fpath,fname+"_agriculturalfields.csv"]))
    #convert fomrat of time stamp
    time = pd.DataFrame(res_hourly.time.str.split(' ',1).tolist(), columns = ['date','hour'])
    #create new datasets with flows and new time stamp
    res_daily = res_hourly[["name","qperc","qsurf","qdrain","qgw_gw","qgw_river","qlateral","rain"]]
    res_daily["date"] =  pd.to_datetime(time.date, format='%d.%m.%Y')
    #group data per field and day and save data
    res_daily = res_daily.groupby(["name","date"]).sum()
    # reset index
    res_daily.reset_index(level=0,inplace=True)
    res_daily.reset_index(level=1,inplace=True)
    # load table with field areas
    fields = pd.read_csv(os.sep.join([fpath,"Fields.csv"]))[["name","area"]]
    # merge with aree
    res_daily=pd.merge( fields,res_daily, on='name')
    #create new index
    res_daily.set_index(['name','date'],inplace=True)
    #save file
    res_daily.to_csv(os.sep.join([fpath,fname+"_agriculturalfields_daily_flows.csv"])) 
    
def stats_FieldData_makeDaily_reaches(fpath,fname):
    #read dataset
    res_hourly = pd.read_csv(os.sep.join([fpath,fname+"_reaches.csv"]))
    #convert fomrat of time stamp
    time = pd.DataFrame(res_hourly.time.str.split(' ',1).tolist(), columns = ['date','hour'])
    #create new datasets with flows and new time stamp
    res_daily = res_hourly[["name","time","conc"]]
    res_daily["date"] =  pd.to_datetime(time.date, format='%d.%m.%Y')
    #group data per field and day and save data
    res_daily = res_daily.groupby(["name","date"]).mean()
    # reset index
    res_daily.reset_index(level=0,inplace=True)
    res_daily.reset_index(level=1,inplace=True)
    #create new index
    res_daily.set_index(['name','date'],inplace=True)
    #save file
    res_daily.to_csv(os.sep.join([fpath,fname+"_reaches_daily.csv"]))   
    
    
    
    
    


def stats_FieldData_calcFlows(fpath,fname,subset,subset_name):
    ###########################################################################
    # calculate flow
    # load field data 
    res = pd.read_csv(os.sep.join([fpath,fname+"_agriculturalfields_daily_flows.csv"])) 
    #merge data    
    res=pd.merge( subset,res, on='name')
    # create index
    res["date"] = pd.to_datetime(res["date"], format='%Y-%m-%d')
    res.set_index(["name","date"],inplace=True)
    # calculate total water flows in m3: flow [mm] * 10 [convert mm to m3] * area [m2] / 10000 [convert m2 to ha] / 86400 [convert day to sec]
    res.qsurf = res.qsurf * res.area /10000. * 10.
    res.qdrain = res.qdrain * res.area /10000. * 10. 
    res.qgw_river = res.qgw_river * res.area /10000. * 10.
    #calculate sum of flows
    res["qsurf_m3sec"] = res.qsurf / 86400.
    res["qdrain_m3sec"] = res.qdrain / 86400.
    res["qgw_river_m3sec"] = res.qgw_river / 86400.
    res["flow_m3sec"] = (res.qsurf + res.qdrain + res.qgw_river) / 86400.
    #sum up flows
    res = res.groupby(res.index.get_level_values('date')).sum()
    #save data
    res[["qsurf_m3sec","qdrain_m3sec","qgw_river_m3sec"]].to_csv(os.sep.join([fpath,fname+"_agriculturalfields_flow_" + subset_name + ".csv"])) 

def stats_FieldData_makeDaily_loads(fpath,fname):
    #read dataset
    res_hourly = pd.read_csv(os.sep.join([fpath,fname+"_agriculturalfields.csv"]))
    #convert fomrat of time stamp
    time = pd.DataFrame(res_hourly.time.str.split(' ',1).tolist(), columns = ['date','hour'])
    #create new datasets with flows and new time stamp
    res_daily = res_hourly[["name","concgw","loadgw","concsw","loadsw","concdrainage","loaddrainage"]]
    res_daily["date"] =  pd.to_datetime(time.date, format='%d.%m.%Y')
    #group data per field and day and save data
    res_daily = res_daily.groupby(["name","date"]).mean()
    # reset index
    res_daily.reset_index(level=0,inplace=True)
    res_daily.reset_index(level=1,inplace=True)
    # load table with field areas
    fields = pd.read_csv(os.sep.join([fpath,"Fields.csv"]))[["name","area"]]
    # merge with aree
    res_daily=pd.merge( fields,res_daily, on='name')
    #create new index
    res_daily.set_index(['name','date'],inplace=True)
    #save file
    res_daily.to_csv(os.sep.join([fpath,fname+"_agriculturalfields_daily_loads.csv"])) 

def stats_FieldData_calcLoads(fpath,fname,subset,subset_name):
    ###########################################################################
    # calculate flow
    # load field data 
    res = pd.read_csv(os.sep.join([fpath,fname+"_agriculturalfields_daily_loads.csv"])) 
    
    flows = pd.read_csv(os.sep.join([fpath,fname+"_agriculturalfields_flow_" + subset_name + ".csv"])) 
    
    
    #merge data    
    res=pd.merge( subset,res, on='name')
    # create index
    res["date"] = pd.to_datetime(res["date"], format='%Y-%m-%d')
    res.set_index(["name","date"],inplace=True)

    ###########################################################################
    #calculate sum of load
    res["load_surf_g"] = res.loadsw
    res["load_drain_g"] = res.loaddrainage
    res["load_gw_g"] = res.loadgw
    res["load_g"] = (res.loadsw + res.loaddrainage + res.loadgw)

    #sum up flows
    res = res.groupby(res.index.get_level_values('date')).sum()
    #save data
    res[["load_surf_g","load_drain_g","load_gw_g","load_g"]].to_csv(os.sep.join([fpath,fname+"_agriculturalfields_load_" + subset_name + ".csv"])) 







def stats_FieldData_plotFlows(fpath,fname,subset_name,start='2010-06-01',end='2010-12-31',withObserved=True):
    res = pd.read_csv(os.sep.join([fpath,fname+"_agriculturalfields_flow_" + subset_name + ".csv"]))
    res.date =  pd.to_datetime(res.date, format='%Y-%m-%d')
    res.set_index(['date'],inplace=True)
    #make figure
    fig = plt.figure(figsize=(5,3))
    # plot simulated data
    ax=res[(res.index >= pd.Timestamp(start)) & (res.index <= pd.Timestamp(end))].plot.area(alpha=.75,colors=["steelblue","orange","forestgreen"])
   
    if withObserved:
        #plot observed data
        obs = pd.read_csv(os.sep.join([fpath,fname+"_observed.csv"]))
        obs.time =  pd.to_datetime(obs.time, format='%Y-%m-%d')
        obs.set_index(['time'],inplace=True)
        dat_observed = obs["flow"][(obs.index >= pd.Timestamp(start)) & (obs.index <= pd.Timestamp(end))]
        dat_observed.plot(legend=True,label="Measured",color="k",linewidth=1,linestyle="--",alpha=1)
        #calc stats
        dat_simulated = res["qsurf_m3sec"] + res["qdrain_m3sec"] + res["qgw_river_m3sec"]
        dat_simulated = dat_simulated[(res.index >= pd.Timestamp(start)) & (res.index <= pd.Timestamp(end))]
        r_squared,NSE=stats_calc_stats(dat_observed,dat_simulated)   
    
    #set axis properties
    ax.set_xlim(pd.Timestamp(start), pd.Timestamp(end))
    ax.set_ylim(0,np.max([dat_observed.max().max()]))
    ax.grid(True)
    ax.set_ylabel('[m$^3$ sec$^{-1}$]')

    ax.set_title(subset_name)
    # plot stats
    if withObserved:
        ax.text(0.1, 0.5, "r$^2$: "+"%.2f NSE: %.2f"%(r_squared,NSE),
                verticalalignment='bottom', horizontalalignment='left',
                transform=ax.transAxes,
                color='k', fontsize=9, 
                bbox=dict(facecolor='0.7', edgecolor='None', boxstyle='round,pad=.5',alpha=.5))
    plt.tight_layout()
    plt.savefig(os.sep.join([fpath,fname+"_agriculturalfields_flow_" + subset_name + ".png"]),dpi=300,transparent=True) 

def stats_catchment_flow(fpath,fname,obs,sim,climate,y_lims,sec_y_lims,start='2010-06-01',end='2010-12-31'):
#    res = pd.read_csv(os.sep.join([fpath,fname+"_agriculturalfields_flow_" + subset_name + ".csv"]))
#    res.date =  pd.to_datetime(res.date, format='%Y-%m-%d')
#    res.set_index(['date'],inplace=True)
    #make figure
    fig = plt.figure(figsize=(7,5))
    # plot simulated data
#    ax=res[(res.index >= pd.Timestamp(start)) & (res.index <= pd.Timestamp(end))].plot.area(alpha=.75,colors=["steelblue","orange","forestgreen"])
 

    dat_simulated = sim["msec"][(sim.index >= pd.Timestamp(start)) & (sim.index <= pd.Timestamp(end))]
    ax=dat_simulated.plot(legend=False,color="g",linewidth=4,linestyle="-",alpha=.5)  

##    obs.time =  pd.to_datetime(obs.time, format='%Y-%m-%d')
#    obs.set_index(['time'],inplace=True)
    dat_observed = obs["msec"][(obs.index >= pd.Timestamp(start)) & (obs.index <= pd.Timestamp(end))]
    dat_observed.plot(legend=False,color="k",linewidth=1,linestyle="--",alpha=1)
    
    
    

    #plot rainfall on secondary axis
    climate["Prec [mm/day]"] = climate["Prec [mm/day]"]*-1
    clim_timeperiod = climate["Prec [mm/day]"][(climate.index >= pd.Timestamp(start)) & (climate.index <= pd.Timestamp(end))]


    ax2=clim_timeperiod.plot(secondary_y=True,  use_index=True,color="k",label="Rainfall")
    ax2.set_ylabel("Rainfall [mm]")
    yticks = [i for i in np.arange(sec_y_lims[0],sec_y_lims[1],sec_y_lims[2])]
    ax2.set_yticks(yticks)
    maxval = clim_timeperiod.min()
    print(yticks,maxval)
    ax2.set_yticklabels([i*-1 if i>=maxval else "" for i in yticks])
    

    #calc stats
    r_squared,NSE=stats_calc_stats(dat_observed,dat_simulated)   
    
    #set axis properties
    ax.set_xlim(pd.Timestamp(start), pd.Timestamp(end))
    ax.set_ylim(0,np.max([dat_observed.max().max()]))
    ax.grid(True)
    ax.set_ylabel('Discharge [m$^3$ sec$^{-1}$]')

    yticks = [i for i in np.arange(y_lims[0],y_lims[1],y_lims[2])]
    ax.set_yticks(yticks)
    flow_maxval = max([dat_simulated.max(),dat_observed.max()])
    ax.set_yticklabels([i if i <= flow_maxval else "" for i in yticks])
    ax.set_xlabel("Date")

    ax.text(0.1, 0.5, "r$^2$: "+"%.2f NSE: %.2f"%(r_squared,NSE),
            verticalalignment='bottom', horizontalalignment='left',
            transform=ax.transAxes,
            color='k', fontsize=9, 
            bbox=dict(facecolor='0.7', edgecolor='None', boxstyle='round,pad=.5',alpha=.5))
    
    
    

    legend_observed = Line2D([],[],color='k', label='Observed',alpha=1,linewidth=.51,linestyle="--")
    legend_simulated = Line2D([],[],color='g', label='Simulated',alpha=.5,linewidth=4,linestyle="-")
    legend_meteo = Line2D([],[],color='k', label='Rainfall',alpha=1,linewidth=1,linestyle="-")
 
    plt.legend(handles=[legend_observed,legend_simulated,legend_meteo],
           bbox_to_anchor=(0.00, 0.1, 0.3, .7),fontsize=10.,frameon=True)


    
    
    plt.tight_layout()
    plt.savefig(os.sep.join([fpath,fname+"_flow.png"]),dpi=300,transparent=True) 

def stats_catchment_conc(fpath,fname,obs,sim,start='2010-06-01',end='2010-12-31'):
#    res = pd.read_csv(os.sep.join([fpath,fname+"_agriculturalfields_flow_" + subset_name + ".csv"]))
#    res.date =  pd.to_datetime(res.date, format='%Y-%m-%d')
#    res.set_index(['date'],inplace=True)
    #make figure
    fig = plt.figure(figsize=(5,3))
    print("############################")
    # plot simulated data
#    ax=res[(res.index >= pd.Timestamp(start)) & (res.index <= pd.Timestamp(end))].plot.area(alpha=.75,colors=["steelblue","orange","forestgreen"])
 
#
#    dat_simulated = sim["conc"][(sim.index >= pd.Timestamp(start)) & (sim.index <= pd.Timestamp(end))]
#    ax=dat_simulated.plot(legend=True,label="Simulated",color="g",linewidth=4,linestyle="-",alpha=.5)  

##    obs.time =  pd.to_datetime(obs.time, format='%Y-%m-%d')
#    obs.set_index(['time'],inplace=True)

#
    dat_observed = obs["conc"][(obs.index >= pd.Timestamp(start)) & (obs.index <= pd.Timestamp(end))]
    dat_observed.plot(legend=True,label="Observed",color="k",linewidth=1,linestyle="--",alpha=1)
    

#    #calc stats
#    r_squared,NSE=stats_calc_stats(dat_observed,dat_simulated)   
#    
#    #set axis properties
#    ax.set_xlim(pd.Timestamp(start), pd.Timestamp(end))
#    ax.set_ylim(0,np.max([dat_observed.max().max()]))
#    ax.grid(True)
#    ax.set_ylabel('[ug/L]')
#
#
#    ax.text(0.1, 0.5, "r$^2$: "+"%.2f NSE: %.2f"%(r_squared,NSE),
#            verticalalignment='bottom', horizontalalignment='left',
#            transform=ax.transAxes,
#            color='k', fontsize=9, 
#            bbox=dict(facecolor='0.7', edgecolor='None', boxstyle='round,pad=.5',alpha=.5))
    plt.tight_layout()
#    plt.savefig(os.sep.join([fpath,fname+"_flow.png"]),dpi=300,transparent=True) 


















def stats_FieldData_eval(fpath,fname):
    ###########################################################################
    # eval fields
    #calc daily values
    stats_FieldData_makeDaily(fpath,fname)
    #calc flow
    # subsets of fields along stream network
    sub1 =  ["f25","f71","f108"]
    sub2 =  ["f72","f81","f5","f100"]
    sub3 = ["f113","f91","f6","f29","f56","f31","f24","f17","f103"]
    sub4 = ["f19","f18","f86","f87","f30","f118"]
    sub5 = ["f63","f54","f46","f48","f57","f33","f121","f120","f85","f27"]
    sub6 = ["f111", "f49","f39","f28","f22","f41","f102","f45","f92","f109","f37","f119","f52","f4","f52"]
    sub7 = ["f26","f99","f98","f114"]
    sub8 = ["f97","f15","f70","f95","f9","f92"]
    subsets = [sub1,sub2,sub3,sub4,sub5,sub6,sub7,sub8]
    subsets = [pd.DataFrame(sub,columns=["name"]) for sub in subsets]
    subsets_names = ["sub1","sub2","sub3","sub4","sub5","sub6","sub7","sub8"]
    #get list of all fields adjacent to river
    fields = pd.read_csv(os.sep.join([fpath,"fields.csv"]))
    fields = pd.DataFrame(fields[fields["reach_connection"]!="None"]["name"])
    #add to list
    subsets += [fields]
    subsets_names += ["adjacent"]
    #eval all subsets
        #convert hourly to daily data
    stats_FieldData_makeDaily(fpath,fname)
    for subset,subset_name in zip(subsets,subsets_names):
        print(subset_name)

        # make selectio of subset of fields
        stats_FieldData_calcFlows(fpath,fname,subset,subset_name)
        #plot data
        stats_FieldData_plotFlows(fpath,fname,subset_name)









