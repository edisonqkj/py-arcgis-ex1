import os
import numpy

## Point Analysis for input data
## Time: 3/3/14
## Author: Edison Qian

## Referenced Function from Google
## {{{ http://code.activestate.com/recipes/410692/ (r8)
# This class provides the functionality we want. You only need to look at
# this if you want to know how this works. It only needs to be defined
# once, no need to muck around with its internals.
class switch(object):
    def __init__(self, value):
        self.value = value
        self.fall = False
 
    def __iter__(self):
        """Return the match method once, then stop"""
        yield self.match
        raise StopIteration
     
    def match(self, *args):
        """Indicate whether or not to enter a case suite"""
        if self.fall or not args:
            return True
        elif self.value in args: # changed for v1.5, see below
            self.fall = True
            return True
        else:
            return False

def ReadAscii(path):
    f=open(path)
    content=f.readlines()
    f.close()
    '''
    ncols         51.000000
    nrows         47.000000
    xllcorner     6295396.084595
    yllcorner     3713187.770986
    cellsize      499.542418
    NODATA_value  -9999.000000
    '''
    head=map(lambda x:float(x.split()[1]),content[0:6])
    data=map(lambda x:\
             # NODATA-->0
             map(lambda y:0 if float(y)==head[5] else int(y),\
                 x.split()),\
             content[6:])
    return [head,data]

def WriteAscii(head,data,path):
    # add head
    content=['ncols         '+str(int(head[0]))+'\n',\
             'nrows         '+str(int(head[1]))+'\n',\
             'xllcorner     '+str(head[2])+'\n',\
             'yllcorner     '+str(head[3])+'\n',\
             'cellsize      '+str(head[4])+'\n',\
             'NODATA_value  '+str(head[5])+'\n']
    # add data
    content.extend(map(lambda x:' '.join(map(str,x))+' \n',data))
    f=open(path,'w')
    f.writelines(content)
    f.close()

def FocalStatistic(x,y,matrix,size):
    # Extract boudary cells of area marked as 1
    col=len(matrix[0])
    row=len(matrix)
    if x>=size//2 and x<col-size//2 and y>=size//2 and y<row-size//2:
        if sum(map(lambda a:sum(a[x-1:x+1+1]),matrix[y-1:y+1+1]))<9:
            # boudary cells of area
            return 1
        else:
            # inner cells of area
            return 0
    elif (x>=0 and x<size//2) or (x>=col-size//2 and x<col) or\
         (y>=0 and y<size//2) or (y>=row-size//2 and y<row):
        # edge process: here, return 0
        return 0
    else:
        print 'Illegal ('+str(x)+','+str(y)+')'
        return -1

def ContractIndex(ori_index_x,ori_index_y,index_x):
    # remove false index from original index of x,y
    # ori_index_x: x index of before analysis
    # ori_index_y: y index of before analysis
    # index_x: x index of after analysis which equals to 1
    res_index_x=map(lambda x:\
                    [i for i,j in enumerate(x) if j==1],\
                    index_x)
    res_index_y=[ori_index_y[i] \
                 for i,j in enumerate(res_index_x) \
                 if len(j)>0]
    res_index_x=[[ori_index_x[i][b]\
                  for a,b in enumerate(res_index_x[i])]\
                 for i,j in enumerate(res_index_x)\
                 if len(j)>0]
    return [res_index_x,res_index_y]

def ExtractPoints(watershed):
    '''
    watershed:
        1,0
    '''
    col=len(watershed[0])
    row=len(watershed)
    ###################################################
    one_index_x=map(lambda x:\
                [i for i,j in enumerate(x) if j==1],\
                watershed)
    one_index_y=[range(row)[i] \
             for i,j in enumerate(one_index_x) \
             if len(j)>0]
    one_index_x=filter(lambda x:len(x)>0,one_index_x)
    ###################################################
    # locate boudary cells' x,y
    bc_tmp_index_x=map(lambda x,y:\
                       [FocalStatistic(j,y,watershed,fdir,3)\
                        for i,j in enumerate(x)],\
                       one_index_x,one_index_y)
    
    #remove not boudary cells' x,y from index
    boudary_index_x,boudary_index_y=ContractIndex(\
        one_index_x,one_index_y,bc_tmp_index_x)
    
    ###################################################
    # return Point cells' x,y
    return boudary_index_x,boudary_index_y

def PointAnalysis(path_iw,path_out,isprint):
    if isprint:
        print ('Area: '+path_iw)
        print ('Out: '+path_out)
    head_iw,iw=ReadAscii(path_iw)
    # extract Points
    out_index_x,out_index_y=ExtractPoints(iw)
    # write to ascii
    head_out=head_iw
    # NODATA=0
    head_out[5]=0
    # mark Point in data matrix
    Point=map(lambda x:map(lambda y:y*0,x),iw)
    if isprint:
        print ('Points x,y index:')
    for i,j in enumerate(out_index_y):
        for k in out_index_x[i]:
            if isprint:
                print str(j)+','+str(k)
            Point[j][k]=1
    if isprint:
        print ('Num of Points: '+str(reduce(lambda x,y:x+y,\
                                             map(lambda a:a.count(1),Point))))
    # call write
    WriteAscii(head_out,Point,path_out)
    if isprint:
        print ('PointAnalysis is finished......')
