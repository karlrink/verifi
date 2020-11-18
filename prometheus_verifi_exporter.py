#!/usr/bin/env python3

__version__='0000.05'

import sys
sys.dont_write_bytecode = True
try:
    import config
except ImportError as e:
    print('Missing config.py: ' + str(e))
    sys.exit(1)

try:
    import mysql.connector
except ImportError as e:
    print(str(e))
    print('    redhat install: yum install mysql-connector-python3')
    print('    debian install: apt-get install python3-mysql.connector')
    sys.exit(1)

import time
import logging
from logging.handlers import RotatingFileHandler
import signal, atexit

import threading
#from collections import defaultdict
import collections

from http.server import HTTPServer, BaseHTTPRequestHandler

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        logger.info(str(self.client_address[0] + ' - - [' + time.asctime() + '] "' + self.command + ' ' + self.path + ' ' + self.request_version + '" 200 -'))
        if self.path == config.param['metricPath']: #'/metrics'
            self.send_response(200)
            self.send_header("Content-type", "text/plain; charset=utf-8")
            self.end_headers()

            for item in gList:
                self.wfile.write(bytes(str(item) + str('\n'), 'utf-8'))

        else:
            logger.info(str(self.client_address[0] + ' - - [' + time.asctime() + '] "' + self.command + ' ' + self.path + ' ' + self.request_version + '" 404 -'))
            self.send_error(404) #404 Not Found
        return

    def do_POST(self):
        logger.info(str(self.client_address[0] + ' - - [' + time.asctime() + '] "' + self.command + ' ' + self.path + ' ' + self.request_version + '" 405 -'))
        self.send_error(405) #405 Method Not Allowed
        return

def get_results(sql):

    try:
        _config = {
            'user': config.param['dbUser'],
            'password': config.param['dbPass'],
            'unix_socket': config.param['dbSocket'],
            'database': '',
            'raise_on_warnings': True,
            'auth_plugin': 'mysql_native_password',
        }
    except Exception as e:
        logger.critical(str(e)) 
        return False

    try:
        cnx = mysql.connector.connect(**_config)
    except mysql.connector.Error as e:
        logger.critical(str(e))
        return False

    cursor = cnx.cursor(buffered=True)
    try:
        cursor.execute(sql)
        if cursor.rowcount > 0:
            get_results = cursor.fetchall()
        else:
            get_results = ''
            logger.warning(str(time.asctime() + ' Warning: get_results is Empty'))

    except Exception as e:
        logger.critical(str(e))
        return False

    cursor.close()
    cnx.close()

    # work with the data...
    # we have get_results fetchall()
    #for row in get_results:
    #    print(row)
    return get_results


def processD():

    sql1Dct1 = {}
    sql1Dct2 = {}
    sql1_up = 0
    sql1 =  """SELECT nic_gateway.gateway_response_data.id_gateway_response_data,nic_gateway.gateway_response_data.id_transaction, 
                      nic_gateway.gateway_response_data.response,nic_gateway.gateway_response_data.response_message, 
                      nic_gateway.gateway_response_data.processor_txn_type,nic_gateway.gateway_response_data.response_code
              FROM nic_gateway.gateway_response_data
              WHERE nic_gateway.gateway_response_data.id_transaction IN ( 
              SELECT transaction.id_transaction 
              FROM nic_gateway.transaction 
              WHERE transaction.transaction_date >= NOW() - INTERVAL 5 MINUTE 
              AND id_transaction > (SELECT MAX(id_transaction) FROM nic_gateway.transaction) - 100000 );
    """
    start1 = time.time()
    sql1_results = get_results(sql1)
    sqltime1 = time.time() - start1
    if sql1_results:
        sql1_up = 1
        row = 0
        for (id_gateway_response_data, id_transaction, response, response_message, processor_txn_type, response_code) in sql1_results:
            txn_type = str(processor_txn_type).lower()
            rsp_msg  = str(response_message).lower()
            row += 1
            sql1Dct1[row] = 'verifi_response_code_count{code="'+str(response_code)+'",type="'+txn_type+'"}'
            sql1Dct2[row] = 'verifi_response_code_message_count{code="'+str(response_code)+'",type="'+txn_type+'",message="'+rsp_msg+'"}'

    Dct1a = collections.defaultdict(int)
    for k,v in sql1Dct1.items():
        Dct1a[v] += 1

    Dct1b = collections.defaultdict(int)
    for k,v in sql1Dct2.items():
        Dct1b[v] += 1


    sql2Dct = {}
    sql2_up = 0
    sql2 =  """SELECT  nic_gateway.merchant_processor.processor_name,nic_gateway.gateway_response_data.response_code
              FROM nic_gateway.gateway_response_data, nic_gateway.merchant_processor
              WHERE nic_gateway.gateway_response_data.id_transaction IN (
              SELECT transaction.id_transaction
              FROM nic_gateway.transaction
              WHERE transaction.transaction_date >= NOW() - INTERVAL 5 MINUTE
              AND id_transaction > (SELECT MAX(id_transaction) FROM nic_gateway.transaction) - 100000 );
    """
    start2 = time.time()
    sql2_results = get_results(sql2)
    sqltime2 = time.time() - start2
    if sql2_results:
        sql2_up = 1
        row = 0
        for (processor_name, response_code) in sql2_results:
            if processor_name == None:
                processor_name = 'None'

            row += 1
            sql2Dct[row] = 'verifi_response_code_processor_count{processor_name="'+str(processor_name)+'",code="'+str(response_code)+'"}'

    Dct2 = collections.defaultdict(int)
    for k,v in sql2Dct.items():
        Dct2[v] += 1


    
    gList.clear()

    gList.append('verifi_sql1_up ' + str(sql1_up))
    gList.append('verifi_sql1_query_time ' + str(sqltime1))
    if sql1_up == 1:
        for k,v in Dct1a.items():
            item = str(k) + ' ' + str(v)
            gList.append(item)
        for k,v in Dct1b.items():
            item = str(k) + ' ' + str(v)
            gList.append(item)

    gList.append('verifi_sql2_up ' + str(sql2_up))
    gList.append('verifi_sql2_query_time ' + str(sqltime2))
    if sql2_up == 1:
        for k,v in Dct2.items():
            item = str(k) + ' ' + str(v)
            gList.append(item)

    return True

def ticker():
    while (sigterm == False):
        processD()
        time.sleep(15)

def stopped():
    logger.info(str(time.asctime()) + ' Info: Server Stop on port ' + str(config.param['listenPort']))

def main(args):

    runner = threading.Thread(target=ticker, name="ticker")
    runner.setDaemon(1)
    runner.start()

    logger.info(str(time.asctime()) + ' Info: Server Start on port ' + str(config.param['listenPort']))
    httpd = HTTPServer(('', config.param['listenPort']), Handler)
    try:
        httpd.serve_forever()
    except (KeyboardInterrupt, SystemExit, Exception):
        sigterm = True
        httpd.server_close()


if __name__ == '__main__':
    gList = []
    sigterm = False

    atexit.register(stopped) #python can't catch SIGKILL (kill -9)
    signal.signal(signal.SIGTERM, lambda signum, stack_frame: sys.exit(1))

    handler = RotatingFileHandler(config.param['logFile'], maxBytes=100000, backupCount=10)
    formatter = logging.Formatter(logging.BASIC_FORMAT)
    handler.setFormatter(formatter)
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    sys.exit(main(sys.argv))

