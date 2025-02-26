from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['chatapp1']

users = db['users']
rooms = db['rooms']
chats = db['chats']
counters = db['counters']

def increment(name):
    counter = counters.find_one_and_update(
        {'_id': name},  
        {'$inc': {'seq': 1}},  
        return_document=True  
    )
    return counter['seq']

def getRoom(snd,rcv):
    room = rooms.find_one({"$or": [{"members": [snd, rcv]},{"members": [rcv, snd]}]})
    return room 

def genMaxChatID(room):
    result = list(chats.aggregate([{'$match': {'room': room}},  {'$group': {'_id': '$room', 'max_chatid': {'$max': '$chatid'}}}]))[0]['max_chatid']
    return result 

def seeChats(username1,username2):
    snd = getID(username1)
    rcv = getID(username2)

    room = rooms.find_one({"$or": [{"members": [snd, rcv]},{"members": [rcv, snd]}]})
    array = []
    if room: 
        messages=chats.find({'room':room['room']})
        for message in messages:
            array.append([getUsername(message['snd']) , message['content']] )
    return array

def checkPassword(user_id,passcode):
    password = users.find_one({'id':user_id})['password']
    if password == passcode:
        return 1
    else:
        return 0
    
def seeChatsByID(snd,rcv):
    room = rooms.find_one({"$or": [{"members": [snd, rcv]},{"members": [rcv, snd]}]})
    array = []
    if room: 
        messages=chats.find({'room':room['room']})
        for message in messages:
            array.append([getUsername(message['snd']) , message['content']] )
    return [array , room['room']] 

def seeChatsByRoom(roomid):
    array = []
    messages=chats.find({'room':roomid})
    for message in messages:
        array.append([getUsername(message['snd']) , message['content']] )
    return array

def sendMessageByRoom(snd,roomid,message):
    chatid = increment("chatid")
    chats.insert_one({'chatid':chatid,'room':roomid,'snd':snd,'content':message})

def sendMessage(snd,rcv,message):
    room = rooms.find_one({'members': {'$all': [snd,rcv]}})

    if room :
        roomid = room['room']
    else :
        roomid = increment("room")
        rooms.insert_one({'room':roomid,'members':[snd,rcv],'isGroup':False})

    chatid = increment("chatid")
    chats.insert_one({'chatid':chatid,'room':roomid,'snd':snd,'content':message})

def check(username):
    if users.find_one({'username':username}):
        return 1
    else:
        return 0
    
def getID(username):
    id = users.find_one({'username':username})['id']
    return id

def getUsername(id):
    document = users.find_one({'id':id})
    return document['username']

def insertNewUser(username,password,name):
    userid = increment("id")
    users.insert_one({'id':userid,'username':username,'name':name,'password':password})

def getMembers(roomid):
    members = db.rooms.find_one(
        {"room": roomid},  
        {"_id": 0, "members": 1}  
    )

    return members

def getInbox(user_id):
    pipeline = [
                {
                    "$match": {
                        "members": user_id  
                    }
                },
                {
                    "$lookup": {
                        "from": "chats",
                        "localField": "room",
                        "foreignField": "room",
                        "as": "room_chats"
                    }
                },
                {
                    "$unwind": "$room_chats"  
                },
                {
                    "$match": {
                        "$or": [
                            { "room_chats.snd": user_id },  
                            { "$expr": { "$in": [user_id, "$members"] } }  
                        ]
                    }
                },
                {
                    "$group": {
                        "_id": "$room",
                        "last_chat_id": { "$max": "$room_chats.chatid" }  
                    }
                },
                {
                    "$sort": { "last_chat_id": -1 }  
                }
            ]

    datas = db.rooms.aggregate(pipeline)

    arrays=[]
    for data in datas:
        room_id = data['_id']
        members = getMembers(room_id)['members']
        if members[0]!=user_id:
            arrays.append({'room':room_id,'friend':members[0],'fname':getUsername(members[0])})
        else:
            arrays.append({'room':room_id,'friend':members[1],'fname':getUsername(members[1])})
    return arrays

def main_menu():
    while True:
        print("\n------CHAT INTERFACE------")
        print("1.Send message\n2.See chats\n3.See inbox\n4.Add new user\n5.Exit")
        choice=int(input("------>"))

        if choice == 1 :
            snd = input("Enter Your Username : ")
            rcv = input("Send to : ")

            if check(snd) and check(rcv):
                message = input("Write your message---->")
                sendMessage(getID(snd),getID(rcv),message)
                print("message sent successfull.....\n")
            else:
                print("Username dont exists\n")

        elif choice == 2:
            snd = input("Enter Your Username : ")
            rcv = input("Chats with : ")
            messages = seeChats(snd,rcv)
            for message in messages:
                print(message)

        elif choice == 3:
            snd = input("Enter Your Username : ")
            people  = getInbox(snd)

            for person in people:
                print(person)
        
        elif choice == 4:
            username = input("Enter Username : ")

            if not check(username):
                name = input("Enter Name : ")
                insertNewUser(username,name)
                print("new user added....")
            else:
                print("Account Already exists...")

        else:
            print("Thank you for using our service! Have a nice day")
            break


