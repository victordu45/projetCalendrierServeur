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
    offsetRecu = content['offset']
    # offsetMax = 20

    mycursor.execute("""    
        SELECT * 
        FROM(
            SELECT idmessage, contenu, datemessage, couleurTheme, idproprietaire, login, ROWNUM r
            FROM (SELECT m.idmessage, m.contenu, m.datemessage, c.couleurTheme, m.idproprietaire, u.login 
                from message m, calendrier c,utilisateur u
                WHERE c.idcalendrier = m.idcalendrier 
                AND u.uniqueID = m.idproprietaire 
                AND m.IDCALENDRIER = :idCalendrier
                order by datemessage
                )
            )
        WHERE r >= 5 
        AND ROWNUM < 15;
    """)

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
        texteResultat = {"messages": "il n'y a pas plus de messages dans le groupe !"}
    conn.close()
    return texteResultat