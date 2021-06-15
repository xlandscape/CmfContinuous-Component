import math
import datetime
import numpy as np

class PET(): 
    def __init__(self): 
        pass
        
    def __call__(self,*args):
        ETo = self.calc_ETo(*args)
        return ETo

    def vectorize_ETo(self,*args):
        vect_func = np.vectorize(self.calc_ETo)
        return vect_func(*args)

    def map_ETo(self,*args):
        return map(self.calc_ETo,*args)
        
    
    def calc_Rs_Hargreaves(Tmin,Tmax,Ra,kRs=.16):
        """
        The difference between the maximum and minimum air temperature is 
        related to the degree of cloud cover in a location. Clear-sky conditions 
        result in high temperatures during the day (Tmax,) because the atmosphere 
        is transparent to the incoming solar radiation and in low temperatures 
        during the night (Tmin) because less outgoing longwave radiation is 
        absorbed by the atmosphere. On the other hand, in overcast conditions,
        Tmax is relatively smaller because a significant part of the incoming
        solar radiation never reaches the earth's surface and is absorbed and
        reflected by the clouds. Similarly, Tmin will be relatively higher as
        the cloud cover acts as a blanket and decreases the net outgoing longwave 
        radiation. Therefore, the difference between the maximum and minimum air 
        temperature (Tmax - Tmin) can be used as an indicator of the fraction of 
        extraterrestrial radiation that reaches the earth's surface. This principle
        has been utilized by Hargreaves and Samani to develop estimates of ETo
        using only air temperature data. 
        
        aww Allen et al. (1998)
        
        
        
        where

        Ra extraterrestrial radiation [MJ m-2 d-1],
        Tmax maximum air temperature [°C],
        Tmin minimum air temperature [°C],
        kRs adjustment coefficient (0.16.. 0.19) [°C-0.5].

        The square root of the temperature difference is closely related to the
        existing daily solar radiation in a given location. The adjustment 
        coefficient kRs is empirical and differs for 'interior' or 'coastal'
        regions:

        · for 'interior' locations, where land mass dominates and 
        air masses are not strongly influenced by a large water body, kRs @ 0.16;
        · for 'coastal' locations, situated on or adjacent to the coast of a 
        large land mass and where air masses are influenced by a nearby water body, kRs @ 0.19.
            """
        Rs = kRs * (Tmax - Tmin)**(1/2) * Ra
        return Rs
    
    def calc_Rs_Supit(Ra,Tmax,Tmin,cc,A_s,B_s,C_s):
        """
        When sunshine duration is not available but minimum and maximum
        temperature and cloud cover are known, the Supit formula is used,
        which is an extension of the Hargreaves formula (Supit, 1994). Again,
        the regression coefficients depend on the geographic location.
        
        
        where 	<Rg 	:  	Incoming daily global solar radiation 	[MJ m-2 d-1]

        	Ra 	
        	Daily extra-terrestrial radiation  	[MJ m-2 d-1]
        
        	CC 	
        	Mean total cloud cover during daytime 	[octa]
        
        	Tmax 	
        	Maximum temperature 	[°C]
        
        	Tmin 	: 	Minimum temperature 	[°C]
        
        	As 	: 	Empirical constants 	[°C-0.5]
        
        	Bs 	: 	Empirical constants 	[-]
        
        	Cs 	: 	Empirical constants 	[MJ m-2 d-1]        
         """
         
        Rs = Ra * (A_s * (Tmax-Tmin)**(1/2) + B_s * (1-cc/8)**(1/2)   ) + C_s
        return Rs
        
    def calc_Rs_Angstrom(actual_sunshine_hours,daylight_hours,Ra,a_s=.25,b_s=.5):
        """
        In the case sunshine duration is available, global radiation is
        calculated using the equation postulated by Ångström (1924) and 
        modified by Prescott (1940). The two constants in this equation
        depend on the geographic location. 
        
        Angstrom formula - (see Allen et al., 1998)        
        
        where
    
        Rs solar or shortwave radiation [MJ m-2 day-1],
    
        actual_sunshine_hours (n) actual duration of sunshine [hour],
    
        DaylightHours (N) maximum possible duration of sunshine or daylight hours [hour],
        --> self.DaylightHours()
    
        n/N relative sunshine duration [-],
    
        Ra extraterrestrial radiation [MJ m-2 day-1],
    
        as regression constant, expressing the fraction of extraterrestrial 
        radiation reaching the earth on overcast days (n = 0),
    
        as+bs fraction of extraterrestrial radiation reaching the earth on 
        clear days (n = N).
    
        Rs is expressed in the above equation in MJ m-2 day-1. The corresponding 
        equivalent evaporation in mm day-1 is obtained by multiplying Rs by 0.408
        (Equation 20). Depending on atmospheric conditions (humidity, dust) and 
        solar declination (latitude and month), the Angstrom values as and bs will 
        vary. Where no actual solar radiation data are available and no calibration 
        has been carried out for improved as and bs parameters, the values 
        a_s = 0.25 and b_s = 0.50 are recommended. 
        """     
        Rs = a_s + b_s * (actual_sunshine_hours/daylight_hours) * Ra
        return Rs

    def calc_Rnl(self,Tmin,Tmax,Rs_Rso,ea):
        sigma = 4.903 * 10**-9
        Tmax_sigma = sigma * (Tmax + 273.16)**4
        Tmin_sigma = sigma * (Tmin + 273.16)**4
        Term1 = (Tmax_sigma + Tmin_sigma) / 2
        Term2 = 0.34 - 0.14 * ea**0.5
        Term3 = 1.35 * Rs_Rso - 0.35
        Rnl = Term1 * Term2 * Term3
        return Rnl
    
    def calc_ea_from_Tdew(self,tdew):
        return 0.6108 * np.exp((17.27*tdew)/(tdew+273.3))
        
    def calc_ea_from_RHmax_RHmin(self,es_Tmin,es_Tmax,RHmin,RHmax):
        return (es_Tmin*RHmax/100 + es_Tmax*RHmin/100)/2     
    
    def calc_ea_from_RHmax(self,es_Tmin,RHmax):
        return es_Tmin*RHmax/100
        
    def calc_ea_from_RHmean(self,es_Tmin,es_Tmax,RHmean):
        return RHmean/100*((es_Tmax+es_Tmin) / 2)
        
    def calc_Ra_from_DOY(self,latitude,DOY):
        lat_radians = self.calc_lat_radians(latitude)
        Gsc = 0.082 
        inverse_realtive_distance = 1 + 0.033 * math.cos(2 * math.pi * DOY / 365)
        solar_decimation = 0.409 * math.sin(2 * math.pi / 365 * DOY - 1.39) 
        sunset_hour_angle = math.acos(-1 * math.tan(lat_radians) * math.tan(solar_decimation)) 
        term1 = 24 * 60 / math.pi * Gsc * inverse_realtive_distance
        term2 = sunset_hour_angle * math.sin(lat_radians) * math.sin(solar_decimation)
        term3 = math.cos(lat_radians) * math.cos(solar_decimation) * math.sin(sunset_hour_angle)
        Ra = term1 * (term2 + term3)
        return Ra
    
    def calc_Ra_from_month(self,latitude,month):
        DOY = self.calc_DOY(month)
        lat_radians = self.calc_lat_radians(latitude)
        Gsc = 0.082 
        inverse_realtive_distance = 1 + 0.033 * math.cos(2 * math.pi * DOY / 365)
        solar_decimation = 0.409 * math.sin(2 * math.pi / 365 * DOY - 1.39) 
        sunset_hour_angle = math.acos(-1 * math.tan(lat_radians) * math.tan(solar_decimation)) 
        term1 = 24 * 60 / math.pi * Gsc * inverse_realtive_distance
        term2 = sunset_hour_angle * math.sin(lat_radians) * math.sin(solar_decimation)
        term3 = math.cos(lat_radians) * math.cos(solar_decimation) * math.sin(sunset_hour_angle)
        Ra = term1 * (term2 + term3)
        return Ra
        
    def calc_DOY(self,month):
        return 30.4 * month - 15
        
    def calc_DaylightHours(self,latitude, DOY):
        lat_radians = self.calc_lat_radians(latitude)
        solar_decimation = 0.409 * math.sin(2 * math.pi / 365 * DOY - 1.39) 
        sunset_hour_angle = math.acos(-1 * math.tan(lat_radians) * math.tan(solar_decimation)) 
        DayLighHours = 24 / math.pi * sunset_hour_angle
        return DayLighHours
    
    def calc_lat_radians(self,latitude):
        return math.pi/180*latitude 
    
    def calc_AtmoshpericPressure(self,altitude):
        # Atmospheric pressure (P) [kPa]
        P = 101.3 * ((293 - 0.0065 * altitude) / 293)**5.26  
        return P
        
    def calc_SlopeVapourPressureCurve(self,Tmean):
        # Slope of vapour pressure curve (D) [kPa °C-1]
        Delta = (4098 * (0.6108 * math.exp(17.27 * Tmean / (Tmean + 237.3)))) / (Tmean + 237.3)**2
        return Delta
    
    def calc_PsychrometricConstant(self,P):
        # Psychrometric constant (g) [kPa °C-1]
        gamma = 0.665 * 10**-3 * P  
        return gamma
        
    def calc_LatentHeatofvaporization(self):
        """        
        The latent heat of vaporization (rho) expresses the energy required to 
        change a unit mass of water from liquid to water vapour in a constant 
        pressure and constant temperature process. The value of the latent heat 
        varies as a function of temperature. At a high temperature, less energy 
        will be required than at lower temperatures. As rho varies only slightly 
        over normal temperature ranges a single value of 2.45 MJ kg-1 is taken 
        in the simplification of the FAO Penman-Monteith equation. This is the 
        latent heat for an air temperature of about 20°C. [Allen, 1998]
        """
        return 2.45
        
    def calc_ETo(self):
        pass
        
