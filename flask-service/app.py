from flask import Flask, jsonify, request
from espn_api.football import League
from flask_cors import CORS
import os
from dotenv import load_dotenv
import requests

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Configure CORS to allow requests from Go backend
# Allow requests from localhost (dev) and Railway (production)
allowed_origins = os.getenv('ALLOWED_ORIGINS', 'http://localhost:8080,https://fantasy-assistant-production.up.railway.app').split(',')
CORS(app, resources={r"/api/*": {"origins": allowed_origins}})

# Default credentials (can be overridden via request headers or environment)
# NOTE: These are placeholder values. In production, always use environment variables.
YOUR_LEAGUE_ID = int(os.getenv('ESPN_LEAGUE_ID', 0))
YOUR_TEAM_ID = int(os.getenv('ESPN_TEAM_ID', 0))
YOUR_YEAR = int(os.getenv('ESPN_YEAR', 2025))
YOUR_ESPN_S2 = os.getenv('ESPN_S2', '')
YOUR_SWID = os.getenv('ESPN_SWID', '')

def normalize_swid(swid):
    """Normalize SWID format - espn-api library expects curly brackets"""
    if not swid:
        return swid
    # Remove any existing brackets
    swid = swid.strip().strip('{}')
    # Add curly brackets if not present
    if not swid.startswith('{'):
        swid = '{' + swid
    if not swid.endswith('}'):
        swid = swid + '}'
    return swid

def get_league_and_team(espn_s2=None, swid=None, league_id=None, team_id=None, year=None):
    """Helper function to initialize league and get team"""
    # Use provided credentials or fall back to defaults
    espn_s2 = espn_s2 or YOUR_ESPN_S2
    swid = swid or YOUR_SWID
    # Normalize SWID format (add curly brackets if missing)
    swid_original = swid
    swid = normalize_swid(swid)
    if swid_original != swid:
        print(f"SWID normalized: '{swid_original[:30]}...' -> '{swid[:30]}...'")
    league_id = league_id or YOUR_LEAGUE_ID
    team_id = team_id or YOUR_TEAM_ID
    year = year or YOUR_YEAR
    
    # Log credentials being used (masked for security)
    print(f"Attempting ESPN connection - LeagueID: {league_id}, TeamID: {team_id}, Year: {year}")
    print(f"ESPNS2 length: {len(espn_s2)}, SWID format: {swid[:20]}...{swid[-5:] if len(swid) > 25 else swid}")
    print(f"SWID starts with {{: {swid.startswith('{')}, ends with }}: {swid.endswith('}')}")
    
    # Try direct HTTP first to verify credentials work
    test_url = f"https://fantasy.espn.com/apis/v3/games/ffl/seasons/{year}/segments/0/leagues/{league_id}"
    cookies = {'swid': swid, 'espn_s2': espn_s2}
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://fantasy.espn.com/football/',
        'Origin': 'https://fantasy.espn.com',
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.9'
    }
    
    # Verify credentials work with direct HTTP
    test_resp = requests.get(test_url, cookies=cookies, headers=headers, timeout=10)
    if test_resp.status_code != 200:
        raise Exception(f"ESPN API returned status {test_resp.status_code}. Credentials may be invalid.")
    
    print("Direct HTTP test passed - credentials are valid. Using espn-api library...")
    
    try:
        league = League(
            league_id=league_id,
            year=year,
            espn_s2=espn_s2,
            swid=swid
        )
    except Exception as e:
        error_msg = str(e)
        error_type = type(e).__name__
        print(f"ESPN League initialization error (type: {error_type}): {error_msg}")
        print(f"Full error details: {repr(e)}")
        
        # Since direct HTTP test passed, the library has an issue
        # Check if it's a 403 error from the library
        if '403' in error_msg or 'Forbidden' in error_msg:
            print("=" * 60)
            print("WARNING: espn-api library returned 403, but direct HTTP test passed!")
            print("This indicates a bug or incompatibility with the espn-api library.")
            print("Attempting to use direct HTTP requests as fallback...")
            print("=" * 60)
            # We'll handle this in the calling code by using direct HTTP
            raise Exception("ESPN library error: Direct HTTP works but library fails. This may be a library version issue.")
        elif '401' in error_msg or 'Unauthorized' in error_msg:
            raise Exception("ESPN returned HTTP 401: Your credentials are invalid.")
        else:
            raise Exception(f"ESPN API error: {error_msg}")
    
    team = None
    for t in league.teams:
        if t.team_id == team_id:
            team = t
            break
    
    if not team:
        return None, None, f'Team with ID {team_id} not found in league {league_id}'
    
    return league, team, None

