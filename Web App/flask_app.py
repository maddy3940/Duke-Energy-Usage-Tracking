from flask import Flask, redirect, render_template, request, url_for
from datetime import datetime, timedelta
import pytz


app = Flask(__name__)
app.config["DEBUG"] = True

@app.route("/")
def main_page():
    return render_template("main_page.html")

@app.route('/result',methods = ['POST', 'GET'])
def result():
    if request.method == 'POST':
        result = request.form
        # x= cal_time(result)
        result= {'Result':cal_time(result['Hours Worked'])}
        return render_template("results.html",result = result)


def alarm(t):
    tz_NY = pytz.timezone('America/New_York')
    datetime_NY = datetime.now(tz_NY)
    result_2 = datetime_NY + timedelta(hours=t)
    return result_2.strftime("%d-%m-%Y, %H:%M %p %Z")

def cal_time(worked_hrs,total_hrs=20):
  # Format 1 - HH MM
  # Format 2 - HH.HH
  #print(worked_hrs,len(worked_hrs))

  if len(worked_hrs)!=11:
    return ("a Enter valid worked hours. Example- 19.20/20 or 19 12/20")
  else:
    f0=worked_hrs.split("/")
    total_hrs=float(f0[1])
    f1= f0[0].split(" ")
    f2= f0[0].split(".")

    if len(f1)!=2 and len(f2)!=2:
      return ("b Enter valid worked hours. Example- 19.20/20 or 19 12/20")

    elif len(f1)==2:
      h=float(f1[0])
      m=float(f1[1])
      m=m/60
      t=h+m
      t=total_hrs-t

    elif len(f2)==2:
      #print("HH.HH")
      t=total_hrs-float(f0[0])

    else:
      return ("c Enter valid worked hours. Example- 19.20/20 or 19 12/20")
    x = alarm(t)
    y ='Set an alarm for ' + str(x) + ' you have to clock in ' + str(round(t,2)) + ' hours more if you want to work for ' + str(total_hrs) + ' this week'
    return y