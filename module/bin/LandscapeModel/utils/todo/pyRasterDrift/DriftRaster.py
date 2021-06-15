# -*- coding: utf-8 -*-
"""
Created on Thu Feb 22 08:44:05 2018

@author: smh
"""
import datetime


def find_nn():
    ###############################################################################
    # Fidn nearest neibouhr 
    
    
    ##load data
    #xls = pd.ExcelFile(r"n:\MOD\106520_BCS_catchment_models\mod\cal\datasets\cmf_GKB\maps\Drift_calc_raster\drift.xlsx")
    #river_raster = xls.parse("river")
    #river_segments = pd.read_csv(r"c:\0_work\bcs_catchmentmodelling\model_runs\final\GKB2_drift\Reaches.csv")
    ##source points
    srcXY = np.array([[x,y] for x,y in zip(river_segments["x"],river_segments["y"])])
    ##target points
    trgXY =  np.array([[x,y] for x,y in zip(river_raster["x"],river_raster["y"])])
    ##find nn
    index = spatial.KDTree(srcXY).query(trgXY)[1]
    #crete results table
    res = pd.DataFrame()
    res = river_raster
    points_nn =  river_segments.iloc[index]
    points_nn.reset_index(inplace=True)
    res["points_id"] = points_nn["name"]
    res["points_x"] = points_nn["x"]
    res["points_y"] = points_nn["y"]
    res.to_csv(r"n:\MOD\106520_BCS_catchment_models\mod\cal\datasets\cmf_GKB\maps\Drift_calc_raster\riversegments_raster_nn.csv")

def save_csv(fpath,fname,dat,header="",delimiter=","):
    if os.path.isfile(fpath+fname):
        mode="a"
    else:
        mode="w" 
    f=open(fpath+fname,mode)
    if mode == "w":
        f.write(delimiter.join(header)+"\n")
    f.write("\n".join([delimiter.join([r if type(r)==str else "%.4f"%(r) for r in row]) for row in dat])+"\n")
    f.close()


import matplotlib.pylab as plt
import numpy as np
import pandas as pd
from Drift import Drift
from scipy import spatial
import os


###############################################################################
# SUB B

