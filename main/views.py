from django.shortcuts import render
import requests
from rest_framework.exceptions import ValidationError
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from shapely.geometry import Polygon
from django.contrib.gis.geos import MultiPolygon, Polygon
import urllib.request
import urllib.parse
from .core import *
import osm2geojson
from shapely.geometry import Point, Polygon

# Create your views here.



class DataViewSet(viewsets.ModelViewSet):
    @action(detail=False,methods=['patch'],url_path='node')
    def get_node_data(self,request):
        name = request.data.get('name', None)
        if name is None:
            name = "data"
        sound, west, north, east,polygon = get_data_from_file_node(request)
        node_data = get_node(sound, west, north, east)
        meta = []
        for item in node_data.get('elements'):

            lat = item.get('lat')
            lon = item.get('lon')
            point = Point(lon, lat)
            is_inside = point.within(polygon)
            if not is_inside:
                meta.append(item)
            else:
                pass
        for i in meta:
            node_data.get('elements').remove(i)

        # file = convert_dict_to_geojson(node_data,'tests_final')

        return get_file_geojson(file_name=name,collection=node_data)

    @action(detail=False, methods=['patch'], url_path='way')
    def get_way_data(self, request):
        name = request.data.get('name', None)
        if name is None:
            name = "data"
        sound, west, north, east,polygon = get_data_from_file_way(request)
        way_data = get_way(sound, west, north, east)
        print([sound, west, north, east])

        index =0
        for item in way_data.get('elements'):
            remove_list = []
            meta =[]
            list_node_remove =[]
            if item.get('type') =='way':
                id_way = item.get('id')
                data_id_way = get_way_info(id_way)
                for i in data_id_way:

                    lat = i.get('lat')
                    lon = i.get('lon')
                    try:
                        point = Point(lon, lat)

                        is_inside = point.within(polygon)
                    except:
                        is_inside = False
                    if not is_inside:
                        remove_list.append(i)
                    else:
                        pass
                for k in remove_list:
                    try:
                        way_data.get('elements')[index].get('nodes').remove(k)
                        list_node_remove.append(k)
                    except:
                        pass


                index = index + 1
                print(index)
            else:
                lat = item.get('lat')
                lon = item.get('lon')
                point = Point(lon, lat)
                is_inside = point.within(polygon)
                if not is_inside:
                    meta.append(item)
                else:
                    pass
            for i in meta:
                way_data.get('elements').remove(i)




        p = osm2geojson.json2geojson(way_data)
        k = convert_dict_to_geojson(way_data,'test1055')
        return get_file_geojson(name,p)

    @action(detail=False, methods=['patch'], url_path='test')
    def get_test(self, request):
        name = request.data.get('name', None)
        if name is None:
            name = "data"
        sound, west, north, east, polygon1 = get_data_from_file_way(request)
        way_data1 = get_way(sound, west, north, east)
        all_way_data =way_data1.get('elements')
        print([sound, west, north, east])
        print( polygon1)
        polygon = create_buffer_polygon(polygon1,200)
        print(polygon)
        elements = []
        i = 0
        for way_data in all_way_data:
            del way_data['bounds']
            list_node = way_data.get('nodes')
            index = len(list_node)-1
            data_node = way_data.get('geometry')

            while index >= 0:
                lat = data_node[index].get('lat')
                lon = data_node[index].get('lon')
                point = Point(lon, lat)
                is_inside = point.within(polygon)
                if not is_inside:
                    way_data1.get('elements')[i].get('nodes').pop(index)
                    way_data1.get('elements')[i].get('geometry').pop(index)

                index = index -1
            i = i+1
            print(i)

        p = osm2geojson.json2geojson(way_data1)
        k = convert_dict_to_geojson(way_data1, 'test1000')
        return  get_file_geojson(name, p)




