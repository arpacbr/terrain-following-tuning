

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
from datetime import timedelta
import pandas as pd
import math

log_path =  '~/src/utilities/terrain-following-tuning/novo_tf/275/'
log_name = 'log_275_2019-5-14-09-59-02_'

#####################
csv_file = log_path + log_name + 'vehicle_global_position_0.csv'
data = pd.read_csv(csv_file)
timestamp1 = (data[:]['timestamp'])
timestamp1 = timestamp1.values
alt = (data[:]['alt'])
alt = alt.values
terrain_alt = (data[:]['terrain_alt'])
terrain_alt = terrain_alt.values
db =  alt - terrain_alt     #it's supposed to be equal to distance_bottom but we don't have distance_bottom yet to be sure...

############################
csv_file = log_path + log_name + 'distance_sensor_0.csv'
data = pd.read_csv(csv_file)
timestamp2 = (data[:]['timestamp'])
timestamp2 = timestamp2.values
current_distance = (data[:]['current_distance'])
current_distance = current_distance.values

ds_window_data = []
ds_window_timestamp = []

processed_residues = []
processed_timestamp = []

N_ds = 5        #how many samples you take to calculate the least square approx.

for element in enumerate(current_distance):
    index_cd , value_cd = element
    if(len(ds_window_data) < N_ds):
        ds_window_data.append(value_cd)
        ds_window_timestamp.append(timestamp2[index_cd])
    else:
        ds_window_data.pop(0)
        ds_window_timestamp.pop(0)
        ds_window_data.append(value_cd)
        ds_window_timestamp.append(timestamp2[index_cd])


        _, res, _, _, _ = np.polyfit(ds_window_timestamp,ds_window_data, 1, full=True)
        res = res
        print(res)
        #res = Sums of residuals; squared Euclidean 2-norm for each column in b - a*x
        processed_residues.append(res)
        processed_timestamp.append(timestamp2[index_cd])

##################################
#plot everything that's interesting
def mjrFormatter(timestamp, pos):
        hours = math.floor((timestamp/(1e6*60*60))%24)     #convert us -> hour
        residue = timestamp - hours*(1e6*60*60)             #residue in us
        minutes =  math.floor((residue/(1e6*60))%60)       #convert us -> minutes
        residue = residue - minutes*(1e6*60)                #residue in us
        seconds = math.floor((residue/(1e6))%60)
        microseconds = residue - seconds*1e6
        return "{0:0.0f}:{1:02.0f}".format(minutes,seconds)


fig, ax = plt.subplots()
fig.suptitle(log_name[0:-1], fontsize=16)
ax.plot(timestamp1, db,'r',label="alt - terrain_alt")
ax.plot(timestamp2,current_distance,'y--',label="current_distance")
ax.plot(processed_timestamp,processed_residues,'k',label="residues")

#ax.plot(timestamp3,dist_bottom,'b',label="dist_bottom")
#ax.plot(timestamp,_t_cnt_vector_will,'g.',label='tcnt',markersize=2)
leg = ax.legend(); #print legend
ax.xaxis.set_major_locator(mticker.AutoLocator())
ax.xaxis.set_major_formatter(mticker.FuncFormatter(mjrFormatter))
plt.xticks(rotation = 45)
plt.show() #display graph
