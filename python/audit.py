import abc
import os.path
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

    def add_record(self, visitor_name: str, time_of_visit: datetime):
        # Fetch file paths
        file_paths = self._file_system.get_files(self._directory_name)

        sorted_paths = sort_by_index(file_paths)
        last_path = find_last_path(sorted_paths)

        # Read entries from last file (in reality, this would default to empty list)
        lines = self._file_system.read_all_lines(last_path[1])

        entry = create_entry(visitor_name, time_of_visit)
        record = Record(last_path[0], lines)
        record = push_or_create_new(record, entry, self._max_entries_per_file)

        new_file = os.path.join(self._directory_name, f"audit_{record.index}.txt")
        self._file_system.write_all_text(new_file, str(record))


@dataclass
class Record:
    index: int
    entries: list[str]

    def __str__(self) -> str:
        return "\n".join(self.entries)


def push_or_create_new(record: Record, item: str, max_size: int) -> Record:
    if len(record.entries) == max_size:
        return Record(record.index + 1, [item])
    return Record(record.index, record.entries + [item])


def sort_by_index(file_paths) -> list[tuple[int, str]]:
    # Sort paths by index, lowest to highest. [(1, 'audits/audit_1.txt'), (2, 'audits/audit_2.txt')]
    return list(enumerate(sorted(file_paths), start=1))


def find_last_path(paths: list[tuple[int, str]]) -> tuple[int, str]:
    # Return last index and path in a list, or a default
    return next(iter(reversed(paths)), (1, ""))


def create_entry(visitor_name: str, time_of_visit: datetime) -> str:
    return visitor_name + ";" + time_of_visit.strftime("%Y-%m-%d %H:%M:%S")
