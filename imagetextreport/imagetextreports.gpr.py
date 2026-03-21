register(
    REPORT,
    id="det_descendant_report_i",
    name=_("Detailed Descendant Report With All Images"),
    description=_(
        "Produces a detailed descendant report with all images and optional todo list."
    ),
    version = '1.0.16',
    gramps_target_version="6.0",
    status=STABLE,
    fname="detdescendantreporti.py",
    authors=["Jon Schewe"],
    authors_email=["jpschewe@mtu.net"],
    category=CATEGORY_TEXT,
    reportclass="ImageDetDescendantReport",
    optionclass="ImageDetDescendantOptions",
    report_modes=[REPORT_MODE_GUI, REPORT_MODE_BKI, REPORT_MODE_CLI],
    require_active=True,
    help_url="Addon:Detailed_Descendant_Report_With_All_Images",
)

register(
    REPORT,
    id="det_ancestral_report_i",
    # TODO dafür wird's keine Übersetzungen geben. siehe README
    name=_("Detailed Ancestral Report With All Images"),
    description=_(
        "Produces a detailed ancestral report with all images and optional todo list."
    ),
    version = '1.0.0',
    gramps_target_version="6.0",
    # TODO erstmal nein, aber was ist 'UNSTABLE'
    status=STABLE,
    fname="detancestralreporti.py",
    authors=[],  # TODO
    authors_email=[],  # TODO
    category=CATEGORY_TEXT,
    reportclass="ImageDetAncestorReport",
    optionclass="ImageDetAncestorReportOptions",
    report_modes=[REPORT_MODE_GUI, REPORT_MODE_BKI, REPORT_MODE_CLI],
    require_active=True,
    help_url="Addon:Detailed_Ancestral_Report_With_All_Images",  # TODO?
)