class PET_FAO56(PET): 
    def __init__(self): 
 
        PET.__init__(self)
    
    def calc_ETo(self,Tmax,Tmin,Ra,Rs,u2,altitude,RH='RHmax',RHmax=None,RHmin=None,RHmean=None,timestep ='daily'):
        #### FAO56 Oenman Monteith equation
        
            #    ETo reference evapotranspiration [mm day-1],
            #    Rn net radiation at the crop surface [MJ m-2 day-1],
            #    G soil heat flux density [MJ m-2 day-1],
            #    T mean daily air temperature at 2 m height [°C],
            #    u2 wind speed at 2 m height [m s-1],
            #    es saturation vapour pressure [kPa],
            #    ea actual vapour pressure [kPa],
            #    es - ea saturation vapour pressure deficit [kPa],
            #    D slope vapour pressure curve [kPa °C-1],
            #    g psychrometric constant [kPa °C-1].        

        # Atmospheric pressure (P) [kPa]
        P = self.calc_AtmoshpericPressure(altitude)         
        #P = 101.3 * ((293 - 0.0065 * altitude) / 293)**5.26 
        
        
         # Psychrometric constant (g) [kPa °C-1]
        gamma = self.calc_PsychrometricConstant(P)
        #gamma = 0.665 * 10**-3 * P         
        
        # Calculate Tmean at 2 m height [°C]
        Tmean = (Tmax + Tmin) / 2
        
        # Slope of vapour pressure curve (D) [kPa °C-1]
        Delta = self.calc_SlopeVapourPressureCurve(Tmean)
        #Delta = (4098 * (0.6108 * math.exp(17.27 * Tmean / (Tmean + 237.3)))) / (Tmean + 237.3)**2        
        
        # Vapor pressure deficit [kPa]
        es_Tmax = 0.6108 * math.exp((17.27 * Tmax) / (Tmax + 237.3))
        es_Tmin = 0.6108 * math.exp((17.27 * Tmin) / (Tmin + 237.3))
        es = (es_Tmax + es_Tmin) / 2
        if RH == 'RHmax':
            ea = self.calc_ea_from_RHmax(es_Tmin,RHmax)
        if RH == 'RHmean':
            ea = self.calc_ea_from_RHmean(es_Tmin,es_Tmax,RHmean)
        if RH == 'RHmaxRHmin':
            ea = self.calc_ea_from_RHmax_RHmin(es_Tmin,es_Tmax,RHmin,RHmax)
        vapor_pressure_deficit = es - ea

        # Rn net radiation at the crop surface [MJ m-2 day-1]
        Rso = (0.75 + 2 * altitude * 10**-5) * Ra

        # Rs/Rso relative shortwave radiation (limited to £ 1.0)
        Rs_Rso = min([Rs/Rso,1.0])            
        Rns = 0.77 * Rs # 1-albedo (grass=0.23)
        Rnl = self.calc_Rnl(Tmin, Tmax, Rs_Rso, ea)
        Rn = Rns - Rnl
        
        # G soil heat flux density [MJ m-2 day-1]
        if timestep == 'daily': G = 0
        if timestep == 'monthly': G = 0.14 * (Tmean - Tmean_LastMonth)
        
        # ETo Grass reference evapotranspiration [mm day-1]
        ETo_numerator = 0.408 * Delta * (Rn - G) + gamma * (900 / (Tmean + 273) * u2 * vapor_pressure_deficit)
        ETo_denumerator = Delta + gamma * (1 + 0.34 * u2)
        ETo = ETo_numerator / ETo_denumerator
        return ETo 
        
