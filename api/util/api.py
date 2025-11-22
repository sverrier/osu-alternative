import requests
import time
import json

class util_api:
    def __init__(self, config):
        self.client = config["CLIENT"]
        self.key = config["KEY"]
        self.delay = float(config["DELAY"]) / 1000
        self.dbname = config["DBNAME"]
        self.username = config["USERNAME"]
        self.password = config["PASSWORD"]
        self.token = ""

    
    def refresh_token(self):
        try:
            url = "https://osu.ppy.sh/oauth/token"
            json_input_string = {
                "grant_type": "client_credentials",
                "client_id": self.client,
                "client_secret": self.key,
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
                self.token = token 

            else: 
                print(response.status_code)

        except Exception as e:
            print(e)

    def get_user(self, user_id):
        complete = False
        magnitude = 1
        
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
                else:
                    raise Exception(f"Unexpected response code: {status}")
                
                complete = True
                magnitude = 1

            except Exception as e:
                print(e)
                time.sleep(self.delay * magnitude)
                magnitude += 5
                self.refresh_token()
        
        return json_response

    def get_users(self, ids):
        complete = False
        magnitude = 1

        # Format the IDs into the query string
        id_query = "&".join([f"ids[]={id}" for id in ids])
        
        while not complete:
            try:
                url = f"https://osu.ppy.sh/api/v2/users?" + id_query
                headers = {
                    "Authorization": f"Bearer {self.token}"  
                }
                
                response = requests.get(url, headers=headers)
                status = response.status_code

                time.sleep(1)
                if status == 200:
                    json_response = response.json()
                    if not json_response:
                        return None
                else:
                    raise Exception(f"Unexpected response code: {status}")
                
                complete = True
                magnitude = 1

            except Exception as e:
                print(e)
                time.sleep(self.delay * magnitude)
                magnitude += 5
                self.refresh_token()
        
        return json_response
    
    def get_user_beatmaps_most_played(self, user, limit, offset):
        complete = False
        magnitude = 1

        # Format the IDs into the query string
        
        while not complete:
            try:
                url = f"https://osu.ppy.sh/api/v2/users/{user}/beatmapsets/most_played?limit={limit}&offset={offset}"
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
                else:
                    raise Exception(f"Unexpected response code: {status}") 
                
                complete = True
                magnitude = 1

            except Exception as e:
                print(e)
                time.sleep(self.delay * magnitude)
                magnitude += 5
                self.refresh_token()
        
        return json_response

    def get_beatmap(self, beatmap_id):
        complete = False
        magnitude = 1
        
        while not complete:
            try:
                url = f"https://osu.ppy.sh/api/v2/beatmaps/{beatmap_id}"
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
                else:
                    raise Exception(f"Unexpected response code: {status}")
                
                complete = True
                magnitude = 1

            except Exception as e:
                print(e)
                time.sleep(self.delay * magnitude)
                magnitude += 5
                self.refresh_token()
        
        return json_response

    def get_beatmaps(self, ids):
        complete = False
        magnitude = 1

        # Format the IDs into the query string
        id_query = "&".join([f"ids[]={id}" for id in ids])
        
        while not complete:
            try:
                url = f"https://osu.ppy.sh/api/v2/beatmaps?" + id_query
                headers = {
                    "Authorization": f"Bearer {self.token}"  
                }
                
                response = requests.get(url, headers=headers)
                status = response.status_code

                time.sleep(1)
                if status == 200:
                    json_response = response.json()
                    if not json_response:
                        return None
                else:
                    raise Exception(f"Unexpected response code: {status}") 
                
                complete = True
                magnitude = 1

            except Exception as e:
                print(e)
                time.sleep(self.delay * magnitude)
                magnitude += 5
                self.refresh_token()
        
        return json_response

    def get_beatmap_scores(self, beatmap_id):
        complete = False
        magnitude = 1
        
        while not complete:
            try:
                url = f"https://osu.ppy.sh/api/v2/beatmaps/{beatmap_id}/scores?limit=100"
                headers = {
                    "Authorization": f"Bearer {self.token}",
                    "x-api-version": "20240529"
                }
                
                response = requests.get(url, headers=headers)
                status = response.status_code

                time.sleep(self.delay)
                if status == 200:
                    json_response = response.json()
                    if not json_response:
                        return None
                    scores = json_response.get("scores", [])

                else:
                    raise Exception(f"Unexpected response code: {status}")
                
                complete = True
                magnitude = 1

            except Exception as e:
                print(e)
                time.sleep(self.delay * magnitude)
                magnitude += 5
                self.refresh_token()
        
        return scores
    
    def get_beatmap_modded_scores(self, beatmap_id, mods):
        """
        Get beatmap scores filtered by mods.
        
        Args:
            beatmap_id: The beatmap ID
            mods: List of mod acronyms (e.g., ['HD', 'DT', 'HR'])
        
        Returns:
            List of scores matching the mod combination
        """
        complete = False
        magnitude = 1
        
        while not complete:
            try:
                base_url = f"https://osu.ppy.sh/api/v2/beatmaps/{beatmap_id}/scores?legacy_only=0&limit=100"
                
                # Add each mod as a separate query parameter
                if mods:
                    mod_params = "&".join([f"mods[]={mod}" for mod in mods])
                    url = f"{base_url}&{mod_params}"
                else:
                    url = base_url
                
                headers = {
                    "Authorization": f"Bearer {self.token}",
                    "x-api-version": "20240529"
                }
                
                response = requests.get(url, headers=headers)
                status = response.status_code

                time.sleep(self.delay)
                
                if status == 200:
                    json_response = response.json()
                    if not json_response:
                        return None
                    
                    scores = json_response.get("scores", [])
                    complete = True
                    magnitude = 1
                    return scores
                else:
                    raise Exception(f"Unexpected response code: {status}")

            except Exception as e:
                print(e)
                time.sleep(self.delay * magnitude)
                magnitude += 5
                self.refresh_token()
        
        return []
    
    def get_beatmap_packs(self, cursor_string = None):
        complete = False
        magnitude = 1
        
        while not complete:
            try:
                url = f"https://osu.ppy.sh/api/v2/beatmaps/packs"
                if cursor_string != None:
                    url = url + "?cursor_string=" + cursor_string
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
                else:
                    raise Exception(f"Unexpected response code: {status}")
                
                complete = True
                magnitude = 1

            except Exception as e:
                print(e)
                time.sleep(self.delay * magnitude)
                magnitude += 5
                self.refresh_token()
        
        return json_response
    
    def get_beatmap_pack(self, tag):
        complete = False
        magnitude = 1
        
        while not complete:
            try:
                url = f"https://osu.ppy.sh/api/v2/beatmaps/packs/{tag}"
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
                else:
                    raise Exception(f"Unexpected response code: {status}")
                
                complete = True
                magnitude = 1

            except Exception as e:
                print(e)
                time.sleep(self.delay * magnitude)
                magnitude += 5
                self.refresh_token()
        
        return json_response

    def get_beatmap_user_scores(self, beatmap_id, user_id):
        complete = False
        magnitude = 1
        
        while not complete:
            try:
                url = f"https://osu.ppy.sh/api/v2/beatmaps/{beatmap_id}/scores/users/{user_id}/all"
                headers = {
                    "Authorization": f"Bearer {self.token}",
                    "x-api-version": "20240529"
                }
                
                response = requests.get(url, headers=headers)
                status = response.status_code

                time.sleep(self.delay)
                if status == 200:
                    json_response = response.json()
                    if not json_response:
                        return None
                    scores = json_response.get("scores", [])

                else:
                    raise Exception(f"Unexpected response code: {status}")
                
                complete = True
                magnitude = 1

            except Exception as e:
                print(e)
                time.sleep(self.delay * magnitude)
                magnitude += 5
                self.refresh_token()
        
        return scores

    def get_scores(self, cursor_string = None):
        complete = False
        magnitude = 1
        
        while not complete:
            try:
                url = f"https://osu.ppy.sh/api/v2/scores" 
                if cursor_string != None:
                    url = url + "?cursor_string=" + cursor_string
                headers = {
                    "Authorization": f"Bearer {self.token}"  
                }

                print(url)
                
                response = requests.get(url, headers=headers)
                status = response.status_code

                time.sleep(1)
                if status == 200:
                    json_response = response.json()
                    if not json_response:
                        return None
                else:
                    raise Exception(f"Unexpected response code: {status}")
                
                complete = True
                magnitude = 1

            except Exception as e:
                print(e)
                time.sleep(self.delay * magnitude)
                magnitude += 5
                self.refresh_token()
        
        return json_response

