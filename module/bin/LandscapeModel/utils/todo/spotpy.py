# -*- coding: utf-8 -*-
"""
Created on Apr 06 10:00 2018
@author(s): Sebastian Multsch

The script is based on a tutorial:
http://fb09-pasig.umwelt.uni-giessen.de/cmf/wiki/semi_distributed#

The setup of the tutorial has been modified in order to simulate hydrological
fluxed of different landuse types (grass, crop, wood, orchards, urban) with a 
lumped molling approach.

"""

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

def plot_flow(fname,model,sim,posterior_threshold=None):
    
    #preapre data
    stats = pd.DataFrame([(a,b,c) for a,b,c in zip(pd.date_range(model.begin,model.end)[1:],sim,model.evaluation()[1:])],columns=["Date","Sim","Obs"])
    r_squared,NSE = stats_calc_stats(stats[~np.isnan(stats["Obs"])]["Obs"],stats[~np.isnan(stats["Obs"])]["Sim"])
    stats.set_index("Date",inplace=True)

    #make plot of river segemnts
    fig = plt.figure(figsize=(10,7))
    
    #plot rainfall
    ax1 = fig.add_axes([0.1,0.71,0.8,0.2]) # x,y, lenght, height
    ax1.bar(stats.index, model.data.P[model.begin+model.data.step:model.end+model.data.step],align='center',color="k",width=.5)
    ax1.invert_yaxis()
    ax1.xaxis.tick_top()
    ax1.xaxis.set_ticks_position('both') # THIS IS THE ONLY CHANGE
    ax1.xaxis_date()
    ax1.grid(True)
    ax1.spines['bottom'].set_color('none')
    ax1.xaxis.set_ticks_position('top')
    ax1.set_ylabel("Rain [mm day$^{-1}$]")
    ax1.set_xlim(pd.Timestamp(model.begin),pd.Timestamp(model.end))    
    ax1.yaxis.tick_right()
    ax1.yaxis.set_label_position("right")
#    ax1.xaxis.set_major_locator(mdates.MonthLocator())
#    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
        
    #plot stream flow
    ax2 = fig.add_axes([0.1,0.2,0.8,0.5]) # x,y, lenght, height
    ax2.plot(stats.index,stats["Sim"],color="b",label="Simulated",linewidth=.7) 
    ax2.plot(stats.index,stats["Obs"],color="r",label="Observed",linewidth=.7)    
    ax2.set_ylim(0,.5)
    ax2.set_ylabel("Flow [m$^3$ sec$^{-1}$]")
    ax2.grid(True)
    ax2.spines['top'].set_color('none')
    ax2.set_xlim(pd.Timestamp(model.begin),pd.Timestamp(model.end))  
    ax2.xaxis.set_ticks_position('bottom')
#    ax2.xaxis.set_major_locator(mdates.MonthLocator())
#    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
    if posterior_threshold:
        #get posteritor distribution
        r = pd.DataFrame([list(i) for i in res[1:]],columns=[i for i in res.dtype.names]) #TODO: skip first run ... error spotpy?
        #select runs with a NSE higher than ..., i.e. posterior distribution
        if len(r[r["like1"]>posterior_threshold])>0:
            r = r[r["like1"]>posterior_threshold]
        #get minimum and maximum vale
        col_names=[i for i in res.dtype.names if i.find("simulation")>-1]
        postdis_sim_min = np.array([min([row[col] for r,row in r.iterrows()])  for col in col_names])
        postdis_sim_max = np.array([max([row[col] for r,row in r.iterrows()])  for col in col_names])
        #make plot
        ax2.fill_between(stats.index, postdis_sim_min, postdis_sim_max, where=postdis_sim_max >= postdis_sim_min, facecolor='b', interpolate=True,alpha=.25)
 
    #plot legend
    ax3  = fig.add_axes([0.1,0.1,0.8,0.1])# x,y, lenght, height
    legend_obs = mlines.Line2D([],[],color="red",label="Observed")
    legend_sim = mlines.Line2D([],[],color="blue",label = "Best simulation")
    legend_rain = mlines.Line2D([],[],color="k",label = "Rainfall")
    handels = [legend_sim,legend_obs,legend_rain]
    if posterior_threshold:
        legend_sim_post = mlines.Line2D([],[],color="blue",label = "Posterior dist.",alpha=.25,linewidth=4)
        handels.append(legend_sim_post)
    ax3.legend(handles=handels, ncol=3,bbox_to_anchor=(0.00, 0.5, 1., .102),fontsize=10.,frameon=True)
    ax3.axis("off")
    ax3.text(0.2, 0.05,"Mielen boven Aalst, 2007"+ "\n"+ "r$^2$: "+"%.2f NSE: %.2f"%(r_squared,NSE),
            verticalalignment='bottom', horizontalalignment='left',
            transform=ax3.transAxes,
            color='k', fontsize=9, 
            bbox=dict(facecolor='0.7', edgecolor='None', boxstyle='round,pad=.5',alpha=.5))

    fig.autofmt_xdate() 
    fig.savefig(fname,dpi=300)
    
    
