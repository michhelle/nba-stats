import streamlit as st
from utils.data_loader import (
    get_player_list, 
    get_player_game_logs, 
    get_player_season_stats, 
    get_current_season,
    get_available_seasons,
    get_box_score,
    compare_players,
    get_player_advanced_stats,
    get_player_headshot_url
)
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="NBA Stats Tracker", layout="wide")
st.title("🏀 NBA Stats Tracker")

st.sidebar.header("Settings")

players_df = get_player_list()
player_names = sorted(players_df["full_name"].tolist())

selected_player = st.sidebar.selectbox("Select a player", player_names)

available_seasons = get_available_seasons()
current_season = get_current_season()

# Default to 2023 season if available, otherwise use current season
default_season = "2023" if "2023" in available_seasons else current_season
default_index = available_seasons.index(default_season) if default_season in available_seasons else 0

selected_season = st.sidebar.selectbox("Select season", available_seasons, index=default_index)

player_id = players_df[players_df["full_name"] == selected_player]["id"].values[0]
logs = get_player_game_logs(player_id, selected_season)

# If no logs available, try to suggest a different season
if logs.empty:
    st.sidebar.warning(f"No data for {selected_player} in {selected_season}.")
    
    # Find the most recent season with data
    for alt_season in sorted(available_seasons, reverse=True):
        if alt_season != selected_season:
            alt_logs = get_player_game_logs(player_id, alt_season)
            if not alt_logs.empty:
                st.sidebar.info(f"💡 Tip: Data for {selected_player} is available in the {alt_season} season. Please select it from the dropdown.")
                break

tab1, tab2, tab3 = st.tabs(["📊 Player Stats", "📋 Box Scores", "🆚 Player Comparison"])

