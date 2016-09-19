from __future__ import unicode_literals

from django.db import models

# Create your models here.

class Sender(models.Model):
    messengerSenderID = models.TextField()
    topic = models.TextField()

class Memory(models.Model):
    sender = models.ForeignKey(Sender)
    key = models.TextField()
    value = models.TextField()

class Conversation(models.Model):
    sender = models.ForeignKey(Sender)
    message = models.TextField()

    