##set header for results file
#header = ["event_id","date","wind direction","river segment","river_cell_id","distance [m]","deposition [%]","drift [mg/river cell]"]
#
#fpath = "c:/0_work/bcs_catchmentmodelling/model_runs/final/GKB2_drift/Drift/"
#filename = "data_50percentile.csv"
###############################################################################
##read FOCUS tabkes
#rautmann = pd.read_csv(fpath+"FOCUS_Rautmann_drift_values.csv")
#interception_table = pd.read_csv(fpath+"FOCUS_CropInterception_SW.csv")
#croptypes = pd.read_csv(fpath+"FOCUS_CropTypes.csv")
#step3_distances = pd.read_csv(fpath+"FOCUS_Step3_distances.csv")
#FOCUS_WaterBody = pd.read_csv(fpath+"FOCUS_WaterBody.csv")
#
################################################################################
## read catchment data and application data
#xls = pd.ExcelFile(fpath+ "drift.xlsx")
#river = xls.parse("river")
#wind = xls.parse("wind")
#wind["Date"] = pd.to_datetime(wind["Date"])
#application = xls.parse("applications")
#fields = xls.parse("fields")
#
#
##############################################################################
## substance parameter and drift calculation settings
#
##substance parameters
#DT50water=44.7 #days
#DT50sediment=44.7 #days
#BBCH = "no interception (00-09)"
#crop = "Maize"
#n_appl = 1
###drift paramteres
#max_distance = 200    #according to SWAT report
#uncertainty = 45
#interception=0
#
##create drift object
#drift = Drift(rautmann,croptypes,interception_table,step3_distances,FOCUS_WaterBody,crop,BBCH,DT50water=DT50water,DT50sediment=DT50sediment)
#
##set interception
#drift.interception = interception
#
##get regression parameter
#A,B,C,D,H = drift.get_regression_parameter(drift.croptype,n_appl)
#
##print info
#print("\n")
#print("Crop: %s Croptype: %s BBCH: %s n_appl: %i max distance: %im uncertainty: %i°"%(crop,drift.croptype,BBCH,n_appl,max_distance,uncertainty))
#print("Regression parameter A: %.4f B: %.4f C: %.4f D: %.4f H%.4f"%(A,B,C,D,H))
#print("\n")       
#        
##############################################################################
## calculate drift input for alll pplications
#
#
#appl = application[application["OBJECTID"]==37879].iloc[0]
#fig = plt.figure(figsize=(9, 7))
#for index_appl,appl in application.iterrows():
#
#    #get ID and crop
#    f = appl["OBJECTID"]
#    crop = appl["Crop"]
#       
#    # get wind directions during application window (between 6:00 am and 10:00 am) 
#    wind_appl_window = wind[(wind["Date"]>=pd.Timestamp(appl["Date"].strftime("%Y-%m-%d")+" 06:00")) & (wind["Date"]<=pd.Timestamp(appl["Date"].strftime("%Y-%m-%d")+" 10:00"))]
#    
#    #get most frequent wind direction
#    wind_direction= wind_appl_window["wind direction"].value_counts().idxmax()
#     
#    #get raster cellcs of current field
#    fields_selected = fields[fields["name"]==f]
#    
#    #print info
#    print(f,crop,wind_direction,len(fields_selected))
#    
#    #cal cinfo 
#    app_mgha= appl["ApplRate"] #mg/ha
#    app_gha = app_mgha/1000 #g/ha
#    area = appl["points_area"] #ha
#    app_g = app_gha * area
#    
#    # create string for summary
#    s = appl["Date"].strftime("%Y-%m-%d")+ "\n"
#    s += "\n"
#    s += "Field: " + str(f) + "\n"
#    s += "Field area: " + "%.2f"%(area) +" ha\n"
#    s += "\n"
#    s += "Crop: " + crop +"\n"
#    s += "App. rate: " + "%.0f"%(app_gha) +" g/ha\n"  
#    s += "App. rate: " + "%.0f"%(app_g) +" g\n"
#    s += "\n"
#    s += "Wind 06:00am - 10:00am:\n"
#    s += ",".join(wind_appl_window["wind direction"].values) + "\n\n"
#    
#    #calcuakte drift for all ruver cells related to tge field
#    start = datetime.datetime.now() 
#    name_vals,poit_id_vals,distance_vals,deposition_vals,drift_vals = drift.calc_drift_catchment(app_gha,appl["points_area"],wind_direction,uncertainty=45,max_distance=max_distance,
#                                       fields_selected_source=fields_selected,f=f,
#                                       river_source=river,xlim=(40500,43000),ylim=(164000,167000),s=s)#,
#    #                                    fpath=fpath+str(f)+"_"+ appl["Date"].strftime("%Y-%m-%d") +".png",fig=fig)      
#    print(datetime.datetime.now()-start)
#    
#    if name_vals != None:
#    #create list with id of application
#        event_id = np.array([appl["event_id"] for i in poit_id_vals])
#        app_date = np.array([appl["Date"].strftime("%Y-%m-%d") for i in poit_id_vals])
#        wind_direction_array = np.array([wind_direction for i in poit_id_vals])
#        #re-arange data and save to csv
#        dat = np.column_stack((event_id,app_date,wind_direction_array,poit_id_vals,name_vals,distance_vals,deposition_vals,drift_vals))
#        save_csv(fpath,filename,dat,header)  
#    else:
#        save_csv(fpath,filename,np.array([(str(appl["event_id"]),appl["Date"].strftime("%Y-%m-%d"),wind_direction,"","","","",""),],dtype=object),header)  
#



###############################################################################
# evaluation


###############################################################################
# make plot of wind directions
#wind_count = pd.DataFrame(wind["wind direction"].value_counts(),columns= ["wind direction"])
#names = ['SSW', 'SW', 'WSW', 'S', 'NE', 'NNE', 'W', 'ENE', 'NW', 'WNW', 'SSE',
#       'NNW', 'N', 'E', 'SE', 'ESE']
#
#
#fig = plt.figure(figsize=(5,5))
#ax1 = fig.add_axes([0.2,0.2,0.7,0.7]) # x,y, lenght, height  
#            
#wind_count.plot(ax=ax1,kind='bar', y = 'wind direction',label="2010-2013, entire year",alpha=.5,edgecolor="w",color="k",fontsize=10)
#
#ax1.set_xlabel("Wind direction")
#ax1.set_ylabel("Count [Occurance per hour]")
#ax1.grid(True)
#
#fig.savefig(fpath+"Winddirections.png",dpi=300)

