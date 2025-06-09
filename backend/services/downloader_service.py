"""
Download service for handling YouTube and SoundCloud downloads using yt-dlp.
"""

import os
import tempfile
import yt_dlp
from typing import Dict, Any, Optional
import re


class DownloaderService:
    """Service class for downloading audio from YouTube and SoundCloud."""
    
    def __init__(self):
        self.temp_dir = tempfile.gettempdir()
    
    def download_audio(self, url: str) -> Dict[str, Any]:
        """
        Download audio from YouTube or SoundCloud URL and return file info.
        
        Args:
            url: YouTube or SoundCloud URL
            
        Returns:
            Dict containing success status, file path, title, and error message if any
        """
        try:
            # Validate URL
            if not self._is_valid_url(url):
                return {
                    "success": False,
                    "error": "Invalid URL. Please provide a valid YouTube or SoundCloud URL."
                }
            
            # Try primary download method first
            result = self._download_with_primary_method(url)
            
            # If primary method fails with n-sig issue or format availability, try fallback method
            error_message_lower = result.get("error", "").lower()
            if "drm protected" in error_message_lower:
                return {
                    "success": False,
                    "error": "This video is DRM-protected and cannot be downloaded."
                }
            if not result["success"] and (
                "nsig extraction failed" in error_message_lower or 
                "n function search" in error_message_lower or
                "requested format is not available" in error_message_lower
            ):
                print("Primary download failed with n-sig/format issue, trying fallback method...")
                result = self._download_with_fallback_method(url)
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"An unexpected error occurred: {str(e)}"
            }
    
    def _download_with_primary_method(self, url: str) -> Dict[str, Any]:
        """Primary download method with standard options."""
        try:
            # Configure yt-dlp options for best quality MP3
            ydl_opts = {
                'format': 'bestaudio/best',  # More flexible format selection
                'outtmpl': os.path.join(self.temp_dir, '%(title)s.%(ext)s'),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '320',
                }],
                'concurrent_fragment_downloads': 5,  # Download multiple fragments at once
                'buffersize': 1024 * 1024,  # 1MB buffer
                'extractaudio': True,
                'audioformat': 'mp3',
                'embed_subs': False,
                'writesubtitles': False,
                'writeautomaticsub': False,
                'ignoreerrors': False,
                'no_warnings': True,
                'quiet': True,
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
                },
                'retries': 5,
                'fragment_retries': 5,
                'skip_unavailable_fragments': False,  # Don't skip fragments to ensure complete download
                'extractor_args': {
                    'youtube': {
                        'skip': [],  # Don't skip any formats
                    }
                },
                'file_access_retries': 5,
                'nocheckcertificate': True,
                'socket_timeout': 30,  # Increased timeout for better fragment handling
            }

            # Initialize variables to store extracted information
            extracted_info = {}
            title = "Unknown_Audio" # Default title
            original_title = "Unknown_Audio"
            uploader = "Unknown_Uploader"
            duration = 0

            # Options for the initial info extraction
            info_extraction_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': 'in_playlist', # Can speed up playlist info extraction
                'extractor_args': ydl_opts.get('extractor_args'), # Use same extractor args
                'http_headers': ydl_opts.get('http_headers'),     # Use same headers
                'retries': ydl_opts.get('retries'),               # Apply retries to info extraction
            }

            # Extract info first to get title, duration, etc.
            with yt_dlp.YoutubeDL(info_extraction_opts) as ydl:
                try:
                    retrieved_info = ydl.extract_info(url, download=False)
                    if not retrieved_info:
                        return {
                            "success": False,
                            "error": "Failed to extract video information: No data returned."
                        }
                    extracted_info = retrieved_info # Store for later use

                    # Handle playlists: if 'entries' is present, use info from the first entry
                    entry_specific_info = extracted_info
                    if 'entries' in extracted_info and extracted_info['entries']:
                        entry_specific_info = extracted_info['entries'][0]
                    
                    title = self._sanitize_filename(entry_specific_info.get('title', 'Unknown'))
                    original_title = entry_specific_info.get('title', 'Unknown') # Keep original for metadata
                    uploader = entry_specific_info.get('uploader', 'Unknown')
                    duration = entry_specific_info.get('duration', 0)
                    
                    # Check if duration is reasonable (less than 20 minutes)
                    if duration and duration > 1200:  # 20 minutes
                        return {
                            "success": False,
                            "error": "Audio is too long. Please select audio shorter than 20 minutes."
                        }
                        
                except yt_dlp.utils.DownloadError as de:
                    # This error message will be checked by download_audio for n-sig issues
                    return {
                        "success": False,
                        "error": f"Failed to extract video information: {str(de)}"
                    }
                except Exception as e:
                    return {
                        "success": False,
                        "error": f"Failed to extract video information (unexpected): {str(e)}"
                    }
            
            # Update output template with sanitized title
            ydl_opts['outtmpl'] = os.path.join(self.temp_dir, f'{title}.%(ext)s')
            
            # Download the audio using the main ydl_opts
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            # Find the downloaded file
            expected_file = os.path.join(self.temp_dir, f'{title}.mp3')
            
            if os.path.exists(expected_file):
                return {
                    "success": True,
                    "file_path": expected_file,
                    "title": title, # Sanitized title
                    "original_title": original_title, # Original title from metadata
                    "uploader": uploader, # Uploader from metadata
                    "duration": duration # Duration from metadata
                }
            else:
                # Try to find any MP3 file with similar name
                for file in os.listdir(self.temp_dir):
                    if file.endswith('.mp3') and title.lower() in file.lower():
                        file_path = os.path.join(self.temp_dir, file)
                        return {
                            "success": True,
                            "file_path": file_path,
                            "title": title,
                            "original_title": original_title,
                            "uploader": uploader,
                            "duration": duration
                        }
                
                return {
                    "success": False,
                    "error": "Downloaded file not found. The download may have failed."
                }
                
        except yt_dlp.DownloadError as e:
            error_msg = str(e)
            
            # Handle specific n-sig extraction failures
            if "nsig extraction failed" in error_msg or "n function search" in error_msg:
                return {
                    "success": False,
                    "error": "YouTube has updated their player. This is a temporary issue that usually resolves within a few hours. Please try again later, or try a different video."
                }
            
            return {
                "success": False,
                "error": f"Download failed: {error_msg}"
            }
        except Exception as e:            return {
                "success": False,
                "error": f"An unexpected error occurred: {str(e)}"
            }
    
    def _download_with_fallback_method(self, url: str) -> Dict[str, Any]:
        """Fallback download method with minimal options to bypass n-sig issues."""
        try:
            # Minimal yt-dlp options that might work when n-sig extraction fails
            ydl_opts = {
                'format': 'worstaudio/worst',  # Use lowest quality to maximize compatibility
                'outtmpl': os.path.join(self.temp_dir, '%(title)s.%(ext)s'),
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '128',  # Lower quality for maximum compatibility
                }],
                'concurrent_fragment_downloads': 3,  # Reduced concurrent downloads for fallback
                'buffersize': 512 * 1024,  # 512KB buffer for fallback
                'extractaudio': True,
                'audioformat': 'mp3',
                'quiet': True,
                'no_warnings': True,
                'nocheckcertificate': True,
                'socket_timeout': 60,  # Even longer timeout for fallback
                'extractor_args': {
                    'youtube': {
                        'skip': ['dash'],  # Only skip DASH in fallback
                        'player_skip': ['js'],  # Skip JavaScript player parsing
                    }
                },
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'
                },
                'retries': 10,  # Increase retries for fallback
                'fragment_retries': 10,
                'file_access_retries': 10,
                'skip_unavailable_fragments': False,  # Don't skip fragments
            }
            
            # Try to extract basic info first
            with yt_dlp.YoutubeDL({'quiet': True, 'no_warnings': True}) as ydl:
                try:
                    info = ydl.extract_info(url, download=False)
                    title = self._sanitize_filename(info.get('title', 'Unknown'))
                except:
                    # If info extraction fails, use a generic title
                    title = f"audio_{url.split('/')[-1][:10]}"
            
            # Update output template
            ydl_opts['outtmpl'] = os.path.join(self.temp_dir, f'{title}.%(ext)s')
            
            # Attempt download with minimal options
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            # Find the downloaded file
            expected_file = os.path.join(self.temp_dir, f'{title}.mp3')
            
            if os.path.exists(expected_file):
                return {
                    "success": True,
                    "file_path": expected_file,
                    "title": title,
                    "original_title": title,
                    "uploader": "Unknown",
                    "duration": 0
                }
            else:
                return {
                    "success": False,
                    "error": "Fallback download method also failed. YouTube may have updated their system."
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Fallback download failed: {str(e)}"
            }
    
    def _is_valid_url(self, url: str) -> bool:
        """Check if the URL is a valid YouTube or SoundCloud URL."""
        youtube_pattern = r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/'
        soundcloud_pattern = r'(https?://)?(www\.)?soundcloud\.com/'
        
        return bool(re.match(youtube_pattern, url, re.IGNORECASE) or 
                   re.match(soundcloud_pattern, url, re.IGNORECASE))
    
    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename to remove invalid characters."""
        # Remove or replace invalid filename characters
        invalid_chars = r'[<>:"/\\|?*]'
        sanitized = re.sub(invalid_chars, '', filename)
        
        # Replace multiple spaces with single space
        sanitized = re.sub(r'\s+', ' ', sanitized)
        
        # Remove leading/trailing whitespace
        sanitized = sanitized.strip()
        
        # Limit length
        if len(sanitized) > 100:
            sanitized = sanitized[:100]
        
        # Ensure it's not empty
        if not sanitized:
            sanitized = "downloaded_audio"
            
        return sanitized
    
    def cleanup_file(self, file_path: str) -> bool:
        """Clean up downloaded file."""
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
                return True
        except Exception as e:
            print(f"Error cleaning up file {file_path}: {e}")
        return False
