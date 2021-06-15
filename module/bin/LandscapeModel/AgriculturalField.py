# -*- coding: utf-8 -*-
"""
Created on Mon Sep 11 13:36:16 2017

@author: smh
"""
from .Plant import Plant
from .Cmf1d_richards import Cmf1d_richards
from .Cmf1d_storage import Cmf1d_storage
from .Cmf1d_timeseries import Cmf1d_timeseries
from .Cmf1d_richards_bucket import Cmf1d_richards_bucket
from LandscapeModel.utils import convert_Koc_to_Kd,calc_Q10FAC,calc_FOCUS_degradationfactor_depth,calc_FOCUS_degradationfactor_theta,calc_LinearSoilTemperature
from LandscapeModel.utils.Parameter import Parameter

class AgriculturalField(Parameter):
    """
    Represents an agricultural field which consits of an cmf1d cell and a 
    plant object. The latter one calculates baresoil evaporation when no
    crop is cultivated or E+T for a specifoc field crop.
    
    The plant is connected via a NeumanBoundary with the soil layer.
    
    The cmf1d cell holds a serveal soil layer, a groundwater and surface
    water storage which are connected with the river segment of the field.
    
    Will be extended with other models, e.g. for calcualting drift  
    """
    def __init__(self,catchment,cell_info,river):
        """
        catchment (Subcatchment):               instance of SubCatchment class
        cell_info (cell_info):                     table with cell_info



        river (cmf.reach):                      river which is connected to surface, groundwater
                                                and drainage flow of the cell.       
        soillayerInfo (Table):                  Table which holds the paramterization of
                                                the soil layer.
        CropCoefficientList (table):            table with crop coefficents.
        """
        #######################################################################

        # set cell specific paramter from input table    
        
        Parameter.__init__(self, cell_info.__dict__.keys(), cell_info.__dict__.values())

        # catchment
        self.catchment = catchment
        #landuse
        self.plant = None
        #river
        self.river = river

        #######################################################################
        # create cmf1d
        # The field is presented by several soil layer and up to three storages
        # (groundwater, surface water, optionally draiange). In case of "richards"
        # and "storage" the water fluxes from the soil to the three storages 
        # are calcualtes based on a Richards and Storage apprach. In case of 
        # timeseries, the water fluxes from the cell/field to the storages
        # are taken from a database.
        
        if self.catchment.modelrun.runtype == "timeseriesCatchment":
            self.cmf1d = Cmf1d_timeseries(self)   
        else:
            if self.soilwaterflux =="richards":
                self.cmf1d = Cmf1d_richards(self)
            elif  self.soilwaterflux =="storage":
                self.cmf1d = Cmf1d_storage(self)
     
            elif  self.soilwaterflux =="richards_bucket":
                self.cmf1d = Cmf1d_richards_bucket(self)
               
        #######################################################################
        # create plant with baresoil conditions  
        #
        # Evaporation from bare soil is also calculated by teh plant model (Plant.py).
        # all plant parameters are set to zero or None and only evaporation is 
        # calculated and extraction from the upper soil layer (by default from
        # the upper soil layer 10 cm below ground, can be set by the user).
        #
        # The evaporation depth (evap_depth) is related to the center of each
        # soil layer.                                                  
        soil_delta_z = [l.thickness for l in self.cmf1d.c.layers]
        soil_zm = [(l.upper_boundary + l.lower_boundary)/2. for l in self.cmf1d.c.layers]  
        soil_evap_depth = [1 if i <= self.evap_depth else 0 for i in soil_zm]
        # create a plant object parameterized for bare soil conditions. This 
        # object is available with the initialization of an agricultural field.
        # During simulation this object can be replaced by an instance another
        # crop (perennial, annual) for a specific growing season. When a crop is 
        # harvested the self.plant attribute is again set up with bare soil 
        # conditions
        self.plant = self.set_plant_parameter("baresoil",soil_delta_z,soil_zm,soil_evap_depth)
        
    def __call__(self,ManagementList,printFieldOutput):
        """
        Check management for any task to conduct and run plant growth. The
        function is called by the owning catchment class. The function manages
        the following processes in consecutive order:
        
        (1) Check management list for tasks: sowing or pesticide application.
        (2) Check harvest of cultivated crop.
        (3) Run plant growth processes.
        (4) run soil-plant interaction processes.
        
        ManagementList (table):  Table with management tasks related to field.  
        printFieldOutput (Boolean):   Indicates if a model output is written to console.
        """
        #######################################################################
        #get current time from solver.
        t = self.catchment.solver.t
        
        #######################################################################
        # The management list holds all tasks to be conducted on the field which
        # are related to sowing, harvest and pesticide application. The management
        # tasks are selected for the specific time and field. Management tasks
        # are sowing and pesticide application. harvest is caclulated in the
        # next step.
        self.manageField(t,ManagementList)
                                        
        #######################################################################
        # When a plant is cultivated check harvest date according to plant DAS.
        # (but only when a crop is cultivated and annual; perennial crops are
        # not harvested)
        self.harvest(t)

        #######################################################################
        # run plant model for one time step
        #
        # Plant gorwth consists of thre major processes: plant developement (as
        # defined by number of days to derivde a specifc growign season), root
        # and leaf development and soil water extraction (evaporation, transpiration)
        self.plant(t,self.cmf1d,self.cmf1d)   
        
        #######################################################################
        # run processes realted to soi plant interaction
        #
        # Soil water abstraction is caclulated based on the plant growth
        # concept of MACRO 5.2 (see Plant.py). Soil water extractions consists
        # of evaporation from the upper soil layer (by default 10 cm below
        # surface, can be modified by the user) and the transpiration flux
        # from the rooting zone (water uptake varies with rooting 
        # depth and distribution across soil layer).
        #               
        # when using the cmf vegetation object the Plant model of MACRO is used
        # to calcualte LAI and rooting depth based on a fixed interval of
        # four development stages according to the das after sowing
        self.run_soilplant_processes()
        
        #######################################################################
        #adjust decay rate 'TODO
