MODULE MyFristModule
    PROC Main()       
        ConfJ\Off; ! These ask the robot to not monitor configdata
        ConfL\Off; ! These ask the robot to not monitor configdata
        
        TPWrite "Hello, World";
        GoHome v1000;
        DrawSquare;
        GoHome v200;
    ENDPROC 
    
    PROC DrawSquare()
        ! Draw a 1 meter square in the XZ plane
        VAR pos corner_a := [500, -1500, 2000+500];
        VAR pos corner_b := [-500, -1500, 2000+500];
        VAR pos corner_c := [-500, -1500, 2000-500];
        VAR pos corner_d := [500, -1500, 2000-500];
        VAR orient rot := [0.707,0.707,0,0]; ![qw, qx, qy, qz]
        VAR confdata config := [0,0,0,0];   ! Set to a default
        VAR extjoint extax := [0,0,0,0,0,0];! Set to a default

        MoveJ [corner_a, rot, config, extax], v500, z10, tool0;
        MoveL [corner_b, rot, config, extax], v500, z10, tool0;
        MoveL [corner_c, rot, config, extax], v500, z10, tool0;
        MoveL [corner_d, rot, config, extax], v500, z10, tool0;
        MoveL [corner_a, rot, config, extax], v500, z100, tool0;
    ENDPROC
    
    PROC GoHome(speeddata speed)
        VAR jointtarget home_joints := [[-90,0,0,0,0,0],[0,0,0,0,0,0]];
        MoveAbsJ home_joints, speed, z0, tool0;
    ENDPROC
ENDMODULE