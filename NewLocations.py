import matplotlib.dates as mdates
myFmt = mdates.DateFormatter('%d %b')

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
plt.rcParams['figure.dpi']=600
plt.gcf().autofmt_xdate()

pd.set_option('display.max_columns', 15)
pd.set_option('display.width', 1000)
class Station:
    def __init__(self, lat=0, lon=0, name=""):
        self.name = name
        self.coor=[lat,lon]

def distance(station1,station2):
    return ((station1.coor[0]-station2.coor[0])**2+(station1.coor[1]-station2.coor[1])**2)**0.5

#Required to read excel file that contains station information
station_list=pd.read_excel("Stations.xlsx",index_col=(0))

stations = []
for i in range(station_list.shape[0]):
    stations.append(Station(station_list.iat[i,1],station_list.iat[i,2],station_list.iat[i,0]))

for i in stations:

    txt = i.name
    txt = txt.replace(" ", "_")
    url = f'https://raw.githubusercontent.com/flowonthegoliv/ENVS666/main/data/liverpool_ENVS666/{txt}.csv'
    
    i.data=pd.read_csv(url,header=None,dtype='unicode')
    i.data[i.data.columns[0]] = pd.to_datetime(i.data[i.data.columns[0]])

    i.data = i.data.rename({i.data.columns[0]: 'Date & Time'},axis=1)
    i.data = i.data.rename({i.data.columns[1]: 'NOx'},axis=1)
    i.data = i.data.rename({i.data.columns[2]: 'CO'},axis=1)
    i.data = i.data.rename({i.data.columns[3]: 'PM01'},axis=1)
    i.data = i.data.rename({i.data.columns[4]: 'PM25'},axis=1)
    i.data = i.data.rename({i.data.columns[5]: 'PM10'},axis=1)
    i.data = i.data.rename({i.data.columns[6]: 'Temperature'},axis=1)
    i.data = i.data.rename({i.data.columns[7]: 'Humidity'},axis=1)
    i.data = i.data.rename({i.data.columns[8]: 'Pressure'},axis=1)
    i.data = i.data.replace(['NaN'],'9999')
    i.data = i.data[i.data.columns[range(0,i.data.shape[1])]].apply(pd.to_numeric)
    i.data[i.data.columns[0]] = pd.to_datetime(i.data[i.data.columns[0]]);
    i.data = i.data.replace([9999],np.nan)
    
#We are removing extreme peaks in the data

for i in stations:
    i.data.loc[i.data['NOx']>500,'NOx']=np.nan

for i in stations:
    i.data.loc[i.data['PM01']>60,'PM01']=np.nan
    
for i in stations:
    i.data.loc[i.data['PM25']>150,'PM25']=np.nan

for i in stations:
    i.data.loc[i.data['PM10']>150,'PM10']=np.nan

mean_values=pd.DataFrame(columns = ['mean_NOx', 'mean_PM01','mean_PM25', 'mean_PM10'])
for i in stations:
    mean_values=mean_values.append({'mean_NOx':i.data['NOx'].mean(),'mean_PM01':i.data['PM01'].mean(),'mean_PM25':i.data['PM25'].mean(), 'mean_PM10':i.data['PM10'].mean()},ignore_index=True)    

NOx_1,NOx_2 = mean_values.nlargest(2,'mean_NOx').index.values
PM01_1,PM01_2  = mean_values.nlargest(2,'mean_PM01').index.values
PM25_1,PM25_2 = mean_values.nlargest(2,'mean_PM25').index.values
PM10_1,PM10_2 = mean_values.nlargest(2,'mean_PM10').index.values

center_coor=[station_list['Latitude'].mean(),station_list['Longitude'].mean()]

#1-New location based on mean_NOx load
total_NOx=mean_values.iat[NOx_1,0]+mean_values.iat[NOx_2,0]

dx=abs(stations[NOx_1].coor[0]-stations[NOx_2].coor[0])/total_NOx
dy=abs(stations[NOx_1].coor[1]-stations[NOx_2].coor[1])/total_NOx

if stations[NOx_1].coor[0] < stations[NOx_2].coor[0]:
    mid_x = stations[NOx_1].coor[0] + dx * mean_values.iat[NOx_2,0]#en sondaki 1 pm1 icin onu degistir
else:
    mid_x = stations[NOx_1].coor[0] - dx * mean_values.iat[NOx_2,0]

if stations[PM01_1].coor[1] > stations[PM01_2].coor[1]:
    mid_y = stations[NOx_1].coor[1] - dy * mean_values.iat[NOx_2,0]
