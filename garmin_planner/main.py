from garmin_planner.client import Client
from garmin_planner.__init__ import logger
from garmin_planner.model.workoutModel import WorkoutModel, WorkoutSegment, WorkoutStep, RepeatStep
from garmin_planner.constant import *
from garmin_planner.parser import *
from enum import Enum as PyEnum
import re
import json
import datetime
import sys
import argparse
import os

__version__ = "0.1.0"

def replace_variables(data, definitionsDict: dict):
    if isinstance(data, str):
        return re.sub(r'\$(\w+)', lambda m: definitionsDict.get(m.group(1), m.group(0)), data)
    elif isinstance(data, dict):
        return {k: replace_variables(v, definitionsDict) for k, v in data.items()}
    elif isinstance(data, list):
        return [replace_variables(item, definitionsDict) for item in data]
    return data

# Serialize to JSON
def serialize(obj):
    # Support Python Enums and the library's enum-like classes
    if isinstance(obj, PyEnum):
        return obj.value if hasattr(obj, "value") else obj.name
    if hasattr(obj, "to_dict") and callable(getattr(obj, "to_dict")):
        return obj.to_dict()
    # Fallback for simple dataclasses/objects used by the library
    return getattr(obj, "__dict__", str(obj))

def createWorkoutList(steps: list, stepCount: list, inRepeat: bool = False):
    workoutSteps = []
    for _, step in enumerate(steps):
        workoutStep = createWorkoutStep(step, stepCount, inRepeat=inRepeat)
        if workoutStep:
            workoutSteps.append(workoutStep)
    return workoutSteps

