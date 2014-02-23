# -*- coding: utf-8 -*-
"""
    precomp.account
    ~~~~~~~~~~~~~~~

    GitHub Authentication

    :copyright: 2014 Carey Metcalfe, Graham McGregor, Phil Schleihauf
"""

from os import urandom
from base64 import urlsafe_b64encode
from precomp import app
from urllib.parse import urlparse, urljoin, parse_qsl
from bson.objectid import ObjectId
from requests.sessions import Session
from requests.utils import default_user_agent
from rauth.service import OAuth2Session, OAuth2Service
from flask import (request, session as client_session, flash, render_template,
                   url_for, redirect, json)
from flask.ext.login import (LoginManager, login_user, logout_user, UserMixin,
                             current_user, login_required)
from flask.ext.pymongo import PyMongo
from flask.ext.kale import Kale


GH_BASE_URL = 'https://api.github.com/'


login_manager = LoginManager(app)

mongo = PyMongo(app)
kale = Kale(app)


def useragentify(session):
    """declare a specific user-agent for commit --blog"""
    user_agent = default_user_agent('commit --blog')
    session.headers.update({'User-Agent': user_agent})


class GHAppSession(Session):
    """A session object for app-authenticated GitHub API requests

    Allows relative URLs from a base_url.

    Injects the app id and secret instead of the user's (useless-for-no-scopes)
    bearer token to make requests to public endpoints with the usual 5000 req
    rate limit rules.
    """

    def __init__(self, base_url, client_id, client_secret):
        super(GHAppSession, self).__init__()
        useragentify(self)
        self.base_url = base_url
        self.client_id = client_id
        self.client_secret = client_secret

    def request(self, method, url, **req_kwargs):
        # absolutify URL
        if not bool(urlparse(url).netloc):
            url = urljoin(self.base_url, url)

        # inject app credentials
        params = req_kwargs.pop('params', {})
        if isinstance(params, str):
            params = parse_qsl(params)
        params.update(client_id=self.client_id,
                      client_secret=self.client_secret)

        return super(GHAppSession, self).request(method, url, params=params,
                     **req_kwargs)


class GHOAuthSession(OAuth2Session):
    """An OAuth2 session for user authentication, with a nice UA header"""

    def __init__(self, *args, **kwargs):
        super(GHOAuthSession, self).__init__(*args, **kwargs)
        useragentify(self)


gh_oauth = OAuth2Service(name='github',
   base_url=GH_BASE_URL,
   authorize_url='https://github.com/login/oauth/authorize',
   access_token_url='https://github.com/login/oauth/access_token',
   client_id=app.config['GITHUB_CLIENT_ID'],
   client_secret=app.config['GITHUB_CLIENT_SECRET'],
   session_obj=GHOAuthSession,
)
AppSession = lambda: GHAppSession(GH_BASE_URL,
   client_id=app.config['GITHUB_CLIENT_ID'],
   client_secret=app.config['GITHUB_CLIENT_SECRET'],
)


@kale.dbgetter
def get_mongodb():
    return mongo.db


class User(kale.Model, UserMixin):

    _collection_name = 'users'

    """
    {
      username: github "login",
      name: github full name or null,
      avatar_url: a url for a lovely picture,
      access_token: github 40 char token,
    }
    """

    @classmethod
    def gh_get_or_create(cls, session):
        user_obj = session.get('user').json()
        user = cls.collection.find_one({'username': str(user_obj['login'])})
        if user is None:
            user = cls(
                username=user_obj['login'],
                name=user_obj.get('name'),
                avatar_url=user_obj.get('avatar_url'),
                access_token=session.access_token,
            )
            user.save()
        fresh = lambda k: user_obj.get(k) != user[k] and user[k] is not None
        newly_updated = filter(fresh, ('name', 'avatar_url'))
        if newly_updated:
            for prop in newly_updated:
                user[prop] = user_obj.get(prop)
            user.save()
        return user

    def get_id(self):
        return str(self._id)

    def get_session(self):
        return gh_oauth.get_session(token=self.access_token)


@login_manager.user_loader
def load_user(user_id):
    oid = ObjectId(user_id)
    user = User.collection.find_one(oid)
    return user


@app.route("/")
def home():
    return render_template("home.html", page='home')


@app.route('/login')
def login():
    auth_uri = gh_oauth.get_authorize_url()
    return redirect(auth_uri)
    # continued in authorized....

@app.route('/authorized')
def authorized():
    # final stage of oauth login

    if 'code' not in request.args:
        flash('Sorry, you gotta sign in through GitHub to use Precomp :(')
        return redirect(url_for('home', auth='sadface'))

    session = gh_oauth.get_auth_session(data={'code': request.args['code']})
    user = User.gh_get_or_create(session)

    login_user(user)
    return redirect(url_for('account'))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/account')
@login_required
def account():
    hide_message = True if 'dismissed_welcome' in current_user else False
    return render_template('account.html', page='account',
                           hide_message=hide_message)


@app.route('/dismiss-welcome')
@login_required
def dismiss_welcome():
    current_user.dismissed_welcome = True
    current_user.save()
    return redirect(url_for('account'))

