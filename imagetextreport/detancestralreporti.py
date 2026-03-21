from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.plug.docgen import StyleSheet
from gramps.plugins.textreport.detancestralreport import (
    DetAncestorReport,
    DetAncestorOptions,
)

from baseoptions import add_image_report_options
from reportmediawriter import MediaReportBase

_ = glocale.translation.gettext  # pyright: ignore[reportOptionalMemberAccess]


class ImageDetAncestorReport(MediaReportBase, DetAncestorReport):
    def endnotes(self, obj) -> str:
        self.inc_sources = True
        parent_result = super().endnotes(obj)
        self.inc_sources = False
        return parent_result


class ImageDetAncestorReportOptions(DetAncestorOptions):
    def make_default_style(self, default_style: StyleSheet) -> None:
        super().make_default_style(default_style)
        add_image_report_options(default_style)
