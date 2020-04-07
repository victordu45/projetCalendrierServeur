from app import app
from flask import json, request, jsonify, send_file
import cx_Oracle

def ConnectionBD():
    return cx_Oracle.connect('ora8trd157_22', 'K+E4+7NLeXWE',
                             cx_Oracle.makedsn('dim-oracle.uqac.ca', 1521, 'dimdb'))

                             
@app.route('/getMessages', methods=['POST'])
def getMessages():
    global connexion
    conn = ConnectionBD()
    mycursor = conn.cursor()
    # Création du JSON
    content = request.json
    # Récupération des données du JSON envoyé
    idCalendrier = content['idCalendrier']
    offsetRecu = content['offset']
    uniqueID = content['uniqueID']
    # offsetMax = 20

    print("[1]offset recu  = ", offsetRecu)
    mycursor.execute(
        """SELECT count(idmessage) FROM message WHERE idcalendrier = :idCalendrier""", idCalendrier=idCalendrier)
    offset = mycursor.fetchone()
    print("offset ------> ", offset[0])
    offsetMax = offset[0]
    if(offsetRecu == -1):

        offset = offset[0] - 10
    else:
        offset = offsetRecu - 10

    print("[2]offset recu  = ", offsetRecu, " offsetMax = ", offsetMax)

    if(offsetRecu >= -1):

        mycursor.execute("""SELECT m.idmessage, m.contenu, m.datemessage, c.couleurTheme, m.idproprietaire, u.login 
    FROM   message m, calendrier c,utilisateur u WHERE c.idcalendrier = m.idcalendrier AND u.uniqueID = m.idproprietaire AND m.IDCALENDRIER = :idCalendrier
    ORDER BY datemessage
    OFFSET :offset ROWS FETCH NEXT :offsetMax ROWS ONLY """, idCalendrier=idCalendrier, offset=offset, offsetMax=offsetMax)

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
                    "idmessage": i[0],
                    "contenu": bytes(i[1].read()).decode("utf-8"),
                    "datemessage": i[2],
                    "color": i[3],
                    "offset": offset,
                    "idUtilisateur": id,
                    "login": i[5]
                }
                texteResultat[str(compteurIdJson)] = json
                compteurIdJson += 1
        else:
            texteResultat = {"vide": "vide"}
    else:
        texteResultat = {"vide": "vide"}
    conn.close()
    return texteResultat