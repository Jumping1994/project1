#!/usr/bin/env python2.7

"""
Columbia W4111 Intro to databases
Example webserver
To run locally
    python server.py
Go to http://localhost:8111 in your browser
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""
from random import randint
import datetime
import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask,url_for,session, request, render_template, g, redirect, Response

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

# The following uses the sqlite3 database test.db -- you can use this for debugging purposes
# However for the project you will need to connect to your Part 2 database in order to use the
# data
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@w4111db.eastus.cloudapp.azure.com/username
#
# For example, if you had username ewu2493, password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://ewu2493:foobar@w4111db.eastus.cloudapp.azure.com/ewu2493"
#
DATABASEURI = "postgresql://xj2178:LXLYRY@w4111db.eastus.cloudapp.azure.com/xj2178"


#
# This line creates a database engine that knows how to connect to the URI above
#
engine = create_engine(DATABASEURI)


#
# START SQLITE SETUP CODE
#
# after these statements run, you should see a file test.db in your webserver/ directory
# this is a sqlite database that you can query like psql typing in the shell command line:
# 
#     sqlite3 test.db
#
# The following sqlite3 commands may be useful:
# 
#     .tables               -- will list the tables in the database
#     .schema <tablename>   -- print CREATE TABLE statement for table
# 
# The setup code should be deleted once you switch to using the Part 2 postgresql database
#
#engine.execute("""DROP TABLE IF EXISTS test;""")
#engine.execute("""CREATE TABLE IF NOT EXISTS test (
 # id serial,
 # name text
#);""")
#engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")
#
# END SQLITE SETUP CODE
#



@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request
  The variable g is globally accessible
  """
  try:
    g.conn = engine.connect()
  except:
    print "uh oh, problem connecting to database"
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to e.g., localhost:8111/foobar/ with POST or GET then you could use
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
  """
  request is a special object that Flask provides to access web request information:
  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments e.g., {a:1, b:2} for http://localhost?a=1&b=2
  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """

  # DEBUG: this is debugging code to see what request looks
  return render_template('homepage.html')


  #
  # example of a database query
  #
@app.route('/login',methods=['GET','POST'])
def login():
  cursor = g.conn.execute("SELECT name,customer_id FROM customer")
  name_ID={}
  for result in cursor:
    name_ID[result[0]]=result[1] # can also be accessed using result[0]
  cursor.close()  
  error=None
  if request.method=='POST':
    name=request.form['name']
    ID=request.form['ID']
    if name not in name_ID:
      error='name does not exist';
    elif int(ID)!=int(name_ID[name]):
      error='Invalid ID,please try again.'
    else:
      session['userID']=ID
      return redirect(url_for('showRestaurant'))
  return render_template('login.html',error=error)
@app.route('/newuser', methods=['POST','GET'])
def newuser():
        c_id=0
        newuser=None
	if request.method == 'POST':
		customername = request.form['customer_name']
		customerage = request.form['customer_age']
		customercontact = request.form['contact_number']
		customeremail = request.form['customer_email']
                cursor=g.conn.execute("select count(*) from customer")		
                for res in cursor:
                    c_id=int(res[0])+1
		tmp = (c_id,customerage,customeremail,customername,customercontact)
		g.conn.execute("insert into customer (customer_id,age,email,name,phone_number) values(%s,%s,%s,%s,%s)",tmp)
                newuser="created"
		return render_template("newuser.html",Cid=c_id,newuser=newuser)
	return render_template("newuser.html",Cid=c_id,newuser=newuser)

@app.route('/showRestaurant',methods=['GET','POST'])
def showRestaurant():
    #return render_template('restaurant.html',restaurants=restaurants)
    #cid_tmp = session.get('cid') # cid with restaurnat
    #if cid_tmp is not None and session.get('logged_in') is not None:
    cursor = g.conn.execute("SELECT * from restaurant") #check restaurant name
    restaurants = cursor.fetchall()
    cursor2=g.conn.execute("SELECT name,R.restaurant_ID,table_no,size from restaurant R, tables_owns T where R.restaurant_ID=T.restaurant_ID")
    cursor3=g.conn.execute("SELECT table_no,restaurant_id from reserves")
    c2=cursor2.fetchall()
    c3=cursor3.fetchall()
    name={}
    error=None
    if request.method=='POST':
      restaurant_name=request.form['restaurant name']
      size=request.form['table size']

      for res2 in c2:
        name[res2[0]]=0
      if restaurant_name not in name:
        error="This restaurant is not available"
        return render_template("showRestaurant.html", restaurants = restaurants,error=error)
      for res2 in c2:
        if res2[0]==restaurant_name and int(size)<res2[3]:
          reserveation_exist=False
          for res3 in c3:
            if res3[0]==res2[2] and res3[1]==res2[1]:
              reserveation_exist=True
              break
          if reserveation_exist==False:
            ID=session.get('userID')
            temp=(ID,res2[2],res2[1],datetime.date.today())
            session['restaurantID']=res2[1]
            g.conn.execute("INSERT into reserves (customer_id,table_no,restaurant_id,time) VALUES (%s,%s,%s,%s)",temp)
            return redirect(url_for('placeorder'))
      error="We can't find a table available for you at this time"	
    return render_template("showRestaurant.html", restaurants = restaurants,error=error)

@app.route('/placeorder', methods=['GET', 'POST'])
def placeorder():
	cursor = g.conn.execute("select name,description,prices from dish")
	dishes = cursor.fetchall()
	dish={}
	error=None
	for res in dishes:
		dish[res[0]]=res[2]
	cursor.close()
	price = 0
	dishnames={}
	finals=[]
       # render_template('placeorder.html', error=error, dishes=dishes)
	if request.method == 'POST':
		dishnames[request.form['dish_name1']]= request.form['quantity1']
		dishnames[request.form['dish_name2']]= request.form['quantity2']
		dishnames[request.form['dish_name3']]= request.form['quantity3']
		for dishname in dishnames:
			if dishname not in dish:
				error = 'Invalid dish';
				return render_template('placeorder.html', error=error, dishes=dishes)
			else:
				#finals.append(dishnames[dishname])
				price += float(dishnames[dishname]) * float(dish[dishname])
                session['price']=price     
		globalcustomerid=session.get('userID')
		globalresid = session.get('restaurantID')
                order_no=int(globalresid*10000)+randint(0,9)*1000+randint(0,9)*100+randint(0,9)*10+randint(0,9)
                session['order_no']=order_no
		tmp = (order_no,globalcustomerid,globalresid)
		g.conn.execute("INSERT into order_places (order_no, customer_id,restaurant_id) values (%s,%s,%s)",tmp)
		for names in dishnames:
			tmp1 = (order_no,names)
			g.conn.execute("INSERT into contains (order_no,name) values (%s,%s)",tmp1)
		return redirect(url_for('payment'))
        return render_template('placeorder.html', error=error, dishes=dishes)

@app.route('/payment', methods=['POST','GET'])
def payment():
	bill=[]
	error = None
	customerid = session.get('userID')
	resid = session.get('restaurantID')
	orderno = session.get('order_no')
	price=session.get('price')
	bill.append(customerid)
	bill.append(resid)
	bill.append(orderno)
	bill.append(price)
	#cursor = g.conn.execute("select work_id from waiter_employs where restaurant_id = %s",resid)
	#wid = cursor.fetchall()
        wid=10001
	bill_no = randint(1,9)*10000+randint(0,9)*1000+randint(0,9)*100+randint(0,9)*10+randint(0,9)
	if request.method == 'POST':
		tip_amount = request.form['amount']
		tmp1 = (datetime.date.today(),float(tip_amount),customerid,wid)
		g.conn.execute("insert into tips (time,amount,customer_id,work_id) values(%s,%s,%s,%s)",tmp1)
		tmp2 = (customerid,resid,float(tip_amount),bill_no)
		g.conn.execute("insert into pays (customer_id,restaurant_id,amount,bill_no) values (%s,%s,%s,%s)",tmp2)
                return redirect(url_for('thankyou'))
	return render_template("payment.html", bill = bill,error=error)
@app.route('/thankyou')
def thankyou():
    return render_template("thankyou.html")
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be 
  # accessible as a variable in index.html:i
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #     
  #     # creates a <div> tag for each element in data
  #     # will print: 
  #     #

  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}

  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
#
# This is an example of a different path.  You can see it at
# 
#     localhost:8111/another
#
# notice that the functio name is another() rather than index()
# the functions for each app.route needs to have different names
#

# Example of adding new data to the database
if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using
        python server.py
    Show the help text using
        python server.py --help
    """

    HOST, PORT = host, port
    print "running on %s:%d" % (HOST, PORT)
    app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
    app.run(host=HOST, port=PORT, debug=true, threaded=threaded)


  run()
