# -*- coding: utf-8 -*-
"""
Created on Fri Feb 15 17:03:56 2019

@author: smh
"""

import os
import LandscapeModel
import numpy as np
from datetime import datetime
import copy
import shutil

class CatchmentSeparator():
    """
    The class handels the separation of a catchment into several solver
    units. For this, iterative algorithm is applied which counts for each
    reach the number of following elemets (reaches and cells). Based on a
    certain threshold, groups are summarized. For each group, a new 
    project is created which is then run by one solver independently.
    
    Attributes:
    -----------
    catchment (LandscapeModel.Catchment): Catchment which should be
    separated into solverunits.
    fname (str): name of project.
    fpath (str): path of project.
    solverunits (LandscapeModel.utils.ParamterList): List with solverunits.
    
    """
    def __init__(self,catchment,name="solverunits"):
        """
        Initialisis class.
        
        Attributes:
        -----------
        catchment (LandscapeModel.Catchment): Catchment which should be
        separated into solverunits.
        name (str): name of project.
        """

        # get some info's from catchment
        self.__c = catchment
        
        # create subdirectory and set name
        self.__fpath_src = os.path.join(self.__c.modelrun.fpath,self.__c.modelrun.key)
        self.__fpath = os.path.join(self.__c.modelrun.fpath,self.__c.modelrun.key,name)
        self.__fname = name

        # create sub-directory for solver units inside catchment folder
        if not os.path.isdir(self.__fpath):
            os.mkdir(self.__fpath)
        else:
            pass#raise Exception("Subdirectory 'solverunits' already exists.")
        
        # create solverunits list
        #self.__message("make initial solverunit list")
        self.solverunits = self.__initialiseSolverUnits(self.__c.inpData.ReachList,
                            self.__c.inpData.CellList)
        
        # find upstream reaches
        #self.__message("find upstream storages")
        self.__findUpstream(self.solverunits,self.__c.inpData.ReachList,
                            self.__c.inpData.CellList)
        
        # run-oder of soverunits
        self.runorder = None
        
    def __repr__(self):
        return ""
    
    def __message(self,s):
        t = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        print(t + ": " + s)
    
    def __call__(self,nCells=9999):
        """
        Separate catchment into solverunits and create relevant file strucutre.
        
        Attributes:
        -----------
        nCells (int): Minimum number of cells to form a solverunit.
        nReaches (int): Minimum number of reaches to form a solverunit.
        fpath (str): Target path for solverunits.
        
        Returns
        -----------
        success (boolean): True if separation was successful        
        """
        success = False

        # create solverunits
        self.__message(s="separate catchment")
        self.__separateCatchment(self.solverunits,nCells)

        # make list with run-order
        self.__message(s="make run-order")
        self.runorder = self.__createRunOrder(self.solverunits)

        # write runlist containing all solverunits
        self.__message(s="make runlist")
        self.__makeRunList(self.solverunits )
        
        # create subdirectories for each solverunits and data
        self.__message(s="make sub-directories of solverunits")
        self.__createProjects(self.solverunits)
        
        # save solverunits
        s=",".join(self.solverunits[0].__dict__.keys()) + "\n"
        s+="\n".join([i.to_string(sep=",") for i in self.solverunits])
        self.__writeFile(s,os.path.join(self.__fpath,self.__fname + "_solverunits.csv"))
        
        # save runorder
        s=",".join(self.runorder[0].__dict__.keys()) + "\n"
        s+="\n".join([i.to_string(sep=",") for i in self.runorder])
        self.__writeFile(s,os.path.join(self.__fpath,self.__fname + "_runorder.csv"))
        
        # True if no error occurs
        success = True
        return success


    def mix_water(self,flows,concs):
        """
        Mixes fluxes (water+solutes) from two or more timeseries.
        
        :param flows: List with timeseries of flows.
        :param flows: list 
        :param concs: List with timeseries of flows.
        :param concs: list
        
        :returns: Three arrays with mixed laods,flows and concs.
        :rtype: np.array
        """
        # calc loads
        mix_loads = np.multiply(flows,concs)
        mix_loads = np.sum(mix_loads,axis=0)
        # sum up flows
        mix_flows = np.sum(flows,axis=0)
        # calc concs
        mix_concs = np.divide(mix_loads,mix_flows)
        return mix_loads,mix_flows,mix_concs
        

    def run_SolverUnits(self):
        """
        Simulate all solverunits in a consecutive order as defined in runorder.
        """
        # start = datetime.now()

        # run solverunits
        count = len(np.unique([i.solverunitID for i in self.solverunits]))
        count_su = 1
        for runorderID in np.unique([i.order for i in self.runorder]):
            # get all solverunits for runorderID
            solverunits = [i.key for i in self.runorder if i.order == runorderID]
            # run solverunits
            for su in solverunits:
                # make simulation
                self.__message(s="simulate %i/%i %s"%(count_su,count,su))
                sc = self.__simulate(self.__fpath,self.__fname+"_runlist",su) 
                db = sc.database
                #self.__message(s="runorderID:%.0f %s %s"%(runorderID, su,str(datetime.now()- start)))
                
                
                ro = self.runorder.getbyAttribute3("key",su)[0]
                
                # copy dat aof downstream reach to next solver unit
                if ro.target_solverunit != "Outlet":
                    
                    # get timeseries of reach
                    reach_src = db.get_data_by_key("reaches",ro.source_storage)
                    reach_src = reach_src[db.columns_ts_reaches].copy()
                    

                    # check if a timeseries for the reach already exists in target sovler unit
                    fname=os.path.join(self.__fpath,ro.target_solverunit,"Timeseries",ro.target_storage+"."+db.ext)
                    header = db.columns_ts_reaches
                    
                    
                    
                    if os.path.exists(fname): 
                        self.__message(s="merge files %s,%s --> %s,%s"%(su,ro.source_storage,ro.target_solverunit,ro.target_storage))
                        # open existing reach
                        reach_trg_exist = db.read_file(fname,db.dtype_ts_reaches,"reaches",isTS=True).copy()
    
                        # set name
                        reach_trg_exist["key"] = ro.target_storage
                   
