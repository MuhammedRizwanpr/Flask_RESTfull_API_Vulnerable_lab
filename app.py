from flask import Flask , render_template  , redirect , request , jsonify
from flask_jwt_extended import create_access_token , set_access_cookies , JWTManager, verify_jwt_in_request, unset_access_cookies , get_jwt_identity ,jwt_required ,get_jwt
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
import re 
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app  =  Flask(__name__)

app.config["JWT_SECRET_KEY"] = "K9v$2Lp!8Qx#7Zm@4Ns%5Tr&1Yw*6Hd^3Bj!9Cx$8Mf@2Qa"

app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)

app.config["JWT_TOKEN_LOCATION"] = ["cookies"]

app.config["JWT_COOKIE_SECURE"] = True

app.config["JWT_COOKIE_CSRF_PROTECT"] = False

app.config["JWT_COOKIE_HTTPONLY"] = True

app.config["JWT_COOKIE_SAMESITE"] = "Lax"
#                                                               ---------------------Rate Limiter -------------
limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["100 per hour"]
)

#                                                                   -------------------  Functiions  -----------------

def validate_password(password):

    if len(password) < 8:
        return False, "Password must contain at least 8 characters"

    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter"

    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter"

    if not re.search(r"[0-9]", password):
        return False, "Password must contain at least one number"

    if not re.search(r"[!@#$%^&*]", password):
        return False, "Password must contain at least one special character"

    return True, "Password is strong"



