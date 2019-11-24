from chatbot import Chat
from .models import Memory, Conversation, Sender
from django.db.utils import OperationalError, ProgrammingError


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