#                        # sum up flow data
#                        reach_trg_exist["flow"] += reach_src["flow"]
#
#                        # sum up loads
#                        loads_src =  reach_src["flow"] *  reach_src["conc"]
#                        loads_trg =  reach_trg_exist["flow"] *  reach_trg_exist["conc"]                      
#
#                        # calculate conc
#                        reach_trg_exist["conc"] = (loads_src+loads_trg) / reach_trg_exist["flow"]

                        
                        flows = [reach_trg_exist["flow"], reach_src["flow"]]
                        concs = [reach_trg_exist["conc"], reach_src["conc"]]
                        mix_loads,mix_flows,mix_concs = self.mix_water(flows,concs)
                        reach_trg_exist["flow"] = mix_flows
                        reach_trg_exist["conc"] = mix_concs

                        # write timeseries to downstream solver unit
                        db.write_file(fname,reach_trg_exist,
                                      fmt=db.fmt_ts_reaches,
                                      header=header,tablename="reaches")
                    
                    else:
                        self.__message(s="copy files %s,%s --> %s,%s"%(su,ro.source_storage,ro.target_solverunit,ro.target_storage))
                        
                        # write timeseries to downstream solver unit
                        reach_src["key"] = ro.target_storage
                        db.write_file(fname,reach_src,fmt=db.fmt_ts_reaches,
                                      header=header,tablename="reaches")
                    
                count_su+=1
                    
        # merge files
        self.merge_files()
                    
    def merge_files(self):
        """
        Merge all files
        """
        
        # get solver units
        db = self.__c.database
        fpath=os.path.join(self.__c .modelrun.fpath,self.__c .modelrun.key)
        key = self.__c.modelrun.key
        fname="solverunits_runorder"
        runorder = LandscapeModel.utils.ParameterList(os.path.join(fpath,"solverunits"),fname,",")
        solverunits = [i.key for i in runorder]
        
        # start with reaches, plants and cells which must be merged by append
        tables = ["reaches"]
        if db.hasPlants:
            tables += ["plants"]
        if db.hasCells:
            tables += ["cells"]
        
        print("merge files")
        for su in solverunits:
            for tbl in tables:
                print ("merge",su,tbl)

                db.append_files(src=os.path.join(fpath,"solverunits",su,su+"_"+tbl),
                                trg=os.path.join(fpath,key+"_"+tbl),
                                tbl=tbl)

        # copy outlets and gws file from su at outlet
        print("copy","outlets and gws")
        #get solverunit at outlet
        su = [i for i in runorder if i.target_storage=="Outlet"][0].source_solverunit
        # copy outlet file
        shutil.copy(src=os.path.join(fpath,"solverunits",su,su+"_outlets."+db.ext),
                    dst=os.path.join(fpath,key+"_outlets."+db.ext))
        # copy gws file
        shutil.copy(src=os.path.join(fpath,"solverunits",su,su+"_gws."+db.ext),
                dst=os.path.join(fpath,key+"_gws."+db.ext))       

    def __simulate(self,fpath,fname,su):
        """
        Makes a siulation with the catchmetn model.
        """
        # create sub-catchment and male run
        runFactory = LandscapeModel.utils.RunFactory(fdir=fpath,fname=fname )
        runFactory(su,printTime=False)      
        sc = runFactory.runs[-1]
        return sc
    
