# -*- coding: utf-8 -*-
"""
Created on Wed Feb 27 11:50:16 2019

@author: smh
"""
# python native
import os

# other
import pandas as pd
import numpy as np
import h5py
from multiprocessing import Pool
import matplotlib.pylab as plt
import matplotlib.dates as mdates




class ParallelProcessing():
    
    def __init__(self,func,ParameterSet,ncores):
        """
        Create an objects which parallizes a function with Pool.
        """
        self.func=func
        self.ParameterSet = ParameterSet
        self.chunks = self.__split(len(self.ParameterSet), ncores)
        self.p = Pool(ncores)
        
    def __call__(self):
        """
        Make parallel processing.
        """
        self.p.starmap(self.func, zip(self.ParameterSet))

    def __split(self,a, n):
        """
        Allocates a set of a modelruns to n cores.
        a (int): count of modelruns
        n (int): count of cores
        
        Returns (list):
        List with number of runs per sub-process.
        """
        a=range(a)
        k, m = divmod(len(a), n)
        return list(a[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in iter(range(n)))


class ParameterSet():
    """
    Just an example as input for ParallelProcessing ...
    """
    def __init__(self,fpath,fname,vars_soillayer,vars_summary,varname_GrwLev,
                 varname_rel_output_layer,varname_rel_output_dep):
        self.fpath=fpath
        self.fname=fname
        self.vars_soillayer=vars_soillayer
        self.vars_summary=vars_summary
        self.varname_GrwLev=varname_GrwLev
        self.varname_rel_output_layer=varname_rel_output_layer
        self.varname_rel_output_dep=varname_rel_output_dep

class TimeSeries():
    """
    Set of generic functions for time series processing
    
    df.groupby(level=[1]).sum()
    
    
    
    """
    def resample(self,data,resample_rule="1H",resample_type="interpolate"):
        """
        """
        # resample to specific timestep by using interpolate or pad (same value)
        if resample_type == "interpolate":
            data_resample=data["flow"].resample(rule=resample_rule).interpolate()
        elif resample_type == "pad":
            data_resample=data["flow"].resample(rule=resample_rule).pad()
        # convert timeseries to data frame
        data_resample = pd.DataFrame(data_resample,columns=["flow"])

        return data_resample
    
    def select_timeperiod(self,data,start_date,end_date,time_format):
        """
        """
        data = data[(data.index >= start_date) & (data.index <= end_date)]
        return data

#   def get_stats(self,stats= ['mean', 'median',"min","max"],
#                  params=['depth', 'volume', 'flow', 'area']):
#        """
#        Calculates stats for a given set of paramter.
#        """
#        agg = dict([(par,stats) for par in params])
#        stats = self.simulated.groupby(["key"]).agg(agg)
#        stats.to_csv(os.path.join(self.fpath,"catchment_stats.csv"))
#        return stats
#
#    def select_by_indices(self,
#                          params = [""],
#                          times=slice(None),
#                          keys=slice(None)):
#        """
#        Select a set of paramter by time and key index.
#        """
#        return self.simulated.loc[(times,keys),params]
    
    
class IO():
    """
    Set of genenric functions for dat ainput/output
    """

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
        

    def save_csv(self,fname,data,fmt,header):
        """
        Saves a numpy file as csv
        """
        
        def convert_fmt(fmt):
            """
            """
            fmt_indicator = [i for i in fmt if i.isalpha()][0]
            
            s="%"
            # check for formattign symbols
            if (fmt_indicator == "S") or (fmt_indicator == "U"):
                s+="s"
            elif (fmt_indicator == "f") :
                s+= "f"
            elif (fmt_indicator == "i") :
                s+= "i"
            
            return s   
        
        
        # convert format
        fmt = ",".join([convert_fmt(i) for i in fmt])
        header = ",".join(header)
        # create types and load
        np.savetxt(fname,data,
               fmt=fmt,newline='\n', 
               header=header, comments='')
    
    
    def write_numpy_to_hdf(self,fname,data,fmt,header,tablename):
        """
        Saves a numpy file as hdf5.
        """
    
        # check if file exists and delete 
        if os.path.exists(fname): 
            f = h5py.File(fname, 'r+')
            f.close()
            os.remove(fname)
        fmt = [i.replace("U","S") for i in fmt]
        dtype = [(n,t) for n,t in zip(header,fmt)]
        f = h5py.File(fname, 'w')
        dset = f.create_dataset(tablename, (len(data),), dtype=dtype,
                                compression="gzip", compression_opts=4)
       
        for colname in header:
            dset[colname] = data[colname]
        f.close()

    def writeTextFile(self,s,fpath,mode="w"):
        """
        Writes a textile.
        
        Attributes:
        -----------
        s (str): text to write into file.
        fpath (str): Target directory.
        mode (str): new file with 'w'; append with 'a'        
        """
        f=open(fpath,mode)
        f.write(s)
        f.close()

class Plots():
    """
    """
    
    
    def figure_performance(self,time,observed,simulated,label,dateformat,fname=""):
        """
        Creates a timeseries chart with observed and simulated data as well
        as calculated various performance measures.
        """
        
#        def calc_stats(obs,sim):
#            # stats
#            r_squared = np.corrcoef(obs,sim)[0][1]**2
#            nse = 1 - (sum((obs-sim)**2)/sum((obs-np.mean(obs))**2))
#            rmse = np.sqrt(np.mean((sim-obs)**2))
#            pbias = (sum (sim-obs) / sum(obs) ) * 100
#            return r_squared,nse,rmse,pbias
#    
#        # calc performance
#        r_squared,nse,rmse,pbias = calc_stats(observed,simulated)
#        
        # create figure
        fig = plt.figure(figsize=[10,5])    
    
        # plot calibration
        host = fig.add_subplot(111)
    
        
        # plot observed and siulated values
        ax1, = host.plot(observed.index, observed,color="r", alpha=1,
                         linewidth=1,  marker="",label="observed")
        ax1, = host.plot(simulated.index, simulated,color="b", alpha=1,
                         linewidth=1,  marker="",label="simulated")
        
        # format axis
        host.set_ylabel(label)
        host.legend(loc=2)
        host.grid(True)
        host.xaxis.set_major_formatter(mdates.DateFormatter(dateformat))
        
#        # plot performance
#        host.text(0.2, 0.98, "r$^2:$%.2f\nnse:%.2f\nrmse:%.2f\npbias:%.2f"%(r_squared,nse,rmse,pbias), 
#                  horizontalalignment='left', 
#                  verticalalignment='top', transform=host.transAxes,
#                  fontsize=10,fontweight="bold")
#    
    
        # save figure
        fig.autofmt_xdate()
        fig.savefig(fname,dpi=300)
        fig.clf()
        
    def ax_hist(self,ax,data=[],colors=[],labels=[],xlabel="",text="",**kwargs):
        
        for dat,col,lab in zip(data,colors,labels):
            # make histogram
            ax.hist(dat,color=col,label=lab,**kwargs)
        ax.set_xlabel(xlabel)
        ax.text(.5,.95,text,fontweight="bold",
        horizontalalignment='center',
        transform=ax.transAxes)
        ax.legend(loc=1,bbox_to_anchor=(0.00, 0.5, 1., .102),fontsize="small")
        

class Example(TimeSeries,IO):
    
    def __init__(self):
        """
        """
        
        TimeSeries.__init__(self)
        IO.__init__(self)
        
    def test(self):
        """
        """
        # call function from sub-class Timeseries
        self.resample()


#if __name__ == "__main__":
#    
#        ###########################################################################
#        #  example
#        ex = Example()
#        ex.resample()
    
    
 