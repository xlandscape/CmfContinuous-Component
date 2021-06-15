# -*- coding: utf-8 -*-
"""
Created on Wed Sep 13 11:36:06 2017

@author: smh
"""
import os
import csv 

from LandscapeModel.DataBase.DataRecord_plant import DataRecord_plant
from LandscapeModel.DataBase.DataRecord_field import DataRecord_field
from LandscapeModel.DataBase.DataRecord_reach import DataRecord_reach
from LandscapeModel.DataBase.DataRecord_outlet import DataRecord_outlet
from LandscapeModel.DataBase.DataRecord_gw import DataRecord_gw

from LandscapeModel.Catchment import Catchment
from LandscapeModel.utils import readInputData
 

class Database(object):
    def __init__(self,catchment=None,fpath="",fname=""):
        
        # Output data
        self.DataRecords_plants = []
        self.DataRecords_fields = []
        self.DataRecords_reaches = []
        self.DataRecords_outlets = [] 
        self.DataRecords_gws = []  
        self.catchment = catchment
        
        self.counter_fields = 0
        self.counter_reaches = 0
        
        self.fpath=fpath
        self.fname = fname
        
        if fname != "":
            ###################################################################
            #agricultural fields
            #create colum names for each soil layer
            if len(self.catchment.fields)>0:
                Vsoil_columns = ["Vsoil_%i"%(i) for i,_ in enumerate(self.catchment.fields[0].cmf1d.c.layers)]
                concsoil_columns = ["concsoil_%i"%(i) for i,_ in enumerate(self.catchment.fields[0].cmf1d.c.layers)]
    #            loadsoil_columns = ["loadsoil_%i"%(i) for i,_ in enumerate(self.catchment.fields[0].cmf1d.c.layers)]
                #make csv-file
            
                
                self.fields_csv = open(os.path.join(fpath,fname + "_" + "agriculturalfields.csv"), 'w',newline='')
                self.fieldswriter = csv.writer(self.fields_csv, delimiter=',', quotechar='"')
    #            self.fieldswriter.writerow(["name","time","qperc","qsurf","qdrain","qgw_gw","qgw_river","qlateral","Vsw","Vgw","Vdr","rain","concgw","loadgw","concsw","loadsw","concdrainage","loaddrainage"]+Vsoil_columns+concsoil_columns+loadsoil_columns)
                self.fieldswriter.writerow(["name","time","qperc","qsurf","qdrain","qgw_river","qgw_gw","Vsw","Vgw","Vdr","rain","concgw","concsw","concdrainage"]+Vsoil_columns+concsoil_columns)
                self.fields_csv.flush()

                ###################################################################
                #plants
                #create colum names for each soil layer
                soil_waterabstraction = ["waterabstraction_%i"%(i) for i,_ in enumerate(self.catchment.fields[0].cmf1d.c.layers)]
                soil_rootwateruptake = ["rootwateruptake_%i"%(i) for i,_ in enumerate(self.catchment.fields[0].cmf1d.c.layers)]
                soil_evaporation = ["evaporation_%i"%(i) for i,_ in enumerate(self.catchment.fields[0].cmf1d.c.layers)]
                rootdistribution = ["rootdistribution_%i"%(i) for i,_ in enumerate(self.catchment.fields[0].cmf1d.c.layers)]
                
                #make csv-file           
                self.plants_csv = open(os.path.join(fpath,fname + "_" + "plants.csv"), 'w',newline='')
                self.plantswriter = csv.writer(self.plants_csv, delimiter=',', quotechar='"')
                self.plantswriter.writerow(["name","plantname","time","das","rootdepth","height","LAI","GLAI","Epot","Eact","Tpot","Tact"]+soil_waterabstraction+soil_rootwateruptake+soil_evaporation+rootdistribution)
                self.plants_csv.flush()

            ###################################################################
            #reaches
            #make csv-file
            self.reaches_csv = open(os.path.join(fpath,fname + "_" + "reaches.csv"), 'w',newline='')
            self.reacheswriter = csv.writer(self.reaches_csv, delimiter=',', quotechar='"')
            self.reacheswriter.writerow(["name","time","depth","conc","load","artificialflux","volume","flow","area","MASS_SED","MASS_SED_DEEP","MASS_SW","PEC_SW","PEC_SED"])
