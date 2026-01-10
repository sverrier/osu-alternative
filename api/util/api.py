import requests
import time
import json

import json
import time
import requests


class util_api:
    def __init__(self, config):
        self.client = config["CLIENT"]
        self.key = config["KEY"]
        self.delay = float(config["DELAY"]) / 1000
        self.dbname = config["DBNAME"]
        self.username = config["USERNAME"]
        self.password = config["PASSWORD"]
        self.token = ""
        self._auth_mode = "client"
        self._user_refresh_token = None

    # -------------------
    # Auth mode switching
    # -------------------

    def use_client_token(self):
        """
        Switch back to client_credentials behavior.
        Keeps the currently loaded token, but enables client refresh on retry.
        """
        self._auth_mode = "client"
        self._user_refresh_token = None

    def use_user_token(self, access_token: str, refresh_token: str | None = None):
        """
        Force all requests to use the provided user access token.
        In user mode we NEVER fallback to client_credentials on retry.
        """
        self._auth_mode = "user"
        self.token = access_token
        self._user_refresh_token = refresh_token

    # -------------------
    # Refresh operations
    # -------------------

    def refresh_client_token(self):
        """
        Client Credentials grant (app token).
        NOTE: osu! expects form-encoded for /oauth/token; JSON often works on some servers
        but keeping it form-encoded is safest/standard.
        """
        try:
            url = "https://osu.ppy.sh/oauth/token"
            data = {
                "grant_type": "client_credentials",
                "client_id": self.client,
                "client_secret": self.key,
                "scope": "public",
            }
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
            }

            response = requests.post(url, headers=headers, data=data, timeout=30)
            time.sleep(self.delay)

            if response.status_code == 200:
                json_response = response.json()
                self.token = json_response.get("access_token", "")
                return json_response
            else:
                raise RuntimeError(f"Client token refresh failed ({response.status_code}): {response.text}")

        except Exception as e:
            print(e)
            raise

    def refresh_user_token(self, refresh_token: str):
        """
        Refresh a USER OAuth token using grant_type=refresh_token.

        Returns:
            dict with access_token, refresh_token, expires_in, token_type, scope
        """
        try:
            url = "https://osu.ppy.sh/oauth/token"

            data = {
                "grant_type": "refresh_token",
                "client_id": self.client,
                "client_secret": self.key,
                "refresh_token": refresh_token,
            }

            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
            }

            response = requests.post(url, data=data, headers=headers, timeout=30)
            time.sleep(self.delay)

            if response.status_code != 200:
                raise RuntimeError(
                    f"User token refresh failed ({response.status_code}): {response.text}"
                )

            json_response = response.json()

            # Apply new access token
            self.token = json_response["access_token"]

            # Refresh-token rotation: store the new refresh token if present
            new_refresh = json_response.get("refresh_token")
            if new_refresh:
                self._user_refresh_token = new_refresh

            return json_response

        except Exception as e:
            print(f"refresh_user_token error: {e}")
            raise

    # -----------------------------------------
    # Unified refresh helper for request retries
    # -----------------------------------------

    def refresh_token(self):
        """
        Refresh whichever token is appropriate for the current auth mode.

        - client mode => refresh_client_token()
        - user mode   => refresh_user_token(self._user_refresh_token)

        IMPORTANT:
        In user mode, we do NOT fallback to client tokens. If we can't refresh
        (missing refresh token), we raise so callers can handle it.
        """
        if self._auth_mode == "client":
            return self.refresh_client_token()

        # user mode
        if not self._user_refresh_token:
            raise RuntimeError("Cannot refresh user token: _user_refresh_token is not set")
        return self.refresh_user_token(self._user_refresh_token)

    # -----------------------------------------
    # Optional: wrapper for your request exception blocks
    # -----------------------------------------

    def _handle_request_exception(self, e: Exception, magnitude: int):
        """
        Call from your except blocks to centralize sleep/backoff + refresh.
        """
        print(e)
        time.sleep(self.delay * magnitude)
        magnitude += 5

        # Refresh correct token for current mode
        self.refresh_token()

        return magnitude


    def get_user(self, user_id, mode):
        complete = False
        magnitude = 1
        
        while not complete:
            try:
                url = f"https://osu.ppy.sh/api/v2/users/{user_id}/{mode}"
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
                magnitude = self._handle_request_exception(e, magnitude)

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

                time.sleep(2)
                if status == 200:
                    json_response = response.json()
                    if not json_response:
                        return None
                else:
                    raise Exception(f"Unexpected response code: {status}")
                
                complete = True
                magnitude = 1

            except Exception as e:
                magnitude = self._handle_request_exception(e, magnitude)
        
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
                magnitude = self._handle_request_exception(e, magnitude)
        
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
                magnitude = self._handle_request_exception(e, magnitude)
        
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

                time.sleep(0.7)
                if status == 200:
                    json_response = response.json()
                    if not json_response:
                        return None
                else:
                    raise Exception(f"Unexpected response code: {status}") 
                
                complete = True
                magnitude = 1

            except Exception as e:
                magnitude = self._handle_request_exception(e, magnitude)
        
        return json_response
    
    
    def get_beatmapsets(self, cursor_string=None):
        complete = False
        magnitude = 1

        while not complete:
            try:
                url = "https://osu.ppy.sh/api/v2/beatmapsets/search?nsfw=true"
                if cursor_string is not None:
                    url = url + "&cursor_string=" + cursor_string
                
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
                magnitude = self._handle_request_exception(e, magnitude)
        
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
                magnitude = self._handle_request_exception(e, magnitude)
        
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
                magnitude = self._handle_request_exception(e, magnitude)
        
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
                magnitude = self._handle_request_exception(e, magnitude)
        
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
                magnitude = self._handle_request_exception(e, magnitude)
        
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
                magnitude = self._handle_request_exception(e, magnitude)
        
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
                magnitude = self._handle_request_exception(e, magnitude)
        
        return json_response

