#!/usr/bin/env python

__version__ =  '001'

import sys
sys.dont_write_bytecode = True

def get_results():

	try:
	    import mysql.connector
	except ImportError as e:
	    print(str(e))
	    print('Try...')
	    print('    redhat install: yum install mysql-connector-python')
	    print('    debian install: apt-get install python-mysql.connector')
	    sys.exit(1)

	try:
	    import config
	except ImportError as e:
	    print('Missing config.py: ' + str(e))
	    sys.exit(1)
	dbSocket = config.gclid['dbSocket']
	dbUser = config.gclid['dbUser']
	dbPass = config.gclid['dbPass']

	try:
	    config = {
		'user': dbUser,
		'password': dbPass,
		'unix_socket': dbSocket,
		'database': '',
		'raise_on_warnings': True,
		'auth_plugin': 'mysql_native_password',
	    }
	except Exception as e:
	    print(str(e)) 
	    sys.exit(1)

	try:
	    cnx = mysql.connector.connect(**config)
	except mysql.connector.Error as e:
	    print(str(e))
	    sys.exit(1)

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
	    sys.exit(1)

	cursor.close()
	cnx.close()

	# work with the data...
	# we have get_results fetchall()/list
	#for row in get_results:
	#    print(row)
	return get_results

if __name__ == '__main__':
    if sys.argv[1:]:
        arg1 = sys.argv[1]
    else:
        print('Usage: ' + sys.argv[0])
        sys.exit(0)

    results = get_results()

    rcDict = {}
    count = 0
    if results:
        for (id_gateway_response_data, id_transaction, response, response_message, processor_txn_type, response_code) in results:
            if arg1 == '--print-raw':
                print(id_gateway_response_data, id_transaction, response, response_message, processor_txn_type, response_code)
            count += 1
            rcDict[count] = response_code


    #print(rcDict)
    from collections import defaultdict
    dct = defaultdict(int)
    for k,v in rcDict.items():
        dct[v] += 1

    #print(dct)
    import json
    print(json.dumps(dct, sort_keys=True, indent=4))


