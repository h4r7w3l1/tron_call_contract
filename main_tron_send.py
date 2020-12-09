#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import argparse
from random import randint
from time import sleep
import json
import configparser
import argparse
from tronpy import Tron
from tronpy.keys import PrivateKey
from tronpy.exceptions import TransactionError
from time import time
import colorama
from colorama import Fore, Back, Style

colorama.init()

logdir = "logs"
config = configparser.ConfigParser()
config.read("config.ini")


NETWORK="NILE" # "MAINNET"

"""
Set blockchain mode above. One param for all configs.
! Use  NETWORK="MAINNET"  for real coins run
---
P.S. Varible [pk] - with privkey init below (35 line)
    If args -p/--pk not use, [pk] sets from config.ini
"""

tronchain = config[NETWORK]['tronchain']
ctraddr = config[NETWORK]['contract']


parser = argparse.ArgumentParser()
parser.add_argument('-a', '--amount', action='store',
                    dest='amount', required=True, type=str)
parser.add_argument('-w', '--wallet', action='store',
                    dest='walletreciver', required=True, type=str)
parser.add_argument('-m', '--memo', action='store',
                    dest='memo', type=str)
parser.add_argument('-p', '--pk', action='store',
                    dest='pk')
args = parser.parse_args()
if args.pk is None:
    pk = config[NETWORK]['pk'] #print("Set from config")
else:
    pk = args.pk #print("set from args")
    
client = Tron(network=tronchain)


result_log = []

def write_to_file():
    	with open(os.path.join(logdir, "main_send_tron_log.txt"), 'a+', encoding='utf-8') as f:
            f.write('\n'.join(str(x) for x in result_log))
            f.write('\n')
            f.close()

def epoch():
    milliseconds = int(time() * 1000)
    return ("["+str(milliseconds)+"]")

def transaction(holder_pubkey, amountconv, priv_key):
    try:
        txn = (
            client.trx.transfer(holder_pubkey, args.walletreciver, amountconv)
            .memo(args.memo)
            .build()
            .sign(priv_key)
        )
        transid = txn.txid
        trnresult = txn.broadcast().wait()
        #print("Tx raw: ", trnresult)
        return trnresult, transid
    except TransactionError:
        return 'Transaction error'


def sendtrx(pk, **kwargs):
    priv_key = PrivateKey(bytes.fromhex(pk))
    holder_pubkey = priv_key.public_key.to_base58check_address()
    holder_balance = client.get_account_balance(holder_pubkey)
    holder_resource = client.get_account_resource(holder_pubkey)
    timeid = epoch()
    print(timeid," - Avalible on", holder_pubkey, ":",Fore.RED, holder_balance, "TRX"+Style.RESET_ALL," |",Fore.GREEN, holder_resource["freeNetUsed"],"/ 5000 Bandwidth"+Style.RESET_ALL," |",Fore.YELLOW, holder_resource["EnergyLimit"], "Energy"+Style.RESET_ALL)

    amountconv = (int(args.amount) * 10 ** 6 )
    trnresult, transid = transaction(holder_pubkey, amountconv, priv_key)
    #Logging
    logmess = print('TX:'+ transid+":"+Fore.LIGHTMAGENTA_EX+" Send "+ str(args.amount)+ " TRX -> "+ args.walletreciver +Style.RESET_ALL+"| Memo: \""+args.memo+"\"")
    logmess = ('TX:'+ transid+":"+Fore.LIGHTMAGENTA_EX+" Send "+ str(args.amount)+ " TRX -> "+ args.walletreciver +Style.RESET_ALL+"| Memo: \""+args.memo+"\"")
    result_log.append(logmess)
    logmess = ("Transaction:",json.dumps(trnresult))
    result_log.append(logmess)
    write_to_file()


sendtrx(pk)
