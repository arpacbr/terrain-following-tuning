

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
from datetime import timedelta
import pandas as pd
import math

log_path =  '~/src/utilities/terrain-following-tuning/novo_tf/277/'
log_name = 'log_277_2019-5-14-10-30-22_'

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



############################LEAST SQUARES######################################
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
        #res = Sums of residuals; squared Euclidean 2-norm for each column in b - a*x
        processed_residues.append(res)
        processed_timestamp.append(timestamp2[index_cd])

print("residues lenght:")
print(len(processed_residues))

####################################VARIANCE FILTER###########################################
moving_diff = []
index_db = 0        #index distance_bottom
max_index_db = len(timestamp1)-1;

for element in enumerate(current_distance):
    index_cd , value_cd = element
    while ( (timestamp2[index_cd]> timestamp1[index_db]) and index_db < (max_index_db-1) ):
        index_db = index_db + 1

    moving_diff.append(np.square(value_cd - db[index_db-1]))

N = 7    #how many samples you take to take the average. always odd in this code
#considering an window...
moving_var = np.convolve(moving_diff, np.ones((N,))/N, mode='valid')       #https://stackoverflow.com/questions/13728392/moving-average-or-running-mean
off = (len(current_distance) - len(moving_var))/2
moving_var_timestamp = timestamp2[off:-off]

moving_dev = np.sqrt(moving_var)
moving_dev_timestamp = moving_var_timestamp

print("moving_var lenght:")
print(len(moving_var))

######################COMBINE###########################

combined_data = []
combined_timestamp = []


counter_data = []
over_crop_data = []
over_crop_timestamp = []

threshold = 0.15       #unit: m^2
time_counter = 0
tf_over_crop = 0       #current value, iteration dependent variable
combined_index = 0

param_tf_delay_rc = 5           #unit:samples
param_tf_delay_cr = 5           #unit:samples

for mv_element in enumerate(moving_dev_timestamp):
    mv_index , mv_ts = mv_element

    for pr_element in enumerate(processed_timestamp):
        pr_index , pr_ts = pr_element

        if(mv_ts == pr_ts):
            value = processed_residues[combined_index]
            timestamp = mv_ts
            combined_data.append(value)
            combined_timestamp.append(timestamp)

            if(tf_over_crop == 0):

                if(combined_data[combined_index]>threshold):
                    time_counter = time_counter + 1

                    if(time_counter >= param_tf_delay_rc):
                        tf_over_crop = 1
                        time_counter = 0

                elif(time_counter > 0):
                        time_counter = time_counter - 1;

            else: #if tf_over_crop == 1
                if(combined_data[combined_index]<threshold):
                    time_counter = time_counter + 1

                    if(time_counter >= param_tf_delay_cr):
                        tf_over_crop = 0
                        time_counter = 0

                elif(time_counter > 0):
                    time_counter = time_counter - 1

            combined_index = combined_index + 1
            counter_data.append(time_counter)
            over_crop_data.append(tf_over_crop)
            over_crop_timestamp.append(mv_ts)

            break

print("combined lenght:")
print(len(combined_data))



#######$$$$$$$$$$$$$$$$$$$$$$$PLOT$$$$$$$$$$$$$$$$$$$$$$################
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
ax.plot(timestamp1, db,'c',label="alt - terrain_alt")
ax.plot(timestamp2,current_distance,'y--',label="current_distance")
ax.plot(processed_timestamp,processed_residues,'k',label="residues")
ax.plot(moving_dev_timestamp,moving_dev,'b',label="moving_dev")
ax.plot(combined_timestamp,combined_data, 'm', label="combined" )
ax.plot(over_crop_timestamp,over_crop_data, 'r', label = "over_crop: true(1), false(0)")
plt.minorticks_on()
plt.grid(True, which = 'both')

#ax.plot(timestamp3,dist_bottom,'b',label="dist_bottom")
#ax.plot(timestamp,_t_cnt_vector_will,'g.',label='tcnt',markersize=2)
leg = ax.legend(); #print legend
ax.xaxis.set_major_locator(mticker.AutoLocator())
ax.xaxis.set_major_formatter(mticker.FuncFormatter(mjrFormatter))
plt.xticks(rotation = 45)
plt.show() #display graph
