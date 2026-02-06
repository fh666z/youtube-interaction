# YouTube API Capabilities Overview

This document lists all available YouTube API functions and capabilities that can be integrated into your interaction app. Functions are organized by source (library/API) and implementation status.

## Currently Implemented Functions

Your app currently uses these tools (defined in `src/tools/youtube.py`):

1. **`extract_video_id`** - Extracts 11-character video ID from YouTube URLs
2. **`fetch_transcript`** - Fetches video transcripts in specified language
3. **`search_youtube`** - Searches YouTube for videos by query string
4. **`get_full_metadata`** - Gets basic metadata (title, views, duration, channel, likes, comments, chapters)
5. **`get_thumbnails`** - Retrieves available thumbnail URLs and resolutions

---

## Available via yt-dlp (Currently Used Library)

yt-dlp can extract much more metadata than currently used. Here are additional fields available from `extract_info()`:

### Video Information
- **`description`** - Full video description text
- **`tags`** - List of video tags/keywords
- **`categories`** - Video category (e.g., "Music", "Gaming", "Education")
- **`upload_date`** - Upload date (YYYYMMDD format)
- **`release_date`** - Release date if different from upload
- **`availability`** - Video availability status
- **`age_limit`** - Age restriction (0, 13, 18, etc.)
- **`is_live`** - Whether video is currently live
- **`was_live`** - Whether video was a live stream
- **`live_status`** - Current live status (not_live, was_live, is_live, post_live, etc.)
- **`format`** - Video format information
- **`format_id`** - Format identifier
- **`ext`** - File extension
- **`resolution`** - Video resolution (e.g., "1080p")
- **`fps`** - Frames per second
- **`vcodec`** - Video codec
- **`acodec`** - Audio codec
- **`filesize`** - File size in bytes
- **`filesize_approx`** - Approximate file size

### Channel Information
- **`channel_id`** - Channel ID
- **`channel_url`** - Channel URL
- **`channel`** - Channel display name
- **`uploader_id`** - Uploader user ID
- **`uploader_url`** - Uploader profile URL
- **`channel_follower_count`** - Number of channel subscribers/followers

### Engagement Metrics
- **`average_rating`** - Average rating (if available)
- **`dislike_count`** - Number of dislikes (if available)
- **`repost_count`** - Number of reposts/shares

### Content Details
- **`subtitles`** - Available subtitle tracks
- **`automatic_captions`** - Available automatic caption tracks
- **`requested_subtitles`** - Requested subtitle information
- **`chapters`** - Video chapters with timestamps (already partially used)
- **`heatmap`** - Engagement heatmap data (if available)

### Playlist Information
- **`playlist`** - Playlist name (if video is in a playlist)
- **`playlist_id`** - Playlist ID
- **`playlist_index`** - Position in playlist
- **`playlist_count`** - Total videos in playlist

### Additional Metadata
- **`webpage_url`** - Canonical video URL
- **`original_url`** - Original URL if redirected
- **`language`** - Video language
- **`location`** - Video location/geographic data
- **`license`** - Video license type
- **`series`** - Series name (if part of a series)
- **`season_number`** - Season number
- **`episode_number`** - Episode number
- **`track`** - Track name (for music videos)
- **`artist`** - Artist name (for music videos)
- **`album`** - Album name (for music videos)
- **`release_year`** - Release year

### Download & Stream Information
- **`formats`** - List of all available formats
- **`requested_formats`** - Requested format information
- **`url`** - Direct video URL
- **`manifest_url`** - Manifest URL for streaming

---

## Available via pytube (Currently Used Library)

Additional capabilities from pytube beyond basic search:

### Search Enhancements
- **Filter by date** - Search videos uploaded within specific date ranges
- **Filter by duration** - Search short videos (< 4 min) or long videos (> 20 min)
- **Filter by type** - Filter by video, channel, playlist, or movie
- **Filter by features** - HD, 4K, CC (closed captions), 3D, Live, Purchased, 360°

