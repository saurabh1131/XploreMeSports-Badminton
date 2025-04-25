import streamlit as st
import random
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import uuid
import json
import os
from collections import defaultdict
import hashlib
import pytz
import shutil

# llm setup
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage

# gdrive setup
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Configure logging
import logging
logging.basicConfig(level=logging.INFO)
logging.getLogger('googleapiclient.discovery_cache').setLevel(logging.ERROR)
logger = logging.getLogger(__name__)

# Set page configuration
st.set_page_config(
    page_title="Badminton AI-App by XploreMeAtSports🥇",
    page_icon="🏸",
    layout="wide"
)

# Initialize session state variables if they don't exist
if 'predefined_players' not in st.session_state:
    st.session_state.predefined_players = [
        {"id": str(uuid.uuid4()), "name": "Saurabh", "skill_level": 2, "games_played": 0, "wins": 0, "points_scored": 0},
        {"id": str(uuid.uuid4()), "name": "Golu", "skill_level": 4, "games_played": 0, "wins": 0, "points_scored": 0},
        {"id": str(uuid.uuid4()), "name": "Shraddha", "skill_level": 3, "games_played": 0, "wins": 0, "points_scored": 0},
        {"id": str(uuid.uuid4()), "name": "Pavan", "skill_level": 3, "games_played": 0, "wins": 0, "points_scored": 0},
        {"id": str(uuid.uuid4()), "name": "Lala", "skill_level": 3, "games_played": 0, "wins": 0, "points_scored": 0},
    ]

if 'temp_players' not in st.session_state:
    st.session_state.temp_players = []

if 'current_teams' not in st.session_state:
    st.session_state.current_teams = {"team_a": [], "team_b": []}

if 'match_history' not in st.session_state:
    st.session_state.match_history = []

if 'waiting_queue' not in st.session_state:
    st.session_state.waiting_queue = []

if 'player_rotation_history' not in st.session_state:
    st.session_state.player_rotation_history = {}

if 'data_updated' not in st.session_state:
    st.session_state.data_updated = False

# Admin and Super Admin authentication variables
if 'admin_password_hash' not in st.session_state:
    st.session_state.admin_password_hash = hashlib.sha256("admin123".encode()).hexdigest()

if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False

if 'admin_authenticated_time' not in st.session_state:
    st.session_state.admin_authenticated_time = None

if 'is_super_admin' not in st.session_state:
    st.session_state.is_super_admin = False

if 'super_admin_authenticated_time' not in st.session_state:
    st.session_state.super_admin_authenticated_time = None

if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'api_key_configured' not in st.session_state:
    st.session_state.api_key = "AIzaSyCvR-EJDDqU881df2CrjgDaQjejttoARXw"
    st.session_state.llm_model = "gemini-2.0-flash"
    st.session_state.api_key_configured = True

# Super Admin password from environment variable
SUPER_ADMIN_PASSWORD = os.getenv('SUPER_ADMIN_PASSWORD', 'SuperAdmin123!')  # Fallback for local testing
SUPER_ADMIN_PASSWORD_HASH = hashlib.sha256(SUPER_ADMIN_PASSWORD.encode()).hexdigest()

# Utility functions
def load_data():
    """Load data from JSON files if they exist"""
    if os.path.exists('badminton_data.json'):
        with open('badminton_data.json', 'r') as f:
            data = json.load(f)
            st.session_state.predefined_players = data.get('predefined_players', st.session_state.predefined_players)
            st.session_state.match_history = data.get('match_history', st.session_state.match_history)
            st.session_state.player_rotation_history = data.get('player_rotation_history', st.session_state.player_rotation_history)
            if 'admin_password_hash' in data:
                st.session_state.admin_password_hash = data['admin_password_hash']

def save_data():
    """Save data to JSON file"""
    data = {
        'predefined_players': st.session_state.predefined_players,
        'match_history': st.session_state.match_history,
        'player_rotation_history': st.session_state.player_rotation_history,
        'admin_password_hash': st.session_state.admin_password_hash
    }
    with open('badminton_data.json', 'w') as f:
        json.dump(data, f)
    st.session_state.data_updated = True

