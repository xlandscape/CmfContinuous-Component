# -*- coding: utf-8 -*-
"""
Created on Wed Sep 13 13:15:18 2017

@author: smh
"""
import cmf

from datetime import datetime,timedelta
import numpy as np

from matplotlib.colors import LightSource
import matplotlib.pyplot as plt
from matplotlib.sankey import Sankey
import matplotlib
from mpl_toolkits.axes_grid1 import make_axes_locatable
import matplotlib.lines as mlines
import matplotlib.patches as mpatches
from matplotlib import animation

from scipy.interpolate import griddata #TODO: solve: wrong numpy version ....
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.lines import Line2D
import matplotlib.animation as animation


class Plotting(object):
    def __init__(self):
        pass
    
    def FieldWaterBalance(self,sc,field_name,title="",fpath=None):
        
        database = sc.database
   
        #get values
        rain = sum([i.rain for i in database.DataRecords_fields if i.name == field_name])
        E = sum([i.Eact for i in database.DataRecords_plants if i.name == field_name])
        T = sum([i.Tact for i in database.DataRecords_plants if i.name == field_name])
        RO = sum([i.qsurf for i in database.DataRecords_fields if i.name == field_name])
        PERC = sum([i.qperc for i in database.DataRecords_fields if i.name == field_name])
        DRAIN = sum([i.qdrain for i in database.DataRecords_fields if i.name == field_name])
        Vsoil = [i.Vsoil for i in database.DataRecords_fields if i.name == field_name]
        dSoil =  sum([Vsoil[-1][i] -Vsoil[0][i] for i in range(len(Vsoil[0]))])
        
        GW_GW = sum([i.qgw_gw for i in database.DataRecords_fields if i.name == field_name])
        GW_RIVER = sum([i.qgw_river for i in database.DataRecords_fields if i.name == field_name])


    	 # print water balance
        print("%s: Rain %.0fmm, E %.0fmm, T %.0fmm, RO %.0fmm, DRAIN %.0fmm, PERC %.2fmm dSoil %.0fmm, GW_GW %.0fmm, GW_RIVER %.0fmm"%(field_name,rain,E,T,RO,DRAIN,PERC,dSoil,GW_GW,GW_RIVER))
           



        # calc summary flows
        ET = E+T
        GW = GW_GW + GW_RIVER
        RO_DRAIN = RO+DRAIN
        
        # calc fractions
        RO_perc = RO/rain
        DRAIN_perc = DRAIN/rain
        E_perc = E/rain
        T_perc = T/rain
        GW_GW_perc = GW_GW/rain
        GW_RIVER_perc = GW_RIVER/rain
        ET_perc = ET/rain
        GW_perc = GW/rain
        RO_DRAIN_perc = RO_DRAIN/rain
    
        # check if zero flows exists, because they are not allowed in sankey plot
        # incase of zero flows, a thin arrow is plotted with a zero label
        if T<=0:
            T_perc = 0.1
        if E<=0:
            E_perc = 0.1
        if RO<=0:
            RO_perc = 0.1
        if DRAIN<=0:
            DRAIN_perc = 0.1
        if RO_DRAIN<=0:
            RO_DRAIN_perc  =0.1
        if GW_GW<=0:
            GW_GW_perc = 0.1
        if GW_RIVER<=0:
            GW_RIVER_perc = 0.1
        

        #create figure
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1, xticks=[], yticks=[], title="")
        sankey = Sankey(ax=ax,unit=None)
        
        #create flows
        sankey.add(flows=[1, -1],
               orientations = [1,0],
               labels=["%.0f mm" % (rain) + "\n\n\n", ''], label="Rain",linewidth=0,fc="cornflowerblue")
        
        sankey.add(flows=[1, -ET_perc,-RO_DRAIN_perc,-GW_perc],
                   orientations = [0,1,0,-1],
                  prior=0,patchlabel="$\\Delta_{soil}$ " + "%.0f mm" % (dSoil),
                  connect=(1, 0), label="",linewidth=0,fc="tan")
        
        sankey.add(flows=[ET_perc, -E_perc,-T_perc],
                   orientations = [0,0,0],
                  prior=1,
                  connect=(1, 0), label="",linewidth=0,fc="tan")
        
        sankey.add(flows=[T_perc,-T_perc],
                   orientations = [0,0],
                  prior=2,
                  connect=(2, 0), label="Transpiration",labels=["","            %.0f mm" % (T)],linewidth=0,fc="green")
        
        sankey.add(flows=[E_perc,-E_perc],
                   orientations = [0,0],
                  prior=2,
                  connect=(1, 0), label="Evaporation",labels=["","%.0f mm            " % (E)],linewidth=0,fc="brown")
        
        sankey.add(flows=[GW_perc, -GW_GW_perc,-GW_RIVER_perc],
                   orientations = [0,0,0],
                  prior=1,
                  connect=(3, 0), label="",linewidth=0,fc="tan")
        
        sankey.add(flows=[GW_GW_perc,-GW_GW_perc],
                   orientations = [0,0],
                  prior=5,
                  connect=(1, 0), label="GW - GW",labels=["","          %.0f mm" % (GW_GW)],linewidth=0,fc="lightblue")
        
        sankey.add(flows=[GW_RIVER_perc,-GW_RIVER_perc],
                   orientations = [0,0],
                  prior=5,
                  connect=(2, 0), label="GW - river",labels=["","%.0f mm          " % (GW_RIVER)],linewidth=0,fc="steelblue")
        
        sankey.add(flows=[RO_DRAIN_perc, -RO_perc,-DRAIN_perc],
                   orientations = [0,0,0],
                  prior=1,
                  connect=(2, 0), linewidth=0,fc="tan")
        
        sankey.add(flows=[RO_perc,-RO_perc],
                   orientations = [0,0],
                  prior=8,
                  connect=(1, 0), label="Runoff",linewidth=0,labels=["","         %.0f mm\n"%(RO)],fc="orange")
        
        # third
        sankey.add(flows=[DRAIN_perc,-DRAIN_perc],
                   orientations = [0,0],
                  prior=8,
                  connect=(2, 0), label="Drainage",linewidth=0,labels=["","\n               %.0f mm"%(DRAIN)],fc="yellow")
        
        #make legends and save figure
        sankey.finish()
        ax.legend(bbox_to_anchor=(0.00, 0.85, 1., .102),ncol=1,frameon=True,fontsize=8)    
        
        ax.text(0.75,0.95,field_name,  transform=ax.transAxes,
        verticalalignment='bottom', horizontalalignment='left',
            color='k', fontsize=8, 
            bbox=dict(facecolor='darkgoldenrod', edgecolor='None', 
                      boxstyle='round,pad=.2',alpha=.5))      
        if not fpath == None: fig.savefig(fpath,dpi=300)
        
        return fig
        
