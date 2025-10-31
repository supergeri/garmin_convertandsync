# Strength Workout Guide

This guide explains how to create strength workouts for Garmin using the YAML format.

## Overview

The app now supports creating strength workouts in addition to running workouts. Strength workouts use different step types and can include custom exercise names.

## Step Types

### Running Workouts
- `warmup` - Warm-up phase
- `cooldown` - Cool-down phase
- `recovery` - Recovery phase between intervals
- `run` - Running interval (aliased to warmup)

### Strength Workouts
- `exercise` - Exercise step (can also use custom exercise names)
- `rest` - Rest period
- `cardio` - Cardio warmup
- `warmup` - General warmup (also available for strength)
- `repeat(n)` - Repeat a set of steps n times

## Exercise Names

You can specify custom exercise names using quotes in the YAML:

```yaml
- "Goblet Squat": 10 reps
- "Bench Press": 8 reps
- "Deadlift": 5 reps
```

## End Conditions

### Time-based
- `15min` - 15 minutes
- `30sec` - 30 seconds

### Distance-based
- `1000m` - 1000 meters

### Repetition-based
- `10 reps` - 10 repetitions (strength workouts only)

### Lap Button
- `lap` - Press lap button to advance

## Exercise Descriptions

You can add descriptions to exercises using the pipe syntax `|`:

```yaml
- "Exercise Name": "lap | Description text here"
```

For example:
```yaml
- "Goblet Squat": "lap | KB RDL Into Goblet Squat x10"
```

## Example Strength Workouts

### Basic Strength Workout
```yaml
workouts:
  basic_strength:
    - cardio: lap  # Cardio warmup
    - warmup: lap  # General warmup
    - repeat(3):
        - "Goblet Squat": 10 reps  # Exercise name with reps
        - rest: lap  # Rest period
```

### Complex Strength Workout with Multiple Exercises
```yaml
workouts:
  full_body_strength:
    - warmup:
        - cardio: lap
        - warmup: lap
    - repeat(3):
        - "Squats": 12 reps
        - rest: lap
        - "Push-ups": 10 reps
        - rest: lap
        - "Bent-over Rows": 10 reps
        - rest: lap
```

### HYROX-Style Workout with Descriptions
```yaml
workouts:
  hyrox_test:
    - warmup:
        - cardio: lap  # Cardio warmup nested under warmup
    - repeat(3):
        - "30-degree Lat Pull-down": "lap | Straight Arm Pull down x 10"
        - "Goblet Squat": "lap | KB RDL Into Goblet Squat x10"
        - "Kettlebell Floor to Shelf": "lap | KB Bottoms Up Press x8 each side"
        - rest: lap
```

Note: Exercise names with hyphens and special characters are automatically converted to Garmin format (UPPER_CASE with underscores).

## Detection

The app automatically detects if a workout is strength or running based on the step types present:
- If `exercise`, `rest`, or `cardio` steps are found, it's a strength workout
- If custom exercise names with `reps` are found, it's a strength workout
- Otherwise, it defaults to running

## Exercise Categories

The app automatically determines exercise categories based on the exercise name:
- "squat" → SQUAT
- "press" → BENCH_PRESS
- "deadlift" → DEADLIFT
- "lat" or "pull" → PULL_UP
- "kettlebell floor to shelf" → DEADLIFT

## Testing

Use the test YAML files to test workout creation:
- `test_strength_workout.yaml` - Basic strength workout
- `test_hyrox_workout.yaml` - HYROX-style workout with descriptions

Run:
```bash
python -m garmin_planner test_strength_workout.yaml
python -m garmin_planner test_hyrox_workout.yaml
```

Ensure your `secrets.yaml` contains valid Garmin Connect credentials.

