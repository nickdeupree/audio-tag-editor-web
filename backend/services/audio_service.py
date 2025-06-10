"""
Audio service for handling audio file operations.
"""

import os
import mutagen
import mutagen.id3
from mutagen.id3 import ID3NoHeaderError, APIC
from mutagen.mp4 import MP4Cover
from mutagen.flac import Picture
import base64
from models.responses import AudioMetadata
import logging

logger = logging.getLogger(__name__)

class AudioService:
    """Service class for audio file operations."""
    
    def extract_metadata(self, file_path: str) -> AudioMetadata:
        """Extract metadata from an audio file."""
        try:
            audio_file = mutagen.File(file_path)
            
            if audio_file is None:
                raise ValueError("Unable to read audio file")
              # Extract common metadata
            title = self._get_tag_value(audio_file, ['TIT2', 'TITLE', '\xa9nam']) or ""
            artist = self._get_tag_value(audio_file, ['TPE1', 'ARTIST', '\xa9ART']) or ""
            album = self._get_tag_value(audio_file, ['TALB', 'ALBUM', '\xa9alb']) or ""
            genre = self._get_tag_value(audio_file, ['TCON', 'GENRE', '\xa9gen']) or ""

            # Extract cover art
            cover_art, cover_art_mime_type = self._extract_cover_art(audio_file)

            return AudioMetadata(
                title=title,
                artist=artist,
                album=album,
                genre=genre,
                cover_art=cover_art,
                cover_art_mime_type=cover_art_mime_type,
            )
            
        except ID3NoHeaderError:
            raise ValueError("No ID3 header found in file")
        except Exception as e:
            raise ValueError(f"Error reading audio file: {str(e)}")
    def _get_tag_value(self, audio_file, tag_keys: list) -> str | None:
        """Get tag value from audio file using multiple possible keys."""
        for key in tag_keys:
            if key in audio_file:
                value = audio_file[key]
                if isinstance(value, list) and len(value) > 0:
                    return str(value[0])
                return str(value)
        return None
    
    def update_metadata(self, file_path: str, metadata: AudioMetadata) -> bool:
        try:
            # Validate file exists and has content
            if not os.path.exists(file_path):
                raise ValueError("File does not exist")
            
            file_size = os.path.getsize(file_path)
            if file_size == 0:
                raise ValueError("Audio file is empty or corrupted")
            
            # Additional validation: try to read the file
            try:
                with open(file_path, 'rb') as f:
                    # Read first few bytes to check if file is readable
                    header = f.read(16)
                    if len(header) == 0:
                        raise ValueError("Audio file is empty or corrupted")
            except Exception as e:
                raise ValueError(f"Cannot read audio file: {str(e)}")

            audio_file = mutagen.File(file_path)
            
            if audio_file is None:
                raise ValueError("Unable to read audio file - it may be corrupted or in an unsupported format")
            
            # Update tags based on file type
            if hasattr(audio_file, 'tags') and audio_file.tags is not None:
                # For MP3 files
                if metadata.title:
                    audio_file.tags['TIT2'] = mutagen.id3.TIT2(encoding=3, text=metadata.title)
                if metadata.artist:
                    audio_file.tags['TPE1'] = mutagen.id3.TPE1(encoding=3, text=metadata.artist)
                if metadata.album:
                    audio_file.tags['TALB'] = mutagen.id3.TALB(encoding=3, text=metadata.album)
                if metadata.genre:
                    audio_file.tags['TCON'] = mutagen.id3.TCON(encoding=3, text=metadata.genre)
                if hasattr(metadata, 'track') and metadata.track:
                    audio_file.tags['TRCK'] = mutagen.id3.TRCK(encoding=3, text=metadata.track)
            
            # Update cover art if provided
            if metadata.cover_art and metadata.cover_art_mime_type:
                print(f"DEBUG: Updating cover art, mime_type: {metadata.cover_art_mime_type}")
                self._update_cover_art_inline(audio_file, metadata.cover_art, metadata.cover_art_mime_type)
            elif metadata.cover_art is None or not metadata.cover_art:
                # Remove existing cover art if cover_art is None or empty
                print("DEBUG: Removing cover art")
                self._remove_cover_art_inline(audio_file)
            
            audio_file.save()
            return True
            
        except Exception as e:
            logger.error(f"Error updating metadata: {str(e)}")
            # Clean up temp file if it exists and is corrupted
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                    logger.debug(f"Cleaned up corrupted temp file: {file_path}")
                except:
                    pass
            raise ValueError(f"Error updating audio file: {str(e)}")
    
    def _update_cover_art_inline(self, audio_file, cover_art_b64: str, mime_type: str):
        """Update cover art within an already loaded audio file object."""
        print(f"DEBUG: _update_cover_art_inline called with mime_type: {mime_type}")
        print(f"DEBUG: Audio file type: {type(audio_file)}")
        print(f"DEBUG: Has tags: {hasattr(audio_file, 'tags')}")
        print(f"DEBUG: Has get: {hasattr(audio_file, 'get')}")
        print(f"DEBUG: Has pictures: {hasattr(audio_file, 'pictures')}")
        
        cover_data = base64.b64decode(cover_art_b64)
        
        # Handle different file formats
        if hasattr(audio_file, 'tags') and audio_file.tags is not None:
            print("DEBUG: Detected MP3/ID3 format")
            # MP3/ID3 tags - remove existing cover art first
            keys_to_remove = [key for key in audio_file.tags.keys() if str(key).startswith('APIC')]
            for key in keys_to_remove:
                del audio_file.tags[key]
            
            # Add new cover art
            audio_file.tags['APIC:'] = APIC(
                encoding=3,  # UTF-8
                mime=mime_type,
                type=3,  # Cover (front)
                desc='Cover',
                data=cover_data
            )
            
        elif hasattr(audio_file, 'get') and hasattr(audio_file, '__setitem__'):
            print("DEBUG: Detected MP4/M4A format")
            # MP4/M4A files
            if mime_type == 'image/png':
                audio_file['covr'] = [MP4Cover(cover_data, MP4Cover.FORMAT_PNG)]
            else:
                audio_file['covr'] = [MP4Cover(cover_data, MP4Cover.FORMAT_JPEG)]
                
        elif hasattr(audio_file, 'pictures'):
            print("DEBUG: Detected FLAC format")
            # FLAC files
            picture = Picture()
            picture.type = 3  # Cover (front)
            picture.mime = mime_type
            picture.desc = 'Cover'
            picture.data = cover_data
            
            # Clear existing pictures and add new one
            audio_file.clear_pictures()
            audio_file.add_picture(picture)
        else:
            print("DEBUG: Unknown audio file format!")
    
    def _remove_cover_art_inline(self, audio_file):
        """Remove cover art from an already loaded audio file object."""
        print(f"DEBUG: _remove_cover_art_inline called")
        print(f"DEBUG: Audio file type: {type(audio_file)}")
        
        # Handle different file formats
        if hasattr(audio_file, 'tags') and audio_file.tags is not None:
            print("DEBUG: Removing cover art from MP3/ID3 format")
            # MP3/ID3 tags - remove existing cover art
            keys_to_remove = [key for key in audio_file.tags.keys() if str(key).startswith('APIC')]
            print(f"DEBUG: Found {len(keys_to_remove)} APIC keys to remove")
            for key in keys_to_remove:
                del audio_file.tags[key]
                
        elif hasattr(audio_file, 'get') and hasattr(audio_file, '__setitem__'):
            print("DEBUG: Removing cover art from MP4/M4A format")
            # MP4/M4A files - remove cover art
            if 'covr' in audio_file:
                print("DEBUG: Removing covr tag")
                del audio_file['covr']
            else:
                print("DEBUG: No covr tag found")
                
        elif hasattr(audio_file, 'pictures'):
            print("DEBUG: Removing cover art from FLAC format")
            # FLAC files - clear all pictures
            audio_file.clear_pictures()
        else:
            print("DEBUG: Unknown audio file format for cover art removal!")

    def _extract_cover_art(self, audio_file) -> tuple[str | None, str | None]:
        """Extract cover art from audio file and return as base64 encoded string with MIME type."""
        try:
            # Handle different file formats
            if hasattr(audio_file, 'tags') and audio_file.tags is not None:
                # MP3/ID3 tags
                for key in audio_file.tags:
                    if key.startswith('APIC'):
                        apic = audio_file.tags[key]
                        if hasattr(apic, 'data') and hasattr(apic, 'mime'):
                            cover_data = base64.b64encode(apic.data).decode('utf-8')
                            return cover_data, apic.mime
                        
            # Handle MP4/M4A files
            if hasattr(audio_file, 'get'):
                cover_data = audio_file.get('covr')
                if cover_data:
                    # MP4 cover art is stored differently
                    cover_bytes = bytes(cover_data[0])
                    # Detect MIME type based on magic bytes
                    mime_type = self._detect_image_mime_type(cover_bytes)
                    cover_b64 = base64.b64encode(cover_bytes).decode('utf-8')
                    return cover_b64, mime_type
                    
            # Handle FLAC files
            if hasattr(audio_file, 'pictures') and audio_file.pictures:
                picture = audio_file.pictures[0]  # Get first picture
                if hasattr(picture, 'data') and hasattr(picture, 'mime'):
                    cover_data = base64.b64encode(picture.data).decode('utf-8')
                    return cover_data, picture.mime
                    
        except Exception as e:
            print(f"Error extracting cover art: {e}")
            
        return None, None
    
    def _detect_image_mime_type(self, image_data: bytes) -> str:
        """Detect MIME type from image data magic bytes."""
        if image_data.startswith(b'\xff\xd8\xff'):
            return 'image/jpeg'
        elif image_data.startswith(b'\x89PNG\r\n\x1a\n'):
            return 'image/png'
        elif image_data.startswith(b'GIF87a') or image_data.startswith(b'GIF89a'):
            return 'image/gif'
        elif image_data.startswith(b'RIFF') and b'WEBP' in image_data[:12]:
            return 'image/webp'
        else:
            return 'image/jpeg'  # Default fallback
    
    def update_cover_art(self, file_path: str, cover_art_b64: str, mime_type: str) -> bool:
        """Update cover art in an audio file."""
        try:
            audio_file = mutagen.File(file_path)
            
            if audio_file is None:
                raise ValueError("Unable to read audio file")
            
            # Decode base64 cover art
            cover_data = base64.b64decode(cover_art_b64)
            
            # Handle different file formats
            if hasattr(audio_file, 'tags') and audio_file.tags is not None:
                # MP3/ID3 tags - remove existing cover art first
                keys_to_remove = [key for key in audio_file.tags.keys() if key.startswith('APIC')]
                for key in keys_to_remove:
                    del audio_file.tags[key]
                
                # Add new cover art
                audio_file.tags['APIC:'] = APIC(
                    encoding=3,  # UTF-8
                    mime=mime_type,
                    type=3,  # Cover (front)
                    desc='Cover',
                    data=cover_data
                )
                
            elif hasattr(audio_file, 'get') and hasattr(audio_file, '__setitem__'):
                # MP4/M4A files
                if mime_type == 'image/png':
                    audio_file['covr'] = [MP4Cover(cover_data, MP4Cover.FORMAT_PNG)]
                else:
                    audio_file['covr'] = [MP4Cover(cover_data, MP4Cover.FORMAT_JPEG)]
                    
            elif hasattr(audio_file, 'pictures'):
                # FLAC files
                picture = Picture()
                picture.type = 3  # Cover (front)
                picture.mime = mime_type
                picture.desc = 'Cover'
                picture.data = cover_data
                
                # Clear existing pictures and add new one
                audio_file.clear_pictures()
                audio_file.add_picture(picture)
            
            audio_file.save()
            return True
            
        except Exception as e:
            raise ValueError(f"Error updating cover art: {str(e)}")