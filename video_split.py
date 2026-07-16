import cv2
import os

def extract_frames_from_time_range(video_path, output_folder, start_time, end_time, fps=None):
    """
    Extract frames from a video between specified time range
    
    Args:
        video_path (str): Path to input video file
        output_folder (str): Path to output folder for images
        start_time (float): Start time in seconds
        end_time (float): End time in seconds
        fps (int, optional): Frames per second to extract. If None, extracts all frames
    
    Returns:
        list: List of saved frame filenames
    """
    
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # Open the video file
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print("Error: Could not open video file")
        return []
    
    # Get video properties
    video_fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    print(f"Video FPS: {video_fps}")
    print(f"Total frames: {total_frames}")
    
    # Calculate frame numbers for start and end times
    start_frame = int(start_time * video_fps)
    end_frame = int(end_time * video_fps)
    
    # Ensure frame numbers are within bounds
    start_frame = max(0, min(start_frame, total_frames - 1))
    end_frame = max(start_frame, min(end_frame, total_frames - 1))
    
    print(f"Extracting frames from {start_time}s (frame {start_frame}) to {end_time}s (frame {end_frame})")
    
    # Set frame position to start frame
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
    
    saved_frames = []
    frame_count = start_frame
    
    # Calculate extraction interval based on desired fps
    if fps and fps < video_fps:
        extract_interval = int(video_fps / fps)
    else:
        extract_interval = 1
    
    while frame_count <= end_frame:
        ret, frame = cap.read()
        
        if not ret:
            break
        
        # Save frame if it matches our extraction interval
        if (frame_count - start_frame) % extract_interval == 0:
            # Create filename with timestamp
            timestamp = frame_count / video_fps
            filename = f"frame_{frame_count:06d}_time_{timestamp:.2f}s.jpg"
            filepath = os.path.join(output_folder, filename)
            
            # Save the frame
            cv2.imwrite(filepath, frame)
            saved_frames.append(filepath)
            print(f"Saved: {filename}")
        
        frame_count += 1
        
        # Break if we've passed the end frame
        if frame_count > end_frame:
            break
    
    # Release the video capture object
    cap.release()
    
    print(f"\nExtraction complete! Saved {len(saved_frames)} frames to {output_folder}")
    return saved_frames

# Alternative: Extract frames at a specific sampling rate
def extract_frames_with_sampling(video_path, output_folder, start_time, end_time, sampling_rate=1):
    """
    Extract frames with custom sampling rate
    
    Args:
        video_path (str): Path to input video file
        output_folder (str): Path to output folder for images
        start_time (float): Start time in seconds
        end_time (float): End time in seconds
        sampling_rate (float): Number of frames to extract per second
    """
    
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print("Error: Could not open video file")
        return
    
    video_fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    start_frame = int(start_time * video_fps)
    end_frame = int(end_time * video_fps)
    
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
    
    # Calculate frame interval based on sampling rate
    if sampling_rate > 0:
        frame_interval = int(video_fps / sampling_rate)
    else:
        frame_interval = 1
    
    frame_count = start_frame
    saved_count = 0
    
    while frame_count <= end_frame:
        ret, frame = cap.read()
        
        if not ret:
            break
        
        if frame_count % frame_interval == 0:
            timestamp = frame_count / video_fps
            filename = f"frame_{saved_count:04d}_time_{timestamp:.2f}s.jpg"
            filepath = os.path.join(output_folder, filename)
            
            cv2.imwrite(filepath, frame)
            print(f"Saved: {filename}")
            saved_count += 1
        
        frame_count += 1
    
    cap.release()
    print(f"\nExtraction complete! Saved {saved_count} frames to {output_folder}")

# Example usage
if __name__ == "__main__":
    # Configuration
    video_path = r"C:\Video\1.mp4"  # Replace with your video path
    output_folder = r"C:\Video\split1"  # Output folder name
    
    # Time range in seconds
    start_time = 67  # Start at 10.5 seconds
    end_time = 74    # End at 15 seconds
    
    # Method 1: Extract all frames between time range
    extract_frames_from_time_range(video_path, output_folder, start_time, end_time)
    
    # Method 2: Extract with custom FPS (e.g., 2 frames per second)
    # extract_frames_from_time_range(video_path, output_folder, start_time, end_time, fps=2)
    
    # Method 3: Extract with sampling rate (e.g., 1 frame per second)
    # extract_frames_with_sampling(video_path, output_folder, start_time, end_time, sampling_rate=1)