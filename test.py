"""
пасрит XML файлы ZoneToGKN и TerritoryToGKN формирую mif/mid файлы по координатам указанным в XML.
Можго парсить много вложенных папок. Файлы mif/mid пишутся в теже директории, где лежат ZoneToGKN и TerritoryToGKN в формате UUID.mif и UUID.mid
"""
from shapely.geometry import Polygon
from shapely.geometry import Point
from lxml import etree, objectify
import sys
import os
import uuid
from xml.dom import minidom
import glob


def parseXML (xmlFileTerr, xmlFileZone):
    """
    парсим XML и формируем массив контуров
    """
    xml_doc_terr = minidom.parse(xmlFileTerr)
    contours = []
    EntitySpatial = xml_doc_terr.getElementsByTagNameNS('*', 'EntitySpatial')
    SpatialElement = EntitySpatial[0].getElementsByTagNameNS('*', 'SpatialElement')
    for sp_item in SpatialElement:
        contour = []
        SpelementUnit = sp_item.getElementsByTagNameNS('*', 'SpelementUnit')
        for sp_unit in SpelementUnit:
            Ordinate = sp_unit.getElementsByTagNameNS('*', 'Ordinate')
            contour.append(str(Ordinate[0].getAttribute('Y') + ' ' + Ordinate[0].getAttribute('X')))
        contours.append(contour)
    xml_doc_zone = minidom.parse(xmlFileZone)
    name_by_doc = xml_doc_zone.getElementsByTagNameNS('*', 'CodeZoneDoc')
    zoneName = name_by_doc[0].firstChild.data
    return contours, zoneName

def fileList(directory):
    """
    функция получает директорию и возвращает спиок файлов XML в указанной директории
    """
    files = []
    files = glob.glob(directory + '/**/TerritoryToGKN_*.xml', recursive=True)
    fileList = []
    for f in files:
        fileTerr = glob.glob(os.path.dirname(f) + '\\TerritoryToGKN_*.xml')
        fileZone = glob.glob(os.path.dirname(f) + '\\ZoneToGKN_*.xml')
        fileList.append((fileTerr[0], fileZone[0], os.path.dirname(f)))
    return fileList

def listToPolygon(coordList):
    """
    функция принимает на вход список координат и выдает объект типа Polygon
    """
    listCoordinates = []
    for item in coordList:
        coord = item.split()
        coordTuple = (float(coord[0]), float(coord[1]))
        listCoordinates.append(coordTuple)
    polygon = Polygon(listCoordinates)
    return polygon


def writeMIF(contoursList, dir_path_to_write):
    """
    формируем MIF файл маза фака
    """
    guid = str(uuid.uuid1())
    outMifFile = dir_path_to_write + '\\' + guid + '.mif'
    outMidFile = dir_path_to_write + '\\' + guid + '.mid'
    file_out_mif = open(outMifFile, 'w', encoding='UTF-8') #
    file_out_mid = open(outMidFile, 'w', encoding='UTF-8') 

    print('Version 300', file=file_out_mif)
    print('Charset "Neutral"', file=file_out_mif)
    print('Delimiter ","', file=file_out_mif)
    print('CoordSys NonEarth Units "m" Bounds (0, 0) (20000000, 20000000)', file=file_out_mif)
    print('Columns 3', file=file_out_mif)
    print('  ID Integer', file=file_out_mif)
    print('  LABEL Char(254)', file=file_out_mif)    
    print('  NOTE Char(254)', file=file_out_mif)
    print('Data\n', file=file_out_mif)
    
    i = 0
    for contour in range(len(contoursList[0])):
        if len(contoursList[0]) > 1 and i < len(contoursList[0]) - 1 and isinstance(listToPolygon(contoursList[0][i]).intersection(listToPolygon(contoursList[0][i+1])), Polygon) and contour == i:
            contoursIn = 0
            for c in range(len(contoursList[0])-i):
                if isinstance(listToPolygon(contoursList[0][i]).intersection(listToPolygon(contoursList[0][c+i])), Polygon) and c > 0: 
                    contoursIn += 1
            if contoursIn >0:
                print('Region {}'.format(contoursIn), file=file_out_mif)
                print(len(contoursList[0][i]), file=file_out_mif)
                for item in contoursList[0][i]:
                    print(item, file=file_out_mif)
                for con in range(contoursIn):
                    if con > 0:
                        print(len(contoursList[0][i+con]), file=file_out_mif)
                        for it in contoursList[0][i+con]:
                            print(it, file=file_out_mif)
                i += (contoursIn + 1)
        elif contour == i:
            print('Region 1', file=file_out_mif)
            print(len(contoursList[0][contour]), file=file_out_mif)
            for item in contoursList[0][contour]:
                print(item, file=file_out_mif)
            i += 1

#    for contour in contoursList[0][0]:
#        print('Region 1', file=file_out_mif)
#        print(len(contour), file=file_out_mif)
#        for item in contour:
#            print(item, file=file_out_mif)

    print(',,"{}"'.format(contoursList[1]), file=file_out_mid)
    file_out_mif.close()
    file_out_mid.close()

if __name__ == '__main__':
    fList = fileList(os.path.abspath(os.curdir))
    count = 1
    lenfList = len(fList)
    for item in fList:
        writeMIF(parseXML(item[0], item[1]), item[2])
        print(str(count) + ' from {}'.format(lenfList))
        count += 1

