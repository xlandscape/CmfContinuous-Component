# -*- coding: utf-8 -*-
"""
Created on Wed Sep 13 11:36:06 2017

@author: smh
"""


from .Database import Database
import numpy as np
from datetime import timedelta
import h5py
import os


class Database_HDF(Database):
    def __init__(self,catchment=None,fpath="",fname="",ext=""):
        """
        """
        
        #init core class
        Database.__init__(self, catchment)


        # create variables for data chunks
        self.chunks = None
        self.chunks_new = None
        self.chunksize = self.catchment.modelrun.chunksize

        if self.chunksize>0:
            # divide the dataseries into several chunks
            self.chunks = self.split(self.nTimes,self.chunksize)
            self.chunks = [[i for i in chunk] for chunk in self.chunks]
            self.chunks_new =  [max(i) for i in self.chunks]

        # convert byte-strign to string because bo support form h5py
        if self.hasCells:
            self.fmt_cells = [i.replace("U","S") for i in self.fmt_cells]
            
            if self.hasPlants:
                self.fmt_plants = [i.replace("U","S") for i in self.fmt_plants]
                
        # create files
                
        if self.createDatabase :
        
            self.createFiles()
        
        # create empty HDF5 on disk
                
        if self.createDatabase :
        
            self.create_HDF5_disk()
        
        
    def create_HDF5_disk(self):
        
        self.createDatabase 
        
        if self.hasCells:
            # cells
            self.__create_hdf(self.fpath_cells+"."+self.ext,self.nCells*self.nTimes,
                            self.fmt_cells,self.columns_cells,"cells")
            if self.hasPlants:
                # plants
                self.__create_hdf(self.fpath_plants+"."+self.ext,self.nCells*self.nTimes,
                    self.fmt_plants,self.columns_plants,"plants")
  
        # outlets
        self.__create_hdf(self.fpath_outlets+"."+self.ext,self.nTimes,
                self.fmt_outlets,self.columns_outlets,"outlets")
        
        # reaches
        self.__create_hdf(self.fpath_reaches+"."+self.ext,self.nTimes*self.nReaches,
                self.fmt_reaches,self.columns_reaches,"reaches")
        
        # gws
        self.__create_hdf(self.fpath_gws+"."+self.ext,self.nTimes,
                self.fmt_gws,self.columns_gws,"gws")

    def createFiles(self):
        """
        """
        
        # get size of datachunk related to time period
        if self.chunks != None:
            nTimes = self.chunks[0][-1]-self.chunks[0][0] + 1
        else:
            nTimes = self.nTimes
    
        # create files        
        if self.hasCells:
            
            # create npy cells
            dtype = [(n,t) for n,t in zip(self.columns_cells,self.fmt_cells)]
            self.cells = np.empty([(self.nCells*nTimes)],dtype)

            if self.hasPlants:
                # create npy plants
                dtype = [(n,t) for n,t in zip(self.columns_plants,self.fmt_plants)]
                self.plants = np.empty([(self.nCells*nTimes)],dtype) 
            
        # create npy reaches
        dtype = [(n,t) for n,t in zip(self.columns_reaches,self.fmt_reaches)]
        self.reaches = np.empty([(self.nReaches*nTimes)],dtype)
        
        # create npy outlets
        dtype = [(n,t) for n,t in zip(self.columns_outlets,self.fmt_outlets)]
        self.outlets = np.empty([nTimes],dtype)
   
        # create npy deep groundwater
        dtype = [(n,t) for n,t in zip(self.columns_gws,self.fmt_gws)]
        self.gws = np.empty([nTimes],dtype)              
