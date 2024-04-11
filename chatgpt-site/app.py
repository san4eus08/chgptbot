from flask import Flask, request, render_template, redirect, session
from flask_sqlalchemy import SQLAlchemy
import bcrypt

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)
app.secret_key = 'ee7bd5bf9515033ce7db761094c679cae4451d26c56731d89a58cb9ea04364c166be82f60537d3d7acf70be3ac9d2c868c5f0638e6b5de468b3c8f0aae25387fd27b29c15a31b57ff37ab2d2554803bd3f0b94daa182396d839b3ee0dbc8077a5fa543404b25ef4933547d616f49d101d19a500b918e3a7964603f6d1c7670deb5cd34c3ad85d404dd3ce961e517157bb728aa67d7a1de7e7d02c21676a2439e73002811468f1197b13fddb78e96218e094e86f3b664af0cbcc6cc7a345defb93ac082c7af949f91a161b6423eeea452cce25736fd8b9e8d817bb82420f3f8bc9e4ca6ccadb62593362a8dafd9e29508f6a2c5d2741b6888b5559fcdca6cffab375a0bf529db66e2b20ec46abe491a214d8a2846693e2339c23688fdb0240bf22b6cba4f6afb3fdd50bb4327c0c20db9d8b15163831accf6f469d31b62ab21bb69ccfab8e7fa6311e2835902d0152a7f1a8a1ff04541d1766d60ef749b7b31a164189b2fff61e65cf1b8d6229e57448e621e13af9f49be68d9057ff3e088cc6d67890377f0db217e6d06c4c76a1fe878db4a9ed3f3e6a6f0c563eeeffdba52f5174a3e6881f93b12008026baf198ff13ac984e1e5f30bad247db1c4373436a092e0316bf799f946392848253de8b78871ec3581babb4eb28fc55e81af63529bf48e07cee782744bb215231762c26c60e4ce5963684a8cd20edf7f3572f1cc3e0'


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

    def __init__(self, email, password, name):
        self.name = name
        self.email = email
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_name = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    text = db.Column(db.String(100), nullable=False)

    def __init__(self, author_name, title, text):
        self.author_name = author_name
        self.title = title
        self.text = text


with app.app_context():
    db.create_all()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        new_user = User(name=name, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/login')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            session['email'] = user.email
            return redirect('/dashboard')
        else:
            return render_template('login.html', error='Invalid user')

    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    if session['email']:
        user = User.query.filter_by(email=session['email']).first()
        return render_template('dashboard.html', user=user)

    return redirect('/login')


@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect('/login')


@app.route('/create_article', methods=['GET', "POST"])
def create_article():
    if request.method == "POST":
        author_name = request.form['author_name']
        title = request.form['title']
        text = request.form['text']
        new_article = Article(author_name=author_name, title=title, text=text)
        db.session.add(new_article)
        db.session.commit()
        return redirect('/articles')

    return render_template("create_article.html")


@app.route('/articles', methods=['GET', 'POST'])
def articles():
    post = Article.query.all()
    return render_template("articles.html", articles=post)


if __name__ == '__main__':
    app.run(debug=True, port=8000)