import datetime
import cmf
import spotpy
#from spotpy.parameter import Uniform
import numpy as np
import pandas as pd
import matplotlib.pylab as plt
import matplotlib.lines as mlines
import os

class CatchmetnModel:
    def __init__(self,fpath,start,end):
        self.fpath = fpath
        self.start = start
        self.end = end

class SpotpySetup(object):
    def __init__(self,fpath,start,end):
        self.fpath = fpath
        self.start = start
        self.end = end
        self.params = [spotpy.parameter.Normal('Ksat',0.3,0.1,0.02,0.2),
                       spotpy.parameter.Normal('Phi',1.2,0.035,0.01,1.22),
                       spotpy.parameter.Normal('alpha',1,0.3,0.1,2.0),
                       spotpy.parameter.Normal('n',.55,0.04,0.02,0.6),
                       spotpy.parameter.Normal('m',.55,0.04,0.02,0.6),
                       ]
        
    def parameters(self):
        return spotpy.parameter.generate(self.params)

    def simulation(self,vector):
        simulations= self.cmfmodel._run(alpha=vector[0],n=vector[1],ksat=vector[2],porosity=vector[3])
        return simulations

    def evaluation(self,evaldates=False):
        if evaldates:
            return self.cmfmodel.eval_dates
        else:
            return self.cmfmodel.observations

    def objectivefunction(self,simulation,evaluation):
        objectivefunction= -spotpy.objectivefunctions.rmse(evaluation,simulation)
        return objectivefunction






if __name__ == '__main__':
    # Get sampler
    from spotpy.algorithms import lhs as Sampler_lhs

    # Check if we are running on a supercomputer or local
    parallel = 'mpi' if 'OMPI_COMM_WORLD_SIZE' in os.environ else 'seq'

#    parallel = 'mpc'

    # Run the models
    runs = 2

    #create cmf
    model = SpotpySetup(begin=datetime.datetime(2007,1,1),end=datetime.datetime(2007,12,31))

    # Create the sampler
    sampler = Sampler_lhs(model, parallel=parallel, dbname=model.dbname,
                      dbformat='csv', save_sim=True)
    #make analysis
    sampler.sample(runs)

    #get results
    res = sampler.getdata()
    
    
    
    
    
    
    
    
    
    
#    #get best model run        
#    best_run = res[np.argmax(res["like1"])]#sampler.status.bestrep
#    sim=list(best_run)[[i for i in res.dtype.names].index("simulation_0"):-1]
#    
#    #make plot
#    plot_flow("melsterbeek_miele_calibration.png",model,sim)#,posterior_threshold=0.35) #posterior_threshold: minimum NSE to select posterior runs

#    #make validation for each posterior dataset
#    posterior_threshold=.3
#    res_posterior = pd.DataFrame([list(i) for i in res[1:]],columns=[i for i in res.dtype.names])
#    if len(res_posterior[res_posterior["like1"]>posterior_threshold])>0:
#        res_posterior = res_posterior[res_posterior["like1"]>posterior_threshold]
#
#    for rowid,bestrun_pars_vector in res_posterior.iterrows():
#        #create new model for validation
#        model_validation = LumpedModel(begin=datetime.datetime(2012,1,1),end=datetime.datetime(2016,12,31))
#        
#        # Get the array of parameter realizations
#        params = spotpy.parameter.get_parameters_array(model)
#    
#        # Create the namedtuple from the parameter names
#        partype =  spotpy.parameter.get_namedtuple_from_paramnames(model, params['name'])
#        par = partype(bestrun_pars_vector["pargrass_V0L1"],
#                                      grass_V0L2=bestrun_pars_vector["pargrass_V0L2"],
#                                      grass_fETV0=bestrun_pars_vector["pargrass_fETV0"],
#                                      grass_fETV1=bestrun_pars_vector["pargrass_fETV1"],
#                                      grass_trL1L2=bestrun_pars_vector["pargrass_trL1L2"],
#                                      grass_trL1out=bestrun_pars_vector["pargrass_trL1out"],
#                                      grass_trL2out=bestrun_pars_vector["pargrass_trL2out"])
#    
#        #run model with 
#        validation_res_q = model_validation.simulation(par=par)
#    
#        #plot validation
#        plot_flow("melsterbeek_miele_validation_"+str(rowid)+".png",model_validation,validation_res_q)
#    
#        

#    
#        