#
        
        
    def WaterFlows(self,sc,outlet_name = "Outlet",gw_name= "Groundwater",title="",fpath=None):
        
        database = sc.database
        #get time index
        time = [i.time for i in database.DataRecords_outlets if i.name == outlet_name]
        #get volume of outlet and groundwater storage
        outlet_vol = [i.volume for i in database.DataRecords_outlets if i.name == outlet_name]
        gw_vol = [i.volume for i in database.DataRecords_gws if i.name == gw_name]
    
        #get flow of outlet and groundwater storage
        outlet_flow = [i.flow / 86400 for i in database.DataRecords_outlets if i.name == outlet_name]
        gw_flow = [i.flow / 86400 for i in database.DataRecords_gws if i.name == gw_name]
    
        #make figure
        fig = plt.figure(figsize=(10,6))
        
        #add subplot and format axis
        ax = fig.add_subplot(1, 1, 1)
        ax.plot(time,outlet_vol,color="lightblue")
        ax.plot(time,gw_vol,color="darkblue")
        ax.set_xlabel("Time [h]")
        ax.set_ylabel("Volume [m$^3$]")
        ax.grid(True)
    
        #make lineplot of reaches
        ax2=ax.twinx()
        ax2.plot(time,outlet_flow,color="lightblue",linestyle="--")
        ax2.plot(time,gw_flow,color="darkblue",linestyle="--")
        ax2.set_ylabel("Flow [m$^3$ sec$^{-1}$]")
    
        # create legend    
        outlet_vol = mlines.Line2D([],[],color='lightblue', label="Outlet volume",alpha=1,linewidth=1,linestyle="-")
        outlet_flow = mlines.Line2D([],[],color='lightblue', label="Outlet flow",alpha=1,linewidth=1,linestyle="--")
        gw_vol = mlines.Line2D([],[],color='darkblue', label="Groundwater volume",alpha=1,linewidth=1,linestyle="-")
        gw_flow = mlines.Line2D([],[],color='darkblue', label="Groundwater flow",alpha=1,linewidth=1,linestyle="--")
        plt.legend(handles=[outlet_vol,outlet_flow,gw_vol,gw_flow],ncol=2,
                       bbox_to_anchor=(0.00, 0.9, 1., .102),fontsize="small",frameon=True)


    def soil_SoluteConc(self,catchment,field,concminmax,loadminmax,fpath=None):
        
        
        fig = plt.figure(figsize=(10, 8))
        concsoil = [i.concsoil for i in catchment.database.DataRecords_fields if i.name == field]
        loadsoil = [i.loadsoil for i in catchment.database.DataRecords_fields if i.name == field]
#        Vsoil = [i.Vsoil for i in catchment.database.DataRecords_fields if i.name == field]
        
        
        
        
        #plot water abstraction
        ax = fig.add_subplot(211)
        im=ax.imshow(np.transpose(concsoil),aspect="auto",cmap=plt.cm.CMRmap_r,vmin=concminmax[0],vmax=concminmax[1])


        ax.set_ylabel("Layer")
        ax.set_xlabel("DAS")       
        im.cmap.set_over("k")
        divider = make_axes_locatable(ax)
        cax = divider.append_axes('bottom', size='10%', pad=0.5)
        cb = fig.colorbar(im,cax=cax, orientation='horizontal')
        
        cb.set_label("Conc Mikrogramm/L") #g/m3 = 1000 Mikrogramm/L
        ax.grid()
        ax.set_xlim(0,365)
        
        
        
        #plot water abstraction
        ax = fig.add_subplot(212)
        im=ax.imshow(np.transpose(loadsoil),aspect="auto",cmap=plt.cm.CMRmap_r,vmin=loadminmax[0],vmax=loadminmax[1])
        ax.set_ylabel("Layer")
        ax.set_xlabel("DAS")       
        im.cmap.set_over("k")
        divider = make_axes_locatable(ax)
        cax = divider.append_axes('bottom', size='10%', pad=0.5)
        cb = fig.colorbar(im,cax=cax, orientation='horizontal')
        
        cb.set_label("[g/ha]") #g/m3 = 1000 Mikrogramm/L
        ax.grid()
        ax.set_xlim(0,365)
        
        plt.tight_layout()
        if not fpath == None:
#            plt.close("all")
            fig.savefig(fpath,dpi=300,transparent=True) 
            
            

    def SoluteConc(self,database,catchment,outlet_name,gw_name,title="",fpath=None):
        
        concoutlet = [i.conc for i in database.DataRecords_outlets if i.name == outlet_name]

        gw_catchment = [i.conc for i in database.DataRecords_gws if i.name == gw_name]
        
        
        
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        ax.plot(concoutlet,label="outlet",color="b")
        ax.plot(gw_catchment,label="gw",color="g")
        
        ax.set_ylim(0,1)

        
        ax.set_xlabel("Time [h]")
        ax.set_ylabel("Concentration [mg L$^{-1}$]")

        #ax.set_ylim(0,50)
        plt.legend(bbox_to_anchor=(0.00, 0.9, 1., .102),frameon=False)
        if not fpath == None:
            plt.tight_layout()
#            plt.close("all")
            fig.savefig(fpath,dpi=300,transparent=True) 
            
#    def WaterNetwork_withValues(self,catchment,t,vmin=0.0,vmax=10.):
#        # get catchment components to draw geometry
#        reaches =  catchment.reaches
#        reaches_names = [i.name for i in catchment.reaches]
#        catchmentoutlet = catchment.catchmentoutlet
#        
#        # get values for coloring
#        vals = []
#        for n in reaches_names:
#            val = [i.depth for i in catchment.database.DataRecords_reaches if (i.name == n) and (i.time == t) ][0]
#            vals.append(val)      
#        val_outlet = [i.volume for i in catchment.database.DataRecords_outlets if (i.name == "CatchmentOutlet") and (i.time == t) ][0]
#        
#        #create figure object and color map
#        fig = plt.figure()
#        ax = fig.add_subplot(1, 1, 1)
#        ax.set_xlim(0,50)
#        ax.set_ylim(0,50)
#        ax.grid(True)    
#        cmap = matplotlib.cm.get_cmap('jet')
#        norm = matplotlib.colors.Normalize(vmin=0.0, vmax=.1)
#    
#        # plot reaches    
#        for reach,value in zip(reaches,vals):    
#            if not (reach.downstream=="CatchmentOutlet"):        
#                downstream_reach = reaches[[i.name for i in reaches].index(reach.downstream)] 
#                ax.plot([reach.x,downstream_reach.x],[reach.y,downstream_reach.y],color=cmap(norm(value))) 
#            else:
#                ax.plot([reach.x,catchmentoutlet.x],[reach.y,catchmentoutlet.y],color=cmap(norm(value)))  
#        
#        #plot catchment outlet
#        ax.plot([catchmentoutlet.x,catchmentoutlet.x],[catchmentoutlet.y,catchmentoutlet.y],linestyle="",marker="o",markersize=20,color=cmap(norm(val_outlet)))
#        ax.set_xlabel("X COORD")
#        ax.set_ylabel("Y COORD")
#        ax.text(0.95, 0.9, t,
#                verticalalignment='bottom', horizontalalignment='right',
#                transform=ax.transAxes,
#                color='k', fontsize=9, 
#                bbox=dict(facecolor='0.7', edgecolor='None', boxstyle='round,pad=.5',alpha=.5))
#        divider = make_axes_locatable(ax)
#        cax = divider.append_axes('right', size='5%', pad=0.05)
#        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
#        sm._A = []
#        fig.colorbar(sm,cax=cax, orientation='vertical')


    def CatchmentMap(self,catchment,title="",fpath=None,withnames=False,
                     fontsize=7,fontcolor="w"):
   

         # get catchment components to draw geometry
        reaches =  catchment.reaches
        catchmentoutlet = catchment.outlet
        fields =  catchment.fields
        
        #create figure object and color map
        fig = plt.figure(figsize=(12,12))
        ax = fig.add_subplot(111)#, projection="3d")
        ax.set_xlabel("X [m]")
        ax.set_ylabel("Y [m]")
        ax.grid(True)    


        color_waterbody = "blue"


