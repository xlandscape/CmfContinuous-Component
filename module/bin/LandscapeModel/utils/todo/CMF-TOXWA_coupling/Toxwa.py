# -*- coding: utf-8 -*-
import os, io, subprocess, pandas, re, shutil

class Toxwa(object):
    """
    Class for TOXWA model.
    Contains attributes and methods for running TOXWA, preparing input and reading output.
    """
    # Name of TXW template file
    txwTemplateFile = "txw_template.txw"
    # Name of MFU template file
    mfuTemplateFile = "mfu_template.mfu"
    # Base name of hydrology file
    hydrologyFileBaseName = "hydrology"
    # Base name of spray drift file
    spraydriftFileBaseName = "spraydrift"
    # Base name of waterbody file
    waterbodyFileBaseName = "waterbody"
    
    # Command to run TOXWA
    runCommand = os.path.join("..","run_TOXWA.BAT")
    # Name of working directory
    workDirName = "work"
    
    def __init__(self, projectDir,inputDir):
        """
        Creates toxwa object
        """
        self.inputDir = inputDir
        self.workDir = os.path.join(projectDir,self.workDirName)
        if not os.path.exists(self.workDirName): os.makedirs(self.workDirName)

        # copy meteorology file
        if not os.path.isfile(os.path.join(self.workDir,"Melsterbeek.met")):
            shutil.copy(os.path.join(self.inputDir,"Melsterbeek.met"),self.workDir)

    def init_reach(self,reach):
        """
        Initializes TOXWA simulation for given reach.
        Writes input files that do not depend on upstream runs (TXW and HYD)
        """
        
        # Read contents of TXW template file
        txwTemplate_file = open(os.path.join(self.inputDir,self.txwTemplateFile),"r")
        txwContent = txwTemplate_file.readlines()
        txwTemplate_file.close()

        # Read spray drift
        spraydrift = pandas.read_csv(os.path.join(self.inputDir,self.spraydriftFileBaseName + "_reach" + str(reach.ID) + ".csv"),comment = "#", header = None)
        spraydriftStr = spraydrift.to_string(header = False, index = False)

        # Read water body information
        waterbody_file = open(os.path.join(self.inputDir,self.waterbodyFileBaseName + "_reach" + str(reach.ID) + ".txt"),"r")
        waterbody = waterbody_file.readlines()
        waterbody_file.close()

        # Insert spraydrift and waterbody information in TXW file
        lineIdx = get_lineIndex(txwContent,"table Loadings")
        txwContent.insert(lineIdx, spraydriftStr  + "\n")
        lineIdx = get_lineIndex(txwContent,"table WaterBody")
        txwContent.insert(lineIdx, "".join(waterbody)  + "\n")
        txw_file = open(os.path.join(self.workDir,"Reach" + str(reach.ID) + ".txw"), "w")
        txw_file.write("".join(txwContent))

        # Copy hydrology file
        shutil.copy(os.path.join(self.inputDir,self.hydrologyFileBaseName + "_reach" + str(reach.ID) + ".hyd"),
                    os.path.join(self.workDir,"Reach" + str(reach.ID) + ".hyd"))

    def __call__(self,reach):
        """
        Runs TOXWA for given reach
        """
        self.write_mfu(reach)
        result = subprocess.check_output('"' + self.runCommand + '"' + " Reach" + str(reach.ID), shell=True, cwd = self.workDir)

    def get_output(self,reach,varName):
        """
        Reads and returns variable varName from TOXWA output file for given reach
        """

        # Figure out if we got a reach object or a reach ID as input. Not pretty but for now...
        if type(reach).__name__ == 'int':
            reachID = reach
        else:
            reachID = reach.ID

        f = open(os.path.join(self.workDir,"Reach" + str(reachID) + ".out"),'r')
        
        # create a generator to loop over lines in output file that contain varName
        lines = varfilter(f,varName)

        # write the lines in a memory buffer
        tmp = io.StringIO()
        for line in lines:
            tmp.write(line)
        f.close()
        tmp.flush()
        tmp.seek(0)

        # read from the memory buffer and convert to a table (DataFrame)
        toxwa_output = pandas.read_table(tmp,delim_whitespace=True,header=None)
        tmp.close()
        return toxwa_output
    
    def write_mfu(self,reach):
        """
        Write MFU file for given reach. This is based output of runs for upstream reaches defined in reach.upstreamIDs
        """
        mfuFile = open(os.path.join(self.workDir, "Reach" + str(reach.ID) + ".mfu"),'w')
        massFlow = list()


        if len(reach.upstreamIDs) == 0:
            # This reach has no upstream reaches 
            mfuFile.write("First_reach")
        else:
            # This reach has upstream reaches
            # Read the mass flow from output files for upstream reaches
            for i in range(len(reach.upstreamIDs)):
                upID = reach.upstreamIDs[i]
                toxwa_output = self.get_output(upID,'MasDwnWatLay_Dmtr')
                # multiply mass flow by upstream fractions (this only matters when 
                # there are multiple upstream reaches)
                massFlow.append(-toxwa_output[3]*reach.upstreamFractions[i])
            
            # sum all the mass flows of the upstream reaches
            toxwa_output[3] = sum(massFlow)

            # Read MFU template file
            file_mfuTempl = open(os.path.join(self.inputDir,self.mfuTemplateFile),'r')
            mfuTempl = file_mfuTempl.read()
            file_mfuTempl.close()

            # Fill in no of upstream reaches and their IDs 
            mfuTempl = re.sub("<nUpstrReach>", str(len(reach.upstreamIDs)), mfuTempl)
            mfuTempl = re.sub("<upstrReachIDs>", ','.join(map(str, reach.upstreamIDs)), mfuTempl)                
            mfuFile.write(mfuTempl + "\n")
            
            # Formatter to convert table to string to write to MFU file
            fmt = [lambda x: "%5.3f" %x,  lambda x: "%s" %x,  lambda x: "%0e" %x]
            mfuStr = toxwa_output.to_string(columns = [0,1,3], header = False, index = False, formatters = fmt)
            mfuFile.write(mfuStr)
            mfuFile.close()

def varfilter(file,varName):
    """
    Creates a generator that allows us to loop over lines in TOXWA output file containing varName
    """
    for line in file:
        if varName in line:
            yield(line)

def get_lineIndex(fileContents,string):
    """
    Searches for string in text file contents and returns line number
    """
    for num, line in enumerate(fileContents, 1):
        if string in line:
            return num
