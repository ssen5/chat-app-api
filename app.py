from flask import Flask, render_template , request ,jsonify
import a
from flask_cors import CORS  
import json

app = Flask(__name__)
CORS(app, origins=["*"])

@app.route('/')
def home():
    return jsonify({"message":"Youre on the Home Page"})

@app.route('/check')
def check():
    snd = str(request.args.get('snd'))
    user_id = a.getID(snd)
    
    return jsonify( {'user':user_id} )

@app.route('/createnewuser',methods=['POST'])
def createNewUser():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    name = data.get('name')

    try:
        x=a.getID(username)
        return jsonify({"isValid":0})
    except:
        a.insertNewUser(username,password,name)

    return jsonify({"isValid":1})



@app.route('/sendmessage',methods=['POST'])
def sendIt():
    data = request.get_json()
    room = data.get('room')
    snd = data.get('snd')
    content = data.get('content')
    rcv=data.get('rcv')

    if room:
        a.sendMessageByRoom(snd,room,content)
    else:
        a.sendMessage(snd,rcv,content)
    
    return jsonify({"status":1})
    
@app.route('/show', methods=['POST'])
def show():  
    query1 = request.form.get('query1')
    query2 = request.form.get('query2')
    
    chats = a.seeChats(query1,query2)
    data = {'array':chats}

    return jsonify(data)

@app.route('/checkpassword')
def checkpassword():
    snd = int(request.args.get('snd'))
    password = request.args.get('ps')
    x = a.checkPassword(snd,password)
    
    return jsonify({'isValid':x})

@app.route('/seechats')
def seechats():
    sender = int(request.args.get('snd'))
    receiver = int(request.args.get('rcv'))

    chats = a.seeChatsByID(sender,receiver)
    data = {'array':chats[0],'sender':a.getUsername(sender),'snd':sender,'room':chats[1],'rcv':a.getUsername(receiver)}

    return jsonify(data)

@app.route('/seechatsbyroom')
def seechatsbyroom():
    sender = int(request.args.get('snd'))
    room = int(request.args.get('room'))

    chats = a.seeChatsByRoom(room)
    data = {'array':chats,'sender':a.getUsername(sender),'room':room}

    return jsonify(data)

@app.route('/newchatu')
def newchat():  
    sender = int(request.args.get('snd'))
    data = {'snd':sender,'sender':a.getUsername(sender)}
    return jsonify(data)

@app.route('/inbox')
def inbox():
    user_id = int(request.args.get('snd'))

    data = {'snd':user_id,'sender':a.getUsername(user_id),'array':a.getInbox(user_id)}

    return jsonify(data)

@app.route('/getchats')
def getchats():
    sender = int(request.args.get('snd'))
    room = int(request.args.get('room'))

    chats = a.seeChatsByRoom(room)
    data = {'array':chats,'sender':a.getUsername(sender)}

    return jsonify(data)

if __name__ == '__main__':
    app.run()







