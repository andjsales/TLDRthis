from flask import Flask, render_template, redirect, request, g, session, flash, url_for
import requests
import bcrypt
import os
from models import db, connect_db, User, Summary, SavedSummary, Folder
from forms import SummarizeContent, LoginForm, SignupForm, EditProfileForm
from secrets_1 import key
from flask_migrate import Migrate

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

# Handle DATABASE_URL replacement
database_url = os.getenv('DATABASE_URL')
if database_url and database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy and Flask-Migrate
db.init_app(app)  # Initialize the db with the Flask app
migrate = Migrate(app, db)

# Connect the db (empty function now)
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
    """
    Add curr user to Flask global
    """
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


# SIGNUP, LOGIN, LOGOUT, HOMEPAGE


@app.route('/')
def redirect_homepage():
    """
    Redirect to homepage
    """
    return redirect("/homepage")


@app.route('/homepage', methods=["GET", "POST"])
def homepage():
    """
    Process and show TLDR form
    """
    form = SummarizeContent()
    summary = None
    if g.user:
        folders = Folder.query.filter_by(user_id=g.user.id).all()
    if form.validate_on_submit():
        summary_data = fetch_summary(form.url.data)
        summary = Summary(
            original_url=form.url.data,
            summary_text=' '.join(summary_data['summary']),
            user_id=g.user.id,
            title=form.title.data)
        db.session.add(summary)
        db.session.commit()
    return render_template('homepage.html', form=form, summary=summary, user=g.user)


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
    Show the login form.
    """
    form = LoginForm()
    if form.validate_on_submit():
        user = User.authenticate(form.username.data, form.password.data)
        if user:
            do_login(user)
            return redirect('/homepage')
            flash('Succesfully logged in!', 'success')

        else:
            flash("Invalid username/password", "danger")
    return render_template('login.html', form=form)


@app.route('/logout')
def logout():
    """
    Logout g.user
    """
    do_logout()
    return redirect('/login')


# SUMMARY ROUTES


@app.route('/summary/<int:summary_id>', methods=['GET', 'POST'])
def summary(summary_id):
    """
    Output summary results
    """
    summary = Summary.query.get_or_404(summary_id)
    folders = Folder.query.all()
    return render_template('summary.html', summary=summary, user=g.user, folders=folders)


@app.route('/summary/<int:summary_id>/save', methods=["POST"])
def save_summary(summary_id):
    """
    - Save the summary.
    - Create a new folder if a new folder name is provided.
    """
    new_folder_name = request.form.get('newFolderName')
    summary = Summary.query.get_or_404(summary_id)
    if not g.user:
        flash('You need to be logged in to save summaries.', 'warning')
        return redirect(url_for('login'))
    summary.user_id = g.user.id
    selected_folder_id = request.form.get('folder')
    if selected_folder_id and selected_folder_id != 'new':
        summary.folder_id = int(selected_folder_id)
    else:
        folder = Folder.query.filter_by(
            folder_name=new_folder_name, user_id=g.user.id).first()
        if not folder:
            folder = Folder(folder_name=new_folder_name, user_id=g.user.id)
            db.session.add(folder)
            db.session.commit()
            flash('New folder created.', 'success')
        summary.folder_id = folder.id
    db.session.add(summary)
    db.session.commit()
    flash('Summary saved successfully.', 'success')
    return redirect(url_for('summary', summary_id=summary.id))


@app.route('/summaries/<int:summary_id>/delete', methods=["POST"])
def delete_summary(summary_id):
    """
    Delete a summary
    """
    summary = Summary.query.get_or_404(summary_id)
    folder_id = summary.folder_id
    if g.user.id != summary.user_id:
        flash('You do not have permission to delete this summary.', 'danger')
        return redirect(url_for('homepage'))
    db.session.delete(summary)
    db.session.commit()
    flash('Summary deleted successfully. Redirecting to folders', 'success')
    return redirect(url_for('show_folder_contents', user_id=g.user.id, folder_id=folder_id))


@app.route('/summaries/<int:user_id>')
def show_summaries(user_id):
    """
    Show user tldr summary history
    """
    user = User.query.get_or_404(user_id)
    summaries = Summary.query.filter_by(
        user_id=user_id).all()
    return render_template('user_summaries.html', user=user, summaries=summaries)


# PROFILE ROUTES


@app.route('/profile/<int:user_id>')
def profile(user_id):
    """
    Render user profile
    """
    user = User.query.get_or_404(user_id)
    return render_template('profile.html', user=g.user)


@app.route('/profile/<int:user_id>/edit', methods=["GET", "POST"])
def edit_profile(user_id):
    """
    Edit user profile
    """
    form = EditProfileForm()
    user = User.query.get_or_404(user_id)
    if form.validate_on_submit():
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.username = form.username.data
        user.email = form.email.data
        user.password = form.password.data
        db.session.commit()
        return redirect(url_for('profile', user_id=user.id))
    return render_template('profile_edit.html', user=user, form=form)


@app.route('/delete_account/<int:user_id>', methods=["POST"])
def delete_account(user_id):
    """
    Delete user account
    """
    if not g.user or g.user.id != user_id:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    user = User.query.get_or_404(user_id)
    folders = Folder.query.filter_by(user_id=user_id).all()
    for folder in folders:
        Summary.query.filter_by(folder_id=folder.id).delete()
        db.session.delete(folder)
    Summary.query.filter_by(user_id=user_id).delete()
    db.session.delete(user)
    db.session.commit()
    flash("Account deleted successfully. Redirecting to Homepage", "success")
    return redirect("/")


# FOLDER ROUTES


@app.route('/<int:user_id>/folders')
def show_folders(user_id):
    """
    Show all user folders 
    """
    user = User.query.get_or_404(user_id)
    folders = Folder.query.filter_by(user_id=user_id).all()
    return render_template('folders.html', user=g.user, folders=folders)


@app.route('/folders/<int:folder_id>')
def show_folder_contents(folder_id):
    """
    Show contents inside folder
    """
    folder = Folder.query.get_or_404(folder_id)
    summaries = Summary.query.filter_by(folder_id=folder.id).all()
    return render_template('show_folder_contents.html', folder=folder, user=g.user, summaries=summaries)


@app.route('/folders/<int:folder_id>/delete', methods=["POST"])
def delete_folder(folder_id):
    """
    Delete folder
    """
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect(url_for('show_login_form'))
    folder = Folder.query.get_or_404(folder_id)
    if folder.user_id != g.user.id:
        flash("Access unauthorized.", "danger")
        return redirect(url_for('show_login_form'))
    db.session.delete(folder)
    db.session.commit()
    flash("Folder deleted successfully.", "success")
    return redirect(url_for('show_folders', user_id=g.user.id))


@app.route('/<int:user_id>/folders', methods=["GET", "POST"])
def new_folder(user_id):
    """
    Create a new folder
    """
    if not g.user or g.user.id != user_id:
        flash("Access unauthorized.", "danger")
        return redirect("/login")
    if request.method == "POST":
        folder_name = request.form.get('folderName')
        if folder_name:
            new_folder = Folder(folder_name=folder_name, user_id=g.user.id)
            db.session.add(new_folder)
            db.session.commit()
            flash("New folder created!", "success")
        else:
            flash("Folder name cannot be empty.", "danger")
    folders = Folder.query.filter_by(user_id=g.user.id).all()
    return render_template('folders.html', folders=folders, user_id=g.user.id)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run()
