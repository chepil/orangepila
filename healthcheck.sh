#/bin/sh

CNT=$(docker ps |grep serial | wc -l)
if [ $CNT = 0 ]
then
    docker start serial
fi

