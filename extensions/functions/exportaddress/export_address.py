import uuid
import urllib2, urllib
import json
from pprint import pprint as pp
from django.core.exceptions import ValidationError
from arches.app.models import models
from arches.app.models.tile import Tile
from arches.app.functions.base import BaseFunction
from arches.app.datatypes.datatypes import DataTypeFactory
from django.contrib.gis.geos import GEOSGeometry

details = {
    'functionid':'2b4906f2-06e2-4287-ad1b-5597f4404c1f',
    'name': 'Export Address',
    'type': 'node',
    'description': 'Just a sample demonstrating node group selection',
    'defaultconfig': {"external_address_url":"", "target_fields":[], "geometry_node":"", "external_reference_node":""},
    'classname': 'ExportAddress',
    'component': 'views/components/functions/export-address'
}

class ExportAddress(BaseFunction):

    def save(self, tile, request):
        self.url = self.config['external_address_url']
        self.geometry_node = self.config['geometry_node']
        self.external_reference_node = self.config['external_reference_node']
        print self.config['target_fields']
        self.field_lookup = {field['node']: field['name'] for field in self.config['target_fields']}
        tile_edits = json.loads(request.POST.get('data'))['data']
        if request:
            address = {
                "geometry": {
                    "spatialReference": {
                        "wkid": 102100,
                        "latestWkid": 3857
                    }
                },
                "attributes": {
                    "EAS_BaseID": None,
                    "EAS_SubID": None,
                    "CNN": None,
                    "Address": None,
                    "Address_Number": None,
                    "Address_Number_Suffix": None,
                    "Street_Name": None,
                    "Street_Type": None,
                    "Unit_Number": None,
                    "Zipcode": None,
                    "Block_Lot": None,
                    "Longitude": None,
                    "Latitude": None,
                    "Location": None
                }
            }

            payload = {
                "adds":[],
                "updates":[],
                "deletes":'',
                "attachments":[],
                "rollbackOnFailure": False,
                "useGlobalIds": False,
                "f": "pjson",
                "token": "tTzVkJ7RPpZmqmlxc7xVBaORWK8vIKQenSkbmK13OnDfIHNKaNCIaH3i6Nz1AUbdnqkEsz8HuA-QqYrndP4yyqgov0NUgabK3lOO19erL-YYPtbIhEzahbSeQ0wPkJx1TH7RVL-gJ9m3iBsV9Affr0NczrLunSdj6rsa1Kg4QI8fTWpdgj0VCy7FaANWggjI6b7kDATtb43W9-hHxmndcjEU9S7lBzCfTty1b4GnAF3dmYhoh4ZBLC-XpsLetKEJ"
            }

            result_node = models.Node.objects.get(pk=self.external_reference_node)

            external_reference = Tile.objects.filter(nodegroup=result_node.nodegroup).filter(resourceinstance=tile.resourceinstance_id)
            tiles = Tile.objects.filter(resourceinstance=tile.resourceinstance_id)
            has_geom = False

            for tile in tiles:
                for tile_node, tile_value in tile.data.iteritems():
                    if tile_node == self.geometry_node:
                        geom = GEOSGeometry(json.dumps(tile_value['features'][0]['geometry']), srid=4326)
                        geom.transform(3857)
                        address['geometry']['x'] = geom.x
                        address['geometry']['y'] = geom.y
                        has_geom = True
                    if tile_node in self.field_lookup:
                        address["attributes"][self.field_lookup[tile_node]] = str(tile_value)

            for edit_node, edit_value in tile_edits.iteritems():
                if edit_node == self.geometry_node:
                    geom = GEOSGeometry(json.dumps(edit_value['features'][0]['geometry']), srid=4326)
                    geom.transform(3857)
                    address['geometry']['x'] = geom.x
                    address['geometry']['y'] = geom.y
                    has_geom = True
                if edit_node in self.field_lookup:
                    address["attributes"][self.field_lookup[edit_node]] = str(edit_value)

            if has_geom:
                if len(external_reference) != 0:
                    address["attributes"]["FID"] = int(external_reference[0].data[self.external_reference_node])
                    payload["updates"].append(address)
                else:
                    payload["adds"].append(address)
                data = urllib.urlencode(payload).replace('None', 'null')
                url = self.config['external_address_url'] + '/applyEdits'
                req = urllib2.Request(url, data)
                f = urllib2.urlopen(req)
                response = f.read()
                response = json.loads(response)
                pp(payload)
                pp(response)
                if len(response['addResults']) > 0:
                    if response['addResults'][0]['success'] == True:
                        result_tile = models.TileModel()
                        result_tile.resourceinstance = models.ResourceInstance.objects.get(pk=tile.resourceinstance_id)
                        result_tile.data = {self.external_reference_node: str(response['addResults'][0]['objectId'])}
                        result_tile.nodegroup = result_node.nodegroup
                        result_tile.save()
                f.close()

        return tile