#         plot reaches    
        for reach in reaches:    
            if not (reach.Downstream=="Outlet"):        
                downstream_reach = reaches[[i.Name for i in reaches].index(reach.Downstream)] 
                ax.plot([reach.x,downstream_reach.x],[reach.y,downstream_reach.y],color=color_waterbody) 
                if withnames:
                    x_coord = (reach.x+downstream_reach.x)/2. 
                    y_coord = (reach.y+downstream_reach.y)/2. 
                    ax.text(x_coord,y_coord,reach.Name, verticalalignment='bottom', horizontalalignment='right',
                            color=fontcolor, fontsize=fontsize, 
                            bbox=dict(facecolor=color_waterbody, edgecolor='None', boxstyle='round,pad=.2',alpha=.5))
            else:
                ax.plot([reach.x,catchmentoutlet.x],[reach.y,catchmentoutlet.y],color=color_waterbody) 
                if withnames:
                    x_coord = (reach.x+catchmentoutlet.x)/2. 
                    y_coord = (reach.y+catchmentoutlet.y)/2. 
                
                    ax.text(x_coord,y_coord,reach.Name, verticalalignment='bottom', horizontalalignment='right',
                        color=fontcolor, fontsize=fontsize, 
                        bbox=dict(facecolor=color_waterbody, edgecolor='None', boxstyle='round,pad=.2',alpha=.5))


        #plot catchment outlet
        ax.plot([catchmentoutlet.x,catchmentoutlet.x],[catchmentoutlet.y,catchmentoutlet.y],linestyle="",marker="o",markersize=7,color="dodgerblue")
        ax.text(catchmentoutlet.x,catchmentoutlet.y,catchmentoutlet.Name, verticalalignment='bottom', horizontalalignment='right',
                        color=fontcolor, fontsize=fontsize, 
                        bbox=dict(facecolor='dodgerblue', edgecolor='None', boxstyle='round,pad=.2',alpha=.5))



        color_cells = "saddlebrown"
#
####        plot fields
        for field in fields:
           
            ax.plot([field.x,field.x],
                    [field.y,field.y],linestyle="",marker="o",
                    markersize=7,color=color_cells)
            ax.text(field.x,field.y,field.key, 
                    verticalalignment='bottom', horizontalalignment='right',
                        color=fontcolor, fontsize=fontsize, 
                        bbox=dict(facecolor=color_cells, edgecolor='None', 
                                  boxstyle='round,pad=.2',alpha=.5))

            if field.river != None:
                
                downstream_reach = reaches[[i.Name for i in reaches].index(field.river.Name)] 
                ax.plot([field.x,downstream_reach.x],[field.y,downstream_reach.y],linestyle="--",linewidth=2,color=color_cells) 

            if field.adjacent_field != None:
                downstream_field = fields[[i.key for i in fields].index(field.adjacent_field.key)] 
                ax.plot([field.x,downstream_field.x],[field.y,downstream_field.y],linestyle="--",linewidth=2,color=color_cells) 



        #plot dem from coords
        x=[]
        y=[]
        z = []
        for field in fields:
            x.append(field.x)
            y.append(field.y)
            z.append(field.z)
        
        for reach in reaches:
            x.append(reach.x)
            y.append(reach.y)
            
            z.append(reach.z)
        
        try:        
            resX=100
            resY=100        
            xi = np.linspace(min(x), max(x), resX)
            yi = np.linspace(min(y), max(y), resY)        
            zi = griddata((x, y), z, (xi[None,:], yi[:,None]),method="cubic")
            hdl = ax.contourf(xi,yi,zi,15,cmap=plt.cm.gist_earth,alpha=.9)
            datco = [0.1, 0.1, 0.2,0.05]
            cbar_ax = fig.add_axes(datco)
            cb1 = plt.colorbar(hdl, cax=cbar_ax, orientation='horizontal')
            cb1.set_label("Altitude (m)")
        except:
            print("ERROR: Could not plot elevation model.")


##        
#        
        if not fpath == None:
            plt.tight_layout()
#            plt.close("all")
            fig.savefig(fpath,dpi=300,transparent=True) 

#
#
    def SolverUnitsMap(self,catchment,solverunits,title="",
                       fpath=None,withnames=False,
                       fontsize=8):
   
         # get catchment components to draw geometry
        reaches =  catchment.reaches
        catchmentoutlet = catchment.outlet
        fields =  catchment.fields
        
        
        
        # create colors for all sub-catchments#
        # create array with shuffled numbers

        unique_su = np.unique([i.solverunitID for i in solverunits])
#        np.random.shuffle(unique_su)
        vmin=1
        vmax = max(range(len(unique_su)))+1
        norm = matplotlib.colors.Normalize(vmin=vmin, vmax=vmax)
        cmap = matplotlib.cm.get_cmap('Set1')
        colors_su = dict(zip(unique_su,[cmap(norm(i+1)) for i in range(len(unique_su))]))

        
        #create figure object and color map
        fig = plt.figure(figsize=(12,12))
        ax = fig.add_subplot(111)#, projection="3d")
        ax.set_xlabel("X [m]")
        ax.set_ylabel("Y [m]")
        ax.grid(True)    


        
        
#         plot reaches    
        for reach in reaches:    
            
            # get color
            subcatch_id = [i.solverunitID for i in solverunits if i.key == reach.Name][0]
            rgba = colors_su[subcatch_id]
            
            if not (reach.Downstream=="Outlet"):        
                downstream_reach = reaches[[i.Name for i in reaches].index(reach.Downstream)] 
                ax.plot([reach.x,downstream_reach.x],[reach.y,downstream_reach.y],color=rgba,linewidth=5) 
                if withnames:
                    x_coord = (reach.x+downstream_reach.x)/2. 
                    y_coord = (reach.y+downstream_reach.y)/2. 
                    ax.text(x_coord,y_coord,reach.Name, verticalalignment='bottom', horizontalalignment='right',
                            color='k', fontsize=fontsize, 
                            bbox=dict(facecolor=rgba, edgecolor='None', boxstyle='round,pad=.2',alpha=.5))
            else:
                ax.plot([reach.x,catchmentoutlet.x],[reach.y,catchmentoutlet.y],color=rgba,linewidth=5,linestyle="--") 
                if withnames:
                    x_coord = (reach.x+catchmentoutlet.x)/2. 
                    y_coord = (reach.y+catchmentoutlet.y)/2. 
                
                    ax.text(x_coord,y_coord,reach.Name, verticalalignment='bottom', horizontalalignment='right',
                        color='k', fontsize=fontsize, 
                        bbox=dict(facecolor=rgba, edgecolor='None', boxstyle='round,pad=.2',alpha=.5))


        #plot catchment outlet
        ax.plot([catchmentoutlet.x,catchmentoutlet.x],[catchmentoutlet.y,catchmentoutlet.y],linestyle="",marker="o",markersize=7,color="dodgerblue")
        ax.text(catchmentoutlet.x,catchmentoutlet.y,catchmentoutlet.Name, verticalalignment='bottom', horizontalalignment='right',
                        color='k', fontsize=fontsize, 
                        bbox=dict(facecolor='dodgerblue', edgecolor='None', boxstyle='round,pad=.2',alpha=.5))