#    def __copyFiles(self,su,runorder,source_catchment):
#        """
#        Copy flow timeseries from upper to lower solverunit 
#        """
#        ro = runorder.getbyAttribute3("key",su)[0]
#        if ro.target_solverunit != "Outlet":
#            
#            
#            
#            
#            
#            
#            # extract data of the reach which is connected to the outlet
#            self.__copy_TimeseriesReaches(source_catchment,
#                                            ro.source_solverunit,
#                                            ro.target_solverunit,
#                                            ro.source_storage,
#                                            ro.target_storage)
#
#    def __copy_TimeseriesReaches(self,source_catchment,source_solverunit,
#                                 target_solverunit,source_storage,
#                                 target_storage) :  
#        # get data of specific reach of su
#        ext = source_catchment.database.ext
#        reach = source_catchment.load_timeseries("cells",source_storage)
#        
#        # create target path
#        fpath=os.path.join(self.__fpath,target_solverunit,"Timeseries")
#        fname=target_storage
#
#        # check if a file already exists
#        if os.path.exists(os.path.join(fpath,fname+"."+ext)): 
#      
#            # open existing file
#            reach2 =  LandscapeModel.utils.ParameterList(fpath,fname,sep=",")
#            # sum up data
#            flow_sum = [sum((i["flow"],j.flow)) for i,j in zip(reach,reach2)]
#
#        else:
#            flow_sum = [i.flow for i in reach]
#
#        # create string
#        header = "key,time,flow_m3day"
#        records  = "\n".join([",".join((target_storage,r.time.strftime("%Y-%m-%dT%H:%M"),
#                                        str(flow))) for r,flow in zip(reach,flow_sum)])
#        s = header +"\n" + records
#        #write file       
#        self.__writeFile(s,os.path.join(fpath,fname+".csv"),mode="w")    
    
    
    
