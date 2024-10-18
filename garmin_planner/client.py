from garmin_planner import constant
from garmin_planner.__init__ import logger
import requests
import pickle
import os
import datetime
import sys

SESSION_FILE = 'session.pkl'

def isTokenExpired(dt: datetime, sec: int):
    return (dt + datetime.timedelta(seconds=sec) < datetime.datetime.now())

class Client(object):
    timeout = 5
    _token = {"token": "", "expiry": 0}
    _refreshToken =  {"token": "", "expiry": 0}
    _lastLoggedIn =  None
    baseHeader = {
        'User-Agent' : "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
        'Accept-Language': "en-US,en;q=0.9",
    }
    getHeader = {
        **baseHeader,
        'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    }
    postHeader = {
        **baseHeader,
        'Content-Type': 'application/json',
        'Origin' : "https://connect.garmin.com",
        'Di-Backend' : "connectapi.garmin.com",
        'Accept': "application/json, text/plain, */*",
    }

    def __init__(self, email, password):
        self.restClient = requests.Session()
        self.email = email
        self.password = password

        # load session if last logged in
        self.tryLoadsession()
    
    def isAuthenticated(self) -> bool:
        if isinstance(self._lastLoggedIn, datetime.datetime): 
            return not isTokenExpired(self._lastLoggedIn, self._token['expiry'])
        return False
    
    def getAllWorkouts(self) -> dict:
        if not self.isAuthenticated():
            isSuccess = self.login()
            if not isSuccess:
                return {}
        res = self.restClient.get(
            constant.GET_ALL_WORKOUT_URL, 
            headers=self.getAuthenticatedGetHeader(), 
            timeout=self.timeout)
        res.raise_for_status() 
        resJson = res.json()
        return resJson

    def getTokenHeader(self):
        return {'Authorization': f"Bearer {self._token['token']}"}

    def getAuthenticatedGetHeader(self):
        return {'x-requested-with': "XMLHttpRequest", **self.getTokenHeader(),
                **self.postHeader}
    
    def getAuthenticatedPostHeader(self):
        return {**self.postHeader, **self.getTokenHeader()}
    
    def deleteWorkout(self, workout: dict) -> bool:
        if not self.isAuthenticated():
            isSuccess = self.login()
            if not isSuccess:
                return False
        res = self.restClient.delete(f"""{constant.DELETE_WORKOUT_URL}/{workout['workoutId']}""", 
                                   headers=self.getAuthenticatedPostHeader(), 
                                   timeout=self.timeout)
        res.raise_for_status() 
        if (res.status_code != 204):
            return False
        
        logger.info(f"""Deleted workoutId: {workout['workoutId']} workoutName: {workout['workoutName']}""")
        return True

    def postScheduleWorkout(self, id, dateJson: dict) -> bool:
        if not self.isAuthenticated():
            isSuccess = self.login()
            if not isSuccess:
                return False
        res = self.restClient.post(f"""{constant.POST_SCHEDULE_WORKOUT_URL}/{id}""", 
                                   headers=self.getAuthenticatedPostHeader(), 
                                   json=dateJson, timeout=self.timeout)
        res.raise_for_status() 
        resJson = res.json()
        if ('workoutScheduleId' not in resJson):
            return False
        return True
    
    def tryLoadsession(self):
        try:
            if os.path.exists(SESSION_FILE):
                # Load the session from a file
                with open('session.pkl', 'rb') as f:
                    session_data = pickle.load(f)
                    self.restClient.cookies.update(session_data['cookies'])
                    self._token = (session_data['token'])
                    self._refreshToken = (session_data['refresh'])
                    self._lastLoggedIn = (session_data['loginTime'])
        except Exception as e:
            logger.error(e)

    
    def importWorkout(self, workoutJson) -> dict:
        if not self.isAuthenticated():
            isSucccess = self.login()
            if not isSucccess:
                return {}
        res = self.restClient.post(constant.POST_CREATE_WORKOUT_URL, 
                                   headers=self.getAuthenticatedPostHeader(), 
                                   data=workoutJson, timeout=self.timeout)
        res.raise_for_status() 
        resJson = res.json()
        logger.info(f"""Imported workout {resJson['workoutName']}""")
        return resJson
    
    def refreshToken(self) -> bool:
        try:
            postData = {"refresh_token": self._refreshToken['token']}
            res = self.restClient.post(constant.POST_REFRESH_URL, headers=self.postHeader, json=postData, timeout=self.timeout)
            res.raise_for_status() 
            resJson = res.json()  
            self._token = {"token": resJson['access_token'],
                "expiry": resJson['expires_in'], }
            self._refreshToken = {"token": resJson['refresh_token'],
                "expiry": resJson['refresh_token_expires_in'], }
            self._lastLoggedIn =datetime.datetime.now()
            logger.info("refreshed token")
            return True
        except Exception as e:
            logger.error("refreshing token failed")
            return False

    # Garmin Connect Login flow
    # 1. Login with credentials
    # 2. Direct to homepage 
    # 3. Call exchanged api for tokens (access token here expire in 5m)
    # 4. Call refresh token (access token last 1h)
    def login(self) -> bool:
        loginCredentials = {
            "username": self.email,
            "password": self.password,
            "rememberMe": 'false',
            "captchaToken": ""}

        try:
            # check whether to refresh token
            if isinstance(self._lastLoggedIn, datetime.datetime) and \
                    not isTokenExpired(self._lastLoggedIn, self._refreshToken['expiry']):
                    isSuccess = self.refreshToken()
                    if (isSuccess):
                        return True

            res = self.restClient.post(constant.POST_LOGIN_URL, headers=self.postHeader, json=loginCredentials, timeout=self.timeout)
            res.raise_for_status() 
            resJson = res.json()  
            ticketId = resJson["serviceTicketId"]
            if (resJson['responseStatus']['type'] != "SUCCESSFUL"):
                logger.error("Login failed")
                sys.exit("Exited program due login failed")
                return False

            # To home page
            res = self.restClient.get(
                f"{constant.GET_HOME_URL}?ticket={ticketId}", 
                timeout=self.timeout,
                headers=self.getHeader
                )
            res.raise_for_status() 

            res = self.restClient.post(
                constant.POST_EXCHANGE_URL, timeout=self.timeout,
                headers=self.getHeader)
            res.raise_for_status() 
            resJson = res.json()  
            if ("access_token" not in resJson or 
                "refresh_token" not in resJson):
                logger.error("Login failed")
                sys.exit("Exited program due login failed")
                return False
            
            self._token = {
                "token": resJson['access_token'],
                "expiry": resJson['expires_in'],
                }
            self._refreshToken = {
                "token": resJson['refresh_token'],
                "expiry": resJson['refresh_token_expires_in'],
                }

            # refresh token
            self.refreshToken()

            # Save session data (cookies, headers, etc.)
            session_data = {
                'cookies': self.restClient.cookies,
                'token': self._token,
                'refresh': self._refreshToken,
                'loginTime': datetime.datetime.now()
            }
            
            with open(SESSION_FILE, 'wb') as f:
                pickle.dump(session_data, f)

            logger.info("Logged in")
            return True
        except requests.exceptions.Timeout:
            logger.error("Login request timed out")
            sys.exit("Exited program due login failed")
            return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Login request failed: {e}")
            sys.exit("Exited program due login failed")
            return False