#!/usr/bin/env python3
"""
Base view class for all transcript type views
"""

from abc import ABC, abstractmethod
from typing import Any

from ..models.message import Message


class BaseView(ABC):
    """
    Abstract base class for all transcript type views.

    Each concrete view class:
    1. Accepts a specific transcript item type
    2. Transforms it into a flattened view model
    3. Returns the view model via to_message()

    Note: from_transcript uses Any for parameters because each subclass
    handles a specific transcript type. This is not a typical LSP scenario
    since Router routes to specific view classes by type.
    """

    @classmethod
    @abstractmethod
    def from_transcript(
        cls,
        item: Any,
        session: Any = None,
    ) -> "BaseView":
        """
        Factory method to create view from transcript item,
        which provides a consistent interface across all view types.

        Subclasses MUST override with specific types.

        >>> view = ViewClass.from_transcript(transcript_item, session)

        :param item: Transcript item (specific type for each view subclass)
        :param session: Optional Session for tool result lookups
        :return: View instance for the transcript item
        """
        pass

    @abstractmethod
    def to_message(self) -> "Message":
        """
        convert the view to a Message for template rendering

        :return: Message
        :rtype: Message
        """
        pass
