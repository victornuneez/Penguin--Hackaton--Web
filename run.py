from app import create_app

app = create_app()

if __name__ == '__main__':
    # debug=True permite ver errores en vivo (Crucial para principiantes)
    app.run(debug=True)