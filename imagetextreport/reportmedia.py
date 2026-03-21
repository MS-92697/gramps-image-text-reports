from collections.abc import Sequence
from dataclasses import dataclass
from typing import Self

from gramps.gen.lib import Media, MediaRef
from gramps.gen.proxy.proxybase import ProxyDbBase


class ReportMediaIterator:
    __slots__ = ["_current_index", "_database", "_media_list"]

    def __init__(
        self,
        database: ProxyDbBase,
        media_list: Sequence[MediaRef | None],
    ) -> None:
        self._database = database
        self._media_list = media_list
        self._current_index = 0

    def __iter__(self) -> Self:
        return self

    @dataclass(frozen=True, slots=True)
    class Item:
        ref: MediaRef
        media: Media

    def __next__(self) -> Item:
        if len(self._media_list) == self._current_index:
            raise StopIteration

        self._current_index += 1
        return (
            curr
            if (curr := self._resolve_at_index(self._current_index - 1))
            else self.__next__()
        )

    def _resolve_at_index(self, index: int) -> Item | None:
        return (
            self.Item(ref=ref, media=val)
            if (ref := self._media_list[index])
            and (val := self._resolve_reference(ref))
            and (mime := val.get_mime_type())
            and mime.startswith("image/")
            else None
        )

    def _resolve_reference(self, ref) -> Media | None:
        handle = ref.get_reference_handle()
        return self._database.get_media_from_handle(handle)


class ReportMedia(list):
    def __init__(
        self,
        database: ProxyDbBase,
        media_list: Sequence[MediaRef | None],
    ) -> None:
        iterator = ReportMediaIterator(database, media_list)
        super().__init__(iterator)


ReportMediaItem = ReportMediaIterator.Item
