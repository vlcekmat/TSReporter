from collections import deque
import io

from config import read_config
from bugs import read_bug_lines, read_bugs_file
from information_compile import get_image


class BugHandler:
    _all_bugs = deque()  # Queue of bugs read from the bugs file, each bug is a stack of lines, the bug head on top
    current = deque()  # The current bug popped from the above queue
    message = None

    def __init__(self, game):
        if game == "A":
            game_path = read_config("documents location") + "/American Truck Simulator"
        else:
            game_path = read_config("documents location") + "/Euro Truck Simulator 2"
        out_string = io.StringIO()
        bug_lines = read_bugs_file(game_path, out_string)
        if out_string.getvalue() == "":
            self._all_bugs = read_bug_lines(bug_lines)
            self.current = self._all_bugs.popleft()
        else:
            self._all_bugs = None
            self.current = None
            self.message = out_string.getvalue()

    def archive(self):
        pass

    def read_next(self):
        if len(self._all_bugs) > 0:
            self.current = self._all_bugs.popleft()
        else:
            self.current = None

    def get_current(self):
        return self.current

    def try_get_image(self):
        images_folder_path = read_config("edited images location")
        my_image = get_image(self.current[0], images_folder_path)
        if my_image == "":
            return None
        else:
            return my_image