def createWorkoutStep(step: dict, stepCount: list, inRepeat: bool = False):
    stepType = None
    exerciseName = None
    category = None
    for stepName in step:
        stepDetail = step[stepName]
        parsedStep, numIteration, explicitCategory = parse_bracket(stepName)
        match parsedStep:
            case "run":
                stepType = StepType.WARMUP
            case "warmup":
                stepType = StepType.WARMUP
                # Check if warmup has nested cardio or other exercises
                if isinstance(stepDetail, list):
                    # Check if there's a cardio child
                    for child in stepDetail:
                        for childName in child:
                            childParsed, _, _ = parse_bracket(childName)
                            if childParsed == "cardio":
                                category = "CARDIO"
                                exerciseName = ""  # Empty exercise name for cardio warmup
                                break
            case "cooldown":
                stepType = StepType.COOLDOWN
            case "recovery":
                stepType = StepType.RECOVERY
            case "exercise":
                stepType = StepType.INTERVAL  # Strength exercises use INTERVAL type
            case "rest":
                stepType = StepType.REST
            case "cardio":
                # Cardio should be treated as an exercise with category
                stepType = StepType.INTERVAL  # Use INTERVAL type for cardio exercises
                category = "CARDIO"
                # We don't set exerciseName for cardio as it's just a category
            case "repeat":
                stepType = StepType.REPEAT
                stepCount[0] += 1
                order = stepCount[0]
                workoutSteps = createWorkoutList(stepDetail, stepCount, inRepeat=True)
                # numIteration might be None if parse_bracket didn't find it
                iterations = int(numIteration) if numIteration else 1
                return RepeatStep(
                    stepId=order,
                    stepOrder=order,
                    workoutSteps=workoutSteps,
                    numberOfIterations=iterations
                )
            case _:
                # For unmatched names, treat as exercise for strength workouts
                # This allows custom exercise names like "Goblet Squat"
                stepType = StepType.INTERVAL  # Strength exercises use INTERVAL type
                # Use explicit category if provided in YAML, otherwise try to determine from exercise name
                if explicitCategory:
                    category = explicitCategory.upper()
                    # For explicit categories, still need to set exerciseName based on exercise name
                    # Special cases for sled and carry categories
                    if category == "SLED":
                        if "sled push" in parsedStep.lower():
                            exerciseName = "PUSH"
                        elif "sled" in parsedStep.lower() and "drag" in parsedStep.lower():
                            exerciseName = "BACKWARD_DRAG"
                    elif category == "CARRY":
                        if "farmer" in parsedStep.lower() and "carry" in parsedStep.lower():
                            exerciseName = "FARMERS_CARRY"
                    elif category == "SHOULDER_PRESS":
                        if "push press" in parsedStep.lower():
                            exerciseName = parsedStep.upper().replace(" ", "_").replace("-", "_")
                elif "bulgarian split squat" in parsedStep.lower():
                    category = "LUNGE"
                elif "good morning" in parsedStep.lower():
                    category = "LEG_CURL"
                elif "clean and jerk" in parsedStep.lower():
                    category = "OLYMPIC_LIFT"
                elif "medicine ball slam" in parsedStep.lower():
                    category = "PLYO"
                elif "ski moguls" in parsedStep.lower():
                    category = "CARDIO"
                elif "pike push" in parsedStep.lower() or "push-up" in parsedStep.lower():
                    category = "PUSH_UP"
                elif "plank" in parsedStep.lower():
                    category = "PLANK"
                elif "burpee" in parsedStep.lower():
                    category = "TOTAL_BODY"
                elif "inverted row" in parsedStep.lower() or "row" in parsedStep.lower():
                    category = "ROW"
                elif "squat" in parsedStep.lower():
                    category = "SQUAT"
                elif "push press" in parsedStep.lower():
                    category = "SHOULDER_PRESS"
                elif "press" in parsedStep.lower():
                    category = "BENCH_PRESS"
                elif "deadlift" in parsedStep.lower():
                    category = "DEADLIFT"
                elif "pull" in parsedStep.lower() or "lat" in parsedStep.lower():
                    category = "PULL_UP"
                    # For lat pull-down exercises, use underscore prefix and convert PULL_DOWN to PULLDOWN
                    # Convert exercise name to Garmin format (UPPER_CASE with underscores)
                    exerciseName = parsedStep.upper().replace(" ", "_").replace("-", "_")
                    if "lat" in parsedStep.lower() or "pull-down" in parsedStep.lower():
                        exerciseName = "_" + exerciseName.replace("PULL_DOWN", "PULLDOWN")
                elif "kettlebell" in parsedStep.lower():
                    # Check for specific kettlebell exercises
                    if "floor to shelf" in parsedStep.lower():
                        category = "DEADLIFT"
                    elif "swing" in parsedStep.lower():
                        category = "HIP_SWING"
                    else:
                        category = "SQUAT"  # Default for kettlebell exercises
                elif "push up" in parsedStep.lower() or "pushup" in parsedStep.lower():
                    category = "PUSH_UP"
                elif "sled push" in parsedStep.lower():
                    category = "SLED"
                    exerciseName = "PUSH"
                elif "sled" in parsedStep.lower() and "drag" in parsedStep.lower():
                    category = "SLED"
                    exerciseName = "BACKWARD_DRAG"
                elif "sled" in parsedStep.lower() or "drag" in parsedStep.lower():
                    category = None  # Not supported by Garmin
                elif "farmer" in parsedStep.lower() and "carry" in parsedStep.lower():
                    category = "CARRY"
                    exerciseName = "FARMERS_CARRY"
                elif "carry" in parsedStep.lower():
                    category = None  # Not supported by Garmin
                elif "push" in parsedStep.lower():
                    category = None  # Not supported by Garmin
                
                # Only set exerciseName if we have a category (category is our way of mapping)
                # Don't set exerciseName for unmapped exercises to avoid sending invalid data
                # Some categories like SLED and CARRY don't need exerciseName
                # Only set it if not explicitly provided by category matching above
                if category is not None and exerciseName is None:
                    # Special case: sled push needs exerciseName="PUSH"
                    if category == "SLED" and "sled push" in parsedStep.lower():
                        exerciseName = "PUSH"
                    # Categories that don't use exerciseName should leave it as None
                    elif category not in ["SLED", "CARRY"]:
                        # Convert exercise name to Garmin format (UPPER_CASE with underscores)
                        exerciseName = parsedStep.upper().replace(" ", "_").replace("-", "_")
                
                # Add more categories as needed
                logger.debug(f"Treating '{parsedStep}' as exercise with name '{exerciseName}', category '{category}'")

        # Handle stepDetail - could be a string or a list
        if isinstance(stepDetail, list):
            # Nested structure (like warmup with children)
            parsedStepDetailDict = {}
            # We'll use default values for the end condition
            if stepType == StepType.WARMUP or stepType == StepType.COOLDOWN:
                parsedStepDetailDict = {
                    'endCondition': ConditionType.LAP_BUTTON,
                    'endConditionValue': 10  # Default value
                }
        else:
            parsedStepDetailDict = parse_stepdetail(stepDetail)
        
        # Add exercise metadata if this is an exercise
        if exerciseName is not None:
            parsedStepDetailDict['exerciseName'] = exerciseName
        # Add category if set (for exercises like cardio which might not have exerciseName)
        if category is not None:
            parsedStepDetailDict['category'] = category
        # Add childStepId if we're inside a repeat
        if inRepeat:
            parsedStepDetailDict['childStepId'] = 1
        stepCount[0] += 1
        order = stepCount[0]
    return WorkoutStep(stepId=order, stepOrder=order, stepType=stepType, **parsedStepDetailDict)

