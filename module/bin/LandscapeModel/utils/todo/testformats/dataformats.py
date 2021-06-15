# -*- coding: utf-8 -*-
"""
Created on Tue Feb  5 16:25:32 2019

@author: smh
"""


import numpy as np
from datetime import datetime
from netCDF4 import Dataset
from datetime import datetime
from netCDF4 import num2date, date2num
import h5py

################################################################################
## create test data
dtype=[("key","U20"),("time","U20"),("val1","f4"),("val2","f4"),("val3","f4"),("val4","f4")]
data = np.empty([24*365],dtype=dtype)
data["key"] = "r123"
data["time"] = "2000-01-01T23:00"
data["val1"] = np.ones([len(data)])*np.random.rand()*10
data["val2"] = np.ones([len(data)])*np.random.rand()*10
data["val3"] = np.ones([len(data)])*np.random.rand()*10
data["val4"] = np.ones([len(data)])*np.random.rand()*10

################################################################################
## create npz
#start = datetime.now()
#np.savez("test_savez",data)
#print("test_savez",datetime.now()-start)
#
################################################################################
## create npz compressed
#start = datetime.now()
#np.savez_compressed("test_savez_compressed",data)
#print("test_savez_compressed",datetime.now()-start)
#
################################################################################
## create netcdf
#start = datetime.now()
# ## create new netcdf-file for climate data
#zlib=True
#nc = Dataset("test_netcdf.nc", "w", format="NETCDF4")
## create dimensions
#index = nc.createDimension("index", len(data))
#index = nc.createVariable("index","S20",("index",),zlib=zlib)
##index[:] = range(len(data))   
## add file info
#nc.description =""
#nc.history = ""
#nc.source =  ""
## add variables
#key = nc.createVariable("key","U20",("index",),zlib=zlib)
#time = nc.createVariable("time","U20",("index",),zlib=zlib)
#val1 = nc.createVariable("val1","f4",("index",),zlib=zlib)
#val2 = nc.createVariable("val2","f4",("index",),zlib=zlib)
#val3 = nc.createVariable("val3","f4",("index",),zlib=zlib)
#val4 = nc.createVariable("val4","f4",("index",),zlib=zlib)
#key[:] = data["key"][:]
#time[:] = data["time"][:]
#val1[:] = data["val1"][:]
#val2[:] = data["val2"][:]
#val3[:] = data["val3"][:]
#val4[:] = data["val4"][:]
#nc.close()
#print("test_netcdf",datetime.now()-start)
#
###############################################################################
# create hdf5
start = datetime.now()

dtype=[("key","S20"),("time","S20"),("val1","f4"),("val2","f4"),("val3","f4"),("val4","f4")]



data = data.astype(dtype)


f = h5py.File('test.hdf5', 'w')
dset = f.create_dataset("data", (len(data),), dtype=dtype)
#dset["key"] = data["key"]
#dset["time"] = data["time"]
#dset["time"] = data["val1"]
#dset["time"]= data["val2"]
#dset["time"]= data["val3"]
#dset["time"]= data["val4"]
dset[:]=data[:]



print("test_hdf5",datetime.now()-start)


f = h5py.File('test.hdf5', 'r')

################################################################################
## create csv
#start = datetime.now()
#f = open("test_csv.csv","w")
#s = "\n".join([",".join([str(val) for val in row]) for row in data]  )
#
#f.write(s)
#f.close()
#print("test_csv",datetime.now()-start)
#
#


#data_n = np.array([data,data,data],dtype=dtype)


##https://docs.python.org/3/library/string.html#format-specification-mini-language
#np.savetxt("test_numpy.csv",data_n,fmt='%s,%s,%.6f,%.6f,%.6f,%.6f', delimiter=',', newline='\n', header=",".join(data.dtype.names), footer='', comments='', encoding='latin1')

         


import numpy as np
import os