jwt = JWTManager(app)
#                                                                    ------------------------ User -----------------
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
@limiter.limit("5 per minute")               
def check_user():

    data = request.get_json()

    if not data:
        return jsonify({
            "message": "Invalid Request"
        }), 400

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({
            "message": "Username and Password are required."
        }), 400

    connection = sqlite3.connect("admin.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM users
        WHERE username=?
    """, (username,))

    row = cursor.fetchone()

    connection.close()

    if row:

        user = dict(row)

        if check_password_hash(user["password"], password):

            access_token = create_access_token(
                identity=user["username"],
                additional_claims={
                    "role": "user"
                }
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

@app.route("/profile_update")
@jwt_required() 
def profile_update():
    
    username = get_jwt_identity()
    connection = sqlite3.connect("admin.db")
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    cursor.execute("""
        SELECT id , username, email, bio
        FROM users 
        WHERE username = ?
    """,(username,))

    user = dict(cursor.fetchone())
    connection.close()

    return render_template("profile_update.html",user=user)

    
#                                                    ---------------------------- error handler ---------------- 

@app.errorhandler(Exception)
def handle_exception(error):

    print(error)  

    return render_template(
        "error.html",
        title = "Error",
        message = "Internal Error"
    )


@app.errorhandler(405)
def mehtod_not_found(error):
    return render_template(
        "error.html",
        title = "Method Error",
        message = "This method is not allow"
    )

@jwt.unauthorized_loader
def missing_token(error):
    return render_template(
        "error.html",
        title="Token Error",
        message="Access token is missing"
    )

@jwt.expired_token_loader
def token_expired(jwt_header, jwt_payload):
    return render_template(
        "error.html",
        title="token error",
        message="Access Token is expired"    
    )

@app.errorhandler(429)
def ratelimit_handler(error):
    return render_template(
        "error.html",
        title="Rate Limit Exceeded",
        message="You have exceeded the rate limit. Please try again later."
    ), 429

#                                                          -----------------------  Admin  -------------------------

@app.route('/admin')
def admin_home():

    verify_jwt_in_request(optional=True)


    if get_jwt_identity() is None:
        return redirect("/admin_login")

    token = get_jwt()

    if token.get("role") != "admin":
        return render_template(
            "error.html",
            title="Access Denied",
            message="Only administrators can access this page"
        ), 403

    return render_template("admin_home.html",user=token.get("sub"))
    

@app.route('/admin_login', methods=["GET", "POST"])
@limiter.limit("5 per minute")
def admin_login():

    if request.method == "GET":
        
        try:
            verify_jwt_in_request()

            return redirect("/admin")
        
        except Exception:
            return render_template("admin_login.html")


    username = request.form["username"]
    password = request.form["password"]

    connection = sqlite3.connect("admin.db")
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM admin WHERE username=?",
        (username,)
    )

    admin = cursor.fetchone()

    connection.close()

    if admin:

        admin = dict(admin)

        if check_password_hash(admin["password"], password):

            access_token = create_access_token(identity=username,
                additional_claims={
                    "role": "admin"
                }
            )

            response = redirect("/admin")

            set_access_cookies(response, access_token)

            return response

    return render_template(
        "admin_login.html",
        error="Invalid Username or Password"
    )

@app.route('/admin_signup', methods= ["GET","POST"])
@limiter.limit("5 per minute")
@jwt_required()
def admin_signup():

    if request.method == "GET":

        role = get_jwt()

        if role["role"] != "admin":
            return render_template(
                "error.html",
                title="Access Denied",
                message="Only administrators can access this page"
            ), 403
        return render_template("admin_signup.html")

    if request.method == "POST":
        fullname = request.form["fullname"]
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]

        hashed_password = generate_password_hash(password)

        connection = sqlite3.connect("admin.db")
        cursor = connection.cursor()

        cursor.execute(""" 
            INSERT INTO admin(fullname, username, email, password)
            VALUES(?, ?, ?, ?)
        """,(fullname, username, email, hashed_password))
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
@limiter.limit("10 per minute")
def create_user_account():
    if request.method == "POST":

        fullname = request.form["fullname"]
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        bio = request.form["bio"]

        hashed_password = generate_password_hash(password)

        connection = sqlite3.connect("admin.db")
        cursor = connection.cursor()

        try:
            cursor.execute(""" 
                INSERT INTO users(fullname, username, email, password, bio)
                VALUES(?, ?, ?, ?, ?)
            """,(fullname, username, email, hashed_password, bio))
            
            connection.commit()
            connection.close()

            return render_template("create_user.html",message="User create successfully")
        
        except sqlite3.IntegrityError:
            connection.close()
            return render_template("create_user.html",error="Username or email already exists.")
        
@app.route("/api/users")
@limiter.limit("30 per minute")
@jwt_required()
def list_users():

    connection = sqlite3.connect("admin.db")
    connection.row_factory = sqlite3.Row

    cursor = connection.cursor()

    token = get_jwt()   

    if token["role"] != "admin":
        return jsonify({
            "message": "Access Denied"
    }), 403

    cursor.execute("""
        SELECT id, username, email, bio
        FROM users
    """)

    users = [dict(user) for user in cursor.fetchall()]

    connection.close()

    return jsonify(users)
            
@app.route("/api/user/<int:id>", methods = ["DELETE"])
@limiter.limit("10 per minute")
@jwt_required() 
def delete_user(id):

    if request.method == "DELETE":

        token = get_jwt()   

        if token["role"] != "admin":
            return jsonify({
                "message": "Access Denied"
            }), 403

        connection = sqlite3.connect("admin.db")
        cursor = connection.cursor()
        
        cursor.execute(" SELECT username FROM users WHERE id = ?",(id,))

        user = cursor.fetchone()

        if user is None:
            return jsonify({
                "message": "User is no found !"
            }), 404

        cursor.execute(
            "DELETE FROM users WHERE id = ?",
            (id,)
        )

        connection.commit()
        connection.close()

        return jsonify({
            "message" : "User delete successfully"
        })

@app.route("/api/user", methods = ["PUT"])
@limiter.limit("20 per minute")
@jwt_required()
def update_user():

    if request.method == "PUT":
        old_username = get_jwt_identity()
        data = request.get_json()

        username = data["username"]
        email = data["email"]
        password = data["password"]
        bio = data["bio"]

        hashed_password = generate_password_hash(password)
        connection = sqlite3.connect("admin.db")
        cursor = connection.cursor()

        cursor.execute( """
            UPDATE users
            SET username = ? , email = ? , password = ? , bio = ?
            WHERE username = ?
            """,(username, email, hashed_password, bio, old_username)
        )

        connection.commit()
        connection.close()

        return jsonify({
            "message" : "User Update successfully. "
        })
    
@app.route("/api/user/<int:id>", methods = ["PUT"])
@limiter.limit("20 per minute")
@jwt_required()
def admin_update_user(id):

    if request.method == "PUT":
        role = get_jwt()
        if role["role"] != "admin":
            return render_template(
                "error.html",
                title="Access Denied",
                message="Only administrators can access this page"
            ), 403
        
        data = request.get_json()

        username = data["username"]
        email = data["email"]
        password = data["password"]
        bio = data["bio"]

        hashed_password = generate_password_hash(password)
        connection = sqlite3.connect("admin.db")
        cursor = connection.cursor()

        cursor.execute( """
            UPDATE users
            SET username = ? , email = ? , password = ? , bio = ?
            WHERE id = ?
            """,(username, email, hashed_password, bio, id)
        )

        connection.commit()
        connection.close()

        return jsonify({
            "message" : "User Update successfully. "
        })

#                                             ------------------------------------- Other api endpoints -----------------

@app.route("/api/validate_password", methods=["POST"])
@limiter.limit("60 per minute")
def validate_password_api():

    data = request.get_json()

    if not data or "password" not in data:
        return jsonify({
            "message": "Password is required."
        }), 400

    password = data["password"]

    is_valid, message = validate_password(password)

    if is_valid:
        return jsonify({
            "valid": True,
            "message": message
        }), 200
    else:
        return jsonify({
            "valid": False,
            "message": message
        }), 400
#                                                             ------------------------- Security Headers -----------------
@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"

    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline'; "
        "style-src 'self' 'unsafe-inline'; "
        "img-src 'self' 'unsafe-inline';"
    )

    response.headers["X-Frame-Options"] = "DENY"

    response.headers["X-Content-Type-Options"] = "nosniff"

    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

    response.headers["Strict-Transport-Security"] = (
        "max-age=31536000; includeSubDomains"
    )

    response.headers["Server"] = ""

    return response

if __name__ == '__main__':
    app.run(
        debug=False,
        ssl_context=("certs/cert.pem", "certs/key.pem")
    )