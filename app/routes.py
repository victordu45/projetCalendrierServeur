from app import app
from flask import json, request, jsonify, send_file
import cx_Oracle
import datetime
import re
from datetime import date
from datetime import datetime, timedelta
import time
from . import chat_service

connexion = " "


def ConnectionBD():
    return cx_Oracle.connect('ora8trd157_22', 'K+E4+7NLeXWE',
                             cx_Oracle.makedsn('dim-oracle.uqac.ca', 1521, 'dimdb'))

@app.route('/login', methods=['POST'])
def conn_bdd():
    global connexion

    # conn = cx_Oracle.connect(bd,"azerty",ip)
    conn = ConnectionBD()
    mycursor = conn.cursor()

    # Création du JSON
    content = request.json

    # Récupération des données du JSON envoyé
    user = content['user']
    password = content['password']

    # Creation cursor
    mycursor.execute(
        """SELECT uniqueID FROM Utilisateur WHERE login = :login and password = :password""", login=user, password=password)

    # Exécution de la requête sql
    myresult = mycursor.fetchone()
    print(myresult)
    uniqueID = myresult[0]

    # Si la longueur du resultat est égale a 1 alors le login et le mot de passe correspondent
    if(len(myresult) == 1):
        conn.close()
        # On renvoit alors true
        return {"result": "added", "uniqueID": uniqueID}
    conn.close()
    return {"value": "Ca marche pas"}  # Sinon on renvoit false


@app.route('/register', methods=['POST'])
def testBD():
    global connexion
    conn = ConnectionBD()
    mycursor = conn.cursor()

    # Création du JSON
    content = request.json

    # Récupération des données du JSON envoyé
    login = content['login']
    password = content['password']
    name = content['name']
    surname = content['surname']
    mail = content['mail']
    color = content['color']

    dateNow = datetime.now()
    dateNow = dateNow.strftime("%d%m%Y%H%M%S-%f")
    uniqueID = login.upper()+'-'+dateNow

    # Creation cursor
    mycursor.execute(
        """SELECT * FROM Utilisateur WHERE login = :login """, login=login)

    # Exécution de la requête sql
    myresult = mycursor.fetchall()

    if(len(myresult) != 0):
        return {"result": "Login déjà utilisé"}
    # Creation cursor
    # mycursor.execute("""SELECT * FROM Utilisateur WHERE email = :mail""", mail = mail)

    # Exécution de la requête sql
    # myresult = mycursor.fetchall()
    a = 0
    # if(len(myresult) != 0):
    #     mail = 'Erreur'
    #     a = 1
    # else:
    #     login = ''

    date_actuelle = date.today()
    # Si a est égale a 1 aucun user ne possede le login ou adresse mail rentré
    if(len(login) > 0):
       # On peut alors créer le nouveau user avec son mot de passe, son nom, son prénom et son login
        mycursor.execute("""INSERT INTO Utilisateur VALUES (:uniqueID, :login, :password, :mail, '0623605498','125' ,:date_actuelle ,:surname, :name)""",
                         uniqueID=uniqueID, login=login, password=password, mail=mail, date_actuelle=date_actuelle, surname=surname, name=name)

        mycursor.execute(
            """INSERT INTO calendrier (nomCalendrier, idAdministrateur, description, couleurTheme) VALUES ('PERSO', :uniqueID, 'Personal Calendar', 'test')""", uniqueID=uniqueID)
        mycursor.execute(
            """SELECT idCalendrier FROM calendrier WHERE nomCalendrier = 'PERSO' and idAdministrateur = :uniqueID""", uniqueID=uniqueID)
        myresult = mycursor.fetchone()
        idCalendrier = myresult[0]
        mycursor.execute("""INSERT INTO utilisateurCalendrier (idCalendrier, idUtilisateur, dateAjoutInvite, idUtilisateurCalendrier, droits) VALUES (:idCalendrier, :uniqueID, sysdate, ug_idutilisateurcalendrier_seq.nextval, 'w')""",
                         idCalendrier=idCalendrier, uniqueID=uniqueID)
        mycursor.execute(
            """UPDATE calendrier SET couleurTheme = :color WHERE idadministrateur = :uniqueID""", uniqueID=uniqueID, color=color)

        # texteResultat = "added"
        conn.commit()
        conn.close()
        return {"result": "added", "Login": login, 'Mail': mail}
    else:
        # Sinon on renvoit un message d'erreur
        conn.close()
        return {"erreur": "Le login ne peut pas être vide"}


