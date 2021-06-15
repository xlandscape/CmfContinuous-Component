# -*- coding: utf-8 -*-
"""
Created on Tue Sep 12 13:29:03 2017

@author: smh
"""

# python native and common
from datetime import datetime
import os
import numpy as np

# hydrology and landscpae
import cmf

import LandscapeModel
#import LandscapeModel.Database
from .RiverSegment import RiverSegment
from .AgriculturalField import AgriculturalField
from .CatchmentGroundwater import CatchmentGroundwater
from LandscapeModel.CatchmentOutlet import CatchmentOutlet

# efate and drift
from LandscapeModel.AquaticEfate.Steps1234 import Steps1234
from LandscapeModel.SprayDrift.SprayDrift import SprayDrift

#interfaces
from LandscapeModel.Interface import CMF_EFATE,CMF_DRIFT

class Catchment(object):
    """ 
    Holds catchment structures such fields, reaches and outlets
     and connects them.
    
    A cmf.project instance is created when this class is initiated. In the 
    next step, river segments are created (cmf.reach) as well as the
    catchment outlet (self.p.NewOutlet). A solver is created and the 
    fields are connected with the river segments and the outlet. In this 
    setup, each field is connected to one river segment. The river
    segments are connected to each other and the outlet.
    
    Field processes are evapotranspiration, percolation, drainage and 
    surface runoff. Percolation drains to the groundwater and then into the
    river segment Surface runoff flows directly into the river segment.
    
    A substance is applied to the field. For the moment into the lowest 
    soil layer (will be changed).      
    
    The results are stored in the database (from database Module) and can 
    be visualised with the functions from the Plotting module.
    """
    def __init__(self,modelrun,printMessage=False,createDatabase=True):
        """
  
        """
        
        self.createDatabase = createDatabase
         
        # set run info
        self.modelrun = modelrun
        
        # get fpath
        self.fpath = os.path.join(self.modelrun.fpath,self.modelrun.key)

        # read input data of first model run
        self.inpData = LandscapeModel.utils.InputData(self.fpath)
        name = self.inpData.CatchmentList[0].key # TODO
        
        # set timestep
        if self.modelrun.timestep == "minute":
            self.timestep =  cmf.min
            self.convertDeltaT = 24*60
        elif self.modelrun.timestep == "hour":
            self.timestep =  cmf.h
            self.convertDeltaT = 24
        elif self.modelrun.timestep == "day":
            self.timestep =  cmf.day
            self.convertDeltaT = 1
            
        # Create a cmf.project wiht or without substance.
        if not self.modelrun.substance == "None":
            subsInfo = self.inpData.SubstanceList[self.modelrun.substance][0]
            self.p = cmf.project(self.modelrun.substance)
            # Get the substance as variable.
            self.subs1, = self.p.solutes
            # Set plant uptake factor from database
            self.subs1.Uptake = subsInfo.plantuptake
        else:
            self.p = cmf.project()


        #######################################################################
        # Initialise the datbase database. if no path is give nthe data is only
        # in memory and not saved to disk.

        self.__initialise_database()
        
        #######################################################################
        # load meteo and rainfall TODO: check
        # self.rainstations is only a dictionary, because "self.p.rainstation_stations['some station']" 
        # not working similar to "self.p.meteo_stations['some station']" 
        self.__message("# load climate data",printMessage)
        self.stations = self.__loadClimateData(self.p,self.inpData.ClimateList)
         
        #######################################################################
        # Each sub-basin holds one outlet. The outlet is based on the class 
        # 'CatchmentOutlet'. At least one river segment must be connected to the
        # outlet. The parameters needed to define an outlet are the name as well
        # as the spatial location (x,y,z) which are defined in the SubbasinList.csv.
        self.__message("# initialise outlet",printMessage)
        self.outlet = self.__initialise_outlet(name,self.inpData.CatchmentList)
        
        #######################################################################
        # A groundwater body can be defined which holds the groudnwater of the
        # entire basin. All water which enters the basin wide groundwater storage
        # is directly routed to the outlet.         
        self.__message("# initialise groundwater",printMessage)
        self.gw = self.__initialise_groundwater(name,self.inpData.CatchmentList,self.outlet)
        
        #######################################################################
        # A catchment holds one or more reaches. During initislaisation the single
        # reaches of an catchment are connected to each other and attached to the
        # reach list of the catchment. A reach is represented by the Riversegment.py
        # class
        self.__message("# initialise reaches",printMessage)
        self.__initialise_reaches(self.inpData.ReachList,self.outlet) 
       
        #######################################################################
        # Create all field which are located in the catchment and connect them
        # with a river segment or another field. Each field is represetned by an
        # object of AgricukturalFields.py.
        # TODO: why field to field not established in Agriculturealfield.py class?
        self.__message("# initialise fields",printMessage)
        self.__initialise_fields(self.inpData,self.reaches,self.stations,self.p)

