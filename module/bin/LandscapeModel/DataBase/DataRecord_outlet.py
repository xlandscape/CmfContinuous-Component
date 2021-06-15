# -*- coding: utf-8 -*-
"""
Created on Wed Sep 13 12:57:25 2017

@author: smh
"""

class DataRecord_outlet(object):
    def __init__(self):
        
        self.time = None
        self.name = ""
        # water fluxes
        self.flow = 0.0
        self.volume = 0.0
        self.conc = 0.0