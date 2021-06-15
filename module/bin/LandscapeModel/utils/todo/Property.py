# -*- coding: utf-8 -*-
"""
Created on Mon Aug  6 15:25:21 2018

@author: smh
"""

class Parameter(object):
    """
    Generic class tempalte for a data record.
    """
    def __init__(self, key, value):
        for (key, value) in zip(key, value):
            self.__dict__[key] = value
    def __setattr__(self, name, value):
        raise Exception("Read only")



class ParameterList(object):
    """
    Iterable class which hodls a set of data records
    """
    i=0
    def __init__(self,fname,sep):
        
        # read input data
        header,records = self.__readFile(fname,sep)
        
        # create list with data        
        self.__data = [Parameter(header,rec)  for rec in records]

    def __iter__(self):
        return self
    
    def __getitem__(self,val):
        
        
        if type(val) == str:
            res = [i for i in self.__data if i.key == val]
            if len(res) > 0:
                return res[0]
            else:
                return None
        elif type(val) == int:
            return self.__data[val]
        else:
            return None
        
        
        
    
    def __next__(self):
        if self.i < len(self.__data):
            self.i += 1
            return self.__data[self.i-1]
        else:
            raise StopIteration()
    
    def __readFile(self,fname,sep):
        """
        Open text file, read header and records.
        
        fname (string): path and name of input data file.
        
        Returns:
            List with header and records
        """
        # open file and read all
        f = open(fname,"r")
        f =  f.read()
        # split by row and col
        f = f.split("\n")
        f = [row.split(sep) for row in f]
        # get header
        header = f[0]
        records = f[1:]
        return header,records
        




if __name__ == "__main__":
    
    
    
    fname = r"n:\MOD\108604_BCS_BEL_pome\mod\cal\EFATE\CMF_Mesterbeek\test1_StreamNetwork_FieldLayer\test.txt"
    
    p = ParameterList(fname=fname,sep=",")

















