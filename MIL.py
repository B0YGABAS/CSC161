#importing the Yagmail library
import yagmail

def MIL(Sento,Subjik,Kontent):
    try:
        #initializing the server connection
        yag = yagmail.SMTP(user='nollibapai@gmail.com', password='Python2.0')
        #sending the email
        #yag.send(to=Sento, subject='PAKYO', contents='<div style="background-color:black;color:white;"><h1>PAKYO KA!!</h1><h2>PAKYO KA!!</h2><h3>PAKYO KA!!</h3><h4>PAKYO KA!!</h4><h5>PAKYO KA!!</h5><h6>PAKYO KA!!</h6><a href="'+Kontent+'">I CLICK NI CHOII!!</a></div>')
        #yag.send(to=Sento, subject='PAKYO', contents='<div style="background-color:black;color:white;"><h1>PAKYO KA!!</h1><h2>PAKYO KA!!</h2><h3>PAKYO KA!!</h3><h4>PAKYO KA!!</h4><h5>PAKYO KA!!</h5><h6>PAKYO KA!!</h6><form method="post" action="'+Kontent+'"><input type="submit" value="I CLICK NI CHOII!!"></form></div>')
        yag.send(to=Sento, subject=Subjik, contents=Kontent)
        print("Email sent successfully")
    except:
        print("Error, email was not sent")