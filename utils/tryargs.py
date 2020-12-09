import argparse
from random import randint
from time import sleep
import configparser
import argparse
from time import time

config = configparser.ConfigParser()
config.read("config.ini")

NETWORK="NILE" # "MAINNET"


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
# print(args.link)
if args.pk is None:
    pk = config[NETWORK]['pk']
    print("Set from config")
else:
    pk = args.pk
    print("set from args")

print(pk)
