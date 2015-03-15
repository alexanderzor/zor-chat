from gevent import monkey
from app import create_app, socketio
monkey.patch_all()

app = create_app(True)

if __name__ == '__main__':
    socketio.run(app)