#        #######################################################################
#        # Each subcathcment holds a drift module which calculates drift input 
#        # into rivier segments or holds a time series with the respective data.
#        if withDrift:
#            print("__read drift")        
#            self.driftcalculator = DriftCalculator(self)
        self.__initialise_drift(self.reaches)

        #######################################################################
        # EFATE
        if not self.modelrun.substance == "None":
            subsInfo = self.inpData.SubstanceList[self.modelrun.substance][0]
            self.__initialise_efate(self.inpData.ReachList,self.reaches,subsInfo,T=1)

#            self.__initialise_efate_NEW(self.inpData.ReachList,self.reaches,subsInfo)

        #######################################################################
        # Create a log-file.
        self.logfile = open(os.path.join(self.fpath,"logfile.txt"),"w")
        self.logfile.write("New moderun\n")
        self.logfile.flush()

       ########################################################################
        # Create solver
        self.__initialise_solver()
        
    def __gettimestring(self):
        """Returns time string with the format: %Y-%m-%dT%H:%M """
        return  self.solver.t.as_datetime().strftime("%Y-%m-%dT%H:%M")
    timestring = property(__gettimestring)
    
    def __call__(self,printCatchmentOutput=False,printFieldOutput=False,
                 printTime=True):
        """
        Calculates plant growth and water fluxes for the entire catchment and
        stores data into database.
        

        printFieldOutput (boolean):     If true a summary of field state 
                                        variables is printed to the console window.
        """
        #######################################################################
        # This is the core run function of the entire model. When executeted, the
        # model (and all spatial entities) are run for the entire time period.
        # Data is sotred to the database if needed and a log-file created. Due 
        # to the fact that situations could occur which inhibit a numerical solution
        # of the water balance the numerical solver is autmotatically restarted two times
        # after a numerical error in order to try again to solve the system.

        # Tell the user the time period        
        if printTime:
            print ("run simulation: ",self.modelrun.begin.strftime("%Y-%m-%dT%H:%M")," --> ", self.modelrun.end.strftime("%Y-%m-%dT%H:%M"))
            print("##############################################################")
        # Write timeperiod to the logfile-
        self.logfile.write("run simulation: " + self.modelrun.begin.strftime("%Y-%m-%dT%H:%M") + " --> " + self.modelrun.end.strftime("%Y-%m-%dT%H:%M") + "\n")
        self.logfile.flush()
        
#        arrINPUT_SW = np.zeros([len(self.reaches)],dtype=np.float32)
#        arrMASS_SW  = np.zeros([len(self.reaches)],dtype=np.float32)
#        arrTEMP  = np.zeros([len(self.reaches)],dtype=np.float32)
#        arrVOL  = np.zeros([len(self.reaches)],dtype=np.float32)


        timecheck_start_run = datetime.now()        
        #######################################################################
        # Start loop. Note that the command "...solver.run" calls CMF and runs the 
        # solver for one time step in order to calcualte fluxes between all
        # storages. The plant growth processes are calculated based on Plant.py
        # and run by the AgriculturalField.py class.
        #
        # Note that the internal time step of CMF is set by the model and depends
        # on the complexity of the numerical system. Thus, even if the user sets the 
        # timestep to hourly the model could internally use minutes if the many
        # fast short time processes occur in the external defined timestep. The
        # results will be still give nfor the external time step.
        for t in self.solver.run(self.modelrun.begin,self.modelrun.end,self.timestep):