class NumpyDataFile():
    
    def __init__(self,data=None,fpath=None,fname=None,dtype=None,shape=None,
                 fmt=None,encoding='latin1'):
        """
        """
        self.fpath = fpath
        self.fname = fname
        self.data = data
        self.fmt=fmt
        self.encoding = encoding
        
        if self.data!=None:
            self.dtype=self.data.dtype
            self.shape = self.data.shape[0]
        else:
            self.dtype=dtype
            self.shape = shape
            
    def create(self,filetype,zipped,mmap_mode=None):
        """
        """
        fname = os.path.join(self.fpath,self.fname+"."+"npy")
        self.data = np.memmap(fname, dtype=self.dtype, mode='w+', shape=self.shape)
        self.data.flush()

        
    def load(self,filetype,zipped=None,mmap_mode=None):
        """
        
        mode : {‘r+’, ‘r’, ‘w+’, ‘c’}, optional

        The file is opened in this mode:
        ‘r’ 	Open existing file for reading only.
        ‘r+’ 	Open existing file for reading and writing.
        ‘w+’ 	Create or overwrite existing file for reading and writing.
        ‘c’ 	Copy-on-write: assignments affect data in memory, but changes are not saved to disk. The file on disk is read-only.
        
        """
        if filetype == "np":
            if zipped:
                ext = "npz"
            else:
                ext = "npy"
            fname = os.path.join(self.fpath,self.fname+"."+ext)
            self.data = np.load(fname,mmap_mode=mmap_mode, allow_pickle=True, 
                                fix_imports=True, encoding='ASCII')['arr_0']

        elif filetype == "csv":
            if zipped:
                ext = "csv"
            else:
                ext = "gz"   
            fname = os.path.join(self.fpath,self.fname+"."+ext)
            self.data = np.loadtxt(fname, dtype=self.dtype, comments='#', 
                                   delimiter=",", converters=None, 
                                   skiprows=1, usecols=None, 
                                   unpack=False, ndmin=0, 
                                   encoding=self.encoding)
            
    def save(self,filetype,zipped):
        """
        
        """
        
        if filetype == "np":
            
            if zipped:
                fname = os.path.join(self.fpath,self.fname+"."+"npz")
                np.savez_compressed(fname,self.data)
            else:
                fname = os.path.join(self.fpath,self.fname+"."+"npy")
                np.save(fname,self.data)
        elif filetype == "csv":
            header = header=",".join(self.data.dtype.names)
            if zipped:

                fname = os.path.join(self.fpath,self.fname+".gz")
                np.savetxt(fname,self.data,
                       fmt=self.fmt,newline='\n', 
                       header=header, comments='', 
                       encoding=self.encoding)
            else:
                fname = os.path.join(self.fpath,self.fname+"."+"csv")
                print(fname)
                np.savetxt(fname,self.data,
                           fmt=self.fmt,newline='\n', 
                           header=header, comments='', 
                           encoding=self.encoding)
    def flush(self):
        """
        """
        if type(self.data) == np.core.memmap:
            self.data.flush()
        else:
            print("no mempmap file")
    def zipfile(self):
        """
        """
        self.save("np",True)


                   


##############################################################################
# 1. create from existing numpy array, test read and write

## load exisitng  dataset 
#fpath='c:/LandscapeModel/CatchmentModel/LandscapeModel/utils/todo/test/'
#fname = "Rummen_reaches_small"
#dtype = [('name', '<U5'), ('time', '<U16'), ('depth', '<f4'), ('conc', '<f4'), ('load', '<f4'), ('artificialflux', '<f4'), ('volume', '<f4'), ('flow', '<f4'), ('area', '<f4'), ('MASS_SED', '<f4'), ('MASS_SED_DEEP', '<f4'), ('MASS_SW', '<f4'), ('PEC_SW', '<f4'), ('PEC_SED', '<f4')]
#reaches = np.loadtxt(fname+".csv", dtype=dtype, comments='#', delimiter=",", converters=None, skiprows=1, usecols=None, unpack=False, ndmin=0, encoding='bytes')
##
## create numpy data file
#
## test all variations to save data
#ndf = NumpyDataFile(data=reaches,fpath=fpath,fname=fname,
#                    fmt='%s,%s,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,')
#ndf.save("np",zipped=False)
#ndf.save("np",zipped=True)
#ndf.save("csv",zipped=False)
#ndf.save("csv",zipped=True)


## test all variations to load data
#ndf = NumpyDataFile(fpath=fpath,fname=fname,dtype=dtype,
#                    fmt='%s,%s,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,')
#ndf.load(filetype="np",zipped=True,mmap_mode="c")


# write a file line by line
#dtype = [('name', '<U5'), ('time', '<U16'), ('depth', '<f4'), ('volume', '<f4'), ('flow', '<f4'), ('area', '<f4')]


#
#ndf = NumpyDataFile(fpath=fpath,fname="test1",dtype=dtype,shape=24*365*1800)
#ndf.create("np",True,mmap_mode=None)
#
#
#


#
#
#ndf = NumpyDataFile(fpath=fpath,fname="test1",dtype=dtype,shape=24*365*1800*20)
#ndf.create(filetype="np",zipped=True,mmap_mode="r+")
#
#
#
#fp = np.memmap("test1.npy", dtype=dtype, mode='r+', shape=24*365*1800*20)
#
#np.savez_compressed("test1.npz",fp)
#