class PET_PriestlyTaylor(PET):
    def __init__(self):
        PET.__init__(self)
    def calc_ETo(self, Tmax,Tmin,Ra,Rs,altitude,RH='RHmax',RHmax=None,RHmin=None,RHmean=None,timestep ='daily',Tmean_LastMonth=None,alpha=1.26,rho=2.45): 

        # Calculate Tmean at 2 m height [°C]
        Tmean = (Tmax + Tmin) / 2
        
        # Slope of vapour pressure curve (D) [kPa °C-1]
        Delta = self.calc_SlopeVapourPressureCurve(Tmean)
        #Delta = (4098 * (0.6108 * math.exp(17.27 * Tmean / (Tmean + 237.3)))) / (Tmean + 237.3)**2        

        # Atmospheric pressure (P) [kPa]
        P = self.calc_AtmoshpericPressure(altitude)          
        #P = 101.3 * ((293 - 0.0065 * altitude) / 293)**5.26 
        
         # Psychrometric constant (g) [kPa °C-1]
        gamma = self.calc_PsychrometricConstant(P)
        #gamma = 0.665 * 10**-3 * P 
        
        # G soil heat flux density [MJ m-2 day-1]
        if timestep == 'daily': G = 0
        if timestep == 'monthly': G = 0.14 * (Tmean - Tmean_LastMonth)

        # Vapor pressure deficit [kPa]
        es_Tmax = 0.6108 * math.exp((17.27 * Tmax) / (Tmax + 237.3))
        es_Tmin = 0.6108 * math.exp((17.27 * Tmin) / (Tmin + 237.3))
        if RH == 'RHmax':
            ea = self.calc_ea_from_RHmax(es_Tmin,RHmax)
        if RH == 'RHmean':
            ea = self.calc_ea_from_RHmean(es_Tmin,es_Tmax,RHmean)
        if RH == 'RHmaxRHmin':
            ea = self.calc_ea_from_RHmax_RHmin(es_Tmin,es_Tmax,RHmin,RHmax)
       
        # Rn net radiation at the crop surface [MJ m-2 day-1]
        Rso = (0.75 + 2 * altitude * 10**-5) * Ra

        # Rs/Rso relative shortwave radiation (limited to £ 1.0)
        Rs_Rso = min([Rs/Rso,1.0])            
        Rns = 0.77 * Rs
        Rnl = self.calc_Rnl(Tmin, Tmax, Rs_Rso, ea)
        Rn = Rns - Rnl
        
        # 2.45 MJ kg-1  is the latent heat for an air temperature of about 20°C.
        rho = P / (1.01 * (Tmean + 273) * 0.287)
        #rho = self.calc_LatentHeatofvaporization()
        
        ETo = alpha * ((Delta / (Delta + gamma)) * (Rn - G) / rho)
        #ETo = 1.26 * (1+gamma/Delta)**(-1) * Rn
        return ETo


