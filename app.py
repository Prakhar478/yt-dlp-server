from flask import Flask, jsonify, request
import yt_dlp
import os

app = Flask(__name__)

@app.route('/stream/<video_id>')
def get_stream(video_id):
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(
                f'https://www.youtube.com/watch?v={video_id}',
                download=False
            )
            
            # Get best audio format
            formats = info.get('formats', [])
            audio_formats = [
                f for f in formats 
                if f.get('acodec') != 'none' 
                and f.get('vcodec') == 'none'
                and f.get('url')
            ]
            
            if not audio_formats:
                # fallback to any format with audio
                audio_formats = [f for f in formats if f.get('url')]
            
            if not audio_formats:
                return jsonify({'error': 'No audio found'}), 404
            
            # Sort by quality
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
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
