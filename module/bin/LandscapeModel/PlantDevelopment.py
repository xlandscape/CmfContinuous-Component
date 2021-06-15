# -*- coding: utf-8 -*-
"""
Created on Thu Sep 28 10:57:00 2017

@author: smh
"""
import math
import numpy as np

class Plant(object):   
    """
    Calculates plant development, leaf area index, evapotranspiration, 
    root distribution and wateruptake from soil according to the waterflow and 
    solute transport model MACRO 5.0 (Larbo and Jarvis,2003)

    Plant developement is calculated based on Julian days. Development is
    divided into a linear and exponential growth phase of the leaf area inde as
    well as a decreasing phase after maturity.
    
    The leaf area index is calculated based on the crop development and fixed 
    shape parameter.
    
    
    Roots are allocated along the entire rootign depth with a
    decreasing exponential function. 

    Potential evapotranspiration is calculated according to Hargreaves-Samani 
    method. Evaporation and transpiration are separated by the leaf area index.
    
    Actual transpiration is calculated based on root water uptake. The latter one
    is calculated related to the root distribution and the soil water content.
    Water stress is calcualted accordign to Feddes (1976). If no sufficient 
    water content is available for water uptake, compensation takes place.

    Actual evaporation is calculated fro mteh potential evaporation rate and
    the water content in the upper soil layer.       
    """

    def __init__(self,name=None,GLAImax=None,GLAImin=None,GLAIharv=None,
                 Dstart=None,Dmin=None,Dmax=None,Dharv=None,
                 cform=None,dform=None,
                 rootinit=None,rootmax=None,
                 heightinit=None,heightmax=None,
                 rpin=None,
                 soil_delta_z=None,soil_zm=None,
                 croptype=None,
                 a_f=0.6,wintercrop=False,
                 nogrowth_LAI=2,
                 nogrowth_rootdepth=.2,
                 nogrowth_height=.2):
        """ 
        name (string):          name of plant
        GLAI (double):          green leaf area index (-)
        GLAImax (double):       max green leaf area index (-)
        GLAImin (double):       min green leaf area index (-)
        GLAIharv (double):      green leaf area index at harvest (-)
        Dstart (double):        day at emergence (days)
        Dmin (double):          day at GLAImin (days)
        Dmax (double):          day at GLAImax (days)
        Dharv (double):         day at harvest (days)
        cform (double):         empirical 'form' exponent development
        dform (double):         empirical 'form' exponent senencence
        rootinit (double):      rootdepth at Dmin (m)
        rootmax (double):       max root depth (m)
        heightinit (double):    height at Dmin (m)
        heightmax (double):     max height (m)
        rpin (double):          emprical root distribution parameter
        soil_delta_z (list):    thickness of each soil layer (m) 
        soil_zm (list):         midpoint of each soil layer (m)

        croptype (string):      'annual' or 'perennial'
        a_f (double):           radiation attenuationfacotr
        wintercrop (string):    'True' or 'False'
        """
        
        self.__nogrowth_LAI         = nogrowth_LAI
        self.__nogrowth_rootdepth   = nogrowth_rootdepth
        self.__nogrowth_height      = nogrowth_height

        # input variables
        self.__name  = name
        self.__GLAImax = GLAImax
        self.__GLAImin = GLAImin
        self.__GLAIharv = GLAIharv
        self.__Dmax = Dmax
        self.__Dmin = Dmin
        self.__Dstart = Dstart
        self.__Dharv = Dharv        
        self.__cform = cform
        self.__dform = dform
        self.__GLAI = 0.0
        self.__LAI = 0.0
        self.__croptype = croptype
        self.__a_f = a_f
        self.__rootinit = rootinit
        self.__rootmax = rootmax
        self.__rpin = rpin
        self.__soil_delta_z = soil_delta_z
        self.__soil_zm = soil_zm
        self.__heightmax=heightmax
        self.__heightinit=heightinit
        
        # calculated during initialisation
        self.__harvest = None # day of harvest in days after soiwng (DAS)
        self.__Lini = None # lenght of initial growth period in DAS
        self.__Ldev = None # length of development period in DAS
        self.__Lend = None # length of end perdio in DAS
        
        

        
        #  calcualte lenght of gorwing period and harvest day in days after sowing
        if self.__croptype == "annual":
            
            if  wintercrop:

                self.__Lini = (365-self.__Dstart) + self.__Dmin
                self.__Ldev = self.__Dmax -self.__Dmin
                self.__Lend = self.__Dharv - self.__Dmax
                self.__harvest = self.__Lini + self.__Ldev + self.__Lend                
            else:
                self.__Lini = self.__Dmin - self.__Dstart
                self.__Ldev = self.__Dmax -self.__Dmin
                self.__Lend = self.__Dharv - self.__Dmax
                self.__harvest = self.__Lini + self.__Ldev + self.__Lend   


        # state variables
        self.__das = 0 # days after sowing (days)
        self.__Epot = 0. # potential evaporation (mm)
        self.__Tpot = 0. # potential transpiration (mm)
        self.__Tact = 0.0 # actual transpiration (mm)
        self.__Eact = 0.0 # actual evaporation (mm)
        self.__PET = 0.0 # potential evapotranspiration (mm)
        self.__waterstress_E = [] # list with evaporation stress factor  per layer (-)
        self.__waterstress_T = [] # list with transpiration stress factor  per layer (-)
        self.__soil_waterabstraction = [] # plant water uptake + evaporation per layer (mm)
        self.__soilevap = [] # evaporation per layer (mm)
        self.__rootdepth = 0 # rooting depth (cm)
        self.__rootdistribution = [0. for i in self.__soil_zm] #rootfraction in eac hsoil layer (-)
        self.__potential_wateruptake = [0. for i in self.__soil_zm] # wateruptake from each soil layer (mm)
        self.__actual_wateruptake = [0. for i in self.__soil_zm] # wateruptake from each soil layer (mm)
        self.__compensated_uptake =[0. for i in self.__soil_zm]  # compensated root water uptake
        self.__pressurehead = [] # pressurehead per layer (cm water column)
        self.__height = 0.0 # plant height (m)
        
    ###########################################################################
    # properties


    def __getName(self):
        """Returns plant name."""
        return self.__name
    Name = property(__getName)    
    
    def __getCropType(self):
        """Returns plant name."""
        return self.__croptype
    CropType = property(__getCropType) 

    def __getGLAI(self):
        """Returns green leaf area index (-)."""
        return  self.__GLAI
    GLAI = property(__getGLAI)  

    def __getLAI(self):
        """Returns leaf area index (-)."""
        return  self.__LAI
    LAI = property(__getLAI)
    
    def __getDAS(self):
        """Returns days after sowing (days)."""
        return  self.__das
    DAS = property(__getDAS)  
    
    def __getHarvest(self):
        """Returns harvest day (days after sowing)."""
        return  self.__harvest
    Harvest = property(__getHarvest) 

    def __getHeight(self):
        """Returns plant height (cm)."""
        return  self.__height
    Height = property(__getHeight) 

    def __getRootingDepth(self):
        """Returns rooting depth (cm)."""
        return  self.__rootdepth
    RootingDepth = property(__getRootingDepth)  
    
    def __getRootDistribution(self):
        """Returns root distribtuion per layer (-)."""
        return  self.__rootdistribution
    RootDistribution = property(__getRootDistribution) 

    def calc_Fsoil(self,LAI,a_f):
        """
        Calculates evaporation factor 'Fsoil' (-)
        
        LAI (double):      leaf area index (-)
        a_f (double):      radiation attenuationfacotr (-)
        """
        return np.exp(-a_f * LAI)
    
    def calc_Fcrop(self,GLAI,a_f):
        """
        Calculates transpiration factor 'Fcrop' (-)
        
        GLAI (double):      grenn leaf area index (-)
        a_f (double):      radiation attenuationfacotr (MACRO = ATTEN)
        """
        return  1. - (np.exp(-a_f * GLAI))

    def calc_development_linear(self,D,GLAImin,Dmin):
        """
        Calculates green leaf area index 'GLAI' during linear 
        growh period.
        
        GLAI (double):      green leaf area index (-)
        GLAImin (double):   min green leaf area index (-)
        D (double):         actual day (days)
        Dmin (double):      day at GLAImin (days)
        """
        return GLAImin * (D / Dmin)
    
    def calc_development_exponential(self,D,GLAImin,GLAImax,Dmin,Dmax,cform):
        """
        Calculates green leaf area index 'GLAI' during exponential 
        growh period.
        
        GLAI (double):      green leaf area index (-)
        GLAImax (double):   max green leaf area index (-)
        GLAImin (double):   min green leaf area index (-)
        D (double):         actual day (days)
        Dmax (double):      day at GLAImax (days)
        Dmin (double):      day at GLAImin (days)
        cform (double):     empirical 'form' exponent
    
        """
        return GLAImin + (GLAImax - GLAImin) * ((D-Dmin) / (Dmax - Dmin))**cform
    
    def calc_senencence(self,D,GLAIharv,GLAImax,Dharv,Dmax,dform):
        """
        Calculates senencence green leaf area index 'GLAI' afterg exponential 
        growh period.
        
        GLAI (double):      green leaf area index (-)
        GLAImax (double):   max green leaf area index (-)
        GLAIharv (double):  green leaf area index at harvest (-)
        D (double):         actual day (days)
        Dmax (double):      day at GLAImax (days)
        Dharv (double):     day at harvest (days)
        dform (double):        empirical 'form' exponent
        """
        return  GLAIharv + (GLAImax - GLAIharv) * ((Dharv-D) / (Dharv - Dmax))**dform
    
    def calc_rootDistribution(self,delta_z,zm,zr,rpin):
       """
       Calculates 'root distribution' in depth zm (-).
       
       delta_z (double):    thickness of layer i
       zm (double):         mid-point of layer i
       zr (double):         rootdepth
       rpin (double):       emprical root distribution parameter
       """
       zeta = 4*np.log(1/(1-rpin/100.))
       r = zeta * (delta_z/zr) * np.exp(-zeta * (zm / zr))   
       return r

    def calc_rootdepth(self,D,Lini,Ldev,rootmax,rootinit,croptype):   
        """
        Calculates 'rootingdepth' in (m).
        
        D (double):         days after sowing
        Lini (double):      lenght of initial period
        Ldev (double):      lenght of development period
        rootmax (double):   maximum rooting depth (m)
        rootinit (double):  initial rootign depth (m)
        croptype (double):  'annual' or 'perennial'
        
        """
        rootdepth =  0
        if croptype == "annual":
            das_Dmin = Lini
            das_Dmax = Lini + Ldev
            
            if D <= das_Dmin:
                rootdepth = rootinit *  (D / das_Dmin)
            elif (D > das_Dmin) and (D <= das_Dmax):
                rootdepth =  rootinit + (rootmax-rootinit) * ((D-das_Dmin) / (das_Dmax - das_Dmin)) 
            elif D > das_Dmax:
                rootdepth = rootmax
        else:
            rootdepth = rootmax
        return rootdepth

    def calc_height(self,D,Lini,Ldev,heightmax,heightinit,croptype):   
        """
        Calculates 'height' in (m).
        
        D (double):         days after sowing
        Lini (double):      lenght of initial period
        Ldev (double):      lenght of development period
        heightmax (double):   maximum rooting depth (m)
        heightinit (double):  initial rootign depth (m)
        croptype (double):  'annual' or 'perennial'
        
        """
        height =  0
        if croptype == "annual":
            das_Dmin = Lini
            das_Dmax = Lini + Ldev
            
            if D <= das_Dmin:
                height = heightinit *  (D / das_Dmin)
            elif (D > das_Dmin) and (D <= das_Dmax):
                height =  heightinit + (heightmax-heightinit) * ((D-das_Dmin) / (das_Dmax - das_Dmin)) 
            elif D > das_Dmax:
                height = heightmax
        else:
            height = heightmax
        return height

    def calc_rootgrowth(self):
        """
        Calculates rootign depth and distribution.
        """
        # calcualte rooting depth
        self.__rootdepth = self.calc_rootdepth(self.__das,self.__Lini,self.__Ldev,self.__rootmax,self.__rootinit,self.__croptype)
        # calculate root distribution
        self.__rootdistribution = []        
        for zm,delta_z in zip(self.__soil_zm,self.__soil_delta_z):
            self.__rootdistribution.append(self.calc_rootDistribution(delta_z,zm,self.__rootdepth,self.__rpin))
        #MACRO approach leads to a small residual which is allocated to teh upper layer according to N.Jarvis
        self.__rootdistribution[0] += (1 - sum(self.__rootdistribution))
       
    def calc_development(self):
        """
        Calcualtes plant development.
        """
        if self.__croptype == "annual":
            
            # linear development period
            if (self.__das <= self.__Lini):
                self.__GLAI = self.calc_development_linear(self.__das,self.__GLAImin,self.__Lini)
                self.__LAI = self.__GLAI
            # exponential development period
            elif (self.__das > self.__Lini) and (self.__das <= (self.__Lini+self.__Ldev)):
                self.__GLAI = self.calc_development_exponential(self.__das,self.__GLAImin,self.__GLAImax,self.__Lini,(self.__Lini+self.__Ldev),self.__cform)
                self.__LAI = self.__GLAI
            # senencence
            elif (self.__das > (self.__Lini+self.__Ldev)) and (self.__das <= (self.__Lini+self.__Ldev+self.__Lend)):
                self.__GLAI = self.calc_senencence(self.__das,self.__GLAIharv,self.__GLAImax,(self.__Lini+self.__Ldev+self.__Lend),(self.__Lini+self.__Ldev),self.__dform)  
        else:
            self.__GLAI = self.__GLAImax
            self.__LAI = self.__GLAI

    def __call__(self,t):
        """
        Calculates plant growth for timestep t.
        
        t (datetime):       actual time
        soil (class):       object which implements soil interface
        atmosphere (class): object which implements atmosphere itnerface
        """
 
        doy = t.DOY()
        
        
 



        # check crop type
        if self.__croptype == "annual":
            
            
            if doy >= self.__Dstart and doy <= self.__Dharv:

                # calculate growing during growing period of annual crops
                if self.__das <= self.__harvest:
        
                    self.__das += 1    
                    # calculate crop development
                    self.calc_development()
                    # calcualte plant height
                    self.__height = self.calc_height(self.__das,self.__Lini,self.__Ldev,self.__heightmax,self.__heightinit,self.__croptype)
                    # calculate potential E and T
                    Fsoil = self.calc_Fsoil(self.__LAI,self.__a_f)
                    Fcrop = self.calc_Fcrop(self.__GLAI,self.__a_f)
                    # calculate root growth
                    self.calc_rootgrowth()

            else:
                self.__GLAI = self.__nogrowth_LAI
                self.__LAI = self.__nogrowth_LAI
                self.__rootdepth = self.__nogrowth_rootdepth
                self.__height = self.__nogrowth_height
                
            if self.__das > self.__harvest:
                self.__das = 0
                    
       # calculate growing during growing period of annual crops
        else:
                self.__das += 1
                # calculate crop development
                self.calc_development()
                # calculate potential E and T
                Fsoil = self.calc_Fsoil(self.__LAI,self.__a_f)
                Fcrop = self.calc_Fcrop(self.__GLAI,self.__a_f)
                if not (self.__name == "baresoil"): 
                    self.calc_rootgrowth()
                    # calcualte plant height
                    self.__height = self.calc_height(self.__das,self.__Lini,self.__Ldev,self.__heightmax,self.__heightinit,self.__croptype)

