# Microsoft-chatbot
Microsoft chatbot build using NLTK-Chatbot and django

# To Running This App in Microsoft Bot Emulator
1. [Download Emulator](https://c2rsetup.officeapps.live.com/c2r/download.aspx?productReleaseID=O365ProPlusRetail&platform=Def&language=en-us&TaxRegion=sg&correlationId=af2dda53-a9e9-49ef-8077-1164dfa45dd5&token=0a28bd4e-8b5b-4b39-bf26-bafa58a196cb&version=O16GA&source=O15OLSO365&Br=4)
2. Install Emulator
3. in command prompt
   ```sh
    git clone https://github.com/ahmadfaizalbh/Microsoft-chatbot.git
    cd Microsoft-chatbot
    pip install -r requirements.txt
    python manage.py makemigrations
    python manage.py migrate
    python manage.py runserver
   ```
4. `Microsoft-chatbot/bot/settings.py` set `DEBUG = True`
5. open another command prompt and execute the following
   ```sh
    cd Microsoft-chatbot
    python manage.py process_tasks
   ```
6. open Emulator
7. Add an endpoint for your bot with Endpoint url `http://localhost:8000/messaging/` and name `localhost` and save
8. open chat and start discussing with the bot
    


## To Run This App in Production
1. Install postgreSQL follow the instruction in page [How to install and use postgresql on ubuntu 14.04](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-postgresql-on-ubuntu-14-04)
2. in shell prompt run  
   ```sh
    git clone https://github.com/ahmadfaizalbh/Microsoft-chatbot.git
   ```
3. Go to [Azure Portal](http://portal.azure.com/)
4. Create a microsoft bot  - [Follow](https://docs.microsoft.com/en-us/azure/bot-service/bot-service-quickstart-registration?view=azure-bot-service-3.0&viewFallbackFrom=azure-bot-service-4.0)
5. Generate <Microsoft App Secret> and then update below lines in `Microsoft-chatbot/bot/settings.py`
   ```python
    DEBUG = False
    APP_CLIENT_ID = `<Microsoft App ID>`
    APP_CLIENT_SECRET = `<Microsoft App Secret>`
   ```
6. in `Microsoft-chatbot/bot/settings.py` also set `ALLOWED_HOSTS` with list of domain names
7. create DB `chatbot` with username `app_user` and password `InfoBotPassword` in postgreSQL or change the credential in settings as per your configuration
   ```sql
    create database chatbot;
    create user app_user with encrypted password 'InfoBotPassword';
    grant all privileges on database chatbot to app_user;
   ```
8. in shell prompt run  
   ```sh
    cd Microsoft-chatbot
    pip install -r requirements.txt
    python manage.py makemigrations
    python manage.py migrate
   ```
9. run `python manage.py process_tasks` in background (put it in `/etc/rc.local` with appropriate path to python and manage.py)
10. configure apache2 config file for this project
11. install [Let's Encrypt](https://letsencrypt.org/)
12. restart server

