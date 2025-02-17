import multiprocessing
import subprocess
import os
import sys

def run_rtsp_stream(args):
    """Run the Recognition-api.py script for a given RTSP URL."""
    rtsp_url_key, rtsp_url_val = args  # Unpack the key-value pair
    # Set the command for subprocess
    command = [
        sys.executable,  # Use the same Python interpreter
        'Recognition-api.py',
        '--rtsp-url', rtsp_url_val,
        '--data-dir', rtsp_url_key,
    ]
    
    try:
        subprocess.run(command, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error while running RTSP stream {rtsp_url_key} ({rtsp_url_val}): {e}")
    except Exception as e:
        print(f"Unexpected error for {rtsp_url_key} ({rtsp_url_val}): {e}")

def start_multiple_streams(rtsp_urls):
    """Start multiple RTSP streams using multiprocessing."""
    # Create a pool of processes, one for each RTSP URL
    args = list(rtsp_urls.items())
    with multiprocessing.Pool(processes=len(rtsp_urls)) as pool:
        pool.map(run_rtsp_stream, args)

if __name__ == '__main__':
    # Define a list of RTSP URLs
    rtsp_urls = {
        'holl': 'rtsp://autobits:Autobits@123@192.168.1.204:554',
        # 'office': 'rtsp://autobits:Autobits@123@192.168.1.203:554',
    }

    # Start the RTSP streams
    start_multiple_streams(rtsp_urls)
