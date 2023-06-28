from flask import (
    Flask, request, render_template, session, flash, redirect, url_for, jsonify
)
import psycopg2

from db import db_connection


app = Flask(__name__)
app.secret_key = 'THISISMYSECRETKEY'  # create the unique one for yourself


@app.route('/login', methods=['GET', 'POST'])
def login():
    """ function to show and process login page """
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = db_connection()
        cur = conn.cursor()
        sql = """
            SELECT id, username
            FROM users
            WHERE username = '%s' AND password = '%s'
        """ % (username, password)
        cur.execute(sql)
        user = cur.fetchone()

        error = ''
        if user is None:
            error = 'Wrong credentials. No user found'
        else:
            session.clear()
            session['user_id'] = user[0]
            session['username'] = user[1]
            return redirect(url_for('index'))

        flash(error)
        cur.close()
        conn.close()

    return render_template('login.html')

@app.route('/logout')
def logout():
    """ function to do logout """
    session.clear()  # clear all sessions
    return redirect(url_for('login'))


@app.route('/')
def index():
    conn = db_connection()
    cur = conn.cursor()
    sql = """
        SELECT art.id, art.title, art.body
        FROM stories art
        ORDER BY art.title
    """
    cur.execute(sql)
    # [(1, "story Title 1", "Art 1 content"), (2, "Title2", "Content 2"), ...]
    stories = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('index.html', stories=stories)


@app.route('/story/create', methods=['GET', 'POST'])
def create():
    # check if user is logged in
    if not session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        data = request.get_json() or {}
        # check existence of title and body
        if data.get('title') and data.get('body'):
            title = data.get('title', '')
            body = data.get('body', '')
            user_id = session.get('user_id')

            # strip() is to remove excessive whitespaces before saving
            title = title.strip()
            body = body.strip()

            conn = db_connection()
            cur = conn.cursor()
            # insert with the user_id
            sql = """
                INSERT INTO stories (title, body, user_id) VALUES ('%s', '%s', %d)
            """ % (title, body, user_id)
            cur.execute(sql)
            conn.commit()  # commit to make sure changes are saved
            cur.close()
            conn.close()
            # an example with redirect
            return jsonify({'status': 200, 'message': 'Success', 'redirect': '/'})

        # else will be error
        return jsonify({'status': 500, 'message': 'No Data submitted'})

    return render_template('create.html')


@app.route('/story/<int:story_id>', methods=['GET'])
def read(story_id):
    # find the story with id = story_id, return not found page if error
    conn = db_connection()
    cur = conn.cursor()
    sql = """
        SELECT art.title, art.body, usr.name
        FROM stories art
        JOIN users usr ON usr.id = art.user_id
        WHERE art.id = %s
    """ % story_id
    cur.execute(sql)
    story = cur.fetchone()
    cur.close()
    conn.close()
    return render_template('detail.html', story=story)


@app.route('/story/edit/<int:story_id>', methods=['GET', 'POST'])
def edit(story_id):
    # check if user is logged in
    if not session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        conn = db_connection()
        cur = conn.cursor()
        title = request.form['title']
        body = request.form['body']
        title = title.strip()
        body = body.strip()

        sql_params = (title, body, story_id)

        sql = "UPDATE stories SET title = '%s', body = '%s' WHERE id = %s" % sql_params
        print(sql)
        cur.execute(sql)
        cur.close()
        conn.commit()
        conn.close()
        # use redirect to go to certain url. url_for function accepts the
        # function name of the URL which is function index() in this case
        return redirect(url_for('index'))

    # find the record first
    conn = db_connection()
    cur = conn.cursor()
    sql = 'SELECT id, title, body FROM stories WHERE id = %s' % story_id
    cur.execute(sql)
    story = cur.fetchone()
    cur.close()
    conn.close()

    return render_template('edit.html', story=story)


@app.route('/story/delete/<int:story_id>', methods=['GET', 'POST'])
def delete(story_id):
    # check if user is logged in
    if not session:
        return redirect(url_for('login'))

    conn = db_connection()
    cur = conn.cursor()
    sql = 'DELETE FROM stories WHERE id = %s' % story_id
    cur.execute(sql)
    cur.close()
    conn.commit()
    conn.close()
    return jsonify({'status': 200, 'redirect': '/'})

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == "POST":
        newName = request.form['registerName']
        newUsername = request.form['registerUsername']
        newPassword = request.form['registerPassword']
        
        conn = db_connection()
        cur = conn.cursor()
        sql = """
            SELECT id, username
            FROM users
            WHERE username = '%s'
        """ % (newUsername)
        cur.execute(sql)
        user = cur.fetchone()
        
        if user is None:
            conn = db_connection()
            cur1 = conn.cursor()
            sql2 = """
            INSERT INTO users (name,username,password) VALUES
            (%s,%s,%s)
            """
            cur1.execute(sql2,(newName,newUsername,newPassword))
            if len(newPassword)>=5 and newPassword.isupper():
                cur1.close()
                conn.commit()
                conn.close()
                message = "Success!"
                flash(message)
            else :
                if (len(newPassword)<5) :
                    error = "Minimal 5 characters for password!"
                    flash (error)
                if (not newPassword.isupper()):
                    error = "Minimal 1 uppercase letter !"
                    flash (error)
                
           
        else :
            error = "username is taken"
            flash (error)

    return render_template('register.html')

