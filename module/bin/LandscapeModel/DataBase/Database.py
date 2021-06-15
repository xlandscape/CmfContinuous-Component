# -*- coding: utf-8 -*-
"""
Created on Wed Sep 13 11:36:06 2017

@author: smh
"""
import os
from datetime import datetime,timedelta
from xml.dom import minidom
import numpy as np
import LandscapeModel
import h5py
import math
import shutil
import fileinput

class Database(object):
    def __init__(self,catchment=None,modelrun=None):
        """
        """

        
        self.date_format="%Y-%m-%dT%H:%M"
        # check if catchment objects exists
        if catchment != None:
            self.catchment = catchment
            self.modelrun = self.catchment.modelrun
            self.fpath = os.path.join(self.modelrun.fpath,self.modelrun.key)
            self.inpD = self.catchment.inpData
        else:
            self.modelrun = modelrun
            self.fpath = os.path.join(self.modelrun.fpath,self.modelrun.key)
            self.inpD = LandscapeModel.utils.InputData(self.fpath)
       
        # set attributes
        self.createDatabase = self.catchment.createDatabase
        self.fname =  self.modelrun.key
        self.ext = self.modelrun.database
        
        # read xml
        xml_fpath=os.sep.join(os.path.abspath(__file__).split("\\")[:-1])
        self.xml =  self.__read_xml(xml_fpath,"database.xml")
                
        # check if cells are assessed
        self.hasCells = False
        if len(self.inpD.CellList)>0 and self.modelrun.runtype != "inStream":
            self.hasCells = True

        # check if cells are assessed
        self.hasPlants = False
        if len(self.inpD.CellList)>0 and self.modelrun.runtype != "inStream" and self.modelrun.runtype != "timeseriesCatchment" :
            self.hasPlants = True

        # check for deep aqufier
        self.hasDeepGW = False
        gwinfo = self.inpD.CatchmentList.getbyAttribute(self.fname ,"component","Groundwater")
        if len(gwinfo)>0: 
            self.hasDeepGW = True

        # get shape of time, cells and reaches
        begin  = self.modelrun.begin+timedelta(hours=1)
        end =  self.modelrun.end+timedelta(hours=1)
        self.daterange = [i for i in self.calc_daterange(begin, end)]
        self.nTimes = len(self.daterange)
        self.nCells = len(self.inpD.CellList)
        self.nReaches = len(self.inpD.ReachList)
        self.nLayer = len([i for i in self.inpD.SoilList if i.key == self.inpD.SoilList[0].key])
        
        # create filepaths
        self.create_filepaths()
        
        # create variables for output data tables
        self.cells = None
        self.plants = None
        self.outlets = None
        self.reaches = None
        self.gws = None
        
        # create column headinds
        self.create_columns()
        
        
        # create info for timeseries
        self.columns_ts_cells = self.xml_getValue(self.xml,"names","ts_cells").split(",")  
        self.columns_ts_reaches = self.xml_getValue(self.xml,"names","ts_reaches").split(",")  
        self.fmt_ts_cells =  self.xml_getValue(self.xml,"types","ts_cells").split(",")
        self.fmt_ts_reaches =  self.xml_getValue(self.xml,"types","ts_reaches").split(",")
        self.dtype_ts_cells = [(n,t) for n,t in zip(self.columns_ts_cells,self.fmt_ts_cells)]
        self.dtype_ts_reaches = [(n,t) for n,t in zip(self.columns_ts_reaches,self.fmt_ts_reaches)]
        
        #create indices
        self.index_cells = 0
        self.index_reaches = 0
        self.index_outlets = 0
        self.index_gws = 0

    def split(self,a, chunksize):
        """
        Allocates a set of a modelruns to n cores.
        a (int): count of records
        chunksize (int): number of itmes per chunk
        
        Returns (list):
        List with number of runs per sub-process.
        """
        n = int(a/chunksize)
        a=range(a)
        k, m = divmod(len(a), n)
        chunks =  list(a[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in iter(range(n)))    
        return chunks
        
    def calc_daterange(self,start_date, end_date):
        """
        """
        delta = timedelta(hours=1)
        while start_date < end_date:
            yield start_date
            start_date += delta    
    
    def create_filepaths(self):
        """
        """
        self.fpath_cells = os.path.join(self.fpath,self.fname + "_" + "cells")
        self.fpath_plants = os.path.join(self.fpath,self.fname + "_" + "plants")
        self.fpath_reaches = os.path.join(self.fpath,self.fname + "_" + "reaches")
        self.fpath_outlets = os.path.join(self.fpath,self.fname + "_" + "outlets")
        self.fpath_gws = os.path.join(self.fpath,self.fname + "_" + "gws")

    def __read_xml(self,fpath,fname):
        # parse an xml file by name
        mydoc = minidom.parse(os.path.join(fpath,fname))
        items = mydoc.getElementsByTagName('item')
        return items
    
    def xml_getValue(self,xml,attr,tbl):
        info=[i for i in xml if i.attributes["key"].value == tbl][0]
        return info.attributes[attr].value
        
    def create_columns(self):
        """
        """
       
        if self.hasCells:
            
            # cells header
            self.columns_cells =  self.xml_getValue(self.xml,"names","cells").split(",")  

            
            # cells format
            types_layer = ["f4" for i in range(self.nLayer)]
            self.fmt_cells =  self.xml_getValue(self.xml,"types","cells").split(",")  +types_layer+types_layer
           
            
            
            if self.modelrun.runtype == "completeCatchment":
                self.columns_cells += ["Vsoil_%i"%(i) for i in range(self.nLayer)]
                self.columns_cells += ["concsoil_%i"%(i) for i in range(self.nLayer)]
                self.fmt_cells += types_layer+types_layer
                self.dtype_cells = [(n,t) for n,t in zip(self.columns_cells,self.fmt_cells)]
            else:
                 self.dtype_cells = [(n,t) for n,t in zip(self.columns_cells,self.fmt_cells)]
            
            if self.hasPlants:
                # plant
                self.columns_plants = self.xml_getValue(self.xml,"names","plants").split(",")      
                self.columns_plants += ["waterabstraction_%i"%(i) for i in range(self.nLayer)]
                self.columns_plants += ["rootwateruptake_%i"%(i) for i in range(self.nLayer)]
                self.columns_plants += ["evaporation_%i"%(i) for i in range(self.nLayer)]
                self.columns_plants += ["rootdistribution_%i"%(i) for i in range(self.nLayer)]
                self.fmt_plants = self.xml_getValue(self.xml,"types","plants").split(",")+types_layer+types_layer+types_layer+types_layer
            


        # reaches
        self.columns_reaches = self.xml_getValue(self.xml,"names","reaches").split(",")  
        self.fmt_reaches = self.xml_getValue(self.xml,"types","reaches").split(",")
        self.dtype_reaches = [(n,t) for n,t in zip(self.columns_reaches,self.fmt_reaches)]
        
        # outlet
        self.columns_outlets = self.xml_getValue(self.xml,"names","outlets").split(",")  
        self.fmt_outlets = self.xml_getValue(self.xml,"types","outlets").split(",")  
        
        # deep groundwater
        self.columns_gws = self.xml_getValue(self.xml,"names","gws").split(",")  
        self.fmt_gws = self.xml_getValue(self.xml,"types","gws").split(",")  

        # create dtype
        
    def convert_fmt(self,fmt):
        """
        """
        fmt_indicator = [i for i in fmt if i.isalpha()][0]
        fmt_length = int("".join([i for i in fmt if i.isnumeric()]))
        
        s="%"
        # check for formattign symbols
        if (fmt_indicator == "S") or (fmt_indicator == "U"):
            s+="s"
        elif (fmt_indicator == "f") :
            s+= "f"
        elif (fmt_indicator == "i") :
            s+= "i"
        
        return s         
       

    
    def __convert_fmt(self,fmt):
        """
        """
        fmt_indicator = [i for i in fmt if i.isalpha()][0]
        fmt_length = int("".join([i for i in fmt if i.isnumeric()]))
        
        s="%"
        # check for formattign symbols
        if (fmt_indicator == "S") or (fmt_indicator == "U"):
            s+="s"
        elif (fmt_indicator == "f") :
            s+= "f"
        elif (fmt_indicator == "i") :
            s+= "i"
        
        return s    
    

    def append_files(self,src="",trg="",tbl=""):
        """
        
        """
    
      # get type and format
        if tbl == "cells":
            dtype = [(n,t) for n,t in zip(self.columns_cells,self.fmt_cells)]
            fmt = ",".join([self.__convert_fmt(i) for i in self.fmt_cells])
        elif tbl == "reaches":
            dtype = [(n,t) for n,t in zip(self.columns_reaches,self.fmt_reaches)]
            fmt = ",".join([self.__convert_fmt(i) for i in self.fmt_reaches])
        elif tbl == "plants":
            dtype = [(n,t) for n,t in zip(self.columns_plants,self.fmt_plants)]
            fmt = ",".join([self.__convert_fmt(i) for i in self.fmt_plants])
        elif tbl == "outlets":
            dtype = [(n,t) for n,t in zip(self.columns_outlets,self.fmt_outlets)]
            fmt = ",".join([self.__convert_fmt(i) for i in self.fmt_outlets])
        elif tbl == "gws":
            dtype = [(n,t) for n,t in zip(self.columns_gws,self.fmt_gws)]
            fmt = ",".join([self.__convert_fmt(i) for i in self.fmt_gws])

        # open source file
        fsrc=self.read_file(src+"."+self.ext,dtype=dtype,tablename=tbl)

        # open target file and append data
        if self.ext == "csv":
            
            trg = trg+"."+self.ext
            src = [src+"."+self.ext]
            
            with open(trg, 'a') as fout, fileinput.input(src) as fin:
                for line in fin:
                    if not fileinput.isfirstline():
                        fout.write(line)
            
            
        elif self.ext == "hdf":
            # open target file in append mode
            ftrg = h5py.File(trg+"."+self.ext, "a")
            dset = ftrg[tbl]
            # append and save            
            start = [i["key"] for i in dset].index(b'')
            end = start+len(fsrc)
            dset[start:end] = fsrc.astype(dset.dtype)
            ftrg.close()
            
    def write_file(self,fname,data,fmt="",header="",tablename=""):
            """
            """
            # csv file
            if self.ext == "csv":
                # convert format
                fmt = ",".join([self.__convert_fmt(i) for i in fmt])
                header = ".".join(header)
                # create types and load
                np.savetxt(fname,data,
                       fmt=fmt,newline='\n', 
                       header=header, comments='')

            # npy file
            elif self.ext == "npy":
                np.save(fname,data)
    
            # npz file
            elif self.ext == "npz":
                np.savez_compressed(fname,data)
                
            # hdf5
            elif self.ext == "hdf":
                self.__save_hdf(fname,data,fmt,header,tablename)
                
    def read_file(self,fname,dtype=None,tablename="",isTS=False,mode="r"):
        """
        """

        # open csv file
        if self.ext == "csv":
            # create types and load
            table = np.loadtxt(fname, dtype=dtype, comments='#', 
                                   delimiter=",", converters=None, 
                                   skiprows=1, usecols=None, 
                                   unpack=False, ndmin=0)

        # open npy file
        elif self.ext == "npy":
            # load
            table = np.load(fname)

        # open npz file
        elif self.ext == "npz":
            # load
            table = np.load(fname)["arr_0"]
            
        elif self.ext == "hdf":
            table = h5py.File(fname,mode)[tablename][:]
            # convert types from 'S' (HDF5 supported) to 'U' (UFT-32, numpy for Python3)
            if tablename == "reaches":
                if isTS:
                    table = table[self.columns_ts_reaches ]
                    table = table.astype(self.dtype_ts_reaches)
                else:
                    table = table.astype(self.dtype_reaches)
            elif tablename == "cells":
                if isTS:
                    table = table[self.columns_ts_cells]
                    table = table.astype(self.dtype_ts_cells)
                else:
                    table = table.astype(self.columns_cells)
        
        return table
    
    def strDate2pyDate(self,date_string,date_format="%Y-%m-%dT%H:%M"):
        return datetime.strptime(date_string,date_format)

    def load_timeseries(self,tablename,key):
        """
        """
        # get filename
        fname = os.path.join(self.fpath,"Timeseries",key+"."+self.ext)
        
        # get filetype
        if tablename == "reaches":
            
            return self.read_file(fname,self.dtype_ts_reaches,tablename,isTS=True)
        elif tablename == "cells":
            return self.read_file(fname,self.dtype_ts_cells,tablename,isTS=True)

    def copy_timeseries_to_file(self,tablename,key,dst_fpath,dst_fname):
        """
        """
        # get data
        fname = os.path.join(dst_fpath,dst_fname +"."+self.ext)
        data = self.get_data_by_key(tablename,key)
        if tablename == "reaches":
            fmt = self.fmt_ts_reaches
            header = self.columns_ts_reaches
            data = data[self.columns_ts_reaches]
            self.write_file(fname,data,fmt=fmt,header=header,tablename=tablename)
        elif tablename == "cells":
            fmt = self.fmt_ts_cells
            header = self.columns_ts_cells
            data = data[self.columns_ts_cells] 
            self.write_file(fname,data,fmt=fmt,header=header,tablename=tablename)
                
        
    def load(self,tablename):
        """
        """

        # get filename
        fname = os.path.join(self.fpath,self.fname+"_"+ tablename +"."+self.ext)

        # set table
        if tablename == "cells":
            dtype = [(n,t) for n,t in zip(self.columns_cells,self.fmt_cells)]
            table = self.read_file(fname,dtype,tablename)
            self.cells = table
        elif tablename == "reaches":
            dtype = [(n,t) for n,t in zip(self.columns_reaches,self.fmt_reaches)]
            table = self.read_file(fname,dtype,tablename)
            self.reaches = table
        elif tablename == "plants":
            dtype = [(n,t) for n,t in zip(self.columns_plants,self.fmt_plants)]
            table = self.read_file(fname,dtype,tablename)
            self.plants = table
        elif tablename == "outlets":
            dtype = [(n,t) for n,t in zip(self.columns_outlets,self.fmt_outlets)]
            table = self.reaf_file(fname,dtype,tablename)
            self.outlets = table
        elif tablename == "gws":
            dtype = [(n,t) for n,t in zip(self.columns_gws,self.fmt_gws)]
            table = self.read_file(fname,dtype,tablename)
            self.gws = table
    
        return table

    def get_data_by_key(self,tablename,key):
        """
        """
        
        if  self.ext == "hdf":
            table = None
        else:
            # set table
            if tablename == "cells":
                table = self.cells
            elif tablename == "reaches":
                table = self.reaches
            elif tablename == "plants":
                table = self.plants
            elif tablename == "outlets":
                table = self.outlets
            elif tablename == "gws":
                table = self.gws
            
        # load cells if needed
        if table == None or type(table)!=np.ndarray: 
            table = self.load(tablename)
        # return dataset
        return table[table["key"]==key]
    

#    def save(self,catchment):
#        """
#        """
#        
#        if self.modelrun.runtype == "completeCatchment":
#            
#            self.save_cells(catchment)
#            
#            
#            if self.hasPlants:
#                self.save_plants(catchment)
#            
#            self.index_cells += self.nCells 
#        
#        # save data
#        self.save_reaches(catchment)
#        self.save_outlet(catchment)
#        
#        if self.hasDeepGW:
#            self.save_gw(catchment)
#            self.index_gws += 1
#        
#        # set index
#        self.index_reaches += self.nReaches 
#        self.index_outlets += 1
#        
#        
#        # manage chunks
#        self.manage_chunks(catchment)
        
    def __save_hdf(self,fname,data,fmt,header,tablename):

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
        
        
    def finalize(self):
        """
        """ 
        pass
    
    def createFiles(self):
        """
        """
        pass
    
    def save_cells(self,catchment):
        """
        """
        pass
            
    def save_reaches(self,catchment):
        """
        """
        pass    

    def save_outlet(self,catchment):
        """
        """
        pass

    def save_gw(self,catchment):
        """
        """
        pass
 