#            
    def save_cells(self,catchment):
        """
        """
        time = catchment.timestring
        for i,f in enumerate(catchment.fields):     

            
            if self.modelrun.runtype == "completeCatchment":
            # get data
                rec = [f.key,time,f.cmf1d.qperc,f.cmf1d.qsurf,f.cmf1d.qdrain,
                       f.cmf1d.qgw_river,f.cmf1d.qgw_gw,f.cmf1d.Vsw,f.cmf1d.Vgw,
                       f.cmf1d.Vdr,f.cmf1d.get_rain(), f.cmf1d.concgw,
                       f.cmf1d.concsw,f.cmf1d.concdrainage]+f.cmf1d.Vsoil+f.cmf1d.concsoil
                       
            elif self.modelrun.runtype == "timeseriesCatchment":
                rec = [f.key,time,0,f.cmf1d.qsurf,f.cmf1d.qdrain,
                       f.cmf1d.qgw_river,f.cmf1d.qgw_gw,f.cmf1d.Vsw,f.cmf1d.Vgw,
                       f.cmf1d.Vdr,f.cmf1d.get_rain(), f.cmf1d.concgw,
                       f.cmf1d.concsw,f.cmf1d.concdrainage]
               
               
               
            # write data
            self.cells[self.index_cells+i] = tuple(rec)
            
    def save_plants(self,catchment):
        """
        """
        time = catchment.timestring
        for i,f in enumerate(catchment.fields):   
            
            # get data
            name = f.key
            das = f.plant.DAS
            rootdepth = f.plant.RootingDepth
            height = f.plant.Height
            LAI = f.plant.LAI
            GLAI = f.plant.GLAI
            if f.plantmodel == "macro":
                Epot =f.plant.Epot
                Tpot = f.plant.Tpot
                Eact = f.plant.Eact
                Tact =f.plant.Tact
                soil_waterabstraction = f.plant.SoilWaterExtraction
                soil_rootwateruptake = f.plant.SoilRootWaterUptake
                soil_evaporation = f.plant.SoilEvaporation
                rootdistribution = f.plant.RootDistribution
            elif f.plantmodel == "cmf":
                Eact = f.cmf1d.Eact
                Tact =f.cmf1d.Tact
                Epot = 0
                Tpot =0
                soil_waterabstraction =[0. for i in  f.cmf1d.c.layers]
                soil_rootwateruptake = [0. for i in  f.cmf1d.c.layers]
                soil_evaporation = [0. for i in  f.cmf1d.c.layers]
                rootdistribution = [0. for i in  f.cmf1d.c.layers]
            rec = [name,time,das,rootdepth,height,LAI,GLAI,Epot,Eact,Tpot,Tact]+ soil_waterabstraction  + soil_rootwateruptake  +soil_evaporation+rootdistribution 

            # write data
            self.plants[self.index_cells+i] = tuple(rec)

    def save_reaches(self,catchment):
        """
        """

        time = catchment.timestring
        for i,r in enumerate(catchment.reaches):
            
            # get data
            rec = [r.Name,time,r.Depth,r.Conc,r.Load,r.ArtificialFlux,r.Volume,r.Flow,
                   r.Area,r.MASS_SED,r.MASS_SED_DEEP,r.MASS_SW,
                   r.PEC_SW,r.PEC_SED]
            
            # write data
            self.reaches[self.index_reaches+i] = tuple(rec)

    def save_outlet(self,catchment):
        """
        """
        
        # get data
        time = catchment.timestring
        name = catchment.outlet.Name
        volume = catchment.outlet.Volume
        conc = catchment.outlet.Conc
        load = catchment.outlet.Load
        flow = catchment.outlet.Flow
        rec = [name,time,volume,conc,load,flow]
        
        # write data
        self.outlets[self.index_outlets] = tuple(rec)
        
    def save_gw(self,catchment):
        """
        """
        
        # get data
        time = catchment.timestring
        name = catchment.gw.Name
        volume = catchment.gw.Volume
        conc = catchment.gw.Conc
        flow = catchment.gw.Flow
        load = catchment.outlet.Load
        # write data
        rec = [time,name,volume,conc,load,flow]
        self.gws[self.index_gws] = tuple(rec)

    def __create_hdf(self,fname,n,fmt,header,tablename):
        """
        """
        
        # check if file exists and delete 
        if os.path.exists(fname): 
            f = h5py.File(fname, 'r+')
            f.close()
            os.remove(fname)
    
        fmt = [i.replace("U","S") for i in fmt]
        dtype = [(n,t) for n,t in zip(header,fmt)]
        f = h5py.File(fname, 'w')
        f.create_dataset(tablename, (n,), dtype=dtype,
                                compression="gzip", compression_opts=4)
        f.close()

    def save(self,catchment):
        """
        """
        
  
         
        self.save_cells(catchment)  
        if self.hasPlants:
            self.save_plants(catchment)
        

        
        # save data
        self.save_reaches(catchment)
        self.save_outlet(catchment)
        
        if self.hasDeepGW:
            self.save_gw(catchment)
            self.index_gws += 1
        
        # set index
        self.index_reaches += self.nReaches 
        self.index_cells += self.nCells 
        self.index_outlets += 1
                
        # manage chunks
        self.manage_chunks(catchment)
        
        

   
    def manage_chunks(self,catchment):
        """
        """
        # check if data chunk option is used
        if self.chunksize>0:
            
            t_index = self.daterange.index(catchment.solver.t.AsPython()) 

            
            if t_index == self.chunks_new[0]:
                
