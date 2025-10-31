import pytest
from garmin_planner.main import createWorkoutJson, serialize
from garmin_planner.constant import SportType
import json


class TestSerialize:
    """Test serialization helper function"""
    
    def test_serialize_with_to_dict_method(self):
        from garmin_planner.constant import SportType
        result = serialize(SportType.RUNNING)
        assert isinstance(result, dict)
        assert result['sportTypeId'] == 1
    
    def test_serialize_with_enum_value(self):
        from enum import Enum
        
        class TestEnum(Enum):
            VALUE1 = "value1"
        
        result = serialize(TestEnum.VALUE1)
        assert result == "value1"


class TestCreateWorkoutJson:
    """Test workout JSON creation"""
    
    def test_create_running_workout_json(self):
        steps = [
            {"warmup": "15min @H(z2)"},
            {"repeat": [
                {"run": "30sec @P(5:30-6:00)"},
                {"recovery": "1200m"}
            ]},
            {"cooldown": "15min @H(z2)"}
        ]
        
        json_result = createWorkoutJson("interval_vo2max", steps)
        workout_dict = json.loads(json_result)
        
        assert workout_dict['workoutName'] == 'interval_vo2max'
        assert workout_dict['sportType']['sportTypeKey'] == 'running'
        assert len(workout_dict['workoutSegments']) == 1
        assert len(workout_dict['workoutSegments'][0]['workoutSteps']) == 3
    
    def test_create_strength_workout_json(self):
        steps = [
            {"warmup": [
                {"cardio": "lap"}
            ]},
            {"repeat": [
                {"Goblet Squat": "10 reps"},
                {"rest": "lap"}
            ]}
        ]
        
        json_result = createWorkoutJson("strength_test", steps)
        workout_dict = json.loads(json_result)
        
        assert workout_dict['workoutName'] == 'strength_test'
        assert workout_dict['sportType']['sportTypeKey'] == 'strength_training'
        assert len(workout_dict['workoutSegments']) == 1
    
    def test_create_strength_workout_with_exercise_names(self):
        steps = [
            {"warmup": [
                {"cardio": "lap"}
            ]},
            {"repeat": [
                {"Goblet Squat": "10 reps"},
                {"rest": "lap"}
            ]}
        ]
        
        json_result = createWorkoutJson("strength_test", steps)
        workout_dict = json.loads(json_result)
        
        # Find the exercise step in the repeat
        repeat_step = None
        for step in workout_dict['workoutSegments'][0]['workoutSteps']:
            if step.get('stepType', {}).get('stepTypeKey') == 'repeat':
                repeat_step = step
                break
        
        assert repeat_step is not None
        assert len(repeat_step['workoutSteps']) == 2
        
        # Check the exercise step
        exercise_step = repeat_step['workoutSteps'][0]
        assert exercise_step['stepType']['stepTypeKey'] == 'interval'
        assert exercise_step.get('exerciseName') == 'GOBLET_SQUAT'
        assert exercise_step.get('category') == 'SQUAT'
        assert exercise_step['endCondition']['conditionTypeKey'] == 'reps'
        assert exercise_step['endConditionValue'] == 10


class TestWorkoutStepCreation:
    """Test individual workout step creation"""
    
    def test_warmup_step_creation(self):
        from garmin_planner.main import createWorkoutStep
        from garmin_planner.constant import StepType, ConditionType
        
        step = {"warmup": "15min"}
        step_count = [0]
        result = createWorkoutStep(step, step_count)
        
        assert result.stepType == StepType.WARMUP
        assert result.endCondition == ConditionType.TIME
        assert result.endConditionValue == 900  # 15 minutes
    
    def test_exercise_step_with_reps(self):
        from garmin_planner.main import createWorkoutStep
        from garmin_planner.constant import StepType, ConditionType
        
        step = {"Goblet Squat": "10 reps"}
        step_count = [0]
        result = createWorkoutStep(step, step_count)
        
        assert result.stepType == StepType.INTERVAL
        assert result.exerciseName == 'GOBLET_SQUAT'
        assert result.category == 'SQUAT'
        assert result.endCondition == ConditionType.REPS
        assert result.endConditionValue == 10
    
    def test_cardio_step(self):
        from garmin_planner.main import createWorkoutStep
        from garmin_planner.constant import StepType, ConditionType
        
        step = {"cardio": "lap"}
        step_count = [0]
        result = createWorkoutStep(step, step_count)
        
        assert result.stepType == StepType.INTERVAL
        assert result.category == 'CARDIO'
        assert result.endCondition == ConditionType.LAP_BUTTON
    
    def test_warmup_with_nested_cardio(self):
        from garmin_planner.main import createWorkoutStep
        from garmin_planner.constant import StepType, ConditionType
        
        step = {"warmup": [
            {"cardio": "lap"}
        ]}
        step_count = [0]
        result = createWorkoutStep(step, step_count)
        
        assert result.stepType == StepType.WARMUP
        assert result.category == 'CARDIO'
        assert result.endCondition == ConditionType.LAP_BUTTON


class TestWorkoutTypeDetection:
    """Test automatic workout type detection"""
    
    def test_detects_running_workout(self):
        steps = [
            {"warmup": "15min"},
            {"run": "5k"},
            {"cooldown": "15min"}
        ]
        
        json_result = createWorkoutJson("run_test", steps)
        workout_dict = json.loads(json_result)
        
        assert workout_dict['sportType']['sportTypeKey'] == 'running'
    
    def test_detects_strength_workout_by_exercise(self):
        steps = [
            {"warmup": [
                {"cardio": "lap"}
            ]},
            {"Goblet Squat": "10 reps"}
        ]
        
        json_result = createWorkoutJson("strength_test", steps)
        workout_dict = json.loads(json_result)
        
        assert workout_dict['sportType']['sportTypeKey'] == 'strength_training'
    
    def test_detects_strength_workout_by_keyword(self):
        steps = [
            {"cardio": "lap"},
            {"rest": "lap"}
        ]
        
        json_result = createWorkoutJson("strength_test", steps)
        workout_dict = json.loads(json_result)
        
        assert workout_dict['sportType']['sportTypeKey'] == 'strength_training'

