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

# Set page configuration
st.set_page_config(
    page_title="XploreMe@Sports - Badminton 🏸",
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

# Admin authentication variables
if 'admin_password_hash' not in st.session_state:
    # Default admin password is "admin123" - should be changed in production
    st.session_state.admin_password_hash = hashlib.sha256("admin123".encode()).hexdigest()

if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False

if 'admin_authenticated_time' not in st.session_state:
    st.session_state.admin_authenticated_time = None

# Utility functions
def load_data():
    """Load data from JSON files if they exist"""
    if os.path.exists('badminton_data.json'):
        with open('badminton_data.json', 'r') as f:
            data = json.load(f)
            st.session_state.predefined_players = data.get('predefined_players', st.session_state.predefined_players)
            st.session_state.match_history = data.get('match_history', st.session_state.match_history)
            st.session_state.player_rotation_history = data.get('player_rotation_history', st.session_state.player_rotation_history)
            # Also load admin password if it exists
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
    # Set flag to indicate data was updated
    st.session_state.data_updated = True

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
    # First check predefined players
    for i, player in enumerate(st.session_state.predefined_players):
        if player["id"] == player_id:
            st.session_state.predefined_players[i]["games_played"] += 1
            st.session_state.predefined_players[i]["points_scored"] += points
            if is_winner:
                st.session_state.predefined_players[i]["wins"] += 1
            return True
    
    # Then check temporary players
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
    
    # Prioritize players who sat out in previous matches
    waiting_priority = []
    for player in players:
        sat_out_count = st.session_state.player_rotation_history.get(player["id"], {}).get("sat_out_count", 0)
        waiting_priority.append((player, sat_out_count))
    
    # Sort by sat_out_count (descending)
    waiting_priority.sort(key=lambda x: x[1], reverse=True)
    
    # Take first 4 players with highest sat_out_count
    selected_players = [p[0] for p in waiting_priority[:4]]
    waiting_players = [p[0] for p in waiting_priority[4:]]
    
    # Randomly divide the 4 players into 2 teams
    random.shuffle(selected_players)
    team_a = selected_players[:2]
    team_b = selected_players[2:4]
    
    # Update player rotation history
    for player in selected_players:
        if player["id"] not in st.session_state.player_rotation_history:
            st.session_state.player_rotation_history[player["id"]] = {"sat_out_count": 0, "consecutive_plays": 0}
        
        st.session_state.player_rotation_history[player["id"]]["consecutive_plays"] += 1
    
    for player in waiting_players:
        if player["id"] not in st.session_state.player_rotation_history:
            st.session_state.player_rotation_history[player["id"]] = {"sat_out_count": 0, "consecutive_plays": 0}
        
        st.session_state.player_rotation_history[player["id"]]["sat_out_count"] += 1
        st.session_state.player_rotation_history[player["id"]]["consecutive_plays"] = 0
    
    # Store waiting players for next match consideration
    st.session_state.waiting_queue = waiting_players
    
    return team_a, team_b

def record_match_result(team_a, team_b, score_a, score_b, notes=""):
    """Record match results and update player statistics"""
    match_id = str(uuid.uuid4())
    
    # Get current time in IST
    ist = pytz.timezone('Asia/Kolkata')
    timestamp = datetime.datetime.now(ist).strftime("%Y-%m-%d %H:%M:%S")
    
    # Determine winning team
    winning_team = "A" if score_a > score_b else "B"
    
    # Update player statistics using dedicated function
    for player in team_a:
        update_player_stats(player["id"], score_a, winning_team == "A")
    
    for player in team_b:
        update_player_stats(player["id"], score_b, winning_team == "B")
    
    # Create match record
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
    return match_record

def verify_admin_password(password):
    """Verify admin password"""
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    return password_hash == st.session_state.admin_password_hash

def check_admin_session_timeout():
    """Check if admin session has timed out (after 30 minutes)"""
    if st.session_state.admin_authenticated_time:
        elapsed_time = datetime.datetime.now() - st.session_state.admin_authenticated_time
        # If more than 30 minutes have passed, log out admin
        if elapsed_time.total_seconds() > 1800:  # 30 minutes = 1800 seconds
            st.session_state.is_admin = False
            st.session_state.admin_authenticated_time = None
            return True
    return False

# Admin authentication component
def admin_authentication():
    """Admin login/logout component"""
    # Check if admin session has timed out
    if st.session_state.is_admin:
        if check_admin_session_timeout():
            st.warning("Admin session has timed out. Please login again.")
    
    # Create sidebar for login/logout
    with st.sidebar:
        st.header("Admin Panel")
        
        if st.session_state.is_admin:
            st.success("Logged in as Admin")
            if st.button("Logout"):
                st.session_state.is_admin = False
                st.session_state.admin_authenticated_time = None
                st.rerun()
                
            # Admin settings
            with st.expander("Admin Settings"):
                st.subheader("Change Admin Password")
                current_password = st.text_input("Current Password", type="password", key="current_pass")
                new_password = st.text_input("New Password", type="password", key="new_pass")
                confirm_password = st.text_input("Confirm New Password", type="password", key="confirm_pass")
                
                if st.button("Change Password"):
                    if not verify_admin_password(current_password):
                        st.error("Current password is incorrect")
                    elif new_password != confirm_password:
                        st.error("New passwords do not match")
                    elif len(new_password) < 6:
                        st.error("New password must be at least 6 characters")
                    else:
                        # Update password
                        st.session_state.admin_password_hash = hashlib.sha256(new_password.encode()).hexdigest()
                        save_data()
                        st.success("Password changed successfully")
        else:
            st.info("Login to access admin features")
            admin_password = st.text_input("Admin Password", type="password", key="admin_pass")
            
            if st.button("Login"):
                if verify_admin_password(admin_password):
                    st.session_state.is_admin = True
                    st.session_state.admin_authenticated_time = datetime.datetime.now()
                    st.success("Login successful")
                    st.rerun()
                else:
                    st.error("Incorrect password")

# App Components
def header_section():
    """App header section"""
    st.title("XploreMe@Sports - Badminton 🏸")
    st.markdown("Manage your badminton matches, teams, and stats!")

def player_management_section():
    """Player management section"""
    st.header("Player Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Predefined Players")
        
        # Display predefined players
        df_predefined = pd.DataFrame(st.session_state.predefined_players)
        if not df_predefined.empty:
            # Reorder columns for better display
            columns_order = ["name", "skill_level", "games_played", "wins", "points_scored"]
            display_columns = [col for col in columns_order if col in df_predefined.columns]
            st.dataframe(df_predefined[display_columns], use_container_width=True)
        
        # Add new predefined player (admin only)
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
        
        # Display temporary players
        df_temp = pd.DataFrame(st.session_state.temp_players)
        if not df_temp.empty:
            # Reorder columns for better display
            columns_order = ["name", "skill_level", "games_played", "wins", "points_scored"]
            display_columns = [col for col in columns_order if col in df_temp.columns]
            st.dataframe(df_temp[display_columns], use_container_width=True)
        else:
            st.info("No temporary players added yet")
        
        # Add new temporary player (admin only)
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
        
        # Clear all temporary players (admin only)
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
    
    # Select active players for today's session
    st.subheader("Select Available Players")
    available_players = []
    
    # Display player selection in a grid of checkboxes
    num_cols = 3
    cols = st.columns(num_cols)
    
    for i, player in enumerate(all_players):
        col_idx = i % num_cols
        with cols[col_idx]:
            # Everyone can select players
            is_selected = st.checkbox(f"{player['name']} (Skill: {player['skill_level']})", key=f"player_{player['id']}")
            if is_selected:
                available_players.append(player)
    
    # Generate random teams
    st.subheader("Team Generation")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Everyone can generate teams
        if st.button("Generate Random Teams", key="gen_teams", disabled=len(available_players) < 4):
            team_a, team_b = generate_random_teams(available_players)
            
            if team_a and team_b:
                st.session_state.current_teams = {"team_a": team_a, "team_b": team_b}
                st.success("Teams generated successfully!")
                st.rerun()
            else:
                st.error("Not enough players to form two teams. Need at least 4 players.")
    
    with col2:
        # Everyone can rematch
        if st.button("Rematch with Same Teams", key="rematch", disabled=not (st.session_state.current_teams["team_a"] and st.session_state.current_teams["team_b"])):
            # Keep the same teams
            st.success("Teams kept for rematch!")
    
    # Display current teams
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
    
    # Waiting queue
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
        # Everyone can view scores, but only admin can input them
        score_a = st.number_input("Score Team A", min_value=0, value=0, step=1, key="score_a", disabled=not st.session_state.is_admin)
    
    with col2:
        st.markdown("<h2 style='text-align: center;'>VS</h2>", unsafe_allow_html=True)
    
    with col3:
        st.subheader("Team B")
        for player in st.session_state.current_teams["team_b"]:
            st.write(f"• {player['name']}")
        # Everyone can view scores, but only admin can input them
        score_b = st.number_input("Score Team B", min_value=0, value=0, step=1, key="score_b", disabled=not st.session_state.is_admin)
    
    # Everyone can view notes, but only admin can input them
    match_notes = st.text_area("Match Notes (optional)", key="match_notes", disabled=not st.session_state.is_admin)
    
    # Admin-only match recording
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
            # Trigger rerun to refresh the UI with updated stats
            st.rerun()

def statistics_section():
    """Statistics and analytics section"""
    st.header("Statistics & Analytics")
    
    tab1, tab2, tab3 = st.tabs(["Player Stats", "Match History", "Team Analysis"])
    
    with tab1:
        st.subheader("Player Performance")
        
        # Combine all players
        all_players = st.session_state.predefined_players + st.session_state.temp_players
        
        if all_players:
            # Create dataframe
            df_players = pd.DataFrame(all_players)
            
            # Calculate win rate
            df_players["win_rate"] = df_players.apply(
                lambda x: round((x["wins"] / x["games_played"]) * 100, 1) if x["games_played"] > 0 else 0,
                axis=1
            )
            
            # Calculate avg points per game
            df_players["avg_points_per_game"] = df_players.apply(
                lambda x: round(x["points_scored"] / x["games_played"], 1) if x["games_played"] > 0 else 0,
                axis=1
            )
            
            # Display table
            columns_to_display = ["name", "games_played", "wins", "win_rate", "points_scored", "avg_points_per_game", "skill_level"]
            st.dataframe(df_players[columns_to_display].sort_values(by="win_rate", ascending=False), use_container_width=True)
            
            # Display charts
            if not df_players.empty and df_players["games_played"].sum() > 0:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Win Rate by Player")
                    fig, ax = plt.subplots(figsize=(10, 6))
                    
                    # Filter players with at least one game
                    active_players = df_players[df_players["games_played"] > 0]
                    
                    # Sort by win rate
                    active_players = active_players.sort_values("win_rate", ascending=False)
                    
                    sns.barplot(x="name", y="win_rate", data=active_players, ax=ax)
                    plt.xticks(rotation=45, ha="right")
                    plt.ylabel("Win Rate (%)")
                    plt.xlabel("")
                    plt.tight_layout()
                    st.pyplot(fig)
                
                with col2:
                    st.subheader("Games Played vs Wins")
                    fig, ax = plt.subplots(figsize=(10, 6))
                    
                    # Create a melted dataframe for grouped bar chart
                    df_melt = pd.melt(
                        active_players,
                        id_vars=["name"],
                        value_vars=["games_played", "wins"],
                        var_name="Metric",
                        value_name="Count"
                    )
                    
                    # Create grouped bar chart
                    sns.barplot(x="name", y="Count", hue="Metric", data=df_melt, ax=ax)
                    plt.xticks(rotation=45, ha="right")
                    plt.tight_layout()
                    st.pyplot(fig)
        else:
            st.info("No player statistics available yet.")
    
    with tab2:
        st.subheader("Match History")
        
        if st.session_state.match_history:
            # Create a dataframe from match history
            match_data = []
            
            for match in st.session_state.match_history:
                # Get player names for each team
                team_a_names = [get_player_by_id(pid)["name"] for pid in match["team_a"] if get_player_by_id(pid)]
                team_b_names = [get_player_by_id(pid)["name"] for pid in match["team_b"] if get_player_by_id(pid)]
                
                match_data.append({
                    "Match ID": match["id"][:8],  # Shortened ID for display
                    "Date": match["timestamp"],
                    "Team A": " & ".join(team_a_names),
                    "Team B": " & ".join(team_b_names),
                    "Score": f"{match['score_a']} - {match['score_b']}",
                    "Winner": f"Team {match['winning_team']}",
                    "Notes": match["notes"]
                })
            
            # Create dataframe and display
            df_matches = pd.DataFrame(match_data)
            st.dataframe(df_matches, use_container_width=True)
            
            # Match statistics chart
            st.subheader("Match Score Distribution")
            
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Extract scores
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
            # Create team combination performance analysis
            team_stats = defaultdict(lambda: {"matches": 0, "wins": 0, "total_points": 0})
            
            for match in st.session_state.match_history:
                # Team A combination
                team_a_key = "&".join(sorted([get_player_by_id(pid)["name"] for pid in match["team_a"] if get_player_by_id(pid)]))
                team_stats[team_a_key]["matches"] += 1
                team_stats[team_a_key]["total_points"] += match["score_a"]
                if match["winning_team"] == "A":
                    team_stats[team_a_key]["wins"] += 1
                
                # Team B combination
                team_b_key = "&".join(sorted([get_player_by_id(pid)["name"] for pid in match["team_b"] if get_player_by_id(pid)]))
                team_stats[team_b_key]["matches"] += 1
                team_stats[team_b_key]["total_points"] += match["score_b"]
                if match["winning_team"] == "B":
                    team_stats[team_b_key]["wins"] += 1
            
            # Create dataframe from team stats
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
            
            # Team win rate chart
            st.subheader("Team Win Rates")
            
            fig, ax = plt.subplots(figsize=(10, 6))
            df_teams_sorted = df_teams.sort_values(by="Win Rate (%)", ascending=False)
            
            # Only show top 10 teams if there are many
            if len(df_teams_sorted) > 10:
                df_teams_sorted = df_teams_sorted.head(10)
            
            sns.barplot(x="Team", y="Win Rate (%)", data=df_teams_sorted, ax=ax)
            plt.xticks(rotation=45, ha="right")
            plt.tight_layout()
            st.pyplot(fig)
        else:
            st.info("No team statistics available yet.")

def main():
    """Main app"""
    # Load data
    load_data()
    
    # Check if the app needs to trigger a rerun based on data updates
    if st.session_state.data_updated:
        st.session_state.data_updated = False
        st.rerun()
    
    # Admin authentication (shown in sidebar)
    admin_authentication()
    
    # App layout
    header_section()
    
    # Main navigation tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Players", "Team Formation", "Match Recording", "Statistics"])
    
    with tab1:
        player_management_section()
    
    with tab2:
        team_formation_section()
    
    with tab3:
        match_recording_section()
    
    with tab4:
        statistics_section()

if __name__ == "__main__":
    main()