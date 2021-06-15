# -*- coding: utf-8 -*-
"""
Created on Wed May 30 10:12:48 2018

@author: smh
"""
import numpy as np

class Steps1234():
    
    def __init__(self,DEGHL_SW_0=10,DEGHL_SED_0=10,KOC=1,Temp0=21.,Q10=2.2,
                 DENS=0.8,POROSITY=0.6,OC=0.05,DEPTH_SED=0.05, DEPTH_SED_DEEP=0.45,
                 DIFF_L_SED=0.005,DIFF_L=0.005,DIFF_W=4.3*(10**-5),T=1):
        
        
        self.reach = None
        
        # cosntant values sediment
        self.DENS =          DENS # DENS:  sediment dry bulk density (kg/L = t/m3)
        self.POROSITY =      POROSITY # POROSITY:porosity of sediment, i.e. pore volume / total volume (-)
        self.OC =            OC # OC: organic carbon content (fraction) 
        self.DEPTH_SED =     DEPTH_SED#0.005 # DEPTH_SED:         depth of the upper sediment layer (m)
        self.DEPTH_SED_DEEP =DEPTH_SED_DEEP#0.45 # DEPTH_SED_DEEP:	depth of the deeper sediment layer (m)
        self.DIFF_L_SED =    DIFF_L_SED # DIFF_L_SED:		diffusion path length in sediment (set to 0.005 m)         
        


       
        ###############################################################################
        # constant values water body
        self.DIFF_L =        DIFF_L # diffusion path length (set to 0.005 m)
        self.DIFF_W =        DIFF_W  #	diffusion coefficient in water (set to 4.3 10-5 m²/d)
    
        ###############################################################################
        # constant values simulation
        self.T =             T  #Time step (1 hour)

        ###############################################################################
        # constant values substance
        self.DEGHL_SW_0 =    DEGHL_SW_0 # Degradation half-life in surface water at temperature Temp0 [°C]
        self.DEGHL_SED_0 =   DEGHL_SED_0 # degradation half-life in sediment at temperature Temp0 [°C]
        self.Temp0 =         Temp0 # [°C]
        self.Q10 =           Q10 # Q10-factor, set to 2.2
        self.KOC =           KOC # #KOC:               sorption constant related to organic carbon (L/kg)

        ###############################################################################
        # state variables
        self.MASS_SW =       0 # mg/m2 or mg
        self.MASS_SED =      0 # mg/m2 or mg
        self.MASS_SED_DEEP = 0 # mg/m2 or mg
        self.PEC_SED       = 0 #mg/m3
        self.PEC_SW       = 0 #mg/m3
        
        self.__DEGHL_SW = 0.
        self.__DEGHL_SED = 0.
        self.__MASS_SW_INT1 = 0.
        self.__MASS_SED_INT1 = 0.
        self.__MASS_SW_INT2 = 0.
        self.__C_SW_INT = 0.
        self.__C_SED_TOT_INT1 = 0.
        self.__DISTRIB_SW_SED = 0.
        self.__MASS_SED_INT2 = 0.
        self.__C_SED_TOT_INT2 = 0.
        self.__C_SED_DEEP_TOT = 0.
        self.__DISTRIB_SED = 0.
        self.__MASS_SW_t0 = 0.
        self.__DEGR_SW = 0.
        self.__DEGR_SED = 0.


    def set_reach(self,reach):
        self.reach= reach
    
    def adjust_degradation(self,Temp,DEGHL_SW_0,DEGHL_SED_0,Q10,Temp0):
        # adjust degradation half-life acoording to actual temperature
        
        #DEGHL_SW:			degradation half-life in surface water (d)
        #DEGHL_SW_0:		degradation half-life in surface water at temperature Temp0 [°C]
        #DEGHL_SW:			degradation half-life in sediment (d)
        #DEGHL_SW_0:		degradation half-life in sediment at temperature Temp0 [°C]
        #Q10:				Q10-factor, set to 2.2
        #Temp				actual temperature of water column and sediment
        #Temp0:			reference temperature during the degradation study

        DEGHL_SW =      DEGHL_SW_0 / Q10**((Temp-Temp0) / 10)						  
        DEGHL_SED =     DEGHL_SED_0 / Q10**((Temp-Temp0) / 10) 
        
        return DEGHL_SW,DEGHL_SED

    def calc_initial_MASS(self,MASS_SW,MASS_SED,DEGHL_SW,DEGHL_SED,INPUT_SW,INPUT_SED):
        # calculate inital substance mass in SW and SED  (for parent compounds only)
        
        #MASS_SW_INT1(t):	temporary compound mass in the water layer at time t (mg/m²)
        #MASS_SW (t-1):		final compound mass in the water layer at time t-1 (mg/m²)
        #DEGHL_SW:			Degradation half-life in surface water (d)
        #INPUT_SW(t)			input into the water layer at time t (mg/m²)
        #MASS_SED_INT1(t):	temporary compound mass in the sediment at time t (mg/m²)
        #MASS_SED (t-1) 	final compound mass in the sediment at time t-1 (mg/m²)
        #DEGHL_SED			Degradation half-life in sediment (d)
        #INPUT_SED(t):		Input into sediment at time t (mg/m²)

        MASS_SW_INT1	=	MASS_SW * np.exp(-np.log(2)/DEGHL_SW) + INPUT_SW
        MASS_SED_INT1	=	MASS_SED * np.exp(-np.log(2)/DEGHL_SED) + INPUT_SED
        
        return MASS_SW_INT1,MASS_SED_INT1

    def calc_masstranfer_WATER_SED(self,MASS_SED_INT1,MASS_SW_INT2,
                                   DEPTH_SW,DEPTH_SED,DENS,
                                   DIFF_W,DIFF_L,
                                   POROSITY,OC,KOC):
        # MASS TRANSFER BETWEEN WATER AND SEDIMENT

        #DISTRIB_SW_SED:    	mass transfer between water and sediment (mg m-² h-1); 
                                #the term C_SED_TOT_INT1 / (POROSITY/DENS +  KOC * OC) 
                                # denotes the pesticide concentration in the pore water of the sediment layer
        #C_SW_INT:          temporary compound concentration in the water layer (mg/m³)
        #C_SED_TOT_INT1:    temporary gravimetric total compound concentration in the upper sediment (mg/t = µg kg-1)

        C_SW_INT		=	MASS_SW_INT2 / DEPTH_SW
        C_SED_TOT_INT1	=	MASS_SED_INT1 / (DEPTH_SED * DENS)
        DISTRIB_SW_SED = -(DIFF_W/24/DIFF_L)*(C_SED_TOT_INT1/(POROSITY/DENS+KOC*OC)-C_SW_INT)

        return DISTRIB_SW_SED,C_SW_INT,C_SED_TOT_INT1

    def calc_final_mass_water(self,MASS_SW_INT2,DISTRIB_SW_SED,T):
        # calculate final compound mass water
        
        ##MASS_SW_INT2(t):	temporary compound mass in the water layer at time t (mg/m²)
        ##MASS_SW(t):		final compound mass in the water layer at time t (mg/m²)
 
        MASS_SW	=		MASS_SW_INT2 - DISTRIB_SW_SED * T

        return MASS_SW

    def calc_masstransfer_upper_lower_SED(self,MASS_SED_DEEP,MASS_SED_INT1,DISTRIB_SW_SED,
                                          DEPTH_SED,DEPTH_SED_DEEP,
                                          DENS,DIFF_L_SED,DIFF_W,
                                          POROSITY,OC,KOC,
                                          T):
        # Distribution between sediment layer

        ##DISTRIB_SW_SED:	mass transfer between water and sediment (mg m-² h-1)
        ##MASS_SED_INT1(t):	temporary compound mass in the sediment at time t (mg/m²)
        ##MASS_SED_INT2(t):	temporary compound mass in the sediment at time t (mg/m²)
        
        ##DISTRIB_SED:	mass transfer between upper and deeper sediment 
        ##(mg m-² h-1)
        ##C_SED_TOT_INT2:	temporary gravimetric total compound concentration in the upper sediment (µg/kg)
        ##C_SED_DEEP_TOT:	gravimetric total compound concentration in the deeper sediment (µg/kg)


        MASS_SED_INT2	=		MASS_SED_INT1 + DISTRIB_SW_SED *  T
        
        
        C_SED_TOT_INT2	=	MASS_SED_INT2 / (DEPTH_SED * DENS)
        
        C_SED_DEEP_TOT	=	MASS_SED_DEEP / (DEPTH_SED_DEEP * DENS)
        
        DISTRIB_SED	=  -(DIFF_W/24 / DIFF_L_SED ) * (C_SED_DEEP_TOT - C_SED_TOT_INT2)/ (POROSITY/DENS + KOC*OC)

        return DISTRIB_SED,MASS_SED_INT2 ,C_SED_TOT_INT2,C_SED_DEEP_TOT

    def calc_final_mass_SED(self,MASS_SED_DEEP,MASS_SED_INT2,DISTRIB_SED,T):
        # final compound mass in sediment mass in upper and lower sediment layer

        #DISTRIB_SED:	mass transfer between upper and deeper sediment (mg m-² h-1)
        #MASS_SED(t):		final compound mass in the upper sediment at time t (mg/m²)
        #MASS_SED_INT2(t):	temporary compound mass in the upper sediment at time t (mg/m²)
        #MASS_SED_DEEP(t):	final compound mass in the deeper sediment at time t (mg/m²)

        MASS_SED			=	MASS_SED_INT2 - DISTRIB_SED *  T
        MASS_SED_DEEP	=	MASS_SED_DEEP + DISTRIB_SED *  T
        
        return MASS_SED,MASS_SED_DEEP

    def calc_PEC(self,MASS_SW_INT2,MASS_SED_INT1,DEPTH_SW,DEPTH_SED,DENS):
        #PEC_SW(t):			surface water concentration at time i (µg/L = mg/m3)
        #PEC_SED(t):			sediment concentration  at time i (µg/kg = mg/t)
        #MASS_SW_INT2(t):		temporary compound mass in the surface water  at time i (mg/m²)
        #MASS_SED_INT1(t):		temporary compound mass in the sediment  at time i (mg/m²)
        #DEPTH_SW:			depth of the water layer (m)
        #DEPTH_SED:			depth of the sediment layer (m)
        #DENS 				sediment bulk density (kg/L)
        PEC_SW	=	 MASS_SW_INT2  /  DEPTH_SW
        PEC_SED	=	 MASS_SED_INT1 /  ( DEPTH_SED * DENS)
        
        return  PEC_SW,PEC_SED


    def runmodel(self,INPUT_SW,INPUT_SED,Temp,VOL_SW,INFLOW,DEPTH_SW):
        # assessment for one time step
        
        # INPUT_SW (mg/m²)
        # INPUT_SED  (mg/m²)
        # Temp (°) The actual temperature in the water body is approximated 
                   # by monthly mean air temperatures.
        #VOL_SW:			regular volume of the water layer (m³);
        #				default values: ditch: 30 m3, stream: 30 m3, pond: 900 m3