def getcropbyname(name):
    cropcoefficients = np.genfromtxt("CropCoefficientlist.csv",names=True,delimiter=",",dtype=[('name', '<U100'), 
                       ('GLAImin', '<f8'), ('GLAImax', '<f8'), ('GLAIharv', '<f8'), 
                       ('rootinit', '<f8'), ('rootmax', '<f8'), 
                       ('heightinit', '<f8'), ('heightmax', '<f8'),
                       ('rpin', '<f8'), 
                       ('Dmin', '<f8'), ('Dstart', '<f8'), ('Dmax', '<f8'), 
                       ('Dharv', '<f8'), ('cform', '<f8'), ('dform', '<f8'), 
                       ('feddes1', '<f8'), ('feddes2', '<f8'), ('feddes3', '<f8'), 
                       ('feddes4', '<f8'), ('croptype', '<U100'), ('wintercrop', '<U100')])
    
    cc = cropcoefficients[cropcoefficients["name"]==name]
    return Plant(name=cc["name"],GLAImax=cc["GLAImax"],GLAImin=cc["GLAImin"],GLAIharv=cc["GLAIharv"],
                     Dstart=cc["Dstart"],Dmin=cc["Dmin"],Dmax=cc["Dmax"],Dharv=cc["Dharv"],
                     cform=cc["cform"],dform=cc["dform"],
                     rootinit=cc["rootinit"],rootmax=cc["rootmax"],
                     heightinit=cc["heightinit"],heightmax=cc["heightmax"],
                     rpin=cc["rpin"],
                     soil_delta_z=[1,1],soil_zm=[0.5,1.5],
                     croptype=cc["croptype"],
                     a_f=0.6,wintercrop=eval(cc["wintercrop"][0]))


