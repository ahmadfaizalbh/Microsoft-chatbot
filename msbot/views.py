from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from chatbot import Chat, reflections, multiFunctionCall
from .models import *
from django.db.utils import OperationalError, ProgrammingError
from background_task import background
import requests
import datetime
import json
import wikipedia
import os

# Create your views here.


app_client_id = "<Microsoft App ID>"
app_client_secret = "<Microsoft App Secret>"


def home(request):
    return render(request, "index.html")


def who_is(query, sessionID="general"):
    try:
        return wikipedia.summary(query)
    except:
        pass
    for new_query in wikipedia.search(query):
        try:
            return wikipedia.summary(new_query)
        except:
            pass
    return "Sorry I could not find any data related to '%s'" % query


class UserMemory:

    def __init__(self, sender_id, *args, **kwargs):
        self.senderID = sender_id
        self.update(*args, **kwargs)

    def __getitem__(self, key):
        try:
            return Memory.objects.get(sender__messengerSenderID=self.senderID, key=key).value
        except:
            raise KeyError(key)

    def __setitem__(self, key, value):
        try:
            memory = Memory.objects.get(sender__messengerSenderID=self.senderID, key=key)
            memory.value = value
            Memory.save()
        except:
            Memory.objects.create(sender__messengerSenderID=self.senderID, key=key, value=value)

    def update(self, *args, **kwargs):
        for k, v in dict(*args, **kwargs).items():
            self[k] = v

    def __delitem__(self, key):
        try:
            return Memory.objects.get(sender__messengerSenderID=self.senderID, key=key).delete()
        except:
            raise KeyError(key)

    def __contains__(self, key):
        return Memory.objects.filter(sender__messengerSenderID=self.senderID, key=key)


class UserConversation:

    def __init__(self, sender_id, *args):
        self.senderID = sender_id
        self.extend(list(*args))

    def __getitem__(self, index):
        try:
            conversation = Conversation.objects.filter(sender__messengerSenderID=self.senderID)
            return (conversation[index] if index >= 0 else conversation.order_by('-id')[-index - 1]).message
        except:
            raise IndexError("list index out of range")

    def __setitem__(self, index, message):
        try:
            conversations = Conversation.objects.filter(sender__messengerSenderID=self.senderID)
            conversation = (conversations[index] if index < 0 else conversations.order_by('-id')[-index])
            conversation.message = message
            conversation.save()
        except:
            raise IndexError("list assignment index out of range")

    def extend(self, items):
        for item in items:
            self.append(item)

    def append(self, message):
        Conversation.objects.create(sender=Sender.objects.get(messengerSenderID=self.senderID), message=message)

    def __delitem__(self, index):
        try:
            conversations = Conversation.objects.filter(sender__messengerSenderID=self.senderID)
            (conversations[index] if index < 0 else conversations.order_by('-id')[-index]).delete()
        except:
            raise IndexError("list index out of range")

    def pop(self):
        try:
            conversation = Conversation.objects.filter(sender__messengerSenderID=self.senderID).order_by('-id')[0]
            message = conversation.message
            conversation.delete()
            return message
        except:
            raise IndexError("pop from empty list")

    def __contains__(self, message):
        return Conversation.objects.filter(sender__messengerSenderID=self.senderID, message=message)


class UserTopic:

    def __init__(self, *args, **kwargs):
        self.update(*args, **kwargs)

    def __getitem__(self, sender_id):
        try:
            return Sender.objects.get(messengerSenderID=sender_id).topic
        except:
            raise KeyError(sender_id)

    def __setitem__(self, sender_id, topic):
        try:
            sender = Sender.objects.get(messengerSenderID=sender_id)
            sender.topic = topic
            sender.save()
        except:
            Sender.objects.create(messengerSenderID=sender_id, topic=topic)

    def update(self, *args, **kwargs):
        for k, v in dict(*args, **kwargs).items():
            self[k] = v

    def __delitem__(self, sender_id):
        try:
            return Sender.objects.get(messengerSenderID=sender_id).delete()
        except:
            pass

    def __contains__(self, sender_id):
        return Sender.objects.filter(messengerSenderID=sender_id)