@app.route('/addNewEvent', methods=['POST'])
def addNewEvent():
    global connexion
    conn = ConnectionBD()
    mycursor = conn.cursor()

    # Création du JSON
    content = request.json

    uniqueID = content['uniqueID']
    idCalendar = content['idCalendar']
    nom = content['nom']
    dateDebut = content['dateDebut']
    heureDebut = content['heureDebut']
    dateFin = content['dateFin']
    heureFin = content['heureFin']
    description = content['description']

    dateDebutConcatene = dateDebut + " " + heureDebut
    date_debut = datetime.strptime(dateDebutConcatene, '%Y-%m-%d %H:%M')
    dateFinConcatene = dateFin + " " + heureFin
    date_fin = datetime.strptime(dateFinConcatene, '%Y-%m-%d %H:%M')
    # print(dateDebutConcatene + "  " + dateFinConcatene)

    dateNow = datetime.now()
    dateNow = dateNow.strftime("%d%m%Y%H%M%S-%f")
    nomId = nom
    nomId = nomId.replace(" ", "_")[:28] +'-' + dateNow
    print(nomId, len(nomId))
    idEvenement = nomId.upper()

    try: 

        mycursor.execute("""INSERT INTO evenement (idEvenement,datedebut,nomevenement,description,datefin) VALUES (:idEvenement,:dateDebut,:nomEvenement,:description,:dateFin) """,
                        idEvenement=idEvenement, dateDebut=date_debut, nomEvenement=nom, description=description, dateFin=date_fin)
        mycursor.execute("""INSERT INTO calendrierEvenement (idcalendrier,idevenement) VALUES (:idCalendrier,:idEvenement) """,
                        idCalendrier=idCalendar, idEvenement=idEvenement)
    except cx_Oracle.Error as e:
        return {"result" : str(e)}

    conn.commit()
    conn.close()
    return {"result" : "added"}


@app.route('/getEventsFromPersonalCalendar', methods=['POST'])
def getEventsFromPersonalCalendar():
    global connexion

    # conn = cx_Oracle.connect(bd,"azerty",ip)
    conn = ConnectionBD()
    mycursor = conn.cursor()

    # Création du JSON
    content = request.json

    uniqueID = content['uniqueID']
    idCalendar = content['idCalendar']
    print(idCalendar)
    mycursor.execute("""SELECT e.nomEvenement, c.couleurTheme,to_char(e.dateDebut,'YYYY-MM-DD HH24:MI'),to_char(e.dateFin, 'YYYY-MM-DD HH24:MI'), e.description,e.idEvenement FROM evenement e, calendrierevenement ce, calendrier c WHERE
    e.idEvenement = ce.idEvenement AND ce.idCalendrier = c.idCalendrier AND ce.idCalendrier = :idCalendrier ORDER BY e.dateDebut """, idCalendrier=idCalendar)
    myresult = mycursor.fetchall()
    compteurIdJson = 0
    texteResultat = {}
    json = {}
    if(len(myresult) > 0):
        for i in myresult:
            json = {
                "nomEvenement": i[0],
                "couleurTheme": i[1],
                "dateDebut": i[2],
                "dateFin": i[3],
                # "description" : i[4].read(),
                "idEvenement" : i[5]
            }
            texteResultat[str(compteurIdJson)] = json
            compteurIdJson += 1
    else:
        texteResultat = {'vide': 'vide'}
    conn.close()
    return texteResultat


