#!/usr/bin/env python

__version__ =  '002'

import sys
sys.dont_write_bytecode = True

import json
import os

try:
    import config
except ImportError as e:
    print('Missing config.py: ' + str(e))
    sys.exit(1)

def get_results():

	try:
	    import mysql.connector
	except ImportError as e:
	    print(str(e))
	    print('Try...')
	    print('    redhat install: yum install mysql-connector-python')
	    print('    debian install: apt-get install python-mysql.connector')
	    sys.exit(1)

	#try:
	#    import config
	#except ImportError as e:
	#    print('Missing config.py: ' + str(e))
	#    sys.exit(1)
        import config
	dbSocket = config.param['dbSocket']
	dbUser = config.param['dbUser']
	dbPass = config.param['dbPass']

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

def verifiRRD(rrdfile, data_dict):
    try:
        import rrdtool
    except ImportError as e:
        print(str(e))
        print('Try...')
        print('    debian install: apt-get install python-rrdtool')
        return False

    data_sources = []
    for k,v in data_dict.items():
        #print(k, v)
        ds = 'DS:' + str(k) + ':GAUGE:600:U:U'
        data_sources.append(ds)

    print(str(data_sources))

    rrdtool.create(str(rrdfile), '--start', '0',
                                 '--step', '300',
                    data_sources,
                    'RRA:AVERAGE:0.5:1:360',
                    'RRA:AVERAGE:0.5:12:1008',
                    'RRA:AVERAGE:0.5:288:2016')
    return True


def writeRRD(rrdfile, data_dict):
    try:
        import rrdtool
    except ImportError as e:
        print(str(e))
        print('Try...')
        print('    debian install: apt-get install python-rrdtool')
        return False

    val = 'N'
    if not os.path.isfile(rrdfile):
        verifiRRD(rrdfile, data_dict)
    else:
        for k,v in data_dict.items():
            val += ':' + str(v)
        try:
            import rrdtool
            rrdtool.update(str(rrdfile), str(val))
        except Exception as e:
            print(e)
    return True

def post(system_id, json_data):
    import urllib2
    import ssl
    if (not os.environ.get('PYTHONHTTPSVERIFY', '') and
        getattr(ssl, '_create_unverified_context', None)):
        ssl._create_default_https_context = ssl._create_unverified_context

    try:
        request = urllib2.Request(config.param['url'] + '?system_id=' + str(system_id))
        request.add_header('content-type', 'application/json')
        request.add_header('x-api-key', system_id)
        post_data = json.dumps(json.JSONDecoder().decode(json_data))
        response = urllib2.urlopen(request, post_data, timeout=20)
        return response.read()
    except Exception as e:
        return str(e)


if __name__ == '__main__':
    if sys.argv[1:]:
        for arg in sys.argv[1:]:
            arg1 = sys.argv[1]
    else:
        print('Usage: ' + sys.argv[0] + ' [option]' + """

        run
        --print-raw
        --write-local
        --disable-post
        """)
        sys.exit(0)

    results = get_results()

    rcDict = {}
    count = 0
    if results:
        for (id_gateway_response_data, id_transaction, response, response_message, processor_txn_type, response_code) in results:
            #if arg1 == '--print-raw':
            if '--print-raw' in sys.argv[1:]:
                print(id_gateway_response_data, id_transaction, response, response_message, processor_txn_type, response_code)
            count += 1
            rcDict[count] = response_code


    #print(rcDict)
    from collections import defaultdict
    dct = defaultdict(int)
    for k,v in rcDict.items():
        dct[v] += 1

    #print(dct)
    #print(json.dumps(dct, sort_keys=True, indent=4))

    system_id = config.param['system_id']

    rrd = {'rrd': 'verifi', 'val': dct, 'type': 'response_code'}
    rrdList = [ rrd ]

    json_data  = '{ "system_id": "' + str(system_id) + '",'
    json_data += '"rrdata": ' + str(json.dumps(rrdList))
    json_data += '}'

    print(json.dumps(json.loads(json_data), sort_keys=True, indent=4))

    if '--write-local' in sys.argv[1:]:
        for k,v in dct.items():
            rrdfile = 'verifi_' + str(k) + '.rrd'
            w = writeRRD(rrdfile, {k:v})
            print('{"file": "' + str(rrdfile) + ', "write": "' + str(w) + '"}')
        #rrdfile = str(response_code) + '.rrd'
        #w = writeRRD(rrdfile, dct)
        #print('{"write": "' + str(w) + '"}')

    if not '--disable-post' in sys.argv[1:]:
        response = post(system_id, json.dumps(json.loads(json_data)))
        try:
            print(json.dumps(json.loads(response)))
        except Exception as e:
            print(response)

    sys.exit(0)