def test():
  
    import cmf
    from datetime import datetime
    import pandas as pd
    #set crop
    grass = getcropbyname("D4_Maize")
#    grass = getcropbyname("D4_Grass/alfalfa")
#    grass = getcropbyname("D4_Pome/stone fruit")
    
    
    begin =datetime(2007,1,1)
    end = datetime(2008,12,31)
    p=cmf.project()
    p.NewCell(1,1,1, 100 ,with_surfacewater=True)
    solver = cmf.CVodeIntegrator(p, 1e-9)
    DAS = cmf.timeseries(begin, cmf.day)
    LAI = cmf.timeseries(begin, cmf.day)
    GLAI = cmf.timeseries(begin, cmf.day)
    RDEPTH = cmf.timeseries(begin, cmf.day)
    HEIGHT = cmf.timeseries(begin, cmf.day)
    
    # Start solver and calculate in daily steps
    for t in solver.run(begin, end, cmf.day):
        grass(t)
        DAS.add(grass.DAS)
        LAI.add(grass.LAI)
        GLAI.add(grass.GLAI)
        RDEPTH.add(grass.RootingDepth)
        HEIGHT.add(grass.Height)
    #    print(t,grass.DAS)
    
    
    res = pd.DataFrame([(t,das,lai,glai,rdepth,height) for t,das,lai,glai,rdepth,height in zip(pd.date_range(begin,end),DAS,LAI,GLAI,RDEPTH,HEIGHT)],columns=["date","das","lai","glai","rdepth","height"])
    res.set_index("date",inplace=True)
    
    ax=res[["lai","glai"]].plot()
    ax.set_ylim(0,8)






