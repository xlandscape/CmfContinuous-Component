# -*- coding: utf-8 -*-
"""
Created on Mon Sep 11 13:36:16 2017

@author: smh
"""
import numpy as np
import cmf
from LandscapeModel.utils import convert_Koc_to_Kd

class Cmf1d(object):
    def __init__(self,AgricultureField):
        """ Creates a new cell 
        
        The soil layer are paramterized according to the input table from
        AgriculturalField.SoilLayerInfo. Each soil layer holds a Neuman-
        Boundary which enables the connection to the plant model.
        
        Surface runoff is caclulated based on GreenAmptInfiltration and 
        connected with a river segment by KinematicSurfaceRunoff. Other 
        connection types are possible.
        
        A groundwater storage recieves water from the lowest soil layer
        vie Richards' flow. The gr storage is connected with the river 
        segment with LinearStorageConnection.

        A drainage can be installed which enables wate rflow from a specific 
        deprh into the river segment.     
        
        Plant ET is modelled with CMDF or Plant.py. In both cases, plant LAI and 
        development is calcualted by Plant.py.
        
        A linear isotherm for adsorption is assumed with a decay rate according
        to substance information.
        
        Soil column and reaches can be connected in different ways as defined
        in the input file, e.g. the sw,gw and drainage storage of one cell can
        be connected with a river segment or another soil column. Moreover, not
        all storages (sw,gw,drainage) must be considered.
        
        Note that CMF1d represents the base class for the implementation of other
        more specific setups of CMF:
            - Cmf1d_richards.py
            - Cmf1d_storage.py
            - Cmf1d_timeseries.py
            
        """
        
        #######################################################################
        # attributes
        # agriculture fields which holds the cmf1d isnstance
        self.af = AgricultureField
        # list for NeumannBoundaries which manage plant water uptake
        self.bc=[]
        
        #######################################################################
        # create cell
        

        self.c = self.af.catchment.p.NewCell(self.af.x,self.af.y,self.af.z,
                                             self.af.area,with_surfacewater=True) 

        #######################################################################        
        # create groundwater storage
        self.groundwater = self.af.catchment.p.NewStorage('groundwater',
                                                          x=self.af.x,y=self.af.y,z=self.af.z-self.af.gw_depth) 

    def create_vegetation(self):
        """
        Connects the cell to a cmf vegetation object with standard values. Crop
        height, rooting depth and LAI is calculated with the MACRO plant growth
        classPlant.py. Root growth is calculated based on a fixed distribution
        of root related to the actual depth. Plant water uptake according
        to Feddes et al..
        """
        # use Shuttleworth-Wallace
        self.c.install_connection(cmf.ShuttleworthWallace)
        # set some inital parameter
        self.c.vegetation.fractio_at_rootdepth = 0.8
        self.c.vegetation.albedo = 0.23
        self.c.vegetation.CanopyClosure = 1.0
        self.c.vegetation.CanopyPARExtinction = 0.7 #0.5 to 0.7
        self.c.vegetation.StomatalResistance = 100 #100 - 300
        if len(self.af.catchment.p.solutes)>0:
            subsInfo = self.af.catchment.inpData.SubstanceList[self.af.catchment.modelrun.substance]
            # set plant uptake
            for etcon in self.c.transpiration.connections:
                etcon.set_tracer_filter(self.af.catchment.subs1,subsInfo.plantuptake)

    def connect_to_catchment_gw(self):
        """
        connects the groundwater storage of hte single cell to the groundwater
        storages of the catchment.
        """
        # connect to catchment groundwater body if needed
        cmf.LinearStorageConnection(self.groundwater,self.af.catchment.gw.Storage,self.af.deep_gw_rt) 

    def connect_to_adjacent_river(self):
        """
        Connects the field to an adjancent field. The connections depends on
        the type, e.g. "RO" (runoff) and/or "GW" (groudnwater) and/or
        "DR" (drainage). The type of connection is defined in the input data
        in Fields.csv.
        """
        # calculate flow width
        
        if self.af.unit_traveltime == "ksat":
            # calculate distance between both storages
            distance = np.sqrt((self.af.river.x - self.af.x)**2 + (self.af.river.y - self.af.y)**2 + (self.af.river.z - self.af.z)**2)  
            #calculate residancetime in days        
            res_time_gw = distance / self.af.residencetime_gw_river
            res_time_dr = distance / self.af.residencetime_drainage_river
            
       
            
        elif self.af.unit_traveltime == "day":
            #calculate residancetime in days        
            res_time_gw =  self.af.residencetime_gw_river
            res_time_dr = self.af.residencetime_drainage_river
        # connect to adjacent storage
        if self.af.reach_connection.find("GW") > -1:
            
            
            cmf.LinearStorageConnection(self.groundwater,self.af.river.Reach ,res_time_gw) 
        if self.af.reach_connection.find("DR") > -1:
            cmf.LinearStorageConnection(self.drainage,self.af.river.Reach,res_time_dr) 
        if self.af.reach_connection.find("RO") > -1:
            #TODO: test???
            if self.af.soilwaterflux == "timeseries":
                cmf.LinearStorageConnection(self.c.surfacewater,self.af.river.Reach ,0.00001)   
            else:
                cmf.KinematicSurfaceRunoff(self.c.surfacewater,self.af.river.Reach,flowwidth=self.af.flowwdith_sw)  

    def connect_to_adjacent_field(self):
        """
        Connects the field to an adjancent field. The connections depends on
        the type, e.g. "RO" (runoff) and/or "GW" (groudnwater) and/or
        "DR" (drainage). The type of connection is defined in the input data
        in Fields.csv.
        """
        
        adjCell = self.af.adjacent_field
        


        if self.af.unit_traveltime == "ksat":
            # calculate distance between both storages
            distance = np.sqrt((adjCell.x - self.af.x)**2 + 
                               (adjCell.y - self.af.y)**2 + 
                               (adjCell.z - self.af.z)**2)  
            
            
            #calculate residancetime in days        
            res_time_gw = distance / self.af.residencetime_gw_river
            res_time_dr = distance / self.af.residencetime_drainage_river
        


        
        elif self.af.unit_traveltime == "day":
            #calculate residancetime in days        
            res_time_gw =  self.af.residencetime_gw_river
            res_time_dr = self.af.residencetime_drainage_river
            
            
        #set water flow connection
        if self.af.field_connection.find("RO")>-1:
            #TODO: test???
            if self.af.soilwaterflux == "timeseries":
                cmf.LinearStorageConnection(self.c.surfacewater,adjCell.cmf1d.c.surfacewater ,0.00001)   
            else:
                cmf.KinematicSurfaceRunoff(self.c.surfacewater,adjCell.cmf1d.c.surfacewater,self.af.flowwdith_sw)
        if self.af.field_connection.find("GW")>-1:
            
            
            cmf.LinearStorageConnection(self.groundwater,adjCell.cmf1d.groundwater,res_time_gw)
        if self.af.field_connection.find("DR")>-1:
            cmf.LinearStorageConnection(self.drainage,adjCell.cmf1d.drainage,res_time_dr)

   
    def add_drainage(self, depth, suction_limit, t_ret):
        """
        Adds a drainage with a kinematic wave representation at depth.
        Here, the drainage becomes active when the layer saturation is above field capacity
        :param: depth in m
        :param: suction_limit The drainage becomes active below the suction pressure in m. 
                Field capacity is between pF 1.8 to pF 2.5, that is a suction pressure between 0.63 - 3.16m
        :param: t_ret Retention time in drainage 
        :returns: A dictionary describing the drainage
        
        """
        l = [L for L in self.c.layers if L.lower_boundary >= min(depth, self.c.layers[-1].lower_boundary)][0]
        drainage = self.af.catchment.p.NewStorage('drainage at ' + str(l), self.c.x + 10, self.c.y, l.position.z) #TODO: why +10 ? possible to use NewStorage instet of NewOutlet ??ß
        # Calculate the water content from the suction limit
        Vret = l.soil.Wetness([-suction_limit])[0] * l.get_capacity()
        # Make the linear storage cnnection with residence time t_ret and the residual volume
        cmf.LinearStorageConnection(l, drainage, residencetime=t_ret, residual=Vret)
        # return the building blocks of the drainage
        return drainage,l# dict(outlet=outlet, depth=depth, layer=l, connection=connection, Vret=Vret)


    ###########################################################################
    # Properties: water flows
    
    def __getqperc(self):
        """Returns percolation to groundwater (m3)."""
        t = self.af.catchment.solver.t
        return  self.c.layers[-1].flux_to(self.groundwater,t) 
    qperc = property(__getqperc)
    
    def __getqsurf(self):
        """Returns surface water flow to the river segment (m3)."""
        t = self.af.catchment.solver.t
        if self.af.river != None:
            return  self.c.surfacewater.flux_to(self.af.river.Reach,t)
        elif self.af.adjacent_field != None:
            return  self.c.surfacewater.flux_to(self.af.adjacent_field.cmf1d.c.surfacewater,t)
        else:
            return 0. 
    qsurf = property(__getqsurf)
    
    def __getqdrain(self):
        """Returns drainage flow to the river segment (m3)."""
        if self.af.hasDrainage:
            t = self.af.catchment.solver.t
            if self.af.river != None:
                return  self.drainage.flux_to(self.af.river.Reach,t)
            elif self.af.adjacent_field != None and self.af.field_connection.find("DR") >-1:
                return  self.drainage.flux_to(self.af.adjacent_field.cmf1d.drainage,t)
            else:
                return self.drainage_layer.flux_to(self.drainage,t)
        else:
            return 0.0
    qdrain = property(__getqdrain)         
    
    def __getqgw_river(self):
        """Returns groundwater flow to the river segment (m3)."""
        t = self.af.catchment.solver.t
        if self.af.river != None:
            return  self.groundwater.flux_to(self.af.river.Reach  ,t) 
        elif self.af.adjacent_field != None and self.af.field_connection.find("GW") > -1:
            return  self.groundwater.flux_to(self.af.adjacent_field.cmf1d.groundwater,t) 
        else:            
            return 0.0 #TODO: 
    qgw_river = property(__getqgw_river) 
    
    def __getqgw_gw(self):
        """Returns groundwater flow to the catchment groundwater (m3)."""
        t = self.af.catchment.solver.t
        if self.af.deep_gw == True:
            return  self.groundwater.flux_to(self.af.catchment.gw.Storage,t) 
        else:            
            return 0.0
    qgw_gw = property(__getqgw_gw) 

    def __getVsw(self):
        """Water volume in (m3)"""
        return  self.c.surfacewater.volume
    Vsw = property(__getVsw)
    
    def __getVgw(self):
        """Water volume in (m3)"""
        return  self.groundwater.volume
    Vgw = property(__getVgw)
    
    def __getVdr(self):
        """Water volume in (m3)"""
        
        if self.af.field_connection.find("DR") >-1:
            return self.drainage.volume
        else:
            return 0.0
    Vdr = property(__getVdr)

    ###########################################################################
    # Properties: solute load and concentration
    
    def __getconcsoil(self):
        """Returns the substance concentration in each soil layer (mg/m3)."""
        t = self.af.catchment.solver.t
        
        
        if len(self.af.catchment.p.solutes)>0:
            return  [l.conc(t,self.af.catchment.p.solutes[0])  for l in self.c.layers] #  g/m3  
        else:
            return  [0  for l in self.c.layers] #  g/m3  
    concsoil = property(__getconcsoil)       

    def __getconcgw(self):
        """Returns substance concentration in groundwater (mg/m3)."""
        t = self.af.catchment.solver.t
        if len(self.af.catchment.p.solutes)>0:
            return  self.groundwater.conc(t,self.af.catchment.p.solutes[0]) 
        else:
            return 0.0
    concgw = property(__getconcgw)      

    def __getconcsw(self):
        """Returns substance concentration in surface water (mg/m3)"""
        t = self.af.catchment.solver.t
        if len(self.af.catchment.p.solutes)>0:
            return self.c.surfacewater.conc(t,self.af.catchment.p.solutes[0]) 
        else:
            return  0 #  g/m3  
    concsw = property(__getconcsw)      

    def __getconcdrainage(self):
        """Returns substance concentration in surface water (mg/m3)."""
        t = self.af.catchment.solver.t
        if self.af.hasDrainage:
            if len(self.af.catchment.p.solutes)>0:
                return  self.drainage.conc(t,self.af.catchment.p.solutes[0]) 
            else:
                return 0
        else:
            return 0.0    
    concdrainage = property(__getconcdrainage)      


    ###########################################################################
    # Properties: flux connections, state and attributes of soil layer
    def __getVsoil(self):
        """Returns water volume of each soil layer."""
        return  [l.volume for l in self.c.layers]
    Vsoil = property(__getVsoil)     
    
    def __get_flux(self):
        """Returns water balance of NeumannBoundary per layer. """
        return np.array([-bc.water_balance(cmf.Time()) for bc in self.bc])
    def __set_flux(self,fluxes):
        """Sets fluxes of NeumannBoundary per layer. """
        for i,bc in enumerate(self.bc):
            if i<len(fluxes):
                bc.flux= fluxes[i] # cmf.timeseries(fluxes[i])
            else:
                bc.flux= 0.0 # cmf.timeseries(0.0)        
    flux=property(__get_flux,__set_flux)

    def __get_Kr(self):
        fieldcapacity=[l.soil.Wetness_pF([1.8]) for l in self.c.layers]
        wiltingpoint=[l.soil.Wetness_pF([4.2]) for l in self.c.layers]
        wetness = [l.wetness for l in self.c.layers]
        kr = [cmf.piecewise_linear(w,0.5*wp,0.5*(fc+wp)) for w,fc,wp in zip(wetness,fieldcapacity,wiltingpoint)]
        return kr
    Kr = property(__get_Kr)

    def __getPressureHead(self):
        """Returns pressurehead of each soil layer (cm)."""
        return [l.matrix_potential*-100 for l in self.c.layers]
    PressureHead = property(__getPressureHead) 

    ###########################################################################
    #some functions to provide climate information for the plant model
    def get_tmin(self,time):
       """ Time as datetime instance: datetime(JJJJ,MM,DD); Returns minimal temperature in Celsius """
       return self.c.get_weather(time).Tmin
    def get_tmax(self,time):
        """ Time as datetime instance: datetime(JJJJ,MM,DD); Returns maximal temperature in Celsius """
        return self.c.get_weather(time).Tmax
    def get_Rs(self,time):
        """ Time as datetime instance: datetime(JJJJ,MM,DD); Returns total solar radiation in [MJ m-2]"""
        return self.c.get_weather(time).Rs
    
    def get_Sunshine(self,time):
        """ Time as datetime instance: datetime(JJJJ,MM,DD); Returns total solar radiation in [MJ m-2]"""
        return self.c.get_weather(time).sunshine 
    def get_Windspeed(self,time):
        """ Time as datetime instance: datetime(JJJJ,MM,DD); Returns total solar radiation in [MJ m-2]"""
        return self.c.get_weather(time).Windspeed  
    def get_rHmean(self,time):
        """ Time as datetime instance: datetime(JJJJ,MM,DD); Returns total solar radiation in [MJ m-2]"""
        return self.c.get_weather(time).rHmean          
    
    def get_rain(self):
        """Returns total rainfall in (mm)"""
        time = self.af.catchment.solver.t
        return self.c.get_rainfall(time) 

    ###########################################################################
    # properites vegetation    
    def __getTact(self):
        """Returns actual transpiration (m3). """
        t = self.af.catchment.solver.t
        return self.c.transpiration(t) 
    Tact = property(__getTact)    
    
    def __getEact(self):
        """Returns actual evaporation (m3)."""
        t = self.af.catchment.solver.t
        return  self.c.evaporation(t) 
    Eact = property(__getEact)  


       

