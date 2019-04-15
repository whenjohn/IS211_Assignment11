import re
from flask import request, redirect
from flask import Flask, render_template
from flask import session



import sqlite3 as lite

app = Flask(__name__)

# Set the secret key to some random bytes. Keep this really secret!
app.secret_key = b'_5#yL"@F4Q8z\n\xec]/'

priority_mapping = {
    1:"Low",
    2:"Medium",
    3:"High"
}



class ValidationError(Exception):
    """ Object raises error"""
    pass



@app.route('/')
def index():
    rows = getTodo()
    #print rows
    if 'error_msg' in session:
        error_msg = session.pop('error_msg', None)
    else:
        error_msg = None
    return render_template('index.html', todo=rows, priority_mapping=priority_mapping, error_msg=error_msg )

def getTodo():
    is_active = 1
    con = lite.connect('todo_db')
    con.row_factory = lite.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM tbl_todo WHERE active=? ORDER BY priority DESC;", (is_active,))
    return cur.fetchall()


@app.route('/submit', methods = ['POST'])
def create():
    priority = request.form['priority']
    task = request.form['task']
    email = request.form['email']
    print(priority, task, email)

    try:
        validateTodo(email, priority)
    except Exception as e:
        #session['error_msg'] = "Error"
        session['error_msg'] = "Error: {}".format(e.message)
        #print "Error: {}".format(e.message)
    else:
        # insert data
        addTodo(task, email, priority)

    return redirect('/')

def validateTodo(email, pri):
    if not isinstance(int(pri), int):
        raise Exception("Invalid Priority")
    if not re.match("^\w+@[a-zA-Z_]+?\.[a-zA-Z]{2,3}$", email):
        raise Exception("Invalid Email")


def addTodo(task, email, pri):
    active = 1
    todo = ((task, email, pri, active),)
    con = lite.connect('todo_db')
    cur = con.cursor()
    cur.executemany("INSERT INTO tbl_todo (task, email, priority, active) VALUES( ?, ?, ?, ?)", todo)
    con.commit()


@app.route('/delete')
def delete():
    set_clear = 0
    todo_id = request.args.get('id')
    print "got id", todo_id
    con = lite.connect('todo_db')
    cur = con.cursor()
    cur.execute("UPDATE tbl_todo SET active = ? WHERE todo_id = ?", (set_clear, todo_id))
    con.commit()
    return redirect('/')

@app.route('/clear_all')
def clear_all():
    con = lite.connect('todo_db')
    cur = con.cursor()
    cur.execute("DELETE FROM tbl_todo")
    con.commit()
    return redirect('/')

if __name__ == "__main__":
    app.run()
