from flask import Flask, jsonify, request, render_template, redirect, url_for, flash

from twilio.rest import Client
import os


account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
verify_sid = os.getenv("TWILIO_VERIFY_SID")

client = Client(account_sid, auth_token)

print("TWILIO_VERIFY_SID loaded:", verify_sid)

from flask import Flask, render_template, request, redirect, session
from models import db, voters, Candidate
import random

app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db.init_app(app)

with app.app_context():
    db.create_all()


otp_store = {}
from flask import render_template



@app.route('/main')
def main():
    return render_template('main.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        data = request.form
        voter = voters(
            full_name=data['full_name'],
            phone=data['phone'],
            dob=data['dob'],
            gender=data['gender'],
            religion=data['religion']
        )
        db.session.add(voter)
        db.session.commit()
        return redirect('/')
    return render_template('signup.html')
@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        phone = request.form.get('phone')

        voter = voters.query.filter_by(phone=phone).first()
        if not voter:
            error = "Invalid credentials. Phone number not registered."
            return render_template('login.html', error=error)

        session['phone'] = phone


        try:
            client.verify.services(verify_sid).verifications.create(
                to=phone,
                channel='sms'
            )
        except Exception as e:
            error = f"Twilio error: {str(e)}"
            return render_template('login.html', error=error)

        return redirect('/verify_otp')

    return render_template('login.html')

@app.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    if request.method == 'POST':
        otp_entered = request.form['otp']
        phone = session.get('phone')

        verification_check = client.verify.services(verify_sid).verification_checks.create(
            to=phone,
            code=otp_entered
        )

        if verification_check.status == "approved":
            return render_template('main.html')  
        else:
            return render_template('verify_failed.html'), 401


    return render_template('verify_otp.html')


@app.route('/get_candidates', methods=['GET'])
def get_candidates():
    candidates = Candidate.query.all()
    result = []
    for candidate in candidates:
        result.append({
            'id': candidate.id,
            'name': candidate.name,
            'party': candidate.party,
            'votes': candidate.vote_count
        })
    return jsonify(result)

@app.route('/vote')
def vote():
    phone = session.get('phone')  
    voter = voters.query.filter_by(phone=phone).first()

    if not voter:
        return "Voter not found.", 404
    if voter.has_voted:
        return render_template('already_voted.html')
    return render_template('vote.html')


@app.route('/submit_vote', methods=['POST'])
def submit_vote():
    data = request.json
    candidate_id = data.get('candidate_id')
    phone = session.get('phone')  

    voter = voters.query.filter_by(phone=phone).first()
    if voter and not voter.has_voted:
        candidate = Candidate.query.get(candidate_id)
        if candidate:
            candidate.vote_count += 1
            voter.has_voted = True
            db.session.commit()
            return jsonify({"success": True})
    return jsonify({"success": False})


from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

@app.route('/add-candidate', methods=['GET', 'POST'])
def add_candidate():
    if request.method == 'POST':
        candidate_id = request.form['id']
        name = request.form['name']
        party = request.form['party']

        try:
            conn = sqlite3.connect('C://Users//Lenovo//Downloads//ballotbyte-secure-vote-main//ballotbyte_backend//instance//database.db')
            cur = conn.cursor()
            cur.execute("INSERT INTO candidate (id, name, party, vote_count) VALUES (?, ?, ?, ?)",
                        (candidate_id, name, party, 0))
            conn.commit()
            conn.close()

            flash('Candidate registered successfully!')
        except sqlite3.IntegrityError:
            flash('Error: Candidate ID already exists. Please use a unique ID.')

        return redirect(url_for('add_candidate'))

    return render_template('add_candidate.html')




@app.route('/aboutus')
def about_us():
    return render_template('aboutus.html')

@app.route('/seed')
def seed():
    db.session.add_all([
        Candidate(name='Alice', party='Red'),
        Candidate(name='Bob', party='Blue'),
        Voter(phone='1234567890'),
        Voter(phone='9876543210')
    ])
    db.session.commit()
    return "Seeded!"

@app.route('/results')
def results():
    return render_template('results.html')
