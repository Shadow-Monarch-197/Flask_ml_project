# Flask Student Answer Evaluation System

## Overview

This project is a **Flask-based web application** that evaluates student answers by comparing them with reference answers using machine learning. The system allows users to upload a folder containing student answer images and a reference answer CSV file. The system extracts text from the images using Optical Character Recognition (OCR), processes keywords, and calculates similarity between student and reference answers to assign scores.

## Features

- **User Authentication**: Secure registration and login using Flask-Login.
- **OCR Processing**: Extracts text from uploaded images using Tesseract.
- **Keyword Extraction**: Uses BERT model to extract keywords from student answers.
- **Similarity Calculation**: Utilizes RoBERTa to compute similarity scores between student answers and reference answers.
- **Marks Calculation**: Automatically assigns marks based on the similarity score between student and reference answers.
- **Results Display**: Shows individual marks for each answer and total marks with a clean, responsive UI built with Tailwind CSS.

## Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS (Tailwind CSS)
- **Database**: SQLite (via SQLAlchemy)
- **Machine Learning**: BERT (for keyword extraction), RoBERTa (for similarity calculation)
- **OCR**: Tesseract
- **Version Control**: Git, GitHub

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Configuration](#configuration)
- [Screenshots](#screenshots)
- [Contributing](#contributing)
- [License](#license)

---

## Installation

**1. Clone the repository:**

git clone https://github.com/yourusername/Flask_ml_project.git
cd Flask_ml_project

**2. Set up a virtual environment (optional but recommended):**

python -m venv venv
source venv/bin/activate  #On Windows: venv\Scripts\activate

**3. Install the dependencies:**

pip install -r requirements.txt

**4. Set up the database:**

#Initialize the SQLite database:

flask shell
from app import db, app
with app.app_context():
    db.create_all()
exit()

**5. Run the Flask app:**

python app.py

The app will be available at http://127.0.0.1:5000/

## Usage

1. **Register** or **Log in** to the system.
2. **Upload a folder** containing the student answer images in `.jpg` or `.jpeg` format.
3. **Upload the reference answers CSV file** in the provided upload section.
4. The system will process the images, compare the answers, and calculate the similarity between student answers and reference answers.
5. **View the results**: The system displays individual scores for each answer and the total score, rounded to two decimal places.

## Screenshots

### 1. **Login Page**
![Login Page](screenshots/Screenshot%20(656).png)

### 2. **Upload Page**
![Upload Page](screenshots/Screenshot%20(658).png)

### 3. **Results Page**
![Results Page](screenshots/Screenshot%20(659).png)
