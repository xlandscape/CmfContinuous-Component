# -*- coding: utf-8 -*-
"""
Created on Wed Feb 27 11:50:16 2019

@author: smh
"""
# python native
import os
from calendar import monthrange
from datetime import timedelta
import shutil
import copy

# other
import pandas as pd
import numpy as np
from .Parameter import ParameterList
from .Tools import TimeSeries,IO

# spatial operations with scipy
from scipy.spatial import Voronoi
from scipy.interpolate import griddata

# spatial operations with shapely
import shapely.ops
from shapely.geometry import Point,Polygon,LineString

# maths, data processing and plotting
import matplotlib.pyplot as plt



class Geometry():
    def __init__(self,name,point=None,geometry=None):
        """
        A generic class representing shapeply geometries.
        
        name(string):                                 Name of geometry.
        point(shapely.Point):                         Coordinates of geometry
        geometry(shapely.Polygon or shapely.LineStr): Geometry.
        """
        self.__name=name
        self.__point=point
        self.__geometry=geometry
        
    def __getName(self):
        """Return name"""
        return self.__name
    def __setName(self,value):
        self.__name = value
    name = property(__getName,__setName)

    def __getPoint(self):
        """Return point"""
        return self.__point
    def __setPoint(self,value):
        self.__point = value
    point = property(__getPoint,__setPoint)

    def __getGeometry(self):
        """Return point"""
        return self.__geometry
    def __setGeometry(self,value):
        self.__geometry = value
    geometry = property(__getGeometry,__setGeometry)


