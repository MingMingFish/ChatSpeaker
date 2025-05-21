async def get_vid(url):
    if 'https://' in url:
        if 'youtube.com' in url:
            if 'v=' in url:
                video_id = url.split('v=')[1]
            elif '/live/' in url:
                video_id = url.split('/live/')[1]
                if '?' in video_id:
                    video_id = video_id.split('?')[0]
            else:
                # print('Invalid YouTube URL: Please enter a live-stream URL.')
                return None
            if '&' in video_id:
                video_id = video_id.split('&')[0]
        else:
            # print('Invalid URL: Please enter a YouTube video URL.')
            return None
    elif len(url) == 11:
        video_id = url
    else:
        # print('Invalid video ID: Please enter a valid YouTube video ID.')
        return None
    return video_id