@app.route('/api/espn/roster', methods=['GET'])
def get_my_roster():
    try:
        # Get credentials from request headers (sent by Go API)
        espn_s2 = request.headers.get('X-ESPN-S2')
        swid = request.headers.get('X-ESPN-SWID')
        league_id_str = request.headers.get('X-ESPN-LEAGUE-ID')
        team_id_str = request.headers.get('X-ESPN-TEAM-ID')
        year_str = request.headers.get('X-ESPN-YEAR')
        
        # Log received headers for debugging (mask credentials)
        print(f"Flask received headers - LeagueID: {league_id_str}, TeamID: {team_id_str}, Year: {year_str}")
        print(f"Flask received ESPNS2: {'present' if espn_s2 else 'MISSING'}, SWID: {'present' if swid else 'MISSING'}")
        
        # Validate required credentials
        if not espn_s2 or not swid:
            return jsonify({'error': f'Missing ESPN credentials - ESPNS2: {"present" if espn_s2 else "MISSING"}, SWID: {"present" if swid else "MISSING"}'}), 400
        
        # Normalize SWID format (espn-api expects curly brackets)
        swid_normalized = normalize_swid(swid)
        if swid != swid_normalized:
            print(f"SWID format normalized: {swid[:20]}... -> {swid_normalized[:20]}...")
        swid = swid_normalized
        
        if not league_id_str or not team_id_str or not year_str:
            return jsonify({'error': 'Missing league/team/year information'}), 400
        
        # Convert to appropriate types
        try:
            league_id = int(league_id_str)
            team_id = int(team_id_str)
            year = int(year_str)
        except ValueError as e:
            return jsonify({'error': f'Invalid league/team/year format: {str(e)}'}), 400
        
        league, team, error = get_league_and_team(
            espn_s2=espn_s2,
            swid=swid,
            league_id=league_id,
            team_id=team_id,
            year=year
        )
        if error:
            return jsonify({'error': error}), 404
        
        # Get current week for projections
        current_week = league.current_week
        
        # Create roster data list with projected and actual points
        roster_data = []
        for player in team.roster:
            # Get projected points for current week
            projected = 0
            actual = 0
            try:
                if hasattr(player, 'stats') and current_week in player.stats:
                    projected = player.stats[current_week].get('projected_points', 0)
                    actual = player.stats[current_week].get('points', 0)
                # Fallback to season averages
                if projected == 0:
                    projected = getattr(player, 'projected_avg_points', 0)
                if actual == 0:
                    actual = getattr(player, 'avg_points', 0)
            except:
                projected = getattr(player, 'projected_avg_points', 0)
                actual = getattr(player, 'avg_points', 0)
            
            player_data = {
                'name': player.name,
                'position': player.position,
                'proTeam': player.proTeam,
                'lineupSlot': player.lineupSlot,
                'projectedPoints': projected,
                'points': actual,
                'injured': getattr(player, 'injured', False),
                'injuryStatus': getattr(player, 'injuryStatus', None),
            }
            roster_data.append(player_data)
        
        return jsonify(roster_data)
    
    except Exception as e:
        error_msg = str(e)
        print(f"ESPN roster endpoint error: {error_msg}")
        # Check if it's an ESPN API error
        if '403' in error_msg or 'Forbidden' in error_msg:
            return jsonify({'error': 'ESPN returned HTTP 403. Your credentials may be expired or you don\'t have access to this league. Please get fresh ESPN cookies and reconnect your account.'}), 403
        elif '401' in error_msg or 'Unauthorized' in error_msg:
            return jsonify({'error': 'ESPN returned HTTP 401. Your credentials are invalid. Please reconnect your ESPN account.'}), 401
        else:
            return jsonify({'error': f'ESPN API error: {error_msg}'}), 500

