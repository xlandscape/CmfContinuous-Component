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
data = np.empty([24],dtype=dtype)
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
################################################################################
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
################################################################################
## create csv
#start = datetime.now()
#f = open("test_csv.csv","w")
#s = "\n".join([",".join([str(val) for val in row]) for row in data]  )
#
#f.write(s)
#f.close()
#print("test_csv",datetime.now()-start)




#data_n = np.array([data,data,data],dtype=dtype)



np.savetxt("test_numpy.txt",data,fmt='%s%s%.6f%.6f%.6f%.6f', delimiter=' ', newline='\n', header=",".join(data.dtype.names), footer='', comments='# ', encoding=None)







#If the filename ends in .gz, the file is automatically saved in compressed gzip format. loadtxt understands gzipped files transparently.




