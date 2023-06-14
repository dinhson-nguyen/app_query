import os

from django.http import HttpResponse
from fiona import Env
import fiona
import json
import shapely
from rest_framework.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.conf import settings
import osm2geojson
from geojson import dump
from urllib.parse import quote
import geojson
import requests
from shapely.geometry import Point
from functools import partial

import pyproj
from shapely.ops import transform
def get_data_from_file_node(request):
    try:
        myfile = request.FILES['geom']
    except:
        return ValidationError({"file not found": "cant find .shp , .geojson file format"})
    file_name = myfile.name
    path = default_storage.save(f'{file_name}', ContentFile(myfile.read()))
    tmp_file = os.path.join(settings.MEDIA_ROOT, path)
    extension = file_name.split('.')[-1]
    if 'shp' in extension:
        with Env(SHAPE_RESTORE_SHX='YES'):
            with fiona.open(tmp_file) as src:
                polygons = []
                try:
                    for record in src:
                        coordinates = record['geometry']['coordinates'][0]
                        lat = [item[1] for item in coordinates[1]]
                        lon = [item[0] for item in coordinates[0]]
                        sound = min(lat)
                        west = min(lon)
                        north = max(lat)
                        east = max(lon)
                        os.remove(tmp_file)
                        return sound, west, north, east
                except:
                    pass

    elif 'geojson' in extension:

        with open(tmp_file) as f:
            data1 = geojson.load(f)
            features = data1.get('features')
            for data in features:
                data_type = data['geometry']['type']
                if data_type =='Polygon':

                    geometry = data['geometry']['coordinates'][0]
                    polygon = shapely.geometry.Polygon(geometry)
                    lat = [item[1] for item in geometry]
                    lon = [item[0] for item in geometry]
                    sound = min(lat)
                    west = min(lon)
                    north = max(lat)
                    east = max(lon)
                    os.remove(tmp_file)
                    return sound,west,north,east, polygon
                elif data_type == 'MultiPolygon':
                    geometry = data['geometry']['coordinates'][0]

                    polygon = shapely.geometry.Polygon(geometry[0])
                    lat = [item[1] for item in geometry[0]]
                    lon = [item[0] for item in geometry[0]]
                    sound = min(lat)
                    west = min(lon)
                    north = max(lat)
                    east = max(lon)
                    os.remove(tmp_file)
                    return sound, west, north, east, polygon
                else:
                    os.remove(tmp_file)
                    return ValidationError({"file not supported": f"type of data {data_type} which is not supported"})
    else:
        os.remove(tmp_file)
        return ValidationError({"file not supported": f"{file_name}file does not supported "})

def get_data_from_file_way(request):
    try:
        myfile = request.FILES['geom']
    except:
        return ValidationError({"file not found": "cant find .shp , .geojson file format"})
    file_name = myfile.name
    path = default_storage.save(f'{file_name}', ContentFile(myfile.read()))
    tmp_file = os.path.join(settings.MEDIA_ROOT, path)
    extension = file_name.split('.')[-1]
    if 'shp' in extension:
        with Env(SHAPE_RESTORE_SHX='YES'):
            with fiona.open(tmp_file) as src:
                polygons = []
                try:
                    for record in src:
                        coordinates = record['geometry']['coordinates'][0]
                        lat = [item[1] for item in coordinates[1]]
                        lon = [item[0] for item in coordinates[0]]
                        sound = min(lat)
                        west = min(lon)
                        north = max(lat)
                        east = max(lon)
                        os.remove(tmp_file)
                        return sound, west, north, east
                except:
                    pass

    elif 'geojson' in extension:

        with open(tmp_file) as f:
            data1 = geojson.load(f)
            features = data1.get('features')
            for data in features:
                data_type = data['geometry']['type']
                if data_type =='Polygon':

                    geometry = data['geometry']['coordinates'][0]
                    polygon = shapely.geometry.Polygon(geometry)
                    lat = [item[1] for item in geometry]
                    lon = [item[0] for item in geometry]
                    sound = min(lat)
                    west = min(lon)
                    north = max(lat)
                    east = max(lon)
                    os.remove(tmp_file)
                    return sound,west,north,east, polygon
                elif data_type == 'MultiPolygon':
                    geometry = data['geometry']['coordinates'][0]

                    polygon = shapely.geometry.Polygon(geometry[0])
                    print(polygon)
                    lat = [item[1] for item in geometry[0]]
                    lon = [item[0] for item in geometry[0]]
                    sound = min(lat)
                    west = min(lon)
                    north = max(lat)
                    east = max(lon)
                    os.remove(tmp_file)
                    return sound, west, north, east, polygon
                else:
                    os.remove(tmp_file)
                    return ValidationError({"file not supported": f"type of data {data_type} which is not supported"})
    else:
        os.remove(tmp_file)
        return ValidationError({"file not supported": f"{file_name}file does not supported "})



