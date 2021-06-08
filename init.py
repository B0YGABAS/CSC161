from flask import Flask,render_template,redirect,session,url_for,request
#from flask_ngrok import run_with_ngrok
import Database_Manager
import datetime
import random
import PHD_PASSWORD_GENERATOR
import MIL

app = Flask(__name__, instance_relative_config=True)
app.secret_key="secret"
#run_with_ngrok(app)

def gen():
    #print(session["machine"][3])
    #print(Database_Manager.SEARCH("machine",session["machine"][0])[0][3])
    if session["machine"][0]!=1 and ("user" in session): #and session["machine"][3]==Database_Manager.SEARCH("machine",session["machine"][0])[0][3]: #Gi abort na ni na part sa line, kie magkaproblema kung lag
        PHD=PHD_PASSWORD_GENERATOR.gen(44)
        Database_Manager.UPDATE("machine", (session["machine"][0],session["machine"][1],session["machine"][2],PHD))
        session["machine"]=Database_Manager.SEARCH("machine",session["machine"][0])[0] #OPTIONAL NI NA LINE
        return PHD
    else:
        return 1

@app.route('/')
@app.route('/login')
def login():
    #MIL.MIL("iapabillon@gmail.com",request.base_url+"PAKYO")
    #print(request.access_route)
    #print("++")
    #print(request.remote_addr)
    #session.pop("user",None)
    #session.pop("machine",None)
    if "user" in session:
        return redirect(url_for('home'))
    if "machine" in session:
        session.pop("machine",None)
    if "OTP" in session:
        session.pop("OTP",None)
    message=""
    if "message" in session:
        message=session["message"]
        session.pop("message",None)
    return render_template('login.html',message=message)

@app.route('/PAKYO', methods=["POST","GET"])
def PAKYO():
    if request.method == "POST":
        return "PAKME"
    return "PAKYO"

@app.route('/OTP')
def OTP():
    message=""
    if "message" in session:
        message=session["message"]
        session.pop("message",None)
    return render_template('OTP.html',message=message)

@app.route('/resendOTP',methods=["POST"])
def resendOTP():
    session["OTP"]=[session["OTP"][0],PHD_PASSWORD_GENERATOR.gen(6),datetime.datetime.now()]
    MIL.MIL(session["OTP"][0][5], "Your OTP is", render_template('webmail.html',webmail=1,GEN=session["OTP"][1]))
    return redirect(url_for('OTP'))

@app.route('/OTPrequest',methods=["POST"])
def OTPrequest():
    otpnewtime=datetime.datetime.now()
    if request.form.get("otp")==session["OTP"][1]:
        if (otpnewtime-session["OTP"][2]).total_seconds()/60<=2:
            session["user"]=Database_Manager.SEARCH("user",session["OTP"][0][0])
            Database_Manager.CREATE("logs",('IN',datetime.datetime.now(),session["user"][0][0],int(session["machine"][0])))
            return redirect(url_for('home'))
        else:
            session["message"]="OTP expired. Click resend OTP"
        #return "success"
    else:
        session["message"]="Wrong OTP"
    return redirect(url_for('OTP'))
    return "fail"
    return "render_template('OTP.html')"

@app.route('/loginpass', methods=["POST"])
def loginpass():
    if Database_Manager.SEARCH("user",request.form.get("username"),1) and request.form.get("username")!="":
        if Database_Manager.SEARCH("user",request.form.get("username"),1)[0][2]==request.form.get("password"):
            session["user"]=Database_Manager.SEARCH("user",request.form.get("username"),1)
            machine=request.form.get("machineid")
            if machine=="":
                machine="1"
            machine=Database_Manager.SEARCH("machine",machine)[0]
            session["machine"]=machine
            #if (session["user"][0][4]!="Teller" or machine[0]!=1) and session["machine"][3]==request.form.get('machinepass'):
            if (Database_Manager.SEARCH("Clearance",session["user"][0][4])[0][5]!=1 or machine[0]!=1) and session["machine"][3]==request.form.get('machinepass'): #Successful login
                #Database_Manager.CREATE("logs",('IN',datetime.datetime.now(),session["user"][0][0],int(machine[0])))
                #return redirect(url_for('home'))
                session["OTP"]=[session["user"][0],PHD_PASSWORD_GENERATOR.gen(6),datetime.datetime.now()]
                session.pop("user",None)
                MIL.MIL(session["OTP"][0][5], "Your OTP is", render_template('webmail.html',webmail=1,GEN=session["OTP"][1]))
                #print(session["OTP"])
                return redirect(url_for('OTP'))
                return "hi  "+session["user"][0][1]
            session.pop("user",None)
            session.pop("machine",None)
            if machine[3]!=request.form.get('machinepass'):
                session["message"]="WARNING! the machine is compromised"
            else:
                session["message"]="Unauthorized Device"
        else:
            session["message"]="Wrong Password"
    else:
        session["message"]="User does not exist"
    return redirect(url_for('login'))

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
    Sender=Database_Manager.SEARCH("user",session["user"][0][0])[0]
    if int(request.form.get("amount"))<=int(Sender[3]):
        if Database_Manager.SEARCH("user",request.form.get("recipient"),1):
            Database_Manager.CREATE("transfers",(None,int(request.form.get("amount")),datetime.datetime.now(),Sender[0],Database_Manager.SEARCH("user",request.form.get("recipient"),1)[0][0]))
            Database_Manager.UPDATE("user", (Sender[0],Sender[1],Sender[2],Sender[3]-int(request.form.get("amount")),Sender[4],Sender[5]))
            recipient=Database_Manager.SEARCH("user",request.form.get("recipient"),1)
            #print(recipient)
            Database_Manager.UPDATE("user", (recipient[0][0],recipient[0][1],recipient[0][2],recipient[0][3]+int(request.form.get("amount")),recipient[0][4],recipient[0][5]))
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
        Database_Manager.UPDATE("user",(userlock[0],userlock[1],userlock[2],userlock[3],request.form.get("clearance"),userlock[5]))
    return redirect(url_for('transactions',a='user'))