@app.route('/getEventsFromDay', methods=['POST'])
def getEventsFromDay():
    global connexion

    # conn = cx_Oracle.connect(bd,"azerty",ip)
    conn = ConnectionBD()
    mycursor = conn.cursor()

    # Création du JSON
    content = request.json
    print(content)
    uniqueID = content['uniqueID']
    idCalendar = content['idCalendar']
    aDate = content['aDay']

    print(idCalendar)
    mycursor.execute("""SELECT e.nomEvenement, c.couleurTheme,to_char(e.dateDebut,'YYYY-MM-DD HH24:MI') as dtDebut,to_char(e.dateFin, 'YYYY-MM-DD HH24:MI'), e.description,e.dateDebut,e.idEvenement FROM evenement e, calendrierevenement ce, calendrier c WHERE 
    e.idEvenement = ce.idEvenement AND ce.idCalendrier = c.idCalendrier AND ce.idCalendrier = :idCalendrier AND to_char(e.dateDebut,'YYYY-MM-DD') = to_char(to_date(:aDate,'YYYY-MM-DD'),'YYYY-MM-DD') ORDER BY e.dateDebut """, idCalendrier=idCalendar, aDate=aDate)
    myresult = mycursor.fetchall()
    compteurIdJson = 0
    texteResultat = {}
    json = {}
    if(len(myresult) > 0):
        for i in myresult:
            json = {
                "nomEvenement": i[0],
                "couleurTheme": i[1],
                "dateDebut": i[2],
                "dateFin": i[3],
                # "description" : i[4].read(),
                "idEvenement" : i[6]
            }
            texteResultat[str(compteurIdJson)] = json
            compteurIdJson += 1
    else:
        texteResultat = {'vide': 'vide'}
    conn.close()
    return texteResultat


@app.route('/getPersonalCalendar', methods=['POST'])
def getPersonalCalendar():
    global connexion
    conn = ConnectionBD()
    mycursor = conn.cursor()

    # Création du JSON
    content = request.json
    uniqueID = content['uniqueID']
    # Renvois tous les calendrier de l'utilisateur (perso)
    mycursor.execute(
        """SELECT c.idCalendrier, c.nomCalendrier, c.description, c.couleurtheme FROM calendrier c WHERE c.idAdministrateur = :uniqueID  """, uniqueID=uniqueID)

    myresult = mycursor.fetchall()
    compteurIdJson = 0
    texteResultat = {}
    # if(len(myresult) > 0):
    for i in myresult:
        json = {
            "idCalendrier": i[0],
            "nomCalendrier": i[1],
            "description": i[2],
            "couleurTheme": i[3]
        }
        texteResultat[str(compteurIdJson)] = json
        compteurIdJson += 1
    return texteResultat
    # else:
    #     #Sinon on renvoit un message d'erreur
    #     texteResultat = "ID Unique de l'utilisateur n'existe pas"
    #     conn.close()
    # conn.close()

    # return {"result":texteResultat}


@app.route('/getSharedCalendars', methods=['POST'])
def getSharedCalendar():
    global connexion
    conn = ConnectionBD()
    mycur = conn.cursor()

    # Création du JSON
    content = request.json
    uniqueID = content['uniqueID']
    # uniqueID = uniqueID[1:]

    # Renvois tous les calendrier de l'utilisateur (partagés)

    mycur.execute("""SELECT c.idCalendrier, c.nomCalendrier, c.description, c.couleurtheme, Administrateur.uniqueID as AdministrateurCalendrier,Invite.uniqueID as InviteAuCalendrier FROM calendrier c, utilisateurcalendrier UtilisateurCalendrierInvite, utilisateur administrateur, utilisateur Invite WHERE 
c.idAdministrateur = administrateur.uniqueID AND c.idCalendrier = UtilisateurCalendrierInvite.idCalendrier
AND UtilisateurCalendrierInvite.idUtilisateur != c.idAdministrateur AND UtilisateurCalendrierInvite.idUtilisateur = Invite.uniqueID AND Invite.uniqueID = :id""", id=uniqueID)

    myresult = mycur.fetchall()
    print("myresult", myresult)
    compteurIdJson = 0
    texteResultat = {}
    print("len myresult", len(myresult))
    if(len(myresult) > 0):
        for i in myresult:
            json = {
                "idCalendrier": i[0],
                "nomCalendrier": i[1],
                "description": i[2],
                "login": i[4],
                "color": i[3]
            }
            texteResultat[str(compteurIdJson)] = json
            compteurIdJson += 1
    else:
        texteResultat = {"vide": "vide"}
    return texteResultat
    # else:
    #     #Sinon on renvoit un message d'erreur
    #     texteResultat = "ID Unique de l'utilisateur n'existe pas"
    #     conn.close()
    # conn.close()

    # return {"result":texteResultat}


