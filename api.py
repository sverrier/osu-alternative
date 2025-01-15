import requests
import time
import json
import user

class util_api:
    def __init__(self, client, key, delay):
        self.client = client
        self.key = key 
        self.delay = delay
    
    def refresh_token(self):
        try:
            url = "https://osu.ppy.sh/oauth/token"
            json_input_string = {
                "grant_type": "client_credentials",
                "client_id": "10010",
                "client_secret": "vv5RulzDxXSuIuqQq19jSDFvUYXOJYVfqhHPXETD",
                "scope": "public"
            }

            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }

            response = requests.post(url, headers=headers, data=json.dumps(json_input_string))
            time.sleep(self.delay) 

            if response.status_code == 200:
                json_response = response.json()
                token = json_response.get("access_token")
                print(token)
                self.token = token 

            else: 
                print(response.status_code)

        except Exception as e:
            print(e)

    def get_user(self, user_id):
        complete = False
        u = None
        magnitude = 1
        backoff = 2  # Assuming a backoff value, adjust as necessary
        
        while not complete:
            try:
                url = f"https://osu.ppy.sh/api/v2/users/{user_id}/osu"
                headers = {
                    "Authorization": f"Bearer {self.token}"  
                }
                
                response = requests.get(url, headers=headers)
                status = response.status_code

                time.sleep(self.delay)
                if status == 200:
                    json_response = response.json()
                    if not json_response:
                        return None
                    u = user.User(json_response)
                else:
                    raise Exception(f"Unexpected response code: {status}")
                
                complete = True
                magnitude = 1

            except Exception as e:
                print(e)
                self.delay = backoff * magnitude
                time.sleep(self.delay)
                magnitude += 1
                self.refresh_token()
        
        return u