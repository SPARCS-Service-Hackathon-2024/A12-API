from flask import Flask
import json
from flask_sqlalchemy import SQLAlchemy

# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost/dbname'  # PostgreSQL을 사용하고자 할 때
db = SQLAlchemy()

class User(db.Model):

    __tablename__="User"

    id = db.Column(db.Integer, primary_key=True)
    userName = db.Column(db.String(80), nullable=False)
    password = db.Column(db.String(120), nullable=False)
    birthday = db.Column(db.String(100), nullable=False)
    familyName = db.Column(db.String(100), nullable=False)
    familyPassword = db.Column(db.String(100), nullable=False)
    phoneNumber = db.Column(db.String(100), nullable=False, unique=True)


class Storybook(db.Model):

    __tablename__="Storybook"

    id = db.Column(db.Integer, primary_key=True)
    familyName = db.Column(db.String(100), nullable=False)
    projectName = db.Column(db.String(100), nullable=False)
    wavUrl = db.Column(db.String(100), nullable=False)
    imageUrl = db.Column(db.String(100), nullable=False)
    text = db.Column(db.String(100), nullable=False)
    priority = db.Column(db.INTEGER, nullable=False) #프로젝트 내부 순서(우선순위)
