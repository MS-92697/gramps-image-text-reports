from dataclasses import dataclass

from gramps.gen.const import GRAMPS_LOCALE as glocale
from gramps.gen.plug.docgen import (FontStyle, ParagraphStyle,
                                    TableStyle, TableCellStyle,
                                    FONT_SANS_SERIF, FONT_SERIF,
                                    PARA_ALIGN_CENTER)
from gramps.gen.plug.report import endnotes
from gramps.gen.plug.report import utils as ReportUtils
from gramps.plugins.textreport.detdescendantreport import (
    DetDescendantReport,
    DetDescendantOptions,
)
from gramps.gen.lib import Citation, Media, MediaRef, Note

_ = glocale.translation.gettext


class ReportMediaIterator:
    __slots__ = ["_media_list", "_current_index", "_database"]

    def __init__(self, database, media_list):
        self._database = database
        self._media_list = media_list
        self._current_index = 0

    def __iter__(self):
        return self
    
    @dataclass(frozen=True, slots=True)
    class Item:
        ref: MediaRef
        media: Media

    def __next__(self) -> Item:
        if len(self._media_list) == self._current_index:
            raise StopIteration
        
        self._current_index += 1
        return (curr
                if (curr := self._resolve_at_index(self._current_index - 1))
                else self.__next__())
    
    def _resolve_at_index(self, index: int) -> Item | None:
        return (self.Item(ref=ref, media=val)
                if (ref := self._media_list[index])
                and (val := self._database.get_media_from_handle(ref.get_reference_handle()))
                and (mime := val.get_mime_type()) and mime.startswith("image/")
                else None)
    

class ReportMedia(list):
    def __init__(self, database, media_list):
        iterator = ReportMediaIterator(database, media_list)
        super().__init__(iterator)


class ImageDetDescendantReport(DetDescendantReport):   
    def write_report(self):
        # PLATYPUS check whether this worked and if yes, describe why.
        # same goes for the other funny override down there.
        self.inc_sources = False
        parent_result = super().write_report()
        self.inc_sources = True
        self.write_endnotes_with_media()
        return parent_result
    
    def write_paragraph(self, text: str, style: str):
        self.doc.start_paragraph(style)
        self.doc.write_text(text, mark=None)
        self.doc.end_paragraph()
    
    def write_images(self, media_list):
        if not (report_media := ReportMedia(self.database, media_list)):
            return

        self.doc.start_table("images","DDRI-GalleryTable")
        self.doc.start_row()
        self.doc.start_cell("DDRI-TableHead", 1)
        self.write_paragraph(self._('Images'), 'DDRI-TableTitle')
        self.doc.end_cell()
        self.doc.end_row()
        for item in report_media:
            description = item.media.get_description()
            self.doc.start_row()
            self.doc.start_cell('DDRI-NormalCell')
            self.write_paragraph(description, 'DDRI-ImageCaptionCenter')
            ReportUtils.insert_image(self.database, self.doc, item.ref, self._user,
                                     align='single', w_cm=17.0, h_cm=19.0)
            self.do_attributes(item.media.get_attribute_list() +
                               item.ref.get_attribute_list() )
            self.write_media_notes(item.media)
            self.doc.end_cell()
            self.doc.end_row()
        self.doc.end_table()
        self.doc.start_paragraph('DDRI-NoteHeader')
        self.doc.end_paragraph()
        self.doc.page_break()

    def do_attributes(self, attr_list):
        for attr in attr_list:
            attr_type = attr.get_type().type2base()
            text = (self._("%(type)s: %(value)s")
                    % {"type": self._(attr_type), "value": attr.get_value()})
            endnotes = self._cite_endnote(attr)
            self.write_paragraph(text, endnotes)

    def endnotes(self, obj):
        self.inc_sources = True
        parent_result = super().endnotes(obj)
        self.inc_sources = False
        return parent_result

    def _cite_endnote(self, obj, prior=''):
        if not self.inc_notes:
            return ""
        if not obj:
            return prior
        
        txt = endnotes.cite_source(self.bibli, self.db, obj, self._locale)
        if not txt:
            return prior
        if prior:
            return self._('%(str1)s, %(str2)s') % {'str1':prior, 'str2':txt}

    def write_media_notes(self, media: Media):
        for _, handle in media.get_referenced_note_handles():
            note: Note = self.database.get_note_from_handle(handle)
            text = note.get_styledtext()
            self.doc.write_styled_note(text, 1, "DDRI-MoreDetails", True, True)

    def write_endnotes_with_media(self):
        if self.bibli.get_citation_count() == 0:
            return

        self.doc.start_paragraph('Endnotes-Header')
        self.doc.write_text(self._locale.translation.gettext('Endnotes'))
        self.doc.end_paragraph()

        for cindex, citation in enumerate(self.bibli.get_citation_list()):
            source = self.database.get_source_from_handle(citation
                                                          .get_source_handle())

            self.doc.start_paragraph('Endnotes-Source', "%d." % cindex)
            self.doc.write_text(_format_source_text(source, self._locale),
                                links=False)
            self.doc.end_paragraph()

            if self.inc_srcnotes:
                endnotes._print_notes(source, self.database, self.doc,
                                      'Endnotes-Source-Notes', links=False)
                citation_plist = source.get_media_list()
                if self.addimages:
                    self.write_images(citation_plist)

            for key, ref in citation.get_ref_list():
                self.doc.start_paragraph(
                    'Endnotes-Ref',
                    self._locale.translation.gettext('%s:') % key)
                self.doc.write_text(_format_ref_text(ref, key, self._locale),
                                    links=False)
                self.doc.end_paragraph()

                if self.inc_srcnotes:
                    endnotes._print_notes(ref, self.database, self.doc,
                                          'Endnotes-Ref-Notes', links=False)
                    ref_plist = ref.get_media_list()
                    if self.addimages:
                        self.write_images(ref_plist)