###        plot fields
        for field in fields:
        
            # get color
            subcatch_id = [i.solverunitID for i in solverunits if i.key == field.key][0]
            rgba = colors_su[subcatch_id]
            
            ax.plot([field.x,field.x],
                    [field.y,field.y],linestyle="",marker="o",
                    markersize=7,color=rgba)
            ax.text(field.x,field.y,field.key, 
                    verticalalignment='bottom', horizontalalignment='right',
                        color='k', fontsize=fontsize, 
                        bbox=dict(facecolor=rgba, edgecolor='None', 
                                  boxstyle='round,pad=.2',alpha=.5))

            if field.river != None:
                
                downstream_reach = reaches[[i.Name for i in reaches].index(field.river.Name)] 
                ax.plot([field.x,downstream_reach.x],[field.y,downstream_reach.y],linewidth=5,linestyle="--",color=rgba) 

            if field.adjacent_field != None:
                downstream_field = fields[[i.key for i in fields].index(field.adjacent_field.key)] 
                ax.plot([field.x,downstream_field.x],[field.y,downstream_field.y],linewidth=5,linestyle="--",color=rgba) 
#

        # plot legend
        legend_items = [ mlines.Line2D([],[],color=i[1], label=i[0],alpha=1,linewidth=5,linestyle="-") for i in colors_su.items()]
        legend_items += [mlines.Line2D([],[],color="k", label="Reach connection",alpha=1,linewidth=1,linestyle="-")]
        legend_items += [mlines.Line2D([],[],color="k", label="Cell connection",alpha=1,linewidth=1,linestyle="--")]

        plt.legend(loc=0,handles=legend_items,
                       bbox_to_anchor=(0.00, 0.9, 1., .102),fontsize=fontsize,frameon=True)









        if not fpath == None:
            plt.tight_layout()
#            plt.close("all")
            fig.savefig(fpath,dpi=300,transparent=True) 




  


    
    def substance_balance(self,sc,field,reaches,minmax,fpath):
        # load field balance
        loadsoil = [sum(i.loadsoil) for i in sc.database.DataRecords_fields if i.name == field]  
        loadgw = [i.loadgw for i in sc.database.DataRecords_fields if i.name == field]   
        loadsw = [i.loadsw for i in sc.database.DataRecords_fields if i.name == field]
        loaddrainage = [i.loaddrainage for i in sc.database.DataRecords_fields if i.name == field]
        #load river and outlet
        load_reaches = []
        for reach in reaches:
            load_reaches.append([i.load for i in sc.database.DataRecords_reaches if i.name == reach]  )
 
        loadoutlet = [i.load for i in sc.database.DataRecords_outlets if i.name == sc.outlet.Name]  
        #get conc
        concsoil = [sum(i.concsoil) for i in sc.database.DataRecords_fields if i.name == field]  
        concgw = [i.concgw for i in sc.database.DataRecords_fields if i.name == field]   
        concsw = [i.concsw for i in sc.database.DataRecords_fields if i.name == field]
        concdrainage = [i.concdrainage for i in sc.database.DataRecords_fields if i.name == field]
        #load river and outlet
        conc_reaches = []
        for reach in reaches:
            conc_reaches.append([i.conc for i in sc.database.DataRecords_reaches if i.name == reach]  )  
        concoutlet = [i.conc for i in sc.database.DataRecords_outlets if i.name == sc.outlet.Name]  
        
        
        load_sum=[]
        i=0
     
        
        for s,gw,sw,drain,outl in zip(loadsoil,loadgw,loadsw,loaddrainage,loadoutlet):
#            print("s %.2f gw %.2f sw %.2f drain %.2f outlet %.2f r1 %.2f r2 %.2f sum %.2f"%(s,gw,sw,drain,outl,r1,r2,sum([s,gw,sw,drain,outl,r1,r2])))
            sum_reaches = sum([r[i] for r in load_reaches])
            load_sum.append(sum([s,gw,sw,drain,outl,sum_reaches]))
            i += 1
        
        fig = plt.figure(figsize=(10,10))
        ax = fig.add_subplot(311)
        ax.plot(concsoil,label="soil")
        ax.plot(concgw,label="gw")
        ax.plot(concsw,label="sw")
        ax.plot(concdrainage,label="drainage")
        for name,dat in zip(reaches,conc_reaches):
            ax.plot(dat,label=name)
        ax.plot(concoutlet,label="outlet")
        ax.legend(loc=0,ncol=2,fontsize=10)
        ax.set_ylabel("Conc ($\mu$/L)")
        
        ax = fig.add_subplot(312)
        ax.plot(loadsoil,label="soil")
        ax.plot(loadgw,label="gw")
        ax.plot(loadsw,label="sw")
        ax.plot(loaddrainage,label="drainage")
        for name,dat in zip(reaches,load_reaches):
            ax.plot(dat,label=name)        
        ax.plot(loadoutlet,label="outlet")        
        ax.legend(loc=0,ncol=2,fontsize=10)
        ax.set_xlabel("DOY")
        ax.set_ylabel("Load (g)")
        ax.set_ylim(minmax)
        
        
        
        ax = fig.add_subplot(313)
        ax.plot(load_sum,label="sum")
        ax.legend(loc=0,ncol=2,fontsize=10)
        ax.set_xlabel("DOY")
        ax.set_ylabel("Load (g)")
        ax.set_ylim(0,1000)
        ax.set_ylim(minmax)
        
        #        
        if not fpath == None:
            plt.tight_layout()
#            plt.close("all")
            fig.savefig(fpath,dpi=300,transparent=True) 







#
#
#













