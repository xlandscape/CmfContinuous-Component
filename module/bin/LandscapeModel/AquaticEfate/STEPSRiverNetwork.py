# -*- coding: utf-8 -*-
"""
Created on Wed May 30 10:12:48 2018

@author: smh
"""

import h5py
import numpy as np
import pandas as pd
import os

from datetime import datetime
from Steps1234 import Steps1234

class STEPSRiverNetwork:
    """
    
    
    The model operates on a minute timestep. Input data must have dt<=1min.
    If input data dt is houry or daily, input values are repeated to resample
    the input values to minutes.
    """
    
    def __init__(self,fpath:str,
                 key:str,
                 filetype:str="csv",
                 db_pars:list= ["MASS_SW","MASS_SED","MASS_SED_DEEP",
                               "PEC_SW","PEC_SED"],
                 **kwargs):
        
        self.fpath = os.path.join(fpath,key)
        self.key = key
        self.filetype = filetype

        # load reach and catchment list
        self.reachlist = pd.read_csv(os.path.join(self.fpath,"ReachList.csv"))
        self.catchmentlist = pd.read_csv(os.path.join(self.fpath,"CatchmentList.csv"))
        
        # load hydrological input data
        fpath = os.path.join(self.fpath,self.key+"_reaches."+self.filetype)
        if self.filetype == "hdf":
           
            # read hdf
            self.simulated =self.read_hdf_to_pandas(fpath,
                                                    keys=["time","key"], 
                                                    dset="reaches",
                                                    time_key="time",
                                                    time_format="%Y-%m-%dT%H:%M",
                                                    convert_byte=["time","key"])
        elif self.filetype == "csv":
            #read csv
            self.simulated = self.read_csv_to_pandas(fpath,
                                                     keys=["time","key"],
                                                     time_key="time",
                                                     time_format="%Y-%m-%dT%H:%M",
                                                     usecols = ["time","key",
                                                                "flow","volume",
                                                                "area","depth"])
