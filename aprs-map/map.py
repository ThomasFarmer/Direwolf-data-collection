
from flask import Flask, render_template
import time
import awsgi
import boto3
import ast
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = "lkkajdghdadkglajkgah"

def proc_geo_type():
    cs_table = os.environ['CALLSIGNTABLE']
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(cs_table)

    response = table.scan()
    data = response['Items']
    processed_geojson = []
    for datarow in data:
        try:
            geojson = ast.literal_eval(datarow["geojson"])
            if geojson["geometry"].get("coordinates") != None:
                processed_geojson.append(geojson)
        except Exception as genex:
            print(genex)
    return processed_geojson

@app.route("/", methods=['GET'])
def show_map():
    return render_template('map.html')

@app.route("/refresh_data", methods=['GET'])
def refresh_data():
    geojson_data = proc_geo_type()
    return geojson_data

def flask_handler(event, context):
    # remapping event data, to fix bug
    event['httpMethod'] = event['requestContext']['http']['method']
    event['path'] = event['requestContext']['http']['path']
    event['queryStringParameters'] = event.get('queryStringParameters', {})
    # serving up response with awsgi
    return awsgi.response(app, event, context, base64_content_types={"image/png"})