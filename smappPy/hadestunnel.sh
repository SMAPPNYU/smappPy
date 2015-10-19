#!/bin/sh

# read the file with HPC login instructions
IFS=$'\n' read -d '' -r -a hpclogin < ~/.ssh/hpclogin.txt

#spawn an ssh process that will port forward
#need the * star to match the entire
#NYU disclaimer message that comes 
#before or else expect will not know
#what to match
#get the password read to send
#send the password with interact
/usr/bin/expect -c "
spawn ssh -L 27017:localhost:27017 ${hpclogin[0]}@hades0.es.its.nyu.edu;
expect \"*hades0.es.its.nyu.edu's password: \";
send \"${hpclogin[1]}\n\";
interact;
"
