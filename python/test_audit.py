from datetime import datetime
from unittest.mock import Mock

from audit import Auditor, AuditPipeline, FileSystem, Record


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

    # Act
    AuditPipeline(3, "audits", file_system_mock).run(
        "Alice", datetime.fromisoformat("2019-04-06T18:00:00")
    )

    # Assert
    file_system_mock.write_all_text.assert_called_with(
        "audits/audit_3.txt", "Alice;2019-04-06 18:00:00"
    )


# User goal: Append the visitor’s name and the time of their visit to the end of the
# most recent file. If maximum entries is in file, start a new one.
# (Exercise assumes records track recency with index in name)


class TestAuditor:
    def test_finds_latest_record(self):
        files = ["audits/audit_1.txt", "audits/audit_3.txt", "audits/audit_2.txt"]
        assert Auditor.latest_path_and_index(files) == (3, "audits/audit_3.txt")

    def test_returns_default_given_no_records(self):
        files = []
        assert Auditor.latest_path_and_index(files) == (0, "")

    def test_adds_entry_to_record(self):
        old = Record(1, ["Jane;2019-04-05 18:00:00"])

        assert Auditor.add_entry(old, "Alice;2019-04-06 18:00:00", 3) == Record(
            1, ["Jane;2019-04-05 18:00:00", "Alice;2019-04-06 18:00:00"]
        )

    def test_starts_new_record_when_max_entries_reached(self):
        old = Record(1, ["a", "b", "c"])

        assert Auditor.add_entry(old, "d", 3) == Record(2, ["d"])

    def test_creates_entry(self):
        assert (
            Auditor.create_entry("Alice", datetime.fromisoformat("2019-04-06 18:00:00"))
            == "Alice;2019-04-06 18:00:00"
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

    def test_stringifies_entries(self):
        record = Record(1, ["Alice;2019-04-06 18:00:00", "Bob;2019-04-06 18:15:00"])

        assert str(record) == "Alice;2019-04-06 18:00:00\nBob;2019-04-06 18:15:00"