#        # calculate baseflow into the water body (L h-1)
#        BASEFLOW = self.calc_BASEFLOW()
#        
#        # calculate inflow into the water body at time at time t (m³)
#        INFLOW = self.calc_INFLOW(BASEFLOW) #

        # DEPTH_SW =      0.3 ##DEPTH_SW:          depth of the water layer (m)
        
        
        
        MASS_SW_t0 = None
        
        # adjust degradation to actual temperature
        DEGHL_SW,DEGHL_SED = self.adjust_degradation(Temp,self.DEGHL_SW_0,self.DEGHL_SED_0,self.Q10,self.Temp0)

        # degrade compound mass in the water layer and sediment at time t (mg/m²)
        MASS_SW_INT1,MASS_SED_INT1 = self.calc_initial_MASS(self.MASS_SW,self.MASS_SED,DEGHL_SW,DEGHL_SED,INPUT_SW,INPUT_SED)

        #calcuate degradation rate
        DEGR_SW = self.MASS_SW	- MASS_SW_INT1
        DEGR_SED = self.MASS_SED - MASS_SED_INT1

        # calculate temporary compound mass 2 in the water layer at time t (mg/m²)
        MASS_SW_INT2 = MASS_SW_INT1 * VOL_SW / (VOL_SW + INFLOW)

        # calculate mass transfer between water and sediment
        DISTRIB_SW_SED,C_SW_INT,C_SED_TOT_INT1 = self.calc_masstranfer_WATER_SED(MASS_SED_INT1,MASS_SW_INT2,
                                   DEPTH_SW,self.DEPTH_SED,self.DENS,
                                   self.DIFF_W,self.DIFF_L,
                                   self.POROSITY,self.OC,self.KOC)

        # calculate final compound mass water
        self.MASS_SW	= self.calc_final_mass_water(MASS_SW_INT2,DISTRIB_SW_SED,self.T)

        # calculate distribution between sediment layer
        DISTRIB_SED,MASS_SED_INT2 ,C_SED_TOT_INT2,C_SED_DEEP_TOT = self.calc_masstransfer_upper_lower_SED(self.MASS_SED_DEEP,MASS_SED_INT1,DISTRIB_SW_SED,
                                                  self.DEPTH_SED,self.DEPTH_SED_DEEP,
                                                  self.DENS,self.DIFF_L_SED,self.DIFF_W,
                                                  self.POROSITY,self.OC,self.KOC,
                                                  self.T)




        # calculate final compound mass in sediment mass in upper and lower sediment layer
        self.MASS_SED,self.MASS_SED_DEEP = self.calc_final_mass_SED(self.MASS_SED_DEEP,
                                                            MASS_SED_INT2,
                                                            DISTRIB_SED,
                                                            self.T)
              
        # calculate PEC
        self.PEC_SW,self.PEC_SED = self.calc_PEC(MASS_SW_INT2,MASS_SED_INT1,DEPTH_SW,self.DEPTH_SED,self.DENS)
        
 

       
