import os
import requests  # Ensure requests is installed
import streamlit as st
import streamlit.components.v1 as components
import json
import hashlib
import uuid
import re
import random
import string
import smtplib
import urllib.parse
import html
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# --- CONFIGURATION ---
# PLEASE VERIFY THIS KEY IS ACTIVE
TMDB_API_KEY = "1a0e50c51630863ed6a140ec12e2bf36" 

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="G4 SOLUTION - Live Movie Recommender",
    layout="wide",
    page_icon="🎥"
)

# --- NEW IMPORT FOR TRAILER SEARCH ---
try:
    from youtube_search import YoutubeSearch
except ImportError:
    # Fallback to avoid crashing if library is missing
    YoutubeSearch = None 

# --- FILE PATHS ---
USER_DB_FILE = 'user_database.json'

# --- EMAIL CREDENTIALS ---
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "agyekumpeter123@gmail.com"
APP_PASSWORD = "lftr wrba rwsq blst"

# --- AUTHENTICATION FUNCTIONS ---
def load_db():
    if not os.path.exists(USER_DB_FILE): return {}
    try:
        with open(USER_DB_FILE, 'r') as f: return json.load(f)
    except: return {}

def save_db(data):
    with open(USER_DB_FILE, 'w') as f: json.dump(data, f, indent=4)

def hash_password(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_password_strength(password):
    if len(password) < 6: return False, "⚠️ Password must be at least 6 characters."
    if not re.search(r"\d", password): return False, "⚠️ Password must contain at least one number."
    if not re.search(r"[A-Z]", password): return False, "⚠️ Password must contain at least one uppercase letter."
    return True, "Valid"

def send_otp_email(receiver_email, otp):
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = receiver_email
        msg['Subject'] = "🔐 G4 SOLUTION: Password Reset OTP"
        body = f"""
        <html><body style="font-family: Arial;">
            <h2 style="color: #FF4B4B;">G4 Solution</h2>
            <p>Your OTP Code:</p>
            <div style="background: #f0f2f6; padding: 15px; border-radius: 10px; font-size: 24px; font-weight: bold;">{otp}</div>
        </body></html>
        """
        msg.attach(MIMEText(body, 'html'))
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, APP_PASSWORD)
        server.sendmail(SENDER_EMAIL, receiver_email, msg.as_string())
        server.quit()
        return True
    except Exception as e:
        return False

def register_user(username, email, password):
    is_strong, msg = check_password_strength(password)
    if not is_strong: return False, msg
    db = load_db()
    if username in db: return False, "⚠️ Username exists!"
    for d in db.values():
        if d.get('email') == email: return False, "⚠️ Email registered!"
    user_id = str(uuid.uuid4())[:8]
    db[username] = {'email': email, 'password': hash_password(password), 'user_id': user_id, 'history': []}
    save_db(db)
    return True, user_id

def authenticate_user(username, password):
    db = load_db()
    if username in db and db[username]['password'] == hash_password(password):
        return True, db[username]
    return False, None

def reset_password(username, new_password):
    db = load_db()
    if username in db:
        db[username]['password'] = hash_password(new_password)
        save_db(db)
        return True
    return False

def save_user_history(username, selected_movie, recommendations):
    db = load_db()
    if username in db:
        entry = {
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'selected_movie': selected_movie,
            'recommendations': [rec['title'] for rec in recommendations]
        }
        db[username]['history'].append(entry)
        save_db(db)

def clear_user_history(username):
    db = load_db()
    if username in db:
        db[username]['history'] = []
        save_db(db)
        return True
    return False

def delete_user_account(username):
    db = load_db()
    if username in db:
        del db[username]
        save_db(db)
        return True
    return False

# --- SESSION STATE ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'username' not in st.session_state: st.session_state.username = None
if 'recommendations' not in st.session_state: st.session_state.recommendations = None
if 'selected_movie_name' not in st.session_state: st.session_state.selected_movie_name = None
if 'fp_step' not in st.session_state: st.session_state.fp_step = 1

