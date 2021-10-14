from market import app
from flask import render_template, redirect, url_for, flash, request
from market.models import Item, User
from market.forms import RegisterForm, LoginForm, Purchase_Item_Form, Sell_Item_Form
from market import db
from flask_login import login_user, logout_user, login_required, current_user

@app.route('/')
@app.route('/home')
def home_page():
	return render_template("home.html")

@app.route('/market', methods=['GET', 'POST'])
@login_required
def market_page():
	purchase_form = Purchase_Item_Form()
	sell_form = Sell_Item_Form()
	if request.method == 'POST':
		purchased_item = request.form.get('purchased_item')
		p_item_object = Item.query.filter_by(name=purchased_item).first()
		if p_item_object:
				if (current_user.can_purchase(p_item_object)):
					p_item_object.owner = current_user.id
					current_user.budget = current_user.budget - p_item_object.price
					db.session.commit()
					flash(f"You have purchased {p_item_object.name} for {p_item_object.price}", category="success")
				else:
					flash(f"You don't have enough funds to purchase {p_item_object.name}", category="danger")
				purchased_item = request.form.get('purchased_item')
		sell_item = request.form.get('sell_item')
		s_item_object = Item.query.filter_by(name=sell_item).first()
		if s_item_object:
				current_user.budget += s_item_object.price
				s_item_object.owner = None
				db.session.commit()
				flash(f"You have sold {s_item_object.name} for {s_item_object.price}", category="success")
		return redirect(url_for('market_page'))
		
	if request.method == 'GET':
		items = Item.query.filter_by(owner=None)
		owned_items = Item.query.filter_by(owner=current_user.id)
		return render_template("market.html", items=items, purchase_form=purchase_form, sell_form=sell_form, owned_items=owned_items)

@app.route('/register', methods=['GET', 'POST'])
def register_page():
	form = RegisterForm()
	if form.validate_on_submit():
		user_to_create = User(username=form.username.data,
							email_address=form.email_address.data,
							password=form.password1.data)
		db.session.add(user_to_create)
		db.session.commit()
		login_user(user_to_create)
		flash(f"Account created successfuly, you are logged in as: {user_to_create.username}", category='success')
		return redirect(url_for('market_page'))
	if form.errors != {}:
		for err_msg in form.errors.values():
			flash(f'There was an error creating a user: {err_msg}', category='danger')
	return render_template("register.html", form=form)

@app.route('/login', methods=['GET','POST'])
def login_page():
	form = LoginForm()
	if form.validate_on_submit():
		attempted_user = User.query.filter_by(username=form.username.data).first()
		attempted_password = form.password.data
		if attempted_user and attempted_user.check_password_correction(
			attempted_password=attempted_password
		):
			login_user(attempted_user)
			flash(f"Success! You are logged in as: {attempted_user.username}", category='success')
			return redirect(url_for('market_page'))
		else:
			flash('Wrong username or password', category='danger')

	return render_template('login.html', form=form)	

@app.route('/logout')
def logout_page():
	logout_user()
	flash('You have been logged out', category='info')
	return redirect(url_for('home_page'))