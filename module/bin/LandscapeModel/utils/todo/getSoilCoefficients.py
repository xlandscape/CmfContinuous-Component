# -*- coding: utf-8 -*-
"""
Created on Fri Oct 20 07:59:28 2017

@author: smh
"""
def get_vanGenuchtenMualem_HYPRES(c,s,om,topsoil,bd,pf):
    """
    Calculates vanGenuchten rention curve parameter n,alpha,Ksat
    
    c (double):         clay content (%)
    s (double):         silt content (%)
    bd (double):         buld density (g/cm³)
    om (double):        organic matte (%)
    topsoil (double):   indicates topsoil horizon (topsoil=1,subsoil=0)
    pf (double):        densitiy of material
    """
    d=bd
    alpha = -14.96 + 0.03135 * c + 0.0351*s + 0.646*om +15.29*d - 0.192*topsoil - 4.671*d**2 - 0.000781*c**2 - 0.00687*om**2 + 0.0449*om**(-1) + 0.0663*np.log(s) + 0.1482*np.log(om) - 0.04546*d*s - 0.4852*d*om +0.00673*topsoil*c
    n =  -25.23 - 0.02195 * c + 0.0074 * s - 0.1940 * om + 45.5 * d - 7.24 * d**2 + 0.0003658 * c**2 + 0.002885 *om**2 -12.81*d**(-1) - 0.1524 * s**(-1) - 0.01958 * om**(-1) - 0.2876*np.log(s) - 0.0709*np.log(om) - 44.6*np.log(d) - 0.02264*d*c + 0.0896*d*om + 0.00718*topsoil*c
    Ksat = 7.755 + 0.0352 * s + 0.93 * topsoil - 0.967 * d**2 - 0.000484 * c**2 - 0.000322 * s**2 + 0.001 * s**(-1) - 0.0748 * om**(-1) - 0.643*np.log(s) - 0.01398*d*c - 0.1673*d*om + 0.02986*topsoil*c -0.03305*topsoil*s
    if pf != None:
        phi = 1 - (bd / pf)
    else:
        phi = -9999
    
    alpha = np.exp(alpha)
    n = np.exp(n)+1
    Ksat = np.exp(Ksat )*24/10/100 # convert mm/h to m/day
    return (Ksat,alpha,n,phi)

def calc_theta_s(c,s,bd,Corg,topsoil,stones=0,stone_porosity = 10):
    """
    #Woesten + adjustment for stone content
    c (double):          clay content (%)
    s (double):          silt content (%)
    bd (double):         buld density (g/cm³)
    Corg (double):       Organic carbon (%)
    topsoil (integer):   indicates topsoil horizon (topsoil=1,subsoil=0)
    stones (double):     stone content (%)
    c (double):          clay content (%)
    """
    
    om = Corg *1.724
    theta_s=(1 -(stones/100 * (1 - stone_porosity/100) ) ) * ( 0.7919 + (0.001691 * c) - (0.29619 * bd) - (0.000001491 * (s**2 ) ) + (0.0000821 * (om**2 )) + (0.02427/c) + ( 0.01113/s ) + (0.01472 * np.log(s)) - (0.0000733 * Corg * 1.724 * c) - (0.000619 * bd * c) - (0.001183 * bd * Corg * 1.724 ) -  (0.0001664 * topsoil * s) ) * 100
    return theta_s


def calc_WATEN(fawc,c,s,bd,Corg,topsoil,RESID = 0,CTEN = 10):
    """
    Calculates vanGenuchten rention curve parameter n,alpha,Ksat
    fawc (double):       field water content plant stress
    c (double):         clay content (%)
    s (double):         silt content (%)
    bd (double):         buld density (g/cm³)
    Corg (double):       Organic carbon (%)
    topsoil (integer):   indicates topsoil horizon (topsoil=1,subsoil=0)
    RESID (double):      ...
    CTEN (double):       ...
    """
    #calculate organic matte rfrom Cor
    om = Corg *1.724
    #calcualte saturated water content
    theta_s = calc_theta_s(c,s,bd,Corg,topsoil,stones=0,stone_porosity = 10)
    # van Genuchten params
    Ksat,alpha,n,phi = get_vanGenuchtenMualem_HYPRES(c,s,om,topsoil,bd,None)
    #calculation of WATEN
    xmpor = theta_s / ((1 + (alpha * CTEN)** n)**(1 - (1 /n))) # water content at CTEN
    TS = theta_s/100 #fictitious sat wc
    M = 1 - 1/n #1-1/n
    T50 = xmpor/100 #xmpor/100
    WILT = theta_s / ((1 + (alpha * 15000)**n)**(1 - (1 /n))) #water content at pF 4.2
    S=(1-fawc)*(T50-WILT/100)+WILT/100 #water content corresponding to WATEN
    TE = (S-RESID/100)/(TS-RESID/100) #effective saturation at WATEN / S
    WATEN  =0.01 * 1/alpha* ((1/(TE**(1/M)) - 1))**(1/n) # [m]
    s = "theta_s %.4f vG-N %.4f vG-alpha %.4f xmpor %.4f S %.4f TE %.4f WATEN %.2f"%(theta_s,n,alpha,xmpor,S,TE,WATEN)
    return WATEN

def plot_rc(ax1,ax2,retcurve,Psi_M,label,vals=()):
    """Plots the retention curve retcurve for the matrix potential values in the array Psi_M
    and the function of K(theta)"""
    

    # Calculate the wetness at the matrix potential
    W = retcurve.Wetness(Psi_M) 
    # plot the retention curve. The methods vgm.Wetness(matrixpotential), vgm.MatricPotential(wetness),
    # vgm.K(wetness) accept numbers as well as arrays for the values
