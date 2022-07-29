from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
import os
from flask_sqlalchemy import SQLAlchemy
from flask_paginate import Pagination, get_page_parameter
from threading import Thread
import requests
import time
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import smtplib
import yagmail #plcirqnbqfzmsvlg
from redis import Redis
from rq import Queue

BTCValue=0
email_set=set()
redis_conn = Redis(host='localhost', port=6379, db=0)
q = Queue('my_queue', connection=redis_conn)


def getNumberOfUsers():
    users = User.query.all()
    return len(users)

def getAllUsers():
    users = User.query.all()
    return users
    
def logInfo(l):
    db.session.add(l)
    db.session.commit()
    
def readAndgetMaxBTC():
    global BTCValue
    page = requests.get('https://api.coingecko.com/api/v3/coins/markets?vs_currency=USD&order=market_cap_desc&per_page=100&page=1&sparkline=false')
    jsonPage = page.json()
    for coin in jsonPage:
        if(coin["id"]=='bitcoin'):
            BTCValue = coin['current_price']
        else:
            break
    users = User.query.all()
    for user in users:
        if user.price<=BTCValue:
            job = q.enqueue(sendMail(user.email))
def sendMail(email):
    print('Sending email')
    user = 'rrcuber@gmail.com'
    app_pwd = 'plcirqnbqfzmsvlg'
    to = email
    subject = 'Bitcoin price update'
    content = ['Bitcoin price updated to '+str(BTCValue)]
    with yagmail.SMTP(user, app_pwd) as yag:
        yag.send(to, subject, content)
        print('Sent email successfully')    
    time.sleep(1000)
app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///krypto.db'
db = SQLAlchemy(app)

class Log(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20),nullable=False, unique=False)
    price = db.Column(db.Integer,nullable=False, unique=False)
    event = db.Column(db.String(10),nullable=False, unique=False)
    def __repr__(self):
        return f"Name : {self.username}, event: {self.event}"

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=False, nullable=False)
    price = db.Column(db.Integer, unique=False, nullable=False)
    email = db.Column(db.String(100),unique=True,nullable=False)
    def __repr__(self):
        return f"Name : {self.username}, Price: {self.price}, Email: {self.email}"
    @property
    def serialize(self):
        return{
            'id' : self.id,
            'username' : self.username,
            'price' : self.price,
            'email' : self.email
        }

@app.route('/home')
def home():
    return "Welcome home"

@app.route('/alerts/create',methods=['POST'])
def create_alert():
    content=request.json
    uname = content['username']
    p = content['price']
    e = content['email']
    if e in email_set:
        email_set.remove(e)
    print(uname, p, e)
    if (User.query.filter(User.username == uname)).count()>0:
        return jsonify({
        "Error":"User already exists"
    })
    u = User(username=uname, price=p, email=e)
    db.session.add(u)
    db.session.commit()
    length = getNumberOfUsers()
    l = Log(username=uname, price=p, event='create')
    logInfo(l)
    return jsonify(content)

@app.route('/getAllUsers', methods=['GET'])
def getUsers():
    args = request.args
    key = args.get('key')
    if key != SECRET_KEY:
        return jsonify({
            "Error":"Invalid token received"
        })
    page = int(request.args.get('page'))
    allUsers = getAllUsers()
    jsonUserList=[]
    for user in allUsers:
        jsonUserList.append(user.__dict__)
    return {
        'users' : [u.username for u in User.query.paginate(page=page,per_page=1).items],
        'prices' : [u.price for u in User.query.paginate(page=page,per_page=1).items],
        'email' : [u.email for u in User.query.paginate(page=page,per_page=1).items]
        }
    
@app.route('/getLogs',methods=['GET'])
def getLogs():
    args = request.args
    key = args.get('key')
    if key != SECRET_KEY:
        return jsonify({
            "Error":"Invalid token received"
        })
    page = int(request.args.get('page'))
    allLogs = Log.query.all()
    jsonAllLogsList = []
    for log in allLogs:
        jsonAllLogsList.append(log.__dict__)
    return{
        'username' : [u.username for u in Log.query.paginate(page=page,per_page=5).items],
        'event' : [u.event for u in Log.query.paginate(page=page,per_page=5).items]
    }    
@app.route('/getLogs',methods=['GET'])
def getlogs():
    print(Log.query.all())
    return "";
@app.route('/alerts/delete',methods=['POST'])
def delete_alert():
    content = request.json
    uname = content['username']
    User.query.filter(User.username == uname).delete()
    db.session.commit()
    l = Log(username=uname,price=0,event='delete')
    logInfo(l)
    return jsonify({
        "Username" : uname
    })
    
if __name__ == '__main__':
    db.create_all()
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=readAndgetMaxBTC, trigger="interval", seconds=10)
    scheduler.start()
    # Shut down the scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())
    SECRET_KEY = 'e07c9cdc-e7be-4e7e-8ba7-9c787e202292'
    app.run(debug=True)