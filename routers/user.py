import json
import re
from datetime import datetime

from flask import Blueprint, session, request
from sqlalchemy.exc import NoResultFound, PendingRollbackError
from werkzeug.exceptions import BadRequestKeyError

from sql import sql_session, Users

user = Blueprint('user', __name__)


def user_dump(users_class):
    return {
        'uid': users_class.uid,
        'userName': users_class.user_name,
        'avatar': users_class.avatar,
        'description': users_class.description,
        'admin': users_class.admin,
        'date': users_class.date
    }


@user.route('/users')
def get_all_users():
    print(datetime.today())
    return json.dumps(sql_session.query(Users).all(), default=user_dump)


@user.route('/user/id/<uid>')
def get_user_by_id(uid):
    try:
        data = sql_session.query(Users).filter_by(uid=uid).one()
        return json.dumps(data, default=user_dump)
    except NoResultFound:
        return json.dumps({
            'message': 'User not found'
        }), 404
    except PendingRollbackError:
        sql_session.rollback()
    except BadRequestKeyError:
        return json.dumps({
            'message': 'Empty form.'
        }), 403


@user.route('/user/name/<user_name>')
def get_user_by_user_name(user_name):
    try:
        data = sql_session.query(Users).filter_by(user_name=user_name).one()
        return json.dumps(data, default=user_dump)
    except NoResultFound:
        return json.dumps({
            'message': 'User not found'
        }), 404
    except PendingRollbackError:
        sql_session.rollback()
    except BadRequestKeyError:
        return json.dumps({
            'message': 'Empty form.'
        }), 403


@user.route('/user/id/<uid>', methods=['DELETE'])
def ban_user(uid):
    if session.get('admin'):
        try:
            goal_user = sql_session.query(Users).filter_by(uid=uid).one()
            sql_session.delete(goal_user)
            sql_session.commit()

            return json.dumps({
                'message': 'Baned user successfully.'
            })
        except PendingRollbackError:
            sql_session.rollback()
        except BadRequestKeyError:
            return json.dumps({
                'message': 'Empty form.'
            }), 403
        except NoResultFound:
            return json.dumps({
                'message': 'User not found'
            }), 404
        finally:
            sql_session.close()
    else:
        return json.dumps({
            'message': 'Permission is not enough.'
        }), 401


@user.route('/user', methods=['POST'])
def change_user_setting():
    try:
        if re.match('[a-zA-z]+://[^\s]*', request.form['avatar']) is None:
            return json.dumps({
                'message': 'Please give a url as your avatar.'
            }), 403

        if session.get('uid') is not None:
            goal_user = sql_session.query(Users).filter_by(uid=session.get('uid')).one()
            goal_user.user_name = request.form['user_name']
            goal_user.avatar = request.form['avatar']
            goal_user.description = request.form['description']
            sql_session.commit()

            return json.dumps({
                'message': 'Changed setting successfully.'
            })
    except PendingRollbackError:
        sql_session.rollback()
    except BadRequestKeyError:
        return json.dumps({
            'message': 'Empty form.'
        }), 403
    except NoResultFound:
        return json.dumps({
            'message': 'User not found'
        }), 404
    finally:
        sql_session.close()

