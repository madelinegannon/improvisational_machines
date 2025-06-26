MODULE Motion

    PROC Main()
        ConfJ\Off;
        ConfL\Off;
        TPWrite "STARTING ROBOT: "+name;
        Reset;
        ResetTargets;
        WHILE TRUE DO
            IF go_home THEN
                GoHome speed_home;
                go_home:=FALSE;
            ELSEIF update_target_joints THEN
                ! Do Move
                update_target_joints:=FALSE;
            ELSEIF update_target_pose THEN
                ! Do Move
                update_target_pose:=FALSE;
            ELSEIF update_target_pos THEN
                ! Do Move
                update_target_pos:=FALSE;
            ELSEIF update_target_orient THEN
                ! Do Move
                update_target_orient:=FALSE;
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

    PROC ResetTargets()
        VAR robtarget pose;
        VAR jointtarget joint;

        ! Get current values
        pose:=CRobT();
        joint:=CJointT();

        target_position:=pose.trans;
        target_pose.trans:=pose.trans;
        target_orientation:=pose.rot;
        target_pose.rot:=target_orientation;
        target_joints:=joint.robax;
    ENDPROC

    PROC GoHome(speeddata speed)
        MoveAbsJ home_joints,speed,z0,tool0;
    ENDPROC

    !*******************************************************
    !************ ADD CUSTOM PROCEDURES BELOW **************
    !*******************************************************

    ! Example: Draws a square based on centroid and width
    PROC DrawSquare(pos center,num width)
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

    ! Example: Copy/Paste Routines from Rhino/Grasshopper's Robots Plugin
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

ENDMODULE