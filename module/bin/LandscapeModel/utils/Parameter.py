# -*- coding: utf-8 -*-
"""
Created on Mon Aug  6 17:18:23 2018

@author: smh
"""

import os
import datetime
from collections import Sequence
import numpy as np



class Parameter(object):
    """
    Generic class tempalte for a data record.
    """
    def __init__(self, key, value,date_format="%Y-%m-%dT%H:%M"):


        value = [self.__convertNumbers(val,date_format) for val in value]
        for (key, value) in zip(key, value):
            self.__dict__[key] = value
#    def __setattr__(self, name, value):
#        raise Exception("Read only")
            
 
    def __convertNumbers(self,val,date_format):
        
    
        try: # is float
            val =  float(val)
        except ValueError:
            try: # is date
                val = self.__strDate2pyDate(val,date_format)
            except ValueError: # is boolean
                if (val.lower() == "true") or (val.lower() == "false"):
                    val = val.lower()
                    val = val[0].upper() + val[1:]
                    val = eval(val)
        return val
      
    def __strDate2pyDate(self,date_string,date_format):
        return datetime.datetime.strptime(date_string,date_format)
    
    
    def to_string(self,number_format="%.4f",date_format="%Y-%m-%dT%H:%M",sep=" "):
        
        items = []
        
        for var in self.__dict__.values():
            
            if type(var) == float:
                tmp =  number_format%(var)  
            elif type(var) == int:
                tmp =  "%.0f"%(var)  
            elif type(var) == str or type(var)==np.str_:
                tmp = var
            elif type(var) == datetime.datetime:
                tmp = var.strftime(date_format)
            elif type(var) == bool:
                tmp = str(var)
            else:
                tmp = "error"
            items.append(tmp)
           
        return sep.join(items)
            
class ParameterList(object): # Sequence
    """
    Iterable class which holds a set of data records
    """
    i = 0
    def __init__(self,fpath=None,fname=None,sep=None,
                 date_format =  "%Y-%m-%dT%H:%M",
                 header=None,records=None):
        

        self.__key = fname
        self.key = self.__key
        
        if header == None:        
            header,records = self.__readFile(os.path.join(fpath,fname+".csv"),sep)


        self.__data = [Parameter(header,rec,date_format)  for rec in records]
        self.__index= len(self.__data)

    def __str__(self):
        s=""
        s += " ".join(self.__data[0].__dict__.keys()) + "\n"
        for p in self.__data:
            s+=p.to_string(number_format="%.4f",date_format="%Y-%m-%dT%H:%M",sep=" ")+"\n"
        return s

    def  __len__(self):
        return self.__index
    
    def __iter__(self):
        for param in self.__data:
            yield param
       
    def getbyAttribute(self,key,Attribute,val):
        res = [v for v in self.__data if (v.__dict__[Attribute]==val) & (v.__dict__["key"]==key)]
        return res
 
    def getbyAttribute2(self,key,Attribute,val,Attribute2,val2):
        res = [v for v in self.__data if ((v.__dict__["key"]==key) & (v.__dict__[Attribute]==val) &  (v.__dict__[Attribute2]==val2))]
        return res    

    def getbyAttribute3(self,Attribute,val):
        res = [v for v in self.__data if (v.__dict__[Attribute]==val)]
        return res

    
    def __getitem__(self,val):
        if type(val) == str:
            res = [v for v in self.__data if v.key == val]
#            if len(res) == 1:
#                return res[0]
#            elif len(res) > 1:
#                return res
            if len(res) > 0:
                return res
            else:
                return None
        elif type(val) == int:
            return self.__data[val]
        
        else:
            return None       

    def delete(self,key):
        self.__data.__delitem__([v.key for v in self.__data].index(key))
        self.__index= len(self.__data)
        
    def add(self,key,value):
        """ append item to data list"""
        p = Parameter(key,value)
        self.__data.append(p)
        self.__index= len(self.__data)



#    def __next__(self):
#        
#        if self.i < len(self.__data):
#            self.i += 1
#            return self.__data[self.i-1]
#        else:
#            self.i=0
#            raise StopIteration()

    def __readFile(self,fname,sep):
        """
        Open text file, read header and records.
        
        fname (string): path and name of input data file.
        
        Returns:
            List with header and records
        """
        # open file and read all
        fobj = open(fname,"r")
        f =  fobj.read()
        fobj.close()
        # split by row and col
        f = f.split("\n")
        f = [row.split(sep) for row in f]

        # check if last row is empty (because of MS Excel is alsways printign an empty row)
        if f[-1] == [""]:
            f=f[:-1]

        # get header header and records
        header = f[0]
        records = f[1:]
        
        return header,records
    
    
    
    
    
    
    
    
    
    
    
#    from collections import Sequence
# 
#class MyStructure(Sequence):
#    def __init__(self):
#        self.data = []
# 
#    def __len__(self):
#        return len(self.data)
# 
#    def append(self, item):
#        self.data.append(item)
# 
#    def remove(self, item):
#        self.data.remove(item)
# 
#    def __repr__(self):
#        return str(self.data)
# 
#    def __getitem__(self, sliced):
#        return self.data[sliced]
    
    
    
    
    
    
    
    
    
    