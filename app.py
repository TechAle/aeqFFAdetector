from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
app = Flask(__name__)


@app.route('/')
def index():
   return "Yes"


if __name__ == '__main__':
   app.run(host='0.0.0.0', port=80)