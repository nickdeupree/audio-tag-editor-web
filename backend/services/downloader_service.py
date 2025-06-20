"""
Download service for handling YouTube and SoundCloud downloads.
"""

import yt_dlp
import tempfile
import os
import re
from typing import Optional, Dict, Any
from utils.debug import debug

class DownloadService:
    """Service class for downloading audio from various platforms."""
    
    def __init__(self):
        """Initialize the download service."""
        self.temp_dir = tempfile.gettempdir()
    
    def download_audio(self, url: str, output_format: str = 'mp3') -> Dict[str, Any]:
        """
        Download audio from URL and return file info.
        
        Args:
            url: URL to download from (YouTube, SoundCloud, etc.)
            output_format: Output audio format (default: 'mp3')
            
        Returns:
            Dict containing file_path, title, artist, and other metadata
        """
        debug.print(f"download_audio called with URL: {url}")
        debug.print(f"Requested output format: {output_format}")
        
        # Clean and validate URL
        cleaned_url = self._clean_url(url)
        debug.print(f"Original URL: {url}")
        debug.print(f"Cleaned URL: {cleaned_url}")
        if not self._is_valid_url(cleaned_url):
            debug.print("URL validation failed")
            raise ValueError("Invalid URL provided")
        
        debug.print("URL validation passed")
        
        # Generate unique filename
        temp_filename = f"downloaded_audio_{os.getpid()}_{id(cleaned_url)}"
        output_path = os.path.join(self.temp_dir, f"{temp_filename}.%(ext)s")
        debug.print(f"Generated temp filename: {temp_filename}")
        debug.print(f"Output path template: {output_path}")
        
        cookies_path = '/etc/secrets/cookies1.txt'
        if not os.path.exists(cookies_path):
            debug.print(f"Cookies file not found at {cookies_path}, using default path")
            cookies_path = os.path.join(os.path.dirname(__file__), 'yt-cookies', 'cookies1.txt')        # Configure yt-dlp options
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': output_format,
                'preferredquality': '192',
            }, {
                'key': 'EmbedThumbnail',
                'already_have_thumbnail': False,
            }],
            'outtmpl': output_path,
            'extractflat': False,
            'writethumbnail': True,
            'writeinfojson': False,
            'noplaylist': True,
            'cookies_from_browser': ['chrome'],
        }
        
        debug.print(f"yt-dlp options configured: {ydl_opts}")
        
        try:
            debug.print("Initializing yt-dlp...")
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Extract info first to get metadata
                debug.print("Extracting video info...")
                info = ydl.extract_info(cleaned_url, download=False)
                debug.print(f"Video info extracted - title: {info.get('title', 'N/A')}")
                debug.print(f"Video duration: {info.get('duration', 'N/A')} seconds")
                debug.print(f"Video uploader: {info.get('uploader', 'N/A')}")
                
                # Download the audio
                debug.print("Starting audio download...")
                ydl.download([cleaned_url])
                debug.print("yt-dlp download completed")
                
                # Find the actual downloaded file
                debug.print("Searching for downloaded file...")
                actual_file_path = self._find_downloaded_file(temp_filename, output_format)
                debug.print(f"Found downloaded file: {actual_file_path}")
                
                if not actual_file_path or not os.path.exists(actual_file_path):
                    debug.print("Downloaded file not found or doesn't exist")
                    raise Exception("Downloaded file not found")
                
                debug.print(f"File exists, size: {os.path.getsize(actual_file_path)} bytes")
                
                # Extract metadata from yt-dlp info
                debug.print("Extracting metadata from yt-dlp info...")
                metadata = self._extract_metadata_from_info(info)
                debug.print(f"Extracted metadata: {metadata}")
                
                platform = self._detect_platform(url)
                debug.print(f"Detected platform: {platform}")
                
                result = {
                    'file_path': actual_file_path,
                    'original_title': info.get('title', ''),
                    'original_url': url,
                    'metadata': metadata,
                    'platform': platform
                }
                
                debug.print(f"Returning download result: {result}")
                return result
                
        except Exception as e:
            debug.print(f"Download failed with error: {str(e)}")
            # Clean up any partial downloads
            debug.print("Cleaning up partial downloads...")
            self._cleanup_partial_downloads(temp_filename)
            raise ValueError(f"Download failed: {str(e)}")
    
    def _clean_url(self, url: str) -> str:
        """
        Clean URL to remove playlist and other unwanted parameters.
        
        Args:
            url: Original URL
            
        Returns:
            Cleaned URL with only essential parameters
        """
        debug.print(f"_clean_url called with: {url}")
        if not url:
            debug.print("Empty URL provided")
            return url
        
        # Handle YouTube URLs
        if 'youtube.com' in url or 'youtu.be' in url:
            debug.print("Detected YouTube URL, cleaning...")
            cleaned = self._clean_youtube_url(url)
            debug.print(f"YouTube URL cleaned: {cleaned}")
            return cleaned
        
        # For other platforms, return as-is for now
        debug.print("Non-YouTube URL, returning as-is")
        return url
    
    def _clean_youtube_url(self, url: str) -> str:
        """
        Clean YouTube URL to extract just the video ID and remove playlist parameters.
        
        Args:
            url: YouTube URL
            
        Returns:
            Clean YouTube URL with just the video ID
        """
        import urllib.parse as urlparse
        
        debug.print(f"_clean_youtube_url called with: {url}")
        
        try:
            parsed = urlparse.urlparse(url)
            debug.print(f"Parsed URL - netloc: {parsed.netloc}, path: {parsed.path}, query: {parsed.query}")
            
            # Handle different YouTube URL formats
            if 'youtu.be' in parsed.netloc:
                # Short format: https://youtu.be/VIDEO_ID
                video_id = parsed.path[1:]  # Remove leading slash
                debug.print(f"Extracted video ID from youtu.be: {video_id}")
                clean_url = f"https://www.youtube.com/watch?v={video_id}"
                debug.print(f"Generated clean URL: {clean_url}")
                return clean_url
            
            elif 'youtube.com' in parsed.netloc:
                # Long format: https://www.youtube.com/watch?v=VIDEO_ID&other_params
                query_params = urlparse.parse_qs(parsed.query)
                debug.print(f"Query params: {query_params}")
                
                if 'v' in query_params:
                    video_id = query_params['v'][0]
                    debug.print(f"Extracted video ID from youtube.com: {video_id}")
                    clean_url = f"https://www.youtube.com/watch?v={video_id}"
                    debug.print(f"Generated clean URL: {clean_url}")
                    return clean_url
            
            # If we can't parse it properly, return the original URL
            debug.print("Could not parse YouTube URL properly, returning original")
            return url
            
        except Exception as e:
            # If parsing fails, return the original URL
            debug.print(f"Exception parsing YouTube URL: {e}, returning original")
            return url
    
    def _is_valid_url(self, url: str) -> bool:
        """Check if URL is valid and from supported platforms."""
        debug.print(f"_is_valid_url called with: {url}")
        
        if not url or not isinstance(url, str):
            debug.print("URL is empty or not a string")
            return False
        
        # Basic URL validation
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        if not url_pattern.match(url):
            debug.print("URL failed regex validation")
            return False
        
        debug.print("URL passed regex validation")
        
        # Check for supported platforms
        supported_domains = [
            'youtube.com', 'youtu.be', 'www.youtube.com',
            'soundcloud.com', 'www.soundcloud.com',
            'm.youtube.com', 'music.youtube.com'
        ]
        
        is_supported = any(domain in url.lower() for domain in supported_domains)
        debug.print(f"URL platform support check: {is_supported}")
        
        return is_supported
    
    def _detect_platform(self, url: str) -> str:
        """Detect the platform from URL."""
        debug.print(f"_detect_platform called with: {url}")
        url_lower = url.lower()
        if 'youtube.com' in url_lower or 'youtu.be' in url_lower:
            debug.print("Detected platform: youtube")
            return 'youtube'
        elif 'soundcloud.com' in url_lower:
            debug.print("Detected platform: soundcloud")
            return 'soundcloud'
        else:
            debug.print("Detected platform: unknown")
            return 'unknown'
    
    def _find_downloaded_file(self, temp_filename: str, format: str) -> Optional[str]:
        """Find the actual downloaded file."""
        debug.print(f"_find_downloaded_file called with temp_filename: {temp_filename}, format: {format}")
        
        # yt-dlp might add additional suffixes to the filename
        possible_extensions = [format, 'mp3', 'm4a', 'webm', 'ogg']
        debug.print(f"Checking possible extensions: {possible_extensions}")
        
        for ext in possible_extensions:
            file_path = os.path.join(self.temp_dir, f"{temp_filename}.{ext}")
            debug.print(f"Checking file: {file_path}")
            if os.path.exists(file_path):
                debug.print(f"Found exact match: {file_path}")
                return file_path
        
        # If exact match not found, search for files with the temp_filename prefix
        debug.print("No exact match found, searching with prefix...")
        try:
            for file in os.listdir(self.temp_dir):
                if file.startswith(temp_filename) and any(file.endswith(f'.{ext}') for ext in possible_extensions):
                    found_path = os.path.join(self.temp_dir, file)
                    debug.print(f"Found prefix match: {found_path}")
                    return found_path
        except Exception as e:
            debug.print(f"Error listing temp directory: {e}")
        
        debug.print("No downloaded file found")
        return None
    
    def _cleanup_partial_downloads(self, temp_filename: str):
        """Clean up any partial download files."""
        debug.print(f"_cleanup_partial_downloads called with: {temp_filename}")
        try:
            files_removed = 0
            for file in os.listdir(self.temp_dir):
                if file.startswith(temp_filename):
                    file_path = os.path.join(self.temp_dir, file)
                    if os.path.exists(file_path):
                        debug.print(f"Removing partial download file: {file_path}")
                        os.unlink(file_path)
                        files_removed += 1
            debug.print(f"Removed {files_removed} partial download files")
        except Exception as e:
            debug.print(f"Error during cleanup: {e}")  # Best effort cleanup
    
    def _extract_metadata_from_info(self, info: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and normalize metadata from yt-dlp info."""
        debug.print("_extract_metadata_from_info called")
        debug.print(f"Available info keys: {list(info.keys())}")
        
        metadata = {
            'title': None,
            'artist': None,
            'album': None,
            'year': None,
            'genre': None,
        }
        
        # Extract title
        title = info.get('title', '')
        debug.print(f"Raw title from info: '{title}'")
        if title:
            # Try to parse artist and title from common formats
            title, artist = self._parse_title_artist(title)
            metadata['title'] = title
            metadata['artist'] = artist
            debug.print(f"Parsed title: '{title}', artist: '{artist}'")
        
        # Try to get artist from various fields
        if not metadata['artist']:
            fields_to_check = ['artist', 'creator', 'uploader', 'channel']
            for field in fields_to_check:
                value = info.get(field)
                if value:
                    metadata['artist'] = value
                    debug.print(f"Found artist from {field}: '{value}'")
                    break
        
        # Try to get album/playlist info
        album_fields = ['album', 'playlist_title', 'playlist']
        for field in album_fields:
            value = info.get(field)
            if value:
                metadata['album'] = value
                debug.print(f"Found album from {field}: '{value}'")
                break
        
        # Extract year from upload date
        upload_date = info.get('upload_date')
        debug.print(f"Upload date: {upload_date}")
        if upload_date and len(upload_date) >= 4:
            try:
                metadata['year'] = int(upload_date[:4])
                debug.print(f"Extracted year: {metadata['year']}")
            except ValueError:
                debug.print(f"Failed to parse year from upload_date: {upload_date}")
        
        # Try to extract genre from tags or categories
        tags = info.get('tags', [])
        categories = info.get('categories', [])
        debug.print(f"Tags: {tags}")
        debug.print(f"Categories: {categories}")
        
        if tags and isinstance(tags, list) and len(tags) > 0:
            metadata['genre'] = tags[0]
            debug.print(f"Set genre from tags: '{tags[0]}'")
        elif categories and isinstance(categories, list) and len(categories) > 0:
            metadata['genre'] = categories[0]
            debug.print(f"Set genre from categories: '{categories[0]}'")
        
        debug.print(f"Final extracted metadata: {metadata}")
        return metadata
    
    def _parse_title_artist(self, title: str) -> tuple[str, Optional[str]]:
        """
        Parse title to extract artist and song title from common formats.
        Common formats:
        - "Artist - Song Title"
        - "Artist: Song Title"
        - "Song Title by Artist"
        - "Artist | Song Title"
        """
        debug.print(f"_parse_title_artist called with: '{title}'")
        
        if not title:
            debug.print("Empty title provided")
            return title, None
        
        # Remove common prefixes/suffixes
        title = re.sub(r'\s*\[.*?\]\s*', '', title)  # Remove [Official Video], etc.
        title = re.sub(r'\s*\(.*?official.*?\)\s*', '', title, flags=re.IGNORECASE)
        debug.print(f"Title after cleanup: '{title}'")
        
        # Pattern: "Artist - Song Title"
        if ' - ' in title:
            parts = title.split(' - ', 1)
            if len(parts) == 2:
                result_title, result_artist = parts[1].strip(), parts[0].strip()
                debug.print(f"Matched pattern 'Artist - Song': title='{result_title}', artist='{result_artist}'")
                return result_title, result_artist
        
        # Pattern: "Artist: Song Title"
        if ': ' in title:
            parts = title.split(': ', 1)
            if len(parts) == 2:
                result_title, result_artist = parts[1].strip(), parts[0].strip()
                debug.print(f"Matched pattern 'Artist: Song': title='{result_title}', artist='{result_artist}'")
                return result_title, result_artist
        
        # Pattern: "Song Title by Artist"
        by_match = re.search(r'^(.+?)\s+by\s+(.+)$', title, re.IGNORECASE)
        if by_match:
            result_title, result_artist = by_match.group(1).strip(), by_match.group(2).strip()
            debug.print(f"Matched pattern 'Song by Artist': title='{result_title}', artist='{result_artist}'")
            return result_title, result_artist
        
        # Pattern: "Artist | Song Title"
        if ' | ' in title:
            parts = title.split(' | ', 1)
            if len(parts) == 2:
                result_title, result_artist = parts[1].strip(), parts[0].strip()
                debug.print(f"Matched pattern 'Artist | Song': title='{result_title}', artist='{result_artist}'")
                return result_title, result_artist
        
        # If no pattern matches, return the whole title as song title
        result_title = title.strip()
        debug.print(f"No pattern matched, returning full title: '{result_title}', artist=None")
        return result_title, None
    
    def cleanup_download(self, file_path: str):
        """Clean up downloaded file."""
        debug.print(f"cleanup_download called for: {file_path}")
        try:
            if file_path and os.path.exists(file_path):
                debug.print(f"Removing file: {file_path}")
                os.unlink(file_path)
                debug.print("File removed successfully")
            else:
                debug.print("File does not exist or path is empty")
        except Exception as e:
            debug.print(f"Error during file cleanup: {e}")  # Best effort cleanup
    
    def test_ytdl_functionality(self) -> Dict[str, Any]:
        """Test yt-dlp functionality with a simple video."""
        test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"  # Rick Roll - always available
        
        ydl_opts = {
            'format': 'worst[ext=mp4]',  # Use worst quality for testing
            'noplaylist': True,
            'extract_flat': True,
            'quiet': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(test_url, download=False)
                return {
                    'success': True,
                    'title': info.get('title', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'uploader': info.get('uploader', 'Unknown')
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
