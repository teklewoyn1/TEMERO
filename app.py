from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import pickle
import numpy as np

popular_df = pickle.load(open('popular.pkl','rb'))
pt = pickle.load(open('pt.pkl','rb'))
books = pickle.load(open('books.pkl','rb'))
similarity_scores = pickle.load(open('similarity_scores.pkl','rb'))
 
 
app = Flask(__name__)
 
 
app.secret_key = 'your secret key'
 
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'TEKi3649$$'
app.config['MYSQL_DB'] = 'kidosapp'
 
mysql = MySQL(app)

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html',
                           book_name = list(popular_df['Book-Title'].values),
                           author=list(popular_df['Book-Author'].values),
                           image=list(popular_df['Image-URL-M'].values),
                           votes=list(popular_df['num_ratings'].values),
                           rating=list(popular_df['avg_rating'].values)
                           )
 

@app.route('/student_signinform')
def student_signinform():
    return render_template('Student/signinform.html')


@app.route('/student_signupform')
def student_signupform():
    return render_template('Student/signupform.html')


@app.route('/instructor_signinform')
def instructor_signinform():
    return render_template('Instructor/signinform.html')


@app.route('/instructor_signupform')
def instructor_signupform():
    return render_template('Instructor/signupform.html')



@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html')


@app.route('/recommend_books',methods=['post'])
def recommend():
    user_input = request.form.get('user_input')
    try:
        index = np.where(pt.index == user_input)[0][0]
    except IndexError:
        return render_template('recommend.html')
    similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:5]

    data = []
    for i in similar_items:
        item = []
        temp_df = books[books['Book-Title'] == pt.index[i[0]]]
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Author'].values))
        item.extend(list(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].values))
        
        data.append(item)

    return render_template('recommend.html', data = data)

@app.route('/student_signin', methods =['GET', 'POST'])
def student_signin():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM students WHERE username = % s AND password = % s', (username, password, ))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            msg = 'Logged in successfully !'
            return redirect(url_for('student_dashboard'))#render_template('dashboard.html', msg = msg)
        else:
            msg = 'Incorrect username / password !'
    return render_template('Student/signinform.html', msg = msg)


@app.route('/instructor_signin', methods =['GET', 'POST'])
def instructor_signin():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM instructors WHERE username = % s AND password = % s', (username, password, ))
        account = cursor.fetchone()
        if account:
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            msg = 'Logged in successfully !'
            return redirect(url_for('instructor_dashboard'))#render_template('dashboard.html', msg = msg)
        else:
            msg = 'Incorrect username / password !'
    return render_template('Instructor/signinform.html', msg = msg)

 
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('home'))
 
@app.route('/student_signup', methods =['GET', 'POST'])
def student_signup():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form :
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM students WHERE username = % s', (username, ))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists !'
            return render_template('Student/signupform.html', msg = msg)
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
            return render_template('Student/signupform.html', msg = msg)
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers !'
            return render_template('Student/signupform.html', msg = msg)
        elif not username or not password or not email:
            msg = 'Please fill out the form !'
            return render_template('Student/signupform.html', msg = msg)
        else:
            cursor.execute('INSERT INTO students VALUES (NULL, % s, % s, % s)', (username, password, email, ))
            mysql.connection.commit()
            msg1 = 'You have successfully registered !'
            return render_template('Student/signinform.html', msg1 = msg1)
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('signupform.html', msg = msg)


@app.route('/instructor_signup', methods =['GET', 'POST'])
def instructor_signup():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form :
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM instructors WHERE username = % s', (username, ))
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists !'
            return render_template('Instructor/signupform.html', msg = msg)
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address !'
            return render_template('Instructor/signupform.html', msg = msg)
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers !'
            return render_template('Instructor/signupform.html', msg = msg)
        elif not username or not password or not email:
            msg = 'Please fill out the form !'
            return render_template('Instructor/signupform.html', msg = msg)
        else:
            cursor.execute('INSERT INTO instructors VALUES (NULL, % s, % s, % s)', (username, password, email, ))
            mysql.connection.commit()
            msg1 = 'You have successfully registered !'
            return render_template('Instructor/signinform.html', msg1 = msg1)
    elif request.method == 'POST':
        msg = 'Please fill out the form !'
    return render_template('Instructor/signupform.html', msg = msg)


@app.route('/student_dashboard')
def student_dashboard():
    return render_template('Student/dashboard.html',
                           book_name = list(popular_df['Book-Title'].values),
                           author=list(popular_df['Book-Author'].values),
                           image=list(popular_df['Image-URL-M'].values),
                           votes=list(popular_df['num_ratings'].values),
                           rating=list(popular_df['avg_rating'].values)
                           )
                           


@app.route('/instructor_dashboard')
def instructor_dashboard():
    return render_template('Instructor/dashboard.html',
                           book_name = list(popular_df['Book-Title'].values),
                           author=list(popular_df['Book-Author'].values),
                           image=list(popular_df['Image-URL-M'].values),
                           votes=list(popular_df['num_ratings'].values),
                           rating=list(popular_df['avg_rating'].values)
                           )
                               

if __name__ == '__main__':
 	app.run(debug=True)