#            self.reacheswriter.writerow(["name","time","depth","conc","load","artificialflux","volume","flow","area"])

            self.reaches_csv.flush()

            ###################################################################
            #outlets
            #make csv-file
            self.outlets_csv = open(os.path.join(fpath,fname + "_" + "outlets.csv"), 'w',newline='')
            self.outletswriter = csv.writer(self.outlets_csv, delimiter=',', quotechar='"')
            self.outletswriter.writerow(["name","time","volume","conc","load","flow"])
            self.outlets_csv.flush()  
            
                        ###################################################################
            #outlets
            #make csv-file
            self.gws_csv = open(os.path.join(fpath,fname + "_" + "gws.csv"), 'w',newline='')
            self.gwswriter = csv.writer(self.gws_csv, delimiter=',', quotechar='"')
            self.gwswriter.writerow(["name","time","volume","conc","load","flow"])
            self.gws_csv.flush()  

    def close(self):
        self.fields_csv.close()
        self.plants_csv.close()
        self.outlets_csv.close()
        self.reaches_csv.close()
        self.gws_csv.close()  
            
    def save_csv(self,catchment):
        time = catchment.timestring
        #######################################################################
        # fields
        for f in catchment.fields:
            
            # water fluxes and solutes
            name = f.key
            #water fluxes            
            qperc = f.cmf1d.qperc
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
            self.fieldswriter.writerow([name,time]+["%.4f"%(i) for i in [qperc,qsurf,qdrain,qgw_river,qgw_gw,Vsw,Vgw,Vdr,rain,concgw,concsw,concdrainage]]+["%.4f"%(i) for i in Vsoil ] + ["%.4f"%(i) for i in concsoil ])
            self.fields_csv.flush()

            ###################################################################
            #plant            
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
            self.plantswriter.writerow([name,plantname,time]+["%.4f"%(i) for i in [das,rootdepth,height,LAI,GLAI,Epot,Eact,Tpot,Tact]]+["%.4f"%(i) for i in soil_waterabstraction ] + ["%.4f"%(i) for i in soil_rootwateruptake ] +["%.4f"%(i) for i in soil_evaporation ] +["%.4f"%(i) for i in rootdistribution ])
            self.plants_csv.flush()
            
        #######################################################################
        # reaches
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
            self.reacheswriter.writerow([name,time]+["%.4f"%(i) for i in[depth,conc,load,artificialflux,volume,flow,area,MASS_SED,MASS_SED_DEEP,MASS_SW,PEC_SW,PEC_SED]])
            self.reaches_csv.flush()            

        ########################################################################
        # outlets "name","time","volume","conc","load","flow"
        #store data of outlet
        name = catchment.outlet.Name
        volume = catchment.outlet.Volume
        conc = catchment.outlet.Conc
        load = catchment.outlet.Load
        flow = catchment.outlet.Flow
        self.outletswriter.writerow([name,time]+["%.4f"%(i) for i in[volume,conc,load,flow]])
        self.outlets_csv.flush()

        ########################################################################
        # gws
        #store data of catchmenwide gw
        if catchment.gw != None:
            name = catchment.gw.Name
            volume = catchment.gw.Volume
            conc = catchment.gw.Conc
            flow = catchment.gw.Flow
            self.gwswriter.writerow([name,time]+["%.4f"%(i) for i in[volume,conc,flow]])
            self.gws_csv.flush()    

                
    def save_csv_reachoutlet(self,catchment):
        time = catchment.timestring

        #######################################################################
        # reaches
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
            self.reacheswriter.writerow([name,time]+["%.4f"%(i) for i in[depth,conc,load,artificialflux,volume,flow,area,MASS_SED,MASS_SED_DEEP,MASS_SW,PEC_SW,PEC_SED]])
            self.reaches_csv.flush()            

        #####################################################################
