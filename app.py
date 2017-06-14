from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import requests
import json
from datetime import datetime
import xml.etree.ElementTree as ET
import HTMLParser
h = HTMLParser.HTMLParser()
from bs4 import BeautifulSoup

app = Flask(__name__)

# This method makes the callout to National Weather Webservice.
def NOAA_Callout(latitude, longitude) :
    # Endpoint URL to connect to web service. It has the port which is used for connection.
    endpoint_url="https://graphical.weather.gov:443/xml/SOAP_server/ndfdXMLserver.php"
    headers = {'content-type': 'text/xml'}
    today_date = str(datetime.now().strftime('%Y-%m-%d'))
    print today_date
    # SOAP Request.
    bodydaybyday = """
                        <SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/" SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
                        <SOAP-ENV:Body>
                        <ns3591:NDFDgen xmlns:ns3591="uri:DWMLgen">
                        <latitude xsi:type="xsd:string">"""+latitude+"""</latitude>
                        <longitude xsi:type="xsd:string">"""+longitude+"""</longitude>
                        <product xsi:type="xsd:string">time-series</product>
                        <startTime xsi:type="xsd:string">"""+today_date+"""T00:00:00</startTime>
                        <endTime xsi:type="xsd:string">"""+today_date+"""T23:59:59</endTime>
                        <Unit xsi:type="xsd:string">e</Unit>
                        <weatherParameters>
                        <maxt xsi:type="xsd:boolean">1</maxt>
                        <mint xsi:type="xsd:boolean">1</mint>
                        <pop12 xsi:type="xsd:boolean">1</pop12>
                        <sky xsi:type="xsd:boolean">1</sky>
                        <wspd xsi:type="xsd:boolean">1</wspd>
                        <wdir xsi:type="xsd:boolean">1</wdir>
                        <waveh xsi:type="xsd:boolean">1</waveh>
                        <icons xsi:type="xsd:boolean">1</icons>
                        </weatherParameters>
                        </ns3591:NDFDgen>
                        </SOAP-ENV:Body>
                        </SOAP-ENV:Envelope>
                    """

    # Callout performed here.
    response = requests.post(endpoint_url,data=bodydaybyday,headers=headers)

    # Parsing reponse.
    response = h.unescape(response.content)

    # Beautiful soup for fetching data from WSDML response (XML tree).
    soup = BeautifulSoup(response, 'html.parser')
    value_dict = {}
    if soup.find('parameters'):
        temperature_tags = soup.findAll('temperature')
        # print temperature_tags
        for tag in temperature_tags:
            value_dict['temperature_'+tag['type']] = int(tag.value.string)
        if soup.findAll('wind-speed') :
            value_dict['wind_speed'] = [int(value.string) for value in soup.findAll('wind-speed')[0].findAll('value')]
        if soup.findAll('direction') :
            value_dict['direction'] = [int(val.string) for val in soup.findAll('direction')[0].findAll('value')]
        if soup.findAll('cloud-amount') :
            value_dict['cloud-amount'] = [int(val.string) for val in soup.findAll('cloud-amount')[0].findAll('value')]
        if soup.findAll('probability-of-precipitation') :
            value_dict['probability-of-precipitation'] = [int(val.string) for val in soup.findAll('probability-of-precipitation')[0].findAll('value')]
        if soup.findAll('conditions-icon') :
            value_dict['conditions-icon'] = [val.string for val in soup.findAll('conditions-icon')[0].findAll('icon-link')]
    return value_dict

# Gets data from html page. Currently, latitude and longitude are defaulted to Arlington.
# You can pass desired coordinates to check for weather update.
@app.route('/call', methods=['GET','POST'])
def callout() :
    if request.method == 'POST':
        data = request.get_json('data')
        latitude = data.split('&')[0].split('=')[1]
        longitude = data.split('&')[1].split('=')[1]
        data_dict = NOAA_Callout(latitude, longitude)
    return json.dumps({'success': data_dict}, 200, {'contentType': 'application/json'})

@app.route('/', methods=['GET'])
def show_index():
    if request.method == 'GET' :
        return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