class PET_Turc(PET):
    def __init__(self):
        PET.__init__(self)
    def calc_ETo(self, Tmax,Tmin,Ra,Rs,altitude,RHmean,RH='RHmax',RHmax=None,RHmin=None,rho=2.45):
        
        # Calculate Tmean at 2 m height [°C]
        Tmean = (Tmax + Tmin) / 2
        
        # Vapor pressure deficit [kPa]
        es_Tmax = 0.6108 * math.exp((17.27 * Tmax) / (Tmax + 237.3))
        es_Tmin = 0.6108 * math.exp((17.27 * Tmin) / (Tmin + 237.3))
        if RH == 'RHmax':
            ea = self.calc_ea_from_RHmax(es_Tmin,RHmax)
        if RH == 'RHmean':
            ea = self.calc_ea_from_RHmean(es_Tmin,es_Tmax,RHmean)
        if RH == 'RHmaxRHmin':
            ea = self.calc_ea_from_RHmax_RHmin(es_Tmin,es_Tmax,RHmin,RHmax)
            
        if RHmean >= 50:
            alpha_T = 1.0
        else:
            alpha_T = 1 + ((50 - RHmean) / 70)

        
        # 2.45 MJ kg-1  is the latent heat for an air temperature of about 20°C.
        rho = P / (1.01 * (Tmean + 273) * 0.287)
        #rho = self.calc_LatentHeatofvaporization()        
       
        ETo = alpha_T * 0.013 * (Tmean / (Tmean + 15)) * ((23.8856 * Rs + 50) / rho)
        return ETo


      
#class PET_HagreavesSamani(PET):
#    def __init__(self):
#        
#        PET.__init__(self)
#        
#    def calc_ETo(self, Tmax,Tmin,Ra): 
#        Tmean = (Tmin + Tmax) / 2
#        ETo = 0.0023 * (Tmean + 17.8) * (Tmax - Tmin)**0.5 * Ra
#        return ETo

class PET_APET(PET):
    def __init__(self):
        PET.__init__(self)
    def calc_ETo(self, Tmax,Tmin,Ra,Rs,altitude,RH='RHmax',RHmax=None,RHmin=None,RHmean=None,b1=13.4,b2=1.13): 

        # Calculate Tmean at 2 m height [°C]
        Tmean = (Tmax + Tmin) / 2
        
        # Slope of vapour pressure curve (D) [kPa °C-1]
        Delta = self.calc_SlopeVapourPressureCurve(Tmean)
        #Delta = (4098 * (0.6108 * math.exp(17.27 * Tmean / (Tmean + 237.3)))) / (Tmean + 237.3)**2        

        # Atmospheric pressure (P) [kPa]
        P = self.calc_AtmoshpericPressure(altitude)         
        #P = 101.3 * ((293 - 0.0065 * altitude) / 293)**5.26 
        
        # Psychrometric constant (g) [kPa °C-1]
        gamma = self.calc_PsychrometricConstant(P)
        #gamma = 0.665 * 10**-3 * P   
        
        # Vapor pressure deficit [kPa]
        es_Tmax = 0.6108 * math.exp((17.27 * Tmax) / (Tmax + 237.3))
        es_Tmin = 0.6108 * math.exp((17.27 * Tmin) / (Tmin + 237.3))
        if RH == 'RHmax':
            ea = self.calc_ea_from_RHmax(es_Tmin,RHmax)
        if RH == 'RHmean':
            ea = self.calc_ea_from_RHmean(es_Tmin,es_Tmax,RHmean)
        if RH == 'RHmaxRHmin':
            ea = self.calc_ea_from_RHmax_RHmin(es_Tmin,es_Tmax,RHmin,RHmax)
        
        # Rn net radiation at the crop surface [MJ m-2 day-1]
        Rso = (0.75 + 2 * altitude * 10**-5) * Ra

        # Rs/Rso relative shortwave radiation (limited to £ 1.0)
        Rs_Rso = min([Rs/Rso,1.0])            
        Rns = 0.77 * Rs
        Rnl = self.calc_Rnl(Tmin, Tmax, Rs_Rso, ea)
        Rn = Rns - Rnl

        #rho = P / (1.01 * (Tmean + 273) * 0.287)
        rho = self.calc_LatentHeatofvaporization()    

        ETo = 1 / rho * (b1 + b2 * (Rn / (1 + gamma * P / Delta)))
        #ETo = b1 + b2 * (1 + gamma * P / Delta)**-1 * Rn
        #ETo = 1.26 * (1+gamma/Delta)**(-1) * Rn
        return ETo

