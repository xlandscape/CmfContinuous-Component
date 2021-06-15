# -*- coding: utf-8 -*-
"""
Created on Thu Mar 15 14:30:37 2018

@author: smh
"""
import matplotlib as mpl
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import matplotlib.patches as patches
from scipy import spatial
from numpy import random,argsort,sqrt

def makeFigure(size=[0.05,0.05,0.8,0.8]):
    fig = plt.figure(figsize=(10, 10))
    ax = fig.add_axes(size)#,projection='3d') # x,y, lenght, height
    return ax
    
def calc_distance_maxtrix(x1,y1,x2,y2):
    x_distance = (x2-x1[:,None])**2
    y_distance = (y2-y1[:,None])**2
    return np.sqrt(x_distance+y_distance)

def calc_elevation_matrix(z1,z2):
    return (z2-z1[:,None])

def get_index_of_next(slope_with_conds):
    # makes everything nan to start with
    tmp = np.zeros(slope_with_conds.shape[0])+np.nan 
    # finds the indices where the entire column would be nan, so the nanargmin would raise an error
    d0 = np.nanmin(slope_with_conds, axis=1) 
    # on the indices where we do not have a nan-column, get the right index with nanargmin, and than put the right value in those points
    tmp[~np.isnan(d0)] = np.nanargmin(slope_with_conds[~np.isnan(d0),:], axis=1)
    return tmp

def simple_idw(x, y, z, xi, yi):
    dist = distance_matrix(x,y, xi,yi)

    # In IDW, weights are 1 / distance
    weights = 1.0 / dist

    # Make weights sum to one
    weights /= weights.sum(axis=0)

    # Multiply the weights for each interpolated point by all observed Z-values
    zi = np.dot(weights.T, z)
    return zi

def distance_matrix(x0, y0, x1, y1):
    obs = np.vstack((x0, y0)).T
    interp = np.vstack((x1, y1)).T

    # Make a distance matrix between pairwise observations
    # Note: from <http://stackoverflow.com/questions/1871536>
    # (Yay for ufuncs!)
    d0 = np.subtract.outer(obs[:,0], interp[:,0])
    d1 = np.subtract.outer(obs[:,1], interp[:,1])

    return np.hypot(d0, d1)

def knn_search(x, D, K):
     """ find K nearest neighbours of data among D """
     ndata = D.shape[1]
     K = K if K < ndata else ndata
     # euclidean distances from the other points
     sqd = sqrt(((D - x[:,:ndata])**2).sum(axis=0))
     idx = argsort(sqd) # sorting
     # return the indexes of K nearest neighbours
     return idx[:K]

def refine_zvalue(point,dem,k=4):

    # knn_search test
    data = np.array([dem["x"],dem["y"]]) # random dataset
    x = np.array([[point["x"]],[point["y"]]]) # query point
    
    # performing the search
    neig_idx = knn_search(x,data,k)
    
#    # plotting the data and the input point
#    plt.plot(data[0,:],data[1,:],'ob',x[0,0],x[1,0],'or')
#    # highlighting the neighbours
#    plt.plot(data[0,neig_idx],data[1,neig_idx],'o',
#      markerfacecolor='None',markersize=15,markeredgewidth=1)
#      
#    plt.xlim(point["x"]-100,point["x"]+100)
#    plt.ylim(point["y"]-100,point["y"]+100)
#    plt.show()

    #calc neew z value from 4 neighbours
    zval=simple_idw(dem["x"][neig_idx], dem["y"][neig_idx], dem["z"][neig_idx], point["x"], point["y"])
    return zval


################################################################################
##create dummy river segments
#
#xvals = [1,2,3,1,2,3,3,3,4,4,4,3,2,2,2]
#yvals = [1,1,1,2,2,2,3,4,4,5,6,6,6,5,4.5]
#zvals = [7,6,5.5,7,6,5,4,3,2,1.5,1,0.8,0.5,0.3,0.1]
#names = ["r%i"%(i+1) for i in range(len(xvals))]
#test = np.array([(n,x,y,z,"") for n,x,y,z in zip(names,xvals,yvals,zvals)],dtype = [("name","<S10"),("x",float),("y",float),("z",float),("next","<S10")])


################################################################################
## load final data
#dtype=[('name', '<S10'), ('x', '<f8'), ('y', '<f8'),('z', '<f8'), ('points_id', '<S10'), ('points_x', '<f8'), ('points_y', '<f8'), ('next', '<S10')]
#test = np.genfromtxt("c:/0_work/bcs_catchmentmodelling/model_runs/final/river.csv",delimiter=",",names=True,dtype=dtype)
#
#
################################################################################
## make inverse distance interpolation of river cells with DEM 
#
##load dem
#dtype=[('x', '<f8'), ('y', '<f8'), ('z', '<f8')]
#dem = np.genfromtxt(r"c:\0_work\bcs_catchmentmodelling\model_runs\z_river\dem_GKb.csv",delimiter=",",names=True,dtype=dtype)



