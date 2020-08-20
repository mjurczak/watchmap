#!/usr/bin/python3

import argparse
import subprocess
import os
import ggps
import matplotlib
import matplotlib.cm as cm
import folium

from geopy.distance import geodesic
from folium import plugins
from folium.plugins import HeatMap

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

def reduce_track(track_data):
    new_track = []
    new_track.append(track_data[0])

    for destination in track_data[1::]:
        distance = geodesic(new_track[-1], destination).meters
        if (distance > 15):
            new_track.append(destination)

    return new_track


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
        reduced_track = reduce_track(thistrack)
        folium.PolyLine(reduced_track, color="red", weight=2, opacity = 0.051, smoothFactor=4.0).add_to(m)

        for point in reduced_track:
            allpoints.append((point[0], point[1], 0.05))
        print("Original track points: ", len(thistrack), " Reduced to: ", len(reduced_track))

        lats = [point[0] for point in reduced_track]
        longs = [point[1] for point in reduced_track]
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