@app.route('/getMembersWritable', methods=['POST'])
def getMembersWritable():
    global connexion
    conn = ConnectionBD()
    mycur = conn.cursor()

    content = request.json
    idcal = content['idCal']

    mycur.execute("""SELECT u.login, uc.droits FROM utilisateur u, utilisateurcalendrier uc WHERE u.uniqueid = uc.idutilisateur AND idcalendrier = :idCal""", idCal=idcal)
    myresult = mycur.fetchall()
    resultat = {}
    for i in myresult:
        resultat[i[0]] = i[1] == 'w'

    print(resultat)

    return resultat


@app.route('/getMembers', methods=['POST'])
def getMembers():
    global connexion
    conn = ConnectionBD()
    mycur = conn.cursor()

    content = request.json
    idcal = content['idCal']

    mycur.execute("""SELECT * FROM utilisateur WHERE uniqueID IN (SELECT idUtilisateur FROM utilisateurCalendrier WHERE idCalendrier = :idCal) ORDER BY login ASC""", idCal=idcal)

    myresult = mycur.fetchall()
    texteResultat = {}
    compteurIdJson = 0
    if(len(myresult) > 0):
        for i in myresult:
            json = {
                "login": i[0],
            }
            texteResultat[str(compteurIdJson)] = json
            compteurIdJson += 1
    else:
        texteResultat = {"vide": "vide"}
    return texteResultat


@app.route('/getInfos', methods=['POST'])
def getInfos():
    global connexion
    conn = ConnectionBD()
    mycur = conn.cursor()

    content = request.json

    idcal = content['idCal']
    mycur.execute(
        """SELECT login FROM utilisateur WHERE uniqueID = (SELECT idAdministrateur FROM calendrier WHERE idCalendrier = :idCal)""", idCal=idcal)
    myresult = mycur.fetchone()
    admin = myresult[0]
    mycur.execute(
        """SELECT * FROM utilisateurCalendrier WHERE idCalendrier = :idCal""", idCal=idcal)
    myresult = mycur.fetchall()
    compteur = len(myresult)

    return {'admin': admin, 'nombre': compteur}


@app.route('/generateToken', methods=['POST'])
def generateToken():

    # nom cal + createur token + date creation
    # int duree_validite
    date = datetime.timestamp(datetime.now())
    print("date", date)
    date_incremente = date + 3600

    # Création du JSON
    content = request.json

    # Récupération des données du JSON envoyé
    # Unique ID du createur
    createur = content['name']
    # Id du calendrier
    nom_cal = content['calendrier']

    token = createur + "/" + nom_cal + "/" + str(date_incremente)
    print("date --> ", date)
    print("date incremente --> ", date_incremente)

    texteResultat = {"token": token}
    print("token", token)
    return jsonify(texteResultat)


