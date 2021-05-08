from flask import Flask,render_template,redirect,session,url_for,request
#from flask_ngrok import run_with_ngrok
#import Database_Manager
import datetime

app = Flask(__name__, instance_relative_config=True)
#run_with_ngrok(app)
app.secret_key="secret"
'''
@app.route('/')
def hi():
    return "hello"

'''
@app.route('/a')
def a():
    ip_address = request.remote_addr
    print(ip_address)
    print(request.access_route)
    print('----------')
    print(request.environ.get('REMOTE_ADDR'))
    if ip_address=="192.168.18.241":
        return ip_address + "----   "+ "".join(i for i in request.access_route)+"YYYY"
    else:
        return ip_address + "----   "+ "".join(i for i in request.access_route)+"NNNNN"
    return ip_address + "----   "+ "".join(i for i in request.access_route)
    return "PAKYO!!!!!!!"

@app.route('/m/<a>')
def m(a):
    if a=="pop":
        session.pop("machine",None)
        return "removed"
    session["machine"]=a
    return "machine added: "+a

@app.route('/')
@app.route('/p')
def p():
    return render_template('localstorage.html')
    '''
    if "machine" not in session:
        return "no"
    return session["machine"]'''
    '''
    print(request.headers.getlist("X-Forwarded-For"))
    print(request.environ)
    return "".join(i for i in request.environ)'''
    #return "\n".join(i for i in request.headers.getlist("X-Forwarded-For"))

if __name__ == "__main__":
    #app.run()
    #app.run(host="192.168.18.241")
    app.run(host="0.0.0.0",port=8080,debug=True)
