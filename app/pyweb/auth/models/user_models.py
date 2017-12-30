from flask_login.mixins import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login_manager
from app.pyweb.common.db_common import DBCommon
from app.pyweb.common.log_common import LogCommon
from app.pyweb.common.time_common import Time_Helper


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(128), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    confirmed = db.Column(db.Boolean, default=False)
    create_time = db.Column(db.DateTime, default=Time_Helper().get_utc())
    phone_number = db.Column(db.String(20), unique=True, index=True)
    last_login_time = db.Column(db.DateTime)
    last_login_place = db.Column(db.String(128))

    def __repr__(self):
        return 'email:%s,username:%s,confirmed:%s' % (self.email, self.username, self.confirmed)

    # password hash set
    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def save(self, user):
        db.session.add(user)
        db.session.commit()

    def delete(self, **kwargs):
        str_filters = DBCommon.dictToQueryStr(kwargs)
        User.query.filter(str_filters).first().delete()

    def get_user(self,**kwargs):
        str_filters = DBCommon.dictToQueryStr(kwargs)
        try:
            return User.query.filter(str_filters).first()
        except Exception as e:
            LogCommon.print_log_error("get_user:get user failed:%s" % e)
            return None

    def get_users(self,**kwargs):
        str_filters = DBCommon.dictToQueryStr(kwargs)
        try:
            return User.query.filter(str_filters)
        except Exception as e:
            LogCommon.print_log_error("get_users:get users failed:%s" % e)
            return None

    def confirm(self, user):
        user.confirmed = True
        db.session.add(user)
        db.session.commit()
        return True

    def reset_password(self,newPass):
        if newPass is None:
            return False
        self.password = newPass
        db.session.add(self)
        return True

    def change_email(self,new_email):
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        # self.avatar_hash = _hashlib.md5(
        #     self.email.encode('utf-8')).hexdigest()
        db.session.add(self)
        return True

    @login_manager.user_loader
    def load_user(userid):
        return User.query.filter_by(id=userid).first()


class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return self.name