#        self.calc_decay():
    
        #######################################################################
        # print output
        if printFieldOutput:    
            if self.plantmodel == "macro":
                print  (t,self.key, "DAS %03d RD %.2fm GLAI %.2f LAI %.2f PET %.2fmm Epot %.2fmm Tpot %.2fmm Eact %.2fmm Tact %.2fmm"%(self.plant.DAS,self.plant.RootingDepth,self.plant.GLAI,self.plant.GLAI,self.plant.PET,self.plant.Epot,self.plant.Tpot,self.plant.Eact,self.plant.Tact))
            elif self.plantmodel == "cmf":
                print  (t,self.key, "DAS %03d RD %.2fm GLAI %.2f LAI %.2f Eact %.2fmm Tact %.2fmm"%(self.plant.DAS,self.plant.RootingDepth,self.plant.GLAI,self.plant.GLAI,self.cmf1d.Eact,self.cmf1d.Tact))

    def manageField(self,t,ManagementList):
        """
        Function that conducts field management. Sowign and pesticide application
        are supported.
        
        t(cmf.time):            Current time.
        ManagementList (table): Table with management tasks.
        """
        #comvert current time to string
#        timestring =  "%i-%02d-%02dT%02d:00"%(t.year,t.month,t.day,t.hour)
        
        

        manageTasks = self.catchment.inpData.CropManagementList.getbyAttribute(self.key,"date",t.as_datetime())
        
    
        
        
        
        # Conduct tasks if available else do nothing      
        if len(manageTasks) >0:
            # Conduct all taskts in list.
            for task in manageTasks:
                # Tell the use the name of the taks whch will be conducted.
                print(t,self.key,task.task,task.description)
                # Currently two tasks are considered: sowing and pesticide 
                # application. The tasks harvest is caclulated by the plant 
                # model since harvset is definded i nthe crop coefficient table
                # as fixed nubmer of days after sowing.
                # check if sowing event occurs
                if task.task == "sowing":
                    # get soil information to caclulate the center of each soil 
                    # layer in order to asses evaporation layers.
                    soil_delta_z = [l.thickness for l in self.cmf1d.c.layers]
                    soil_zm = [(l.upper_boundary + l.lower_boundary)/2. for l in self.cmf1d.c.layers]  
                    soil_evap_depth = [1 if i <= self.evap_depth else 0 for i in soil_zm]
                    # Get crop name and set plant parameters
                    crop = task.description
                    self.plant = self.set_plant_parameter(crop,soil_delta_z,soil_zm,soil_evap_depth)
                    #Write info to logfile
                    self.catchment.logfile.write( self.key + ", " + task.task + ", " + task.description+ "\n")
                    self.catchment.logfile.flush()
                # Check if pesticdes are applied.
                if task.task == "ApplyPesticide":
                    
                    
                    if not self.catchment.modelrun.substance == "None":
                    
                        # Apply pesticide into surface water storage. Aapplication 
                        # rates are given in g/ha, so values are convert to m2 (/10000.) 
                        # and then multiply by the field are to derivde the total 
                        # amount of substance applied to the specific field. The 
                        # format of 'description' is fixed and listed i nteh management
                        # table.
                        # Get name of substance
      
                        # The substance can be applied to the soil surface or directly
                        # incorporated into the upper soil layer.
                        # Get application method.
                        substance_applmethod = task.description.split(" ")[1]
                        # Apply pesticide according to application method.
                        if substance_applmethod == "GroundSpray":
                            # In case of ground spray the substanc eis applied to the 
                            # surface water storage.
                            substance = float(task.value) * 0.1 * self.area  # convert g/ha to mg/m2 and multiply by area
                            self.cmf1d.c.surfacewater.Solute(self.catchment.substance).state = substance
                            #Write info to logfile
                            self.catchment.logfile.write( self.key + ", " + task.task + ", " + task.value + ", "+ task.description+ "\n")
                            self.catchment.logfile.flush()
                            
                        elif substance_applmethod == "SoilIncorporation":
                            # In case of soik incroporation the substance is applied
                            # into the soil layer realted to the given incorporation depth.
                            depth = float(task.description.split(" ")[2])
                            l = [L for L in self.cmf1d.c.layers if L.lower_boundary >= min(depth, self.cmf1d.c.layers[-1].lower_boundary)][0]
                            substance = float(task.value) * 0.1 * self.area  # convert g/ha to mg/m2 and multiply by area
                            l.Solute(self.catchment.substance).state = substance
                            #Write info to logfile
                            self.catchment.logfile.write( self.key + ", " + task.task + ", " + task.value + "g/ha, "+ task.description+ "m\n")
                            self.catchment.logfile.flush()
                        # The solver of CMF has to be restarted in order to recalculate
                        # state variables considering the applied substance.
                        self.catchment.solver.reset() #
    
    def harvest(self,t):
        """
        Checks is a plant is cultivated. If so, the current number of days after
        sowing are compared with the harvest date as give ni ndys after sowing.
        When a plant is harvested the current plant object is replaced by 
        baresoil conditions.
        """
        #check if a plant is cultivated
        if self.plant.Name != "baresoil":
            #check if the plant is an annual crop           
            if self.plant.CropType == "annual":
                # check if the cumulative days after sowing are larger or equal
                # to the harvest date (as defined in days).
                if self.plant.DAS >= self.plant.Harvest:
                    # The harvest taks just deleles the specifc plant object
                    # with a plant object paramterized based on bare soil 
                    #conditions.
                    # Tell the user that the plant is harvested.
                    print(t,self.key,"harvest",self.plant.Name)
                    # Get some information for calcuating evpaoration from soil layer
                    soil_delta_z = [l.thickness for l in self.cmf1d.c.layers]
                    soil_zm = [(l.upper_boundary + l.lower_boundary)/2. for l in self.cmf1d.c.layers]  
                    soil_evap_depth = [1 if i <= self.evap_depth else 0 for i in soil_zm]
                    # Create a plant which is paramterized for baresoil conditions.
                    self.plant = self.set_plant_parameter("baresoil",soil_delta_z,soil_zm,soil_evap_depth)
        
    def run_soilplant_processes(self):
        """
        Run all processes which have to be synchronized between the plant and 
        the soil. This includes currently soil water abstraction and in case of
        modelling platn water proceses with CMF the setting of CMF plant parameter
        as calculated with MACRO (green LAI, rooting depth, plant height).
        """
        if self.plantmodel == "macro":
            #######################################################################
            # Soil water abstraction is caclulated based on the plant growth
            # concept of MACRO 5.2 (see Plant.py). Soil water extractions consists
            # of evaporation from the upper soil layer (by default 10 cm below
            # surface, can be modified by the user) and the transpiration flux
            # from the rooting zone (water uptake varies with rooting 
            # depth and distribution across soil layer).
            flux = [-fl * self.area / 1000.   for fl in  self.plant.SoilWaterExtraction] # convert mm to m3/area    * self.area / 1000.  
            self.cmf1d.flux = flux 
 
        elif self.plantmodel == "cmf":
            ######################################################################
            # when using the cmf vegetation object the Plant model of MACRO is used
            # to calcualte LAI and rooting depth based on a fixed interval of
            # four development stages according to the das after sowing
            self.cmf1d.c.vegetation.LAI = self.plant.GLAI
            self.cmf1d.c.vegetation.RootDepth = self.plant.RootingDepth
            self.cmf1d.c.vegetation.Height = self.plant.Height
        
    def set_plant_parameter(self,crop,soil_delta_z,soil_zm,soil_evap_depth):
        """
        Create a plant opbject for calculating the evaporation from bare soil
        conditions. All paramters are constant.
        """
        # get crop coefficent set
        cc = self.catchment.inpData.CropCoefficientList[crop][0]

        # Create a plant object specific or the current crop.
        plant = Plant(self,name=cc.key,
                       GLAImax=cc.GLAImax,GLAImin=cc.GLAImin,GLAIharv=cc.GLAIharv,
                       Dstart=cc.Dstart,Dmin=cc.Dmin,Dmax=cc.Dmax,Dharv=cc.Dharv,
                       cform=cc.cform,dform=cc.dform,
                       rootinit=cc.rootinit,rootmax=cc.rootmax,
                       heightinit=cc.heightinit,heightmax=cc.heightmax,
                       rpin=cc.rpin,
                       soil_delta_z=soil_delta_z,
                       soil_zm=soil_zm,
                       soil_evap_depth=soil_evap_depth,
                       feddes=[cc.feddes1,cc.feddes2,cc.feddes3,cc.feddes4],
                       croptype=cc.croptype,
                       altitude=self.z,latitude=self.latitude,maxcomp=2.,a_f=0.6,wintercrop=cc.wintercrop)
        return plant
        