class PET_PPET(PET):
    def __init__(self):
        PET.__init__(self)
    def calc_ETo(self,accuracy=0.001,rho=2.45):         
        pass

#def test_map(count=1000000):
#        
#    Tmin =  12.3
#    Tmax = 21.5
#    ea = 2.85
#    u2 = 2.078
#    Tmean_april = 16.9
#    Tmean_march = 29.2
#    altitude = 100
#    Ra = 41.09
#    Rs = 22.07
#    RHmax = 84
#    RHmin = 63
#    
#    #print calc_Ra(13.73,105)
#    #print calc_DaylightHours(13.73,105)        
#    pet_fao56 = PET_FAO56() 
#    #print pet_fao56(Tmax,Tmin,Ra,Rs,u2,altitude,'RHmaxRHmin',RHmax,RHmin,None,'daily',None)
#    #
#    #pet_pt = PET_PriestlyTaylor() 
#    #print pet_pt(Tmax,Tmin,Ra,Rs,altitude,'RHmaxRHmin',RHmax,RHmin,None,'daily',None)
#    #pet_hs = PET_HagreavesSamani() 
#    #print pet_hs(Tmax,Tmin,Ra)
#    
#    #pet_turc = PET_Turc() 
#    #print pet_turc(Tmax,Tmin,Ra,Rs,altitude,((RHmin+RHmax)/2),'RHmaxRHmin',RHmax,RHmin,2.45)
#    
#    Tmin =  [12.3 for i in range(count)]
#    Tmax = [21.5 for i in range(count)]
#    ea = [2.85 for i in range(count)]
#    u2 = [2.078 for i in range(count)]
#    Tmean_april = [16.9 for i in range(count)]
#    Tmean_march = [29.2 for i in range(count)]
#    altitude = [100 for i in range(count)]
#    Ra = [41.09 for i in range(count)]
#    Rs = [22.07 for i in range(count)]
#    RHmax = [84 for i in range(count)]
#    RHmin = [63 for i in range(count)]
#
#    start = datetime.datetime.now()
#
#    x=pet_fao56.map_ETo(Tmax,Tmin,Ra,Rs,u2,altitude,['RHmaxRHmin' for i in Tmax],RHmax,RHmin,[None for i in Tmax],['daily' for i in Tmax])
#    print datetime.datetime.now()-start
#
#
#def test_vectorize(x=1000,y=1000):
#            
#    Tmin =  12.3
#    Tmax = 21.5
#    ea = 2.85
#    u2 = 2.078
#    Tmean_april = 16.9
#    Tmean_march = 29.2
#    altitude = 100
#    Ra = 41.09
#    Rs = 22.07
#    RHmax = 84
#    RHmin = 63
#    
#    #print calc_Ra(13.73,105)
#    #print calc_DaylightHours(13.73,105)        
#    pet_fao56 = PET_FAO56() 
#    #print pet_fao56(Tmax,Tmin,Ra,Rs,u2,altitude,'RHmaxRHmin',RHmax,RHmin,None,'daily',None)
#    #
#    #pet_pt = PET_PriestlyTaylor() 
#    #print pet_pt(Tmax,Tmin,Ra,Rs,altitude,'RHmaxRHmin',RHmax,RHmin,None,'daily',None)
#    #pet_hs = PET_HagreavesSamani() 
#    #print pet_hs(Tmax,Tmin,Ra)
#    
#    #pet_turc = PET_Turc() 
#    #print pet_turc(Tmax,Tmin,Ra,Rs,altitude,((RHmin+RHmax)/2),'RHmaxRHmin',RHmax,RHmin,2.45)
#    
#    Tmin = np.empty([x,y]);Tmin.fill(12.3)  
#    Tmax = np.empty([x,y]);Tmax.fill(21.5 ) 
#    ea = np.empty([x,y]);ea.fill(2.85) 
#    u2 = np.empty([x,y]);u2.fill(2.078)  
#    Tmean_april = np.empty([x,y]);Tmean_april.fill(16.9)  
#    Tmean_march = np.empty([x,y]);Tmean_march.fill(29.2)  
#    altitude = np.empty([x,y]);altitude.fill(100) 
#    Ra = np.empty([x,y]);Ra.fill(41.09)  
#    Rs = np.empty([x,y]);Rs.fill(22.)
#    RHmax = np.empty([x,y]);RHmax.fill(84) 
#    RHmin = np.empty([x,y]);RHmin.fill(6)  
#    RH = np.empty([x,y],dtype=('S10'));RH.fill('RHmaxRHmin')    
#    none = np.empty([x,y]);none.fill(None)
#    daily = np.empty([x,y],dtype=('S5'));daily.fill('daily')
#
#    start = datetime.datetime.now()
#    ff=pet_fao56.vectorize_ETo(Tmax,Tmin,Ra,Rs,u2,altitude,RH,None,None,None,'daily')
#    print datetime.datetime.now()-start