#            try:


            ###################################################################
            # The first step of the runtime loop is to run  plant growth model 
            # of all fields. Moreover, management tasks such as sowing, 
            # harvest and pestice application are condcuted.
            #
            # The field balance of the three storages groundwater, drainage and 
            # surface water can slo be taken from a timeseries for each 
            # field. In that case CMF solely reads the time series without
            # running a water balance and plant growth.
            # Either all fields have a timeseries or none. thus, checking
            # the first one is suffient.
            if len(self.fields)>0:
            
                if self.modelrun.runtype != "timeseriesCatchment" and self.modelrun.runtype != "inStream":
                    for f in self.fields:
                        # Run plant growth of each field and management tasks.
                        f(self.inpData.CropManagementList,printFieldOutput)


            # run drift and efate of each reach
            if self.modelrun.efate != "None":
                
                for reach in self.reaches:
                    
                    # get drift input
                    driftrate = reach.Drift.drift2cmf_rate(t.as_datetime(),self.subs1.Name)
                    INPUT_SW = driftrate * reach.Area
                   
                    reach.Efate.efate_run(INPUT_SW,reach.Load,reach.WaterTemperature,reach.Volume)   
            
                    # update substance mass in water
                    if (reach.Efate.reach.Efate.efate2cmf_MASS_SW())>10**(-9):
                        reach.Reach.Solute(self.subs1).state = reach.Efate.efate2cmf_MASS_SW()
                    else:
                        reach.Reach.Solute(self.subs1).state = 0
                   
#                    if INPUT_SW>0:
#                        reach.Reach.Solute(self.subs1).state = (reach.Reach.Solute(self.subs1).state+INPUT_SW)
#                        
                
                
                
                
#                # get reach parameter
#                for i,reach in enumerate(self.reaches):
#                    
#                    # get drift input
#                    driftrate = reach.Drift.drift2cmf_rate(t.AsPython(),self.subs1.Name)
#                    arrINPUT_SW[i] = driftrate * reach.Area                
#                    arrMASS_SW[i] = reach.Load
#                    arrTEMP[i] = reach.WaterTemperature
#                    arrVOL[i] = reach.Volume
#                
#                # run efate
#                self.efate(arrINPUT_SW,arrMASS_SW,arrTEMP,arrVOL)   
#                
#                print(self.efate.MASS_SW)
#                    
#                # set new mass 
#                for reach,mass in zip(self.reaches,self.efate.MASS_SW):
#                    
#                    if mass>10**(-9):
#                        reach.Reach.Solute(self.subs1).state = mass
#                    else:
#                        reach.Reach.Solute(self.subs1).state = 0                    
#                    
                    
                    

            ###################################################################
            # The data can be stored i nmemory or in a database. A database
            # is represented by CSV-file for field processes, plant growth
            # and river segments. Data mangement is handeled by Database.py.
#            if  self.modelrun.database != "None":
#                # Save data to CSV-file when the field water balances are
#                # taken from a time series.
#                if len(self.fields)>0:
#                    if self.modelrun.runtype == "timeseriesCatchment":
#                                               
#                        self.database.save_csv_cmf1dtimeseries(self)   
#                    else:
#                        # Save all data to file.
#                        self.database.save_csv(self)
#                else:
#                    self.database.save_csv_reachoutlet(self)
#            else:
#                # Save all data to memory.
#                self.database.save(self)
                
                
            if  self.modelrun.database != "None":

                self.database.save(self)                
                
                

            ###################################################################
            # Print time elapsed, model time and the water balance of the 
            # outlet and the river segments.
            if printCatchmentOutput:
                print(datetime.now()- timecheck_start_run,
                      self.timestring,"Outlet %06.3fm3"%(self.outlet.Volume),
                      " ".join([r.Name + " %06.3fm" % (r.Depth) for r in self.reaches]))
            if printTime:
                print(f'{datetime.now()- timecheck_start_run} {self.solver.t:%Y-%m-%d %H:%M}')
            else:
                if (t.day % 15 == 0) and (t.hour % 12 == 0):
                    print(f'{datetime.now()- timecheck_start_run} {self.solver.t:%Y-%m-%d %H:%M}')
    
                
            # Write moodel time to logfile.
            self.logfile.write(self.solver.t.AsDate().to_string() + "\n")
            self.logfile.flush()


            self.solver.reset()

#            except BaseException as e:
#                self.logfile.write(self.solver.t.AsDate().to_string() + " "  +str(e) +"\n")
#                self.logfile.write(self.solver.t.AsDate().to_string() + " " +"break" +"\n")
#                runtime = (datetime.now()-timecheck_start_run)
#                runtime_string = "runtime %02.0fd:%02.0fh %02.0fmin:%02.0fsec" % (runtime.days,runtime.days/24.,runtime.seconds/60., runtime.seconds)
#                self.logfile.write(runtime_string + "\n")
#                self.logfile.flush()
#                return runtime_string
            

