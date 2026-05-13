"""Pydantic models for the resume schema.

Mirrors the TypeScript discriminated-union schema defined in SCHEMA.md.
Validation errors point at the offending field with a real error path.
"""

from __future__ import annotations

from typing import Annotated, Literal, Union

from pydantic import BaseModel, ConfigDict, Field


class _Strict(BaseModel):
    """Base model that forbids unknown fields, so typos surface as errors."""

    model_config = ConfigDict(extra="forbid")


class Link(_Strict):
    label: str
    href: str


class Contact(_Strict):
    location: str | None = None
    email: str | None = None
    phone: str | None = None
    note: str | None = None


class Header(_Strict):
    name: str
    contact: Contact | None = None
    links: list[Link] = Field(default_factory=list)


class TimelineItem(_Strict):
    title: str
    org: str | None = None
    location: str | None = None
    dates: str | None = None
    href: str | None = None
    bullets: list[str] = Field(default_factory=list)


class KeyValueItem(_Strict):
    label: str
    value: str


class ListItem(_Strict):
    text: str
    href: str | None = None


class ProseData(_Strict):
    body: str


class KeyValueData(_Strict):
    items: list[KeyValueItem]


class ListData(_Strict):
    items: list[ListItem]


class TimelineData(_Strict):
    items: list[TimelineItem]


class ProseSection(_Strict):
    name: str
    kind: Literal["prose"]
    data: ProseData


class KeyValueSection(_Strict):
    name: str
    kind: Literal["keyvalue"]
    data: KeyValueData


class ListSection(_Strict):
    name: str
    kind: Literal["list"]
    data: ListData


class TimelineSection(_Strict):
    name: str
    kind: Literal["timeline"]
    data: TimelineData


Section = Annotated[
    Union[ProseSection, KeyValueSection, ListSection, TimelineSection],
    Field(discriminator="kind"),
]


class Resume(_Strict):
    template: str
    header: Header
    sections: list[Section] = Field(default_factory=list)