#         outlets
        #store data of outlet
        name = catchment.outlet.Name
        volume = catchment.outlet.Volume
        conc = catchment.outlet.Conc
        load = catchment.outlet.Load
        flow = catchment.outlet.Flow
        self.outletswriter.writerow([name,time]+["%.4f"%(i) for i in[volume,conc,load,flow]])
        self.outlets_csv.flush()    
        
    def save_csv_cmf1dtimeseries(self,catchment):
        time = catchment.timestring
        
        #######################################################################
        # fields
        for f in catchment.fields:
            # water fluxes and solutes
            name = f.key

            #water fluxes            
            qsurf = f.cmf1d.qsurf
            qdrain = f.cmf1d.qdrain
            qgw_river = f.cmf1d.qgw_river
            qgw_gw = f.cmf1d.qgw_gw
       
            Vsw = f.cmf1d.Vsw
            Vgw =  f.cmf1d.Vgw
            Vdr =  f.cmf1d.Vdr
            rain = f.cmf1d.get_rain()
            #solutes
            concgw = f.cmf1d.concgw

#            loadgw = f.cmf1d.loadgw

            concsw = f.cmf1d.concsw
#            loadsw = f.cmf1d.loadsw
            concdrainage = f.cmf1d.concdrainage
#            loaddrainage = f.cmf1d.loaddrainage
            #write data to file
            self.fieldswriter.writerow([name,time]+["%.4f"%(i) for i in [0,qsurf,qdrain,qgw_river,qgw_gw,Vsw,Vgw,Vdr,rain,concgw,concsw,concdrainage]])#+["%.4f"%(i) for i in Vsoil ] + ["%.4f"%(i) for i in concsoil ] +["%.4f"%(i) for i in loadsoil ])
            self.fields_csv.flush()

        #######################################################################
        # reaches
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
            self.reacheswriter.writerow([name,time]+["%.4f"%(i) for i in[depth,conc,load,artificialflux,volume,flow,area,MASS_SED,MASS_SED_DEEP,MASS_SW,PEC_SW,PEC_SED]])
            self.reaches_csv.flush()            

        #####################################################################
