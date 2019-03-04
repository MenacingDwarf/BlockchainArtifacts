from flask import Flask, make_response, request, render_template, redirect
import requests
import datetime
import random


app = Flask(__name__)


@app.route('/')
def main_page():
    if request.cookies.get('login') is None:
        return render_template('authorization.html')
    else:
        user = requests.get('http://localhost:3000/api/Character/' + request.cookies.get('login'))
        return render_template('main-page.html', balance=user.json()['balance'], login=user.json()['login'])


@app.route('/login/', methods=['POST'])
def log_in():
    users = requests.get('http://localhost:3000/api/Character/'+request.form['login'])
    if users.status_code == 404:
        return redirect('/')
    elif users.json()['password'] != request.form['password']:
        return redirect('/')
    else:
        resp = make_response(redirect('/'))
        resp.set_cookie('login', request.form['login'])
        return resp


@app.route('/register/', methods=['POST'])
def register():
    users = requests.get('http://localhost:3000/api/Character/'+request.form['login'])
    if users.status_code != 404:
        return redirect('/')
    else:
        if requests.post('http://localhost:3000/api/Character', data={"$class": "org.acme.mynetwork.Character",
                                                                      "login": request.form['login'],
                                                                      "password": request.form['password'],
                                                                      "balance": 0
                                                                      }).status_code == 200:
            resp = make_response(redirect('/'))
            resp.set_cookie('login', request.form['login'])
            return resp
        else:
            return redirect('/')


@app.route('/quit')
def quit():
    resp = make_response(redirect('/'))
    resp.set_cookie('login', '', expires=0)
    return resp


@app.route('/puzzles')
def puzzles():
    puzzles_list = requests.get('http://localhost:3000/api/Puzzle',
                                params={"filter": "{\"where\":{\"status\": \"open\"}}"})

    return render_template('puzzles.html', puzzles=puzzles_list.json())


@app.route('/artifacts')
def artifacts():
    artifacts_list = requests.get('http://localhost:3000/api/Artifact',
                                  params={"filter": "{\"where\":{\"owner\": \"resource:org.acme.mynetwork.Character#" +
                                                    request.cookies.get('login') + "\"}}"})
    return render_template('artifacts.html', artifacts=artifacts_list.json())


@app.route('/offers')
def offers():
    recipient_offers_list = requests.get('http://localhost:3000/api/Offer',
                                         params={"filter":
                                                 "{\"where\":{"
                                                 "\"recipient\": \"resource:org.acme.mynetwork.Character#" +
                                                 request.cookies.get('login') + "\","
                                                 "\"status\": \"open\"}}"})
    autor_offers_list = requests.get('http://localhost:3000/api/Offer',
                                     params={"filter":
                                             "{\"where\":{"
                                             "\"autor\": \"resource:org.acme.mynetwork.Character#" +
                                             request.cookies.get('login') + "\","
                                             "\"status\": \"open\"}}"})
    return render_template('offers.html', recipient_offers=recipient_offers_list.json(),
                           autor_offers=autor_offers_list.json())


@app.route('/sell', methods=['POST'])
def sell():
    offerId = str(random.randint(1, 9999))
    requests.post('http://localhost:3000/api/Offer', data={"$class": "org.acme.mynetwork.Offer",
                                                            "offerId": "offer" + offerId,
                                                            "artifact": request.form['id'],
                                                            "autor": request.cookies.get('login'),
                                                            "recipient": "adminstore",
                                                            "status": "open"
                                                           })
    requests.post('http://localhost:3000/api/Trade', data={"$class": "org.acme.mynetwork.Trade",
                                                           "offer": "offer" + offerId,
                                                           "timestamp": datetime.datetime.now()
                                                           })

    return redirect('/')


@app.route('/transfer', methods=['POST'])
def transfer():
    requests.post('http://localhost:3000/api/Offer', data={"$class": "org.acme.mynetwork.Offer",
                                                            "offerId": "offer" + str(random.randint(1, 9999)),
                                                            "artifact": request.form['id'],
                                                            "autor": request.cookies.get('login'),
                                                            "recipient": request.form['recipient'],
                                                            "status": "open"
                                                           })

    return redirect('/')


@app.route('/check', methods=['POST'])
def check():
    puzzle = requests.get('http://localhost:3000/api/Puzzle/'+request.form['id'])
    if str(puzzle.json()['answer']) == str(request.form['answer']):
        r = requests.post('http://localhost:3000/api/SolvePuzzle', data={"$class": "org.acme.mynetwork.SolvePuzzle",
                                                                         "puzzle": request.form['id'],
                                                                         "solver": request.cookies.get('login'),
                                                                         "timestamp": datetime.datetime.now()
                                                                         })

    return redirect('/')


@app.route('/accept', methods=['POST'])
def accept():
    requests.post('http://localhost:3000/api/Trade', data={"$class": "org.acme.mynetwork.Trade",
                                                           "offer": request.form['id'],
                                                           "timestamp": datetime.datetime.now()
                                                           })

    return redirect('/')


if __name__ == '__main__':
    app.run()
