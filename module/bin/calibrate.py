# -*- coding: utf-8 -*-
"""
Created on Apr 06 10:00 2018
@author(s): Sebastian Multsch


"""

# Get sampler
from spotpy.algorithms import lhs as Sampler_lhs
  
import datetime
import spotpy
from spotpy.parameter import Uniform
import numpy as np
import pandas as pd
import matplotlib.pylab as plt
import matplotlib.lines as mlines
import os  
import LandscapeModel

def convert_obs():
    reachfile = pd.read_csv("C:/LandscapeModel/CatchmentModel/projects/Discharge_Data/Mielen-boven-Aalst_interpolated.csv")
    reachfile["time"]=pd.to_datetime(reachfile["time"])
    reachfile.set_index("time",inplace=True)
    reachfile=reachfile.resample('24H').fillna("nearest")
    reachfile.reset_index(inplace=True)
    reachfile["time"] = reachfile["time"].dt.strftime("%Y-%m-%dT%H:%M")
    reachfile["flow"] = reachfile["Value"]*86400
    reachfile.set_index("time",inplace=True)
    reachfile[["flow"]].to_csv("C:/LandscapeModel/CatchmentModel/projects/Discharge_Data/Mielen-boven-Aalst_interpolated2.csv")
    


def calc_stats(obs,sim):
    # stats
    r_squared = np.corrcoef(obs,sim)[0][1]**2
    NSE = 1 - (sum((obs-sim)**2)/sum((obs-np.mean(obs))**2))
    return r_squared,NSE

def resample_dataset(file,rule='24H',start_date=None,end_date=None):
    reachfile = pd.read_csv(file)
    reachfile["time"]=pd.to_datetime(reachfile["time"],format="%Y-%m-%dT%H:%M")
    reachfile.set_index("time",inplace=True)
    res_q=reachfile["flow"].resample(rule=rule).mean()
    
    if start_date != None:
        start_date = start_date
        end_date = end_date
        res_q = res_q[(res_q.index >= start_date) & (res_q.index <= end_date)]
    return res_q

class CatchmentModel:
    
    def __init__(self,fpath,fname,LinearSolverType,resample,start_date, end_date):
        """
        Creates a warpper for the catchmet model and sets new parameter from
        spotpy.
        """
        
        self.fpath = fpath
        self.fname = fname
        self.LinearSolverType = LinearSolverType
        self.resample = resample
        self.start_date = start_date
        self.end_date = end_date
        self.Q=None
        
    def create_soillist(self,Ksat,Phi,alpha,n):
        """
        Replaces the parameter in soil list with new ones.
        """
    
        # read soillist
        soillist = LandscapeModel.utils.ParameterList(os.path.join(self.fpath,"projects",self.fname),"SoilList",",")

        #write new soil list
        s = "key,depth,Ksat,Phi,alpha,n,m,Corg,residual_wetness" + "\n"
        s += "\n".join( [ ",".join( [str(i) for i in [l.key,l.depth,Ksat,Phi,alpha,n,-1,-9999,-9999]]) for l in soillist] )
        f = open(os.path.join(self.fpath,"projects",self.fname,"SoilList.csv"),"w")
        f.write(s)
        f.close()

    def __setparameters(self, par):
        """
        Sets the parameters for all cells seperately
        """
        self.create_soillist(par.Ksat,par.Phi,par.alpha,par.n)           
            

    def __makemodelrun(self):
        """
        Maks a model run of CatchmentModel using runlist.
        """
        # set solver method
        LinearSolverType = self.LinearSolverType
     
        # current path
        fpath = os.sep.join(os.path.abspath(__file__).split(os.sep)[:-1])
        
        # read runlist
        runList = LandscapeModel.utils.ParameterList(os.path.join(self.fpath,"projects"),self.fname,",")
        print(os.path.join(fpath,"projects"))
        run = runList[0]
            
        print("make run:",run.fpath)

        # read input data of first model run
        inpD = LandscapeModel.utils.InputData(run.fpath)
        
        # set up catchment
        sc = LandscapeModel.Catchment(modelrun=run,inpData=inpD,
                                      LinearSolverType=LinearSolverType)
        
        # make model run
        start = datetime.datetime.now()
        sc(printTime=False)
        print("runtime", datetime.datetime.now()-start)
    
    def __getFlow(self):
        """
        Extract flow data from reach.
        """

        # read results and resample to daily data
        file = os.path.join(self.fpath,"projects",self.fname,self.fname+"_reaches.csv")
        res_q = resample_dataset(file,self.resample,self.start_date,self.end_date)

        return res_q
        
    def __call__(self,par=None):
        """
        Conduct model run with given paramter set and return simulation data.
        """
        
        # set params
        if par != None:
            self.__setparameters(par)
        
        # make model run
        self.__makemodelrun()
        
        self.Q = self.__getFlow()
        # returneval data
        return self.Q
            