## get dominating wind direction during applications
#wind_application=[]
#for index_appl,appl in application.iterrows():
#    f = appl["OBJECTID"]
#    crop = appl["Crop"]
#    wind_appl_window = wind[(wind["Date"]>=pd.Timestamp(appl["Date"].strftime("%Y-%m-%d")+" 06:00")) & (wind["Date"]<=pd.Timestamp(appl["Date"].strftime("%Y-%m-%d")+" 10:00"))]
#    wind_direction= wind_appl_window["wind direction"].value_counts().idxmax()
#    wind_application.append(wind_direction)
#
#wind_application = pd.DataFrame(wind_application,columns=["wind direction"])
#
#wind_application_count = pd.DataFrame(wind_application["wind direction"].value_counts(),columns= ["wind direction"])
#

##############################################################################
## plto daily observed and simualted values
#res = pd.read_csv(fpath+"data_50percentile.csv")
#res["date"] = pd.to_datetime(res["date"])
#res_daily = res.groupby(["date"]).sum()
#res_daily.reset_index(inplace=True)
##load observed data
#xls = pd.ExcelFile(fpath+ "psm_all_daily_final.xlsx")
#obs = xls.parse("obs")
#obs["Date"] = pd.to_datetime(obs["Date"])
#obs.set_index("Date",inplace=True)
#obs_daily = obs.resample(rule='24H',how='sum')
#obs_daily.reset_index(inplace=True)
#day_offset=1
#
#dat = []
#
#def get_val(o):
#    vals = o["FLU load  [mg]"].values
#    if len(vals)>0:
#        val = o["FLU load  [mg]"].values[0]
#    else:
#        val =0
#    return val
#    
#for _,r in res_daily.iterrows():
#    o=obs_daily[obs_daily["Date"] == r["date"]] 
#    o_plus_day=obs_daily[obs_daily["Date"] == r["date"]+ pd.DateOffset(1)]
#    o_minus_days=obs_daily[obs_daily["Date"] == r["date"]- pd.DateOffset(1)]
#
#
#    dat.append((r["date"],r["drift [mg/river cell"],get_val(o_minus_days),get_val(o),get_val(o_plus_day)))
#
#dat = pd.DataFrame(dat,columns=["date","Simulated drift","Observed steam load (-1day)","Observed steam load","Observed steam load (+1day)"])
#dat.set_index("date",inplace=True)
#print(dat.sum())
#for year in range(2010,2014):
#    print(year,dat[dat.index.year==year].sum())







#for year in range(2010,2014,1):
#    fig = plt.figure(figsize=(15,5))
#    ax1 = fig.add_axes([0.2,0.2,0.7,0.7]) # x,y, lenght, height  
#    dat_year = dat[dat.index.year==year]
#    ax1.bar(dat_year.index, dat_year["Simulated drift"],color="r",edgecolor="None",alpha=.5,width=1,label="Simulated drift")
#    ax1.plot(dat_year.index, dat_year["Observed steam load"],color="k",alpha=1,marker="o",markersize=5,linewidth=0,label="Observed steam load")    
#    ax1.set_ylim(0,2500)
#    ax1.legend(loc=0)
#    ax1.grid(True)
#    ax1.set_xlabel("Date")
#    ax1.set_ylabel("[mg day$^{-1}$]")
#    fig.savefig(fpath+"drift_90percentile"+str(year)+".png",dpi=300) 

################################################################################
## plot cumulative density functions of deposition
#data_50percentile = pd.read_csv(fpath+"data_50percentile.csv")
#data_90percentile = pd.read_csv(fpath+"data_90percentile.csv")
#
#
## empirical CDF
#def F(x,data):
#    return float(len(data[data <= x]))/len(data)
#
#
#vF = np.vectorize(F, excluded=['data'])
#
## calc cdf for 90% percentile
#x_90percentile=np.sort(data_90percentile["deposition [%]"])
#y_90percentile=vF(x=x_90percentile, data=data_90percentile["deposition [%]"])
#
## calc cdf for 50% percentile
#x_50percentile=np.sort(data_50percentile["deposition [%]"])
#y_50percentile=vF(x=x_50percentile, data=data_50percentile["deposition [%]"])

