import os
from flask import Flask
from flask_restful import Resource, Api, reqparse
from geopy.geocoders import MapBox
from sqlalchemy import create_engine

# Parameters of Postgres
if 'RDS_HOSTNAME' in os.environ:
    POSTGRES = {
        'user': os.environ['RDS_USERNAME'],
        'pw': os.environ['RDS_PASSWORD'],
        'db': os.environ['RDS_DB_NAME'],
        'host': os.environ['RDS_HOSTNAME'],
        'port': os.environ['RDS_PORT'],
    }
else:
    POSTGRES = {
        'user': 'postgres',
        'pw': '123456',
        'db': 'postgis_25_sample',
        'host': 'localhost',
        'port': '5432',
    }

URI = "postgresql://{user}:{pw}@{host}:{port}/{db}". \
    format(user=POSTGRES['user'],
           pw=POSTGRES['pw'],
           db=POSTGRES['db'],
           host=POSTGRES['host'],
           port=POSTGRES['port'])

# initialize Flask App and Database Engine
app = Flask(__name__)
api = Api(app)
engine = create_engine(URI)

# Request Parsing
parser = reqparse.RequestParser()
parser.add_argument('hour', type=int, location='args')
parser.add_argument('origin', location='args')
parser.add_argument('destination', location='args')


class Routes(Resource):
    def get(self):
        args = parser.parse_args()

        # get parameters from requests
        hour, orig, dest = args['hour'], args['origin'], args['destination']

        # geocode origin and destination
        api_key = "pk.eyJ1Ijoib3Blbi1hZGRyZXNzZXMiLCJhIjoiSGx0a1B1NCJ9.2O1QelK6jnFXfDznC2pNSw"
        geocoder = MapBox(api_key=api_key, timeout=None)
        origin_lat, origin_lon = self._geocode(geocoder, orig)
        dest_lat, dest_lon = self._geocode(geocoder, dest)

        geojson = self._get_shortest_path_json(hour, origin_lon, origin_lat, dest_lon, dest_lat)

        return geojson, 200, {'Access-Control-Allow-Origin': '*'}

    @staticmethod
    def _geocode(geocoder, address):
        location = geocoder.geocode(address)
        return location.latitude, location.longitude

    def _get_shortest_path_json(self, hour, orig_lon, orig_lat, dest_lon, dest_lat):
        with engine.connect() as con:
            con.execute(self._delete_table_query())
            con.execute(self._create_table_query() % hour)
            rs = con.execute(self._shortest_path_query() % (orig_lon, orig_lat, dest_lon, dest_lat))
            data = rs.fetchall()

        geojson = {"type": "FeatureCollection"}

        features = []
        for i in range(len(data)):
            features.append(data[i][0])

        geojson['features'] = features

        return geojson

    @staticmethod
    def _delete_table_query():
        return "DROP TABLE IF EXISTS crash_count"

    @staticmethod
    def _create_table_query():
        return """
        CREATE TABLE crash_count
        AS (
        WITH cnt AS (
        SELECT network.id,
        network.start as source,
        network.end as target,
        network.geometry,
        count(network.id) as cost
        FROM route_api_drivenetwork AS network
        JOIN route_api_crashes AS crashes
        ON ST_DWithin(network.geometry, crashes.geometry, 0.003)
        WHERE crashes.hour = %s
        GROUP BY network.id
        ) -- crash count of each edge in a particular hour
        SELECT drive.id,
        drive.start::bigint source,
        drive.end::bigint target,
        drive.geometry,
        coalesce(cnt.cost, 0) as cost
        FROM route_api_drivenetwork drive
        LEFT JOIN cnt
        ON drive.id = cnt.id
        ); -- join the drive network table, and fill null with 0
        """

    @staticmethod
    def _shortest_path_query():
        return """
        WITH origin AS (
        SELECT nodes.id,
        nodes.osmid,
        nodes.geometry,
        ST_Distance(nodes.geometry, ST_GeomFromText('POINT(%s %s)', 4326)) AS dist
        FROM route_api_drivenodes nodes
        ORDER BY dist
        LIMIT 1
        ), -- the closest point to the origin
        dest AS (
        SELECT nodes.id,
        nodes.osmid,
        nodes.geometry,
        ST_Distance(nodes.geometry, ST_GeomFromText('POINT(%s %s)', 4326)) AS dist
        FROM route_api_drivenodes nodes
        ORDER BY dist
        LIMIT 1
        ) -- the closest point to the destination
        SELECT json_build_object(
        'type',       'LineString',
        'id',         id,
        'geometry',   ST_AsGeoJSON(geom)::json
        )
        FROM (
        SELECT crash_count.id,
        crash_count.geometry geom
        FROM pgr_dijkstra(
        'SELECT id, source, target, cost FROM crash_count',
        (SELECT osmid::bigint from origin),
        (SELECT osmid::bigint from dest)
        ) AS path -- calculate shortest path
        JOIN crash_count
        ON path.edge = crash_count.id) AS output_table
        """


api.add_resource(Routes, '/api')

if __name__ == "__main__":
    app.run()