#        #######################################################################
#        # canopy storage
#                # Make c.canopy a water storage
#        self.c.add_storage('Canopy','C')
#        # Split the rainfall from the rain source (RS) between 
#        # intercepted rainfall (RS->canopy) and throughfall (RS-surface)
#        cmf.Rainfall(self.c.canopy,self.c,False,True) # RS->canopy, only intercepted rain
#        cmf.Rainfall(self.c.surfacewater,self.c,True,False) # RS->surface, only throughfall
#        # Use an overflow mechanism, eg. the famous Rutter-Interception Model
#        cmf.RutterInterception(self.c.canopy,self.c.surfacewater,self.c) 
#        # And now the evaporation from the wet canopy (using a classical Penman equation)
#        cmf.CanopyStorageEvaporation(self.c.canopy,self.c.evaporation,self.c)
    
          
#        #######################################################################
#        # snow
#        self.c.add_storage('Snow','S')
#        cmf.Snowfall(self.c.snow,self.c)
#        snowmelt = cmf.SimpleTindexSnowMelt(self.c.snow,self.c.surfacewater,self.c,rate=7.0)

#        #######################################################################
#        # lateral flow connection between soil layer and river
#        for l in self.c.layers:
#            cmf.Darcy(l,self.af.river.Reach,10)#TODO: calc flowwidth between river and cell
##            # Calculate the water content from the suction limit
#            Vret = l.soil.Wetness([-1])[0] * l.get_capacity()
##            # Make the linear storage cnnection with residence time t_ret and the residual volume
#            cmf.LinearStorageConnection(l, self.af.river.Reach, residencetime=25, residual=Vret)
##           