#         outlets
        #store data of outlet
        name = catchment.outlet.Name
        volume = catchment.outlet.Volume
        conc = catchment.outlet.Conc
        load = catchment.outlet.Load
        flow = catchment.outlet.Flow
        self.outletswriter.writerow([name,time]+["%.4f"%(i) for i in[volume,conc,load,flow]])
        self.outlets_csv.flush()    


        ########################################################################
        # gws
        if catchment.gw != None:
            #store data of outlet
            name = catchment.gw.Name
            volume = catchment.gw.Volume
            conc = catchment.gw.Conc
            flow = catchment.gw.Flow
            self.gwswriter.writerow([name,time]+["%.4f"%(i) for i in[volume,conc,flow]])
            self.gws_csv.flush()   



    def save(self,catchment):
        
        time = catchment.timestring
        
        #######################################################################
        # fields
        for f in catchment.fields:
            rec = DataRecord_field()
            ###################################################################
            # water fluxes and solutes
            rec.name = f.key
            #water fluxes            
            rec.qperc = f.cmf1d.qperc
            rec.Vsoil = f.cmf1d.Vsoil
            rec.qsurf = f.cmf1d.qsurf
            rec.qdrain = f.cmf1d.qdrain
            rec.qgw_river = f.cmf1d.qgw_river
            rec.qgw_gw = f.cmf1d.qgw_gw
            rec.rain = f.cmf1d.get_rain()
            #solutes
            rec.concgw = f.cmf1d.concgw
            rec.concsoil = f.cmf1d.concsoil
            rec.concsw = f.cmf1d.concsw
            rec.concdrainage = f.cmf1d.concdrainage
            catchment.database.DataRecords_fields.append(rec)
            
            ###################################################################
            #plant
            rec = DataRecord_plant()
            rec.name = f.key
            rec.plantname = f.plant.Name
            rec.time = time
            rec.das = f.plant.DAS
            rec.rootdepth = f.plant.RootingDepth
            rec.height = f.plant.Height
            rec.LAI = f.plant.LAI
            rec.GLAI = f.plant.GLAI
            if f.plantmodel == "macro":
                rec.Epot =f.plant.Epot
                rec.Tpot = f.plant.Tpot
                rec.Eact = f.plant.Eact
                rec.Tact =f.plant.Tact
                rec.soil_waterabstraction = f.plant.SoilWaterExtraction
                rec.soil_rootwateruptake = f.plant.SoilRootWaterUptake
                rec.soil_evaporation = f.plant.SoilEvaporation
                rec.rootdistribution = f.plant.RootDistribution
            elif f.plantmodel == "cmf":
                rec.Eact = f.cmf1d.Eact
                rec.Tact =f.cmf1d.Tact
                rec.Epot = 0
                rec.Tpot =0
                rec.soil_waterabstraction =[]
                rec.soil_rootwateruptake = []
                rec.soil_evaporation = []
                rec.rootdistribution = []
            catchment.database.DataRecords_plants.append(rec)

        #######################################################################
        # reaches
        for r in catchment.reaches:
            rec = DataRecord_reach()
            rec.name = r.Name
            rec.time =time
            rec.depth = r.Depth
            
            if not self.catchment.modelrun.substance == "None":
                rec.conc = r.Conc
                rec.load = r.Load
            rec.artificialflux = r.ArtificialFlux
            rec.volume = r.Volume
            rec.flow = r.Flow
            rec.area = r.Area
            rec.MASS_SED = r.MASS_SED
            rec.MASS_SED_DEEP = r.MASS_SED_DEEP
            rec.MASS_SW = r.MASS_SW
            rec.PEC_SW = r.PEC_SW
            rec.PEC_SED = r.PEC_SED

            catchment.database.DataRecords_reaches.append(rec)
            
        ########################################################################
        # outlets
        #store data of outlet
        rec = DataRecord_outlet()
        rec.name = catchment.outlet.Name
        rec.time = time
        rec.volume = catchment.outlet.Volume
        if not self.catchment.modelrun.substance == "None":
            rec.conc = catchment.outlet.Conc
            rec.load = catchment.outlet.Load
        rec.flow = catchment.outlet.Flow
        catchment.database.DataRecords_outlets.append(rec)  
        
        #######################################################################
        # gw
        if (catchment.gw != None):
            rec = DataRecord_gw()
            rec.name = catchment.gw.Name
            rec.time = time
            rec.volume = catchment.gw.Volume
            rec.conc = catchment.gw.Conc
            rec.flow = catchment.gw.Flow
            catchment.database.DataRecords_gws.append(rec)          

