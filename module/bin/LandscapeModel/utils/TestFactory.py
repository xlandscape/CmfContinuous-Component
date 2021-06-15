# -*- coding: utf-8 -*-
"""
Created on Wed Aug  8 14:27:04 2018

@author: smh
"""
import LandscapeModel

class TestFactory():
    
    def __init__(self,fdir,fname,nc,py):
        self.fdir = fdir
        self.fname = fname
        self.nc   = nc
        self.py   = py

    def __test(self,message,func,**kwargs):
        self.__message("\nTEST: %s\n"%(message))
        try:
            res = func(**kwargs)
            self.__message("\nTEST: successful\n")
            return res
        except Exception as e:
            self.__message("\nTEST: " + str(e) + "\n")
            
    def __message(self,s):
            print(s)    

    def run_completeCatchment(self): #TODO: ready?
        """
        Test run_completeCatchment.
        
        The respective function calls are, e.g.:
            # runFactory = LandscapeModel.utils.RunFactory(fdir)
            # runFactory.run_completeCatchment(asBatch=False) or
            # runFactory.run_completeCatchment(asBatch=False, name = "some run ID")
        """
        runFactory = self.__test("load data with RunFactory",
                                 LandscapeModel.utils.RunFactory,
                                 fdir=self.fdir,
                                 fname = self.fname)
        self.__test(message = "call run_completeCatchment",
                    func = runFactory.run_completeCatchment,
                    asBatch=False)

    def run_timeseriesCatchment(self,name=""): #TODO: implement and test
        """
        Test run_timeseriesCatchment.
        
        The respective function calls are, e.g.:
            # runFactory = LandscapeModel.utils.RunFactory(fdir)
            # runFactory.run_timeseriesCatchment(asBatch=False) or
            # runFactory.run_timeseriesCatchment(asBatch=False, name = "some run ID")
        """
        runFactory = self.__test("load data with RunFactory",
                                 LandscapeModel.utils.RunFactory,
                                 fdir=self.fdir,
                                 fname = self.fname)
        
        self.__test(message = "call run_timeseriesCatchment",
                    func = runFactory.run_timeseriesCatchment,
                    asBatch=False,
                    name = name)

    def run_artificialStream(self): #TODO: implement and test
        """
        Test run_artificialStream.
        
        The respective function calls are, e.g.:
            # runFactory = LandscapeModel.utils.RunFactory(fdir)
            # runFactory.run_artificialStream(asBatch=False) or
            # runFactory.run_artificialStream(asBatch=False, name = "some run ID")
        """
        runFactory = self.__run("load data with RunFactory",
                                 LandscapeModel.utils.RunFactory,
                                 fdir=self.fdir,
                                 fname = self.fname)
        self.__test(message = "call run_artificialStream",
                    func = runFactory.run_artificialStream,
                    asBatch=False)        
        
    def run_uniqueFields(self):
        """
        Test run_uniqueFields.
        
        The respective function calls are, e.g.:
            # runFactory = LandscapeModel.utils.RunFactory(fdir)
            # runFactory.run_uniqueFields(asBatch=False) or
            # runFactory.run_uniqueFields(asBatch=False, name = "some run ID")
        """
        runFactory = self.__test("load data with RunFactory",
                                 LandscapeModel.utils.RunFactory,
                                 fdir=self.fdir,
                                 fname = self.fname)

        self.__test(message = "call run_uniqueFields",
                    func = runFactory.run_uniqueFields,
                    asBatch=True,
                    ncores=self.nc ,pythonpath=self.py ,execute=True)     
        
        
        
        
        
        
        
        
        
        