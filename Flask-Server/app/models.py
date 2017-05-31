# -*- coding: utf-8 -*-
import time
from flask_login import UserMixin
from datetime import datetime, date
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """用户"""
    __tablename__ = 'users'
    __table_args__ = {'mysql_engine': 'InnoDB'}  # 支持事务操作和外键

    id = db.Column(db.String(11), doc='手机号码', primary_key=True)
    password = db.Column(db.String(32), doc='密码', nullable=False)
    payPassword = db.Column(db.String(32), doc='支付密码', nullable=False)
    nickname = db.Column(db.String(20), doc='昵称', default='猿眼用户', nullable=False)
    money = db.Column(db.Float, doc='账户余额', default=50, nullable=False)
    description = db.Column(db.String(50), doc='个性签名', default='这个人很懒，什么也没留下', nullable=False)
    avatar = db.Column(db.String(20), doc='头像路径', default='MonkeyEye.jpg')
    isAdmin = db.Column(db.Boolean, doc='是否管理员', default=False)

    orders = db.relationship('Order', backref='users', cascade='all', lazy='dynamic')
    coupons = db.relationship('Coupon', backref='users', cascade='all', lazy='dynamic')
    favorites = db.relationship('Favorite', backref='users', cascade='all', lazy='dynamic')
    comments = db.relationship('Comment', backref='users', cascade='all', lazy='dynamic')

    def __repr__(self):
        return '%s <%s>' % (self.nickname, self.id)

    def __json__(self):
        return {
            'id': self.id,
            'nickname': self.nickname,
            'avatar': '/static/images/user/%s' % self.avatar,
            'description': self.description,
            'money': self.money
        }


class Movie(db.Model):
    """电影"""
    __tablename__ = 'movies'
    __table_args__ = {'mysql_engine': 'InnoDB'}  # 支持事务操作和外键

    id = db.Column(db.String(32), primary_key=True)
    expired = db.Column(db.Boolean, doc='是否下架', default=False, nullable=False)
    name = db.Column(db.String(25), doc='电影名称', nullable=False)
    description = db.Column(db.Text, doc='电影介绍', default='暂无介绍', nullable=False)
    playingTime = db.Column(db.Date, doc='上映时间', default=date.today(), nullable=False)
    duration = db.Column(db.SmallInteger, doc='电影时长(分钟)', nullable=False)
    movieType = db.Column(db.String(20), doc='电影类型', nullable=False)
    playingType = db.Column(db.String(15), doc='放映类型', nullable=False)
    rating = db.Column(db.Float, doc='电影评分', default=0)
    ratingNum = db.Column(db.SmallInteger, doc='评分人数', default=0)
    poster = db.Column(db.String(40), doc='海报路径')

    screens = db.relationship('Screen', backref='movies', cascade='all', lazy='dynamic')
    recommends = db.relationship('Recommend', backref='movies', cascade='all', lazy='dynamic')
    comments = db.relationship('Comment', backref='movies', cascade='all', lazy='dynamic')
    favorites = db.relationship('Favorite', backref='movies', cascade='all', lazy='dynamic')

    def __repr__(self):
        return '%s <%s>' % (self.name, self.id)

    def __json__(self):
        return {
            'id': self.id,
            'name': self.name,
            'poster': '/static/images/poster/%s' % self.poster,
            'movieType': self.movieType,
            'playingType': self.playingType,
            'playingTime': time.mktime(self.playingTime.timetuple()) * 1000,
            'duration': self.duration,
            'rating': self.rating,
            'description': self.description,
            'ratingNum': self.ratingNum
        }


class Screen(db.Model):
    """场次"""
    __tablename__ = 'screens'
    __table_args__ = {'mysql_engine': 'InnoDB'}  # 支持事务操作和外键

    id = db.Column(db.String(32), primary_key=True)
    movieId = db.Column(db.String(32), db.ForeignKey('movies.id'), nullable=False)
    time = db.Column(db.DateTime, doc='场次时间', default=datetime.now(), nullable=False)
    hallNum = db.Column(db.String(1), doc='放映厅(1-5)', nullable=False)
    price = db.Column(db.Float, doc='票价', default=30, nullable=False)
    ticketNum = db.Column(db.SmallInteger, doc='电影总票数', default=120, nullable=False)

    orders = db.relationship('Order', backref='screens', cascade='all', lazy='dynamic')

    def __repr__(self):
        res = {
            'id': self.id,
            'name': Movie.query.get(self.movieId).name,
            'time': self.time.strftime('%Y-%m-%d %X')
        }
        return '{name} [{time}] <{id}>'.format(**res)

    def __json__(self):
        movie = Movie.query.get(self.movieId)
        return {
            'id': self.id,
            'movie': movie.__json__(),
            'time': time.mktime(self.time.timetuple()) * 1000,
            'price': self.price,
            'ticketNum': self.ticketNum,
            'hallNum': self.hallNum,
            'playingType': movie.playingType
        }