with tab1:
    if not logs.empty:
        col1, col2 = st.columns([1, 3])

        with col1:
            player_headshot_url = get_player_headshot_url(player_id)
            if player_headshot_url:
                st.markdown(
                    f"""
                    <div style="text-align: center; margin-top: 50px;">
                        <img src="{player_headshot_url}" alt="{selected_player}" width="200">
                        <p>{selected_player}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        with col2:
            st.subheader(f"📊 {selected_season} NBA Season Summary")
            season_stats = get_player_season_stats(player_id, selected_season)
            
            if season_stats:
                sum_col1, sum_col2, sum_col3, sum_col4 = st.columns(4)
                
                with sum_col1:
                    st.metric("Games Played", f"{season_stats.get('games_played', 0)}")
                    st.metric("PPG", f"{season_stats.get('ppg', 0.0):.1f}")
                
                with sum_col2:
                    st.metric("RPG", f"{season_stats.get('rpg', 0.0):.1f}")
                    st.metric("APG", f"{season_stats.get('apg', 0.0):.1f}")
                
                with sum_col3:
                    st.metric("SPG", f"{season_stats.get('spg', 0.0):.1f}")
                    st.metric("BPG", f"{season_stats.get('bpg', 0.0):.1f}")
                
                with sum_col4:
                    st.metric("MPG", f"{season_stats.get('mpg', 0.0):.1f}")
                    st.metric("FG%", f"{season_stats.get('fg_pct', 0.0):.3f}")

        st.divider()

        st.subheader("🔬 Advanced Statistics")
        advanced_stats = get_player_advanced_stats(player_id, selected_season)
        
        if advanced_stats:
            adv_col1, adv_col2, adv_col3 = st.columns(3)
            
            with adv_col1:
                if 'pts_std' in advanced_stats:
                    st.metric("Points Std Dev", f"{advanced_stats['pts_std']:.1f}")
                if 'avg_minutes' in advanced_stats:
                    st.metric("Avg Minutes", f"{advanced_stats['avg_minutes']:.1f}")
            
            with adv_col2:
                if 'total_minutes' in advanced_stats:
                    st.metric("Total Minutes", f"{advanced_stats['total_minutes']:.0f}")
                if 'pts_variance' in advanced_stats:
                    st.metric("Points Variance", f"{advanced_stats['pts_variance']:.1f}")
            
            with adv_col3:
                if 'true_shooting_pct' in advanced_stats:
                    st.metric("True Shooting %", f"{advanced_stats['true_shooting_pct']:.3f}")

        with st.expander(f"📋 {selected_player} - {selected_season} Game Logs", expanded=False):
            available_columns = logs.columns.tolist()
            default_columns = ["GAME_DATE", "MATCHUP", "PTS", "REB", "AST", "STL", "BLK", "MIN", "FG_PCT", "FG3_PCT", "FT_PCT"]
            display_columns = [col for col in default_columns if col in available_columns]
            
            st.dataframe(logs[display_columns])

        st.subheader("📈 Performance Charts")
        
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            st.subheader("📈 Points Over Time")
            if 'PTS' in logs.columns and 'GAME_DATE' in logs.columns and not logs['PTS'].isnull().all():
                if logs['PTS'].sum() > 0:
                    fig, ax = plt.subplots(figsize=(8, 5))
                    ax.plot(logs["GAME_DATE"], logs["PTS"], marker='o', color='blue', linewidth=2, markersize=4)
                    ax.set_title(f"{selected_player} - Points Per Game ({selected_season})")
                    ax.set_xlabel("Game Date")
                    ax.set_ylabel("Points")
                    ax.grid(True, alpha=0.3)
                    plt.xticks(rotation=45)
                    plt.tight_layout()
                    st.pyplot(fig)
                else:
                    st.info("Player has not scored any points this season.")
            else:
                st.warning("Points data is not available to display this chart.")

            st.subheader("⏱️ Minutes Played Over Time")
            if 'MIN' in logs.columns and 'GAME_DATE' in logs.columns and not logs['MIN'].isnull().all():
                if logs['MIN'].sum() > 0:
                    fig3, ax3 = plt.subplots(figsize=(8, 5))
                    ax3.plot(logs["GAME_DATE"], logs["MIN"], marker='o', color='green', linewidth=2, markersize=4)
                    ax3.set_title(f"{selected_player} - Minutes Per Game ({selected_season})")
                    ax3.set_xlabel("Game Date")
                    ax3.set_ylabel("Minutes")
                    ax3.grid(True, alpha=0.3)
                    plt.xticks(rotation=45)
                    plt.tight_layout()
                    st.pyplot(fig3)
                else:
                    st.info("Player has not played any minutes this season.")
            else:
                st.warning("Minutes data is not available to display this chart.")
        
        with chart_col2:
            st.subheader("📊 Other Stats (Last 10 Games)")
            other_stats_cols = ["REB", "AST", "STL", "BLK"]
            if all(col in logs.columns for col in other_stats_cols) and 'GAME_DATE' in logs.columns:
                logs_to_plot = logs.tail(10).copy()
                logs_to_plot['display_date'] = logs_to_plot['GAME_DATE'].dt.strftime('%m-%d')
                
                fig2, ax2 = plt.subplots(figsize=(8, 5))
                logs_to_plot.plot(x="display_date", y=other_stats_cols, kind="bar", ax=ax2)
                ax2.set_title(f"{selected_player} - Recent Performance ({selected_season})")
                ax2.set_xlabel("Game Date")
                ax2.set_ylabel("Count")
                plt.xticks(rotation=45)
                plt.tight_layout()
                st.pyplot(fig2)
            else:
                st.warning("REB, AST, STL, or BLK data is not available to display this chart.")

            st.subheader("🎯 Shooting Percentages Over Time")
            shooting_cols = ['FG_PCT', 'FG3_PCT', 'FT_PCT']
            available_shooting_cols = [col for col in shooting_cols if col in logs.columns]

            if available_shooting_cols and 'GAME_DATE' in logs.columns and logs[available_shooting_cols].sum().sum() > 0:
                fig4, ax4 = plt.subplots(figsize=(8, 5))
                
                for col in available_shooting_cols:
                    if logs[col].sum() > 0: # Only plot if there is data
                        marker = 'o' if col == 'FG_PCT' else 's' if col == 'FG3_PCT' else '^'
                        color = 'orange' if col == 'FG_PCT' else 'red' if col == 'FG3_PCT' else 'purple'
                        label = 'FG%' if col == 'FG_PCT' else '3P%' if col == 'FG3_PCT' else 'FT%'
                        ax4.plot(logs["GAME_DATE"], logs[col], marker=marker, color=color, linewidth=2, markersize=4, label=label)
                
                ax4.set_title(f"{selected_player} - Shooting Percentages ({selected_season})")
                ax4.set_xlabel("Game Date")
                ax4.set_ylabel("Percentage")
                ax4.grid(True, alpha=0.3)
                if ax4.has_data():
                    ax4.legend()
                plt.xticks(rotation=45)
                plt.tight_layout()
                st.pyplot(fig4)
            else:
                st.warning("Shooting percentage data is not available or is all zero.")

    else:
        st.error(f"No data available for {selected_player} in the {selected_season} NBA season.")
        st.info("Try selecting a different season or player.")

with tab2:
    st.subheader("📋 Box Score Analysis")
    
    if not logs.empty:
        required_columns = ['GAME_ID', 'GAME_DATE', 'MATCHUP']
        available_columns = [col for col in required_columns if col in logs.columns]
        
        if len(available_columns) >= 2:  # Need at least GAME_DATE and MATCHUP
            if 'GAME_ID' in logs.columns:
                game_options = logs[['GAME_ID', 'GAME_DATE', 'MATCHUP']].drop_duplicates()
            else:
                game_options = logs[['GAME_DATE', 'MATCHUP']].drop_duplicates()
                game_options['GAME_ID'] = game_options.index  # Create a dummy ID
            
            game_options['display'] = game_options['GAME_DATE'].dt.strftime('%Y-%m-%d') + ' - ' + game_options['MATCHUP']
            
            selected_game = st.selectbox(
                "Select a game for detailed box score:",
                options=game_options['display'].tolist()
            )
            
            if selected_game:
                game_matches = game_options[game_options['display'] == selected_game]
                if game_matches.empty:
                    st.error("Selected game not found in data.")
                else:
                    game_info = game_matches.iloc[0]
                    
                    if 'GAME_ID' in game_info and game_info['GAME_ID'] != game_info.name:
                        game_id = game_info['GAME_ID']
                        
                        player_box, team_box = get_box_score(game_id)
                        
                        if not player_box.empty:
                            st.subheader(f"📊 Player Box Score - {selected_game}")
                            
                            player_game_stats = player_box[player_box['PLAYER_ID'] == player_id]
                            
                            if not player_game_stats.empty:
                                player_stats = player_game_stats.iloc[0]
                                
                                box_col1, box_col2, box_col3, box_col4 = st.columns(4)
                                
                                with box_col1:
                                    st.metric("Points", int(player_stats.get('PTS', 0)))
                                    st.metric("Rebounds", int(player_stats.get('REB', 0)))
                                
                                with box_col2:
                                    st.metric("Assists", int(player_stats.get('AST', 0)))
                                    st.metric("Steals", int(player_stats.get('STL', 0)))
                                
                                with box_col3:
                                    st.metric("Blocks", int(player_stats.get('BLK', 0)))
                                    st.metric("Minutes", player_stats.get('MIN', '0'))
                                
                                with box_col4:
                                    st.metric("FG%", f"{player_stats.get('FG_PCT', 0):.3f}")
                                    st.metric("3P%", f"{player_stats.get('FG3_PCT', 0):.3f}")
                                
                                st.subheader("🎯 Game Performance Breakdown")
                                
                                categories = ['PTS', 'REB', 'AST', 'STL', 'BLK']
                                values = [player_stats.get(cat, 0) for cat in categories]
                                
                                fig_radar, ax_radar = plt.subplots(figsize=(10, 6))
                                bars = ax_radar.bar(categories, values, color=['blue', 'green', 'purple', 'orange', 'red'])
                                ax_radar.set_title(f"{selected_player} Performance - {selected_game}")
                                ax_radar.set_ylabel('Count')
                                
                                for bar, value in zip(bars, values):
                                    height = bar.get_height()
                                    ax_radar.text(bar.get_x() + bar.get_width()/2., height,
                                                f'{value}', ha='center', va='bottom')
                                
                                plt.tight_layout()
                                st.pyplot(fig_radar)
                            
                            st.subheader("📋 Complete Game Box Score")
                            st.dataframe(player_box)
                        
                        else:
                            st.error("No box score data available for this game.")
                    
                    else:
                        st.subheader(f"📊 Game Data - {selected_game}")
                        
                        game_date = game_info['GAME_DATE']
                        matchup = game_info['MATCHUP']
                        
                        game_data = logs[(logs['GAME_DATE'] == game_date) & (logs['MATCHUP'] == matchup)]
                        
                        if not game_data.empty:
                            player_game_data = game_data.iloc[0]
                            
                            box_col1, box_col2, box_col3, box_col4 = st.columns(4)
                            
                            with box_col1:
                                st.metric("Points", int(player_game_data.get('PTS', 0)))
                                st.metric("Rebounds", int(player_game_data.get('REB', 0)))
                            
                            with box_col2:
                                st.metric("Assists", int(player_game_data.get('AST', 0)))
                                st.metric("Steals", int(player_game_data.get('STL', 0)))
                            
                            with box_col3:
                                st.metric("Blocks", int(player_game_data.get('BLK', 0)))
                                st.metric("Minutes", player_game_data.get('MIN', '0'))
                            
                            with box_col4:
                                st.metric("FG%", f"{player_game_data.get('FG_PCT', 0):.3f}")
                                st.metric("3P%", f"{player_game_data.get('FG3_PCT', 0):.3f}")
                            
                            st.subheader("🎯 Game Performance Breakdown")
                            
                            categories = ['PTS', 'REB', 'AST', 'STL', 'BLK']
                            values = [player_game_data.get(cat, 0) for cat in categories]
                            
                            fig_radar, ax_radar = plt.subplots(figsize=(10, 6))
                            bars = ax_radar.bar(categories, values, color=['blue', 'green', 'purple', 'orange', 'red'])
                            ax_radar.set_title(f"{selected_player} Performance - {selected_game}")
                            ax_radar.set_ylabel('Count')
                            
                            for bar, value in zip(bars, values):
                                height = bar.get_height()
                                ax_radar.text(bar.get_x() + bar.get_width()/2., height,
                                            f'{value}', ha='center', va='bottom')
                            
                            plt.tight_layout()
                            st.pyplot(fig_radar)
                            
                            st.subheader("📋 Game Data")
                            st.dataframe(game_data)
                        
                        else:
                            st.error("No game data found for the selected game.")
        
        else:
            st.error("Required columns (GAME_DATE, MATCHUP) not found in game logs.")
            st.write("Available columns:", list(logs.columns))
    
    else:
        st.info("No game data available. Please select a player with game logs first.")

with tab3:
    st.subheader("🆚 Player Comparison")
    
    st.write("Select players to compare their season statistics:")
    
    comparison_players = st.multiselect(
        "Choose players to compare (up to 6):",
        player_names,
        max_selections=6,
        help="Select 2-6 players to compare their season statistics"
    )
    
    if len(comparison_players) >= 2:
        st.write(f"Loading statistics for {len(comparison_players)} players...")
        
        comparison_player_ids = []
        for player_name in comparison_players:
            player_id = players_df[players_df["full_name"] == player_name]["id"].values[0]
            comparison_player_ids.append(player_id)
        
        comparison_data = compare_players(comparison_player_ids, selected_season)
        
        if not comparison_data.empty:
            player_id_to_name = {players_df[players_df["full_name"] == name]["id"].values[0]: name for name in comparison_players}
            comparison_data['player_name'] = comparison_data['player_id'].map(player_id_to_name)
            
            st.success(f"✅ Successfully loaded data for {len(comparison_data)} players")
            
            comp_col1, comp_col2 = st.columns(2)
            
            with comp_col1:
                fig_ppg, ax_ppg = plt.subplots(figsize=(10, 6))
                bars = ax_ppg.bar(comparison_data['player_name'], comparison_data['ppg'], color='skyblue')
                ax_ppg.set_title('Points Per Game Comparison')
                ax_ppg.set_ylabel('PPG')
                plt.xticks(rotation=45)
                
                for bar, value in zip(bars, comparison_data['ppg']):
                    height = bar.get_height()
                    ax_ppg.text(bar.get_x() + bar.get_width()/2., height,
                              f'{value}', ha='center', va='bottom')
                
                plt.tight_layout()
                st.pyplot(fig_ppg)
                
                fig_rpg, ax_rpg = plt.subplots(figsize=(10, 6))
                bars = ax_rpg.bar(comparison_data['player_name'], comparison_data['rpg'], color='lightgreen')
                ax_rpg.set_title('Rebounds Per Game Comparison')
                ax_rpg.set_ylabel('RPG')
                plt.xticks(rotation=45)
                
                for bar, value in zip(bars, comparison_data['rpg']):
                    height = bar.get_height()
                    ax_rpg.text(bar.get_x() + bar.get_width()/2., height,
                              f'{value}', ha='center', va='bottom')
                
                plt.tight_layout()
                st.pyplot(fig_rpg)
            
            with comp_col2:
                fig_apg, ax_apg = plt.subplots(figsize=(10, 6))
                bars = ax_apg.bar(comparison_data['player_name'], comparison_data['apg'], color='plum')
                ax_apg.set_title('Assists Per Game Comparison')
                ax_apg.set_ylabel('APG')
                plt.xticks(rotation=45)
                
                for bar, value in zip(bars, comparison_data['apg']):
                    height = bar.get_height()
                    ax_apg.text(bar.get_x() + bar.get_width()/2., height,
                              f'{value}', ha='center', va='bottom')
                
                plt.tight_layout()
                st.pyplot(fig_apg)
                
                fig_shooting, ax_shooting = plt.subplots(figsize=(10, 6))
                x = range(len(comparison_data))
                width = 0.25
                
                ax_shooting.bar([i - width for i in x], comparison_data['fg_pct'], width, label='FG%', color='orange')
                ax_shooting.bar(x, comparison_data['fg3_pct'], width, label='3P%', color='red')
                ax_shooting.bar([i + width for i in x], comparison_data['ft_pct'], width, label='FT%', color='purple')
                
                ax_shooting.set_title('Shooting Percentages Comparison')
                ax_shooting.set_ylabel('Percentage')
                ax_shooting.set_xticks(x)
                ax_shooting.set_xticklabels(comparison_data['player_name'], rotation=45)
                ax_shooting.legend()
                plt.tight_layout()
                st.pyplot(fig_shooting)
            
            st.subheader("📋 Detailed Comparison Table")
            display_cols = ['player_name', 'games_played', 'ppg', 'rpg', 'apg', 'spg', 'bpg', 'mpg', 'fg_pct', 'fg3_pct', 'ft_pct']
            available_display_cols = [col for col in display_cols if col in comparison_data.columns]
            st.dataframe(comparison_data[available_display_cols])
            
            st.subheader("🏆 Season Summary")
            if not comparison_data.empty:
                summary_col1, summary_col2, summary_col3 = st.columns(3)

                with summary_col1:
                    top_scorer = comparison_data.loc[comparison_data['ppg'].idxmax()]
                    st.metric("Top Scorer", f"{top_scorer['ppg']:.1f} PPG", top_scorer['player_name'])
                    
                    top_rebounder = comparison_data.loc[comparison_data['rpg'].idxmax()]
                    st.metric("Top Rebounder", f"{top_rebounder['rpg']:.1f} RPG", top_rebounder['player_name'])
                
                with summary_col2:
                    top_assister = comparison_data.loc[comparison_data['apg'].idxmax()]
                    st.metric("Top Assister", f"{top_assister['apg']:.1f} APG", top_assister['player_name'])
                    
                    top_shooter = comparison_data.loc[comparison_data['fg_pct'].idxmax()]
                    st.metric("Best FG%", f"{top_shooter['fg_pct']:.3f}", top_shooter['player_name'])
                
                with summary_col3:
                    most_games = comparison_data.loc[comparison_data['games_played'].idxmax()]
                    st.metric("Most Games", f"{most_games['games_played']}", most_games['player_name'])
                    
                    top_3pt = comparison_data.loc[comparison_data['fg3_pct'].idxmax()]
                    st.metric("Best 3P%", f"{top_3pt['fg3_pct']:.3f}", top_3pt['player_name'])
            else:
                st.write("No data to summarize.")
        
        else:
            st.error("No comparison data available for the selected players.")
            st.write("This might be due to:")
            st.write("- Players not having data for the selected season")
            st.write("- API connection issues")
            st.write("- Players being inactive in the selected season")
            st.write("Try selecting different players or a different season.")
    
    else:
        st.info("Please select at least 2 players to compare.")