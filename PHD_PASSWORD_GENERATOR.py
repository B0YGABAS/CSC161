import random

def gen(taas):
    password=[]
    for i in range(taas):
        if random.randint(0,3)==0:
            password.append(random.randint(ord('A'),ord('Z')))
        elif random.randint(0,3)==1:
            password.append(random.randint(ord('a'),ord('z')))
        else:
            password.append(random.randint(ord('0'),ord('9')))
    passwordfinal="".join(chr(i) for i in password)
    return passwordfinal
#print(chr(65))
#print(gen(25))