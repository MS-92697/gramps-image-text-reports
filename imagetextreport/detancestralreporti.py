"""Implementation and options for detailed ancestor report."""

from _reportmediawriter import MediaReportBase
from baseoptions import add_image_report_options
from gramps.gen.const import GRAMPS_LOCALE
from gramps.gen.lib.citationbase import CitationBase
from gramps.gen.plug.docgen import StyleSheet
from gramps.plugins.textreport.detancestralreport import (
    DetAncestorOptions,
    DetAncestorReport,
)

if GRAMPS_LOCALE is None:
    raise TypeError
_ = GRAMPS_LOCALE.translation.gettext


class ImageDetAncestorReport(MediaReportBase, DetAncestorReport):
    """Detailed ancestor report with images."""

    def endnotes(self, obj: CitationBase) -> str:
        """Write endnotes without sources."""
        self.inc_sources = True
        parent_result = super().endnotes(obj)
        self.inc_sources = False
        return parent_result


class ImageDetAncestorReportOptions(DetAncestorOptions):
    """Options for detailed ancestor report with images."""

    def make_default_style(self, default_style: StyleSheet) -> None:
        """Make the detailed ancestor report (with images) default style."""
        super().make_default_style(default_style)
        add_image_report_options(default_style)