def log_chat_question_answer(question, answer):
    """Log the question and answer to a JSON file"""
    chat_log_file = 'chat_history.json'
    ist = pytz.timezone('Asia/Kolkata')
    timestamp = datetime.datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S")
    log_entry = {
        "timestamp": timestamp,
        "question": question,
        "answer": answer
    }
    
    if os.path.exists(chat_log_file):
        with open(chat_log_file, 'r') as f:
            try:
                logs = json.load(f)
            except json.JSONDecodeError:
                logs = []
    else:
        logs = []
    
    logs.append(log_entry)
    with open(chat_log_file, 'w') as f:
        json.dump(logs, f, indent=2)

def get_player_by_id(player_id):
    """Get player object by ID"""
    for player in st.session_state.predefined_players:
        if player["id"] == player_id:
            return player
    for player in st.session_state.temp_players:
        if player["id"] == player_id:
            return player
    return None

def update_player_stats(player_id, points, is_winner):
    """Update a player's statistics by ID"""
    for i, player in enumerate(st.session_state.predefined_players):
        if player["id"] == player_id:
            st.session_state.predefined_players[i]["games_played"] += 1
            st.session_state.predefined_players[i]["points_scored"] += points
            if is_winner:
                st.session_state.predefined_players[i]["wins"] += 1
            return True
    
    for i, player in enumerate(st.session_state.temp_players):
        if player["id"] == player_id:
            st.session_state.temp_players[i]["games_played"] += 1
            st.session_state.temp_players[i]["points_scored"] += points
            if is_winner:
                st.session_state.temp_players[i]["wins"] += 1
            return True
    
    return False

def get_all_available_players():
    """Get list of all available players (predefined + temporary)"""
    return st.session_state.predefined_players + st.session_state.temp_players

def generate_random_teams(players, previous_teams=None):
    """Generate random teams with consideration for player sitting out history"""
    if len(players) < 4:
        return None, None
    
    waiting_priority = []
    for player in players:
        sat_out_count = st.session_state.player_rotation_history.get(player["id"], {}).get("sat_out_count", 0)
        waiting_priority.append((player, sat_out_count))
    
    waiting_priority.sort(key=lambda x: x[1], reverse=True)
    selected_players = [p[0] for p in waiting_priority[:4]]
    waiting_players = [p[0] for p in waiting_priority[4:]]
    
    random.shuffle(selected_players)
    team_a = selected_players[:2]
    team_b = selected_players[2:4]
    
    for player in selected_players:
        if player["id"] not in st.session_state.player_rotation_history:
            st.session_state.player_rotation_history[player["id"]] = {"sat_out_count": 0, "consecutive_plays": 0}
        st.session_state.player_rotation_history[player["id"]]["consecutive_plays"] += 1
    
    for player in waiting_players:
        if player["id"] not in st.session_state.player_rotation_history:
            st.session_state.player_rotation_history[player["id"]] = {"sat_out_count": 0, "consecutive_plays": 0}
        st.session_state.player_rotation_history[player["id"]]["sat_out_count"] += 1
        st.session_state.player_rotation_history[player["id"]]["consecutive_plays"] = 0
    
    st.session_state.waiting_queue = waiting_players
    return team_a, team_b

def record_match_result(team_a, team_b, score_a, score_b, notes=""):
    """Record match results, update player statistics, and push to Git"""
    match_id = str(uuid.uuid4())
    ist = pytz.timezone('Asia/Kolkata')
    timestamp = datetime.datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S")
    winning_team = "A" if score_a > score_b else "B"
    
    for player in team_a:
        update_player_stats(player["id"], score_a, winning_team == "A")
    for player in team_b:
        update_player_stats(player["id"], score_b, winning_team == "B")
    
    match_record = {
        "id": match_id,
        "timestamp": timestamp,
        "team_a": [p["id"] for p in team_a],
        "team_b": [p["id"] for p in team_b],
        "score_a": score_a,
        "score_b": score_b,
        "winning_team": winning_team,
        "notes": notes
    }
    
    st.session_state.match_history.append(match_record)
    save_data()
    push_to_gdrive(match_history=True)
    return match_record

def verify_admin_password(password):
    """Verify admin password"""
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    return password_hash == st.session_state.admin_password_hash

def check_admin_session_timeout():
    """Check if admin session has timed out (after 30 minutes)"""
    if st.session_state.admin_authenticated_time:
        elapsed_time = datetime.datetime.now() - st.session_state.admin_authenticated_time
        if elapsed_time.total_seconds() > 1800:
            st.session_state.is_admin = False
            st.session_state.admin_authenticated_time = None
            return True
    return False

