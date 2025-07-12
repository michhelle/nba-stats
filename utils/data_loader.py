from nba_api.stats.static import players, teams
from nba_api.stats.endpoints import playergamelog, boxscoretraditionalv2, leaguedashteamstats
from nba_api.stats.library.parameters import Season
import pandas as pd
from datetime import datetime
import streamlit as st

@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_player_list():
    """Get all active NBA players with more detailed information"""
    player_data = players.get_active_players()
    df = pd.DataFrame(player_data)
    # Add a full name column for easier selection
    df['full_name'] = df['first_name'] + ' ' + df['last_name']
    return df

@st.cache_data(ttl=1800)  # Cache for 30 minutes
def get_current_season():
    """Get the current NBA season year"""
    current_year = datetime.now().year
    current_month = datetime.now().month
    # if we're before October, use previous year
    if current_month < 10:
        return str(current_year - 1)
    else:
        return str(current_year)

@st.cache_data(ttl=1800)  # Cache for 30 minutes
def get_player_game_logs(player_id, season=None):
    """Get player game logs for a specific season"""
    if season is None:
        season = get_current_season()
    
    try:
        logs = playergamelog.PlayerGameLog(
            player_id=player_id, 
            season=season
        ).get_data_frames()[0]
        
        if not logs.empty:
            # Let pandas infer the date format, coercing errors to NaT
            logs["GAME_DATE"] = pd.to_datetime(logs["GAME_DATE"], errors='coerce')
            
            # Drop rows where date conversion failed
            logs.dropna(subset=['GAME_DATE'], inplace=True)
            
            logs = logs.sort_values("GAME_DATE")
            
            # Ensure all relevant stat columns are numeric, coercing errors
            numeric_cols = [
                'PTS', 'REB', 'AST', 'STL', 'BLK', 'MIN', 
                'FG_PCT', 'FG3_PCT', 'FT_PCT'
            ]
            for col in numeric_cols:
                if col in logs.columns:
                    logs[col] = pd.to_numeric(logs[col], errors='coerce').fillna(0)
            
            # Ensure GAME_ID column exists
            if 'GAME_ID' not in logs.columns:
                logs['GAME_ID'] = logs.index
        
        return logs
    except Exception as e:
        print(f"Error fetching data for player {player_id}, season {season}: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=1800)  # Cache for 30 minutes
def get_player_season_stats(player_id, season=None):
    """Get player's season averages and totals as a simple dictionary."""
    if season is None:
        season = get_current_season()
    
    try:
        logs = get_player_game_logs(player_id, season)
        if logs.empty:
            return {}

        # Safely calculate stats
        stats = {
            'games_played': len(logs),
            'ppg': logs['PTS'].mean(),
            'rpg': logs['REB'].mean(),
            'apg': logs['AST'].mean(),
            'spg': logs['STL'].mean(),
            'bpg': logs['BLK'].mean(),
            'mpg': logs['MIN'].mean(),
            'fg_pct': logs['FG_PCT'].mean(),
            'fg3_pct': logs['FG3_PCT'].mean(),
            'ft_pct': logs['FT_PCT'].mean(),
        }

        # Replace NaN with 0 and round the values
        for key, value in stats.items():
            if pd.isna(value):
                stats[key] = 0
            else:
                # Round percentages to 3 decimal places, others to 1
                if '_pct' in key:
                    stats[key] = round(value, 3)
                else:
                    stats[key] = round(value, 1)

        return stats
    except Exception as e:
        print(f"Error calculating season stats for player {player_id}: {e}")
        return {}

@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_available_seasons():
    """Get list of available seasons (last 5 years)"""
    current_year = int(get_current_season())
    return [str(year) for year in range(current_year - 4, current_year + 1)]

@st.cache_data(ttl=1800)  # Cache for 30 minutes
def get_box_score(game_id):
    """Get box score data for a specific game"""
    try:
        box_score = boxscoretraditionalv2.BoxScoreTraditionalV2(
            game_id=game_id
        ).get_data_frames()
        
        # Return both player and team box scores
        player_box = box_score[0] if len(box_score) > 0 else pd.DataFrame()
        team_box = box_score[1] if len(box_score) > 1 else pd.DataFrame()
        
        return player_box, team_box
    except Exception as e:
        print(f"Error fetching box score for game {game_id}: {e}")
        return pd.DataFrame(), pd.DataFrame()

def compare_players(player_ids, season=None):
    """Compare multiple players' season stats."""
    if season is None:
        season = get_current_season()
    
    comparison_data = []
    
    for player_id in player_ids:
        try:
            stats = get_player_season_stats(player_id, season)
            if stats:  # Check if the dictionary is not empty
                player_info = {
                    'player_id': player_id,
                    'season': season,
                    'games_played': stats.get('games_played', 0),
                    'ppg': stats.get('ppg', 0.0),
                    'rpg': stats.get('rpg', 0.0),
                    'apg': stats.get('apg', 0.0),
                    'spg': stats.get('spg', 0.0),
                    'bpg': stats.get('bpg', 0.0),
                    'mpg': stats.get('mpg', 0.0),
                    'fg_pct': stats.get('fg_pct', 0.0),
                    'fg3_pct': stats.get('fg3_pct', 0.0),
                    'ft_pct': stats.get('ft_pct', 0.0)
                }
                comparison_data.append(player_info)
        except Exception as e:
            print(f"Error processing player {player_id} for comparison: {e}")
    
    return pd.DataFrame(comparison_data)

def get_player_advanced_stats(player_id, season=None):
    """Get advanced statistics for a player"""
    if season is None:
        season = get_current_season()
    
    try:
        logs = get_player_game_logs(player_id, season)
        if not logs.empty:
            # Calculate advanced stats
            advanced_stats = {}
            
            # Efficiency stats
            if 'FG_PCT' in logs.columns and 'FG3_PCT' in logs.columns:
                advanced_stats['true_shooting_pct'] = logs['FG_PCT'].mean()
                advanced_stats['effective_fg_pct'] = logs['FG_PCT'].mean()
            
            # Usage stats
            if 'MIN' in logs.columns:
                advanced_stats['avg_minutes'] = logs['MIN'].mean()
                advanced_stats['total_minutes'] = logs['MIN'].sum()
            
            # Consistency stats
            if 'PTS' in logs.columns:
                advanced_stats['pts_std'] = logs['PTS'].std()
                advanced_stats['pts_variance'] = logs['PTS'].var()
            
            return advanced_stats
        return {}
    except Exception as e:
        print(f"Error calculating advanced stats for player {player_id}: {e}")
        return {}

def get_player_headshot_url(player_id):
    """Construct the URL for a player's headshot image."""
    return f"https://cdn.nba.com/headshots/nba/latest/1040x760/{player_id}.png"
