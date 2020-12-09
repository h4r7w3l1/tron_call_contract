#!/usr/bin/env python3
from tronpy import keys

def main():
    f=open("list.txt", "r")
    f1 = f.readlines()
    for x in f1:
        x = x.strip('\n')
        print(x, keys.to_base58check_address(x))


if __name__=="__main__":
    main()
