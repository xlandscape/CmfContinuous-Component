# -*- coding: utf-8 -*-
"""
Created on Wed Sep 13 12:14:04 2017

@author: smh
"""


#from sqlalchemy import Column, ForeignKey, Integer, String
#from sqlalchemy.ext.declarative import declarative_base
#
#Base = declarative_base()

class DataRecord_reach(object):
#    __table__name = 'Reach'
    def __init__(self):
        
        self.time = None
        self.name = ""
        # water fluxes
        self.depth = 0.0
        self.conc = 0.0
        self.load = 0.0
        self.artificialflux = 0.0
        self.volume = 0.0
        self.flow = 0.0
        self.area = 0.0
        self.MASS_SW = 0.0
        self.MASS_SED = 0.0
        self.MASS_SED_DEEP = 0.0
        self.PEC_SW = 0.0
        self.PEC_SED = 0.0

