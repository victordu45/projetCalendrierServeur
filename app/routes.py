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
    print('ok')
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
    color = content['color']


    dateNow = datetime.now()
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

        mycursor.execute("""INSERT INTO calendrier (nomCalendrier, idAdministrateur, description, couleurTheme) VALUES ('PERSO', :uniqueID, 'Personal Calendar', 'test')""", uniqueID=uniqueID)
        mycursor.execute("""SELECT idCalendrier FROM calendrier WHERE nomCalendrier = 'PERSO' and idAdministrateur = :uniqueID""", uniqueID=uniqueID)
        myresult = mycursor.fetchone()
        idCalendrier = myresult[0]
        mycursor.execute("""INSERT INTO utilisateurCalendrier (idCalendrier, idUtilisateur, dateAjoutInvite, idUtilisateurCalendrier, droits) VALUES (:idCalendrier, :uniqueID, sysdate, ug_idutilisateurcalendrier_seq.nextval, 'w')""", idCalendrier=idCalendrier, uniqueID=uniqueID)
        mycursor.execute("""UPDATE calendrier SET couleurTheme = :color WHERE idadministrateur = :uniqueID""", uniqueID=uniqueID, color=color)

        texteResultat = "added"
        conn.commit()
        conn.close()
    else:
        #Sinon on renvoit un message d'erreur
        texteResultat = "Ce login est déjà utilisé"
        conn.close()
    return {"result":texteResultat}

@app.route('/addNewEvent', methods= ['POST'])
def addNewEvent():
    global ip
    global bd
    # conn = cx_Oracle.connect(bd,"azerty",ip)
    conn = cx_Oracle.connect('baussenac/azerty@192.168.0.143:1521/xe')
    mycursor = conn.cursor()

    #Création du JSON
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
    idEvenement = nom.upper()+'-'+ dateNow
    print("type idEv  -->", type(idEvenement))
    print("type idCal -->", idEvenement)
    print("type date_debut  -->", type(date_debut))
    print(" date_debut -->", date_debut)
    print("type nom  -->", type(nom))
    print("nom -->", nom)
    print("type description  -->", type(description))
    print(" description -->", description)
    print("type date_fin  -->", type(date_fin))
    print(" date_fin -->", date_fin)

    mycursor.execute("""INSERT INTO evenement (idEvenement,datedebut,nomevenement,description,datefin) VALUES (:idEvenement,:dateDebut,:nomEvenement,:description,:dateFin) """,idEvenement=idEvenement, dateDebut = date_debut, nomEvenement = nom, description = description, dateFin = date_fin)
    mycursor.execute("""INSERT INTO calendrierEvenement (idcalendrier,idevenement) VALUES (:idCalendrier,:idEvenement) """,idCalendrier = idCalendar,idEvenement=idEvenement)
    
    conn.commit()
    conn.close()
    return "added"

@app.route('/getEventsFromPersonalCalendar', methods= ['POST'])
def getEventsFromPersonalCalendar():
    global ip
    global bd
    # conn = cx_Oracle.connect(bd,"azerty",ip)
    conn = cx_Oracle.connect('baussenac/azerty@192.168.0.143:1521/xe')
    mycursor = conn.cursor()

    #Création du JSON
    content = request.json

    uniqueID = content['uniqueID']
    idCalendar = content['idCalendar']
    print(idCalendar)
    mycursor.execute("""SELECT e.nomEvenement, c.couleurTheme,e.dateDebut,e.dateFin FROM evenement e, calendrierevenement ce, calendrier c WHERE 
    e.idEvenement = ce.idEvenement AND ce.idCalendrier = c.idCalendrier AND ce.idCalendrier = :idCalendrier """, idCalendrier = idCalendar)
    myresult = mycursor.fetchall()
    compteurIdJson = 0
    texteResultat = {}
    json = {}
    if(len(myresult) > 0):
        for i in myresult:
            json = {
                "nomEvenement" : i[0],
                "couleurTheme" : i[1],
                "dateDebut" : i[2],
                "dateFin" : i[3]
            
            }
            texteResultat[str(compteurIdJson)] = json
            compteurIdJson += 1
    else:
        texteResultat = {'vide' : 'vide'}
    conn.close()
    return texteResultat
    
    
    