#    def CatchmentMap_3D(self,catchment,xlim,ylim,zlim,title="",fpath=None):
#   
#         # get catchment components to draw geometry
#        reaches =  catchment.reaches
#        catchmentoutlet = catchment.outlet
#        fields =  catchment.fields
#        meteos = catchment.p.meteo_stations
#        
#        #create figure object and color map
#        fig = plt.figure(figsize=(11,8))
#        ax = fig.add_subplot(111, projection="3d")
#        ax.set_xlim(100,0)
#        ax.set_ylim(100,0)
#        ax.set_zlim(zlim)
#        
#        ax.set_xlabel("X [m]")
#        ax.set_ylabel("Y [m]")
#        ax.grid(True)    
##        
###         plot reaches    
##        for reach in reaches:    
##            if not (reach.Downstream=="Outlet"):        
##                downstream_reach = reaches[[i.Name for i in reaches].index(reach.Downstream)] 
##                ax.plot([reach.x,downstream_reach.x],[reach.y,downstream_reach.y],color="lightblue") 
##                x_coord = (reach.x+downstream_reach.x)/2. 
##                y_coord = (reach.y+downstream_reach.y)/2.
##                
##                
##                
##                ax.text(x_coord,y_coord,reach.z,reach.Name, verticalalignment='bottom', horizontalalignment='right',
##                color='k', fontsize=8, 
##                bbox=dict(facecolor='lightblue', edgecolor='None', boxstyle='round,pad=.2',alpha=.5))
##            else:
##                ax.plot([reach.x,catchmentoutlet.x],[reach.y,catchmentoutlet.y],color="lightblue") 
##                x_coord = (reach.x+catchmentoutlet.x)/2. 
##                y_coord = (reach.y+catchmentoutlet.y)/2. 
##                ax.text(x_coord,y_coord,reach.z,reach.Name, verticalalignment='bottom', horizontalalignment='right',
##                        color='k', fontsize=8, 
##                        bbox=dict(facecolor='lightblue', edgecolor='None', boxstyle='round,pad=.2',alpha=.5))
##
##        #plot catchment outlet
##        ax.plot([catchmentoutlet.x,catchmentoutlet.x],[catchmentoutlet.y,catchmentoutlet.y],linestyle="",marker="o",markersize=7,color="dodgerblue")
##        ax.text(catchmentoutlet.x,catchmentoutlet.y,catchmentoutlet.z,catchmentoutlet.Name, verticalalignment='bottom', horizontalalignment='right',
##                        color='k', fontsize=8, 
##                        bbox=dict(facecolor='dodgerblue', edgecolor='None', boxstyle='round,pad=.2',alpha=.5))
####        plot fields
##        for field in fields:
##           
##            ax.plot([field.x,field.x],
##                    [field.y,field.y],linestyle="",marker="o",
##                    markersize=7,color="darkgoldenrod")
##            ax.text(field.x,field.y,field.z,field.name, 
##                    verticalalignment='bottom', horizontalalignment='right',
##                        color='k', fontsize=8, 
##                        bbox=dict(facecolor='darkgoldenrod', edgecolor='None', 
##                                  boxstyle='round,pad=.2',alpha=.5))
##
##            if field.river != None:
##                
##                downstream_reach = reaches[[i.Name for i in reaches].index(field.river.Name)] 
##                ax.plot([field.x,downstream_reach.x],[field.y,downstream_reach.y],linestyle="--",linewidth=0.5,color="darkgoldenrod") 
##
##            if field.adjacent_field != None:
##                downstream_field = fields[[i.name for i in fields].index(field.adjacent_field.name)] 
##                ax.plot([field.x,downstream_field.x],[field.y,downstream_field.y],linestyle="--",linewidth=0.5,color="darkgoldenrod") 
##
#
#            
#        #plot weather stations
#       
##        for meteo in meteos:
##            ax.plot([meteo.x,meteo.x],
##                    [meteo.y,meteo.y],linestyle="",marker="x",
##                    markersize=7,color="k")
##            ax.text(meteo.x,meteo.y,meteo.Name, 
##                    verticalalignment='bottom', horizontalalignment='right',
##                        color='k', fontsize=8, 
##                        bbox=dict(facecolor='k', edgecolor='None', 
##                                  boxstyle='round,pad=.2',alpha=.5))
#
#        # plot legend
#        legend_reach = mpatches.Patch(color='lightblue', label='River segment',alpha=1,linewidth=0)
#        legend_outlet = mpatches.Patch(color='dodgerblue', label='Catchment outlet',alpha=1,linewidth=0)
#        legend_field = mpatches.Patch(color='darkgoldenrod', label='Field',alpha=1,linewidth=0)
#        legend_meteo = mpatches.mlines.Line2D([],[],color='k', label='Meteostation',alpha=1,linewidth=0,marker="x")
#        plt.legend(handles=[legend_reach,legend_outlet,legend_field,legend_meteo],
#                   bbox_to_anchor=(0.00, 0.9, 1., .102),fontsize=8.,frameon=True,facecolor="w")
#        
#        #plot dem from coords
#        x=[]
#        y=[]
#        z = []
#        for field in fields:
#            x.append(field.x)
#            y.append(field.y)
#            z.append(field.z)
#        
#        for reach in reaches:
#            x.append(reach.x)
#            y.append(reach.y)
#            print(reach.z)
#            z.append(reach.z)
#        
#        
#        resX=100
#        resY=100
#        
#        xi = np.linspace(min(x), max(x), resX)
#        yi = np.linspace(min(y), max(y), resY)
#        
#        zi = griddata((x, y), z, (xi[None,:], yi[:,None]),method="cubic")
#
#
##        hdl = ax.contourf(xi,yi,zi,15,cmap=plt.cm.jet,alpha=.35)
#        
#
#
#        ls = LightSource(270, 45)
#        # To use a custom hillshading mode, override the built-in shading and pass
#        # in the rgb colors of the shaded surface calculated from "shade".
#
##        
##        hdl = ax.plot_surface(xi, yi, zi, alpha=.35, linewidth=0,cmap=plt.cm.jet,antialiased=True, 
##                shade=False,rstride=1, cstride=1,vmin=min(z),vmax=max(z))
##        
##        ax.set_zlim(min(z)-10,max(z)+10)
#
#        datco = [0.65, 0.15, 0.3,0.05]
#        cbar_ax = fig.add_axes(datco)
#        cb1 = plt.colorbar(hdl, cax=cbar_ax, orientation='horizontal')
#        cb1.set_label("Altitude (m)")
#        
##        
#        if not fpath == None:
#            plt.tight_layout()
##            plt.close("all")
#            fig.savefig(fpath,dpi=300,transparent=True) 
#
##        ax.view_init(15, 45)
##
#

    def CatchmentMap2(self,fig,t,catchment,parameter,xlims,ylims,reaches_min,reaches_max,fpath=None,cbar_label=""):
    

        ax1 = fig.add_axes([0.1,0.5,0.7,0.4]) # x,y, lenght, height

        # get values at timestept t
        reaches =  catchment.reaches
        reaches_names = [i.Name for i in catchment.reaches]
        catchmentoutlet = catchment.outlet
        vals_reaches = []
        for n in reaches_names:
            if parameter == "flow":
                val = [i.flow for i in catchment.database.DataRecords_reaches if (i.name == n) and (i.time == t) ][0]
            elif parameter == "conc":
                val = [i.conc for i in catchment.database.DataRecords_reaches if (i.name == n) and (i.time == t) ][0]
            elif parameter == "load":
                val = [i.load for i in catchment.database.DataRecords_reaches if (i.name == n) and (i.time == t) ][0]
            vals_reaches.append(val)      



        #create a colorbar
        cmap = matplotlib.cm.get_cmap('autumn_r')
        norm = matplotlib.colors.Normalize(vmin=reaches_min, vmax=reaches_max)

        # get catchment components to draw geometry
        reaches =  catchment.reaches
        catchmentoutlet = catchment.outlet
#        fields =  catchment.fields
#        meteos = catchment.p.meteo_stations


        # create map
        ax1.set_xlim(xlims)
        ax1.set_ylim(ylims)
        ax1.set_xlabel("X [m]")
        ax1.set_ylabel("Y [m]")
        ax1.grid(True)    
        # plot reaches  
        for reach,value in zip(reaches,vals_reaches):  
            if value > 0.0001:
                color=cmap(norm(value))
            else:
                color = "lightblue"
            if not (reach.Downstream=="Outlet"):        
                
                downstream_reach = reaches[[i.Name for i in reaches].index(reach.Downstream)] 
                ax1.plot([reach.x,downstream_reach.x],[reach.y,downstream_reach.y],color=color,linewidth=5) 
            else:
                ax1.plot([reach.x,catchmentoutlet.x],[reach.y,catchmentoutlet.y],color=color,linewidth=5)  

##        #plot catchment outlet
        ax1.plot([catchmentoutlet.x,catchmentoutlet.x],[catchmentoutlet.y,catchmentoutlet.y],linestyle="",marker="o",markersize=7,color="0.7")
        ax1.text(catchmentoutlet.x,catchmentoutlet.y,catchmentoutlet.Name, verticalalignment='bottom', horizontalalignment='right',
                        color='0.7', fontsize=10, 
                        bbox=dict(facecolor='0.7', edgecolor='None', boxstyle='round,pad=.2',alpha=.5))
        
        
