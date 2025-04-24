# XploreMe@Sports - Badminton 🏸

<p align="center">
  <img src="[https://cdn.pixabay.com/photo/2012/11/28/10/37/badminton-67640_1280.jpg](https://media.istockphoto.com/id/1033954336/photo/badminton-courts-with-players-competing.jpg)" alt="Badminton Court" width="200">
</p>

Welcome to **XploreMe@Sports - Badminton**, an interactive web application built with Streamlit to manage badminton matches, teams, and player statistics. This app is designed to help badminton enthusiasts track their games, analyze performance, and have fun with a built-in AI chatbot, "BadmintonBuddy." Whether you're organizing a casual match or diving into stats, this app has you covered!

---

## ✨ Features
- **Player Management**: Add and manage predefined and temporary players with their skill levels.
- **Team Formation**: Automatically generate random teams based on player availability and rotation history.
- **Match Recording**: Log match results, scores, and notes, with admin-only access for security.
- **Statistics & Analytics**: View detailed player stats, match history, and team performance with visualizations.
- **BadmintonBuddy AI-Assistant**: Chat with an AI to ask questions about the data or get fun badminton insights.
- **Theme Toggle**: Switch between light and dark themes with a default light mode for a personalized experience.

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
3. Configure the Google API key for the AI assistant:
   - Open `badminton_app.py` and update `st.session_state.api_key` with your Google API key.
   - Ensure `st.session_state.llm_model` is set to a valid model (e.g., "gemini-2.0-flash-lite").

### Running the App
1. Launch the Streamlit app:
   ```bash
   streamlit run badminton_app.py
   ```
2. Open your browser and navigate to the provided local URL (e.g., `http://localhost:8501`).

---

## 🎮 Usage
- **Admin Access**: Log in as an admin using the default password "admin123" (change it via the admin panel for security).
- **Player Management**: Add players and clear temporary ones as needed.
- **Team Formation**: Select available players and generate teams or rematch with the same lineup.
- **Match Recording**: Record results after generating teams (admin-only).
- **Statistics**: Explore tabs for player stats, match history, and team analysis with charts.
- **Chatbot**: Ask "BadmintonBuddy" fun questions like "Is Golu the champ?" or "Who’s the best player?"
- **Theme Settings**: Toggle between light and dark themes from the sidebar.

---

## 💾 Data Storage
- Player data, match history, and admin settings are saved to `badminton_data.json`.
- Chat logs are stored in `chat_history.json` for reference.

---

## 🎨 Customization
- **Theme**: The app uses custom CSS to adapt to light/dark themes with a badminton-inspired design (green, orange, white).
- **AI Model**: Adjust the `llm_model` in the code to use different Google Generative AI models.
- **Images**: Replace the shuttlecock image URL in `header_section()` with your own for a personal touch.

---

## 🤝 Contributing
Feel free to fork this repository and submit pull requests! Ideas for improvements:
- Add more detailed match analytics (e.g., point-by-point data).
- Enhance the chatbot with more humorous responses.
- Support multi-language interfaces.

---

## 📜 License
This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

---

## 🙌 Acknowledgments
- Built with [Streamlit](https://streamlit.io/) for an interactive UI.
- Powered by [Google Generative AI](https://ai.google/) for the chatbot.
- Inspired by the love for badminton and community sports!

Happy smashing! 🏸 Let me know if you need help—BadmintonBuddy’s got your back! 😄
```
