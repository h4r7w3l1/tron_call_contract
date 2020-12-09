#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import csv
from random import randint
from time import sleep
import json
import configparser
import argparse
from decimal import Decimal
from tronpy import Tron
from tronpy.keys import PrivateKey
from tronpy.exceptions import AddressNotFound

config = configparser.ConfigParser()
config.read("config.ini")  # Testnet tronchain = nile  or Real   tronchain = mainnet


# Присваиваем значения внутренним переменным
tronchain   = config['TronNile']['tronchain']
pk = config['TronNile']['pk']
ctraddr = config['TronNile']['contract']
amount = 130
parser = argparse.ArgumentParser(description='Value TRX. Default or not set: 130 trx')
parser.add_argument('-a', '--amount', type=int, action='store', dest='amount', default='130', required=True)
args = parser.parse_args()
print(args)

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
	if kpub_balance >= amount:
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
		amountFreeze = (freez20persent * 1000000)
		txnfreez = (
			client.trx.freeze_balance(walletgen_pub, int(amountFreeze),  "ENERGY")
			.build()
			.sign(priv_key)
			)
		print(txnfreez.txid)
		hold_result = txnfreez.broadcast().wait()
		print(hold_result)
		sleep(160)
	#else if
		walletgen_pub_bal = client.get_account_balance(walletgen_pub)
		print(check_balance(walletgen_pub))
		cntr = client.get_contract(ctraddr)  # contract address to call
		amountCntr = (walletgen_pub_bal * 1000000)
		txcall = (
			cntr.functions.deposit.with_transfer(amountCntr)	# 100_000_000 = 100
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


runtron = main(pk, amount)