#fig = plt.figure(figsize=(5,5))
#ax1 = fig.add_axes([0.2,0.2,0.7,0.7]) # x,y, lenght, height  
#ax1.plot(x_90percentile,y_90percentile,label="90%-percentile")
#ax1.plot(x_50percentile,y_50percentile,label="50%-percentile")
#ax1.grid(True)
#ax1.set_xlabel("Deposition [%]")
#ax1.set_ylabel("Frequency [normalized]")
#ax1.legend(loc=4)
#fig.savefig(fpath+"deposition_90percentile.png",dpi=300) 
#


###############################################################################
## create summary of drift values
#
##load drift data
#drift = pd.read_csv(fpath+"data_50percentile.csv")
##format data
#drift["date"] = pd.to_datetime(drift["date"])
##set application hour to 10:00
#drift["date"] = drift["date"].apply(lambda x: x.replace(hour=10))
##create summary per day and river segment
#drift_summary = drift[["date","river segment","drift load [mg]"]].groupby(["date","river segment"]).sum()
##drift_summary.to_csv(fpath+"data_50percentile_summary.csv")
#drift_summary.reset_index(inplace=True)
##get unique list of river segments
#reaches = pd.unique(drift_summary['river segment'])
##get data of one reach
#reach = reaches[0]
#drift_reach = drift_summary[drift_summary["river segment"]==reach]
#drift_reach.set_index("date",inplace=True)
##set drift water flux
#drift_reach["drift flux [m3]"]=1
##create a time period according to the modelling step and period
#alldata = pd.DataFrame(pd.date_range("2010-01-01","2013-12-31",freq="H"),columns=["time"])
#alldata["name"] = reach
#alldata.set_index("time",inplace=True)
##join data
#alldata = alldata.join(drift_reach)
#
## do the same for all over river segemnts
#for reach in reaches:
#    print (reach)
#    
#    drift_reach = drift_summary[drift_summary["river segment"]==reach]
#    drift_reach.set_index("date",inplace=True)
#    #set drift water flux
#    drift_reach["drift flux [m3]"]=1
#    #create a time period according to the modelling step and period
#    time = pd.DataFrame(pd.date_range("2010-01-01","2013-12-31",freq="H"),columns=["time"])
#    time["name"] = reach
#    time.set_index("time",inplace=True)
#    #join data
#    alldata = alldata.append(time.join(drift_reach))
##drop unneccessary columns
#alldata.drop('river segment', axis=1, inplace=True)
##set nan values to zero
#alldata.loc[pd.isnull(alldata["drift load [mg]"]),"drift load [mg]"]=0
#alldata.loc[pd.isnull(alldata["drift flux [m3]"]),"drift flux [m3]"]=0
###save data
#alldata.to_csv(fpath+"GKB2_drift.csv")


################################################################################
## SUB F

# TODO:
#        self.deposition /=2 # TODO: delete (ind Drift.py)

#
###set header for results file
#header = ["event_id","date","wind direction","river segment","river_cell_id","distance [m]","deposition [%]","drift [mg/river cell]"]
##
#fpath = "c:/0_work/bcs_catchmentmodelling/model_runs/final/GKB2_SubF_drift/"
#filename = "data_50percentile.csv"
###############################################################################
##read FOCUS tabkes
#rautmann = pd.read_csv(fpath+"FOCUS_Rautmann_drift_values.csv")
#interception_table = pd.read_csv(fpath+"FOCUS_CropInterception_SW.csv")
#croptypes = pd.read_csv(fpath+"FOCUS_CropTypes.csv")
#step3_distances = pd.read_csv(fpath+"FOCUS_Step3_distances.csv")
#FOCUS_WaterBody = pd.read_csv(fpath+"FOCUS_WaterBody.csv")
#
################################################################################
## read catchment data and application data
#xls = pd.ExcelFile(fpath+ "drift.xlsx")
#river = xls.parse("river")
#wind = xls.parse("wind")
#wind["Date"] = pd.to_datetime(wind["Date"])
#application = xls.parse("applications")
#fields = xls.parse("fields")


