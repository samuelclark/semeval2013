#!/bin/bash

/bin/rm -f md5.txt

for k in $(ls task?/*.arc task?/*.pkl task?/*.tsv); do 
    echo -n $k >> md5.txt
    echo -n "	" >> md5.txt
    md5 -q $k >> md5.txt
done
