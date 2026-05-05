from datetime import datetime
from unittest.mock import Mock

from audit import AuditManager, FileSystem, Record, push_or_create_new


def test__audit__create_file__when_current_file_overflows(monkeypatch):
    # Arrange
    file_system_mock = Mock(
        spec_set=FileSystem,
    )
    monkeypatch.setattr(
        file_system_mock,
        "get_files",
        lambda x: ["audits/audit_2.txt", "audits/audit_1.txt"],
    )
    monkeypatch.setattr(
        file_system_mock,
        "read_all_lines",
        lambda x: [
            "Peter;2019-04-06 16:30:00",
            "Jane;2019-04-06 16:40:00",
            "Jack;2019-04-06 17:00:00",
        ],
    )
    sut = AuditManager(3, "audits", file_system_mock)

    # Act
    sut.add_record("Alice", datetime.fromisoformat("2019-04-06T18:00:00"))

    # Assert
    file_system_mock.write_all_text.assert_called_with(
        "audits/audit_3.txt", "Alice;2019-04-06 18:00:00"
    )


# Shell: Filesystem
# Read files -> Core -> Write files
# Core:
# Partition last file contents into Record (index, Entries) based on max size
# Append Entry to last Record or create new one if overflow
# Return last Record, it's the only one that needs writing


class TestRecord:
    def test_has_index_and_entries(self):
        record = Record(1, ["Alice;2019-04-06 18:00:00"])

        assert record.index == 1
        assert record.entries == ["Alice;2019-04-06 18:00:00"]


class TestPushOrCreateNew:
    def test_adds_entry_to_existing_record(self):
        old = Record(1, ["a", "b"])

        assert push_or_create_new(old, "c", 3) == Record(1, ["a", "b", "c"])

    def test_returns_new_record_given_max_size_will_be_exceeded(self):
        old = Record(1, ["a", "b", "c"])

        assert push_or_create_new(old, "d", 3) == Record(2, ["d"])
