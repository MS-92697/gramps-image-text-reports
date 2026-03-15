from dataclasses import dataclass
from functools import partial

from gramps.gen.const import GRAMPS_LOCALE as glocale
_ = glocale.translation.gettext
from gramps.gen.plug.menu import (BooleanOption, NumberOption, PersonOption,
                                  EnumeratedListOption)
from gramps.gen.plug.docgen import (FontStyle, ParagraphStyle,
                                    TableStyle, TableCellStyle,
                                    FONT_SANS_SERIF, FONT_SERIF,
                                    PARA_ALIGN_CENTER)
from gramps.gen.plug.report import endnotes
from gramps.gen.plug.report import utils as ReportUtils
from gramps.gen.plug.report import MenuReportOptions
from gramps.gen.plug.report import stdoptions
from gramps.plugins.textreport.detdescendantreport import DetDescendantReport
from gramps.gen.lib import Citation, Media, MediaRef, Note


class ReportMediaIterator:
    __slots__ = ["_media_list", "_current_index"]

    def __init__(self, media_list):
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
                if (ref := self._media_list[index].get_reference_handle())
                and (val := self.database.get_media_from_handle(ref))
                and (mime := val.get_mime_type()) and mime.startswith("image/")
                else None)


class DetailedDescendantReportI(DetDescendantReport):   
    def write_report(self):
        parent_result = super().write_report()
        self.write_endnotes_with_media()
        return parent_result
    
    def write_images(self, media_list):
        self.doc.start_table("images","DDRI-GalleryTable")
        self.doc.start_row()
        self.doc.start_cell("DDRI-TableHead", 1)
        self.write_paragraph(self._('Images'), style='DDRI-TableTitle')
        self.doc.end_cell()
        self.doc.end_row()
        for item in ReportMediaIterator(media_list):
            description = item.media.get_description()
            self.doc.start_row()
            self.doc.start_cell('DDRI-NormalCell')
            self.write_paragraph(description, style='DDRI-ImageCaptionCenter')
            ReportUtils.insert_image(self.database, self.doc, item, self._user,
                                     align='single', w_cm=17.0, h_cm=19.0)
            self.do_attributes(item.media.get_attribute_list() +
                               item.get_attribute_list() )
            self.write_media_notes(item.media)
            self.doc.end_cell()
            self.doc.end_row()
        self.doc.end_table()
        self.doc.start_paragraph('DDRI-NoteHeader')
        self.doc.end_paragraph()
        self.doc.page_break()

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

