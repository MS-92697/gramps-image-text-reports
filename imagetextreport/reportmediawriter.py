from gramps.gen.plug.report import endnotes
from gramps.gen.plug.report import utils as ReportUtils
from gramps.gen.lib import Media, Note

from base import ImageTextReportBase
from reportmedia import ReportMedia


class ReportMediaWriter[TReport: ImageTextReportBase]:
    def __init__(self, report: TReport):
        self._report = report

    def write_paragraph(self, text: str, style: str):
        self._report.doc.start_paragraph(style)
        self._report.doc.write_text(text, mark=None)
        self._report.doc.end_paragraph()

    def write_images(self, media_list):
        if not (report_media := ReportMedia(self._report.database, media_list)):
            return

        self._report.doc.start_table("images","DDRI-GalleryTable")
        self._report.doc.start_row()
        self._report.doc.start_cell("DDRI-TableHead", 1)
        self.write_paragraph(self._report._('Images'), 'DDRI-TableTitle')
        self._report.doc.end_cell()
        self._report.doc.end_row()
        for item in report_media:
            description = item.media.get_description()
            self._report.doc.start_row()
            self._report.doc.start_cell('DDRI-NormalCell')
            self.write_paragraph(description, 'DDRI-ImageCaptionCenter')
            ReportUtils.insert_image(self._report.database, self._report.doc, item.ref, self._report._user,
                                     align='single', w_cm=17.0, h_cm=19.0)
            self.do_attributes(item.media.get_attribute_list() +
                               item.ref.get_attribute_list() )
            self.write_media_notes(item.media)
            self._report.doc.end_cell()
            self._report.doc.end_row()
        self._report.doc.end_table()
        self._report.doc.start_paragraph('DDRI-NoteHeader')
        self._report.doc.end_paragraph()
        self._report.doc.page_break()

    # PLATYPUS
    # I don't know whether it really works as required or what this actually
    # is expected to do.
    # I noticed the list concatenation
    # needed to be fixed (that's why I restored implementation from git log)
    # but my current test db does not really cover this one.
    # * Noticed it was unused because I broke the report indirection in this
    # implementation and the report creation worked
    # → bother dad whether this is required
    def do_attributes(self, attr_list):
        for attr in attr_list:
            attr_type = attr.get_type().type2base()
            text = (self._report._("%(type)s: %(value)s")
                    % {"type": self._report._(attr_type), "value": attr.get_value()})
            endnotes = self._cite_endnote(attr)
            self.write_paragraph(text, endnotes)

    def _cite_endnote(self, obj, prior='') -> str:
        if not self._report.inc_notes:
            return ""
        if not obj:
            return prior

        txt = endnotes.cite_source(self._report.bibli, self._report.db, obj, self._report._locale)
        if not txt:
            return prior
        if prior:
            return self._report._('%(str1)s, %(str2)s') % {'str1':prior, 'str2':txt}
        return ""

    def write_media_notes(self, media: Media):
        for _, handle in media.get_referenced_note_handles():
            note: Note = self._report.database.get_note_from_handle(handle)
            text = note.get_styledtext()
            self._report.doc.write_styled_note(text, 1, "DDRI-MoreDetails", True, True)

    def write_endnotes_with_media(self):
        if self._report.bibli.get_citation_count() == 0:
            return

        self._report.doc.start_paragraph('Endnotes-Header')
        self._report.doc.write_text(self._report._locale.translation.gettext('Endnotes'))
        self._report.doc.end_paragraph()

        for cindex, citation in enumerate(self._report.bibli.get_citation_list()):
            source = self._report.database.get_source_from_handle(citation
                                                          .get_source_handle())

            self._report.doc.start_paragraph('Endnotes-Source', "%d." % cindex)
            self._report.doc.write_text(_format_source_text(source, self._report._locale),
                                links=False)
            self._report.doc.end_paragraph()

            if self._report.inc_srcnotes:
                endnotes._print_notes(source, self._report.database, self._report.doc,
                                      'Endnotes-Source-Notes', links=False)
                citation_plist = source.get_media_list()
                if self._report.addimages:
                    self.write_images(citation_plist)

            for key, ref in citation.get_ref_list():
                self._report.doc.start_paragraph(
                    'Endnotes-Ref',
                    self._report._locale.translation.gettext('%s:') % key)
                self._report.doc.write_text(_format_ref_text(ref, key, self._report._locale),
                                    links=False)
                self._report.doc.end_paragraph()

                if self._report.inc_srcnotes:
                    endnotes._print_notes(ref, self._report.database, self._report.doc,
                                          'Endnotes-Ref-Notes', links=False)
                    ref_plist = ref.get_media_list()
                    if self._report.addimages:
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

    return ref_txt