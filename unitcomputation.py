# -*- coding: cp936 -*-
import os
import sys
import arcpy
from test_clearfile import *
from PointAnalysis import *

## Unit Computation for each input data file
## Time: 3/3/14
## Author: Edison Qian
    
def ExtractRidge(ascii_path):
    isprint=False
    # full path of file
    if isprint:
        print("Dealing with %s" %ascii_path)
    base,filename=os.path.split(ascii_path)
    name=filename.split('.')[0]
    fileformat=filename.split('.')[1]

    # 0. Prepare Temporal & Result Directory
    if isprint:
        print ('###################################')
    tmp_dir=base+'/t'+name+'/'
    res_dir=base+'/c'+name+'/'
    # Temporal
    if os.path.exists(tmp_dir):
        if isprint:
            print ('Exist '+tmp_dir)
        CleanDir(tmp_dir,isprint)
        if isprint:
            print ('Clear '+tmp_dir)
    os.mkdir(tmp_dir)
    if isprint:
        print ('Create '+tmp_dir)
    # result
    if os.path.exists(res_dir):
        if isprint:
            print ('Exist '+res_dir)
        CleanDir(res_dir,isprint)
        if isprint:
            print ('Clear '+res_dir)
    os.mkdir(res_dir)
    if isprint:
        print ('Create '+res_dir)

    arcpy.env.workspace = tmp_dir
    # 1. Create DEM Raster
    dem=tmp_dir+'dem'
    rasterType = "INTEGER"
    Ascii2Raster(ascii_path,rasterType,dem,isprint)
    if isprint:
        print ('1 is finished......')

    # 2. Fill DEM
    fill=tmp_dir+'fill'
    Fill(dem,fill,isprint)
    if isprint:
        print ('2 is finished......')

    # 3. Flow Direction
    fdir=tmp_dir+'fdir'
    ffdir=tmp_dir+'ffdir'
    map(FlowDirection,[dem,fill],[fdir,ffdir],[isprint,isprint])
    if isprint:
        print ('3 is finished......')

    # 4. Filled Area & Select Max Area
    filledarea=tmp_dir+'filledarea'
    plg=tmp_dir+'plg.shp'
    plg_area=tmp_dir+'plg_area.shp'
    plg_area_mshp=tmp_dir+'plg_area_max.shp'
    plg_area_mrst=tmp_dir+'plg_area_max'
    cellsize=499.542418
    
    GetFilledArea(dem,fill,filledarea,isprint)
    Raster2Polygon(filledarea,plg,isprint)
    CalShpArea(plg,plg_area,isprint)
    GetMaxAreaFeature(plg_area,plg_area_mshp,isprint)
    Polygon2Raster(plg_area_mshp,cellsize,dem,plg_area_mrst,isprint)
    if isprint:
        print ('4 is finished......')
    
    # 5. Initial Watershed
    iwatershed=tmp_dir+'iwatershed'
    Watershed(fdir,plg_area_mrst,dem,iwatershed,isprint)
    if isprint:
        print ('5 is finished......')

    # 6. Convert Filled Direction & Initial Watershed to Ascii
    iw_asc=tmp_dir+'iw.txt'
    Raster2Ascii(iwatershed,iw_asc,isprint)
    if isprint:
        print ('6 is finished......')

    # 7. Extract Points from Ascii
    point_asc=tmp_dir+'point.txt'
    PointAnalysis(iw_asc,point_asc,isprint)
    if isprint:
        print ('7 is finished......')

    # 8. Create point Raster
    point=tmp_dir+'point'
    rasterType = "INTEGER"
    Ascii2Raster(point_asc,rasterType,point,isprint)
    if isprint:
        print ('8 is finished......')

#
# Functions
#
def Ascii2Raster(ascii,rasterType,raster,isprint):
    arcpy.ASCIIToRaster_conversion(ascii, raster, rasterType)
    if isprint:
        print ('Ascii2Raster is finished....')

def Raster2Ascii(raster,ascii,isprint):
    arcpy.RasterToASCII_conversion(raster, ascii)
    if isprint:
        print ('Raster2Ascii is finished....')
    
def CalShpArea(inshp,outshp,isprint):
    arcpy.CalculateAreas_stats(inshp, outshp)
    if isprint:
        print ('CalShpArea is finished....')

def GetMaxAreaFeature(inshp,outshp,isprint):
    records=arcpy.SearchCursor(inshp,"","","","")
    feature_area=[]
    ID=[]
    for record in records:
        if int(record.GRIDCODE)==1:
            feature_area.append(float(record.F_AREA))
            ID.append(int(record.ID))
    index=feature_area.index(max(feature_area))
    where_clause = '"ID" = '+str(ID[index])
    arcpy.Select_analysis(inshp, outshp, where_clause)
    if isprint:
        print ('GetMaxAreaFeature is finished....')

def Fill(dem,fill,isprint):
    arcpy.CheckOutExtension("spatial")
    arcpy.gp.Fill_sa(dem, fill, "")
    if isprint:
        print ('Fill is finished....')

def FlowDirection(dem,flowdir,isprint):
    arcpy.CheckOutExtension("spatial")
    arcpy.gp.FlowDirection_sa(dem, flowdir, "NORMAL", '')
    if isprint:
        print ('FlowDirection is finished....')

def GetFilledArea(dem,fill,filledarea,isprint):
    arcpy.CheckOutExtension("spatial")
    base,filename=os.path.split(dem)
    minus=base+'/minus'
    arcpy.gp.Minus_sa(dem, fill,minus)
    arcpy.gp.LessThan_sa(minus, 0,filledarea)
    if isprint:
        print ('GetFilledArea is finished....')

def Raster2Polygon(raster,plg,isprint):
    arcpy.RasterToPolygon_conversion(raster, plg, "NO_SIMPLIFY", "VALUE")
    if isprint:
        print ('Raster2Polygon is finished....')

def Polygon2Raster(plg,cellsize,extent,raster,isprint):
    #GRIDCODE=1
    arcpy.env.extent=extent
    arcpy.env.snapRaster=extent
    arcpy.PolygonToRaster_conversion(plg, "GRIDCODE", raster, "CELL_CENTER", "NONE", cellsize)
    if isprint:
        print ('Polygon2Raster is finished....')

def Watershed(flowdir,point,extent,watershed,isprint):
    #point: raster or point shp
    arcpy.CheckOutExtension("Spatial")
    field="VALUE"
    arcpy.gp.Watershed_sa(flowdir,point,watershed,field)
    if isprint:
        print ('Watershed is finished....')
