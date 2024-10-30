import fiona
import pandas as pd
import xml.etree.ElementTree as ET
from pyproj import Proj

def read_metadata(meta_file):
    """ Load the XML file
    meta_file: str - metadata.xml
    return:
        srs: str - epsg
        srr_origin: - translation

    """
    tree = ET.parse(meta_file)
    root = tree.getroot()
    srs = root.findall('SRS')[0].text
    srs_origin = [float(c) for c in root.findall('SRSOrigin')[0].text.split(',')]
    return srs, srs_origin


def write_poly(lonlat, shape_file):
    # define schema
    schema = {
        'geometry':'Polygon',
        'properties':[('Name','str')]
    }

    #open a fiona object
    polyShp = fiona.open(shape_file, mode='w', driver='ESRI Shapefile', schema=schema, crs="EPSG:4326")

    #save record and close shapefile
    rowDict = {
        'geometry' : {
            'type':'Polygon',
            'coordinates': [lonlat]
        },
        'properties': {
            'Name' : 'test'
        },
    }
    polyShp.write(rowDict)
    polyShp.close()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--poly_file", type=str, help=".txt file", default="data/poly.txt")
    parser.add_argument("--shape_file", type=str, help="output .shp file", default="output/roi.shp")
    parser.add_argument("--meta_file", type=str, help="metadata.xml", default="data/metadata.xml")
    args = parser.parse_args()

    # read points
    with open(args.poly_file, 'r') as f:
        polydata = [[float(l) for l in line.split(',')] for line in f.readlines()]
    
    # read metadata.xml
    epsg, t = read_metadata(args.meta_file)

    # utm(x,y,z) --> lon,lat,alt
    proj = Proj(epsg)
    xyList = []
    for i in range(len(polydata)):
        x, y = polydata[i][0] + t[0], polydata[i][1] + t[1]
        lon, lat = proj(x, y, inverse=True)
        xyList.append((lon, lat))
    
    write_poly(xyList, args.shape_file)
    