class PET_PenmanMonteith(PET): 
    def __init__(self): 
 
        PET.__init__(self)
    
    def calc_ETo(self,Tmax,Tmin,Ra,Rs,u2,altitude,ea):
        #### FAO56 Oenman Monteith equation
        
            #    ETo reference evapotranspiration [mm day-1],
            #    Rn net radiation at the crop surface [MJ m-2 day-1],
            #    G soil heat flux density [MJ m-2 day-1],
            #    T mean daily air temperature at 2 m height [°C],
            #    u2 wind speed at 2 m height [m s-1],
            #    es saturation vapour pressure [kPa],
            #    ea actual vapour pressure [kPa],
            #    es - ea saturation vapour pressure deficit [kPa],
            #    D slope vapour pressure curve [kPa °C-1],
            #    g psychrometric constant [kPa °C-1].        

        # Atmospheric pressure (P) [kPa]
        P = self.calc_AtmoshpericPressure(altitude)         
        #P = 101.3 * ((293 - 0.0065 * altitude) / 293)**5.26 
        
        
         # Psychrometric constant (g) [kPa °C-1]
        gamma = self.calc_PsychrometricConstant(P)
        #gamma = 0.665 * 10**-3 * P         
        
        # Calculate Tmean at 2 m height [°C]
        Tmean = (Tmax + Tmin) / 2
        
        # Slope of vapour pressure curve (D) [kPa °C-1]
        Delta = self.calc_SlopeVapourPressureCurve(Tmean)
        #Delta = (4098 * (0.6108 * math.exp(17.27 * Tmean / (Tmean + 237.3)))) / (Tmean + 237.3)**2        
        
        # Vapor pressure deficit [kPa]
        es_Tmax = 0.6108 * math.exp((17.27 * Tmax) / (Tmax + 237.3))
        es_Tmin = 0.6108 * math.exp((17.27 * Tmin) / (Tmin + 237.3))
        es = (es_Tmax + es_Tmin) / 2
   
        vapor_pressure_deficit = es - ea

        # Rn net radiation at the crop surface [MJ m-2 day-1]
        Rso = (0.75 + 2 * altitude * 10**-5) * Ra

        # Rs/Rso relative shortwave radiation (limited to £ 1.0)
        Rs_Rso = min([Rs/Rso,1.0])            
        Rns = 0.77 * Rs # 1-albedo (grass=0.23)
        Rnl = self.calc_Rnl(Tmin, Tmax, Rs_Rso, ea)
        Rn = Rns - Rnl
        
        # G soil heat flux density [MJ m-2 day-1]
        G = 0

        
        # ETo Grass reference evapotranspiration [mm day-1]
        ETo_numerator = 0.408 * Delta * (Rn - G) + gamma * (900 / (Tmean + 273) * u2 * vapor_pressure_deficit)
        ETo_denumerator = Delta + gamma * (1 + 0.34 * u2)
        ETo = ETo_numerator / ETo_denumerator
        return ETo 






#



    
    
def calc_Rnl(Tmin,Tmax,Rs_Rso,ea):
    sigma = 4.903 * 10**-9
    Tmax_sigma = sigma * (Tmax + 273.16)**4
    Tmin_sigma = sigma * (Tmin + 273.16)**4
    Term1 = (Tmax_sigma + Tmin_sigma) / 2
    Term2 = 0.34 - 0.14 * ea**0.5
    Term3 = 1.35 * Rs_Rso - 0.35
    Rnl = Term1 * Term2 * Term3
    return Rnl
    
