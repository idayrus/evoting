from sys import argv

try:
    port = 8081

    if len(argv) > 1:
        port = int(argv[1])

    # Import
    from app import app

    # Run
    app.run(host='0.0.0.0', port=port, debug=True)

except Exception as e:
    print("Something went wrong, process terminated...")
    print("Error Report: " + str(e))