class Recommend(db.Model):
    """推荐"""
    __tablename__ = 'recommends'
    __table_args__ = {'mysql_engine': 'InnoDB'}  # 支持事务操作和外键

    movieId = db.Column(db.String(32), db.ForeignKey('movies.id'), primary_key=True, nullable=False)

    def __json__(self):
        movie = Movie.query.get(self.movieId)
        return {
            'movieId': self.movieId,
            'poster': '/static/images/poster/%s' % movie.poster,
            'playingTime': time.mktime(movie.playingTime.timetuple()) * 1000
        }


class Order(db.Model):
    """订单"""
    __tablename__ = 'orders'
    __table_args__ = {'mysql_engine': 'InnoDB'}  # 支持事务操作和外键

    id = db.Column(db.String(32), primary_key=True)
    screenId = db.Column(db.String(32), db.ForeignKey('screens.id'), nullable=False)
    seat = db.Column(db.PickleType, doc='座位号(逗号分隔)', nullable=False)
    username = db.Column(db.String(32), db.ForeignKey('users.id'), nullable=False)
    createTime = db.Column(db.DateTime, doc='创建时间', nullable=False)
    status = db.Column(db.Boolean, doc='订单状态(0:未支付,1:已支付)', default=0, nullable=False)
    couponId = db.Column(db.String(32), db.ForeignKey('coupons.id'))
    payPrice = db.Column(db.Float, doc='实际支付', nullable=False)
    totalPrice = db.Column(db.Float, doc='原价', nullable=False)

    def __repr__(self):
        screen = Screen.query.get(self.screenId)
        movie = Movie.query.get(screen.movieId)
        res = {
            'id': self.id,
            'hallNum': screen.hallNum,
            'seat': self.seat,
            'name': movie.name,
            'time': screen.time.strftime('%Y-%m-%d %X')
        }
        return '{name} {time}放映 {hallNum}号厅{seat}座 订单{id}'.format(**res)

    def __json__(self):
        return {
            'id': self.id,
            'screenId': self.screenId,
            'createTime': time.mktime(self.createTime.timetuple()) * 1000,
            'username': self.username,
            'seat': self.seat,
            'status': self.status,
            'couponId': self.couponId,
            'payPrice': self.payPrice,
            'totalPrice': self.totalPrice
        }


class Coupon(db.Model):
    """优惠券"""
    __tablename__ = 'coupons'
    __table_args__ = {'mysql_engine': 'InnoDB'}  # 支持事务操作和外键

    id = db.Column(db.String(32), primary_key=True)
    discount = db.Column(db.SmallInteger, doc='折扣', nullable=False, default=5)
    condition = db.Column(db.SmallInteger, doc='满多少元可用', default=30, nullable=False)
    username = db.Column(db.String(32), db.ForeignKey('users.id'), nullable=False, doc='手机号码')
    expiredTime = db.Column(db.Date, doc='过期时间', nullable=False)
    status = db.Column(db.Boolean, doc='状态(0:未使用,1:已使用)', default=0, nullable=False)

    def __json__(self):
        return {
            'id': self.id,
            'discount': self.discount,
            'condition': self.condition,
            'expiredTime': time.mktime(self.expiredTime.timetuple()) * 1000,
            'status': self.status
        }


class Favorite(db.Model):
    """收藏"""
    __tablename__ = 'favorites'
    __table_args__ = {'mysql_engine': 'InnoDB'}  # 支持事务操作和外键

    id = db.Column(db.String(32), primary_key=True)
    username = db.Column(db.String(32), db.ForeignKey('users.id'), nullable=False, doc='手机号码')
    movieId = db.Column(db.String(32), db.ForeignKey('movies.id'), nullable=False)

    def __json__(self):
        return {
            'id': self.id,
            'username': self.username,
            'movie': Movie.query.get(self.movieId).__json__()
        }


class Comment(db.Model):
    """评论"""
    __tablename__ = 'comments'
    __table_args__ = {'mysql_engine': 'InnoDB'}  # 支持事务操作和外键

    id = db.Column(db.String(32), primary_key=True)
    username = db.Column(db.String(32), db.ForeignKey('users.id'), nullable=False, doc='手机号码')
    movieId = db.Column(db.String(32), db.ForeignKey('movies.id'), nullable=False)
    content = db.Column(db.Text, nullable=False, doc='评论内容')
    rating = db.Column(db.SmallInteger, nullable=False, doc='电影评分')

    def __repr__(self):
        return self.id

    def __json__(self):
        return {
            'id': self.id,
            'username': self.username,
            'content': self.content,
            'rating': self.rating
        }
