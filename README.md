G4 SOLUTION – AI Movie Recommender System
📌 Project Title

G4 SOLUTION – Movie Recommender

🎯 Project Purpose

The G4 SOLUTION Movie Recommender System is designed to help users discover movies tailored to their interests. It combines:

Content-Based Filtering: Recommends movies similar in genres, overview, cast, crew, and keywords.

Collaborative Filtering: Suggests movies based on rating patterns from users with similar tastes.

The system is deployed as an interactive Streamlit web application featuring user authentication, search history, embedded trailers, and external watch/download links.

🔗 Hosted App:
https://movie-recommender-group4.streamlit.app/

📘 Table of Contents

Project Description

Key Features

Technologies Used

Project Architecture

Data Handling

Installation Guide

How to Use

Data Sources

Team Credits

📖 Project Description

This system builds an AI-powered movie recommendation engine using hybrid ML techniques. A polished Streamlit UI allows users to:

Sign up, log in, reset passwords via OTP.

Select a movie and get intelligent recommendations.

Watch embedded YouTube trailers.

Access external platforms such as Netflix, MovieBox, Nkiri, and Fzmovies.

Save, view, and download their recommendation history.

The machine learning workflow includes metadata extraction, preprocessing, text vectorization, similarity matrix computation, and user rating analysis.

✨ Key Features
1. Recommendation Engines
Content-Based Filtering

Uses:

Overview text

Genres

Keywords

Top 3 cast

Director

Tools used:
CountVectorizer (max_features=5000, stop_words='english') + Cosine Similarity.

Collaborative Filtering

Uses:

User rating patterns from ratings.csv

Item-based similarity via cosine_similarity

2. User Account System

Secure registration

Login

Password reset with email OTP

SHA-256 password hashing

Unique User IDs (UUID)

3. Recommendation History

Automatic history saving

View previous results

Download or clear history

4. Interactive Movie Details

Movie overview

Embedded YouTube trailer via youtube-search

Buttons linking to:

Netflix

Fzmovies

Nkiri

MovieBox

Google search

5. UI/UX Enhancements

Beautiful custom CSS

Typewriter animation

Glassmorphism login page

Dark mode toggle

Organized layout with columns, tabs & dialog popups

🛠 Technologies Used
Core Python Libraries

pandas

numpy

scikit-learn

ast

pickle

gzip

json

hashlib

re

datetime

uuid

random

string

urllib.parse

Email & OTP

smtplib

email.mime.text

email.mime.multipart

Web App Framework

Streamlit

Extra Tools

youtube-search

Custom HTML/CSS/JS inside Streamlit

🏗 Project Architecture
project/
│
├── movie_recommend.py               # Main Streamlit app
├── movie_dict.pkl                   # Preprocessed movie metadata
├── similarity.pkl.gz                # Content-based similarity matrix
├── collab_similarity.pkl.gz         # Collaborative similarity matrix
├── collab_titles.pkl                # List of movie titles for collab filtering
├── user_database.json               # Stores user accounts & history
│
├── data/
│   ├── tmdb_5000_movies.csv
│   ├── tmdb_5000_credits.csv
│   ├── ratings.csv
│   ├── movies.csv
│
└── notebook/
    └── movie_recommender_notebook.ipynb  # Generates model files

📊 Data Handling
Content-Based Filtering Data

Loaded from:

tmdb_5000_movies.csv

tmdb_5000_credits.csv

Merged on title

Extracted features:

overview

genres

keywords

cast (top 3)

director

Metadata cleaning functions in notebook:

convert() – extract all names

convert3() – extract top 3 cast members

fetch_director() – extract director

A unified tags column is created from all cleaned fields → lowercased → vectorized.

Collaborative Filtering Data

Loaded from:

ratings.csv

movies.csv

Merged into ratings_with_name

Pivoted into user–movie matrix

Transposed for item-based similarity

🚀 Installation Guide
1. Clone the Repository
git clone <repository_url>
cd <repository_directory>

2. Create a Virtual Environment
python -m venv venv
venv\Scripts\activate       # Windows
source venv/bin/activate    # Mac/Linux

3. Install Dependencies
pip install -r requirements.txt

4. Add Required Data Files

Place these CSV files in your project folder:

tmdb_5000_movies.csv

tmdb_5000_credits.csv

ratings.csv

movies.csv

5. Generate Model Files

Run the notebook to produce:

movie_dict.pkl

similarity.pkl.gz

collab_similarity.pkl.gz

collab_titles.pkl

Ensure they are placed beside movie_recommend.py.

6. Configure Email (OTP System)

In movie_recommend.py, update:

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "your_email@gmail.com"
APP_PASSWORD = "your_app_password"

7. Start the Application
streamlit run movie_recommend.py


Your browser opens automatically.

🖥 How to Use

Launch the app

Register / Log In

Choose recommendation engine:

Content-Based

Collaborative

Select a movie

Click Find Recommendations

View details, watch trailer, open external links

Check history in the sidebar

Download or clear history

📂 Data Sources

TMDB 5000 Movie Dataset
https://www.kaggle.com/datasets/tmdb/tmdb-movie-metadata

MovieLens Rating Dataset (25M)
https://grouplens.org/datasets/movielens/

👥 Team Credits – G4 SOLUTION

Developed under Thrive Africa Machine Learning & AI Program

Contributors

Peter Agyekum

Felicia I. Nduefuna

Olivia Mawufemor Attipoe

Donkor Promise Esi Rhoda

Osborn Tulasi

Onipayede John Kwaku

Peter Agyekum Boateng

Aning Jason

Maxwell Adu

Michael Nyarku

Yeboah Eldad
