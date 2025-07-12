# NBA Stats Tracker

An interactive web application built with Streamlit that provides detailed statistics for NBA players. Users can view season averages, game logs, advanced metrics, and compare multiple players.

## Features

- **Player Statistics:** View comprehensive stats for any player, including season averages, game logs, and advanced metrics.
- **Player Headshots:** See a headshot of the selected player for a more engaging experience.
- **Performance Charts:** Visualize player performance over time with interactive charts for points, minutes, and shooting percentages.
- **Box Scores:** Analyze detailed box scores for individual games.
- **Player Comparison:** Compare season statistics for up to six players side-by-side.
- **Seasonal Data:** Select different NBA seasons to view historical data.

## Getting Started

Follow these instructions to set up and run the project locally.

### Prerequisites

- Python 3.8+
- An IDE like VS Code or PyCharm (optional)

### Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/michhelle/nba-stats.git
    cd nba-stats
    ```

2.  **Create and activate a virtual environment:**

    - **Windows:**
      ```bash
      python -m venv venv
      .\venv\Scripts\activate
      ```
    - **macOS / Linux:**
      ```bash
      python3 -m venv venv
      source venv/bin/activate
      ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### Usage

1.  **Run the Streamlit application:**

    ```bash
    streamlit run nba_app.py
    ```

2.  Open your web browser and navigate to the local URL provided by Streamlit (usually `http://localhost:8501`).

3.  Use the sidebar to select a player and a season to begin exploring stats.

## Technologies Used

- **Framework:** [Streamlit](https://streamlit.io/)
- **Data Analysis:** [pandas](https://pandas.pydata.org/), [numpy](https://numpy.org/)
- **Data Visualization:** [Matplotlib](https://matplotlib.org/), [Seaborn](https://seaborn.pydata.org/)
- **NBA Data:** [nba-api](https://github.com/swar/nba_api)

---

_This project is for educational purposes and is not affiliated with the NBA._
