"""
Download service for handling YouTube and SoundCloud downloads.
"""

import yt_dlp
import tempfile
import os
import re
from typing import Optional, Dict, Any

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
        # Clean and validate URL
        cleaned_url = self._clean_url(url)
        print(f"DEBUG: Original URL: {url}")
        print(f"DEBUG: Cleaned URL: {cleaned_url}")
        if not self._is_valid_url(cleaned_url):
            raise ValueError("Invalid URL provided")
        
        # Generate unique filename
        temp_filename = f"downloaded_audio_{os.getpid()}_{id(cleaned_url)}"
        output_path = os.path.join(self.temp_dir, f"{temp_filename}.%(ext)s")
        
        # Configure yt-dlp options
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': output_format,
                'preferredquality': '192',
            }],
            'outtmpl': output_path,
            'extractflat': False,
            'writethumbnail': False,
            'writeinfojson': False,
            'noplaylist': True,  # Force single video download, ignore playlists
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Extract info first to get metadata
                info = ydl.extract_info(cleaned_url, download=False)
                
                # Download the audio
                ydl.download([cleaned_url])
                
                # Find the actual downloaded file
                actual_file_path = self._find_downloaded_file(temp_filename, output_format)
                
                if not actual_file_path or not os.path.exists(actual_file_path):
                    raise Exception("Downloaded file not found")
                
                # Extract metadata from yt-dlp info
                metadata = self._extract_metadata_from_info(info)
                
                return {
                    'file_path': actual_file_path,
                    'original_title': info.get('title', ''),
                    'original_url': url,
                    'metadata': metadata,
                    'platform': self._detect_platform(url)
                }
                
        except Exception as e:
            # Clean up any partial downloads
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
        if not url:
            return url
        
        # Handle YouTube URLs
        if 'youtube.com' in url or 'youtu.be' in url:
            return self._clean_youtube_url(url)
        
        # For other platforms, return as-is for now
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
        
        try:
            parsed = urlparse.urlparse(url)
            
            # Handle different YouTube URL formats
            if 'youtu.be' in parsed.netloc:
                # Short format: https://youtu.be/VIDEO_ID
                video_id = parsed.path[1:]  # Remove leading slash
                return f"https://www.youtube.com/watch?v={video_id}"
            
            elif 'youtube.com' in parsed.netloc:
                # Long format: https://www.youtube.com/watch?v=VIDEO_ID&other_params
                query_params = urlparse.parse_qs(parsed.query)
                
                if 'v' in query_params:
                    video_id = query_params['v'][0]
                    return f"https://www.youtube.com/watch?v={video_id}"
            
            # If we can't parse it properly, return the original URL
            return url
            
        except Exception:
            # If parsing fails, return the original URL
            return url
    
    def _is_valid_url(self, url: str) -> bool:
        """Check if URL is valid and from supported platforms."""
        if not url or not isinstance(url, str):
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
            return False
        
        # Check for supported platforms
        supported_domains = [
            'youtube.com', 'youtu.be', 'www.youtube.com',
            'soundcloud.com', 'www.soundcloud.com',
            'm.youtube.com', 'music.youtube.com'
        ]
        
        return any(domain in url.lower() for domain in supported_domains)
    
    def _detect_platform(self, url: str) -> str:
        """Detect the platform from URL."""
        url_lower = url.lower()
        if 'youtube.com' in url_lower or 'youtu.be' in url_lower:
            return 'youtube'
        elif 'soundcloud.com' in url_lower:
            return 'soundcloud'
        else:
            return 'unknown'
    
    def _find_downloaded_file(self, temp_filename: str, format: str) -> Optional[str]:
        """Find the actual downloaded file."""
        # yt-dlp might add additional suffixes to the filename
        possible_extensions = [format, 'mp3', 'm4a', 'webm', 'ogg']
        
        for ext in possible_extensions:
            file_path = os.path.join(self.temp_dir, f"{temp_filename}.{ext}")
            if os.path.exists(file_path):
                return file_path
        
        # If exact match not found, search for files with the temp_filename prefix
        for file in os.listdir(self.temp_dir):
            if file.startswith(temp_filename) and any(file.endswith(f'.{ext}') for ext in possible_extensions):
                return os.path.join(self.temp_dir, file)
        
        return None
    
    def _cleanup_partial_downloads(self, temp_filename: str):
        """Clean up any partial download files."""
        try:
            for file in os.listdir(self.temp_dir):
                if file.startswith(temp_filename):
                    file_path = os.path.join(self.temp_dir, file)
                    if os.path.exists(file_path):
                        os.unlink(file_path)
        except Exception:
            pass  # Best effort cleanup
    
    def _extract_metadata_from_info(self, info: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and normalize metadata from yt-dlp info."""
        metadata = {
            'title': None,
            'artist': None,
            'album': None,
            'year': None,
            'genre': None,
        }
        
        # Extract title
        title = info.get('title', '')
        if title:
            # Try to parse artist and title from common formats
            title, artist = self._parse_title_artist(title)
            metadata['title'] = title
            metadata['artist'] = artist
        
        # Try to get artist from various fields
        if not metadata['artist']:
            metadata['artist'] = (
                info.get('artist') or 
                info.get('creator') or 
                info.get('uploader') or 
                info.get('channel')
            )
        
        # Try to get album/playlist info
        metadata['album'] = (
            info.get('album') or 
            info.get('playlist_title') or 
            info.get('playlist')
        )
        
        # Extract year from upload date
        upload_date = info.get('upload_date')
        if upload_date and len(upload_date) >= 4:
            try:
                metadata['year'] = int(upload_date[:4])
            except ValueError:
                pass
        
        # Try to extract genre from tags or categories
        tags = info.get('tags', [])
        categories = info.get('categories', [])
        if tags and isinstance(tags, list) and len(tags) > 0:
            metadata['genre'] = tags[0]
        elif categories and isinstance(categories, list) and len(categories) > 0:
            metadata['genre'] = categories[0]
        
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
        if not title:
            return title, None
        
        # Remove common prefixes/suffixes
        title = re.sub(r'\s*\[.*?\]\s*', '', title)  # Remove [Official Video], etc.
        title = re.sub(r'\s*\(.*?official.*?\)\s*', '', title, flags=re.IGNORECASE)
        
        # Pattern: "Artist - Song Title"
        if ' - ' in title:
            parts = title.split(' - ', 1)
            if len(parts) == 2:
                return parts[1].strip(), parts[0].strip()
        
        # Pattern: "Artist: Song Title"
        if ': ' in title:
            parts = title.split(': ', 1)
            if len(parts) == 2:
                return parts[1].strip(), parts[0].strip()
        
        # Pattern: "Song Title by Artist"
        by_match = re.search(r'^(.+?)\s+by\s+(.+)$', title, re.IGNORECASE)
        if by_match:
            return by_match.group(1).strip(), by_match.group(2).strip()
        
        # Pattern: "Artist | Song Title"
        if ' | ' in title:
            parts = title.split(' | ', 1)
            if len(parts) == 2:
                return parts[1].strip(), parts[0].strip()
        
        # If no pattern matches, return the whole title as song title
        return title.strip(), None
    
    def cleanup_download(self, file_path: str):
        """Clean up downloaded file."""
        try:
            if file_path and os.path.exists(file_path):
                os.unlink(file_path)
        except Exception:
            pass  # Best effort cleanup
    
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