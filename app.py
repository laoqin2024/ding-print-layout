from app import create_app


# Legacy entrypoint: keep `python3 app.py` working,
# but delegate all logic to the refactored application factory.
app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)