import sys
from MouseAutomation import MouseAutomation


def main() -> int:
    mouse_auto = MouseAutomation()
    mouse_auto.start()
    return 0


if __name__ == '__main__':
    sys.exit(main())
