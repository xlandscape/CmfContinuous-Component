# -*- coding: utf-8 -*-
"""
Created on Tue Sep 12 14:09:02 2017

@author: smh
"""

class CatchmentOutlet(object):
    """
    Catchment outlet.
    
    The class mainly manages data transfer and the initialisation of cmf.NewOutlet
    with input data.
    """
    
    def __init__(self,name,x,y,z):
        """
        Creates a catchment outlet.
        
        name (string):              name
        x (double):                 x coordinate 
        y (double):                 y coordinate 
        z (double):                 altitude 
        """
        self.__catchment = None
        self.__name = name
        self.__x = x
        self.__y = y
        self.__z = z
        self.__outlet = None

        
    ###########################################################################
    # properties
    def __getName(self):
        """Name"""
        return self.__name
    Name = property(__getName)

    def __getX(self):
        """x coord"""
        return self.__x
    x = property(__getX)

    def __getY(self):
        """y coord"""
        return self.__y
    y = property(__getY)

    def __getZ(self):
        """z coord"""
        return self.__z
    z = property(__getZ)
    
    def __getOutlet(self):
        """Outlet"""
        return self.__outlet
    Outlet = property(__getOutlet)
    
    def __getvolume(self):
        """Water volume in (m3)"""
        return  self.__outlet.volume
    Volume = property(__getvolume)
    
    def __getflow(self):
        """Water flow (m3)"""
        t = self.__catchment.solver.t
        return  self.__outlet.waterbalance(t)
    Flow = property(__getflow)
        
    def __getconc(self):
        """Solute concentration"""
        t = self.__catchment.solver.t
        if len(self.__catchment.p.solutes)>0:
            return   self.__outlet.conc(t,self.__catchment.p.solutes[0]) #mg/m3
        else:
            return 0
    Conc = property(__getconc)       

    def __getload(self):
        """Solute load"""
        t = self.__catchment.solver.t
        if len(self.__catchment.p.solutes)>0:
            return self.__outlet.conc(t,self.__catchment.p.solutes[0]) * self.__outlet.volume #mg
        else:
            return 0
    Load = property(__getload)   

    def initialisze_with_project(self,catchment):
        """
        Initialises a CatchmentOutlet with a cmf.project.
        
        catchment (SubCatchment):   a subcatchment object
        """
        self.__catchment = catchment
        self.__outlet = self.__catchment.p.NewStorage(self.__name,x=self.__x,y=self.__y,z=self.__z) 
        