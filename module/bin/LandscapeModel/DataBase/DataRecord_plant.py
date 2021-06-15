# -*- coding: utf-8 -*-
"""
Created on Wed Sep 13 11:47:52 2017

@author: smh
"""

class DataRecord_plant(object):
    def __init__(self):
        
        self.time = None
        self.name = ""
        self.plantname = ""
        
        # state variables 
        
        self.das = 0.0
        self.rootdepth = 0.0
        self.rootdistribution = []
        self.soil_waterabstraction = []
        self.soil_rootwateruptake = []
        self.soil_evaporation = []
        self.LAI = 0.0
        self.GLAI = 0.0
        self.Epot = 0.0
        self.Tpot = 0.0
        self.Eact = 0.0
        self.Tact = 0.0
        self.Height = 0.0