#    def read(self,fpath,fname,begin,end,timestep,timestep_convert,clim_start,clim_step):
#        
#        #######################################################################
#        # read input data
#        ClimateStationList,FieldList,SubbasinList,ReachList,SoilLayerList,SubstanceList,CropCoefficientList,ManagementList = readInputData(fpath)
#        sub1 = SubbasinList[SubbasinList["name"]==fname]
#
#        ###############################################################################
#        # create a subcatchment isntance TODO: substance!!!
#        catchment = SubCatchment(ReachList,sub1,FieldList, SubstanceList[0],
#                                 ClimateStationList,SoilLayerList, CropCoefficientList,
#                                 ManagementList, timestep,timestep_convert,begin,
#                                 database_path="",inputdata_path=fpath,
#                                 clim_start=clim_start,clim_step=clim_step)
#                                      
#        ###############################################################################                                   
#        # function to read data
#        def readFile(fpath):
#            dat = open(fpath,"r")
#            dat = dat.read()
#            dat = dat.split("\n")
#            header = dat[0].split(",")
#            if dat[-1] == "": dat=dat[:-1]
#            dat = [tuple(i.split(",")) for i in  dat[1:]]   
#            return header,dat                
#        
#        #######################################################################
#        # # read data: agricultural fields
##        header,dat = readFile(os.sep.join([fpath,fname+"_agriculturalfields.csv"]))
##        for row in dat:
#    
#        print("read _griculturalfields")
#        with open(os.sep.join([fpath,fname+"_agriculturalfields.csv"]),"r") as dat:
#            #skip header
#            dat.readline()
#            #read data
#            for line in dat:
#                row = line.split(",")
#  
#                
#                rec = DataRecord_field()
#                rec.name = row[0]
#                t = row[1].split(".")
#                rec.time = cmf.Time(int(t[0]),int(t[1]),int(t[2]))           
#                rec.qperc = float(row[2])
#                rec.qsurf = float(row[3])
#                rec.qdrain = float(row[4])
#                rec.qgw_gw = float(row[5])
#                rec.qgw_river = float(row[6])
#                rec.qlateral = float(row[7])
#                
#                rec.Vsw = float(row[8])
#                rec.Vgw = float(row[9])
#                rec.Vdr =  float(row[10])
#                
#                rec.rain =float(row[11])
#                rec.concgw = float(row[12])
#                rec.loadgw = float(row[13])
#                rec.concsw = float(row[14])
#                rec.loadsw = float(row[15])
#                rec.concdrainage = float(row[16])
#                rec.loaddrainage = float(row[17])
#                rec.Vsoil = [float(row[i]) for i in range(18,41,1)]
#                rec.concsoil = [float(row[i]) for i in range(42,65,1)]
#                rec.loadsoil = [float(row[i]) for i in range(66,90,1)]
#                
#                catchment.database.DataRecords_fields.append(rec)
#        
#        #######################################################################
#        # # read data: palns data
#        header,dat = readFile(os.sep.join([fpath,fname+"_plants.csv"]))        
#        for row in dat:
#            rec = DataRecord_plant()
#            rec.name = row[0]
#            rec.plantname = row[1]
#            t = row[2].split(".")
#            rec.time = cmf.Time(int(t[0]),int(t[1]),int(t[2]))           
#            rec.das = int(float(row[3]))
#            rec.rootdepth = float(row[4])
#            rec.height = float(row[5])
#            rec.LAI = float(row[6])
#            rec.GLAI = float(row[7])
#            rec.Epot = float(row[8])
#            rec.Tpot = float(row[9])
#            rec.Eact = float(row[10])
#            rec.Tact = float(row[11])
#            rec.soil_waterabstraction = [float(row[i]) for i in range(12,36,1)]
#            rec.soil_rootwateruptake = [float(row[i]) for i in range(36,60,1)]
#            rec.soil_evaporation = [float(row[i]) for i in range(60,84,1)]
#            rec.rootdistribution = [float(row[i]) for i in range(84,108,1)]
#            catchment.database.DataRecords_plants.append(rec)                                     
#                                     
#        #######################################################################
#        # reaches
##        header,dat = readFile(os.sep.join([fpath,fname+"_reaches.csv"]))
#        print("read _reaches")
#        with open(os.sep.join([fpath,fname+"_reaches.csv"]),"r") as dat:
#            #skip header
#            dat.readline()
#            #read data
#            for line in dat:
#                row = line.split(",")
#                rec = DataRecord_reach()
#                rec.name = row[0]
#                t = row[1].split(".")
#                rec.time = rec.time = cmf.Time(int(t[0]),int(t[1]),int(t[2])) 
#                rec.depth = float(row[2])
#                rec.conc = float(row[3])
#                rec.load = float(row[4])
#                rec.artificialflux = float(row[5])
#                rec.volume = float(row[6])
#                rec.flow = float(row[7])
#                rec.Area = float(row[8])
#                catchment.database.DataRecords_reaches.append(rec)
#                
#        ########################################################################
#        # outlets
#        print("read _outlets")
#        with open(os.sep.join([fpath,fname+"_outlets.csv"]),"r") as dat:
#            #skip header
#            dat.readline()
#            #read data
#            for line in dat:
#                row = line.split(",")
#                rec = DataRecord_outlet()
#                rec.name = row[0]
#                t = row[1].split(".")
#                rec.time = rec.time = cmf.Time(int(t[0]),int(t[1]),int(t[2])) 
#                rec.volume = float(row[2])
#                rec.conc = float(row[3])
#                rec.load = float(row[4])
#                rec.flow = float(row[5])
#                catchment.database.DataRecords_outlets.append(rec)   
#                
#        return catchment
        
        
        
        
        
        
        