#------------------------------------------------------------------------
#
# DetDescendantOptions
#
#------------------------------------------------------------------------
class DetailedDescendantIOptions(MenuReportOptions):

    """
    Defines options and provides handling interface.
    """

    def __init__(self, name, dbase):
        MenuReportOptions.__init__(self, name, dbase)

    def add_menu_options(self, menu):
        """
        Add options to the menu for the detailed descendant report.
        """

        # Report Options
        category = _("Report Options")
        add_option = partial(menu.add_option, category)

        pid = PersonOption(_("Center Person"))
        pid.set_help(_("The center person for the report"))
        add_option("pid", pid)

        stdoptions.add_name_format_option(menu, category)

        stdoptions.add_private_data_option(menu, category)

        numbering = EnumeratedListOption(_("Numbering system"), "Henry")
        numbering.set_items([
                ("Henry",      _("Henry numbering")),
                ("d'Aboville", _("d'Aboville numbering")),
                ("Record (Modified Register)",
                               _("Record (Modified Register) numbering"))])
        numbering.set_help(_("The numbering system to be used"))
        add_option("numbering", numbering)

        generations = NumberOption(_("Generations"), 10, 1, 100)
        generations.set_help(
            _("The number of generations to include in the report")
            )
        add_option("gen", generations)

        pagebbg = BooleanOption(_("Page break between generations"), False)
        pagebbg.set_help(
                     _("Whether to start a new page after each generation."))
        add_option("pagebbg", pagebbg)

        pageben = BooleanOption(_("Page break before end notes"),False)
        pageben.set_help(
                     _("Whether to start a new page before the end notes."))
        add_option("pageben", pageben)

        stdoptions.add_localization_option(menu, category)

        # Content

        add_option = partial(menu.add_option, _("Content"))

        usecall = BooleanOption(_("Use callname for common name"), False)
        usecall.set_help(_("Whether to use the call name as the first name."))
        add_option("usecall", usecall)

        fulldates = BooleanOption(_("Use full dates instead of only the year"),
                                  True)
        fulldates.set_help(_("Whether to use full dates instead of just year."))
        add_option("fulldates", fulldates)

        listc = BooleanOption(_("List children"), True)
        listc.set_help(_("Whether to list children."))
        add_option("listc", listc)

        computeage = BooleanOption(_("Compute death age"),True)
        computeage.set_help(_("Whether to compute a person's age at death."))
        add_option("computeage", computeage)

        omitda = BooleanOption(_("Omit duplicate ancestors"), True)
        omitda.set_help(_("Whether to omit duplicate ancestors."))
        add_option("omitda", omitda)

        verbose = BooleanOption(_("Use complete sentences"), True)
        verbose.set_help(
                 _("Whether to use complete sentences or succinct language."))
        add_option("verbose", verbose)

        desref = BooleanOption(_("Add descendant reference in child list"),
                               True)
        desref.set_help(
                    _("Whether to add descendant references in child list."))
        add_option("desref", desref)

        category_name = _("Include")
        add_option = partial(menu.add_option, _("Include"))

        incnotes = BooleanOption(_("Include notes"), True)
        incnotes.set_help(_("Whether to include notes."))
        add_option("incnotes", incnotes)

        inctodo = BooleanOption(_("Include TODO notes"), True)
        inctodo.set_help(_("Whether to include TODO notes."))
        add_option("inctodo", inctodo)

        incattrs = BooleanOption(_("Include attributes"), False)
        incattrs.set_help(_("Whether to include attributes."))
        add_option("incattrs", incattrs)

        incphotos = BooleanOption(_("Include Photo/Images from Gallery"), True)
        incphotos.set_help(_("Whether to include images."))
        add_option("incphotos", incphotos)

        incnames = BooleanOption(_("Include alternative names"), False)
        incnames.set_help(_("Whether to include other names."))
        add_option("incnames", incnames)

        incevents = BooleanOption(_("Include events"), False)
        incevents.set_help(_("Whether to include events."))
        add_option("incevents", incevents)

        incaddresses = BooleanOption(_("Include addresses"), False)
        incaddresses.set_help(_("Whether to include addresses."))
        add_option("incaddresses", incaddresses)

        incsources = BooleanOption(_("Include sources"), False)
        incsources.set_help(_("Whether to include source references."))
        add_option("incsources", incsources)

        incsrcnotes = BooleanOption(_("Include sources notes"), False)
        incsrcnotes.set_help(_("Whether to include source notes in the "
            "Endnotes section. Only works if Include sources is selected."))
        add_option("incsrcnotes", incsrcnotes)

        incmates = BooleanOption(_("Include spouses"), False)
        incmates.set_help(_("Whether to include detailed spouse information."))
        add_option("incmates", incmates)

        incmateref = BooleanOption(_("Include spouse reference"), False)
        incmateref.set_help(_("Whether to include reference to spouse."))
        add_option("incmateref", incmateref)

        incssign = BooleanOption(_("Include sign of succession ('+')"
                                   " in child-list"), True)
        incssign.set_help(_("Whether to include a sign ('+') before the"
                            " descendant number in the child-list to indicate"
                            " a child has succession."))
        add_option("incssign", incssign)

        incpaths = BooleanOption(_("Include path to start-person"), False)
        incpaths.set_help(_("Whether to include the path of descendancy "
                            "from the start-person to each descendant."))
        add_option("incpaths", incpaths)

        # Missing information

        add_option = partial(menu.add_option, _("Missing information"))

        repplace = BooleanOption(_("Replace missing places with ______"), False)
        repplace.set_help(_("Whether to replace missing Places with blanks."))
        add_option("repplace", repplace)

        repdate = BooleanOption(_("Replace missing dates with ______"), False)
        repdate.set_help(_("Whether to replace missing Dates with blanks."))
        add_option("repdate", repdate)

    def make_default_style(self, default_style):
        """Make the default output style for the Detailed Ancestral Report"""
        font = FontStyle()
        font.set(face=FONT_SANS_SERIF, size=16, bold=1)
        para = ParagraphStyle()
        para.set_font(font)
        para.set_header_level(1)
        para.set_top_margin(0.25)
        para.set_bottom_margin(0.25)
        para.set_alignment(PARA_ALIGN_CENTER)
        para.set_description(_('The style used for the title of the page.'))
        default_style.add_paragraph_style("DDRI-Title", para)

        font = FontStyle()
        font.set(face=FONT_SANS_SERIF, size=14, italic=1)
        para = ParagraphStyle()
        para.set_font(font)
        para.set_header_level(2)
        para.set_top_margin(0.25)
        para.set_bottom_margin(0.25)
        para.set_description(_('The style used for the generation header.'))
        default_style.add_paragraph_style("DDRI-Generation", para)

        font = FontStyle()
        font.set(face=FONT_SANS_SERIF, size=10, italic=0, bold=1)
        para = ParagraphStyle()
        para.set_font(font)
        para.set_left_margin(1.5)   # in centimeters
        para.set_top_margin(0.25)
        para.set_bottom_margin(0.25)
        para.set_description(_('The style used for the children list title.'))
        default_style.add_paragraph_style("DDRI-ChildTitle", para)

        font = FontStyle()
        font.set(size=10)
        para = ParagraphStyle()
        para.set_font(font)
        para.set(first_indent=-0.75, lmargin=2.25)
        para.set_top_margin(0.125)
        para.set_bottom_margin(0.125)
        para.set_description(_('The style used for the children list.'))
        default_style.add_paragraph_style("DDRI-ChildList", para)

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

        endnotes.add_endnote_styles(default_style)