#        runtime_string = "runtime %02.0fd:%02.0fh %02.0fmin:%02.0fsec" % (runtime.days,runtime.days/24.,runtime.seconds/60., runtime.seconds)
#        self.logfile.write(runtime_string + "\n")
#        self.logfile.flush()
#        #######################################################################
#        # When the model run is finish clise the database and the logfile.
#        if self.database_path!="": self.database.close()
#        self.logfile.close()
#        #return model runtime
        
        # close data
        
        
        self.database.finalize()
        print("runtime",datetime.now()-timecheck_start_run)
        return self


    def __message(self,s,printMessage):
        if printMessage: print(s)

    def __initialise_solver(self):
        """
        Creates solver.
        
        Attributes
        ----------
        p (CMF.Project): a cmf.project
        separate_solver(boolean): indicates if solute and water solver should
        be separated.
        threads (int): nubmer of threads
        """
        # set number of cores
        cmf.set_parallel_threads(self.modelrun.threads)

        # create solver
        try:  # get solver class from runlist
            solvertype = vars(cmf)[self.modelrun.solvertype]
            if not issubclass(solvertype, cmf.Integrator):
                raise KeyError
        except KeyError:
            raise ValueError('{} is not a cmf solver'.format(self.modelrun.solvertype))
        

                

        if self.modelrun.solutesolvertype != "None":
 
            # creat water solver class
            wsolvertype = vars(cmf)[self.modelrun.solvertype]
            wsolver = wsolvertype(self.p)
            
            # check solute solver class exists
            try:  # get solver class from runlist
                ssolvertype = vars(cmf)[self.modelrun.solutesolvertype]
                if not issubclass(ssolvertype, cmf.Integrator):
                    raise KeyError
            except KeyError:
                raise ValueError('{} is not a cmf solver'.format(self.modelrun.solutesolvertype))
            
            # create solute solverclass
            ssolver = ssolvertype(self.p)
            
            # create combined solver 
            solver = cmf.SoluteWaterIntegrator(self.p.solutes, wsolver, ssolver, self.p)
            
        else:
            solver = solvertype(self.p, 1e-9)

                
        self.solver = solver

    def __initialise_database(self):


        if self.modelrun.database == "csv":
            database =  LandscapeModel.DataBase.Database_CSV(self)
        elif (self.modelrun.database == "npy") or (self.modelrun.database == "npz"):
            database =  LandscapeModel.DataBase.Database_NP(self)   
        elif self.modelrun.database == "hdf":
            database = LandscapeModel.DataBase.Database_HDF(self)
        self.database = database
        
    def __initialise_efate(self,ReachList,reaches,subsInfo,T=1):
        """
        Creates an efate instance for each river segment.
        """


        ReachList = [ReachList[i] for i in range(len(ReachList))]
        for reach,rl in zip(reaches,ReachList):
            efate = None
            # create efate
            if self.modelrun.efate == "steps1234":
            
                efate  = Steps1234(length=reach.Length,width=reach.Width,
                        DEGHL_SW_0=subsInfo.DT50sw,
                                              DEGHL_SED_0=subsInfo.DT50sed,
                                              KOC=subsInfo.KOC,
                                              Temp0=subsInfo.Temp0,
                                              Q10=subsInfo.Q10,
                                              DENS=rl.dens,POROSITY=rl.porosity,
                                              OC=rl.oc,DEPTH_SED=rl.depth_sed,
                                              DEPTH_SED_DEEP=rl.depth_sed_deep,
                                              DIFF_L_SED=0.005,DIFF_L=0.005,
                                              DIFF_W=4.3*(10**-5),
                                              convertDeltaT=self.convertDeltaT)
            #create interface
            CMF_EFATE(reach,efate)

