#!/bin/env python3
import sys
myserver=str(sys.argv[1])
sox=['server1','server2']
top10=['server1','server3']

allaudits={"sox":sox,"top10":top10}
validaudits=[]

for item in allaudits:
  for server in allaudits[item]:
    if server.lower()==myserver.lower() and item not in validaudits:
      validaudits.append(item)

print(validaudits)

