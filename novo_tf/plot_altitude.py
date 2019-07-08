import pandas as pd
from datetime import timedelta
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import math
import numpy as np
import os

log_path =  '~/src/utilities/novo_tf/275/'
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
diff =  alt - terrain_alt

############################
csv_file = log_path + log_name + 'distance_sensor_0.csv'
data = pd.read_csv(csv_file)
timestamp2 = (data[:]['timestamp'])
timestamp2 = timestamp2.values
current_distance = (data[:]['current_distance'])
current_distance = current_distance.values

##############################
csv_file = log_path + log_name + 'vehicle_local_position_0.csv'
data = pd.read_csv(csv_file)
timestamp3 = (data[:]['timestamp'])
timestamp3 = timestamp3.values
dist_bottom = (data[:]['dist_bottom'])
dist_bottom = dist_bottom.values


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
ax.plot(timestamp1, diff,'r',label="alt - terrain_alt")
ax.plot(timestamp2,current_distance,'y--',label="current_distance")
#ax.plot(timestamp3,dist_bottom,'b',label="dist_bottom")
#ax.plot(timestamp,_t_cnt_vector_will,'g.',label='tcnt',markersize=2)
leg = ax.legend(); #print legend
ax.xaxis.set_major_locator(mticker.AutoLocator())
ax.xaxis.set_major_formatter(mticker.FuncFormatter(mjrFormatter))
plt.xticks(rotation = 45)
plt.show() #display graph