##############################################################################
## substance parameter and drift calculation settings
#
##substance parameters
#DT50water=44.7 #days
#DT50sediment=44.7 #days
#BBCH = "no interception (00-09)"
#crop = "Potatoes"
#n_appl = 1
###drift paramteres
#max_distance = 200    #according to SWAT report
#uncertainty = 45
#interception=0
#
##create drift object
#drift = Drift(rautmann,croptypes,interception_table,step3_distances,FOCUS_WaterBody,crop,BBCH,DT50water=DT50water,DT50sediment=DT50sediment)
#
##set interception
#drift.interception = interception
#
##get regression parameter
#A,B,C,D,H = drift.get_regression_parameter(drift.croptype,n_appl)
#
##print info
#print("\n")
#print("Crop: %s Croptype: %s BBCH: %s n_appl: %i max distance: %im uncertainty: %i°"%(crop,drift.croptype,BBCH,n_appl,max_distance,uncertainty))
#print("Regression parameter A: %.4f B: %.4f C: %.4f D: %.4f H%.4f"%(A,B,C,D,H))
#print("\n")       
#        
##############################################################################
## calculate drift input for alll applications
#
#
#
#fig = plt.figure(figsize=(9, 7))
#for index_appl,appl in application.iterrows():
#
#    #get ID and crop
#    f = appl["OBJECTID"]
#    crop = appl["Crop"]
#       
#    # get wind directions during application window (between 6:00 am and 10:00 am) 
#    wind_appl_window = wind[(wind["Date"]>=pd.Timestamp(appl["Date"].strftime("%Y-%m-%d")+" 06:00")) & (wind["Date"]<=pd.Timestamp(appl["Date"].strftime("%Y-%m-%d")+" 10:00"))]
#    
#    #get most frequent wind direction
#    wind_direction= wind_appl_window["wind direction"].value_counts().idxmax()
#     
#    #get raster cellcs of current field
#    fields_selected = fields[fields["name"]==f]
#    
#    #print info
#    print(f,crop,wind_direction,len(fields_selected))
#    
#    #cal cinfo 
#    app_mgha= appl["ApplRate"] #mg/ha
#    app_gha = app_mgha/1000 #g/ha
#    area = appl["points_area"] #ha
#    app_g = app_gha * area
#    
#    # create string for summary
#    s = appl["Date"].strftime("%Y-%m-%d")+ "\n"
#    s += "\n"
#    s += "Field: " + str(f) + "\n"
#    s += "Field area: " + "%.2f"%(area) +" ha\n"
#    s += "\n"
#    s += "Crop: " + crop +"\n"
#    s += "App. rate: " + "%.0f"%(app_gha) +" g/ha\n"  
#    s += "App. rate: " + "%.0f"%(app_g) +" g\n"
#    s += "\n"
#    s += "Wind 06:00am - 10:00am:\n"
#    s += ",".join(wind_appl_window["wind direction"].values) + "\n\n"
#    
#    #calcuakte drift for all ruver cells related to tge field
#    start = datetime.datetime.now() 
#    name_vals,poit_id_vals,distance_vals,deposition_vals,drift_vals = drift.calc_drift_catchment(app_gha,appl["points_area"],wind_direction,uncertainty=45,max_distance=max_distance,
#                                       fields_selected_source=fields_selected,f=f,
#                                       river_source=river,xlim=(40500,43000),ylim=(164000,167000),s=s,
#                                        fpath=fpath+str(f)+"_"+ appl["Date"].strftime("%Y-%m-%d") +".png",fig=fig)      
#    print(datetime.datetime.now()-start)
#    
#    if name_vals != None:
#    #create list with id of application
#        event_id = np.array([appl["event_id"] for i in poit_id_vals])
#        app_date = np.array([appl["Date"].strftime("%Y-%m-%d") for i in poit_id_vals])
#        wind_direction_array = np.array([wind_direction for i in poit_id_vals])
#        #re-arange data and save to csv
#        dat = np.column_stack((event_id,app_date,wind_direction_array,poit_id_vals,name_vals,distance_vals,deposition_vals,drift_vals))
#        save_csv(fpath,filename,dat,header)  
#    else:
#        save_csv(fpath,filename,np.array([(str(appl["event_id"]),appl["Date"].strftime("%Y-%m-%d"),wind_direction,"","","","",""),],dtype=object),header)  
#



