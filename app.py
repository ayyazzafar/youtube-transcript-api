from flask import Flask, jsonify, request
from flask_cors import CORS
from youtube_transcript_api import YouTubeTranscriptApi

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes


@app.route('/get_youtube_transcript', methods=['GET'])
def get_youtube_transcript():
    video_url = request.args.get('video_url')
    if not video_url:
        return jsonify({"error": "No video URL provided"}), 400

    video_id = video_url.split("v=")[1]
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return jsonify({"video_id": video_id, "transcript": transcript})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
