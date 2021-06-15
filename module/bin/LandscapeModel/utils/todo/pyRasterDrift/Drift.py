# -*- coding: utf-8 -*-
"""
Created on Mon Feb 19 13:30:43 2018

@author: smh
"""
import numpy as np
import pandas as pd
import matplotlib.pylab as plt
import matplotlib.patches as mpatches

class Drift():
    
    def __init__(self,rautmann,croptypes,interception_table,step3_distances,FOCUS_WaterBody,crop,BBCH,DT50water,
                 DT50sediment, degradation_days=[1,2,4,7,14,21,28,100]):
        """        
        rautman (table):                Table with rautmann drift values
        croptypes (table):              Table with crop types
        interception_table (table):     Table with SW interception values
        step3_distances (table):        Table with z1 and z2 for assessing drift for Step3
        FOCUS_WaterBody (table):        Infos about water body geomtry and sediment according to FOCUS.
        crop (string):                  Crop
        BBCH (string):                  BBCH stage: 
                                        no interception(00-09)
                                        minimal crop cover (10-19)
                                        intermediate crop cover (20-39)
                                        full canopy (40-89)

        DT50_water (double):            DT50 water [days]
        DT50sedimentr (double):         DT50 water [days]

        degradation_days (list):        List with degradation_days [days]
        """
        
        #set drift value database
        self.rautmann = rautmann
        
        #set crop type table
        self.croptypes = croptypes
        
        #set interception table
        self.interception_table = interception_table
        
        #set distance table for step3 calculations
        self.step3_distances = step3_distances
        
        #set FOCUS water body table with geometries and sediment params
        self.FOCUS_WaterBody = FOCUS_WaterBody
        
        #crop type
        self.croptype = self.croptypes["CropType_Rautmann"][self.croptypes["Crop"]==crop].values[0]
        
        # coefficients
        self.crop = crop
        self.BBCH = BBCH
        self.degradation_days = degradation_days
        self.DT50water = DT50water
        self.DT50sediment = DT50sediment
        self.interception = 0
        
        #regressio nparameter
        self.regression_A = 0
        self.regression_B = 0
        self.regression_C = 0
        self.regression_D = 0
        self.regression_H = 0
        
        #state variables water body and sediment
        self.water_volume = 0.0
        self.water_surface = 0.0
        self.water_depth = 0.0
        self.sediment_height = 0.0
        self.sediment_density = 0.0
        self.sediment_percentage = 0.0
        
        #sate variables
        self.interception = 0.0
        self.deposition = 0.0
        self.drift = 0.0
        self.PECini_sw = 0.0
        self.PECini_sed = 0.0
        self.PECsw_degradation = []
        self.PECsed_degradation  = []
        self.summary = ""
        
        #fixid parameters for wind vector
        wind_degree = [0,22.5,45,67.5,90,112.5,135,157.5,180,202.5,225,247.5,270,292.5,315,337.5]
