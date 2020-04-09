from flask import Flask, render_template
from flask_socketio import SocketIO, join_room,leave_room, send, emit
import cx_Oracle
from datetime import datetime



def connectionBD():
  return cx_Oracle.connect('ora8trd157_22', 'K+E4+7NLeXWE', cx_Oracle.makedsn('dim-oracle.uqac.ca',1521,'dimdb'))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

conn = connectionBD()
mycursor = conn.cursor()

mycursor.execute("""SELECT * FROM Utilisateur WHERE login = :login """,login = "Baptiste")
myresult = mycursor.fetchall()
print(len(myresult))
conn.close()

connected_users = []

@socketio.on("message")
def handle_msg(msg):
  print("message :",msg)
  #ajout message dans la bd par rapport à l'id du calendrier. 
  #ceux qui ont "rejoind la room" se voit modifier son dernier message lu
  conn = connectionBD()
  cursorInsertMsg = conn.cursor()

  proprietaire = msg["user"]
  contenuSocket = msg["msg"]
  idCalSocket = msg["room"]
  print(msg["user"])

  cursorInsertMsg.execute("""
  SELECT login
  FROM utilisateur
  WHERE uniqueId = :usr
  """, usr=proprietaire)
  (login,)=cursorInsertMsg.fetchone()

  cursorInsertMsg.execute("""
  SELECT SYSTIMESTAMP FROM dual
  """)
  (date,)=cursorInsertMsg.fetchone()
  print(date)


  send({"user" : login, "message" : contenuSocket, "createdAt" : date, "idUtilisateur" : proprietaire},room = msg["room"])

  cursorInsertMsg.execute("""insert into message (contenu,idCalendrier,idProprietaire) values (utl_raw.cast_to_raw(:contenu), :idCal, :idProprio)""",
    contenu=contenuSocket, idCal=idCalSocket,idProprio=proprietaire)

  conn.commit()
  conn.close()

@socketio.on("join")
def join_to_room(data):  
  global connected_users
  username = data["username"]
  room = data["room"]
  join_room(room)
  connected_users.append(username)
  print(connected_users)

  
  emit('users-changed',{'user' : username, 'event' : "join"}, room=room)
  print(username + 'joined the room : '+ room)

@socketio.on("left")
def leave_to_room(data):
  global connected_users
  username = data["username"]
  room = data["room"]
  leave_room(room)
  connected_users.pop(username)
  print(connected_users)
  emit('users-changed',{'user' : username, 'event' : "left"}, room=room)
  print(username + ' left the room : '+ room)


 
if __name__ == '__main__':
    socketio.run(app, port=5001, host='0.0.0.0')