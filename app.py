from flask import Flask, render_template, request, redirect, url_for, session
import re
import psycopg2

#establishing the connection
conn = psycopg2.connect(
   database="bookstore", user='root', password='password', host='localhost', port= '5432'
)



app = Flask(__name__)

app.secret_key = 'your secret key'

@app.route('/')
def main():
    return redirect('/pythonlogin')

@app.route('/pythonlogin/', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        # Check if account exists using MySQL
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password,))
        # Fetch one record and return result
        account = cursor.fetchone()
        # If account exists in accounts table in out database
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account[0]
            session['username'] = account[1]
            # Redirect to home page
            if account[1] == 'customer':
                return redirect('/useradmin')
            else :
                return redirect(url_for('profile'))
            #return 'Logged in successfully!'
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
    # Show the login form with message (if any)
    return render_template('index.html', msg=msg)

# http://localhost:5000/pythinlogin/home - this will be the home page, only accessible for loggedin users
@app.route('/pythonlogin/home')
def home():
    return redirect('/useradmin')
    '''# Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('home.html', username=session['username'])
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))'''

# http://localhost:5000/pythinlogin/profile - this will be the profile page, only accessible for loggedin users
@app.route('/pythonlogin/profile')
def profile():
    # Check if user is loggedin
    if  session['loggedin']:
        # We need all the account info for the user so we can display it on the profile page
        print('hello')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM holdings WHERE golden_id = %s', (session['id'],))
        accounts = cursor.fetchall()
        print(len(accounts))
        # Show the profile page with account info
        return render_template('profile.html',len = len(accounts), accounts=accounts)
    # User is not loggedin redirect to login page
    return redirect(url_for('login'))

@app.route('/info/<id>')
def info(id):
    print(id)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM holdings WHERE golden_id = %s', (id,))
    user_info = cursor.fetchall()
    print(len(user_info))
    return render_template('userDetail.html',len = len(user_info), accounts=user_info)


# http://localhost:5000/python/logout - this will be the logout page
@app.route('/pythonlogin/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('login'))






# http://localhost:5000/pythinlogin/register - this will be the registration page, we need to use both GET and POST requests
@app.route('/pythonlogin/register', methods=['GET', 'POST'])
def register():
    # Output message if something goes wrong...
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html', msg=msg)





@app.route('/useradmin')
def useradmin():
    cursor = conn.cursor()
    cursor.execute('select * from match_results')
    #cursor.execute("SELECT * FROM employee")
    employee = cursor.fetchall()
    return render_template('useradmin.html', employee=employee)
 
@app.route('/updateemployee', methods=['POST'])
def updateemployee():
        pk = request.form['pk']
        name = request.form['name']
        value = request.form['value']
        cursor = conn.cursor()
        if name == 'name':
           cursor.execute("UPDATE match_results SET name = %s WHERE id = %s ", (value, pk))
        elif name == 'email':
           cursor.execute("UPDATE match_results SET email = %s WHERE id = %s ", (value, pk))
        elif name == 'phone':
           cursor.execute("UPDATE match_results SET is_same = %s WHERE id = %s ", (value, pk))
        conn.commit()
        cursor.close()
        return redirect('/useradmin')
        return json.dumps({'status':'OK'})

if __name__ == '__main__':
    app.run(debug=True)