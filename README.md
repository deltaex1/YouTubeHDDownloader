# YouTubeHDDownloader
YouTube utilizes DASH, which adapatively stores resolutions >720p in separate video and audio tracks.
This script downloads YouTube's DASH videos stream, audio stream, and SRT subtitles using YouTube's API search and pytube3, then combines HD disparate Video and Audio streams using ffmpeg into a single 1080p MP4 file; and can be re-run to capture new video search results that had not previously been downloaded. A random timer delay has been implemented to slow down the download of each video to avoid overloading YouTube's servers and violating its ToS.

This script has logging capabilities with some levels of error handling (most notably API quota), and can be re-run to prevent downloading videos that has already been downloaded previously. (os.path.exists)

This script utilizes the API's JSON results to capture the VideoID and VideoTitle, and assumes the first 3 digit of the VideoTitle text string to be the episode number, writes the files with the naming convention: VideoEpsisode - VideoID - VideoTitle.xxx

The sample API search example utilizes a specific channel, specific keywords, and type = video - and searches for Sanrio's Gudetama Official Videos with English subtitles available. Sample search: https://www.youtube.com/results?search_query=gudetama+animation+episode+official+upload+%E3%80%90sanrio+official%E3%80%91

Utilization of the YouTube API is subjected to a Google API Key and its associated quota.
