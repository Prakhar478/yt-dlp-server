from flask import Flask, jsonify
import yt_dlp
import os

app = Flask(__name__)

def get_cookies_file():
    cookies_content = os.environ.get('YOUTUBE_COOKIES')
    if not cookies_content:
        return None
    path = '/tmp/cookies.txt'
    with open(path, 'w') as f:
        f.write(cookies_content)
    return path

@app.route('/stream/<video_id>')
def get_stream(video_id):
    try:
        cookies_file = get_cookies_file()
        ydl_opts = {
    'format': 'bestaudio/best',
    'quiet': True,
    'no_warnings': True,
    'extractor_args': {
        'youtube': {
            'player_client': ['mweb'],
        }
    },
    'socket_timeout': 10,
}
        if cookies_file:
            ydl_opts['cookiefile'] = cookies_file

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(
                f'https://www.youtube.com/watch?v={video_id}',
                download=False
            )
            formats = info.get('formats', [])
            audio_formats = [
                f for f in formats
                if f.get('acodec') != 'none'
                and f.get('vcodec') == 'none'
                and f.get('url')
            ]
            if not audio_formats:
                audio_formats = [f for f in formats if f.get('url')]
            if not audio_formats:
                return jsonify({'error': 'No audio found'}), 404

            best = sorted(
                audio_formats,
                key=lambda f: f.get('abr') or f.get('tbr') or 0,
                reverse=True
            )[0]

            return jsonify({
                'streamUrl': best['url'],
                'duration': info.get('duration', 0),
                'title': info.get('title', ''),
                'uploader': info.get('uploader', ''),
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    cookies = os.environ.get('YOUTUBE_COOKIES')
    return jsonify({
        'status': 'ok',
        'cookies_loaded': bool(cookies),
        'cookies_length': len(cookies) if cookies else 0
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
