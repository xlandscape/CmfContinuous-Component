# -*- coding: utf-8 -*-
'''
'''

import pandas as pd
import numpy as np
#import spotpy.hydrology.signatures as sig
#import spotpy.objectivefunctions as obj
import matplotlib.pyplot as plt
import os
import matplotlib.lines as mlines


class Signatures():
    
    def __init__(self):            
        self.conversion_factor = 86400 # converts m³/day to m³/s
        self.hyd_year_start, self.hyd_year_end = 10, 9
        
    def check_data_inputs(self, simulated, observed):
        simulated = simulated.index.droplevel(1)
        sim_years = simulated.year.unique()
        
        observed = observed.index.droplevel(1)
        obs_years = observed.year.unique()
        
        n = 0
        for year in sim_years:
            if year in obs_years:
                n = n+1
        pct = int((n/len(sim_years))*100)
        del n
        print('Observation covers %s pct of simulation period' % pct)
        return pct
            
    def createFolder(self, directory):
        """
        Creates a folder
        
        @params: target directory
        
        """
        try:
            if not os.path.exists(directory):
                os.makedirs(directory)
        except OSError:
            print ('Error: Creating directory. ' + directory)
            
                           
    def plot_ObjectiveFunctions(self, fname, NSE_val, bias_val, r2_val, period, results_path):
        """
        plots the results of the objective functions
        
        @params: 
            self.fname = Name of project
            NSE_val = NSE list values for period*
            bias_val = bias list values for period*
            r2_val = r2 list values for period*
            period* = month or year
        
        """
        fig1 = plt.figure(1)
                
        plt.subplot(311)
        plt.scatter(*zip(*NSE_val), color='r')
        plt.grid(True)
        plt.ylabel('NSE')

        plt.subplot(312)
        plt.scatter(*zip(*bias_val), color='b')
        plt.grid(True)
        plt.ylabel('bias')
                     
        plt.subplot(313)
        plt.scatter(*zip(*r2_val),color='g')
        plt.grid(True)
        plt.ylabel('r²')
