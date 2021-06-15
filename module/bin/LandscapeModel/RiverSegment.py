# -*- coding: utf-8 -*-
"""
Created on Tue Sep 12 14:00:04 2017

@author: smh
"""
import cmf

class RiverSegment(object):
    """
    Represents  a segment of a river. The geometry is  represented by a 
    different shapes, eg. triangular, rectangular and SWAT-type reach. The 
    class  manages data transfer and the initialisation of cmf.reach with input
    data.
    """

    __slots__ = ["__catchment", "__name","__x","__y","__z","__downstream", 
                "__initial_depth","__manning_n","__bankslope","__flowwidth",
                "__bottomwidth","__floodplainslope", "__reach_shape","__reach","__nbc",
                "__efate","__drift","__water_temperature","downstream_storage"]
    
    def __init__(self,catchment,name,x,y,z,downstream,initial_depth,manning_n,
                 flowwidth,reach_shape,bankslope,bottomwidth,floodplainslope):
        """
        Creates a river segment which holds a cmf.reach.
        
        name (string):              name
        x (double):                 x coordinate 
        y (double):                 y coordinate 
        z (double):                 altitude 
        downstream (string):        downstream river segment
        initial depth (double):     initial water depth (m)
        manning_n (double):         Mannings' n
        bankslope (double):         Bankslope
        flowwidth (double):         distance to next reach our outlet
        downstream_riversegment (RiverSegement): downstream riversegment
        """
        
        #reach location and info
        self.__catchment = catchment
        self.__name = name
        self.__x = x
        self.__y = y
        self.__z = z
        self.__downstream = downstream
        self.__initial_depth = initial_depth
        self.__manning_n = manning_n
        self.__bankslope = bankslope
        self.__flowwidth = flowwidth
        self.__bottomwidth  = bottomwidth
        self.__reach_shape = None
        self.__floodplainslope = floodplainslope
        
        # create reach shape
        if reach_shape =="TriangularReach":
            self.__reach_shape = cmf.TriangularReach(self.__flowwidth,self.__bankslope)
        elif reach_shape =="RectangularReach":
            self.__reach_shape =  cmf.RectangularReach(self.__flowwidth, self.__bottomwidth )
        elif reach_shape =="SWATReachType":
            self.__reach_shape = cmf.SWATReachType(self.__flowwidth)
            
            self.__reach_shape.BottomWidth = self.__bottomwidth
            self.__reach_shape.ChannelDepth = self.__initial_depth
            self.__reach_shape.BankSlope = self.__bankslope
            self.__reach_shape.FloodPlainSlope = self.__floodplainslope
            
        self.__reach_shape.set_nManning(self.__manning_n)
         #create reach
        self.__reach =  self.__catchment.p.NewReach(x=self.__x,y=self.__y,z=self.__z,shape=self.__reach_shape,diffusive=False)
        
        # set initial condiditions
        self.__reach.depth = self.__initial_depth

        # create Neumann Boundary
        nbc=cmf.NeumannBoundary.create(self.__reach)
        nbc.Name="Boundary condition " + self.__name
        if len(self.__catchment.p.solutes)>0:
            nbc.connections[0].set_tracer_filter(self.__catchment.p.solutes[0],1)
        self.__nbc = nbc
        
    	# efate module
        self.__efate =    None#Steps_EFATE(DEGHL_SW_0=None,DEGHL_SED_0=None,KOC=None,Temp0=None,Q10=None)

        #drift module
        self.__drift =    None
        
        # connection ot downstream storage
        self.downstream_storage = None

    def set_downstreamStorage(self,downstreamStorage):
        self.downstream_storage=downstreamStorage
        

    ###########################################################################
    # properties
    
    def __getdrift(self):
        """Get drift"""
        return  self.__drift
    
    def __setdrift(self,value):
        """Set drift"""
        self.__drift = value
    Drift = property(__getdrift,__setdrift)    

    def __getefate(self):
        """Get efate"""
        return  self.__efate
    
    def __setefate(self,value):
        """Set efate"""
        self.__efate = value
    Efate = property(__getefate,__setefate)
    
    def __get_length(self):
        """ Return Length"""
        return self.__flowwidth
    Length = property(__get_length)        

    def __get_width(self):
        """ Return Lenght"""
        return self.__bottomwidth
    Width = property(__get_width)           
    
    def __getMASS_SW(self):
        """MASS_SW"""
        if self.__efate != None:
            return self.__efate.efate2cmf_MASS_SW()
        else:
            return 0
    MASS_SW = property(__getMASS_SW)

    def __getMASS_SED(self):
        """MASS_SED"""
        if self.__efate != None:
            return self.__efate.efate2cmf_MASS_SED()
        else:
            return 0
    MASS_SED = property(__getMASS_SED)

    def __getMASS_SED_DEEP(self):
        """MASS_SED_DEEP"""
        if self.__efate != None:
            return self.__efate.efate2cmf_MASS_SED_DEEP()
        else:
            return 0
    MASS_SED_DEEP = property(__getMASS_SED_DEEP)

    def __getPEC_SW(self):
        """PEC_SW"""
        if self.__efate != None:
            return self.__efate.efate2cmf_PEC_SW()
        else:
            return 0
    PEC_SW = property(__getPEC_SW)

    def __getPEC_SED(self):
        """PEC_SED"""
        if self.__efate != None:
            return self.__efate.efate2cmf_PEC_SED()
        else:
            return 0
    PEC_SED = property(__getPEC_SED)
    
    def __getflux(self):
        """Get flux"""
        return  self.__nbc.flux 
    
    def __setflux(self,value):
        """Set flux"""
        self.__nbc.flux = value
    Flux = property(__getflux,__setflux)      


    def __getNBC(self):
        """Get flux"""
        return  self.__nbc 
    def __setNBC(self,value):
        """Set NBC"""
        self.__nbc = value
    NBC = property(__getNBC,__setNBC) 

       
    def __getwater_temperature(self):
        """Get drift"""
        return  12
    def __setwater_temperature(self,value):
        """Set drift"""
        pass
    WaterTemperature = property(__getwater_temperature,__setwater_temperature)       
    

    
    def __getName(self):
        """Name"""
        return self.__name
    Name = property(__getName)
    
    def __getX(self):
        """x coord"""
        return self.__x
    x = property(__getX)

    def __getY(self):
        """y coord"""
        return self.__y
    y = property(__getY)

    def __getZ(self):
        """z coord"""
        return self.__z
    z = property(__getZ)

    def __getDownstream(self):
        """Downstream river segment"""
        return  self.__downstream
    Downstream = property(__getDownstream)
    
    def __getReach(self):
        """Downstream river segment"""
        return  self.__reach
    Reach = property(__getReach)
    
    def __getdepth(self):
        """Water depth in (m)"""
        return  self.__reach.depth
    def __setdepth(self,value):
        """Water depth in (m)"""
        self.__reach.depth = value
    Depth = property(__getdepth,__setdepth)

    def __getVolume(self):
        """Solute concentration"""
        return  self.__reach.volume
    Volume = property(__getVolume) 
      
    def __getArea(self):
        """Returns the area of the surface for a given volume. """
        return  self.__reach.wet_area()
    Area = property(__getArea) 

    def __getFlow(self):
        """Flow"""
        t = self.__catchment.solver.t
        return self.__reach.flux_to(self.downstream_storage,t)
    Flow = property(__getFlow) 
        
    def __getconc(self):
        """Solute concentration"""
        t=self.__catchment.solver.t
        if len(self.__catchment.p.solutes)>0:
            return  self.__reach.conc(t,self.__catchment.p.solutes[0])
        else:
            return 0
    Conc = property(__getconc)       

    def __getload(self):
        """Solute load"""
#        t = self.__catchment.solver.t
        if len(self.__catchment.p.solutes)>0:
            return self.__reach.Solute(self.__catchment.p.solutes[0]).state# self.__reach.conc(t,self.__catchment.p.solutes[0]) * self.__reach.volume
        else:
            return 0
    Load = property(__getload)       

    def __getArtificialFlux(self):
        """Solute load"""
        t = self.__catchment.solver.t
        return  self.__nbc.flux_to(self.__reach,t)
    ArtificialFlux = property(__getArtificialFlux)      