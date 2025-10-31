import pytest
from garmin_planner.parser import parse_bracket, parse_stepdetail, parse_time_to_minutes
from garmin_planner.constant import ConditionType, TargetType


class TestParseBracket:
    """Test parsing of bracket notation"""
    
    def test_parse_bracket_with_repeat(self):
        parsed, num_iteration = parse_bracket("repeat(3)")
        assert parsed == "repeat"
        assert num_iteration == "3"
    
    def test_parse_bracket_without_brackets(self):
        parsed, num_iteration = parse_bracket("warmup")
        assert parsed == "warmup"
        assert num_iteration is None
    
    def test_parse_bracket_with_spaces(self):
        parsed, num_iteration = parse_bracket("Goblet Squat")
        assert parsed == "goblet squat"
        assert num_iteration is None
    
    def test_parse_bracket_with_repeat_spaces(self):
        parsed, num_iteration = parse_bracket("repeat(8)")
        assert parsed == "repeat"
        assert num_iteration == "8"


class TestParseTimeToMinutes:
    """Test time parsing to minutes"""
    
    def test_parse_time_with_minutes_and_seconds(self):
        result = parse_time_to_minutes("5:30")
        assert result == 5.5
    
    def test_parse_time_minutes_only(self):
        result = parse_time_to_minutes("10:00")
        assert result == 10.0
    
    def test_parse_time_zero(self):
        result = parse_time_to_minutes("0:30")
        assert result == 0.5


class TestParseStepDetail:
    """Test parsing of step details"""
    
    def test_parse_time_in_seconds(self):
        result = parse_stepdetail("30sec")
        assert result['endCondition'] == ConditionType.TIME
        assert result['endConditionValue'] == 30
    
    def test_parse_time_in_minutes(self):
        result = parse_stepdetail("15min")
        assert result['endCondition'] == ConditionType.TIME
        assert result['endConditionValue'] == 900  # 15 * 60
    
    def test_parse_distance(self):
        result = parse_stepdetail("1000m")
        assert result['endCondition'] == ConditionType.DISTANCE
        assert result['endConditionValue'] == 1000
    
    def test_parse_distance_in_kilometers(self):
        result = parse_stepdetail("5k")
        assert result['endCondition'] == ConditionType.DISTANCE
        assert result['endConditionValue'] == 5000  # 5km = 5000m
    
    def test_parse_lap_button(self):
        result = parse_stepdetail("lap")
        assert result['endCondition'] == ConditionType.LAP_BUTTON
        assert result['endConditionValue'] == 1
    
    def test_parse_reps(self):
        result = parse_stepdetail("10 reps")
        assert result['endCondition'] == ConditionType.REPS
        assert result['endConditionValue'] == 10
    
    def test_parse_heart_rate_zone(self):
        result = parse_stepdetail("@H(z2)")
        assert result['targetType'] == TargetType.HEART_RATE_ZONE
        assert result['zoneNumber'] == 2
    
    def test_parse_pace(self):
        result = parse_stepdetail("@P(5:30-6:00)")
        assert result['targetType'] == TargetType.PACE
        assert result['targetValueOne'] is not None
        assert result['targetValueTwo'] is not None
    
    def test_parse_complex_step(self):
        result = parse_stepdetail("15min @H(z2)")
        assert result['endCondition'] == ConditionType.TIME
        assert result['endConditionValue'] == 900
        assert result['targetType'] == TargetType.HEART_RATE_ZONE
        assert result['zoneNumber'] == 2
    
    def test_parse_reps_with_more_context(self):
        result = parse_stepdetail("Goblet Squat 10 reps")
        assert result['endCondition'] == ConditionType.REPS
        assert result['endConditionValue'] == 10
    
    def test_parse_empty_string(self):
        result = parse_stepdetail("")
        assert result == {}