def calc_Ra_from_DOY(latitude,DOY):
    lat_radians = math.pi/180*latitude 
    
    Gsc = 0.082 
    inverse_realtive_distance = 1 + 0.033 * math.cos(2 * math.pi * DOY / 365)
    solar_decimation = 0.409 * math.sin(2 * math.pi / 365 * DOY - 1.39) 
    sunset_hour_angle = math.acos(-1 * math.tan(lat_radians) * math.tan(solar_decimation)) 
    term1 = 24 * 60 / math.pi * Gsc * inverse_realtive_distance
    term2 = sunset_hour_angle * math.sin(lat_radians) * math.sin(solar_decimation)
    term3 = math.cos(lat_radians) * math.cos(solar_decimation) * math.sin(sunset_hour_angle)
    Ra = term1 * (term2 + term3)
    return Ra

    def calc_Rnl(Tmin,Tmax,Rs_Rso,ea):
        sigma = 4.903 * 10**-9
        Tmax_sigma = sigma * (Tmax + 273.16)**4
        Tmin_sigma = sigma * (Tmin + 273.16)**4
        Term1 = (Tmax_sigma + Tmin_sigma) / 2
        Term2 = 0.34 - 0.14 * ea**0.5
        Term3 = 1.35 * Rs_Rso - 0.35
        Rnl = Term1 * Term2 * Term3
        return Rnl
        
def calc_DaylightHours(latitude, DOY):
    lat_radians = math.pi/180*latitude 
    solar_decimation = 0.409 * math.sin(2 * math.pi / 365 * DOY - 1.39) 
    sunset_hour_angle = math.acos(-1 * math.tan(lat_radians) * math.tan(solar_decimation)) 
    DayLighHours = 24 / math.pi * sunset_hour_angle
    return DayLighHours




def calcETo(DOY,sunhours,Tmin,Tmax,Tmean,Wind,RHmean,G,altitude,latitude):
    #constants
    AerDyn_Resistance=206
    AeroT_Cff = 900
    rc = 70
    albedo=0.23
    a_s =0.25
    b_s = 0.5
    # Vapor pressure deficit [kPa]
    ea_Tmax = 0.6108 * math.exp((17.27 * Tmax) / (Tmax + 237.3))
    ea_Tmin = 0.6108 * math.exp((17.27 * Tmin) / (Tmin + 237.3))
    ea = (ea_Tmax + ea_Tmin) / 2
    edew = RHmean/100*((ea_Tmax+ea_Tmin) / 2)
    # Rad term
    Ra=calc_Ra_from_DOY(latitude,DOY)
    N=calc_DaylightHours(latitude, DOY)
    Rs=Rs = (a_s + b_s * (sunhours/N)) * Ra
    Rns = (1-albedo) * Rs # 1-albedo (grass=0.23)
    Rso = (0.75 + 2 * altitude * 10**-5) * Ra
    Rs_Rso = min([Rs/Rso,1.0])            
    Rns = 0.77 * Rs # 1-albedo (grass=0.23)
    Rnl = calc_Rnl(Tmin, Tmax, Rs_Rso, edew)
    Rn = Rns - Rnl
    Rn_G=Rn-G
    Lambda = 2.501-(0.002361*(Tmean))
    Delta = (4098 * (0.6108 * math.exp(17.27 * Tmean / (Tmean + 237.3)))) / (Tmean + 237.3)**2
    P =  101.3 * ((293 - 0.0065 * altitude) / 293)**5.26  
    ra = AerDyn_Resistance / Wind
    Gamma1=0.0016286*P/Lambda
    Gamma2=Gamma1*(1+rc/ra)
    dl_gm=Delta/(Delta+Gamma2)
    Radterm = dl_gm*Rn_G/Lambda
    gm_dl = Gamma1/(Delta+Gamma2)
    Areoterm = gm_dl*AeroT_Cff / (Tmean+273)*Wind*(ea-edew)
    ET=Radterm+Areoterm
    return ET,Ra,Rn,Rs

    
    
def calcETo2(DOY,Rs,Tmin,Tmax,Tmean,Wind,vapourpressure,G,altitude,latitude):
    #constants
    AerDyn_Resistance=206
    AeroT_Cff = 900
    rc = 70
    albedo=0.23
    a_s =0.25
    b_s = 0.5
    # Vapor pressure deficit [kPa]
    ea_Tmax = 0.6108 * math.exp((17.27 * Tmax) / (Tmax + 237.3))
    ea_Tmin = 0.6108 * math.exp((17.27 * Tmin) / (Tmin + 237.3))
    ea = (ea_Tmax + ea_Tmin) / 2
    edew = vapourpressure
    # Rad term
    Ra=calc_Ra_from_DOY(latitude,DOY)
    Rns = (1-albedo) * Rs # 1-albedo (grass=0.23)
    Rso = (0.75 + 2 * altitude * 10**-5) * Ra
    Rs_Rso = min([Rs/Rso,1.0])            
    Rns = 0.77 * Rs # 1-albedo (grass=0.23)
    Rnl = calc_Rnl(Tmin, Tmax, Rs_Rso, edew)
    Rn = Rns - Rnl
    Rn_G=Rn-G
    Lambda = 2.501-(0.002361*(Tmean))
    Delta = (4098 * (0.6108 * math.exp(17.27 * Tmean / (Tmean + 237.3)))) / (Tmean + 237.3)**2
    P =  101.3 * ((293 - 0.0065 * altitude) / 293)**5.26  
    ra = AerDyn_Resistance / Wind
    Gamma1=0.0016286*P/Lambda
    Gamma2=Gamma1*(1+rc/ra)
    dl_gm=Delta/(Delta+Gamma2)
    Radterm = dl_gm*Rn_G/Lambda
    gm_dl = Gamma1/(Delta+Gamma2)
    Areoterm = gm_dl*AeroT_Cff / (Tmean+273)*Wind*(ea-edew)
    ET=Radterm+Areoterm
    return ET,Ra,Rn,Rs




