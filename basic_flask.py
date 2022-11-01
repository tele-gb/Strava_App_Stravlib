from flask import Flask, render_template, request,send_file
import io
import base64
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
import seaborn as sns
import numpy as np
import pandas as pd

app=Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/input')
def input():
    return render_template('input.html')


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