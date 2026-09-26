#!/usr/bin/env python3
"""
csv_to_char_sheet.py
=====================
Fills the official D&D 5e "Character Sheet Fillable" PDF from a CSV of
field values (as produced by dnd_5e_character_sheet.csv), then:

  1. Detects any field whose value would overflow the space available
     for it on the printed page (either the text is too wide for a
     single-line field, too tall for a multi-line box at a normal
     font size, or there simply is no fillable field for it at all).
  2. Splices any overflowing field's full text across a small "glue
     booklet": a stack of pages sized to exactly match that field's own
     box on the sheet, with a blank strip along the top of each page
     left for gluing, so the stack can be cut out, glued together along
     that strip, and glued down over the original box as a flip-up
     insert of the same footprint.
  3. Produces a booklet-ready version of the filled character sheet
     itself: pages are reordered and imposed two-up on landscape
     (11x17 / tabloid-style) sheets so that printing double-sided and
     folding down the middle produces a correctly ordered saddle-
     stitched booklet.

Usage:
    python csv_to_char_sheet.py character.csv blank_sheet.pdf output_dir/

Outputs (written to output_dir/):
    filled_character_sheet.pdf   - the original layout, fields filled in
    overflow_report.txt          - list of anything that didn't fit
    character_sheet_booklet.pdf  - the filled sheet, booklet-imposed
    overflow_glue_booklets.pdf   - only if something overflowed: actual-
                                    size, cut-and-glue insert pages

Requires: pypdf, reportlab  (pip install pypdf reportlab)
"""

import csv
import sys
import os
import textwrap
from dataclasses import dataclass, field as dc_field
from typing import Optional

from pypdf import PdfReader, PdfWriter, Transformation
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.pdfbase.pdfmetrics import stringWidth

# --------------------------------------------------------------------------
# Tunable layout assumptions (the PDF itself doesn't fix a font size for
# most fields - Acrobat auto-sizes them - so these are the sizes we assume
# when *estimating* whether text will fit, for the purposes of flagging
# likely overflow. They match what Acrobat's auto-size usually lands on
# for a form field of this size.)
# --------------------------------------------------------------------------
SINGLE_LINE_FONT_SIZE = 10
MULTI_LINE_FONT_SIZE = 9
FONT_NAME = "Helvetica"
LINE_HEIGHT_FACTOR = 1.18
CELL_PADDING = 3  # points of padding assumed inside every field box

# --------------------------------------------------------------------------
# Static field map: CSV "field" name -> PDF AcroForm field name.
# Only the fields with irregular / non-obvious PDF names need listing;
# everything else (skills, saves, spell levels) is resolved dynamically
# by inspecting the PDF's own field geometry, below.
# --------------------------------------------------------------------------
STATIC_FIELD_MAP = {
    # Header
    "Character Name": "CharacterName",
    "Class & Level": "ClassLevel",
    "Background": "Background",
    "Player Name": "PlayerName",
    "Race": "Race ",
    "Alignment": "Alignment",
    "Experience Points": "XP",
    # Ability scores
    "Strength": "STR", "Strength Modifier": "STRmod",
    "Dexterity": "DEX", "Dexterity Modifier": "DEXmod ",
    "Constitution": "CON", "Constitution Modifier": "CONmod",
    "Intelligence": "INT", "Intelligence Modifier": "INTmod",
    "Wisdom": "WIS", "Wisdom Modifier": "WISmod",
    "Charisma": "CHA", "Charisma Modifier": "CHamod",
    # Core stats
    "Inspiration": "Inspiration",
    "Proficiency Bonus": "ProfBonus",
    "Armor Class": "AC",
    "Initiative": "Initiative",
    "Speed": "Speed",
    "Hit Point Maximum": "HPMax",
    "Current Hit Points": "HPCurrent",
    "Temporary Hit Points": "HPTemp",
    "Hit Dice Total": "HDTotal",
    "Passive Wisdom (Perception)": "Passive",
    # Attacks
    "Attack 1 Name": "Wpn Name", "Attack 1 Bonus": "Wpn1 AtkBonus", "Attack 1 Damage/Type": "Wpn1 Damage",
    "Attack 2 Name": "Wpn Name 2", "Attack 2 Bonus": "Wpn2 AtkBonus ", "Attack 2 Damage/Type": "Wpn2 Damage ",
    "Attack 3 Name": "Wpn Name 3", "Attack 3 Bonus": "Wpn3 AtkBonus  ", "Attack 3 Damage/Type": "Wpn3 Damage ",
    # Equipment / money
    "Copper Pieces (CP)": "CP", "Silver Pieces (SP)": "SP", "Electrum Pieces (EP)": "EP",
    "Gold Pieces (GP)": "GP", "Platinum Pieces (PP)": "PP",
    "Equipment List": "Equipment",
    "Other Proficiencies & Languages": "ProficienciesLang",
    # Traits
    "Personality Traits": "PersonalityTraits ",
    "Ideals": "Ideals",
    "Bonds": "Bonds",
    "Flaws": "Flaws",
    "Features & Traits": "Features and Traits",
    "Additional Features & Traits": "Feat+Traits",
    # Personal characteristics (page 2)
    "Age": "Age", "Height": "Height", "Weight": "Weight",
    "Eyes": "Eyes", "Skin": "Skin", "Hair": "Hair",
    "Character Backstory": "Backstory",
    # Allies
    "Ally/Organization 1 Name": "FactionName",
    "Allies & Organizations Notes": "Allies",
    # Treasure
    "Treasure": "Treasure",
    # Spellcasting header
    "Spellcasting Class": "Spellcasting Class 2",
    "Spellcasting Ability": "SpellcastingAbility 2",
    "Spell Save DC": "SpellSaveDC  2",
    "Spell Attack Bonus": "SpellAtkBonus 2",
}

