from app import app
from flask import json, request, jsonify, send_file
import cx_Oracle

def ConnectionBD():
    return cx_Oracle.connect('ora8trd157_22', 'K+E4+7NLeXWE',
                             cx_Oracle.makedsn('dim-oracle.uqac.ca', 1521, 'dimdb'))


@app.route('/getMessages', methods=['POST'])
def getMessages():
    conn = ConnectionBD()
    mycursor = conn.cursor()

    # Création du JSON
    content = request.json
    # Récupération des données du JSON envoyé
    idCalendrier = content['idCalendrier']
    offset = content['offset']
    # offset est la "page" de message qu'on va envoyer, ex: 1 = les premiers 15messages, 2, les 15messages suivants, etc..

    mycursor.execute("""SELECT count(idmessage)
    FROM message
    WHERE idcalendrier = :idCal
    """, idCal=idCalendrier)

    (nbr_message_total,) = mycursor.fetchone()
    
    pointeur_message = nbr_message_total - offset
    
    mycursor.execute("""    
        SELECT * 
        FROM(
            SELECT idmessage, contenu, datemessage, couleurTheme, idproprietaire, login, ROWNUM r
            FROM (SELECT m.idmessage, m.contenu, m.datemessage, c.couleurTheme, m.idproprietaire, u.login 
                from message m, calendrier c,utilisateur u
                WHERE c.idcalendrier = m.idcalendrier 
                AND u.uniqueID = m.idproprietaire 
                AND m.IDCALENDRIER = :idCalendrierQuery
                order by datemessage
                )
            )
        WHERE r >= :offsetQuery 
        AND ROWNUM <= 15
    """, idCalendrierQuery=idCalendrier,offsetQuery=pointeur_message+1)

    myresult = mycursor.fetchall()
    # print("myresult" , myresult)
    compteurIdJson = 0
    texteResultat = []
    # print("len myresult" , len(myresult))
    if(len(myresult) > 0):
        for i in myresult:
            jsonM = {
                "idmessage": i[0],
                "message": bytes(i[1].read()).decode("utf-8"),
                "createdAt": i[2],
                "color": i[3],
                "offset": offset,
                "idUtilisateur": i[4],
                "user": i[5]
            }
            texteResultat.append(jsonM)
            compteurIdJson += 1
    else:
        texteResultat = ["il n'y a pas de message"]
    conn.close()
    return json.dumps(texteResultat)