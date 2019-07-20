#! /usr/bin/env python
import uuid
import hashlib
import requests
import xmltodict
from datetime import date, datetime
import argparse

balance_url = "https://api.privatbank.ua/p24api/balance"
transactions_url = "https://api.privatbank.ua/p24api/rest_fiz"


request_template = """<?xml version="1.0" encoding="UTF-8"?>
<request version="1.0">
<merchant>
{merchant}
</merchant>
<data>{data}</data>
</request>
"""

balance_data_template = """<oper>cmt</oper>
<wait>0</wait>
<test>0</test>
<payment id="{payment_id}">
<prop name="cardnum" value="{cardnum}" />
<prop name="country" value="UA" />
</payment>"""


transactions_data_template = """<oper>cmt</oper>
<wait>0</wait>
<test>0</test>
<payment id="{payment_id}">
<prop name="sd" value="{sd}" />
<prop name="ed" value="{ed}" />
<prop name="cardnum" value="{cardnum}" />
</payment>"""

merchant_template="""
<id>{id}</id>
<signature>{signature}</signature>
"""



def current_balance(client_id, secret, card):
    id = uuid.uuid4()
    data = balance_data_template.format(payment_id=str(id), cardnum=card)
    data_for_sig = data + secret
    signature = hashlib.sha1(hashlib.md5(data_for_sig.encode("utf-8")).hexdigest().encode("utf-8")).hexdigest()
    merchant = merchant_template.format(id=client_id, signature=signature)
    request = request_template.format(merchant=merchant, data= data)
    r = requests.post(balance_url,  data=request)
    content = xmltodict.parse(r.content)
    amount = content['response']['data']['info']['cardbalance']['balance']
    return amount
    

def get_transactions(client_id, secret, card, from_date, to_date):
    id = uuid.uuid4()
    data = transactions_data_template.format(payment_id=str(id), cardnum=card, sd=from_date, ed=to_date)
    data_for_sig = data + secret
    signature = hashlib.sha1(hashlib.md5(data_for_sig.encode("utf-8")).hexdigest().encode("utf-8")).hexdigest()
    merchant = merchant_template.format(id=client_id, signature=signature)
    request = request_template.format(merchant=merchant, data= data)
    r = requests.post(transactions_url,  data=request)
    content = xmltodict.parse(r.content)
    statements = content['response']['data']['info']['statements']
    if 'statement' in statements:
        statements = statements['statement']
    else:
        return []
    transactions = []
    for statement in statements:
        transaction = {}
        trantime = statement["@trandate"] +" " + statement["@trantime"]
        trantime = datetime.strptime(trantime, '%Y-%m-%d %H:%M:%S')
        transaction["datetime"] = trantime
        transaction["amount"] = statement["@amount"].split()[0]
        transaction["rest"] = statement["@rest"].split()[0]
        transaction["terminal"] = statement["@terminal"]
        transaction["description"] = statement["@description"]
        transactions.append(transaction)
    return transactions