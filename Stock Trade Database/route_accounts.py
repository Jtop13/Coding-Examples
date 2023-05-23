from flask import render_template
from werkzeug.security import generate_password_hash, check_password_hash


def register_route(request, session, redirect, url_for, getDb):
    if request.method == 'GET':
        # User is already logged in.  Redirect browser to the query end point.
        if session['loggedIn']:
            return redirect(url_for('home'))
        else:
            return render_template('register.html')    
    else:
        if request.method == 'POST':
            user = request.form['user']
            passwd = request.form['passwd']
            passwdmatch = request.form['passwdmatch']
            
            #check if username is empty
            if user == '':
                return render_template('register.html', error="ERROR: Must fill out username!")
            
            #check for no special characters
            if not user.isalnum():
                return render_template('register.html', error="ERROR: Username must contain only letters or numbers!")

            #check if password is empty
            if passwd == '':
                return render_template('register.html', error="ERROR: Must fill out password!")

            #check if passwords don't match
            if passwd != passwdmatch:
                return render_template('register.html', error="ERROR: Passwords do not match!")
                
            if len(passwd) < 12:
                return render_template('register.html', error="ERROR: Passwords below length 12!")

            with getDb().cursor() as cur:
                # Check if username is already in database
                query = 'SELECT user from users where username=%(usr)s;'
                vars = {'usr' : user}
                cur.execute(query, vars)
                result = cur.fetchone()
                # It's best to not leave an unneeded transaction hanging around,
                getDb().commit()
                if result != None:
                    return render_template('register.html', error="ERROR: Username already in use!")
                else:
                    hashed_password = generate_password_hash(passwd)
                    query = 'INSERT INTO users (username, password) VALUES (%s, %s)'
                    cur.execute(query, (user, hashed_password))
                    getDb().commit()
            session['createdaccount'] = "Successfully created account!"
            session['loggedIn'] = True
            session['user'] = user
            session.modified = True
            return redirect(url_for('home'))


        #return render_template('register.html')

def logout_route(session, redirect, url_for):    
    if session['loggedIn'] == True:
        session.clear()
        session.modified = True
        return redirect(url_for('home'))
    else:
        return redirect(url_for('home'))

def login_route(request, session,redirect, url_for, getDb):
    if request.method == 'GET':
        # User is already logged in.  Redirect browser to the query end point.
        if session['loggedIn']:
            return redirect(url_for('home'))
        else:
            return render_template('login.html')
    # The request is a POST.
    else:
        # Get login credentials from the form.
        user = request.form['user']
        passwd = request.form['passwd']
        
        
        # Open a cursor using a context manager.  The cursor will be closed
        # when the context is exited.  Cursors are used to interact with
        # the records returned by a query.  See the documentation for the
        # Cursor class in psycopg2 for details.
        with getDb().cursor() as cur:
            # %(usr)s is a named parameter in the query string.
            # vars is a dictionary specifying the mapping from the
            # named parameters to their values.  Constructing the query
            # in this flashion allows psycopg2 to properly escape input
            # from users, preventing SQL injection attacks.
            query = 'select password from users where username=%(usr)s;'
            vars = {'usr' : user}
            cur.execute(query, vars)
            result = cur.fetchone()
            # By default, any DB operation, even a read, opens a transaction.
            # It's best to not leave an unneeded transaction hanging around,
            # so let's commit it.
            getDb().commit()

        # If user isn't in users, result will be None.  Attempt to
        # authenticate user.
        if result != None and check_password_hash(result['password'], passwd):
            session['loggedIn'] = True
            session['user'] = user
            session.modified = True
            if session['redirectPortfolio']:
                return render_template('portfolio.html')
            else:
                return render_template('home.html', user=session['user'])
        else:
            
            return render_template('login.html', loginerror="ERROR: Username and Password do not match or Account not found")



