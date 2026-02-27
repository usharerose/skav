#!/usr/bin/env python3
"""
Unit tests for DocumentContentItem models
"""

from typing import Any, cast

import pytest

from vibehist.core.models.contents.document import (
    DocumentContentItem,
    DocumentContentSource,
)

SAMPLE_DOCUMENT_SOURCE: dict[str, str] = {
    "type": "base64",
    "media_type": "application/pdf",
    "data": "JVBERi0xLjcKCjEgMCBvYmogICUgZW50cnkgcG9pbnQKPDwKICAvVHlwZSAvQ2F0YWxvZwog==",
}

SAMPLE_DOCUMENT_ITEM: dict[str, Any] = {
    "type": "document",
    "source": SAMPLE_DOCUMENT_SOURCE,
}


class TestDocumentContentSource:
    """Test DocumentContentSource model"""

    def test_minimal_source_with_model_validate(self) -> None:
        """Test creating document source using model_validate"""
        source = DocumentContentSource.model_validate(SAMPLE_DOCUMENT_SOURCE)

        assert source.type == "base64"
        assert source.media_type == "application/pdf"
        assert isinstance(source.data, str)

    def test_type_default_value(self) -> None:
        """Test that type has default value 'base64'"""
        source_data = {
            "media_type": "application/pdf",
            "data": "SGVsbG8gV29ybGQ=",
        }
        source = DocumentContentSource.model_validate(source_data)

        assert source.type == "base64"

    def test_invalid_media_type_rejected(self) -> None:
        """Test that invalid media_type is rejected"""
        invalid_data = {
            "type": "base64",
            "media_type": cast(Any, "image/png"),  # Only "application/pdf" is valid
            "data": "SGVsbG8gV29ybGQ=",
        }
        with pytest.raises(ValueError):
            DocumentContentSource.model_validate(invalid_data)

    def test_invalid_type_rejected(self) -> None:
        """Test that invalid type is rejected"""
        invalid_data = {
            "type": cast(Any, "url"),  # Only "base64" is valid
            "media_type": "application/pdf",
            "data": "SGVsbG8gV29ybGQ=",
        }
        with pytest.raises(ValueError):
            DocumentContentSource.model_validate(invalid_data)


class TestDocumentContentItem:
    """Test DocumentContentItem model"""

    def test_document_content_item_with_model_validate(self) -> None:
        """Test creating document content item using model_validate"""
        item = DocumentContentItem.model_validate(SAMPLE_DOCUMENT_ITEM)

        assert item.type == "document"
        assert item.source.media_type == "application/pdf"
        assert isinstance(item.source.data, str)

    def test_type_default_value(self) -> None:
        """Test that type has default value 'document'"""
        item_data = {
            "source": {
                "media_type": "application/pdf",
                "data": "SGVsbG8gV29ybGQ=",
            }
        }
        item = DocumentContentItem.model_validate(item_data)

        assert item.type == "document"

    def test_nested_source_data(self) -> None:
        """Test accessing nested source data"""
        item_data = {
            "source": {
                "type": "base64",
                "media_type": "application/pdf",
                "data": "cGRmZGF0YQ==",
            }
        }
        item = DocumentContentItem.model_validate(item_data)

        assert item.source.type == "base64"
        assert item.source.media_type == "application/pdf"
        assert item.source.data == "cGRmZGF0YQ=="

    def test_invalid_type_rejected(self) -> None:
        """Test that invalid type is rejected"""
        data = {
            **SAMPLE_DOCUMENT_ITEM,
            "type": cast(Any, "invalid_type"),
        }
        with pytest.raises(ValueError):
            DocumentContentItem.model_validate(data)
