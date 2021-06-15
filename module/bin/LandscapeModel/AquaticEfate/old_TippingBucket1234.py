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

class TippinBucket1234:
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
                                                     time_format="%Y-%m-%dT%H:%M")
        
        # select required data columns
        self.simulated  = self.simulated[["flow","volume","area"]]
        
        # get reahnames as list sorted 
        self.reachnames = list(self.simulated.index.levels[1])
        

        # get timestep and period
        t0 =        self.simulated.index.levels[0][0]
        t1 =        self.simulated.index.levels[0][1]
        tn =        self.simulated.index.levels[0][-1]    
        self.time = list(pd.date_range(start=t0,end=tn,freq="1Min"))
        self.dt = t1-t0
        
        # get number of timesteps and reaches
        self.n_reaches = self.simulated.index.levels[1].shape[0]
        self.n_time = len(self.time)
    
        # reshape hydrological input data
        self.flow = self.simulated.flow.values.reshape([self.n_time,self.n_reaches])
        self.flow = np.divide(self.flow,1440.) # scale flow in 3/day to to minutes
        self.vol = self.simulated.volume.values.reshape([self.n_time,self.n_reaches])
        self.wetarea = self.simulated.area.values.reshape([self.n_time,self.n_reaches])
    
        # get geometry    
        rl_sort =  self.reachlist.sort_values("key")
        self.length = self.get_flowwidths()
        self.width = np.ones([self.n_reaches],dtype=np.float32) *rl_sort.bottomwidth.values

        # create efate model
        self.efate = Steps1234(self.length,self.width,**kwargs)    
    
        # create state variables   
        self.temp = np.ones([self.n_time,self.n_reaches],dtype=np.float32) * 12 #TODO: use observed tempeature
        self.load_inflow = np.zeros([self.n_reaches],dtype=np.float32) 
        self.load_outflow = np.zeros([self.n_reaches],dtype=np.float32) 
        self.tb_mass = np.zeros([self.n_reaches],dtype=np.float32) 
    
        # set connections
        self.con = np.zeros([self.n_reaches,self.n_reaches],dtype=np.float32)
        self.create_cons()

        # variable for surface water
        self.input_sw = np.zeros([self.n_time,self.n_reaches],dtype=np.float32)
    
        # spray drift
        self.spraydrift = pd.read_csv(os.path.join(self.fpath,"SprayDriftList.csv"))
        self.create_spraydrift()
        