else:
    mid_y = stations[NOx_1].coor[1] + dy * mean_values.iat[NOx_2,0]

mid_point=[mid_x,mid_y]
new_x=2*mid_point[0]-center_coor[0]
new_y=2*mid_point[1]-center_coor[1]
new_point=[new_x,new_y]

new_station_NOx=Station(new_point[0],new_point[1],'NOx based new point')

#2-New location based on mean_PM01 load
total_PM01=mean_values.iat[PM01_1,1]+mean_values.iat[PM01_2,1]

dx=abs(stations[PM01_1].coor[0]-stations[PM01_2].coor[0])/total_PM01
dy=abs(stations[PM01_1].coor[1]-stations[PM01_2].coor[1])/total_PM01

if stations[PM01_1].coor[0] < stations[PM01_2].coor[0]:
    mid_x = stations[PM01_1].coor[0] + dx * mean_values.iat[PM01_2,1]
else:
    mid_x = stations[PM01_1].coor[0] - dx * mean_values.iat[PM01_2,1]

if stations[PM01_1].coor[1] > stations[PM01_2].coor[1]:
    mid_y = stations[PM01_1].coor[1] - dy * mean_values.iat[PM01_2,1]
else:
    mid_y = stations[PM01_1].coor[1] + dy * mean_values.iat[PM01_2,1]

mid_point=[mid_x,mid_y]
new_x=2*mid_point[0]-center_coor[0]
new_y=2*mid_point[1]-center_coor[1]

new_point=[new_x,new_y]

new_station_PM01=Station(new_point[0],new_point[1],'PM01 based new point')

#3-New location based on mean_PM25 load
total_PM25=mean_values.iat[PM25_1,2]+mean_values.iat[PM25_2,2]

dx=abs(stations[PM25_1].coor[0]-stations[PM25_2].coor[0])/total_PM25
dy=abs(stations[PM25_1].coor[1]-stations[PM25_2].coor[1])/total_PM25

if stations[PM25_1].coor[0] < stations[PM25_2].coor[0]:
    mid_x = stations[PM25_1].coor[0] + dx * mean_values.iat[PM25_2,2]
else:
    mid_x = stations[PM25_1].coor[0] - dx * mean_values.iat[PM25_2,2]

if stations[PM25_1].coor[1] > stations[PM25_2].coor[1]:
    mid_y = stations[PM25_1].coor[1] - dy * mean_values.iat[PM25_2,2]
else:
    mid_y = stations[PM25_1].coor[1] + dy * mean_values.iat[PM25_2,2]

mid_point=[mid_x,mid_y]
new_x=2*mid_point[0]-center_coor[0]
new_y=2*mid_point[1]-center_coor[1]

new_point=[new_x,new_y]

new_station_PM25=Station(new_point[0],new_point[1],'PM25 based new point')

#4-New location based on mean_PM10 load
total_PM10=mean_values.iat[PM10_1,3]+mean_values.iat[PM10_2,3]

dx=abs(stations[PM10_1].coor[0]-stations[PM10_2].coor[0])/total_PM10
dy=abs(stations[PM10_1].coor[1]-stations[PM10_2].coor[1])/total_PM10

if stations[PM10_1].coor[0] < stations[PM10_2].coor[0]:
    mid_x = stations[PM10_1].coor[0] + dx * mean_values.iat[PM10_2,3]
else:
    mid_x = stations[PM10_1].coor[0] - dx * mean_values.iat[PM10_2,3]

if stations[PM10_1].coor[1] > stations[PM10_2].coor[1]:
    mid_y = stations[PM10_1].coor[1] - dy * mean_values.iat[PM10_2,3]
else:
    mid_y = stations[PM10_1].coor[1] + dy * mean_values.iat[PM10_2,3]

mid_point=[mid_x,mid_y]
new_x=2*mid_point[0]-center_coor[0]
new_y=2*mid_point[1]-center_coor[1]

new_point=[new_x,new_y]

new_station_PM10=Station(new_point[0],new_point[1],'PM10 based new point')

new_stations=np.array([new_station_NOx.coor,new_station_PM01.coor,new_station_PM25.coor,new_station_PM10.coor])

labels=[new_station_NOx.name,new_station_PM01.name,new_station_PM25.name,new_station_PM10.name,]

plt.scatter(new_stations[:,1],new_stations[:,0])

#new_stations variable contains all calculated coordinates 
print("all code worked")