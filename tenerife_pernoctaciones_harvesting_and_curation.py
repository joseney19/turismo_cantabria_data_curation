import io
import xml.etree.ElementTree as ET
import requests
import json
import zipfile
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import itertools as it
#harvesting dlcturismouc
oai = requests.get('https://zenodo.org/oai2d?verb=ListRecords&set=user-dlcturismouc&metadataPrefix=oai_dc')
oaiTree = ET.fromstring(oai.text)
ctrl = 0
for i in oaiTree.iter():
    if ('{http://purl.org/dc/elements/1.1/}title' == i.tag and 'Turismo_Tenerife' == i.text) or ctrl:
        ctrl = 1
    if '{http://www.openarchives.org/OAI/2.0/}identifier' == i.tag and ctrl:
        identifier = i.text
        ctrl = 0
#getting specific identifier of interest		
oai = requests.get(f'https://zenodo.org/oai2d?verb=GetRecord&metadataPrefix=datacite3&identifier={identifier}')
oaiTree = ET.fromstring(oai.text)
ctrl = 0
for i in oaiTree.iter():
    if (ctrl == 0) and i.tag == '{http://datacite.org/schema/kernel-3}relatedIdentifier':
        ctrl=1
        doi = i.text
#solving the DOI of interest
url = 'https://doi.org/'+doi #DOI solver URL
headers = {'Accept': 'application/vnd.citationstyles.csl+json;q=1.0'} #Type of response accpeted
r = requests.get(url, headers=headers) #POST with headers

data = json.loads(r.text)
for elem in data:
    if elem == 'URL':
        url = data[elem]
headers = {'accept': 'application/json'}
r2 = requests.get('https://zenodo.org/api/records/'+[str(s) for s in url.split('/') if s.isdigit()][0],headers)
data = json.loads(r2.text)
for elem in data:
    if elem == 'files':
        dataset_link = data[elem][0]['links']['self']
#loading tenerife_pernoc with the file .xls from the link
tenerife_pernoc = pd.read_excel(io.BytesIO(requests.get(dataset_link).content))
#filtering data subset
tenerife_pernoc = tenerife_pernoc[(tenerife_pernoc.año > 2005) & (tenerife_pernoc.año < 2019) & (tenerife_pernoc.mes < 13)]
#convert subset of data to csv
tenerife_pernoc_csv = tenerife_pernoc.to_csv(sep=',', encoding='utf-8')
#getting into Zenodo with access token more info in https://developers.zenodo.org/#rest-api
parametros = {'access_token': 'f30coEUmUl2ViwIcfy4cUTbHZ0W5RIn87YxyNzFShnjOLpaN7cdSZ7Eb2aPq'}
r = requests.get('https://zenodo.org/api/deposit/depositions',
                 params= parametros)
#creating an empty upload
headers = {"Content-Type": "application/json"}
r = requests.post('https://zenodo.org/api/deposit/depositions',
                   params=parametros, json={},
                   headers=headers)
#upload a new file
deposition_id = r.json()['id'] # Get the deposition id from the previous response
data = {'filename': 'Curated Pernoctaciones Tenerife'}
files = {'file': tenerife_pernoc_csv}
r = requests.post('https://zenodo.org/api/deposit/depositions/%s/files' % deposition_id,
                   params=parametros, data=data,
                   files=files)
#add meta data
data = {
     'metadata': {
         'title': 'Curated Pernoctaciones Tenerife',
         'upload_type': 'dataset',
         'description': 'Curated Pernoctaciones Tenerife',
         'creators': [{'name': 'UC, Students',
                       'affiliation': 'dlcturismouc'}]
     }
}
r = requests.put('https://zenodo.org/api/deposit/depositions/%s' % deposition_id,
                  params=parametros, data=json.dumps(data),
                  headers=headers)
#publish
r = requests.post('https://zenodo.org/api/deposit/depositions/%s/actions/publish' % deposition_id,
                      params=parametros )