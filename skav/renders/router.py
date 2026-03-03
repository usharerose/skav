#!/usr/bin/env python3
"""
Transcript router with auto-discovery.

Routes transcript items to their appropriate view classes using naming convention:
- View class name pattern: {ItemType}View
- Maps to: {ItemType}TranscriptItem

Example:
    UserView → UserTranscriptItem
    AssistantView → AssistantTranscriptItem

Usage:
    from skav.renders.router import route

    # 方式 1: 模块级函数（推荐）
    view = route(item, session)

    # 方式 2: 类方法
    from skav.renders.router import Router
    view = Router.route(item, session)
"""

import logging
from typing import Any

from ..transcripts.models import transcript_items
from ..transcripts.models.transcript_items import TranscriptItemType
from .views.base import BaseView

logger = logging.getLogger(__name__)


class Router:
    """
    Router for transcript views with auto-discovery.

    Automatically scans BaseView subclasses and maps them to transcript
    item types based on naming convention.
    """

    _registry: dict[type, type[BaseView]] = {}
    _initialized = False

    # 渐进式启用：当前只支持 user 视图
    # 设置为 None 表示启用所有视图
    _enabled_views: set[str] | None = {"user"}

    @classmethod
    def _auto_discover(cls) -> dict[type, type[BaseView]]:
        """
        Auto-discover view classes by scanning BaseView subclasses.

        Uses naming convention: {ItemType}View → {ItemType}TranscriptItem

        Returns:
            Dictionary mapping transcript item types to view classes
        """
        registry = {}

        for view_class in BaseView.__subclasses__():
            view_name = view_class.__name__

            # 提取类型名称：UserView → User
            if not view_name.endswith("View"):
                logger.debug(f"Skipping {view_name}: doesn't follow naming convention")
                continue

            item_type_name = view_name[:-4]  # 移除 "View" 后缀
            transcript_item_name = f"{item_type_name}TranscriptItem"

            # 检查是否在启用列表中
            if cls._enabled_views is not None:
                if item_type_name.lower() not in cls._enabled_views:
                    logger.debug(
                        f"Skipping {view_name}: not enabled (enabled: {cls._enabled_views})"
                    )
                    continue

            # 动态导入对应的 TranscriptItem 类型
            try:
                transcript_item_class = getattr(transcript_items, transcript_item_name, None)

                if transcript_item_class is None:
                    logger.warning(
                        f"View {view_name} maps to {transcript_item_name}, "
                        f"but this transcript item type doesn't exist"
                    )
                    continue

                registry[transcript_item_class] = view_class
                logger.debug(f"Auto-registered {view_name} for {transcript_item_name}")

            except Exception as e:
                logger.error(f"Error auto-registering {view_name}: {e}")

        return registry

    @classmethod
    def _ensure_initialized(cls) -> None:
        """Ensure the registry is initialized (lazy initialization)."""
        if not cls._initialized:
            cls._registry = cls._auto_discover()
            cls._initialized = True
            logger.info(
                f"Router auto-discovered {len(cls._registry)} view(s): "
                f"{[v.__name__ for v in cls._registry.values()]}"
            )

    @classmethod
    def route(cls, item: TranscriptItemType, session: Any = None) -> BaseView:
        """
        Route transcript item to appropriate view class.

        Args:
            item: Transcript item (any type from TranscriptItemType union)
            session: Optional Session for tool result lookups

        Returns:
            View instance for the transcript item

        Raises:
            ValueError: If no view class is registered for the item type
        """
        cls._ensure_initialized()

        item_type = type(item)
        view_class = cls._registry.get(item_type)

        if view_class is None:
            registered_types = [t.__name__ for t in cls._registry.keys()]
            logger.error(
                f"No view class registered for {item_type.__name__}. "
                f"Registered types: {registered_types}"
            )
            raise ValueError(f"No view class registered for type: {item_type.__name__}")

        # Create view instance
        try:
            if session is not None:
                return view_class.from_transcript(item, session)
            return view_class.from_transcript(item)
        except Exception as e:
            logger.error(f"Error creating view for {item_type.__name__}: {e}")
            raise

    @classmethod
    def get_view_class(cls, item: TranscriptItemType) -> type[BaseView]:
        """
        Get view class for a transcript item without instantiating.

        Args:
            item: Transcript item

        Returns:
            View class for the transcript item

        Raises:
            ValueError: If no view class is registered for the item type
        """
        cls._ensure_initialized()

        item_type = type(item)
        view_class = cls._registry.get(item_type)

        if view_class is None:
            raise ValueError(f"No view class registered for type: {item_type.__name__}")

        return view_class

    @classmethod
    def enable_views(cls, views: set[str]) -> None:
        """
        Set which views are enabled.

        Args:
            views: Set of view names to enable (e.g., {"user", "assistant"})
                   Set to None to enable all views
        """
        cls._enabled_views = views
        cls._initialized = False  # Force re-discovery
        logger.info(f"Router enabled views: {views}")

    @classmethod
    def register(cls, item_type: type, view_class: type[BaseView]) -> None:
        """
        Manually register a view class for a transcript item type.

        Useful for:
        - Overriding auto-discovered mappings
        - Registering views that don't follow naming convention

        Args:
            item_type: The transcript item type
            view_class: The view class to handle that type
        """
        cls._ensure_initialized()
        cls._registry[item_type] = view_class
        logger.info(f"Router manually registered {view_class.__name__} for {item_type.__name__}")

    @classmethod
    def list_registered_types(cls) -> list[type]:
        """
        Get list of all registered transcript item types.

        Returns:
            List of transcript item types
        """
        cls._ensure_initialized()
        return list(cls._registry.keys())

    @classmethod
    def reset(cls) -> None:
        """
        Reset the router (useful for testing).

        Clears all registrations and forces re-discovery on next use.
        """
        cls._registry.clear()
        cls._initialized = False
        logger.debug("Router reset")


# 模块级便捷函数（推荐使用）
def route(item: TranscriptItemType, session: Any = None) -> BaseView:
    """
    Route transcript item to appropriate view class.

    This is the recommended way to use the router.

    Args:
        item: Transcript item (any type from TranscriptItemType union)
        session: Optional Session for tool result lookups

    Returns:
        View instance for the transcript item

    Example:
        from skav.renders.router import route

        view = route(transcript_item, session)
        message = view.to_message()
    """
    return Router.route(item, session)


__all__ = ["Router", "route"]