import pandas as pd
import datetime
pet = PET_PenmanMonteith()
latitude = 50.72749
altitude=128

#
#dat = pd.read_csv(r"c:\0_work\bcs_catchmentmodelling\BEL_pome\BEL_pome_modelruns\clim101096.csv")
#
#dat["Date"]=pd.to_datetime(dat["Date"])
#dat["DOY"] =  dat["Date"].apply(lambda x: x.dayofyear)
eto=[]


for i in range(len(dat)):

    
    Tmin=dat.iloc[i]["TEMPERATURE_MIN"]
    Tmax=dat.iloc[i]["TEMPERATURE_MAX"]
    Tmean=(Tmin+Tmax)/2
    
    u10 = dat.iloc[i]["WINDSPEED"]
    u2 =  u10*4.87/np.log(67.8*10-5.42)  #u2 = uz * 4 . 87 / ln ( 67 . 8 * z − 5 . 42 )
    rs = dat.iloc[i]["RADIATION"]/1000 # convert kJ to MJ
    Doy = dat.iloc[i]["DOY"]
    vapourpressure = dat.iloc[i]["VAPOURPRESSURE"] / 10 # convert hectopascal to kilopascal
    ET,Ra,Rn,Rs = calcETo2(Doy,rs,Tmin,Tmax,Tmean,u2,vapourpressure,0,altitude,latitude) 
    eto.append(ET)

    
    print(i,len(dat),ET)
    
dat["ETo_PenmanMonteith"]=eto
dat.to_csv(r"c:\0_work\bcs_catchmentmodelling\BEL_pome\BEL_pome_modelruns\ETo_PenmanMonteith2.csv")

#
#
##xls = pd.ExcelFile(r"c:\0_work\bcs_catchmentmodelling\MACRO522\hourly_climate.xlsx")
##dat = xls.parse("2010")
#
#dat_daily=dat.groupby(['Year', 'month', 'Day']).mean()
#dat_daily.to_csv(r"c:\0_work\bcs_catchmentmodelling\MACRO522\daily_climate.csv")
#




































#
#import pandas as pd
#import datetime
#pet = PET_PenmanMonteith()
#latitude = 50.8
#altitude=50
#
#
#xls = pd.ExcelFile(r"c:\0_work\bcs_catchmentmodelling\MACRO522\hourly_climate.xlsx")
#dat = xls.parse("hourly_climate")
#dat["Date_Pandas"]=pd.to_datetime(dat["Date"])
#dat["DOY"] =  dat["Date_Pandas"].apply(lambda x: x.dayofyear)
#eto=[]
#ra = []
#rn = []
#rs = []
#
#for i in range(len(dat)):
#    
#    Tmin=dat.iloc[i]["Tmin"]
#    Tmax=dat.iloc[i]["Tmax"]
#    Tmean=(Tmin+Tmax)/2
#    Wind = dat.iloc[i]["Wind"]
#    sunhours = dat.iloc[i]["Sunhours"]
#    Doy = dat.iloc[i]["DOY"]
#    RHmean = dat.iloc[i]["RHmean"]
#    ET,Ra,Rn,Rs = calcETo(Doy,sunhours,Tmin,Tmax,Tmean,Wind,RHmean,0,altitude,latitude) 
#    eto.append(ET)
#    ra.append(Ra)
#    rn.append(Rn)
#    rs.append(Rs)
#    
#    print(i,len(dat),ET)
#dat["ET"]=eto
#dat["Ra"]=ra
#dat["Rn"]=rn
#dat["Rs"]=rs
#dat.to_csv(r"c:\0_work\bcs_catchmentmodelling\MACRO522\hourly_climate.csv")
#
#
#
##xls = pd.ExcelFile(r"c:\0_work\bcs_catchmentmodelling\MACRO522\hourly_climate.xlsx")
##dat = xls.parse("2010")
#
#dat_daily=dat.groupby(['Year', 'month', 'Day']).mean()
#dat_daily.to_csv(r"c:\0_work\bcs_catchmentmodelling\MACRO522\daily_climate.csv")
#
#