#    def __copyFiles(self,su,runorder,fpath):
#        """
#        Copy flow timeseries from upper to lower solverunit 
#        """
#        ro = runorder.getbyAttribute3("key",su)[0]
#        if ro.target_solverunit != "Outlet":
#            # open reach file
#            fpath = os.path.join(fpath,su)
#            fname = su + "_reaches"
#            reachfile =  LandscapeModel.utils.ParameterList(fpath,
#                                                            fname,sep=",")
#            # extract data of the reach which is connected to the outlet
#            self.__copy_TimeseriesReaches(reachfile,
#                                            ro.source_solverunit,
#                                            ro.target_solverunit,
#                                            ro.source_storage,
#                                            ro.target_storage)
#
#    def __copy_TimeseriesReaches(self,reachfile,source_solverunit,
#                                 target_solverunit,source_storage,
#                                 target_storage) :  
#        # get data of specific reach of su
#        reach=reachfile.getbyAttribute3("key",source_storage)
#        
#        # create target path
#        fpath=os.path.join(self.__fpath,target_solverunit,"Timeseries")
#        fname=target_storage
#  
#
#        
#        # check if a file already exists
#        if os.path.exists(os.path.join(fpath,fname+".csv")): 
#            # if other timeseries already exists, sum up data
#            # open existing file
#            reach2 =  LandscapeModel.utils.ParameterList(fpath,fname,sep=",")
#            # sum up flow
#            flow_sum = [sum((i.flow,j.flow)) for i,j in zip(reach,reach2)]
#            # sum up loads
#            load = [sum((i.conc*i.volume,j.conc*j.volume)) for i,j in zip(reach,reach2)]
#            # calculate concentration
#            conc = [i/j for i,j in zip(load/flow_sum)]
#            print("\n\n###########",conc[:40])
#        else:
#            flow_sum = [i.flow for i in reach]
#            conc = [i.conc for i in reach]
#
#        # create string
#        header = "key,time,flow,conc"
#        records  = "\n".join([",".join((target_storage,r.time.strftime("%Y-%m-%dT%H:%M"),
#                                        str(flow),str(conc))) for r,flow in zip(reach,flow_sum,conc)])
#        s = header +"\n" + records
#        #write file       
#        self.__writeFile(s,os.path.join(fpath,fname+".csv"),mode="w")    


    
#    def __copyFiles(self,su,runorder,fpath):
#        """
#        Copy flow timeseries from upper to lower solverunit 
#        """
#        ro = runorder.getbyAttribute3("key",su)[0]
#        if ro.target_solverunit != "Outlet":
#            # open reach file
#            fpath = os.path.join(fpath,su)
#            fname = su + "_outlets"
#            outletfile =  LandscapeModel.utils.ParameterList(fpath,
#                                                            fname,sep=",")
#            # extract data of the reach which is connected to the outlet
#            self.__copy_TimeseriesReaches(outletfile,
#                                            ro.source_solverunit,
#                                            ro.target_solverunit,
#                                            ro.source_storage,
#                                            ro.target_storage)
#
#    def __copy_TimeseriesReaches(self,outletfile,source_solverunit,
#                                 target_solverunit,source_storage,
#                                 target_storage) :  
#        
#        # get data of specific reach of su
#        outlet=outletfile.getbyAttribute3("name","Outlet")
#        
#        # calculate flow into outlet per timestep
#        qOut = [0]+ [i.volume for i in outlet]
#        qOut = [(d1-d0)*24 for d0,d1 in zip(qOut[:-1],qOut[1:])]
#        qOut = [i.flow for i in outlet]
#        
#        
#        # create target path
#        fpath=os.path.join(self.__fpath,target_solverunit,"Timeseries")
#        fname=target_storage
#        
#        # check if a file already exists
#        if os.path.exists(os.path.join(fpath,fname+".csv")): 
#            # if other timeseries already exists, sum up data
#            
#            # open existing file
#            reach_target =  LandscapeModel.utils.ParameterList(fpath,fname,sep=",")
#            # sum up data
#   
#            flow_sum = [sum((i,j.flow_m3day)) for i,j in zip(qOut,reach_target)]
#
#        else:
#            flow_sum = [i for i in qOut]
#
#        conc_mgm3 = [ 0 for i in range(len(outlet))]
#
#        # create string
#        header = "key,time,flow_m3day,conc_mgm3"
#        records  = "\n".join([",".join((target_storage,r.time.strftime("%Y-%m-%dT%H:%M"),
#                                        str(flow),str(con))) for r,flow,con in zip(outlet,flow_sum,conc_mgm3)])
#        s = header +"\n" + records
#        #write file            
#        self.__writeFile(s,os.path.join(fpath,fname+".csv"),mode="w")    
#    
#    
#    
#    
#
    
    def plotMap(self,fontsize=8,withnames=True):
        """
        Plots a map of all solverunits
        """
        # make plot of solver units
        self.__message(s="plot solverunits")
        plot = LandscapeModel.utils.Plotting()   
        plot.SolverUnitsMap(self.__c,self.solverunits ,
                             title=self.__fname,
                             fpath=os.path.join(self.__fpath,self.__fname + ".png"),
                             withnames=withnames,
                             fontsize=fontsize)
    
    def __find_reaches(self,reach,ReachList):
        """
        Returns a list of reaches which are upstream of the specific reach. 
        Moreover, it indicates that if the specific reach is the outer end
        of a river branch, ie.e the source.
        
        Attributes:
        -----------
        reach (LandscapeModel.RiverSegment): River segment for which all
        upstream segments should be found.
        ReachList (LandscapeModel.utils.ParamterList): List with all
        reaches of catchment.
        
        Returns:
        --------
        endReach (boolean): Indicates if the reach is the source of a
        branch in the catchment and has no upstream storages.
        reaches (List): List of LandscapeModel.RiverSegments which are up-
        stream of the reach.
        """
        endReach = False
        reaches = [i for i in ReachList if i.downstream == reach.key]
        if len(reaches)<1:
            endReach=True
        return endReach,reaches
        
    def __find_cells(self,cell,CellList):
        """
        Returns a list of cells which are upstream of the specific reach. 
        Moreover, it indicates that if the specific cell is the outer end.
        
        Attributes:
        -----------
        cell (LandscapeModel.AgriculturalField): Cell for which all
        connected upstream cells should be found.
        CellList (LandscapeModel.utils.ParamterList): List with all
        cells of catchment.
        
        Returns:
        --------
        endCell (boolean): Indicates if the cell is the source in the 
        catchment and has no upstream storages.
        cells (List): List of LandscapeModel.AgriculturalFields which are 
        upstream of the cell.
        """
        endCell = False
        cells = [i for i in CellList if i.adjacent_field == cell.key]
        if len(cells)<1:
            endCell=True
        return endCell,cells

    def __find_neighbours_cells(self,target_reach):
        """
        Returns a list of cells which are upstream of the specific reach. 

        Attributes:
        -----------
        target_reach (landscapeMode.RiverSegment): River segment for which 
        all upstream cells should be found.
        
        Returns:
        --------
        cellList (LandscapeModel.utils.ParamterList): List with all pairs of
        target_reach (=key) and related upstream cells (=source).
        """
        CellList =self.__c.inpData.CellList
        # find all cells which are directly connected to the target reach
        source_cells = [i for i in CellList if i.reach == target_reach]
        # find all fields which are connected to the fields
        source_cells_tmp = source_cells
        cellList = []
        if len(source_cells_tmp)<1:
            cellList= []
        else:
            endCell = False
            while not endCell: 
                for cell in source_cells_tmp:
                    endCell,source_cells_tmp = self.__find_cells(cell,CellList)
                    source_cells+=source_cells_tmp
            records = [(target_reach,src.key) for src in source_cells]
            cellList = LandscapeModel.utils.ParameterList(header=["key","source"],records=records)
        return cellList

    def __find_neighbours_reaches(self,target_reach):
        """
        Returns a list of reaches which are upstream of the specific reach. 

        Attributes:
        -----------
        target_reach (LandscapeMode.RiverSegment): River segment for which 
        all upstream cells should be found.
        
        Returns:
        --------
        reachList (LandscapeModel.utils.ParamterList): List with all pairs of
        target_reach (=key) and related upstream reaches (=source).
        """
        ReachList = self.__c.inpData.ReachList
        if len([i for i in ReachList if i.downstream == target_reach])<1:
            return []
        # find all reachese
        source_reaches= [i for i in ReachList if i.downstream == target_reach]
        # find all fields which are connected to the fields
        source_reaches_tmp = source_reaches
        endReach = False
        reachList = []
        while not endReach: 
            for reach in source_reaches_tmp:
                endReach,source_reaches_tmp = self.__find_reaches(reach,ReachList)
                source_reaches+=source_reaches_tmp
        records=[(target_reach,src.key) for src in source_reaches]
        reachList =  LandscapeModel.utils.ParameterList(header=["key","source"],records=records)
        return reachList

    def __find_neighbours_all(self,target_reach):
        """
        Returns a list of cells which are upstream of the specific reach. 

        Attributes:
        -----------
        target_reach (landscapeMode.RiverSegment): River segment for which 
        all upstream cells should be found.
        
        Returns:
        --------
        srcList (LandscapeModel.utils.ParamterList): List with all pairs of
        target_reach (=key) and related upstream reaches/cells (=source).
        """

        # find all reachese
        reaches = self.__find_neighbours_reaches(target_reach)
        all_cells = self.__find_neighbours_cells(target_reach)

        for reach in reaches:
            cells = self.__find_neighbours_cells(reach.source)
            if len(cells)>0:
                all_cells += cells

        if len(all_cells)>0:
            all_cells = [i.source for i in all_cells]
            
            
        records=[(target_reach,i) for i in all_cells]
        srcList =  LandscapeModel.utils.ParameterList(header=["key","source"],records=records)
        return srcList

    def __findUpstream(self,solverunits,ReachList,CellList):
        """
        Find upstream storage for each cell or reach.
        
        Attributes:
        -----------
        solverunits (LandscapeModel.utils.ParamterList): List with all 
        solverunits (key,solverunitID)
        ReachList (LandscapeModel.utils.ParamterList): List of reaches.
        CellList (LandscapeModel.utils.ParamterList): List of cells.
        solverunits (key,solverunitID)
        """
        # set upstream storages
        for rec in solverunits:
            upstream=[]
            if rec.storagetype=="reach":
               upstream=self.__find_reaches(rec,ReachList)
            else:
               upstream=self. __find_cells(rec,CellList)
            if len(upstream[1])<1:
                rec.upstream="is_source"
            else:
                rec.upstream=upstream[1][0].key  
        return solverunits
    
    def __initialiseSolverUnits(self,ReachList,CellList):
        """
        Creates a starting list with solver units. Each solverunitID is
        initiated with 1.
        
        Attributes:
        -----------
        ReachList (LandscapeModel.utils.ParamterList): List of reaches.
        CellList (LandscapeModel.utils.ParamterList): List of cells.
        
        Returns:
        --------
        solverunits (LandscapeModel.utils.ParamterList): List with solverunits.
        """
        # set header
        header = ["key","solverunitID","storagetype","downstream", "upstream"]
        # get all reaches
        records=[(i.key,"su1","reach",i.downstream,"") for i in self.__c.inpData.ReachList]
        # get all cells
        records+=[(i.key,"su1","cell", i.reach,"") if i.reach!="None" else 
                  (i.key,"su1","cell", i.adjacent_field,"") for i in self.__c.inpData.CellList]
        # create list
        solverunits = LandscapeModel.utils.ParameterList(header=header ,
                                                           records=records)
        return solverunits
    
    def __separateCatchment(self,solverunits, nCells=9999):
        """
        Separates a catchment into solver units. 
        
        Attributes:
        -----------
        nCells (int): Minimum number of a cell sequence to form a solverunit.
        solverunits (LandscapeModel.utils.ParamterList): List with all 
        
        Returns:
        --------
        solverunits (LandscapeModel.utils.ParamterList): List with all 
        solverunits (key,solverunitID)
        target_reach (=key) and related upstream reaches/cells (=source).
        """
        # TODO find solution
        for i in solverunits:
            i.solverunitID = "su%.0f"%(1)

        
        # get list with branches
        branches = []
        for reach in self.__c.inpData.ReachList:
            reach_branches = [r for r in self.__c.inpData.ReachList 
                              if r.downstream == reach.key]
            if len(reach_branches) > 1:
                branches += reach_branches
                
        # find first and last reach of each branch
        branch_reaches = []
        for branch in branches:
            branch_upstream=[]
            next_branch = False
            nextreach = branch
            while not next_branch:
                endReach,reaches = self.__find_reaches(nextreach,
                                                       self.__c.inpData.ReachList)
                if len(reaches)>1 or endReach:
                    next_branch = True
                else:
                    branch_upstream.append(reaches[0])
                    nextreach = reaches[0]
            branch_reaches.append(branch_upstream)
            
        # set new solverids
        solverids = np.arange(0,len(branches))+2
        # set a counter for solverunits starting with one
        for i,branch in enumerate(branches):
            subcatch_id = solverids[i]
            
            # set solverunit of branch start
            solverunits[branch.key][0].solverunitID = "su%.0f"%(subcatch_id)
            
            # set solverunit of fields directly attached to start branch
            cells = self.__find_neighbours_cells(branch.key)
            if len(cells)>0:
                for cell in cells:
                    solverunits[cell.source][0].solverunitID = "su%.0f"%(subcatch_id) 

            # set solverunit of all reaches and cells of a branch
            for reach in branch_reaches[i]:

                # set reach solverid
                solverunits[reach.key][0].solverunitID = "su%.0f"%(subcatch_id)

                # find all cells
                cells = self.__find_neighbours_cells(reach.key)
                
                if len(cells)>0:
                    for cell in cells:
                        solverunits[cell.source][0].solverunitID = "su%.0f"%(subcatch_id) 


        #TODO: how to handle a sequence with cells without reach in catchment?
        #        # create a new solverunit if a sequence of fields has > nCells
        #        subcatch_id = solverids[-1]
        #        for i,branch in enumerate(branches):
        #                # set solverunit of all reaches and cells of a branch
        #                for reach in branch_reaches[i]:
        #                    
        #                    # find all cells
        #                    cells = self.__find_neighbours_cells(reach.key)
        #                    if len(cells)>nCells:
        #                        subcatch_id+=1
        #                        print(subcatch_id)
        #                        for cell in cells:
        #                            solverunits[cell.source][0].solverunitID = "su%.0f"%(subcatch_id) 
        return solverunits

    def __getOrder(self,runorderID,runorder):
        """
        Creates one run-order level a deletes items, which have a level
        
        Attributes:
        -----------
        runorderID (int): Current run order.
        runorder (LandscapeModel.utils.ParamterList): List with runorders.
        """
        source_solverunit = [i.source_solverunit for i in runorder if i.order==0]
        target_solverunit = [i.target_solverunit for i in runorder if i.order==0]
        for su in source_solverunit:
            source=[i for i in target_solverunit if i==su]
            if len(source)<1:
                runorder[su][0].order = runorderID
        return runorder

        
    def __createRunOrder(self,solverunits):
        """
        Creates a list with the run-order of solverunits.
        
        Attributes:
        -----------
        solverunits (LandscapeModel.utils.ParamterList): List with solverunits.
        
        Returns:
        --------
        runorder (LandscapeModel.utils.ParamterList): List with runorder.
        """
        # create header
        header = ["key","order","source_solverunit","target_solverunit","source_storage","target_storage"]
        recs = []
        for su in solverunits:
            print(su.key)
            if su.downstream != "Outlet":
                # get solverunit of downstream element
                su_downstream=solverunits[su.downstream][0]
                if su_downstream.solverunitID != su.solverunitID:
                    rec=(su.solverunitID,0,su.solverunitID, 
                         su_downstream.solverunitID,su.key,
                         su_downstream.key)
                    recs.append(rec)
            else:
                rec=(su.solverunitID,0,su.solverunitID, 
                         "Outlet",su.key,
                         "Outlet")
                recs.append(rec)
                
        # create list
        runorder = LandscapeModel.utils.ParameterList(header=header,records=recs)
        for rec in runorder:
            rec.order = 0
        # get run-order
        runorderID=1
        
        
        
        while not len(runorder.getbyAttribute3("order",0))<1:
            

            
            runorder=self.__getOrder(runorderID,runorder)
            runorderID+=1
            
            if runorderID>1000:
                return runorder
            
        return runorder

    def __makeRunList(self,solverunits):
        """
        Creates a new runlist containing all solverunits.
        
        Attributes:
        -----------
        solverunits (LandscapeModel.utils.ParamterList): List with all 
        solverunits (key,solverunitID)     
        """
        runs=[]
        # get unique solver units
        unique_solverunits = np.unique([i.solverunitID for i in solverunits])
        # iterate though all unique solver units and create runlist entry
        for sub in unique_solverunits:
            runL = copy.deepcopy(self.__c.modelrun)
            runL.key = sub
            runL.fpath = self.__fpath
            runL.catchment_separation = "FALSE"
            runs.append(runL.to_string(sep=","))
        # prepare header
        s= ",".join(self.__c.modelrun.__dict__.keys()) + "\n"
        s+= "\n".join(runs)
        self. __writeFile(s,os.path.join(self.__fpath,self.__fname+"_runlist.csv"))

    def __createProjects(self,solverunits):
        """
        Creates a subdirectory for each solverunit with related files from the
        catchment.
        
        Attributes:
        -----------
        solverunits (LandscapeModel.utils.ParamterList): List with all 
        solverunits (key,solverunitID)  
        """
        
        ext = "." + self.__c.database.ext 
        
        # get filelist from catchment
        inputfiles = self.__c.inpData.__dict__.keys()
        inputfiles = [i+".csv" for i in inputfiles if (i!="ReachList") and (i!="CellList") and (i!="CatchmentList")]
        # get unique solver units
        unique_solverunits = np.unique([i.solverunitID for i in solverunits]) 
        # iterate all solverunits
        for su in unique_solverunits:
               
            # create a subdirectory
            fpath=os.path.join(self.__fpath,su)
