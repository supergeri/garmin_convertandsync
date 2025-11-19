"""FastAPI wrapper for Garmin Sync API."""
from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
from typing import Optional, List, Dict
import logging

from garmin_planner.client import Client
from garmin_planner.main import importWorkouts, scheduleWorkouts, createWorkoutJson
from garmin_planner.model.workoutModel import SportType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Garmin Sync API", version="0.1.0")


class LoginRequest(BaseModel):
    email: str
    password: str


class WorkoutRequest(BaseModel):
    name: str
    steps: List
    sport: Optional[str] = None


class ImportWorkoutsRequest(BaseModel):
    email: str
    password: str
    workouts: Dict
    delete_same_name: bool = False


class ScheduleRequest(BaseModel):
    email: str
    password: str
    start_from: str  # YYYY-MM-DD
    workouts: List[str]


@app.get("/")
async def root():
    return {"service": "Garmin Sync API", "version": "0.1.0"}


@app.get("/health")
async def health():
    return {"status": "healthy", "service": "garmin-sync"}


@app.post("/workouts")
async def get_workouts(request: LoginRequest):
    """Get all workouts for a user."""
    try:
        client = Client(request.email, request.password)
        workouts = client.getAllWorkouts()
        return {"workouts": workouts}
    except Exception as e:
        logger.error(f"Error getting workouts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/workouts/{workout_id}")
async def get_workout(workout_id: str, email: str, password: str):
    """Get a specific workout by ID."""
    try:
        client = Client(email, password)
        workout = client.getWorkout(workout_id)
        return {"workout": workout}
    except Exception as e:
        logger.error(f"Error getting workout: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/workouts/import")
async def import_workouts(request: ImportWorkoutsRequest):
    """Import workouts to Garmin Connect."""
    try:
        client = Client(request.email, request.password)
        importWorkouts(request.workouts, request.delete_same_name, client)
        return {"status": "success", "message": "Workouts imported successfully"}
    except Exception as e:
        logger.error(f"Error importing workouts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/workouts/schedule")
async def schedule_workouts(request: ScheduleRequest):
    """Schedule workouts on Garmin Connect."""
    try:
        client = Client(request.email, request.password)
        scheduleWorkouts(request.start_from, request.workouts, client)
        return {"status": "success", "message": "Workouts scheduled successfully"}
    except Exception as e:
        logger.error(f"Error scheduling workouts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/workouts/create")
async def create_workout(
    name: str = Body(...),
    steps: List = Body(...),
    sport: Optional[str] = Body(None)
):
    """Create workout JSON (does not import to Garmin)."""
    try:
        sport_type = None
        if sport:
            sport_upper = sport.upper()
            if sport_upper == "HIIT":
                sport_type = SportType.HIIT
            elif sport_upper in ["STRENGTH", "STRENGTH_TRAINING"]:
                sport_type = SportType.STRENGTH
            elif sport_upper in ["RUNNING", "RUN"]:
                sport_type = SportType.RUNNING
        
        workout_json = createWorkoutJson(name, steps, sport_type)
        return {"workout": workout_json}
    except Exception as e:
        logger.error(f"Error creating workout: {e}")
        raise HTTPException(status_code=500, detail=str(e))