#        print("MASS_SW_INT1 %.2f MASS_SW_INT2 %.2f MASS_SW %.2f "%(MASS_SW_INT1,MASS_SW_INT2,self.MASS_SW))
#        print("MASS_SW %.2f MASS_SED PEC %.2f MASS_SED_DEEP %.2f "%(MASS_SW,MASS_SED,MASS_SED_DEEP))
#        print("PEC_SW %.2f PEC_SED PEC %.2f"%( self.PEC_SW,self.PEC_SED))        
#        return self.MASS_SW,self.MASS_SED,self.MASS_SED_DEEP,self.PEC_SW,self.PEC_SED,DISTRIB_SW_SED,DISTRIB_SED,DEGR_SW,DEGR_SED





    
        return self.MASS_SW,self.MASS_SED,self.MASS_SED_DEEP,self.PEC_SW,self.PEC_SED,DEGHL_SW,DEGHL_SED,MASS_SW_INT1,MASS_SED_INT1,MASS_SW_INT2,C_SW_INT,C_SED_TOT_INT1,DISTRIB_SW_SED,MASS_SED_INT2,C_SED_TOT_INT2,C_SED_DEEP_TOT,DISTRIB_SED,MASS_SW_t0,DEGR_SW,DEGR_SED

#    def runmodel_CMF(self,INPUT_SW,MASS_SW,Temp,VOL_SW,lenght):
    def __call__(self,INPUT_SW):
        # assessment for one time step
        
        # INPUT_SW (mg)
        # INPUT_SED  (mg)
        # Temp (°) The actual temperature in the water body is approximated 
                   # by monthly mean air temperatures.
        #VOL_SW:			regular volume of the water layer (m³);
        #				default values: ditch: 30 m3, stream: 30 m3, pond: 900 m3
        width = 0.3


    
        MASS_SW = self.reach.cmf2efate_load()
        Temp = self.reach.cmf2efate_watertemperature()
        VOL_SW = self.reach.cmf2efate_volume()
        lenght = self.reach.cmf2efate_lenght()



        VOL_SED =  (self.DEPTH_SED * lenght * width)
        VOL_SED_DEEP =  (self.DEPTH_SED * lenght * width)


        # set the current mass in the surface water body according to CMF calculation
        self.MASS_SW = MASS_SW

