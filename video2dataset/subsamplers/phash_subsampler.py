# Required libraries
import tempfile
import os
import imagehash
from PIL import Image
import ffmpeg

from .subsampler import Subsampler

class FramePhashSubsampler(Subsampler):
    """
    Generates perceptual hashes (phashes) for the frames of a video.
    
    Args:
        hash_size (int): The size of the hash to compute, affecting the granularity of the comparison.
        frame_rate (int): Number of frames per second to sample for hash generation.
        
    The subsampler extracts frames at the specified frame_rate, computes a phash for each frame, and stores these hashes.
    """
    
    def __init__(self, hash_size=8, frame_rate=1):
        self.hash_size = hash_size
        self.frame_rate = frame_rate
    
    def __call__(self, streams, metadata=None):
        video_bytes = streams["video"]
        phashes = []
        subsampled_metas = []
        
        for i, vid_bytes in enumerate(video_bytes):
            with tempfile.TemporaryDirectory() as tmpdir:
                input_path = os.path.join(tmpdir, "input.mp4")
                output_path = os.path.join(tmpdir, "frame_%04d.jpg")
                
                # Write video bytes to temporary file
                with open(input_path, "wb") as f:
                    f.write(vid_bytes)
                
                try:
                    # Extract frames at specified frame rate
                    ffmpeg.input(input_path).filter('fps', fps=self.frame_rate).output(output_path, format='image2', vframes=1).run()
                    
                    # Compute phash for each extracted frame
                    for frame_file in sorted(os.listdir(tmpdir)):
                        if frame_file.endswith(".jpg"):
                            frame_path = os.path.join(tmpdir, frame_file)
                            with Image.open(frame_path) as frame:
                                phash = imagehash.phash(frame, hash_size=self.hash_size)
                                phashes.append(str(phash))
                
                except Exception as e:
                    return [], None, str(e)
                
                if metadata is not None:
                    subsampled_metas.append(metadata[i])
        
        # Assuming the metadata format and how phashes are to be incorporated or returned
        if metadata is not None:
            for meta, phash in zip(subsampled_metas, phashes):
                meta['phash'] = phash
        
        return streams, metadata, None
