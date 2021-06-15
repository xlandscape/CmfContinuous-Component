# -*- coding: utf-8 -*-
"""
Created on Wed Sep 13 11:36:06 2017

@author: smh
"""

import csv 
from .Database import Database

class Database_CSV(Database):
    def __init__(self,catchment=None,fpath="",fname=""):
        """
        """
        
        #init core class
        Database.__init__(self, catchment)
        
        # create files
        self.createFiles()

    def createFiles(self):
        """
        """
    
        if self.hasCells:
            # cells
            self.cells = open(self.fpath_cells + ".csv", 'w',newline='')
            self.fieldswriter = csv.writer(self.cells, delimiter=',', quotechar='"')
            self.fieldswriter.writerow(self.columns_cells)
            self.cells.flush()
            
            if self.hasPlants:
                # plants
                self.plants = open(self.fpath_plants +".csv", 'w',newline='')
                self.plantswriter = csv.writer(self.plants, delimiter=',', quotechar='"')
                self.plantswriter.writerow(self.columns_plants)
                self.plants.flush()

        # reaches
        self.reaches =open(self.fpath_reaches+".csv", 'w',newline='')
        self.reacheswriter = csv.writer(self.reaches, delimiter=',', quotechar='"')
        
        self.reacheswriter.writerow(self.columns_reaches)
        self.reaches.flush()

        # outlets 
        self.outlets = open(self.fpath_outlets+".csv", 'w',newline='')
        self.outletswriter = csv.writer(self.outlets, delimiter=',', quotechar='"')
        self.outletswriter.writerow(self.columns_outlets)
        self.outlets.flush()  
        
        # gw
        self.gws = open(self.fpath_gws+".csv", 'w',newline='')
        self.gwswriter = csv.writer(self.gws, delimiter=',', quotechar='"')
        self.gwswriter.writerow(self.columns_gws)
        self.gws.flush()  
            
    def save_cells(self,catchment):
        """
        """
        time = catchment.timestring
        #######################################################################
        # fields
        for f in catchment.fields:
            
            # water fluxes and solutes
            name = f.key
            #water fluxes            
            
            Vsoil = f.cmf1d.Vsoil
            qsurf = f.cmf1d.qsurf
            qdrain = f.cmf1d.qdrain
            qgw_gw = f.cmf1d.qgw_gw
            qgw_river = f.cmf1d.qgw_river
            Vsw = f.cmf1d.Vsw
            Vgw =  f.cmf1d.Vgw
            Vdr =  f.cmf1d.Vdr
            rain = f.cmf1d.get_rain()
            concgw = f.cmf1d.concgw
            concsoil = f.cmf1d.concsoil
            concsw = f.cmf1d.concsw
            concdrainage = f.cmf1d.concdrainage

            #write data to file
            if self.modelrun.runtype == "completeCatchment":
                qperc = f.cmf1d.qperc
                self.fieldswriter.writerow([name,time]+["%.8f"%(i) for i in [qperc,qsurf,qdrain,qgw_river,qgw_gw,Vsw,Vgw,Vdr,rain,concgw,concsw,concdrainage]]+["%.8f"%(i) for i in Vsoil ] + ["%.8f"%(i) for i in concsoil ])
            elif self.modelrun.runtype == "timeseriesCatchment":            
                 self.fieldswriter.writerow([name,time]+["%.8f"%(i) for i in [0,qsurf,qdrain,qgw_river,qgw_gw,Vsw,Vgw,Vdr,rain,concgw,concsw,concdrainage]])
           
            
            
            self.cells.flush()
    
    def save_plants(self,catchment):
        """
        """
        time = catchment.timestring
        for f in catchment.fields:         
            name = f.key
            plantname = f.plant.Name
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
                #write data to file
            self.plantswriter.writerow([name,time,plantname]+["%.4f"%(i) for i in [das,rootdepth,height,LAI,GLAI,Epot,Eact,Tpot,Tact]]+["%.4f"%(i) for i in soil_waterabstraction ] + ["%.4f"%(i) for i in soil_rootwateruptake ] +["%.4f"%(i) for i in soil_evaporation ] +["%.4f"%(i) for i in rootdistribution ])
            self.plants.flush()
            
    def save_reaches(self,catchment):
        """
        """
        time = catchment.timestring
        for r in catchment.reaches:
            name = r.Name
            depth = r.Depth
            conc = r.Conc
            load = r.Load
            artificialflux = r.ArtificialFlux
            volume = r.Volume
            flow = r.Flow   
            area = r.Area
            MASS_SED = r.MASS_SED
            MASS_SED_DEEP = r.MASS_SED_DEEP
            MASS_SW = r.MASS_SW
            PEC_SW = r.PEC_SW
            PEC_SED = r.PEC_SED
            self.reacheswriter.writerow([name,time]+["%.8f"%(i) for i in[depth,conc,load,artificialflux,volume,flow,area,MASS_SED,MASS_SED_DEEP,MASS_SW,PEC_SW,PEC_SED]])
            self.reaches.flush()

    def save_outlet(self,catchment):
        """
        """
        time = catchment.timestring
        name = catchment.outlet.Name
        volume = catchment.outlet.Volume
        conc = catchment.outlet.Conc
        load = catchment.outlet.Load
        flow = catchment.outlet.Flow
        self.outletswriter.writerow([name,time]+["%.8f"%(i) for i in[volume,conc,load,flow]])
        self.outlets.flush()
        
    def save_gw(self,catchment):
        """
        """
        time = catchment.timestring
        name = catchment.gw.Name
        volume = catchment.gw.Volume
        conc = catchment.gw.Conc
        flow = catchment.gw.Flow
        self.gwswriter.writerow([name,time]+["%.8f"%(i) for i in[volume,conc,flow]])
        self.gws.flush()

        
    def save(self,catchment):
        """
        """
        

            
        
        if self.hasPlants:
            self.save_plants(catchment)
        
            

        self.save_cells(catchment)
        # save data
        self.save_reaches(catchment)
        self.save_outlet(catchment)
        
        if self.hasDeepGW:
            self.save_gw(catchment)
            self.index_gws += 1
        
        # set index
        self.index_reaches += self.nReaches 
        self.index_outlets += 1
        self.index_cells += self.nCells 
        
      
    def finalize(self):
        """
        """
        if self.cells!=None: self.cells.close()
        if self.plants!=None: self.plants.close()
        if self.outlets!=None: self.outlets.close()
        if self.reaches!=None: self.reaches.close()
        if self.gws!=None: self.gws.close()  
    