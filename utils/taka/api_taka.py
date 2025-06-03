import requests
from utils.taka.auth_taka import HEADERS

API_URL = "https://api.taka.io/proscore"

def get_user_clubs(token, cookies):
    headers = HEADERS.copy()
    headers['authorization'] = ''  # como en curl
    headers['cookie'] = build_cookie_header(token, cookies)

    query = {
        "operationName": "me",
        "variables": {},
        "query": """query me {
            me {
                id
                firstName
                lastName
                username
                picture
                email
                onboarded
                downloadOnBoarded
                forcePasswordChangeOnLogin
                club { id name __typename }
                tocAccepted
                wantToReceiveUpdates
                defaultTeams {
                    id name
                    info {
                        category { id __typename }
                        __typename
                    }
                    __typename
                }
                roles
                stripeCustomerId
                dob
                isVerified
                player {
                    id mongoId dob isU13
                    clubs { id name __typename }
                    parentEmail parentConsentProvided parentConsentTime
                    detailsPerSeason {
                        id season seasonName position
                        club { id name __typename }
                        category { id name __typename }
                        organisations { id name __typename }
                        currentTeams { teamId teamName __typename }
                        __typename
                    }
                    picture
                    __typename
                }
                createdAt
                permissions {
                    accessMyDownloads proInCurrentSeason requiredPlayerInfo
                    requiredSurvey requiredUserInformation isMLS viewUnclaimedProfile
                    accessDataCollectionFeatureFlag
                    organisations { id name __typename }
                    colleges { id name __typename }
                    pages
                    __typename
                }
                loginByEmail
                __typename
            }
        }"""
    }

    print("▶️ LLAMANDO a get_user_clubs")
    print("HEADERS:\n", headers)
    print("QUERY:\n", query["query"])

    try:
        response = requests.post(API_URL, json=query, headers=headers)
        print("✅ STATUS:", response.status_code)
        print("🔁 RESPONSE JSON:", response.text)
        return response.json()
    except Exception as e:
        print("❌ ERROR en get_user_clubs:", e)
        return None

def build_cookie_header(token, cookies):
    # reconstruye lo que ves en curl: todas las cookies claves
    all_cookies = cookies.copy()
    all_cookies['auth_token'] = token

    return "; ".join(f"{k}={v}" for k, v in all_cookies.items())



def get_game_video(token, cookies, game_id):
    headers = HEADERS.copy()
    headers['cookie'] = f"auth_token={token}"

    query = {
        "operationName": "GameHighlights",
        "variables": {"game_id": game_id},
        "query": """
        query GameHighlights($game_id: Int!) {
          gameHighlights(game_id: $game_id) {
            id
            video_id
            sources {
              src
              type
            }
          }
        }
        """
    }

    response = requests.post(API_URL, json=query, headers=headers, cookies=cookies)
    return response.json()
