from typing import Final
from enum import Enum

# URLS
POST_LOGIN_URL: Final[str] = "https://sso.garmin.com/portal/api/login?clientId=GarminConnect&locale=en-US&service=https%3A%2F%2Fconnect.garmin.com%2Fmodern"
GET_HOME_URL: Final[str] = "https://connect.garmin.com/modern"
POST_EXCHANGE_URL: Final[str] = "https://connect.garmin.com/modern/di-oauth/exchange"
POST_REFRESH_URL: Final[str] = "https://connect.garmin.com/services/auth/token/refresh"
POST_CREATE_WORKOUT_URL: Final[str] = "https://connect.garmin.com/workout-service/workout"
POST_SCHEDULE_WORKOUT_URL: Final[str] = "https://connect.garmin.com/workout-service/schedule"
GET_ALL_WORKOUT_URL: Final[str] = "https://connect.garmin.com/workout-service/workouts?start=1&limit=999&myWorkoutsOnly=true&sharedWorkoutsOnly=false&orderBy=WORKOUT_NAME&orderSeq=ASC&includeAtp=false"
DELETE_WORKOUT_URL: Final[str] = "https://connect.garmin.com/workout-service/workout"

# A constnat used to convert pace to certain value recognised by garmin connect
PACE_CONST = 16.66666

DATE_FORMAT = "%Y-%m-%d"

# Workout data 
class SportType(Enum):
    RUNNING = {
      "sportTypeId": 1,
      "sportTypeKey": "running",
      "displayOrder": 1
    }

    def to_dict(self):
        return self.value


class DistanceUnit(Enum):
    KILOMETER = {
      "unitKey": "kilometer"
    }
    MILE = {
      "unitKey": "mile"
    },

    def to_dict(self):
        return self.value

class StepType(Enum):
    WARMUP = {
        "stepTypeId": 1,
        "stepTypeKey": "warmup",
        "displayOrder": 1
    }
    COOLDOWN = {
        "stepTypeId": 2,
        "stepTypeKey": "cooldown",
        "displayOrder": 2
    }
    INTERVAL = {
        "stepTypeId": 3,
        "stepTypeKey": "interval",
        "displayOrder": 3
    }
    RECOVERY = {
        "stepTypeId": 4,
        "stepTypeKey": "recovery",
        "displayOrder": 4
    }
    REPEAT = {
        "stepTypeId": 6,
        "stepTypeKey": "repeat",
        "displayOrder": 6
    }

    def to_dict(self):
        return self.value


class ConditionType(Enum):
    LAP_BUTTON = {
        "conditionTypeId": 1,
        "conditionTypeKey": "lap.button",
        "displayOrder": 1,
        "displayable": True
    }
    TIME = {
        "conditionTypeId": 2,
        "conditionTypeKey": "time",
        "displayOrder": 2,
        "displayable": True
    }
    DISTANCE = {
        "conditionTypeId": 3,
        "conditionTypeKey": "distance",
        "displayOrder": 3,
        "displayable": True
    }
    ITERATION_ENDS = {
        "conditionTypeId": 7,
        "conditionTypeKey": "iterations",
        "displayOrder": 7,
        "displayable": False
    }

    def to_dict(self):
        return self.value


class TargetType(Enum):
    NO_TARGET = {
        "workoutTargetTypeId": 1,
        "workoutTargetTypeKey": "no.target",
        "displayOrder": 1
    }
    # This need targetValueOne, Two
    PACE = {
        "workoutTargetTypeId": 6,
        "workoutTargetTypeKey": "pace.zone",
        "displayOrder": 6
    }
    HEART_RATE_ZONE = {
        "workoutTargetTypeId": 4,
        "workoutTargetTypeKey": "heart.rate.zone",
        "displayOrder": 4
    }

    def to_dict(self):
        return self.value