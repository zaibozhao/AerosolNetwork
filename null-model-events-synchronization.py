#-----------------------------------------------------------------------------------------------------------------
# null-model-events-synchronization
#
# Using the random phase method to shuffle the time series
# Calculate the synchronization of events after shuffling
# 
#-----------------------------------------------------------------------------------------------------------------

import numpy as np
import h5py
from numba import jit
from math import e

# Obtain time series of the start time of extreme events
def get_time (data_array,event_threshold):

    date = np.zeros((len(data_array),))
    threshold = event_threshold
    date[data_array>threshold] = 1

    tmp = date[1:] + date[:-1]
    if date[0] == 0:
        tmp = np.insert(tmp,0,0)
    else:
        tmp = np.insert(tmp,0,1)

    loc = np.arange(len(data_array))
    tmp_1 = loc[tmp == 1]

    events_time = []
    for k in range (0,len(tmp_1),2):
        time_tmp = tmp_1[k]
        events_time.append(time_tmp)
    
    return(np.array(events_time))

# Compute event synchronization between each node of the network
@jit(nopython=True)
def EvSy(i,j,k):

    timestamp_array1 = i
    timestamp_array2 = j
    
    event1= len(timestamp_array1)
    event2= len(timestamp_array2)

    EvSy_all = 0
    EvSy_ij = 0
    EvSy_ji = 0 

    for i in range (1,(event1-1)):
        for j in range (1,(event2-1)):
            delay = (min (timestamp_array1[i+1]-timestamp_array1[i],timestamp_array1[i]-timestamp_array1[i-1],timestamp_array2[j+1]-timestamp_array2[j],timestamp_array2[j]-timestamp_array2[j-1]))/2
                    
            waiting_time = timestamp_array1[i] - timestamp_array2[j]

            if -delay < waiting_time and waiting_time <= 0 and abs(waiting_time) <= k:
                EvSy_ij += 1
            if 0 <= waiting_time and waiting_time < delay and abs(waiting_time) <= k:
                EvSy_ji += 1
            if abs(waiting_time) <= delay and abs(waiting_time) <= k :
                EvSy_all += 1

    return(EvSy_ij,EvSy_ji,EvSy_all)

def get_events (data_array,event_threshold):

    date = np.zeros((len(data_array),))
    threshold = event_threshold
    date[data_array>threshold] = 1

    tmp = date[1:] + date[:-1]
    if date[0] == 0:
        tmp = np.insert(tmp,0,0)
    else:
        tmp = np.insert(tmp,0,1)

    loc = np.arange(len(data_array))
    tmp_1 = loc[tmp == 1]

    events_time = []
    for k in range (0,len(tmp_1),2):
        time_tmp = tmp_1[k]
        events_time.append(time_tmp)

    events_num = len(events_time)
    return(events_num)
#-----------------------------------------------------------------------------------------------------------------

absolute_address = '/mnt/data208/ChenJin/DOG/Work1/data'
data_address = absolute_address + '/SHUFFLED_DATA/FT_1.h5'
threshold_address = absolute_address + '/SHUFFLED_DATA/event_threshold.h5'
save_address = absolute_address + '/ALL/NULL_MODEL/EvSy_FT_1.h5'

f = h5py.File(data_address,'r')
data = f['Global'][:]
lat = f['lat'][:]
lon = f['lon'][:]
f.close()

f_threshold = h5py.File(threshold_address,'r')
threshold = f_threshold['threshold'][:]
f_threshold.close()
    
#-----------------------------------------------------------------------------------------------------------------

events  = np.zeros((len(lat),len(lon)))
EvSy_all = np.zeros((len(lat),len(lon),len(lat),len(lon)))
EvSy_ij = np.zeros((len(lat),len(lon),len(lat),len(lon)))
EvSy_ji = np.zeros((len(lat),len(lon),len(lat),len(lon)))

for i in range (0,len(lat),1):
    for j in range (0,len(lon),1):
        events[i,j] = get_events(data[...,i,j],threshold[i,j])

a=0
for m in range(0,len(lat),1):
    for n in range(0,len(lon),1):
        print(a)
        a+=1
        for p in range(0,len(lat),1):
            for q in range(0,len(lon),1):
                if m == p and n == q :
                    continue
                else:
                    ij,ji,ES = EvSy(get_time(data[...,m,n],threshold[m,n]),get_time(data[...,p,q],threshold[p,q]),30)
                    EvSy_ij[m][n][p][q] = ij
                    EvSy_ji[m][n][p][q] = ji
                    EvSy_all[m][n][p][q] = ES

f_w = h5py.File(save_address,'w')
f_w['EvSy_ij'] = EvSy_ij
f_w['EvSy_ji'] = EvSy_ji
f_w['EvSy_all'] = EvSy_all
f_w['events'] = events
f_w['lat'] = lat
f_w['lon'] = lon
f_w.close()

