from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.plugins.textreport.detancestralreport import (
    DetAncestorReport, 
    DetAncestorOptions,
)

_ = glocale.translation.gettext


class ImageDetAncestorReport(DetAncestorReport):
    pass


class ImageDetAncestorReportOptions(DetAncestorOptions):
    pass