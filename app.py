from flask import Flask, render_template, redirect, request
import requests
from flask_sqlalchemy import SQLAlchemy
from models import db, connect_db, User, Summary, SavedSummary
from forms import SummarizeContent, LoginForm, SignupForm
from secrets_1 import key
from flask_migrate import Migrate


app = Flask(__name__)
migrate = Migrate(app, db)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tldrthis.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'mysecret'

connect_db(app)

base_url = 'https://tldrthis.p.rapidapi.com/v1/model/abstractive/summarize-url/'

headers = {
    'content-type': 'application/json',
    'X-RapidAPI-Key': key,
    'X-RapidAPI-Host': 'tldrthis.p.rapidapi.com'
}


def fetch_summary(url):
    data = {
        'url': url,
        'min_length': 100,
        'max_length': 300,
        'is_detailed': False
    }
    response = requests.post(base_url, headers=headers, json=data)
    return response.json()


@app.route('/')
def redirect_homepage():
    return redirect("/homepage")


@app.route('/create', methods=["GET", "POST"])
def signup():
    """
    Signup form
    """
    form = SignupForm()
    if form.validate_on_submit():
        user = User.signup(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            username=form.last_name.data,
            password=form.password.data,
            email=form.email.data
        )
        db.session.add(user)
        db.session.commit()
        return redirect('/login', user=user)
    return render_template('signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def show_login_form():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.authenticate(form.username.data, form.password.data)
        return redirect('/homepage', user=user)
    return render_template('login.html', form=form)


@app.route('/homepage', methods=['GET', 'POST'])
def homepage():
    form = SummarizeContent()
    # user = User.query.get_or_404()
    if form.validate_on_submit():
        summary_data = fetch_summary(form.url.data)
        summary = Summary(
            original_url=form.url.data,
            summary_text=' '.join(summary_data['summary']),
            # user_id=user.id,
            title=form.title.data)
        db.session.add(summary)
        db.session.commit()
        return render_template('summary.html', summary=summary)
    return render_template('homepage.html', form=form)


@app.route('/summary/<int:summary_id>', methods=['GET', 'POST'])
def summary(summary_id):
    summary = Summary.query.get_or_404(summary_id)
    return render_template('summary.html', summary=summary)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
