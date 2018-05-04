from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:donkeykong@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'y337kGcys&zP3B'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(250))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, email, password):
        self.email = email
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'index', 'blog']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')

        
@app.route('/blog', methods=['POST', 'GET'])
def blog():
    blogs = Blog.query.all()

    users = User.query.all()
    
    return render_template('blog.html', blogs=blogs, users=users)

@app.route('/newpost', methods=['POST', 'GET'])
def n_post():
    owner = User.query.filter_by(email=session['email']).first()
    if request.method == 'POST':
        blog_name = request.form['blg_name']
        if blog_name == "":
            u_error = "You must enter a blog name"
            return render_template('newpost.html', name_error=u_error)
        blog_content = request.form['blogpost']
        if blog_content == "":
            b_error = "You must enter blog content"
            return render_template('newpost.html', blg_name=blog_name, content_error=b_error)
    
        new_blog = Blog(blog_name, blog_content, owner)
        db.session.add(new_blog)
        db.session.commit()
        
        return render_template('blogpost.html', blog=new_blog)

    else:
        return render_template('newpost.html')

@app.route('/blogpost')
def blogpost():

    blog_id = request.args.get('id')
        
    blog = Blog.query.get(blog_id)
        
    return render_template('blogpost.html', blog=blog)

@app.route('/singleUser')
def singleUser():
    user_id = request.args.get('id')
        
    user = User.query.get(user_id)

    blogs = Blog.query.filter_by(owner_id=user_id)
        
    return render_template('singleUser.html', user=user, blogs=blogs)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        u_name = request.form['username']
        p_word = request.form['password']
        p_word2 = request.form['pass_word2']
        u_error = ""
        p_error = ""
        m_error = ""

        if u_name == "":
            u_error = "The username is invalid"
            return render_template('signup.html', user_name=u_name, username_error=u_error)
        if len(u_name) < 3 or len(u_name) > 20:
            u_error = "The username must be between 3 and 20 characters"
            return render_template('signup.html',user_name=u_name, username_error=u_error)
        if " " in u_name:
            u_error = "The username cannot contain any spaces"
            return render_template('signup.html',user_name=u_name, username_error=u_error)
        if p_word == "":
            p_error = "The password is invalid"
            return render_template('signup.html', user_name=u_name, password=p_word, password_error=p_error)
        if len(p_word) < 3 or len(p_word) > 20:
            p_error = "The password must be between 3 and 20 characters"
            return render_template('signup.html', user_name=u_name, password=p_word, password_error=p_error)
        if " " in p_word:
            p_error = "The password cannot contain any spaces"
            return render_template('signup.html', user_name=u_name, password=p_word, password_error=p_error)
        if p_word != p_word2:
            m_error = "The passwords do not match"
            return render_template('signup.html', user_name=u_name, password=p_word, match_error=m_error)
    
        existing_user = User.query.filter_by(email=u_name).first()
        if not existing_user:
            new_user = User(u_name, p_word)
            db.session.add(new_user)
            db.session.commit()
            session['email'] = u_name
            return redirect('/')
        else:
            return "<h1>Duplicate user</h1>"

    return render_template('signup.html')
        

@app.route('/login', methods=['POST', 'GET'])
def login():
    uname_err = "The username or password is incorrect"

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(email=username).first()
        if user and user.password == password:
            session['email'] = username
            return redirect('/')
        else:
            return render_template('login.html', username=username, username_error=uname_err)

    return render_template('login.html')

@app.route('/')
def index():

    users = User.query.all()

    return render_template('index.html', users=users)

@app.route('/logout', methods = ['GET', 'POST'])
def logout():
    del session['email']
    return redirect('/blog')

if __name__ == '__main__':
    app.run()