point = test[0]
ref_zvals = []
for point in test:
    ref_zval = refine_zvalue(point,dem,k=4)
    ref_zvals.append(ref_zval)
    

#
## knn_search test
#data = random.rand(2,200) # random dataset
#x = random.rand(2,1) # query point
#
## performing the search
#neig_idx = knn_search(x,data,10)
#
## plotting the data and the input point
#plt.plot(data[0,:],data[1,:],'ob',x[0,0],x[1,0],'or')
## highlighting the neighbours
#plt.plot(data[0,neig_idx],data[1,neig_idx],'o',
#  markerfacecolor='None',markersize=15,markeredgewidth=1)
#plt.show()
#






#
###laod data in bounding box
#xmin=41800
#xmax=41900
#ymin=165600
#ymax=16600
#test = test[(test["x"]>xmin)&(test["x"]<xmax)&(test["y"]>ymin)]

#
################################################################################
## set grid spacing 
#gridspacing = 1.1
#
################################################################################
##make plot of river segments
#ax = makeFigure()
#ax.plot(test["x"],test["y"],color="lightblue",marker="o",linestyle="",alpha=1,markersize=5,markeredgecolor="None")
#ax.set_xlim(0,10)
#ax.set_ylim(0,10)
#ax.grid(True)
#ax.set_xlabel("x")
#ax.set_ylabel("y")
#ax.set_ylabel("z")
#for val in test:
#    ax.text(val["x"]+0.1,val["y"],"%.1fm"%(val["z"]), fontsize="small",horizontalalignment='left', fontweight="bold")
#
#
#
################################################################################
## calcualte next river segment for all segments
#
##calcualte distance between points
#distance = calc_distance_maxtrix(test["x"],test["y"],test["x"],test["y"])
##calcute elevation difference betwee npoints
#elevation = calc_elevation_matrix(test["z"],test["z"])
##calcualte slope
#slope = elevation / distance
## set conditions
#conds = (distance > 0)  & (distance < gridspacing)  & (slope < 0)
##apply conditions to slopes
#slope_with_conds = np.where(conds,slope,np.nan)
##get index of next river element
#index_next_river_segment = get_index_of_next(slope_with_conds)
##get name of next segment without nan
#index_next_river_segment_nonan = index_next_river_segment[~np.isnan(index_next_river_segment)].astype(int)
##set next river segment
#test["next"][~np.isnan(index_next_river_segment)] = test["name"][index_next_river_segment_nonan]       
#   
#
#def calc_angle_maxtrix(self,x1,y1,x2,y2):
#    tmp_x = x2-x1[:,None]
#    tmp_y = y2-y1[:,None]
#    radians = np.arctan2(tmp_x,tmp_y)
#    return angle  
#
################################################################################
## plot connections
#for reach in test: 
#    if not reach["next"] == b"":
#        #get coordiantes
#        x1 = reach["x"]
#        y1 = reach["y"]
#        x2 = test["x"][test["name"] == reach["next"]][0]
#        y2 = test["y"][test["name"] == reach["next"]][0]
#        
#        #plot line connection
#        ax.plot([x1,x2],[y1,y2],color="lightblue",linewidth=2,alpha=1)
#        # plot angle in radians between both points
#        
#        
#        if (x1-x2)<0 and (y1-y2) == 0 :
#            radians = np.arctan2((x1-x2),(y1-y2))
#        elif (x1-x2)==0 and (y1-y2) < 0 :
#            radians = np.arctan2((x2-x1),(y2-y1))
#        elif (x1-x2) > 0 and (y1-y2) == 0 :
#            radians = np.arctan2((x1-x2),(y2-y1))
#        elif (x1-x2)==0 and (y1-y2) > 0 :
#            radians = np.arctan2((x1-x2),(y2-y1))
#        
#        print(reach["name"],reach["next"],(x1-x2),(y1-y2),radians)
#
#        
#        # plot arrow in flow direction
#        triangle = patches.RegularPolygon(((x1+x2)/2, (y1+y2)/2),  3, 0.1,color="lightblue",orientation=radians)
#        ax.add_patch(triangle)
#    
#    

###############################################################################
# print results          
                            
##print results
#print("\n\ndistance")
#print(distance)
#print("\n\nslope")
#print(slope)
#print("\n\nslope_with_conds")
#print(slope_with_conds)
##print("\n\nslope_min")
##print(slope_min)
#print("\n\n index_next_river_segment")
#print(index_next_river_segment)
#print("\n\n next segment")
#print(test["name"][index_next_river_segment_nonan])









    
    
