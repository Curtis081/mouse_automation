import pytest
from unittest.mock import patch
import datetime
from MouseAutomation import UserInput, TimeUtils


class TestUserInput:
    @pytest.mark.parametrize("inputs, expected", [
        (['d'], True),
        (['a'], True),
        (['n'], False),
        (['dx'], True),
    ])
    def test_prompt_yes_no(self, inputs, expected):
        with patch('builtins.input', side_effect=inputs):
            assert UserInput.prompt_yes_no(inputs) == expected

    @pytest.mark.parametrize("inputs, expected", [
        (['10:30', datetime.time(9, 00)], datetime.time(10, 30)),
        (['7:30', datetime.time(9, 00)], datetime.time(7, 30)),
        (['d', datetime.time(9, 00)], datetime.time(9, 00)),
    ])
    def test_prompt_time(self, inputs, expected):
        with patch('builtins.input', side_effect=inputs):
            prompt_start, default_start = inputs
            assert UserInput.prompt_time(prompt_start, default_start) == expected

    @pytest.mark.parametrize("inputs, expected", [
        (['dd', datetime.time(9, 00)], datetime.time(9, 00)),
    ])
    def test_prompt_time_attribute_error(self, inputs, expected):
        with patch('builtins.input', side_effect=inputs):
            prompt_start, default_start = inputs
            with pytest.raises(AttributeError):
                UserInput.prompt_time(prompt_start, default_start)

    @pytest.mark.parametrize("inputs, expected", [
        (['120', 180], 120),
        (['d', 180], 180),
        # (['dx', 180], 180),
    ])
    def test_get_delay_time(self, inputs, expected):
        with patch('builtins.input', side_effect=inputs):
            prompt, default = inputs
            assert UserInput.prompt_integer(prompt, default) == expected

    @pytest.mark.parametrize("inputs, expected", [
        (['dx', 180], 180),
    ])
    def test_get_delay_time_attribute_error(self, inputs, expected):
        with patch('builtins.input', side_effect=inputs):
            prompt, default = inputs
            with pytest.raises(AttributeError):
                UserInput.prompt_integer(prompt, default)


class TestTimeUtils:
    def test_is_time_in_range(self):
        start_time = datetime.time(9, 0)
        end_time = datetime.time(17, 0)
        # A time within the range
        assert TimeUtils.is_time_in_range(start_time, end_time, datetime.time(12, 0)) is True
        # A time before the range
        assert TimeUtils.is_time_in_range(start_time, end_time, datetime.time(8, 59)) is False
        # A time after the range
        assert TimeUtils.is_time_in_range(start_time, end_time, datetime.time(17, 1)) is False
        # Start time edge case
        assert TimeUtils.is_time_in_range(start_time, end_time, start_time) is True
        # End time edge case
        assert TimeUtils.is_time_in_range(start_time, end_time, end_time) is True

    @pytest.mark.parametrize("inputs, expected", [
        (["09:00", "17:00"], (datetime.time(9, 0), datetime.time(17, 0))),  # normal case
        (["d", "d"], (datetime.time(9, 0), datetime.time(18, 0))),  # default case, assuming defaults are 9:00 and 18:00
    ])
    def test_get_validated_time_range(self, inputs, expected):
        default_start = datetime.time(9, 0)
        default_end = datetime.time(18, 0)
        # Patch 'input' to return values from 'inputs' list each time it's called
        time_utils_obj = TimeUtils()
        with patch('builtins.input', side_effect=inputs):
            prompt_start, prompt_end = inputs
            expected = expected
            assert time_utils_obj.get_validated_time_range(prompt_start=prompt_start,
                                                           prompt_end=prompt_end,
                                                           default_start=default_start,
                                                           default_end=default_end) == expected

    @pytest.mark.parametrize("inputs, expected", [
        (["x", "d", "y", "d"], (datetime.time(9, 0), datetime.time(18, 0))),  # default case, assuming defaults are 9:00 and 18:00
    ])
    def test_get_validated_time_range_press_x_d_y_d(self, monkeypatch, inputs, expected):
        default_start = datetime.time(9, 0)
        default_end = datetime.time(18, 0)
        time_utils_obj = TimeUtils()
        responses = iter(inputs)
        monkeypatch.setattr('builtins.input', lambda msg: next(responses))
        assert time_utils_obj.get_validated_time_range("Enter start time (HH:MM): ",
                                                       "Enter end time (HH:MM): ",
                                                       default_start=default_start,
                                                       default_end=default_end) == expected

    @pytest.mark.parametrize("inputs, expected", [
        (["x", "d", "y"], "expected raises StopIteration")
    ])
    def test_get_validated_time_range_press_raise_error(self, monkeypatch, inputs, expected):
        default_start = datetime.time(9, 0)
        default_end = datetime.time(18, 0)
        time_utils_obj = TimeUtils()
        with pytest.raises(StopIteration):
            responses = iter(inputs)
            monkeypatch.setattr('builtins.input', lambda msg: next(responses))
            start, end = time_utils_obj.get_validated_time_range("Enter start time (HH:MM): ",
                                                                 "Enter end time (HH:MM): ",
                                                                 default_start=default_start,
                                                                 default_end=default_end)


if __name__ == "__main__":
    pytest.main()
