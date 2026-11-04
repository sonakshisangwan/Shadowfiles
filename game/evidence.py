"""Evidence and Case domain models."""
from abc import ABC, abstractmethod

class Evidence(ABC):
    def __init__(self, name, filepath):
        self.name = name
        self._filepath = filepath

    def read_lines(self):
        """Generator: yields one line at a time."""
        with open(self._filepath, encoding="utf-8") as f:
            for line in f:
                yield line.rstrip("\n")

    @abstractmethod
    def describe(self):
        """Return a string description of the evidence."""
        ...

class EmailEvidence(Evidence):
    def describe(self):
        return f"📧 Email dump: {self.name}"

class ChatEvidence(Evidence):
    def describe(self):
        return f"💬 Chat log: {self.name}"

class Case:
    def __init__(self, title, story, evidence, answers):
        self.title = title
        self.story = story
        self.evidence = evidence
        self.__answers = set(answers)

    def check(self, found):
        found = set(found)
        hits = found & self.__answers
        precision = len(hits) / len(found) if found else 0
        recall = len(hits) / len(self.__answers) if self.__answers else 0
        return precision, recall
