from app import app
from flask import json,request,jsonify, send_file
import cx_Oracle
from datetime import date

ip = "192.168.0.143"
bd = "baussenac"

@app.route('/login' , methods=['POST'])
def conn_bdd():
    global ip
    global bd

    # conn = cx_Oracle.connect(bd,"azerty",ip)
    conn = cx_Oracle.connect('baussenac/azerty@192.168.0.143:1521/xe')
    mycursor = conn.cursor()

    #Création du JSON
    content = request.json

    #Récupération des données du JSON envoyé
    user = content['user']
    password = content['password']

    #Creation cursor
    mycursor.execute("""SELECT * FROM Utilisateur WHERE login = :login and password = :password""",login = user,password = password)

    #Exécution de la requête sql
    myresult = mycursor.fetchall()
    
    #Si la longueur du resultat est égale a 1 alors le login et le mot de passe correspondent
    if(len(myresult) == 1):
        conn.close()
        return {"result":"added"} #On renvoit alors true
    conn.close()
    return {"value":"Ca marche pas"} #Sinon on renvoit false




@app.route('/register', methods = ['POST'])
def testBD():
    global ip
    global bd

    # conn = cx_Oracle.connect(bd,"azerty",ip)
    conn = cx_Oracle.connect('baussenac/azerty@192.168.0.143:1521/xe')
    mycursor = conn.cursor()

    #Création du JSON
    content = request.json

    #Récupération des données du JSON envoyé
    login = content['login']
    password = content['password']
    name = content['name']
    surname = content['surname']
    mail = content['mail']

    #Creation cursor
    mycursor.execute("""SELECT * FROM Utilisateur WHERE login = :login """,
    login = login)

    #Exécution de la requête sql
    myresult = mycursor.fetchall()
    date_actuelle = date.today()

    #Si la longueur du resultat est égale a 0 aucun user ne possede le login rentré 
    if(len(myresult) == 0):
        #On peut alors créer le nouveau user avec son mot de passe, son nom, son prénom et son login
        mycursor.execute("""INSERT INTO Utilisateur VALUES (:uniqueID, :login, :password, :mail, '0623605498','125' ,:date_actuelle ,:surname, :name)""",uniqueID=login,login=login,password=password, mail=mail,date_actuelle=date_actuelle,surname=surname, name=name)
        texteResultat = "added"
        conn.commit()
        conn.close()
    else:
        #Sinon on renvoit un message d'erreur
        texteResultat = "Ce login est déjà utilisé"
        conn.close()
    return {"result":texteResultat}

    