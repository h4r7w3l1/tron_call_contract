from tronpy import Tron
from tronpy.keys import PrivateKey
import time
import csv
from time import sleep
client = Tron(network='main')

def main():
    cntr = client.get_contract("TWiti6GpPJPRXtCFKURdTtxN7UEcurQoeS")
    f=open("listaddresstronexonepython.txt", "r")
    f1 = f.readlines()
    for x in f1:
        x = x.strip('\n')
        sleep(3)
        print(x, cntr.functions.getUserReferralBonus(x), cntr.functions.getUserReferrer(x))


if __name__=="__main__":
    main()


