# -*- coding: utf-8 -*-
"""
Created on Tue Feb 19 10:30:00 2019

@author: smh
"""

import h5py
import numpy as np

dtype=dtype=[("colA","U2"),("colB","U2")]
data  =np.array([("a","a"),("x","X"),("c","c")],dtype=dtype)
print(data)



s=data["colA"][0]
print(type(s))


dtype=[("colA","S2"),("colB","S2")]
f = h5py.File("test_dtype.hdf", 'w')
dset = f.create_dataset("test", (len(data),), dtype=dtype,
                compression="gzip", compression_opts=4)
dset[:]=data
print(dset[:])


f.close()


#hasattr(bytearray, 'decode') and isinstance(bytearray.decode(), str)