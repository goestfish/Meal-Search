from flask import Flask, request, render_template, send_from_directory, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from elasticsearch import Elasticsearch
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'  # 用于闪现消息

db = SQLAlchemy(app)
es = Elasticsearch(
    [{'host': 'localhost', 'port': 9200, 'scheme': 'http'}]
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    security_question = db.Column(db.String(200), nullable=False)
    security_answer_hash = db.Column(db.String(120), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def set_security_answer(self, answer):
        self.security_answer_hash = generate_password_hash(answer)

    def check_security_answer(self, answer):
        return check_password_hash(self.security_answer_hash, answer)

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user:
            if user.check_password(password):
                # session['username'] = username  # 设置会话
                return render_template('search.html')
            else:
                flash('Incorrect password. Please try again.')
        else:
            flash('Username not registered. Please sign up.')
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        security_question = request.form['security_question']
        security_answer = request.form['security_answer']
        user = User.query.filter_by(username=username).first()
        if user:
            flash('Username already exists. Please choose a different one.')
            return render_template('register.html', username=username, security_question=security_question, security_answer=security_answer)  # 保留用户输入
        else:
            new_user = User(username=username, security_question=security_question)
            new_user.set_password(password)
            new_user.set_security_answer(security_answer)
            try:
                db.session.add(new_user)
                db.session.commit()
                flash('Registration successful. Please log in.')
                return redirect(url_for('login'))
            except:
                db.session.rollback()
                flash('Registration failed. Please try again.')
    return render_template('register.html')



@app.route('/logout')
def logout():
    return redirect(url_for('login'))

@app.route('/search', methods=['GET'])
def search_recipe():
    query = request.args.get('q')
    response = es.search(
        index="recipes",
        body={
            "query": {
                "match": {
                    "strMeal": query
                }
            }
        }
    )
    hits = response['hits']['hits']
    return render_template('search_results.html', hits=hits, query=query)

@app.route('/meals', methods=['GET'])
def list_meals():
    response = es.search(
        index="recipes",
        body={
            "query": {
                "match_all": {}
            },
            "size": 1000
        }
    )
    hits = response['hits']['hits']
    meals = [hit['_source']['strMeal'] for hit in hits]
    return jsonify(meals)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static', 'image'),
                               'favicon.png', mimetype='image/png')

@app.route('/users')
def users():
    users = User.query.all()
    return render_template('users.html', users=users)

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        if 'username' in request.form and 'security_answer' not in request.form:
            username = request.form['username']
            user = User.query.filter_by(username=username).first()
            if user:
                return render_template('forgot_password_step2.html', username=username, security_question=user.security_question)
            else:
                flash('Username not found. Please try again.')
                return render_template('forgot_password.html')
        elif 'security_answer' in request.form:
            username = request.form['username']
            security_answer = request.form['security_answer']
            new_password = request.form['new_password']
            user = User.query.filter_by(username=username).first()
            if user and user.check_security_answer(security_answer):
                user.set_password(new_password)
                db.session.commit()
                flash('Password reset successful. Please log in with your new password.')
                return redirect(url_for('login'))
            else:
                flash('Incorrect answer to security question. Please try again.')
                return render_template('forgot_password_step2.html', username=username, security_question=user.security_question)
    return render_template('forgot_password.html')





if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # 创建数据库和表
    app.run(debug=True)
