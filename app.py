import requests
from flask import Flask, jsonify, request
from flask_cors import CORS
from youtube_transcript_api import YouTubeTranscriptApi
from pytube import YouTube
import tempfile
import os

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

CA_CERT_URL = "https://raw.githubusercontent.com/luminati-io/luminati-proxy/master/bin/ca.crt"

def get_transcript_with_proxy_and_cert(video_id, proxy_url, ca_cert_url):
    # Download the CA certificate
    ca_cert_response = requests.get(ca_cert_url)
    ca_cert_response.raise_for_status()  # Ensure we got the certificate

    # Create a temporary file to store the certificate
    with tempfile.NamedTemporaryFile(delete=False, suffix='.crt') as temp_cert:
        temp_cert.write(ca_cert_response.content)
        temp_cert_path = temp_cert.name

    try:
        # Configure the proxy settings
        proxies = {
            'http': proxy_url,
            'https': proxy_url
        }

        # Create a custom session with the proxy settings and CA certificate
        session = requests.Session()
        session.proxies.update(proxies)
        session.verify = temp_cert_path

        # Create a custom fetcher function that uses the proxied session
        def proxied_fetcher(url):
            response = session.get(url)
            return response.text

        # Use the custom fetcher with YouTubeTranscriptApi
        transcript = YouTubeTranscriptApi.get_transcript(video_id, proxies=proxies, fetcher=proxied_fetcher)

        return transcript

    finally:
        # Clean up the temporary certificate file
        os.unlink(temp_cert_path)

@app.route('/get_youtube_transcript', methods=['GET'])
def get_youtube_transcript():
    video_url = request.args.get('video_url')
    if not video_url:
        return jsonify({"error": "No video URL provided"}), 400

    video_id = video_url.split("v=")[1]
    try:
        proxy_url = 'http://brd-customer-hl_ad65f0f9-zone-residential_proxy1-country-us:76r52c3q5iz7@brd.superproxy.io:22225'
        transcript = get_transcript_with_proxy_and_cert(video_id, proxy_url, CA_CERT_URL)
        return jsonify({"video_id": video_id, "transcript": transcript})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_video_title', methods=['GET'])
def get_video_title_route():
    video_url = request.args.get('video_url')
    if not video_url:
        return jsonify({"error": "No video_url provided"}), 400

    video_title = get_video_title(video_url)
    if not video_title:
        return jsonify({"error": "Error retrieving video title"}), 500

    return jsonify({"video_url": video_url, "video_title": video_title})

def get_video_title(url):
    try:
        video = YouTube(url)
        return video.title
    except Exception as e:
        print(f"Error retrieving video title: {str(e)}")
        return None

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)