from flask import Flask, render_template, request,send_file,session
import io
import base64
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import seaborn as sns
import numpy as np
import pandas as pd
import requests
import urllib3
# import xmltodict
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from stravaio import StravaIO
from pprint import pprint # just a handy printing function
from stravaio import strava_oauth2
from datetime import datetime, timedelta

app=Flask(__name__)
app.secret_key = "Lis@2104"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/input')
def input():
    client_id = "96903"
    client_secret = "0f4e7f68927263eb277b60fa2ef396b7964cdc94"

    token = strava_oauth2(client_id=client_id, client_secret=client_secret)
    strava_access_token=token['access_token']
    # First_name=token['firstname']
    # Surname=token['lastname']
    session['sac'] = strava_access_token

    return render_template('input.html',strava_access_token=strava_access_token,token=token)

@app.route('/lastruns')
def lastruns():
    strava_access_token = session.get('sac') 
    activites_url = "https://www.strava.com/api/v3/athlete/activities"
    header = {'Authorization': 'Bearer ' + strava_access_token}
    param = {'per_page': 200, 'page': 1}
    my_dataset = requests.get(activites_url, headers=header, params=param).json()
    print(header)
    activitiesbyid_url = "https://www.strava.com/api/v3/activities/{}"
    # url = activitiesbyid_url.format(runid)

    best_5k_ls = []
    name_ls = []
    date_ls = []

    its = len(my_dataset)

    run_ls=[]
    for i in range (0,20):
        run_ls.append(my_dataset[i]['id'])

    best_5k_ls=[]
    best_5k_qls=[]
    best_5k_rls=[]
    date_ls=[]
    for i in range (0,len(run_ls)):
        runid = run_ls[i]
#     print(runid)
        url = activitiesbyid_url.format(runid)
        activities = requests.get(url, headers=header).json()
        #WORK OUT LENGTH OF BEST ACTIVITIES DICTIONARY
    
        print(url)
#       print(activities)

        if len(activities) == 63:
            if len(activities['best_efforts']) > 5:
                datetime_obj = datetime.strptime(activities['start_date'], '%Y-%m-%dT%H:%M:%S%z')      
                date=datetime_obj.date()
                date_ls.append(date)

                best_5k_qls.append(activities["best_efforts"][5]["elapsed_time"]//60)
                best_5k_rls.append(activities["best_efforts"][5]["elapsed_time"]%60)
                best_5k_ls.append(activities["best_efforts"][5]["elapsed_time"]/60)

                # best_5k_ls.reverse()
                # date_ls.reverse()
                # best_5k_qls.reverse()
                # best_5k_rls.reverse()

   
    return render_template('lastruns.html',best_5k_ls=best_5k_ls,date_ls=date_ls,best_5k_rls=best_5k_rls,
                           best_5k_qls=best_5k_qls)


@app.route('/calculate')
def calculate():
    balance = request.args.get('balance')
    apr = request.args.get('APR')
    min_pay = request.args.get('min_pay')
    its=0
    total_int = 0
    cbal = int(balance)
    bal_list=[]
    while cbal > 0:
        its = its + 1
        int_amt = round(cbal*((float(apr)/100)/12),2)
        pay_amt = round(max(cbal*(float(min_pay)/100)+int_amt,5),2)
        nbal = cbal+int_amt-pay_amt
        cbal = round(nbal,2)  
        total_int = round(total_int+int_amt,2)
        bal_list.append(cbal)
        xax = list(range(its))

#start to make chart object
    fig,ax=plt.subplots(figsize=(6,6))
    ax=sns.set(style="darkgrid")
    sns.lineplot(x=xax,y=bal_list).set(title="Paydown Curve")
    canvas=FigureCanvas(fig)
# 'converts chart into bytes'
    img=io.BytesIO()
    fig.savefig(img)
    img.seek(0)
#GETS THE VALUE OF THE CHART AND PUTS IN A VARIABLE
    plot_url = base64.b64encode(img.getvalue()).decode('utf8')
    return render_template('calculate.html',plot_url=plot_url,
                            balance=balance,apr=apr,
                            min_pay=min_pay,its=its,
                            total_int=total_int)

@app.route('/username_report')
def username_report():
    username = request.args.get('username')
        # <li>Have a capital letter</li>
        # <li>Have a lowercase letter</li>
        # <li>Have a number at the end</li>
    upper = 0
    lower = 0
    for i in username:
        if i.isupper():
            upper=upper + 1
    if upper > 0:
        upper = True

    for i in username:
        if i.islower():
            lower=lower + 1
    if lower > 0:
        lower = True

    num_end = username[-1].isdigit()

    report = upper and lower and num_end


    return render_template('username_report.html',username=username,upper=upper,lower=lower,num_end=num_end,report=report)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('/404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)  