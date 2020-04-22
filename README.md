# nutil/verifi

karl.rink@db01repl3:~/verifi$ ./response_code.tracker.py
Usage: ./response_code.tracker.py [option]

        run
        --print-raw
        --write-local
        --disable-post
        
karl.rink@db01repl3:~/verifi$ ./response_code.tracker.py --print-raw --write-local --disable-post
(137389681, 137463320, u'1', u'Transaction Void Successful', u'void', u'100')
(137389682, 137463321, u'2', u'Transaction failed  because of payment processing failure.: 302 - Insufficient funds. Please use another card or contact your bank for assistance', u'sale', u'202')
(137389683, 137463322, u'2', u'Transaction failed  because of payment processing failure.: 530 - This transaction has been declined. Please check card details and try again, or contact your bank for assistance', u'sale', u'201')
(137389684, 137463323, u'2', u'Order creation failure due to problematic input., The credit card expiration month must be a number between 1 and 12., The stated credit card expiration date has already passed.', u'sale', u'223')
(137389685, 137463324, u'1', u'APPROVED', u'validate', u'100')
(137389686, 137463325, u'2', u'Insufficient funds', u'sale', u'202')
(137389687, 137463326, u'1', u'Approved', u'validate', u'100')
(137389688, 137463327, u'2', u'Transaction failed  because of payment processing failure.: 530 - This transaction has been declined. Please check card details and try again, or contact your bank for assistance', u'sale', u'201')
(137389689, 137463328, u'2', u'Order creation failure due to problematic input., The credit card expiration month must be a number between 1 and 12., The stated credit card expiration date has already passed.', u'sale', u'223')
(137389690, 137463329, u'1', u'Approved', u'sale', u'100')
(137389691, 137463330, u'2', u'Issuer Declined', u'sale', u'200')
(137389692, 137463331, u'1', u'Approved', u'sale', u'100')
(137389693, 137463332, u'1', u'Approved', u'sale', u'100')
(137389694, 137463333, u'1', u'Approval', u'sale', u'100')
(137389695, 137463334, u'1', u'Approved', u'sale', u'100')
(137389696, 137463335, u'2', u'Transaction failed  because of payment processing failure.: 806 - This transaction is not authorized due to restrictions by your bank. Please use a different card or contact your bank for assistance', u'sale', u'204')
(137389697, 137463336, u'2', u'Issuer Declined', u'auth', u'200')
(137389700, 137463337, u'1', u'Approved', u'sale', u'100')
(137389698, 137463338, u'2', u'Order creation failure due to problematic input., The credit card expiration month must be a number between 1 and 12., The stated credit card expiration date has already passed.', u'auth', u'223')
(137389699, 137463339, u'1', u'Transaction Void Successful', u'void', u'100')
(137389701, 137463340, u'1', u'Approved', u'sale', u'100')
(137389703, 137463341, u'2', u'Issuer Declined', u'sale', u'200')
(137389702, 137463342, u'1', u'Transaction Void Successful', u'void', u'100')
(137389704, 137463343, u'1', u'Approval', u'sale', u'100')
(137389705, 137463344, u'2', u'Order creation failure due to problematic input., The credit card expiration month must be a number between 1 and 12., The stated credit card expiration date has already passed.', u'sale', u'223')
(137389706, 137463345, u'2', u'Transaction failed  because of payment processing failure.: 806 - This transaction is not authorized due to restrictions by your bank. Please use a different card or contact your bank for assistance', u'sale', u'204')
(137389707, 137463346, u'1', u'Approved', u'sale', u'100')
(137389708, 137463347, u'1', u'Approved', u'sale', u'100')
(137389709, 137463348, u'1', u'Approved', u'refund', u'100')
(137389710, 137463349, u'1', u'Approved', u'sale', u'100')
(137389711, 137463350, u'1', u'Approved', u'sale', u'100')
(137389712, 137463351, u'1', u'Approved', u'sale', u'100')
(137389713, 137463352, u'1', u'APPROVED', u'sale', u'100')
(137389714, 137463353, u'2', u'AVS Match', u'sale', u'891')
(137389715, 137463354, u'1', u'Approved', u'validate', u'100')
(137389717, 137463355, u'1', u'Approved', u'sale', u'100')
(137389716, 137463356, u'1', u'Transaction Void Successful', u'void', u'100')
(137389718, 137463357, u'1', u'Approved', u'refund', u'100')
(137389719, 137463358, u'1', u'Approved', u'sale', u'100')
(137389720, 137463359, u'1', u'SUCCESS', u'sale', u'100')
(137389721, 137463360, u'1', u'SUCCESS', u'sale', u'100')
(137389722, 137463361, u'1', u'Approved', u'sale', u'100')
(137389723, 137463362, u'1', u'Approved', u'sale', u'100')
(137389724, 137463363, u'2', u'Transaction failed  because of payment processing failure.: 302 - Insufficient funds. Please use another card or contact your bank for assistance', u'sale', u'202')
(137389725, 137463364, u'1', u'Approved', u'sale', u'100')
(137389726, 137463365, u'1', u'Approved', u'sale', u'100')
(137389727, 137463366, u'1', u'APPROVED', u'validate', u'100')
(137389728, 137463367, u'1', u'Approved', u'sale', u'100')
(137389729, 137463368, u'1', u'Approved', u'sale', u'100')
(137389730, 137463369, u'1', u'Approved', u'sale', u'100')
(137389731, 137463370, u'1', u'Approved', u'sale', u'100')
(137389732, 137463371, u'1', u'APPROVED', u'sale', u'100')
(137389733, 137463372, u'1', u'Approved', u'sale', u'100')
(137389734, 137463373, u'1', u'Approved', u'sale', u'100')
(137389735, 137463374, u'1', u'APPROVED', u'refund', u'100')
(137389736, 137463375, u'1', u'Approved', u'sale', u'100')
{
    "rrdata": [
        {
            "rrd": "verifi", 
            "type": "response_code", 
            "val": {
                "100": 41, 
                "200": 3, 
                "201": 2, 
                "202": 3, 
                "204": 2, 
                "223": 4, 
                "891": 1
            }
        }
    ], 
    "system_id": "123456"
}
['DS:201:GAUGE:600:U:U']
{"file": "verifi_201.rrd, "write": "True"}
['DS:200:GAUGE:600:U:U']
{"file": "verifi_200.rrd, "write": "True"}
['DS:202:GAUGE:600:U:U']
{"file": "verifi_202.rrd, "write": "True"}
['DS:204:GAUGE:600:U:U']
{"file": "verifi_204.rrd, "write": "True"}
['DS:891:GAUGE:600:U:U']
{"file": "verifi_891.rrd, "write": "True"}
['DS:100:GAUGE:600:U:U']
{"file": "verifi_100.rrd, "write": "True"}
['DS:223:GAUGE:600:U:U']
{"file": "verifi_223.rrd, "write": "True"}
karl.rink@db01repl3:~/verifi$



karl.rink@db01repl3:~/verifi$ ./response_code.tracker.py run
{
    "201": 1, 
    "200": 10, 
    "202": 8, 
    "250": 1, 
    "204": 1, 
    "300": 1, 
    "225": 5, 
    "100": 57, 
    "223": 2, 
    "801": 7
}
karl.rink@db01repl3:~/verifi$


karl.rink@db01repl3:~/verifi$ ./response_code.tracker.py run
(137361056, 137434677, u'2', u'Transaction failed  because of payment processing failure.: 530 - This transaction has been declined. Please check card details and try again, or contact your bank for assistance', u'sale', u'201')
(137361057, 137434678, u'1', u'Approved', u'sale', u'100')
(137361058, 137434679, u'2', u'Order creation failure due to problematic input., The credit card expiration month must be a number between 1 and 12., The stated credit card expiration date has already passed.', u'sale', u'223')
(137361059, 137434680, u'2', u'Insufficient funds', u'sale', u'202')
(137361060, 137434681, u'2', u'Transaction failed  because of payment processing failure.: 302 - Insufficient funds. Please use another card or contact your bank for assistance', u'sale', u'202')
(137361061, 137434682, u'1', u'Approved', u'sale', u'100')

karl.rink@db01repl3:~/verifi$ time ./response_code.tracker.py run >/dev/null

real	0m0.163s
user	0m0.088s
sys	0m0.012s



