from flask import Flask, render_template, request,send_file,session,url_for
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
from pprint import pprint # just a handy printing function
from stravalib import Client
from datetime import datetime, timedelta
from flask_wtf import FlaskForm
from wtforms import (StringField, SubmitField,BooleanField,DateTimeField,
                    SelectField,TextAreaField,RadioField,StringField)
from wtforms.validators import DataRequired
from guitar import Guitar
from Strava_Stats import StravaStats
import fretboard  
# from IPython.display import SVG, display


import os
os.environ['APP_SETTINGS'] = 'settings.cfg'


app=Flask(__name__)
app.secret_key = "Lis@2104"

#put these in enviroment vars

app.config.from_envvar("APP_SETTINGS")


# client_id = "96903"
# client_secret = "0f4e7f68927263eb277b60fa2ef396b7964cdc94"


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/strava')
def index():
    c = Client()
    url = c.authorization_url(client_id=app.config["CLIENT_ID"],
                            redirect_uri=url_for('.lastruns',_external=True )
                            ,scope=['read_all','profile:read_all','activity:read_all'],
                            approval_prompt="force")
    print(url)
    return render_template('index.html',authorize_url=url)

@app.route('/lastruns')
def lastruns():

    code = request.args.get("code")
    stuff = request.view_args.items
    print(code)
    print(stuff)
    client = Client()
    access_token = client.exchange_code_for_token(
                                                    client_id=app.config["CLIENT_ID"],
                                                    client_secret=app.config["CLIENT_SECRET"],
                                                    code=code,
                                                )
    # Probably here you'd want to store this somewhere -- e.g. in a database.
    strava_athlete = client.get_athlete()
    # print(access_token['access_token'])
    session['sac'] = access_token['access_token']


    return render_template('lastruns.html',code=code,athlete=strava_athlete,access_token=access_token,)


strava=StravaStats()

@app.route('/lastruns2')
def lastruns2():
    strava_access_token = session.get('sac') 
    header2 = {'Authorization': 'Bearer ' + strava_access_token}

    print(f'Access Token: {strava_access_token}')
    print(f'Header: {header2}')
 
    actlist = strava.all_activities(header2)
    testlist = strava.activities_list(actlist,5000,50)
    testdf = strava.multi_activities(50,testlist,header2)
    testdf2 = strava.rolling_df(testdf,3)



   
    return render_template('lastruns2.html',
                            tables=[testdf2.to_html(classes='data')], titles=testdf2.columns.values)


# @app.route('/calculate')
# def calculate():
#     balance = request.args.get('balance')
#     apr = request.args.get('APR')
#     min_pay = request.args.get('min_pay')
#     its=0
#     total_int = 0
#     cbal = int(balance)
#     bal_list=[]
#     while cbal > 0:
#         its = its + 1
#         int_amt = round(cbal*((float(apr)/100)/12),2)
#         pay_amt = round(max(cbal*(float(min_pay)/100)+int_amt,5),2)
#         nbal = cbal+int_amt-pay_amt
#         cbal = round(nbal,2)  
#         total_int = round(total_int+int_amt,2)
#         bal_list.append(cbal)
#         xax = list(range(its))

# #start to make chart object
#     fig,ax=plt.subplots(figsize=(6,6))
#     ax=sns.set(style="darkgrid")
#     sns.lineplot(x=xax,y=bal_list).set(title="Paydown Curve")
#     canvas=FigureCanvas(fig)
# # 'converts chart into bytes'
#     img=io.BytesIO()
#     fig.savefig(img)
#     img.seek(0)
# #GETS THE VALUE OF THE CHART AND PUTS IN A VARIABLE
#     plot_url = base64.b64encode(img.getvalue()).decode('utf8')
#     return render_template('calculate.html',plot_url=plot_url,
#                             balance=balance,apr=apr,
#                             min_pay=min_pay,its=its,
#                             total_int=total_int)

#define some globel variable
guitar = Guitar()
scale_types = guitar.scale_dict
tuning_types = guitar.tuning_dict

@app.route('/guitarscale', methods=['GET', 'POST'])
def guitarscale():
    if request.method == 'POST':
        # Get form inputs

        # scale_type = request.form['scale_type']
        scale_type = request.form.get('scale_type', 'maj_scale')
        root = request.form['root_note']
        tuning_type = request.form.get('tuning_type', 'standard')
        svg_file = "static/test.png"

        guitar.draw_fretboard(0,12,root,scale_type,tuning_type,0,svg_file)
        svg_image=guitar.get_svg_string(svg_file)
        svg_image_base64 = base64.b64encode(svg_image.encode('utf-8')).decode('utf-8')


        return render_template('guitarscale.html',
                               svg_image=svg_image_base64,
                            scale_types=scale_types,scale_type=scale_type,tuning_types=tuning_types,root=root,tuning_type=tuning_type
                            #    ,root_note=root_note
                            )
    return render_template('guitarscale.html',
                           svg_image=None,
                           scale_types=scale_types,tuning_types=tuning_types
                        #    ,root_note=root_note
                           )


@app.errorhandler(404)
def page_not_found(e):
    return render_template('/404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)  