 # -*- coding: utf-8 -*-
"""
Created on Wed Dec  5 16:36:06 2018

@author: smh
"""

import cmf
from datetime import datetime

###############################################################################
# STRUCT

class DriftRate():
    """
    STRUCT for the definition of a substance application.
    """    
    def __init__(self,Substance,Reach,Time,DriftRate):
        self.Substance = Substance
        self.Reach = Reach
        self.Time = Time
        self.DriftRate = DriftRate

###############################################################################
# MODELS

class Reach(object):
    """
    Creates a reach object at the given location and shape. After setup of
    reach object connect the reach to downstream water body. Optionally, a
    timeseries can be used as input for inflow and concentration.
    
    Example
    -------
        #create reach with triangular shape
        shape = cmf.TriangularReach(100,0.2) # flowdith=100m; bankslope=0.2
        r1 = Reach("r1",x=100,y=0,z=1,p=p,shape=shape) 
        #connect reaches with each other and outlet
        r1.set_downstream(outlet,"outlet")
        # or
        r2.set_downstream(r1)
        #set inflow and conc for each reach
        r2.set_inflow(start,timestep,inflow,conc)

    Attributes:
    -----------
        name (str): Name of reach.
        x (float): x-coordinate [m].
        y (float): y-coordiante [m].
        z (float): Altitute [m].
        p (cmf.cmf_core.project): Project of CMF.
        shape (cmf.IChannel): Geometry of reach 
                              (reactangular,triangular,trapezoid).
        downstream (cmf.Reach): Downstream reach.
        efate (Efate): Aquatic efate interface.
        drift (drift): Drift interface.
    Todo:
    -----
        * check all shapes
        * check with TOXSWA
    """   
    
    def __init__(self,name,x,y,z,p,shape):
        """ Create reach object.
        
        Args:
        -----
        name (str): Name of reach.
        x (float): x-coordinate.
        y (float): y-coordiante.
        z (float): Altitute.
        p (cmf.cmf_core.project): Project of CMF.
        shape (cmf.IChannel): Geometry of reach 
                              (reactangular,triangular,trapezoid).
        """
        self.name = name
        self.p = p
        self.cmf__reach = self.p.NewReach(x=x,y=y,z=z,shape=shape,diffusive=False)
        self.nbc = cmf.NeumannBoundary.create(self.cmf__reach)
        self.nbc.connections[0].set_tracer_filter(self.p.solutes[0],1) 
        self.downstream = None
        self.efate = None
        self.drift = None
    def __call__(self,t):
        # get solute load from efate module at the end of timestep
        self.cmf__reach.Solute(self.p.solutes[0]).state = self.efate.efate2cmf_load()   

    def set_drift(self,drift):
        """ Connects reach with drift"""
        self.drift = drift
    def set_efate(self,efate):
        """ Connects reach with efate"""
        self.efate = efate
    def set_downstream(self,downstream,downstream_type=""):
        if downstream_type!="outlet":
            self.cmf__reach.set_downstream(downstream.cmf__reach)
            self.downstream = downstream.cmf__reach
        else:
            self.cmf__reach.set_outlet(downstream)
            self.downstream = downstream
    def set_inflow(self,start,timestep,inflow=None,conc=None):
        """ Set inflow (m3/day) and conc (mg/m3)"""
        if inflow != None:
            self.nbc.flux =  cmf.timeseries.from_sequence(start , timestep,inflow) 
        if conc != None:
            self.nbc.concentration[self.p.solutes[0]] = cmf.timeseries.from_sequence(start , timestep,conc)
    def get_lenght(self):
        return 100 # fixed lenght of 100m
    def get_load(self,t):
        """ Returns solute load in mg"""
        return  self.cmf__reach.Solute(self.p.solutes[0]).state
    def get_conc(self,t):
        """ Returns solute concentration in mg/m3"""
        return self.cmf__reach.conc(t,self.solute) 
    def get_vol(self,t):
        """ Returns volume m3"""
        return self.cmf__reach.volume
    def get_flow(self,t):
        """ Returns outflow in m3/day"""
        return self.cmf__reach.flux_to(self.downstream,t)
    def get_wetarea(self):
        """ Returns wet area in m2"""
        return self.cmf__reach.wet_area()

