<p align="center">
  XploreMe@Sports - Badminton 🏸
</p>

<p align="center">
  <img src="https://img.freepik.com/free-psd/badminton-template-design_23-2151491185.jpg" alt="Badminton Court" width="600">
</p>

Welcome to **XploreMe@Sports - Badminton**, an interactive web application built with Streamlit to manage badminton matches, teams, and player statistics. Designed for enthusiasts, this app tracks games, analyzes performance, and offers AI-powered insights via "BadmintonBuddy," now enhanced with advanced LLM capabilities. Whether you're organizing matches or exploring stats, this app is your ultimate badminton companion!

---

## ✨ Features
- **Player Management**: Add and manage predefined and temporary players with AI-assigned skill levels (1-5).
- **Team Formation**: Auto-generate balanced teams based on player availability, rotation history, and skills.
- **Match Recording**: Log results, scores, and notes (admin-only), with LLM parsing of match prompts.
- **Statistics & Analytics**: View detailed player stats, match history, team performance, and AI-generated insights with visualizations.
- **BadmintonBuddy AI-Assistant**: Leverage LLM for match recording, skill assessment, interesting season stats, and interactive chats.
- **Admin & Super Admin Features**: 
  - Admin: Manage players, record matches, and view analytics.
  - Super Admin: Edit match history, delete matches, restore backups, list/download files, and sync with Google Drive.
- **Theme Toggle**: Switch between light and dark themes (default light) for a personalized experience.

---

## 🛠 Installation

### Prerequisites
- Python 3.8 or higher
- Pip package manager

### Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/xploreme-sports-badminton.git
   cd xploreme-sports-badminton
   ```
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure environment variables:
   - Create a `.env` file in the root directory with:
     ```
     GOOGLE_API_KEY=your_google_api_key
     ADMIN_PASSWORD=your_admin_password
     SUPER_ADMIN_PASSWORD=your_super_admin_password
     ```
   - Alternatively, set these as environment variables in your system.
4. Ensure Google Drive API credentials are set up:
   - Place `service-account-key.json` in the working directory for Google Drive sync.

### Running the App
1. Launch the Streamlit app:
   ```bash
   streamlit run badminton_app.py
   ```
2. Open your browser and navigate to the provided local URL (e.g., `http://localhost:8501`).

---

## 🎮 Usage
- **Login**:
  - **Admin**: Log in with the `ADMIN_PASSWORD` (default "admin123", change via `.env`).
  - **Super Admin**: Log in with the `SUPER_ADMIN_PASSWORD` (default "SuperAdmin123!", change via `.env`) for advanced controls.
- **Player Management**: Add predefined/temporary players; view AI-assigned skill levels.
- **Team Formation**: Select players and generate teams or rematch with the same lineup.
- **Match Recording**: Enter results (e.g., "Golu and Saurabh vs Pavan and Shraddha, 23-21")—LLM parses and logs them (admin-only).
- **Statistics**:
  - Explore player stats, match history, team analysis, and performance trends.
  - AI enhances with average skill, player skills, and interesting facts (e.g., "Saurabh: Biggest comeback from 11-3").
- **Super Admin Features**:
  - **Edit Match History**: Modify scores/notes in a table and save to `badminton_data.json`.
  - **Delete Matches**: Remove matches with a checkbox and sync changes.
  - **Restore Backups**: Upload `.json` files (e.g., `badminton_data.json`) and sync to Google Drive.
  - **List/Download Files**: View and download files (e.g., logs, data) from the working directory.
- **Chatbot**: Ask "BadmintonBuddy" questions like "Who’s the best player?" or "What’s the closest match?"
- **Theme Settings**: Toggle light/dark themes from the sidebar.

---

## 🎨 Customization
- **Theme**: Custom CSS adapts to light/dark themes with a badminton-inspired design (green, orange, white).
- **AI Model**: Adjust `st.session_state.llm_model` (e.g., "gemini-2.0-flash-lite") in `badminton_app.py` for different Google Generative AI models.
- **Images**: Replace the shuttlecock image URL in `header_section()` with your own.
- **Passwords**: Update `ADMIN_PASSWORD` and `SUPER_ADMIN_PASSWORD` in `.env` for security.

---

## 🤝 Contributing
Fork this repository and submit pull requests! Ideas for improvements:
- Add point-by-point match analytics.
- Enhance LLM with predictive insights (e.g., next match winner).
- Support multi-language interfaces.
- Add mobile-friendly UI adjustments.

---

## 📜 License
This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

---

## 🙌 Acknowledgments
- Built with [Streamlit](https://streamlit.io/) for an interactive UI.
- Powered by [Google Generative AI](https://ai.google/) for LLM features (match parsing, skill levels, stats).
- Inspired by the badminton community and sports analytics enthusiasts!

Happy smashing! 🏸 BadmintonBuddy is here to assist—let me know your feedback! 😄