@app.route('/depositwithdraw', methods=["POST"])
def depositwithdraw():
    if "user" not in session:
        return redirect(url_for('login'))
    #print(request.form.get('clientname'))
    #print(request.form.get('clientid'))
    clientid=Database_Manager.SEARCH("user", request.form.get("clientid"))
    clientname=Database_Manager.SEARCH("user", request.form.get("clientname"),1)
    #print(clientid[0][3])
    #print(x==y)
    #print(x)
    #print(y)
    if not (clientid==clientname and len(clientid)==1):
        session["message"]="Name and ID are mismatched"
        return redirect(url_for('home'))
    #Database_Manager.SEARCH("Clearance",clientid[0][4])[0][8]
    elif Database_Manager.SEARCH("Clearance",clientid[0][4])[0][8]==0:
        session["message"]="Account is frozen!"
        return redirect(url_for('home'))
    #print(Database_Manager.SEARCH("Clearance",clientid[0][4]))
    if request.form.get("mode")=="deposit":
        Database_Manager.CREATE("deposits_or_withdrawals",(None,int(request.form.get("depositamount")),0,datetime.datetime.now(),request.form.get("clientid"),session["user"][0][0]))
        Database_Manager.UPDATE("user", (clientid[0][0],clientid[0][1],clientid[0][2],clientid[0][3]+int(request.form.get("depositamount")),clientid[0][4],clientid[0][5]))
        session["message"]="You have requested to deposit Php"+str(int(request.form.get("depositamount")))+". Your teller will update your balance once he/she receives your cash"
        return redirect(url_for('home'))
    else:
        if int(request.form.get("withdrawamount"))<=int(clientid[0][3]):
            Database_Manager.CREATE("deposits_or_withdrawals",(None,0,int(request.form.get("withdrawamount")),datetime.datetime.now(),request.form.get("clientid"),session["user"][0][0]))
            Database_Manager.UPDATE("user", (clientid[0][0],clientid[0][1],clientid[0][2],clientid[0][3]-int(request.form.get("withdrawamount")),clientid[0][4],clientid[0][5]))
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
    if "searchlock" in session:
        session.pop("searchlock",0)
    return redirect(url_for('login'))