#        wind_name = ["N","NNO","NO","ONO","O","OSO","SO","SSO","S","SSW","SW","WSW","W","WNW","NW","NNW"]
        wind_name = ["N","NNE","NE","ENE","E","ESE","SE","SSE","S","SSW","SW","WSW","W","WNW","NW","NNW"]
        wind = dict(zip(wind_name,wind_degree))
        self.wind = wind
        
        #vectorized functions
        #vectorized distance        
        self.vectorize_distance = np.vectorize(self.calc_distance)
        #vectorized angle
        self.vectorize_angle = np.vectorize(self.calc_angle)
        #vectorzie check windcorridor
        self.vectorize_windcorridor = np.vectorize(self.check_windcorridor)

    def calc_grid(self,wind_direction,uncertainty,max_distance,fields_selected,f,river,
                  xlim=None,ylim=None,fpath=None):
        """
        Finds for each cell of a gridded river the shortest distance to the edge
        of a gridded field. The calculation is limited by a maximum distance
        between river and ftje wind corridor. The wind corridor is given by the
        current wind direction and an uncertainty term.
        
        wind_direction (string):    Wind direction
                                    ["N","NNO","NO","ONO","O","OSO","SO","SSO",
                                     "S","SSW","SW","WSW","W","WNW","NW","NNW"]
        uncertainty (double):       Uncertainty of widn angle [°]
        max_distance (double):      Maximum distance drift occures [m].
        fields_selected (table):    Table with name, x, and y coordinate of the 
                                    grid cells which represent one field.
        f (string):                 name of current field.
        river (table):              Table with name, x and y coordinate of the grid
                                    cells which represent one river cell.
        xlim (tuple):               Two double values defining x-axis lims.
        ylim (tuple):               Two double values defining y-axis lims.
        fpath (string):             
        
        Returns (list);
        List with name of river cell, field and shortest disntance [m].
        """        
        # make plot of grid cells of field and river
        fig = plt.figure(figsize=(7, 7))
        ax1 = fig.add_axes([0.1,0.1,0.8,0.8]) # x,y, lenght, height
        # plot current field
        ax1.scatter(fields_selected["x"],fields_selected["y"],s=50,c="b",edgecolor="None")
        ax1.plot(river["x"],river["y"],c="lightblue",marker="o",markeredgecolor="None",linewidth=10,markersize=20)
        ax1.grid(True)
        ax1.set_xlim(0,10)
        ax1.set_ylim(0,10)      
        #find nearest field cell for each river cell
        #list with final distance between river and field
        river_field_conn = []
        for r in range(len(river)):
            print(r)
            #get current river cell
            rivseg = river.iloc[r]
            #empty list for all field cells which are in maximum distance and
            #wind corridor
            rivseg_dist = []
            for field_index in range(len(fields_selected)):
                field = fields_selected.iloc[field_index]
                #check if the rive cell is inside the macimum distance and
                # in the wind corridor.
                isCorridor,distance=self.check_conditions(field["x"],field["y"],rivseg["x"],rivseg["y"],wind_direction,uncertainty,max_distance)
                if isCorridor:
                    #append to list if in corridor and distance
                    rivseg_dist.append((rivseg["name"],isCorridor,distance,rivseg["x"],rivseg["y"],field["name"],field["x"],field["y"]),)
            
            if len(rivseg_dist)>0:
                #find the field cell which is nearest to the river cell and inside
                # wind corridor.               
                index = [i[2] for i in rivseg_dist].index([min([i[2] for i in rivseg_dist if i[1]])])
                #plot connection between river cell and edge of field
                ax1.plot([rivseg_dist[index][6],rivseg_dist[index][3]],[rivseg_dist[index][7],rivseg_dist[index][4]],"r--")
                ax1.scatter(rivseg_dist[index][6],rivseg_dist[index][7],s=150,c="None",edgecolor="r")  
                #attach conn to list
                river_field_conn.append((rivseg_dist[index][0],rivseg_dist[index][5],rivseg_dist[index][2]))
        
        ax1.text(0.05,0.95,"Wind direction: " + wind_direction,transform=ax1.transAxes,fontweight="bold")        
        #save figure
        if fpath != None:
            fig.savefig(fpath,dpi=300)
        
        return river_field_conn
    
    def calc_distance_maxtrix(self,x1,y1,x2,y2):
        x_distance = (x2-x1[:,None])**2
        y_distance = (y2-y1[:,None])**2
        return np.sqrt(x_distance+y_distance)
     
    def calc_angle_maxtrix(self,x1,y1,x2,y2):
        tmp_x = x2-x1[:,None]
        tmp_y = y2-y1[:,None]
        radians = np.arctan2(tmp_x,tmp_y)
        angle = np.rad2deg(radians)
        angle[angle<0]+=360
        return angle
    
    def check_bounding_box(self,wind_direction,uncertainty,max_distance,fields_selected_source,river_source):
        #get wind angle
        wind_angle = self.wind[wind_direction]
        
        # a bounding box is applied to make a pre-selection of fields and river 
        # segemetns depending on the the maximum distance allowign drift        
        
        #get bounding box of selected field
        field_x_min = fields_selected_source["x"].min()-max_distance
        field_x_max = fields_selected_source["x"].max()+max_distance
        field_y_min = fields_selected_source["y"].min()-max_distance
        field_y_max = fields_selected_source["y"].max()+max_distance
        #select river cells which are in bounding box
        river = river_source[(river_source["x"]>=field_x_min)&(river_source["x"]<=field_x_max)&(river_source["y"]>=field_y_min)&(river_source["y"]<=field_y_max)]
            
        #get bounding box of river cells
        river_x_min = river["x"].min()-max_distance
        river_x_max = river["x"].max()+max_distance
        river_y_min = river["y"].min()-max_distance
        river_y_max = river["y"].max()+max_distance                 
        # select only field cells whic hare in range of the rive +/- max distance
        fields_selected = fields_selected_source[(fields_selected_source["x"]>=river_x_min)&(fields_selected_source["x"]<=river_x_max)&(fields_selected_source["y"]>=river_y_min)&(fields_selected_source["y"]<=river_y_max)]
        return river,fields_selected


    def calc_drift_catchment(self,appl_rate,field_area,wind_direction,uncertainty,max_distance,fields_selected_source,f,river_source,
                      xlim=None,ylim=None,s=None,fpath=None,fig=None):
        """
        Finds for each cell of a gridded river the shortest distance to the edge
        of a gridded field. The calculation is limited by a maximum distance
        between river and ftje wind corridor. The wind corridor is given by the
        current wind direction and an uncertainty term.
        
        appl_rate (double):         Applicatio nrate [g/ha]
        field_area (double):        Area of field [ha]
        wind_direction (string):    Wind direction
                                    ["N","NNO","NO","ONO","O","OSO","SO","SSO",
                                     "S","SSW","SW","WSW","W","WNW","NW","NNW"]
        uncertainty (double):       Uncertainty of widn angle [°]
        max_distance (double):      Maximum distance drift occures [m].
        fields_selected (table):    Table with name, x, and y coordinate of the 
                                    grid cells which represent one field.
        f (string):                 name of current field.
        river (table):              Table with name, x and y coordinate of the grid
                                    cells which represent one river cell.
        xlim (tuple):               Two double values defining x-axis lims.
        ylim (tuple):               Two double values defining y-axis lims.
        s (string):                 Additional text for figure
        fpath (string):             Target path of figure
        
        Returns (list);
        List with name of river cell, field and shortest disntance [m].
        """      
        #get wind angle
        wind_angle = self.wind[wind_direction]
        #write string
        s += "Most frequent: " + wind_direction + "\n"
        s += "Max distance: " + "%.0fm"%(max_distance) + "\n"
        s += "Wind uncertainty: " + "%.0f°"%(uncertainty)  + "\n\n"
        
        # a bounding box is applied to make a pre-selection of fields and river 
        # segemetns depending on the the maximum distance allowign drift   

        #get bounding box of selected field
        field_x_min = fields_selected_source["x"].min()-max_distance
        field_x_max = fields_selected_source["x"].max()+max_distance
        field_y_min = fields_selected_source["y"].min()-max_distance
        field_y_max = fields_selected_source["y"].max()+max_distance
        #select river cells which are in bounding box
        river = river_source[(river_source["x"]>=field_x_min)&(river_source["x"]<=field_x_max)&(river_source["y"]>=field_y_min)&(river_source["y"]<=field_y_max)]
            
        #get bounding box of river cells
        river_x_min = river["x"].min()-max_distance
        river_x_max = river["x"].max()+max_distance
        river_y_min = river["y"].min()-max_distance
        river_y_max = river["y"].max()+max_distance                 
        # select only field cells whic hare in range of the rive +/- max distance
        fields_selected = fields_selected_source[(fields_selected_source["x"]>=river_x_min)&(fields_selected_source["x"]<=river_x_max)&(fields_selected_source["y"]>=river_y_min)&(fields_selected_source["y"]<=river_y_max)]
          
        #check if at least one river cell is in max distance of a field cell
        if len(river)>0 and len(fields_selected)>0:
            
            def checkBounds(x,y):
                #calculate angle between river cells and all field cells
                vect_angle  = self.vectorize_angle(river["x"],river["y"],x,y)    
                #select all field which are inside wind corridor
                return self.vectorize_windcorridor(vect_angle,wind_angle,uncertainty) 
                
            # check wind corridor for min/max field bounds 
            llcorner = checkBounds(field_x_min,field_y_min)
            lrcorner = checkBounds(field_x_max,field_y_min)
            ulcorner = checkBounds(field_x_min,field_y_max)
            urcorner = checkBounds(field_x_max,field_y_max)  
            #make slecetion of river cells
            river  = river [llcorner | lrcorner | ulcorner | urcorner] 
                                         
            # get grid coordinates of river
            x1 = river["x"].values
            y1 = river["y"].values
            river_names = river["name"].values            
            river_point_id = river["points_id"].values            
            
            # get grid coordiantes of fields
            x2 = fields_selected["x"].values
            y2 = fields_selected["y"].values
            
            #calc distance
            distance = self.calc_distance_maxtrix(x1,y1,x2,y2)
            #check max distance
            distance_check = distance <= max_distance
            #calc angle
            angle = self.calc_angle_maxtrix(x1,y1,x2,y2)
            #check wind corridor
            wind_angl_min = wind_angle-uncertainty
            wind_angle_max = wind_angle+uncertainty
            wind_corridor = (angle>=wind_angl_min)&(angle<=wind_angle_max )

            # combine maximum distance with wind corridor condition
            conds = distance_check & wind_corridor
            distance_with_conds = np.where(conds,distance,np.nan)

            ##calculate minimum distance
            distance_min = np.nanmin(distance_with_conds,axis=1) # [m]
        
            #calc total river area
            river_total_drift_area = distance_min.size - np.count_nonzero(np.isnan(distance_min))

            # check if drift area zero
            if river_total_drift_area > 0:
                
                #get distance values
                distance_vals = distance_min[np.isnan(distance_min)==False]

                #get name of river cells
                name_vals = river_names[np.isnan(distance_min)==False]
                river_point_id_vals = river_point_id[np.isnan(distance_min)==False]                
                
                #calc drift
                
                deposition_drift = np.array([self.calc_drift_total(appl_rate,dis,4) for dis in distance_vals])# each cell 2m x 2 m  =4m2
                
                #get depostion values
                deposition = deposition_drift[:,0]
                mean_deposition = deposition.mean() 
                max_deposition = deposition.max() 
                min_deposition = deposition.min() 
                
                #get drift            
                drift = deposition_drift[:,1]
                sum_drift = drift.sum()#mg     
                   
                #calcualte maximum drift: app_rate x field_area x mean depostion
                limit_drift = appl_rate * 10 * field_area * mean_deposition / 100. #g
                limit_drift *= 1000 # convert g to mg
                
            else:
                                
                mean_deposition = 0
                max_deposition = 0 
                min_deposition = 0
                
                #get drift            
                drift = 0
                sum_drift = 0
                
                #calcualte maximum drift: app_rate x field_area x mean depostion
                limit_drift = 0
                limit_drift *= 1000 # convert g to mg
                
                deposition = None
                drift = None
                distance_vals = None
                name_vals = None
                river_point_id_vals = None
                
        else:
           
            deposition = None
            drift = None
            distance_vals = None
            name_vals = None
            river_point_id_vals = None
        
        # make plot of grid cells of field and river
        if fpath!=None:   
            
            #check if data avaialable
            
            if not len(river)>0 or not len(fields_selected)>0:
                x1 = river_source["x"].values
                y1 = river_source["y"].values
                # get grid coordiantes of fields
                x2 = fields_selected_source["x"].values
                y2 = fields_selected_source["y"].values
            
            ax11 = fig.add_axes([0.1,0.78,0.2,0.2]) # x,y, lenght, height  
            
            ax11.scatter(river_source["x"].values,river_source["y"].values,s=1,c="lightblue",edgecolor="None")
            ax11.scatter(fields_selected_source["x"].values,fields_selected_source["y"].values,s=1,c="orange",edgecolor="None")
            ax11.set_xticklabels("")
            ax11.set_yticklabels("")
            ax11.grid(True)
                        #plot text
            ax11.text(1.05,0.99,s,transform=ax11.transAxes,fontweight="bold",horizontalalignment='left', verticalalignment='top')  
            
            
            ax1 = fig.add_axes([0.1,0.1,0.5,0.5]) # x,y, lenght, height
            # plot field
            ax1.scatter(x2,y2,s=1,c="orange",edgecolor="None")
            ax1.plot(x1,y1,color="lightblue",marker="o",markeredgecolor="None",linewidth=0,markersize=4)
            #format axis
            ax1.grid(True)
            ax1.set_xlim(np.min([x1.min(),x2.min()])-max_distance,np.max([x1.max(),x2.max()])+max_distance)
            ax1.set_ylim(np.min([y1.min(),y2.min()])-max_distance,np.max([y1.max(),y2.max()])+max_distance)
            ax1.set_xlabel("X [m]")
            ax1.set_ylabel("Y [m]")
            
            s2=""
            if len(river)>0 and len(fields_selected)>0:            
                #plot connection between nearest edge of field and river cells
                i=0
                for cond,dis in zip(conds,distance_with_conds):
                    if not (np.isnan(dis).all()):
                        ind = np.nanargmin(dis)
                        ax1.plot(x1[i],y1[i],marker="o",color="None",markeredgecolor="r",markersize=2)
                        ax1.plot([x1[i],x2[ind]],[y1[i],y2[ind]],linestyle="--",color="r",linewidth=.5)
                    i+=1
                
                #write string    
                s2 += "River area: %.0f m$^2$"%(river_total_drift_area*4) + "\n" #each cell has 4m2                
                s2 += "Mean deposition: %.2f"%(mean_deposition) + "% " + ("(%.2f-%.2f)")%(min_deposition,max_deposition) + "\n" 
                
                s2 += "\n"
                s2 += "Drift: %.0f mg/field"%(sum_drift) + "\n" #each cell has 4m2
                s2 += "(Drift$_{max}$: %.0f mg/field)"%(limit_drift) + "\n" #each cell has 4m2
                
            
            #plot river

            ax1.text(1.05,0.99,s2,transform=ax1.transAxes,fontweight="bold",horizontalalignment='left', verticalalignment='top')

            #plot legend
            ax5  = fig.add_axes([0.6,0.1,0.2,0.2])
            ax5.axis('off')
            legend_urb = mpatches.Patch(color='orange', label='Field cell',alpha=.75,linewidth=0)
            legend_riv = mpatches.Patch(color='lightblue', label='River cell',alpha=.75,linewidth=0)
            legend_gra = mpatches.Patch(color='red', label='Drift path',alpha=.75,linewidth=0)
            plt.legend(handles=[legend_urb,legend_riv,legend_gra],ncol=1, loc="center", fontsize=10.,fancybox=True, framealpha=0.5)
            fig.savefig(fpath,dpi=300)        
            plt.close("all")
            fig.clf()

        #get distance

        return name_vals,river_point_id_vals,distance_vals,deposition,drift



