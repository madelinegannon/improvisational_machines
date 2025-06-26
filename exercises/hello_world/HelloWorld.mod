MODULE HelloWorld
    PROC Main()              
        TPWrite "Hello, World";
        GoHome;
    ENDPROC 
    
    PROC GoHome()
        VAR jointtarget home_joints := [[-90,0,0,0,0,0],[0,0,0,0,0,0]];
        MoveAbsJ home_joints, v1000, z0, tool0;
    ENDPROC
ENDMODULE