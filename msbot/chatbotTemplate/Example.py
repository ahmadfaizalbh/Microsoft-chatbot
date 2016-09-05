from chatbot import Chat,reflections,multiFunctionCall
import wikipedia

def whoIs(query,sessionID="general"):
    try:
        return wikipedia.summary(query)
    except:
        for newquery in wikipedia.search(query):
            try:
                return wikipedia.summary(newquery)
            except:
                pass
    return "I don't know about "+query
        
    

call = multiFunctionCall({"whoIs":whoIs})
firstQuestion="Hi, how are you?"
chat=Chat("Example.template", reflections,call=call)

senderID="1,2,3"
chat._startNewSession(senderID)             
chat.conversation[senderID].append('Say "Hello"')
#firstQuestion='Say "Hello"'
#chat.converse(firstQuestion,sessionID=senderID)
message=""
while message!="bye":
    message=raw_input(">")
    chat.conversation[senderID].append(message)
    result = chat.respond(message,sessionID=senderID)               
    chat.conversation[senderID].append(result)
    print result
