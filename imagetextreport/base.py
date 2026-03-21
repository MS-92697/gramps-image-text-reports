from abc import ABC
from typing import Any

from gramps.gen.plug.report import Report
from gramps.gen.utils.grampslocale import GrampsLocale


class ImageTextReportBase(Report, ABC):
    db: Any  # PLATYPUS
    bibli: Any  # PLATYPUS
    inc_notes: bool
    inc_srcnotes: bool
    addimages: bool
    _locale: GrampsLocale