class CatchmentConnector():
    
    def __init__(self,fpath,simplify_connections,connection_type,
                 check_outer=True):
        

        
        """
        Creates connections between fields and river segments.
        
        The basis for the connections are Thiessen/Voroni polygons. The neighbours
        of a field are defined by the shared borders of the Voroni polygons. The 
        water flux goes in the direction of the nearest adjancent field with a
        loer altitude. If a river segment intersects a polygon the water flows 
        directly into the river segment.
        The user can use an automatic function to simplify the river network in
        iterative steps. This functions checks for each field and connection, if a
        field can be directly connected with the after next field without crossing
        the voroni polygons of other field in between.

          
        fpath(string): Path to project folder which contains the Fields.csv and
                       Reach.csv.
        simplify_connections(int): Number of iterations for simply functions
        connection_type(string): Type of connection, e.g. RO,GW and DR or any
                                 combination ("RO_GW",...)
        """
        print("################## "+ "read input data" +" ##################")
        # read fields and create voroni-polygons
        self.__fields = self.__read_fields(fpath)
        self.fields =  self.__fields
        # read raches and create river segemnts
        self.__reaches = self.__read_reaches(fpath)
        self.reaches = self.__reaches
        print("################## "+ "create connections" +" ##################")
        # get connections
        self.__connections = self.__connect(self.__fields,self.__reaches)
        
        # simplify connections
        self.__fields_simplified = []
        for i in range(simplify_connections):
            print("################## "+ str(i+1) +" ##################")
            self.__connections,fields_simplified = self.__simplify_connections()
            self.__fields_simplified += fields_simplified
        
        # save table
        print("################## "+ "save Fields.csv" +" ##################")
        self.__makeFieldTable(fpath,connection_type)

        if check_outer:
            print("################## "+ "check outer reaches and repair" +" ##################")
            self.__add_connection_outer_reaches(fpath)
    
    def __getconnections(self):
        """Get connections"""
        return  self.__connections
    Connections = property(__getconnections)
    
    def __read_fields(self,fpath): 
        
        fields = pd.read_csv(os.path.join(fpath,"CellList.csv"))
        points = np.array([[x,y] for x,y in zip(fields["x"],fields["y"])])
        elevations = np.array([z for z in fields["z"]])
        names = [f["key"] for i,f in fields.iterrows()]
        
        # get voroni polygons
        vor = Voronoi(points)
        regions, vertices = self.__voronoi_finite_polygons_2d(vor)

        # convert points and polys to shapely objects
        polys = [vertices[region] for region in regions]
        polys_shapely = [Polygon(poly) for poly in polys]
        points_shapely = [Point(p[0],p[1],z) for p,z in zip(points,elevations)]       
        
        #create field objects from points and polys
        fields=[]
        for name,point in zip(names,points_shapely):
            # find polygon
            for poly in polys_shapely:
                if poly.intersects(point):
                    point_poly = poly
            # create new field
            fields.append(Geometry(name,point,point_poly))
        return fields

    def __read_reaches(self,fpath):
        """
        Create a list of line esgments which represent the river network.
        
        Data requirement:
            - Reaches.csv
            - SubbasinList.csv
            
        Returns:
            List of shapely.geometry.LineString. 
        """
        # read input tables
        ReachList = pd.read_csv(os.path.join(fpath,"ReachList.csv"))
        SubbasinList = pd.read_csv(os.path.join(fpath,"CatchmentList.csv"))
        outlet = SubbasinList[SubbasinList["component"]=="Outlet"]
      
        # build reach segments on the basis of shapely LineString
        reaches = []
        for index,reach in ReachList.iterrows():
            # get coords
            x1 = reach["x"]
            y1 = reach["y"]
            if reach["downstream"] == "Outlet":
                x2 = outlet.x
                y2= outlet.y
            else:
                x2 = ReachList["x"][ReachList["key"]==reach["downstream"]]
                y2 = ReachList["y"][ReachList["key"]==reach["downstream"]]
            shapely_line = shapely.geometry.LineString([(x1,y1),(x2,y2)])        
            reaches.append(Geometry(reach["key"],Point(x1,y1,reach.z),shapely_line))
        
        return reaches


    def __add_connection_outer_reaches(self,fpath):
        # check if each outer reach has a cell connection
        ReachList = pd.read_csv(os.path.join(fpath,"ReachList.csv"))
        CellList = pd.read_csv(os.path.join(fpath,"CellList.csv"))
        CellList.set_index("key",inplace=True)
        
        # get all outside reaches
        reaches_outside = list(set(ReachList.key) - set(ReachList.downstream))
    
        # get all outside reaches with no cell connection
        reach_outside_no_cellcon = pd.DataFrame(list(set(reaches_outside) - set(CellList.reach)),columns=["reach"])
        reach_outside_no_cellcon = pd.merge(reach_outside_no_cellcon,ReachList,
                                            how="inner",
                                            left_on="reach",right_on="key")
    
        # find next cell
        for i in range(len(reach_outside_no_cellcon)):
            reach = reach_outside_no_cellcon.iloc[i]
           
            # get cells upslope
            cells = CellList[CellList.z>reach.z]
            
            # calcualte distance
            x1 = reach.x
            x2 = cells.x
            y1 = reach.y
            y2 = cells.y
            dist = ((x1 - x2[:, None])**2 + (y1 - y2[:, None])**2)**(1/2)
            mindist = np.argmin(dist)
            
            # change reach connection
            reachname = reach.reach
            cellname = cells.iloc[mindist].name            
            print(reachname,cellname)
            CellList.at[cells.iloc[mindist].name,"reach"] = reach.reach
            
            # update connection list
            cell_index = [i.name for i in self.fields].index(cellname)
            reach_index = [i.name for i in self.reaches].index(reachname)
            self.__connections[cell_index] = self.reaches[reach_index]
    
        # save CellList with new connections
        CellList.to_csv(os.path.join(fpath,"CellList.csv"))
        
    def __connect(self,fields,reaches):
        """
        Connects field with each other:
            1) A field is always connected to the reach in case of intersection
            2) Find neighbouring fields by Voroni polygons
            3) Check if decreasing slope
            4) Calculate distance to each other
            5) Select nearest downslope neighbouring field
            6) Check if the linear connection between two fields intersects a 
               a reach segment.
            7) If there is no connection the field is connected with the next
               downhill reach
        TODO:
        Other selection methods could be related to slope, shared line
        segment and other wegithign factors.
        
        fields([Field]): List with field informations
        
        Returns([Fields])
        List with field connections
        """
        # find next field for each polygon
        fields_connections = []
        for f_source in fields:
            connections = []
            nextgeometry = None
            # 1) A field is always connected to the reach in case of intersection
            for reach in reaches:
                if f_source.geometry.intersects(reach.geometry):
                    connections.append(reach)
            # get nearest reach
            if len(connections)>0:
                # get nearest reach
                distance_reaches = [[ np.sqrt((con.point.x-f_source.point.x)**2 +(con.point.y-f_source.point.y)**2) for con in connections]]
                nextgeometry =  connections[np.argmin(distance_reaches)]
            
            # 2) Find neighbouring fields by Voroni polygons
            else:
                for f_target in fields:
                    if f_source.geometry.touches(f_target.geometry):
                        connections.append(f_target)
    
                # 3) Check if decreasing slope  
                connections = [con for con in connections if con.point.z<f_source.point.z]
    
                # 4) Calculate distance to each other
                distances = [ np.sqrt((con.point.x-f_source.point.x)**2 +(con.point.y-f_source.point.y)**2) for con in connections]
                               
                if len(connections)>0:

                    # 5) Select nearest downslope neighbouring field
                    nextgeometry =  connections[np.argmin(distances)]
                   
                    # 6) Check if the linear connection between two fields intersects a reach segment.
                    
                    # create a line segment between both fields
                    field_to_field = LineString([(f_source.point.x,f_source.point.y),(nextgeometry.point.x,nextgeometry.point.y)])
                    
                    # intersect field_to_field with reaches
                    field_to_field_connection = [reach for reach in reaches if field_to_field.intersects(reach.geometry)]
                    
                    # get nearest reach
                    if len(field_to_field_connection)>0:
                        # get nearest reach
                        distance_reaches = [ np.sqrt((con.point.x-f_source.point.x)**2 +(con.point.y-f_source.point.y)**2) for con in field_to_field_connection]
                        nextgeometry =  field_to_field_connection[np.argmin(distance_reaches)]
                else:
                    
                    # 7) If there is no connection the field is connected with the next downhill reach
                    
                    # get downhill reaches
                    reach_downhill = [reach for reach in reaches if reach.point.z < f_source.point.z]
                    # find nearest downhill reach
                    distances = [ np.sqrt((reach.point.x-f_source.point.x)**2 +(reach.point.y-f_source.point.y)**2) for reach in reach_downhill]
                    nextgeometry =  reach_downhill[np.argmin(distances)]
                    
                    # 8) Check step  7) for other fills in between which are downslope
                    
                    # create a line segment between field and reach
                    field_to_reach = LineString([(f_source.point.x,f_source.point.y),(nextgeometry.point.x,nextgeometry.point.y)])
                    
                    # intersect field_to_field with reaches
                    
                    # get downhill fields
                    field_downhill = [field for field in fields if field.point.z < f_source.point.z]
                    field_to_reach_connection = [field for field in field_downhill if field_to_reach.intersects(field.geometry)]

                    
                    if len(field_to_reach_connection)>0:
                        # get nearest reach
                        distance_reaches = [ np.sqrt((con.point.x-f_source.point.x)**2 +(con.point.y-f_source.point.y)**2) for con in field_to_reach_connection]
                        nextgeometry =  field_to_reach_connection[np.argmin(distance_reaches)]
   
            # add connection
            fields_connections.append(nextgeometry)
            
        return fields_connections        

    def __simplify_connections(self):
        """
        Simplify flow connections, i.e. check if a field can be connected with
        the after next downhill geometry.     
        """
        connections_simplified = []
        
        
        fields_simplified = []
        
        # get field names
        field_names = [field.name for field in self.__fields]

        # loop through all fields
        for field,con in zip(self.__fields,self.__connections):    
            
            # the new con equals the old one
            con_new = con
            
            #or ...
            
            # get the next geometry (only in case of a field)          
            if con.name.find("f")>=0:

                connection_next_field = self.__connections[field_names.index(con.name)]

                # if the connection of the next field is down slope the actual field
                # skip the actual connection
                if field.point.z > connection_next_field.point.z:
                    
                     # check if the connection does not intersects other fields
                     line = shapely.geometry.LineString([(field.point.x,field.point.y),(connection_next_field.point.x,connection_next_field.point.y)])        
                     fields_intersected  =[field.name for field in self.__fields if field.geometry.intersects(line)]
                     #remove current field and connection_next_field
                     fields_intersected.remove(field.name)
                     if connection_next_field.name.find("f")>=0:
                         fields_intersected.remove(connection_next_field.name)
                     
                     
                     if not len(fields_intersected)>0:
                        print("simplified",field.name)
                        con_new = connection_next_field
                        
                        fields_simplified.append(field.name)
            
            connections_simplified.append(con_new)
            
            
        return connections_simplified,fields_simplified

    def __voronoi_finite_polygons_2d(self,vor, radius=None):
        """
        Reconstruct infinite voronoi regions in a 2D diagram to finite
        regions.
    
        Parameters
        ----------
        vor : Voronoi
            Input diagram
        radius : float, optional
            Distance to 'points at infinity'.
    
        Returns
        -------
        regions : list of tuples
            Indices of vertices in each revised Voronoi regions.
        vertices : list of tuples
            Coordinates for revised Voronoi vertices. Same as coordinates
            of input vertices, with 'points at infinity' appended to the
            end.
            
        https://stackoverflow.com/questions/34968838/python-finite-boundary-voronoi-cells
    
    
        """
    
        if vor.points.shape[1] != 2:
            raise ValueError("Requires 2D input")
    
        new_regions = []
        new_vertices = vor.vertices.tolist()
    
        center = vor.points.mean(axis=0)
        if radius is None:
            radius = vor.points.ptp().max()
    
        # Construct a map containing all ridges for a given point
        all_ridges = {}
        for (p1, p2), (v1, v2) in zip(vor.ridge_points, vor.ridge_vertices):
            all_ridges.setdefault(p1, []).append((p2, v1, v2))
            all_ridges.setdefault(p2, []).append((p1, v1, v2))
    
        # Reconstruct infinite regions
        for p1, region in enumerate(vor.point_region):
            vertices = vor.regions[region]
    
            if all(v >= 0 for v in vertices):
                # finite region
                new_regions.append(vertices)
                continue
    
            # reconstruct a non-finite region
            ridges = all_ridges[p1]
            new_region = [v for v in vertices if v >= 0]
    
            for p2, v1, v2 in ridges:
                if v2 < 0:
                    v1, v2 = v2, v1
                if v1 >= 0:
                    # finite ridge: already in the region
                    continue
    
                # Compute the missing endpoint of an infinite ridge
    
                t = vor.points[p2] - vor.points[p1] # tangent
                t /= np.linalg.norm(t)
                n = np.array([-t[1], t[0]])  # normal
    
                midpoint = vor.points[[p1, p2]].mean(axis=0)
                direction = np.sign(np.dot(midpoint - center, n)) * n
                far_point = vor.vertices[v2] + direction * radius
    
                new_region.append(len(new_vertices))
                new_vertices.append(far_point.tolist())
    
            # sort region counterclockwise
            vs = np.asarray([new_vertices[v] for v in new_region])
            c = vs.mean(axis=0)
            angles = np.arctan2(vs[:,1] - c[1], vs[:,0] - c[0])
            new_region = np.array(new_region)[np.argsort(angles)]
    
            # finish
            new_regions.append(new_region.tolist())
    
        return new_regions, np.asarray(new_vertices)

    def __makeFieldTable(self,fpath,connection_type = "RO_GW"):
        """
        """
        
        
        
        # open original field table
        fields = pd.read_csv(os.path.join(fpath,"CellList.csv"))
        fields.set_index("key",inplace=True)
        
        # create a copy of the field table
        fields.to_csv(os.path.join(fpath,"CellList_original.csv"))
        fields.reset_index(inplace=True)
        
        # get dictionary of connection
        conDict = self.asDict()        

        # set connections
        fields["reach"] = fields["key"].map(conDict)
        fields["adjacent_field"] = fields["key"].map(conDict)
        fields["reach"] = fields["reach"].apply(lambda x: 'None' if not x.find("r")>-1 else x)
        fields["adjacent_field"] = fields["adjacent_field"].apply(lambda x: 'None' if not x.find("f")>-1 else x)
        
        # set connection type
        fields["reach_connection"] = fields["reach"].apply(lambda x: 'None' if not x.find("r")>-1 else connection_type)
        fields["field_connection"] = fields["adjacent_field"].apply(lambda x: 'None' if not x.find("f")>-1 else connection_type)

        # save data table
        fields.set_index("key",inplace=True)
        fields.to_csv(os.path.join(fpath,"CellList.csv"))

    def asDict(self):
        """
        """
        return dict(zip([field.name  if not field == None else "None" for field in self.__fields],[con.name if not con == None else "None" for con in self.__connections]))
     
    def makePlot(self,fname,resX=100,resY=100,plotVoroni=False,
                 plotElevation=True,plot_simplified=False,fontsize=8,
                 markersize=1):

        reaches = self.__reaches
        fields = self.__fields
        connections = self.__connections
        
        # make figure
        fig = plt.figure(figsize=(12,12))
        ax = fig.add_subplot(111)
        
        # plot line segments
        for reach in reaches:
            ax.plot(reach.geometry.xy[0],reach.geometry.xy[1],linewidth=1,alpha=1,color="lightblue")
            ax.text(reach.point.x,reach.point.y, reach.name,
                    verticalalignment='bottom', horizontalalignment='left',
                    color='0.5', fontsize=fontsize)
        
        # plot fields and voroni polygons
        for field in fields:
            if plotVoroni:
                ax.fill(*field.geometry.boundary.xy, alpha=0.4)
            ax.plot(field.point.x,field.point.y, color="k",marker="o",linewidth=0,markersize=markersize)
            ax.text(field.point.x,field.point.y, field.name,
                    verticalalignment='bottom', horizontalalignment='left',
                    color='k', fontsize=fontsize)
       
        # plot connections  
        for field,con in zip(fields,connections):
            if con != None:
                
                if not plot_simplified:
                
                    ax.plot([field.point.x,con.point.x],[field.point.y,con.point.y],"k--")
                else:
                    
                    if len([f for f in self.__fields_simplified if f==field.name])>0:
                        ax.plot([field.point.x,con.point.x],[field.point.y,con.point.y],"r--")
                    else:
                        ax.plot([field.point.x,con.point.x],[field.point.y,con.point.y],"k--")
                        
                    
        # plot elevation
        x = [f.point.x for f in fields]
        y = [f.point.y for f in fields]
        z = [f.point.z for f in fields]
        ax.set_xlim(min(x),max(x))
        ax.set_ylim(min(y),max(y))
        if plotElevation and not plotVoroni:
            # plot elevation
            xi = np.linspace(min(x), max(x), resX)
            yi = np.linspace(min(y), max(y), resY)
            zi = griddata((x, y), z, (xi[None,:], yi[:,None]),method="cubic")
            hdl = ax.contourf(xi,yi,zi,15,cmap=plt.cm.gist_earth,alpha=.9)
            datco = [0.65, 0.15, 0.3,0.05]
            cbar_ax = fig.add_axes(datco)
            cb1 = plt.colorbar(hdl, cax=cbar_ax, orientation='horizontal')
            cb1.set_label("Altitude (m)")
        plt.tight_layout()
        fig.savefig(fname,dpi=300)