#        
        plt.savefig(os.path.join(results_path, 'OBJ_plots_%s_%s.png' % (fname, period)), dpi=150)
        plt.close(fig1)

        
    def plot_FDC(self, fname, simulated, observed, year, ylim, results_path):
        '''
            Calculates and plots a flow duration curve from x. 

        All observations/simulations are ordered and the empirical probability is
        calculated. This is then plotted as a flow duration curve. 

        When x has more than one dimension along axis, a range flow duration curve 
        is plotted. This means that for every probability a min and max flow is 
        determined
        '''
        
        sort_sim = np.sort(simulated)[::-1]
        exceedence_simulated = np.arange(1.,len(sort_sim)+1) / len(sort_sim)
        plt.plot(exceedence_simulated*100, sort_sim, label='simulated')
        plt.xlabel("Exceedence [%]")
        plt.ylabel("Flow rate")
        try:
            sort_observed = np.sort(observed)[::-1]
            exceedence_observed = np.arange(1.,len(sort_observed)+1) / len(sort_observed)
            plt.plot(exceedence_observed*100, sort_observed, label='observed')
        except:
            pass
        try:
            fname = "%s_%s" % (fname,year)
        except:
            pass
        try:
            plt.ylim(0,ylim)
        except:
            pass
        plt.xlabel("Exceedence [%]")
        plt.ylabel("Flow rate [m³/s]")
        plt.legend()
        plt.grid()
        plt.show()
        plt.savefig(os.path.join(results_path, 'FDC_%s.png' % fname), format="png")
        plt.close()
    
    def plot_FDC_single(self, fname, simulated, year, ylim, results_path):
        '''
        Calculates and plots a flow duration curve from x. 

        All simulations are ordered and the empirical probability is
        calculated. This is then plotted as a flow duration curve. 

        When x has more than one dimension along axis, a range flow duration curve 
        is plotted. This means that for every probability a min and max flow is 
        determined
        '''
        
        sort_sim = np.sort(simulated)[::-1]
        exceedence_simulated = np.arange(1.,len(sort_sim)+1) / len(sort_sim)
        plt.plot(exceedence_simulated*100, sort_sim, label='simulated')
        plt.xlabel("Exceedence [%]")
        plt.ylabel("Flow rate")
        try:
            fname = "%s_%s" % (fname,year)
        except:
            pass
        try:
            plt.ylim(0,ylim+0.1)
        except:
            pass
        plt.xlabel("Exceedence [%]")
        plt.ylabel("Flow rate [m³/s]")
        plt.legend()
        plt.grid()
        plt.show()
        plt.savefig(os.path.join(results_path, 'FDC_%s.png' % fname), format="png")
        plt.close()
    
    def make_plot(self, fname, observed, df_sim, r_squared, NSE, results_path, rain=None):
        """
        plots the simulation results and observed flow as lineplot
        
        @params: 
            fname = str - Name of project
            observed = list - observed
            simulated = pd.DataFrame - simulated
            r_squared = float - r² value (used for box information)
            NSE = float - NSE value (used for box information)
            rain = pd.DataFrame - rainfall timeseries
      
        """        
        #read climate data
        # get
        begin = df_sim.index[0]
        end = df_sim.index[-1]
        
        
        fig = plt.figure(figsize=(10,7))
        
        
            
        try:
            rain = rain[(rain.index>=pd.Timestamp(begin))&(rain.index<=pd.Timestamp(end))]
            if rain.empty == False:
            
                r = rain.resample("24H").sum()/24
            
                #plot rainfall
                ax1 = fig.add_axes([0.1,0.7,0.8,0.2]) # x,y, lenght, height
                ax1.bar(r.index, r.rain.values,align='center',color="k")
                ax1.invert_yaxis()
                ax1.xaxis.tick_top()
                ax1.xaxis.set_ticks_position('both') # THIS IS THE ONLY CHANGE
                ax1.xaxis_date()
                ax1.grid(True)
                ax1.spines['bottom'].set_color('none')
                ax1.xaxis.set_ticks_position('top')
                ax1.set_ylabel("Rain [mm day$^{-1}$]")
                ax1.set_xlim(pd.Timestamp(begin),pd.Timestamp(end))    
                ax1.yaxis.tick_right()
                ax1.yaxis.set_label_position("right")
                legend_rain = mlines.Line2D([],[],color="k",label = "Rainfall")
        except:
            pass
        
        
        #plot strea, flow
        ax = fig.add_axes([0.1,0.2,0.8,0.5]) # x,y, lenght, height
        ax.plot(df_sim.index,observed.values,color="b",linestyle="--",label="Observed")

        ax.plot(df_sim.index,df_sim.values,color="r",label="Simulated", alpha=.8)
        
        # important if only simulated is available

        
        ax.set_xlim(pd.Timestamp(begin),pd.Timestamp(end))
        ymax = max(observed.values)+.1
        ax.set_ylim(0,ymax)
        ax.set_ylabel("Flow [m$^3$ sec$^{-1}$]")
        ax.set_yticks(np.arange(0,ymax,0.25))
        ax.grid(True)
        
        ax.spines['top'].set_color('none')
        ax.xaxis.set_ticks_position('bottom')
        #plot legend
        ax5  = fig.add_axes([0.1,0.1,0.8,0.1])# x,y, lenght, height
        
        legend_sim = mlines.Line2D([],[],color="red",label="Simulated")
        legend_obs = mlines.Line2D([],[],color="blue",label = "Observed")
        
        
        
        try:
            ax5.legend(handles=[legend_sim,legend_obs,legend_rain], ncol=3,bbox_to_anchor=(0.00, 0.5, 1., .102),fontsize=10.,frameon=True)
        except:
            ax5.legend(handles=[legend_sim,legend_obs], ncol=2,bbox_to_anchor=(0.00, 0.5, 1., .102),fontsize=10.,frameon=True)

            
        ax5.axis("off")        
        ax5.text(0.2, 0.1,"Gauging station"  + "\n"+ "r$^2$: "+"%.2f NSE: %.2f"%(r_squared,NSE),
                verticalalignment='bottom', horizontalalignment='left',
                transform=ax5.transAxes,
                color='k', fontsize=9, 
                bbox=dict(facecolor='0.7', edgecolor='None', boxstyle='round,pad=.5',alpha=.5))
        
        fig.autofmt_xdate() 
        fig.savefig(os.path.join(results_path, '%s_Plot.png' % fname), dpi=800)
        plt.close('all')
        del fig
            
        
    def make_plot_single(self, fname, df_sim, results_path, rain=None):
        """
        plots the simulation results and observed flow as lineplot
        
        @params: 
            fname = str - Name of project
            observed = list - observed
            simulated = pd.DataFrame - simulated
            r_squared = float - r² value (used for box information)
            NSE = float - NSE value (used for box information)
            rain = pd.DataFrame - rainfall timeseries
      
        """       
        #read climate data
        # get
        begin = df_sim.index[0]
        end = df_sim.index[-1]
                     
        try:
            
            rain = rain[(rain.index>=pd.Timestamp(begin))&(rain.index<=pd.Timestamp(end))]
            if rain.empty == False:
                fig = plt.figure(figsize=(10,7))
                r = rain.resample("24H").sum()/24
                             
                #plot rainfall
                ax1 = fig.add_axes([0.1,0.7,0.8,0.2]) # x,y, lenght, height
                ax1.bar(r.index, r.rain.values,align='center',color="k", label="Rainfall")
                ax1.invert_yaxis()
                ax1.xaxis.tick_top()
                ax1.xaxis.set_ticks_position('both') 
                ax1.xaxis_date()
                ax1.grid(True)
                ax1.spines['bottom'].set_color('none')
                ax1.xaxis.set_ticks_position('top')
                ax1.set_ylabel("Rain [mm day$^{-1}$]")
                ax1.set_xlim(pd.Timestamp(begin),pd.Timestamp(end))    
                ax1.yaxis.tick_right()
                ax1.yaxis.set_label_position("right")
                ax = fig.add_axes([0.1,0.2,0.8,0.5])
                ax.spines['top'].set_color('none')
            else:
                fig = plt.figure(figsize=(10,5))
                ax = fig.add_subplot(1, 1, 1)
            
        except:
            fig = plt.figure(figsize=(10,5))
            ax = fig.add_subplot(1, 1, 1)
            
        ax.plot(df_sim.index,df_sim.values,color="b",label="Simulated")
               
        ax.set_xlim(pd.Timestamp(begin),pd.Timestamp(end))
        ymax = max(df_sim.values)+.1
        ax.set_ylim(0,ymax)
        ax.set_ylabel("Flow [m$^3$ sec$^{-1}$]")
