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

## Detection

The app automatically detects if a workout is strength or running based on the step types present:
- If `exercise`, `rest`, or `cardio` steps are found, it's a strength workout
- If custom exercise names with `reps` are found, it's a strength workout
- Otherwise, it defaults to running

## Testing

Use the `test_strength_workout.yaml` file to test strength workout creation. Run:

```bash
python -m garmin_planner test_strength_workout.yaml
```

Ensure your `secrets.yaml` contains valid Garmin Connect credentials.

