from flask import Blueprint, redirect, url_for, flash, render_template, request
from flask_login import current_user, login_user, logout_user, login_required
from sqlalchemy import or_, and_, func

from talkintunes import bcrypt, db
from talkintunes.users.forms import RegistrationForm, LoginForm, UpdateAccountForm, RequestResetForm, ResetPasswordForm
from talkintunes.models import User, Messages
from talkintunes.users.utils import save_picture, send_reset_email, decrypt_message, encrypt_message, generate_rsa_key, \
    serialize_rsa_key_to_pem

users = Blueprint('users', __name__)


@users.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        private_key = generate_rsa_key()

        private_pem_file_path, public_pem = serialize_rsa_key_to_pem(private_key,form.username.data)

        user = User(username=form.username.data,
                    email=form.email.data,
                    password=hashed_pw,
                    public_key=public_pem,
                    private_key=private_pem_file_path)
        db.session.add(user)
        db.session.commit()
        flash(f'Your account has been created. You can now Login!', 'success')
        return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)

@users.route('/')
@users.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('You have been logged in', 'success')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash('Login Unsuccessful! Please check Email and Password', 'danger')
    return render_template('login.html', title='Login', form=form)


@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('users.login'))


@users.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file

        current_user.username = form.username.data
        current_user.email = form.email.data

        db.session.commit()
        flash('Your account has been submitted', 'success')
        return redirect(url_for('users.account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_path = url_for('static', filename=current_user.image_file)
    return render_template('account.html', title='Account',
                           image_path=image_path, form=form)


@login_required
@users.route("/user")
def user_messages():
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=current_user.username).first_or_404()

    subquery = db.session.query(
        func.max(Messages.date).label("max_date"),
        func.least(Messages.sender_id, Messages.receiver_id).label("sorted_sender_id"),
        func.greatest(Messages.sender_id, Messages.receiver_id).label("sorted_receiver_id")
    ).group_by("sorted_sender_id", "sorted_receiver_id").subquery()

    # Join the Messages table with the subquery to get the complete message data for the last messages
    last_messages = db.session.query(Messages).join(
        subquery,
        and_(
            or_(
                Messages.sender_id == user.id,
                Messages.receiver_id == user.id
            ),
            func.least(Messages.sender_id, Messages.receiver_id) == subquery.c.sorted_sender_id,
            func.greatest(Messages.sender_id, Messages.receiver_id) == subquery.c.sorted_receiver_id,
            Messages.date == subquery.c.max_date
        )
    ).all()

    # for msg in last_messages:
    #     content = msg['content']

    return render_template('user_messages.html', messages=last_messages, title='Messages', user=user)


@users.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        redirect(url_for('main.home'))
    user = User.verify_reset_token(token=token)
    if user is None:
        flash('This is an invalid or expired tokne', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_pw
        db.session.commit()
        flash(f'Your password has been updated. You can now Login!', 'success')
        return redirect(url_for('users.login'))
    return render_template('reset_token.html', title='Reset Password', form=form)

# def get_all_users():
#     users = User.query.with_entities(User.username, User.id).all()