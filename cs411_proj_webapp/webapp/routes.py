from flask import render_template, request, url_for, flash, redirect
from webapp import app


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

        if not username:
            flash('Username is required!')
        elif not password:
            flash('Password is required!')
        else:
            return redirect(url_for('index'))
    return render_template('create.html')


@app.route("/search")
def search():
    """where the search bar is"""
    return render_template('search.html')


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
