# -*- coding: utf-8 -*-
"""
Created on Fri Oct 19 09:05:32 2018

@author: smh
"""

import scipy
import scipy.stats
import matplotlib.pylab as plt
import numpy as np
import pandas as pd

# read data
result = pd.read_csv(r"C:\Users\smh\Desktop\res\results_gkb2.csv")


#for param in  ['CR_HS', 'CR_PM', 'local_HS', 'local_PM', 'MARS', 'WFDEI_HS',  'WFDEI_PM']:

year=2010

#for month in range(1,13,1):
#    
res = result[(result.year == year) ]

# get datasets
obs = [i for i,j in zip(res.obs,res.sim) if not pd.isna(i) and not pd.isna(j) ]
sim = [j for i,j in zip(res.obs,res.sim) if not pd.isna(i)and not pd.isna(j) ]


#obs = np.log(obs)
#sim = np.log(sim)

# makes stats
print("shapiro-test obs",scipy.stats.shapiro(obs)[1])
print("shapiro-test sim",scipy.stats.shapiro(sim)[1])
print("levene",scipy.stats.levene(obs,sim)[1])

print("t-test",scipy.stats.ttest_ind(obs,sim)[1])
print("ks-test",scipy.stats.ks_2samp(obs,sim)[1])


# plot data
fig = plt.figure()
ax = fig.add_subplot(211)
ax.hist(obs,alpha=.5,color="r",label="Observed")
ax.hist(sim,alpha=.5,color="b",label="simulated")
ax.set_xlabel("m$^3$/sec")
ax.set_ylabel("Frequency")
ax.grid(True)

ax.set_title(str(month))
plt.legend(loc=0)
ax = fig.add_subplot(212)
ax.plot(obs,alpha=.5,color="r",label="Observed")
ax.plot(sim,alpha=.5,color="b",label="simulated")
ax.set_ylabel("m$^3$/sec")
ax.set_xlabel("Time")
ax.grid(True)
    