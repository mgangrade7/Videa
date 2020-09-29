from flask import Flask, jsonify, request, Response
import requests
import json
import redis
import hashlib

app = Flask(__name__)
db = redis.Redis(host='redis', port=6379)


@app.route('/')
def index():
    return '<h1>Videa Backend Assignment</h1>'


@app.route("/films", methods=["POST"])
def films():
    try:
        if request.method == 'POST':
            req = requests.get('https://swapi.dev/api/films/')
            if req.status_code == 200:
                hash = hashlib.md5(str.encode("films"))
                hashKey = hash.hexdigest()
                val = db.get(name=hashKey)
                if(val is None or len(val) <= 1):
                    reqContent = req.json()
                    data = []
                    for film in reqContent['results']:
                        data.append(
                            {'title': film['title'], 'episode_id': film['episode_id'], 'release_date': film['release_date']})
                    db.set(name=hashKey, value=json.dumps(data), ex=50)
                    return Response(json.dumps(data), mimetype='application/json')
                else:
                    return Response(val, mimetype='application/json')
        else:
            return {'error': 'Invalid Response'}
    except Exception as e:
        return {'error': e}


@app.route("/characters", methods=["POST"])
def characters():
    try:
        if request.method == 'POST':
            reqData = request.get_json()
            filmid = reqData['filmid']
            req = requests.get(
                'https://swapi.dev/api/films/{}/'.format(filmid))

            if req.status_code == 200:
                hash = hashlib.md5(str.encode(str(filmid)))
                hashKey = hash.hexdigest()
                val = db.get(name=hashKey)
                if(val is None or len(val) <= 1):
                    reqContent = req.json()
                    data = []
                    for character in reqContent['characters']:
                        id = character.split("/")[-2]
                        t = requests.get(character).json()
                        data.append({'id': id, 'name': t['name']})
                    db.set(name=hashKey, value=json.dumps(data), ex=50)
                    return Response(json.dumps(data), mimetype='application/json')
                else:
                    return Response(val, mimetype='application/json')
            else:
                return {'error': 'Invalid film id'}
    except Exception as e:
        return {'error': e}


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)
