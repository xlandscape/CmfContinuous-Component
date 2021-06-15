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

    def __init__(self,af=None,name=None,GLAImax=None,GLAImin=None,GLAIharv=None,
                 Dstart=None,Dmin=None,Dmax=None,Dharv=None,
                 cform=None,dform=None,
                 rootinit=None,rootmax=None,
                 heightinit=None,heightmax=None,
                 rpin=None,
                 soil_delta_z=None,soil_zm=None,soil_evap_depth=None,
                 feddes=None,croptype=None,
                 altitude=None,latitude=None,maxcomp=2.,a_f=0.6,wintercrop=False):
        """ 
        af (AgriculturalField): agricultural field object which hods the plant
        name (string):          name o fplant
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
        soil_evap_depth (list): indicates if soil layer contributes to
                                evaporation (1=yes; 0=no)
        feddes (list):          Four water stress parameter in cm water column
        croptype (string):      'annual' or 'perennial'
        altitude (double):      elevation (m)
        latitude (double):      ölatitude in decimal degree
        maxcomp (double):       maximum water uptake compensation factor (-)
        a_f (double):           radiation attenuationfacotr
        wintercrop (string):    'True' or 'False'
        """
        
        #field
        self.af = af
        
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
        self.__soil_evap_depth = soil_evap_depth
        self.__feddes_waterstress = feddes
        self.__maxcomp = maxcomp
        self.__altitude = altitude
        self.__latitude = latitude
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

    def __getPET(self):
        """Returns potential evapotranspiration (mm). """
        value = self.__PET 
        return value
    PET = property(__getPET)    
    

    def __getTact(self):
        """Returns actual transpiration mm). """
        
        value = self.__Tact 
        return value
    Tact = property(__getTact)    
    
    def __getEact(self):
        """Returns actual evaporation (mm)."""
        value = self.__Eact 
        return  value
    Eact = property(__getEact)           

    def __getTpot(self):
        """Returns potential transpiration (mm)."""
        value = self.__Tpot 
        return  value
    Tpot = property(__getTpot)    
    
    
    def __getEpot(self):
        """Returns potential evaporation (mm)."""
        value = self.__Epot 
        return  value
    Epot = property(__getEpot)    

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

    def __getSoilWaterExtraction(self):
        """Returns soil water abstraction (Eact+Tact) per layer (mm)."""
        return  [i for i in self.__soil_waterabstraction]
    SoilWaterExtraction = property(__getSoilWaterExtraction) 
     
    def __getSoilRootWaterUptake(self):
        """Returns root water uptake per layer (mm)."""       
        return  [i for i in self.__actual_wateruptake]
    SoilRootWaterUptake = property(__getSoilRootWaterUptake) 

    def __getSoilEvaporation(self):
        """Returns soi levaporation per layer (mm)."""
        return [i for i in self.__soilevap]
    SoilEvaporation = property(__getSoilEvaporation) 
    
    def __getRootDistribution(self):
        """Returns root distribtuion per layer (-)."""
        return  self.__rootdistribution
    RootDistribution = property(__getRootDistribution) 

    ###########################################################################
    # functions leaf area index

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

    ###########################################################################
    # functions root growth
    
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

    def calc_FeddedWaterstress(self,h_soil,feddes_waterstress): 
        """
        Computes water uptake stress factor alpha (0-1.)
                
        h_soil (list):      soil pressurehead per layer in(cm water column) 
        feddes_waterstress: plant specific parameter for Feddes et al.
        """
        h_plant = feddes_waterstress
        if h_soil<h_plant[0] or h_soil>h_plant[-1]: return 0
        if h_soil>=h_plant[1] and h_soil<=h_plant[2]: return 1
        elif h_soil<h_plant[1]: return (h_soil-h_plant[0])/(h_plant[1]-h_plant[0])
        else: return (h_plant[-1]-h_soil)/(h_plant[-1]-h_plant[-2])
  
    def compensate(self,Sh,Sp,pressurehead,alpha,feddes_opt,maxcomp):
        """
        Calculates compensation factors for each layer in the rootingzone.
        
        Compensation capacity = (Actual uptake-Potential uptake)*maxcom
        s_p (list):             potential water uptake per layer (mm)
        s_h (List):             actual water uptake per layer (mm)
        pressurehead (list):    pressurehead per layer in (cm)
        alpha (list):           water uptake stress factor (0-1) (-) 
        maxcomp (double):       maximum compensation capacity factor (-)
        feddes_opt (double):    plant pressure head until water uptake can 
                                occur without stress in [cm water column].
        """
        #Remaining alpha of the less stress soil layer
        remaining_alpha= [max(1-(m/feddes_opt),0.) for i,m in enumerate(pressurehead)]         
        #Remaining uptake capacity of the soillayer
        remaining_uptake=sum(Sp)-sum(Sh)       
        #Returns list with the compensation values in mm    
        return [min(r/sum(remaining_alpha)*remaining_uptake,maxcomp*Sh[i])for i,r in enumerate(remaining_alpha)]      

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
        
    def calc_wateruptake(self):
        """
        Calculates water uptake.
        """
        if self.__feddes_waterstress:
            # calcuate potential uptake from each layer
            self.__potential_wateruptake = [rootfraction*self.__Tpot for rootfraction in self.__rootdistribution]
            # calcuatle water stres factor transpiration # 
            self.__waterstress_T = [self.calc_FeddedWaterstress(pressure,self.__feddes_waterstress)  for pressure in self.__pressurehead]
           # calcualte actual water uptake            
            self.__actual_wateruptake = [wpot*stress for wpot,stress in zip(self.__potential_wateruptake,self.__waterstress_T)]   
            # calculate water uptake compensation between soil layer TODO: test further
            self.__compensated_uptake = [0 for i in self.__potential_wateruptake]# self.compensate(self.__actual_wateruptake,self.__potential_wateruptake,self.__pressurehead,self.__waterstress_T,self.__feddes_waterstress[2],self.__maxcomp)
            # calculate total water uptake
            self.__actual_wateruptake = [act+com for act,com in zip(self.__actual_wateruptake,self.__compensated_uptake)]
            #calcuate actual transpiration
            self.__Tact = sum(self.__actual_wateruptake)        
        # calcualte evaproation from upper sol layer accordign to evap_depth
        #TODO: evaporation onyl from upper layer ... no need for allocation of E, because cmf does the job ....
        Epot_per_Layer = self.__Epot / len([i for i in self.__waterstress_E if i > 0 ])
        self.__soilevap = [Epot_per_Layer * i for i in self.__waterstress_E]
        # calcualte evaporation
        self.__Eact = sum(self.__soilevap) #TODO: no compensatio for E
        #calcualte total soil water extraction E + T
        if len(self.__actual_wateruptake)<1:
            self.__actual_wateruptake = [0 for i in self.__soil_delta_z]       
        self.__soil_waterabstraction = [(t+e) for t,e in zip(self.__actual_wateruptake,self.__soilevap)]
       
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

    def calc_Ra_from_DOY(self,latitude,DOY):
        lat_radians = math.pi/180*latitude 
        Gsc = 0.082 
        inverse_realtive_distance = 1 + 0.033 * math.cos(2 * math.pi * DOY / 365)
        solar_decimation = 0.409 * math.sin(2 * math.pi / 365 * DOY - 1.39) 
        sunset_hour_angle = math.acos(-1 * math.tan(lat_radians) * math.tan(solar_decimation)) 
        term1 = 24 * 60 / math.pi * Gsc * inverse_realtive_distance
        term2 = sunset_hour_angle * math.sin(lat_radians) * math.sin(solar_decimation)
        term3 = math.cos(lat_radians) * math.cos(solar_decimation) * math.sin(sunset_hour_angle)
        Ra = term1 * (term2 + term3)
        return Ra

    
    def calcETo2(self,DOY,Rs,Tmin,Tmax,Wind,vapourpressure,G,altitude,latitude):
        Tmean=(Tmin+Tmax)/2
        #constants
        AerDyn_Resistance=206
        AeroT_Cff = 900
        rc = 70
        albedo=0.23
        # Vapor pressure deficit [kPa]
        ea_Tmax = 0.6108 * math.exp((17.27 * Tmax) / (Tmax + 237.3))
        ea_Tmin = 0.6108 * math.exp((17.27 * Tmin) / (Tmin + 237.3))
        ea = (ea_Tmax + ea_Tmin) / 2
        edew = vapourpressure
        # Rad term
        Ra=self.calc_Ra_from_DOY(latitude,DOY)
        Rns = (1-albedo) * Rs # 1-albedo (grass=0.23)
        Rso = (0.75 + 2 * altitude * 10**-5) * Ra
        Rs_Rso = min([Rs/Rso,1.0])            
        Rns = 0.77 * Rs # 1-albedo (grass=0.23)
        Rnl = self.calc_Rnl(Tmin, Tmax, Rs_Rso, edew)
        Rn = Rns - Rnl
        Rn_G=Rn-G
        Lambda = 2.501-(0.002361*(Tmean))
        Delta = (4098 * (0.6108 * math.exp(17.27 * Tmean / (Tmean + 237.3)))) / (Tmean + 237.3)**2
        P =  101.3 * ((293 - 0.0065 * altitude) / 293)**5.26  
        ra = AerDyn_Resistance / Wind
        Gamma1=0.0016286*P/Lambda
        Gamma2=Gamma1*(1+rc/ra)
        dl_gm=Delta/(Delta+Gamma2)
        Radterm = dl_gm*Rn_G/Lambda
        gm_dl = Gamma1/(Delta+Gamma2)
        Areoterm = gm_dl*AeroT_Cff / (Tmean+273)*Wind*(ea-edew)
        ET=Radterm+Areoterm
        ET = max(0,ET)
        return ET,Ra,Rn,Rs



    def __call__(self,t,soil,atmosphere):
        """
        Calculates plant growth for timestep t.
        
        t (datetime):       actual time
        soil (class):       object which implements soil interface
        atmosphere (class): object which implements atmosphere itnerface
        """
        # get soil pressruehead for each layer
        pressurehead = soil.PressureHead
        # get evaporation stress factor for each layer
        waterstress_E = soil.Kr
        
        
        
        # get climate variables
        self.__PET = atmosphere.get_Sunshine(t)


