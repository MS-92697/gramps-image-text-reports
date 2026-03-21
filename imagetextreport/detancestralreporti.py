from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.plugins.textreport.detancestralreport import (
    DetAncestorReport,
    DetAncestorOptions,
)

from base import ImageTextReportBase
from baseoptions import add_image_report_options
from reportmediawriter import ReportMediaWriter

_ = glocale.translation.gettext # pyright: ignore[reportOptionalMemberAccess]


class ImageDetAncestorReport(ImageTextReportBase, DetAncestorReport):
    def write_report(self):
        # PLATYPUS check whether this worked and if yes, describe why.
        # same goes for the other funny override down there.
        self.inc_sources = False
        parent_result = super().write_report()
        self.inc_sources = True
        ReportMediaWriter(self).write_endnotes_with_media()
        return parent_result

    def endnotes(self, obj):
        self.inc_sources = True
        parent_result = super().endnotes(obj)
        self.inc_sources = False
        return parent_result


class ImageDetAncestorReportOptions(DetAncestorOptions):
    def make_default_style(self, default_style):
        super().make_default_style(default_style)
        add_image_report_options(default_style)