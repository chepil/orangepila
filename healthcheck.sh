#/bin/sh

CNT=$(docker ps |grep serial | wc -l)
if [ $CNT = 0 ]
then
    exec /usr/bin/docker start serial &
fi