#        # create output variables
#        self.MASS_SW = np.zeros([self.n_time,self.n_reaches],dtype=np.float32)
#        self.MASS_SED = np.zeros([self.n_time,self.n_reaches],dtype=np.float32)
#        self.MASS_SED_DEEP = np.zeros([self.n_time,self.n_reaches],dtype=np.float32)
#        self.PEC_SW = np.zeros([self.n_time,self.n_reaches],dtype=np.float32)
#        self.PEC_SED = np.zeros([self.n_time,self.n_reaches],dtype=np.float32)


        print("create database")

        # create output parameter
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
        
        @TODO: A simple predictor - corrector solver. 
        
        
        """
        
        print("simulate")
        start = datetime.now()
        tout = 0
        dt_sub = int(self.dt.seconds / 60)
        
        # run simulation
        for t in range(self.n_time):
            
            # run simulation for timesteps smaller than dt input with same values
            for step in range(dt_sub):
            
                self.printout(t," input ",self.input_sw[t],printres)
                
                # 1. run steps1234
                self.efate(self.input_sw[t],self.tb_mass,self.temp[t],self.vol[t])
                
                # 2. set mass 
                self.tb_mass = self.efate.MASS_SW
                self.printout(t," cmp start ",self.efate.MASS_SW,printres)
        
                # 3. save results of current time step to memory
                self.save(t)
        
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
            i._mmap.close()
        
    def resample(self,rule="1Min"):
        """
        NOT USED
        """
        # upsample hours to minutes
        gb=self.simulated.groupby(level=["key"])
        res=gb.apply(lambda x: x.reset_index(level=["key"]).resample(rule="1Min").pad())
        self.simulated =res.swaplevel()[["flow","volume","area"]]
        
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
            tind = self.time.index(pd.Timestamp(event.time))
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
            if t % 60 == 0:
                for ds in self.db:
                    ds.flush()
            
            
#            
#        
#        
#        
#        self.MASS_SW[t] = self.efate.MASS_SW
#        self.MASS_SED[t] = self.efate.MASS_SED
#        self.MASS_SED_DEEP[t] = self.efate.MASS_SED_DEEP
#        self.PEC_SW[t] = self.efate.PEC_SW
#        self.PEC_SED[t] = self.efate.PEC_SED
#        
#        if t % 60 == 0:
#            self.MASS_SW.flush()
#            self.MASS_SED.flush()
#            self.MASS_SED_DEEP.flush()
#            self.PEC_SW.flush()
#            self.PEC_SED.flush()

#    def write(self,ftype):
#        """
#        """
#        
#        # create header
#        params = ["MASS_SW","MASS_SED","MASS_SED_DEEP","PEC_SW","PEC_SED"]
#        header = [par+"_"+ reach for par in params for reach in self.reachnames ]
#        
#        # read results
#        
#        
#        # concat data
##        res=np.hstack((self.MASS_SW,self.MASS_SED,self.MASS_SED_DEEP,self.PEC_SW,self.PEC_SED))
#        # get file name
#        
#        if ftype == "csv":
#            # save file
#            fname = os.path.join(self.fpath,"steps1234"+".csv")
#            np.savetxt(fname,res,fmt='%.4f', delimiter=',', newline='\n',
#                       header=",".join(header),)
#        elif ftype == "npz":
#            fname = os.path.join(self.fpath,"steps1234"+".npz")
#            np.savez_compressed(fname,res)
#        elif ftype == "npy":
#            fname = os.path.join(self.fpath,"steps1234"+".npy")
#            np.save(fname,res)
#
    
    def write_reach_file(self,withHydro=True):
        """
        
        mode : {‘r+’, ‘r’, ‘w+’, ‘c’}, optional

        The file is opened in this mode:
        ‘r’ 	Open existing file for reading only.
        ‘r+’ 	Open existing file for reading and writing.
        ‘w+’ 	Create or overwrite existing file for reading and writing.
        ‘c’ 	Copy-on-write: assignments affect data in memory, but changes are not saved to disk. The file on disk is read-only.
        
        
        """
        # create list with keys
        keys = np.array([(t,r) for r in self.reachnames for t in self.time])

        # read files
        self.MASS_SED = np.load(os.path.join(self.fpath,"steps_MASS_SED.npy"),
                                mmap_mode="r")['arr_0']
        self.MASS_SED_DEEP = np.load(os.path.join(self.fpath,"stepsMASS_SED_DEEP.npy"),
                                     mmap_mode="r")['arr_0']
        self.MASS_SW = np.load(os.path.join(self.fpath,"steps_MASS_SW.npy"),
                               mmap_mode="r")['arr_0']
        self.PEC_SW = np.load(os.path.join(self.fpath,"steps_PEC_SW.npy"),
                              mmap_mode="r")['arr_0']
        self.PEC_SED = np.load(os.path.join(self.fpath,"steps_PEC_SED.npy"),
                               mmap_mode="r")['arr_0']
    
        # create dataframe
        df = pd.DataFrame({'key':           keys[:,1],
                           'time':          keys[:,0],
                           'MASS_SED':      self.MASS_SED.T.flatten(),
                           'MASS_SED_DEEP': self.MASS_SED_DEEP.T.flatten(),
                           'MASS_SW':       self.MASS_SW.T.flatten(),
                           'PEC_SW':        self.PEC_SW.T.flatten(),
                           'PEC_SED':       self.PEC_SED.T.flatten()} )
        
        # set indices
        df.set_index(["time","key"],inplace=True)
        
        # sort data
        df.sort_index(level=[0], ascending=True,inplace=True)
         
        # join with hydro
        if withHydro:
            df = self.simulated.merge(df,left_index=True,right_index=True)
        

        # save to disk
        df.to_csv(os.path.join(self.fpath,"steps1234_reaches"+".csv"),
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
                           time_format="%Y-%m-%dT%H:%M"):
        
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
        data = pd.read_csv(fname)
        # create dattime from string
        if time_key != None:
            data ["time"]=pd.to_datetime(data [time_key],format=time_format)
        # set keys
        if keys != None:
            data.set_index(keys,inplace=True)
        return data


if __name__ == "__main__":
    
    fpath =  "c:/LandscapeModel2019/projects/Rummen_subCatch_20reaches/"
    key = "hydro_v01_medium_minute"
    filetype="csv"

    # create model    
    tb1234 = TippinBucket1234(fpath,key,filetype,
                             DEGHL_SW_0=1000,DEGHL_SED_0=43.9,KOC=1024000,Temp0=21.,Q10=2.2,
                             DENS=0.8,POROSITY=0.6,OC=0.05,DEPTH_SED=0.05, DEPTH_SED_DEEP=0.45,
                             DIFF_L_SED=0.005,DIFF_L=0.005,DIFF_W=4.3*(10**-5),
                             convertDeltaT=24.*60) # the DT values are per day, so convert to minutes

    # make model run
    tb1234(printres=False)
            
    # write to disk
    print("write results to disk")
    #tb1234.write(ftype="npy")

    #df=tb1234.write_reach_file()
















