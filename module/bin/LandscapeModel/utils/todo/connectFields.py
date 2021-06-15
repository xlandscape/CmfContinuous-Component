# -*- coding: utf-8 -*-
"""
Created on Fri May 18 09:15:54 2018

@author: smh
"""

# spatial operations with scipy
from scipy.spatial import Voronoi
from scipy.interpolate import griddata

# spatial operations with shapely
import shapely.ops
from shapely.geometry import Point,Polygon,LineString

# maths, data processing and plotting
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# general
import os


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


class FieldConnector():
    
    def __init__(self,fpath,simplify_connections,connection_type):
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
        

     
    def makePlot(self,fname,resX=100,resY=100,plotVoroni=False,plotElevation=True,plot_simplified=False):

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
                    color='0.5', fontsize=8)
        
        # plot fields and voroni polygons
        for field in fields:
            if plotVoroni:
                ax.fill(*field.geometry.boundary.xy, alpha=0.4)
            ax.plot(field.point.x,field.point.y, 'ko')
            ax.text(field.point.x,field.point.y, field.name,
                    verticalalignment='bottom', horizontalalignment='left',
                    color='k', fontsize=8)
       
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
        if plotElevation:
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
                

################################################################################
##  Velm



fieldcon = FieldConnector(fpath="c:/LandscapeModel/CatchmentModel/projects/Velm/",simplify_connections=4,connection_type="RO_GW")
fieldcon.makePlot("Velm_dem_simplyfied2.png",resX=100,resY=100,plotVoroni=False,plotElevation=True,plot_simplified=True)
fieldcon.makePlot("Velm_voroni_simplyfied2.png",resX=100,resY=100,plotVoroni=True,plotElevation=False,plot_simplified=True)





#FieldList = pd.read_csv(os.path.join(fpath,"Fields.csv"))
#
#ReachList = pd.read_csv(os.path.join(fpath,"Reaches.csv"))

#for i,field in FieldList.iterrows():
#    
#    # find connection
#    if field["reach"]!="None":
#        con = ReachList[ReachList["name"] == field["reach"]]
#    else:
#        con = FieldList[FieldList["name"] == field["adjacent_field"]]
#
#    if field["z"] < con["z"].values[0]:
#        print(field["name"],con["name"].values[0],field["z"],con["z"].values[0])
#

## check field list with reaches
#
#
#def repair_ReachList(fpath):
#    """
#    """
#    ReachList = readCSV(os.path.join(fpath,"Reaches.csv"),
#                         [('name', 'U100'), ('x', '<f8'), ('y', '<f8'), 
#               ('z', '<f8'),('downstream', 'U100'),
#               ('initial_depth', '<f8'),('manning_n', '<f8'), ('bankslope', '<f8')])
#
#    #make copy of original file
#    writeCSV(ReachList,os.path.join(fpath,"Reaches_copy_original.csv"),delimiter=",")
#    # adjust elevation in reach list until valid stream network
#    correct = False
#    counter=0
#    while not correct:
#        counter+=1
#        reaches_slope = []
#        for r,reach in enumerate(ReachList):
#            z1 = reach["z"]
#            if not reach["downstream"] == "Outlet":
#                reach_downstream = ReachList[ReachList["name"]==reach["downstream"]][0]
#                z2 = reach_downstream["z"] 
#                # if not valid adjust elevation of actual and donwstream reach
#                if not (z1-z2)>0:
#                    reaches_slope.append(reach["name"]+ " z=%.4fm"%(z1)+ " --> " +reach["downstream"]+" z=%.4fm"%(z2))
#                    mid = (z1+z2) / 2
#                    ReachList[list(ReachList["name"]).index(reach["downstream"])]["z"] =mid-0.01
#                    ReachList[r]["z"] =  mid+0.01
#        if not len(reaches_slope)>0:
#            correct=True
#        print(counter)
#    #save adjusted reach list
#    writeCSV(ReachList,os.path.join(fpath,"Reaches.csv"),delimiter=",")
#





























