from sys import argv
import waitress

if __name__ == '__main__':
    try:
        # Get Port
        port = 8081
        if len(argv) > 1:
            port = int(argv[1])

        # Import
        from app import app

        # Serve
        waitress.serve(app, port=port, host="127.0.0.1", threads=4)

    except Exception as e:
        print("Something went wrong, process terminated...")
        print("Error Report: " + str(e))
