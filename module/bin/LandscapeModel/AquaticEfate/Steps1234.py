# -*- coding: utf-8 -*-
"""
Created on Wed May 30 10:12:48 2018

@author: smh
"""
import numpy as np

class Steps1234():
    
    def __init__(self,length:np.float32,
                 width:np.float32,
                 DEGHL_SW_0:np.float32=10,
                 DEGHL_SED_0:np.float32=10,
                 KOC:np.float32=1,
                 Temp0:np.float32=21.,
                 Q10:np.float32=2.2,
                 DENS:np.float32=0.8,
                 POROSITY:np.float32=0.6,
                 OC:np.float32=0.05,
                 DEPTH_SED:np.float32=0.05,
                 DEPTH_SED_DEEP:np.float32=0.45,
                 DIFF_L_SED:np.float32=0.005,
                 DIFF_L:np.float32=0.005,
                 DIFF_W:np.float32=4.3*(10**-5),
                 convertDeltaT:np.float32=24.):
        """
        Calculates aquatic efate for a water and several sediment layer.
        
        :param length: Length of waterbody (m)
        :type length: float
        :param width: width of water body (m)
        :type width: float
        :param DEGHL_SW_0: Degradation half-life in surface water at temperature Temp0 [°C]
        :type DEGHL_SW_0: float
        :param DEGHL_SED_0: Degradation half-life in sediment at temperature Temp0 [°C]
        :type DEGHL_SED_0: float
        :param KOC: Sorption constant related to organic carbon (L/kg)
        :type KOC: float
        :param Temp0: Input [mg]
        :type Temp0: float
        :param Q10: Q10-factor.
        :type Q10: float
        :param DENS: Sediment dry bulk density (kg/L = t/m3)
        :type DENS: float
        :param POROSITY: Porosity of sediment, i.e. pore volume / total volume (-)
        :type POROSITY: float
        :param OC:  Organic carbon content (fraction) 
        :type OC: float
        :param DEPTH_SED: Depth of the upper sediment layer (m)
        :type DEPTH_SED: float
        :param DEPTH_SED_DEEP: Depth of the deeper sediment layer (m)
        :type DEPTH_SED_DEEP: float
        :param DIFF_L_SED: Diffusion path length in sediment (set to 0.005 m)         
        :type DIFF_L_SED: float
        :param DIFF_L: Diffusion path length (set to 0.005 m)
        :type DIFF_L: float
        :param DIFF_W: Diffusion coefficient in water (set to 4.3 10-5 m²/d)
        :type DIFF_W: float
        :param convertDeltaT: Time conversion factor related to days, 
                                e.g. 24 in case of hourly time step
        :type convertDeltaT: float
        :returns: -
        :rtype: -
        """ 
        
        self.convertDeltaT = convertDeltaT
        
        ###############################################################################
        # constant values substance
        self.DEGHL_SW_0 =    DEGHL_SW_0 * self.convertDeltaT
        self.DEGHL_SED_0 =   DEGHL_SED_0 * self.convertDeltaT 
        self.Temp0 =         Temp0 # [°C]
        self.Q10 =           Q10 # 
        self.KOC =           KOC # #KOC:               

        ###############################################################################
        # constant values water body
        self.DIFF_L =        DIFF_L #
        self.DIFF_W =        DIFF_W  #	

        #######################################################################
        # sediment properties
        self.DENS =          DENS
        self.POROSITY =      POROSITY 
        self.OC =            OC
        self.DEPTH_SED =     DEPTH_SED    
        self.DEPTH_SED_DEEP =DEPTH_SED_DEEP
        self.DIFF_L_SED =    DIFF_L_SED 
        
        self.diff_SED = -1 * (self.DIFF_W/self.convertDeltaT/ self.DIFF_L_SED )
        self.diff_SW = -1 * (self.DIFF_W/self.convertDeltaT/self.DIFF_L)
        self.log2 = -np.log(2)
        
        #######################################################################
        # geometries
        self.length = length
        self.width = width
        self.VOL_SED =  (self.DEPTH_SED * self.length * self.width)
        self.VOL_SED_DEEP =  (self.DEPTH_SED * self.length * self.width)
        self.GRAV_SED     = (self.VOL_SED*self.DENS)    
        self.GRAV_SED_DEEP     = (self.VOL_SED_DEEP*self.DENS) 
        self.area =  width * length
        self.SED_solid = (self.POROSITY/self.DENS+self.KOC*self.OC)
        
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


    def __call__(self,INPUT_SW:np.float32,MASS_SW:np.float32,TEMP,VOL:np.float32):
        """
        Calculates efate fro water and sediment.
        
        :param INPUT_SW: Input [mg]
        :type INPUT_SW: float
        :param MASS_SW: Actual mass SW [mg]
        :type MASS_SW: float
        :param TEMP: Temperature (Celcius)
        :type TEMP: float
        :param VOL: Water volume [m3]
        :type VOL:   float
            
        :returns: -
        :rtype: -
        """       
        # set the current mass in the surface water body according to CMF calculation
        self.MASS_SW = MASS_SW

        # 1. Adjust degradation to actual temperature (d)    
        temp_corr = self.Q10**((TEMP-self.Temp0) / 10)
        DEGHL_SW =      self.DEGHL_SW_0 / temp_corr						  
        DEGHL_SED =     self.DEGHL_SED_0 / temp_corr		

        # 2. degrade compound mass in the water layer and sediment at time t (mg)
        MASS_SW_INT1	= self.MASS_SW * np.exp(self.log2/DEGHL_SW)  + INPUT_SW
        MASS_SED_INT1  = self.MASS_SED * np.exp(self.log2/DEGHL_SED)
        MASS_SW_INT2 = MASS_SW_INT1 # needed to be in line with standard STEPS1234 approach
        self.__DEGR_SW = self.MASS_SW	- MASS_SW_INT1
        self.__DEGR_SED= self.MASS_SED - MASS_SED_INT1
                        
        # 3. calculate mass transfer between water and sediment
        C_SW_INT = MASS_SW_INT2 / VOL  # mg/m³
        C_SED_TOT_INT1 = MASS_SED_INT1  /  self.GRAV_SED   #  (mg/t = µg kg-1)
        DISTRIB_SW_SED = self.diff_SW * (C_SED_TOT_INT1/self.SED_solid-C_SW_INT) # (mg m-2 h-1); 
        DISTRIB_SW_SED *= self.area #DISTRIB_SW_SED (mg m-² h-1) * area = DISTRIB_SW_SED  (mg/h)

        # 4. calculate final compound mass water for the timesetp (mg)
        self.MASS_SW	= MASS_SW_INT2 - DISTRIB_SW_SED
    
        # 5. calculate distribution between sediment layer
        MASS_SED_INT2 =  MASS_SED_INT1 + DISTRIB_SW_SED
        C_SED_TOT_INT2 = MASS_SED_INT2   /  self.GRAV_SED_DEEP  #  (mg/t = µg kg-1)
        C_SED_DEEP_TOT = self.MASS_SED_DEEP  /   self.GRAV_SED   #  (mg/t = µg kg-1)
        DISTRIB_SED	=  self.diff_SED * (C_SED_DEEP_TOT - C_SED_TOT_INT2)/ self.SED_solid
        DISTRIB_SED	*= self.area #DISTRIB_SED (mg m-² h-1) * area = DISTRIB_SED  (mg/h)
        
        # 6. Calculate final compound mass in sediment 
        self.MASS_SED =	MASS_SED_INT2 - DISTRIB_SED 
        self.MASS_SED_DEEP	= self.MASS_SED_DEEP + DISTRIB_SED
 
        # 7. calculate PEC
        self.PEC_SW = MASS_SW_INT2 / VOL
        self.PEC_SED = MASS_SED_INT1 /  self.GRAV_SED 