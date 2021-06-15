# -*- coding: utf-8 -*-
import os, shutil, pandas
from Reach import Reach
from Toxwa import Toxwa

class CMF_TOXWA_coupler(object):
    """
    Class for CMF-TOXWA coupler
    """
    toxwaInputDir = os.path.join(os.getcwd(),"TOXWA_input")

    def __init__(self,nReach):
        """
        Initializes coupler for all reaches
        """
        # create instance of Toxwa class
        self.toxwa = Toxwa(os.getcwd(),self.toxwaInputDir)

        self.nReach = nReach

        # create list of reaches
        self.reaches = [Reach(ID+1) for ID in range(nReach)]

        # One upstream reach splitting to two downstream reaches
        #reaches[0].set_upstreamIDs([])
        #reaches[0].set_upstreamFractions([])
        #reaches[1].set_upstreamIDs([1])
        #reaches[1].set_upstreamFractions([0.3])
        #reaches[2].set_upstreamIDs([1])
        #reaches[2].set_upstreamFractions([0.7])

        # Two upstream reaches joining to one downstream reach
        self.reaches[0].set_upstreamIDs([])
        self.reaches[0].set_upstreamFractions([])
        self.reaches[1].set_upstreamIDs([])
        self.reaches[1].set_upstreamFractions([])
        self.reaches[2].set_upstreamIDs([1,2])
        self.reaches[2].set_upstreamFractions([1,1])

        for reach in self.reaches: self.toxwa.init_reach(reach)
    
    def __call__(self):
        """
        Runs TOXWA for all reaches
        """
        for reach in self.reaches: self.toxwa(reach)

    def process_toxwa_output(self):
        """
        Writes average concentration of all reaches to a single CSV file
        """
        output_table = self.toxwa.get_output(self.reaches[0],"ConLiqWatTgtAvg_Dmtr")
        for reach in self.reaches[1:]:
            toxwa_output = self.toxwa.get_output(reach,"ConLiqWatTgtAvg_Dmtr")
            output_table = pandas.concat([output_table, toxwa_output[3]], 1)
        hdr = ["Time step", "Time", "Variable"] + ["Reach" + str(i) for i in range(self.nReach)]
        output_table.to_csv("ConLiqWatTgtAvg_Dmtr.csv", header = hdr, index = False)
            
if __name__ == "__main__":
    coupler = CMF_TOXWA_coupler(3)
    coupler()
    coupler.process_toxwa_output()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    