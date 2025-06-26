MODULE Server_Basic
    VAR socketdev client_socket;
    VAR socketdev server_socket;
    VAR string client_ip;
    VAR string receive_string;
    VAR string IP_address_local:="127.0.0.1";
    VAR string IP_address_robot:="192.168.1.100";
    VAR num port:=1025;

    PROC Main()
        StartServer;
        WHILE TRUE DO
            Receive;
        ENDWHILE
    ENDPROC

    PROC StartServer()
        TPWrite "Starting Server";
        ! Bind to the Server Socket
        SocketCreate server_socket;
        SocketBind server_socket,IP_address_local,port;
        SocketListen server_socket;

        ! Wait for a connection
        TPWrite "Waiting for connection...";
        SocketAccept server_socket,client_socket\ClientAddress:=client_ip,\Time:=WAIT_MAX;
        TPWrite "Connected to client: "+client_ip;
        TPWrite "Listening for commands...";
    ENDPROC

    PROC Receive()
        SocketReceive client_socket\Str:=receive_string;
        TPWrite "Client wrote: "+receive_string;
        SocketSend client_socket\Str:="Hello from server!";
    ENDPROC
ENDMODULE