from flask import Flask ,render_template


@app.route("/")
def home():
    return render_template("erro.html")