@app.route('/api/espn/optimize-lineup', methods=['GET'])
def optimize_lineup():
    try:
        # Get credentials from request headers
        espn_s2 = request.headers.get('X-ESPN-S2')
        swid = request.headers.get('X-ESPN-SWID')
        league_id_str = request.headers.get('X-ESPN-LEAGUE-ID')
        team_id_str = request.headers.get('X-ESPN-TEAM-ID')
        year_str = request.headers.get('X-ESPN-YEAR')
        
        # Validate required credentials
        if not espn_s2 or not swid:
            return jsonify({'error': 'Missing ESPN credentials (espn_s2 or swid)'}), 400
        
        if not league_id_str or not team_id_str or not year_str:
            return jsonify({'error': 'Missing league/team/year information'}), 400
        
        # Normalize SWID format (espn-api expects curly brackets)
        swid = normalize_swid(swid)
        
        try:
            league_id = int(league_id_str)
            team_id = int(team_id_str)
            year = int(year_str)
        except ValueError as e:
            return jsonify({'error': f'Invalid league/team/year format: {str(e)}'}), 400
        
        league, team, error = get_league_and_team(
            espn_s2=espn_s2,
            swid=swid,
            league_id=league_id,
            team_id=team_id,
            year=year
        )
        if error:
            return jsonify({'error': error}), 404
        
        current_week = league.current_week
        
        # Get all players with their projections
        players = []
        for player in team.roster:
            projected = 0
            try:
                if hasattr(player, 'stats') and current_week in player.stats:
                    projected = player.stats[current_week].get('projected_points', 0)
                if projected == 0:
                    projected = getattr(player, 'projected_avg_points', 0)
            except:
                projected = getattr(player, 'projected_avg_points', 0)
            
            players.append({
                'name': player.name,
                'position': player.position,
                'proTeam': player.proTeam,
                'lineupSlot': player.lineupSlot,
                'eligibleSlots': player.eligibleSlots,
                'projectedPoints': projected,
                'injured': getattr(player, 'injured', False),
                'injuryStatus': getattr(player, 'injuryStatus', None),
                'playerId': getattr(player, 'playerId', None)
            })
        
        # Sort by projected points (highest first)
        players.sort(key=lambda x: x['projectedPoints'], reverse=True)
        
        # Define lineup requirements (typical ESPN lineup)
        lineup_slots = {
            'QB': 1,
            'RB': 2,
            'WR': 2,
            'TE': 1,
            'RB/WR/TE': 1,  # FLEX
            'D/ST': 1,
            'K': 1
        }
        
        optimal_lineup = []
        benched = []
        filled_slots = {slot: 0 for slot in lineup_slots.keys()}
        
        # First pass: Fill position-specific slots
        for player in players:
            if player['injured'] and player['injuryStatus'] in ['OUT', 'IR']:
                player['recommendedSlot'] = 'BE'
                benched.append(player)
                continue
            
            # Try to place in specific position slot
            if player['position'] in lineup_slots and filled_slots[player['position']] < lineup_slots[player['position']]:
                player['recommendedSlot'] = player['position']
                filled_slots[player['position']] += 1
                optimal_lineup.append(player)
            else:
                # Check if eligible for flex
                if 'RB/WR/TE' in player['eligibleSlots'] and filled_slots['RB/WR/TE'] < lineup_slots['RB/WR/TE']:
                    if player['position'] in ['RB', 'WR', 'TE']:
                        player['recommendedSlot'] = 'RB/WR/TE'
                        filled_slots['RB/WR/TE'] += 1
                        optimal_lineup.append(player)
                    else:
                        player['recommendedSlot'] = 'BE'
                        benched.append(player)
                else:
                    player['recommendedSlot'] = 'BE'
                    benched.append(player)
        
        return jsonify({
            'optimalLineup': optimal_lineup,
            'bench': benched,
            'totalProjected': sum(p['projectedPoints'] for p in optimal_lineup)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/espn/free-agents', methods=['GET'])
def get_free_agents():
    try:
        # Get credentials from request headers
        espn_s2 = request.headers.get('X-ESPN-S2')
        swid = request.headers.get('X-ESPN-SWID')
        league_id_str = request.headers.get('X-ESPN-LEAGUE-ID')
        team_id_str = request.headers.get('X-ESPN-TEAM-ID')
        year_str = request.headers.get('X-ESPN-YEAR')
        
        # Validate required credentials
        if not espn_s2 or not swid:
            return jsonify({'error': 'Missing ESPN credentials (espn_s2 or swid)'}), 400
        
        if not league_id_str or not team_id_str or not year_str:
            return jsonify({'error': 'Missing league/team/year information'}), 400
        
        # Normalize SWID format (espn-api expects curly brackets)
        swid = normalize_swid(swid)
        
        try:
            league_id = int(league_id_str)
            team_id = int(team_id_str)
            year = int(year_str)
        except ValueError as e:
            return jsonify({'error': f'Invalid league/team/year format: {str(e)}'}), 400
        
        league, team, error = get_league_and_team(
            espn_s2=espn_s2,
            swid=swid,
            league_id=league_id,
            team_id=team_id,
            year=year
        )
        if error:
            return jsonify({'error': error}), 404
        
        # Get query parameters
        position = request.args.get('position', None)  # Filter by position (QB, RB, WR, TE, K, D/ST)
        size = int(request.args.get('size', 50))  # Number of results (default 50)
        
        # Handle empty string as None
        if position == '':
            position = None
        
        current_week = league.current_week
        
        # Get free agents from the league
        # ESPN API provides free_agents method
        free_agents = league.free_agents(size=size, position=position)
        
        # Process free agent data
        free_agent_data = []
        for player in free_agents:
            projected = 0
            actual = 0
            try:
                if hasattr(player, 'stats') and current_week in player.stats:
                    projected = player.stats[current_week].get('projected_points', 0)
                    actual = player.stats[current_week].get('points', 0)
                if projected == 0:
                    projected = getattr(player, 'projected_avg_points', 0)
                if actual == 0:
                    actual = getattr(player, 'avg_points', 0)
            except:
                projected = getattr(player, 'projected_avg_points', 0)
                actual = getattr(player, 'avg_points', 0)
            
            player_data = {
                'name': player.name,
                'position': player.position,
                'proTeam': player.proTeam,
                'projectedPoints': projected,
                'points': actual,
                'injured': getattr(player, 'injured', False),
                'injuryStatus': getattr(player, 'injuryStatus', 'ACTIVE'),
                'playerId': getattr(player, 'playerId', None),
                'percentOwned': getattr(player, 'percent_owned', 0),
                'percentStarted': getattr(player, 'percent_started', 0),
            }
            free_agent_data.append(player_data)
        
        return jsonify({
            'players': free_agent_data,
            'count': len(free_agent_data)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/espn/ai-start-sit', methods=['POST'])
def ai_start_sit_advice():
    try:
        import requests
        
        data = request.get_json()
        player_a = data.get('playerA')
        player_b = data.get('playerB')
        
        if not player_a or not player_b:
            return jsonify({'error': 'Both playerA and playerB are required'}), 400
        
        # Build the AI prompt
        prompt = f"""You are an expert fantasy football advisor. Analyze these two players and recommend which one to START this week.

Player A: {player_a['name']} ({player_a['position']})
- Team: {player_a['proTeam']}
- Projected Points: {player_a['projectedPoints']:.1f}
- Season Average: {player_a['points']:.1f} PPG
- Current Slot: {player_a['lineupSlot']}
- Injury Status: {player_a.get('injuryStatus', 'Healthy')}
- Injured: {'Yes' if player_a.get('injured') else 'No'}

Player B: {player_b['name']} ({player_b['position']})
- Team: {player_b['proTeam']}
- Projected Points: {player_b['projectedPoints']:.1f}
- Season Average: {player_b['points']:.1f} PPG
- Current Slot: {player_b['lineupSlot']}
- Injury Status: {player_b.get('injuryStatus', 'Healthy')}
- Injured: {'Yes' if player_b.get('injured') else 'No'}

Provide your recommendation in EXACTLY this format:
RECOMMENDATION: [A or B]
CONFIDENCE: [number from 0-100]
REASONING: [2-3 sentences explaining your choice, focusing on projected points, matchup, health, and recent performance]

Be concise and direct."""

        # Call Gemini API
        gemini_api_key = os.getenv('GEMINI_API_KEY')
        if not gemini_api_key:
            return jsonify({'error': 'Gemini API key not configured'}), 500
        
        gemini_url = f'https://generativelanguage.googleapis.com/v1/models/gemini-2.0-flash:generateContent?key={gemini_api_key}'
        
        gemini_request = {
            'contents': [{
                'parts': [{'text': prompt}]
            }],
            'generationConfig': {
                'temperature': 0.7,
                'topK': 40,
                'topP': 0.95
            }
        }
        
        response = requests.post(gemini_url, json=gemini_request, timeout=30)
        
        if response.status_code != 200:
            return jsonify({'error': f'Gemini API error: {response.text}'}), 500
        
        gemini_response = response.json()
        
        if not gemini_response.get('candidates') or len(gemini_response['candidates']) == 0:
            return jsonify({'error': 'No response from Gemini'}), 500
        
        ai_text = gemini_response['candidates'][0]['content']['parts'][0]['text']
        
        # Parse the AI response
        recommendation = 'A'
        confidence = 50
        reasoning = ai_text
        
        # Extract structured data from response
        lines = ai_text.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('RECOMMENDATION:'):
                rec = line.split(':', 1)[1].strip().upper()
                if 'A' in rec:
                    recommendation = 'A'
                elif 'B' in rec:
                    recommendation = 'B'
            elif line.startswith('CONFIDENCE:'):
                try:
                    conf_str = line.split(':', 1)[1].strip().replace('%', '')
                    confidence = int(conf_str)
                except:
                    pass
            elif line.startswith('REASONING:'):
                reasoning = line.split(':', 1)[1].strip()
        
        return jsonify({
            'recommendation': recommendation,
            'confidence': confidence,
            'reasoning': reasoning,
            'playerAName': player_a['name'],
            'playerBName': player_b['name']
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Use PORT environment variable (Railway provides this) or default to 5002
    port = int(os.getenv('PORT', 5002))
    app.run(host='0.0.0.0', port=port, debug=False)