@app.route('/getPersonalCalendar', methods= ['POST'])
def getPersonalCalendar():
    global ip
    global bd
    conn = cx_Oracle.connect('baussenac/azerty@192.168.0.143:1521/xe')
    mycursor = conn.cursor()

    #Création du JSON
    content = request.json
    uniqueID = content['uniqueID']
    #Renvois tous les calendrier de l'utilisateur (perso)
    mycursor.execute("""SELECT c.idCalendrier, c.nomCalendrier, c.description, c.couleurtheme FROM calendrier c 
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
            "couleurTheme" : i[3]
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
    conn = cx_Oracle.connect('baussenac/azerty@192.168.0.143:1521/xe')
    mycur = conn.cursor()

    #Création du JSON
    content = request.json
    uniqueID = content['uniqueID']
    # uniqueID = uniqueID[1:]
    
    #Renvois tous les calendrier de l'utilisateur (partagés)
    
    mycur.execute("""SELECT c.idCalendrier, c.nomCalendrier, c.description, c.couleurtheme, Administrateur.uniqueID as AdministrateurCalendrier,Invite.uniqueID as InviteAuCalendrier FROM calendrier c, utilisateurcalendrier UtilisateurCalendrierInvite, utilisateur administrateur, utilisateur Invite WHERE 
c.idAdministrateur = administrateur.uniqueID AND c.idCalendrier = UtilisateurCalendrierInvite.idCalendrier
AND UtilisateurCalendrierInvite.idUtilisateur != c.idAdministrateur AND UtilisateurCalendrierInvite.idUtilisateur = Invite.uniqueID AND Invite.uniqueID = :id""", id=uniqueID)

    myresult = mycur.fetchall()
    print("myresult" , myresult)
    compteurIdJson = 0
    texteResultat = {}
    print("len myresult" , len(myresult))
    if(len(myresult) > 0):
        for i in myresult:
            json = {
                "idCalendrier" : i[0],
                "nomCalendrier" : i[1],
                "description" : i[2],
                "login" : i[4],
                "color" : i[3]
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
    print("date",date)
    date_incremente = date + 3600

    #Création du JSON
    content = request.json

    #Récupération des données du JSON envoyé
    #Unique ID du createur
    createur = content['name']
    #Id du calendrier
    nom_cal = content['calendrier']

    token = createur + "/" + nom_cal + "/" + str(date_incremente)
    print("date --> " , date)
    print("date incremente --> ", date_incremente)

    texteResultat = {"token" : token}
    print("token", token)
    return jsonify(texteResultat)


@app.route('/verifToken', methods= ['POST'])
def verifToken():
    global ip
    global bd

    conn = cx_Oracle.connect('baussenac/azerty@192.168.0.143:1521/xe')
    mycursor = conn.cursor()

    #Création du JSON
    content = request.json
    #Récupération des données du JSON envoyé
    uniqueID = ""
    token = content['token']
    uniqueID = content['uniqueID']
    print('token : ', token)
    print('unique id --> ', uniqueID)
    # print('idcalendar', )
    token_decoupe = re.split(r'\W',token)
    token_decoupe_slash = token.split('/')
    # print(token_decoupe_slash)
    # print("token_decoupe 0 --> ",token_decoupe[0])
    # print("token_decoupe 1 --> ",token_decoupe[1])
    # print("timestamp incremente : ", token_decoupe[2])
    date_actuelle = datetime.timestamp(datetime.now())
    date_actuelle_decoupe = re.split(r'\W',str(date_actuelle))
    # print("timestamp today :", date_actuelle_decoupe[0])

    if (date_actuelle_decoupe[0] > token_decoupe[6]) :
        print("heure actuelle : ", datetime.fromtimestamp(int(date_actuelle_decoupe[0])), " heure incremente ",datetime.fromtimestamp(int(token_decoupe[6])))
        print("Token invalide")
        return "token invalide" 
    else :
        print("heure actuelle : ", datetime.fromtimestamp(int(date_actuelle_decoupe[0])), " heure incremente ",datetime.fromtimestamp(int(token_decoupe[6])))
        print("Token valide")
        print("dans if" , token_decoupe_slash[1], uniqueID)
        mycursor.execute("""INSERT INTO utilisateurCalendrier (idcalendrier, idutilisateur, idutilisateurcalendrier, dateajoutinvite, droits) values (:idCalendrier,:idUtilisateur,ug_idutilisateurcalendrier_seq.nextval,sysdate, 'r')""",idCalendrier=token_decoupe_slash[1], idUtilisateur=uniqueID)
        conn.commit()
        return "token valide"

@app.route('/addCalendar', methods= ['POST'])
def addCalendar():

    #unique id
    #id calendar
    conn = cx_Oracle.connect('baussenac/azerty@192.168.0.143:1521/xe')
    mycursor = conn.cursor()

    #Création du JSON
    content = request.json

    uniqueID = content['uniqueID']
    nom_calendrier = content['nom_calendrier']
    description = content["description"]
    couleurtheme = content['couleurtheme']
    print("uniqueID --> ", uniqueID)
    print("nom_calendrier --> ", nom_calendrier)
    print("description --> ", description)
    print("couleurtheme --> ", couleurtheme)
    


    mycursor.execute("""INSERT INTO calendrier (nomcalendrier,idadministrateur,description,couleurtheme) VALUES (:nomcalendrier,:idadministrateur,:description,:couleurtheme) """, nomcalendrier = nom_calendrier, idadministrateur = uniqueID, description = description, couleurtheme = couleurtheme)
    conn.commit()
    conn.close()
    return "succes"


@app.route('/getProfil', methods= ['POST'])
def getProfil():
    conn = cx_Oracle.connect('baussenac/azerty@192.168.0.143:1521/xe')
    mycursor = conn.cursor()

    content = request.json

    uniqueID = content['uniqueID']

    mycursor.execute("""SELECT login, email, nom, prenom FROM utilisateur WHERE uniqueID = :uniqueID""", uniqueID = uniqueID)

    myresult = mycursor.fetchall()

    if(len(myresult) > 0):
        for i in myresult:
            json = {
                "login" : i[0],
                "email" : i[1],
                "nom" : i[2],
                "prenom" : i[3]
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


@app.route('/suppEvent', methods= ['POST'])
def suppEvent():


    conn = cx_Oracle.connect('baussenac/azerty@192.168.0.143:1521/xe')
    mycursor = conn.cursor()
    # Création du JSON
    content = request.json
    # Récupération des données du JSON envoyé
    idEvenement = content['idEvenement']
    print("idEvenement --> ",idEvenement)
    #Creation cursor
    mycursor.execute("""SELECT * FROM Evenement WHERE idEvenement = :idEvenement """,
    idEvenement = idEvenement)
    #Exécution de la requête sql
    myresult = mycursor.fetchall()
    date_actuelle = date.today()
    #Si la longueur du resultat est égale a 0 aucun user ne possede le login rentré 
    if(len(myresult) == 0):
        texteResultat = "Cet evenement n'existe pas"
        conn.close()
    else:
        mycursor.execute("""DELETE FROM Evenement WHERE idEvenement = :idEvenement """,idEvenement=idEvenement)
        texteResultat = "deleted"
        conn.commit()
        conn.close()
    return {"result":texteResultat}



@app.route('/modifEvent', methods= ['POST'])
def modifEvent():


    conn = cx_Oracle.connect('baussenac/azerty@192.168.0.143:1521/xe')
    mycursor = conn.cursor()
    # Création du JSON
    content = request.json
    # Récupération des données du JSON envoyé
    idEvenement = content['idEvenement']
    dateDebut = content['dateDebut']
    nomEvenement = content['nomEvenement']
    description = content['description']
    dateFin = content['dateFin']


    print("idEvenement --> ",idEvenement)
    #Creation cursor
    mycursor.execute("""SELECT * FROM Evenement WHERE idEvenement = :idEvenement """,
    idEvenement = idEvenement)
    #Exécution de la requête sql
    myresult = mycursor.fetchall()
    date_actuelle = date.today()
    #Si la longueur du resultat est égale a 0 aucun user ne possede le login rentré 
    if(len(myresult) == 0):
        texteResultat = "Cet evenement n'existe pas"
        conn.close()
    else:
        mycursor.execute("""UPDATE Evenement SET dateDebut = :dateDebut, nomEvenement = :nomEvenement, description = :description, dateFin = :dateFin    WHERE idEvenement = :idEvenement """,idEvenement=idEvenement,dateDebut=dateDebut,dateFin=dateFin,description=description,nomEvenement=nomEvenement)
        texteResultat = "updated"
        conn.commit()
        conn.close()
    return {"result":texteResultat}

@app.route('/getMessages',methods=['POST'])
def getMessages():
    conn = cx_Oracle.connect('baussenac/azerty@192.168.0.143:1521/xe')
    mycursor = conn.cursor()
    # Création du JSON
    content = request.json
    # Récupération des données du JSON envoyé
    idCalendrier = content['idCalendrier']
    uniqueID = content['uniqueID']
    mycursor.execute( """SELECT m.idmessage, m.contenu, m.datemessage, c.couleurTheme, m.idproprietaire 
FROM   message m, calendrier c WHERE c.idcalendrier = m.idcalendrier AND m.IDCALENDRIER = :idCalendrier
ORDER BY datemessage
OFFSET 0 ROWS FETCH NEXT 200 ROWS ONLY """, idCalendrier=idCalendrier)

    myresult = mycursor.fetchall()
    # print("myresult" , myresult)
    compteurIdJson = 0
    texteResultat = {}
    # print("len myresult" , len(myresult))
    if(len(myresult) > 0):
        for i in myresult:
            # print("type du contenu -->",type(i[1]))
            # print(bytes(i[1].read()).decode("utf-8"))
            if uniqueID == i[4]:
                id = uniqueID
            else:
                id = i[4] 
            json = {
                "idmessage" : i[0],
                "contenu" : bytes(i[1].read()).decode("utf-8"),
                "datemessage" : i[2],
                "color" : i[3],
                "idUtilisateur" : id
            }
            texteResultat[str(compteurIdJson)] = json
            compteurIdJson += 1
    else:
        texteResultat = {"vide" : "vide"}
    conn.close()
    return texteResultat

@app.route('/createMessage', methods= ['POST'])
def createMessage():

    conn = cx_Oracle.connect('baussenac/azerty@192.168.0.143:1521/xe')
    mycursor = conn.cursor()
    # Création du JSON
    content = request.json
    # Récupération des données du JSON envoyé
    idCalendrier = content['idCalendrier']
    contenu = content['contenu'].encode('utf-8')
    contenu = contenu.hex()
    uniqueID = content['uniqueID']

    # contenu.encode("hex")
    #id_redacteur = content['id_redacteur']
    
    mycursor.execute("""INSERT INTO message (idProprietaire,contenu,idCalendrier) VALUES (:uniqueID,:contenu,:idCalendrier) """, uniqueID = uniqueID, contenu = contenu, idCalendrier = idCalendrier)
    conn.commit()
    conn.close()
    return {"result":"insertion succes"}


@app.route('/getUsersFromCalendar', methods= ['POST'])
def getUsersFromCalendar():

    conn = cx_Oracle.connect('baussenac/azerty@192.168.0.143:1521/xe')
    mycursor = conn.cursor()
    # Création du JSON
    content = request.json
    # Récupération des données du JSON envoyé
    
    mycur.execute("""SELECT Invite.uniqueID , Invite.login, C.idcalendrier, c.idadministrateur,uc.droits FROM calendrier C, utilisateurcalendrier uc, utilisateur Invite WHERE c.idcalendrier = uc.idcalendrier AND Invite.uniqueID = uc.idutilisateur AND c.idadministrateur != Invite.uniqueID
AND c.idcalendrier = :id """, id=uniqueID)

    myresult = mycur.fetchall()
    print("myresult" , myresult)
    compteurIdJson = 0
    texteResultat = {}
    print("len myresult" , len(myresult))
    if(len(myresult) > 0):
        for i in myresult:
            json = {
                "idInvite" : i[0],
                "loginInvite" : i[1],
                "idCalendrier" : [2],
                "droits" : i[4]
            }
            texteResultat[str(compteurIdJson)] = json
            compteurIdJson += 1
    else:
        texteResultat = {"vide" : "vide"}
    conn.close()
    return texteResultat
    
    


# @app.route('/suppMessage', methods = ['POST'])
# def suppMessage():    

    
@app.route('/createPayement', methods = ['POST'])
def createPayement():

    content = request.json
    
    participants = content['participants']
    montant_total = content['montant_total']
    montant_paye = content['montant_paye']
    print("participants  --> ",participants)
    print("montant paye --> ",montant_paye)
    print("montant total --> ", montant_total)
    total = 0
    #donne cout total
    for a in range(len(participants)):
        print(participants[a] , " a paye " , montant_paye[a] , " sur " , montant_total)
        total += int(montant_paye[a])
    cout_par_personne = total/len(participants)
    tab_cout = []
    for a in range(len(participants)):
        tab_cout.append(cout_par_personne - int(montant_paye[a]))
    dico = {}
    for a in range(len(participants)):
        #cle = nom_participant : val_attribue 
        dico[participants[a]] = tab_cout[a]    
    print("dico --> ",dico)
    dico = sorted(dico.items(), key=lambda t: t[1])
    print("dico trie --> ", dico )
    for a in range(len(dico)):
        print("dico --> ", dico[a])
        print(dico[a][0] , " est a  --> " , dico[a][1])
    #affecter plus petit a plus grand dans le dico 
    #tant que toutes les valeurs ne sont pas 0 on réitère
    #on affecte le plus possible pour arriver a 0
    #une fois arrivé à 0 on swap sur celui d'après


    for a in range(len(dico)):
        reducteur = 1
        while dico[a][1] != 0.0 :
            print(reducteur)
            # print("le plus endette : ", dico[a])
            # print("le moins endette : ", dico[len(dico)-a-1])
            if dico[len(dico)-reducteur][1] == 0 :
                reducteur += 1
            else :
                if dico[a][1] < dico[len(dico)-reducteur][1] :
                    print("droite plus grand que gauche")
                    # print(dico[a][1], " : ", dico[len(dico)-reducteur][1])
                    # dico[len(dico)-reducteur][1]
                    dico[a][1] = dico[a][1] + dico[len(dico)-reducteur][1]
                    reducteur += 1
                else : 
                    dico[len(dico)-reducteur][1] += dico[a][1]
                    print("gauche plus grand que droite")
                    reducteur += 1



    return "test okey"