from mist_main import app as application

if __name__ == "__main__":
    try:
        application.run(debug=True)
    except Exception:
        application.logger.exception('Failed')
