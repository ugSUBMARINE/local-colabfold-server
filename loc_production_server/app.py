from pre_app import create_app

app = create_app()
if __name__ == "__maine__":
    app.run(host="0.0.0.0", debug=True)
