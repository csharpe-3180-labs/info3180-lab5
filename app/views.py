"""
Flask Documentation:     https://flask.palletsprojects.com/
Jinja2 Documentation:    https://jinja.palletsprojects.com/
Werkzeug Documentation:  https://werkzeug.palletsprojects.com/
This file creates your application.
"""

from app import app, db, login_manager
from flask import render_template, request, jsonify, send_file, redirect, url_for, flash, session, abort
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import UserProfile, Movie
from app.forms import LoginForm, MovieForm
from flask import send_from_directory
from is_safe_url import is_safe_url
import os


###
# Routing for your application.
###

@app.route('/')
def index():
    return jsonify(message="This is the beginning of our API")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('secure_page'))
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = db.session.execute(db.select(UserProfile).filter_by(username=username)).scalar()
        if user is not None and check_password_hash(user.password, password):
            remeber_me = False

            if 'remeber_me' in request.form:
                remeber_me = True
                login_user(user, remember=remeber_me)
                flash('Logged in successfully.', 'success')
                next_page = request.args.get('next')

                if not is_safe_url(next_page, request.host):
                    return abort(400)
                return redirect(next_page or url_for('home'))
            else:
                flash('Username or Password is incorrect.', 'danger')

            flash_errors(form)
            return render_template('login.html', form=form)

@app.route('logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

@login_manager.user_loader
def load_user(id):
    return db.session.execute(db.select(UserProfile).filter_by(id=id)).scalar()

@app.route('/api/v1/movies', methods=['POST'])
@login_required
def movies():
    form = MovieForm()
    if form.validate_on_submit():
        title = form.title.data
        description = form.description.data
        poster_file = form.poster.data

        filename = secure_filename(poster_file.filename)
        upload_folder = app.config.get('UPLOAD_FOLDER')
        os.makedirs(upload_folder, exist_ok=True)
        poster_file.save(os.path.join(upload_folder, filename))

        movie = Movie(title=title, description=description, poster=filename)
        db.session.add(movie)
        db.session.commit()

        return jsonify({
            'message': 'Movie Successfully added',
            'title': movie.title,
            'poster': movie.poster,
            'description': movie.description
        }), 201

    return jsonify({'errors': form_errors(form)}), 400

###
# The functions below should be applicable to all Flask apps.
###

# Here we define a function to collect form errors from Flask-WTF
# which we can later use
def form_errors(form):
    error_messages = []
    """Collects form errors"""
    for field, errors in form.errors.items():
        for error in errors:
            message = u"Error in the %s field - %s" % (
                    getattr(form, field).label.text,
                    error
                )
            error_messages.append(message)

    return error_messages

@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also tell the browser not to cache the rendered page. If we wanted
    to we could change max-age to 600 seconds which would be 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404