'''
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
            if newtran[i][j]==session["user"][0][1] or (Database_Manager.SEARCH("Clearance",session["user"][0][4])[0][7] and (tablehead[j]=="Status" and newtran[i][j]==0)):
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
'''
@app.route('/transactions/<a>') #WARSHAK KAAU
def transactions(a):
    if "user" not in session:
        return redirect(url_for('login'))
    #session.pop("searchlock",0)
    tablehead=Database_Manager.READFIELDS(a)
    transaction=Database_Manager.SEARCH(a)
    newtran=[]
    newesttran=[]
    message=""
    searchlock=session["user"][0][1]
    Clearance=Database_Manager.SEARCH("Clearance",session["user"][0][4])[0]
    if "searchlock" in session:
        #print(session["searchlock"])
        searchlock=session["searchlock"][1]
        message="You are spectating "+session["searchlock"][1]+"'s account. The balance is Php "+str(session["searchlock"][3])+"."
        Clearance=Clearance+("SEARCHLOCK ACTIVATED!",)
        #print(Clearance)
        #message="SEARCHLOCK ACTIVATED!"
    for i in range(len(transaction)):
        newtran.append(list(transaction[i]))
        for j in range(len(transaction[i])):
            if (tablehead[j]=="From" or tablehead[j]=="To" or tablehead[j]=="Teller" or tablehead[j]=="User") and transaction[i][j]!=None:
                del newtran[i][j]
                newtran[i].insert(j,Database_Manager.SEARCH("user",transaction[i][j],0)[0][1])
    for i in range(len(newtran)):
        purge=[]
        for j in range(len(newtran[i])):
            if newtran[i][j]==searchlock or (Database_Manager.SEARCH("Clearance",session["user"][0][4])[0][7] and (tablehead[j]=="Status" and newtran[i][j]==0)):
                purge.append("no")
        if len(purge)>=1:
            newesttran.append(newtran[i])
    if Database_Manager.SEARCH("Clearance",session["user"][0][4])[0][1]:
        newesttran=newtran
    clearances=Database_Manager.SEARCH("Clearance")
    newclear=[]
    for i in clearances:
        newclear.append(i[0])
    return render_template('transactions.html',user=session["user"],Clearance=Clearance,PHD=gen(),message=message,transaction=newesttran,tablehead=tablehead,clearances=newclear)

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

@app.route('/searchlock/<addelete>', methods=["POST"])
def searchlock(addelete):
    if addelete=="add":
        try:
            session["searchlock"]=Database_Manager.SEARCH("user",request.form.get("searchlock"),1)[0]
        except:
            session["message"]="User does not exist"
            if "searchlock" in session:
                session.pop("searchlock",0)
            return redirect(url_for('home'))
        return redirect(url_for('transactions',a="deposits_or_withdrawals"))
    else:
        session.pop("searchlock",0)
        return redirect(url_for('home'))

@app.route('/createaccount')
def createaccount():
    return render_template("createaccount.html",webmail=0)

@app.route('/createaccountpass', methods=["POST"])
def createaccountpass():
    #print(request.form.get("username"))
    #print(request.form.get("password"))
    #print(request.form.get("email"))
    if Database_Manager.SEARCH("user",request.form.get("username"),1):
        session["message"]="username exists"
    elif Database_Manager.SEARCH("user",request.form.get("email"),5):
        session["message"]="email exists"
    else:
        #Database_Manager.CREATE("user", (None,request.form.get("username"),request.form.get("password"),0,"Client",request.form.get("email")))
        MIL.MIL(request.form.get("email"),"Verify Your account at Banko Ni Andre",render_template("webmail.html",webmail=2,fields=[request.form.get("username"),request.form.get("password"),request.form.get("email")]))
        session["message"]="Check your email"
    return redirect(url_for('login'))

@app.route('/lokads',methods=["POST"])
def lokads():
    if request.method == 'POST':
        #print(request.form.get("nim"))
        #print(request.form.get("pass"))
        #print(request.form.get("imil"))
        return "lokaj"
    return "lokads"

@app.route('/createfinal',methods=["POST"])
def createfinal():
    if request.method == 'POST':
        if Database_Manager.SEARCH("user",request.form.get("nim"),1) or Database_Manager.SEARCH("user",request.form.get("imil"),5):
            session["message"]="Email already Verified"
        else:
            Database_Manager.CREATE("user", (None,request.form.get("nim"),request.form.get("pass"),0,"Client",request.form.get("imil")))
            session["message"]="Email Verified"
        return redirect(url_for('login'))

@app.route('/forgetpassword')
def forgetpassword():
    return render_template('forgotpass.html')

@app.route('/requestforgetpassword',methods=["POST"])
def requestforgetpassword():
    if Database_Manager.SEARCH("user",request.form.get("imil"),5):
        MIL.MIL(Database_Manager.SEARCH("user",request.form.get("imil"),5)[0][5], "Change Your Password", render_template('webmail.html',webmail=2,fields=[Database_Manager.SEARCH("user",request.form.get("imil"),5)[0][0]]))
        session["message"]="Password reset sent to email"
    else:
        session["message"]="Email does not exist"
    return redirect(url_for('login'))

@app.route('/forgotprefinal',methods=["POST"])
def forgotprefinal():
    return render_template('forgotpassfinal.html',aydi=request.form.get("aydi")) 

@app.route('/forgotfinal',methods=["POST"])
def forgotfinal():
    usersearch=Database_Manager.SEARCH("user",request.form.get("aydi"))[0]
    Database_Manager.UPDATE("user",(usersearch[0],usersearch[1],request.form.get("password"),usersearch[3],usersearch[4],usersearch[5]))
    session["message"]="Password reset"
    return redirect(url_for('login'))
    
        
if __name__ == "__main__":
    app.run(host='localhost',debug=True)
    #app.run()