#    def calc_drift_catchment(self,appl_rate,field_area,wind_direction,uncertainty,max_distance,fields_selected_source,f,river_source,
#                  xlim=None,ylim=None,s=None,fpath=None):
#        """
#        Finds for each cell of a gridded river the shortest distance to the edge
#        of a gridded field. The calculation is limited by a maximum distance
#        between river and ftje wind corridor. The wind corridor is given by the
#        current wind direction and an uncertainty term.
#        
#        appl_rate (double):         Applicatio nrate [g/ha]
#        field_area (double):        Area of field [ha]
#        wind_direction (string):    Wind direction
#                                    ["N","NNO","NO","ONO","O","OSO","SO","SSO",
#                                     "S","SSW","SW","WSW","W","WNW","NW","NNW"]
#        uncertainty (double):       Uncertainty of widn angle [°]
#        max_distance (double):      Maximum distance drift occures [m].
#        fields_selected (table):    Table with name, x, and y coordinate of the 
#                                    grid cells which represent one field.
#        f (string):                 name of current field.
#        river (table):              Table with name, x and y coordinate of the grid
#                                    cells which represent one river cell.
#        xlim (tuple):               Two double values defining x-axis lims.
#        ylim (tuple):               Two double values defining y-axis lims.
#        s (string):                 Additional text for figure
#        fpath (string):             Target path of figure
#        
#        Returns (list);
#        List with name of river cell, field and shortest disntance [m].
#        """       
#
#        #get wind angle
#        wind_angle = self.wind[wind_direction]
#        
#        # a bounding box is applied to make a pre-selection of fields and river 
#        # segemetns depending on the the maximum distance allowign drift        
#        
#        #get bounding box of selected field
#        field_x_min = fields_selected_source["x"].min()-max_distance
#        field_x_max = fields_selected_source["x"].max()+max_distance
#        field_y_min = fields_selected_source["y"].min()-max_distance
#        field_y_max = fields_selected_source["y"].max()+max_distance
#        #select river cells which are in bounding box
#        river = river_source[(river_source["x"]>=field_x_min)&(river_source["x"]<=field_x_max)&(river_source["y"]>=field_y_min)&(river_source["y"]<=field_y_max)]
#            
#        #get bounding box of river cells
#        river_x_min = river["x"].min()-max_distance
#        river_x_max = river["x"].max()+max_distance
#        river_y_min = river["y"].min()-max_distance
#        river_y_max = river["y"].max()+max_distance                 
#        # select only field cells whic hare in range of the rive +/- max distance
#        fields_selected = fields_selected_source[(fields_selected_source["x"]>=river_x_min)&(fields_selected_source["x"]<=river_x_max)&(fields_selected_source["y"]>=river_y_min)&(fields_selected_source["y"]<=river_y_max)]
#                 
#
#        # make plot of grid cells of field and river
#        if fpath!=None:        
#            fig = plt.figure(figsize=(7, 7))
#            ax1 = fig.add_axes([0.1,0.1,0.8,0.8]) # x,y, lenght, height
#            # plot current field
#            ax1.scatter(fields_selected_source["x"],fields_selected_source["y"],s=1,c="orange",edgecolor="None")
#            ax1.plot(river_source["x"],river_source["y"],color="lightblue",marker="o",markeredgecolor="None",linewidth=0,markersize=1)
#            ax1.grid(True)
#            ax1.set_xlim(min(field_x_min,river_x_min),max(field_x_max,river_x_max))
#            ax1.set_ylim(min(field_y_min,river_y_min),max(field_y_max,river_y_max))
#            ax1.set_xlabel("X [m]")
#            ax1.set_ylabel("Y [m]")
#
#        if len(river)>0 and len(fields_selected)>0:
#            
#            # get river cells which are inside the angle of the field boundaries
#            # ind wind direction
#
#            def checkBounds(x,y):
#                #calculate angle between river cells and all field cells
#                vect_angle  = self.vectorize_angle(river["x"],river["y"],x,y)    
#                #select all field which are inside wind corridor
#                return self.vectorize_windcorridor(vect_angle,wind_angle,uncertainty)    
#            # check wind corridor for min/max field bounds 
#            llcorner = checkBounds(field_x_min,field_y_min)
#            lrcorner = checkBounds(field_x_max,field_y_min)
#            ulcorner = checkBounds(field_x_min,field_y_max)
#            urcorner = checkBounds(field_x_max,field_y_max)  
#            #make slecetion of river cells
#            river  = river [llcorner | lrcorner | ulcorner | urcorner] 
#                     
#    
#            
#
#            
#            
#            fields_x = fields_selected["x"].values
#            fields_y = fields_selected["y"].values
#            fields_name = fields_selected["y"].values
#            
#            
#            
#            
#            
#            
#            ###################################################################
#            # new matrix calcualtion
#                   
#            river_x = river["x"].values
#            river_y = river["y"].values
#            
#            #calculate distance
#            distances = self.calc_distance_maxtrix(river_x,river_y,fields_x,fields_y)
#            
#            #check if distance lower than max distance            
#            distances_check = distances <=max_distance
#            
#            #calcualte angle
##            angles = self.calc_angle_maxtrix(river_x,river_y,fields_x,fields_y)
#            
#            #find nearest field cell for each river cell
#            #list with final distance between river and field
#            river_field_conn = []
#            
#            index_r=0
#            for river_index, rivseg in river.iterrows():
#                
#                rivseg_name = rivseg["name"]
#                rivseg_x = rivseg["x"]
#                rivseg_y = rivseg["y"]
#                
#                #calculate distance between river cell and all field cells
#                vect_distances = distances[:,index_r]#self.vectorize_distance(rivseg_x,rivseg_y ,fields_x,fields_y)
#                
#
#                #check distance if is in max distance
#                vect_check_distances = distances_check[index_r,:]#vect_distances<=max_distance
#                
#                #calculate angle between river cell and all field cells
#                vect_angle  = self.vectorize_angle(rivseg_x,rivseg_y ,fields_x,fields_y)  
#
#                #select all field which are inside wind corridor
#                vect_check_windcorridor   = self.vectorize_windcorridor(vect_angle,wind_angle,uncertainty)
#                
#                #get all segemnts in angle and distance
#                cond = vect_check_distances & vect_check_windcorridor
#                rivseg_dist = [(rivseg_name, dis_check,dis,rivseg_x,rivseg_y,name,x,y ) for x,y,name,dis_check,dis in zip(fields_x[cond],fields_y[cond],fields_name[cond],vect_check_distances[cond],vect_distances[cond])]
#
#                #find nearest field cell for each river cell
#                if len(rivseg_dist)>0:
#                    #find the field cell which is nearest to the river cell and inside
#                    # wind corridor.  
#                    index = [i[2] for i in rivseg_dist].index(min([i[2] for i in rivseg_dist if i[1]]))
#                    if fpath!=None:  
#                        
#    #                plot connection between river cell and edge of field
#                        ax1.plot([rivseg_dist[index][6],rivseg_dist[index][3]],[rivseg_dist[index][7],rivseg_dist[index][4]],"r--")
#                        ax1.scatter(rivseg_dist[index][6],rivseg_dist[index][7],s=5,c="None",edgecolor="r")  
#
#                    #calc drift
#                    self.calc_drift_total(appl_rate,rivseg_dist[index][2],4)# each cell 2m x 2 m  =4m2
#
#                    #attach conn to list
#                    river_field_conn.append((rivseg_dist[index][0],rivseg_dist[index][5],rivseg_dist[index][2],self.deposition,self.drift))
#                
#                index_r +=1
#   
#            #plot wind direction
#            if fpath!=None: 
#
#                #print river area influenced by drift
#                if len(river_field_conn)>0:
#                    s += "River area: %.0f m$^2$"%(len(river_field_conn)*4) + "\n" #each cell has 4m2
#                    mean_deposition = np.mean([i[-2] for i in river_field_conn])
#                    min_deposition = min([i[-2] for i in river_field_conn])
#                    max_deposition = max([i[-2] for i in river_field_conn])
#                    
#                    max_drift = appl_rate * field_area * mean_deposition / 100. #g
#                    max_drift *=1000. #mg
#                    
#                    s += "Mean deposition: %.2f"%(mean_deposition) + "% " + ("(%.2f-%.2f)")%(min_deposition,max_deposition) + "\n"  
#          
#                    s += "Drift: %.2f mg"%(sum([i[-1] for i in river_field_conn])) + "\n" #each cell has 4m2
#                    s += "Drift max: %.4f mg"%(max_drift) + "\n" #each cell has 4m2
#                    
#        else:
#            rivseg_dist = None
#            river_field_conn = None
#            
#        #save figure
#        if fpath != None:
#            ax1.text(0.05,0.95,"Wind direction: " + wind_direction,transform=ax1.transAxes,fontweight="bold")  
#            ax1.text(0.05,0.9,s,transform=ax1.transAxes,color="r",horizontalalignment='left', verticalalignment='top')  
#            fig.savefig(fpath,dpi=300)
#        
#        return rivseg_dist,river_field_conn
#        
####        
##        
        
            
    def __call__(self,application_rate,x1,y1,x2,y2,wind_direction,uncertainty,max_distance,water_surface = 1):
        
        isCorridor,distance =  self.check_conditions(x1,y1,x2,y2,wind_direction,uncertainty,max_distance)
    
        if isCorridor:
            
            #calculate dirft using Rautmann values and variable distance
            self.calc_Step123(application_rate=application_rate,number_of_applications=1,approach = "Variable",waterbody="Step12 waterbody",distance=distance,water_surface=water_surface)
            return isCorridor,self.deposition,self.drift
        else:
            
            return isCorridor,0,0
         
    def calc_drift_total(self,application_rate,distance,water_surface):
        
        """
        Drift inputs: the basis for the calculation of the PEC values is the depostion of 
        the substance. The deposition value is calculated on the basis of the 
        Rautman / Ganzelmeyer drift values who provide regression coefficients
        to calcualte the percentage deposition i nrelation to the distance
        
        Note that the minimum distance for field crops is 1m and for hops, 
        orchards and vineyards 3m.

        Moreover, a hingepoint is defined for fruit crops (15m) and hops (15m)
        which defines the threshold for using close or far parameter values.
        
        See also for parameterisation of A and B:
        https://www.julius-kuehn.de/at/ab/abdrift-und-risikominderung/abdrifteckwerte/
        
        Distance (double):      Distance to water body (1m or 3m in case of step 1)
        number_of_applications (integer):   Nubmer of applications 
        
        approach (string):      'Step1' or 'Step2' or 'Variable'
        """

            
        #adjust applicatio nrate for crop interception
        application_rate = (1-self.interception) * application_rate
        
        # cgeck distance (minimum field crops: 1m; trees: 3m)
        distance = self.check_distance(self.croptype,distance)

 
        #calculate deposition [%]      
        self.deposition = self.calc_deposition_Rautmann(distance,self.regression_A,
                                                        self.regression_B,
                                                        self.regression_C,
                                                        self.regression_D,
                                                        self.regression_H)        
        self.deposition /=2 # TODO: delete
        
        # water surface
        self.water_surface = water_surface
        
        #calc drift [mg/m2 water body]
        self.drift = self.calc_drift(application_rate,self.deposition,self.water_surface)
        
        return self.deposition, self.drift
        
    def calc_Step123(self,application_rate,number_of_applications,approach,waterbody,distance=None,water_surface=None):
        
        """
        Drift inputs: the basis for the calculation of the PEC values is the depostion of 
        the substance. The deposition value is calculated on the basis of the 
        Rautman / Ganzelmeyer drift values who provide regression coefficients
        to calcualte the percentage deposition i nrelation to the distance
        
        Note that the minimum distance for field crops is 1m and for hops, 
        orchards and vineyards 3m.

        Moreover, a hingepoint is defined for fruit crops (15m) and hops (15m)
        which defines the threshold for using close or far parameter values.
        
        See also for parameterisation of A and B:
        https://www.julius-kuehn.de/at/ab/abdrift-und-risikominderung/abdrifteckwerte/
        
        Distance (double):      Distance to water body (1m or 3m in case of step 1)
        number_of_applications (integer):   Nubmer of applications 
        
        approach (string):      'Step1' or 'Step2' or 'Variable'
        """
        
        #get regression parameter
        A,B,C,D,H = self.get_regression_parameter(self.croptype,number_of_applications)
        
        #TODO: how to handle step3 interception (commonly calcualted by MACRO)
        if (approach == "Step2") or (approach == "Variable"):#or (approach == "Step3"): 
            #get interception
            self.interception = self.interception_table[self.BBCH][(self.interception_table["Crop"]==self.crop)].values[0]
            
            #adjust applicatio nrate for crop interception
            application_rate = (1-self.interception) * application_rate
            
        # cgeck distance in case of step1, step2 and varriable
        # step3 distance is take nfrom table
        if (approach == "Step1") or (approach == "Step2"): #fixed distance
            if (self.croptype == "FruitCrops (early)") or (self.croptype == "FruitCrops (late)") or (self.croptype == "Hops") or (self.croptype == "Grapevine (late)") or (self.croptype == "Vegetables (>50cm)"):
                distance = 3
            else:
                distance = 1
        elif approach == "Variable":
            #check distance
            distance = self.check_distance(self.croptype,distance)
        elif (approach == "Step3"):
            step3dis = self.step3_distances[(self.step3_distances["Crop"]==self.crop) & (self.step3_distances["Water body type"]==waterbody)]
            
        #calculate deposition [%]
        if (approach == "Step1") or (approach == "Step2") or (approach == "Variable"):
            self.deposition = self.calc_deposition_Rautmann(distance,A,B,C,D,H)        
        elif (approach == "Step3"):           
            z1 = step3dis["z1"].values[0]
            z2 = step3dis["z2"].values[0]
            self.deposition = self.calc_deposition_footways(A,B,C,D,z1,z2,H)
         
        # get sediment and water body parameter 
        params = self.FOCUS_WaterBody[self.FOCUS_WaterBody["water body"] == waterbody]
        
        # get sediment parameter
        self.sediment_percentage = params["sediment percentage of PECsw [%]"]
        self.sediment_density = params["sediment bc [g/ml]"]
        self.sediment_height = params["sediment height [m]"]
        
        # get water parameter
        self.water_depth = params["depth [m]"]
        self.water_volume = params["volume [m3]"]
        self.water_surface = params["area [m2]"]
                 
        if (approach == "Variable"):
            self.water_surface = water_surface
        
        #calc drift [mg/m2 water body]
        self.drift = self.calc_drift(application_rate,self.deposition,self.water_surface)
        
        
        #calc PECini sw [ug/L]
        self.PECini_sw = self.calc_PECini_sw(self.drift,self.water_volume)
        
        #calc PECini sed [ug/L]
        self.PECini_sed  = self.calc_PECini_sed(self.PECini_sw ,self.water_depth,self.sediment_height,self.sediment_density,self.sediment_percentage)
        
        #calc degradation scheme PECsw
        self.PECsw_degradation = [self.calc_degradation(self.PECini_sw,day,self.DT50water) for day in self.degradation_days]
        
        #calc degradation scheme PECsed
        self.PECsed_degradation = [self.calc_degradation(self.PECini_sed,day,self.DT50sediment) for day in self.degradation_days]
        

        #preapre summary string
        summary = "###########################################"+ "\n"
        summary += "FOCUS drift (" + approach + "): " + self.crop + ", " + self.BBCH + ", " + waterbody +   "\n"
        summary += "\n"
        if (approach == "Step1") or (approach == "Step2") or (approach == "Variable"): 
            summary += "Application rate %.2fg/ha  Distance %.2fm "%(application_rate,distance) + "\n"
        elif (approach == "Step3"):
            summary += "Application rate %.2fg/ha z1 %.2fm z1 %.2fm "%(application_rate,z1,z2) + "\n"
        summary += "Deposition %.2f  Drift %.2fmg"%(self.deposition,self.drift )+ "\n"
        summary += "PECsw_ini %.4fug/L  PECsed_ini %.4fug/L"%(self.PECini_sw,self.PECini_sed ) + "\n"
        summary += "\n"
        summary += "%4s %6s %6s" % ("Day","PECsw","PECsed") + "\n"
        summary += "\n".join(["%4.0f %.4f %.4f"%(day,PECsw,PECsed) for day,PECsw,PECsed in zip(self.degradation_days,self.PECsw_degradation,self.PECsed_degradation)]) + "\n"
        summary += "\n"
        summary += "###########################################"+ "\n"
        self.summary = summary


   
    def get_regression_parameter(self,croptype,number_of_applications):
        """
        Returns regression paramter for Rautmann equation.
        
        croptype (string):                  Crop type: FieldCrop, FruitCrops (early), 
                                            FruitCrops (late), Grapevine, Hops, 
                                            Vegetables (<50cm),Vegetables (>50cm)
        number_of_applications (integer):   Nubmer of applications
 
        
        see FOCUS 2001 SWS APPENDIX B PARAMETERIZATION OF SPRAY DRIFT INPUT

        Returns
        Regression coefficients A,B,C,D and hinge point H [-]
        """
        
        #get drift parameters
        params = self.rautmann[(self.rautmann["Crop"]==croptype) & (self.rautmann["Applications"]==number_of_applications)]
        
        #in case of fruits crops and hopds different values are used in relation
        #to the distance
        if (self.croptype == "FruitCrops (early)") or (self.croptype == "FruitCrops (late)") or (self.croptype == "Hops"):
            A = params["A_close"].values[0]
            B = params["B_close"].values[0]
            C = params["A_far"].values[0]
            D = params["B_far"].values[0]
            H = params["hingepoint"].values[0]
        else:
            A = params["A_close"].values[0]
            B = params["B_close"].values[0]
            C = 0
            D = 0
            H = 0
        
        self.regression_A = A
        self.regression_B = B
        self.regression_C = C
        self.regression_D = D
        self.regression_H = H
        
        
        
        return A,B,C,D,H
  
    def check_distance(self,croptype,distance):
        """
        Checks the distance for regression parameter:the minimum distance for 
        field crops is 1m and for hops,orchards and vineyards 3m.
        
        croptype (string):                  Crop type: FieldCrop, FruitCrops (early), 
                                            FruitCrops (late), Grapevine, Hops, 
                                            Vegetables (<50cm),Vegetables (>50cm)
        Distance (double):      Distance to wter body.
        
        Returns
        Adjusted distance [m]
        """
        if (croptype == "FruitCrops (early)") or (croptype == "FruitCrops (late)") or (croptype == "Hops")  or (croptype == "Grapevine (early)")or (croptype == "Grapevine (late)")   or   (croptype == "Vegetables (>50cm)"):
            if distance < 3 :
                distance = 3
        if (croptype == "FieldCrop") or (croptype == "Vegetables (<50cm)") :
            if distance <1:
                distance = 1
        return distance
    
    def calc_deposition_footways(self,A,B,C,D,z1,z2,H):
        """

        See FOCUS 2001 final Report SW

        A, B, C, D = previously defined regression parameters
        z1 = distance from edge of treated field to closest edge of water body (m)
        z2 = distance from edge of treated field to farthest edge of water body (m)
        H = distance limit for each regression (m), also called hinge point.


        deposition mean percent drift loading across a water body that extends from a dis-tance of z1 to z2 from the edge of the treated field
        """
        
        if (self.croptype == "FruitCrops (early)") or (self.croptype == "FruitCrops (late)") or (self.croptype == "Hops"):
            # hinge point between z1 and z2
            if (z1 < H ) and (H < z2):
                deposition = ((A / (B+1)) * (H**(B+1) - z1**(B+1)) + (C / (D+1)) * (z2**(D+1) - H**(D+1))) * (1/(z2-z1))
                
            # hinge point larger than z1 and z2
            elif (z2 <= H):
                deposition = (A / ((z2-z1) * (B+1))) * (z2**(B+1) - z1**(B+1))
                
            # hinge point lower than z1 and z2 
            elif (z1 >= H):
                deposition = (C / ((z2-z1) * (D+1))) * (z2*(D+1) - z1**(D+1))
        else:
            deposition = (A / ((z2-z1) * (B+1))) * (z2**(B+1) - z1**(B+1))
            
        return deposition

    def calc_deposition_Rautmann(self,Distance,A,B,C,D,H):
        """
        Calculates deposition according to Rautmann/Ganzelmeyer regression coefficients.
        
        A (double):             Regression coefficient [-].
        B (double):             Regression coefficient [-].
        Distance (double):      Distance to wter body.
         
        Returns
        Deposition (double):    Deposition of substance [%].
            
        deposition (%) = A * distance (m) ^ B
        
        See also for parameterisation of A and B:
        https://www.julius-kuehn.de/at/ab/abdrift-und-risikominderung/abdrifteckwerte/
        """

        if (self.croptype == "FruitCrops (early)") or (self.croptype == "FruitCrops (late)") or (self.croptype == "Hops"):
            if Distance <= H:
                deposition = A*Distance**B
            else:
                deposition = C*Distance**D   
        else:
            deposition = A*Distance**B
            
        return deposition

    def calc_drift(self,application_rate,deposition,water_surface):
        """
        Calculates drift according to deposition percentage.
        
        application_rate (double):  Application rate [g / ha]
        deposition (double):        Deposition rate [%]
        deposition (double):        Water sruface area [m2]
        
        Returns
        Drift (double):             Drift[mg/waterbody]
        """
        return (application_rate / 10) *  (deposition / 100) * water_surface
    
    def calc_degradation(self,PECini_sw,day,DT50_water):
        """
        Calculates PEC after a certain number of days.
        PECini_sw (double):        Initial PEC value [ug/L]
        day (double):           Number of days after PECini [days]
        DT50_water (double):    DT50 water [days]
        
        Returns
        PEC (dobule):   PEC value after degradation.
        """
        return PECini_sw * np.exp(day*(-np.log(2)/DT50_water))
    
    def calc_PECini_sw(self,Drift,water_volume):
        """
        Caclulates PECini for surface water.
        water_volume:             Water volume [m3]
        Drift (double):      Drift[mg]
        
        Returns
        PECini_sw (double):     Initial PEC of surface water [mg/m3 = ug/L]
        """
        PECini_sw = Drift/water_volume

        return PECini_sw
        
    def calc_PECini_sed(self,PECini_sw,water_height,sediment_height,sediment_density,sediment_percentage):
        """
        Caclualtes PEC ini for sediment layer.
        
        PECini_sw (double):             Initial PEC of surface water [ug/L]
        water_height (double):          Water table height [cm]
        sediment_height (double):              Sedimentheight [cm]
        water_height (double):          Sediment_density [g/cm3]
        sediment_percentage (double):   Sediment [%]
        
        Returns
        PECini_sed (double):    Initial PEC of sediment [ug/L]
        """
        PECini_sed = PECini_sw*sediment_percentage*water_height/(100*sediment_density*sediment_height)
        return PECini_sed


    def check_conditions(self,wind_direction,uncertainty,max_distance,distance,angle,wind_angle):
        """
        Check if a drift input is possible between two points.

        x1 (double):                x coordiante point1 [m]
        y1 (dobule):                y coordiante point1 [m]
        x2 (double):                x coordiante point2 [m]
        y2 (dobule):                y coordiante point2 [m]
        wind_direction (string):    Wind direction (SW,NW,NON,...)
        uncertainty (double):       Uncertainty of wind angle
        max_distnace (double):      Maximum distance between two points
                                    where drift occurs
        Returns
        True/False
        """