#        Rs = atmosphere.get_Rs(t)
#        Tmax = atmosphere.get_tmax(t)
#        Tmin = atmosphere.get_tmin(t)
#
#        Ra = self.calc_Ra_from_DOY(self.__latitude,t.DOY())
#        # calc PET with hargreaves-Samani  
#        self.__PET = 0.0023 * ((Tmax + Tmin)/2. + 17.8) * (Tmax - Tmin)**0.5 * Rs


        #self.__PET /= self.af.catchment.timestep_convert
        # check crop type
        if self.__croptype == "annual":
            # calculate growing during growing period of annual crops
            if self.__das < self.__harvest:
                # update DAS
                # i ncase of hourly steps update DAS at the beginning of the day 
                if self.af.catchment.solver.t.hour==0:
                    self.__das += 1    
                # calculate crop development
                self.calc_development()
                # calcualte plant height
                self.__height = self.calc_height(self.__das,self.__Lini,self.__Ldev,self.__heightmax,self.__heightinit,self.__croptype)
                # calculate potential E and T
                Fsoil = self.calc_Fsoil(self.__LAI,self.__a_f)
                Fcrop = self.calc_Fcrop(self.__GLAI,self.__a_f)
                self.__Epot = self.__PET * Fsoil
                self.__Tpot = self.__PET * Fcrop
                # calculate root growth
                self.calc_rootgrowth()
                # calculate water uptake
                if self.af.plantmodel == "macro":
                    self.__pressurehead = pressurehead
                    self.__waterstress_E = [stress if depth== 1 else 0 for depth,stress in zip(self.__soil_evap_depth,waterstress_E)]
                    self.calc_wateruptake()
            # set all state variables to zero when no plant exists
            else:
                self.__GLAI = 0.
                self.__LAI = 0.
                self.__Tpot = 0
                self.__Epot = 0
                self.__Tact = 0.
                self.__Eact = 0.
                self.__rootdepth = 0.
                self.__height = 0.0
                self.__root_distribution = [0. for i in self.__soil_zm]
                self.__soil_waterabstraction = [0. for i in self.__soil_zm]
                self.__actual_wateruptake = [0. for i in self.__soil_zm]
                self.__soilevap = [0. for i in self.__soil_zm]
       # calculate growing during growing period of annual crops
        else:
                # update DAS
                # i ncase of hourly steps update DAS at the beginning of the day 
                if self.af.catchment.solver.t.hour==0:
                    self.__das += 1
                # calculate crop development
                self.calc_development()
                # calculate potential E and T
                Fsoil = self.calc_Fsoil(self.__LAI,self.__a_f)
                Fcrop = self.calc_Fcrop(self.__GLAI,self.__a_f)
                self.__Epot = self.__PET * Fsoil
                self.__Tpot = self.__PET * Fcrop
                # calculate root growth (the perennial growth path is also used
                # for baresoil conditions which requires no root growth)
                if not (self.__name == "baresoil"): 
                    self.calc_rootgrowth()
                    # calcualte plant height
                    self.__height = self.calc_height(self.__das,self.__Lini,self.__Ldev,self.__heightmax,self.__heightinit,self.__croptype)
                #calcualte water uptake
                if self.af.plantmodel == "macro":
                    self.__pressurehead = pressurehead
                    self.__waterstress_E = [stress if depth==1 else 0 for depth,stress in zip(self.__soil_evap_depth,waterstress_E)]
                    self.calc_wateruptake()    
