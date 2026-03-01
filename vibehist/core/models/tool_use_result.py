#!/usr/bin/env python3
"""
Tool use result model
"""

from typing import Any, Literal

from pydantic import BaseModel, Field

from .contents import TextContentItem
from .usage import Usage


class AnnotationItem(BaseModel):
    notes: str


class FileItem(BaseModel):
    filePath: str | None = None

    # TODO: check the enumerable values of `type`
    type: Literal["image/png"] | str | None = None

    base64: str | None = None
    originalSize: int | None = None

    content: str | None = None
    numLines: int | None = None
    startLine: int | None = None
    totalLines: int | None = None


class TodoItem(BaseModel):
    activeForm: str
    content: str

    # TODO: check the enumerable values of `status`
    status: Literal["completed", "in_progress", "pending"] | str


class QuestionOptionItem(BaseModel):
    label: str
    description: str


class QuestionItem(BaseModel):
    question: str
    header: str
    options: list[QuestionOptionItem]
    multiSelect: bool


class ResultContentItem(BaseModel):
    title: str
    url: str


class ResultItem(BaseModel):
    tool_use_id: str
    content: list[ResultContentItem]


class StatusChange(BaseModel):
    # TODO: check the enumerable values of statuses
    from_: Literal["completed", "deleted", "in_progress", "pending"] | str = Field(alias="from")
    to: Literal["completed", "deleted", "in_progress", "pending"] | str


class StructuredPatch(BaseModel):
    lines: list[str]
    newLines: int
    newStart: int
    oldLines: int
    oldStart: int


class TaskSubagent(BaseModel):
    description: str
    exitCode: str | None = None  # numeric exit code
    output: str
    status: str
    task_id: str
    task_type: str


class TaskTodoWrite(BaseModel):
    id: str  # numeric ID
    subject: str


class ToolUseResult(BaseModel):
    agentId: str | None = None

    # TODO: add comments on business meaning of the key of `annotations`
    annotations: dict[str, AnnotationItem] | None = None

    # key is as same as `annotations` key
    # value is the answer of the key (question), which is as same as `annotations` value's `notes`
    answers: dict[str, str] | None = None

    appliedLimit: int | None = None
    backgroundTaskId: str | None = None
    commandName: str | None = None

    # TODO: check the enumerable values of `content` when it's a list
    content: str | list[TextContentItem | Any] | None = None

    durationMs: int | None = None
    durationSeconds: float | None = None
    file: FileItem | None = None
    filePath: str | None = None
    filenames: list[str] | None = None
    interrupted: bool | None = None
    isAgent: bool | None = None
    isImage: bool | None = None
    message: str | None = None

    # TODO: check the enumerable values of `mode`
    mode: Literal["content", "files_with_matches"] | str | None = None

    newString: str | None = None
    newTodos: list[TodoItem] | None = None
    noOutputExpected: bool | None = None
    numFiles: int | None = None
    numLines: int | None = None
    oldString: str | None = None
    oldTodos: list[TodoItem] | None = None

    # original content of the file
    originalFile: str | None = None

    persistedOutputPath: str | None = None
    persistedOutputSize: int | None = None
    plan: str | None = None
    prompt: str | None = None
    query: str | None = None
    questions: list[QuestionItem] | None = None
    replaceAll: bool | None = None
    results: list[ResultItem | str] | None = None
    retrieval_status: str | None = None
    returnCodeInterpretation: str | None = None
    shell_id: str | None = None

    # TODO: check the enumerable values of `status`
    status: Literal["completed", "deleted", "in_progress", "pending"] | str | None = None

    statusChange: StatusChange | None = None
    stderr: str | None = None
    stdout: str | None = None
    structuredPatch: list[StructuredPatch] | None = None
    success: bool | None = None
    task: TaskSubagent | TaskTodoWrite | None = None
    taskId: str | None = None  # numeric ID
    totalDurationMs: int | None = None
    totalTokens: int | None = None
    totalToolUseCount: int | None = None
    truncated: bool | None = None

    # TODO: check the enumerable values of `type`
    type: Literal["create", "image", "pdf", "text", "update"] | str | None = None

    updatedFields: list[str] | None = None
    usage: Usage | None = None
    userModified: bool | None = None
