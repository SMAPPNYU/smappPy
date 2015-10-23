#!/bin/sh

scriptpath=$(cd "$(dirname "$0")"; pwd)

#create a new screen and execute our interactive bash script inside it
screen -dmS "hadestunnel" $scriptpath/hadesexpect.sh
