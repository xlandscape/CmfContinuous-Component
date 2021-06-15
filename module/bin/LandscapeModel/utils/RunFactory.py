# -*- coding: utf-8 -*-
"""
Created on Wed Aug  8 09:55:38 2018

@author: smh
"""

import os
import subprocess    
from datetime import datetime
import LandscapeModel

class RunFactory(object):
    
    def __init__(self,fdir,fname):
        """
        fdir (string): path of project folder
        """
#        self.message("create runfactory: " + fdir)
        self.fdir = fdir
        self.fname = fname
        self.runlist = LandscapeModel.utils.ParameterList(self.fdir,self.fname,",")
        self.runs = []

    def setup(self,key="",printMessage=False,createDatabase=True,**kwargs):
        
        # get list with model runs
        if key != "" and key!="None":
            runs = [i for i in self.runlist if i.key  == key and i.simulate == True]
        else:
            runs = [i for i in self.runlist if i.simulate == True]  
    
        if len(runs)<1:
            raise ValueError("No valid run ID found")
    
        for run in runs: 
            if printMessage: self.message("# Create catchment")                     
            self.runs.append(LandscapeModel.Catchment(run,printMessage=printMessage,
                                                      createDatabase=createDatabase))
    
    def __call__(self,key="",printMessage=False,plotMap=False,**kwargs):  
        """
        Make a single model run with 'name' or comptue all runs listed in
        run List.
        """
        
        # get list with model runs
        if key != "" and key!="None":
            runs = [i for i in self.runlist if i.key  == key and i.simulation == True]
        else:
            runs = [i for i in self.runlist if i.simulation == True]  
    
        if len(runs)<1:
            
            self.message("simulation: no run to simulate")
            
        else:
            
            for run in runs: 
                
                if printMessage: self.message("simulation: create catchment")  
                print("project: ",run.key)
                self.runs.append(LandscapeModel.Catchment(run,printMessage=printMessage))
                
                if plotMap:
                    plot=LandscapeModel.utils.Plotting()
                    catchment = self.runs[-1]
                    plot.CatchmentMap(catchment,withnames=True,
                                      fpath=os.path.join(catchment.fpath,"Map.png"))
                if run.catchment_separation != True:
                    print("simulation: run",self.runs[-1].modelrun.key)
                    self.runs[-1](**kwargs)
    
                else:
                    print("simulation: separate",self.runs[-1].modelrun.key)                 
                    catchSep = LandscapeModel.utils.CatchmentSeparator(self.runs[-1])
                    catchSep()
                    catchSep.plotMap(fontsize=8,withnames=True)
                    print("simulation: run",self.runs[-1].modelrun.key)      
                    catchSep.run_SolverUnits()

    def preprocessing(self,key,
                      make_catchcon=False,
                      has_scenarios=False):
        """
        """
        # select specific key if needed
        if key != "" and key!="None":
            runs = [i for i in self.runlist if i.key  == key and i.preprocessing == True]
        else:
            runs = [i for i in self.runlist if i.preprocessing == True]
            
        # conduct pre-processing
        for run in runs:
            self.__preprocessing(run,make_catchcon,has_scenarios)
        
    def __preprocessing(self,run,
                        make_catchcon=False,
                        has_scenarios=False):
        """
        """
        key = run.key
        fpath_project = os.path.join(run.fpath,run.key)
        ###########################################################################
        # pre-processing
        
        if make_catchcon:
            # create connections between cells<>cells and cells<>reches
            catchcon = LandscapeModel.utils.PreProcessing.CatchmentConnector(
                                                            fpath_project,
                                                            simplify_connections=4,
                                                            connection_type="RO_GW")
            # plot results of connections
            catchcon.makePlot(os.path.join(fpath_project,"flow_network_voroni.png"),resX=100,resY=100,plotVoroni=True,
                            plotElevation=False,plot_simplified=True,fontsize=4,markersize=0.5)
            catchcon.makePlot(os.path.join(fpath_project,"flow_network.png"),resX=100,resY=100,plotVoroni=False,
                            plotElevation=True,plot_simplified=True,fontsize=4,markersize=0.5)
        
        # calculate area-weighted flow timeseries of reach each and create files
        if run.runtype == "inStream":
            ayc = LandscapeModel.utils.PreProcessing.AreaYieldCatchment(
                                                        run.fpath,
                                                        key,
                                                        frunlist=self.fname,
                                                        filetype = run.database,
                                                        time_format="%Y-%m-%dT%H:%M")
            
            data_resampled=ayc.create_timeseries(resample_rule="1H",
                                                 resample_type="interpolate")
        
            if has_scenarios:
                # create scenarios (365 days dry 10%-percentile, medium 50%-percentile and 
                # wet 90%-percentile year) and create files
                ayc.create_timeseries_scenarios(resample_rule="1H",
                                                 resample_type="interpolate")

    def postprocessing(self,key="None",**kwargs):
        """
        """
        # select specific key if needed
        if key != "" and key!="None":
            runs = [i for i in self.runlist if i.key  == key and i.postprocessing == True]
        else:
            runs = [i for i in self.runlist if i.postprocessing == True]
        # conduct post-processing
        for run in runs:
            self.__postprocessing(run,**kwargs)
        
    def __postprocessing(self,run,
                         stats = True,
                         zero_flow = True,
                         performance = False,
                         catchment_hydrology = False,
                         catchment_efate=False,
                         branch_hydrology_and_efate=False,
                         reach_hydrology_and_efate=False,
                         catchment_validation=False,
                         plot_percentile_over_time=False,
                         ):
        """
        Conducts post-processing.
        
        :param run: Modelrun settings related to runlist.csv
        :type run: modelrun
        
        :returns: - 
        :rtype: -
        """
        
        # create post-processing class
        pstPrc = LandscapeModel.utils.PostProcessing(os.path.join(run.fpath,run.key),
                                                     run.key,time_format="%Y-%m-%dT%H:%M")
    
        if stats:
            # calculate stats and save file
            stats = pstPrc.get_stats(stats= ['mean', 'median',"min","max"],
                          params=['depth', 'volume', 'flow', 'area'])
        
            # make plots
            pstPrc.map_stats(stats)
        
        # plot percentiles of variables
        if plot_percentile_over_time:
            pstPrc.plot_percentile_over_time(params=['depth', 'volume', 'flow', 'area'])
        
        if zero_flow:
            # get all reaches with at least one value with flow == 0 and make a plot.
            pstPrc.get_zero_flow_reaches(stats)
    
        if performance:
            # plot observed versus simulated flow
            pstPrc.performance("flow")
    
        if catchment_hydrology:
            # plot histogramm of hydrological parameter across catchment
            pstPrc.catchment_hydrology()
        
        if catchment_efate:
            # plot cumulative distribution function of PEC values across catchment
            pstPrc.catchment_efate(datetime(1900,5,10,10),[1,2,4,8,16,24],
                                   maxSW=.4,maxSED=.05)
    
        if branch_hydrology_and_efate:
            # plot 3-D plot of two reach variables, e.g. PEC_SW and flow
            pstPrc.branch_hydrology_and_efate("PEC_SW",
                                                   "PEC$_{SW}$ [$\mu$g L$^{-1}$]",
                                                   "flow",
                                                   "Flow [m³ sec$^{-1}$]",
                                                   reach_start="r1443",reach_end="r1438",
                                                   tstart = datetime(1900,5,2,8),
                                                   tend = datetime(1900,5,3,23),
                                                   tintverval = 4,
                                                   timescale="hourly",
                                                   vmin=None,vmax=None,fname="1")
        if reach_hydrology_and_efate:
            # plot resutls of single reach    
            pstPrc.reach_hydrology_and_efate("r1443",tstart=datetime(1900,5,2,8),
                                             tend=datetime(1900,5,3,23),
                                          ymax=[0.15,4,0.5,20],
                                          maxconc=5.,
                                          maxload=5.)  

        if catchment_validation:
            pstPrc.catchment_validation()

    def message(self,s):
        """
        Writes a user message.
        """
        print(s)

    def split(self,a, n):
        """
        Allocates a set of a modelruns to n cores.
        a (int): count of modelruns
        n (int): count of cores
        
        Returns (list):
        List with number of runs per sub-process.
        """
        k, m = divmod(len(a), n)
        return (a[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in iter(range(n)))

    def __create_batchfiles(self,ncores=2,pythonpath="",execute = True):
        """
        Creates a batch process to run several single projects in parallel. The
        batch process is governed by a master batch-file which calls 1 to n 
        slave - batch files. Each slave is run in its own separated process. A 
        slave itself contain 1 - n projects.
        
        ncores (int): Nubmer of cores available for modelling (= nubmer of slaves)
        pythonpath (string): path of python.exe
        execute (boolean): if True, the master batch-file is called with subpross.Popen
        """
        names = []
        filenames=[]
        for chunk in list(self.split(range(len(self.runList)), ncores)):
            batch = []
            batch.append("@echo off")
            if len(chunk)>0:
                for c in chunk:
                    filename = self.__getExecutable(self.fdir,self.runList[c].name)   
                    filenames.append(filename)
                    batch.append('call '+ pythonpath +' ' + '"' + self.fdir +os.sep+ filename + '"') 
                #create batch-file
                name = str(min(chunk)+1) + "_" + str(max(chunk)+1)
                f = open(os.path.join(self.fdir,"slave_" + name + ".cmd"),"w")
                f.write("\n".join(batch))
                f.close()                
                names.append(name)        

        # preapre master batch-file to start slaves
        #create master batch-self
        f = open(os.path.join(self.fdir,"master_run.cmd"),"w")
        f.write("\n".join(["start slave_" + name + ".cmd" for name in names]))
        f.close() 

        #make runs 
        if execute:
            os.chdir(self.fdir)
            process = subprocess.Popen(self.fdir + os.sep + "master_run.cmd", shell=True,  stdin=None, stdout=None, stderr=None, close_fds=True)
            out, err = process.communicate()
            process.wait()

    def __getExecutable(self,fdir,runname):
        s=[]
        s.append('import os')
        s.append('import LandscapeModel')
        s.append('if __name__ == "__main__":')
        s.append('\tfdir = os.sep.join(os.path.abspath(__file__).split(os.sep)[:-1])')
        s.append('\trunFactory = LandscapeModel.utils.RunFactory(fdir=r"'  + self.fdir + '",fname="' + self.fname +  '")')
        s.append('\trunFactory("' + runname + '")')
        s="\n".join(s)
        filename = "main_"+runname+".py"
        f = open(os.path.join(fdir,filename),"w")
        f.write(s)
        f.close()
        return filename
        
        