def _format_source_text(source, elocale):
    if not source:
        return ""

    trans_text = elocale.translation.gettext
    # trans_text is a defined keyword (see po/update_po.py, po/genpot.sh)

    src_txt = ""

    if source.get_author():
        src_txt += source.get_author()

    if source.get_title():
        if src_txt:
            # Translators: needed for Arabic, ignore otherwise
            src_txt += trans_text(", ")
        # Translators: used in French+Russian, ignore otherwise
        src_txt += trans_text('"%s"') % source.get_title()

    if source.get_publication_info():
        if src_txt:
            # Translators: needed for Arabic, ignore otherwise
            src_txt += trans_text(", ")
        src_txt += source.get_publication_info()

    if source.get_abbreviation():
        if src_txt:
            # Translators: needed for Arabic, ignore otherwise
            src_txt += trans_text(", ")
        src_txt += "(%s)" % source.get_abbreviation()

    return src_txt


def _format_ref_text(ref, key, elocale):
    if not ref:
        return ""

    ref_txt = ""

    datepresent = False
    date = ref.get_date_object()
    if date is not None and not date.is_empty():
        datepresent = True
    if datepresent:
        if ref.get_page():
            ref_txt = "%s - %s" % (ref.get_page(), elocale.get_date(date))
        else:
            ref_txt = elocale.get_date(date)
    else:
        ref_txt = ref.get_page()

    # Print only confidence level if it is not Normal
    if ref.get_confidence_level() != Citation.CONF_NORMAL:
        ref_txt += (
            " ["
            + elocale.translation.gettext(conf_strings[ref.get_confidence_level()])
            + "]"
        )

    return ref_txt


class ImageDetDescendantOptions(DetDescendantOptions):
    def make_default_style(self, default_style):
        super().make_default_style(default_style)

        font = FontStyle()
        font.set(face=FONT_SANS_SERIF, size=10, italic=0, bold=1)
        para = ParagraphStyle()
        para.set_font(font)
        para.set(first_indent=0.0, lmargin=1.5)
        para.set_top_margin(0.25)
        para.set_bottom_margin(0.25)
        default_style.add_paragraph_style("DDRI-NoteHeader", para)

        para = ParagraphStyle()
        para.set(lmargin=1.5)
        para.set_top_margin(0.25)
        para.set_bottom_margin(0.25)
        para.set_description(_('The basic style used for the text display.'))
        default_style.add_paragraph_style("DDRI-Entry", para)

        para = ParagraphStyle()
        para.set(first_indent=-1.5, lmargin=1.5)
        para.set_top_margin(0.25)
        para.set_bottom_margin(0.25)
        para.set_description(_('The style used for the first personal entry.'))
        default_style.add_paragraph_style("DDRI-First-Entry", para)

        font = FontStyle()
        font.set(size=10, face=FONT_SANS_SERIF, bold=1)
        para = ParagraphStyle()
        para.set_font(font)
        para.set(first_indent=0.0, lmargin=1.5)
        para.set_top_margin(0.25)
        para.set_bottom_margin(0.25)
        para.set_description(_('The style used for the More About header and '
            'for headers of mates.'))
        default_style.add_paragraph_style("DDRI-MoreHeader", para)

        font = FontStyle()
        font.set(face=FONT_SERIF, size=10)
        para = ParagraphStyle()
        para.set_font(font)
        para.set(first_indent=0.0, lmargin=1.5)
        para.set_top_margin(0.25)
        para.set_bottom_margin(0.25)
        para.set_description(_('The style used for additional detail data.'))
        default_style.add_paragraph_style("DDRI-MoreDetails", para)

        tbl = TableStyle()
        tbl.set_width(100)
        tbl.set_columns(3)
        tbl.set_column_width(0, 33)
        tbl.set_column_width(1, 33)
        tbl.set_column_width(2, 34)
        default_style.add_table_style("DDRI-GalleryTable", tbl)

        cell = TableCellStyle()
        cell.set_top_border(1)
        cell.set_bottom_border(1)
        default_style.add_cell_style("DDRI-TableHead", cell)

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

        cell = TableCellStyle()
        default_style.add_cell_style("DDRI-NormalCell", cell)

        font = FontStyle()
        font.set_size(8)
        para = ParagraphStyle()
        para.set_alignment(PARA_ALIGN_CENTER)
        para.set_font(font)
        para.set_top_margin(ReportUtils.pt2cm(3))
        para.set_bottom_margin(ReportUtils.pt2cm(3))
        para.set_description(_('A style used for image captions.'))
        default_style.add_paragraph_style("DDRI-ImageCaptionCenter", para)