# Skill/save CSV label -> PDF text-field name (the bonus/value box).
# Proficiency checkboxes are resolved geometrically, see resolve_checkbox().
SKILL_FIELD_MAP = {
    "Acrobatics (Dex)": "Acrobatics",
    "Animal Handling (Wis)": "Animal",
    "Arcana (Int)": "Arcana",
    "Athletics (Str)": "Athletics",
    "Deception (Cha)": "Deception ",
    "History (Int)": "History ",
    "Insight (Wis)": "Insight",
    "Intimidation (Cha)": "Intimidation",
    "Investigation (Int)": "Investigation ",
    "Medicine (Wis)": "Medicine",
    "Nature (Int)": "Nature",
    "Perception (Wis)": "Perception ",
    "Performance (Cha)": "Performance",
    "Persuasion (Cha)": "Persuasion",
    "Religion (Int)": "Religion",
    "Sleight of Hand (Dex)": "SleightofHand",
    "Stealth (Dex)": "Stealth ",
    "Survival (Wis)": "Survival",
}
SAVE_FIELD_MAP = {
    "Strength": "ST Strength", "Dexterity": "ST Dexterity", "Constitution": "ST Constitution",
    "Intelligence": "ST Intelligence", "Wisdom": "ST Wisdom", "Charisma": "ST Charisma",
}

# Fields that are genuinely multi-line boxes on the sheet (word-wrapped).
MULTILINE_FIELDS = {
    "PersonalityTraits ", "Ideals", "Bonds", "Flaws", "AttacksSpellcasting",
    "ProficienciesLang", "Equipment", "Features and Traits", "Allies",
    "Backstory", "Feat+Traits", "Treasure",
}


@dataclass
class FieldInfo:
    name: str
    ftype: str
    page: int          # 1-indexed
    rect: list          # [x0, y0, x1, y1]
    ff: Optional[int] = None


def introspect_fields(pdf_path):
    """Read every AcroForm widget out of the PDF with its page + rect."""
    reader = PdfReader(pdf_path)
    infos = []
    for pageno, page in enumerate(reader.pages, start=1):
        annots = page.get("/Annots")
        if not annots:
            continue
        for a in annots:
            obj = a.get_object()
            name = obj.get("/T")
            parent = obj.get("/Parent")
            if name is None and parent is not None:
                name = parent.get_object().get("/T")
            if name is None:
                continue
            ft = obj.get("/FT")
            if ft is None and parent is not None:
                ft = parent.get_object().get("/FT")
            ff = obj.get("/Ff")
            if ff is None and parent is not None:
                ff = parent.get_object().get("/Ff")
            rect = obj.get("/Rect")
            if rect is None:
                continue
            infos.append(FieldInfo(str(name), str(ft), pageno, [float(x) for x in rect], ff))
    return infos, reader


