# Main file for estimating failure probabilities pertaining to a certain cluster

import numpy as np
import pickle
from survivalmodels import survival
import pandas as pd

np.set_printoptions(threshold=np.inf)

## ============================
## Load dataset
firedf = pd.read_csv('hexTable.csv',usecols=range(1,24))
header_list = list(firedf)

# count the number of clusters
nclusters = len(set(firedf.Cluster))

## ============================
## Load pickle file

with open("dict_hexdata_prob.pickle","rb") as freq3:
    hexlocation = pickle.load(freq3)
    
with open("dict_hexdata_prob_noweather.pickle","rb") as freq4:
    hexlocation_noweath = pickle.load(freq4)

## ===========================
# Changeable parameters
curr_weather = 'clear-day'
day='Monday'
month = 'FEBRUARY'
timenow = 10*60*60             # Seconds from 12 am of the current day
datenow =  27
analysistime = 35*24*60*60        # in seconds

## ===========================
# Initialize other parameters

days_week = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
days_month = [31,28,31,30,31,30,31,31,30,31,30,31]
months_year = ['JANUARY','FEBRUARY','MARCH','APRIL','MAY','JUNE','JULY','AUGUST','SEPTEMBER','OCTOBER','NOVEMBER','DECEMBER']

time_cuts = 60*60*np.array([0,6,12,18,24]) # in seconds
tod_values = ['Early_Morning','Late_Morning','After_Noon','Night']

## ==========================
## Estimate disc TOD

if timenow > 0 and timenow < 6:
    disc_tod = 'Early_Morning'
elif timenow>6*60*60 and timenow<12*60*60:
    disc_tod = 'Late_Morning'
elif timenow>12*60*60 and timenow<18*60*60:
    disc_tod = 'After_Noon'
else:
    disc_tod = 'Night'

time_ineach = [] # amount of time in each segment
tod_ineach = [disc_tod] # discrete time value in each segment

tinitial = time_cuts[tod_values.index(disc_tod) + 1]-timenow # remaining time in the current segment

if tinitial < analysistime:
    time_ineach.append(tinitial)
else:
    time_ineach.append(analysistime)

num_segments = 1

if analysistime > tinitial:
    tmp = (analysistime-tinitial)/(6*60*60)
    for i1 in range(tmp):
        time_ineach.append(6*60*60)
    if (analysistime-tinitial)%(6*60*60) > 0:
        num_segments = 1 + tmp + 1
        time_remain = (analysistime-tinitial)%(6*60*60)
        time_ineach.append(time_remain)
    else:
        num_segments = 1+ tmp

repeat_tod_values = num_segments * tod_values

if analysistime > tinitial:
    tmp = (analysistime-tinitial)/(6*60*60)
    initial_index = repeat_tod_values.index(disc_tod)
    
    for i1 in range(tmp):
        tod_ineach.append(repeat_tod_values[initial_index + i1+1])
    
    if (analysistime-tinitial)%(6*60*60) > 0:
        time_remain = (analysistime-tinitial)%(6*60*60)
        tod_ineach.append(repeat_tod_values[initial_index + tmp+1])
        
# Time in each total
time_ineach_total = [] # cumulative time by each segment, used for survival probability calculations
time_ineach_total.append(time_ineach[0])

for i1 in range(1, len(time_ineach)):
    time_ineach_total.append(time_ineach_total[i1-1] + time_ineach[i1])
    
time_ineach_total_add_initial = [] # add initial time (current time) to the analysis time 
for i1 in range(len(time_ineach_total)):
    time_ineach_total_add_initial.append(timenow+time_ineach_total[i1])

## ==========================
## Estimate day 

index_currentday = days_week.index(day) # obtain the index of current day in the list of days

day_ineach = [] # obtain the day in each month
week_repeat = ((analysistime/(24*60*60*7))+1)*days_week

for i1 in range(len(time_ineach_total)):
    future_day = (time_ineach_total_add_initial[i1]-1)/(24*60*60)
    
    day_ineach.append(week_repeat[index_currentday+future_day])
 
## ==========================
## Estimate month
        
days_currentmonth = days_month[months_year.index(month)]

date_ineach = [datenow]
month_ineach = [month]
month_repeat2 = 2*months_year