@app.route('/verifToken', methods=['POST'])
def verifToken():
    global connexion

    conn = ConnectionBD()
    mycursor = conn.cursor()

    # Création du JSON
    content = request.json
    # Récupération des données du JSON envoyé
    uniqueID = ""
    token = content['token']
    uniqueID = content['uniqueID']
    print('token : ', token)
    print('unique id --> ', uniqueID)
    # print('idcalendar', )
    token_decoupe = re.split(r'\W', token)
    token_decoupe_slash = token.split('/')
    # print(token_decoupe_slash)
    # print("token_decoupe 0 --> ",token_decoupe[0])
    # print("token_decoupe 1 --> ",token_decoupe[1])
    # print("timestamp incremente : ", token_decoupe[2])
    date_actuelle = datetime.timestamp(datetime.now())
    date_actuelle_decoupe = re.split(r'\W', str(date_actuelle))
    # print("timestamp today :", date_actuelle_decoupe[0])

    if (date_actuelle_decoupe[0] > token_decoupe[6]):
        print("heure actuelle : ", datetime.fromtimestamp(int(
            date_actuelle_decoupe[0])), " heure incremente ", datetime.fromtimestamp(int(token_decoupe[6])))
        print("Token invalide")
        return "token invalide"
    else:
        print("heure actuelle : ", datetime.fromtimestamp(int(
            date_actuelle_decoupe[0])), " heure incremente ", datetime.fromtimestamp(int(token_decoupe[6])))
        print("Token valide")
        print("dans if", token_decoupe_slash[1], uniqueID)
        mycursor.execute("""INSERT INTO utilisateurCalendrier (idcalendrier, idutilisateur, idutilisateurcalendrier, dateajoutinvite, droits) values (:idCalendrier,:idUtilisateur,ug_idutilisateurcalendrier_seq.nextval,sysdate, 'r')""",
                         idCalendrier=token_decoupe_slash[1], idUtilisateur=uniqueID)
        conn.commit()
        return "token valide"


@app.route('/addCalendar', methods=['POST'])
def addCalendar():
    global connexion
    # unique id
    # id calendar
    conn = ConnectionBD()
    mycursor = conn.cursor()

    # Création du JSON
    content = request.json

    uniqueID = content['uniqueID']
    nom_calendrier = content['nom_calendrier']
    description = content["description"]
    couleurtheme = content['couleurtheme']
    print("uniqueID --> ", uniqueID)
    print("nom_calendrier --> ", nom_calendrier)
    print("description --> ", description)
    print("couleurtheme --> ", couleurtheme)

    mycursor.execute("""INSERT INTO calendrier (nomcalendrier,idadministrateur,description,couleurtheme) VALUES (:nomcalendrier,:idadministrateur,:description,:couleurtheme) """,
                     nomcalendrier=nom_calendrier, idadministrateur=uniqueID, description=description, couleurtheme=couleurtheme)
    conn.commit()
    conn.close()
    return {"result": "succes"}


@app.route('/getProfilCalendar', methods=['POST'])
def getProfilCalendar():
    global connexion
    conn = ConnectionBD()
    mycursor = conn.cursor()

    content = request.json

    uniqueID = content['uniqueID']
    idCalend = content['idCalendrier']

    print('idCalendrier = ', idCalend)
    return {"data": "data"}


@app.route('/getProfil', methods=['POST'])
def getProfil():
    global connexion
    conn = ConnectionBD()
    mycursor = conn.cursor()

    content = request.json

    uniqueID = content['uniqueID']

    mycursor.execute(
        """SELECT login, email, nom, prenom FROM utilisateur WHERE uniqueID = :uniqueID""", uniqueID=uniqueID)

    myresult = mycursor.fetchall()

    if(len(myresult) > 0):
        for i in myresult:
            json = {
                "login": i[0],
                "email": i[1],
                "nom": i[2],
                "prenom": i[3]
            }

    return json

# @app.route('/SuppUser', methods= ['POST'])
# def SuppUser():


#     conn = cx_Oracle.connect('baussenac/azerty@192.168.0.143:1521/xe')
#     mycursor = conn.cursor()

#     #Création du JSON
#     content = request.json

#     #Récupération des données du JSON envoyé
#     idUtilisateur = content['idUtilisateur']
#     print("idUtilisateur --> ",idUtilisateur)

#     #Creation cursor
#     mycursor.execute("""SELECT * FROM Utilisateur WHERE uniqueID = :idUtilisateur """,
#     idUtilisateur = idUtilisateur)

