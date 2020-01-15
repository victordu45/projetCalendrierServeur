from app import app
from flask import json,request,jsonify, send_file
import cx_Oracle
import datetime 
import re
from datetime import date
from datetime import datetime, timedelta
import time

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
    mycursor.execute("""SELECT uniqueID FROM Utilisateur WHERE login = :login and password = :password""",login = user,password = password)

    #Exécution de la requête sql
    myresult = mycursor.fetchone()
    uniqueID = myresult[0]
    
    #Si la longueur du resultat est égale a 1 alors le login et le mot de passe correspondent
    if(len(myresult) == 1):
        conn.close()
        return {"result":"added", "uniqueID":uniqueID} #On renvoit alors true
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


    dateNow = datetime.datetime.now()
    dateNow = dateNow.strftime("%d%m%Y%H%M%S-%f")
    uniqueID = login.upper()+'-'+dateNow

    #Creation cursor
    mycursor.execute("""SELECT * FROM Utilisateur WHERE login = :login """,
    login = login)

    #Exécution de la requête sql
    myresult = mycursor.fetchall()
    date_actuelle = date.today()

    #Si la longueur du resultat est égale a 0 aucun user ne possede le login rentré 
    if(len(myresult) == 0):
       #On peut alors créer le nouveau user avec son mot de passe, son nom, son prénom et son login
        mycursor.execute("""INSERT INTO Utilisateur VALUES (:uniqueID, :login, :password, :mail, '0623605498','125' ,:date_actuelle ,:surname, :name)""",uniqueID=uniqueID,login=login,password=password, mail=mail,date_actuelle=date_actuelle,surname=surname, name=name)
        texteResultat = "added"
        conn.commit()
        conn.close()
    else:
        #Sinon on renvoit un message d'erreur
        texteResultat = "Ce login est déjà utilisé"
        conn.close()
    return {"result":texteResultat}

"""@app.route('/addNewEvent', methods= ['POST'])
def addNewEvent():
    global ip
    global bd
    # conn = cx_Oracle.connect(bd,"azerty",ip)
    conn = cx_Oracle.connect('baussenac/azerty@192.168.0.143:1521/xe')
    mycursor = conn.cursor()

    #Création du JSON
    content = request.json

    login = content['login']
    nom = content['nom']
    dateDebut = content['dateDebut']
    heureDebut = content['heureDebut']
    dateFin = content['dateFin']
    heureFin = content['heureFin']
    description = content['description']"""


@app.route('/getPersonalCalendar', methods= ['POST'])
def getPersonalCalendar():
    global ip
    global bd
    # conn = cx_Oracle.connect(bd,"azerty",ip)
    conn = cx_Oracle.connect('baussenac/azerty@192.168.0.143:1521/xe')
    mycursor = conn.cursor()

    #Création du JSON
    content = request.json
    uniqueID = content['uniqueID']
    #Renvois tous les calendrier de l'utilisateur (perso)
    mycursor.execute("""SELECT c.idCalendrier, c.nomCalendrier, c.description FROM calendrier c 
    WHERE c.idAdministrateur = :uniqueID  """,uniqueID=uniqueID)
    
    myresult = mycursor.fetchall()
    compteurIdJson = 0
    texteResultat = {}
    # if(len(myresult) > 0):
    for i in myresult:
        json = {
            "idCalendrier" : i[0],
            "nomCalendrier" : i[1],
            "description" : i[2],
        }
        texteResultat[str(compteurIdJson)] = json
        compteurIdJson += 1
    return texteResultat
    # else:
    #     #Sinon on renvoit un message d'erreur
    #     texteResultat = "ID Unique de l'utilisateur n'existe pas"
    #     conn.close()
    # conn.close()
    
    #return {"result":texteResultat}

@app.route('/getSharedCalendars', methods= ['POST'])
def getSharedCalendar():
    global ip
    global bd
    # conn = cx_Oracle.connect(bd,"azerty",ip)
    conn = cx_Oracle.connect('baussenac/azerty@192.168.0.143:1521/xe')
    mycursor = conn.cursor()

    #Création du JSON
    content = request.json
    uniqueID = content['uniqueID']
    #Renvois tous les calendrier de l'utilisateur (partagés)
    mycursor.execute("""SELECT c.idCalendrier, c.nomCalendrier, c.description, Administrateur.uniqueID as AdministrateurCalendrier,Invite.uniqueID as InviteAuCalendrier 
FROM calendrier c, utilisateurcalendrier UtilisateurCalendrierInvite, utilisateur administrateur, utilisateur Invite WHERE 
c.idAdministrateur = administrateur.uniqueID AND Invite.uniqueID = :uniqueID AND c.idCalendrier = UtilisateurCalendrierInvite.idCalendrier
AND UtilisateurCalendrierInvite.idUtilisateur != c.idAdministrateur AND UtilisateurCalendrierInvite.idUtilisateur = Invite.uniqueID""",uniqueID=uniqueID)
    
    myresult = mycursor.fetchall()
    compteurIdJson = 0
    texteResultat = {}
    if(len(myresult) > 0):
        for i in myresult:
            json = {
                "idCalendrier" : i[0],
                "nomCalendrier" : i[1],
                "description" : i[2],
                "login" : i[4],
            }
            texteResultat[str(compteurIdJson)] = json
            compteurIdJson += 1
    else:
        texteResultat = {"vide" : "vide"}
    return texteResultat
    # else:
    #     #Sinon on renvoit un message d'erreur
    #     texteResultat = "ID Unique de l'utilisateur n'existe pas"
    #     conn.close()
    # conn.close()
    
    #return {"result":texteResultat}



@app.route('/generateToken', methods= ['POST'])
def generateToken():

    #nom cal + createur token + date creation    
    # int duree_validite
    date = datetime.timestamp(datetime.now())
    date_incremente = date + 3600

    #Création du JSON
    content = request.json

    #Récupération des données du JSON envoyé
    createur = content['name']
    nom_cal = content['calendrier']

    token = createur + "/" + nom_cal + "/" + str(date_incremente)
    print("date --> " , date)
    print("date incremente --> ", date_incremente)

    return token


@app.route('/verifToken', methods= ['POST'])
def verifToken():

    #Création du JSON
    content = request.json
    #Récupération des données du JSON envoyé
    token = content['token']
    token_decoupe = re.split(r'\W',token)

    print("timestamp incremente : ", token_decoupe[2])
    date_actuelle = datetime.timestamp(datetime.now())
    date_actuelle_decoupe = re.split(r'\W',str(date_actuelle))
    print("timestamp today :", date_actuelle_decoupe[0])

    if (date_actuelle_decoupe[0] > token_decoupe[2]) :
        print("heure actuelle : ", datetime.fromtimestamp(int(date_actuelle_decoupe[0])), " heure incremente ",datetime.fromtimestamp(int(token_decoupe[2])))
        return "token invalide" 
    else :
        print("heure actuelle : ", datetime.fromtimestamp(int(date_actuelle_decoupe[0])), " heure incremente ",datetime.fromtimestamp(int(token_decoupe[2])))
        return "token valide"

    