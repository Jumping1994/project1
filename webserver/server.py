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
import datetime
import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask,url_for, request, render_template, g, redirect, Response

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


#
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
    if name not in name_ID:
      error='name does not exist';
    elif int(request.form['ID'])!=int(name_ID[name]):
      error='Invalid ID,please try again.'
    else:
      return redirect(url_for('showRestaurant'))
  return render_template('login.html',error=error)

@app.route('/showRestaurant',methods=['GET','POST'])
def showRestaurant():
    #return render_template('restaurant.html',restaurants=restaurants)
    #cid_tmp = session.get('cid') # cid with restaurnat
    #if cid_tmp is not None and session.get('logged_in') is not None:
    cursor = g.conn.execute("SELECT * from restaurant") #check restaurant name
    restaurants = cursor.fetchall()
    cursor2=g.conn.execute("SELECT name,R.restaurant_ID,table_no,size from restaurant R, tables_owns T where R.restaurant_ID=T.restaurant_ID")
    cursor3=g.conn.execute("SELECT table_no,restaurant_id from reserves")

    name={}
    error=None
    if request.method=='POST':
     restaurant_name=request.form['restaurant name']
     size=request.form['table size']

     for res2 in cursor2:
       name[res2[0]]=0
     if restaurant_name not in name:
       error="This restaurant is not available"
       return render_template("showRestaurant.html", restaurants = restaurants,error=error)
     if error==None:
       for res2 in cursor2:
         if res2[0]==restaurant_name and size<res2[3]:
           reserveation_exist=False
           for res3 in cursor3:
             if res3[0]==res2[2] and res3[1]==res2[1]:
               reserveation_exist=True;
               break;
             if reserveation_exist==False:
               g.conn.execute("INSERT into reserves (table_no,restaurant_id,time) VALUES (res2[2],res2[1],datetime.date.today())")
               return render_template("showRestaurant.html", restaurants = restaurants,error=error,table_no=res2[2])
    # error="We can't find a table available for you"	
   # return render_template("showRestaurant.html", restaurants = restaurants,error=error)
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be 
  # accessible as a variable in index.html:
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
@app.route('/another')
def another():
  return render_template("anotherfile.html")


# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
  name = request.form['name']
  g.conn.execute('INSERT INTO test VALUES (NULL, ?)', name)
  return redirect('/')

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
    app.run(host=HOST, port=PORT, debug=true, threaded=threaded)


  run()