def verify_super_admin_password(password):
    """Verify super admin password"""
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    return password_hash == SUPER_ADMIN_PASSWORD_HASH

def check_super_admin_session_timeout():
    """Check if super admin session has timed out (after 30 minutes)"""
    if st.session_state.super_admin_authenticated_time:
        elapsed_time = datetime.datetime.now() - st.session_state.super_admin_authenticated_time
        if elapsed_time.total_seconds() > 1800:
            st.session_state.is_super_admin = False
            st.session_state.super_admin_authenticated_time = None
            return True
    return False

# Admin and Super Admin authentication component
def admin_authentication():
    """Admin and Super Admin login/logout component"""
    with st.sidebar:
        st.header("Admin Panel")
        
        # Check admin session timeout
        if st.session_state.is_admin:
            if check_admin_session_timeout():
                st.warning("Admin session has timed out. Please login again.")
        
        # Admin login/logout
        if st.session_state.is_admin:
            st.success("Logged in as Admin")
            if st.button("Logout", key="admin_logout"):
                st.session_state.is_admin = False
                st.session_state.admin_authenticated_time = None
                st.rerun()
            
            with st.expander("Admin Settings"):
                st.subheader("Change Admin Password")
                current_password = st.text_input("Current Password", type="password", key="current_pass")
                new_password = st.text_input("New Password", type="password", key="new_pass")
                confirm_password = st.text_input("Confirm New Password", type="password", key="confirm_pass")
                
                if st.button("Change Password", key="change_admin_password"):
                    if not verify_admin_password(current_password):
                        st.error("Current password is incorrect")
                    elif new_password != confirm_password:
                        st.error("New passwords do not match")
                    elif len(new_password) < 6:
                        st.error("New password must be at least 6 characters")
                    else:
                        st.session_state.admin_password_hash = hashlib.sha256(new_password.encode()).hexdigest()
                        save_data()
                        st.success("Password changed successfully")
        else:
            st.info("Login to access admin features")
            admin_password = st.text_input("Admin Password", type="password", key="admin_pass")
            if st.button("Login", key="admin_login"):
                if verify_admin_password(admin_password):
                    st.session_state.is_admin = True
                    st.session_state.admin_authenticated_time = datetime.datetime.now()
                    st.success("Login successful")
                    st.rerun()
                else:
                    st.error("Incorrect password")

        # Super Admin panel (below Admin panel)
        st.header("Super Admin Panel")
        if st.session_state.is_super_admin:
            if check_super_admin_session_timeout():
                st.warning("Super Admin session has timed out. Please login again.")
        
        if st.session_state.is_super_admin:
            st.success("Logged in as Super Admin")
            if st.button("Logout", key="super_admin_logout"):
                st.session_state.is_super_admin = False
                st.session_state.super_admin_authenticated_time = None
                st.rerun()
            
            with st.expander("Super Admin Settings"):
                st.subheader("Restore Backup Files")
                allowed_files = {"service-account-key.json", "chat_history.json", "badminton_data.json"}
                uploaded_files = st.file_uploader(
                    "Upload backup files",
                    type=["json"],
                    accept_multiple_files=True,
                    help="Upload service-account-key.json, chat_history.json, or badminton_data.json to restore."
                )
                
                if uploaded_files:
                    for uploaded_file in uploaded_files:
                        if uploaded_file.name not in allowed_files:
                            st.error(f"Invalid file name. Allowed files: {', '.join(allowed_files)}")
                            continue
                        file_path = os.path.join(os.getcwd(), uploaded_file.name)
                        if os.path.exists(file_path):
                            backup_path = f"{file_path}.bak"
                            shutil.copy2(file_path, backup_path)
                            logger.info(f"Backed up {file_path} to {backup_path}")
                        with open(file_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        st.success(f"Restored {uploaded_file.name} to {file_path}")
                        logger.info(f"Restored {uploaded_file.name} to {file_path}")
                        # Reload data if badminton_data.json is restored
                        if uploaded_file.name == "badminton_data.json":
                            load_data()
                
                if st.button("Sync Restored Files to Google Drive", key="sync_to_gdrive"):
                    success = upload_to_drive()
                    st.success("Files synced to Google Drive!" if success else "Sync failed. Check logs.")
        else:
            st.info("Login to access super admin features")
            super_admin_password = st.text_input("Super Admin Password", type="password", key="super_admin_pass")
            if st.button("Login", key="super_admin_login"):
                if verify_super_admin_password(super_admin_password):
                    st.session_state.is_super_admin = True
                    st.session_state.super_admin_authenticated_time = datetime.datetime.now()
                    st.success("Super Admin login successful")
                    st.rerun()
                else:
                    st.error("Incorrect password")

# App Components
def header_section():
    """App header section"""
    st.title("✨XploreMeAtSports: Badminton🏸")
    st.markdown("Manage your badminton matches, teams, and stats!")

def footer_section():
    """App Footer section"""
    st.markdown(
        """
        <style>
            #footer {
                position: fixed;
                bottom: 10px;
                left: 50%;
                transform: translateX(-50%);
                font-size: 14px;
                color: gray;
                text-align: center;
                z-index: 1000;
            }
        </style>
        <div id="footer">
            Built by <b>XploreMe@Sports</b> with 🧡
        </div>
        """,
        unsafe_allow_html=True
    )

def player_management_section():
    """Player management section"""
    st.header("Player Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Predefined Players")
        df_predefined = pd.DataFrame(st.session_state.predefined_players)
        if not df_predefined.empty:
            columns_order = ["name", "skill_level", "games_played", "wins", "points_scored"]
            display_columns = [col for col in columns_order if col in df_predefined.columns]
            st.dataframe(df_predefined[display_columns], use_container_width=True)
        
        with st.expander("Add New Predefined Player"):
            new_player_name = st.text_input("Player Name", key="new_predefined_name")
            new_player_skill = st.slider("Skill Level (1-5)", 1, 5, 3, key="new_predefined_skill")
            add_button = st.button("Add Player", key="add_predefined", disabled=not st.session_state.is_admin)
            if not st.session_state.is_admin:
                st.info("Admin login required to add players")
            if add_button:
                if new_player_name:
                    new_player = {
                        "id": str(uuid.uuid4()),
                        "name": new_player_name,
                        "skill_level": new_player_skill,
                        "games_played": 0,
                        "wins": 0,
                        "points_scored": 0
                    }
                    st.session_state.predefined_players.append(new_player)
                    save_data()
                    st.success(f"Added {new_player_name} to predefined players!")
                    st.rerun()
                else:
                    st.error("Please enter a player name")
    
    with col2:
        st.subheader("Temporary Players")
        df_temp = pd.DataFrame(st.session_state.temp_players)
        if not df_temp.empty:
            columns_order = ["name", "skill_level", "games_played", "wins", "points_scored"]
            display_columns = [col for col in columns_order if col in df_temp.columns]
            st.dataframe(df_temp[display_columns], use_container_width=True)
        else:
            st.info("No temporary players added yet")
        
        with st.expander("Add New Temporary Player"):
            new_temp_name = st.text_input("Player Name", key="new_temp_name")
            new_temp_skill = st.slider("Skill Level (1-5)", 1, 5, 3, key="new_temp_skill")
            add_temp_button = st.button("Add Temporary Player", key="add_temp", disabled=not st.session_state.is_admin)
            if not st.session_state.is_admin:
                st.info("Admin login required to add players")
            if add_temp_button:
                if new_temp_name:
                    new_player = {
                        "id": str(uuid.uuid4()),
                        "name": new_temp_name,
                        "skill_level": new_temp_skill,
                        "games_played": 0,
                        "wins": 0,
                        "points_scored": 0
                    }
                    st.session_state.temp_players.append(new_player)
                    st.success(f"Added {new_temp_name} as temporary player!")
                    st.rerun()
                else:
                    st.error("Please enter a player name")
        
        clear_button = st.button("Clear All Temporary Players", key="clear_temp", disabled=not st.session_state.is_admin)
        if not st.session_state.is_admin:
            st.info("Admin login required to clear players")
        if clear_button:
            st.session_state.temp_players = []
            st.success("Cleared all temporary players!")
            st.rerun()

def team_formation_section():
    """Team formation and match management section"""
    st.header("Team Formation")
    
    all_players = get_all_available_players()
    player_names = [p["name"] for p in all_players]
    
    st.subheader("Select Available Players")
    available_players = []
    num_cols = 3
    cols = st.columns(num_cols)
    for i, player in enumerate(all_players):
        col_idx = i % num_cols
        with cols[col_idx]:
            is_selected = st.checkbox(f"{player['name']} (Skill: {player['skill_level']})", key=f"player_{player['id']}")
            if is_selected:
                available_players.append(player)
    
    st.subheader("Team Generation")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Generate Random Teams", key="gen_teams", disabled=len(available_players) < 4):
            team_a, team_b = generate_random_teams(available_players)
            if team_a and team_b:
                st.session_state.current_teams = {"team_a": team_a, "team_b": team_b}
                st.success("Teams generated successfully!")
                st.rerun()
            else:
                st.error("Not enough players to form two teams. Need at least 4 players.")
    
    with col2:
        if st.button("Rematch with Same Teams", key="rematch", disabled=not (st.session_state.current_teams["team_a"] and st.session_state.current_teams["team_b"])):
            st.success("Teams kept for rematch!")
    
    if st.session_state.current_teams["team_a"] and st.session_state.current_teams["team_b"]:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Team A")
            for player in st.session_state.current_teams["team_a"]:
                st.write(f"• {player['name']} (Skill: {player['skill_level']})")
        with col2:
            st.subheader("Team B")
            for player in st.session_state.current_teams["team_b"]:
                st.write(f"• {player['name']} (Skill: {player['skill_level']})")
    
    if st.session_state.waiting_queue:
        st.subheader("Players Waiting")
        waiting_text = ", ".join([p["name"] for p in st.session_state.waiting_queue])
        st.info(f"Waiting: {waiting_text}")

def match_recording_section():
    """Match recording section"""
    st.header("Record Match Results")
    
    if not (st.session_state.current_teams["team_a"] and st.session_state.current_teams["team_b"]):
        st.warning("Generate teams first before recording match results.")
        return
    
    col1, col2, col3 = st.columns([2, 1, 2])
    with col1:
        st.subheader("Team A")
        for player in st.session_state.current_teams["team_a"]:
            st.write(f"• {player['name']}")
        score_a = st.number_input("Score Team A", min_value=0, value=0, step=1, key="score_a", disabled=not st.session_state.is_admin)
    with col2:
        st.markdown("<h2 style='text-align: center;'>VS</h2>", unsafe_allow_html=True)
    with col3:
        st.subheader("Team B")
        for player in st.session_state.current_teams["team_b"]:
            st.write(f"• {player['name']}")
        score_b = st.number_input("Score Team B", min_value=0, value=0, step=1, key="score_b", disabled=not st.session_state.is_admin)
    
    match_notes = st.text_area("Match Notes (optional)", key="match_notes", disabled=not st.session_state.is_admin)
    record_button = st.button("Record Match Result", key="record_match", disabled=not st.session_state.is_admin)
    if not st.session_state.is_admin:
        st.info("Admin login required to record match results")
    if record_button:
        if score_a == 0 and score_b == 0:
            st.error("Please enter valid scores for the match.")
        else:
            record_match_result(
                st.session_state.current_teams["team_a"],
                st.session_state.current_teams["team_b"],
                score_a,
                score_b,
                match_notes
            )
            st.success("Match recorded successfully!")
            st.rerun()

def statistics_section():
    """Statistics and analytics section"""
    st.header("Statistics & Analytics")
    tab1, tab2, tab3 = st.tabs(["Player Stats", "Match History", "Team Analysis"])
    
    with tab1:
        st.subheader("Player Performance")
        all_players = st.session_state.predefined_players + st.session_state.temp_players
        if all_players:
            df_players = pd.DataFrame(all_players)
            df_players["win_rate"] = df_players.apply(
                lambda x: round((x["wins"] / x["games_played"]) * 100, 1) if x["games_played"] > 0 else 0, axis=1
            )
            df_players["avg_points_per_game"] = df_players.apply(
                lambda x: round(x["points_scored"] / x["games_played"], 1) if x["games_played"] > 0 else 0, axis=1
            )
            columns_to_display = ["name", "games_played", "wins", "win_rate", "points_scored", "avg_points_per_game", "skill_level"]
            st.dataframe(df_players[columns_to_display].sort_values(by="win_rate", ascending=False), use_container_width=True)
            if not df_players.empty and df_players["games_played"].sum() > 0:
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("Win Rate by Player")
                    fig, ax = plt.subplots(figsize=(10, 6))
                    active_players = df_players[df_players["games_played"] > 0].sort_values("win_rate", ascending=False)
                    sns.barplot(x="name", y="win_rate", data=active_players, ax=ax)
                    plt.xticks(rotation=45, ha="right")
                    plt.ylabel("Win Rate (%)")
                    plt.xlabel("")
                    plt.tight_layout()
                    st.pyplot(fig)
                with col2:
                    st.subheader("Games Played vs Wins")
                    fig, ax = plt.subplots(figsize=(10, 6))
                    df_melt = pd.melt(
                        active_players,
                        id_vars=["name"],
                        value_vars=["games_played", "wins"],
                        var_name="Metric",
                        value_name="Count"
                    )
                    sns.barplot(x="name", y="Count", hue="Metric", data=df_melt, ax=ax)
                    plt.xticks(rotation=45, ha="right")
                    plt.tight_layout()
                    st.pyplot(fig)
        else:
            st.info("No player statistics available yet.")
    
    with tab2:
        st.subheader("Match History")
        if st.session_state.match_history:
            match_data = []
            for match in st.session_state.match_history:
                team_a_names = [get_player_by_id(pid)["name"] for pid in match["team_a"] if get_player_by_id(pid)]
                team_b_names = [get_player_by_id(pid)["name"] for pid in match["team_b"] if get_player_by_id(pid)]
                match_data.append({
                    "Match ID": match["id"][:8],
                    "Date": match["timestamp"],
                    "Team A": " & ".join(team_a_names),
                    "Team B": " & ".join(team_b_names),
                    "Score": f"{match['score_a']} - {match['score_b']}",
                    "Winner": f"Team {match['winning_team']}",
                    "Notes": match["notes"]
                })
            df_matches = pd.DataFrame(match_data)
            st.dataframe(df_matches, use_container_width=True)
            st.subheader("Match Score Distribution")
            fig, ax = plt.subplots(figsize=(10, 6))
            scores_data = []
            for match in st.session_state.match_history:
                scores_data.append({
                    "Match": f"Match {len(scores_data) + 1}",
                    "Team A": match["score_a"],
                    "Team B": match["score_b"]
                })
            df_scores = pd.DataFrame(scores_data)
            df_melt = pd.melt(
                df_scores,
                id_vars=["Match"],
                value_vars=["Team A", "Team B"],
                var_name="Team",
                value_name="Score"
            )
            sns.barplot(x="Match", y="Score", hue="Team", data=df_melt, ax=ax)
            plt.xticks(rotation=45, ha="right")
            plt.tight_layout()
            st.pyplot(fig)
        else:
            st.info("No match history available yet.")
    
    with tab3:
        st.subheader("Team Analysis")
        if st.session_state.match_history:
            team_stats = defaultdict(lambda: {"matches": 0, "wins": 0, "total_points": 0})
            for match in st.session_state.match_history:
                team_a_key = "&".join(sorted([get_player_by_id(pid)["name"] for pid in match["team_a"] if get_player_by_id(pid)]))
                team_stats[team_a_key]["matches"] += 1
                team_stats[team_a_key]["total_points"] += match["score_a"]
                if match["winning_team"] == "A":
                    team_stats[team_a_key]["wins"] += 1
                team_b_key = "&".join(sorted([get_player_by_id(pid)["name"] for pid in match["team_b"] if get_player_by_id(pid)]))
                team_stats[team_b_key]["matches"] += 1
                team_stats[team_b_key]["total_points"] += match["score_b"]
                if match["winning_team"] == "B":
                    team_stats[team_b_key]["wins"] += 1
            team_data = []
            for team_key, stats in team_stats.items():
                win_rate = round((stats["wins"] / stats["matches"]) * 100, 1) if stats["matches"] > 0 else 0
                avg_points = round(stats["total_points"] / stats["matches"], 1) if stats["matches"] > 0 else 0
                team_data.append({
                    "Team": team_key,
                    "Matches": stats["matches"],
                    "Wins": stats["wins"],
                    "Win Rate (%)": win_rate,
                    "Avg Points": avg_points
                })
            df_teams = pd.DataFrame(team_data)
            st.dataframe(df_teams.sort_values(by="Win Rate (%)", ascending=False), use_container_width=True)
            st.subheader("Team Win Rates")
            fig, ax = plt.subplots(figsize=(10, 6))
            df_teams_sorted = df_teams.sort_values(by="Win Rate (%)", ascending=False)
            if len(df_teams_sorted) > 10:
                df_teams_sorted = df_teams_sorted.head(10)
            sns.barplot(x="Team", y="Win Rate (%)", data=df_teams_sorted, ax=ax)
            plt.xticks(rotation=45, ha="right")
            plt.tight_layout()
            st.pyplot(fig)
        else:
            st.info("No team statistics available yet.")

# Chatbot section
def chatbot_section():
    """Chatbot interaction section"""
    st.header("BadmintonBuddy AI-Assistant 🤖")
    st.write("Ask questions about your badminton data, players, statistics, and match history!")
    
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    user_query = st.chat_input("Ask something about the badminton data...")
    
    if user_query:
        st.session_state.chat_history.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.write(user_query)
        
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("Thinking...")
            try:
                response_content = process_query(user_query)
                log_chat_question_answer(user_query, response_content)
                message_placeholder.markdown(response_content)
                st.session_state.chat_history.append({"role": "assistant", "content": response_content})
                push_to_gdrive(chat_history=True)
            except Exception as e:
                message_placeholder.markdown(f"Error processing your query: {str(e)}")
                st.error("Failed to get a response from the model. Please check the logs.")

def process_query(user_query):
    """Process the user query with the LLM"""
    try:
        try:
            with open('badminton_data.json', 'r', encoding='utf-8') as file:
                badminton_data = json.load(file)
        except FileNotFoundError:
            badminton_data = "Error: The badminton_data.json file was not found. Also, please recommend that the user play some matches."
        except json.JSONDecodeError:
            return "Error: Invalid JSON format in badminton_data.json."
        
        last_five_questions = []
        user_messages = [msg for msg in reversed(st.session_state.chat_history) if msg["role"] == "user"]
        for i in range(min(5, len(user_messages))):
            last_five_questions.append(user_messages[i]["content"])
        
        prompt_template = ChatPromptTemplate.from_template(
            """You are BadmintonBuddy, a super chill and fun badminton assistant who loves to chat about the game like a best friend! Your main job is to answer questions about the provided badminton data in JSON format, but you can also tackle general badminton topics (like rules or strategies) or even off-topic stuff if it makes sense. Here’s how to roll:

1. **Figure Out the Vibe**:
   - Check if the user’s question is about the JSON data, general badminton stuff, or something totally random.
   - Use the last 5 user questions to understand the conversation context and tailor your response accordingly.

2. **If It’s About the JSON Data**:
   - Dig into the JSON to get the scoop (think players, matches, stats, etc.).
   - Answer the question in a fun, clear way—use bullet points or headings if it helps!
   - If the question’s a bit vague (like “who’s the best player?”), assume something reasonable (maybe most wins?) and explain your thinking.
   - Handle weird cases like a pro:
     - If the JSON’s empty or missing stuff, say so and give what you can.
     - If the question asks for something not in the JSON, let them know and maybe throw in a general answer.
     - If the question’s confusing, say why and suggest a different way to look at it.

3. **If It’s Badminton-Related but Not JSON Data**:
   - Share your badminton know-how (rules, tips, fun facts) in a friendly way.
   - Mention that you’re going off general knowledge, not the data.

4. **If It’s Not About Badminton**:
   - Be nice and say your main gig is badminton, but try to give a quick, helpful answer if you can.
   - If it’s way out of your league, suggest tweaking the question to something badminton-related.

5. **Keep It Short but Sweet**:
   - Don’t ramble, but make sure you cover what they asked. Think of it like a quick chat over a shuttlecock!

6. **Be a Buddy, Not a Robot**:
   - Talk like you’re hanging out with a friend—casual, fun, and maybe a little goofy!
   - If the user’s question has a playful tone (like mentioning a “lucky racket” or “comeback queen”), lean into it with some humor—maybe throw in a silly suggestion or a fun emoji. 🏸
   - Even for serious questions, keep it light and engaging, like you’re cheering them on.

**JSON Data**:
{badminton_data}

**Last 5 User Questions**:
{last_questions}

**User's Current Question**:
{user_ask}

Give your answer in a clear, buddy-like way, using headings or bullet points if needed, and toss in some fun where it fits!""")
        
        model = ChatGoogleGenerativeAI(
            model=st.session_state.llm_model,
            google_api_key=st.session_state.api_key,
            temperature=0.25
        )
        
        prompt = prompt_template.format(
            badminton_data=json.dumps(badminton_data, indent=2),
            last_questions="\n".join(last_five_questions) if last_five_questions else "No previous questions.",
            user_ask=user_query
        )
        message = HumanMessage(content=prompt)
        response = model.invoke([message])  # Updated to use invoke instead of __call__
        
        return response.content
    except Exception as e:
        return f"An error occurred: {str(e)}"

def get_drive_service():
    """Get authenticated Google Drive service using a service account."""
    try:
        logger.info("Loading service account credentials")
        SCOPES = ['https://www.googleapis.com/auth/drive.file']
        
        credentials_json = os.getenv('GOOGLE_CREDENTIALS')
        if credentials_json:
            logger.info("Using credentials from GOOGLE_CREDENTIALS environment variable")
            creds = service_account.Credentials.from_service_account_info(
                json.loads(credentials_json), scopes=SCOPES)
        else:
            SERVICE_ACCOUNT_FILE = os.getenv('GOOGLE_SERVICE_ACCOUNT_KEY_PATH', 'service-account-key.json')
            logger.info(f"Using service account key file: {SERVICE_ACCOUNT_FILE}")
            if not os.path.exists(SERVICE_ACCOUNT_FILE):
                logger.error(f"Service account key file not found: {SERVICE_ACCOUNT_FILE}")
                return None
            creds = service_account.Credentials.from_service_account_file(
                SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        
        logger.info("Building Google Drive service")
        drive_service = build('drive', 'v3', credentials=creds, cache_discovery=False)
        logger.info("Google Drive service created successfully")
        return drive_service
    
    except Exception as e:
        logger.error(f"Error building Drive service: {str(e)}")
        return None

def upload_to_drive(chat_history=False, match_history=False):
    """Upload badminton_data.json and chat_history.json to Google Drive."""
    try:
        if chat_history:
            files_to_upload = ["chat_history.json"]
        elif match_history:
            files_to_upload = ["badminton_data.json"]
        else:
            files_to_upload = ["badminton_data.json", "chat_history.json"]
        
        files_to_upload = [f for f in files_to_upload if os.path.exists(f)]
        if not files_to_upload:
            logger.warning("No output files found to upload")
            return False
        
        drive_service = get_drive_service()
        if not drive_service:
            logger.error("Failed to get Google Drive service")
            return False
        
        ist = pytz.timezone('Asia/Kolkata')
        timestamp = datetime.datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S")
        target_folder_id = '1u5w1ESII4eCx9CE6LGp-ehPJd3rTriZf'
        
        uploaded_files = []
        for file_path in files_to_upload:
            file_name = os.path.basename(file_path)
            query = f"name = '{file_name}' and trashed = false"
            
            response = drive_service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name, parents)'
            ).execute()
            
            file_metadata = {
                'name': file_name,
                'parents': [target_folder_id]
            }
            
            media = MediaFileUpload(
                file_path,
                resumable=True
            )
            
            if response.get('files'):
                file_id = response['files'][0]['id']
                current_parents = response['files'][0].get('parents', [])
                
                if target_folder_id not in current_parents:
                    logger.info(f"Moving {file_name} to target folder")
                    file = drive_service.files().update(
                        fileId=file_id,
                        addParents=target_folder_id,
                        removeParents=','.join(current_parents),
                        media_body=media,
                        fields='id, parents'
                    ).execute()
                else:
                    logger.info(f"Updating existing file: {file_name}")
                    file = drive_service.files().update(
                        fileId=file_id,
                        media_body=media,
                        fields='id'
                    ).execute()
            else:
                logger.info(f"Uploading new file: {file_name}")
                file = drive_service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id'
                ).execute()
            
            uploaded_files.append(file_name)
        
        logger.info(f"Successfully uploaded {', '.join(uploaded_files)} to Google Drive")
        return True
    except Exception as e:
        logger.error(f"Google Drive upload error: {str(e)}")
        return False

def push_to_gdrive(chat_history=False, match_history=False):
    """Push data to Google Drive"""
    try:
        upload_to_drive(chat_history=chat_history, match_history=match_history)
    except Exception as e:
        logger.error(f"Failed to upload to GDrive: {str(e)}")

def main():
    """Main app"""
    load_data()
    if st.session_state.data_updated:
        st.session_state.data_updated = False
        st.rerun()
    
    admin_authentication()
    header_section()
    footer_section()
    
    tab1, tab2, tab3, tab4 = st.tabs(["Players", "Team Formation", "Match Recording", "Statistics"])
    with tab1:
        player_management_section()
        chatbot_section()
    with tab2:
        team_formation_section()
    with tab3:
        match_recording_section()
    with tab4:
        statistics_section()

if __name__ == "__main__":
    main()
