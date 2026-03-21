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
    authors=["Jon Schewe", "Florian Schieder"],
    authors_email=["jpschewe@mtu.net", "florian.schieder@web.de"],
    category=CATEGORY_TEXT,
    reportclass="ImageDetDescendantReport",
    optionclass="ImageDetDescendantOptions",
    report_modes=[REPORT_MODE_GUI, REPORT_MODE_BKI, REPORT_MODE_CLI],
    require_active=True,
)

register(
    REPORT,
    id="det_ancestral_report_i",
    name=_("Detailed Ancestral Report With All Images"),
    description=_(
        "Produces a detailed ancestral report with all images and optional todo list."
    ),
    version = '1.0.0',
    gramps_target_version="6.0",
    status=STABLE,
    fname="detancestralreporti.py",
    authors=["Florian Schieder"],
    authors_email=["florian.schieder@web.de"],
    category=CATEGORY_TEXT,
    reportclass="ImageDetAncestorReport",
    optionclass="ImageDetAncestorReportOptions",
    report_modes=[REPORT_MODE_GUI, REPORT_MODE_BKI, REPORT_MODE_CLI],
    require_active=True,
)
