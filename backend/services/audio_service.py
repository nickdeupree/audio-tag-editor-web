"""
Audio service for handling audio file operations.
"""

import mutagen
from mutagen import mp3, id3, mp4, flac
from mutagen.id3 import ID3NoHeaderError, APIC
from mutagen.mp4 import MP4Cover
from mutagen.flac import Picture
import base64
from models.responses import AudioMetadata
from utils.debug import debug

class AudioService:
    debug.disable()
    """Service class for audio file operations."""
    
    def extract_metadata(self, file_path: str) -> AudioMetadata:
        """Extract metadata from an audio file."""
        debug.print(f"extract_metadata called for file: {file_path}")
        try:
            debug.print("Loading audio file with mutagen...")
            audio_file = mutagen.File(file_path)
            
            if audio_file is None:
                debug.print("Failed to load audio file - mutagen returned None")
                raise ValueError("Unable to read audio file")
            
            debug.print(f"Successfully loaded audio file, type: {type(audio_file)}")
            
            # Extract common metadata
            debug.print("Extracting metadata tags...")
            title = self._get_tag_value(audio_file, ['TIT2', 'TITLE', '\xa9nam']) or ""
            debug.print(f"Extracted title: '{title}'")
            artist = self._get_tag_value(audio_file, ['TPE1', 'ARTIST', '\xa9ART']) or ""
            debug.print(f"Extracted artist: '{artist}'")
            album = self._get_tag_value(audio_file, ['TALB', 'ALBUM', '\xa9alb']) or ""
            debug.print(f"Extracted album: '{album}'")
            year_str = self._get_tag_value(audio_file, ['TDRC', 'DATE', '\xa9day'])
            debug.print(f"Extracted year string: '{year_str}'")
            genre = self._get_tag_value(audio_file, ['TCON', 'GENRE', '\xa9gen']) or ""
            debug.print(f"Extracted genre: '{genre}'")

            # Convert year to integer if valid, otherwise None
            year = None
            if year_str:
                debug.print(f"Attempting to parse year from: '{year_str}'")
                try:
                    # Extract just the year part if it's a full date
                    year_part = year_str.split('-')[0] if '-' in year_str else year_str
                    year = int(year_part)
                    debug.print(f"Successfully parsed year: {year}")
                except (ValueError, TypeError):
                    year = None
                    debug.print(f"Failed to parse year from: '{year_str}'")

            # Extract cover art
            debug.print("Extracting cover art...")
            cover_art, cover_art_mime_type = self._extract_cover_art(audio_file)
            debug.print(f"Cover art extracted - has_art: {cover_art is not None}, mime_type: {cover_art_mime_type}")

            debug.print("Creating AudioMetadata object...")
            return AudioMetadata(
                title=title,
                artist=artist,
                album=album,
                year=year,
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
        debug.print(f"_get_tag_value called with keys: {tag_keys}")
        for key in tag_keys:
            if key in audio_file:
                value = audio_file[key]
                debug.print(f"Found tag {key} with value: {value} (type: {type(value)})")
                if isinstance(value, list) and len(value) > 0:
                    result = str(value[0])
                    debug.print(f"Returning list value[0]: '{result}'")
                    return result
                result = str(value)
                debug.print(f"Returning string value: '{result}'")
                return result
        debug.print(f"No matching tags found for keys: {tag_keys}")
        return None
    
    def update_metadata(self, file_path: str, metadata: AudioMetadata) -> bool:
        """Update metadata in an audio file."""
        debug.print(f"update_metadata called for file: {file_path}")
        debug.print(f"Metadata to update: title='{metadata.title}', artist='{metadata.artist}', album='{metadata.album}', year={metadata.year}, genre='{metadata.genre}', has_cover_art={metadata.cover_art is not None}")
        try:
            debug.print("Loading audio file for metadata update...")
            audio_file = mutagen.File(file_path)
            
            if audio_file is None:
                debug.print("Failed to load audio file for update")
                raise ValueError("Unable to read audio file")
            
            # Handle MP3 files specifically
            if hasattr(audio_file, 'tags') and hasattr(audio_file, 'add_tags'):
                debug.print("Detected MP3 file")
                # Ensure tags exist - this is the key fix!
                if audio_file.tags is None:
                    debug.print("No ID3 tags found, adding them")
                    audio_file.add_tags()
                
                # Update tags using ID3 format
                if metadata.title:
                    debug.print(f"Updating title tag to {metadata.title}")
                    audio_file.tags['TIT2'] = id3.TIT2(encoding=3, text=metadata.title)
                if metadata.artist:
                    debug.print(f"Updating artist tag to {metadata.artist}")
                    audio_file.tags['TPE1'] = id3.TPE1(encoding=3, text=metadata.artist)
                if metadata.album:
                    debug.print(f"Updating album tag to {metadata.album}")
                    audio_file.tags['TALB'] = id3.TALB(encoding=3, text=metadata.album)
                if metadata.year:
                    debug.print(f"Updating year tag to {metadata.year}")
                    audio_file.tags['TDRC'] = id3.TDRC(encoding=3, text=str(metadata.year))
                if metadata.genre:
                    debug.print(f"Updating genre tag to {metadata.genre}")
                    audio_file.tags['TCON'] = id3.TCON(encoding=3, text=metadata.genre)
                
            # Handle other formats (MP4, FLAC, etc.)
            elif hasattr(audio_file, '__setitem__'):
                debug.print("Detected other format, using direct tag setting")
                # For MP4, FLAC, etc.
                if metadata.title:
                    debug.print(f"Updating title tag to {metadata.title}")
                    if 'TIT2' in audio_file:
                        del audio_file['TIT2']
                    audio_file['TIT2'] = metadata.title
                if metadata.artist:
                    debug.print(f"Updating artist tag to {metadata.artist}")
                    if 'TPE1' in audio_file:
                        del audio_file['TPE1']
                    audio_file['TPE1'] = metadata.artist
                if metadata.album:
                    debug.print(f"Updating album tag to {metadata.album}")
                    if 'TALB' in audio_file:
                        del audio_file['TALB']
                    audio_file['TALB'] = metadata.album
                if metadata.year:
                    debug.print(f"Updating year tag to {metadata.year}")
                    if 'TDRC' in audio_file:
                        del audio_file['TDRC']
                    audio_file['TDRC'] = str(metadata.year)
                if metadata.genre:
                    debug.print(f"Updating genre tag to {metadata.genre}")
                    if 'TCON' in audio_file:
                        del audio_file['TCON']
                    audio_file['TCON'] = metadata.genre
            else:
                debug.print("Unknown audio format or no existing tags - skipping metadata update")
                
            # Update cover art if provided
            if metadata.cover_art and metadata.cover_art_mime_type:
                debug.print(f"Updating cover art, mime_type: {metadata.cover_art_mime_type}")
                self._update_cover_art_inline(audio_file, metadata.cover_art, metadata.cover_art_mime_type)
            elif metadata.cover_art is None or not metadata.cover_art:
                # Remove existing cover art if cover_art is None or empty
                debug.print("Removing cover art")
                self._remove_cover_art_inline(audio_file)
            
            audio_file.save()
            debug.print(f"Audio file saved successfully to: {file_path}")
            return True
            
        except Exception as e:
            raise ValueError(f"Error updating audio file: {str(e)}")
    
    def _update_cover_art_inline(self, audio_file, cover_art_b64: str, mime_type: str):
        """Update cover art within an already loaded audio file object."""
        debug.print(f"_update_cover_art_inline called with mime_type: {mime_type}")
        debug.print(f"Audio file type: {type(audio_file)}")
        
        cover_data = base64.b64decode(cover_art_b64)
        
        # Handle MP3 files specifically
        if isinstance(audio_file, mutagen.mp3.MP3):
            debug.print("Updating cover art for MP3/ID3 format")
            
            # Ensure tags exist
            if audio_file.tags is None:
                debug.print("Adding ID3 tags for cover art")
                audio_file.add_tags()
            
            # Remove existing cover art first
            keys_to_remove = [key for key in audio_file.tags.keys() if str(key).startswith('APIC')]
            debug.print(f"Removing {len(keys_to_remove)} existing APIC frames")
            for key in keys_to_remove:
                del audio_file.tags[key]
            
            # Add new cover art
            debug.print(f"Adding new APIC frame with {len(cover_data)} bytes")
            audio_file.tags['APIC:'] = APIC(
                encoding=3,  # UTF-8
                mime=mime_type,
                type=3,  # Cover (front)
                desc='Cover',
                data=cover_data
            )
            debug.print("APIC frame added successfully")
            
        elif hasattr(audio_file, 'get') and hasattr(audio_file, '__setitem__'):
            debug.print("Detected MP4/M4A format")
            # MP4/M4A files
            if mime_type == 'image/png':
                audio_file['covr'] = [MP4Cover(cover_data, MP4Cover.FORMAT_PNG)]
            else:
                audio_file['covr'] = [MP4Cover(cover_data, MP4Cover.FORMAT_JPEG)]
                
        elif hasattr(audio_file, 'pictures'):
            debug.print("Detected FLAC format")
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
            debug.print("Unknown audio file format!")
    
    def _remove_cover_art_inline(self, audio_file):
        """Remove cover art from an already loaded audio file object."""
        debug.print("_remove_cover_art_inline called")
        debug.print(f"Audio file type: {type(audio_file)}")
        
        # Handle different file formats
        if hasattr(audio_file, 'tags') and audio_file.tags is not None:
            debug.print("Removing cover art from MP3/ID3 format")
            # MP3/ID3 tags - remove existing cover art
            keys_to_remove = [key for key in audio_file.tags.keys() if str(key).startswith('APIC')]
            debug.print(f"Found {len(keys_to_remove)} APIC keys to remove")
            for key in keys_to_remove:
                debug.print(f"Removing APIC key: {key}")
                del audio_file.tags[key]
            debug.print("Cover art removal completed for MP3/ID3")
                
        elif hasattr(audio_file, 'get') and hasattr(audio_file, '__setitem__'):
            debug.print("Removing cover art from MP4/M4A format")
            # MP4/M4A files - remove cover art
            if 'covr' in audio_file:
                debug.print("Removing covr tag")
                del audio_file['covr']
                debug.print("covr tag removed")
            else:
                debug.print("No covr tag found")
                
        elif hasattr(audio_file, 'pictures'):
            debug.print("Removing cover art from FLAC format")
            # FLAC files - clear all pictures
            audio_file.clear_pictures()
            debug.print("All pictures cleared from FLAC file")
        else:
            debug.print("Unknown audio file format for cover art removal!")

    def _extract_cover_art(self, audio_file) -> tuple[str | None, str | None]:
        """Extract cover art from audio file and return as base64 encoded string with MIME type."""
        debug.print("_extract_cover_art called")
        debug.print(f"Audio file type: {type(audio_file)}")
        try:
            # Handle different file formats
            if hasattr(audio_file, 'tags') and audio_file.tags is not None:
                debug.print("Checking MP3/ID3 tags for cover art")
                # MP3/ID3 tags
                for key in audio_file.tags:
                    if key.startswith('APIC'):
                        debug.print(f"Found APIC tag: {key}")
                        apic = audio_file.tags[key]
                        if hasattr(apic, 'data') and hasattr(apic, 'mime'):
                            debug.print(f"APIC has data ({len(apic.data)} bytes) and mime type: {apic.mime}")
                            cover_data = base64.b64encode(apic.data).decode('utf-8')
                            debug.print(f"Returning MP3 cover art, base64 length: {len(cover_data)}")
                            return cover_data, apic.mime
                        else:
                            debug.print("APIC tag found but missing data or mime type")
                debug.print("No APIC tags found in MP3/ID3")
                        
            # Handle MP4/M4A files
            if hasattr(audio_file, 'get'):
                debug.print("Checking MP4/M4A for cover art")
                cover_data = audio_file.get('covr')
                if cover_data:
                    debug.print(f"Found covr tag with {len(cover_data)} items")
                    # MP4 cover art is stored differently
                    cover_bytes = bytes(cover_data[0])
                    debug.print(f"Cover bytes length: {len(cover_bytes)}")
                    # Detect MIME type based on magic bytes
                    mime_type = self._detect_image_mime_type(cover_bytes)
                    debug.print(f"Detected MIME type: {mime_type}")
                    cover_b64 = base64.b64encode(cover_bytes).decode('utf-8')
                    debug.print(f"Returning MP4 cover art, base64 length: {len(cover_b64)}")
                    return cover_b64, mime_type
                else:
                    debug.print("No covr tag found in MP4/M4A")
                    
            # Handle FLAC files
            if hasattr(audio_file, 'pictures') and audio_file.pictures:
                debug.print(f"Checking FLAC pictures, found {len(audio_file.pictures)} pictures")
                picture = audio_file.pictures[0]  # Get first picture
                if hasattr(picture, 'data') and hasattr(picture, 'mime'):
                    debug.print(f"FLAC picture has data ({len(picture.data)} bytes) and mime type: {picture.mime}")
                    cover_data = base64.b64encode(picture.data).decode('utf-8')
                    debug.print(f"Returning FLAC cover art, base64 length: {len(cover_data)}")
                    return cover_data, picture.mime
                else:
                    debug.print("FLAC picture found but missing data or mime type")
            else:
                debug.print("No pictures found in FLAC file")
                    
        except Exception as e:
            debug.print(f"Error extracting cover art: {e}")
            
        debug.print("No cover art found in any format")
        return None, None
    
    def _detect_image_mime_type(self, image_data: bytes) -> str:
        """Detect MIME type from image data magic bytes."""
        debug.print(f"_detect_image_mime_type called with {len(image_data)} bytes")
        debug.print(f"First 12 bytes: {image_data[:12]}")
        
        if image_data.startswith(b'\xff\xd8\xff'):
            debug.print("Detected JPEG format")
            return 'image/jpeg'
        elif image_data.startswith(b'\x89PNG\r\n\x1a\n'):
            debug.print("Detected PNG format")
            return 'image/png'
        elif image_data.startswith(b'GIF87a') or image_data.startswith(b'GIF89a'):
            debug.print("Detected GIF format")
            return 'image/gif'
        elif image_data.startswith(b'RIFF') and b'WEBP' in image_data[:12]:
            debug.print("Detected WEBP format")
            return 'image/webp'
        else:
            debug.print("Unknown format, defaulting to JPEG")
            return 'image/jpeg'  # Default fallback
    
    def update_cover_art(self, file_path: str, cover_art_b64: str, mime_type: str) -> bool:
        """Update cover art in an audio file."""
        debug.print(f"update_cover_art called for file: {file_path}")
        debug.print(f"Cover art mime_type: {mime_type}")
        debug.print(f"Cover art base64 length: {len(cover_art_b64)}")
        try:
            debug.print("Loading audio file for cover art update...")
            audio_file = mutagen.File(file_path)
            
            if audio_file is None:
                debug.print("Failed to load audio file for cover art update")
                raise ValueError("Unable to read audio file")
            
            debug.print(f"Audio file loaded successfully, type: {type(audio_file)}")
            
            # Decode base64 cover art
            debug.print("Decoding base64 cover art...")
            cover_data = base64.b64decode(cover_art_b64)
            debug.print(f"Decoded cover data length: {len(cover_data)} bytes")
            
            # Handle different file formats
            if hasattr(audio_file, 'tags') and audio_file.tags is not None:
                debug.print("Updating cover art for MP3/ID3 format")
                # MP3/ID3 tags - remove existing cover art first
                keys_to_remove = [key for key in audio_file.tags.keys() if key.startswith('APIC')]
                debug.print(f"Removing {len(keys_to_remove)} existing APIC frames")
                for key in keys_to_remove:
                    debug.print(f"Removing APIC key: {key}")
                    del audio_file.tags[key]
                
                # Add new cover art
                debug.print("Adding new APIC frame...")
                audio_file.tags['APIC:'] = APIC(
                    encoding=3,  # UTF-8
                    mime=mime_type,
                    type=3,  # Cover (front)
                    desc='Cover',
                    data=cover_data
                )
                debug.print("APIC frame added successfully")
                
            elif hasattr(audio_file, 'get') and hasattr(audio_file, '__setitem__'):
                debug.print("Updating cover art for MP4/M4A format")
                # MP4/M4A files
                if mime_type == 'image/png':
                    debug.print("Adding PNG cover to MP4")
                    audio_file['covr'] = [MP4Cover(cover_data, MP4Cover.FORMAT_PNG)]
                else:
                    debug.print("Adding JPEG cover to MP4")
                    audio_file['covr'] = [MP4Cover(cover_data, MP4Cover.FORMAT_JPEG)]
                debug.print("MP4 cover art updated")
                    
            elif hasattr(audio_file, 'pictures'):
                debug.print("Updating cover art for FLAC format")
                # FLAC files
                picture = Picture()
                picture.type = 3  # Cover (front)
                picture.mime = mime_type
                picture.desc = 'Cover'
                picture.data = cover_data
                
                # Clear existing pictures and add new one
                debug.print("Clearing existing FLAC pictures...")
                audio_file.clear_pictures()
                debug.print("Adding new FLAC picture...")
                audio_file.add_picture(picture)
                debug.print("FLAC cover art updated")
            else:
                debug.print("Unknown audio file format for cover art update!")
                return False
            
            debug.print("Saving audio file with updated cover art...")
            audio_file.save()
            debug.print(f"Cover art update completed for: {file_path}")
            return True
            
        except Exception as e:
            debug.print(f"Error updating cover art: {str(e)}")
            raise ValueError(f"Error updating cover art: {str(e)}")