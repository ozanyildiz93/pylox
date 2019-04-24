""""
A scanner class that provides common functionality of scanner and parser
it takes an iterable as source which can be string or list
it keeps track of current element
supported functions
peek(index): returns to element at index relative to current position
   in case out of border elements returns None
advance(): replaces current element with the next element
rewind(count): moves header count many steps back
consume(): returns current element and advances the scanner
match(elements): returns a boolean if current element is equal to one of the
    given elements
    if it is equal than advances the scanner
is_finished(): returns a boolean indicating if scanner run out of element
advance_until(elem): advances scanner until reaching to elem or end of source
    returns number of times scanner advanced
start_recording(): informs scanner that elements starting from current element
    will be requested later for outside caller
stop_recording(): returns elements starting from the current element when start_recording called
    until the current element excluding the current element
    if no matching start_recording function can be found raises EnvironmentError
"""
from typing import Iterable


class BaseScanner(object):
    def __init__(self, source: Iterable[object]):
        self.source = source
        self.head = 0
        self.size = len(source)
        self.recording_head = None

    def peek(self, index: int = 0) -> object:
        target_index = self.head + index
        if target_index < 0:
            return None
        if target_index >= self.size:
            return None
        return self.source[target_index]

    def is_finished(self) -> bool:
        return self.head >= self.size

    def advance(self) -> None:
        self.head = min(self.head + 1, self.size)

    def consume(self) -> object:
        current_object = self.peek()
        self.advance()
        return current_object

    def match(self, targets: Iterable[object]) -> bool:
        if self.peek() in targets:
            self.advance()
            return True
        return False

    def advance_until(self, target: object) -> int:
        count = 0
        while self.peek() != target:
            count += 1
            self.advance()
            if self.is_finished():
                break
        return count

    def rewind(self, count=1):
        self.head = max(0, self.head - count)

    def start_recording(self) -> None:
        self.recording_head = self.head

    def stop_recording(self, reset=True) -> Iterable[object]:

        head = self.recording_head
        if reset:
            self.recording_head = None
        if head is None:
            raise RuntimeError("stop_recording called without a matching"
                               "start_recording call.")
        return self.source[head:self.head]