#        # upsample hours to minutes
#        gb=self.simulated.groupby(level=["key"])
#        res=gb.apply(lambda x: x.reset_index(level=["key"]).resample(rule="1Min").pad())
#        self.simulated =res.swaplevel()[["flow","volume","area"]]
        
        # get reahnames as list sorted 
        self.reachnames = list(self.simulated.index.levels[1])
        

        # get timestep and period
        self.t0 =        self.simulated.index.levels[0][0]
        self.t1 =        self.simulated.index.levels[0][1]
        self.tn =        self.simulated.index.levels[0][-1]  
        self.dt = self.t1-self.t0
        # if hourly, extent from 23:00 to 23:59
        if self.dt.seconds == 3600:
            self.tn = pd.Timestamp(year=self.tn.year,month=self.tn.month,
                                   day=self.tn.day,hour=self.tn.hour,
                                   minute=59)

        # crerate time index of output
        self.time = list(pd.date_range(start=self.t0,end=self.tn,freq="1Min"))
        self.n_time = len(self.time)
        
        # get number of timesteps and reaches
        self.n_reaches = self.simulated.index.levels[1].shape[0]
        self.n_time_input = self.simulated.index.levels[0].shape[0]#len(self.time)
        self.time_input = list(self.simulated.index.levels[0])
    
        # reshape hydrological input data
        self.flow = self.simulated.flow.values.reshape([self.n_time_input,self.n_reaches])
        self.flow = np.divide(self.flow,1440.) # scale flow in 3/day to to minutes
        self.vol = self.simulated.volume.values.reshape([self.n_time_input,self.n_reaches])
        self.wetarea = self.simulated.area.values.reshape([self.n_time_input,self.n_reaches])
        self.temp = np.ones([self.n_time_input,self.n_reaches],
                            dtype=np.float32) * 12 #TODO: use observed temperature
    
        # variable input solutes sw
        self.input_sw = np.zeros([self.n_time_input,self.n_reaches],dtype=np.float32)
    
        # spray drift
        self.spraydrift = pd.read_csv(os.path.join(self.fpath,"SprayDriftList.csv"))
        self.create_spraydrift()    
    
        # get geometry    
        rl_sort =  self.reachlist.sort_values("key")
        self.length = self.get_flowwidths()
        self.width = np.ones([self.n_reaches],dtype=np.float32) *rl_sort.bottomwidth.values

        # create efate model
        self.efate = Steps1234(self.length,self.width,**kwargs)    
    
        # set connections
        self.con = np.zeros([self.n_reaches,self.n_reaches],dtype=np.float32)
        self.create_cons()

        # create state variables   
        self.load_inflow = np.zeros([self.n_reaches],dtype=np.float32) 
        self.load_outflow = np.zeros([self.n_reaches],dtype=np.float32) 
        self.tb_mass = np.zeros([self.n_reaches],dtype=np.float32)     

        # create database
        self.db_pars = db_pars
        self.db_dirs= [os.path.join(self.fpath,"steps_"+f+".npy") for f in self.db_pars]
        self.db=[]
        
        # create db, delete existing files
        for f in self.db_dirs: 
            if os.path.isfile(f): 
                os.remove(f)
            npy = np.memmap(f,mode="w+",dtype=np.float32,
                            shape=(self.n_time,self.n_reaches))
            npy.flush()
            self.db.append(npy)
        
    def printout(self,t:int,s:str,vals:np.ndarray, printres:bool=False):
        if printres:
            return print(str(t)+ s + " ".join(["%.4f"%(i) for i in vals]))
        
    def __call__(self,printres:bool=False):
        """

        
        """
        
        print("simulate")
        start = datetime.now()
        tout = 0
        dt_sub = int(self.dt.seconds / 60)
        
        
        input_sw_at_zero = np.zeros(self.input_sw[0].shape,dtype=np.float32) 
        
        # run simulation
        for t in range(self.n_time_input):
            
            
            input_sw_at_t = self.input_sw[t]
            
            # run simulation for timesteps smaller than dt input with same values
            for step in range(dt_sub):
                
                print(self.time_input[t],self.time[tout])
            
                self.printout(t," input ",self.input_sw[t],printres)
                
                # 1. run steps1234
                self.efate(input_sw_at_t,self.tb_mass,
                           self.temp[t],self.vol[t])
                
                #set input to zero
                input_sw_at_t = input_sw_at_zero
                
                # 2. set mass 
                self.tb_mass = self.efate.MASS_SW
                self.printout(t," cmp start ",self.efate.MASS_SW,printres)
        
                # 3. save results of current time step to memory
                self.save(tout)
        
                # 4. Calculate laod of reach outflow
                self.load_outflow = self.efate.PEC_SW * self.flow[t]
                self.printout(t," cmp out ",self.load_outflow,printres)
        
                # 5. Substract outflow
                self.tb_mass -= self.load_outflow
        
                # 6. Sum up outflow loads as inflow for each reach according to connections 
                self.load_inflow = np.sum(self.con * self.load_outflow,axis=1)
                
                # 7. Add inflow
                self.tb_mass += self.load_inflow
                self.printout(t," cmp next ",self.tb_mass,printres)

                tout += 1

        # print runtime
        print(datetime.now()-start)  
        
        print("close database")
        
        # final flush
        for i in self.db:
            i.flush()
 
    def close_db(self):
        for i in self.db:
            i.flush()
            i._mmap.close()
        
    def get_flowwidths(self):
        """
        """        
        rl_sort =  self.reachlist.sort_values("key")
        outlet=self.catchmentlist[self.catchmentlist.component=="Outlet"]

        flowwidth = []
        for i in range(len(rl_sort)):         
            reach = rl_sort.iloc[i]
            
            # get coords
            x1 = reach.x
            y1 = reach.y
            z1 = reach.z
            if reach.downstream == "Outlet":
                x2 = outlet.x.values[0]
                y2= outlet.y.values[0]
                z2 = outlet.z.values[0]
            else:
                x2 = rl_sort[rl_sort["key"]==reach.downstream].x.values[0]
                y2 = rl_sort[rl_sort["key"]==reach.downstream].y.values[0]
                z2 = rl_sort[rl_sort["key"]==reach.downstream].z.values[0]

                #calculate flow width               
            flowwidth.append(np.sqrt((x2-x1)**2 + (y2-y1)**2 + (z2-z1)**2))
        return np.array(flowwidth,dtype=np.float32)
        
    def create_spraydrift(self):
        """
        """
        
        # set connections
        for i in range(len(self.spraydrift)):    
            event = self.spraydrift.iloc[i]
            # get reach index
            rind = self.reachnames.index(event.key)
            # get time index
            tind = self.time_input.index(pd.Timestamp(event.time))
            self.input_sw[tind,rind] = event.rate
        # multiply with wet area
        self.input_sw *= self.wetarea    

    def create_cons(self):
        """
        """
        # set connections
        for i,name in enumerate(self.reachnames):    
            # get inflow from others
            inflow = self.reachlist[self.reachlist.downstream==name].key.values
            # get index of inflows
            inflow_ind = [self.reachnames.index(reach) for reach in inflow]
            #set connection
            for ind in inflow_ind:
                self.con[i,ind]=1
        
    def save(self,t):
        """
        """
        for par,ds in zip(self.db_pars,self.db):
            ds[t] = vars(self.efate)[par]
            if t % 3600 == 0:
                for ds in self.db:
                    ds.flush()
            
    def write_reach_file(self,withHydro=False,agg=None,rule="1H"):
        """    
        """
        
        # create list with keys
        keys = np.array([(t,r) for r in self.reachnames for t in self.time])

        # create dataframe
        df = pd.DataFrame()
        df["key"] = keys[:,1]
        df["time"] = keys[:,0]
        for par,ds in zip(self.db_pars,self.db):
            df[par] = ds.T.flatten()

        # set indices
        df.set_index(["time","key"],inplace=True)
        
        # aggregate
        if agg!=None:
            gb=df.groupby(level=["key"])
            
            if agg == "min":
                df=gb.apply(lambda x: x.reset_index(level=["key"]).resample(rule=rule).pad())

            elif agg == "max":
                df=gb.apply(lambda x: x.reset_index(level=["key"]).resample(rule=rule).max())

            elif agg == "mean":
                df=gb.apply(lambda x: x.reset_index(level=["key"]).resample(rule=rule).mean())
            
            df=df.swaplevel()[["MASS_SW","MASS_SED","MASS_SED_DEEP","PEC_SW","PEC_SED"]]
            agg = "_"+agg

        
        # sort data
        df.sort_index(level=[0], ascending=True,inplace=True)
         
        # join with hydro
        if withHydro:
            print("merge")
            df = self.simulated.merge(df,left_index=True,right_index=True)
        
        # save to disk
        df.to_csv(os.path.join(self.fpath,"steps_reaches"+agg+".csv"),
                  date_format="%Y-%m-%dT%H:%M")
        
        return df

    def read_hdf_to_pandas(self,fname="",keys=None, 
                           dset=None,
                           time_key=None,
                           time_format="%Y-%m-%dT%H:%M",
                           convert_byte=None):
        """
        Reads a hdf5 file with h5py and returns pandas dataframe.

        By defining a keys and/or a time_key and index is established and
        string-dates are converted to datetime.
        convert_byte is a variable for a workaround of a datatype issue between
        Python3 numpy and h5py.

        :param fname: Path and name of file with extention.
        :type fname: str
        :param keys: List with keys.
        :type keys: list(str)        
        :param dset: Name of dataset in hdf5 file.
        :type keys: str  
        :param time_key: Name of time key.
        :type time_key: str        
        :param time_format: Datetime format, e.g."%Y-%m-%dT%H:%M".
        :type time_format: str        
        :param convert_byte: Variables where fomrat must be converted..
        :type convert_byte: list(str)   
        
        :returns: Data frame
        :rtype: pandas.DataFrame        
        """
        # read hdf and extract all data into numpy array
        npy = h5py.File(fname, 'r')[dset][:]
        # create DataFrame from numpy arra
        data = pd.DataFrame(npy)
        # convert byte-string to strings @TODO: slow
        for par in convert_byte:
            data[par]= data[par].apply(lambda x: str(x,'utf-8'))
        # convert time string to datetime objects
        if time_key != None:
            data ["time"]=pd.to_datetime(data [time_key],format=time_format)
        # set keys
        if keys != None:
            data.set_index(keys,inplace=True)
        return data
        
    def read_csv_to_pandas(self,fname="",keys=None,time_key=None,
                           time_format="%Y-%m-%dT%H:%M",**kwargs):
        
        """
        Reads a csv file with h5py and returns pandas dataframe.
    
        By defining a keys and/or a time_key and index is established and
        string-dates are converted to datetime.
        convert_byte is a variable for a workaround of a datatype issue between
        Python3 numpy and h5py.
    
        :param fname: Path and name of file with extention.
        :type fname: str
        :param keys: List with keys.
        :type keys: list(str)        
        :param time_key: Name of time key.
        :type time_key: str        
        :param time_format: Datetime format, e.g."%Y-%m-%dT%H:%M".
        :type time_format: str        
        
        :returns: Data frame
        :rtype: pandas.DataFrame        
        """
        # read file
        data = pd.read_csv(fname,**kwargs)
        # create dattime from string
        if time_key != None:
            data ["time"]=pd.to_datetime(data [time_key],format=time_format)
        # set keys
        if keys != None:
            data.set_index(keys,inplace=True)
        return data    