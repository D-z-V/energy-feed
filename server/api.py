from flask import Flask, jsonify
from scraper import scrape
from flask_cors import CORS, cross_origin
from flask_socketio import SocketIO, emit
from parallel import fetch, summarizer
from grammar import fix_text

app = Flask(__name__)
CORS(app, support_credentials=True)
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/api')
def api():
    data = fetch()
    return jsonify(data)
    
    
@socketio.on('summarize_content')
def handle_summarize_content(data):
    summarized_content = summarizer(data['content'], min_length=120, do_sample=False)[0]['summary_text']
    summarized_content = summarized_content[0].upper() + summarized_content[1:]
    summarized_content = fix_text(summarized_content)
    emit("content_updated", {'content': summarized_content, 'id': data['id']}, broadcast=True)
    return "ok"
    
if __name__ == '__main__':
    socketio.run(app)