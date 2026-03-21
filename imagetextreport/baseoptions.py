from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.plug.docgen import (
    FontStyle,
    ParagraphStyle,
    StyleSheet,
    TableStyle,
    TableCellStyle,
    FONT_SANS_SERIF,
    FONT_SERIF,
    PARA_ALIGN_CENTER,
)
from gramps.gen.plug.report import utils as ReportUtils

_ = glocale.translation.gettext  # pyright: ignore[reportOptionalMemberAccess]


def add_image_report_options(default_style: StyleSheet) -> None:
    _add_note_header_option(default_style)
    _add_entry_option(default_style)
    _add_first_entry_option(default_style)
    _add_more_header_option(default_style)
    _add_more_details_option(default_style)
    _add_gallery_style_option(default_style)
    _add_table_head_option(default_style)
    _add_table_title_option(default_style)
    _add_normal_cell_option(default_style)
    _add_image_caption_center_option(default_style)


def _add_note_header_option(default_style: StyleSheet) -> None:
    font = FontStyle()
    font.set(face=FONT_SANS_SERIF, size=10, italic=0, bold=1)
    para = ParagraphStyle()
    para.set_font(font)
    para.set(first_indent=0.0, lmargin=1.5)
    para.set_top_margin(0.25)
    para.set_bottom_margin(0.25)
    default_style.add_paragraph_style("DDRI-NoteHeader", para)


def _add_entry_option(default_style: StyleSheet) -> None:
    para = ParagraphStyle()
    para.set(lmargin=1.5)
    para.set_top_margin(0.25)
    para.set_bottom_margin(0.25)
    para.set_description(_("The basic style used for the text display."))
    default_style.add_paragraph_style("DDRI-Entry", para)


def _add_first_entry_option(default_style: StyleSheet) -> None:
    para = ParagraphStyle()
    para.set(first_indent=-1.5, lmargin=1.5)
    para.set_top_margin(0.25)
    para.set_bottom_margin(0.25)
    para.set_description(_("The style used for the first personal entry."))
    default_style.add_paragraph_style("DDRI-First-Entry", para)


def _add_more_header_option(default_style: StyleSheet) -> None:
    font = FontStyle()
    font.set(size=10, face=FONT_SANS_SERIF, bold=1)
    para = ParagraphStyle()
    para.set_font(font)
    para.set(first_indent=0.0, lmargin=1.5)
    para.set_top_margin(0.25)
    para.set_bottom_margin(0.25)
    para.set_description(
        _("The style used for the More About header and for headers of mates.")
    )
    default_style.add_paragraph_style("DDRI-MoreHeader", para)


def _add_more_details_option(default_style: StyleSheet) -> None:
    font = FontStyle()
    font.set(face=FONT_SERIF, size=10)
    para = ParagraphStyle()
    para.set_font(font)
    para.set(first_indent=0.0, lmargin=1.5)
    para.set_top_margin(0.25)
    para.set_bottom_margin(0.25)
    para.set_description(_("The style used for additional detail data."))
    default_style.add_paragraph_style("DDRI-MoreDetails", para)


def _add_gallery_style_option(default_style: StyleSheet) -> None:
    tbl = TableStyle()
    tbl.set_width(100)
    tbl.set_columns(3)
    tbl.set_column_width(0, 33)
    tbl.set_column_width(1, 33)
    tbl.set_column_width(2, 34)
    default_style.add_table_style("DDRI-GalleryTable", tbl)


def _add_table_head_option(default_style: StyleSheet) -> None:
    cell = TableCellStyle()
    cell.set_top_border(1)
    cell.set_bottom_border(1)
    default_style.add_cell_style("DDRI-TableHead", cell)


def _add_table_title_option(default_style: StyleSheet) -> None:
    font = FontStyle()
    font.set_bold(1)
    font.set_type_face(FONT_SANS_SERIF)
    font.set_size(12)
    font.set_italic(1)
    para = ParagraphStyle()
    para.set_font(font)
    para.set_top_margin(ReportUtils.pt2cm(3))
    para.set_bottom_margin(ReportUtils.pt2cm(3))
    para.set_description(_("The style used for image labels."))
    default_style.add_paragraph_style("DDRI-TableTitle", para)


def _add_normal_cell_option(default_style: StyleSheet) -> None:
    cell = TableCellStyle()
    default_style.add_cell_style("DDRI-NormalCell", cell)


def _add_image_caption_center_option(default_style: StyleSheet) -> None:
    font = FontStyle()
    font.set_size(8)
    para = ParagraphStyle()
    para.set_alignment(PARA_ALIGN_CENTER)
    para.set_font(font)
    para.set_top_margin(ReportUtils.pt2cm(3))
    para.set_bottom_margin(ReportUtils.pt2cm(3))
    para.set_description(_("A style used for image captions."))
    default_style.add_paragraph_style("DDRI-ImageCaptionCenter", para)