#        #plot fields
#        for field in fields:
#            ax1.plot([field.x,field.x],
#                    [field.y,field.y],linestyle="",marker="o",
#                    markersize=7,color="0.7")
#            ax1.text(field.x,field.y,field.name, 
#                    verticalalignment='bottom', horizontalalignment='right',
#                        color='0.7', fontsize=10, 
#                        bbox=dict(facecolor='0.7', edgecolor='None', 
#                                  boxstyle='round,pad=.2',alpha=.5))
#        #plot weather stations
#        for meteo in meteos:
#            ax1.plot([meteo.x,meteo.x],
#                    [meteo.y,meteo.y],linestyle="",marker="x",
#                    markersize=7,color="0.7")
#            ax1.text(meteo.x,meteo.y,meteo.Name, 
#                    verticalalignment='bottom', horizontalalignment='right',
#                        color='0.7', fontsize=10, 
#                        bbox=dict(facecolor='0.7', edgecolor='None', 
#                                  boxstyle='round,pad=.2',alpha=.5))


#        if field.river != None:
#            
#            downstream_reach = reaches[[i.Name for i in reaches].index(field.river.Name)] 
#            ax1.plot([field.x,downstream_reach.x],[field.y,downstream_reach.y],linestyle="--",linewidth=0.5,color='0.7') 
#
#        if field.adjacent_field != "None":
#            downstream_field = fields[[i.name for i in fields].index(field.adjacent_field)] 
#            ax1.plot([field.x,downstream_field.x],[field.y,downstream_field.y],linestyle="--",linewidth=0.5,color='0.7') 

        

        divider = make_axes_locatable(ax1)
        cax = divider.append_axes('right', size='5%', pad=0.05)
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
        sm._A = []
        sm
        cb=fig.colorbar(sm,cax=cax, orientation='vertical')
        cb.set_label(cbar_label)

#
#        #get doy
#        doy = t.DOY()
#        #plot volume outlet and groundwater
#        ax2 = fig.add_axes([0.1,0.1,0.7,0.15]) # x,y, lenght, height
#        outlet_volume = [i.volume for i in catchment.database.DataRecords_outlets if i.name == "Outlet"]
#        ax2.plot(outlet_volume,label=catchment.outlet.Name)
#        ax2.set_xlabel("DAS")
#        ax2.set_ylabel("Outlet volume [m$^3$]")
#        ax2.set_ylim(0,max(outlet_volume))
#        ax2.set_xlim(0,365)
#        # plot vertical line which shows current day
#        ax2.plot([doy,doy],[0,max(outlet_volume)],"r-",linewidth=1)
#        

    
        ax1.text(0.8,0.9,"%04.0f-%02.0f-%02.0f: %02.0fh"%(t.year,t.month,t.day,t.hour),  transform=ax1.transAxes,
            verticalalignment='bottom', horizontalalignment='left',
                color='k', fontsize=10, 
                bbox=dict(facecolor='0.75', edgecolor='None', 
                          boxstyle='round,pad=.2',alpha=.5))      

#

        
        if not fpath == None:
#            plt.tight_layout()
            plt.close("all")
            fig.savefig(fpath,dpi=500,transparent=True) 
        
            fig.clf()







    def plot_PlantGrowth(self,database,field_name,title="",fpath=None):
    
        fig = plt.figure(figsize=(10, 8))
        #
 

        #get data from database
        rootdepth =[i.rootdepth for i in database.DataRecords_plants if i.name == field_name]
        soil_rootwateruptake = [i.soil_rootwateruptake for i in database.DataRecords_plants if i.name == field_name]
        soil_evaporation = [i.soil_evaporation for i in database.DataRecords_plants if i.name == field_name]
        LAI = [i.LAI for i in database.DataRecords_plants if i.name == field_name]
        GLAI = [i.GLAI for i in database.DataRecords_plants if i.name == field_name]
        Epot = [i.Epot for i in database.DataRecords_plants if i.name == field_name]
        Tpot = [i.Tpot for i in database.DataRecords_plants if i.name == field_name]
        Eact =[i.Eact for i in database.DataRecords_plants if i.name == field_name]   
        Tact = [i.Tact for i in database.DataRecords_plants if i.name == field_name]
       
        # plot LAI and GLAI
        ax = fig.add_subplot(5, 1, 1)
        ax.plot(GLAI,label="GLAI",linewidth=1,linestyle="-",markersize=1)
        ax.plot(LAI,label="LAI",linewidth=1,linestyle="-",markersize=1)
        ax.set_xticklabels([""])
        ax.set_ylabel("[m2/m2]")
        ax.set_xlim(0,365)
        ax.legend(loc=0)
        ax.grid()
        ax.set_title(title)
        
        # plot tpot,Epot,Eact,Tact
        ax = fig.add_subplot(5, 1, 2)
        ax.plot(Tpot,label="Tpot",linewidth=4,linestyle="-",markersize=1,color="g",alpha=.35)
        ax.plot(Epot,label="Epot",linewidth=4,linestyle="-",markersize=1,color="orange",alpha=.35)
        ax.plot(Tact,label="Tact",linewidth=1,linestyle="-",markersize=1,color="g")
        ax.plot(Eact,label="Eact",linewidth=1,linestyle="-",markersize=1,color="orange")
        ax.set_xticklabels([""])
        ax.set_ylabel("[mm]")
        ax.set_xticklabels([""])
        ax.legend(loc=0)
        ax.set_xlim(0,365)
        ax.grid()
        
        

        #plot rooting depth
        ax = fig.add_subplot(5, 1, 3)
        ax.plot([i*-1 if i>0 else 0 for i in rootdepth],label="rooting depth",linewidth=4,linestyle="-",markersize=1,color="g",alpha=.35)
        ax.set_ylabel("Depth [m]")
        ax.set_xticklabels([""])
        ax.legend(loc=0)
        ax.set_xlim(0,365)
        ax.grid()
        
        #plot water abstraction
        ax = fig.add_subplot(5, 1, 4)
        im=ax.imshow(np.transpose(soil_rootwateruptake),aspect="auto",cmap=plt.cm.gist_heat_r,vmin=0,vmax=5)
        ax.set_ylabel("Layer")
        ax.set_xlabel("DAS")       
        divider = make_axes_locatable(ax)
        cax = divider.append_axes('bottom', size='10%', pad=0.5)
        cb = fig.colorbar(im,cax=cax, orientation='horizontal')
        cb.set_label("Water uptake plant [mm]")
        ax.grid()
        ax.set_xlim(0,365)
        
        ax = fig.add_subplot(5, 1, 5)
        im=ax.imshow(np.transpose(soil_evaporation),aspect="auto",cmap=plt.cm.gist_heat_r,vmin=0,vmax=5)
        ax.set_ylabel("Layer")
        ax.set_xlabel("DAS")       
        divider = make_axes_locatable(ax)
        cax = divider.append_axes('bottom', size='10%', pad=0.5)
        cb = fig.colorbar(im,cax=cax, orientation='horizontal')
        cb.set_label("Evaporation [mm]")
        ax.grid()
        ax.set_xlim(0,365)

        

        if not fpath == None:
            plt.tight_layout()
#            plt.close("all")
            fig.savefig(fpath,dpi=300)



