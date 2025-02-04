1) run the eval server with command "python3 WebSocketServer.py"
    a) Eval server hosts a Wesocket server listening on port 8001. The web interface is connected to this server

2) Launch the web page "html/index.html"
    a) Enter the ip address of the machine where you are running the eval server
        i) Typically you would launch the webpage from the laptop on which you are running the eval server
            IN sucha a case you can use the ip address 127.0.0.1
    b) Enter the password your eval client expects ( This is your 16 char AES key)

NOTE:
1) Eval server also hosts a TCP server which waits for a connection from the "eval client" on Ultra96
2) To understand the code start from WebSocketServer.handler()
