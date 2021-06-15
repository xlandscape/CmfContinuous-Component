# -*- coding: utf-8 -*-
"""
Created on Wed Feb 27 11:50:16 2019

@author: smh
"""


def get_Catchment_per_Reach(CellList):
    """
    In order to derive the catchment area which is related to one reach,
    the field areas of all fields attached in first, second ,... order to
    the reach must be summarized.
    """
    # get cells per reach
    conFieldReach = []
    for cell in CellList:
        foundreach = False
        actCell = cell
        while not foundreach:            
            if actCell.reach != "None":
                conFieldReach.append([actCell.reach,cell.key,cell.area])
                foundreach = True 
            else:
                actCell = [i for i in self.CellList if i.key == actCell.adjacent_field][0]
    return  ParameterList(header=["key","cell","area"],records=conFieldReach)



