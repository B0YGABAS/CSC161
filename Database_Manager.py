import mysql.connector
import datetime

DATABASE=mysql.connector.connect(host="localhost",user="root",password="Python2.0",db ="bank")

DATA=DATABASE.cursor()

def CREATE(table,tuples):
    DATAFIELDS=READFIELDS(table)
    DATAFIELDSTRING="insert into "+table+" ("
    for i in DATAFIELDS:
        DATAFIELDSTRING=DATAFIELDSTRING+"`"+i+"`"
        if i!=DATAFIELDS[-1]:
            DATAFIELDSTRING=DATAFIELDSTRING+","
    DATAFIELDSTRING=DATAFIELDSTRING+") VALUES ("
    for i in DATAFIELDS:
        DATAFIELDSTRING=DATAFIELDSTRING+"%s"
        if i!=DATAFIELDS[-1]:
            DATAFIELDSTRING=DATAFIELDSTRING+","
    DATAFIELDSTRING=DATAFIELDSTRING+")"
    print(DATAFIELDSTRING)
    DATA.execute(DATAFIELDSTRING,tuples)
    DATABASE.commit()

def SEARCH(table,search="",foreignindex=0,tupletostring=0, orderby=0):
    DATAFIELDS=READFIELDS(table)
    DATAFIELDSTRING="SELECT * from "+table
    if search!="":
        DATAFIELDSTRING=DATAFIELDSTRING+" where `"+DATAFIELDS[foreignindex]+"`=\'"+str(search)+"\'"
    if orderby!=0:
        DATAFIELDSTRING=DATAFIELDSTRING+" order by "+DATAFIELDS[abs(orderby)]
        if orderby<0:
            DATAFIELDSTRING=DATAFIELDSTRING+" DESC"
    #print(DATAFIELDSTRING)
    DATA.execute(DATAFIELDSTRING)
    if tupletostring==0:
        return DATA.fetchall()
    else:
        tupletostring=DATA.fetchall()
        for i in range(len(tupletostring)):
            tupletostring[i]=list(tupletostring[i])
        return tupletostring
        
def READFIELDS(table=()):
    table="\'"+table+"\'"
    DATAFIELDSTRING="SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE table_schema = 'bank' and TABLE_NAME ="+table+" order by ORDINAL_POSITION"
    DATA.execute(DATAFIELDSTRING)
    DATAFIELDFETCH=DATA.fetchall()
    DATAFIELDS=[]
    for i in DATAFIELDFETCH:
        DATAFIELDS.append(i[3])
    return DATAFIELDS

def inspect(table,search):
    table="`"+table+"`"
    DATAFIELDSTRING="SELECT * from "+table+" where Userid="+search
    DATA.execute(DATAFIELDSTRING)
    return DATA.fetchall()

def UPDATE(table,tuples):
    DATAFIELDS=READFIELDS(table)
    DATAFIELDSTRING="update "+table+" set "
    for i in DATAFIELDS:
        DATAFIELDSTRING=DATAFIELDSTRING+"`"+i+"`=%s"
        if i==DATAFIELDS[-1]:
            DATAFIELDSTRING=DATAFIELDSTRING+" where `"+DATAFIELDS[0]+"`=%s"
        else:
            DATAFIELDSTRING=DATAFIELDSTRING+","
    tuples=tuples+(tuples[0],)
    #print(DATAFIELDSTRING)
    DATA.execute(DATAFIELDSTRING,tuples)
    DATABASE.commit()

def DELETE(table,id,index=0):
    DATAFIELDS=READFIELDS(table)
    DATAFIELDSTRING="delete from "+table+" where ("+DATAFIELDS[index]+"="+id+")"
    print(DATAFIELDSTRING)
    DATA.execute(DATAFIELDSTRING)
    DATABASE.commit()

def User_Profile_lockon(account):
    '''x=READFIELDS("user")
    print(x)'''
    account=str(account)
    DATAFIELDS=SEARCH("profile",account)
    for i in DATAFIELDS:
        if i[-1]==account:
            return i
    return False

#CREATE('user',(None,'Isaiah Andre Pabillon','WHATDASHIT',0,'Client'))
    
'''
#CREATE("item","wa")
CREATE("user",(2,"Zia","zia@msu","shannon"))
#CREATE("phone_number",("0420",420))
#CREATE("order",(3,420,1,'1969-4-20',1,1))
CREATE("user",(520,"Zea","Zea@msu","Shannon"))
UPDATE("user",(520,"Zea","Zea@msui","Shannon",520))
#DELETE("user","520")
'''
#CREATE("image",(4205,))
#print(SEARCH("image",""))
'''
x=User_Profile_lockon(520)
if x:
    print(x)
x=SEARCH("item","New",1,0,5)
for i in x:
    print(i)'''