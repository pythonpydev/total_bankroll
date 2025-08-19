from flask import Blueprint, render_template, redirect, url_for, flash, current_app, request, session
from flask_security import login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email
from werkzeug.security import check_password_hash

auth_bp = Blueprint('auth', __name__)

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')

class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Register')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    print(f"Processing login request. Form method: {request.method}")
    if request.method == 'GET':
        # Clear flash messages on GET to prevent showing old messages
        session.pop('_flashes', None)
    if request.method == 'POST':
        if form.validate_on_submit():
            user_datastore = current_app.extensions['security'].datastore
            user = user_datastore.find_user(email=form.email.data)
            if user and check_password_hash(user.password, form.password.data):
                print(f"User {user.email} found and password verified. User ID: {user.id}")
                if user.id is None:
                    print(f"Error: User {user.email} has no ID. Not logging in.")
                    flash('Account error: No user ID. Please contact support.', 'danger')
                    return redirect(url_for('auth.login'))
                login_user(user)
                print(f"login_user called. User authenticated: {current_user.is_authenticated}")
                print(f"User ID in session: {session.get('user_id')}")
                print(f"Flask session after login_user: {session}")
                flash('Logged in successfully!', 'success')
                return redirect(url_for('home.home'))
            else:
                print(f"Invalid email or password for {form.email.data}")
                flash('Invalid email or password.', 'danger')
    return render_template('security/login_user.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user_datastore = current_app.extensions['security'].datastore
        db = current_app.extensions['sqlalchemy'].db
        user = user_datastore.create_user(
            email=form.email.data,
            password=user_datastore.hash_password(form.password.data),
            fs_uniquifier=os.urandom(24).hex()
        )
        db.session.commit()
        print(f"Registered user: email={user.email}, id={user.id}, fs_uniquifier={user.fs_uniquifier}")
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('security/register_user.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    print(f"Logging out user: {current_user.email}, session before: {session}")
    logout_user()
    print(f"Session after logout: {session}")
    flash('Logged out successfully.', 'success')
    return redirect(url_for('auth.login'))