#                print("save data from memory to disk ...")
                
                # save current files
                self.savechunk(self.chunks[0][0],self.chunks[0][-1])
                
                # remove chunk from list
                self.chunks.remove(self.chunks[0])
                self.chunks_new.remove(self.chunks_new[0])
                
                
                if catchment.solver.t.AsPython() != self.daterange[-1]:
                    # create new temporary files
                    self.createFiles()
            
                    # reset indexes of memory files
                    self.index_cells = 0
                    self.index_reaches = 0
                    self.index_outlets = 0
                    self.index_gws = 0
        
    def savechunk(self,t_start,t_end):
        

        
        if self.hasCells:
            # cells
            self.__save_hdf_chunk(self.fpath_cells+"."+self.ext,self.cells,
                            self.fmt_cells,self.columns_cells,"cells",
                            t_start,t_end,multiplier=self.nCells,readmode="a")
            
            if self.hasPlants:
                # plants
                self.__save_hdf_chunk(self.fpath_plants+"."+self.ext,self.plants,
                    self.fmt_plants,self.columns_plants,"plants",
                     t_start,t_end,multiplier=self.nCells,readmode="a")
  
        # outlets
        self.__save_hdf_chunk(self.fpath_outlets+"."+self.ext,self.outlets,
                self.fmt_outlets,self.columns_outlets,"outlets",
                 t_start,t_end,multiplier=1,readmode="a")
        
        # reaches
        self.__save_hdf_chunk(self.fpath_reaches+"."+self.ext,self.reaches,
                self.fmt_reaches,self.columns_reaches,"reaches",
                t_start,t_end,multiplier=self.nReaches,readmode="a")
        
        # gws
        self.__save_hdf_chunk(self.fpath_gws+"."+self.ext,self.gws,
                self.fmt_gws,self.columns_gws,"gws",
                 t_start,t_end,multiplier=1,readmode="a")  



    def __save_hdf_chunk(self,fname,data,fmt,header,tablename,
                         t_start,t_end,multiplier,readmode="a"):
        """
        """
        
        dset=None

        # open existing hdf file
        f = h5py.File(fname, readmode)
        dset = f[tablename]
            
        # convert data formats
        data = data.astype(dset.dtype)
        
        # save data
        dset[t_start*multiplier:(t_end*multiplier)+multiplier] = data
        
        # close file
        f.close()

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
        if self.chunksize<1:
            if self.hasCells:
                
                # cells
                self.__save_hdf(self.fpath_cells+"."+self.ext,self.cells,
                                self.fmt_cells,self.columns_cells,"cells")
                if self.hasPlants:
                    # plants
                    self.__save_hdf(self.fpath_plants+"."+self.ext,self.plants,
                        self.fmt_plants,self.columns_plants,"plants")
      
            # outlets
            self.__save_hdf(self.fpath_outlets+"."+self.ext,self.outlets,
                    self.fmt_outlets,self.columns_outlets,"outlets")
            
            # reaches
            self.__save_hdf(self.fpath_reaches+"."+self.ext,self.reaches,
                    self.fmt_reaches,self.columns_reaches,"reaches")
            
            # gws
            self.__save_hdf(self.fpath_gws+"."+self.ext,self.gws,
                    self.fmt_gws,self.columns_gws,"gws")
            
  