# zor-chat
simple chat application

Initialize
$ git clone https://github.com/alexanderzor/zor-chat

$ cd zor-chat

$ virtualenv venv

$ source venv/bin/activate

$ pip install -r requirements.txt

Database

$ python chat.py db init

$ python chat.py db migrate -m "first migration"

$ python chat.py db upgrade

Run the application

$ python run.py