class Spotpy_CatchmentModel:
    """
    """
    
    Ksat = Uniform(1,25, doc='Ksat')#100,300 #230
    Phi = Uniform(0.3,0.7, doc='Phi')#100,300 #230
    alpha = Uniform(0.001,0.1, doc='alpha')#100,300 #230
    n = Uniform(1.0,2.0, doc='n')#100,300 #230
   
    def __init__(self, fpath="",fname="",target_reach="",resample='24H',
                 start_date=None,end_date=None):
        """
        Initializes the model.

        """
        self.fpath = fpath
        self.fname = fname
        self.target_reach = target_reach
        self.resample=resample
        self.start_date = start_date
        self.end_date = end_date        
        # load observed data and resmaple daily
        file = os.path.join(self.fpath,"projects",self.fname,"observation.csv")
        self.obs = resample_dataset(file,rule=self.resample,
                                    start_date=self.start_date,
                                    end_date=self.end_date)
        
    def simulation(self, par):
        """
        Sets the parameters of the model and starts a run
        :return: np.array with runoff in mm/day
        """                
        cm = CatchmentModel(fpath=self.fpath,fname=self.fname,
                            LinearSolverType=0,resample=self.resample,
                            start_date=self.start_date,end_date=self.end_date)
        res_q = cm(par=par)
        return res_q.values

    def evaluation(self):
        """Returns the evaluation data"""
        return self.obs.values

    def objectivefunction(self, simulation, evaluation):
        """Calculates the objective function"""
        return spotpy.objectivefunctions.nashsutcliffe(simulation,evaluation)

if __name__ == '__main__':
    
    ###########################################################################
    # settings
    fpath = os.sep.join(os.path.abspath(__file__).split(os.sep)[:-1])
    fname_calibration = "Rummen_calibration"
    fname_validation = "Rummen_validation"
    target_reach = "r1"
    resample = "24H"
    start_date_cal = datetime.datetime(2007,1,1)
    end_date_cal = datetime.datetime(2007,12,31)
    start_date_val = datetime.datetime(2008,1,1)
    end_date_val = datetime.datetime(2008,12,31)
    runs = 2
    
    ###########################################################################
    # run analysis
    
    # create model
    cm_spotpy = Spotpy_CatchmentModel(fpath,fname_calibration,target_reach,
                                      resample=resample,start_date=start_date_cal,
                                      end_date=end_date_cal)
    
    # Create the sampler and make runs
    sampler = Sampler_lhs(cm_spotpy, parallel="seq", dbname=
                          os.path.join(fpath,"projects",fname_calibration,"spotpy"),
                          dbformat='csv', save_sim=True)
    sampler.sample(runs)
    res = sampler.getdata()
    best_run = res[np.argmax(res["like1"])]#sampler.status.bestrep
    
    ###########################################################################
    # process calibration
    
    # make modelrun with best paramterset
    cm_calibration = CatchmentModel(fpath=fpath,fname=fname_calibration,
                            LinearSolverType=0,resample=resample,
                            start_date=start_date_cal,end_date=end_date_cal)    
    cm_calibration.create_soillist(best_run["parKsat"],best_run["parPhi"],
                       best_run["paralpha"],best_run["parn"])
    Qcal = cm_calibration()
      
    # get observatio ndata calibration
    file = os.path.join(fpath,"projects",fname_validation,"observation.csv")
    cal = resample_dataset(file,rule=resample,
                            start_date=start_date_cal,
                            end_date=end_date_cal)
    timecal = cal.index
    Qobscal = cal.values
    
    # get observed data validation
    file = os.path.join(fpath,"projects",fname_validation,"observation.csv")
    val = resample_dataset(file,rule=resample,
                            start_date=start_date_val,
                            end_date=end_date_val)
    timeval = val.index
    Qobsval = val.values    

    # calculate performance calibration
    R2cal,NSEcal=calc_stats(Qobscal,Qcal)

    # make plot
    fig = plt.figure(figsize=[10,5])    

    # plot calibration
    host = fig.add_subplot(111)
    ax1, = host.plot(timecal, Qobscal,color="r", alpha=1,linewidth=1,  marker="",label="observed")
    ax1, = host.plot(timecal, Qcal,color="b", alpha=1,linewidth=1,  marker="",label="simulated")
    host.set_ylabel("m³/day")
    host.legend(loc=2)
    host.grid(True)
    host.text
    host.text(0.05, 0.68, "r$^2:$%.2f\nNSE:%.2f"%(R2cal,NSEcal), horizontalalignment='left', 
              verticalalignment='bottom', transform=host.transAxes,fontsize=10)
    host.set_title("Calibration")
    
    
    # save figure
    fig.autofmt_xdate()
    fig.savefig(os.path.join(fpath,"projects",fname_calibration,"calibration.png"),dpi=300)
    fig.clf()
    
    ###########################################################################
    # process validation
     
    # make validation model
    cm_validation = CatchmentModel(fpath=fpath,fname=fname_validation,
                            LinearSolverType=0,resample=resample,
                            start_date=start_date_val,end_date=end_date_val)
    cm_validation.create_soillist(best_run["parKsat"],best_run["parPhi"],
                       best_run["paralpha"],best_run["parn"])
    Qval = cm_validation()
    
    # make plot
    fig = plt.figure(figsize=[10,5])    

    # calculate performance validation
    R2val,NSEval=calc_stats(Qobsval,Qval)
    
    # plot validation
    host = fig.add_subplot(111)
    ax1, = host.plot(timeval, Qobsval,color="r", alpha=1,linewidth=1,  marker="",label="observed")
    ax1, = host.plot(timeval, Qval,color="b", alpha=1,linewidth=1,  marker="",label="simulated")
    host.set_ylabel("m³/day")
    host.legend(loc=2)
    host.grid(True)
    host.text
    host.text(0.05, 0.68, "r$^2:$%.2f\nNSE:%.2f"%(R2cal,NSEcal), horizontalalignment='left', 
              verticalalignment='bottom', transform=host.transAxes,fontsize=10)
    host.set_title("Validation")
    
    # save figure
    fig.autofmt_xdate()
    fig.savefig(os.path.join(fpath,"projects",fname_validation,"validation.png"),dpi=300)
    fig.clf()
    