# -*- coding: utf-8 -*-
"""
Created on Thu Apr 25 15:05:33 2019

@author: smh
"""

import csv
f = open("sample.csv", "wb")
writer = csv.writer(f)
writer.writerows([['string'.encode('ascii'), 1], ['string'.encode('ascii'), 2]])
f.close()

reader = csv.reader(open("sample.csv", "rb"))
print (reader.next())