#!/usr/bin/env python3

__version__='0000.0'

import time
import sys
sys.dont_write_bytecode = True

from http.server import HTTPServer, BaseHTTPRequestHandler
PORT_NUMBER = 9181

import threading
#import queue
#qData = queue.Queue()

from collections import defaultdict

#gData = {}
gList = []
sigterm = False

try:
    import mysql.connector
except ImportError as e:
    print(str(e))
    print('    redhat install: yum install mysql-connector-python3')
    print('    debian install: apt-get install python3-mysql.connector')
    sys.exit(1)

try:
    import config
except ImportError as e:
    print('Missing config.py: ' + str(e))
    sys.exit(1)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/metrics':
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(bytes(str(self.command) + str(' \n'),'utf-8'))

            #for item in qData.queue:
            for item in gList:
                self.wfile.write(bytes(str(item) + str(' \n'),'utf-8'))


        else:
            self.send_error(404) #404 Not Found
        return

    def do_POST(self):
        self.send_error(405) #405 Method Not Allowed
        return

def get_results():

    dbSocket = config.param['dbSocket']
    dbUser = config.param['dbUser']
    dbPass = config.param['dbPass']

    try:
        _config = {
            'user': dbUser,
            'password': dbPass,
            'unix_socket': dbSocket,
            'database': '',
            'raise_on_warnings': True,
            'auth_plugin': 'mysql_native_password',
        }
    except Exception as e:
        print(str(e)) 
        return False

    try:
        cnx = mysql.connector.connect(**_config)
    except mysql.connector.Error as e:
        print(str(e))
        return False

    sql =  "SELECT nic_gateway.gateway_response_data.id_gateway_response_data,nic_gateway.gateway_response_data.id_transaction, "
    sql += "       nic_gateway.gateway_response_data.response,nic_gateway.gateway_response_data.response_message, "
    sql += "       nic_gateway.gateway_response_data.processor_txn_type,nic_gateway.gateway_response_data.response_code "
    sql += "FROM nic_gateway.gateway_response_data " 
    sql += "WHERE nic_gateway.gateway_response_data.id_transaction IN ( "
    sql += "  SELECT transaction.id_transaction "
    sql += "  FROM nic_gateway.transaction "
    sql += "  WHERE transaction.transaction_date >= NOW() - INTERVAL 5 MINUTE "
    sql += "  AND id_transaction > (SELECT MAX(id_transaction) FROM nic_gateway.transaction) - 100000 "
    sql += " );"
    #sql += "LIMIT 5"

    cursor = cnx.cursor(buffered=True)
    try:
        cursor.execute(sql)
        if cursor.rowcount > 0:
            get_results = cursor.fetchall()
        else:
            get_results = ''

    except Exception as e:
        print(str(e))
        return False

    cursor.close()
    cnx.close()

    # work with the data...
    # we have get_results fetchall()/list
    #for row in get_results:
    #    print(row)
    return get_results




def processD():
    sqlData = {}
    start = time.time()
    results = get_results()
    sqltime = time.time() - start
    print('sqltime: ' + str(sqltime))
    if results:
        row = 0
        for (id_gateway_response_data, id_transaction, response, response_message, processor_txn_type, response_code) in results:
            row += 1
            #sqlData[row] = response_code, str(processor_txn_type).lower(), str(response_message).lower()
            txn_type = str(processor_txn_type).lower()
            rsp_msg  = str(response_message).lower()
            sqlData[row] = 'verifi_response_code_count{code="' + str(response_code) + '",type="' + txn_type + '",message="' + rsp_msg + '"}'

    dct = defaultdict(int)
    for k,v in sqlData.items():
        dct[v] += 1


    #gData = dct
    #for k,v in gData.items():
    #    print(k, v)

    #for k,v in dct.items():
    #    item = str(k) + ' ' + str(v)
    #    qData.put(item)

    
    promHELP = '# HELP verifi_response_code_count Total number of verifi response codes. Only updated after SQL query, not continuously.'
    promTYPE = '# TYPE verifi_response_code_count counter'

    gList.clear()
    gList.append(promHELP)
    gList.append(promTYPE)
    for k,v in dct.items():
        item = str(k) + ' ' + str(v)
        gList.append(item)




# HELP verifi_response_code_count Total number of verifi response codes. Only updated after SQL query, not continuously.
# TYPE verifi_response_code_count counter

    
def ticker():
    while (sigterm == False):
        processD()
        time.sleep(15)

if __name__ == '__main__':

    watcher = threading.Thread(target=ticker, name="ticker")
    watcher.setDaemon(1)
    watcher.start()

    print(str(time.asctime()) + " Server Start - " + str(PORT_NUMBER))
    httpd = HTTPServer(('', PORT_NUMBER), Handler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        sigterm == True

    httpd.server_close()
    print(str(time.asctime()) + " Server Stop - " + str(PORT_NUMBER))


#if __name__ == '__main__':
#    sys.exit(main(sys.argv))


