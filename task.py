#!./venv/bin/python3.10
# -*- coding: utf-8 -*-
#pip install apscheduler
#pip install -U icmplib
from datetime import datetime
import time
from apscheduler.schedulers.blocking import BlockingScheduler
#from apscheduler.schedulers.background import BackgroundScheduler
from pytz import utc
from pytz import timezone
from icmplib import multiping
import signal
from switch_channel_to_rezerv import switch_channel
import logging
logging.basicConfig(filename="icmp_rt.log", level=logging.DEBUG,format='%(asctime)s - %(message)s', datefmt='%Y%m%dT%H:%M:%S')
logger = logging.getLogger("icmp_rt.log")


def signal_handler(signal, frame):
    print('\nEnd of program by signal'+ str(sinal))
    logger.warn('\nEnd of program by signal'+ str(sinal))
    scheduler.shutdown(wait=False)
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)


def hostcheck():
#    print(datetime.now(timezone('Europe/Moscow')))
    addresses=['192.168.30.1','192.168.29.1','192.168.15.1']
    hosts=multiping(addresses, count=4, interval=0.1, timeout=1, concurrent_tasks=5, source=None, family=None, privileged=False)
    sum=0
    for host in hosts:
        if host.is_alive:
            sum+=1
    print(datetime.now(timezone('Europe/Moscow')),'sum:'+str(sum)) 
    logger.info(str(datetime.now(timezone('Europe/Moscow')))+'; sum:'+str(sum))   
    if sum==0:
        print('Канал не работает - перключаем')
        logger.warn('Канал не работает - перключаем')
        switch_channel()
#       scheduler.shutdown(wait=False)  
if __name__ == '__main__':
    try:    
        scheduler = BlockingScheduler(timezone='Europe/Moscow')
        scheduler.add_job(hostcheck, 'interval', seconds=1)
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown(wait=False)  
        logger.error('Завершение программы пользователем Ctrl+C')
    except Exception as e:
        print(e)
        scheduler.shutdown(wait=False)  
        logger.error(str(e))

    '''

        while True:
            time.sleep(0.5)
    '''
