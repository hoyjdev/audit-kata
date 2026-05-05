import abc
import os.path
from dataclasses import dataclass
from datetime import datetime
from typing import Any


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
        # Sorted paths by index, lowest to highest. [(1, 'audits/audit_1.txt'), (2, 'audits/audit_2.txt')]
        sorted_paths = self._sort_by_index(file_paths)
        # Create entry
        entry = visitor_name + ";" + time_of_visit.strftime("%Y-%m-%d %H:%M:%S")

        if len(sorted_paths) == 0:
            # Edge case: no paths, then create one file and write
            new_file = os.path.join(self._directory_name, "audit_1.txt")
            self._file_system.write_all_text(new_file, entry)
            return

        # Otherwise: Read all lines from last file
        current_file_index, curr_file_path = sorted_paths[-1]
        lines = self._file_system.read_all_lines(curr_file_path)

        record = Record(current_file_index, lines)
        record = push_or_create_new(record, entry, self._max_entries_per_file)

        if len(lines) < self._max_entries_per_file:
            # If there are fewer lines than max, write to last file
            self._file_system.write_all_text(curr_file_path, str(record))
        else:
            # If there are more lines than max, write to new file
            new_file = os.path.join(self._directory_name, f"audit_{record.index}.txt")
            self._file_system.write_all_text(new_file, str(record))

    @staticmethod
    def _sort_by_index(file_paths) -> list[tuple[Any, Any]]:
        return list(enumerate(sorted(file_paths), start=1))


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