#size=100
################################################################################
## create netcdf
#start = datetime.now()
# ## create new netcdf-file for climate data
#zlib=True
#nc = Dataset("test_netcdf2.nc", "w", format="NETCDF4")
## create dimensions
#index = nc.createDimension("index", 100)
#index = nc.createVariable("index","S20",("index",),zlib=zlib)
##index[:] = range(len(data))   
## add file info
#nc.description =""
#nc.history = ""
#nc.source =  ""
## add variables
#key = nc.createVariable("key","S10",("index",),zlib=zlib)
#time = nc.createVariable("time","S10",("index",),zlib=zlib)
#val1 = nc.createVariable("val1","f8",("index",),zlib=zlib)
#val2 = nc.createVariable("val2","f8",("index",),zlib=zlib)
#val3 = nc.createVariable("val3","f8",("index",),zlib=zlib)
#val4 = nc.createVariable("val4","f8",("index",),zlib=zlib)
#data =  np.ones([size])*np.random.rand()*10
#key[:size] = np.array(["f" for f in data])
#time[:size] = np.array(["f" for f in data])
#val1[:size] = data
#val2[:size] = data
#val3[:size] =data
#val4[:size] =data
#nc.close()
#
#
#
#nc = Dataset("test_netcdf.nc", "r", format="NETCDF4")
## create dimensions
#
#








## create hdf5
#start = datetime.now()
#dtype=[("key","S20"),("time","S20"),("val1","f4"),("val2","f4"),("val3","f4"),("val4","f4")]
#f = h5py.File('test.hdf5', 'w')
#dset = f.create_dataset("data", (len(data),), dtype=dtype)
#dset["key"] = data["key"]
#dset["time"] = data["time"]
#dset["time"] = data["val1"]
#dset["time"]= data["val2"]
#dset["time"]= data["val3"]
#dset["time"]= data["val4"]
#f.close()
#print("test_hdf5",datetime.now()-start)
#
#
#
## create hdf5
#start = datetime.now()
#dtype=[("key","S20"),("time","S20"),("val1","f4"),("val2","f4"),("val3","f4"),("val4","f4")]
#f = h5py.File('test2.hdf5', 'w')
#dset = f.create_dataset("data", (len(data),), dtype=dtype)
#
#for r,rec in enumerate(data):
#
#    dset[r]["key"] = data[r]["key"]
#    dset[r]["time"] = data[r]["time"]
#    dset[r]["time"] = data[r]["val1"]
#    dset[r]["time"]= data[r]["val2"]
#    dset[r]["time"]= data[r]["val3"]
#    dset[r]["time"]= data[r]["val4"]
#    dset.flush()
#f.close()
#print("test_hdf5",datetime.now()-start)
#




################################################################################
## create netcdf
#start = datetime.now()
# ## create new netcdf-file for climate data
#zlib=True
#nc = Dataset("test_netcdf.nc", "w", format="NETCDF4")
## create dimensions
#index = nc.createDimension("index", len(data))
#index = nc.createVariable("index","S20",("index",),zlib=zlib)
##index[:] = range(len(data))   
## add file info
#nc.description =""
#nc.history = ""
#nc.source =  ""
## add variables
#key = nc.createVariable("key","U20",("index",),zlib=zlib)
#time = nc.createVariable("time","U20",("index",),zlib=zlib)
#val1 = nc.createVariable("val1","f4",("index",),zlib=zlib)
#val2 = nc.createVariable("val2","f4",("index",),zlib=zlib)
#val3 = nc.createVariable("val3","f4",("index",),zlib=zlib)
#val4 = nc.createVariable("val4","f4",("index",),zlib=zlib)
#key[:] = data["key"][:]
#time[:] = data["time"][:]
#val1[:] = data["val1"][:]
#val2[:] = data["val2"][:]
#val3[:] = data["val3"][:]
#val4[:] = data["val4"][:]
#nc.close()
#print("test_netcdf",datetime.now()-start)
#
#
#
#
################################################################################
## create netcdf
#start = datetime.now()
# ## create new netcdf-file for climate data
#zlib=True
#nc = Dataset("test_netcdf2.nc", "w", format="NETCDF4")
## create dimensions
#index = nc.createDimension("index", len(data))
#index = nc.createVariable("index","S20",("index",),zlib=zlib)
##index[:] = range(len(data))   
## add file info
#nc.description =""
#nc.history = ""
#nc.source =  ""
## add variables
#key = nc.createVariable("key","U20",("index",),zlib=zlib)
#time = nc.createVariable("time","U20",("index",),zlib=zlib)
#val1 = nc.createVariable("val1","f4",("index",),zlib=zlib)
#val2 = nc.createVariable("val2","f4",("index",),zlib=zlib)
#val3 = nc.createVariable("val3","f4",("index",),zlib=zlib)
#val4 = nc.createVariable("val4","f4",("index",),zlib=zlib)








