

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

print(len(db))
print(len(current_distance))

moving_diff = []
index_db = 0        #index distance_bottom
max_index_db = len(timestamp1)-1;

for element in enumerate(current_distance):
    index_cd , value_cd = element
    while ( (timestamp2[index_cd]> timestamp1[index_db]) and index_db < (max_index_db-1) ):
        index_db = index_db + 1

    moving_diff.append(np.square(value_cd - db[index_db-1]))

print(len(moving_diff))
N = 7    #how many samples you take to take the average. always odd in this code
#considering an window...
moving_var = np.convolve(moving_diff, np.ones((N,))/N, mode='valid')       #https://stackoverflow.com/questions/13728392/moving-average-or-running-mean
off = (len(current_distance) - len(moving_var))/2
moving_var_timestamp = timestamp2[off:-off]

moving_dev = np.sqrt(moving_var)
moving_dev_timestamp = moving_var_timestamp


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
ax.plot(moving_var_timestamp,moving_var,'k',label="moving_var")
ax.plot(moving_dev_timestamp,moving_dev,'b',label="moving_dev")

#ax.plot(timestamp3,dist_bottom,'b',label="dist_bottom")
#ax.plot(timestamp,_t_cnt_vector_will,'g.',label='tcnt',markersize=2)
leg = ax.legend(); #print legend
ax.xaxis.set_major_locator(mticker.AutoLocator())
ax.xaxis.set_major_formatter(mticker.FuncFormatter(mjrFormatter))
plt.xticks(rotation = 45)
plt.show() #display graph
