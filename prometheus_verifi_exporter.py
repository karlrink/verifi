#!/usr/bin/env python3

__version__='0000.03'

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
from collections import defaultdict
from http.server import HTTPServer, BaseHTTPRequestHandler

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        #127.0.0.1 - - [31/May/2020 19:09:05] "GET /metrics HTTP/1.1" 200 -
        logger.info(str(self.client_address[0] + ' - - [' + time.asctime() + '] "' + self.command + ' ' + self.path + ' ' + self.request_version + '" 200 -'))
        #if self.path == '/metrics':
        if self.path == config.param['metricPath']:
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

def get_results():

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

    sql =  """SELECT nic_gateway.gateway_response_data.id_gateway_response_data,nic_gateway.gateway_response_data.id_transaction, 
                     nic_gateway.gateway_response_data.response,nic_gateway.gateway_response_data.response_message, 
                     nic_gateway.gateway_response_data.processor_txn_type,nic_gateway.gateway_response_data.response_code,
                     nic_gateway.merchant_processor.id_merchant_processor, nic_gateway.merchant_processor.processor_name
              FROM nic_gateway.gateway_response_data, nic_gateway.merchant_processor
              WHERE nic_gateway.gateway_response_data.id_transaction IN ( 
              SELECT transaction.id_transaction 
              FROM nic_gateway.transaction 
              WHERE transaction.transaction_date >= NOW() - INTERVAL 5 MINUTE 
              AND id_transaction > (SELECT MAX(id_transaction) FROM nic_gateway.transaction) - 100000 
              );
    """

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
    # we have get_results fetchall()/list
    #for row in get_results:
    #    print(row)
    return get_results


def processD():
    verifi_up = 0
    sqlData = {}
    start = time.time()
    results = get_results()
    sqltime = time.time() - start
    if results:
        verifi_up = 1
        row = 0
        for (id_gateway_response_data, id_transaction, response, response_message, processor_txn_type, response_code, id_merchant, processor_name) in results:
            txn_type = str(processor_txn_type).lower()
            rsp_msg  = str(response_message).lower()
            row += 1
            #sqlData[row] = 'verifi_response_code_count{code="'+str(response_code)+'",type="'+txn_type+'",message="'+rsp_msg+'",mid="'+str(id_merchant)+'",mname="'+processor_name+'"}'
            sqlData[row] = 'verifi_response_code_count{code="'+str(response_code)+'",type="'+txn_type+'",message="'+rsp_msg+'",mname="'+processor_name+'"}'

    dct = defaultdict(int)
    for k,v in sqlData.items():
        dct[v] += 1

    gList.clear()

    promHELP0 = '# HELP verifi_up Whether the SQL service for verifi is up.'
    promTYPE0 = '# TYPE verifi_up gauge'
    promDATA0 = 'verifi_up ' + str(verifi_up)
    gList.append(promHELP0)
    gList.append(promTYPE0)
    gList.append(promDATA0)

    promHELP1 = '# HELP verifi_sql_query_time Number of seconds to query SQL.'
    promTYPE1 = '# TYPE verifi_sql_query_time gauge'
    promDATA1 = 'verifi_sql_query_time ' + str(sqltime)
    gList.append(promHELP1)
    gList.append(promTYPE1)
    gList.append(promDATA1)

    if verifi_up == 1:
        promHELP2 = '# HELP verifi_response_code_count Total number of verifi response codes. Only updated after SQL query, not continuously.'
        promTYPE2 = '# TYPE verifi_response_code_count untyped'
        gList.append(promHELP2)
        gList.append(promTYPE2)
        for k,v in dct.items():
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
        sigterm == True
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

