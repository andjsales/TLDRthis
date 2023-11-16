from flask import Flask, render_template, redirect, request, g, session
import requests
from flask_sqlalchemy import SQLAlchemy
from models import db, connect_db, User, Summary, SavedSummary
from forms import SummarizeContent, LoginForm, SignupForm
from secrets_1 import key
from flask_migrate import Migrate

CURR_USER_KEY = "curr_user"

app = Flask(__name__)
migrate = Migrate(app, db)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///tldrthis'
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
    """
    Fetch data for API
    """
    data = {
        'url': url,
        'min_length': 100,
        'max_length': 300,
        'is_detailed': False
    }
    response = requests.post(base_url, headers=headers, json=data)
    return response.json()


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""
    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])
    else:
        g.user = None


def do_login(user):
    """Log in user."""
    session[CURR_USER_KEY] = user.id


def do_logout():
    """
    Logout user.
    """
    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route('/')
def redirect_homepage():
    """
    Redirect to homepage
    """
    return redirect("/homepage")


@app.route('/homepage', methods=["GET"])
def homepage():
    form = SummarizeContent()
    return render_template('homepage.html', user=g.user, form=form)


@app.route('/homepage', methods=["POST"])
def summary_form():
    """
    TLDR form on homepage
    """
    form = SummarizeContent()
    user = g.user
    if form.validate_on_submit():
        summary_data = fetch_summary(form.url.data)
        summary = Summary(
            original_url=form.url.data,
            summary_text=' '.join(summary_data['summary']),
            user_id=g.user,
            title=form.title.data)
        db.session.add(summary)
        db.session.commit()
    return render_template('summary.html', summary=summary, form=form, user=g.user)


@app.route('/signup', methods=["GET", "POST"])
def signup():
    """
    Create account form
    """
    form = SignupForm()
    if form.validate_on_submit():
        user = User.signup(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            username=form.username.data,
            password=form.password.data,
            email=form.email.data
        )
        db.session.commit()
        return redirect('/login')
    return render_template('signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def show_login_form():
    """
    Show the login form
    """
    form = LoginForm()
    if form.validate_on_submit():
        user = User.authenticate(form.username.data, form.password.data)
        do_login(user)
        return redirect('/homepage')
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    do_logout()
    return redirect('/login')


@app.route('/summary/<int:summary_id>', methods=['GET', 'POST'])
def summary(summary_id):
    """
    Output summary results
    """
    summary = Summary.query.get_or_404(summary_id)
    return render_template('summary.html', summary=summary)


@app.route('/profile/<int:user_id>')
def profile(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('profile.html', user=user)


@app.route('/summaries/<int:user_id>')
def show_summaries(user_id):
    user = User.query.get_or_404(user_id)
    summaries = Summary.query.all()
    return render_template('user_summaries.html', user=user, summaries=summaries)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
