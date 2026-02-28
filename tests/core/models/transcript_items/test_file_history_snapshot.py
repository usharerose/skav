#!/usr/bin/env python3
"""
Unit tests for FileHistorySnapshotTranscriptItem model
"""

import datetime
from typing import Any

import pytest

from vibehist.core.models.transcript_items.file_history_snapshot import (
    FileHistorySnapshotTranscriptItem,
    Snapshot,
    TrackedFileBackup,
)

SAMPLE_SNAPSHOT_MINIMAL: dict[str, Any] = {
    "type": "file-history-snapshot",
    "messageId": "278b7984-e9af-42ad-8c23-6676db801501",
    "snapshot": {
        "messageId": "278b7984-e9af-42ad-8c23-6676db801501",
        "trackedFileBackups": {},
        "timestamp": "2026-02-24T02:20:53.415Z",
    },
    "isSnapshotUpdate": False,
}

SAMPLE_SNAPSHOT_WITH_TRACKED_FILE: dict[str, Any] = {
    "type": "file-history-snapshot",
    "messageId": "db838491-0caf-444b-a1ff-518dad7eae04",
    "snapshot": {
        "messageId": "e75ea9c5-f7c2-4a09-aee6-803be0c3bdea",
        "trackedFileBackups": {
            "test/conf/test_config.py": {
                "backupFileName": "1a2c1563547d06e9@v1",
                "version": 1,
                "backupTime": "2026-02-24T06:29:46.709Z",
            }
        },
        "timestamp": "2026-02-24T06:29:29.607Z",
    },
    "isSnapshotUpdate": True,
}

SAMPLE_SNAPSHOT_VERSION_2: dict[str, Any] = {
    "type": "file-history-snapshot",
    "messageId": "60bdd0f8-b045-45ca-8b9e-3f9ed8cafcec",
    "snapshot": {
        "messageId": "60bdd0f8-b045-45ca-8b9e-3f9ed8cafcec",
        "trackedFileBackups": {
            "test/conf/test_config.py": {
                "backupFileName": "1a2c1563547d06e9@v2",
                "version": 2,
                "backupTime": "2026-02-24T06:32:38.137Z",
            }
        },
        "timestamp": "2026-02-24T06:32:38.130Z",
    },
    "isSnapshotUpdate": False,
}

SAMPLE_SNAPSHOT_WITH_NULL_BACKUP_FILENAME: dict[str, Any] = {
    "type": "file-history-snapshot",
    "messageId": "dbeef230-d77d-4770-8be7-fee63b234a28",
    "snapshot": {
        "messageId": "ef36d3b6-2df9-4f8c-b4bb-99aa98d6bdd6",
        "trackedFileBackups": {
            "k8s/helm/templates/_helpers.tpl": {
                "backupFileName": None,
                "version": 1,
                "backupTime": "2026-02-24T06:54:43.302Z",
            }
        },
        "timestamp": "2026-02-24T06:53:06.450Z",
    },
    "isSnapshotUpdate": True,
}


class TestTrackedFileBackup:
    """Test TrackedFileBackup model validation"""

    def test_tracked_file_backup_with_model_validate(self) -> None:
        """Test creating TrackedFileBackup using model_validate with real data"""
        backup_data = SAMPLE_SNAPSHOT_WITH_TRACKED_FILE["snapshot"]["trackedFileBackups"][
            "test/conf/test_config.py"
        ]
        backup = TrackedFileBackup.model_validate(backup_data)

        assert backup.backupFileName == "1a2c1563547d06e9@v1"
        assert backup.version == 1
        assert isinstance(backup.backupTime, datetime.datetime)

    def test_backup_time_parsing_real_data(self) -> None:
        """Test ISO 8601 timestamp parsing using real data"""
        backup_data = SAMPLE_SNAPSHOT_WITH_TRACKED_FILE["snapshot"]["trackedFileBackups"][
            "test/conf/test_config.py"
        ]
        backup = TrackedFileBackup.model_validate(backup_data)

        assert backup.backupTime.year == 2026
        assert backup.backupTime.month == 2
        assert backup.backupTime.day == 24
        assert backup.backupTime.hour == 6
        assert backup.backupTime.minute == 29
        assert backup.backupTime.second == 46
        assert backup.backupTime.tzinfo is not None

    def test_version_field_real_data(self) -> None:
        """Test version field using real data"""
        backup_data = SAMPLE_SNAPSHOT_VERSION_2["snapshot"]["trackedFileBackups"][
            "test/conf/test_config.py"
        ]
        backup = TrackedFileBackup.model_validate(backup_data)

        assert backup.version == 2

    def test_backup_filename_field_real_data(self) -> None:
        """Test backupFileName field using real data"""
        backup_data = SAMPLE_SNAPSHOT_WITH_TRACKED_FILE["snapshot"]["trackedFileBackups"][
            "test/conf/test_config.py"
        ]
        backup = TrackedFileBackup.model_validate(backup_data)

        assert backup.backupFileName == "1a2c1563547d06e9@v1"

    def test_backup_filename_null(self) -> None:
        """Test backupFileName field with None value"""
        backup_data = SAMPLE_SNAPSHOT_WITH_NULL_BACKUP_FILENAME["snapshot"]["trackedFileBackups"][
            "k8s/helm/templates/_helpers.tpl"
        ]
        backup = TrackedFileBackup.model_validate(backup_data)

        assert backup.backupFileName is None
        assert backup.version == 1