#        return self.__das,self.__rootdepth,self.__rootdistribution,self.__soil_waterabstraction,self.__LAI,self.__GLAI,self.__Epot,self.__Tpot,self.__Eact,self.__Tact,self.__actual_wateruptake,self.__soilevap















#
#
#
#class AtmosphereSoilInterface(object):
#    def __init__(self):
#        
#        
#        self.soil_zm = [.05,.15,.25,.35,.45,.55,.65,.75,.85,.95]
#        self.soil_delta  = [0.1 for i in self.soil_zm]
#        
#        
#        
#        self.evap_depth = 0.2
#        self.soil_evap_depth = [1 if i <= self.evap_depth else 0 for i in self.soil_zm]
#
#    def get_pressurehead(self):
#        return [200. for i in self.soil_zm]
#    def get_Kr(self):
#        return [1. for i in self.soil_zm]
#    def get_Rs(self,t):
#        return 25
#    def get_tmean(self,t):
#        return 20.
#    def get_tmax(self,t):
#        return 25.
#    def get_tmin(self,t):
#        return 15.


#
#
#    
#
#import matplotlib.pyplot as plt
#from mpl_toolkits.axes_grid1 import make_axes_locatable
#import datetime
## TODO: connect E and T with cmf
#  
## summer cerals
#GLAImax = 4.
#GLAImin = 0.01
#GLAIharv = 2.
#Dstart = 125
#Dmin =  126
#Dmax = 179
#Dharv = 247
#x1 = 2. #cform
#x2 = 0.3 #dform
#croptype = "annual"
#wintercrop=False
#rootinit = 0.01
#rootmax = 0.5
#zeta = 60
#feddes_waterstress = [0.,1.,500.,16000.]
#
### winter cerals params
##GLAImax = 6.
##GLAImin = 1
##GLAIharv = 2.
##Dstart = 268
##Dmin =  84
##Dmax = 174
##Dharv = 238
##x1 = 2. #cform
##x2 = 0.2 #dform
##rootinit = 0.1# 0.2
##rootmax = 1.3 # 1.3
##zeta = 60
##feddes_waterstress = [0.,1.,500.,16000.]
##croptype = "annual"
##wintercrop=True
#
#
#atmsoil = AtmosphereSoilInterface()
##plant = Plant(name="baresoil",GLAImax=GLAImax,GLAImin=GLAImin,GLAIharv=GLAIharv,
##             Dstart=Dstart,Dmin=Dmin,Dmax=Dmax,Dharv=Dharv,
##             cform=x1,dform=x2,
##             rootinit=rootinit,rootmax=rootmax,rpin=zeta,
##             soil_delta_z=atmsoil.soil_delta,soil_zm=atmsoil.soil_zm, soil_evap_depth=atmsoil.soil_evap_depth,
##             feddes_waterstress=feddes_waterstress,croptype=croptype,
##             altitude=0,maxcomp=2.,a_f=0.6,wintercrop=wintercrop)
##
##
#
#plant = Plant(name="baresoil",GLAImax=0.,GLAImin=None,GLAIharv=None,
#                     Dstart=None,Dmin=None,Dmax=None,Dharv=None,
#                     cform=2.,dform=0.2,
#                     rootinit=0,rootmax=0,rpin=None,
#                     soil_delta_z=atmsoil.soil_delta,soil_zm=atmsoil.soil_zm, soil_evap_depth=atmsoil.soil_evap_depth,
#                     feddes_waterstress=None,croptype="perennial",
#                     altitude=0,maxcomp=2.,a_f=0.6,wintercrop=False)
#
#
#
#
#dummy_date = datetime.datetime.now()
#res = [plant(dummy_date,atmsoil,atmsoil) for i in range(1,365)]
#
#

