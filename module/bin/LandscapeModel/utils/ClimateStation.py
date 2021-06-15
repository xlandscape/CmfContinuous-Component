# -*- coding: utf-8 -*-
"""
Created on Tue Sep  4 17:04:24 2018

@author: smh
"""
import cmf
from .Parameter import ParameterList

class ClimateStation(ParameterList):
    
    def __init__(self,project,cs,**kwargs):
        # fpath,fname,sep
        
        #create paamter list
        ParameterList.__init__(self, **kwargs)

        # get column headings
        col = [i for i in self[0].__dict__]

        # determine timestep
        delta_t = (self[1].key - self[0].key)
        if delta_t.days == 1:
            step = cmf.day
        elif delta_t.seconds == 3600:
            step = cmf.h

        self.step = step
        self.delta_t = delta_t
        
        # create meteo station
        self.meteo_station = project.meteo_stations.add_station(cs.key,
                                           position=(cs.x,cs.y,cs.z),
                                           latitude=cs.lat,longitude=cs.lon)
        
        # function to check if a certain climate paramter exists
        def check_field_exists(fieldname):
            has_parameter = False
            if len([i for i in col if i == fieldname]):
                 has_parameter = True
            return has_parameter

        # create climate data
        if check_field_exists("rain"):
            self.rain = cmf.timeseries(begin = self[0].key, step = step)
            for i in self: self.rain.add(i.rain) 
         
            
        # climate data is only read in if no eto is avaialable:
        if not check_field_exists("eto"):
            if check_field_exists("tmax"):
                self.meteo_station.Tmax = cmf.timeseries(begin = self[0].key, step = step)
                for i in self: self.meteo_station.Tmax.add(i.tmax) 
                
            if check_field_exists("tmin"):
                self.meteo_station.Tmin = cmf.timeseries(begin = self[0].key, step = step)
                for i in self: self.meteo_station.Tmin.add(i.tmin) 
            
            if check_field_exists("rhmean"):
                self.meteo_station.rHmean = cmf.timeseries(begin = self[0].key, step = step)
                for i in self: self.meteo_station.rHmean.add(i.rhmean) 
            
            if check_field_exists("windspeed"):
                self.meteo_station.Windspeed = cmf.timeseries(begin = self[0].key, step = step)
                for i in self: self.meteo_station.Windspeed.add(i.windspeed) 
        
            if check_field_exists("sunshine"):
                self.meteo_station.Sunshine  = cmf.timeseries(begin = self[0].key, step = step)
                for i in self: self.meteo_station.Sunshine.add(i.sunshine) 
        else:
            
            # set dummy parameter because otherwise cmf is not working
            self.meteo_station.Tmax = cmf.timeseries(begin = self[0].key, step = step)
            for i in self: self.meteo_station.Tmax.add(0) 
            
            #TODO: sunshine variable is used as dummy for eto
            self.meteo_station.Sunshine = cmf.timeseries(begin = self[0].key, step = step)
            for i in self: self.meteo_station.Sunshine.add(i.eto) 

        # create rainstation
        self.rain_station = project.rainfall_stations.add(cs.key,self.rain,(cs.x,cs.y,cs.z))   
        
        
        
        
        
        