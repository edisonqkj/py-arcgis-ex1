# -*- coding: cp936 -*-
import os
import shutil

def CleanDir(Dir,isprint):
    if os.path.isdir( Dir ):
        paths = os.listdir( Dir )
        for path in paths:
            filePath = os.path.join( Dir, path )
            if os.path.isfile( filePath ):
                try:
                    os.remove( filePath )
                except os.error:
                    #ref logging
                    autoRun.exception( "remove %s error." %filePath )
            elif os.path.isdir( filePath ):
                if filePath[-4:].lower() == ".svn".lower():
                    continue
                shutil.rmtree(filePath,True)
    if isprint:
        print 'all files are removed......'
    os.rmdir(Dir)
    if isprint:
        print Dir+' is also removed'
    return True
