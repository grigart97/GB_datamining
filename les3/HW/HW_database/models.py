import datetime as dt
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from sqlalchemy import Column, Integer, String, ForeignKey, Table, DateTime, Boolean

Base = declarative_base()


class UrlMixin:
    url = Column(String, nullable=False, unique=True)


class IDMixin:
    id = Column(Integer, primary_key=True)


tag_post = Table(
    'tag_post',
    Base.metadata,
    Column('post_id', Integer, ForeignKey('post.id')),
    Column('tag_id', Integer, ForeignKey('tag.id'))
)


class Post(Base, UrlMixin, IDMixin):
    __tablename__ = 'post'
    post_title = Column(String, nullable=False, unique=False)
    img_url = Column(String, nullable=False, unique=False)
    post_date = Column(DateTime, nullable=False, unique=False)
    author_id = Column(Integer, ForeignKey('user.id'))
    author = relationship('User')
    tags = relationship('Tag', secondary=tag_post)
    comments = relationship('Comment')


class User(Base, IDMixin):
    __tablename__ = 'user'
    name = Column(String, nullable=False, unique=False)
    post = relationship(Post)
    comments = relationship('Comment')


class Tag(Base, UrlMixin):
    __tablename__ = 'tag'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    posts = relationship(Post, secondary=tag_post)


class Comment(Base, IDMixin):
    __tablename__ = 'comment'
    parent_id = Column(Integer, ForeignKey('comment.id'), nullable=False)
    root_comment_id = Column(Integer, ForeignKey('comment.id'), nullable=False)
    likes_count = Column(Integer)
    body = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    hidden = Column(Boolean)
    deep = Column(Integer)
    post_id = Column(Integer, ForeignKey('post.id'))
    author_id = Column(Integer, ForeignKey('user.id'))
    author = relationship('User')

    def __init__(self, **kwargs):
        self.id = kwargs['id']
        self.parent_id = kwargs['parent_id']
        self.root_comment_id = kwargs['root_comment_id']
        self.likes_count = kwargs['likes_count']
        self.body = kwargs['body']
        self.created_at = dt.datetime.fromisoformat(kwargs['created_at'])
        self.hidden = kwargs['hidden']
        self.deep = kwargs['deep']
        self.author = kwargs['author']





