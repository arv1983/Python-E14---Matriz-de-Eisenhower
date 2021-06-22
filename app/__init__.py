from flask import request, jsonify, render_template, Flask, Blueprint
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from flask_sqlalchemy import SQLAlchemy
from environs import Env
import psycopg2
from sqlalchemy.sql.sqltypes import Text 
from sqlalchemy.orm import backref, relationship

app = Flask(__name__)
env = Env()
env.read_env()

db = SQLAlchemy()

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://anderson:1234@localhost:5432/e14'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JSON_SORT_KEYS"] = False

class productCategory(db.Model):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(String, nullable=False)


class productEisenhowers(db.Model):
    __tablename__ = "eisenhowers"
    id = Column(Integer, primary_key=True)
    type = Column(String(100))

class productTask(db.Model):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=False)
    duration = Column(Integer)
    importance = Column(Integer)
    urgency = Column(Integer)
    eisenhower_id = Column(Integer, ForeignKey("eisenhowers.id"))
    

class productTaskCategory(db.Model):    
    __tablename__ = "tasks_categories"
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)


    



db.init_app(app)
with app.app_context():
    db.create_all()
    


def prioridade(i, u):
    Eisenhowers = (i * 2) + u
    # get_Eisenhowers = productEisenhowers().query.all()
    if Eisenhowers == 3:
        Eisenhowers = 1
    elif Eisenhowers == 4:
        Eisenhowers = 2
    elif Eisenhowers == 5:
        Eisenhowers = 3
    else:
        Eisenhowers = 4
    return Eisenhowers

    
@app.route('/', methods=["GET"])
def get_all():
    task = productTaskCategory().query.all()
    array = []
    for data in task:
        cat = productCategory().query.filter_by(id=data.category_id).first()
        pro = productTask().query.filter_by(id=data.task_id).first()
        
        array.append({"category": {
            "name": cat.name,
            "description": cat.description,
            "task": [
                {
             "name": pro.name,
             "description": pro.description,
             "priority": productEisenhowers().query.filter_by(id=pro.eisenhower_id).first().type
                }
            ]
        }

        })
        

    return jsonify(array)


@app.route('/category', methods=["POST"])
def get_create():
    data = request.get_json()

    
    record_db = productCategory(**data)
    db.session.add(record_db)
    db.session.commit()
    
    return data,201

@app.route('/task', methods=["POST"])
def task():
    data = request.get_json()
    
    

    
    u = int(data.get('urgency'))
    i = int(data.get('importance'))

    if u > 2 or i > 2:
        return {"error": {
            "valid options": {
                "importance": [
                    1,
                    2
                    ],
            "urgency": [
                1,
                2
                ]
            },
            "receieved options":{"importance": i,
            "urgency": u
            }}
        }
        

    
    
    record = {**data}
    record['eisenhower_id'] = prioridade(i, u)

    record_db = productTask(**record)
    db.session.add(record_db)
    db.session.commit()
    
    
    
    eisenhower_classification = productEisenhowers().query.filter_by(id=record['eisenhower_id']).first().type
    
    

    return {'name': record_db.name,
    'description': record_db.description,
    'duration': record_db.duration,
    'eisenhower_classification': eisenhower_classification
    }


@app.route('/task_category', methods=["POST"])
def task_category():
    data = request.get_json()
    
    
    category = data.get('category_name')
    task = data.get('task_name')
    category_id = productCategory.query.filter_by(name=category).first()
    task_id = productTask.query.filter_by(name=task).first()

    record = {'task_id': int(task_id.id),
    'category_id': int(category_id.id)}

    Eisenhowers = prioridade(task_id.importance, task_id.urgency)

    record_db = productTaskCategory(**record)
    db.session.add(record_db)
    db.session.commit()    
    eisenhower_classification = productEisenhowers().query.filter_by(id=Eisenhowers).first().type
    return {"task": task_id.name,
    "category": category_id.name,
    "eisenhower_classification": eisenhower_classification}
