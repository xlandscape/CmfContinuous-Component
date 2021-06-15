# -*- coding: utf-8 -*-
"""
Created on Wed May 30 07:43:31 2018

@author: smh
"""


# create inflow
def q_manning(V,width,depth,lenght,n_manning,zmax,zmin):
    """
    Calculates the flow rate from a given water volume (m3) in the reach
    """
    # area (m)
    A = V / lenght
    # wetted perimeter (m)
    P = 2*depth+width
    # q manning (m3/sec)
    q = A * (A/P)**(2/3) * np.sqrt(((zmax-zmin)/lenght)/n_manning)
    return q

q_manning = q_manning(V=30,width=1,depth=.3,lenght=100,n_manning=0.035,zmax=1,zmin=0)
print(q_manning)