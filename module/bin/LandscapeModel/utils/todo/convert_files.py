# -*- coding: utf-8 -*-
"""
Created on Tue Feb 26 10:05:51 2019

@author: smh
"""

def save_hdf(fname,data,fmt,header,tablename):

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

def read_hdf(fname,tablename):  
    return h5py.File(fname, 'r')[tablename]
    
        
import os
import numpy as np 
import h5py
from numpy.lib.recfunctions import append_fields

###############################################################################
## convert reach
#
## source path
#src = "c:/LandscapeModel2019/projects/test_csv_separated_inStream/Timeseries/"
#
## target path
##trg = "n:/MOD/108604_LandscapeModelling/_mod/CaseStudies/2019_DLTpome_Rummen/LandscapeModel2019/projects/areayieldCatchment/TimeSeries/"
#trg = "c:/LandscapeModel2019/projects/test_hdf_separated_inStream/Timeseries/"
#
## list files
#files = os.listdir(src)
#
## convert all fules
##fname = files[0]
#for fname in files:
#    
#    if not  os.path.exists(os.path.join(trg,fname.split(".")[0]+".csv")):
#        print(fname)
#        
#        # open file with numpy
#        src_dtype = [("key","U10"),("time","U16"),("flow","f4"),("conc","f4")]#[("key","U10"),("time","U16"),("flow_m3day","f4")]
#        table = np.loadtxt(os.path.join(src,fname), dtype=src_dtype, comments='#', 
#                           delimiter=",", converters=None, 
#                           skiprows=1, usecols=None, 
#                           unpack=False, ndmin=0)
#        
#        # append missing columns, because old version of timeseries had no column 'conc'
##        table = append_fields(table, 'conc', np.zeros([len(table)],dtype="f4"))
##        table = table.astype( [("key","U10"),("time","U16"),("flow","f4"),("conc","f4")])
##        table = table.data[1:]
#        
##        # creaty NPY
##        np.save(os.path.join(trg,fname.split(".")[0]+".npy"),table)
##        
##        # creaty NPZ
##        np.savez(os.path.join(trg,fname.split(".")[0]+".npz"),table)
##        
##        # create CSV 
##        np.savetxt(os.path.join(trg,fname.split(".")[0]+".csv"),table,
##               fmt="%s,%s,%f,%f",newline='\n', 
##               header="key,time,flow,conc", comments='')
#        
#        # save hdf
#        save_hdf(os.path.join(trg,fname.split(".")[0]+".hdf"),table,["U10","U16","f4","f4"],
#                 ["key","time","flow","conc"],"reaches")


##############################################################################
# convert cell
        


src = "c:/_CatchmentModel_v093/projects/experiments/landscapeyieldCatchment/Rummen_subCatch_Velm/Timeseries/"
trg = "c:/_CatchmentModel_v093/projects/experiments/landscapeyieldCatchment/Rummen_subCatch_Velm/Timeseries_hdf/"


# list files
files = os.listdir(src)

for fname in files:
    print(fname)
  
    dtype=[('key', 'U10'), ('time', 'U16'), ('qperc', '<f8'), ('qsurf', '<f8'), ('qdrain', '<f8'), ('concgw', '<f8'), ('concsw', '<f8'), ('concdrainage', '<f8')]
    table = np.loadtxt(os.path.join(src,fname),dtype=dtype,  comments='#', 
                               delimiter=",", converters=None, 
                               skiprows=1, usecols=None, 
                               unpack=False, ndmin=0)

#    # create CSV 
#    np.savetxt(os.path.join(trg,fname.split(".")[0]+".csv"),table,
#           fmt="%s,%s,%f,%f,%f,%f,%f,%f",newline='\n', 
#           header='key,time,qperc,qsurf,qdrain,concgw,concsw,concdrainage', comments='')
    
    # save hdf
    save_hdf(fname=os.path.join(trg,fname.split(".")[0]+".hdf"),data=table,fmt=["U10","U16","f4","f4","f4","f4","f4","f4"],
             header=['key', 'time', 'qperc', 'qsurf', 'qdrain', 'concgw', 'concsw', 'concdrainage'],tablename="cells")
    
