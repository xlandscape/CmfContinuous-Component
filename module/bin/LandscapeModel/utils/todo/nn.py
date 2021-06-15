# -*- coding: utf-8 -*-
"""
Created on Thu Jan 18 09:11:54 2018

@author: smh
"""

from scipy import spatial
import numpy as np
import pandas as pd
import datetime

#load data
xls = pd.ExcelFile(r"n:\MOD\106520_BCS_catchment_models\mod\cal\datasets\cmf_GKB\GAP_20102013\GAP_Flufenacet_GKB2_20102013.xlsx")
points = xls.parse("points_agriculture_grass")
gap = xls.parse("gap")
#source points
srcXY = np.array([[x,y] for x,y in zip(points["x"],points["y"])])
#target points
trgXY =  np.array([[x,y] for x,y in zip(gap["x"],gap["y"])])
#find nn
index = spatial.KDTree(srcXY).query(trgXY)[1]
#crete results table
res = pd.DataFrame()
res = gap
points_nn =  points.iloc[index]
points_nn.reset_index(inplace=True)
res["points_id"] = points_nn["ID"]
res["points_x"] = points_nn["x"]
res["points_y"] = points_nn["y"]
res["points_area"] = points_nn["area"]
res["points_soil"] = points_nn["soil"]
res.to_csv(r"n:\MOD\106520_BCS_catchment_models\mod\cal\datasets\cmf_GKB\GAP_20102013\GAP_Flufenacet_GKB2_20102013_nn.csv")
