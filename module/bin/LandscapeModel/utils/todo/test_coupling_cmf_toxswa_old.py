# -*- coding: utf-8 -*-
"""
Created on Fri Nov 23 10:23:12 2018

@author: smh
"""


#class Model1_catchment:
#    """ A model which calculates stateA."""
#    def __init__(self):
#        self.interface_efate = None
#        self.stateA = 0.
#    def get_stateA(self):
#        return self.stateA
#    def calculate_stateA(self):
#        """ Calculate stateA variable."""
#        self.stateA = 42
#    def connect(self,interface):
#        self.interface_efate = interface
#    def __call__(self):
#        """ Run model for one time step."""
#        self.calculate_stateA()




import cmf
import datetime

class Catchment():
    
    def __init__(self,start,end,timestep,solute="CMP_A"):
        #create cmf project 
        self.p=         cmf.project(solute)
        self.solute, =  self.p.solutes
        #create outlet
        self.outlet =   None    
        self.reaches = None
        
        self.start = start
        self.end = end
        self.timestep=timestep
        
        # create catchment
        self.__create_model()

        # create solver
        self.solver = cmf.CVodeIntegrator(self.p,1e-9)
        
        self.efate = None

    def connect(self,efate):
        self.efate=efate
        
    def run(self,printOut=True):
        """  """
        # create solver
        for t in self.solver.run(self.start, self.end, self.timestep):
            r1 = self.get_flow(t,"r1") / 86400
            r2 = self.get_flow(t,"r2") / 86400
            r3 = self.get_flow(t,"r3") / 86400
            vol = self.outlet.volume
            print(t,"r1 %.3fm3/s r2 %.2f m3/s r3 %.2f m3/s outlet: %.2fm3"%(r1,r2,r3,vol),self.reach1.conc(t,self.solute))


    def __create_model(self):
        """ create hydrological objects """        
        # create outlet
        self.outlet = self.p.NewStorage("outlet",0,0,0)   
        
        # create reaches
        shape = cmf.TriangularReach(100,0.2) # flowdith=100m; bankslope=0.2
        self.reach1 = self.p.NewReach(x=100,y=0,z=1,shape=shape,diffusive=False)
        self.reach2 = self.p.NewReach(x=200,y=0,z=2,shape=shape,diffusive=False)
        self.reach3 = self.p.NewReach(x=100,y=100,z=2,shape=shape,diffusive=False)
        
        # connect reaches and outlet
        self.reach1.set_outlet(self.outlet)
        self.reach2.set_downstream(self.reach1)
        self.reach3.set_downstream(self.reach1)

        # create a Neumann boundary for each reach
        self.reach1_nbc = cmf.NeumannBoundary.create(self.reach1)
        self.reach1_nbc.connections[0].set_tracer_filter(self.p.solutes[0],1) # allow solute transport
        self.reach2_nbc = cmf.NeumannBoundary.create(self.reach2)
        self.reach2_nbc.connections[0].set_tracer_filter(self.p.solutes[0],1) # allow solute transport
        self.reach3_nbc = cmf.NeumannBoundary.create(self.reach3)
        self.reach3_nbc.connections[0].set_tracer_filter(self.p.solutes[0],1) # allow solute transport

        # just a list with the reach name, cmf-object and next reach
        self.reaches = [("r1",self.reach1,self.outlet,self.reach1_nbc),("r2",self.reach2,self.reach1,self.reach2_nbc),("r3",self.reach3,self.reach1,self.reach3_nbc)]

    def set_inflow(self,reachname,inflow,conc):
        """ Set inflow (m3/day) and conc (mg/m3)"""
        reach = self.__get_reach_byName(reachname)
        reach[3].flux =  cmf.timeseries.from_sequence(self.start , self.timestep,inflow) 
        reach[3].concentration[self.solute] = cmf.timeseries.from_sequence(self.start , self.timestep,conc)

    def __get_reach_byName(self,reachname):
         """ Get rach by name """
         return [r for r in self.reaches if r[0]==reachname][0]

    def get_lenght(self,reachname):
        return 100 # fixed lenght of 100m

    def get_load(self,t,reachname):
        """ Returns solute load in mg"""
        reach = self.__get_reach_byName(reachname)
        return reach.conc(t,self.solute) *reach.volume

    def get_conc(self,t,reachname):
        """ Returns solute concentration in mg/m3"""
        reach = self.__get_reach_byName(reachname)
        return reach.conc(t,self.solute) 
    
    def get_vol(self,t,reachname):
        """ Returns volume m3"""
        reach = self.__get_reach_byName(reachname)
        return reach.volume

    def get_flow(self,t,reachname):
        """ Returns outflow in m3/day"""
        reach = self.__get_reach_byName(reachname)
        return reach[1].flux_to(reach[2],t)


