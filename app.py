import os
from flask import send_from_directory
from flask import Flask, render_template, url_for, redirect, flash, request, \
    make_response, jsonify
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user, login_user
from flask_restful import Api
from flask_bootstrap import Bootstrap
from config import Config
from werkzeug.urls import url_parse
from werkzeug.security import generate_password_hash, check_password_hash
from webargs import fields, validate, ValidationError
from webargs.flaskparser import use_args, use_kwargs
import jwt
import json
import datetime


app = Flask(__name__)
app.config.from_object(Config)
config = app.config
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
api = Api(app)
bootstrap = Bootstrap(app)


from nhs_app.api.models import models
from nhs_app.api.data import data
from nhs_app.api.auth import auth
from nhs_app.resource.update_aggregator import Aggregator
from nhs_app.resource.node import NodeRegister
from nhs_app.resource.user import UserLogout
from nhs_app.resource.ml_resource import MLDownload, MLTrainingResource, ModelAvailability
from nhs_app.resource.project import Dashboard, Homepage, ApiDoc
from nhs_app.forms.user_forms import UserLogin, UserRegister
from nhs_app.models.user_model import User
from nhs_app.models.uploaded_model import UploadedModelMeta
# from auth.main import login_required


app.register_blueprint(auth, url_prefix='/api/auth')
app.register_blueprint(data, url_prefix='/api/data')
app.register_blueprint(models, url_prefix='/api/models')

api.add_resource(Homepage, '/index', '/', endpoint='index')
api.add_resource(Aggregator, '/update/<string:uid>', endpoint='update')
api.add_resource(NodeRegister, '/node', endpoint='node')
api.add_resource(UserLogout, '/logout', endpoint='logout')
api.add_resource(ApiDoc, '/doc', endpoint='doc')
api.add_resource(Dashboard, '/dashboard', endpoint='dashboard')
api.add_resource(MLDownload, '/model', endpoint='model')
api.add_resource(MLTrainingResource, '/train', endpoint='train')
api.add_resource(ModelAvailability, '/available', endpoint='available')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = UserLogin()
    if form.validate_on_submit():
        user = User.find_by_username(form.username.data)
        if user is None  or not user.check_password(form.password.data):
            # or user.user_type != 1:
            flash('Invalid username or password')
            return redirect(url_for('login'))

        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')

        return redirect(next_page)

    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
  if current_user.is_authenticated:
    return redirect(url_for('dashboard'))

    form = UserRegister()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data, user_type=False,
                    password=form.password.data)
        user.save_to_db()
        flash('Congratulations, registration completed. System admin will review and approve your permissions shortly.')
        return redirect(url_for('index'))

    return render_template('register.html', form=form)



@app.errorhandler(404)
def not_found_error(error):
    headers = {'Content-Type': 'text/html'}
    return make_response(render_template('404.html'), 400, headers)


@app.errorhandler(500)
def internal_error(error):
    headers = {'Content-Type': 'text/html'}
    return make_response(render_template('500.html'), 500, headers)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


if __name__ == '__main__':
    db.init_app(app)
    app.run(port=5000, debug=True)
