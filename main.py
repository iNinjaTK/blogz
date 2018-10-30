from flask import Flask, request, redirect, render_template, session, flash, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:password@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = "secretkey"

class Entry(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    blogtitle = db.Column(db.String(120))
    blogcontent = db.Column(db.String(400))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, blogtitle, blogcontent, owner):
        self.blogtitle = blogtitle
        self.blogcontent = blogcontent
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Entry', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'blog', 'index', 'signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/', methods=['GET'])
def index():
    # TODO - Display a list of all users
    if request.method == 'GET' and request.args.get('id'):
        owner = User.query.filter_by(id=request.args.get('id')).first()
        entries = Entry.query.filter_by(owner=owner).all()
        return render_template('authorpage.html',
        title=owner,
        entries=entries,
        owner=owner)
    if request.method == 'GET' and request.args.get('owner'):
        owner = User.query.filter_by(username=request.args.get('owner')).first()
        entries = Entry.query.filter_by(owner_id=owner.id).all()
        return render_template('authorpage.html',
        title='Blog Posts',
        entries=entries)
    else:
        users = User.query.all()
        return render_template('index.html',
        title="Blog Users!",
        users=users)
    

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:

            # TODO - "remember" that the user has logged in

            session['username'] = username
            flash("Logged In")
            return redirect('/newpost')

        else:

            # TODO - explain why login failed

            flash("User password incorrect, or user does not exist", 'error')

    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify_password = request.form['verify_password']
        username_error = ''
        password_error = ''
        verify_password_error = ''
        
        # TODO - validate user's data

        existing_user = User.query.filter_by(username=username).first()

        if not existing_user:

            # TODO - confirm if any fields (username, password, verify_password) are empty
            
            if username == '':
                username_error = "Blank username is not valid."
            if password == '':
                password_error = "Blank password is not valid."
                password = ''
            if verify_password == '':
                verify_password_error = "Blank verification is not valid."
                verify_password = ''

            # TODO - confirm if username is not valid
            
            if " " in username:
                username_error = "Username cannot have blank space(s)."
            elif len(username) < 3 and not len(username) == 0:
                username_error = "Username cannot have less than three (3) characters."
            elif len(username) > 20:
                username_error = "Username cannot have more than twenty (20) characters."

            # TODO - confirm if password matches verify_password
            
            if not password == verify_password:
                password_error = "Passwords don't match."
                password = ''
                verify_password = ''

            if not username_error and not password_error and not verify_password_error:
                # successful new user
                new_user = User(username, password)
                db.session.add(new_user)
                db.session.commit()
 
                # TODO - "remember" the user

                session['username'] = username
                return redirect("/newpost")

            else:
                return render_template('signup.html', 
                username_error=username_error, 
                username=username, 
                password_error=password_error, 
                password=password, 
                verify_password_error=verify_password_error, 
                verify_password=verify_password)

        else:

            # TODO - if user already exists

            username_error = "username already exists"
            return render_template('signup.html', 
                username_error=username_error,
                username=username)

    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/')

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    if request.method == 'POST':
        blogtitle = request.form['blogtitle']
        blogcontent = request.form['blogcontent']
        owner = User.query.filter_by(username=session['username']).first()
        blogtitle_error = ''
        blogcontent_error = ''

        # TODO - validate user's data

        if blogtitle == '':
            blogtitle_error = 'Please fill in the title'
        if blogcontent == '':
            blogcontent_error = 'Please fill in the body'

        if not blogtitle_error and not blogcontent_error:
            new_entry = Entry(blogtitle, blogcontent, owner)
            db.session.add(new_entry)
            db.session.commit()
            return render_template('postpage.html',
            title=new_entry.blogtitle,
            content=new_entry.blogcontent,
            owner=owner.username)
        else:
            return render_template('newpost.html',
            blogtitle=blogtitle,
            blogcontent=blogcontent,
            blogtitle_error=blogtitle_error,
            blogcontent_error=blogcontent_error)
    return render_template('newpost.html')

@app.route('/blog', methods=['GET'])
def blog():
    
    if request.method == 'GET' and request.args.get('id'):
        entry = Entry.query.filter_by(id=request.args.get('id')).first()
        return render_template('postpage.html',
        title=entry.blogtitle,
        content=entry.blogcontent,
        owner=entry.owner.username)
    if request.method == 'GET' and request.args.get('owner'):
        owner = User.query.filter_by(username=request.args.get('owner')).first()
        entries = Entry.query.filter_by(owner_id=owner.id).all()
        return render_template('authorpage.html',
        title='Blog Posts',
        entries=entries)
    else:
        entries = Entry.query.all()
        return render_template('blog.html',
        title="Build a Blog",
        entries=entries)

if __name__ == '__main__':
    app.run()