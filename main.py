# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START gae_python38_render_template]
# [START gae_python3_render_template]

import datetime

from flask import Flask, render_template, request, flash, session
import boto3
app = Flask(__name__)
app.secret_key = "passkeysetforflash"





#Home page functions
@app.route('/')
def root():
    # For the sake of example, use static information to inflate the template.
    # This will be replaced with real information in later steps.
    return render_template('index.html', qitems=session['items'],subs=getsubs())
#________________________________________________login functions
@app.route('/login', methods=('GET', 'POST'))
def loginpage():
    return render_template('loginpage.html')

@app.route("/logout")
def logout():
    session['logged_in'] = False
    session['user_name'] = ""
    session['email'] = ""
    session['items'] = []
    return root()

@app.route("/checkLogin", methods = ['POST'])
def checkLogin():
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('login')
    email = request.form['email']
    password = request.form['Password']
    response = table.get_item(Key={'email': email})
    if 'Item' in response:
        if password == response['Item']['password']:
            session['logged_in'] = True
            session['user_name'] = response['Item']['user_name']
            session['email'] = response['Item']['email']

            return root()
        else:
            flash('Incorrect Password')
            return render_template("loginpage.html")
    else:
        flash('Incorrect Email')
        return render_template("loginpage.html")

#______________________________________________________________________register functions
@app.route('/register', methods=('GET', 'POST'))
def registerpage():
    return render_template('registerpage.html')

@app.route("/checkRegister", methods = ['POST'])
def checkRegister():
    dynamodb = boto3.client('dynamodb')
    table = dynamodb.Table('login')
    email = request.form['email']
    password = request.form['Password']
    Username = request.form['Username']

    response = table.get_item(Key={'email': email})
    if 'Item' in response:
        flash('The email already exists')
        return render_template("registerpage.html")
    else:
        item = {
            'password': password,
            'email': email,
            'user_name': Username
        }
        table.put_item(Item=item)
        return loginpage()
#_________________________________________________
@app.route("/query", methods = ['POST'])
def query():
    items = []
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('music')
    Title = request.form['Title']
    Yearof = request.form['Year']
    Artist = request.form['Artist']
    if(Artist == "" and Title == "" and Yearof == ""):
        flash('You must fill in at least one criteria')
        return (render_template("index.html", qitems=[], subs=getsubs()))
    if(Title != ""):
        query_params = {
            'KeyConditionExpression': 'Title = :value1',
            'ExpressionAttributeValues': {
                ':value1': Title
            }
        }
        response = table.query(**query_params)
        for obj in response["Items"]:
            items.append(obj)
    if (Artist != ""):
        filter_expression = 'Artist = :Artist'
        expression_attribute_values = {
            ':Artist': Artist
        }
        response = table.scan(
                    FilterExpression=filter_expression,
                    ExpressionAttributeValues=expression_attribute_values)
        for obj in response["Items"]:
            if obj not in items:
                items.append(obj)
    if (Yearof != ""):
        reserved_attribute_name = 'Year'
        expression_attribute_name = '#y'
        filter_expression = f'{expression_attribute_name} = :Year'
        expression_attribute_values = {
            ':Year': Yearof
        }
        expression_attribute_names = {
            expression_attribute_name: reserved_attribute_name
        }
        response = table.scan(
                    FilterExpression=filter_expression,
                    ExpressionAttributeValues=expression_attribute_values,
                    ExpressionAttributeNames=expression_attribute_names
        )
        for obj in response["Items"]:
            if obj not in items:
                items.append(obj)
    if(len(items) == 0):
        flash('No items found')
    for obj in items:
        obj["Img_url"] = "https://songimagemymusicsite.s3.amazonaws.com/" + obj["Title"].replace(" ", "_") +"_Image.jpg"
        obj["Img_url"] =  obj["Img_url"].replace("#", "%23")
    session['items'] = items
    return (render_template("index.html",qitems = items,subs=getsubs()))


@app.route("/Subscribe", methods = ['POST'])
def Subscribe():
    vals = dict(request.form)
    convtwolist = list(vals.keys())[0]
    finaltitle = str(convtwolist)
    email = session['email']
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Subscriptions')
    response = table.get_item(Key={'email': email, 'Title' : finaltitle})
    if 'Item' in response:
        flash("you are already subscribed!")
        return (render_template("index.html", qitems=session['items'],subs=getsubs()))
    else:
        item = {
            'email': email,
            'Title': finaltitle
        }
        table.put_item(Item=item)
    return (render_template("index.html", qitems=session['items'],subs=getsubs()))

def getsubs():
    if not session['logged_in']:
        return []
    rawsubs = []
    subs = []
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Subscriptions')
    query_params = {
        'KeyConditionExpression': 'email = :value1',
        'ExpressionAttributeValues': {
            ':value1': session['email']
        }
    }
    response = table.query(**query_params)
    for obj in response["Items"]:
        rawsubs.append(obj)
    table = dynamodb.Table('music')
    for obj in rawsubs:
        query_params = {
            'KeyConditionExpression': 'Title = :value1',
            'ExpressionAttributeValues': {
                ':value1': obj['Title']
            }
        }
        response = table.query(**query_params)
        for obj in response["Items"]:
            subs.append(obj)
    for obj in subs:
        obj["Img_url"] = "https://songimagemymusicsite.s3.amazonaws.com/" + obj["Title"].replace(" ", "_") +"_Image.jpg"
        obj["Img_url"] =  obj["Img_url"].replace("#", "%23")
    return subs

@app.route("/UnSubscribe", methods = ['POST'])
def UnSubscribe():
    vals = dict(request.form)
    convtwolist = list(vals.keys())[0]
    finaltitle = str(convtwolist)
    email = session['email']
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('Subscriptions')
    table.delete_item(Key={'email': email, 'Title' : finaltitle})
    return (render_template("index.html", qitems=session['items'],subs=getsubs()))


if __name__ == '__main__':

    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    # Flask's development server will automatically serve static files in
    # the "static" directory. See:
    # http://flask.pocoo.org/docs/1.0/quickstart/#static-files. Once deployed,
    # App Engine itself will serve those files as configured in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [END gae_python3_render_template]
# [END gae_python38_render_template]
