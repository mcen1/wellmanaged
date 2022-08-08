#!/bin/env python3
from datetime import datetime, timedelta
import math
import sys
mymonth=datetime.today().strftime("%m")
myyear=datetime.today().strftime("%Y")
myquarter=str((math.ceil(int(mymonth)/3))).replace('.0','')
curquarter=myyear+"_Q"+myquarter
if int(myquarter)==1:
  premonth="4"
  preyear=str(int(myyear)-1)
else:
  premonth=str(int(myquarter)-1)
  preyear=myyear
prequarter=preyear+"_Q"+premonth
if sys.argv[1]=="current":
  print(curquarter)
elif  sys.argv[1]=="previous":
  print(prequarter)
