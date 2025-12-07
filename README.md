1. Overall Project Purpose and Title
Project Title/Name: "G4 SOLUTION - Movie Recommender"

Overall Purpose: The project aims to develop a comprehensive movie recommendation system. It combines two primary recommendation techniques:

Content-Based Filtering: Recommends movies based on similarity of their content (overview, genres, keywords, cast, crew).
Collaborative Filtering: Recommends movies based on the rating patterns of similar users.
The system is presented through an interactive Streamlit web application, allowing user authentication, personalized recommendations, history tracking, and external links for watching/downloading movies.

2. Data Handling Specifics (Notebook)
Content-Based Filtering Data:
Original Datasets: tmdb_5000_movies.csv and tmdb_5000_credits.csv.
Loading: These CSV files are loaded into pandas DataFrames named movies and credits respectively.
Merging: The movies and credits DataFrames are merged based on the common column 'title'.
Selection: Only relevant columns for content-based filtering ('movie_id', 'title', 'overview', 'genres', 'keywords', 'cast', 'crew') are selected to form the primary movies DataFrame for this method.
Collaborative Filtering Data:
Original Datasets: ratings.csv and movies.csv.
Loading: These CSV files are loaded into pandas DataFrames named ratings_df and titles_df respectively.
Merging: ratings_df is merged with titles_df on the 'movieId' column to associate ratings with movie titles, creating ratings_with_name.
Pivot Table Creation: A user_movie_matrix is created using a pivot table from ratings_with_name. Rows represent userIds, columns represent titles, and values are the rating. Missing ratings are filled with 0.
Transposition: The user_movie_matrix is transposed (.T) to prepare for calculating similarity between movies based on user ratings (item-based collaborative filtering).
3. Movie Metadata Extraction and Cleaning Functions (Notebook)
The notebook defines three custom Python functions to extract and clean movie metadata, primarily from stringified JSON-like structures in the raw datasets:

convert(obj):

