from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:buildablog@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = "secretkey"

class Entry(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    blogtitle = db.Column(db.String(120))
    blogcontent = db.Column(db.String(400))

    def __init__(self, blogtitle, blogcontent):
        self.blogtitle = blogtitle
        self.blogcontent = blogcontent

@app.route('/', methods=['GET'])
def index():
    return redirect('/blog')

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    if request.method == 'POST':
        blogtitle = request.form['blogtitle']
        blogcontent = request.form['blogcontent']
        blogtitle_error = ''
        blogcontent_error = ''

        # TODO - validate user's data

        if blogtitle == '':
            blogtitle_error = 'Please fill in the title'
        if blogcontent == '':
            blogcontent_error = 'Please fill in the body'

        if not blogtitle_error and not blogcontent_error:
            new_entry = Entry(blogtitle, blogcontent)
            db.session.add(new_entry)
            db.session.commit()
            return render_template('postpage.html',
            title=new_entry.blogtitle,
            content=new_entry.blogcontent)
        else:
            return render_template('newpost.html',
            title='Add a Blog',
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
        content=entry.blogcontent)
    else:
        entries = Entry.query.all()
        return render_template('blog.html',
        title="Build a Blog",
        entries=entries)

if __name__ == '__main__':
    app.run()