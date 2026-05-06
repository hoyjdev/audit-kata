import abc
import os
from dataclasses import dataclass
from datetime import datetime


class FileSystem(abc.ABC):
    @abc.abstractmethod
    def get_files(self, dir_name: str):
        raise NotImplementedError

    @abc.abstractmethod
    def write_all_text(self, new_file: str, content: str):
        raise NotImplementedError

    @abc.abstractmethod
    def read_all_lines(self, path: str):
        raise NotImplementedError


class AuditManager:
    def __init__(
        self, max_entries_per_file: int, directory_name: str, file_system: FileSystem
    ):
        self._max_entries_per_file = max_entries_per_file
        self._directory_name = directory_name
        self._file_system = file_system

    def run(self, visitor_name: str, time_of_visit: datetime) -> None:
        file_paths = self._file_system.get_files(self._directory_name)
        (recent_idx, recent_path) = Auditor.latest_path_and_index(file_paths)
        entries = self._file_system.read_all_lines(recent_path)

        record = Auditor.add_entry(
            Record(recent_idx, entries),
            Auditor.create_entry(visitor_name, time_of_visit),
            self._max_entries_per_file,
        )

        new_file = os.path.join(self._directory_name, f"audit_{record.index}.txt")
        self._file_system.write_all_text(new_file, str(record))


class Auditor:
    @staticmethod
    def latest_path_and_index(file_paths: list[str]) -> tuple[int, str]:
        if records := list(enumerate(sorted(file_paths), start=1)):
            return records[-1]
        else:
            return (0, "")

    @staticmethod
    def add_entry(record: Record, entry: str, max_size: int) -> Record:
        if len(record.entries) == max_size:
            return Record(record.index + 1, [entry])
        return Record(record.index, record.entries + [entry])

    @staticmethod
    def create_entry(visitor_name: str, time_of_visit: datetime) -> str:
        return visitor_name + ";" + time_of_visit.strftime("%Y-%m-%d %H:%M:%S")


@dataclass
class Record:
    index: int
    entries: list[str]

    def __str__(self) -> str:
        return "\n".join(self.entries)
