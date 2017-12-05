# -*- coding: utf-8 -*-
"""
@author: yangliu

"""

#%% load modules
import os
import pandas as pd
import re
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib as mpl
import plotly as py
from plotly.graph_objs import *
#%% load data
os.chdir(r'C:\Users\10245\Desktop\Courses\Data Vis\Assi 2 committe')
data=pd.read_excel('committe.xlsx',index_col=0)
#行政区表格
loca=pd.read_excel('location.xlsx')
province=set(loca['province'])#省份
bj=loca.iloc[0,:]#北京
#%% 找出每个人任职过的单位和对应时间段
persons={}
for name in data.index:
    person=[]
    experience=data.loc[name,'履历']#个人履历
    lines=experience.splitlines()#将履历各条记录分开
    for line in lines:
        start=np.nan#某一阶段的任职开始时间，初始化
        end=np.nan#某一阶段的任职结束时间，初始化
        parts=line.split(',')
        if len(parts)==1:
            description=parts[0]
        else:
            description=''
            for i in range(1,len(parts)):
                description+=parts[i]
            date=re.findall('\d{4}',parts[0])
            if len(date)==2:
                start=int(date[0])
                end=int(date[1])
            elif len(date)==1:
                if line==lines[0]:
                    end=date[0]
                elif line==lines[-1]:
                    start=date[0]

        flag_county=False
        for county in loca['county']:
            res_county=re.findall(county,description)
            if len(res_county)>=1:
                flag_county=True
                break
        if flag_county==True:#在县级单位任职
            temp=loca[loca['county']==res_county[0]]
            temp=temp.iloc[0,:]
            person.append([start,end,temp['province'],temp['city'],temp['county'],temp['long'],temp['lat']])
        else:
            flag_city=False
            for city in loca['city']:
                res=re.findall(city,description)
                if len(res)>=1:
                    flag_city=True
                    break
            if flag_city==True:#在市级行政单位任职
                temp=loca[loca['city']==res[0]]
                temp=temp.iloc[0,:]
                person.append([start,end,temp['province'],temp['city'],temp['city'],temp['long'],temp['lat']])

            else:
                flag_pro=False
                for p in loca['province']:
                    res=re.findall(p,description)
                    if len(res)>=1:
                        flag_pro=True
                        break
                if flag_pro==True:#在省级行政单位任职
                     temp=loca[loca['province']==res[0]]
                     temp=temp.iloc[0,:]
                     person.append([start,end,temp['province'],temp['province'],temp['province'],temp['long'],temp['lat']])
                else:
                     res=re.findall('中央',description)
                     if len(res)>=1:#在中央任职
                         person.append([start,end,'中央','中央','中央',bj['long'],bj['lat']])
    person=pd.DataFrame(person,columns=['start','end','province','city','county','long','lat'])
    if len(person)==0:
        continue
    else:
        persons[name]=person

#%%任职所在地经纬度
geoCoordMap={}
for key,value in persons.items():
    person=persons[key]
    for i in person.index:
        geoCoordMap[person.loc[i,'county']]=[person.loc[i,'long'],person.loc[i,'lat']]
#%%#挖掘委员之间共事次数
processed=[]
links={}
for name1,person1 in persons.items():
    processed.append(name1)
    sites1=set(person1['county'])
    for name2,person2 in persons.items():
        if name2 not in processed:
            links[(name1,name2)]=0#default link:0
            sites2=set(person2['county'])
            common=sites1 & sites2
            if len(common)>0:#在同一地点工作过，但不一定在同一时间段
                for c in common:
                    if c=='中央':
                        continue
                    #下面判断是否在同一时间段
                    temp1=np.array(person1[person1['county']==c].iloc[0,:])
                    temp2=np.array(person2[person2['county']==c].iloc[0,:])
                    if not isinstance(temp1[0],float) and isinstance(temp1[1],float):
                        if not float(temp2[1])<float(temp1[0]) or float(temp2[0])>float(temp1[1]):
                            links[(name1,name2)]+=1
                    elif isinstance(temp1[0],float):
                        if not float(temp2[0])>float(temp1[1]):
                            links[(name1,name2)]+=1
                    elif isinstance(temp1[1],float):
                        if not float(temp2[1])<float(temp1[0]):
                            links[(name1,name2)]+=1
#%%#提取共事次数在0以上的记录
elist=[]
for key,value in links.items():
    if value!=0:
        elist.append((key[0],key[1],value))
#%%#共事网络图
G=nx.Graph()
G.add_weighted_edges_from(elist)
pos=nx.spring_layout(G,iterations=100)
#%%
edge_trace = Scatter(
    x=[],
    y=[],
    text=[],
    line=Line(width=0.5,color='#888'),
    hoverinfo='text',
    mode='lines')
for edge in G.edges():
    x0, y0 =pos[edge[0]]
    x1, y1 =pos[edge[1]]
    edge_trace['x'] += [x0, x1, None]
    edge_trace['y'] += [y0, y1, None]
    edge_trace['text'].append(edge[0]+'-'+edge[1])

node_trace = Scatter(
    x=[],
    y=[],
    text=[],
    mode='markers',
    hoverinfo='text',
    marker=Marker(
        showscale=True,
        # colorscale options
        # 'Greys' | 'Greens' | 'Bluered' | 'Hot' | 'Picnic' | 'Portland' |
        # Jet' | 'RdBu' | 'Blackbody' | 'Earth' | 'Electric' | 'YIOrRd' | 'YIGnBu'
        colorscale='YIGnBu',
        reversescale=True,
        color=[],
        size=10,
        colorbar=dict(
            thickness=15,
            title='Node Connections',
            xanchor='left',
            titleside='right'
        ),
        line=dict(width=2)))

for node in G.nodes():
    x, y = pos[node]
    node_trace['x'].append(x)
    node_trace['y'].append(y)
nodes=G.nodes()
for node, adjacencies in enumerate(G.adjacency_list()):
    node_trace['marker']['color'].append(len(adjacencies))
    adj=adjacencies[0]
    for i in range(1,len(adjacencies)):
        adj+=' '+adjacencies[i]
    node_info = nodes[node]+'. 共事次数: '+str(len(adjacencies))+'\t 共事委员：'+adj
    node_trace['text'].append(node_info)
fig = Figure(data=Data([edge_trace, node_trace]),
             layout=Layout(
                title='<br> 中央委员共事情况',
                titlefont=dict(size=16),
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20,l=5,r=5,t=40),
                xaxis=XAxis(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=YAxis(showgrid=False, zeroline=False, showticklabels=False)))

py.offline.plot(fig, filename='Network.html')

