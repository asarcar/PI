## Filename: server.py 
 
from flask import Flask, request
 
app = Flask(__name__)
 
@app.route('/', methods=['GET'])
def handle_verification():
    return request.args['hub.challenge']
 
if __name__ == '__main__':
    app.run(port=5002, debug=True)