#    def __initialise_efate_NEW(self,ReachList,reaches,subsInfo):
#        """
#        Creates an efate instance for each river segment.
#        """
#
#
#        lengths = np.array([reach.Length for reach in reaches])
#        widths = np.array([reach.Width for reach in reaches])
#        DENS = np.array([rl.dens for rl in ReachList])
#        POROSITY = np.array([rl.porosity for rl in ReachList])
#        OC = np.array([rl.oc for rl in ReachList])
#        DEPTH_SED = np.array([rl.depth_sed for rl in ReachList])
#        DEPTH_SED_DEEP = np.array([rl.depth_sed_deep for rl in ReachList])
#
#        self.efate  = Steps1234(length=lengths,width=widths,
#                        DEGHL_SW_0=subsInfo.DT50sw,
#                                  DEGHL_SED_0=subsInfo.DT50sed,
#                                  KOC=subsInfo.KOC,
#                                  Temp0=subsInfo.Temp0,
#                                  Q10=subsInfo.Q10,
#                                  DENS=DENS,POROSITY=POROSITY,
#                                  OC=OC,DEPTH_SED=DEPTH_SED,
#                                  DEPTH_SED_DEEP=DEPTH_SED_DEEP,
#                                  DIFF_L_SED=0.005,DIFF_L=0.005,
#                                  DIFF_W=4.3*(10**-5))

    def __initialise_drift(self,reaches):
        """
        Creates a drift instance for each river segment.
        """
        for reach in reaches:
            drift = None
            if self.modelrun.drift == "xdrift":
                drift = SprayDrift(fpath=self.fpath,fname=
                                   "SprayDriftList",sep=",")
                CMF_DRIFT(reach,drift)


    def __initialise_fields(self,inpData,reaches,stations,project):
        """
        Method to initialise the fields of an subcatchment.
        
        FieldList(table):               Table with fields and attributes.
        Reaches(list):                  Reach list of subcatchment
        CropCoefficientList (table):    Table with crop coefficients
        SoilLayerList(table):           Table with soil coefficients
        Rainstations(cmf.climstations): Rainstation
        Project(cmf.project):           Current CMF project
        """
        
        #######################################################################
        # Create agricultural fields based on the information in the FieldList
        # which is defined in the input data. A field is connected either to a
        # river segment or another field.
        fields = []
        
        
        if self.modelrun.runtype != "inStream":
            for f in inpData.CellList:
                # Look for downstream reach.
                if f.reach == "None":
                    river = None
                else:
                    # Get downstream reach (the connection between river segment 
                    # and field is made in the cmf1d class)
                    river = reaches[[i.Name for i in reaches].index(f.reach)]
                fields.append(AgriculturalField(self,f,river))
                                                
                # Connect rainfall and metostation with field.
                if fields[0].soilwaterflux != "timeseries":
                    # Connect field to rainfall and meteostation
                    rainstation = [r for r in stations if r.key == f.rainstation][0].rain_station
                    meteostation = project.meteo_stations[f.meteostation]
                    rainstation.use_for_cell(fields[-1].cmf1d.c)
                    meteostation.use_for_cell(fields[-1].cmf1d.c)
            
            
            
            # Connect field with adjacent fields
            for f,flist in zip(fields,inpData.CellList):
                # Look for downstream field
                if flist.adjacent_field == "None":
                    f.adjacent_field = None    
                else:
                    # Get downstream field                
                    adjacent_field = fields[[i.key for i in fields].index(flist.adjacent_field)]
                    f.adjacent_field = adjacent_field
                    # Connect fields
                    f.cmf1d.connect_to_adjacent_field()
        
