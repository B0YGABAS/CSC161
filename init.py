from flask import Flask,render_template,redirect,session,url_for,request
from flask_ngrok import run_with_ngrok
import Database_Manager
import datetime

app = Flask(__name__, instance_relative_config=True)
app.secret_key="secret"
run_with_ngrok(app)

@app.route('/')
@app.route('/login')
def login():
    print(request.access_route)
    print("++")
    print(request.remote_addr)
    if "user" in session:
        return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/loginpass', methods=["POST"])
def loginpass():
    if Database_Manager.SEARCH("user",request.form.get("username"),1):
        if Database_Manager.SEARCH("user",request.form.get("username"),1)[0][2]==request.form.get("password"):
            #print(Database_Manager.SEARCH("user",request.form.get("username"),1))
            session["user"]=Database_Manager.SEARCH("user",request.form.get("username"),1)
            #session["Clearance"]=Database_Manager.SEARCH("Clearance",session["user"][0][4])
            Database_Manager.CREATE("logs",('IN',datetime.datetime.now(),session["user"][0][0]))
            #print(session["user"])
            return redirect(url_for('home'))
            return "hi  "+session["user"][0][1]
    return "PAKYO"

@app.route('/home')
def home():
    if "user" not in session:
        return redirect(url_for('login'))
    #print(session["Clearance"])
    message=""
    if "message" in session:
        message=session["message"]
        session.pop("message",None)
    return render_template('home.html',user=session["user"],Clearance=Database_Manager.SEARCH("Clearance",session["user"][0][4])[0],message=message)

@app.route('/transfer')
def transfer():
    if "user" not in session:
        return redirect(url_for('login'))
    message=""
    if "message" in session:
        message=session["message"]
        session.pop("message",None)
    return render_template('Transfer.html',user=session["user"],Clearance=Database_Manager.SEARCH("Clearance",session["user"][0][4])[0],message=message)

@app.route('/transferrequest', methods=["POST"])
def transferrequest():
    if "user" not in session:
        return redirect(url_for('login'))
    if int(request.form.get("amount"))<=int(session["user"][0][3]):
        if Database_Manager.SEARCH("user",request.form.get("recipient"),1):
            Database_Manager.CREATE("transfers",(None,int(request.form.get("amount")),datetime.datetime.now(),False,session["user"][0][0],Database_Manager.SEARCH("user",request.form.get("recipient"),1)[0][0],None))
            session["message"]="You have requested to transfer Php"+str(int(request.form.get("amount")))+" to "+request.form.get("recipient")+". Your teller will update your balance"
        else:
            session["message"]="The Recipient can't be found"
    return redirect(url_for('transfer'))

@app.route('/modifyaccount', methods=["POST"])
def modifyaccount():
    if "user" not in session:
        return redirect(url_for('login'))
    userlock=Database_Manager.SEARCH("user",request.form.get("userid"))[0]
    #print(userlock)
    #return "yawa"
    if request.form.get("clearance")!='unchange' and request.form.get("clearance")!=None:
        Database_Manager.UPDATE('user',(userlock[0],userlock[1],userlock[2],userlock[3],request.form.get("clearance")))
    if request.form.get("passchange")!=None:
        userlock=Database_Manager.SEARCH("user",request.form.get("userid"))[0]
        Database_Manager.UPDATE('user',(userlock[0],userlock[1],request.form.get("passchange"),userlock[3],userlock[4]))
    return redirect(url_for('transactions',a='user'))

@app.route('/depositwithdraw', methods=["POST"])
def depositwithdraw():
    if "user" not in session:
        return redirect(url_for('login'))
    #print(request.form.get("depositamount"))
    if request.form.get("mode")=="deposit":
        #print(datetime.datetime.now())
        Database_Manager.CREATE("deposits_or_withdrawals",(None,int(request.form.get("depositamount")),0,datetime.datetime.now(),False,session["user"][0][0],None))
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
    Database_Manager.CREATE("logs",('OUT',datetime.datetime.now(),session["user"][0][0]))
    session.pop("user",None)
    #session.pop("Clearance",None)
    return redirect(url_for('login'))