class Model2_toxswa:
    """ A model which requires stateA to calculate stateB"""
    def __init__(self):
        self.catchment = None
        self.__load = 0.
    def connect(self,catchment):
        self.catchment = catchment
    def __call__(self,t):
        """ Run model for one time step."""
        # get load at beginnign of timestep
        load = self.cmf2tox_load(self,t)
        # do some calculations
        # load = self.calc(t)
        #set new load of toxswa
        self.__load = load
    def get_load(self):
        return self.__load

class Interface_catchment_toxswa:
    """ Interface between Model1 and Model2"""
    def __init__(self,catchment,toxswa):
        self.catchment = catchment
        self.toxswa = toxswa 
    def connect_models(self):
        self.catchment.connect(self)
        self.toxswa.connect(self)
    def cmf2tox_ReachLenght(self,reachname):
        """ Length of reach (m) L	constant"""
        return self.catchment.get_lenght(reachname)
    def cmf2tox_load(self,t,reachname):
        """ Returns solute load in mg"""
        return self.catchment.get_load(t,reachname)
    def cmf2tox_conc(self,t,reachname):
        """ Returns solute concentration in mg/m3"""
        return self.catchment.get_conc(t,reachname)
    def cmf2tox_vol(self,t,reachname):
        """ Returns volume m3"""
        return self.catchment.get_vol(t,reachname)
    def cmf2tox_flow(self,t,reachname):
        """ Returns outflow in m3/day"""
        return self.catchment.get_flow(t,reachname)
    def tox2cmf_load(self,t):
        """ Returns load from toxswa"""
        return self.toxswa.get_load(t)
    
    
#    def get_ReachWidth(self):
#        """ Width of the bottom of water system (m)	constant """
#        reach = self.Model1_catchment.reach
#        return reach.width
#    def get_ReachSlope(self):
#        """ Width of the bottom of water system (m)	constant """
#        reach = self.Model1_catchment.reach
#        return reach.slope
#    def get_ReachPerimeterWaterSediment(self):
#        """ Water depth defining perimeter for exchange between water layer and sediment (m)	h1	constant """
#        reach = self.Model1_catchment.reach
#        return reach.depth #TODO: correct?
#    def get_ReachOM(self):
#        """ Mass ratio of organic matter in suspended solids (g.g-1)	mom,ss	constant """
#        reach = self.Model1_catchment.reach
#        return reach.OC * 1 #TODO: add conversion
#    def get_ReachDryMassMacrophytes(self):
#        """ Dry mass of macrophyte biomass per m2 bottom (g.m-2)	Xmp	constant """
#        reach = self.Model1_catchment.reach
#        return 0 #TODO: not calcualted by CMF
#    def get_ReachSuspendedSolids(self):
#        """ Concentration of suspended solids (g.m-3)	Xss	constant """
#        reach = self.Model1_catchment.reach
#        return 0 #TODO: could be done by CMF by adding an addtional solute; discuss with PK
#    def get_NumberOfSegemnts(self):
#        """ Number of segments in reach		constant """
#        reach = self.Model1_catchment.reach
#        return 0 #TODO: To be clarified
#    def get_ReachTemperature(self,t):
#        """ Temperature of water (°C)		Variable, time series t=time """
#        return reach.Temperature(t) # not calculated by CMF.


###################################################################
## setup models and conduct model runs for a certain time period
## create models
#model1_catchment = Model1_catchment()
#model2_toxswa = Model2_toxswa()
## create interface
#interface = Interface_catchment_toxswa(model1_catchment,model2_toxswa,unit_conversion_stateA=100)
## connect models
#interface.connect_models()
#timesteps = range(1,11)
#for timestep in timesteps:
#    model1_catchment() 
#    model2_toxswa()
#    print(timestep,model1_catchment.get_stateA(),model2_toxswa.get_stateB())
#	
#    
    
# set start, end and timestep of simulation
start =datetime.datetime(2010,1,1,0)
end = datetime.datetime(2010,1,2,0)
timestep=cmf.h

# create simple catchment
catchment = Catchment(start,end,timestep,solute="CMP_A")
# create inflow (1000m3)
inflow = [1000 for i in  range(int((end-start).total_seconds()/3600))]
# set solute input
conc = [0 for i in  range(int((end-start).total_seconds()/3600))]
conc[2]=10
# set inflow and concentration
catchment.set_inflow("r2",inflow,conc)
catchment.set_inflow("r3",inflow,conc)

#create efate
toxswa = Model2_toxswa()
# create interface
interface = Interface_catchment_toxswa(catchment,toxswa)
interface.connect_models()

# run model
#catchment.run()




