class Toxswa:
    """ toxswa model"""
    def __init__(self):
        self.reach = None
        self.drift = None
        self.__load = 0.
    def set_reach(self,reach):
        self.reach = reach
    def set_drift(self,drift):
        self.drift = drift
    def __call__(self,t):
        """ Run model for one time step."""
        #get drift input
        load_drift = self.drift.drift2efate_drift()
        # get load from cmf-reach
        load_reach = self.reach.cmf2efate_load(t)
        self.__load = load_drift+load_reach
        # do some degradation
        self.__load *= 1.0
        return True
    def get_load(self):
        return self.__load

class Drift():
    """
    Collection of drift events. Events are define for a specific timestep and 
    river segment.
    """
    i=0
    def __init__(self,DriftRates):
        self.__DriftRates = DriftRates
        self.reach = None
        self.__rate = 0
        self.__total = 0
    def __gettotal(self):
        """get drift (mg)"""
        return self.__total
    Total = property(__gettotal)
    def __getrate(self):
        """get driftrate (mg/m2)"""
        return self.__rate
    Rate = property(__getrate)
    def __iter__(self):
        return self
    def __getitem__(self,val):
        return self.__DriftRates[val]
    def __next__(self):
        if self.i < len(self.__DriftRates):
            self.i += 1
            return self.__DriftRates[self.i-1]
        else:
            raise StopIteration()          
    def __call__(self,t):
        # get current drift rate
        if self.__DriftRates != None:
            events = [i for i in self.__DriftRates if (i.Time==t)]
            if len(events)>0:
                self.__rate = sum([e.DriftRate for e in events]) # events[0].AppRate  # 
            else:
                self.__rate = 0
        self.__total = self.__rate * self.reach.cmf2drift_wetarea()
    def set_reach(self,reach):
        self.reach = reach

###############################################################################
# INTERFACES

class CMF_EFATE:
    """
    Interface between one reach and one toxswa.
    
    There is a two-way data transfer between Toxswa and cmf.
    """
    def __init__(self,reach,efate):
        self.reach = reach
        self.efate = efate 
        self.connect_models()
    def connect_models(self):
        self.reach.set_efate(self)
        self.efate.set_reach(self)
    def cmf2efate_ReachLenght(self):
        """ Length of reach (m) L	constant"""
        return self.reach.get_lenght()
    def cmf2efate_load(self,t):
        """ Returns solute load in mg"""
        return self.reach.get_load(t)
    def cmf2efate_conc(self,t):
        """ Returns solute concentration in mg/m3"""
        return self.reach.get_conc(t)
    def cmf2efate_vol(self,t):
        """ Returns volume m3"""
        return self.reach.get_vol(t)
    def cmf2efate_flow(self,t):
        """ Returns outflow in m3/day"""
        return self.reach.get_flow(t)
    def efate2cmf_load(self):
        """ Returns load from efate"""
        return self.efate.get_load()
    def efate_run(self,t):
        """ Ru nefate"""
        return self.efate(t)
    
class CMF_DRIFT():
    """ 
    Interface between one reach and Xdrift.
    
    Data transfer is one-way from CMF to drift.
    """
    def __init__(self,reach,drift):
        """
        For testing xdrift is just a list of drift events.
        
        Args:
            reach (CMF.Reach): Reach of CMF.
            xdrift (List): List of SubstanceApplication
        """
        self.reach = reach
        self.drift = drift 
        # connect models
        self.connect_models()
    def connect_models(self):
        self.reach.set_drift(self)
        self.drift.set_reach(self)     
    def cmf2drift_wetarea(self):
        return self.reach.get_wetarea()
    
class EFATE_DRIFT():
    """ 
    Interface between efate and Xdrift.
    
    Data transfer is one-way from Drift to efate.
    """
    def __init__(self,efate,drift):
        """
        Args:
            reach (CMF.Reach): Reach of CMF.
            xdrift (List): List of SubstanceApplication
        """
        self.efate = efate
        self.drift = drift 
        # connect models
        self.connect_models()
    def connect_models(self):
        self.efate.set_drift(self)
    def drift2efate_drift(self):
        """ Return drift into water body (mg)"""
        return self.drift.Total
    
