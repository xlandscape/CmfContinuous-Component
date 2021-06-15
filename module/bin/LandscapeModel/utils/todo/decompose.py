# -*- coding: utf-8 -*-
"""
Created on Fri Jul 26 14:18:07 2019

@author: smh
"""

 def decompose(series, frequency, s_window = 'periodic', log = False,  **kwargs):
        '''
        Decompose a time series into seasonal, trend and irregular components using loess, 
        acronym STL.
        https://www.rdocumentation.org/packages/stats/versions/3.4.3/topics/stl
    
        params:
            series: a time series
    
            frequency: the number of observations per “cycle” 
                       (normally a year, but sometimes a week, a day or an hour)
                       https://robjhyndman.com/hyndsight/seasonal-periods/
    
            s_window: either the character string "periodic" or the span 
                     (in lags) of the loess window for seasonal extraction, 
                     which should be odd and at least 7, according to Cleveland 
                     et al.
    
            log:    boolean.  take log of series
    
    
    
            **kwargs:  See other params for stl at 
               https://www.rdocumentation.org/packages/stats/versions/3.4.3/topics/stl
        '''
    
        df = pd.DataFrame()
        df['date'] = series.index
        if log: series = series.pipe(np.log)
        s = [x for x in series.values]
        length = len(series)
        s = r.ts(s, frequency=frequency)
        decomposed = [x for x in r.stl(s, s_window).rx2('time.series')]
        df['observed'] = series.values
        df['trend'] = decomposed[length:2*length]
        df['seasonal'] = decomposed[0:length]
        df['residuals'] = decomposed[2*length:3*length]
        return df    
    

    import pandas as pd
    
    from rpy2.robjects import r, pandas2ri
    import numpy as np
    from rpy2.robjects.packages import importr    
    import pandas as pd
    import numpy as np
    
    
#    obs_per_cycle = 52
#    observations = obs_per_cycle * 3
#    data = [v+2*i for i,v in enumerate(np.random.normal(5, 1, observations))]
#    tidx = pd.date_range('2016-07-01', periods=observations, freq='w')
#    ts = pd.Series(data=data, index=tidx)
#    df = decompose(ts, frequency=obs_per_cycle, s_window = 'periodic')    
#    df.set_index("date",inplace=True)
#        
#    df.plot(subplots=True)
    
    
##        

#    time = pstPrc.simulated.index.get_level_values(0)
#    gb = pstPrc.simulated["depth"].groupby([time.year,time.month,time.day])
#    Q2 = gb.quantile(.50)


#
#    ts = pstPrc.select_by_indices(params = ["depth"],  times=slice(None),  keys=["r381"])
#    ts.reset_index("key",inplace=True)
#    
#
#    df = decompose(ts["depth"], frequency=10*365*, s_window = 'periodic')    
#    df.set_index("date",inplace=True)
#        
#    df.plot(subplots=True)
#        
#    
##    
##    
#    
#    
#    
#    
#    
    
    
    
    
    
    
    
    
    