#        distance = self.calc_distance(x1,y1,x2,y2)

        isCorridor = self.check_windcorridor(angle,wind_angle,uncertainty)

        if (distance <= max_distance) and isCorridor:
            return True
        else:
            return False
            
#            
#    def check_conditions(self,x1,y1,x2,y2,wind_direction,uncertainty,max_distance,distance=0):
#        """
#        Check if a drift input is possible between two points.
#
#        x1 (double):                x coordiante point1 [m]
#        y1 (dobule):                y coordiante point1 [m]
#        x2 (double):                x coordiante point2 [m]
#        y2 (dobule):                y coordiante point2 [m]
#        wind_direction (string):    Wind direction (SW,NW,NON,...)
#        uncertainty (double):       Uncertainty of wind angle
#        max_distnace (double):      Maximum distance between two points
#                                    where drift occurs
#        Returns
#        True/False
#        """
##        distance = self.calc_distance(x1,y1,x2,y2)
#
#        isCorridor = self.calc_wind_corridor(x1,y1,x2,y2,wind_direction,uncertainty)
#
#        if (distance <= max_distance) and isCorridor:
#            return True#,distance
#        else:
#            return False#,distance


    def calc_angle(self,x1,y1,x2,y2):
        """
        Calculates angle between two points depending on x and y coords.
        
        x1 (double):     x coordiante point1 [m]
        y1 (dobule):     y coordiante point1 [m]
        x2 (double):     x coordiante point2 [m]
        y2 (dobule):     y coordiante point2 [m]
        
        Returns
        angle (double):     Angle between point1 and point2 [°]
        """
        radians = np.arctan2((x2-x1),(y2-y1))
        angle = np.rad2deg(radians)
        if (angle<0):
            angle=angle+360
        return angle
    
    def calc_distance(self,x1,y1,x2,y2):
        """
        Calculates angle between two points depending on x and y coords.
        
        x1 (double):     x coordiante point1 [m]
        y1 (dobule):     y coordiante point1 [m]
        x2 (double):     x coordiante point2 [m]
        y2 (dobule):     y coordiante point2 [m]
        
        Returns
        distance (double):     Distance between point1 and point2 [m]
        """
        return np.sqrt((y1-y2)**2+(x1-x2)**2)


 
    def check_windcorridor(self,angle,wind_angle,uncertainty):
        """
        Calculates the wind corridor from a field in relattion to a given wind
        direction. The wind corridor is given by the wind direction +/- an
        uncertainty term. 
        

        wind_direction (string):    Wind direction (SW,NW,NON,...)
        uncertainty (double):       Uncertainty of wind angle.
        
        Returns
        Boolean values indicating if point2 is in the wind corridor of point1.
        """
  