#     #Exécution de la requête sql
#     myresult = mycursor.fetchall()
#     date_actuelle = date.today()

#     #Si la longueur du resultat est égale a 0 aucun user ne possede le login rentré
#     if(len(myresult) == 0):
#         texteResultat = "Cet utilisateur n'existe pas"
#         conn.close()
#     else:
#         mycursor.execute("""DELETE FROM Utilisateur WHERE uniqueID = :idUtilisateur """,idUtilisateur=idUtilisateur)
#         mycursor.execute("""DELETE FROM SuivirMessageLu WHERE login = :login """,login=login)
#         mycursor.execute("""DELETE FROM UtilisateurCalendrier WHERE idUtilisateur = :idUtilisateur """,idUtilisateur=idUtilisateur)
#         mycursor.execute("""DELETE FROM Utilisateur WHERE login = :login """,login=login)
#         mycursor.execute("""DELETE FROM Utilisateur WHERE login = :login """,login=login)


#         texteResultat = "deleted"
#         conn.commit()
#         conn.close()

#     return {"result":texteResultat}


@app.route('/suppEvent', methods=['POST'])
def suppEvent():
    global connexion
    conn = ConnectionBD()
    # Création du JSON
    content = request.json
    # Récupération des données du JSON envoyé
    idEvenement = content['idEvenement']
    print("idEvenement --> ", idEvenement)
    # Creation cursor
    mycursor.execute("""SELECT * FROM Evenement WHERE idEvenement = :idEvenement """,
                     idEvenement=idEvenement)
    # Exécution de la requête sql
    myresult = mycursor.fetchall()
    date_actuelle = date.today()
    # Si la longueur du resultat est égale a 0 aucun user ne possede le login rentré
    if(len(myresult) == 0):
        texteResultat = "Cet evenement n'existe pas"
        conn.close()
    else:
        mycursor.execute(
            """DELETE FROM Evenement WHERE idEvenement = :idEvenement """, idEvenement=idEvenement)
        texteResultat = "deleted"
        conn.commit()
        conn.close()
    return {"result": texteResultat}


@app.route('/modifEvent', methods=['POST'])
def modifEvent():
    global connexion

    conn = ConnectionBD()
    conn = ConnectionBD()
    content = request.json
    # Récupération des données du JSON envoyé
    idEvenement = content['idEvenement']
    dateDebut = content['dateDebut']
    nomEvenement = content['nomEvenement']
    description = content['description']
    dateFin = content['dateFin']
    print("idEvenement --> ", idEvenement)
    # Creation cursor
    mycursor.execute("""SELECT * FROM Evenement WHERE idEvenement = :idEvenement """,
                     idEvenement=idEvenement)
    # Exécution de la requête sql
    myresult = mycursor.fetchall()
    date_actuelle = date.today()
    # Si la longueur du resultat est égale a 0 aucun user ne possede le login rentré
    if(len(myresult) == 0):
        texteResultat = "Cet evenement n'existe pas"
        conn.close()
    else:
        mycursor.execute("""UPDATE Evenement SET dateDebut = :dateDebut, nomEvenement = :nomEvenement, description = :description, dateFin = :dateFin    WHERE idEvenement = :idEvenement """,
                         idEvenement=idEvenement, dateDebut=dateDebut, dateFin=dateFin, description=description, nomEvenement=nomEvenement)
        texteResultat = "updated"
        conn.commit()
        conn.close()
    return {"result": texteResultat}