#        ax.set_yticks(np.arange(0,ymax,0.25))
        ax.grid(True)
                
        ax.xaxis.set_ticks_position('bottom')

        try: 
            ax1.legend()
            ax.legend()
        except:
            ax.legend()
            
            
        fig.autofmt_xdate() 
        fig.savefig(os.path.join(results_path, '%s_Plot.png' % fname), dpi=800)
        plt.close('all')
        del fig
        
    def calcBasicSig(self, simulated):
        """
        calculates the basic signatures using the SPOTPY libary
        
        @params: simulated = simulated flow as list
        """
    
        MeanFlow = sig.get_mean(simulated)
    
        Skewness = sig.get_skewness(simulated)
        
        Q001 = sig.get_q0_01(simulated)
        Q01 = sig.get_q0_1(simulated)    
        Q1 = sig.get_q1(simulated)
        Q5 = sig.get_q5(simulated)
        Q10 = sig.get_q10(simulated)
        Q20 = sig.get_q20(simulated)
        Q85 = sig.get_q85(simulated)
        Q95 = sig.get_q95(simulated)
        Q99 = sig.get_q99(simulated)
        SFDC = sig.get_sfdc(simulated)
        QVC = sig.get_qcv(simulated)
        QHF = sig.get_qhf(simulated)
        QLF = sig.get_qlf(simulated)
        QLV = sig.get_qlv(simulated)
        recession = sig.get_recession(simulated)
        zero_q = sig.get_zero_q_freq(simulated)
        baseflow_index = sig.get_bfi(simulated)
        
        return MeanFlow, Skewness, Q001, Q01, Q1, Q5, Q10, Q20, Q85, Q95, Q99,SFDC, QVC,QHF, QLF,QLV, recession,zero_q, baseflow_index



    def objectivefunction(self, observed, simulated):
        """
        calculates the objective functions using the SPOTPY libary
        
        @params: 
            observed = observed flow as list
            simulated = simulated flow as list
        """
        NSE = obj.nashsutcliffe(observed, simulated)
        bias = obj.bias(observed, simulated)
        r2 = obj.rsquared(observed, simulated)
        return NSE, bias, r2

               
    def calc_signatures(self, simulated_inp, observed_inp, gaugingstation, fname, results_path, rain=None):
        """
        calculates all basic signatures using the SPOTPY libary
        
        @params: 
            simulated_inp = pd.DataFrame - simulated values
            observed_inp = pd.DataFrame - observed values
            gaugingstation = str - Reach_ID used for selection in simulation DF
            fname = str - projekt name
            results_path = str - path where results are stored
            rain = pd DataFrame - rainfall data
        """

        print('compare_to_observed')
        
        new = []  
        df_sim = simulated_inp.xs(gaugingstation,level=1) 

        df_sim = df_sim.flow.resample('D').mean()/self.conversion_factor
                
        observed = observed_inp.xs(gaugingstation,level=1)            
        observed = observed.resample('D').mean()/self.conversion_factor
        
        observed = observed[(observed.index>=pd.Timestamp(df_sim.index[0]))&(observed.index<=pd.Timestamp(df_sim.index[-1]))]
              
        observed_values = observed.flow.values
        
        simulated = df_sim.values.tolist()
        ylim = max(simulated)
        year='All'
              
        self.plot_FDC(fname, simulated, observed_values, year, ylim, results_path)
        
        print(len(observed_values), len(simulated))
            
        NSE, bias, r2 = self.objectivefunction(observed_values, simulated)
            
        self.make_plot(fname, observed, df_sim, r2, NSE, results_path, rain)
       
        MeanFlow, Skewness, Q001, Q01, Q1, Q5, Q10, Q20, Q85, Q95, Q99, SFDC, QVC, QHF, QLF, QLV, recession,zero_q, baseflow_index  = self.calcBasicSig(simulated)
                                 
        new.append([fname, NSE, bias, r2, MeanFlow, Skewness, Q001, Q01, Q1, Q5, Q10, Q20, Q85, Q95, Q99,SFDC,QVC,QHF,QLF,QLV,recession,zero_q,baseflow_index])
        del df_sim, simulated, observed, observed_values, NSE, bias, r2
            
        columns = ['run_name','NSE', 'bias', 'r2', 'MeanFlow', 'Skewness', 'Q001', 'Q01', 'Q1', 'Q5', 'Q10', 'Q20', 'Q85', 'Q95', 'Q99','SFDC','QVC','QHF','QLF','QLV','recession', 'zero_q','baseflow_index']
        res = pd.DataFrame(new, columns=columns)
                        
        res.to_csv(os.path.join(results_path, 'Signatures_%s.csv' % fname), index=None)
        del new
           

    def calc_yearly_TS(self, simulated_inp, observed_inp, gaugingstation, fname, results_path):
       
        """
        calculates all basic signatures using the SPOTPY libary and plots flow duration curves for each year
        
        @params: 
            simulated_inp = pd.DataFrame - simulated values
            observed_inp = pd.DataFrame - observed values
            gaugingstation = str - Reach_ID used for selection in simulation DF
            fname = str - projekt name
            results_path = str - path where results are stored
            rain = pd DataFrame - rainfall data
        """
        print('calc_yearly_TS')
                
        new = []  

        NSE_val = []
        bias_val = []
        r2_val = []

        df_sim = simulated_inp.xs(gaugingstation,level=1)        
        df_sim = df_sim.flow.resample('D').mean()/self.conversion_factor
        
        ylim = max(df_sim.values.tolist())
                   
        years = df_sim.index.year.unique()           
        for year in years[:-1]:

            next_year = year + 1
            
            df_calc = df_sim['%s-%s'% (year,self.hyd_year_start) : '%s-09' % next_year]
            
            observed = observed_inp.xs(gaugingstation,level=1)            
            observed = observed.resample('D').mean()/self.conversion_factor
            observed = observed[(observed.index>=pd.Timestamp(df_calc.index[0]))&(observed.index<=pd.Timestamp(df_calc.index[-1]))]
            observed = observed.flow.values
            
            print(df_calc.dtypes)
            simulated = df_calc.values.tolist()
            
            self.plot_FDC(fname, simulated, observed, year, ylim, results_path)
            
            NSE, bias, r2 = self.objectivefunction(observed, simulated)
            MeanFlow, Skewness, Q001, Q01, Q1, Q5, Q10, Q20, Q85, Q95, Q99, SFDC, QVC, QHF, QLF, QLV, recession,zero_q, baseflow_index  = self.calcBasicSig(simulated)                
            
            print(year, len(observed), len(simulated), 'NSE:', NSE, 'bias:', bias, 'r²:', r2)
           
            NSE_val.append([year, NSE])
            bias_val.append([year, bias])
            r2_val.append([year, r2])
                                               
            new.append([fname, year, NSE, bias, r2, MeanFlow, Skewness, Q001, Q01, Q1, Q5, Q10, Q20, Q85, Q95, Q99,SFDC,QVC,QHF,QLF,QLV,recession,zero_q,baseflow_index])
            del df_calc, NSE, bias, r2, observed, simulated, year
            
        
        del NSE_val, bias_val, r2_val
                   
        columns = ['run_name','Year', 'NSE', 'bias', 'r2', 'MeanFlow', 'Skewness', 'Q001', 'Q01', 'Q1', 'Q5', 'Q10', 'Q20', 'Q85', 'Q95', 'Q99','SFDC','QVC','QHF','QLF','QLV','recession', 'zero_q','baseflow_index']
        res = pd.DataFrame(new, columns=columns)
                        
        res.to_csv(os.path.join(results_path, '%s_yearly_TS_to_obs.csv' % fname), index=None)
    
    
    def calc_signatures_sim_only(self, simulated_inp, gaugingstation, fname, results_path, rain=None):
        """
        calculates basic signatures for simulation timeseries without gauging data comparison using the SPOTPY libary
        
        @params: 
            simulated_inp = pd.DataFrame - simulated values
            gaugingstation = str - Reach_ID used for selection in simulation DF
            fname = str - projekt name
            results_path = str - path where results are stored
            rain = pd DataFrame - rainfall data
        """

        print('calculate simulation signatures')
        
        new = []  
        df_sim = simulated_inp.xs(gaugingstation,level=1) 

        df_sim = df_sim.flow.resample('D').mean()/self.conversion_factor
                
        
        simulated = df_sim.values.tolist()
        ylim = max(simulated)
        year='All'
              
        self.plot_FDC_single(fname, simulated, year, ylim, results_path)
                   
        self.make_plot_single(fname, df_sim, results_path, rain)
       
        MeanFlow, Skewness, Q001, Q01, Q1, Q5, Q10, Q20, Q85, Q95, Q99, SFDC, QVC, QHF, QLF, QLV, recession,zero_q, baseflow_index  = self.calcBasicSig(simulated)
                                 
        new.append([fname,MeanFlow, Skewness, Q001, Q01, Q1, Q5, Q10, Q20, Q85, Q95, Q99,SFDC,QVC,QHF,QLF,QLV,recession,zero_q,baseflow_index])
        del df_sim, simulated, ylim, year 
            
        columns = ['run_name','MeanFlow', 'Skewness', 'Q001', 'Q01', 'Q1', 'Q5', 'Q10', 'Q20', 'Q85', 'Q95', 'Q99','SFDC','QVC','QHF','QLF','QLV','recession', 'zero_q','baseflow_index']
        res = pd.DataFrame(new, columns=columns)
                        
        res.to_csv(os.path.join(results_path, 'Signatures_%s_single.csv' % fname), index=None)
        del new
