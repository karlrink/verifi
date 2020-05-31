#!/usr/bin/env python3

__version__='0000.00'

import sys
sys.dont_write_bytecode = True

def usage():
    print("Usage: " + sys.argv[0] + " option" + """

    options:
    --web.listen-port=9181
    --web.telemetry-path=/metrics
    --log.level=info

    --help
    """)
    sys.exit(0)

from http.server import HTTPServer, BaseHTTPRequestHandler
import time
import threading
from collections import defaultdict

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
        #print('PATH ' + METRIC_PATH)
        #if self.path == '/metrics':
        if self.path == METRIC_PATH:
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()

            for item in gList:
                self.wfile.write(bytes(str(item) + str('\n'), 'utf-8'))

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
    verifi_up = 0
    sqlData = {}
    start = time.time()
    results = get_results()
    sqltime = time.time() - start
    if results:
        verifi_up = 1
        row = 0
        for (id_gateway_response_data, id_transaction, response, response_message, processor_txn_type, response_code) in results:
            txn_type = str(processor_txn_type).lower()
            rsp_msg  = str(response_message).lower()
            row += 1
            sqlData[row] = 'verifi_response_code_count{code="' + str(response_code) + '",type="' + txn_type + '",message="' + rsp_msg + '"}'

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

def main(PORT_NUMBER, METRIC_PATH):

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


if __name__ == '__main__':
    PORT_NUMBER = 9181
    METRIC_PATH = '/metrics'

    if sys.argv[1:]:
        for arg in sys.argv[1:]:
            if arg == '--help':
                usage()
            if '=' in arg:
                arg0 = arg.split('=')[0]
                arg1 = arg.split('=')[1]
                if arg0 == '--web.listen-port':
                    PORT_NUMBER = int(arg1)
                if arg0 == '--web.telemetry-path':
                    METRIC_PATH = str(arg1)
            else:
                print('Unknown : ' + str(arg))
                usage()

                
    sys.exit(main(PORT_NUMBER, METRIC_PATH))

