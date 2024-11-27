import subprocess
import cv2
import numpy as np

def stream_with_cuda(rtsp_url):
    """
    Streams RTSP video using FFmpeg with CUDA hardware acceleration and pipes the frames for processing.

    Args:
        rtsp_url (str): The RTSP stream URL.
    """
    command = [
        "ffmpeg",
        "-hwaccel", "cuda",                    # Enable CUDA hardware acceleration
        # "-hwaccel_output_format", "cuda",     # Use CUDA for the output format
        "-i", rtsp_url,                       # Input RTSP stream
        "-f", "rawvideo",                     # Output raw video to stdout
        "-pix_fmt", "bgr24",                  # Convert to OpenCV-compatible format
        "-sn",                                # Disable subtitles
        "-tune", "zerolatency",               # Optimize for low latency
        "-"                                   # Pipe to stdout
    ]

    # Assuming a 1920x1080 stream resolution
    frame_width = 1920
    frame_height = 1080
    frame_size = frame_width * frame_height * 3  # bgr24: 3 bytes per pixel

    try:
        print("Starting FFmpeg process running cuda...")
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=10**8)

        while True:
            # Read raw video frame from stdout
            raw_frame = process.stdout.read(frame_size)

            if len(raw_frame) != frame_size:
                print("Incomplete frame received. Exiting...")
                break

            # Convert raw bytes to a NumPy array
            frame = np.frombuffer(raw_frame, np.uint8).reshape((frame_height, frame_width, 3))

            # Display the frame using OpenCV
            cv2.imshow("RTSP Stream (CUDA Accelerated)", frame)

            # Exit on pressing 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except Exception as e:
        print(f"Error: {e}")
    finally:
        process.terminate()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    rtsp_stream_url = "rtsp://marketingoffice:CameraOffice@999@10.20.11.2:554/unicast/c4/s0/live"
    stream_with_cuda(rtsp_stream_url)