class AreaYieldCatchment(TimeSeries,IO):
    
    def __init__(self,fpath,
                 key,
                 frunlist,
                 filetype = "csv",
                 time_format="%Y-%m-%dT%H:%M"):
        """
        """
        
        # implement parent classes
        TimeSeries.__init__(self)
        IO.__init__(self)
        
        # set catchment project
        self.fpath = os.path.join(fpath,key)
        self.fname = key
        self.filetype = filetype
        self.time_format = time_format
        self.frunlist = frunlist
        
        # open modlerunlist
        runList = ParameterList(fpath,frunlist,",")
        self.modelrun =  [i for i in runList if i.key  == key][0]
        
        
        # load cell list
        self.CellList = pd.read_csv(os.path.join(self.fpath,"CellList.csv"))
        self.CellList.set_index("key",inplace=True)
        
        # load observed data
        self.observation = pd.read_csv(os.path.join(self.fpath,"observation.csv"))
        self.observation ["time"]=pd.to_datetime(self.observation ["time"],
                         format=self.time_format)
        self.observation.set_index("time",inplace=True)
        
        # set format and header fo hdf5-file
        self.fmt = ['U10', 'U16', 'f8', 'f8']
        self.header =  ['key', 'time', 'flow', 'conc']
        self.dtype = [('key', 'U10'), ('time', 'U16'), ('flow', 'f8'), ('conc', 'f8')]

    def create_timeseries(self,resample_rule,resample_type):
        """
        """
    
        # get catchment area per reach
        cellareas = self.get_Catchment_per_Reach(self.CellList)
        
        # get start and end
        start = self.observation.index[0]
        end = self.observation.index[-1]

        # check for missing values
        dates = pd.Index(pd.date_range(start=start,
                                       end=end,freq="1D"))
        print("Missing values:\n",self.observation.index.difference(dates))
        
        # create sudirectory if needed
        trg_fpath = os.path.join(self.fpath,"Timeseries")
        if not os.path.exists(trg_fpath):
            os.mkdir(trg_fpath)
        
        # resample data
        data_resampled = self.resample(self.observation,resample_rule,resample_type)
        
        # select time window
        data_resampled = self.select_timeperiod(data_resampled,start,
                                                               end,
                                                               self.time_format)
               
        # calc area yield catchment and store files into TimeSeries folder
        self.calc_areayieldcatchment(data_resampled,cellareas,
                                trg_fpath,self.fmt,self.dtype,
                                self.header,self.filetype)

    def create_timeseries_scenarios(self,resample_rule,resample_type):
        """
        """

        # get catchment area per reach
        cellareas = self.get_Catchment_per_Reach(self.CellList)

        # get scenarios
        scenarios = self.get_scenario(self.observation)
        
        # save
        runs=[]
        for sce in ["dry","wet","medium"]:        
            data = pd.DataFrame(scenarios[sce]).rename(columns={sce:"flow"})
            
            # create a new project folder and copy files
            trg_fpath = os.path.join(self.fpath+"_"+sce)
            if not os.path.exists(trg_fpath):
                os.mkdir(trg_fpath)
            files = [i for i in os.listdir(self.fpath) if i!="Timeseries"]
            print("copy source project to ",trg_fpath)
            for file in files:
                shutil.copy(os.path.join(self.fpath,file),os.path.join(trg_fpath,file))



            # add files to runlist
            runL = copy.deepcopy(self.modelrun)
            runL.key = self.modelrun.key + "_" + sce
            runL.begin = "1900-01-01T00:00"
            runL.end = "1900-12-31T23:00"
            runs.append(runL.to_string(sep=","))

