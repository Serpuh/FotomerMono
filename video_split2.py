import cv2
import os
import shutil

def clean_folder(folder_path):
    """
    Очищает папку от всех файлов, сохраняя структуру подпапок
    
    Args:
        folder_path (str): Путь к папке для очистки
    
    Returns:
        tuple: (количество удаленных файлов, список ошибок)
    """
    errors = []
    deleted_count = 0
    
    # Проверяем существование папки
    if not os.path.exists(folder_path):
        return 0, [f"Папка '{folder_path}' не существует"]
    
    if not os.path.isdir(folder_path):
        return 0, [f"Путь '{folder_path}' не является папкой"]
    
    try:
        # Проходим по всем элементам в папке
        for item in os.listdir(folder_path):
            item_path = os.path.join(folder_path, item)
            
            try:
                if os.path.isfile(item_path) or os.path.islink(item_path):
                    # Удаляем файлы и символические ссылки
                    os.unlink(item_path)
                    deleted_count += 1
                elif os.path.isdir(item_path):
                    # Рекурсивно очищаем вложенные папки
                    sub_deleted, sub_errors = clean_folder(item_path)
                    deleted_count += sub_deleted
                    errors.extend(sub_errors)
                    
            except Exception as e:
                errors.append(f"Ошибка при удалении '{item}': {str(e)}")
                
    except Exception as e:
        errors.append(f"Ошибка доступа к папке: {str(e)}")
    
    return deleted_count, errors

def extract_frames_between_seconds(video_path, output_dir, start_sec, end_sec):
    """
    Extract all frames from a video between specified seconds.
    
    Args:
        video_path: Path to the input MP4 video
        output_dir: Directory to save extracted frames
        start_sec: Start time in seconds
        end_sec: End time in seconds
    """
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Open the video file
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print("Error: Could not open video file")
        return
    
    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    fps=20
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    video_duration = total_frames / fps
    
    print(f"Video FPS: {fps}")
    print(f"Total frames: {total_frames}")
    print(f"Video duration: {video_duration:.2f} seconds")
    
    # Calculate frame numbers
    start_frame = int(start_sec * fps)
    end_frame = int(end_sec * fps)
    
    # Ensure frame numbers are within valid range
    start_frame = max(0, min(start_frame, total_frames - 1))
    end_frame = max(start_frame, min(end_frame, total_frames - 1))
    
    print(f"Extracting frames from {start_sec}s to {end_sec}s")
    print(f"Frame range: {start_frame} to {end_frame}")
    
    # Set the video position to start frame
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
    
    frame_count = 0
    extracted_count = 0

    tick: bool = True

    while True:
        ret, frame = cap.read()
        
        if not ret:
            break
        
        current_frame = start_frame + frame_count
        
        # Stop if we've reached the end frame
        if current_frame > end_frame:
            break
        
        
        # Save the frame
        output_path = os.path.join(output_dir, f"frame_{current_frame:06d}.jpg")
        cv2.imwrite(output_path, frame)

        """
        if tick: 
            cv2.imwrite(output_path, frame)
            tick = False
        else:
            tick = True
        """
        frame_count += 1
        extracted_count += 1
        
        # Optional: Print progress every 30 frames
        if frame_count % 30 == 0:
            print(f"Extracted {frame_count} frames...")
    
    # Release the video capture object
    cap.release()
    
    print(f"\nExtraction complete!")
    print(f"Total frames extracted: {extracted_count}")
    print(f"Frames saved to: {output_dir}")

# Example usage
if __name__ == "__main__":
    video_path = r"C:\Video\v2\v2.mp4"  # Replace with your video path
    output_dir = r"C:\Video\v2\split"  # Output directory

    clean_folder(output_dir)
    
    # Extract frames between 67 and 73 seconds
    extract_frames_between_seconds(video_path, output_dir, 6, 15)