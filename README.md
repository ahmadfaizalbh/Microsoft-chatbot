# Microsoft-chatbot
Microsoft chatbot build using NLTK-Chatbot and django

## To run this app
1. Install postgreSQL follow the instruction in page [How to install and use postgresql on ubuntu 14.04](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-postgresql-on-ubuntu-14-04)
2. in shell prompt run
  ```sh
  pip install -r requirements.txt
  git clone https://github.com/ahmadfaizalbh/Microsoft-chatbot.git
  ```
3. Go to [https://dev.botframework.com/bots](https://dev.botframework.com/bots)
4. create a microsoft bot
5. Generate <Microsoft App Secret> and then update below lines in views.py 
  ```python
  app_client_id = `<Microsoft App ID>`
  app_client_secret = `<Microsoft App Secret>`
  ```
6. create DB `chatbot` with username `app_user` and password `InfoBotPassword` in postgreSQL or change the credential in settings as per your configuration
  ```sql
  create database chatbot;
  create user app_user with encrypted password 'InfoBotPassword';
  grant all privileges on database chatbot to app_user;
  ```
7. in shell prompt run  
  ```sh
  cd Microsoft-chatbot
  python3 manage.py makemigrations
  python3 manage.py migrate
  ```
8. run `python manage.py process_tasks` in background (put it in `/etc/rc.local` with appropriate path to python and manage.py)
9. configure apache2 config file for this project
10. install [Let's Encrypt](https://letsencrypt.org/)
11. restart server