for i1 in range(1,len(time_ineach_total)):
    if day_ineach[i1]==day_ineach[i1-1]: # same day
        date_ineach.append(date_ineach[i1-1])
        month_ineach.append(month_ineach[i1-1])
    else:
        nextday = date_ineach[i1-1]+1
        if nextday > days_month[months_year.index(month_ineach[i1-1])]: # next month, next day
            date_ineach.append(1)
            month_ineach.append(month_repeat2[month_repeat2.index(month_ineach[i1-1])+1])
        else:
            # next day, same month
            date_ineach.append(date_ineach[i1-1]+1)
            month_ineach.append(month_ineach[i1-1])
            

## ========================
# Analysis time is divided into multiple segments based on disc TOD and day
# Compute the failure probability in each segment for each cluster
cluster_failure_probs_segments = []

for i3 in range(num_segments):
    cluster_failure_probs = np.zeros(nclusters,)
    
    if i3==0:
        for i1 in range(nclusters):
            cluster_failure_probs[i1] = 1 - survival(i1+1,time_ineach_total[i3])
    else:
        for i1 in range(nclusters):
            cluster_failure_probs[i1] = np.abs((survival(i1+1,time_ineach_total[i3]) - survival(i1+1,time_ineach_total[i3-1])))
        
    cluster_failure_probs_segments.append(cluster_failure_probs)
    
## ========================
# Hex locations

cluster_hex_probs_segments = []

for i3 in range(num_segments):
    if i3==0:
        hex_dict = {} # key: cluster, value = probabilities of locations (also a dictionary)
        for i1 in range(nclusters):
            if cluster_failure_probs_segments[i3][i1]>0:
                features_tuple = (curr_weather, tod_ineach[i3], day_ineach[i3], month_ineach[i3])
                str_features_tuple = str(features_tuple)
                hex_dict[i1+1] = hexlocation[i1+1][str_features_tuple]
            else:
                hex_dict[i1+1] = {}
                
        cluster_hex_probs_segments.append(hex_dict)
    else:
        hex_dict = {} # key: cluster, value = probabilities of locations (also a dictionary)
        for i1 in range(nclusters):
            if cluster_failure_probs_segments[i3][i1]>0:
                features_tuple = (tod_ineach[i3], day_ineach[i3], month_ineach[i3])
                str_features_tuple = str(features_tuple)
                hex_dict[i1+1] = hexlocation_noweath[i1+1][str_features_tuple]
            else:
                hex_dict[i1+1] = {}
                
        cluster_hex_probs_segments.append(hex_dict)
    

## ==================================
# Compute overall probabilities
cluster_hexprobs_predict = {}
cluster_hexprobs_predict_combine = {}

for i1 in range(nclusters):
    hex_probs_segments_clusters = []
    for i2 in range(num_segments):
        tmp_dict = cluster_hex_probs_segments[i2][i1+1]
        prob_segment = ((1.0)*time_ineach_total[i2])/analysistime
        prob_incident = cluster_failure_probs_segments[i2][i1]
        tmp_dict3={}
        
        if len(tmp_dict)>0:
            for i3 in range(len(tmp_dict)):
                tmp_dict3[tmp_dict.keys()[i3]] = prob_incident*tmp_dict.values()[i3]
                
        hex_probs_segments_clusters.append(tmp_dict3)

    cluster_hexprobs_predict[i1+1] = hex_probs_segments_clusters
                                             
    # Now we need to sum probabilities across all segments
    
    hexprobs_predict_combine = {}
    combine_set_hexdict = set()
    
    for i2 in range(num_segments):
        combine_set_hexdict = combine_set_hexdict | set(cluster_hexprobs_predict[i1+1][i2])
        
    for i2 in combine_set_hexdict:
        tmpval = 0
        for i3 in range(num_segments):
            tmpval = tmpval + cluster_hexprobs_predict[i1+1][i3].get(i2,0)
          
        hexprobs_predict_combine[i2] = tmpval
                                
    cluster_hexprobs_predict_combine[i1+1]= hexprobs_predict_combine
                                    
for i1 in range(nclusters):
    print "================= Hex locations and probabilities corresponding to Cluster" + str(i1+1)
    print cluster_hexprobs_predict_combine[i1+1]
    
    
print "Note: If Hex location probabilities is not printed, then data corresponding to incidents at the set parameters are not available in the dataset"  
    
                                



 