@app.route('/getUsersFromCalendar', methods=['POST'])
def getUsersFromCalendar():
    global connexion
    conn = ConnectionBD()
    mycursor = conn.cursor()
    conn = ConnectionBD()
    # Récupération des données du JSON envoyé

    mycur.execute("""SELECT Invite.uniqueID , Invite.login, C.idcalendrier, c.idadministrateur,uc.droits FROM calendrier C, utilisateurcalendrier uc, utilisateur Invite WHERE c.idcalendrier = uc.idcalendrier AND Invite.uniqueID = uc.idutilisateur AND c.idadministrateur != Invite.uniqueID
AND c.idcalendrier = :id """, id=uniqueID)

    myresult = mycur.fetchall()
    print("myresult", myresult)
    compteurIdJson = 0
    texteResultat = {}
    print("len myresult", len(myresult))
    if(len(myresult) > 0):
        for i in myresult:
            json = {
                "idInvite": i[0],
                "loginInvite": i[1],
                "idCalendrier": [2],
                "droits": i[4]
            }
            texteResultat[str(compteurIdJson)] = json
            compteurIdJson += 1
    else:
        texteResultat = {"vide": "vide"}
    conn.close()
    return texteResultat

@app.route('/createPayement', methods=['POST'])
def createPayement():

    content = request.json

    participants = content['participants']
    montant_paye = content['montant_paye']
    montant_total = sum(montant_paye)
    print("participants  --> ", participants)
    print("montant paye --> ", montant_paye)
    print("montant total --> ", montant_total)
    montant_a_paye_pers = montant_total/len(participants)
    print("montant que chaque personne doit payer", montant_a_paye_pers)

    dico = []
    # donne cout total
    for a in range(len(participants)):
        liste = []
        dico.append(liste)
        dico[a].append(montant_paye[a]-montant_a_paye_pers)
        dico[a].append(participants[a])
    print("dico ---> ", dico)
    dico.sort()
    print("dico trie ---> ", dico)

    plus_petit = dico[0][0]
    print("plus_petit", plus_petit)
    plus_grand = dico[len(dico)-1][0]
    print("plus_grand", plus_grand)
    print()

    while dico[0][0] != 0 and dico[len(dico)-1][0] != 0:
        dico[0][0] = dico[0][0] + dico[len(dico)-1][0]
        print(dico[len(dico)-1][1], " recevra ",
              dico[len(dico)-1][0], " de ", dico[0][1])
        dico[len(dico)-1][0] = dico[len(dico)-1][0] - dico[len(dico)-1][0]
        # print("dico apres echange boucle",dico)
        dico.sort()
        print("dico apres tri", dico)
        print()

    print("dico apres echange", dico)

    return "test okey"


@app.route('/isAdmin', methods=['POST'])
def isAdmin():
    global connexion
    conn = ConnectionBD()
    mycur = conn.cursor()

    conn = ConnectionBD()
    uniqueID = content['login']
    idCal = content['idCal']

    mycur.execute("""SELECT idadministrateur FROM calendrier WHERE idcalendrier = :idCal AND idadministrateur = :uniqueID""",
                  idCal=idCal, uniqueID=uniqueID)
    myresult = mycur.fetchall()
    if len(myresult) == 1:
        return {'result': 1}
    else:
        return {'result': 0}


@app.route('/changeDroits', methods=['POST'])
def changeDroits():
    global connexion
    conn = ConnectionBD()
    mycur = conn.cursor()

    content = request.json
    conn = ConnectionBD()
    idCal = content['idCal']

    for i in membres:
        print(membres[i])
        if membres[i]:
            mycur.execute(
                """SELECT uniqueID FROM utilisateur WHERE login = :membre""", membre=i)
            id = mycur.fetchone()
            id = id[0]
            mycur.execute(
                """UPDATE utilisateurcalendrier SET droits = 'w' WHERE idcalendrier = :idCal AND idutilisateur = :membre""", idCal=idCal, membre=id)
        else:
            mycur.execute(
                """SELECT uniqueID FROM utilisateur WHERE login = :membre""", membre=i)
            id = mycur.fetchone()
            id = id[0]
            mycur.execute(
                """UPDATE utilisateurcalendrier SET droits = 'r' WHERE idcalendrier = :idCal AND idutilisateur = :membre""", idCal=idCal, membre=id)

    conn.commit()
    conn.close()
    return {'result': 'added'}


@app.route("/newTransaction", method=["POST"])
def newTransaction():
    conn = connectionBD()
    conn.close()