### Video Object Methods
- **`streams`** - Access video/audio streams
- **`thumbnail_url`** - Get thumbnail URL
- **`watch_url`** - Get watch URL
- **`embed_url`** - Get embed URL
- **`length`** - Video length in seconds
- **`publish_date`** - Publish date
- **`rating`** - Average rating
- **`description`** - Video description
- **`keywords`** - Video keywords/tags
- **`views`** - View count
- **`author`** - Channel name
- **`author_url`** - Channel URL
- **`channel_id`** - Channel ID
- **`caption_tracks`** - Available caption tracks

### Channel Object Methods
- **`channel_name`** - Channel name
- **`channel_url`** - Channel URL
- **`videos`** - Get all videos from channel
- **`video_count`** - Total video count
- **`views`** - Total channel views
- **`about`** - Channel about page info
- **`playlists`** - Get channel playlists

### Playlist Object Methods
- **`title`** - Playlist title
- **`owner`** - Playlist owner
- **`video_urls`** - List of video URLs in playlist
- **`videos`** - Get all video objects in playlist
- **`views`** - Total playlist views
- **`length`** - Number of videos

---

## Available via youtube-transcript-api (Currently Used Library)

Additional capabilities beyond basic transcript fetching:

### Transcript Functions
- **`list_transcripts()`** - List all available transcripts (manual and auto-generated)
- **`find_transcript()`** - Find transcript by language codes
- **`translate_transcript()`** - Translate transcript to another language
- **`fetch()`** - Fetch transcript with timing information
- **`get_transcript()`** - Get transcript as list of dictionaries with timestamps

### Transcript Metadata
- **Language codes** - Detect available languages
- **Is translatable** - Check if transcript can be translated
- **Is generated** - Check if transcript is auto-generated vs manual
- **Language** - Get transcript language

---

## Available via Official YouTube Data API v3

**Note:** These require API key or OAuth 2.0 authentication. Your app currently doesn't use the official API.

### Video Resources
- **`videos.list`** - Get video details (snippet, contentDetails, statistics, status, etc.)
- **`videos.insert`** - Upload videos (requires OAuth)
- **`videos.update`** - Update video metadata (requires OAuth)
- **`videos.delete`** - Delete videos (requires OAuth)
- **`videos.rate`** - Rate videos (like/dislike) (requires OAuth)
- **`videos.getRating`** - Get user's rating of videos (requires OAuth)
- **`videos.reportAbuse`** - Report abusive content (requires OAuth)

### Search Resources
- **`search.list`** - Advanced search with filters:
  - By keyword, location, published date range
  - Filter by type (video, channel, playlist)
  - Filter by video definition, duration, caption availability
  - Filter by video category, license, safe search
  - Order by relevance, date, rating, title, view count
  - Get trending videos by region

### Channel Resources
- **`channels.list`** - Get channel information:
  - Snippet (title, description, thumbnails, custom URL)
  - ContentDetails (related playlists, uploads playlist)
  - Statistics (subscriber count, video count, view count)
  - BrandingSettings (channel art, profile image)
  - ContentOwnerDetails (for content owners)
- **`channels.update`** - Update channel settings (requires OAuth)
- **`channels.updateBrandingSettings`** - Update branding (requires OAuth)

### Playlist Resources
- **`playlists.list`** - Get playlist information
- **`playlists.insert`** - Create playlists (requires OAuth)
- **`playlists.update`** - Update playlists (requires OAuth)
- **`playlists.delete`** - Delete playlists (requires OAuth)
- **`playlistItems.list`** - Get videos in a playlist
- **`playlistItems.insert`** - Add videos to playlist (requires OAuth)
- **`playlistItems.update`** - Update playlist items (requires OAuth)
- **`playlistItems.delete`** - Remove videos from playlist (requires OAuth)

