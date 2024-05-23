#!./venv/bin/python3.10
# -*- coding: utf-8 -*-

from scrapli.driver.core import IOSXEDriver
from scrapli.driver.core import NXOSDriver
import logging
logging.basicConfig(filename="./interface_status_change.log", level=logging.INFO,format='%(asctime)s - %(message)s', datefmt='%Y%m%dT%H:%M:%S')
logger = logging.getLogger("interface_shut_no_shut")
class ConnectContextManager():
     def __init__(self,DEVICE_NAME):
         self.device_name=DEVICE_NAME
         self.conn=None
         return None
     def __enter__(self):
         try:
             self.conn=IOSXEDriver(**self.device_name)
             self.conn.open()
             logger.info(f'self.device_name["host"] - Connectin Opened')
         except Exception as e:
             logger.error(str(e))
             logger.error(f'Unable connect to {self.device_name["host"]}')
         return self.conn
     def __exit__(self,exc_type, exc_value, exc_tb):
         if self.conn:
             self.conn.close()

class ConnectContextManagerNX():
     def __init__(self,DEVICE_NAME):
         self.device_name=DEVICE_NAME
         self.conn=None
         return None
     def __enter__(self):
         try:
             self.conn=NXOSDriver(**self.device_name)
             self.conn.open()
             logger.info(f'{self.device_name["host"]} - Connectin Opened')
         except Exception as e:
             logger.error(str(e))
             logger.error(f'Unable connect to {self.device_name["host"]}')
         return self.conn
     def __exit__(self,exc_type, exc_value, exc_tb):
         if self.conn:
             self.conn.close()
