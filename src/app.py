import os
import click
import sqlalchemy as sa
import datetime  

from flask import Flask, current_app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime


class Base(DeclarativeBase):
  pass


db = SQLAlchemy(model_class=Base)



class User(db.Model):
    id: Mapped[int] = mapped_column(sa.Integer,primary_key=True)
    username: Mapped[str] = mapped_column(sa.String,unique=True, nullable=False)

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, username={self.username!r})"
    
class Post(db.Model):
    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True)
    title: Mapped[str] = mapped_column(sa.String, nullable=False)
    body: Mapped[str] = mapped_column(sa.String, nullable=False)
    created: Mapped[datetime] = mapped_column(sa.DateTime, server_default=sa.func.now())
    author_id: Mapped[int]= mapped_column(sa.ForeignKey('user.id'))
    def __repr__(self) -> str:
        return f"Post(id={self.id!r}, title={self.title!r}, author_id={self.author_id!r})"


@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    global db
    with current_app.app_context():
        db.create_all()
    
    click.echo('Initialized the database.')


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY_DATABASE_URI='sqlite:///dio_bank.sqlite',
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:    
        pass

    # Register cli commands
    app.cli.add_command(init_db_command)
    # Initialize extensions
    db.init_app(app)    

    from src.controllers import user
    app.register_blueprint(user.app)

    return app