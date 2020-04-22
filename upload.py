# -*- coding: utf-8 -*-
"""
Created on Tue Apr 21 12:49:33 2020

@author: lalit
"""

from flask import *
import pandas as pd
from opencage.geocoder import OpenCageGeocode
from opencage.geocoder import InvalidInputError, RateLimitExceededError, UnknownError
import folium
from folium.features import DivIcon
from folium import plugins
import json
app = Flask(__name__)  
 
@app.route('/')  
def upload():
    return render_template("file_upload_form.html")  
 
@app.route('/success', methods = ['POST'])  
def success():
    if request.method == 'POST':
        f = request.files['file']
        df_addresses = pd.read_csv(f)
        
        df_addresses.Zipcode = df_addresses.Zipcode.apply(str)
        df_addresses['full_address'] = df_addresses['Address']+','+df_addresses['City']+','+df_addresses['State']+','+df_addresses['Zipcode']+','+'USA'
        df_addresses['sequence']=df_addresses.groupby('Group').cumcount()+1
        def set_value(row_number, assigned_value): 
            return assigned_value[row_number] 
# Create the dictionary 
        event_dictionary ={'Anita Carson':'pink','Tim Edwards': 'yellow','Johnathan Shaw' : 'blue', 'Josh Jennings' : 'violet', 'Andrew Burt' : 'green' ,'Tony Bonetti' : 'cadetblue' } 
  

        df_addresses['Color'] = df_addresses['Group'].apply(set_value, args =(event_dictionary, ))
        key = '0ba6084e61384f88816ab2eaa53b1983'
        gmaps_key = OpenCageGeocode(key)
        df_addresses['Latitude'] = None
        df_addresses['Longitude'] = None
        list_lat = []   # create empty lists
        list_long = []
        for index, row in df_addresses.iterrows():
            geocode_result = gmaps_key.geocode(df_addresses['full_address'][index])
            lat = geocode_result[0]['geometry']['lat']
            long = geocode_result[0]['geometry']['lng']

            list_lat.append(lat)
            list_long.append(long)


# create new columns from lists    

        df_addresses['Latitude'] = list_lat   

        df_addresses['Longitude'] = list_long
  
        lat_mean = df_addresses['Latitude'].mean()
        long_mean = df_addresses['Longitude'].mean()

        df_group = df_addresses['Group'].unique()
        MEMP_COORDINATES = (lat_mean, long_mean)


        mapa = folium.Map(location=MEMP_COORDINATES, zoom_start=10)



        for grp_name, df_group in df_addresses.groupby('Group'):
            feature_group = folium.FeatureGroup(grp_name)
            for row in df_group.itertuples():
                folium.Marker(location=[row.Latitude, row.Longitude],
                      popup = ('Address: ' + str(row.full_address) + '<br>'
                    'Tech: ' + str(row.Group)), 
                     icon = plugins.BeautifyIcon(
                                    number= str(row.sequence),
                                    border_width=2,
                                    iconShape= 'marker',
                                    inner_icon_style= 'margin-top:2px',
                                     background_color  = row.Color,
                     )).add_to(feature_group)
            feature_group.add_to(mapa)

        folium.LayerControl().add_to(mapa)
        print(df_addresses)
        #f.save(f.filename)
        #return render_template("success.html", name = f.filename)
        return mapa._repr_html_()
  
if __name__ == '__main__':
    app.run(debug = True)