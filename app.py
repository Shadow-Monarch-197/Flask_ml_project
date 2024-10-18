import os
from flask import Flask, render_template, redirect, url_for, flash, request
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from forms import LoginForm, RegistrationForm, UploadForm
from models.ocr_processing import process_and_store_student_answers
from models.keyword_extraction import extract_and_store_keywords
from models.similarity_calculation import calculate_similarity_between_embeddings, get_keywords_embeddings
from models.scoring import calculate_marks_for_student_answers
import pandas as pd

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'  # Replace with a secure secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'  # SQLite database setup

# Define upload folder paths
STUDENT_UPLOAD_FOLDER = 'student_uploads/'
REFERENCE_UPLOAD_FOLDER = 'reference_uploads/'

# Ensure these directories exist
os.makedirs(STUDENT_UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REFERENCE_UPLOAD_FOLDER, exist_ok=True)

app.config['STUDENT_UPLOAD_FOLDER'] = STUDENT_UPLOAD_FOLDER
app.config['REFERENCE_UPLOAD_FOLDER'] = REFERENCE_UPLOAD_FOLDER

db = SQLAlchemy(app)

# Flask-Login setup
login_manager = LoginManager(app)
login_manager.login_view = 'login'  # Redirect to login if not authenticated

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))  # Updated for SQLAlchemy 2.0+

# User model for authentication
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

# Registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('upload'))
    form = RegistrationForm()
    if form.validate_on_submit():
        new_user = User(username=form.username.data, email=form.email.data, password=form.password.data)
        db.session.add(new_user)
        db.session.commit()
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('upload'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.password == form.password.data:  # Replace with hashed password check in production
            login_user(user)
            flash('Login successful!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('upload'))
        else:
            flash('Login unsuccessful. Please check your credentials.', 'danger')
    return render_template('login.html', form=form)

# Logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out!', 'info')
    return redirect(url_for('login'))

# Upload route for student answers and reference CSV
@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    form = UploadForm()
    if form.validate_on_submit():
        # Get the student folder path from the form
        student_folder = form.student_folder.data

        # Validate if the provided student folder exists
        if not os.path.exists(student_folder) or not os.path.isdir(student_folder):
            flash('Invalid student folder path. Please provide a valid directory.', 'danger')
            return redirect(url_for('upload'))

        # Handle reference CSV upload
        reference_file = form.reference_csv.data
        if reference_file:
            reference_filename = secure_filename(reference_file.filename)
            reference_path = os.path.join(app.config['REFERENCE_UPLOAD_FOLDER'], reference_filename)
            reference_file.save(reference_path)
        else:
            flash('Please upload a valid CSV file.', 'danger')
            return redirect(url_for('upload'))

        # Redirect to the model processing route with the folder and CSV path as arguments
        return redirect(url_for('run_model', student_folder=student_folder, reference_csv=reference_path))

    return render_template('upload.html', form=form)

# Route to run the model with uploaded files
@app.route('/run_model', methods=['GET'])
@login_required
def run_model():
    student_folder = request.args.get('student_folder')
    reference_csv = request.args.get('reference_csv')

    # Debugging to ensure the data is correct
    print(f"Student folder: {student_folder}")
    print(f"Reference CSV: {reference_csv}")

    try:
        image_paths = [os.path.join(student_folder, filename) for filename in os.listdir(student_folder) if filename.endswith(('.jpg', '.jpeg'))]
        if not image_paths:
            flash("No valid images found in the provided folder.", 'danger')
            return redirect(url_for('upload'))
        segmented_answers = process_and_store_student_answers(image_paths)
        print(f"Segmented answers: {segmented_answers}")
    except Exception as e:
        flash(f"Error processing student images: {str(e)}", 'danger')
        return redirect(url_for('upload'))

    try:
        reference_answers = pd.read_csv(reference_csv)["Answers"].tolist()
        print(f"Reference answers: {reference_answers}")
    except Exception as e:
        flash(f"Error reading reference CSV: {str(e)}", 'danger')
        return redirect(url_for('upload'))

    try:
        student_keywords = extract_and_store_keywords(segmented_answers)
        reference_keywords = extract_and_store_keywords(reference_answers)
        print(f"Student keywords: {student_keywords}")
        print(f"Reference keywords: {reference_keywords}")
    except Exception as e:
        flash(f"Error extracting keywords: {str(e)}", 'danger')
        return redirect(url_for('upload'))

    try:
        student_embeddings = get_keywords_embeddings(student_keywords)
        reference_embeddings = get_keywords_embeddings(reference_keywords)
        similarity_scores = calculate_similarity_between_embeddings(student_embeddings, reference_embeddings)
        print(f"Similarity scores: {similarity_scores}")
    except Exception as e:
        flash(f"Error calculating similarity: {str(e)}", 'danger')
        return redirect(url_for('upload'))

    try:
        student_marks = calculate_marks_for_student_answers(similarity_scores, max_marks=5)
        # Round student marks to 2 decimal places - Added Code
        student_marks = [round(marks, 2) for marks in student_marks]  # <-- ADDED
        total_marks = round(sum(student_marks), 2)  # <-- ADDED
        print(f"Student marks: {student_marks}")
        print(f"Total marks: {total_marks}")
    except Exception as e:
        flash(f"Error calculating marks: {str(e)}", 'danger')
        return redirect(url_for('upload'))

    # Render the results.html template with the results
    return render_template('results.html', student_marks=student_marks, total_marks=total_marks, enumerate=enumerate)

# Default route to redirect to upload page after login
@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('upload'))
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
