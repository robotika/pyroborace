|    Signal          |    Start Byte    |    Type     |    Units           |    Description                                                                 |
|--------------------|------------------|-------------|--------------------|--------------------------------------------------------------------------------|
|    SteerAng        |    0             |    float    |    deg             |    “+” – left, “-“ - right                                                     |
|    AccelRequest    |    4             |    float    |    N∙m or % gas    |    Overall torque request or gas pedal percentage   (depending on CtrlMode)    |
|    BrakeRequest    |    8             |    float    |    % brake         |    brake pedal request (0 to 1)                                                |
|    GearPos         |    12            |    int32    |    -               |    gear position: -1 – reverse,    0 – neutral, 1 - drive                      |
|    CtrlMode        |    16            |    uint8    |    -               |    control mode:   3 – torque request, N∙m   11 –gas pedal request, %          |
|    Ctr             |    20            |    uint8    |    -               |    the simulator checks if controller is alive using   this counter            |