def createWorkoutJson(workoutName: str, steps: list):
    stepCount = [0]
    sport_type = SportType.RUNNING  # default; adjust if yaml specifies otherwise
    
    # Detect sport type based on step names
    def has_strength_steps(steps):
        for step in steps:
            for stepName in step:
                parsedStep, _, _ = parse_bracket(stepName)
                if parsedStep in ["exercise", "rest", "cardio"]:
                    return True
                # Check if we have any common strength indicators
                # Custom exercise names are treated as strength if not running steps
                if parsedStep == "repeat":
                    if has_strength_steps(step[stepName]):
                        return True
                elif parsedStep not in ["run", "warmup", "cooldown", "recovery", "repeat"]:
                    # Unknown step type, likely a strength exercise name
                    # Check if the step detail contains "reps" which is strength-specific
                    stepDetail = step[stepName]
                    if isinstance(stepDetail, str) and "reps" in stepDetail.lower():
                        return True
        return False
    
    if has_strength_steps(steps):
        sport_type = SportType.STRENGTH

    workoutSteps = createWorkoutList(steps, stepCount)

    workout_segment = WorkoutSegment(
        segmentOrder=1,
        sportType=sport_type,
        workoutSteps=workoutSteps
    )

    workout_model = WorkoutModel(
        workoutName=workoutName,
        sportType=sport_type,
        subSportType=None,
        workoutSegments=[workout_segment],
        estimatedDistanceUnit=None,
        avgTrainingSpeed=None,
        estimatedDurationInSecs=None,
        estimatedDistanceInMeters=None,
        estimateType=None
    )

    return json.dumps(workout_model, default=serialize)

def importWorkouts(workouts: dict, toDeletePrevious: bool, conn: Client):
    allWorkouts = []
    if toDeletePrevious:
        allWorkouts = conn.getAllWorkouts()

    for name in workouts:
        if toDeletePrevious and (name in [wo['workoutName'] for wo in allWorkouts]):
            filtered = [wo for wo in allWorkouts if wo['workoutName'] == name]
            for toDelete in filtered:
                conn.deleteWorkout(toDelete)

        steps = workouts[name]
        jsonData = createWorkoutJson(name, steps)
        conn.importWorkout(jsonData)

def _ensure_date(d):
    """Accept datetime.date, datetime.datetime, or 'YYYY-MM-DD' string."""
    if isinstance(d, datetime.date):
        return d
    if isinstance(d, datetime.datetime):
        return d.date()
    if isinstance(d, str):
        try:
            return datetime.datetime.strptime(d, DATE_FORMAT).date()
        except Exception:
            logger.error(f"Invalid date string '{d}'. Expected format {DATE_FORMAT}")
            return None
    logger.error(f"Unsupported date type for '{d}' ({type(d)})")
    return None