###############################################################################
## evaluation
#
#
###############################################################################
# make plot of wind directions
#wind_count = pd.DataFrame(wind["wind direction"].value_counts(),columns= ["wind direction"])
#names = ['SSW', 'SW', 'WSW', 'S', 'NE', 'NNE', 'W', 'ENE', 'NW', 'WNW', 'SSE',
#       'NNW', 'N', 'E', 'SE', 'ESE']
#
#
#fig = plt.figure(figsize=(5,5))
#ax1 = fig.add_axes([0.2,0.2,0.7,0.7]) # x,y, lenght, height  
#            
#wind_count.plot(ax=ax1,kind='bar', y = 'wind direction',label="2010-2013, entire year",alpha=.5,edgecolor="w",color="k",fontsize=10)
#
#ax1.set_xlabel("Wind direction")
#ax1.set_ylabel("Count [Occurance per hour]")
#ax1.grid(True)
#
#fig.savefig(fpath+"Winddirections.png",dpi=300)
#
## get dominating wind direction during applications
#wind_application=[]
#for index_appl,appl in application.iterrows():
#    f = appl["OBJECTID"]
#    crop = appl["Crop"]
#    wind_appl_window = wind[(wind["Date"]>=pd.Timestamp(appl["Date"].strftime("%Y-%m-%d")+" 06:00")) & (wind["Date"]<=pd.Timestamp(appl["Date"].strftime("%Y-%m-%d")+" 10:00"))]
#    wind_direction= wind_appl_window["wind direction"].value_counts().idxmax()
#    wind_application.append(wind_direction)
#
#wind_application = pd.DataFrame(wind_application,columns=["wind direction"])
#
#wind_application_count = pd.DataFrame(wind_application["wind direction"].value_counts(),columns= ["wind direction"])
#
#
##############################################################################
## plto daily observed and simualted values
#res = pd.read_csv(fpath+"data_50percentile.csv")
#res["date"] = pd.to_datetime(res["date"])
#res_daily = res.groupby(["date"]).sum()
#res_daily.reset_index(inplace=True)
##load observed data
#xls = pd.ExcelFile(fpath+ "psm_all_daily_final.xlsx")
#obs = xls.parse("obs")
#obs["Date"] = pd.to_datetime(obs["Date"])
#obs.set_index("Date",inplace=True)
#obs_daily = obs.resample(rule='24H',how='sum')
#obs_daily.reset_index(inplace=True)
#day_offset=1
#
#dat = []
#
#def get_val(o):
#    vals = o["METR load  [mg]"].values
#    if len(vals)>0:
#        val = o["METR load  [mg]"].values[0]
#    else:
#        val =0
#    return val
#    
#for _,r in res_daily.iterrows():
#    o=obs_daily[obs_daily["Date"] == r["date"]] 
#    o_plus_day=obs_daily[obs_daily["Date"] == r["date"]+ pd.DateOffset(1)]
#    o_minus_days=obs_daily[obs_daily["Date"] == r["date"]- pd.DateOffset(1)]
#
#
#    dat.append((r["date"],r["drift [mg/river cell]"],get_val(o_minus_days),get_val(o),get_val(o_plus_day)))
#
#dat = pd.DataFrame(dat,columns=["date","Simulated drift","Observed stream load (-1day)","Observed stream load","Observed stream load (+1day)"])
#dat.set_index("date",inplace=True)
#print(dat.sum())
#for year in range(2010,2014):
#    print(year,dat[dat.index.year==year].sum())
#
#for year in range(2010,2014,1):
#    fig = plt.figure(figsize=(15,5))
#    ax1 = fig.add_axes([0.2,0.2,0.7,0.7]) # x,y, lenght, height  
#    dat_year = dat[dat.index.year==year]
#    ax1.bar(dat_year.index, dat_year["Simulated drift"],color="r",edgecolor="None",alpha=.5,width=1,label="Simulated drift")
#    ax1.plot(dat_year.index, dat_year["Observed steam load"],color="k",alpha=1,marker="o",markersize=5,linewidth=0,label="Observed steam load")    
#    ax1.set_ylim(0,2500)
#    ax1.legend(loc=0)
#    ax1.grid(True)
#    ax1.set_xlabel("Date")
#    ax1.set_ylabel("[mg day$^{-1}$]")
#    fig.savefig(fpath+"drift_90percentile"+str(year)+".png",dpi=300) 

