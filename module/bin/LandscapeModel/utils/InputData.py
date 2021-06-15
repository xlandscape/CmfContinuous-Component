# -*- coding: utf-8 -*-
"""
Created on Mon Aug  6 15:25:21 2018

@author: smh
"""

import os
from xml.dom import minidom
from .Parameter import ParameterList

class InputData(object):
    """
    Iterable class which holds a set of data records
    """
    def __init__(self,fpath,sep=","):
        
        # read input data information from xml
        key = [i.attributes['name'].value for i in self.__read_info(
                os.sep.join(os.path.abspath(__file__).split("\\")[:-1]),"input_tables.xml")]
        value = [ParameterList(fpath,fname,sep) for fname in key]
         
        for (key, value) in zip(key, value):
           self.__dict__[key] = value
    
    def __setattr__(self, name, value):
        raise Exception("Read only")

    def __read_info(self,fpath,fname):
        # parse an xml file by name
        mydoc = minidom.parse(os.path.join(fpath,fname))
        items = mydoc.getElementsByTagName('item')
        return items



#if __name__ == "__main__":
#    
#    fpath = r"c:\LandscapeModel\artificialStream_test1"
#    inpData = InputData(fpath,sep=",")
#    CatchmentList = inpData.CatchmentList
#    print([inpData.ReachList[i].key for i in range(len(inpData.ReachList))])
#    print(CatchmentList.getbyAttribute("Melsterbeek","component","Groundwater").component)
#    print([(p.key,p.depth) for p in inpData.SoilList["soil1"]])
#    print([i.key for i in inpData.CellList])
#    print([i.key for i in inpData.CellList])
#    print(inpData.CropManagementList.getbyAttribute("f1","date","2000_04_16_00"))


#    print([i for i in inpData.CellList if i.key == "f1"][0])
#    print([i for i in inpData.CellList if i.key == "f2"][0])
#    print([i for i in inpData.CellList if i.key == "f3"][0])
#
#    print(inpData.CropManagementList.getbyAttribute("f2","date",'2001-01-01T00:00'))
#    print(inpData.CropManagementList.getbyAttribute("f3","date",'2001-01-01T00:00'))


#     test climate station
#    p = cmf.project()
#    cs = inpData.ClimateList[0]
#    clim=ClimateStation(project = p,cs=cs,fpath=fpath,fname="clim1",sep=",",date_format="%Y-%m-%dT%H:%M")
#    print(clim.__dict__)



    # find reach of each cell
    
#    cell_reach = []
#    for c in inpData.CellList:
#        if c.reach != "None":
#            cell_reach.append([c.key,c.area,c.reach])
#        else:
#    for reach in inpData.ReachList:
#        
#        # get area of fields which are directly attached to the reach
#        area1 = sum([c.area for c in inpData.CellList if c.reach == reach.key])
#        print(reach.key,area1)
##    inpData.CellList
#

#    
#    pass


    









