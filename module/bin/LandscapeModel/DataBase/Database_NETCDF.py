# -*- coding: utf-8 -*-
"""
Created on Wed Sep 13 11:36:06 2017

@author: smh
"""
from datetime import timedelta
from netCDF4 import date2num
from netCDF4 import Dataset
from .Database import Database

class Database_NETCDF(Database):
    def __init__(self,catchment=None,fpath="",fname=""):
        """
        """
        
        # zip files
        self.zlib = True
        
        # skip indeces when creating netcdf-variables from table header
        self.skip_indices = 2

        # set number format
        self.dtype = "f4"
        
        #init core class
        Database.__init__(self, catchment,fpath,fname)

    def netcdf_create(self,fname,keys,times,zlib=True,
                      description="",
                      history="",
                      source="",
                      time_units="hours since 0001-01-01 00:00:00.0",
                      time_calendar = "gregorian"):
        """
        Creates a netcdf file containing data.
        """
        ## create new netcdf-file for climate data
        nc = Dataset(fname, "w", format="NETCDF4")
        
        # create dimensions
        KEY = nc.createDimension("key", len(keys))
        TIME = nc.createDimension("time", len(times))
        
        # create variable for each dimension
        KEY = nc.createVariable("key","i8",("key",),zlib=zlib)
        TIME = nc.createVariable("time","i8",("time",),zlib=zlib)
                
        # set data of dimensions
        KEY[:] = keys
        TIME[:] = times
        
        # set time info 
        TIME.units = time_units
        TIME.calendar = time_calendar
        
        # add file info
        nc.description = description
        nc.history = history
        nc.source =  source
        
        # return file
        return nc     
    
    def netcdf_addVariable(self,nc,name,dtype,unit="",shape=("key","time",),zlib=True):
        """
        Adds a variable to an existing netcdf-file.
        """
        param = nc.createVariable(name,dtype,shape,zlib=zlib)
        param.unit = unit
        return param
              
    def createFiles(self):
        """
        """
        
        # create time key
        begin  = self.catchment.modelrun.begin+timedelta(hours=1)
        end =  self.catchment.modelrun.end+timedelta(hours=1)
        units = "hours since 0001-01-01 00:00:00.0"
        calendar = "gregorian"
        times = [i for i in self.daterange(begin, end)]
        self.times = date2num(times,units=units,calendar=calendar)

        # create location key for cells and reaches
        getInt = lambda x: int("".join([i  for i in x if i.isdigit()]))
        self.keys_cells = [getInt(i.key) for i in self.catchment.fields]
        self.keys_reaches = [getInt(i.Name) for i in self.catchment.reaches]
    
        if self.hasCells:
            
            # create netcdf cells
            self.cells = self.netcdf_create(self.fpath_cells+".nc",
                                            self.keys_cells,self.times,
                                            zlib=self.zlib)
            # add variables cells
            for col in self.columns_cells[self.skip_indices:]: 
                self.netcdf_addVariable(self.cells,col,dtype=self.dtype,
                                        zlib=self.zlib)
            
            # create netcdf plants
            self.plants = self.netcdf_create(self.fpath_plants+".nc",
                                             self.keys_cells,self.times,
                                        zlib=self.zlib)
            # add variables plants
            for col in self.columns_plants[self.skip_indices:]: 
                self.netcdf_addVariable(self.plants,col,dtype=self.dtype,
                                        zlib=self.zlib)
        
        # create netcdf reaches
        self.reaches = self.netcdf_create(self.fpath_reaches+".nc",
                                          self.keys_reaches,self.times,
                                        zlib=self.zlib)
        # add variables reaches
        for col in self.columns_reaches[self.skip_indices:]:  
            self.netcdf_addVariable(self.reaches,col,dtype=self.dtype,
                                        zlib=self.zlib)       
        
       # create netcdf outlets
        self.outlets = self.netcdf_create(self.fpath_outlets+".nc",[0],
                                          self.times,
                                        zlib=self.zlib)
        # add variables outlets
        for col in self.columns_outlets[self.skip_indices:]:  
            self.netcdf_addVariable(self.outlets,col,dtype=self.dtype,
                                        zlib=self.zlib)              
     
        # create netcdf deep groundwater
        self.gws = self.netcdf_create(self.fpath_gws+".nc",[0],self.times,
                                        zlib=self.zlib)
        for col in self.columns_gws[self.skip_indices:]: 
            self.netcdf_addVariable(self.gws,col,dtype=self.dtype,
                                        zlib=self.zlib)         
    
    def save_cells(self,catchment):
        """
        """

        for i,f in enumerate(catchment.fields):     

            # get data
            rec = [f.cmf1d.qperc,f.cmf1d.qsurf,f.cmf1d.qdrain,
                   f.cmf1d.qgw_river,f.cmf1d.qgw_gw,f.cmf1d.Vsw,f.cmf1d.Vgw,
                   f.cmf1d.Vdr,f.cmf1d.get_rain(), f.cmf1d.concgw,
                   f.cmf1d.concsw,f.cmf1d.concdrainage]+f.cmf1d.Vsoil+f.cmf1d.concsoil
           
            # write data
            for colname,val in zip(self.columns_cells[2:],rec):
                self.cells[colname][i,self.index] = val
    
    def save_plants(self,catchment):
        """
        """

        for i,f in enumerate(catchment.fields):       

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

            # write data
            rec = [das,rootdepth,height,LAI,GLAI,Epot,Eact,Tpot,Tact]+ soil_waterabstraction  + soil_rootwateruptake  +soil_evaporation+rootdistribution 
            for colname,val in zip(self.columns_plants[2:],rec):
                self.plants[colname][i,self.index] = val
            
    def save_reaches(self,catchment):
        """
        """
        for i,r in enumerate(catchment.reaches):
            
            # get data
            rec = [r.Depth,r.Conc,r.Load,r.ArtificialFlux,r.Volume,r.Flow,
                   r.Area,r.MASS_SED,r.MASS_SED_DEEP,r.MASS_SW,
                   r.PEC_SW,r.PEC_SED]

            # write data
            for colname,val in zip(self.columns_reaches[2:],rec):
                self.reaches[colname][i,self.index] = val


    def save_outlet(self,catchment):
        """
        """
        
        # get data
        volume = catchment.outlet.Volume
        conc = catchment.outlet.Conc
        load = catchment.outlet.Load
        flow = catchment.outlet.Flow
        
        # write data
        rec = [volume,conc,load,flow]
        for colname,val in zip(self.columns_outlets[2:],rec):
            self.outlets[colname][0,self.index] = val

    def save_gw(self,catchment):
        """
        """
        
        # get data
        volume = catchment.gw.Volume
        conc = catchment.gw.Conc
        flow = catchment.gw.Flow
        
        # write data
        rec = [volume,conc,flow]
        for colname,val in zip(self.columns_gws[2:],rec):
            self.gws[colname][0,self.index] = val
   
    def finalize(self):
        """
        """
        self.cells.close()
        self.plants.close()
        self.outlets.close()
        self.reaches.close()
        self.gws.close()  