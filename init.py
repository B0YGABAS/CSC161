from flask import Flask,render_template,redirect,session,url_for,request
#from flask_ngrok import run_with_ngrok
import Database_Manager
import datetime
import random
import PHD_PASSWORD_GENERATOR

app = Flask(__name__, instance_relative_config=True)
app.secret_key="secret"
#run_with_ngrok(app)

def gen():
    #print(session["machine"][3])
    #print(Database_Manager.SEARCH("machine",session["machine"][0])[0][3])
    if session["machine"][0]!=1 and session["machine"][3]==Database_Manager.SEARCH("machine",session["machine"][0])[0][3]:
        PHD=PHD_PASSWORD_GENERATOR.gen(44)
        Database_Manager.UPDATE("machine", (session["machine"][0],session["machine"][1],session["machine"][2],PHD))
        session["machine"]=Database_Manager.SEARCH("machine",session["machine"][0])[0] #OPTIONAL NI NA LINE
        return PHD
    else:
        return 1

@app.route('/')
@app.route('/login')
def login():
    #print(request.access_route)
    #print("++")
    #print(request.remote_addr)
    #session.pop("user",None)
    #session.pop("machine",None)
    if "user" in session:
        return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/loginpass', methods=["POST"])
def loginpass():
    if Database_Manager.SEARCH("user",request.form.get("username"),1):
        if Database_Manager.SEARCH("user",request.form.get("username"),1)[0][2]==request.form.get("password"):
            session["user"]=Database_Manager.SEARCH("user",request.form.get("username"),1)
            machine=request.form.get("machineid")
            if machine=="":
                machine="1"
            machine=Database_Manager.SEARCH("machine",machine)[0]
            session["machine"]=machine
            if (session["user"][0][4]!="Teller" or machine[0]!=1) and session["machine"][3]==request.form.get('machinepass'): #Successful login
                Database_Manager.CREATE("logs",('IN',datetime.datetime.now(),session["user"][0][0],int(machine[0])))
                return redirect(url_for('home'))
                return "hi  "+session["user"][0][1]
            session.pop("user",None)
            session.pop("machine",None)
            if machine[3]!=request.form.get('machinepass'):
                return "WARNING! the machine is compromised"
            else:
                return "Unauthorized Device"
        else:
            return "Wrong Password"
    return "PAKYO"

@app.route('/home')
def home():
    if "user" not in session:
        return redirect(url_for('login'))
    message=""
    if "message" in session:
        message=session["message"]
        session.pop("message",None)
    return render_template('home.html',user=session["user"],Clearance=Database_Manager.SEARCH("Clearance",session["user"][0][4])[0],PHD=gen(),message=message,machine=session["machine"])

@app.route('/transfer')
def transfer():
    if "user" not in session:
        return redirect(url_for('login'))
    message=""
    if "message" in session:
        message=session["message"]
        session.pop("message",None)
    #print(message)
    return render_template('Transfer.html',user=session["user"],Clearance=Database_Manager.SEARCH("Clearance",session["user"][0][4])[0],PHD=gen(),message=message)

@app.route('/transferrequest', methods=["POST"])
def transferrequest():
    if "user" not in session:
        return redirect(url_for('login'))
    if int(request.form.get("amount"))<=int(session["user"][0][3]):
        if Database_Manager.SEARCH("user",request.form.get("recipient"),1):
            Database_Manager.CREATE("transfers",(None,int(request.form.get("amount")),datetime.datetime.now(),session["user"][0][0],Database_Manager.SEARCH("user",request.form.get("recipient"),1)[0][0]))
            session["message"]="You have requested to transfer Php"+str(int(request.form.get("amount")))+" to "+request.form.get("recipient")+". Your teller will update your balance"
        else:
            session["message"]="The Recipient can't be found"
    else:
        session["message"]="Insufficient Balance"
    return redirect(url_for('transfer'))

@app.route('/modifyaccount', methods=["POST"])
def modifyaccount():
    if "user" not in session:
        return redirect(url_for('login'))
    userlock=Database_Manager.SEARCH("user",request.form.get("userid"))[0]
    if request.form.get("clearance")!='unchange' and request.form.get("clearance")!=None:
        Database_Manager.UPDATE('user',(userlock[0],userlock[1],userlock[2],userlock[3],request.form.get("clearance")))
    return redirect(url_for('transactions',a='user'))

