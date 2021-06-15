# -*- coding: utf-8 -*-
"""
Created on Thu Dec 13 10:42:43 2018

@author: smh
"""

class CMF_EFATE:
    """
    Interface between one reach and quatic efate.
    """
    def __init__(self,reach,efate):
        self.reach = reach
        self.efate = efate 
        self.connect_models()
    def connect_models(self):
        self.reach.Efate = self 
    def cmf2efate_lenght(self):
        """ Length of reach (m) L	constant"""
        return self.reach.Lenght
    def cmf2efate_load(self):
        """ Returns solute load in mg"""
        return self.reach.Load
    def cmf2efate_conc(self):
        """ Returns solute concentration in mg/m3"""
        return self.reach.Conc
    def cmf2efate_volume(self):
        """ Returns volume m3"""
        return self.reach.Volume
    def cmf2efate_flow(self):
        """ Returns outflow in m3/day"""
        return self.reach.Flow
    def cmf2efate_watertemperature(self):
        """ water temperatuer °C """
        return self.reach.WaterTemperature
    def efate2cmf_load(self):
        """ Returns load from efate (mg)"""
        return self.efate.get_load()
    def efate_run(self,INPUT_SW,MASS_SW,TEMP,VOL):
        """ Ru nefate"""
        self.efate(INPUT_SW,MASS_SW,TEMP,VOL)
    def efate2cmf_MASS_SW(self):
        """MASS_SW"""
        return self.efate.MASS_SW
    def efate2cmf_MASS_SED(self):
        """MASS_SED"""
        return self.efate.MASS_SED
    def efate2cmf_MASS_SED_DEEP(self):
        """MASS_SED_DEEP"""
        return self.efate.MASS_SED_DEEP
    def efate2cmf_PEC_SW(self):
        """PEC_SW"""
        return self.efate.PEC_SW
    def efate2cmf_PEC_SED(self):
        """PEC_SED"""
        return self.efate.PEC_SED

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    