from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from chatbot import reflections, multiFunctionCall
from .handler import initiate_chat
from background_task import background
from django.conf import settings
import requests
import datetime
import json
import wikipedia
import os

# Create your views here.


def home(request):
    return render(request, "index.html")


def who_is(query, sessionID="general"):
    try:
        return wikipedia.summary(query)
    except requests.exceptions.SSLError:
        return "Sorry I could not search online due to SSL error"
    except:
        pass
    for new_query in wikipedia.search(query):
        try:
            return wikipedia.summary(new_query)
        except:
            pass
    return "Sorry I could not find any data related to '%s'" % query


chat = initiate_chat(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                  "chatbotTemplate",
                                  "Example.template"
                                  ),
                     reflections,
                     call=multiFunctionCall({"whoIs": who_is}))


def respond(service_url, reply_to_id, from_data,
            recipient_data, message, message_type, conversation):
    if settings.APP_CLIENT_ID != "<Microsoft App ID>":
        url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
        data = {
            "grant_type": "client_credentials",
            "client_id": settings.APP_CLIENT_ID,
            "client_secret": settings.APP_CLIENT_SECRET,
            "scope": "https://api.botframework.com/.default"
        }
        response = requests.post(url, data)
        response_data = response.json()
        headers = {
            "Authorization": "%s %s" % (response_data["token_type"], response_data["access_token"])
        }
    else:
        headers = {}
    if service_url[-1] != "/":
        service_url += "/"
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
        headers=headers
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