def scheduleWorkouts(startfrom, workouts: dict, conn: Client):
    start_date = _ensure_date(startfrom)
    if not start_date:
        logger.error(f"Invalid date {startfrom} format, example of proper date: {DATE_FORMAT}")
        return False

    allWorkouts = conn.getAllWorkouts()
    workoutMap = {value['workoutName']: value['workoutId'] for _, value in enumerate(allWorkouts)}
    logger.debug(f"Workouts on garmin: {workoutMap}")

    toScheduleDate = start_date

    for toScheduleWorkout in workouts:
        currentDate = toScheduleDate
        toScheduleDate += datetime.timedelta(days=1)
        if toScheduleWorkout not in workoutMap:
            logger.warning(f"Workout '{toScheduleWorkout}' not found in Garmin account. Skipping.")
            continue

        workoutId = workoutMap[toScheduleWorkout]
        dateJson = {"date": currentDate.strftime(DATE_FORMAT)}
        success = conn.scheduleWorkout(workoutId, dateJson)
        if success:
            logger.info(f"Scheduled workout {toScheduleWorkout} on date {currentDate}")
        else:
            logger.error("Something went wrong during scheduling")

def _resolve_paths(arg_file_name: str):
    """
    Resolve:
      - project_root (repo root)
      - file_path: absolute or project-relative YAML passed on CLI
      - secrets_path: from env or common locations
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))  # .../garmin_planner/garmin_planner
    project_root = os.path.dirname(current_dir)               # .../garmin_planner

    # Resolve the schedule file (allow absolute or project-relative)
    file_path = arg_file_name if os.path.isabs(arg_file_name) else os.path.join(project_root, arg_file_name)

    # Secrets lookup order: ENV -> project root -> package dir
    secrets_path = os.environ.get("GARMIN_SECRETS", "")
    if not (secrets_path and os.path.exists(secrets_path)):
        candidates = [
            os.path.join(project_root, "secrets.yaml"),
            os.path.join(current_dir,  "secrets.yaml"),
        ]
        secrets_path = next((p for p in candidates if os.path.exists(p)), "")

    return current_dir, project_root, file_path, secrets_path

def main():
    logger.info(f"Running Garmin Planner {__version__}")
    argparser = argparse.ArgumentParser(description="Garmin Planner")
    argparser.add_argument('file_name', type=str, help='Input YAML file name (absolute or project-relative)')
    args = argparser.parse_args()
    file_name = args.file_name

    current_dir, project_root, file_path, secrets_path = _resolve_paths(file_name)

    if not os.path.exists(file_path):
        logger.error(f"The file '{file_path}' does not exist.")
        sys.exit("Exited program due to yaml file not found")

    logger.info(f"Current working directory: {os.getcwd()}")

    # default settings
    settings = {"deleteSameNameWorkout": False}

    # preprocess secrets yaml file and get email and password
    secrets = parseYaml(secrets_path) if secrets_path else None
    if not secrets:
        logger.error(f"Failed to parse secrets.yaml (looked at: {secrets_path or 'ENV var GARMIN_SECRETS not set'})")
        sys.exit("Exiting: secrets.yaml not found or invalid.")
    if ("email" not in secrets) or ("password" not in secrets):
        logger.error("Missing 'email' or 'password' in secrets.yaml")
        sys.exit("Exiting: 'email' or 'password' not found.")

    email = secrets['email']
    password = secrets['password']
    garminCon = Client(email, password)

    # parse input yaml file
    data = parseYaml(file_path)
    if not isinstance(data, dict):
        logger.error(f"YAML '{file_path}' did not parse to a dictionary.")
        sys.exit(1)

    # settings
    if "settings" in data and isinstance(data["settings"], dict):
        if "deleteSameNameWorkout" in data['settings']:
            settings['deleteSameNameWorkout'] = bool(data['settings']['deleteSameNameWorkout'])

    # replace definitions
    if "definitions" in data and isinstance(data["definitions"], dict):
        definitionsDict = data['definitions']
        data = replace_variables(data, definitionsDict)

    if "workouts" in data and isinstance(data["workouts"], dict):
        workouts = data['workouts']
        importWorkouts(
            workouts=workouts,
            toDeletePrevious=settings['deleteSameNameWorkout'],
            conn=garminCon
        )

    if "schedulePlan" in data and isinstance(data["schedulePlan"], dict):
        schedulePlan = data['schedulePlan']
        startDate = schedulePlan.get('start_from')
        workouts = schedulePlan.get('workouts', [])
        if startDate and workouts:
            scheduleWorkouts(startDate, workouts, garminCon)
        else:
            logger.warning("schedulePlan provided but missing 'start_from' or 'workouts'.")

    logger.info("Finished processing yaml file")

if __name__ == "__main__":
    main()