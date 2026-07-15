from flask import Flask , render_template  , redirect , request , jsonify
from flask_jwt_extended import create_access_token , set_access_cookies , JWTManager, verify_jwt_in_request, unset_access_cookies , get_jwt_identity
import sqlite3
app  =  Flask(__name__)

app.config["JWT_SECRET_KEY"] = "your_secret_key"

app.config["JWT_TOKEN_LOCATION"] = ["cookies"]

app.config["JWT_COOKIE_SECURE"] = False

app.config["JWT_COOKIE_CSRF_PROTECT"] = False

jwt = JWTManager(app)

@app.route("/")
def user_login():

    try:
        verify_jwt_in_request()

        username = get_jwt_identity()

        connection = sqlite3.connect("admin.db")
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()

        cursor.execute(" SELECT * FROM users WHERE username=?",(username,))
        
        user = dict(cursor.fetchone())
        connection.close()

        return render_template("user_dashboard.html",user=user)

    except Exception as e:
        print(e)

        return render_template("user_login.html")

@app.route("/api/login", methods=["POST"])
def check_user():

    data = request.get_json()

    username = data["username"]
    password = data["password"]

    connection = sqlite3.connect("admin.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM users
        WHERE username=? AND password=?
    """, (username, password))

    row = cursor.fetchone()

    connection.close()

    if row:

        user = dict(row)

        access_token = create_access_token(
            identity=user["username"]
        )
        
        response = jsonify({
            "message": "Login successful"
        })

        set_access_cookies(response, access_token)

        return response

    return jsonify({
        "message": "Invalid Username or Password"
    }), 401


@app.route("/user_logout")
def user_logout():

    response = redirect("/")

    unset_access_cookies(response)

    return response


@app.route("/profile_update/<int:id>")
def profile_update(id):
    
    connection = sqlite3.connect("admin.db")
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute("""
        SELECT id , username, email, bio
        FROM users WHERE id=?
    """,(id,))

    user = dict(cursor.fetchone())
    connection.close()

    return render_template("profile_update.html",user=user)

@app.route('/admin')
def admin_home():
    try:
        verify_jwt_in_request()

        return render_template("admin_home.html")

    except Exception:

        return redirect("/admin_login")
    
@app.route("/api/users")
def list_users():

    connection = sqlite3.connect("admin.db")
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, username, email, bio
        FROM users
    """)

    users = [dict(user) for user in cursor.fetchall()]

    connection.close()

    return jsonify(users)

@app.route('/admin_login',methods= ["GET","POST"])
def admin_login():

    if request.method == "GET":

        return render_template("admin_login.html")
    
    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        connection = sqlite3.connect("admin.db")
        cursour = connection.cursor()

        cursour.execute("SELECT * FROM admin WHERE username=? AND password=?", (username,password))
        admin =  cursour.fetchone()
        connection.close()

    if admin:
        access_token = create_access_token(identity=username)

        response = redirect("/admin")
        set_access_cookies(response,access_token)

        return response
    
    return render_template("/admin_login.html",error="Invalid Username or Password")

@app.route('/admin_signup', methods= ["GET","POST"])
def admin_signup():

    if request.method == "GET":
        return render_template("admin_signup.html")

    if request.method == "POST":
        fullname = request.form["fullname"]
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        connection = sqlite3.connect("admin.db")
        cursor = connection.cursor()

        cursor.execute(""" 
            INSERT INTO admin(fullname, username, email, password)
            VALUES(?, ?, ?, ?)
        """,(fullname, username, email, password))
        connection.commit()
        connection.close()

        return redirect("/admin_login")
    
@app.route("/admin_logout")
def admin_logout():

    response = redirect("/admin")

    unset_access_cookies(response)

    return response

@app.route("/create_user")
def create_user():
    return render_template("create_user.html")

@app.route("/api/create_user", methods = ["POST"])
def create_user_account():
    if request.method == "POST":

        fullname = request.form["fullname"]
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        bio = request.form["bio"]

        connection = sqlite3.connect("admin.db")
        cursor = connection.cursor()

        try:
            cursor.execute(""" 
                INSERT INTO users(fullname, username, email, password, bio)
                VALUES(?, ?, ?, ?, ?)
            """,(fullname, username, email, password, bio))
            
            connection.commit()
            connection.close()

            return render_template("create_user.html",message="User create successfully")
        
        except sqlite3.IntegrityError:
            connection.close()
            return render_template("create_user.html",error="Username or email already exists.")
            
@app.route("/api/user/<int:id>", methods = ["DELETE"])
def delete_user(id):

    if request.method == "DELETE":
        connection = sqlite3.connect("admin.db")
        cursor = connection.cursor()

        cursor.execute(
            "DELETE FROM users WHERE id=?",
            (id,)
        )

        connection.commit()
        connection.close()

        return jsonify({
            "message" : "User delete successfully"
        })

@app.route("/api/user/<int:id>", methods = ["PUT"])
def update_user(id):

    if request.method == "PUT":
        data = request.get_json()

        username = data["username"]
        email = data["email"]
        password = data["password"]
        bio = data["bio"]

        connection = sqlite3.connect("admin.db")
        cursor = connection.cursor()

        cursor.execute( """
            UPDATE users
            SET username = ? , email = ? , password = ? , bio = ?
            WHERE id = ?
            """,(username, email, password, bio, id)
        )

        connection.commit()
        connection.close()

        return jsonify({
            "message" : "User Update successfully. "
        })

@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

if __name__ == '__main__':
    app.run(debug=True)