class UserSession:

    def __init__(self, obj_class, *args, **kwargs):
        self.objClass = obj_class
        self.update(*args, **kwargs)

    def __getitem__(self, sender_id):
        try:
            return self.objClass(Sender.objects.get(messengerSenderID=sender_id).messengerSenderID)
        except:
            raise KeyError(sender_id)

    def __setitem__(self, sender_id, val):
        Sender.objects.get_or_create(messengerSenderID=sender_id)
        self.objClass(sender_id, val)

    def update(self, *args, **kwargs):
        for k, v in dict(*args, **kwargs).items():
            self[k] = v

    def __delitem__(self, sender_id):
        try:
            return Sender.objects.get(messengerSenderID=sender_id).delete()
        except:
            raise KeyError(sender_id)

    def __contains__(self, sender_id):
        return Sender.objects.filter(messengerSenderID=sender_id)


class MyChat(Chat):

    def __init__(self, *arg, **karg):
        super(MyChat, self).__init__(*arg, **karg)
        self._memory = UserSession(UserMemory, self._memory)
        self.conversation = UserSession(UserConversation, self.conversation)
        self.topic.topic = UserTopic(self.topic.topic)
        self.start_new_session = self._startNewSession


def initiate_chat(*arg, **karg):
    try:
        return MyChat(*arg, **karg)
    except (OperationalError, ProgrammingError):  # No DB exist
        print("error No DB exist")
        return Chat(*arg, **karg)


chat = initiate_chat(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  "chatbotTemplate",
                                  "Example.template"
                                  ),
                     reflections,
                     call=multiFunctionCall({"whoIs": who_is}))


def respond(service_url, reply_to_id, from_data,
            recipient_data, message, message_type, conversation):
    url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": app_client_id,
        "client_secret": app_client_secret,
        "scope": "https://api.botframework.com/.default"
    }
    response = requests.post(url, data)
    response_data = response.json()
    response_url = service_url + "v3/conversations/%s/activities/%s" % (conversation["id"], reply_to_id)
    requests.post(
        response_url,
        json={
            "type": message_type,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f%zZ"),
            "from": from_data,
            "conversation": conversation,
            "recipient": recipient_data,
            "text": message,
            "replyToId": reply_to_id
        },
        headers={
            "Authorization": "%s %s" % (response_data["token_type"], response_data["access_token"])
        }
    )


@background(schedule=1)
def initiate_conversation(data):
    conversation_id = data["id"]
    message = 'Welcome to NLTK-Chat demo.'
    sender_id = data["conversation"]["id"]
    chat.start_new_session(sender_id)
    chat.conversation[sender_id].append(message)
    respond(data["serviceUrl"],
            conversation_id,
            data["recipient"],
            {"id": sender_id},
            message,
            "message",
            data["conversation"])


@background(schedule=1)
def respond_to_client(data):
    conversation_id = data["id"]
    message = data["text"]
    sender_id = data["conversation"]["id"]
    chat.attr[sender_id] = {'match': None, 'pmatch': None, '_quote': False, 'substitute': True}
    chat.conversation[sender_id].append(message)
    message = message.rstrip(".! \n\t")
    result = chat.respond(message, sessionID=sender_id)
    chat.conversation[sender_id].append(result)
    respond(
        data["serviceUrl"],
        conversation_id,
        data["recipient"],
        data["from"],
        result,
        "message",
        data["conversation"]
    )
    del chat.attr[sender_id]


def conversation_handler(request):
    data = json.loads(request.body)
    # Send text message
    if data["type"] == "conversationUpdate":
        initiate_conversation(data)
    if data["type"] == "message":
        respond_to_client(data)
    return HttpResponse("It's working")


@csrf_exempt
def web_hook(request):
    if request.method == "POST":
        return conversation_handler(request)
    return HttpResponse("Invalid request method")