#    plot(Psi_M, W * retcurve.Porosity(0))
    ax1.plot((W * retcurve.Porosity(0))*100.,np.log(Psi_M*-1*100),label=label + "\n" + "Ksat %.2f, alpha %.2f\nn %.2f, phi %.2f"%vals)
    # label axis
    ax1.set_ylabel('pF')
    ax1.set_xlabel(r'$\theta$ [%]')
    ax1.grid()
    ax1.set_ylim(0,7)
    ax1.set_xlim(0,60)
    ax1.legend(loc=0,fontsize=8)
    # Make lower plot (K(W))
#    semilogy(Psi_M, retcurve.K(W))
    ax2.plot(retcurve.K(W),np.log(Psi_M*-1*100),label="")
    ax2.set_ylabel("")
    ax2.set_xlabel(r'$K(\theta) [\frac{m}{day}]$')
    ax2.set_ylim(0,7)
    ax2.grid()
    ax2.legend(loc=0,fontsize=8)

def calc_porosity(rb,rd=2.65):
    """
    rb (double):    Buld density [g/cm3]
    rd (double):    Particle density [g/cm3]
    
    returns Porosity [cm3/cm3]
    """
    return 1-(rb/rd)


import matplotlib.pylab as plt
import cmf
import numpy as np

##############################################################################
# laod soil information
Psi_M = np.arange(0,-3,-0.01)
dtype=dtype=[('ID', 'i'), ('Layer', '<f8'), ('depth_m', '<f8'), ('clay_perc', '<f8'), ('silt_perc', '<f8'), ('sand_perc', '<f8'), ('rock_perc', '<f8'), ('bulkdensity_gcm3', '<f8'), ('availablewatercapacity_mm', '<f8'), ('Ksat_mday', '<f8'), ('Corg_perc', '<f8'), ('density_material', '<f8')]
soils = np.genfromtxt(r"c:\0_work\SYN\Soil\soildata_SYN.csv",delimiter=",",names=True)


###############################################################################
# determine van Genuchten params
if soils[0]["Layer"] == 1:
    topsoil = 1
else:
    topsoil = 0
dat = open("c:/0_work/SYN/Soil/vanGenuchten_HYPRES.csv","w")
dat.write("soil,layer,HYPRES_Ksat,HYPRES_alpha,HYPRES_n" + "\n")
for s,_ in enumerate(soils):
    clay = soils[s]["clay_perc"]
    silt = soils[s]["silt_perc"]
    Corg = soils[s]["Corg_perc"]
    bd = soils[s]["bulkdensity_gcm3"]
    pf = soils[s]["density_material"]
    Ksat,alpha,n,phi = get_vanGenuchtenMualem_HYPRES(clay,silt,Corg,topsoil,bd,pf)
    print("soil %i layer %i"%(soils[s]["ID"],soils[s]["Layer"]),Ksat,alpha,n,phi)

    dat.write("%i,%i,%.2f,%.2f,%.2f"%(soils[s]["ID"],soils[s]["Layer"],Ksat,alpha,n) + "\n")

    fig = plt.figure()
    # Make upper plot
    ax1 = fig.add_subplot(1,2,1)
    ax2 = fig.add_subplot(1,2,2) 
    vgm = cmf.VanGenuchtenMualem(Ksat=Ksat, alpha=alpha, n=n, phi=phi)
    plot_rc(ax1,ax2,vgm,Psi_M,"soil %i layer %i"%(soils[s]["ID"],soils[s]["Layer"]),(soils[s]["Ksat_mday"],alpha,n,phi))
    plt.tight_layout()
    fig.savefig("c:/0_work/SYN/Soil/"+ "soil %i layer %i" % (soils[s]["ID"],soils[s]["Layer"])+ ".png",dpi=300)
dat.close()

################################################################################
## write soillayer file
#depths = [0.01,0.0225,0.04,0.0625,0.09,0.1225,0.16,0.2025,0.25,0.3025,0.36,0.4225,0.49,0.5625,0.64,0.7225,0.81,0.9025,1,1.1025,1.21,1.3225,1.44,1.50]
#dat = open(r"n:\MOD\106520_BCS_catchment_models\mod\cal\datasets\cmf_GKB\cmf_inputdata\SoilLayer.csv","w")
#dat.write("field,depth,Ksat,Phi,alpha,n,m,Corg" + "\n")
#for soilname in np.unique(soils["ID"]):
#    soil = soils[(soils["ID"]==soilname)]
#    for depth in depths:
#        isDepth=False
#        i=0
#        while not isDepth:
#            if depth<=soil[i]["depth_m"]:
#                isDepth=True
#            else:
#                i+=1
#        
#        clay = soil[i]["clay_perc"]
#        silt = soil[i]["silt_perc"]
#        Corg = soil[i]["Corg_perc"]
#        bd = soil[i]["bulkdensity_gcm3"]
#        pf = soil[i]["density_material"]
#        if soil[i]["Layer"] == 1:
#            topsoil = 1
#        else:
#            topsoil = 0
#        Ksat,alpha,n,phi = get_vanGenuchtenMualem_HYPRES(clay,silt,Corg,topsoil,bd,pf)
#        #use Ksat from reprot
#        Ksat = soil[i]["Ksat_mday"]
#
#        dat.write("soil%s,%.2f,%.2f,%.2f,%.2f,%.2f,%.2f,%.4f" % (int(soilname),depth,Ksat,phi,alpha,n,-1,Corg/100) + "\n")
#
#dat.close()


###############################################################################
# calcualtion of WATEN for MACRO
ksat = get_vanGenuchtenMualem_HYPRES(15,58,.1764,1,1.5,pf=None)
#s=calc_WATEN(0.8,5,17,1.1,5.5,1)
print(ksat)