################################################################################
## plot cumulative density functions of deposition
#data_50percentile = pd.read_csv(fpath+"data_50percentile.csv")
##data_90percentile = pd.read_csv(fpath+"data_90percentile.csv")
#
#
## empirical CDF
#def F(x,data):
#    return float(len(data[data <= x]))/len(data)
#
#
#vF = np.vectorize(F, excluded=['data'])
##
### calc cdf for 90% percentile
##x_90percentile=np.sort(data_90percentile["deposition [%]"])
##y_90percentile=vF(x=x_90percentile, data=data_90percentile["deposition [%]"])
#
## calc cdf for 50% percentile
#x_50percentile=np.sort(data_50percentile["deposition [%]"])
#y_50percentile=vF(x=x_50percentile, data=data_50percentile["deposition [%]"])
#
#fig = plt.figure(figsize=(5,5))
#ax1 = fig.add_axes([0.2,0.2,0.7,0.7]) # x,y, lenght, height  
##ax1.plot(x_90percentile,y_90percentile,label="90%-percentile")
#ax1.plot(x_50percentile,y_50percentile,label="50%-percentile")
#ax1.grid(True)
#ax1.set_xlabel("Deposition [%]")
#ax1.set_ylabel("Frequency [normalized]")
#ax1.legend(loc=4)
#fig.savefig(fpath+"deposition_90percentile.png",dpi=300) 


#
##############################################################################
# create summary of drift values

#load drift data
drift = pd.read_csv(fpath+"data_50percentile.csv")
#format data
drift["date"] = pd.to_datetime(drift["date"])
#set application hour to 10:00
drift["date"] = drift["date"].apply(lambda x: x.replace(hour=10))
#create summary per day and river segment
drift_summary = drift[["date","river segment","drift load [mg]"]].groupby(["date","river segment"]).sum()
#drift_summary.to_csv(fpath+"data_50percentile_summary.csv")
drift_summary.reset_index(inplace=True)
#get unique list of river segments
reaches = pd.unique(drift_summary['river segment'])
#get data of one reach
reach = reaches[0]
drift_reach = drift_summary[drift_summary["river segment"]==reach]
drift_reach.set_index("date",inplace=True)
#set drift water flux
drift_reach["drift flux [m3]"]=1
#create a time period according to the modelling step and period
alldata = pd.DataFrame(pd.date_range("2010-01-01","2013-12-31",freq="H"),columns=["time"])
alldata["name"] = reach
alldata.set_index("time",inplace=True)
#join data
alldata = alldata.join(drift_reach)

# do the same for all over river segemnts
for reach in reaches:
    print (reach)
    
    drift_reach = drift_summary[drift_summary["river segment"]==reach]
    drift_reach.set_index("date",inplace=True)
    #set drift water flux
    drift_reach["drift flux [m3]"]=1
    #create a time period according to the modelling step and period
    time = pd.DataFrame(pd.date_range("2010-01-01","2013-12-31",freq="H"),columns=["time"])
    time["name"] = reach
    time.set_index("time",inplace=True)
    #join data
    alldata = alldata.append(time.join(drift_reach))
#drop unneccessary columns
alldata.drop('river segment', axis=1, inplace=True)
#set nan values to zero
alldata.loc[pd.isnull(alldata["drift load [mg]"]),"drift load [mg]"]=0
alldata.loc[pd.isnull(alldata["drift flux [m3]"]),"drift flux [m3]"]=0
##save data
alldata.to_csv(fpath+"GKB2_drift.csv")


#
#
#
#
#



































































