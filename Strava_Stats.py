##### A CLASS TO PULL STRAVA STATISTICS                      ######
##### THE 'STRAVIO' FUNCTION WON'T BE USED FROM THIS CLASS   ######
##### THE STRAVLIB FUNCTION WILL BE USED INSTEAD AS IT SEEMS EASIER 



import requests
import urllib3
# import xmltodict
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
# from stravaio import StravaIO
# from stravaio import strava_oauth2
from pprint import pprint # just a handy printing function
from datetime import datetime, timedelta
import pandas as pd
import math
import time
import json
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.dates as mdates



class StravaStats:
    
    def __init__(self):
        
        self.activites_url = "https://www.strava.com/api/v3/athlete/activities"
        self.request_page_num = 1
        self.all_activities_list = []
        self.activitiesbyid_url = "https://www.strava.com/api/v3/activities/{}"
                
    # def authenticate(self,id,secret):
    #     token = strava_oauth2(client_id=id, client_secret=secret)
    #     strava_access_token=token['access_token']
    #     return token

    # def start_client(self,id,secret):
    #     strava_access_token = self.authenticate(id,secret)
    #     client = StravaIO(access_token=strava_access_token)
    #     header = {'Authorization': 'Bearer ' + strava_access_token['access_token']}
    #     return header     
    
    def all_activities(self,header):
        all_activities_list = []
        
        while True:
            param = {'per_page': 200, 'page': self.request_page_num}
            # initial request, where we request the first page of activities
            my_dataset = requests.get(self.activites_url, headers=header, params=param).json()

            # check the response to make sure it is not empty. If it is empty, that means there is no more data left. So if you have
            # 1000 activities, on the 6th request, where we request page 6, there would be no more data left, so we will break out of the loop
            if len(my_dataset) == 0:
                print("breaking out of while loop because the response is zero, which means there must be no more activities")
                break

            # if the all_activities list is already populated, that means we want to add additional data to it via extend.
            if all_activities_list:
                print("all_activities is populated")
                all_activities_list.extend(my_dataset)

            # if the all_activities is empty, this is the first time adding data so we just set it equal to my_dataset
            else:
                print("all_activities is NOT populated")
                all_activities_list = my_dataset

            self.request_page_num += 1
            
        return all_activities_list
    
    def activities_list(self,dataset,distance,last_x):
        activity_list = []
        for i in range (0,len(dataset)):
            x = (math.floor(dataset[i]['distance']/1000)*1000)
            if dataset[i]['type'] == "Run" and x == distance:
                if len(activity_list) < last_x:
                    activity_list.append(dataset[i]['id'])
        return activity_list
    
    def batchsize(self,batch_size,activity_list):
        id_batches = [activity_list[i:i + batch_size] for i in range(0, len(activity_list), batch_size)]
        return id_batches
    
    def pull_activity(self,runid,header):
        url = self.activitiesbyid_url.format(runid)
        activities = requests.get(url, headers=header).json()
        return activities
    
    def convert_to_seconds(self,value):
        minutes, seconds = divmod(value, 1)
        seconds=int(minutes) * 60 + int(seconds * 100)
        seconds=int(seconds)
        return seconds

    def convert_to_seconds_df(self,input_df,column):
        date_list = input_df.index.tolist()
        val_list = []
        for d in date_list:
            minutes, seconds = divmod(input_df.loc[d,column], 1)
            val_list.append(int(minutes) * 60 + int(seconds * 100))
        return val_list

    def convert_to_minutes(self,value):
        q = str(value//60)
        r = str(value%60)
        r = r.zfill(2)
        combined = float((q) + '.' + (r))
        return combined
    
    def multi_activities(self,batch_size,activity_list,header):
        test_list = []
        distance_list = []
        date_list = []
        best_time = []
        be_list = []
        runid_list=[]
        
        id_batches = self.batchsize(batch_size,activity_list)

        for batch_num, id_batch in enumerate(id_batches,start=1):
            print(f"Processing batch {batch_num}")
            for i in id_batch:
                activity=self.pull_activity(i,header)
                if len(activity) == 63:
                    runid_list.append(activity['id']) 
                    test_list.append(len(activity))
                    distance_list.append(activity['distance'])
                    datetime_obj = datetime.strptime(activity['start_date'], '%Y-%m-%dT%H:%M:%S%z')      
                    date=datetime_obj.date()
                    date_list.append(date)
                    be_list.append(len(activity['best_efforts']))
                    if len(activity['best_efforts']) == 6:
                        seconds=activity["best_efforts"][5]["elapsed_time"]
                        combined = self.convert_to_minutes(seconds)
                        best_time.append(combined)                         
                    elif len(activity['best_efforts']) == 7:
                        seconds=activity["best_efforts"][6]["elapsed_time"]
                        combined = self.convert_to_minutes(seconds)
                        best_time.append(combined)  
                    else:
                        best_time.append(0)
                        
        rev_runid=list(reversed(runid_list))
        rev_best=list(reversed(best_time))
        rev_dates=list(reversed(date_list))
        rev_dist = list(reversed(distance_list))

        data = {
            "RunID":rev_runid,
            "Date":rev_dates,
            "Distance":rev_dist,
            "Best_Time":rev_best
        }

        df = pd.DataFrame(data)
        df['Date'] = pd.to_datetime(df['Date'])
        
        return df
    
    def rolling_df(self,input_df,window):
        input_df['seconds']=input_df["Best_Time"].apply(self.convert_to_seconds)
        rolling_mean = input_df["seconds"].rolling(window=window).mean()
        rolling_median = input_df["seconds"].rolling(window=window).median()
        input_df["rolling_mean"] = rolling_mean
        input_df["rolling_median"] = rolling_median
        input_df2=input_df.fillna(0)
        input_df2["rolling_mean"] = input_df2["rolling_mean"].astype(int)
        input_df2["rolling_median"] = input_df2["rolling_median"].astype(int)
        input_df2["rolling_mean"] = input_df2["rolling_mean"].apply(self.convert_to_minutes)
        input_df2["rolling_median"] = input_df2["rolling_median"].apply(self.convert_to_minutes)   
        return input_df2
    
    
    def basic_stats(self,input_df):
        sec_list = self.convert_to_seconds_df(input_df,'Best_Time')
        mean_seconds = sum(sec_list)/len(sec_list)
        mean_of_runs = self.convert_to_minutes(int(mean_seconds))

        sec_list.sort() 
        mid = len(sec_list) // 2
        res = (sec_list[mid] + sec_list[~mid]) / 2

        median_of_runs = self.convert_to_minutes(int(res))

        fastest_time = input_df['Best_Time'].min()
        fastest_day = input_df.loc[input_df['Best_Time'] == fastest_time,'Date'].squeeze()
        slowest_time = input_df['Best_Time'].max()
        slowest_day = input_df.loc[input_df['Best_Time'] == slowest_time,'Date'].squeeze()
        print(f" Average Run Time is {round(mean_of_runs,2)}")
        print(f" Median Run Time is {median_of_runs}")     
        print(f" The fastest time was {fastest_time}, on the {fastest_day}")
        print(f" The slowest time was {slowest_time}, on the {slowest_day}")
        latest_date = input_df['Date'].max()
        last_run_time = input_df.loc[input_df['Date'] == latest_date,'Best_Time'].squeeze()
        current_time_delta = self.convert_to_seconds(last_run_time)-self.convert_to_seconds(mean_of_runs)

        if current_time_delta <- 0:
            print(f" Your last run was {abs(round(current_time_delta,2))} seconds faster then your average")
        else:
            print(f" Your last run was {abs(round(current_time_delta,2))} seconds slower then your average")
            

    def plot(self,df):
        df['rolling_mean'] = df['rolling_mean'].replace(0, np.nan)
        df['rolling_median'] = df['rolling_median'].replace(0, np.nan)
        plt.figure(figsize=(15, 15)) 
        # plt.ylim(ymin=0)
        # plt.ylim(bottom=28,top=40)
        ax = plt.axes()
        ax.set_facecolor("aliceblue",)

        # Format the x-axis to show every month    
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
        # Rotate x-axis labels for better readability
        plt.xticks(rotation=45)
        plt.scatter(df['Date'],df['Best_Time'],edgecolors='black',c='white',s=200)
        # plt.scatter(new_df['Date'],new_df['10k_time'],edgecolors='black',c='blue',s=200)
        plt.plot(df['Date'],df['rolling_mean'],lw=10,c='red',alpha=0.5)
        plt.plot(df['Date'],df['rolling_median'],lw=10,c='green',alpha=0.5)
        plt.ylabel('5k time',fontname="Arial", fontsize=20)
        plt.xlabel('Date',fontname="Arial", fontsize=20)
        plt.xticks(rotation=90,fontname="Arial", fontsize=20)
        plt.yticks(np.arange(round(df['Best_Time'].min(),0)-1,df['Best_Time'].max()+1 , step=1),fontname="Arial", fontsize=20)
        plt.grid(linestyle='--')
        plt.show()
