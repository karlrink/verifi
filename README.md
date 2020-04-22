# nutil/verifi

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