#        MASS_SW_t0 = MASS_SW

        # 1. Adjust degradation to actual temperature (d)
        DEGHL_SW,DEGHL_SED = self.adjust_degradation(Temp,self.DEGHL_SW_0,self.DEGHL_SED_0,self.Q10,self.Temp0)
        
        
        DEGHL_SW =      self.DEGHL_SW_0 / self.Q10**((Temp-self.Temp0) / 10)						  
        DEGHL_SED =     self.DEGHL_SED_0 / self.Q10**((Temp-self.Temp0) / 10) 
        

        # 2. degrade compound mass in the water layer and sediment at time t (mg)
        MASS_SW_INT1	= self.MASS_SW * np.exp(-np.log(2)/DEGHL_SW)  + INPUT_SW
        MASS_SED_INT1  = self.MASS_SED * np.exp(-np.log(2)/DEGHL_SED)
        MASS_SW_INT2 = MASS_SW_INT1 # needed to be in line with standard STEPS1234 approach
        

        MASS_SW_INT2 = MASS_SW_INT1 # needed to be in line with standard STEPS1234 approach
        
        

#        #calcuate degradation rate
#        DEGR_SW = self.MASS_SW	- MASS_SW_INT1
#        DEGR_SED = self.MASS_SED - MASS_SED_INT1
                
        # 3. calculate mass transfer between water and sediment
        C_SW_INT = MASS_SW_INT2 / VOL_SW  # mg/m³
        C_SED_TOT_INT1 = MASS_SED_INT1  /  (VOL_SED*self.DENS)  #  (mg/t = µg kg-1)
        DISTRIB_SW_SED = -(self.DIFF_W/24/self.DIFF_L)* (C_SED_TOT_INT1/(self.POROSITY/self.DENS+self.KOC*self.OC)-C_SW_INT) # (mg m-2 h-1); 
        DISTRIB_SW_SED *= (width * lenght) #DISTRIB_SW_SED (mg m-² h-1) * area = DISTRIB_SW_SED  (mg/h)




        # 4. calculate final compound mass water for the timesetp (mg)
        self.MASS_SW	= MASS_SW_INT2 - DISTRIB_SW_SED
    
        # 5. calculate distribution between sediment layer
        MASS_SED_INT2 =  MASS_SED_INT1 + DISTRIB_SW_SED
        C_SED_TOT_INT2 = MASS_SED_INT2   /  (VOL_SED_DEEP*self.DENS)  #  (mg/t = µg kg-1)
        C_SED_DEEP_TOT = self.MASS_SED_DEEP  /   (VOL_SED*self.DENS)  #  (mg/t = µg kg-1)
        DISTRIB_SED	=  -(self.DIFF_W/24 / self.DIFF_L_SED ) * (C_SED_DEEP_TOT - C_SED_TOT_INT2)/ (self.POROSITY/self.DENS + self.KOC*self.OC)
        DISTRIB_SED	*= (width * lenght) #DISTRIB_SED (mg m-² h-1) * area = DISTRIB_SED  (mg/h)
        
        # 6. Calculate final compound mass in sediment 
        self.MASS_SED =	MASS_SED_INT2 - DISTRIB_SED 
        self.MASS_SED_DEEP	= self.MASS_SED_DEEP + DISTRIB_SED
 
      
        # 7. calculate PEC
        self.PEC_SW = MASS_SW_INT2 / VOL_SW if not np.isnan(MASS_SW_INT2 / VOL_SW) else 0
        self.PEC_SED = MASS_SED_INT1 /  (VOL_SED*self.DENS)
                
        
#        print("MASS_SW_INT1 %.2f MASS_SW_INT2 %.2f MASS_SW %.2f DISTRIB_SW_SED %.2f"%(MASS_SW_INT1,MASS_SW_INT2,self.MASS_SW,DISTRIB_SW_SED))

#        return self.MASS_SW,self.MASS_SED,self.MASS_SED_DEEP,self.PEC_SW,self.PEC_SED,DEGHL_SW,DEGHL_SED,MASS_SW_INT1,MASS_SED_INT1,MASS_SW_INT2,C_SW_INT,C_SED_TOT_INT1,DISTRIB_SW_SED,MASS_SED_INT2,C_SED_TOT_INT2,C_SED_DEEP_TOT,DISTRIB_SED,MASS_SW_t0,DEGR_SW,DEGR_SED