class TestSnapshot:
    """Test Snapshot model validation"""

    def test_minimal_snapshot_with_model_validate(self) -> None:
        """Test creating minimal snapshot using model_validate"""
        snapshot_data = SAMPLE_SNAPSHOT_MINIMAL["snapshot"]
        snapshot = Snapshot.model_validate(snapshot_data)

        assert snapshot.messageId == "278b7984-e9af-42ad-8c23-6676db801501"
        assert snapshot.trackedFileBackups == {}
        assert isinstance(snapshot.timestamp, datetime.datetime)

    def test_snapshot_with_tracked_files_real_data(self) -> None:
        """Test snapshot with tracked file backups using real data"""
        snapshot_data = SAMPLE_SNAPSHOT_WITH_TRACKED_FILE["snapshot"]
        snapshot = Snapshot.model_validate(snapshot_data)

        assert snapshot.messageId == "e75ea9c5-f7c2-4a09-aee6-803be0c3bdea"
        assert len(snapshot.trackedFileBackups) == 1

        # Access tracked file by file path
        backup = snapshot.trackedFileBackups["test/conf/test_config.py"]
        assert backup.backupFileName == "1a2c1563547d06e9@v1"
        assert backup.version == 1

    def test_timestamp_parsing_real_data(self) -> None:
        """Test ISO 8601 timestamp parsing using real data"""
        snapshot_data = SAMPLE_SNAPSHOT_WITH_TRACKED_FILE["snapshot"]
        snapshot = Snapshot.model_validate(snapshot_data)

        assert isinstance(snapshot.timestamp, datetime.datetime)
        assert snapshot.timestamp.year == 2026
        assert snapshot.timestamp.month == 2
        assert snapshot.timestamp.day == 24
        assert snapshot.timestamp.hour == 6
        assert snapshot.timestamp.minute == 29
        assert snapshot.timestamp.tzinfo is not None

    def test_tracked_file_backups_dict_access(self) -> None:
        """Test accessing tracked file backups by file path"""
        snapshot_data = SAMPLE_SNAPSHOT_VERSION_2["snapshot"]
        snapshot = Snapshot.model_validate(snapshot_data)

        # Access by exact file path
        backup = snapshot.trackedFileBackups["test/conf/test_config.py"]
        assert backup.version == 2
        assert backup.backupFileName == "1a2c1563547d06e9@v2"


class TestFileHistorySnapshotTranscriptItem:
    """Test FileHistorySnapshotTranscriptItem model validation"""

    def test_required_fields_real_data(self) -> None:
        """Test that all required fields are present using real data"""
        entry = FileHistorySnapshotTranscriptItem.model_validate(SAMPLE_SNAPSHOT_MINIMAL)

        assert entry.type == "file-history-snapshot"
        assert entry.messageId == "278b7984-e9af-42ad-8c23-6676db801501"
        assert isinstance(entry.snapshot, Snapshot)
        assert entry.isSnapshotUpdate is False

    def test_type_default_value(self) -> None:
        """Test that type field has default value 'file-history-snapshot'"""
        entry = FileHistorySnapshotTranscriptItem.model_validate(SAMPLE_SNAPSHOT_MINIMAL)

        assert entry.type == "file-history-snapshot"

    def test_is_snapshot_update_false_real_data(self) -> None:
        """Test with isSnapshotUpdate=False using real data"""
        entry = FileHistorySnapshotTranscriptItem.model_validate(SAMPLE_SNAPSHOT_MINIMAL)

        assert entry.isSnapshotUpdate is False

    def test_is_snapshot_update_true_real_data(self) -> None:
        """Test with isSnapshotUpdate=True using real data"""
        entry = FileHistorySnapshotTranscriptItem.model_validate(SAMPLE_SNAPSHOT_WITH_TRACKED_FILE)

        assert entry.isSnapshotUpdate is True

    def test_snapshot_with_empty_tracked_files_real_data(self) -> None:
        """Test snapshot with empty trackedFileBackups using real data"""
        entry = FileHistorySnapshotTranscriptItem.model_validate(SAMPLE_SNAPSHOT_MINIMAL)

        assert entry.snapshot.trackedFileBackups == {}

    def test_snapshot_with_tracked_files_real_data(self) -> None:
        """Test snapshot with tracked file backups using real data"""
        entry = FileHistorySnapshotTranscriptItem.model_validate(SAMPLE_SNAPSHOT_WITH_TRACKED_FILE)

        assert len(entry.snapshot.trackedFileBackups) == 1
        backup = entry.snapshot.trackedFileBackups["test/conf/test_config.py"]
        assert backup.version == 1

    def test_message_id_field_real_data(self) -> None:
        """Test messageId field using real data"""
        entry = FileHistorySnapshotTranscriptItem.model_validate(SAMPLE_SNAPSHOT_WITH_TRACKED_FILE)

        assert entry.messageId == "db838491-0caf-444b-a1ff-518dad7eae04"

    def test_snapshot_message_id_different_from_entry(self) -> None:
        """Test case where snapshot.messageId differs from entry.messageId"""
        entry = FileHistorySnapshotTranscriptItem.model_validate(SAMPLE_SNAPSHOT_WITH_TRACKED_FILE)

        assert entry.messageId == "db838491-0caf-444b-a1ff-518dad7eae04"
        assert entry.snapshot.messageId == "e75ea9c5-f7c2-4a09-aee6-803be0c3bdea"
        assert entry.messageId != entry.snapshot.messageId

    def test_invalid_type_rejected(self) -> None:
        """Test that invalid type is rejected"""
        data = {
            **SAMPLE_SNAPSHOT_MINIMAL,
            "type": "invalid-type",
        }
        with pytest.raises(ValueError):
            FileHistorySnapshotTranscriptItem.model_validate(data)