if __name__ == "__main__":
    
    ###########################################################################
    # set start, end and timestep of simulation
    start = datetime(2010,1,1,8)
    end = datetime(2010,1,1,18)
    timestep=cmf.min

    ###########################################################################
    # create some inflow and conc data for the time period
    inflow = [1 for i in  range(int((end-start).total_seconds()/3600))]
#    conc = [0 for i in  range(int((end-start).total_seconds()/3600))]
#    conc[2]=10
    conc=None
    
    ###########################################################################
    #create cmf project with a solute, one outlet and three reaches
    p = cmf.project("CMP_A")
    #get solute
    solute, = p.solutes
    # create and outlet
    outlet = p.NewStorage("outlet",0,0,0)   
    #create reaches with the same shape
    shape = cmf.TriangularReach(100,0.2) # flowdith=100m; bankslope=0.2
    r1 = Reach("r1",x=100,y=0,z=1,p=p,shape=shape) 
    r2 = Reach("r2",x=200,y=0,z=2,p=p,shape=shape)
    r3 = Reach("r3",x=100,y=100,z=2,p=p,shape=shape)
    
    ###########################################################################
    # add one more reach 'r4':
    r4 = Reach("r4",x=100,y=200,z=3,p=p,shape=shape)
    ###########################################################################
    
    #connect reaches with each other and outlet
    r1.set_downstream(outlet,"outlet")
    r2.set_downstream(r1)
    r3.set_downstream(r1)
    
    ###########################################################################
    # connect r4 with r3:
    r4.set_downstream(r3)
    ###########################################################################

    #set inflow and conc for each reach
    r2.set_inflow(start,timestep,inflow,conc)
    r3.set_inflow(start,timestep,inflow,conc)
    
    ###########################################################################
    # add some artificial inflow
    r4.set_inflow(start,timestep,inflow,conc)
    ###########################################################################

    
    
    

    ###########################################################################
    # create toxswa objects 
    txw1 = Toxswa() 
    txw2 = Toxswa() 
    txw3 = Toxswa() 
    
    ###########################################################################
    # create interfaces amd connect models
    cmftox1 = CMF_EFATE(r1,txw1)
    cmftox2 = CMF_EFATE(r2,txw2)
    cmftox3 = CMF_EFATE(r3,txw3)

    ###########################################################################
    # create drift models
    d1 = Drift(DriftRates = [])
    d2 = Drift(DriftRates = [DriftRate("CMP_A","r2",datetime(2010,1,1,10),1000.0)])
    d3 = Drift(DriftRates = [DriftRate("CMP_A","r2",datetime(2010,1,1,10),1000.0)]) 
    
    # connect drift with cmf
    cmfdrift1 = CMF_DRIFT(r1,d1)
    cmfdrift2 = CMF_DRIFT(r2,d2)
    cmfdrift3 = CMF_DRIFT(r3,d3)

    # connect drift with efate
    efatedrift1 = EFATE_DRIFT(txw1,d1)
    efatedrift2 = EFATE_DRIFT(txw2,d2)
    efatedrift3 = EFATE_DRIFT(txw3,d3)    
    
    ###########################################################################
    # make simulations
    d_models = [d1,d2,d3]
    txw_models = [txw1,txw2,txw3]
    reach_models = [r1,r2,r3]
    solver = cmf.CVodeIntegrator(p,1e-9)
    for t in solver.run(start, end, timestep):

        for model in d_models:  # run drift
            model(t)
        
        for model in txw_models: # run efate
            model(t)
            
        for model in reach_models: # run reaches
            model(t)
        
        
        solver.reset()
        # note: the whole system is solved each loop
        # print some state variables
        print(t,"r1: %.3fm3/day r1: %.2fmg"%
              (r1.get_flow(t),r3.get_load(t)))
    

    





        