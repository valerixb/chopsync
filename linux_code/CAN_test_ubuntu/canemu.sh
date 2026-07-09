#!/bin/bash

# speed setpoint 49
cansend can0 2C0#40.00.20.00.31.00.00.00
# actual speed 58
cansend can0 2C0#40.01.20.00.3A.00.00.00
# lifted UP
cansend can0 2C0#40.0C.20.00.01.00.00.00
#rotating
cansend can0 2C0#40.80.20.00.01.00.00.00
# no faults
cansend can0 2C0#40.87.20.00.00.00.00.00
# init phase ended
cansend can0 2C0#40.25.20.00.00.00.00.00

