import os
import csv
import gzip
import gpxpy
from fitparse import FitFile

def extract_lat_long_and_time_from_gpx(file_path):
    with open(file_path, 'r') as gpx_file:
        gpx = gpxpy.parse(gpx_file)
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    # point.time is a datetime.datetime object or None
                    return point.latitude, point.longitude, point.time
    return None, None, None


def extract_lat_long_and_time_from_fit(file_path):
    with gzip.open(file_path, 'rb') as gz_file:
        fitfile = FitFile(gz_file)
        for record in fitfile.get_messages('record'):
            lat = None
            lon = None
            timestamp = None
            for data in record:
                if data.name == 'position_lat' and data.value is not None:
                    lat = data.value * (180 / 2**31)
                if data.name == 'position_long' and data.value is not None:
                    lon = data.value * (180 / 2**31)
                if data.name == 'timestamp' and data.value is not None:
                    timestamp = data.value  # usually a datetime.datetime object
            if lat is not None and lon is not None:
                return lat, lon, timestamp
    return None, None, None


def process_folder(folder_path, output_csv):
    with open(output_csv, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['file_id', 'latitude', 'longitude', 'timestamp'])
        
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            
            if filename.endswith('.gpx'):
                lat, lon, timestamp = extract_lat_long_and_time_from_gpx(file_path)
                file_id = os.path.splitext(filename)[0]
            
            elif filename.endswith('.fit.gz'):
                lat, lon, timestamp = extract_lat_long_and_time_from_fit(file_path)
                file_id = filename[:-7]
            
            else:
                continue  # skip other files
            
            if lat is not None and lon is not None:
                # Convert timestamp to ISO format string if not None
                ts_str = timestamp.isoformat() if timestamp else ''
                writer.writerow([file_id, lat, lon, ts_str])
            else:
                print(f"Warning: Could not extract lat/lon from {filename}")

folder_path = '/Users/Nicole/Desktop/export_51827613/activities/'
output_csv = '/Users/Nicole/Desktop/export_51827613/output_coordinates.csv'

process_folder(folder_path, output_csv)

