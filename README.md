# Microsoft-chatbot
Microsoft chatbot build using NLTK-Chatbot and django

## To run this app
1. Go to [https://dev.botframework.com/bots](https://dev.botframework.com/bots)
2. create a microsoft bot
3. Generate <Microsoft App Secret> and then update below lines in views.py 
  ```python
  app_client_id = `<Microsoft App ID>`
  app_client_secret = `<Microsoft App Secret>`
  ```

4. in shell prompt run
  ```sh
  sudo pip install -U django
  git clone https://github.com/ahmadfaizalbh/Chatbot.git
  cd Chatbot
  sudo setup.py install
  cd ../
  pip install wikipedia,mock,py_execute
  git clone https://github.com/ahmadfaizalbh/django-background-tasks.git
  cd django-background-tasks
  sudo python setup.py develop
  cd ../
  git clone https://github.com/ahmadfaizalbh/Microsoft-chatbot.git
  cd Microsoft-chatbot
  python manage.py makemigrations
  python manage.py migrate
  ```
5. run `python manage.py process_tasks` in background (put it in `/etc/rc.local` with appropriate path to python and manage.py)

6. configure apache2 config file for this project
7. install [Let's Encrypt](https://letsencrypt.org/)
8. restart server