### Comment Resources
- **`commentThreads.list`** - Get comment threads for videos
- **`commentThreads.insert`** - Post comments (requires OAuth)
- **`commentThreads.update`** - Update comments (requires OAuth)
- **`commentThreads.moderateComments`** - Moderate comments (requires OAuth)
- **`comments.list`** - Get comment replies
- **`comments.insert`** - Reply to comments (requires OAuth)
- **`comments.update`** - Update comment replies (requires OAuth)
- **`comments.delete`** - Delete comments (requires OAuth)
- **`comments.markAsSpam`** - Mark comments as spam (requires OAuth)
- **`comments.setModerationStatus`** - Set moderation status (requires OAuth)

### Subscription Resources
- **`subscriptions.list`** - Get user subscriptions (requires OAuth)
- **`subscriptions.insert`** - Subscribe to channels (requires OAuth)
- **`subscriptions.delete`** - Unsubscribe from channels (requires OAuth)

### Caption Resources
- **`captions.list`** - List captions for videos
- **`captions.insert`** - Upload captions (requires OAuth)
- **`captions.update`** - Update captions (requires OAuth)
- **`captions.delete`** - Delete captions (requires OAuth)
- **`captions.download`** - Download caption files

### Activity Resources
- **`activities.list`** - Get channel activity feed (requires OAuth for own channel)

### I18n Resources
- **`i18nLanguages.list`** - Get supported languages
- **`i18nRegions.list`** - Get supported regions

### Analytics Resources (YouTube Analytics API - Separate)
- **`reports.query`** - Get analytics data (views, watch time, revenue, etc.) (requires OAuth)

### Live Streaming Resources (YouTube Live Streaming API - Separate)
- **`liveBroadcasts.insert`** - Create live broadcasts (requires OAuth)
- **`liveBroadcasts.update`** - Update broadcasts (requires OAuth)
- **`liveBroadcasts.delete`** - Delete broadcasts (requires OAuth)
- **`liveStreams.insert`** - Create stream objects (requires OAuth)
- **`liveStreams.update`** - Update streams (requires OAuth)
- **`liveStreams.delete`** - Delete streams (requires OAuth)

---

## Summary by Category

### Read-Only Operations (No OAuth Required)
✅ **Currently Implemented:**
- Video search
- Video metadata extraction
- Transcript fetching
- Thumbnail retrieval

🆕 **Available to Add:**
- Enhanced metadata (description, tags, categories, dates, etc.)
- Channel information (subscriber count, channel details)
- Playlist information
- Comment reading (requires API key)
- Advanced search filters
- Trending videos by region
- Available subtitle/caption languages
- Video chapters with timestamps
- Related videos
- Video formats and stream information

### Write Operations (Requires OAuth 2.0)
- Upload videos
- Update video metadata
- Create/manage playlists
- Add/remove videos from playlists
- Post/update/delete comments
- Subscribe/unsubscribe to channels
- Rate videos (like/dislike)
- Upload/manage captions
- Manage channel settings

### Analytics & Advanced (Requires OAuth 2.0)
- Channel analytics
- Video performance metrics
- Revenue data
- Live streaming management

---

## Recommendations for Your Interaction App

Based on your current implementation, here are logical next steps:

### High Priority (Easy to Add - Uses Existing Libraries)
1. **Enhanced Metadata Extraction** - Extract description, tags, categories, upload date
2. **Channel Information** - Get channel subscriber count, channel details
3. **Playlist Support** - Get playlist information and list videos in playlists
4. **Advanced Search Filters** - Filter by date, duration, type, features
5. **Transcript with Timestamps** - Get transcript with timing information
6. **Available Languages** - List available transcript/caption languages

### Medium Priority (Requires API Key Setup)
1. **Comment Reading** - Read comments on videos
2. **Trending Videos** - Get trending videos by region
3. **Related Videos** - Get videos related to a specific video
4. **Advanced Channel Info** - Get detailed channel statistics

### Low Priority (Requires OAuth Setup)
1. **User Interactions** - Like/dislike, subscribe, comment (if you want user actions)
2. **Playlist Management** - Create/manage playlists (if you want user data modification)

---

## Next Steps

1. Review this list and select which functions you want to add
2. I'll help you implement the selected functions
3. For functions requiring API keys/OAuth, we'll need to set up authentication