def y_center(rect):
    return (rect[1] + rect[3]) / 2.0


def resolve_checkbox(text_field, all_fields):
    """Find the checkbox sitting immediately to the left of a text field,
    on the same row (matched by vertical center) and same page."""
    best, best_dy = None, 999
    for f in all_fields:
        if f.ftype != "/Btn" or f.page != text_field.page:
            continue
        if f.rect[0] >= text_field.rect[0]:
            continue  # must be to the left
        dy = abs(y_center(f.rect) - y_center(text_field.rect))
        if dy < 6 and dy < best_dy:
            best, best_dy = f, dy
    return best


def checked_on_value(reader, field_name):
    """Return the '/Yes'-style value that checks a given checkbox field."""
    root = reader.trailer["/Root"]
    acro = root["/AcroForm"]
    for f in acro["/Fields"]:
        obj = f.get_object()
        if str(obj.get("/T")) == field_name:
            ap = obj.get("/AP")
            if ap and "/N" in ap:
                for k in ap["/N"].keys():
                    if k != "/Off":
                        return k
            kids = obj.get("/Kids")
            if kids:
                for kid in kids:
                    ko = kid.get_object()
                    ap = ko.get("/AP")
                    if ap and "/N" in ap:
                        for k in ap["/N"].keys():
                            if k != "/Off":
                                return k
    return "/Yes"


def bucket_x(x, size=5):
    return round(x / size) * size


def build_spell_level_map(all_fields):
    """
    Geometrically discover the cantrip line + 9 leveled spell-slot boxes
    on page 3, without hardcoding ~140 field names. Returns:
        levels[level] = {
            "spells": [field_name, ...] top-to-bottom,
            "checks": [field_name-or-None, ...] aligned with spells,
            "slots_total": field_name or None,
            "slots_expended": field_name or None,
        }
    """
    page3 = [f for f in all_fields if f.page == 3]
    spell_fields = [f for f in page3 if f.name.startswith("Spells")]
    slot_total_fields = [f for f in page3 if f.name.startswith("SlotsTotal")]

    from collections import defaultdict
    columns = defaultdict(list)
    for f in spell_fields:
        columns[bucket_x(f.rect[0])].append(f)
    column_centers = sorted(columns)  # e.g. [40, 230, 415], left to right

    def split_into_boxes(items, gap_threshold=25):
        items = sorted(items, key=lambda f: -f.rect[1])
        boxes, current = [], []
        prev_y = None
        for f in items:
            if prev_y is not None and (prev_y - f.rect[1]) > gap_threshold:
                boxes.append(current)
                current = []
            current.append(f)
            prev_y = f.rect[1]
        if current:
            boxes.append(current)
        return boxes

    def nearest_column(x):
        return min(column_centers, key=lambda c: abs(c - x))

    # bucket each SlotsTotal/SlotsRemaining pair by which spell-column it
    # sits nearest to, then sort each column's pairs top-to-bottom.
    slots_by_column = defaultdict(list)
    for f in slot_total_fields:
        rem_name = "SlotsRemaining" + f.name[len("SlotsTotal"):]
        slots_by_column[nearest_column(f.rect[0])].append((f.rect[1], f.name, rem_name))
    for col in slots_by_column:
        slots_by_column[col].sort(key=lambda t: -t[0])

    # First column's first box (8 lines, no slot pairing) = cantrips
    # (level 0); everything else is levels 1..9 in reading order,
    # left column first, each column's boxes paired to that column's
    # own slot fields in the same top-to-bottom order.
    levels = {}
    level_no = 0
    for col in column_centers:
        boxes = split_into_boxes(columns[col])
        col_slots = list(slots_by_column[col])
        for box in boxes:
            names = [f.name for f in box]
            checks = [ (resolve_checkbox(f, page3).name if resolve_checkbox(f, page3) else None) for f in box ]
            st_name, sr_name = None, None
            if level_no == 0:
                pass  # first box overall is always the cantrip line (no slots)
            elif col_slots:
                _, st_name, sr_name = col_slots.pop(0)
            levels[level_no] = {
                "spells": names,
                "checks": checks,
                "slots_total": st_name,
                "slots_expended": sr_name,
            }
            level_no += 1
            if level_no > 9:
                break
        if level_no > 9:
            break
    return levels