#
            # create sudirectory if needed
            trg_fpath = os.path.join(trg_fpath,"Timeseries")
            if not os.path.exists(trg_fpath):
                os.mkdir(trg_fpath)
                
            # resample data
            data_resampled = self.resample(data,resample_rule,resample_type).iloc[1:]#TODO: check
    
           # save scenario
            data_resampled["key"]  = np.unique(self.observation["key"])[0]
            data_resampled.to_csv(os.path.join(os.path.join(self.fpath+"_"+sce),"observation.csv"))
    
    
            # calc area yield catchment and store files into TimeSeries folder
            self.calc_areayieldcatchment(data_resampled,cellareas,
                                    trg_fpath,self.fmt,self.dtype,
                                    self.header,self.filetype) 
        # add to runlist
        s= "\n".join(runs)
        print(s)
        fpath = os.path.join(self.modelrun.fpath,self.frunlist+".csv")
        self.writeTextFile(s,fpath,"a")

    def get_Catchment_per_Reach(self,CellList):
        """
        In order to derive the catchment area which is related to one reach,
        the field areas of all fields attached in first, second ,... order to
        the reach must be summarized.
        """
        # get cells per reach
        conFieldReach = []
        
        for key in self.CellList.index.values:
            cell = self.CellList.loc[key]
            foundreach = False
            actCell = cell
            while not foundreach: 

                if actCell.reach != "None":
                    conFieldReach.append([actCell.reach,key,cell.area])
                    foundreach = True 
                else:
                    actCell = CellList.loc[actCell.adjacent_field]      #[i for i in CellList if i.key == actCell.adjacent_field][0]
        return ParameterList(header=["key","cell","area"],records=conFieldReach)
    
    def calc_areayieldcatchment(self,data,cellareas,
                                trg_fpath,fmt,dtype,
                                header,filetype="csv"):
        """
        Calculates area yield catchment flow per river segment.
        """
        
        # calcualte specific discharge per catchment area
        area =sum([i.area for i in cellareas])
        

        # get time as string
        time_as_string = [i.strftime(self.time_format) for i in data.index]
        
        # create a file for each reach
        print("write timeseries",trg_fpath)
        for reach in np.unique([i.key for i in cellareas]):
            reach = str(reach)
            
             # create new dataframe for reach and calculate total inflow into reach
            cell_area = sum([i.area for i in cellareas.getbyAttribute3("key",reach)])
            table = np.empty([len(data)],dtype=dtype)
            table["key"] = reach 
            table["time"] = time_as_string 
            table["flow"] = data["flow"] / area * cell_area 
            table["conc"] = 0 
            # save hdf
            if filetype=="csv":
                self.save_csv(os.path.join(trg_fpath,reach+".csv"),table,fmt,header)
            elif filetype=="hdf":
                self.write_numpy_to_hdf(os.path.join(trg_fpath,reach+".hdf"),table,fmt,header,"reaches")
    
    def get_scenario(self,observed):
        """
        Cacluates a standard hydrological year for a give ntime series for
        dry (10th percentile), normal (50th percentile) and wet (90th percentile)
        conditions.
        
        Returns pandas dataframe.
        """
        scenarios = []
        # create dry,wet and normal scenario
        for month in range(1,13,1):
            for day in range(1,monthrange(1900,month)[1]+1,1):
                # get data for month / day combination
                flow = observed[(observed.index.day==day) & (observed.index.month==month)].flow
                # calculate percentiles
                dry = flow.quantile(0.1)
                medium = flow.quantile(0.5)
                wet = flow.quantile(0.9)
                
                if day==31 and month==12:
                    date = pd.Timestamp(year=1900,month=month,day=day,hour=23)
                else:
                    date = pd.Timestamp(year=1900,month=month,day=day)   
                
                scenarios.append((date,dry,medium,wet))
        # create date frame
        scenarios = pd.DataFrame(scenarios,columns=["time","dry","medium","wet"])
        scenarios.set_index("time",inplace=True)
        # plot scenarios
        scenarios.plot()       
        return scenarios            