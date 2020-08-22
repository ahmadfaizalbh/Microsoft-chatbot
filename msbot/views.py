from django.shortcuts import render
from chatbot import register_call
import requests
import wikipedia


def home(request):
    return render(request, "index.html")


@register_call("whoIs")
def who_is(query, session_id="general"):
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

