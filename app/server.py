from flask import Flask, render_template
import socket

app = Flask(__name__)

ver=1

@app.route("/")
def root():
    return render_template('root.html', host=socket.gethostname())

@app.route("/healthz")
def helthz():
    return "healthy"

if __name__ == '__main__':
    app.run(host="0.0.0.0")
