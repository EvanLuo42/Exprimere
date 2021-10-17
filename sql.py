from datetime import datetime

from sqlalchemy import create_engine, Column, String, Integer, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:////Users/phakel/PycharmProjects/exprimere/exprimere.db', echo=True,
                       connect_args={'check_same_thread': False})
Base = declarative_base()
Session = sessionmaker(bind=engine)
sql_session = Session()


class Articles(Base):
    __tablename__ = 'articles'

    aid = Column(String(50), primary_key=True, unique=True)
    title = Column(String(50), unique=True)
    content = Column(String(300), unique=True)
    likes = Column(Integer)
    comments = Column(Integer)
    shares = Column(Integer)
    reads = Column(Integer)
    cover = Column(String(50))
    author = Column(Integer)
    avatar = Column(String(50))
    nick_name = Column(String(50))
    date = Column(Integer)

    def __init__(self, aid, title, content, cover, author, avatar, nick_name, likes=0, comments=0, shares=0, reads=0,
                 date=datetime.now().timestamp()):
        self.aid = aid
        self.title = title
        self.content = content
        self.likes = likes
        self.comments = comments
        self.shares = shares
        self.reads = reads
        self.cover = cover
        self.author = author
        self.date = date
        self.avatar = avatar
        self.nick_name = nick_name


class Users(Base):
    __tablename__ = 'users'

    uid = Column(Integer, primary_key=True, autoincrement=True, unique=True)
    user_name = Column(String(50), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    avatar = Column(String(50))
    description = Column(String(100))
    admin = Column(Boolean)
    date = Column(Integer)

    def __init__(self, user_name, password, email, avatar='', description='', admin=False,
                 date=datetime.now().timestamp()):
        self.user_name = user_name
        self.password = password
        self.avatar = avatar
        self.description = description
        self.admin = admin
        self.date = date
        self.email = email


class Comments(Base):
    __tablename__ = 'comments'

    comment_id = Column(Integer, primary_key=True, autoincrement=True)
    aid = Column(String(50))
    author = Column(Integer)
    content = Column(String(100))
    avatar = Column(String(50))
    nick_name = Column(String(50))
    date = Column(Integer)

    def __init__(self, author, content, nick_name, avatar, aid, date=datetime.now().timestamp()):
        self.date = date
        self.author = author
        self.content = content
        self.avatar = avatar
        self.nick_name = nick_name
        self.aid = aid


class Subscribes(Base):
    __tablename__ = 'subscribes'

    subscribe_id = Column(Integer, autoincrement=True, primary_key=True)
    subscribed_article = Column(String(50))
    subscriber = Column(Integer)

    def __init__(self, subscribed_article, subscriber):
        self.subscriber = subscriber
        self.subscribed_article = subscribed_article


class Likes(Base):
    __tablename__ = 'likes'

    like_id = Column(Integer, primary_key=True, autoincrement=True)
    aid = Column(String(50), primary_key=True)
    uid = Column(Integer)

    def __init__(self, aid, uid):
        self.aid = aid
        self.uid = uid


Base.metadata.create_all(engine, checkfirst=True)