@app.route('/setstatus', methods=["POST"])
def setstatus():
    if "user" not in session:
        return redirect(url_for('login'))
    if Database_Manager.SEARCH("Clearance",session["user"][0][4])[0][2]==1:
        if request.form.get('type')=='deposits_or_withdrawalsID':
            session["message"]="Transaction Verified"
            retrieve=Database_Manager.SEARCH("deposits_or_withdrawals",request.form.get('status'))[0]
            userupdate=Database_Manager.SEARCH("user",retrieve[5])
            if int(userupdate[0][3])-int(retrieve[2])>=0:
                Database_Manager.UPDATE('deposits_or_withdrawals',(retrieve[0],retrieve[1],retrieve[2],retrieve[3],1,retrieve[5],session["user"][0][0]))
                #userupdate=Database_Manager.SEARCH("user",retrieve[5])
                Database_Manager.UPDATE('user',(userupdate[0][0],userupdate[0][1],userupdate[0][2],int(userupdate[0][3])+int(retrieve[1])-int(retrieve[2]),userupdate[0][4]))
            else:
                session["message"]="Transaction Failed, insufficient balance"
        else:
            retrieve=Database_Manager.SEARCH("transfers",request.form.get('status'))[0]
            userupdate=Database_Manager.SEARCH("user",retrieve[4])
            Database_Manager.UPDATE('transfers',(retrieve[0],retrieve[1],retrieve[2],1,retrieve[4],retrieve[5],session["user"][0][0]))
            if int(userupdate[0][3])-int(retrieve[1])>=0:
            #userupdate=Database_Manager.SEARCH("user",retrieve[4])
                Database_Manager.UPDATE('user',(userupdate[0][0],userupdate[0][1],userupdate[0][2],int(userupdate[0][3])-int(retrieve[1]),userupdate[0][4]))
                userupdate=Database_Manager.SEARCH("user",retrieve[5])
                Database_Manager.UPDATE('user',(userupdate[0][0],userupdate[0][1],userupdate[0][2],int(userupdate[0][3])+int(retrieve[1]),userupdate[0][4]))
            else:
                session["message"]="Transaction Failed, insufficient balance"
    else:
        session["message"]="Invalid Clearance"
    #session.pop("Clearance",None)
    return redirect(url_for('login'))

@app.route('/transactions/<a>')
def transactions(a):
    if "user" not in session:
        return redirect(url_for('login'))
    #logs=Database_Manager.SEARCH("logs")
    #transfers=Database_Manager.SEARCH("transfers")
    #deposits=Database_Manager.SEARCH("deposits_or_withdrawals")
    tablehead=Database_Manager.READFIELDS(a)
    transaction=Database_Manager.SEARCH(a)
    newtran=[]
    newesttran=[]
    for i in range(len(transaction)):
        newtran.append(list(transaction[i]))
        for j in range(len(transaction[i])):
            #print(transaction[i][j])
            #print(tablehead[j])
            if (tablehead[j]=="From" or tablehead[j]=="To" or tablehead[j]=="Teller" or tablehead[j]=="User") and transaction[i][j]!=None:
                #newtran[i][j]==Database_Manager.SEARCH("user",transaction[i][j],0)[0][1]
                del newtran[i][j]
                newtran[i].insert(j,Database_Manager.SEARCH("user",transaction[i][j],0)[0][1])
                #print("success")
    for i in range(len(newtran)):
        purge=[]
        for j in range(len(newtran[i])):
            #print(j==session["user"][0][1])
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
    #print(newtran)
    #tablehead=0
    #print(tablehead)
    #print(transaction)
    '''
    if Database_Manager.SEARCH("Clearance",session["user"][0][4])[0][1]:
        logs=Database_Manager.SEARCH("logs")
        transfers=Database_Manager.SEARCH("transfers")
        deposits=Database_Manager.SEARCH("deposits or withdrawals")
    else:
        logs=Database_Manager.SEARCH("logs",session["user"][0][0],2)
        transfers=list(set(Database_Manager.SEARCH("transfers",session["user"][0][0],4))+set(Database_Manager.SEARCH("transfers",session["user"][0][0],5))+set(Database_Manager.SEARCH("transfers",session["user"][0][0],6))-(set(Database_Manager.SEARCH("transfers",session["user"][0][0],4))&set(Database_Manager.SEARCH("transfers",session["user"][0][0],5))&set(Database_Manager.SEARCH("transfers",session["user"][0][0],6))))
        print(transfers)
        deposits=Database_Manager.SEARCH("deposits or withdrawals")
    '''
    return render_template('transactions.html',user=session["user"],Clearance=Database_Manager.SEARCH("Clearance",session["user"][0][4])[0],transaction=newesttran,tablehead=tablehead,clearances=newclear)

if __name__ == "__main__":
    #app.run(host='localhost',debug=True)
    app.run()