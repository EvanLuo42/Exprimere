import hashlib
import json
import re

from flask import Blueprint, request, session
from sqlalchemy.exc import NoResultFound, PendingRollbackError, IntegrityError
from werkzeug.exceptions import BadRequestKeyError

from sql import sql_session, Articles, Likes, Comments

article = Blueprint('article', __name__)


def article_dump(article_class):
    return {
        'aid': article_class.aid,
        'title': article_class.title,
        'content': article_class.content,
        'likes': article_class.likes,
        'comments': article_class.comments,
        'shares': article_class.shares,
        'reads': article_class.reads,
        'cover': article_class.cover,
        'author': article_class.author,
        'avatar': article_class.avatar,
        'nick_name': article_class.nick_name,
        'date': article_class.date
    }


@article.route('/articles')
def get_all_articles():
    return json.dumps(sql_session.query(Articles).all(), default=article_dump)


@article.route('/article/id/<aid>')
def get_article_by_id(aid):
    try:
        data = sql_session.query(Articles).filter_by(aid=aid).one()
        data.reads = data.reads + 1
        return json.dumps(data, default=article_dump)
    except NoResultFound:
        return json.dumps({
            'message': 'Article not found'
        }), 404
    except PendingRollbackError:
        sql_session.rollback()
    except BadRequestKeyError:
        return json.dumps({
            'message': 'Empty form.'
        }), 403


@article.route('/article', methods=['POST'])
def add_article():
    try:
        if request.form['title'] == '' or request.form['content'] == '' or request.form['avatar'] == '' or \
                request.form['nick_name'] == '':
            return json.dumps({
                'message': 'Empty form.'
            }), 403

        if re.match('[a-zA-z]+://[^\s]*', request.form['avatar']) is None:
            return json.dumps({
                'message': 'Please give a url as your avatar.'
            }), 403

        if re.match('[a-zA-z]+://[^\s]*', request.form['cover']) is None:
            return json.dumps({
                'message': 'Please give a url as your cover.'
            }), 403

        if session.get('uid') is not None:
            aid = (hashlib.md5(request.form['title'].encode(encoding='utf-8')).hexdigest())[8:-8].lower()
            new_article = Articles(aid=aid,
                                   title=request.form['title'],
                                   content=request.form['content'],
                                   cover=request.form['cover'],
                                   author=session.get('uid'),
                                   avatar=request.form['avatar'],
                                   nick_name=request.form['nick_name'])
            sql_session.add(new_article)
            sql_session.commit()

            return json.dumps({
                'message': 'Add article successfully.'
            })
        else:
            return json.dumps({
                'message': 'You are offline. Please login first.'
            })
    except IntegrityError:
        return json.dumps({
            'message': 'Article existed.'
        }), 409
    except PendingRollbackError:
        sql_session.rollback()
    except BadRequestKeyError:
        return json.dumps({
            'message': 'Empty form.'
        }), 403
    finally:
        sql_session.close()


@article.route('/article/id/<aid>', methods=['DELETE'])
def delete_article(aid):
    try:
        if session.get('admin'):
            goal_article = sql_session.query(Articles).filter_by(aid=aid).one()
            sql_session.delete(goal_article)
            sql_session.commit()
            return json.dumps({
                'message': 'Delete article successfully.'
            })
        else:
            return json.dumps({
                'message': 'Permission is not enough.'
            }), 401
    except PendingRollbackError:
        sql_session.rollback()
    except BadRequestKeyError:
        return json.dumps({
            'message': 'Empty form.'
        }), 403
    finally:
        sql_session.close()


@article.route('/article/id/<aid>/like')
def like_article(aid):
    try:
        if session.get('uid'):
            goal_article = sql_session.query(Articles).filter_by(aid=aid).one()
            goal_article.likes = goal_article.likes + 1
            sql_session.commit()

            goal_like = Likes(aid=aid, uid=session.get('uid'))
            sql_session.add(goal_like)
            sql_session.commit()

            return json.dumps({
                'message': 'Liked successfully.'
            })
        else:
            return json.dumps({
                'message': 'Please login first.'
            }), 401
    except NoResultFound:
        return json.dumps({
            'message': 'Article not found'
        }), 404
    except PendingRollbackError:
        sql_session.rollback()
    except BadRequestKeyError:
        return json.dumps({
            'message': 'Empty form.'
        }), 403
    finally:
        sql_session.close()


@article.route('/article/id/<aid>/comment', methods=['POST'])
def comment_article(aid):
    try:
        if session.get('uid') is None:
            return json.dumps({
                'message': 'Please login first.'
            }), 401

        if request.form['content'] == '' or request.form['avatar'] == '' or request.form['nick_name'] == '':
            return json.dumps({
                'message': 'Empty form.'
            }), 403

        if re.match('[a-zA-z]+://[^\s]*', request.form['avatar']) is None:
            return json.dumps({
                'message': 'Please give a url as your avatar.'
            }), 403

        if session.get('uid'):
            goal_article = sql_session.query(Articles).filter_by(aid=aid).one()
            goal_article.comments = goal_article.comments + 1
            sql_session.commit()

            comment = Comments(author=session.get('uid'),
                               content=request.form['content'],
                               avatar=request.form['avatar'],
                               nick_name=request.form['nick_name'],
                               aid=aid)
            sql_session.add(comment)
            sql_session.commit()

            return json.dumps({
                'message': 'Commented successfully.'
            })
    except NoResultFound:
        return json.dumps({
            'message': 'Article not found'
        }), 404
    except PendingRollbackError:
        sql_session.rollback()
    except BadRequestKeyError:
        return json.dumps({
            'message': 'Empty form.'
        }), 403
    finally:
        sql_session.close()


@article.route('/article/id/<aid>/subscribe')
def subscribe_article(aid):
    try:
        if session.get('uid'):
            goal_article = sql_session.query(Articles).filter_by(aid=aid).one()
            goal_article.likes = goal_article.likes + 1
            sql_session.commit()

            goal_like = Likes(aid=aid, uid=session.get('uid'))
            sql_session.add(goal_like)
            sql_session.commit()

            return json.dumps({
                'message': 'Liked successfully.'
            })
        else:
            return json.dumps({
                'message': 'Please login first.'
            }), 401
    except NoResultFound:
        return json.dumps({
            'message': 'Article not found'
        }), 404
    except PendingRollbackError:
        sql_session.rollback()
    except BadRequestKeyError:
        return json.dumps({
            'message': 'Empty form.'
        }), 403
    finally:
        sql_session.close()
