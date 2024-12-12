import subprocess
import time
import re

def run_stream():
    # Start the RTSP stream processing (e.g., FFmpeg)
    return subprocess.Popen(
        [   'nice', '-n', '10',
            'ffmpeg', 
            # '-hwaccel', 'cuda', 
            '-i', "rtsp://autobits:Autobits@123@192.168.1.203:554",
            '-vf', 'scale=960:540',
            '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-an', '-sn', '-'],
        stderr=subprocess.PIPE,  # Capture errors for monitoring
        universal_newlines=True
    )

def monitor_stream(process):
    for line in process.stderr:
        print(line.strip())  # Optional: log the output for debugging
        
        # Check for duplicate frames
        if "dup=" in line:
            print("Duplicate frames detected. Restarting stream...")
            return True  # Signal to restart
        
        # Check for missed packets or stalling
        if "missed packets" in line or "max delay reached" in line:
            print("Stream stuck or packets missed. Restarting stream...")
            return True  # Signal to restart

    return False  # No issues detected

def main():
    max_restarts = 5  # Set a limit on how many times to restart
    restart_count = 0
    
    while restart_count < max_restarts:
        process = run_stream()
        
        try:
            # Monitor the process
            should_restart = monitor_stream(process)
            
            if should_restart:
                restart_count += 1
                process.terminate()
                time.sleep(5)  # Add a delay before restarting
            else:
                # If process ends without issues, break the loop
                break
        
        except KeyboardInterrupt:
            print("Exiting...")
            process.terminate()
            break
        
        except Exception as e:
            print(f"Error: {e}")
            process.terminate()
            break

if __name__ == "__main__":
    main()
