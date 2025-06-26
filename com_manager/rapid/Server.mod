MODULE Server
    VAR socketdev client_socket;
    VAR socketdev server_socket;
    VAR string client_ip;
    VAR string receive_string;

    PROC Main()
        StartServer;
        WHILE TRUE DO
            Receive;
        ENDWHILE
    ERROR
        IF ERRNO=ERR_SOCK_CLOSED THEN
            TPWrite "Client Socket Closed.";
            StartServer;
        ENDIF
    ENDPROC

    PROC StartServer()
        TPWrite "Starting Server";
        ! Bind to the Server Socket
        SocketCreate server_socket;
        IF RobOS() THEN
            ! If connected to Robot Controller
            SocketBind server_socket,IP_address_robot,port_robot;
        ELSE
            ! If connect to Virtual Controller
            SocketBind server_socket,IP_address_local,port_local;
        ENDIF
        SocketListen server_socket;

        ! Wait for a connection
        TPWrite "Waiting for connection...";
        SocketAccept server_socket,client_socket\ClientAddress:=client_ip,\Time:=WAIT_MAX;
        TPWrite "Connected to client: "+client_ip;
        TPWrite "Listening for commands...";
    ERROR
        IF ERRNO=ERR_SOCK_TIMEOUT THEN
            RETRY;
        ELSEIF ERRNO=ERR_SOCK_CLOSED THEN
            RETURN ;
        ELSE
            ! No error recovery handling
            TPWrite "Socket Error...Cannot Recover.";
        ENDIF
    ENDPROC

    PROC Receive()
        SocketReceive client_socket\Str:=receive_string;
        TPWrite "Client wrote: "+receive_string;
        SocketSend client_socket\Str:="Recieved: "+receive_string;
        ParseMessage receive_string;
    ERROR
        IF ERRNO=ERR_SOCK_TIMEOUT THEN
            RETRY;
        ELSEIF ERRNO=ERR_SOCK_CLOSED THEN
            TPWrite "Socket Closed. Restarting Server";
            StartServer;
            RETRY;
        ELSEIF ERRNO=ERR_SOCK_TIMEOUT THEN
            RETRY;
        ELSEIF ERRNO=ERR_STRTOOLNG THEN
            TPWrite "STRING TOO LONG!.";
        ELSE
            ! No error recovery handling
            TPWrite "Socket Error...Cannot Recover.";
        ENDIF
    ENDPROC

    PROC ParseMessage(string message)
        VAR string key;
        VAR string val;
        VAR num msg_length;
        VAR num split_index;
        VAR bool ok;
        VAR string center_str;
        VAR string width_str;

        ! Check if we have a complete message
        msg_length:=StrMatch(message,1,";");
        split_index:=StrMatch(message,1,"/");

        IF msg_length>StrLen(message) OR split_index>msg_length THEN
            TPWrite "A Corrupt or Incomplete Message was Received: "+message;
        ELSE
            key:=StrPart(message,1,split_index-1);
            val:=StrPart(message,split_index+1,msg_length-split_index-1);
            TPWrite "key: "+key;
            TPWrite "val: "+val;
            IF key="GoHome" THEN
                ! Expects: [v_tcp,v_orient,v_leax,v_reax]
                ok:=StrToVal(val,speed_home);
                IF NOT ok THEN
                    speed_home:=v500;
                ENDIF
                go_home:=TRUE;
            ELSEIF key="DrawSquare" THEN
                ! Expects: [x,y,z]|width
                split_index:=StrMatch(val,1,"|");
                center_str:=StrPart(val,1,split_index-1);
                width_str:=StrPart(val,split_index+1,StrLen(val)-split_index);
                TPWrite width_str;
                ok:=StrToVal(center_str,center);
                ok:=StrToVal(width_str,width);
                draw_square:=TRUE;
            ELSEIF key="GoGH" THEN
                ! Expects: GoGH/;
                go_myGHmotion:=TRUE;
            ENDIF
        ENDIF
    ENDPROC

ENDMODULE