import os
import subprocess
import json
from flask import current_app
from app import celery, db
from app.models import Video, VideoResolution
import ffmpeg
from PIL import Image
import uuid

@celery.task(bind=True)
def process_video_async(self, video_id):
    """Process video asynchronously with Celery."""
    try:
        video = Video.query.get(video_id)
        if not video:
            raise Exception(f"Video with ID {video_id} not found")
        
        processor = VideoProcessor(video, self)
        processor.process()
        
    except Exception as e:
        # Update video status to failed
        video = Video.query.get(video_id)
        if video:
            video.update_processing_status('failed', error_message=str(e))
        raise

class VideoProcessor:
    """Video processing class using FFmpeg."""
    
    def __init__(self, video, task=None):
        self.video = video
        self.task = task
        self.upload_folder = current_app.config['UPLOAD_FOLDER']
        self.resolutions = current_app.config['VIDEO_RESOLUTIONS']
        
    def process(self):
        """Main processing pipeline."""
        try:
            # Update status to processing
            self.video.update_processing_status('processing', 0)
            
            # Step 1: Extract video metadata
            self.update_progress(10, "Extracting video metadata...")
            self.extract_metadata()
            
            # Step 2: Generate thumbnail
            self.update_progress(20, "Generating thumbnail...")
            self.generate_thumbnail()
            
            # Step 3: Process video resolutions
            self.update_progress(30, "Processing video resolutions...")
            self.process_resolutions()
            
            # Step 4: Complete processing
            self.update_progress(100, "Processing complete")
            self.video.update_processing_status('completed')
            
        except Exception as e:
            self.video.update_processing_status('failed', error_message=str(e))
            raise
    
    def update_progress(self, progress, message=""):
        """Update processing progress."""
        if self.task:
            self.task.update_state(
                state='PROGRESS',
                meta={'current': progress, 'total': 100, 'status': message}
            )
        self.video.update_processing_status('processing', progress)
    
    def extract_metadata(self):
        """Extract video metadata using FFprobe."""
        print(f"Processing video file: {self.video.file_path}")
        print(f"File exists: {os.path.exists(self.video.file_path)}")
        try:
            probe = ffmpeg.probe(self.video.file_path)
            video_stream = next((stream for stream in probe['streams'] 
                               if stream['codec_type'] == 'video'), None)
            
            if video_stream:
                self.video.width = int(video_stream.get('width', 0))
                self.video.height = int(video_stream.get('height', 0))
                self.video.fps = float(eval(video_stream.get('r_frame_rate', '0/1')))
                self.video.codec = video_stream.get('codec_name', '')
                
                # Calculate bitrate
                if 'bit_rate' in video_stream:
                    self.video.bitrate = int(video_stream['bit_rate'])
                elif 'format' in probe and 'bit_rate' in probe['format']:
                    self.video.bitrate = int(probe['format']['bit_rate'])
            
            # Get duration
            if 'format' in probe and 'duration' in probe['format']:
                self.video.duration = float(probe['format']['duration'])
            
            db.session.commit()
            
        except Exception as e:
            print(f"Error details: {str(e)}")
            print(f"Error type: {type(e)}")
            if hasattr(e, 'stderr'):
                print(f"stderr: {e.stderr}")
            raise Exception(f"Failed to extract metadata: {str(e)}")
    
    def generate_thumbnail(self):
        """Generate video thumbnail."""
        try:
            thumbnail_filename = f"{uuid.uuid4().hex}.jpg"
            thumbnail_path = os.path.join(self.upload_folder, 'thumbnails', thumbnail_filename)
            
            # Ensure thumbnails directory exists
            os.makedirs(os.path.dirname(thumbnail_path), exist_ok=True)
            
            # Extract frame at 10% of video duration or 5 seconds, whichever is smaller
            seek_time = min(self.video.duration * 0.1 if self.video.duration else 5, 5)
            
            (
                ffmpeg
                .input(self.video.file_path, ss=seek_time)
                .output(thumbnail_path, vframes=1, format='image2', vcodec='mjpeg')
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
            
            # Resize thumbnail to standard size
            self.resize_thumbnail(thumbnail_path)
            
            self.video.thumbnail_path = thumbnail_path
            db.session.commit()
            
        except Exception as e:
            # Thumbnail generation is not critical, log but don't fail
            print(f"Warning: Failed to generate thumbnail: {str(e)}")
    
    def resize_thumbnail(self, thumbnail_path, max_width=320, max_height=180):
        """Resize thumbnail to standard dimensions."""
        try:
            with Image.open(thumbnail_path) as img:
                # Calculate new dimensions maintaining aspect ratio
                img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
                
                # Save resized image
                img.save(thumbnail_path, 'JPEG', quality=85, optimize=True)
                
        except Exception as e:
            print(f"Warning: Failed to resize thumbnail: {str(e)}")
    
    def process_resolutions(self):
        """Process video into multiple resolutions."""
        if not self.video.width or not self.video.height:
            return
        
        original_height = self.video.height
        processed_count = 0
        
        for resolution_config in self.resolutions:
            target_height = resolution_config['height']
            
            # Skip if original resolution is lower than target
            if original_height < target_height:
                continue
            
            try:
                progress = 30 + (processed_count * 60 // len(self.resolutions))
                self.update_progress(progress, f"Processing {resolution_config['name']}...")
                
                self.create_resolution(resolution_config)
                processed_count += 1
                
            except Exception as e:
                print(f"Warning: Failed to create {resolution_config['name']}: {str(e)}")
                continue
    
    def create_resolution(self, resolution_config):
        """Create a specific resolution variant."""
        resolution_name = resolution_config['name']
        target_height = resolution_config['height']
        target_bitrate = resolution_config['bitrate']
        
        # Calculate target width maintaining aspect ratio
        aspect_ratio = self.video.width / self.video.height
        target_width = int(target_height * aspect_ratio)
        
        # Ensure even dimensions for video encoding
        target_width = target_width - (target_width % 2)
        target_height = target_height - (target_height % 2)
        
        # Generate output filename
        base_name = os.path.splitext(self.video.filename)[0]
        output_filename = f"{base_name}_{resolution_name}.mp4"
        output_path = os.path.join(self.upload_folder, 'processed', output_filename)
        
        # Ensure processed directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # FFmpeg encoding
        (
            ffmpeg
            .input(self.video.file_path)
            .output(
                output_path,
                vcodec='libx264',
                acodec='aac',
                video_bitrate=target_bitrate,
                audio_bitrate='128k',
                vf=f'scale={target_width}:{target_height}',
                preset='medium',
                crf=23,
                movflags='faststart'  # Enable progressive download
            )
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
        
        # Get file size
        file_size = os.path.getsize(output_path)
        
        # Create database record
        video_resolution = VideoResolution(
            video_id=self.video.id,
            resolution=resolution_name,
            file_path=output_path,
            file_size=file_size,
            bitrate=int(target_bitrate.replace('k', '')) * 1000,
            width=target_width,
            height=target_height
        )
        
        db.session.add(video_resolution)
        db.session.commit()

def get_video_info(file_path):
    """Get basic video information without processing."""
    try:
        probe = ffmpeg.probe(file_path)
        video_stream = next((stream for stream in probe['streams'] 
                           if stream['codec_type'] == 'video'), None)
        
        if not video_stream:
            return None
        
        info = {
            'width': int(video_stream.get('width', 0)),
            'height': int(video_stream.get('height', 0)),
            'duration': float(probe['format'].get('duration', 0)),
            'codec': video_stream.get('codec_name', ''),
            'fps': float(eval(video_stream.get('r_frame_rate', '0/1')))
        }
        
        return info
        
    except Exception as e:
        print(f"Error getting video info: {str(e)}")
        return None

def validate_video_file(file_path):
    """Validate if file is a valid video."""
    try:
        probe = ffmpeg.probe(file_path)
        video_streams = [stream for stream in probe['streams'] 
                        if stream['codec_type'] == 'video']
        return len(video_streams) > 0
    except:
        return False