def get_node(south,west,north,east):
    query =  f'[out:json];node({south},{west},{north},{east});out geom;'


    url = 'http://localhost/api/interpreter?data='+ quote(query)
    response = requests.get(url)
    data1 = response.text

    dict = json.loads(data1)
    return dict
def get_node_info(id):
    query = f'[out:json];node({id});out skel qt;'

    url = 'http://localhost/api/interpreter?data=' + quote(query)
    response = requests.get(url)
    data1 = response.text

    dict = json.loads(data1)
    m= dict.get('elements')[0]
    return m.get('lat'),m.get('lon')
def get_way_info(id):
    query = f'[out:json];way({id});(._;>;);out skel qt;'

    url = 'http://localhost/api/interpreter?data=' + quote(query)
    response = requests.get(url)
    data1 = response.text

    dict = json.loads(data1)
    m= dict.get('elements')
    return m
def get_way(south,west,north,east):
    query =  f'[out:json];way({south},{west},{north},{east});out geom;'


    url = 'http://localhost/api/interpreter?data='+ quote(query)
    response = requests.get(url)
    data1 = response.text

    dict = json.loads(data1)
    return dict

def get_way_from_node(id):
    query = f'[out:json];node(id:{id});way(bn);out geom;>;out skel qt;'
    url = 'http://localhost/api/interpreter?data='+ quote(query)
    response = requests.get(url)
    data1 = response.text

    dict = json.loads(data1)
    return dict

def get_relation_from_way(id):
    query = f'[out:json];way(id:{id});rel(bw);out meta;>;out skel qt;'
    url = 'http://localhost/api/interpreter?data='+ quote(query)
    response = requests.get(url)
    data1 = response.text
    dict = json.loads(data1)
    return dict

def convert_dict_to_geojson(dict,name):
    p =  osm2geojson.json2geojson(dict)
    with open(f'{name}.geojson', 'w') as f:
        dump(p, f)
def save_geojson_bbox(south,west,north,east):
    dict = get_node(south,west,north,east)
    p =  osm2geojson.json2geojson(dict)
    with open('data_prxcvfhcxfghcgh.geojson', 'w') as f:
        dump(p, f)
def save_geojson_way(id):
    dict = get_way_from_node(id)
    p = osm2geojson.json2geojson(dict)
    with open('data_way.geojson', 'w') as f:
        dump(p, f)

def get_file_geojson(file_name, collection):
    geo = json.dumps(collection, ensure_ascii=False).encode('utf8')
    response = HttpResponse(geo, content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename={}'.format(quote(file_name + '.geojson'))
    return response



def create_buffer_polygon(polygon,buffer_in_meters):
    project = pyproj.Transformer.from_proj(
        pyproj.Proj(init='epsg:4326'),  # source coordinate system
        pyproj.Proj(init='epsg:26913'))  # destination coordinate system
    reverse_transform = pyproj.Transformer.from_proj(
        pyproj.Proj(init='epsg:26913'),  # source coordinate system
        pyproj.Proj(init='epsg:4326'))   # destination coordinate system
    # g1 is a shapley Polygon

    g2 = transform(project.transform, polygon)  # apply projection
    new_polygon = g2.buffer(buffer_in_meters)

    return transform(reverse_transform.transform,new_polygon)