class SubplotAnimation(animation.TimedAnimation):
    def __init__(self,catchment,xlim,ylim,timeslot,monitor,rainsource,plotFieldValues,interval=50,skipflow=0.):
        
        self.monitor=monitor
        self.plotFieldValues = plotFieldValues
        self.catchment = catchment
        
        #######################################################################
        # create plots
        fig = plt.figure(figsize=(10, 10))
        ax0 = fig.add_axes([0.1,0.1,0.7,0.08]) # x,y, lenght, height
        ax1 = fig.add_axes([0.1,0.2,0.7,0.12]) # x,y, lenght, height
        ax2 = fig.add_axes([0.1,0.33,0.7,0.12]) # x,y, lenght, height
        ax3 = fig.add_axes([0.1,0.5,0.7,0.4]) # x,y, lenght, height
        self.ax0 = ax0
        self.ax3 = ax3
        
        #######################################################################
        # get data
        self.dates = [i.time for i in self.catchment.database.DataRecords_outlets if i.name == "Outlet"][timeslot[0]:timeslot[1]]
        self.days = [datetime(d.year,d.month,d.day).timetuple().tm_yday for d in self.dates]
        self.concs = []
        for m in self.monitor:
            self.concs.append([i.conc for i in self.catchment.database.DataRecords_reaches if (i.name == m)][timeslot[0]:timeslot[1]])
        #get flow of monitor reaches
        self.flows = []
        for m in self.monitor:
            self.flows.append([i.volume for i in self.catchment.database.DataRecords_reaches if (i.name == m)][timeslot[0]:timeslot[1]])
        #rainfall
        self.rainfall = [i.rain for i in self.catchment.database.DataRecords_fields if (i.name == rainsource)][timeslot[0]:timeslot[1]]

        #######################################################################
        #make plot for management
        self.line_management_state = Line2D([], [], color='red')
        ax0.add_line(self.line_management_state)
        ax0.set_xlim(min(self.days),max(self.days))
        ax0.set_ylim(0,1)
        ax0.set_xlabel('days')
        ax0.set_ylabel('')
        ax0.set_yticks([])
        legend_sowing = mpatches.Patch(color='green', label='Sowing',alpha=.5,linewidth=0)
        legend_psm = mpatches.Patch(color='orange', label='PSM',alpha=.5,linewidth=0)
        ax0.legend(handles=[legend_sowing,legend_psm],
                   bbox_to_anchor=(0.00, 0.9, 1., .102),fontsize=8.,frameon=True,facecolor="w")
        self.line_psm = []
        self.line_sowing = []

        #######################################################################
        # make empty line plot for flow
        norm = matplotlib.colors.Normalize(vmin=0, vmax=len(self.monitor)+1)
        cmap = matplotlib.cm.get_cmap('jet')
        
        self.line_flow_state = Line2D([], [], color='red')
        self.line_monitor_flow = []
        for m,monitor in enumerate(self.monitor):
            line_flow = Line2D([], [],label=monitor,alpha=0.75,linewidth=3,color=cmap(norm(m)))    
            ax1.add_line(line_flow)
            self.line_monitor_flow.append(line_flow)
        ax1.add_line(self.line_flow_state)
        ax1.set_xlim(min(self.days),max(self.days))
        ax1.set_ylim(0,np.max(self.flows))
        ax1.set_xlabel('')
        ax1.set_ylabel('[m$^3$ day$^{-1}$]')
        ax1.set_xticks([])
        ax1.legend(loc=4,fontsize=8)
        
        #######################################################################
        # create second axis for rainfall
        ax4 = ax1.twinx()
        ax4.set_xlabel('')
        ax4.set_ylabel('[mm]')
        ax4.set_xticks([])
        ax4.set_xlim(min(self.days),max(self.days))
        ax4.set_ylim(0,max(self.rainfall))
        self.line_rainfall = Line2D([], [], color='black',label="rainfall",alpha=0.25,linewidth=3)
        ax4.add_line(self.line_rainfall)
        ax4.legend(loc=1,fontsize=8)
        
        #######################################################################
        self.line_monitor_conc = []
        for m,monitor in enumerate(self.monitor):
            line_conc = Line2D([], [],label=monitor,alpha=0.75,linewidth=3,color=cmap(norm(m)))    
            ax2.add_line(line_conc)
            self.line_monitor_conc.append(line_conc)
        #make empy lineplot for concentration
        self.line_conc_state = Line2D([], [], color='red')
        ax2.add_line(self.line_conc_state)
        ax2.set_xlim(min(self.days),max(self.days))
        ax2.set_ylim(0,np.max(self.concs))
        ax2.set_xlabel('')
        ax2.set_ylabel('[µg L$^{-1}$]')
        ax2.set_xticks([])
        ax2.legend(loc=1,fontsize=8)

        #make empty linplot for catchment map
        self.line_outlets = Line2D([], [], color='black')
        ax3.add_line(self.line_outlets)
        self.line_reaches = [Line2D([], []) for reach in catchment.reaches]
        for line2d in self.line_reaches:
            ax3.add_line(line2d)
        ax3.set_xlim(xlim)
        ax3.set_ylim(ylim)
        
        #get min/max values of reaches
        vals_reaches = [i.conc for i in catchment.database.DataRecords_reaches]
        self.norm = matplotlib.colors.Normalize(vmin=min(vals_reaches), vmax=max(vals_reaches))
        self.cmap = matplotlib.cm.get_cmap('jet')

        #create colorbar
        divider = make_axes_locatable(ax3)
        cax = divider.append_axes('right', size='5%', pad=0.05)
        sm = plt.cm.ScalarMappable(cmap=self.cmap, norm=self.norm)
        sm._A = []
        sm
        cb=fig.colorbar(sm,cax=cax, orientation='vertical')
        cb.set_label("Concentration [µ L$^{-1}$]")
        
                #init catchment
        self.init_catchment_map()
        
        #plot legend
        if self.plotFieldValues:
            self.ax3.text(0.6,0.05,"Field losses: \nID  Runoff  Drainage  Groundwater",  transform=self.ax3.transAxes,
            verticalalignment='bottom', horizontalalignment='left',
                color='0.25', fontsize=10, 
                bbox=dict(facecolor='0.75', edgecolor='None', 
                          boxstyle='round,pad=.2',alpha=.5))  
    
        animation.TimedAnimation.__init__(self, fig, interval=interval, blit=True)

    def _draw_frame(self, framedata):
        t=framedata
        doy = datetime(t.year,t.month,t.day).timetuple().tm_yday
        
        #plot flow
        for line2d,flow in zip(self.line_monitor_flow,self.flows):
            line2d.set_data(self.days,flow)
        self.line_flow_state.set_data([doy,doy],[0,np.max(self.flows)])
        
        #plot rainfall
        self.line_rainfall.set_data(self.days,self.rainfall)
        
        #plot concentration
        for line2d,conc in zip(self.line_monitor_conc,self.concs):
            line2d.set_data(self.days,conc)

        self.line_conc_state.set_data([doy,doy],[0,np.max(self.concs)])
        
        #plot outlet
        self.plot_outlet(t)

        #plot reaches
        self.plot_reaches(t)
        
        #plot mangement
        self.plot_management(self.ax0)
        self.line_management_state.set_data([doy,doy],[0,1])
    
        #plot time
        s="%04.0f-%02.0f-%02.0f: %02.0fh"%(t.year,t.month,t.day,t.hour)
        #del old time
        self.ax3.text(0.75,0.9,s,  transform=self.ax3.transAxes,
        verticalalignment='bottom', horizontalalignment='left',
            color='w', fontsize=10, 
            bbox=dict(facecolor='w', edgecolor='None', 
                      boxstyle='round,pad=.2',alpha=.5))    
        self.ax3.text(0.75,0.9,s,  transform=self.ax3.transAxes,
        verticalalignment='bottom', horizontalalignment='left',
            color='0.25', fontsize=10, 
            bbox=dict(facecolor='0.75', edgecolor='None', 
                      boxstyle='round,pad=.2',alpha=.5))    
        
        #plot field values
        if self.plotFieldValues:
            self.plot_fields(t)

        # draw artists
        self._drawn_artists = [self.line_flow_state,self.line_conc_state,self.line_outlets,self.line_management_state] + self.line_reaches + self.line_psm + self.line_sowing + self.line_monitor_flow + self.line_monitor_conc

    def new_frame_seq(self):        
        return self.dates
