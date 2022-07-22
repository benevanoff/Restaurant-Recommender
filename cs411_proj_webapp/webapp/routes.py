from mimetypes import init
from flask import render_template, request, url_for, flash, redirect
from webapp import app, db
import sqlalchemy
import json

@app.route('/')
@app.route('/index')
def index():
    """Main page"""
    return render_template('index.html', title='Midterm DEMO')


@app.route("/create", methods=('GET', 'POST'))
def create():
    conn = db.connect()

    username = ""
    password = ""
    realname = ""
     
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        realname = request.form['realname']
      
        #if not username:
        #    flash('Username is required!')
        #elif not password:
        #    flash('Password is required!')
       # else:
        #    return redirect(url_for('index'))

    test_query = 'DELETE FROM cs411_proj_data.Users'
    conn.execute(test_query)
    query = 'INSERT INTO cs411_proj_data.Users (Username, Password, Realname) VALUES ("{}","{}","{}"); '.format(username, password, realname)
    conn.execute(query)
    conn.close()
    return render_template('create.html')


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

@app.route("/update")
def update():
    return render_template('update.html')


@app.route("/delete")
def delete():
    return render_template('delete.html')


@app.route("/query1")
def query1():
    return render_template('query1.html')


@app.route("/query2")
def query2():
    return render_template('query2.html')

# # used to allow user logging out
# # adapt the html to show this
# @app.route("/logout")
# def logout():
#     logout_user()
#     return redirect(url_for("index"))
#
# @app.route("/register", methods=['GET', 'POST'])
# def register():
#     if current_user.is_authenticated:
#         return redirect(url_for("index"))
#
#     form = RegistrationForm()
#     if form.validate_on_submit():
#         user = User(username=form.username.data, email=form.email.data)
#         user.set_password(form.password.data)
#         db.session.add(user)
#         db.session.commit()
#         flash("Congratulations, you are now a registered user!")
#         return redirect(url_for("login"))
#     return render_template("register.html", title="Register", form=form)
