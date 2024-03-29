﻿#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
from random import randint
from time import sleep
import json
import configparser
from decimal import Decimal
from tronpy import Tron
from tronpy.keys import PrivateKey
from tronpy.exceptions import AddressNotFound

config = configparser.ConfigParser()
config.read("config.ini") 

NETWORK="NILE" # "MAINNET"

# Присваиваем значения внутренним переменным
tronchain   = config[NETWORK]['tronchain']
pk = config[NETWORK]['pk']
ctraddr = config[NETWORK]['contract']
tronctl = config[NETWORK]['tronctl']

client = Tron(network=tronchain)

def write_to_file(content, path):
	with open(path,'a+',encoding='utf-8') as f:
		f.write("\n")
		f.write(json.dumps(content,ensure_ascii=True))
		

def walletgenerate():
	walletgen = client.generate_address()
	walletgen_pub = walletgen["base58check_address"]
	walletgen_pk = walletgen["private_key"]
	print("Gen new addr:", walletgen_pub + ", priv:", walletgen_pk)
	write_to_file(walletgen, path="generate_wallets.txt")
	return walletgen_pub, walletgen_pk

def check_balance(address):
	try:
		walletgen_pub_bal = client.get_account_balance(address) #> Decimal('399.202692')
		print("Check balance for", address + " =", walletgen_pub_bal)
		return walletgen_pub_bal
	except AddressNotFound:
		return 'Adress not found..!'

def main(pk, amount):
	#Init
	priv_key = PrivateKey(bytes.fromhex(pk))
	kpub = priv_key.public_key.to_base58check_address()	# Get address from private key
	kpub_balance = client.get_account_balance(kpub) #> Decimal('399.202692')
	amountconv = (amount * 1000000)
	if kpub_balance >= int(amount):
		walletgen_pub, walletgen_pk =  walletgenerate()
		txn = (
			client.trx.transfer(kpub, walletgen_pub, amountconv)
			.build()
			.sign(priv_key)
			)
		print("Transaction:",txn.txid)
		trnresult = txn.broadcast().wait()
		print("Tx raw: ", trnresult)
		write_to_file(trnresult, path="send_trx_log.txt")
		# After transfer
		sleep(60)
		walletgen_pub_bal = client.get_account_balance(walletgen_pub)
		print(check_balance(walletgen_pub))
		priv_key = PrivateKey(bytes.fromhex(walletgen_pk)) # restart object
		freez20persent =  (float(walletgen_pub_bal) - (float(walletgen_pub_bal) * 0.8))
		freez20persentint = str(int(freez20persent))
		freezedelegat = os.system(tronctl +" account freeze " + freez20persentint + " --delegate " + walletgen_pub + " -t 1 -s another-imported -v")
		print(freezedelegat)
		sleep(160)
	#else if
		walletgen_pub_bal = client.get_account_balance(walletgen_pub)
		print(check_balance(walletgen_pub))
		cntr = client.get_contract(ctraddr)  # contract address to call
		amountCntr = (walletgen_pub_bal * 1000000)
		txcall = (
			cntr.functions.deposit.with_transfer(int(amountCntr))	# 100_000_000 = 100
			.call(walletgen_pub)
			.with_owner(walletgen_pub)  # address of the _sender
			.fee_limit(5_000_000)
			.build()
			.sign(priv_key)
			)
		print(txcall.txid)
		call_result = txcall.broadcast().wait()
		print(call_result)
		write_to_file(call_result, path="call_cantract_log.txt")
	else:
    		print("Not enought money")
	# print(check_balance(walletgen_pub))

if __name__ == "__main__":
    if len (sys.argv) > 1:
    		amount = sys.argv[1]
    		runtron = main(pk, int(amount))
    else:
        print ("Need amount sum")
