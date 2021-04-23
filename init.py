from flask import Flask,render_template,redirect,session,url_for,request
import mysql.connector
app = Flask(__name__)

@app.route('/')
def hello_world():
    return render_template('login.html')

if __name__ == "__main__":
    app.run(host='localhost',debug=True)