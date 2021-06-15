# -*- coding: utf-8 -*-
"""
Created on Thu Dec 13 10:33:33 2018

@author: smh
"""

class CMF_DRIFT():
    """ 
    Interface between one reach and Xdrift.
    
    Data transfer is one-way from CMF to drift.
    """
    def __init__(self,reach,drift):
        """
        For testing xdrift is just a list of drift events.
        
        Args:
            reach (CMF.Reach): Reach of CMF.
            xdrift (List): List of SubstanceApplication
        """
        self.reach = reach
        self.drift = drift 
        # connect models
        self.connect_models()
    def connect_models(self):
        self.reach.Drift = self
        self.drift.set_reach(self)     
    def cmf2drift_wetarea(self):
        return self.reach.get_wetarea()
    def cmf2drift_name(self):
        return self.reach.Name
    def drift2cmf_rate(self,t,substance):
        self.drift(t,substance)
        return self.drift.Rate