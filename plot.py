#!/usr/bin/python3

import argparse
import subprocess
import os
import ggps

from xml.dom import minidom
import matplotlib
import matplotlib.cm as cm
import folium
from folium import plugins
from folium.plugins import HeatMap
import xml.etree.ElementTree as et

def is_float_try(str):
    try:
        float(str)
        return True
    except ValueError:
        return False

def read_gpx_files(gpxdir):
    counter = 0
    for gpxfile in os.listdir(gpxdir):
        filepath = os.path.join(gpxdir,gpxfile)
        print("Processig file: ", gpxfile)
        
        if gpxfile.endswith(".gpx"):
            handler = ggps.GpxHandler()
        elif gpxfile.endswith(".tcxf"):
            handler = ggps.TcxHandler()
        else:
            continue
        try:
            handler.parse(filepath)
        except:
            continue
        trackpoints = handler.trackpoints
        print("Adding", len(trackpoints), "points")

        yield trackpoints
        counter+= 1
        if counter > 50:
            continue


def plot_osm_map(tracks, output):
    m = folium.Map(zoom_start=15)
    folium.TileLayer('openstreetmap').add_to(m)
    folium.TileLayer('stamentoner').add_to(m)
    folium.TileLayer('stamenterrain').add_to(m)
    allpoints = []
    bounds = []

    for track in tracks:
        thistrack = []

        print("Current number of points: ", len(allpoints))
        for point in track:
            if is_float_try(point.get("latitudedegrees")) and is_float_try(point.get("longitudedegrees")):
                thistrack.append((float(point.get("latitudedegrees")), float(point.get("longitudedegrees"))))
                allpoints.append((point.get("latitudedegrees"), point.get("longitudedegrees"), 0.05))
        folium.PolyLine(thistrack, color="red", weight=2, opacity = 0.1, smoothFactor=4.0).add_to(m)

        lats = [float(point.get('latitudedegrees')) for point in track]
        longs = [float(point.get('longitudedegrees')) for point in track]
        swne = [min(lats), min(longs), max(lats), max(longs)]
        bounds.append(swne)

    print("Total number of points: ", len(allpoints))
    
    HeatMap(allpoints, gradient={0.05: 'blue', 0.4: 'lime', 0.7: 'yellow', 1: 'red'}, radius=8, blur=10).add_to(folium.FeatureGroup(name='Heat Map').add_to(m))
    folium.LayerControl().add_to(m)

    s = min(bounds, key=lambda x: x[0])[0]
    w = min(bounds, key=lambda x: x[1])[1]
    n = max(bounds, key=lambda x: x[2])[2]
    e = max(bounds, key=lambda x: x[3])[3]
    m.fit_bounds([[s, w], [ n, e]])

    m.save(output)

def main():
    parser = argparse.ArgumentParser(description="Plot GPX data onto a map")
    parser.add_argument(
        "-d", "--dir", help="Input directory", required=True, type=str,
    )
    parser.add_argument(
        "-o", "--output", help="Output map name. Defaults to heatmap-map.html", default='heatmap-map.html', type=str,
    )

    args = parser.parse_args()
    data_directory=args.dir

    tracks = read_gpx_files(data_directory)
    plot_osm_map(tracks, args.output)


if __name__ == "__main__":
    main()