@app.route('/depositwithdraw', methods=["POST"])
def depositwithdraw():
    if "user" not in session:
        return redirect(url_for('login'))
    if request.form.get("mode")=="deposit":
        Database_Manager.CREATE("deposits_or_withdrawals",(None,int(request.form.get("depositamount")),datetime.datetime.now(),False,session["user"][0][0],None))
        session["message"]="You have requested to deposit Php"+str(int(request.form.get("depositamount")))+". Your teller will update your balance once he/she receives your cash"
        return redirect(url_for('home'))
    else:
        if int(request.form.get("withdrawamount"))<=int(session["user"][0][3]):
            Database_Manager.CREATE("deposits_or_withdrawals",(None,0,int(request.form.get("withdrawamount")),datetime.datetime.now(),False,session["user"][0][0],None))
            session["message"]="You have requested to withdraw Php"+str(int(request.form.get("withdrawamount")))+". Your teller will update your balance once you receive your cash"
            return redirect(url_for('home'))
        else:
            session["message"]="You don't have enough balance"
            return redirect(url_for('home'))
        return "w"
    return "hello world"
    return render_template('home.html',user=session["user"],Clearance=Database_Manager.SEARCH("Clearance",session["user"][0][4])[0])

@app.route('/logout', methods=["POST"])
def logout():
    Database_Manager.CREATE("logs",('OUT',datetime.datetime.now(),session["user"][0][0],session["machine"][0]))
    session.pop("user",None)
    session.pop("machine",None)
    return redirect(url_for('login'))

@app.route('/transactions/<a>') #WARSHAK KAAU
def transactions(a):
    if "user" not in session:
        return redirect(url_for('login'))
    tablehead=Database_Manager.READFIELDS(a)
    transaction=Database_Manager.SEARCH(a)
    newtran=[]
    newesttran=[]
    for i in range(len(transaction)):
        newtran.append(list(transaction[i]))
        for j in range(len(transaction[i])):
            if (tablehead[j]=="From" or tablehead[j]=="To" or tablehead[j]=="Teller" or tablehead[j]=="User") and transaction[i][j]!=None:
                del newtran[i][j]
                newtran[i].insert(j,Database_Manager.SEARCH("user",transaction[i][j],0)[0][1])
    for i in range(len(newtran)):
        purge=[]
        for j in range(len(newtran[i])):
            if newtran[i][j]==session["user"][0][1] or (Database_Manager.SEARCH("Clearance",session["user"][0][4])[0][2] and (tablehead[j]=="Status" and newtran[i][j]==0)):
                purge.append("no")
        if len(purge)>=1:
            newesttran.append(newtran[i])
    if Database_Manager.SEARCH("Clearance",session["user"][0][4])[0][1]:
        newesttran=newtran
    clearances=Database_Manager.SEARCH("Clearance")
    newclear=[]
    for i in clearances:
        newclear.append(i[0])
    return render_template('transactions.html',user=session["user"],Clearance=Database_Manager.SEARCH("Clearance",session["user"][0][4])[0],PHD=gen(),transaction=newesttran,tablehead=tablehead,clearances=newclear)

@app.route('/registermachine', methods=["POST"])
def registermachine():
    #lokajmachine=Database_Manager.CREATE("machine", (None,request.form.get("branchname"),request.form.get("pcnumber"),random.randint(0,999999)))
    #session["machine"]=Database_Manager.CREATE("machine", (None,request.form.get("branchname"),request.form.get("pcnumber"),random.randint(0,999999)))[0]
    session["machine"]=Database_Manager.SEARCH("machine", Database_Manager.CREATE("machine", (None,request.form.get("branchname"),request.form.get("pcnumber"),PHD_PASSWORD_GENERATOR.gen(44)))[0])[0]
    #print(session["machine"])
    return render_template('lokajstorage.html',lokaj=session["machine"])

@app.route('/redirect_to_home', methods=["POST"])
def redirect_to_home():
    if request.form.get("setmachine"):
        Disable=Database_Manager.SEARCH("machine",request.form.get("setmachine"))[0]
        Database_Manager.UPDATE("machine",(Disable[0],Disable[1]+"!--Disabled--!",Disable[2],random.randint(0,999999)))
        session["machine"]=Database_Manager.SEARCH("machine",1)[0]
    #print(request.form.get("setmachine"))
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(host='localhost',debug=True)
    #app.run()
