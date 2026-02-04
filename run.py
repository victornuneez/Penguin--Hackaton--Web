from app import create_app
import socket

app = create_app()

if __name__ == '__main__':
    # debug=True permite ver errores en vivo (Crucial para principiantes)
    host_name = socket.gethostname()
    ip = socket.gethostbyname(host_name) 
    app.run(host=ip, debug=True)