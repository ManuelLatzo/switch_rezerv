#!./venv/bin/python3.10
# -*- coding: utf-8 -*-
import os
import datetime
import logging
from dotenv import load_dotenv
from scrapli.driver.core import IOSXEDriver
from device_name import ConnectContextManager, ConnectContextManagerNX
import re
import time
from pytz import timezone
import yaml
from base64 import b64decode


logging.basicConfig(filename="scrapli.log", level=logging.DEBUG,format='%(asctime)s - %(message)s', datefmt='%Y%m%dT%H:%M:%S')
dt=datetime.datetime.now().strftime("%Y%m%d")
logger = logging.getLogger(f"{dt}"+"_interface_shut_no_shut")
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))
production_mode=os.getenv('production_mode')
timezoneoffset=int(os.getenv('timezoneoffset'))
try:
    if (not os.path.exists("state.yaml")):
        with  open(os.path.join(basedir,"state.yaml"), 'w',encoding="utf-8") as state_file:
            #check channel state
            datetimestamp=time.time()+timezoneoffset
            state={'state':None,'datetimestamp': datetimestamp,'datetimestamptext':datetime.datetime.fromtimestamp(datetimestamp).strftime('%Y%m%dT%H%M%S')}
            state_file.write(yaml.safe_dump(state))
    else:
        with  open(os.path.join(basedir,"state.yaml"), 'r',encoding="utf-8") as state_file:
            state=yaml.safe_load(state_file)
            if state is None:
                datetimestamp=time.time()+timezoneoffset
                state={'state':None,'datetimestamp': datetimestamp,'datetimestamptext':datetime.datetime.fromtimestamp(datetimestamp).strftime('%Y%m%dT%H%M%S')}
except Exception as e:
        print(e)
devices=[]
with  open(os.path.join(basedir,"env.yaml.encoded"), 'r',encoding="utf-8") as f:
    devices=f.read()
    devices=b64decode(devices)
    devices=yaml.safe_load(devices)

def shut3750port(device,cmd):
    conf_dict={'shut':['interface GigabitEthernet1/0/24','shutdown'],
                 'noshut':['interface GigabitEthernet1/0/24','no shutdown']}
    check_dict={'portstate':['show interfaces GigabitEthernet1/0/24 | include GigabitEthernet1/0/24']}
    command=conf_dict.get(cmd,None)
    try:
        with ConnectContextManager(device) as conn:
            response = conn.send_command("show interfaces GigabitEthernet1/0/24 | include GigabitEthernet1/0/24")
            if cmd in conf_dict.keys():
               print('Performing configuring 3750 ...')
               if production_mode==True:
                  print("production_mode = True - Конфигурирование")
                  logger.info("production_mode = True")
                  logger.info("Конфигурирование")
                  result=conn.send_configs(command)
               else:
                  print("production_mode = False - Когфигурирование отключено")
                  logger.info("production_mode = False")
                  logger.info("Конфигурирование отключено")               
#               result=conn.send_configs(command)
            response = conn.send_commands(check_dict.get('portstate'))
            return response.result
    except Exception as e:
            print(e)
            logger.error(e)


def N3Kport(device,cmd):
    conf_dict={'shut':['interface Ethernet1/43','shutdown','switchport access vlan 204'],
                 'noshut':['interface Ethernet1/43','switchport access vlan 203','no shutdown']}
    check_dict={'portstate':['show interface ethernet 1/43 | include Ethernet1/43']}
    command=conf_dict.get(cmd,None)
    try:
        with ConnectContextManagerNX(device) as conn:
            response = conn.send_command("show interface ethernet 1/43 | include Ethernet1/43")
            if cmd in conf_dict.keys():
               print('Performing configring N3K ...')
               if production_mode==True:
                  print("production_mode = True - Конфигурирование")
                  logger.info("production_mode = True")
                  logger.info("Когфигурирование")
                  result=conn.send_configs(command)
               else:
                  print("production_mode = False - Конфигурирование отключено")
                  logger.info("production_mode = False")
                  logger.info("Когфигурирование отключено")               
