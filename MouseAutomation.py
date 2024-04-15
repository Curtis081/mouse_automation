import pyautogui
import time
import datetime
import logging
import threading
import keyboard
from typing import Tuple
from colorama import init as colorama_init, Fore, Style


class Config:
    def __init__(self):
        self.__default_start_time = datetime.time(9, 0)
        self.__default_end_time = datetime.time(18, 0)
        self.__default_delay_time = 180  # in seconds
        self.__pressed_key = "f4"

    def get_default_start_time(self):
        return self.__default_start_time

    def get_default_end_time(self):
        return self.__default_end_time

    def get_default_delay_time(self):
        return self.__default_delay_time

    def get_pressed_key(self):
        return self.__pressed_key


class UserInput:
    @staticmethod
    def prompt_yes_no(prompt: str) -> bool:
        user_input = input(prompt).strip().lower()
        if user_input == 'n':
            print(f"{Fore.GREEN}Disabled.{Style.RESET_ALL}")
        return False if user_input == 'n' else True

    @staticmethod
    def prompt_time(prompt: str, default_time: datetime.time = None) -> datetime.time:
        while True:
            user_input = input(prompt).strip().lower()
            if user_input == 'd' and default_time:
                return default_time
            try:
                hours, minutes = map(int, user_input.split(':'))
                return datetime.time(hours, minutes)
            except ValueError:
                print(f"{Fore.RED}Invalid format. Enter HH:MM or 'd' for default.{Style.RESET_ALL}")

    @staticmethod
    def prompt_integer(prompt: str, default: int) -> int:
        while True:
            user_input = input(prompt).strip().lower()
            if user_input == 'd':
                return default
            try:
                delay = int(user_input)
                if delay > 0:
                    return delay
                else:
                    print("Enter a positive integer.")
            except ValueError:
                print(f"{Fore.RED}Invalid input. Enter an integer or 'd' for default.{Style.RESET_ALL}")


class TimeUtils:
    @staticmethod
    def is_time_in_range(start: datetime.time, end: datetime.time, current: datetime.time) -> bool:
        return start <= current <= end

    @staticmethod
    def get_validated_time_range(prompt_start: str, prompt_end: str, default_start: datetime.time,
                                 default_end: datetime.time) -> Tuple[datetime.time, datetime.time]:
        while True:
            start_time = UserInput.prompt_time(prompt_start, default_start)
            end_time = UserInput.prompt_time(prompt_end, default_end)
            if start_time < end_time:
                return start_time, end_time
            else:
                print(f"{Fore.RED}End time must be later than start time. "
                      f"Try again or press 'd' for default.{Style.RESET_ALL}")


class LoggerConfig:
    @staticmethod
    def setup():
        logging.basicConfig(
            level=logging.WARNING,
            format="%(relativeCreated)6d %(threadName)s %(message)s"
        )


class MouseAutomation(Config):
    def __init__(self):
        super().__init__()
        pyautogui.FAILSAFE = False  # disable FailSafeException

    def start(self):
        colorama_init()
        LoggerConfig.setup()
        event = threading.Event()

        event_check_enabled = UserInput.prompt_yes_no(
            f"If you NEED to {Fore.YELLOW}DISABLE{Style.RESET_ALL} "
            f"press '{self.get_pressed_key().upper()}' to exit the program, "
            f"{Fore.YELLOW}enter 'N/n'{Style.RESET_ALL}, otherwise any key or press Enter to enable: "
        )

        if event_check_enabled:
            threading.Thread(target=self.keyboard_monitor, args=(event,), daemon=True).start()

        start_time, end_time = TimeUtils.get_validated_time_range(
            "Enter start time (HH:MM) or 'd' for default: ",
            "Enter end time (HH:MM) or 'd' for default: ",
            self.get_default_start_time(), self.get_default_end_time()
        )

        delay_time = UserInput.prompt_integer(
            "Enter delay time in seconds or 'd' for default: ", self.get_default_delay_time()
        )

        while input("Move mouse to desired position and press 'p' then Enter to capture: ") != 'p':
            print(f"{Fore.RED}Invalid input.{Style.RESET_ALL}")
            pass

        target_x, target_y = pyautogui.position()
        logging.info(f"Mouse position set to: {target_x}, {target_y}")

        self.perform_clicks(event, target_x, target_y, start_time, end_time, delay_time)

    @staticmethod
    def perform_clicks(event, x, y, start_time, end_time, delay):
        while not event.is_set():
            if TimeUtils.is_time_in_range(start_time, end_time, datetime.datetime.now().time()):
                current_x, current_y = pyautogui.position()
                # Click the mouse at the desired position
                pyautogui.click(x, y, button='left')
                # Move the mouse cursor to the original position
                pyautogui.moveTo(current_x, current_y)
                print(f"Clicked at: {x}, {y}")
            else:
                print("Outside allowed click time.")
            print("Current time: ", time.ctime())
            event.wait(delay)

    def keyboard_monitor(self, event):
        while not event.is_set():
            if keyboard.is_pressed(self.get_pressed_key()):
                event.set()
            event.wait(0.1)