#            self.__message(s=fpath)
            if not os.path.isdir(fpath):
                os.mkdir(fpath)
            
            # copy each input file of catchment
            for file in inputfiles:
                src = os.path.join(self.__fpath_src,file)
                trg = os.path.join(self.__fpath,su,file)
                shutil.copyfile(src,trg)
           
            # create new reach list
            reachList = []
            for reach in [i.key for i in solverunits if i.solverunitID == su]:
                reach = [i for i in self.__c.inpData.ReachList if i.key == reach]
                reachList.append(reach)
            
            # find all reaches of solver units
            ReachList = [i.key for i in self.solverunits if (i.storagetype=="reach") and (i.solverunitID==su)]
            
            # get data for each reach from catchment
            ReachList =  [ self.__c.inpData.ReachList[i][0] for i in ReachList]
            
            # find all cells of solver units
            cells = [i.key for i in self.solverunits if (i.storagetype=="cell") and (i.solverunitID==su)]
            
            # get data for each ceell from catchment
            CellList =  [self.__c.inpData.CellList[i][0] for i in cells]
            
            # get reaches to create CatchmentList
            reaches = [i.key for i in solverunits if (i.storagetype=="reach") and (i.solverunitID==su)]
            
            # get downstream reaches
            downstreams=[self.__c.inpData.ReachList[i][0].downstream for i in reaches]
            
            # find reach with no downstream connection which needs outlet
            downstream=[d for d in downstreams if len([r for r in reaches if d==r])<1][0]
            catchmentList = copy.deepcopy(self.__c.inpData.CatchmentList)
            if not downstream == "Outlet":
                downstream = self.__c.inpData.ReachList[downstream][0]
                for i in catchmentList:
                    i.x = downstream.x
                    i.y = downstream.y
                    i.z = downstream.z
                # set outlet in ReachList
                reach = [r for r in ReachList if (r.downstream==downstream.key)][0]
                reach.downstream = "Outlet"

            # copy climate data
            for station in self.__c.inpData.ClimateList:
                src=os.path.join(self.__fpath_src,station.key+".csv")
                trg=os.path.join(self.__fpath,su,station.key+".csv")
                shutil.copyfile(src,trg)
            
            # write file CatchmentList.csv
            s= ",".join(self.__c.inpData.CatchmentList[0].__dict__.keys()) + "\n"
            s+= "\n".join([i.to_string(sep=",") for i in catchmentList])
            self. __writeFile(s,os.path.join(self.__fpath,su,"CatchmentList.csv"))
            
            # make ReachList.csv
            s= ",".join(self.__c.inpData.ReachList[0].__dict__.keys()) + "\n"
            s+= "\n".join( [ i.to_string(sep=",") for i in ReachList])
            self. __writeFile(s,os.path.join(self.__fpath,su,"ReachList.csv"))

            # create folder for time series#
            fpath = os.path.join(self.__fpath,su,"TimeSeries")
            if not os.path.isdir(fpath):
                os.mkdir(fpath)
     
            # copy spraydrift list
            if os.path.isfile(os.path.join(self.__fpath_src,"SprayDriftList.csv")):
                src=os.path.join(self.__fpath_src,"SprayDriftList.csv")
                trg=os.path.join(os.path.join(self.__fpath,su,"SprayDriftList.csv"))
                shutil.copyfile(src,trg)      
                
            # copy timeseries reaches
            if os.path.isdir(os.path.join(self.__fpath_src,"TimeSeries")):
                existing_ts = os.listdir(os.path.join(self.__fpath_src,"TimeSeries"))              
                for reach in ReachList:
                    if len([i for i in existing_ts if reach.key+ext ==i])>0:
                        src=os.path.join(self.__fpath_src,"TimeSeries",reach.key+ext)
                        trg=os.path.join(os.path.join(self.__fpath,su,"TimeSeries",reach.key+ext))
                        shutil.copyfile(src,trg)
   
            # make CellList.csv
            if self.__c.modelrun.runtype != "inStream":
                s= ",".join(self.__c.inpData.CellList[0].__dict__.keys()) + "\n"
                s+= "\n".join( [ i.to_string(sep=",") for i in CellList])
                self.__writeFile(s,os.path.join(self.__fpath,su,"CellList.csv"))
                
                # copy timeseries cells
                if os.path.isdir(os.path.join(self.__fpath_src,"TimeSeries")):
                    existing_ts = os.listdir(os.path.join(self.__fpath_src,"TimeSeries"))              
                    for cell in CellList:
                        if len([i for i in existing_ts if cell.key+ext==i])>0:
                            src=os.path.join(self.__fpath_src,"TimeSeries",cell.key+ext)
                            trg=os.path.join(os.path.join(self.__fpath,su,"TimeSeries",cell.key+ext))
                            shutil.copyfile(src,trg)                
            else:
                s="key,reach,reach_connection,adjacent_field,field_connection,x,y,z,latitude,gw_depth,residencetime_gw_river,residencetime_drainage_river,puddledepth,saturated_depth,evap_depth,area,deep_gw	deep_gw_rt,drainage_depth,drainage_suction_limit,drainage_t_ret,flowwdith_sw,slope_sw,nManning,hasDrainage,meteostation,rainstation,soil,plantmodel,unit_traveltime,soilwaterflux"
                self.__writeFile(s,os.path.join(self.__fpath,su,"CellList.csv"))
            

    def __writeFile(self,s,fpath,mode="w"):
        """
        Writes a textile.
        
        Attributes:
        -----------
        s (str): text to write into file.
        fpath (str): Target directory.
        mode (str): new file with 'w'; append with 'a'        
        """
        f=open(fpath,mode)
        f.write(s)
        f.close()