#        wind_angle-=180
        if wind_angle<0: wind_angle+=360
        
        isCorridor=False
        if angle>0 and angle<=180:
        
#            print("<180",angle,wind_angle,wind_angle-uncertainty,wind_angle+uncertainty)
                
            if wind_angle>=0 and wind_angle <= 180:
                
                if (angle>(wind_angle-uncertainty) and angle<=(wind_angle+uncertainty)):
                    isCorridor=True
            
            else:
                
                if (angle+360>(wind_angle-uncertainty) and angle+360<=(wind_angle+uncertainty)):
                    isCorridor=True
            
        else:
            
#            print(">180",angle,wind_angle,wind_angle-uncertainty,wind_angle+uncertainty)
                
            if wind_angle>=180 and wind_angle <= 360:
            
                
                    
                if (angle>(wind_angle-uncertainty) and angle<=(wind_angle+uncertainty)):
                    isCorridor=True
        
            else:
                
                if (angle-360>(wind_angle-uncertainty) and angle-360<=(wind_angle+uncertainty)):
                    isCorridor=True
                    
        return isCorridor    
    
    
#    def calc_wind_corridor(self,x1,y1,x2,y2,wind_direction,uncertainty):
#        """
#        Calculates the wind corridor from a field in relattion to a given wind
#        direction. The wind corridor is given by the wind direction +/- an
#        uncertainty term. 
#        
#        x1 (double):                x coordiante point1 [m]
#        y1 (dobule):                y coordiante point1 [m]
#        x2 (double):                x coordiante point2 [m]
#        y2 (dobule):                y coordiante point2 [m]
#        wind_direction (string):    Wind direction (SW,NW,NON,...)
#        uncertainty (double):       Uncertainty of wind angle.
#        
#        Returns
#        Boolean values indicating if point2 is in the wind corridor of point1.
#        """
#        #calc anlge
#        radians,angle = self.calc_angle(x1,y1,x2,y2)
#        
#        #get wind angle
#        wind_angle = self.wind[wind_direction]
#        wind_angle-=180
#        if wind_angle<0: wind_angle+=360
#        
#        isCorridor=False
#        if angle>0 and angle<=180:
#        
##            print("<180",angle,wind_angle,wind_angle-uncertainty,wind_angle+uncertainty)
#                
#            if wind_angle>=0 and wind_angle <= 180:
#                
#                if (angle>(wind_angle-uncertainty) and angle<=(wind_angle+uncertainty)):
#                    isCorridor=True
#            
#            else:
#                
#                if (angle+360>(wind_angle-uncertainty) and angle+360<=(wind_angle+uncertainty)):
#                    isCorridor=True
#            
#        else:
#            
##            print(">180",angle,wind_angle,wind_angle-uncertainty,wind_angle+uncertainty)
#                
#            if wind_angle>=180 and wind_angle <= 360:
#            
#                
#                    
#                if (angle>(wind_angle-uncertainty) and angle<=(wind_angle+uncertainty)):
#                    isCorridor=True
#        
#            else:
#                
#                if (angle-360>(wind_angle-uncertainty) and angle-360<=(wind_angle+uncertainty)):
#                    isCorridor=True
#                    
#        return isCorridor    
#    
    