def load_csv(csv_path):
    rows = []
    with open(csv_path, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            rows.append(r)
    return rows


def split_list(text):
    if not text:
        return []
    if "\n" in text:
        parts = [p.strip() for p in text.split("\n")]
    else:
        parts = [p.strip() for p in text.split(",")]
    return [p for p in parts if p]


def estimate_wrapped_lines(text, font_size, box_width):
    usable_width = max(box_width - 2 * CELL_PADDING, 10)
    max_chars = max(int(usable_width / (font_size * 0.5)), 1)
    lines = 0
    for para in text.split("\n"):
        wrapped = textwrap.wrap(para, width=max_chars) or [""]
        lines += len(wrapped)
    return lines


def check_overflow(field_name, text, all_fields_by_name):
    """Return an overflow warning string, or None if it fits."""
    if not text:
        return None
    f = all_fields_by_name.get(field_name)
    if f is None:
        return f"No fillable box exists for this field on the sheet."
    width = f.rect[2] - f.rect[0]
    height = f.rect[3] - f.rect[1]
    if field_name in MULTILINE_FIELDS:
        lines_needed = estimate_wrapped_lines(text, MULTI_LINE_FONT_SIZE, width)
        line_height = MULTI_LINE_FONT_SIZE * LINE_HEIGHT_FACTOR
        lines_available = max(int(height / line_height), 1)
        if lines_needed > lines_available:
            return (f"Text needs ~{lines_needed} lines at {MULTI_LINE_FONT_SIZE}pt but the box "
                    f"only fits ~{lines_available}.")
    else:
        # Acrobat auto-sizes single-line fields to fit the box height, so a
        # short, squat comb field (e.g. a skill bonus) is legitimately meant
        # to hold its text at a small font - scale our assumption to match,
        # rather than flagging every tiny box against a fixed 10pt font.
        font_size = min(SINGLE_LINE_FONT_SIZE, max(6.0, height - 2))
        w = stringWidth(text, FONT_NAME, font_size)
        available = width - 2 * CELL_PADDING
        if w > available:
            return (f"Text is ~{w:.0f}pt wide even at a shrunk {font_size:.1f}pt font, "
                    f"but the box is only {available:.0f}pt wide.")
    return None


def make_glue_booklets(overflow_items, fields_by_name, out_path):
    """
    Build a print-and-cut PDF of small "flip booklets": for each overflowing
    field, splice its full text across as many pages as needed, each page
    sized to exactly match that field's box on the original sheet (so the
    stack can be cut out, stapled/glued along the top strip, and glued
    directly over the original box as a flip-up insert of the same footprint).

    overflow_items: list of (label, text, reason, field_name-or-None)
    """
    GLUE_MARGIN = 26      # blank strip left along the top edge for gluing
    CAPTION_H = 10         # tiny assembly-guide caption printed ABOVE the
                           # cut line (outside the glued piece, trimmed away)
    DEFAULT_W, DEFAULT_H = 200, 140  # fallback size when there's no real box
    SHEET_W, SHEET_H = letter
    PAGE_MARGIN = 36
    GAP_X, GAP_Y = 16, 18

    def wrap_text_lines(text, font_size, box_width):
        usable = max(box_width - 2 * CELL_PADDING, 10)
        max_chars = max(int(usable / (font_size * 0.5)), 1)
        lines = []
        for para in text.split("\n"):
            lines.extend(textwrap.wrap(para, width=max_chars) or [""])
        return lines

    # Build the flat list of individual cut-pieces to pack: (w, h_content,
    # caption, [lines-for-this-piece]). Tiny single-line fields (a 2-3
    # character skill/save bonus that's a couple points too wide) aren't
    # practical to turn into a cut-and-glue booklet - those are left out
    # here and simply called out in overflow_report.txt instead.
    pieces = []
    for label, text, reason, field_name in overflow_items:
        f = fields_by_name.get(field_name) if field_name else None
        if f is not None and field_name not in MULTILINE_FIELDS:
            continue  # minor single-line overflow - not worth a booklet
        if f is not None:
            box_w = f.rect[2] - f.rect[0]
            box_h = f.rect[3] - f.rect[1]
            size_note = ""
        else:
            box_w, box_h = DEFAULT_W, DEFAULT_H
            size_note = " (no box on the original sheet - generic card size)"

        font_size = min(MULTI_LINE_FONT_SIZE, max(6.0, box_h / 2))
        line_height = font_size * LINE_HEIGHT_FACTOR
        lines_per_page = max(1, int(box_h / line_height))
        all_lines = wrap_text_lines(text, font_size, box_w)
        chunks = [all_lines[i:i + lines_per_page] for i in range(0, len(all_lines), lines_per_page)] or [[]]

        total = len(chunks)
        for i, chunk in enumerate(chunks, start=1):
            caption = f"{label}{size_note} - piece {i}/{total}"
            pieces.append((box_w, box_h, font_size, caption, chunk))

    if not pieces:
        c = canvas.Canvas(out_path, pagesize=letter)
        c.setFont("Helvetica", 10)
        c.drawString(50, letter[1] - 60,
                     "All overflow was minor single-line text - see overflow_report.txt.")
        c.save()
        return

    # Shelf-pack the pieces onto letter sheets, left-to-right/top-to-bottom.
    c = canvas.Canvas(out_path, pagesize=letter)
    cursor_x, cursor_y = PAGE_MARGIN, SHEET_H - PAGE_MARGIN
    row_max_h = 0

    def new_sheet():
        nonlocal cursor_x, cursor_y, row_max_h
        c.showPage()
        cursor_x, cursor_y = PAGE_MARGIN, SHEET_H - PAGE_MARGIN
        row_max_h = 0

    for box_w, box_h, font_size, caption, chunk in pieces:
        cell_h = GLUE_MARGIN + box_h
        if cursor_x + box_w > SHEET_W - PAGE_MARGIN:
            cursor_x = PAGE_MARGIN
            cursor_y -= (row_max_h + CAPTION_H + GAP_Y)
            row_max_h = 0
        if cursor_y - (CAPTION_H + cell_h) < PAGE_MARGIN:
            new_sheet()

        top = cursor_y - CAPTION_H
        # assembly-guide caption (trimmed away, outside the cut line) -
        # clipped to this cell's own width so neighboring captions can't
        # bleed into each other in the tightly packed layout.
        c.setFont("Helvetica-Oblique", 6)
        clipped = caption
        while stringWidth(clipped, "Helvetica-Oblique", 6) > box_w and len(clipped) > 4:
            clipped = clipped[:-2]
        c.drawString(cursor_x, cursor_y - CAPTION_H + 2, clipped)
        # cut line around the whole piece (glue strip + content area)
        c.setDash(3, 2)
        c.rect(cursor_x, top - cell_h, box_w, cell_h, stroke=1, fill=0)
        # divider between the blank glue strip and the content area
        c.line(cursor_x, top - GLUE_MARGIN, cursor_x + box_w, top - GLUE_MARGIN)
        c.setDash()
        # content
        c.setFont(FONT_NAME, font_size)
        ty = top - GLUE_MARGIN - font_size
        for line in chunk:
            c.drawString(cursor_x + CELL_PADDING, ty, line)
            ty -= font_size * LINE_HEIGHT_FACTOR

        cursor_x += box_w + GAP_X
        row_max_h = max(row_max_h, cell_h)

    c.save()


def make_booklet(page_objects, out_path):
    """Impose pages 2-up on landscape sheets in booklet (saddle-stitch) order."""
    pages = list(page_objects)
    n = len(pages)
    while n % 4 != 0:
        pages.append(None)
        n += 1
    sheets = n // 4
    order = []
    for i in range(sheets):
        order.append((n - 2 * i, 2 * i + 1))       # front of sheet: left, right
        order.append((2 * i + 2, n - 2 * i - 1))   # back of sheet: left, right

    writer = PdfWriter()
    for left_no, right_no in order:
        left_p = pages[left_no - 1] if 1 <= left_no <= len(pages) else None
        right_p = pages[right_no - 1] if 1 <= right_no <= len(pages) else None
        src = left_p or right_p
        pw = float(src.mediabox.width) if src else 612.0
        ph = float(src.mediabox.height) if src else 792.0
        sheet = writer.add_blank_page(width=2 * pw, height=ph)
        if left_p is not None:
            sheet.merge_transformed_page(left_p, Transformation().translate(0, 0))
        if right_p is not None:
            sheet.merge_transformed_page(right_p, Transformation().translate(pw, 0))
    with open(out_path, "wb") as fh:
        writer.write(fh)


def main(csv_path, pdf_path, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    rows = load_csv(csv_path)
    values = {r["section"] + "||" + r["field"]: (r.get("value") or "").strip() for r in rows}

    all_fields, reader = introspect_fields(pdf_path)
    fields_by_name = {f.name: f for f in all_fields}
    spell_levels = build_spell_level_map(all_fields)

    text_values = {}     # pdf_field_name -> text
    check_values = {}    # pdf_field_name -> True/False
    overflow_items = []  # (label, text, reason, field_name-or-None)

    def get(section, field):
        return values.get(section + "||" + field, "")

    def set_text(pdf_name, text, label):
        if not text:
            return
        text_values[pdf_name] = text
        reason = check_overflow(pdf_name, text, fields_by_name)
        if reason:
            overflow_items.append((label, text, reason, pdf_name))

    # --- static fields -----------------------------------------------
    for r in rows:
        label = f'{r["section"]}: {r["field"]}'
        val = (r.get("value") or "").strip()
        pdf_name = STATIC_FIELD_MAP.get(r["field"])
        if pdf_name:
            set_text(pdf_name, val, label)

    # --- fields that have no box on this template at all --------------
    for section, field in [
        ("Personal Characteristics", "Character Appearance"),
        ("Allies & Organizations", "Ally/Organization 1 Symbol Description"),
    ]:
        val = get(section, field)
        if val:
            reason = check_overflow("__no_field__", val, fields_by_name)
            overflow_items.append((f"{section}: {field}", val, reason, None))

    # --- saving throws --------------------------------------------------
    for ability, pdf_name in SAVE_FIELD_MAP.items():
        prof = get("Saving Throws", f"{ability} Save Proficient")
        bonus = get("Saving Throws", f"{ability} Save Bonus")
        set_text(pdf_name, bonus, f"Saving Throws: {ability} Save Bonus")
        if prof in ("1", "true", "True", "yes", "Yes"):
            cb = resolve_checkbox(fields_by_name[pdf_name], all_fields)
            if cb:
                check_values[cb.name] = True

    # --- skills -----------------------------------------------------
    for label, pdf_name in SKILL_FIELD_MAP.items():
        prof = get("Skills", f"{label} Proficient")
        bonus = get("Skills", f"{label} Bonus")
        set_text(pdf_name, bonus, f"Skills: {label} Bonus")
        if prof in ("1", "true", "True", "yes", "Yes"):
            cb = resolve_checkbox(fields_by_name[pdf_name], all_fields)
            if cb:
                check_values[cb.name] = True

    # --- death saves (checkbox triples) --------------------------------
    successes = get("Core Stats", "Death Save Successes")
    failures = get("Core Stats", "Death Save Failures")
    death_boxes = sorted(
        [f for f in all_fields if f.page == 1 and f.ftype == "/Btn"
         and 440 <= f.rect[1] <= 472 and f.rect[0] > 340],
        key=lambda f: -f.rect[1],
    )
    success_boxes = sorted([f for f in death_boxes if f.rect[1] > 456], key=lambda f: f.rect[0])
    failure_boxes = sorted([f for f in death_boxes if f.rect[1] <= 456], key=lambda f: f.rect[0])
    try:
        for i in range(int(successes or 0)):
            if i < len(success_boxes):
                check_values[success_boxes[i].name] = True
        for i in range(int(failures or 0)):
            if i < len(failure_boxes):
                check_values[failure_boxes[i].name] = True
    except ValueError:
        pass

    # --- spellcasting: cantrips + levels 1-9 --------------------------
    cantrips = split_list(get("Spellcasting", "Cantrips Known"))
    if 0 in spell_levels:
        for text, pdf_name in zip(cantrips, spell_levels[0]["spells"]):
            set_text(pdf_name, text, "Spellcasting: Cantrip")
        if len(cantrips) > len(spell_levels[0]["spells"]):
            extra = ", ".join(cantrips[len(spell_levels[0]["spells"]):])
            overflow_items.append(("Spellcasting: Cantrips Known (extra)", extra,
                                    "More cantrips than there are cantrip lines on the sheet.", None))

    for lvl in range(1, 10):
        info = spell_levels.get(lvl)
        if not info:
            continue
        total = get("Spellcasting", f"Level {lvl} Slots Total")
        expended = get("Spellcasting", f"Level {lvl} Slots Expended")
        if info["slots_total"]:
            set_text(info["slots_total"], total, f"Spellcasting: Level {lvl} Slots Total")
        if info["slots_expended"]:
            set_text(info["slots_expended"], expended, f"Spellcasting: Level {lvl} Slots Expended")

        spells_raw = split_list(get("Spellcasting", f"Level {lvl} Spells (Prepared marked with *)"))
        for i, spell_text in enumerate(spells_raw):
            if i >= len(info["spells"]):
                overflow_items.append((f"Spellcasting: Level {lvl} Spells (extra)",
                                        ", ".join(spells_raw[i:]),
                                        "More spells than there are lines for this level.", None))
                break
            prepared = spell_text.strip().startswith("*")
            clean = spell_text.strip().lstrip("*").strip()
            set_text(info["spells"][i], clean, f"Spellcasting: Level {lvl} Spell")
            if prepared and i < len(info["checks"]) and info["checks"][i]:
                check_values[info["checks"][i]] = True

    # --- write the filled PDF ------------------------------------------
    writer = PdfWriter()
    writer.append(reader)
    for page in writer.pages:
        writer.update_page_form_field_values(page, text_values)
    for cb_name in check_values:
        on_val = checked_on_value(reader, cb_name)
        for page in writer.pages:
            writer.update_page_form_field_values(page, {cb_name: on_val})
    try:
        writer.set_need_appearances_writer(True)
    except Exception:
        pass

    filled_path = os.path.join(out_dir, "filled_character_sheet.pdf")
    with open(filled_path, "wb") as fh:
        writer.write(fh)

    # --- overflow report -------------------------------------------------
    report_path = os.path.join(out_dir, "overflow_report.txt")
    with open(report_path, "w", encoding="utf-8") as fh:
        if not overflow_items:
            fh.write("No overflow detected - everything fits on the sheet.\n")
        else:
            fh.write(f"{len(overflow_items)} field(s) did not fit and were spliced into "
                      "overflow_glue_booklets.pdf:\n\n")
            for label, text, reason, _field_name in overflow_items:
                fh.write(f"- {label}\n    Reason: {reason}\n")

    # --- booklet-impose the filled sheet itself (always) -----------------
    pages_for_booklet = list(PdfReader(filled_path).pages)
    booklet_path = os.path.join(out_dir, "character_sheet_booklet.pdf")
    make_booklet(pages_for_booklet, booklet_path)

    # --- overflow -> glue-in booklets, sized to each field's own box ------
    glue_path = None
    if overflow_items:
        glue_path = os.path.join(out_dir, "overflow_glue_booklets.pdf")
        make_glue_booklets(overflow_items, fields_by_name, glue_path)

    print(f"Filled sheet:   {filled_path}")
    print(f"Overflow report:{report_path}  ({len(overflow_items)} item(s))")
    print(f"Booklet PDF:    {booklet_path}  (print double-sided, flip on short edge, fold in half)")
    if glue_path:
        print(f"Glue booklets:  {glue_path}  (print actual size, cut out, stack in order per "
              "field, glue the blank top strip, and glue that strip over the original box)")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(__doc__)
        sys.exit(1)
    main(sys.argv[1], sys.argv[2], sys.argv[3])
