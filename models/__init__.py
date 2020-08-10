from datetime import datetime
from pytz import timezone
from os import environ
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv, find_dotenv
# from pathlib import Path
# from sqlalchemy import create_engine
# import pandas as pd

from db import db
from common.random_rainbow import make_random_gradient

load_dotenv(find_dotenv())
SQLALCHEMY_DATABASE_URI = environ.get("SQLALCHEMY_DATABASE_URI")

project_files = db.Table(
    'project_files',
    db.Column(
        'project_id',
        db.Integer,
        db.ForeignKey('projects.uid'),
        primary_key=True
    ),
    db.Column(
        'file_id',
        db.Integer,
        db.ForeignKey('filedata.uid'),
        primary_key=True
    )
)


class User(UserMixin, db.Model):
    """User account model."""

    __tablename__ = 'app_users'

    id = db.Column(
        db.Integer,
        primary_key=True
    )
    name = db.Column(
        db.String(100),
        nullable=False,
        unique=True
    )
    email = db.Column(
        db.String(40),
        unique=True,
        nullable=False
    )
    password = db.Column(
        db.String(200),
        primary_key=False,
        unique=False,
        nullable=False
    )
    website = db.Column(
        db.String(60),
        index=False,
        unique=False,
        nullable=True
    )
    created_on = db.Column(
        db.DateTime,
        index=False,
        unique=False,
        nullable=True,
        default=datetime.now(timezone("US/Eastern")),
    )
    last_login = db.Column(
        db.DateTime,
        index=False,
        unique=False,
        nullable=True
    )
    background = db.Column(
        db.Text,
        nullable=False,
        unique=False,
        default=make_random_gradient()
    )

    def set_password(self, password):
        """Create hashed password."""
        self.password = generate_password_hash(
            password,
            method='sha256'
        )

    def check_password(self, password):
        """Check hashed password."""
        return check_password_hash(self.password, password)

    def track_login(self):
        """Set the last_login value to now """
        self.last_login = datetime.now(timezone("US/Eastern"))

    def __repr__(self):
        return '<User {}>'.format(self.username)


class Project(db.Model):

    __tablename__ = 'projects'

    uid = db.Column(
        db.Integer,
        primary_key=True
    )
    name = db.Column(
        db.String(50),
        nullable=False,
        unique=True
    )
    description = db.Column(
        db.Text,
        nullable=False,
        unique=False
    )
    created_by = db.Column(
        db.Integer,
        db.ForeignKey("app_users.id"),
        nullable=False
    )
    background = db.Column(
        db.Text,
        nullable=False,
        unique=False,
        default=make_random_gradient()
    )
    tmc_files = db.relationship(
        'TMCFile',
        secondary=project_files,
        lazy='subquery',
        backref=db.backref(__tablename__, lazy=True)
    )

    def num_files(self):
        return len(self.tmc_files)

    def created_by_user(self):
        return User.query.filter_by(id=self.created_by).first()


class TMCFile(db.Model):

    __tablename__ = 'filedata'

    uid = db.Column(
        db.Integer,
        primary_key=True
    )
    filename = db.Column(
        db.Text,
        nullable=False,
        unique=False
    )
    title = db.Column(
        db.Text,
        nullable=True,
        unique=False
    )
    # project_id = db.Column(
    #     db.Integer,
    #     db.ForeignKey("projects.uid"),
    #     nullable=False
    # )
    model_id = db.Column(
        db.Integer,
        nullable=True
    )
    uploaded_by = db.Column(
        db.Integer,
        db.ForeignKey("app_users.id"),
        nullable=False
    )
    lat = db.Column(
        db.Text,
        nullable=True,
        unique=False,
        default=39.852413
    )
    lng = db.Column(
        db.Text,
        nullable=True,
        unique=False,
        default=-75.264969
    )
    data_date = db.Column(
        db.DateTime,
        index=False,
        unique=False,
        nullable=True
    )
    modes = db.Column(
        db.Text,
        nullable=True,
        unique=False
    )
    legs = db.Column(
        db.Text,
        nullable=True,
        unique=False
    )
    movements = db.Column(
        db.Text,
        nullable=True,
        unique=False
    )
    am_peak_start = db.Column(
        db.DateTime,
        index=False,
        unique=False,
        nullable=True
    )
    pm_peak_start = db.Column(
        db.DateTime,
        index=False,
        unique=False,
        nullable=True
    )
    am_volume = db.Column(
        db.Float,
        index=False,
        unique=False,
        nullable=True
    )
    pm_volume = db.Column(
        db.Float,
        index=False,
        unique=False,
        nullable=True
    )
    count_start_time = db.Column(
        db.DateTime,
        nullable=True,
        unique=False
    )
    count_end_time = db.Column(
        db.DateTime,
        nullable=True,
        unique=False
    )

    project_ids = db.relationship(
        'Project',
        secondary=project_files,
        lazy='subquery',
        backref=db.backref(__tablename__, lazy=True)
    )

    def pid_list(self):
        return [p.uid for p in self.project_ids]

    def num_projects(self):
        num = len(self.project_ids)
        return num
        # if num == 1:
        #     txt = "project"
        # else:
        #     txt = "projects"
        # return f"{num} {txt}"

    def name(self):
        if self.title:
            return self.title
        else:
            return self.filename

    def upload_user(self):
        return User.query.filter_by(id=self.uploaded_by).first()