#
#        cmf.LinearStorageConnection(fields[-1].cmf1d.c.surfacewater,fields[4].cmf1d.c.surfacewater ,0.00001)  
#        cmf.LinearStorageConnection(fields[-1].cmf1d.c.surfacewater,fields[5].cmf1d.c.surfacewater ,0.00001)   
#        cmf.LinearStorageConnection(fields[-1].cmf1d.c.surfacewater,fields[7].cmf1d.c.surfacewater ,0.00001)   

        self.fields =  fields

    def __initialise_reaches(self,ReachList,outlet):
        """
        Method to initialise the reaches of thhe catchment and connect each other.
        
        ReachList(table):        Information on each reach.
        outlet(CatchmentOutlet): Object of catchment outlet.
        """
        # Create lsit with RiverSegment.py objects for each reach defined in
        # the reach list.
        reaches = []
        for reach in ReachList:           
            # get coords
            x1 = reach.x
            y1 = reach.y
            z1 = reach.z
            if reach.downstream == outlet.Name:
                x2 = outlet.x
                y2= outlet.y
                z2 = outlet.z
            else:

                x2 = ReachList[reach.downstream][0].x
                y2 = ReachList[reach.downstream][0].y
                z2 = ReachList[reach.downstream][0].z
                
            #calculate flow width               
            flowwidth = np.sqrt((x2-x1)**2 + (y2-y1)**2 + (z2-z1)**2)
            #create RiverSegment object and attach to reach list.
            reaches.append(RiverSegment(self,reach.key,reach.x,reach.y,reach.z,
                                             reach.downstream,reach.initial_depth,
                                             reach.manning_n,flowwidth,
                                             reach.shape,reach.bankslope,
                                             reach.bottomwidth,
                                             reach.floodplainslope))
                                             

        #Connect reaches with each other and/or the catchment outlet.
        for r in reaches:
            if r.Downstream == self.outlet.Name:
                # connect reach with outlet
                r.Reach.set_outlet(outlet.Outlet)
                r.set_downstreamStorage(outlet.Outlet)
            else:
                #find downstream reach
                downstream_reach = reaches[[i.Name for i in reaches].index(r.Downstream)].Reach
                #connect to downstream reach
                r.Reach.set_downstream(downstream_reach)
                r.set_downstreamStorage(downstream_reach)
                     
        # load time serires reaches
        for reach in reaches:
            fn = os.path.join(self.fpath,"TimeSeries",reach.Name+"."+self.database.ext)
            if os.path.isfile(fn) :
                #print("load data: ",reach.Name)
                # get time series
                dat=self.database.load_timeseries("reaches",reach.Name)               
                begin = self.database.strDate2pyDate(dat[0]["time"])
                # set timeseries
                reach.Flux = cmf.timeseries.from_sequence(begin,self.timestep,dat["flow"])  
                if not self.modelrun.substance == "None":
                    reach.NBC.concentration[self.subs1] = cmf.timeseries.from_sequence(begin ,self.timestep,dat["conc"])   #mg/m3 

        # Return the reach list.
        self.reaches =  reaches

    def __initialise_groundwater(self,key,CatchmentList,outlet):
        """
        Method to initisalie a catchment-wide groundwater storage. The storage
        is optional.
        
        CatchmentList(table): List with the propertie of the subbasin.
        """
        # Get groundwater sotrage attributes from subbasin list
        gwinfo = CatchmentList.getbyAttribute(key,"component","Groundwater")
        # Create dummy groundwater storage if nothing has been defined.
        if not len(gwinfo)>0: #no gw body
            gw =  None#CatchmentGroundwater('None',None,None,None,None)
        # Create a groundwater storage according to the settings in the subbasin
        # list, initilise with the project and connect the storage with a kinematic
        # wave with the catchment outlet.
        else:
            gw = CatchmentGroundwater("Groundwater",x=gwinfo[0].x,y=gwinfo[0].y,z=gwinfo[0].z,residencetime=gwinfo[0].residencetime)
            gw.initialisze_with_project(self)
            cmf.LinearStorageConnection(gw.Storage,outlet.Outlet,gw.residencetime)
        return gw

    def __initialise_outlet(self,key,CatchmentList):
        """
        Method to initisalie the outlet as defined in the subbasin list.
        
        SubbasinList(table): List with the propertie of the subbasin.
        """
        # Get information of outlet of current subbasin.
        outletinfo = CatchmentList.getbyAttribute(key,"component","Outlet")[0]
        # Create an outtlet object based on spatial location.
        outlet = CatchmentOutlet("Outlet",  outletinfo.x,outletinfo.y,outletinfo.z)
        # Initisalise outlete with catchment.
        outlet.initialisze_with_project(self)
        return outlet


    def __loadClimateData(self,p,ClimateList):
        """
        Load climate data.
        """
        stations = []
        for cs in ClimateList:
            stations.append(LandscapeModel.utils.ClimateStation(project = p,cs=cs,fpath=self.fpath,fname=cs.key,sep=",",date_format="%Y-%m-%dT%H:%M"))
        return stations
    
    def get_flowwidths(self):
        outlet = [i for i in self.inpData.CatchmentList if i.component == "Outlet"][0]
        flowwidth = []
        for reach in self.inpData.ReachList:           
            # get coords
            x1 = reach.x
            y1 = reach.y
            z1 = reach.z
            if reach.downstream == "Outlet":
                x2 = outlet.x
                y2= outlet.y
                z2 = outlet.z
            else:
                x2 = self.reaches[reach.downstream][0].x
                y2 = self.reaches[reach.downstream][0].y
                z2 = self.reaches[reach.downstream][0].z
                #calculate flow width               
            flowwidth.append((reach.key,np.sqrt((x2-x1)**2 + (y2-y1)**2 + (z2-z1)**2)))
        return flowwidth
    
    
    
    
    
