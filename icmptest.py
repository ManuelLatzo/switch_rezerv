#!./venv/bin/python3.10
# -*- coding: utf-8 -*-
#pip install apscheduler
#pip install -U icmplib

from datetime import datetime
from pytz import timezone
from icmplib import ping
from icmplib import multiping
print(datetime.now(timezone('Europe/Moscow')))
addresses=['192.168.30.1','192.168.29.1','192.168.15.1']
hosts=multiping(addresses, count=2, interval=0.5, timeout=1, concurrent_tasks=5, source=None, family=None, privileged=False)
sum=0
for host in hosts:
    if host.is_alive:
        sum+=1
print(sum)
print(datetime.now(timezone('Europe/Moscow')))