Purpose: Extracts all name values from a stringified list of dictionaries. Used for genres and keywords columns.
Mechanism:
Checks for NaN values and returns an empty list if found.
If the object is already a list (meaning it's already processed), it returns it as is.
Uses ast.literal_eval() to safely convert the string representation of a list of dictionaries into an actual Python list.
Iterates through this list and appends the name value of each dictionary to a new list.
Handles cases where the original might have been a list of strings directly.
Returns the compiled list of names.
convert3(obj):

Purpose: Similar to convert(), but specifically extracts only the top 3 name values from a stringified list of dictionaries. Used for the cast column to get the main actors.
Mechanism:
Performs NaN and pre-processed list checks similar to convert().
Uses ast.literal_eval() for safe string conversion.
Iterates through the evaluated list, appending name values to a list L.
Includes a counter to stop appending after 3 names have been extracted, then breaks the loop.
Returns the list containing at most the first 3 names.
fetch_director(obj):

Purpose: Extracts the name of the director from the crew column. This column also contains stringified JSON-like data for various crew members.
Mechanism:
Performs NaN and pre-processed list checks.
Uses ast.literal_eval() for safe string conversion.
Iterates through the list of crew dictionaries.
Checks if a dictionary has a job key with the value 'Director' and a name key.
If a director is found, their name is appended to a list L, and the loop is immediately exited using break (assuming only one director per movie for this purpose).
Returns the list, which will contain either the director's name or be empty if no director was found.
4. 'Tags' Column Creation and Preprocessing (Notebook)
For content-based filtering, a comprehensive 'tags' column is created by combining various cleaned and preprocessed movie metadata. This process involves several steps:

Overview Processing:

The overview column (which contains text summaries) is converted into a list of words. Each movie's overview string is split into individual words using x.split(). If an overview is NaN or not a string, it's replaced with an empty list.
Space Removal for Categorical Data:

For the genres, keywords, cast, and crew columns (which are now lists of names after applying the convert, convert3, and fetch_director functions), any spaces within the names are removed. For example, 'Science Fiction' becomes 'ScienceFiction' and 'Sam Worthington' becomes 'SamWorthington'. This is done to treat multi-word entities as single tags, preventing them from being split into separate, less meaningful words during vectorization.
Concatenation of Features:

The processed overview (list of words), genres (list of single-word tags), keywords (list of single-word tags), cast (list of top 3 single-word cast names), and crew (list containing the single-word director's name) columns are all concatenated together to form a single list of strings, which is then assigned to the new tags column.
Final Tag String Creation:

The tags column, which is currently a list of strings for each movie, is then transformed into a single space-separated string by joining all elements of the list (" ".join(x)).
Lowercasing:

Finally, all the text in the tags column is converted to lowercase (x.lower()). This ensures that case sensitivity does not affect the similarity calculations (e.g., 'Action' and 'action' are treated as the same tag).
5. Vectorization and Similarity Calculation (Notebook)
Both content-based and collaborative filtering rely on calculating similarities between movies, but they use different underlying data representations and similarity matrices.

Content-Based Filtering Similarity:
Vectorization (CountVectorizer):

The tags column (which contains the preprocessed textual features for each movie) is converted into a numerical representation using CountVectorizer.
max_features=5000: This parameter limits the vocabulary to the 5000 most frequent words, which helps in managing dimensionality and focuses on the most significant terms.
stop_words='english': Common English stop words (like 'the', 'is', 'a') are removed as they generally do not carry much semantic meaning for distinguishing between movies.
The fit_transform() method learns the vocabulary from the tags and transforms the text into a matrix of token counts (vectors). .toarray() converts this sparse matrix into a dense NumPy array.
Similarity Calculation (cosine_similarity):

The cosine_similarity function from sklearn.metrics.pairwise is then applied to the vectors array.
This generates a similarity matrix, where each element (i, j) represents the cosine similarity between movie i and movie j based on their tags.
Cosine similarity measures the cosine of the angle between two non-zero vectors. A value closer to 1 indicates higher similarity, while a value closer to 0 indicates lower similarity (or orthogonality).
Collaborative Filtering Similarity:
Data Preparation:

The user_movie_matrix (a pivot table with userIds as rows, titles as columns, and ratings as values) is first transposed using .T.
This transposition converts the matrix so that movie titles become the rows and users become the columns. This is crucial for item-based collaborative filtering, as it allows us to compare movies based on their rating patterns across users.
Similarity Calculation (cosine_similarity):

The cosine_similarity function is applied to the transposed user_movie_matrix.T.
This creates the collab_similarity matrix, where each element (i, j) represents the cosine similarity between movie i and movie j based on how users have rated them. Movies that tend to be rated similarly by the same users will have a higher collaborative similarity score.
6. Streamlit Application Features (movie_recommend.py)
The Streamlit application is designed to provide a comprehensive and interactive movie recommendation experience with several key features:

User Authentication System:

Registration: Users can sign up with a unique username, email, and password. Password strength is checked (min 6 chars, 1 number, 1 uppercase).
Login: Existing users can log in with their credentials.
Password Reset: A "Forgot Password" feature allows users to reset their password via email OTP (One-Time Password) verification. This involves sending an email using smtplib.
User Management:

History Tracking: The application saves the user's search history, including the selected movie and the recommendations received, along with a timestamp. This history can be viewed in the sidebar.
History Management: Users can clear their entire search history.
Account Deletion: Users have the option to permanently delete their account.
Recommendation Engines:

Engine Selection: Users can switch between "Content-Based Filtering" and "Collaborative Filtering" modes using a radio button in the sidebar.
Movie Selection: A dropdown (st.selectbox) allows users to select a movie to get recommendations from.
Recommendation Display: After finding recommendations, a grid of 5 recommended movies is displayed with their titles, overviews, and posters.
Interactive Movie Details:

"View Details & Watch" Dialog: Clicking a button on a recommended movie opens a dialog box (st.dialog).
Movie Overview: Displays a detailed overview of the selected movie.
Embedded Trailer: Integrates YouTube search (youtube-search library) to find and embed the movie's trailer directly within the app.
External Links: Provides quick links to external platforms like Nkiri, Fzmovies (for download), Netflix, and MovieBox (for streaming), allowing users to search for the full movie.
User Interface & Experience Enhancements:

Dynamic UI: Uses Streamlit's layout features (st.columns, st.container, st.tabs, st.sidebar).
Theming: Includes a dark mode toggle to switch between light and dark themes.
Animations & Custom CSS: Custom CSS is injected for styling, including glassmorphism effects for the login page, a typewriter effect for the title, and a background animation.
Help Dialog: A "How it Works" dialog provides instructions on using the application.
Quick Export: Allows users to download a text file of the current recommendations.
History Export: Users can view and download details of past recommendations from their history.
External Integrations:

WhatsApp Group Link: Provides a link to join a team WhatsApp group.
Colab Notebook Link: Links to the project's Google Colab notebook.
Thrive Africa Campus Link: Links to the Thrive Africa campus page.
Team and Project Information:

An expandable section in the sidebar lists the team members and project details (Course, Provider, Mentor).
7. Technologies Used (Libraries and Frameworks)
The project leverages a combination of Python libraries for data processing, machine learning, and web application development:

Python Libraries (Notebook):
numpy: For numerical operations, especially with arrays.
pandas: For data manipulation and analysis (DataFrames).
ast: For safely evaluating string representations of Python literal structures (e.g., lists of dictionaries).
sklearn.feature_extraction.text.CountVectorizer: For converting text data into numerical feature vectors (Bag of Words model).
sklearn.metrics.pairwise.cosine_similarity: For calculating the similarity between two sets of vectors.
pickle: For serializing and de-serializing Python object structures (saving and loading models).
gzip: For compressing and decompressing files, used for saving similarity matrices efficiently.
Python Libraries (Streamlit Application - app_code):
os: For interacting with the operating system (e.g., file paths).
pickle: For loading serialized data (movie dictionary, similarity matrices).
gzip: For decompressing loaded similarity matrices.
pandas: For data manipulation, especially with the loaded movies_df.
streamlit: The primary framework for building the interactive web application.
streamlit.components.v1 as components: For embedding custom HTML components.
json: For handling JSON data, specifically the user database.
hashlib: For hashing passwords (SHA256).
uuid: For generating unique user IDs.
re: For regular expressions, used in password strength checking.
random: For generating random numbers (e.g., OTP).
string: For string operations (e.g., generating OTP characters).
smtplib: For sending emails (e.g., password reset OTP).
urllib.parse: For parsing and quoting URLs (e.g., YouTube search queries, external links).
email.mime.text.MIMEText: For creating email text content.
email.mime.multipart.MIMEMultipart: For creating multi-part email messages.
datetime: For handling dates and times (e.g., history timestamps).
youtube_search.YoutubeSearch: (External library, potentially pip install youtube-search) For searching YouTube videos to embed trailers.
Other:
HTML/CSS/JavaScript: Used within streamlit.components.v1 for custom UI elements, animations, and dynamic effects (e.g., typewriter effect, background animation, glassmorphism).
Google Colab: The development environment where the notebook was created and run.
8. Data Files Used
The following data files are used by the project:

tmdb_5000_movies.csv: Contains metadata for movies from TMDB, including budget, genres, homepage, overview, popularity, revenue, runtime, title, vote average, vote count, etc. Used for content-based filtering.
tmdb_5000_credits.csv: Contains movie credits data, specifically cast and crew information, which is merged with the movies dataset. Used for content-based filtering.
ratings.csv: Contains user ratings for movies, with userId, movieId, and rating information. Used for collaborative filtering.
movies.csv: Contains movie IDs and titles, used to map movie IDs to titles in the ratings dataset for collaborative filtering.
TMDB_movie_dataset_v11.csv: This file appears in an earlier version of the notebook (db66e867) but is then superseded by tmdb_5000_movies.csv and tmdb_5000_credits.csv for the actual content-based filtering setup. It seems to be an alternative or exploratory dataset not ultimately used in the final content-based model creation.
user_database.json: This file is created and managed by the Streamlit application to store user authentication information (username, email, hashed password, user ID) and recommendation history.
Intermediate/Output Files (generated by the notebook for the app):

movie_dict.pkl: A pickled dictionary representation of the new_df DataFrame, containing movie_id, title, tags, genres, and overview. Used by the Streamlit app.
similarity.pkl.gz: A gzipped pickled file containing the content-based cosine similarity matrix. Used by the Streamlit app.
collab_similarity.pkl.gz: A gzipped pickled file containing the collaborative filtering cosine similarity matrix. Used by the Streamlit app.
collab_titles.pkl: A pickled object containing the list of movie titles used in the collaborative filtering model. Used by the Streamlit app.
Draft README Content
Subtask:
Based on the analysis, draft the comprehensive README content.

# G4 SOLUTION: AI Movie Recommender System

## Project Description

This project develops an advanced **AI Movie Recommender System** designed to help users discover new movies tailored to their tastes. Leveraging a hybrid approach, the system combines **Content-Based Filtering** and **Collaborative Filtering** techniques to provide accurate and diverse recommendations. The application is built as a user-friendly web interface using **Streamlit**, offering personalized experiences, secure user authentication, and interactive movie details, including embedded trailers and external streaming links.

## Key Features

*   **Content-Based Filtering**: Recommends movies based on similarity in movie attributes such as genre, keywords, cast, crew (director), and plot overview. If you liked *Movie A*, you'll get recommendations for movies similar to *Movie A*.
*   **Collaborative Filtering**: Provides recommendations by finding users with similar taste patterns and suggesting movies they have enjoyed. This helps in discovering movies outside your usual preferences but loved by people like you.
*   **User Authentication System**: A robust system allowing users to:
    *   **Register**: Create new accounts with secure password strength validation.
    *   **Login**: Access personalized features.
    *   **Password Reset with OTP**: Securely reset forgotten passwords via email-based One-Time Passwords (OTP).
*   **Recommendation History**: Users can view, clear, and download their past recommendation searches, enabling them to keep track of their discoveries.
*   **Interactive Movie Details**: For each recommended movie, users can:
    *   View a detailed **overview**.
    *   Watch **embedded YouTube trailers** directly within the app.
    *   Access **external streaming and download links** (e.g., Netflix, Fzmovies) to find where to watch the movie.
*   **Intuitive User Interface (UI/UX)**:
    *   **Dark Mode Toggle**: Users can switch between dark and light themes for a comfortable viewing experience.
    *   **Custom CSS & Animations**: Enhanced visual appeal with a modern design, including a glassmorphism effect for the login/signup page and subtle background animations.
*   **Responsive Design**: Optimized for various screen sizes, ensuring a seamless experience across devices.

## Technologies Used

This project utilizes a variety of Python libraries, frameworks, and web technologies:

### Core Python Libraries:
*   **`pandas`**: For data manipulation and analysis.
*   **`numpy`**: For numerical operations, especially with similarity matrices.
*   **`scikit-learn`**: Specifically `CountVectorizer` for text vectorization and `cosine_similarity` for calculating movie similarities.
*   **`ast`**: For safely evaluating string representations of Python literal structures.
*   **`pickle`**: For serializing and deserializing Python objects (saving and loading models).
*   **`gzip`**: For compressing and decompressing model files.
*   **`json`**: For managing user authentication data.
*   **`hashlib`**: For secure password hashing.
*   **`uuid`**: For generating unique user IDs.
*   **`re`**: For regular expressions in password strength checks.
*   **`random`**: For generating OTPs.
*   **`string`**: For character sets in OTP generation.
*   **`smtplib`**: For sending emails (OTP). 
*   **`email.mime.text`**, **`email.mime.multipart`**: For creating email content.
*   **`datetime`**: For timestamping user history.
*   **`urllib.parse`**: For URL encoding, used in external links and trailer search.

### Frameworks & Tools:
*   **Streamlit**: The primary framework for building the interactive web application.
*   **`youtube-search`**: A third-party library for searching YouTube videos to embed trailers.
*   **HTML/CSS/JavaScript**: Used within Streamlit's `st.markdown` and `st.components.v1.components.html` for advanced UI customization, animations, and interactive elements.

## Setup Instructions

Follow these steps to get the G4 SOLUTION AI Movie Recommender System up and running on your local machine.

### 1. Prerequisites

Ensure you have the following installed:
*   **Python 3.8+**: Download from [python.org](https://www.python.org/downloads/).
*   **`pip`**: Python's package installer, usually comes with Python.

### 2. Clone the Repository

First, clone this GitHub repository to your local machine:

```bash
git clone <repository_url>
cd <repository_directory>
3. Set Up a Virtual Environment (Recommended)
It's highly recommended to use a virtual environment to manage project dependencies:

python -m venv venv
source venv/bin/activate  # On macOS/Linux
venv\Scripts\activate    # On Windows
4. Install Dependencies
Install all required Python packages using pip and the requirements.txt file:

pip install -r requirements.txt
5. Obtain Data Files and Model Files
This application requires several data files and pre-processed model files. You will need to:

a. Download Raw Data: Obtain the following CSV files and place them in your project directory: * tmdb_5000_movies.csv * tmdb_5000_credits.csv * ratings.csv * movies.csv

*(These files are typically provided alongside the project or can be downloaded from sources like Kaggle, e.g., [TMDB 5000 Movie Dataset](https://www.kaggle.com/datasets/tmdb/tmdb-movie-metadata) and [MovieLens 25M Dataset](https://grouplens.org/datasets/movielens/)).*
b. Generate Model Files: Run the provided Jupyter Notebook (e.g., movie_recommender_notebook.ipynb) to execute the data processing and model training steps. This notebook will generate the following .pkl and .gz files which are essential for the Streamlit app: * movie_dict.pkl * similarity.pkl.gz * collab_similarity.pkl.gz * collab_titles.pkl

Ensure these files are located in the same directory as `movie_recommend.py`.
6. Configure Email Credentials (for OTP)
To enable the password reset functionality, you need to configure an email account for sending OTPs. Edit the movie_recommend.py file and update the following lines with your Gmail credentials:

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "your_email@gmail.com"  # Replace with your email
APP_PASSWORD = "your_app_password"    # Replace with your generated app password
Important: For Gmail, you will need to generate an App Password, as direct password login for third-party apps is often blocked. Refer to Google's documentation on App Passwords.

7. Run the Streamlit Application
Once all files are in place and dependencies are installed, run the application from your terminal:

streamlit run movie_recommend.py
Your browser will automatically open the Streamlit application. If it doesn't, navigate to the local URL displayed in your terminal (usually http://localhost:8501).

How to Use the App
Login/Sign Up: Upon launching the app, you'll be greeted by a login/signup page. Create a new account or log in if you're a returning user.
Select Recommendation Engine: In the sidebar, choose between 'Content-Based Filtering' or 'Collaborative Filtering'.
Choose a Movie: From the dropdown list, select a movie you enjoy or have enjoyed in the past. This movie will serve as the basis for recommendations.
Get Recommendations: Click the 'Find Recommendations' button to generate a list of 5 movies.
Explore Details: Click 'View Details & Watch' on any recommended movie card to see its overview, watch its trailer, and find external streaming/download links.
Manage History: Your searches are saved in the 'History' section in the sidebar. You can view past recommendations, download records, or clear your history.
Data Sources
TMDB 5000 Movie Dataset: Provides comprehensive movie metadata (genres, keywords, cast, crew, overview, etc.) used for content-based analysis. Source
MovieLens 25M Dataset: Contains user ratings data used to train the collaborative filtering model. Source
Team Credits
This project was proudly developed by G4 SOLUTION, a team from the Thrive Africa Machine Learning & AI course.

Contributors:
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

Final Task
Subtask:
Present the generated detailed README content to the user, ready for inclusion in their GitHub repository. This will complete the task of providing a comprehensive documentation for the application.

Summary:
Data Analysis Key Findings
Project Core: The project, "G4 SOLUTION - Movie Recommender," integrates both Content-Based Filtering and Collaborative Filtering techniques to provide personalized movie recommendations through an interactive Streamlit web application.
Content-Based Filtering Mechanism: This method processes tmdb_5000_movies.csv and tmdb_5000_credits.csv. It extracts and cleans movie metadata (genres, keywords, cast, crew, overview) into a unified 'tags' column, then uses CountVectorizer (with max_features=5000 and stop_words='english') and cosine_similarity to compute movie similarities.
Collaborative Filtering Mechanism: This approach utilizes ratings.csv and movies.csv to construct a user_movie_matrix. cosine_similarity is then applied to the transposed matrix to determine item-based collaborative similarities.
Streamlit Application Functionality: The movie_recommend.py application offers robust features including user authentication (registration, login, password reset via email OTP using smtplib), personalized history tracking (view, clear, export), a dynamic UI for selecting recommendation engines, interactive movie details (overview, embedded YouTube trailers via youtube-search, external streaming/download links), and UI enhancements like dark mode and custom CSS.
Technology Stack: Key Python libraries include pandas, numpy, scikit-learn for data processing and modeling, and streamlit as the primary web framework. Persistence is handled with pickle and gzip for model files, and json for user data (user_database.json).
Data and Model Assets: The application relies on input CSV files (tmdb_5000_movies.csv, tmdb_5000_credits.csv, ratings.csv, movies.csv) and consumes pre-generated model files (movie_dict.pkl, similarity.pkl.gz, collab_similarity.pkl.gz, collab_titles.pkl) for its recommendation logic.
Insights or Next Steps
The detailed analysis of the application's components, data flow, and technologies directly facilitated the creation of a comprehensive and user-friendly README, which is essential for project understanding and deployment.
Ensuring that the README explicitly covers the generation of model files and the configuration of external services like email for OTP provides critical guidance for users setting up the project locally.