#               result=conn.send_configs(command)
            response = conn.send_commands(check_dict.get('portstate'))
            return response.result
    except Exception as e:
            print(e)
            logger.error(e)


def ConnectionCheck():
    def mainChannel():
        with ConnectContextManager(devices[0]) as conn:
            response = shut3750port(devices[0],'portstate')
            if re.search('up',response):
                state['3750']=1
            if re.search('down',response):                
                state['3750']=0
    def rezervChannel():
        with ConnectContextManagerNX(devices[1]) as conn:
            response = N3Kport(devices[1],'portstate')
            if re.search('up',response):
                state['NEXUS3K']=1                
            if re.search('down',response):                
                state['NEXUS3K']=0                

    try:
     if state.get('state',None) is None:
    #if true: #Всегда проверять канал
        print('Проверка состояния канала')
        logger.info('Проверка состояния канала')
        mainChannel()
        rezervChannel()
        if state['3750']==1 and state['NEXUS3K']==0:
           state['state']=0
        elif state['3750']==0 and state['NEXUS3K']==1:
             state['state']=1
        else:
            print('Check ports! Inconsistent state! 3750 -> GigabitEthernet1/0/24; HQ-ESW-DC-2 -> Ethernet1/43 ')
            print(state)
            print('Set Main Channel as default')
            mainChannel()
            logger.error('Check ports! Inconsistent state!')
            logger.error(str(state))
            print(state)
     if state.get('state')==0: 
        print('Включен основной канал ') 
        logger.info('Включен основной канал')
     if state.get('state')==1: 
        print('Включен резервный канал ') 
        logger.info('Включен резервный канал')
    except Exception as e:
       logger.error(str(e))
       print('Connection Error')
       print(e)
       exit(0)


def switch_channel():
    print("START: ",state)
    ConnectionCheck()
    if state.get('state')==0:
       print('Переключение на резерв')
       logger.info('Переключение на резерв')
       r=shut3750port(devices[0],'shut')
       print('Переключили 3750: shutdown')
       logger.info('Переключение на резерв: shutdown')
       print('Pause 5 sec')
       time.sleep(5)
       r=N3Kport(devices[1],'noshut')
       print('Переключили NEXUS3K: no shutdown')
       logger.info('Переключили NEXUS3K: no shutdown')
       state['3750']=0
       state['NEXUS3K']=1
       state['state']=1
    elif state.get('state')==1:
       print('Переключение на основной канал')
       logger.info('Переключение на основной канал')
       r=N3Kport(devices[1],'shut')
       print('Переключили NEXUS3K: shutdown')
       logger.info('Переключили NEXUS3K: shutdown')
       print('Pause 5 sec')
       time.sleep(5)
       r=shut3750port(devices[0],'noshut')
       print('Переключили 3750: no shutdown')
       logger.info('Переключили 3750: no shutdown')
       state['3750']=1
       state['NEXUS3K']=0
       state['state']=0
    else:
            print('Check ports! Inconsistent state! 3750 -> GigabitEthernet1/0/24; HQ-ESW-DC-2 -> Ethernet1/43 ')
            print(state)
            logger.error('Check ports! Inconsistent state!')
            logger.error(str(state))
            exit(0)
    with  open(os.path.join(basedir,"state.yaml"), 'w',encoding="utf-8") as state_file:
	    #check channel state
        datetimestamp=time.time()+timezoneoffset
        state['datetimestamp']=datetimestamp
        state['datetimestamptext']=datetime.datetime.fromtimestamp(datetimestamp).strftime('%Y%m%dT%H%M%S')
        state_file.write(yaml.safe_dump(state))   
    time.sleep(5)         
    print("FINISH: ",state)
    logger.info("FINISH: "+ str(state))


if __name__ == "__main__":
    switch_channel()