# --- LOGIN PAGE ---
def login_page():
    st.markdown("""
    <style>
        .stApp { background-color: #0e1117; color: white; }
        .glass-card { background: rgba(255,255,255,0.1); padding: 20px; border-radius: 15px; border: 1px solid rgba(255,75,75,0.5); text-align: center; }
        .title-text { color: #FF4B4B; font-weight: 900; font-size: 2rem; margin-bottom: 0; }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="glass-card"><p class="title-text">G4 SOLUTION CINEMA</p><p>Live API Movie Recommender</p></div>', unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])
        with tab1:
            l_user = st.text_input("Username", key="l_user")
            l_pass = st.text_input("Password", type="password", key="l_pass")
            if st.button("🚀 Enter App", type="primary", use_container_width=True):
                if authenticate_user(l_user, l_pass)[0]:
                    st.session_state.logged_in = True
                    st.session_state.username = l_user
                    st.rerun()
                else: st.error("Invalid credentials")
        
        with tab2:
            s_user = st.text_input("Username", key="s_user")
            s_email = st.text_input("Email", key="s_email")
            s_pass = st.text_input("Password", type="password", key="s_pass")
            if st.button("✨ Create Account", use_container_width=True):
                success, msg = register_user(s_user, s_email, s_pass)
                if success: 
                    st.success("Account created!")
                    st.session_state.logged_in = True
                    st.session_state.username = s_user
                    st.rerun()
                else: st.error(msg)

# --- MAIN APP ---
def main_app():
    # --- CSS ---
    st.markdown("""
        <style>
        header[data-testid="stHeader"] { background-color: #FF4B4B !important; }
        header[data-testid="stHeader"]::after {
            content: 'G4 SOLUTION - LIVE API'; color: white; font-weight: 900; 
            position: absolute; left: 50%; top: 50%; transform: translate(-50%, -50%);
        }
        .rec-card {
            background-color: #2b2b2b; background-size: cover; background-position: center;
            border: 1px solid rgba(255, 75, 75, 0.2); border-radius: 15px; height: 400px;
            position: relative; overflow: hidden; box-shadow: 0 4px 10px rgba(0,0,0,0.3);
            display: flex; flex-direction: column; justify-content: flex-end; margin-bottom: 10px;
        }
        .rec-card:hover { transform: translateY(-8px); border-color: #FF4B4B; }
        .card-content {
            padding: 15px; width: 100%;
            background: linear-gradient(to top, rgba(0,0,0,0.95) 0%, rgba(0,0,0,0.8) 70%, transparent 100%);
        }
        .movie-title { font-size: 1.1rem; font-weight: 900; color: white; margin-bottom: 5px; }
        .movie-genre { font-size: 0.75rem; color: #FF4B4B; font-weight: 700; text-transform: uppercase; }
        .movie-overview { font-size: 0.7rem; color: #ddd; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden; }
        .footer { text-align: center; padding: 20px; color: #888; border-top: 1px solid #333; margin-top: 50px; }
        </style>
    """, unsafe_allow_html=True)

    # --- API FUNCTIONS ---
    @st.cache_data
    def fetch_genres():
        """Get genre list from TMDb"""
        try:
            url = f"https://api.themoviedb.org/3/genre/movie/list?api_key={TMDB_API_KEY}&language=en-US"
            data = requests.get(url, timeout=5).json()
            return {g['id']: g['name'] for g in data['genres']}
        except: 
            return {}

    def search_movie(query):
        """Search for a movie by name on TMDb"""
        try:
            url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={urllib.parse.quote(query)}&page=1"
            return requests.get(url, timeout=5).json().get('results', [])
        except Exception as e: 
            st.error(f"Search Error: {e}")
            return []

    def get_tmdb_recommendations(movie_id):
        """Get recommendations with fallback to 'similar'"""
        results = []
        try:
            # 1. Try Recommendations Endpoint
            url = f"https://api.themoviedb.org/3/movie/{movie_id}/recommendations?api_key={TMDB_API_KEY}&language=en-US&page=1"
            data = requests.get(url, timeout=5).json()
            results = data.get('results', [])

            # 2. If empty, try Similar Endpoint (Fallback)
            if not results:
                url_sim = f"https://api.themoviedb.org/3/movie/{movie_id}/similar?api_key={TMDB_API_KEY}&language=en-US&page=1"
                data_sim = requests.get(url_sim, timeout=5).json()
                results = data_sim.get('results', [])

            # 3. Limit to top 5
            results = results[:5]
            
            # 4. Format Data
            formatted_recs = []
            genre_map = fetch_genres()
            
            for m in results:
                poster_path = m.get('poster_path')
                image = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else "https://via.placeholder.com/500x750?text=No+Image"
                
                # Get Genres safely
                g_ids = m.get('genre_ids', [])
                g_names = [genre_map.get(gid) for gid in g_ids if gid in genre_map]
                genre_str = " • ".join(g_names[:2]) if g_names else "Genre Unavailable"

                formatted_recs.append({
                    'id': m['id'],
                    'title': m['title'],
                    'info': m.get('overview', 'No overview available.'),
                    'image': image,
                    'genre': genre_str
                })
            return formatted_recs
        except Exception as e:
            st.error(f"Recommendation Error: {e}")
            return []

    # --- SIDEBAR ---
    with st.sidebar:
        st.markdown("<h2 style='text-align: center; color: #FF4B4B;'>G4 SOLUTION</h2>", unsafe_allow_html=True)
        st.success(f"👤 **{st.session_state.username}**")
        if st.button("🚪 Logout"):
            st.session_state.logged_in = False
            st.rerun()
        
        st.divider()
        
        # Help Dialog
        @st.dialog("📚 How to Use")
        def help_dialog():
            st.write("1. Type a movie name in the search bar.")
            st.write("2. Select the correct movie from the dropdown.")
            st.write("3. Click 'Get Recommendations'.")
            st.write("4. We fetch live data from TMDb to show you the best matches!")
            
        if st.button("❓ How it Works"):
            help_dialog()

        st.divider()
        st.write("### 📜 History")
        if st.button("🗑️ Clear History"):
            clear_user_history(st.session_state.username)
            st.rerun()

        with st.expander("View Recent"):
            db = load_db()
            history = db.get(st.session_state.username, {}).get('history', [])
            for h in reversed(history[-5:]):
                st.write(f"🎬 **{h['selected_movie']}**")
                st.caption(h['timestamp'])
                st.divider()

    # --- MAIN CONTENT ---
    st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>LIVE MOVIE RECOMMENDER</h1>", unsafe_allow_html=True)
    st.caption("Search for any movie globally, and we will fetch live recommendations from TMDb.")

    # 1. Search Bar
    search_query = st.text_input("🔍 Type a movie name (e.g., Avengers, Titanic, Matrix)", placeholder="Press Enter to search...")

    if search_query:
        # Fetch search results from API
        search_results = search_movie(search_query)
        
        if search_results:
            # Create a dictionary for the selectbox: "Movie Title (Year)" -> Movie Object
            movie_options = {}
            for m in search_results[:10]: # Limit to top 10 matches
                title = m['title']
                year = m.get('release_date', 'N/A')[:4]
                label = f"{title} ({year})"
                movie_options[label] = m # Store full movie object
            
            selected_label = st.selectbox("Select the exact movie:", list(movie_options.keys()))
            
            if st.button("✨ Get Recommendations", type="primary", use_container_width=True):
                selected_movie_obj = movie_options[selected_label]
                movie_id = selected_movie_obj['id']
                st.session_state.selected_movie_name = selected_movie_obj['title']
                
                with st.spinner("Fetching live data from TMDb..."):
                    recs = get_tmdb_recommendations(movie_id)
                    st.session_state.recommendations = recs
                    save_user_history(st.session_state.username, selected_label, recs)
        else:
            st.warning("No movies found with that name. Please check spelling.")

    # 2. Display Results
    if st.session_state.recommendations:
        st.divider()
        st.subheader(f"Because you liked '{st.session_state.selected_movie_name}':")
        
        cols = st.columns(5)
        for i, movie in enumerate(st.session_state.recommendations):
            with cols[i]:
                # Sanitize text
                clean_title = html.escape(str(movie['title']))
                clean_genre = html.escape(str(movie['genre']))
                clean_info = html.escape(str(movie['info']))

                card_html = f"""
                <div class="rec-card" style="background-image: url('{movie['image']}');">
                    <div class="card-content">
                        <div class="movie-title">{clean_title}</div>
                        <div class="movie-genre">{clean_genre}</div>
                        <div class="movie-overview">{clean_info}</div>
                    </div>
                </div>
                """
                st.markdown(card_html, unsafe_allow_html=True)
                
                # View Details Button
                @st.dialog("📽️ Movie Details", width="large")
                def show_details(m):
                    c1, c2 = st.columns([1, 2])
                    with c1: st.image(m['image'])
                    with c2:
                        st.header(m['title'])
                        st.caption(m['genre'])
                        st.write(m['info'])
                        
                        # Trailer Search
                        if YoutubeSearch:
                            try:
                                res = YoutubeSearch(f"{m['title']} trailer", max_results=1).to_dict()
                                if res: st.video(f"https://www.youtube.com/watch?v={res[0]['id']}")
                            except: st.error("Trailer not found")

                if st.button(f"👁️ View {i+1}", key=f"btn_{i}", use_container_width=True):
                    show_details(movie)
    
    # Message if recommendations came back empty
    elif st.session_state.recommendations is not None and len(st.session_state.recommendations) == 0:
        st.info("No similar recommendations found for this movie. Try a more popular title!")

    # --- FOOTER ---
    st.markdown("""
    <div class="footer">
        © 2025 <b>G4 SOLUTION</b> | Powered by TMDb API <br>
        <i>"Real-time recommendations, globally sourced."</i>
    </div>
    """, unsafe_allow_html=True)

# --- APP FLOW ---
if not st.session_state.logged_in:
    login_page()
else:
    main_app()