#        return iter(range(self.t.size))

    def _init_draw(self):
        lines = [self.line_flow_state,self.line_conc_state,self.line_outlets,self.line_management_state] + self.line_reaches  + self.line_psm + self.line_sowing + self.line_monitor_flow + self.line_monitor_conc
        for l in lines:
            l.set_data([], [])

    def plot_management(self,ax):
        #plot management
        #date,field,task,description
        for task in self.catchment.ManagementList:
            date_manage = task["date"].split("_")
            doy_manage = datetime(int(date_manage[0]),int(date_manage[1]),int(date_manage[2])).timetuple().tm_yday
            if task["task"] == "sowing":
                line_sowing = Line2D([doy_manage,doy_manage],[0,1], color='green',linewidth=3,alpha=.5)
                ax.add_line(line_sowing)
                self.line_sowing += [line_sowing]
            elif task["task"] == "ApplyPesticide":
                line_psm = Line2D([doy_manage,doy_manage],[0,1], color='orange',linewidth=3.,alpha=.5)                
                ax.add_line(line_psm)               
                self.line_psm += [line_psm]
        
    def plot_fields(self,t):
        
        for field in self.catchment.fields:
            
            #get field values
            RO = [i.qsurf for i in self.catchment.database.DataRecords_fields if (i.name == field.key) and (i.time == t)][0]
            DRAIN = [i.qdrain for i in self.catchment.database.DataRecords_fields if (i.name == field.key) and (i.time == t)][0]
            GW = [i.qgw_river for i in self.catchment.database.DataRecords_fields if (i.name == field.key) and (i.time == t)][0]
            
            #make string
            s = field.name + "  %03.0f  %03.0f  %03.0f"%(RO,DRAIN,GW)

            #delete old text
            self.ax3.text(field.x,field.y,s, 
                    verticalalignment='bottom', horizontalalignment='right',
                        color='w', fontsize=8, 
                        bbox=dict(facecolor='w', edgecolor='None', 
                                  boxstyle='round,pad=.2',alpha=.5))
            #print new text
            self.ax3.text(field.x,field.y,s, 
                    verticalalignment='bottom', horizontalalignment='right',
                        color='0.25', fontsize=8, 
                        bbox=dict(facecolor='0.7', edgecolor='None', 
                                  boxstyle='round,pad=.2',alpha=.5))
        
        

    def plot_outlet(self,t):
        value = [i.conc for i in self.catchment.database.DataRecords_outlets if (i.name == "Outlet") and (i.time == t) ][0]
        catchmentoutlet = self.catchment.outlet
        self.line_outlets.set_data([],[])
        self.line_outlets.set_data([catchmentoutlet.x,catchmentoutlet.x],[catchmentoutlet.y,catchmentoutlet.y])
        self.line_outlets.set_linestyle("")
        self.line_outlets.set_marker("o")
        self.line_outlets.set_markersize("10")
#        self.line_outlets.set_color(color=self.cmap(self.norm(value)))
        self.line_outlets.set_color(color="0.75")
        

    def plot_reaches(self,t):
        #get outlet
        catchmentoutlet = self.catchment.outlet
        # get values at timestept t
        reaches =  self.catchment.reaches
        reaches_names = [i.Name for i in reaches]
        vals_reaches = []
        for n in reaches_names:
            val = [i.conc for i in self.catchment.database.DataRecords_reaches if (i.name == n) and (i.time == t) ][0]
            vals_reaches.append(val)    
        #plot data
        for reach,value,line2d in zip(reaches,vals_reaches,self.line_reaches):    
            line2d.set_data([],[])
            if not (reach.Downstream=="Outlet"):        
                downstream_reach = reaches[[i.Name for i in reaches].index(reach.Downstream)] 
                line2d.set_data([reach.x,downstream_reach.x],[reach.y,downstream_reach.y])
                line2d.set_color(color=self.cmap(self.norm(value))) 
                line2d.set_linewidth(3)        
            else:
                line2d.set_data([reach.x,catchmentoutlet.x],[reach.y,catchmentoutlet.y])
                line2d.set_color(color=self.cmap(self.norm(value)))
                line2d.set_linewidth(3)
        
    def init_catchment_map(self):
        
        # get catchment components to draw geometry
        reaches =  self.catchment.reaches
        catchmentoutlet = self.catchment.outlet
        fields =  self.catchment.fields
        
        for reach in reaches:    
            if not (reach.Downstream=="Outlet"):        
                downstream_reach = reaches[[i.Name for i in reaches].index(reach.Downstream)] 
                x_coord = (reach.x+downstream_reach.x)/2. 
                y_coord = (reach.y+downstream_reach.y)/2. 
                self.ax3.text(x_coord,y_coord,reach.Name, verticalalignment='bottom', horizontalalignment='right',
                color='0.25', fontsize=8, 
                        bbox=dict(facecolor='0.7', edgecolor='None', 
                                  boxstyle='round,pad=.2',alpha=.5))
            else:
                x_coord = (reach.x+catchmentoutlet.x)/2. 
                y_coord = (reach.y+catchmentoutlet.y)/2. 
                self.ax3.text(x_coord,y_coord,reach.Name, verticalalignment='bottom', horizontalalignment='right',
                        color='0.25', fontsize=8, 
                        bbox=dict(facecolor='0.7', edgecolor='None', 
                                  boxstyle='round,pad=.2',alpha=.5))
                 
##        #plot catchment outlet
        self.ax3.text(catchmentoutlet.x,catchmentoutlet.y,catchmentoutlet.Name, verticalalignment='bottom', horizontalalignment='right',
                        color='0.25', fontsize=8, 
                        bbox=dict(facecolor='0.7', edgecolor='None', 
                                  boxstyle='round,pad=.2',alpha=.5))
        #plot fields
        for field in fields:
            self.ax3.plot([field.x,field.x],
                    [field.y,field.y],linestyle="",marker="o",
                    markersize=7,color="0.7")

            if field.river != None:                 
                downstream_reach = reaches[[i.Name for i in reaches].index(field.river.Name)] 
                self.ax3.plot([field.x,downstream_reach.x],[field.y,downstream_reach.y],linestyle="--",linewidth=0.5,color='0.7') 
            if field.adjacent_field != None:
                downstream_field = field.adjacent_field 
                self.ax3.plot([field.x,downstream_field.x],[field.y,downstream_field.y],linestyle="--",linewidth=0.5,color='0.7') 
    




