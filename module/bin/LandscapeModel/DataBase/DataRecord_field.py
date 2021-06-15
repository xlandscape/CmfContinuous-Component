# -*- coding: utf-8 -*-
"""
Created on Wed Sep 13 11:47:52 2017

@author: smh
"""

class DataRecord_field(object):
    def __init__(self):
        
        self.time = None
        self.name = ""
        # water fluxes
        self.Vgw = 0.0
        self.qperc = 0.0
        self.qsurf = 0.0
        self.qdrain = 0.0
        self.qgw_gw = 0.0
        self.qgw_river = 0.0
        self.qlateral = 0.0
        self.Vsoil = []
        self.delta_Vsoil = []
        
        self.rain = 0.0
        
        #solutes concentration
        self.concgw = 0.0
        self.concsoil =[]
        self.loadgw = 0.0
        self.loadsoil =[]  
        
        self.concsw = 0.0
        self.loadsw = 0.0
        self.concdrainage = 0.0
        self.loaddrainage = 0.0       
