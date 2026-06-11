from datetime import datetime, timezone
import argparse
import re
import urllib.parse


parser = argparse.ArgumentParser(description="Convert timestamp to human-readable format")
parser.add_argument("timestamp", help="Timestamp in YYYYMMDDHHMMSS.fff or MM/DD/YYYY HH:MM:SS format")
parser.add_argument("--current-time", action="store_true", help="print current time in ISO 8601")

def convert_from_iso(timestamp):
    timestamp = re.search(r'(\d+\.\d+)$', timestamp).group(1)
    # Format: YYYYMMDDHHMMSS.fff
    dt_obj = datetime.strptime(timestamp, "%Y%m%d%H%M%S.%f")

    human_readable = dt_obj.strftime("%B %d, %Y, %I:%M:%S.%f")[:-3] + " " + dt_obj.strftime("%p")
    time_part = timestamp[8:14]
    hours = time_part[0:2]
    minutes = time_part[2:4]
    seconds = time_part[4:6]
    military_time = f"{hours}{minutes} hours"
    military_time_with_seconds = f"{hours}:{minutes}:{seconds}"
    dt_utc = dt_obj.replace(tzinfo=timezone.utc)
    iso8601 = dt_utc.strftime("%Y-%m-%dT%H:%M:%S.") + f"{dt_utc.microsecond // 1000:03d}+00:00"
    iso8601_encoded = urllib.parse.quote(iso8601, safe="")

    print(f"Original: {timestamp_str}")
    print(f"Human Readable: {human_readable}")
    print(f"Military Time: {military_time}")
    print(f"Military Time with Seconds: {military_time_with_seconds}")
    print(f"ISO 8601: {iso8601}")
    print(f"ISO 8601 URL Encoded: {iso8601_encoded}")

def check_format(timestamp_str):
    if re.match(r"^\d{2}/\d{2}/\d{4} \d{1,2}:\d{2}:\d{2}$", timestamp_str):
        print("Detected Standard Slash format (MM/DD/YYYY HH:MM:SS)")
        return "slash"
    
    if re.search(r"(\d{14})\.(\d{3})", timestamp_str):
        print("Detected ISO 8601 Format")
        return "iso"
    
    else:
        print("No Valid time format detected.")
        return "Invalid"


def convert_to_iso_8601(source_str):
    '''
    take a time string: "MM/DD/YYYY HH:MM:SS"
    '''
    dt_obj = datetime.strptime(source_str, "%m/%d/%Y %H:%M:%S")
    raw_target = dt_obj.strftime("%Y%m%d%H%M%S.%f")
    final = raw_target[:-3]
    print(f"ISO 8601 timestamp: {final}")


def current_time():
    now = datetime.now()
    basic_iso = now.strftime("%Y%m%d%H%M%S.%f")[:-3]
    return basic_iso

if __name__ == '__main__':
    args = parser.parse_args()
    timestamp_str = args.timestamp
    format = check_format(timestamp_str=timestamp_str)
    if format == "iso":
        convert_from_iso(timestamp_str)
    elif format == "slash":
        convert_to_iso_8601(timestamp_str)
    if args.current_time:
        print(f"Current time: {current_time()}")
