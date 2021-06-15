# -*- coding: utf-8 -*-
"""
Created on Thu Dec 13 10:38:24 2018

@author: smh
"""
from LandscapeModel.utils.Parameter import ParameterList

class SprayDrift(ParameterList):
    def __init__(self,**kwargs):
        #create paamter list
        ParameterList.__init__(self, **kwargs)
        self.__rate = 0
        self.reach = None
    def set_reach(self,reach):
        self.reach=reach
    def get_rate(self):
        return self.__rate
    Rate = property(get_rate)        
    def __call__(self,t,substance):
        """ Return drift value in mg/m2"""
        event=self.getbyAttribute2(self.reach.cmf2drift_name(),"substance",substance,"time",t)
        if len(event)>0:
            self.__rate = event[0].rate
        else:
            self.__rate = 0
            
            


            
            
            
            
            