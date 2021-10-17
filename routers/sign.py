import hashlib
import json
import uuid

from flask import Blueprint, request, session
from sqlalchemy.exc import IntegrityError, NoResultFound, PendingRollbackError
from werkzeug.exceptions import BadRequestKeyError

import utils.email
from sql import sql_session, Users

sign = Blueprint('sign', __name__)
authing_email = []


@sign.route('/login', methods=['POST'])
def login():
    try:
        sha256 = hashlib.sha256()
        sha256.update(request.form['password'].encode('utf-8'))
        data = sql_session.query(Users).filter_by(user_name=request.form['user_name'],
                                                  password=sha256.hexdigest()).one()
        session['uid'] = data.uid
        session['admin'] = data.admin

        return json.dumps({
            'message': 'Login successfully.'
        })
    except NoResultFound:
        return json.dumps({
            'message': 'Username or password incorrect.'
        }), 400
    except PendingRollbackError:
        sql_session.rollback()


@sign.route('/register', methods=['POST'])
def register():
    if request.form['user_name'] == '' or request.form['password'] == '' or request.form['captcha'] == '':
        return json.dumps({
            'message': 'Empty form.'
        }), 403

    time = 0

    for captcha in authing_email:
        if captcha.captcha == request.form['captcha']:
            time = time + 1
            authing_email.remove(captcha)

    if time != 0:
        try:
            sha256 = hashlib.sha256()
            sha256.update(request.form['password'].encode('utf-8'))
            new_user = Users(user_name=request.form['user_name']
                             , password=sha256.hexdigest()
                             , email=request.form['email'])
            sql_session.add(new_user)
            sql_session.commit()
            sql_session.close()

            return json.dumps({
                'message': 'Register successfully.'
            })
        except IntegrityError:
            return json.dumps({
                'message': 'User existed'
            }), 409
        except PendingRollbackError:
            sql_session.rollback()
        except BadRequestKeyError:
            return json.dumps({
                'message': 'Empty form.'
            }), 403
    else:
        return json.dumps({
            'message': 'Captcha incorrect.'
        }), 403


class Captcha:
    email = ''
    captcha = ''

    def __init__(self, email, captcha):
        self.email = email
        self.captcha = captcha


@sign.route('/captcha')
def send_captcha():
    if request.args.get('email') is not None or request.args.get('email') != '':
        captcha = Captcha(request.args.get('email'), hashlib.md5(str(uuid.uuid4())
                                                                 .encode(encoding='utf-8')).hexdigest()[1:-25].lower())
        for authing in authing_email:
            if authing.email == captcha.email:
                authing_email.remove(authing)
        if utils.email.send_captcha(captcha):
            authing_email.append(captcha)
            return json.dumps({
                'message': 'Captcha sended successfully.'
            })
        else:
            return json.dumps({
                'message': 'System error.'
            }), 502


@sign.route('/password', methods=['POST'])
def change_password():
    try:
        if request.form['captcha'] == '' or request.form['email'] == '' or request.form['password'] == '':
            return json.dumps({
                'message': 'Empty form.'
            }), 403

        user = sql_session.query(Users).filter_by(email=request.form['email']).one()
        time = 0
        for captcha in authing_email:
            if captcha.captcha == request.form['captcha'] and captcha.email == request.form['email']:
                time = time + 1
                authing_email.remove(captcha)

        if time != 0:
            sha256 = hashlib.sha256()
            sha256.update(request.form['password'].encode('utf-8'))
            user.password = sha256.hexdigest()
            sql_session.commit()
            sql_session.close()
            return json.dumps({
                'message': 'Password changed successfully.'
            })
        else:
            return json.dumps({
                'message': 'Captcha incorrect.'
            }), 401
    except PendingRollbackError:
        sql_session.rollback()
    except BadRequestKeyError:
        return json.dumps({
            'message': 'Empty form.'
        }), 403
