#!/usr/bin/env python3
"""
Identify columns that are likely to be null or have low value
Based on API data structure analysis
"""

def identify_problematic_columns():
    """Identify columns that should be removed based on API data analysis"""

    print("=== IDENTIFYING PROBLEMATIC COLUMNS ===")

    # From ISCJXXQGMB API analysis, these columns are often null or not useful:
    iscjxxqgmb_null_columns = [
        'home_team_logo',      # Usually null or not needed
        'away_team_logo',      # Usually null or not needed
        'match_weight',        # Internal API field, often null
        'set_number',          # Not always applicable
        'match_time_extended', # Usually null
        'in_top',              # Internal ranking, often null
        'match_in_campaign',   # Usually null
        'yellow_cards_home',   # Often 0 or null
        'yellow_cards_away',   # Often 0 or null
        'red_cards_home',      # Often 0 or null
        'red_cards_away',       # Often 0 or null
        'corners_home',        # Often 0 or null
        'corners_away',        # Often 0 or null
        'segment_scores',      # Complex JSON, often null
        'sets_score',          # Complex JSON, often null
        'overtime_score',      # Usually null
        'regular_time_score',  # Usually null
        'after_penalties_score', # Usually null
        'line_status',         # Internal API field
        'is_outright',         # Usually False/null
        'is_cyber',            # Usually False/null
        'in_favorites',        # Usually False/null
        'other_outcomes_qty'   # Usually 0
    ]

    # From 1xBet API analysis, fewer null columns but some still:
    xbet_null_columns = [
        # Most 1xBet data is cleaner, but some fields might be null
    ]

    print(f"ISCJXXQGMB API - Potentially null/unused columns: {len(iscjxxqgmb_null_columns)}")
    for col in iscjxxqgmb_null_columns:
        print(f"  - {col}")

    print(f"\n1xBet API - Potentially null/unused columns: {len(xbet_null_columns)}")
    for col in xbet_null_columns:
        print(f"  - {col}")

    # Columns that should be kept (essential for sports data)
    essential_columns = [
        'id',                  # Primary key
        'match_id',           # Unique identifier
        'timestamp',          # When data was collected
        'home_team',          # Essential
        'away_team',          # Essential
        'score',              # Essential
        'status',             # Essential (live/pregame)
        'period',             # Essential
        'tournament',         # Essential
        'sport',              # Essential
        'odds_home',          # Betting data
        'odds_away',          # Betting data
        'odds_draw',          # Betting data
        'event_count',        # Useful metric
        'start_time',         # Essential
        'data_source',        # Track data origin
        'home_team_id',       # Useful for joins
        'away_team_id',       # Useful for joins
        'stoppage_time',      # Match state
        'half_time'           # Match state
    ]

    print(f"\nESSENTIAL COLUMNS TO KEEP: {len(essential_columns)}")
    for col in essential_columns:
        print(f"  + {col}")

    print(f"\n=== RECOMMENDATION ===")
    print(f"Current schema: 43 columns")
    print(f"Optimized schema: {len(essential_columns)} columns")
    print(f"Columns to remove: {43 - len(essential_columns)}")
    print(f"Space savings: ~{((43 - len(essential_columns)) / 43 * 100):.1f}%")

    return iscjxxqgmb_null_columns, xbet_null_columns, essential_columns

if __name__ == "__main__":
    identify_problematic_columns()