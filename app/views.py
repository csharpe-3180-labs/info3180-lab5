"""
Flask Documentation:     https://flask.palletsprojects.com/
Jinja2 Documentation:    https://jinja.palletsprojects.com/
Werkzeug Documentation:  https://werkzeug.palletsprojects.com/
This file creates your application.
"""

from app import app, db, login_manager
from flask import render_template, request, jsonify, send_file, redirect, url_for, flash, session, abort
from flask_login import login_user, logout_user, current_user, login_required
from flask_wtf.csrf import generate_csrf, CSRFError
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import UserProfile, Movie
from app.forms import LoginForm, MovieForm
from flask import send_from_directory
from urllib.parse import urlparse, urljoin
import os


def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and ref_url.netloc == test_url.netloc


###
# Routing for your application.
###

@app.route('/')
def index():
    return jsonify(message="This is the beginning of our API")

@app.route('/api/v1/csrf-token', methods=['GET'])
def get_csrf():
    return jsonify({'csrf_token': generate_csrf()})



@app.route('/api/v1/movies', methods=['POST'])
def movies():
    form = MovieForm()
    if form.validate_on_submit():
        title = form.title.data
        description = form.description.data
        poster_file = form.poster.data

        filename = secure_filename(poster_file.filename)
        upload_folder = app.config.get('UPLOAD_FOLDER') or 'uploads'
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

@app.route('/api/v1/movies', methods=['GET'])
def get_movies():
    movies = db.session.execute(db.select(Movie)).scalars().all()
    movie_list = [
        {
            'id': m.id,
            'title': m.title,
            'description': m.description,
            'poster': f'/api/v1/posters/{m.poster}'
        } for m in movies
    ]
    return jsonify({'movies': movie_list})

@app.route('/api/v1/posters/<filename>', methods=['GET'])
def get_poster(filename):
    return send_from_directory(
        os.path.join(os.getcwd(), app.config.get('UPLOAD_FOLDER', 'uploads')),
        filename
    )

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
    response.headers['Cache-Control'] = 'public, max-age=600'
    return response


@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    return jsonify({'errors': [str(e.description)]}), 400

@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404

