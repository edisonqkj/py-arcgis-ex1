# -*- coding: cp936 -*-
import os
import sys
import datetime
from multiprocessing import Pool
from unitcomputation import *

## Master Control Function
## Time: 3/3/14
## Author: Edison Qian

if __name__ == '__main__':
    files=['E:/select/r0_51x47.txt',
           'E:/select/r0_79x77.txt',
           'E:/select/r0_89x65.txt',
           'e:/select/r0_101x109.txt',
           'e:/select/r0_104x88.txt',
           'e:/select/r0_127x80.txt',
           'e:/select/r0_139x136.txt',
           'e:/select/r0_204x209.txt']
    
    print ('')
    print ('###################################')
    pool_costtime_start= datetime.datetime.now()

    pool = Pool(len(files))
    pool.map(ExtractRidge, files)
    pool.close()
    pool.join()

    print ('[Pool Cost time: '+\
           str((datetime.datetime.now() - pool_costtime_start).seconds)+\
          ' seconds]')
    
    print ('')
    print ('###################################')
    single_costtime_start= datetime.datetime.now()
    map(ExtractRidge, files)
    print ('[Single Cost time: '+\
          str((datetime.datetime.now() - single_costtime_start).seconds)+\
          ' seconds]')
    
