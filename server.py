from flask import *

app = Flask(__name__)


@app.route('/', methods=['GET'])
def upload_file():
    link = request.args.get('link')
    # download(link)
    # return 200, "asdf"
    return send_from_directory(directory="", filename='Deal With The Devil (賭ケグルイOP) ／ダズビー COVER-BL8EOtE9oXY.mp3')
    # return send_from_directory(directory="", filename=download(link))


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
