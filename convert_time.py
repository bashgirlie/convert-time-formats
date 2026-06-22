from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
import argparse
import re
import urllib.parse
import sys


parser = argparse.ArgumentParser(description="Convert timestamp to human-readable format")
parser.add_argument("timestamp", nargs='?', help="Timestamp in YYYYMMDDHHMMSS.fff format")
parser.add_argument("--current-time", action="store_true", help="print current time in ISO 8601")
parser.add_argument("-tz", "--timezone", default="UTC", help="Target timezone (e.g., America/New_York)")

def check_format(timestamp_str):
    if re.match(r"^\d{2}/\d{2}/\d{4} \d{1,2}:\d{2}:\d{2}$", timestamp_str):
        print("Detected Standard Slash format (MM/DD/YYYY HH:MM:SS)")
        return "slash"
    
    if re.search(r"(\d{14})\.(\d{3})", timestamp_str):
        print("Detected ISO 8601 Format")
        return "iso"
    
    if isinstance(timestamp_str, str):
        # 2. Handle string-encoded Epoch numbers (e.g., "1719054000")
        if timestamp_str.isdigit() or (timestamp_str.replace('.', '', 1).isdigit() and timestamp_str.count('.') <= 1):
            return "epoch"
    else:
        print("No Valid time format detected.")
        return "Invalid"
    
'''def convert_timezone(dt_obj, target_tz_str="UTC"):
    if dt_obj.tzinfo is None:
        dt_obj = dt_obj.replace(tzinfo=timezone.utc)
    return dt_obj.astimezone(ZoneInfo(target_tz_str))'''

def convert_timezone(dt_obj, target_tz_str="UTC"):
    # Force baseline to UTC if naive
    if dt_obj.tzinfo is None:
        dt_obj = dt_obj.replace(tzinfo=timezone.utc)
        
    try:
        # 1. Try standard lookup first
        return dt_obj.astimezone(ZoneInfo(target_tz_str))
    except Exception:
        # 2. Hardcoded fallback for common US timezones if system files are completely missing
        tz_upper = target_tz_str.upper()
        fallback_zones = {
            "UTC": 0, "GMT": 0,
            "US/EASTERN": -4, "AMERICA/NEW_YORK": -4,      # June = Daylight Saving (EDT)
            "US/CENTRAL": -5, "AMERICA/CHICAGO": -5,       # CDT
            "US/MOUNTAIN": -6, "AMERICA/DENVER": -6,       # MDT
            "US/PACIFIC": -7, "AMERICA/LOS_ANGELES": -7     # PDT
        }
        
        if tz_upper in fallback_zones:
            hours_offset = fallback_zones[tz_upper]
            manual_tz = timezone(timedelta(hours=hours_offset))
            return dt_obj.astimezone(manual_tz)
        else:
            print(f"Warning: Timezone '{target_tz_str}' not found in system or fallback map. Defaulting to UTC.")
            return dt_obj.astimezone(timezone.utc)


def convert_from_iso(timestamp, target_tz):
    # Extract the full 14 digits + dot + 3 digits from the URL or raw string
    match = re.search(r"(\d{14})\.(\d{3})", timestamp_str)
    isolated_timestamp = match.group(0) if match else timestamp_str
    # Format: YYYYMMDDHHMMSS.fff
    dt_obj = datetime.strptime(timestamp, "%Y%m%d%H%M%S.%f")

    #apply timezone conversion
    dt_obj = convert_timezone(dt_obj, target_tz)

    human_readable = dt_obj.strftime("%B %d, %Y, %I:%M:%S.%f")[:-3] + " " + dt_obj.strftime("%p")
    
    # Re-extract time components from the localized object for military prints
    hours = dt_obj.strftime("%H")
    minutes = dt_obj.strftime("%M")
    seconds = dt_obj.strftime("%S")
    
    military_time = f"{hours}{minutes} hours"
    military_time_with_seconds = f"{hours}:{minutes}:{seconds}"
    
    # Standard ISO 8601 presentation with timezone offset
    iso8601 = dt_obj.strftime("%Y-%m-%dT%H:%M:%S.") + f"{dt_obj.microsecond // 1000:03d}" + dt_obj.strftime("%z")
    iso8601_encoded = urllib.parse.quote(iso8601, safe="")

    print(f"Original: {timestamp_str}")
    print(f"Human Readable: {human_readable}")
    print(f"Military Time: {military_time}")
    print(f"Military Time with Seconds: {military_time_with_seconds}")
    print(f"ISO 8601: {iso8601}")
    print(f"ISO 8601 URL Encoded: {iso8601_encoded}")

def convert_to_iso_8601(source_str, target_tz):
    '''
    take a time string: "MM/DD/YYYY HH:MM:SS"
    '''
    dt_obj = datetime.strptime(source_str, "%m/%d/%Y %H:%M:%S")
    #apply timezone conversion
    dt_obj = convert_timezone(dt_obj, target_tz)
    raw_target = dt_obj.strftime("%Y%m%d%H%M%S.%f")
    final = raw_target[:-3]
    print(f"ISO 8601 timestamp: {final}")

def convert_from_epoch(epoch_val, target_tz):
    '''
    Detect 13-digit epoch time
    '''
    dt_obj = datetime.fromtimestamp(float(epoch_val), tz=timezone.utc)
    dt_obj = convert_timezone(dt_obj, target_tz)


    
    human_readable = dt_obj.strftime("%m/%d/%Y %I:%M:%S %p")
    military_time = dt_obj.strftime("%H%M")
    military_time_seconds = dt_obj.strftime("%H%M%S")
    iso8601 = dt_obj.strftime("%Y%m%d%H%M%S.%f")[:-3]
    iso8601_encoded = urllib.parse.quote(iso8601, safe="")
    print(f"Human Readable: {human_readable}")
    print(f"Military Time: {military_time}")
    print(f"Military Time Seconds: {military_time_seconds}")
    print(f"ISO 8601: {iso8601}")
    print(f"ISO 8601 URL Encoded: {iso8601_encoded}")



def current_time():
    now = datetime.now()
    basic_iso = now.strftime("%Y%m%d%H%M%S.%f")[:-3]
    return basic_iso

if __name__ == '__main__':
    args = parser.parse_args()
    
    if args.timestamp:
        timestamp_str = args.timestamp
        format = check_format(timestamp_str=timestamp_str)
        if format == "iso":
            convert_from_iso(timestamp_str, args.timezone)
        elif format == "slash":
            convert_to_iso_8601(timestamp_str, args.timezone)
        elif format == "epoch":
            convert_from_epoch(timestamp_str, args.timezone)
    
    if args.current_time:
        print(f"Current time: {current_time()}")

    if not args.timestamp and not args.current_time:
        parser.print_help()
        sys.exit(1)
    
