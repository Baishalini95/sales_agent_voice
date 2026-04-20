from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return '<h1>Server is working!</h1><p>Your chatbot app should work now.</p>'

if __name__ == '__main__':
    print("Starting test server on port 5000...")
    app.run(debug=True, host='127.0.0.1', port=5000)