#    def calc_decay(self):
#        """
#        The decay rate has to be adpated to the assumtpions made in FOCUS
#        scenarios. The steps include an adjusment to depth, soil termperature
#        and water content.
#        """
#        #######################################################################
#        # set decay rate and adjust accoring to environmental conditions and depth
#        # the decay rate is adjusted according to FOCUS guidance for depth, temperature and theta
#        # see lanscapemodel.utils for details
#        # get surface temerpature
#        surface_temperature = (self.cmf1d.c.get_weather(t).Tmax+self.cmf1d.c.get_weather(t).Tmin)/2.
#        # get depth of profile
#        depth_profile = self.cmf1d.c.layers[-1].boundary[1]
#        #get average temerpature at bottom boudnary of soil profile
#        bottom_temperature = 10. #TODO equal to annual average temperature?
#        #depth adjustment
#        for l in self.cmf1d.c.layers:
#            l_center = (l.boundary[0]+l.boundary[1])/2
#            #depth adjustment
#            adjustment_decay_depth = calc_FOCUS_degradationfactor_depth(l_center) # on the basis of layer center depth
##            #theta adjustment
##            adjustment_decay_theta = calc_FOCUS_degradationfactor_theta(l.theta, l.soil.Wetness_pF([1.8]))
##            #calculate temperature forthe layer
##            layer_temperature = calc_LinearSoilTemperature(surface_temperature,bottom_temperature,l_center,depth_profile)
##            #calculate Q10FAC
##            adjustment_decay_Q10FAC = calc_Q10FAC(layer_temperature,bottom_temperature,QFAC=self.catchment.substancedata["QFAC"])
##            # calculate decay rate
#            l.Solute(self.catchment.substance).decay = 1 / self.catchment.substancedata["DT50soil"] #/ adjustment_decay_depth) #)adjustment_decay_Q10FAC #* adjustment_decay_depth * adjustment_decay_theta
##             TODO: note that decay is given in 1/day in cmf!!!!!!!!!!!!

        
        
        
        
        
        
        
        
        
        
        
        
        
        
        