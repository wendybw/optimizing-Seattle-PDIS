import json
import random
from qgis.core import QgsVectorLayer, QgsProject, QgsApplication, QgsSimpleMarkerSymbolLayerBase
from urllib.request import urlopen
from urllib.error import HTTPError

def reachable_tree(lon, lat, uphill, downhill, avoidCurbs, streetAvoidance, max_cost, reverse):
   url = 'http://incremental-alpha.westus.cloudapp.azure.com/api/v1/routing/reachable_tree/custom.json?lon='+str(lon)+'&lat='+str(lat)+'&uphill='+str(uphill)+'&downhill='+str(downhill)+'&avoidCurbs='+str(avoidCurbs)+'&streetAvoidance='+str(streetAvoidance)+'&max_cost='+str(max_cost)

   downloaded_file_prefix = '/walkshed_data/data'
   downloaded_file = downloaded_file_prefix+str(random.randrange(100000))+'.json'
   downloaded_file2 = downloaded_file_prefix+str(random.randrange(100000))+'.json'
   downloaded_file3 = downloaded_file_prefix+str(random.randrange(100000))+'.json'

   try:
       r = urlopen(url)
   except HTTPError as e:
       if e.code == 422:
           print('Validation error: ' + e.read().decode())
           return
       else:
           raise e

   data = json.loads(r.read())

   if not "edges" in data:
       print('No results were returned from AccessMap: ' + str(data))
       return

   with open(downloaded_file, 'w', encoding='utf-8') as f:
       json.dump(data["edges"], f)

   with open(downloaded_file2, 'w', encoding='utf-8') as f:
       json.dump(data["node_costs"], f)

   with open(downloaded_file3, 'w', encoding='utf-8') as f:
       json.dump(data["origin"], f)

   # Add imported data into QGIS
   layer = QgsVectorLayer(downloaded_file, 'Reachable Tree', 'ogr')
   layer.renderer().symbol().setWidth(1)
   layer.triggerRepaint()
   QgsProject.instance().addMapLayer(layer)

   # Add imported data into QGIS
   layer = QgsVectorLayer(downloaded_file2, 'Cost', 'ogr')
   layer.triggerRepaint()
   QgsProject.instance().addMapLayer(layer)

   # Add imported data into QGIS
   layer = QgsVectorLayer(downloaded_file3, 'Origin', 'ogr')
   layer.renderer().symbol().symbolLayer(0).setSize(6)
   layer.renderer().symbol().symbolLayer(0).setShape(QgsSimpleMarkerSymbolLayerBase.Star)
   layer.triggerRepaint()
   QgsProject.instance().addMapLayer(layer)

   QgsApplication.processEvents()

def process_parking_data(csv_file):
   with open(csv_file, 'r') as file:
       headers = file.readline().strip().split(',')
       for line in file:
           values = line.strip().split(',')
           row = dict(zip(headers, values))
           lon = float(row['xcoord'])
           lat = float(row['ycoord'])
           reachable_tree(
               lon=lon,
               lat=lat,
               uphill=0.08,
               downhill=0.1,
               avoidCurbs=0,
               streetAvoidance=1,
               max_cost=600,
               reverse=0
           )

csv_file_path = '/geometry_scope_signs.csv'

# Process the parking data from the CSV file
process_parking_data(csv_file_path)
