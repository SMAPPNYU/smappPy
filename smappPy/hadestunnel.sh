#!/bin/sh

scriptpath=$(cd "$(dirname "$0")"; pwd)

#kill screen sessions that already have the name hades tunnel.
# for session in $(screen -ls | grep -o '[0-9]*\.hades'); do screen -S "${session}" -X quit; done

#create a new screen and execute our interactive bash script inside it
screen -dmS "hadestunnel" $scriptpath/hadesexpect.sh