#
#
##
##
##
##
##
#### grass/alfalfa
###GLAImax = 0.
###GLAImin = None
###GLAIharv = None
###Dstart = None
###Dmin =  None
###Dmax = None
###Dharv = None
###x1 = 2.
###x2 = 0.2
###rootinit = 10
###rootmax = 10
###zeta = None
###feddes_waterstress  = [0.,1.,500.,16000.]
###croptype = "perennial"
###wintercrop=False
####soil params
###evap_depth = 0.2
###soil_delta_z =  [.01 for i in range(20)] + [.05 for i in range(16)]
###soil_zm = [0.005, 0.015, 0.025, 0.035, 0.045, 0.055, 0.065, 0.075, 0.085, 0.095, 0.105, 0.115, 0.125, 0.135, 0.145, 0.155, 0.165, 0.175, 0.185, 0.195, 0.225, 0.275, 0.324, 0.375, 0.425, 0.475, 0.525, 0.575, 0.625, 0.675, 0.725, 0.775, 0.825, 0.875, 0.925, 0.975]
###soil_evap_depth = [1 if i <= evap_depth else 0 for i in soil_zm]
###
####some dummy state varaibles
###pressurehead = [1. for i in soil_zm]
###waterstress_E = [1. for i in soil_zm]
###
###
###
##
#
#
#def plot_SoilWaterBalance(fpath=None):
#
#    fig = plt.figure(figsize=(10, 8))
#    #
#    
#    ax = fig.add_subplot(6, 1, 1)
#    ax.plot([i[5] for i in res],label="GLAI",linewidth=1,linestyle="-",markersize=1)
#    ax.plot([i[4] for i in res],label="LAI",linewidth=1,linestyle="-",markersize=1)
#    ax.set_xticklabels([""])
#    ax.set_ylabel("[m2/m2]")
#    ax.set_xlim(0,365)
#    ax.legend(loc=0)
#    ax.grid()
#    
#    ax = fig.add_subplot(6, 1, 2)
#    ax.plot([i[7] for i in res],label="Tpot",linewidth=4,linestyle="-",markersize=1,color="g",alpha=.35)
#    ax.plot([i[6] for i in res],label="Epot",linewidth=4,linestyle="-",markersize=1,color="orange",alpha=.35)
#    ax.plot([i[9] for i in res],label="Tact",linewidth=1,linestyle="-",markersize=1,color="g")
#    ax.plot([i[8] for i in res],label="Eact",linewidth=1,linestyle="-",markersize=1,color="orange")
#    ax.set_xticklabels([""])
#    ax.set_ylabel("[mm]")
#    ax.set_xticklabels([""])
#    ax.legend(loc=0)
#    ax.set_xlim(0,365)
#    ax.grid()
#    
#    ax = fig.add_subplot(6, 1, 3)
#    ax.plot([i[1]*-1 for i in res],label="rooting depth",linewidth=4,linestyle="-",markersize=1,color="g",alpha=.35)
#    ax.set_ylabel("Depth [m]")
#    ax.set_xticklabels([""])
#    ax.legend(loc=0)
#    ax.set_xlim(0,365)
#    ax.grid()
#
#    ax = fig.add_subplot(6, 1, 4)
#    im=ax.imshow(np.transpose([r[2] for r in res]),aspect="auto",cmap=plt.cm.jet,vmin=0,vmax=.1)
#    ax.set_ylabel("Layer")
#    ax.set_xlabel("DAS")
#    divider = make_axes_locatable(ax)
#    cax = divider.append_axes('bottom', size='10%', pad=0.3)
#    cb = fig.colorbar(im,cax=cax, orientation='horizontal')
#    cb.set_label("Rootgrowth [m]")
#    ax.grid()
#    ax.set_xlim(0,365)    
#    
#    ax = fig.add_subplot(6, 1, 5)
#    im=ax.imshow(np.transpose([r[-1] for r in res]),aspect="auto",cmap=plt.cm.gist_heat_r,vmin=0,vmax=10)
#    ax.set_ylabel("Layer")
#    ax.set_xlabel("DAS")
#    divider = make_axes_locatable(ax)
#    cax = divider.append_axes('bottom', size='10%', pad=0.3)
#    cb = fig.colorbar(im,cax=cax, orientation='horizontal')
#    cb.set_label("Evaporation [mm]")
#    ax.grid()
#    ax.set_xlim(0,365)
#
#    ax = fig.add_subplot(6, 1, 6)
#    im=ax.imshow(np.transpose([r[-2] for r in res]),aspect="auto",cmap=plt.cm.gist_heat_r,vmin=0,vmax=10)
#    ax.set_ylabel("Layer")
#    ax.set_xlabel("DAS")
#    divider = make_axes_locatable(ax)
#    cax = divider.append_axes('bottom', size='10%', pad=0.3)
#    cb = fig.colorbar(im,cax=cax, orientation='horizontal')
#    cb.set_label("Transpiration (E+T) [mm]")
#    ax.grid()
#    ax.set_xlim(0,365)  
#    
##    
##    
##    
##    
#    
#    
#    
#    
#    
#    if not fpath == None:
#        plt.tight_layout()
#        fig.savefig(fpath + "PlantGrowth.png",dpi=300)
#    
#
#plot_SoilWaterBalance("")
#
#
#
#
##
#













