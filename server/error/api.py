from flask import Flask, jsonify
from scraper import scrape
from flask_cors import CORS, cross_origin
from flask_socketio import SocketIO, emit
from parallel import fetch
from transformers import BartTokenizer,BartForConditionalGeneration, pipeline

model=BartForConditionalGeneration.from_pretrained('Yale-LILY/brio-cnndm-uncased')
tokenizer=BartTokenizer.from_pretrained('Yale-LILY/brio-cnndm-uncased')
summarizer=pipeline("summarization",model=model,tokenizer=tokenizer,batch_size=16,truncation=True,device=0)


app = Flask(__name__)
CORS(app, support_credentials=True)
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/api')
@cross_origin(supports_credentials=True)
def api():
    data = fetch()
    return jsonify(data)
    
    
@socketio.on('summarize_content')
@cross_origin(supports_credentials=True)
def handle_summarize_content(data):
    summarized_content = summarizer(data['content'], min_length=120, do_sample=False)[0]['summary_text']
    emit('content_updated', {'content': summarized_content, 'id': data['id']} , broadcast=True)

    
if __name__ == '__main__':
    socketio.run(app)