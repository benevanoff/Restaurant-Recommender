from mimetypes import init
from flask import render_template, request, url_for, flash, redirect, session
from webapp import app, db
import sqlalchemy
import json

from webapp import database as db_helper


@app.route("/create", methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        realname = request.form['realname']
        conn = db.connect()
        insert_Customers = 'INSERT INTO Customer (username, real_name) VALUES ("{}","{}"); '.format(username,realname)
        conn.execute(insert_Customers)
        insert_Users = 'INSERT INTO Credential (Username, Password) VALUES ("{}","{}"); '.format(username,password)
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
        pwd_query = 'SELECT Password FROM Credential WHERE Username="{}"'.format(username) # passwords should be hashed but they're not for the demo
        db_res = conn.execute(pwd_query)
        conn.close()
        pwd_res = json.dumps([dict(e) for e in db_res.fetchall()]) # format to grab by key easy
        pwd = (json.loads(pwd_res[1:len(pwd_res)-1]))["Password"] # pwd_res is a list string but only one object should be returned so we can strip off [] at beginning/end
        print(pwd)
        if pwd == pwd_input:
            session["username"] = username
            return redirect("/search")
        # else tell template renderer to add invalid login message
    return render_template('login.html')


@app.route('/')
@app.route("/search")
def search():
    """where the search bar is"""
    if not session.get("username"):
        # if not there in the session then redirect to the login page
        print("aha")
        flash("Please log in or sign up first")
        return redirect(url_for("login"))
    return render_template('search.html', username=session["username"])

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
            cafes_res = conn.execute(query, keyword='%'+request.args["cafe"]+'%')
            cafes = cafes_res.fetchall()
            res["cafe"] = json.dumps([dict(e) for e in cafes])

    conn.close()
    return res


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


@app.route("/suggest_handler")
def suggest():
    conn = db.connect()
    res = {}
    for key in request.args.keys():
        username = session["username"]
        if key == "restaurants" and request.args["restaurants"] == "true":
            query = sqlalchemy.text('SELECT DISTINCT res_id, res_name, price_level, rating, num_ratings, address FROM Restaurant r JOIN ServeRestaurant s ON r.id = s.res_id WHERE price_level IN (1, 2) AND rating > 4.5 AND num_ratings > 100 AND food_id IN (SELECT food_id FROM Favorites WHERE username="'+session["username"]+'") ORDER BY rating DESC, num_ratings DESC LIMIT 15');
            suggestions = conn.execute(query)
            res["restaurants"] = json.dumps([dict(e) for e in suggestions.fetchall()])
        if key == "bars" and request.args["bars"] == "true":
            query = sqlalchemy.text('SELECT DISTINCT bar_id, res_name, price_level, rating, num_ratings, address FROM Bar r JOIN ServeBar s ON r.id = s.bar_id WHERE price_level IN (1, 2) AND rating > 4.5 AND num_ratings > 100 AND food_id IN (SELECT food_id FROM Favorites WHERE username="'+session["username"]+'") ORDER BY rating DESC, num_ratings DESC LIMIT 15');
            suggestions = conn.execute(query)
            res ["bars"] = json.dumps([dict(e) for e in suggestions.fetchall()])
        if key == "cafes" and request.args["cafes"] == "true":
            query = sqlalchemy.text('SELECT DISTINCT cafe_id, res_name, price_level, rating, num_ratings, address FROM Cafe r JOIN ServeCafe s ON r.id = s.cafe_id WHERE price_level IN (1, 2) AND rating > 4.5 AND num_ratings > 100 AND food_id IN (SELECT food_id FROM Favorites WHERE username="'+session["username"]+'") ORDER BY rating DESC, num_ratings DESC LIMIT 15');
            suggestions = conn.execute(query)
            res ["cafes"] = json.dumps([dict(e) for e in suggestions.fetchall()])
    conn.close()
    return res

@app.route("/place_details")
def place_details():
    place_name = ""
    place_address = ""
    place_type = ""
    place_id = 0
    details = {}
    for key in request.args.keys():
        if key == "restaurant":
            place_type = "restaurant"
            place_id = request.args["restaurant"]
            details = db_helper.fetch_place_details(place_type, place_id)
        if key == "bar":
            place_type = "bar"
            place_id = request.args["bar"]
            details = db_helper.fetch_place_details(place_type, place_id)
        if key == "cafe":
            place_type = "cafe"
            place_id = request.args["cafe"]
            details = db_helper.fetch_place_details(place_type, place_id)
    place_name = details["place_name"]
    place_address = details["place_address"]
    menu = details["menu"]
    return render_template('place_details.html', p_id=place_id, p_type=place_type, name=place_name, address=place_address, menu=(json.loads(menu))) # only one place and menu will be rendered per page

@app.route("/food_history_insert", methods=('GET','POST'))
def food_history_insert():
    if "username" not in session or "place_type" not in request.form or "food_id" not in request.form or "place_id" not in request.form:
        return {"status": 500}
    if request.form["place_type"] == "bar":
        conn = db.connect()
        conn.execute(f'INSERT INTO OrderBar (username, food_id, bar_id) VALUES ("{session["username"]}", {request.form["food_id"]}, {request.form["place_id"]})')
        conn.close()
    if request.form["place_type"] == "cafe":
        conn = db.connect()
        conn.execute(f'INSERT INTO OrderCafe (username, food_id, cafe_id) VALUES ("{session["username"]}", {request.form["food_id"]}, {request.form["place_id"]})')
        conn.close()
    if request.form["place_type"] == "restaurant":
        conn = db.connect()
        conn.execute(f'INSERT INTO OrderRestaurant (username, food_id, res_id) VALUES ("{session["username"]}", {request.form["food_id"]}, {request.form["place_id"]})')
        conn.close()
        
    return {"status" : 200}

@app.route("/history")
def history():
    if "username" not in session:
        return redirect("/login")
    conn = db.connect()
    resto_res = conn.execute(f'SELECT dish_name, res_id FROM OrderRestaurant o JOIN Food f ON o.food_id=f.id WHERE username="{session["username"]}"').fetchall()
    bar_res = conn.execute(f'SELECT dish_name, bar_id FROM OrderBar o JOIN Food f ON o.food_id=f.id WHERE username="{session["username"]}"').fetchall()
    cafe_res = conn.execute(f'SELECT dish_name, cafe_id FROM OrderCafe o JOIN Food f ON o.food_id=f.id WHERE username="{session["username"]}"').fetchall()
    conn.close()
    
    hist = []
    for x in bar_res:
        hist.append({"food_id" : x[0], "place_id" : x[1]})
    for x in resto_res:
        hist.append({"food_id" : x[0], "place_id" : x[1]})
    for x in cafe_res:
        hist.append({"food_id" : x[0], "place_id" : x[1]})
        
    return render_template('history.html', histories=hist)

@app.route("/preferences")
def preferences():
    if "username" not in session:
        return redirect('/login')

    return render_template('preferences.html')

@app.route("/add_food")
def add_food():
    if "username" not in session:
        return redirect('/login')

    return render_template('add_food.html')

@app.route("/logout")
def logout():
    if "username" in session:
        session.pop("username")
    return redirect("/login")

@app.route("/food_search_handler")
def food_search_handler():
    if "keyword" not in request.args:
        return {"status": 500}
    conn = db.connect()
    query = sqlalchemy.text('SELECT id, dish_name FROM Food WHERE dish_name LIKE :keyword LIMIT 10')
    query_res = conn.execute(query, keyword='%'+request.args["keyword"]+'%').fetchall()
    conn.close()
    return json.dumps([dict(e) for e in query_res])

@app.route("/insert_favorite", methods=('GET','POST'))
def insert_favorites():
    if "username" not in session or "food_id" not in request.form:
        return {"status": 500}
    db.connect().execute(f'INSERT INTO Favorites (username, food_id) VALUES ("{session["username"]}", "{request.form["food_id"]}")')
    return {"status": 200}



# @app.route("/query2", methods = ('GET','POST'))
# def query2():
#     if request.method == 'POST':
#         conn = db.connect()
#         fields = "username, COUNT(*) AS num_order_brave "
#         table1 = "Customer C NATURAL JOIN OrderRestaurant O "
#         table2 = "Customer C NATURAL JOIN OrderCafe O "
#         subquery = "SELECT food_id FROM Customer C1 NATURAL JOIN Favorites WHERE C.username != C1.username"
#         query_search = (f"(SELECT {fields}"
#                         f"FROM {table1}"
#                         f"WHERE O.food_id IN ({subquery}) "
#                         "GROUP BY username) UNION "
#                         f"(SELECT {fields}"
#                         f"FROM {table2}"
#                         f"WHERE O.food_id IN ({subquery}) "
#                         "GROUP BY username) "
#                         "ORDER BY num_order_brave DESC "
#                         "LIMIT 15;")
#         results = conn.execute(query_search).fetchall()
#         return render_template('archived/query2.html', results=results)
#     return render_template('archived/query2.html')


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
            return render_template('archived/search_validation.html', all_tables=table_info)

        results = db_helper.search_table_tuple(table, column, tuple_key)
        if len(results) == 0:
            flash("No records found")
        return render_template('archived/search_validation.html', all_tables=table_info, results=results)

    return render_template('archived/search_validation.html', all_tables=table_info)
