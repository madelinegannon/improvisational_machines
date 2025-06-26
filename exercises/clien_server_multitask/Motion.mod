MODULE Motion
    VAR socketdev client_socket;
    VAR socketdev server_socket;
    VAR string client_ip;
    VAR string receive_string;
    VAR string IP_address_local:="127.0.0.1";
    VAR string IP_address_robot:="192.168.1.100";
    VAR num port:=1025;

    PROC Main()
        ConfJ\Off;
        ConfL\Off;
        Reset;
        WHILE TRUE DO
            IF go_home THEN
                GoHome speed_home;
                go_home:=FALSE;
            ELSEIF draw_square THEN
                DrawSquare center,width;
                draw_square:=FALSE;
            ELSEIF go_myGHmotion THEN
                MyGHMotion;
                go_myGHmotion:=FALSE;
            ELSE
            ENDIF
        ENDWHILE
    ENDPROC

    PROC DrawSquare(pos center,num width)
        ! Draw a 1 meter square in the XZ plane
        VAR pos corner_a;
        VAR pos corner_b;
        VAR pos corner_c;
        VAR pos corner_d;
        VAR orient rot:=[-0.707,0.707,0,0];
        VAR confdata config:=[0,0,0,0];
        VAR extjoint extax:=[0,0,0,0,0,0];

        corner_a:=[center.x+width/2.0,center.y,center.z+width/2.0];
        corner_b:=[center.x-width/2.0,center.y,center.z+width/2.0];
        corner_c:=[center.x-width/2.0,center.y,center.z-width/2.0];
        corner_d:=[center.x+width/2.0,center.y,center.z-width/2.0];

        MoveJ [corner_a,rot,config,extax],v500,z10,tool0;
        MoveL [corner_b,rot,config,extax],v500,z10,tool0;
        MoveL [corner_c,rot,config,extax],v500,z10,tool0;
        MoveL [corner_d,rot,config,extax],v500,z10,tool0;
        MoveL [corner_a,rot,config,extax],v500,z100,tool0;
    ENDPROC

    PROC MyCustomMotion()
        VAR confdata config:=[0,0,0,0];
        VAR extjoint extax:=[0,0,0,0,0,0];
        VAR speeddata speed:=v500;

        MoveAbsJ [[-122.0054,-49.6432,51.7564,-86.6235,-32.0677,86.0174],[0,0,0,0,0,0]],v500,z10,tool0;
        MoveL [[500,-1000,1750],[0.5,0.5,0.5,-0.5],config,extax],speed,fine,tool0;
        MoveL [[500,-1000,2750],[0.5,0.5,0.5,-0.5],config,extax],speed,fine,tool0;
        MoveL [[-500,-1000,2750],[0.5,0.5,0.5,-0.5],config,extax],speed,fine,tool0;
        MoveL [[-500,-1000,1750],[0.5,0.5,0.5,-0.5],config,extax],speed,fine,tool0;
    ENDPROC

    PROC MyGHMotion()
        MoveAbsJ [[-90,-58.5747,54.1368,180,-4.4379,-180],[0,9E9,9E9,9E9,9E9,9E9]],DefaultSpeed,fine,DefaultTool;
        MoveL [[135.232,-1000,1789.443],[0.5,0.5,0.5,-0.5],conf,[0,9E9,9E9,9E9,9E9,9E9]],DefaultSpeed,fine,DefaultTool\WObj:=DefaultFrame;
        MoveL [[259.508,-1000,1846.198],[0.5,0.5,0.5,-0.5],conf,[0,9E9,9E9,9E9,9E9,9E9]],DefaultSpeed,fine,DefaultTool\WObj:=DefaultFrame;
        MoveL [[362.76,-1000,1935.667],[0.5,0.5,0.5,-0.5],conf,[0,9E9,9E9,9E9,9E9,9E9]],DefaultSpeed,fine,DefaultTool\WObj:=DefaultFrame;
        MoveL [[436.623,-1000,2050.601],[0.5,0.5,0.5,-0.5],conf,[0,9E9,9E9,9E9,9E9,9E9]],DefaultSpeed,fine,DefaultTool\WObj:=DefaultFrame;
        MoveL [[475.114,-1000,2181.689],[0.5,0.5,0.5,-0.5],conf,[0,9E9,9E9,9E9,9E9,9E9]],DefaultSpeed,fine,DefaultTool\WObj:=DefaultFrame;
        MoveL [[475.114,-1000,2318.311],[0.5,0.5,0.5,-0.5],conf,[0,9E9,9E9,9E9,9E9,9E9]],DefaultSpeed,fine,DefaultTool\WObj:=DefaultFrame;
        MoveL [[436.623,-1000,2449.399],[0.5,0.5,0.5,-0.5],conf,[0,9E9,9E9,9E9,9E9,9E9]],DefaultSpeed,fine,DefaultTool\WObj:=DefaultFrame;
        MoveL [[362.76,-1000,2564.333],[0.5,0.5,0.5,-0.5],conf,[0,9E9,9E9,9E9,9E9,9E9]],DefaultSpeed,fine,DefaultTool\WObj:=DefaultFrame;
        MoveL [[259.508,-1000,2653.802],[0.5,0.5,0.5,-0.5],conf,[0,9E9,9E9,9E9,9E9,9E9]],DefaultSpeed,fine,DefaultTool\WObj:=DefaultFrame;
        MoveL [[135.232,-1000,2710.557],[0.5,0.5,0.5,-0.5],conf,[0,9E9,9E9,9E9,9E9,9E9]],DefaultSpeed,fine,DefaultTool\WObj:=DefaultFrame;
        MoveL [[0,-1000,2730],[0.5,0.5,0.5,-0.5],conf,[0,9E9,9E9,9E9,9E9,9E9]],DefaultSpeed,fine,DefaultTool\WObj:=DefaultFrame;
        MoveL [[-135.232,-1000,2710.557],[0.5,0.5,0.5,-0.5],conf,[0,9E9,9E9,9E9,9E9,9E9]],DefaultSpeed,fine,DefaultTool\WObj:=DefaultFrame;
        MoveL [[-259.508,-1000,2653.802],[0.5,0.5,0.5,-0.5],conf,[0,9E9,9E9,9E9,9E9,9E9]],DefaultSpeed,fine,DefaultTool\WObj:=DefaultFrame;
        MoveL [[-362.76,-1000,2564.333],[0.5,0.5,0.5,-0.5],conf,[0,9E9,9E9,9E9,9E9,9E9]],DefaultSpeed,fine,DefaultTool\WObj:=DefaultFrame;
        MoveL [[-436.623,-1000,2449.399],[0.5,0.5,0.5,-0.5],conf,[0,9E9,9E9,9E9,9E9,9E9]],DefaultSpeed,fine,DefaultTool\WObj:=DefaultFrame;
        MoveL [[-475.114,-1000,2318.311],[0.5,0.5,0.5,-0.5],conf,[0,9E9,9E9,9E9,9E9,9E9]],DefaultSpeed,fine,DefaultTool\WObj:=DefaultFrame;
        MoveL [[-475.114,-1000,2181.689],[0.5,0.5,0.5,-0.5],conf,[0,9E9,9E9,9E9,9E9,9E9]],DefaultSpeed,fine,DefaultTool\WObj:=DefaultFrame;
        MoveL [[-436.623,-1000,2050.601],[0.5,0.5,0.5,-0.5],conf,[0,9E9,9E9,9E9,9E9,9E9]],DefaultSpeed,fine,DefaultTool\WObj:=DefaultFrame;
        MoveL [[-362.76,-1000,1935.667],[0.5,0.5,0.5,-0.5],conf,[0,9E9,9E9,9E9,9E9,9E9]],DefaultSpeed,fine,DefaultTool\WObj:=DefaultFrame;
        MoveL [[-259.508,-1000,1846.198],[0.5,0.5,0.5,-0.5],conf,[0,9E9,9E9,9E9,9E9,9E9]],DefaultSpeed,fine,DefaultTool\WObj:=DefaultFrame;
        MoveL [[-135.232,-1000,1789.443],[0.5,0.5,0.5,-0.5],conf,[0,9E9,9E9,9E9,9E9,9E9]],DefaultSpeed,fine,DefaultTool\WObj:=DefaultFrame;
    ENDPROC

    PROC GoHome(speeddata speed)
        VAR jointtarget home_joints:=[[90,0,0,0,0,0],[0,0,0,0,0,0]];
        MoveAbsJ home_joints,speed,z0,tool0;
    ENDPROC
ENDMODULE