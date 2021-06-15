# -*- coding: utf-8 -*-
"""
Created on Mon Jul  2 14:15:16 2018

@author: smh
"""

from datetime import datetime
import cmf


class ModelrunList():
    i=0
    def __init__(self,fpath):
        """
        Collection of modelrun defintions.
        
        The base .csv-file must have the following columns:
        name,begin,end,clim_start,clim_step,timestep_convert,timestep,separate_solver,threads,database
        
        name (string): name of subfolder which holds the modelrun.
        begin (string): begin simulation (%Y-%m-%dT%H:%M, eg 2001-01-31-T00:00)
        end (string): end simulation (%Y-%m-%dT%H:%M, eg 2001-01-31-T23:00)
        clim_step (string): start climate timeseries (%Y-%m-%dT%H:%M, eg 2001-01-31-T23:00)
        timestep_convert (double): Value which is used to convert plant water balance.
        timestep (string):  Timestep of model run, eg.g 'day' or 'hour'
        separate_solver (string): Indicating if water and solute solver should be separated, eg. 'False' or 'True'
        threads (int): Number of threads.
        database (string): path of results database; if empty, no database is written.

        """
        #read file
        f = open(fpath,"r")
        f = f.read()
        f = f.split("\n")[1:]
        if f[-1] == "": f=f[:-1]
        f = [tuple(i.split(",")) for i in  f]
        
        #iterate through file and generate modelruns
        self.data = []
        for rec in f:
            
            #get data
            fpath = rec[0]
            name = rec[1]
            begin = datetime.strptime(rec[2], "%Y-%m-%dT%H:%M")
            end = datetime.strptime(rec[3], "%Y-%m-%dT%H:%M")
            clim_start = datetime.strptime(rec[4], "%Y-%m-%dT%H:%M")
            if rec[5] == "day":                             
                clim_step = cmf.day
            elif rec[5] == "hour":
                clim_step = cmf.h
            if rec[6] == "day":                             
                timestep = cmf.day
                timestep_convert = 1
            elif rec[6] == "hour":
                timestep = cmf.h
                timestep_convert = 24
            separate_solver = eval(rec[7])
            threads = int(rec[8])
            database = rec[9]
            substance = rec[10]
            efate = rec[11]
            drift = rec[12]
            runtype = rec[13]
            
            #create modelrun
            mr = Modelrun(fpath,name,begin,end,clim_start,clim_step,timestep_convert,
                 timestep,separate_solver,threads,database,substance,efate,drift,runtype)
            self.data.append(mr)
    
    def __len__(self):
        return len(self.data)
    
    def __iter__(self):
        return self
    
    def __getitem__(self,val):
        return self.data[val]
    
    def __next__(self):
        if self.i < len(self.data):
            self.i += 1
            return self.data[self.i-1]
        else:
            raise StopIteration()        

class Modelrun():
    
    def __init__(self,fpath,name,begin,end,clim_start,clim_step,timestep_convert,
                 timestep,separate_solver,threads,database,substance,efate,drift,
                 runtype):
        self.fpath = fpath
        self.name = name
        self.begin = begin
        self.end = end
        self.clim_start = clim_start
        self.clim_step = clim_step
        self.timestep_convert = timestep_convert
        self.timestep = timestep
        self.separate_solver = separate_solver
        self.threads = threads
        self.database = database
        self.substance = substance
        self.efate = efate
        self.drift = drift   
        self.runtype = runtype