def run_ttest(fpath="c:/0_work/bcs_catchmentmodelling/model_runs/final/GKB2_SubB_drift/Drift/"):
            
    ###################s###########################################################
    # run drift module for all crop types and create plot
    
    # usbstance settings
    DT50water=67 #days
    DT50sediment=67#days
    ApplRate = 12 #g/ha
    BBCH = "no interception (00-09)"
    
    #read rautmann table
    rautmann = pd.read_csv(fpath+"FOCUS_Rautmann_drift_values.csv")
    interception_table = pd.read_csv(fpath+"FOCUS_CropInterception_SW.csv")
    croptypes = pd.read_csv(fpath+"FOCUS_CropTypes.csv")
    step3_distances = pd.read_csv(fpath+"FOCUS_Step3_distances.csv")
    FOCUS_WaterBody = pd.read_csv(fpath+"FOCUS_WaterBody.csv")
    
    #function to assess drfit values depending on fixded distance steps
    def test_drift(crop):
        # Field crop
        drift = Drift(rautmann,croptypes,interception_table,step3_distances,FOCUS_WaterBody,crop,BBCH,DT50water=DT50water,DT50sediment=DT50sediment)
        vals=[]
        for i in [0.1,1,2,3,5,10,15,20,30,40,50]:#range(1,200):
            drift.calc_Step12(ApplRate,i,5,approach = "Variable")
            vals.append(drift.deposition)
            print(crop,i,drift.deposition)
        return vals    
         
    #create pandas dtaframe
    #drift_values = pd.DataFrame()
    #drift_values["FieldCrop"] = test_drift("Cereals, spring and winter")
    #drift_values["FruitCrops (early)"] = test_drift("FruitCrops (early)")
    #drift_values["FruitCrops (late)"] = test_drift("FruitCrops (late)")
    #drift_values["Grapevine (early)"] = test_drift("Grapevine (early)")
    #drift_values["Grapevine (late)"] = test_drift("Grapevine (late)")
    #drift_values["Hops"] = test_drift("Hops")
    #
    ##make plot
    #ax=drift_values.plot()
    #ax.set_xlabel("Distance [m]")
    #ax.set_ylabel("Deposition [%]")
    #ax.grid(True)
    #ax.set_ylim(0,30)
    
    drift = Drift(rautmann,croptypes,interception_table,step3_distances,FOCUS_WaterBody,"FruitCrops (early)",BBCH,DT50water=DT50water,DT50sediment=DT50sediment)
    drift.calc_Step123(application_rate=ApplRate,number_of_applications=1,approach = "Step1",waterbody="Step12 waterbody",distance=1)
    print(drift.summary)

    drift = Drift(rautmann,croptypes,interception_table,step3_distances,FOCUS_WaterBody,"FruitCrops (early)",BBCH,DT50water=DT50water,DT50sediment=DT50sediment)
    drift.calc_Step123(application_rate=ApplRate,number_of_applications=1,approach = "Step3",waterbody="Stream",distance=None)
    print(drift.summary)
    

run_ttest()