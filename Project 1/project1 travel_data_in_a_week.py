# -*- coding: utf-8 -*-
"""
Created on Sun Oct 29 18:55:36 2017

@author: yangliu
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

os.chdir(r"C:\Users\10245\Desktop\Data Vis\Project 1")

xlsx=pd.ExcelFile('bicycle.xlsx')
walk=xlsx.parse('Walking')
data=xlsx.parse('Bicycle')
walk.dropna(axis=0,how='any',inplace=True)
data.dropna(axis=0,how='any',inplace=True)

#daily travel distance
freq=data['DATE'].value_counts().sort_index()
date=freq.index
duration=[]
bicy_dist=[]
for t in freq.index:
    block=data[data['DATE']==t]
    duration.append(block['DURATION'].sum())
    bicy_dist.append(block['DISTANCE'].sum())
bicy_dist=np.array(bicy_dist)
distance=bicy_dist+walk['DISTANCE']#total distance each day

plt.style.use('ggplot')
#plot daily travel distance
fig,axes=plt.subplots(2,1,figsize=(9,9))
axes[0].bar(date,distance,width=0.5)
axes[1].bar(date,distance,width=0.5)
axes[1].set_ylim(8,18)
axes[0].set_title('(a) Default limit: start from 0',fontsize=10)
axes[1].set_title('(b) Modified limit: [8,18]',fontsize=10)
def labels(axes):
    for ax in axes:
        ax.set_xlabel('Date')
        ax.set_ylabel('Daily Travel Distance(KM)')
labels(axes)
fig.suptitle('Comparison between Different Data Limits',fontsize=12)
fig.subplots_adjust(hspace=0.4)
plt.savefig('Daily_travel_distance.png',dpi=800)
plt.show()

#Daily_Travel_Distance()
num_days=len(date)
num_periods=24
data['tag_time']=[t.hour for t in data['TIME']]
img=np.zeros((num_periods,num_days))
for t in freq.index:
    block=data[data['DATE']==t]
    tag_time=block['tag_time'].value_counts().sort_index()
    img[tag_time.index,t.day-date[0].day]=tag_time.values
#pDaily_Travel_Distance()
fig,axes=plt.subplots(figsize=(3,6))
axes.set_title('Daily Riding Periods')
axes.set_xlabel('Date')
axes.set_ylabel('Time Period')
cr=axes.imshow(img,cmap=plt.cm.gray)
axes.set_xticks(range(num_days))
axes.set_yticks(range(num_periods),range(num_periods))
axes.yaxis.set_major_locator(ticker.MultipleLocator(2))
def format_date(val,pos=None):
    if val%2==0:
        return date[val].strftime('%m-%d')
    else:
        return ''
axes.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))
# Move left and bottom spines outward by 10 points
axes.spines['left'].set_position(('outward', 5))
axes.spines['bottom'].set_position(('outward', 5))
# Hide the right and top spines
axes.spines['right'].set_visible(False)
axes.spines['top'].set_visible(False)
# Only show ticks on the left and bottom spines
axes.yaxis.set_ticks_position('left')
axes.xaxis.set_ticks_position('bottom')
axes.grid(False)
fig.autofmt_xdate()
cbar=fig.colorbar(cr)
plt.savefig('Daily_Riding_Periods.png',dpi=800)
plt.show()

