from flask import render_template, request, flash, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from app import app, db, bcrypt
from app.forms import RegistrationForm, LoginForm, TransferForm
from app.models import Users,Transfer
from flask_migrate import Migrate
from datetime import datetime

migrate = Migrate(app, db)


@app.route("/", methods=["GET", "POST"])
def home():
    return render_template("home.html")


@app.route("/user_menu",methods=["GET","POST"])
def user_menu():
    if request.method == "GET":
        return render_template("blogs/user_menu.html")
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            user = Users.query.filter_by(email=form.email.data).first()
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                session['username'] = user.username
                flash('You are now logged in!', 'success')
                return redirect(url_for('user_menu'))
            else:
                flash("Invalid email or password", "danger")
                return redirect(url_for('login'))
    return render_template('auth/login.html', form=form)




@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            user = Users(
                username=form.username.data,
                phone=form.phone.data,
                email=form.email.data,
                balance=form.balance.data,
                password=hashed_password
            )
            db.session.add(user)
            db.session.commit()
            flash('You are now registered!', 'success')
            return redirect(url_for('login'))
    return render_template('auth/register.html', form=form)


@app.route("/show_balance",methods=['GET', 'POST'])
def show_balance():
    if request.method == 'POST':
        return redirect(url_for('user_menu'))
    username=session['username'];
    user=Users.query.filter_by(username=username).first()
    return render_template('blogs/balance.html', user=user)


@app.route("/show_transfer", methods=['GET', 'POST'])
def show_transfer():
    transfer = TransferForm()
    if request.method == 'GET':
        return render_template('blogs/transfer_money.html', transfer=transfer)
    else:
        if transfer.validate_on_submit():
            user_from = Users.query.filter_by(username=session['username']).first()
            user_to = Users.query.filter_by(username=transfer.username.data).first()

            if user_from and user_to and user_from != user_to and transfer.balance.data > 0:
                if user_from.balance >= transfer.balance.data:
                    user_from.balance -= transfer.balance.data
                    user_to.balance += transfer.balance.data

                    transaction = Transfer(
                        from_username=user_from.username,
                        to_username=user_to.username,
                        balance=transfer.balance.data
                    )

                    db.session.add(transaction)
                    db.session.commit()
                    return redirect(url_for('user_menu'))
                else:
                    flash('Sizda yetarli mablag\' mavjud emas', 'danger')
            else:
                flash('To\'lov amalga oshirib bo\'lmadi. Tekshiring va qayta urinib ko\'ring.', 'danger')

        return render_template('blogs/transfer_money.html', transfer=transfer)












@app.route("/show_history")
def show_history():
    pass

@app.route("/log_out")
def log_out():
    session.pop('username')
    return redirect(url_for('home'))

@app.route("/show_add",methods=['GET', 'POST'])
def show_add():
    user = Users.query.filter_by(username=session['username']).first()
    if request.method == 'GET':
        return render_template("blogs/add_balance.html")
    elif request.method == 'POST':
        num = request.form.get('num')
        num = int(num)
        if num < 0:
            flash('Please enter a positive number', 'danger')
        elif num:
            user.balance += num
            db.session.commit()
            flash('Balance successfully added!', 'success')
        return redirect(url_for('user_menu'))

@app.route("/user_delete")
def user_delete():
    user = Users.query.filter_by(username=session['username']).first()
    db.session.delete(user)
    db.session.commit()
    return redirect(url_for('home'))


