from mimetypes import init
from flask import render_template, request, url_for, flash, redirect, session
from webapp import app, db
import sqlalchemy
import json

from webapp import database as db_helper

@app.route('/')
@app.route('/index')
def index():
    """Main page"""
    return render_template('index.html', title='Midterm DEMO')


@app.route("/create", methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        realname = request.form['realname']
        conn = db.connect()
        insert_Customers = 'INSERT INTO Customer (username, real_name) VALUES ("{}","{}"); '.format(username,realname)
        conn.execute(insert_Customers)
        insert_Users = 'INSERT INTO Users (Username, Password) VALUES ("{}","{}"); '.format(username,password)
        conn.execute(insert_Users)
        conn.close()
        
    return render_template('create.html')

@app.route("/login", methods=('GET', 'POST'))
def login():
    for key in session:
        if key == "username":
            return redirect("/search") # redirect to main page if already logged in
    if request.method == 'POST':
        username = request.form['username']
        pwd_input = request.form['password']
        conn = db.connect()
        pwd_query = 'SELECT Password FROM Users WHERE Username="{}"'.format(username) # passwords should be hashed but they're not for the demo
        db_res = conn.execute(pwd_query)
        conn.close()
        pwd_res = json.dumps([dict(e) for e in db_res.fetchall()]) # format to grab by key easy
        pwd = (json.loads(pwd_res[1:len(pwd_res)-1]))["Password"] # pwd_res is a list but only one object should be returned so we can strip off [] at beginning/end
        print(pwd)
        if pwd == pwd_input:
            session["username"] = username
            return redirect("/search")
        # else tell template renderer to add invalid login message
    return render_template('login.html')


@app.route("/search")
def search():
    """where the search bar is"""
    return render_template('search.html')

@app.route("/search_handler")
def search_handler():
    """grab places with names LIKE keyword"""
    res = {}
    conn = db.connect()
    for key in request.args.keys():
        if key == "bar":
            query = sqlalchemy.text('SELECT * FROM Bar WHERE res_name LIKE :keyword LIMIT 10')
            bars_res = conn.execute(query, keyword='%'+request.args["bar"]+'%')
            bars = bars_res.fetchall()
            res["bars"] = json.dumps([dict(e) for e in bars])
        if key == "restaurant":
            query = sqlalchemy.text('SELECT * FROM Restaurant WHERE res_name LIKE :keyword LIMIT 10')
            restos_res = conn.execute(query, keyword='%'+request.args["restaurant"]+'%')
            restaurants = restos_res.fetchall()
            res["restaurant"] = json.dumps([dict(e) for e in restaurants])
        if key == "cafe":
            query = sqlalchemy.text('SELECT * FROM Cafe WHERE res_name LIKE :keyword LIMIT 10')
            cafes_res = conn.execute(query, keyword='%'+request.args["restaurant"]+'%')
            cafes = cafes_res.fetchall()
            res["cafe"] = json.dumps([dict(e) for e in cafes])

    conn.close()
    return res


@app.route("/search_validation", methods=('GET', 'post'))
def search_validation():
    """
    This search bar can be used to search for a certain records in a certain relation
    this can be used to show the results of our operation
    e.g.: first search to show the existence of a user "john", then perform delete, then search again
    to show no such "john exists anymore".
    """
    table_info = db_helper.get_db_info()
    if request.method == "POST":
        table = request.form['table']
        column = request.form['column']
        tuple_key = request.form['tupleKey']

        if table not in table_info or column not in table_info[table]:
            flash("Use a valid table-column pair")
            return render_template('search_validation.html', all_tables=table_info)

        results = db_helper.search_table_tuple(table, column, tuple_key)
        if len(results) == 0:
            flash("No records found")
        return render_template('search_validation.html', all_tables=table_info, results=results)

    return render_template('search_validation.html', all_tables=table_info)


@app.route("/update", methods=('GET', 'POST'))
def update():
    if request.method == 'POST':
        username = request.form['username']
        old_password = request.form['oldPassword']
        new_password = request.form['newPassword']

        if "" in [username, old_password, new_password]:
            flash("Filling out all fields!")

        update_stat = db_helper.update_password(username, old_password, new_password)
        if update_stat == 0:
            # successful update
            return redirect(url_for('index'))

        if update_stat == 1:
            flash("User not found")
        else:
            flash("Incorrect password")

    return render_template('update.html')


@app.route("/delete", methods=('GET', 'POST'))
def delete():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if "" in [username, password]:
            flash("Filling out all fields!")

        delete_stat = db_helper.delete_user(username, password)
        if delete_stat == 0:
            # successful delete
            return redirect(url_for("index"))

        if delete_stat == 1:
            flash("User not found")
        else:
            flash("Incorrect password")
        return render_template('delete.html')

    return render_template('delete.html')


@app.route("/query1")
def query1():
    return render_template('query1.html')


@app.route("/suggest")
def suggest():
    conn = db.connect()
    res = {}
    for key in request.args.keys():
        username = ""
        print(request.args["bars"])
        if key == "username": # username needs to be first parameter so it is recognized before making queries
            username = request.args["username"]
        if key == "restaurants" and request.args["restaurants"] == "true":
            query = sqlalchemy.text('SELECT DISTINCT res_name, price_level, rating, num_ratings, address FROM Restaurant r JOIN ServeRestaurant s ON r.id = s.res_id WHERE price_level IN (1, 2) AND rating > 4.5 AND num_ratings > 100 AND food_id IN (SELECT food_id FROM Favorites WHERE username="'+request.args["username"]+'") ORDER BY rating DESC, num_ratings DESC LIMIT 15');
            suggestions = conn.execute(query)
            res["restaurants"] = json.dumps([dict(e) for e in suggestions.fetchall()])
        if key == "bars" and request.args["bars"] == "true":
            query = sqlalchemy.text('SELECT DISTINCT res_name, price_level, rating, num_ratings, address FROM Bar r JOIN ServeBar s ON r.id = s.bar_id WHERE price_level IN (1, 2) AND rating > 4.5 AND num_ratings > 100 AND food_id IN (SELECT food_id FROM Favorites WHERE username="'+request.args["username"]+'") ORDER BY rating DESC, num_ratings DESC LIMIT 15');
            suggestions = conn.execute(query)
            res ["bars"] = json.dumps([dict(e) for e in suggestions.fetchall()])
        if key == "cafes" and request.args["cafes"] == "true":
            query = sqlalchemy.text('SELECT DISTINCT res_name, price_level, rating, num_ratings, address FROM Cafe r JOIN ServeCafe s ON r.id = s.cafe_id WHERE price_level IN (1, 2) AND rating > 4.5 AND num_ratings > 100 AND food_id IN (SELECT food_id FROM Favorites WHERE username="'+request.args["username"]+'") ORDER BY rating DESC, num_ratings DESC LIMIT 15');
            suggestions = conn.execute(query)
            res ["cafes"] = json.dumps([dict(e) for e in suggestions.fetchall()])
    conn.close()
    return res



