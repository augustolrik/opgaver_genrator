from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.shapes import Circle, Drawing, Line, Polygon, Rect, String
from reportlab.platypus import Image as RLImage, PageBreak, Paragraph, SimpleDocTemplate, Table, TableStyle
from html import escape
import os
import random

BASE_MAPPE = os.path.dirname(os.path.abspath(__file__))

styles = getSampleStyleSheet()
labyrint_celle_style = styles["Normal"].clone("LabyrintCelle")
labyrint_celle_style.alignment = TA_CENTER
labyrint_celle_style.leading = 9
laes_og_forstaa_style = styles["Normal"].clone("LaesOgForstaa")
laes_og_forstaa_style.fontSize = 8.5
laes_og_forstaa_style.leading = 10
kode_tekst_style = styles["Normal"].clone("KodeOpgaveTekst")
kode_tekst_style.fontSize = 8.5
kode_tekst_style.leading = 10
kode_style = styles["Normal"].clone("KodeOpgaveKode")
kode_style.fontName = "Courier"
kode_style.fontSize = 8
kode_style.leading = 9
hemmelig_kode_style = styles["Normal"].clone("HemmeligKode")
hemmelig_kode_style.fontSize = 8.3
hemmelig_kode_style.leading = 9.5


#%% ---------- HURTIG OPSAETNING ----------

FILNAVN = "opgaver_matematik_bånd_let.pdf"
PDF_MAPPE = r"C:\Python\opgaver_genrator\random_opgaver_pdf"
ANTAL_SIDER = 50
ANTAL_OPGAVER_I_BOKS = 5
MAX_PYRAMIDE_OPGAVER = 3
FIRKANT_AREAL_BILLEDE_STI = os.path.join(BASE_MAPPE, "posters", "firkant_billede.png")
TREKANT_AREAL_BILLEDE_STI = os.path.join(BASE_MAPPE, "posters", "trekant_areal_billede.png")


# Brug navnene herunder i BOKS_VALG.
# Du kan skrive "klokke" eller fx ("plus", "let").
# Vælg 4 bokse til almindelig print eller 8 bokse til dobbeltsidet print.
# Ved 8 bokse bruges de første 4 på forsiderne og de næste 4 på bagsiderne.
# Skriv None for at slukke en boks midlertidigt.

# virker:
# Regning:
# plus, minus, gange, division, procent, broeker
#
# Visuelle regneopgaver:
# visuel_plus (maks 2), visuel_minus (maks 2), visuel_gange (maks 2)
# visuel_division (maks 2), visuel_division_2 (maks 2)
# visuel_procent (maks 2), visuel_broek (maks 2), visuel_areal (maks 2)
#
# Geometri og maaling:
# areal_firkant, omkreds_firkant, areal_trekant
# areal_cirkel, omkreds_cirkel, pytagoras
# vinkel_trekant (maks 3), vinkel_firkant (maks 3)
#
# Algebra og tal:
# ligninger, lav_tallet, find_primtal
#
# Moenstre og logik:
# talpyramide (maks 4), gangepyramide (maks 4), raekkefoelger
# rangering_regnestykker, rutespil (maks 1), labyrint_spil (maks 1)
# kode_opgaver (maks 2), hemmelige_koder (maks 4)
#
# Matematiklaesning:
# laes_og_forstaa (maks 2)
#
# Tid:
# klokke, cykeltid


option_save_1=1
# niveaus = "let", "mellem", "svaer", "random"

if option_save_1==0:
    BOKS_VALG = [
        ("visuel_division", "mellem"),
        ("visuel_areal", "mellem"),
        ("visuel_gange", "mellem"),
        ("visuel_plus","svaer"),
        ("ligninger", "mellem"),
        ("labyrint_spil", "mellem"),
        ("talpyramide", "mellem"),
        ("rutespil", "mellem"),
    ]
if option_save_1==1:
   
       BOKS_VALG = [
        ("visuel_division", "let"),
        ("visuel_areal", "let"),
        ("visuel_gange", "let"),
        ("visuel_plus","mellem"),
        ("ligninger", "let"),
        ("labyrint_spil", "let"),
        ("talpyramide", "let"),
        ("rutespil", "let"),
        ]
if option_save_1==2:
    BOKS_VALG = [
         ("raekkefoelger", "let"),
         ("raekkefoelger", "svaer"),
         ("raekkefoelger", "mellem"),
        ("raekkefoelger", "random"),
    ]

if option_save_1==3:
    BOKS_VALG = [
        ("talpyramide", "mellem"),
        ("ligninger", "let"),
        ("klokke","random"),
        ("cykeltid", "let"),
    ]

BOKS_SKABELONER = {
    "plus": {
        "titel": "Plus",
        "forklaring": "Regn stykkerne og skriv svaret.",
        "generator": ("plus", "random"),
    },
    "visuel_plus": {
        "titel": "Visuel plus",
        "forklaring": "Tæl tingene og skriv svaret.",
        "generator": ("visuel_plus", "random"),
        "maks_antal": 2,
    },
    "minus": {
        "titel": "Minus",
        "forklaring": "Regn stykkerne og skriv svaret.",
        "generator": ("minus", "random"),
    },
    "visuel_minus": {
        "titel": "Visuel minus",
        "forklaring": "Streg fra og skriv hvor mange der er tilbage.",
        "generator": ("visuel_minus", "random"),
        "maks_antal": 2,
    },
    "gange": {
        "titel": "Gange",
        "forklaring": "Regn stykkerne og skriv svaret.",
        "generator": ("gange", "random"),
    },
    "visuel_gange": {
        "titel": "Visuel gange",
        "forklaring": "Tæl rækker og kolonner, og skriv gangestykket.",
        "generator": ("visuel_gange", "random"),
        "maks_antal": 2,
    },
    "division": {
        "titel": "Division",
        "forklaring": "Regn stykkerne og skriv svaret.",
        "generator": ("division", "random"),
    },
    "visuel_division": {
        "titel": "Visuel division",
        "forklaring": "Del tingene ligeligt og skriv svaret.",
        "generator": ("visuel_division", "random"),
        "maks_antal": 2,
    },
    "visuel_division_2": {
        "titel": "Kagedeling",
        "forklaring": "Del kagerne ligeligt mellem dem der spiser.",
        "generator": ("visuel_division_2", "random"),
        "maks_antal": 2,
    },
    "procent": {
        "titel": "Procent",
        "forklaring": "Regn stykkerne og skriv svaret.",
        "generator": ("procent", "random"),
    },
    "broeker": {
        "titel": "Brøker",
        "forklaring": "Regn brøk-opgaverne og skriv svaret.",
        "generator": ("broeker", "random"),
    },
    "visuel_procent": {
        "titel": "Visuel procent",
        "forklaring": "Find hvor mange procent af felterne der er farvet.",
        "generator": ("visuel_procent", "random"),
        "maks_antal": 2,
    },
    "visuel_broek": {
        "titel": "Visuel brøk",
        "forklaring": "Skriv brøken for den farvede del.",
        "generator": ("visuel_broek", "random"),
        "maks_antal": 2,
    },
    "visuel_areal": {
        "titel": "Visuel areal",
        "forklaring": "Hvor mange kager kan der laves af kagedejen?",
        "generator": ("visuel_areal", "random"),
        "maks_antal": 2,
    },
    "areal_firkant": {
        "titel": "Areal af firkanter",
        "forklaring": "Find arealet i hver opgave.",
        "generator": ("areal_firkant", "random"),
    },
     "omkreds_firkant": {
        "titel": "Omkreds af firkanter",
        "forklaring": "Find Omkredsen i hver opgave.",
        "generator": ("omkreds_firkant", "random"),
    }
    
    ,
    "areal_trekant": {
        "titel": "Areal af trekanter",
        "forklaring": "Find arealet i hver opgave.",
        "generator": ("areal_trekant", "random"),
    },
    "areal_cirkel": {
        "titel": "Areal af cirkler",
        "forklaring": "Find arealet i hver opgave.",
        "generator": ("areal_cirkel", "random"),
    },
    "omkreds_cirkel": {
        "titel": "Omkreds af cirkler",
        "forklaring": "Find omkredsen i hver opgave.",
        "generator": ("omkreds_cirkel", "random"),
    },
    "pytagoras": {
        "titel": "Pytagoras",
        "forklaring": "Brug a² + b² = c² til at finde den manglende side.",
        "generator": ("pytagoras", "random"),
    },
    "cykeltid": {
        "titel": "Cykeltid",
        "forklaring": "Regn ud hvor lang tid turen tager.",
        "generator": ("cykeltid", "random"),
    },
    "ligninger": {
        "titel": "Ligninger",
        "forklaring": "Find x eller find x og y i hver opgave.",
        "generator": ("ligning", "random"),
    },
    "klokke": {
        "titel": "Klokke",
        "forklaring": "Find hvor lang tid der er mellem de to klokkesæt.",
        "generator": ("klokke", "random"),
    },
    "talpyramide": {
        "titel": "Talpyramider",
        "forklaring": "Læg de to felter under sammen.",
        "generator": ("talpyramide", "random"),
        "maks_antal": 4,
    },
    "gangepyramide": {
        "titel": "Gangepyramider",
        "forklaring": "Gang de to felter under sammen.",
        "generator": ("gangepyramide", "random"),
        "maks_antal": 4,
    },
    "lav_tallet": {
        "titel": "Lav Tallet",
        "forklaring": "Byg tallet med gange af primtal.",
        "generator": ("lav_tallet", "random"),
    },
    "find_primtal": {
        "titel": "Find primtal",
        "forklaring": "Find primtal blandt tallene.",
        "generator": ("find_primtal", "random"),
    },
    "rangering_regnestykker": {
        "titel": "Ranger regnestykker",
        "forklaring": "Brug overslag. Regn ikke præcist. Sæt fra mindst til størst.",
        "generator": ("rangering_regnestykker", "random"),
        "maks_antal": 2,
    },
    "rutespil": {
        "titel": "Rutespil",
        "forklaring": "Find 3 veje ned til de rigtige tal.",
        "generator": ("rutespil", "random"),
        "maks_antal": 1,
    },
    "vinkel_trekant": {
    "titel": "Trekantvinkler",
    "forklaring": "Find den skjulte vinkel.",
    "generator": ("vinkel_trekant", "random"),
    "maks_antal": 3,
    },
    "vinkel_firkant": {
    "titel": "Firkantvinkler",
    "forklaring": "Find den skjulte vinkel.",
    "generator": ("vinkel_firkant", "random"),
    "maks_antal": 3,
    },
    "labyrint_spil": {
        "titel": "Labyrint Spil",
        "forklaring": "Gå fra START til SLUT gennem labyrinten.",
        "generator": ("labyrint_spil", "random"),
        "maks_antal": 1,
    },
    "raekkefoelger": {
        "titel": "Rækkefølger",
        "forklaring": "Find mønsteret og skriv det manglende led.",
        "generator": ("raekkefoelger", "random"),
    },
    "kode_opgaver": {
        "titel": "Programmeringskode",
        "forklaring": "Læs den lille kode fra top til bund. Skriv værdien til sidst.",
        "generator": ("kode_opgaver", "random"),
        "maks_antal": 2,
    },
    "hemmelige_koder": {
        "titel": "Hemmelige koder",
        "forklaring": "Knæk koden og skriv den hemmelige besked.",
        "generator": ("hemmelige_koder", "random"),
        "maks_antal": 4,
    },
    "laes_og_forstaa": {
        "titel": "Læs og forstå matematik",
        "forklaring": "Læs teksten. Find de oplysninger du skal bruge, og løs opgaven.",
        "generator": ("laes_og_forstaa", "random"),
        "maks_antal": 2,
    },
}



#%% ---------- OPGAVETYPER ----------

import math
import random
import os

def vinkel_trekant_let():
    v1 = random.choice([30, 35, 40, 45, 50, 55, 60])
    v2 = random.choice([40, 45, 50, 55, 60, 65, 70])
    v3 = 180 - v1 - v2
    if v3 <= 15:
        return vinkel_trekant_let()
    return lav_trekant_vinkel_opgave(v1, v2, v3)


def vinkel_trekant_mellem():
    v1 = random.randint(25, 75)
    v2 = random.randint(25, 75)
    v3 = 180 - v1 - v2
    if v3 <= 15:
        return vinkel_trekant_mellem()
    return lav_trekant_vinkel_opgave(v1, v2, v3)


def vinkel_trekant_svaer():
    v1 = random.randint(20, 80)
    v2 = random.randint(20, 80)
    v3 = 180 - v1 - v2
    if v3 <= 10:
        return vinkel_trekant_svaer()
    return lav_trekant_vinkel_opgave(v1, v2, v3)


def vinkel_trekant(niveau="random"):
    if niveau == "random":
        type_opgave = random.choice(["let", "let", "mellem", "mellem", "svaer"])
    else:
        type_opgave = niveau

    if type_opgave == "let":
        return vinkel_trekant_let()
    if type_opgave == "mellem":
        return vinkel_trekant_mellem()
    if type_opgave == "svaer":
        return vinkel_trekant_svaer()
    raise ValueError(f"Ukendt niveau for vinkel_trekant: {niveau}")


def lav_trekant_vinkel_opgave(v1, v2, v3):
    skjult_indeks = random.randint(0, 2)
    labels = [f"{v1}°", f"{v2}°", f"{v3}°"]
    labels[skjult_indeks] = "?"

    tegning = Drawing(120, 80)
    tegning.add(Line(18, 12, 102, 12))
    tegning.add(Line(18, 12, 60, 62))
    tegning.add(Line(102, 12, 60, 62))
    tegning.add(String(8, 2, labels[0], fontSize=11))
    tegning.add(String(94, 2, labels[1], fontSize=11))
    tegning.add(String(56, 66, labels[2], fontSize=11))

    opgave_tabel = Table(
        [
            [Paragraph("Find den skjulte vinkel.", styles["Normal"])],
            [tegning],
        ],
        colWidths=[120],
    )
    opgave_tabel.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    return opgave_tabel


def vinkel_firkant_let():
    v1 = random.choice([70, 80, 90, 100, 110])
    v2 = random.choice([70, 80, 90, 100, 110])
    v3 = random.choice([70, 80, 90, 100, 110])
    v4 = 360 - v1 - v2 - v3
    if v4 <= 20:
        return vinkel_firkant_let()
    return lav_firkant_vinkel_opgave(v1, v2, v3, v4)


def vinkel_firkant_mellem():
    v1 = random.randint(50, 130)
    v2 = random.randint(50, 130)
    v3 = random.randint(50, 130)
    v4 = 360 - v1 - v2 - v3
    if v4 <= 20:
        return vinkel_firkant_mellem()
    return lav_firkant_vinkel_opgave(v1, v2, v3, v4)


def vinkel_firkant_svaer():
    v1 = random.randint(35, 145)
    v2 = random.randint(35, 145)
    v3 = random.randint(35, 145)
    v4 = 360 - v1 - v2 - v3
    if v4 <= 15:
        return vinkel_firkant_svaer()
    return lav_firkant_vinkel_opgave(v1, v2, v3, v4)


def vinkel_firkant(niveau="random"):
    if niveau == "random":
        type_opgave = random.choice(["let", "let", "mellem", "mellem", "svaer"])
    else:
        type_opgave = niveau

    if type_opgave == "let":
        return vinkel_firkant_let()
    if type_opgave == "mellem":
        return vinkel_firkant_mellem()
    if type_opgave == "svaer":
        return vinkel_firkant_svaer()
    raise ValueError(f"Ukendt niveau for vinkel_firkant: {niveau}")


def lav_firkant_vinkel_opgave(v1, v2, v3, v4):
    skjult_indeks = random.randint(0, 3)
    labels = [f"{v1}°", f"{v2}°", f"{v3}°", f"{v4}°"]
    labels[skjult_indeks] = "?"

    tegning = Drawing(130, 85)
    tegning.add(Line(18, 18, 102, 18))
    tegning.add(Line(102, 18, 112, 62))
    tegning.add(Line(112, 62, 30, 70))
    tegning.add(Line(30, 70, 18, 18))
    tegning.add(String(8, 6, labels[0], fontSize=11))
    tegning.add(String(100, 6, labels[1], fontSize=11))
    tegning.add(String(108, 66, labels[2], fontSize=11))
    tegning.add(String(10, 66, labels[3], fontSize=11))

    opgave_tabel = Table(
        [
            [Paragraph("Find den skjulte vinkel.", styles["Normal"])],
            [tegning],
        ],
        colWidths=[125],
    )
    opgave_tabel.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    return opgave_tabel

def gange_let():
    a = random.randint(2, 12)
    b = random.randint(2, 12)
    return f"{a} x {b} ="


def gange_mellem():
    a = random.randint(11, 25)
    b = random.randint(13, 99)
    return f"{a} x {b} ="


def gange_svaer():
    a = random.randint(11, 99)
    b = random.randint(17, 99)
    return f"{a} x {b} ="


def gange(niveau="random"):
    if niveau == "random":
        type_opgave = random.choice(["let",  "mellem", "mellem", "svaer"])
    else:
        type_opgave = niveau

    if type_opgave == "let":
        return gange_let()
    if type_opgave == "mellem":
        return gange_mellem()
    if type_opgave == "svaer":
        return gange_svaer()
    raise ValueError(f"Ukendt niveau for gange: {niveau}")


def lav_visuel_gange_opgave(raekker, kolonner, ting_navn, farve):
    celle_stoerrelse = 12
    prik_radius = 4
    start_x = 44
    start_y = 66
    tegn_bredde = 190
    tegn_hoejde = 94
    samlet_bredde = (kolonner - 1) * celle_stoerrelse
    samlet_hoejde = (raekker - 1) * celle_stoerrelse
    forskyd_x = max(0, (90 - samlet_bredde) / 2)
    forskyd_y = max(0, (58 - samlet_hoejde) / 2)

    tegning = Drawing(tegn_bredde, tegn_hoejde)
    tegning.add(String(10, 78, f"{raekker} raekker", fontSize=10))
    tegning.add(String(126, 78, f"{kolonner} i hver", fontSize=10))

    ramme_x = start_x + forskyd_x - 8
    ramme_y = start_y - forskyd_y - samlet_hoejde - 8
    ramme_bredde = samlet_bredde + 16
    ramme_hoejde = samlet_hoejde + 16
    tegning.add(Rect(ramme_x, ramme_y, ramme_bredde, ramme_hoejde, strokeColor=colors.black, fillColor=None))

    for raekke in range(raekker):
        for kolonne in range(kolonner):
            x = start_x + forskyd_x + kolonne * celle_stoerrelse
            y = start_y - forskyd_y - raekke * celle_stoerrelse
            tegning.add(Circle(x, y, prik_radius, strokeColor=colors.black, fillColor=colors.HexColor(farve)))

    tekst = f"{raekker} x {kolonner} = _____"
    opgave_tabel = Table(
        [
            [Paragraph(f"Hvor mange {ting_navn} er der i alt?", styles["Normal"])],
            [tegning],
            [Paragraph(tekst, styles["Normal"])],
        ],
        colWidths=[190],
    )
    opgave_tabel.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
    ]))
    return opgave_tabel


def vaelg_visuel_ting():
    return random.choice([
        "prikker",
        "cirkler",
        "kugler",
        "kager",
        "planeter",
        "stjerner",
        "perler",
        "knapper",
        "bolde",
    ])


def vaelg_visuel_gange_ting():
    return vaelg_visuel_ting()


def visuel_gange_let():
    raekker = random.choice([2, 3, 4])
    kolonner = random.randint(2, 6)
    return lav_visuel_gange_opgave(raekker, kolonner, vaelg_visuel_gange_ting(), "#2a9d8f")


def visuel_gange_mellem():
    raekker = random.choice([3, 4, 5, 6])
    kolonner = random.randint(4, 8)
    return lav_visuel_gange_opgave(raekker, kolonner, vaelg_visuel_gange_ting(), "#e9c46a")


def visuel_gange_svaer():
    raekker = random.choice([5, 6, 7])
    kolonner = random.randint(6, 9)
    return lav_visuel_gange_opgave(raekker, kolonner, vaelg_visuel_gange_ting(), "#e76f51")


def visuel_gange(niveau="random"):
    if niveau == "random":
        type_opgave = random.choice(["let", "let", "mellem", "mellem", "svaer"])
    else:
        type_opgave = niveau

    if type_opgave == "let":
        return visuel_gange_let()
    if type_opgave == "mellem":
        return visuel_gange_mellem()
    if type_opgave == "svaer":
        return visuel_gange_svaer()
    raise ValueError(f"Ukendt niveau for visuel_gange: {niveau}")



def division_let():
    b = random.randint(2, 10)
    a = b * random.randint(2, 10)
    return f"{a} / {b} ="



def division_mellem():
    b = random.randint(6, 33)
    a = b * random.randint(6, 20)
    return f"{a} / {b} ="



def division_svaer():
    b = random.randint(13, 40)
    a = b * random.randint(11, 66)
    return f"{a} / {b} ="



def division(niveau="random"):
    if niveau == "random":
        type_opgave = random.choice(["let", "mellem", "mellem", "svaer"])
    else:
        type_opgave = niveau

    if type_opgave == "let":
        return division_let()
    if type_opgave == "mellem":
        return division_mellem()
    if type_opgave == "svaer":
        return division_svaer()
    raise ValueError(f"Ukendt niveau for division: {niveau}")


def lav_visuel_division_opgave(antal, grupper, ting_navn, farve):
    kolonner = min(8, antal)
    tegn_bredde = 190
    tegn_hoejde = 104
    start_x = 12
    start_y = 72
    afstand = 14

    tegning = Drawing(tegn_bredde, tegn_hoejde)
    tegning.add(String(10, 90, f"{antal} {ting_navn}", fontSize=10))
    tegning.add(String(136, 90, f"{grupper} grupper", fontSize=10))

    for indeks in range(antal):
        kolonne = indeks % kolonner
        raekke = indeks // kolonner
        x = start_x + (kolonne * afstand)
        y = start_y - (raekke * afstand)
        tegning.add(Circle(x, y, 4.5, strokeColor=colors.black, fillColor=colors.HexColor(farve)))

    boks_bredde = 15
    boks_hoejde = 14
    raekke_mellemrum = 4
    kolonne_mellemrum = 6
    grupper_pr_kolonne = 4 if grupper > 4 else grupper
    antal_gruppe_kolonner = 2 if grupper > 4 else 1
    samlet_gruppe_bredde = (antal_gruppe_kolonner * boks_bredde) + ((antal_gruppe_kolonner - 1) * kolonne_mellemrum)
    gruppe_start_x = 185 - samlet_gruppe_bredde
    gruppe_start_y = 58

    for indeks in range(grupper):
        gruppe_kolonne = indeks // grupper_pr_kolonne
        gruppe_raekke = indeks % grupper_pr_kolonne
        x = gruppe_start_x + gruppe_kolonne * (boks_bredde + kolonne_mellemrum)
        y = gruppe_start_y - gruppe_raekke * (boks_hoejde + raekke_mellemrum)
        tegning.add(Rect(x, y, boks_bredde, boks_hoejde, strokeColor=colors.black, fillColor=None))
        tegning.add(String(x + 6, y + 4, "?", fontSize=9))

    tekst = f"{antal} / {grupper} = _____"
    spoergsmaal = f"Hvor mange {ting_navn} skal der i hver gruppe?"
    opgave_tabel = Table(
        [
            [Paragraph(spoergsmaal, styles["Normal"])],
            [tegning],
            [Paragraph(tekst, styles["Normal"])],
        ],
        colWidths=[190],
    )
    opgave_tabel.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
    ]))
    return opgave_tabel


def visuel_division_let():
    grupper = random.choice([2, 3, 4])
    svar = random.randint(2, 6)
    antal = grupper * svar
    return lav_visuel_division_opgave(antal, grupper, "bolde", "#4dabf7")


def visuel_division_mellem():
    grupper = random.choice([3, 4, 5, 6])
    svar = random.randint(3, 8)
    antal = grupper * svar
    return lav_visuel_division_opgave(antal, grupper, "perler", "#f4a261")


def visuel_division_svaer():
    grupper = random.choice([5, 6, 7, 8])
    svar = random.randint(4, 6)
    antal = grupper * svar
    return lav_visuel_division_opgave(antal, grupper, "stjerner", "#9c89b8")


def visuel_division(niveau="random"):
    if niveau == "random":
        type_opgave = random.choice(["let", "let", "mellem", "mellem", "svaer"])
    else:
        type_opgave = niveau

    if type_opgave == "let":
        return visuel_division_let()
    if type_opgave == "mellem":
        return visuel_division_mellem()
    if type_opgave == "svaer":
        return visuel_division_svaer()
    raise ValueError(f"Ukendt niveau for visuel_division: {niveau}")


def lav_visuel_division_2_opgave(kager, emojis, emoji):
    emoji_font_findes = registrer_emoji_font()
    emoji_font = EMOJI_FONT_NAVN if emoji_font_findes else "Helvetica"
    kolonner = min(8, kager)
    tegn_bredde = 190
    tegn_hoejde = 104
    kage_start_x = 14
    kage_start_y = 72
    afstand = 13
    emoji_start_x = 128
    emoji_start_y = 70
    emoji_mellemrum = 14

    tegning = Drawing(tegn_bredde, tegn_hoejde)
    tegning.add(String(10, 90, f"{kager} kager", fontSize=10))
    tegning.add(String(120, 90, f"{emojis} spiser", fontSize=10))

    for indeks in range(kager):
        kolonne = indeks % kolonner
        raekke = indeks // kolonner
        x = kage_start_x + kolonne * afstand
        y = kage_start_y - raekke * afstand
        tegning.add(Circle(x, y, 4.5, strokeColor=colors.black, fillColor=colors.HexColor("#f4d35e")))
        tegning.add(Circle(x + 1.5, y + 1.5, 0.8, strokeColor=colors.HexColor("#8d5524"), fillColor=colors.HexColor("#8d5524")))

    for indeks in range(emojis):
        y = emoji_start_y - indeks * emoji_mellemrum
        tegning.add(String(emoji_start_x, y, emoji, fontName=emoji_font, fontSize=12))
        tegning.add(String(emoji_start_x + 18, y + 1, "får ___", fontSize=8))

    opgave_tabel = Table(
        [
            [Paragraph("Hvor mange kager kan hver få?", styles["Normal"])],
            [tegning],
            [Paragraph(f"{kager} / {emojis} = _____", styles["Normal"])],
        ],
        colWidths=[190],
    )
    opgave_tabel.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
    ]))
    return opgave_tabel


def vaelg_spise_emoji():
    return random.choice(DYRE_EMOJIS)


def visuel_division_2_let():
    emojis = random.choice([2, 3])
    kager_pr_emoji = random.choice([1, 2, 3])
    kager = emojis * kager_pr_emoji
    return lav_visuel_division_2_opgave(kager, emojis, vaelg_spise_emoji())


def visuel_division_2_mellem():
    emojis = random.choice([2, 3, 4])
    kager_pr_emoji = random.choice([2, 3, 4])
    kager = emojis * kager_pr_emoji
    return lav_visuel_division_2_opgave(kager, emojis, vaelg_spise_emoji())


def visuel_division_2_svaer():
    emojis = random.choice([3, 4, 5])
    kager_pr_emoji = random.choice([2, 3, 4])
    kager = emojis * kager_pr_emoji
    return lav_visuel_division_2_opgave(kager, emojis, vaelg_spise_emoji())


def visuel_division_2(niveau="random"):
    if niveau == "random":
        type_opgave = random.choice(["let", "let", "mellem", "mellem", "svaer"])
    else:
        type_opgave = niveau

    if type_opgave == "let":
        return visuel_division_2_let()
    if type_opgave == "mellem":
        return visuel_division_2_mellem()
    if type_opgave == "svaer":
        return visuel_division_2_svaer()
    raise ValueError(f"Ukendt niveau for visuel_division_2: {niveau}")



def plus_let():
    return f"{random.randint(10, 99)} + {random.randint(10, 99)} ="


def plus_mellem():
    return f"{random.randint(100, 999)} + {random.randint(100, 999)} ="


def plus_svaer():
    return f"{random.randint(1000, 9999)} + {random.randint(1000, 9999)} ="


def plus(niveau="random"):
    if niveau == "random":
        type_opgave = random.choice(["let", "let", "mellem", "mellem", "svaer"])
    else:
        type_opgave = niveau

    if type_opgave == "let":
        return plus_let()
    if type_opgave == "mellem":
        return plus_mellem()
    if type_opgave == "svaer":
        return plus_svaer()
    raise ValueError(f"Ukendt niveau for plus: {niveau}")


def plus_random():
    return plus("random")


def tegn_visuel_regnegruppe(tegn, antal, start_x, start_y, kolonner, farve, streg_fra=0):
    afstand = 12
    for indeks in range(antal):
        kolonne = indeks % kolonner
        raekke = indeks // kolonner
        x = start_x + kolonne * afstand
        y = start_y - raekke * afstand
        tegn.add(Circle(x, y, 4, strokeColor=colors.black, fillColor=colors.HexColor(farve)))
        if indeks >= antal - streg_fra:
            tegn.add(Line(x - 5, y - 5, x + 5, y + 5, strokeColor=colors.red))
            tegn.add(Line(x - 5, y + 5, x + 5, y - 5, strokeColor=colors.red))


def lav_visuel_plus_opgave(a, b, ting_navn, farve):
    tegning = Drawing(190, 92)
    tegning.add(String(14, 76, f"{a} {ting_navn}", fontSize=10))
    tegning.add(String(116, 76, f"{b} {ting_navn}", fontSize=10))
    tegning.add(String(90, 45, "+", fontSize=18))
    tegn_visuel_regnegruppe(tegn=tegning, antal=a, start_x=18, start_y=58, kolonner=5, farve=farve)
    tegn_visuel_regnegruppe(tegn=tegning, antal=b, start_x=116, start_y=58, kolonner=5, farve=farve)

    opgave_tabel = Table(
        [
            [Paragraph(f"Hvor mange {ting_navn} er der i alt?", styles["Normal"])],
            [tegning],
            [Paragraph(f"{a} + {b} = _____", styles["Normal"])],
        ],
        colWidths=[190],
    )
    opgave_tabel.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
    ]))
    return opgave_tabel


def visuel_plus_let():
    a = random.randint(2, 8)
    b = random.randint(2, 8)
    return lav_visuel_plus_opgave(a, b, vaelg_visuel_ting(), "#2a9d8f")


def visuel_plus_mellem():
    a = random.randint(6, 14)
    b = random.randint(6, 14)
    return lav_visuel_plus_opgave(a, b, vaelg_visuel_ting(), "#e9c46a")


def visuel_plus_svaer():
    a = random.randint(10, 18)
    b = random.randint(10, 18)
    return lav_visuel_plus_opgave(a, b, vaelg_visuel_ting(), "#e76f51")


def visuel_plus(niveau="random"):
    if niveau == "random":
        type_opgave = random.choice(["let", "let", "mellem", "mellem", "svaer"])
    else:
        type_opgave = niveau

    if type_opgave == "let":
        return visuel_plus_let()
    if type_opgave == "mellem":
        return visuel_plus_mellem()
    if type_opgave == "svaer":
        return visuel_plus_svaer()
    raise ValueError(f"Ukendt niveau for visuel_plus: {niveau}")



def minus_let():
    a = random.randint(20, 99)
    b = random.randint(10, a - 1)
    return f"{a} - {b} ="


def minus_mellem():
    a = random.randint(100, 999)
    b = random.randint(10, a - 1)
    return f"{a} - {b} ="


def minus_svaer():
    a = random.randint(1000, 9999)
    b = random.randint(100, a - 1)
    return f"{a} - {b} ="


def minus(niveau="random"):
    if niveau == "random":
        type_opgave = random.choice(["let", "let", "mellem", "mellem", "svaer"])
    else:
        type_opgave = niveau

    if type_opgave == "let":
        return minus_let()
    if type_opgave == "mellem":
        return minus_mellem()
    if type_opgave == "svaer":
        return minus_svaer()
    raise ValueError(f"Ukendt niveau for minus: {niveau}")


def minus_random():
    return minus("random")


def lav_visuel_minus_opgave(a, b, ting_navn, farve):
    tegning = Drawing(190, 96)
    tegning.add(String(12, 80, f"{a} {ting_navn}", fontSize=10))
    tegning.add(String(106, 80, f"Kryds {b} ud", fontSize=10))
    tegn_visuel_regnegruppe(tegn=tegning, antal=a, start_x=18, start_y=62, kolonner=9, farve=farve)

    opgave_tabel = Table(
        [
            [Paragraph(f"Kryds {b} {ting_navn} ud. Hvor mange er der tilbage?", styles["Normal"])],
            [tegning],
            [Paragraph(f"{a} - {b} = _____", styles["Normal"])],
        ],
        colWidths=[190],
    )
    opgave_tabel.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
    ]))
    return opgave_tabel


def visuel_minus_let():
    a = random.randint(6, 14)
    b = random.randint(2, a - 2)
    return lav_visuel_minus_opgave(a, b, vaelg_visuel_ting(), "#4dabf7")


def visuel_minus_mellem():
    a = random.randint(12, 22)
    b = random.randint(4, a - 4)
    return lav_visuel_minus_opgave(a, b, vaelg_visuel_ting(), "#f4a261")


def visuel_minus_svaer():
    a = random.randint(20, 30)
    b = random.randint(8, a - 6)
    return lav_visuel_minus_opgave(a, b, vaelg_visuel_ting(), "#9c89b8")


def visuel_minus(niveau="random"):
    if niveau == "random":
        type_opgave = random.choice(["let", "let", "mellem", "mellem", "svaer"])
    else:
        type_opgave = niveau

    if type_opgave == "let":
        return visuel_minus_let()
    if type_opgave == "mellem":
        return visuel_minus_mellem()
    if type_opgave == "svaer":
        return visuel_minus_svaer()
    raise ValueError(f"Ukendt niveau for visuel_minus: {niveau}")



def procent_let():
    procenter = random.choice([10, 20, 25, 50])
    tal = random.choice([20, 40, 60, 80, 100, 200, 400])
    return f"Hvad er {procenter}% af {tal}?"



def procent_mellem():
    procenter = random.choice([5, 10, 15, 20, 25, 30, 40, 50])
    tal = random.randint(20, 500)
    return f"Hvad er {procenter}% af {tal}?"



def procent_svaer():
    type_opgave = random.choice(["af", "stigning", "fald"])

    if type_opgave == "af":
        procenter = random.choice([12, 18, 35, 45, 60, 75])
        tal = random.randint(100, 1000)
        return f"Hvad er {procenter}% af {tal}?"

    if type_opgave == "stigning":
        procenter = random.choice([10, 15, 20, 25, 30])
        tal = random.randint(100, 900)
        return f"{tal} stiger med {procenter}%. Hvad bliver tallet?"

    procenter = random.choice([10, 15, 20, 25, 30, 40])
    tal = random.randint(100, 900)
    return f"{tal} falder med {procenter}%. Hvad bliver tallet?"



def procent(niveau="random"):
    if niveau == "random":
        type_opgave = random.choice(["let", "let", "mellem", "mellem", "svaer"])
    else:
        type_opgave = niveau

    if type_opgave == "let":
        return procent_let()
    if type_opgave == "mellem":
        return procent_mellem()
    if type_opgave == "svaer":
        return procent_svaer()
    raise ValueError(f"Ukendt niveau for procent: {niveau}")



def broeker_let():
    naevner = random.choice([2, 3, 4, 5, 6, 8, 10])
    taeller1 = random.randint(1, naevner - 1)
    taeller2 = random.randint(1, naevner - 1)
    return f"{taeller1}/{naevner} + {taeller2}/{naevner} ="


def broeker_mellem():
    opgavetype = random.choice(["minus", "forkort", "udvid"])

    if opgavetype == "minus":
        naevner = random.choice([3, 4, 5, 6, 8, 10, 12])
        taeller1 = random.randint(1, naevner - 1)
        taeller2 = random.randint(1, taeller1)
        return f"{taeller1}/{naevner} - {taeller2}/{naevner} ="

    if opgavetype == "forkort":
        faktor = random.choice([2, 3, 4, 5])
        grund_taeller = random.randint(1, 9)
        grund_naevner = random.randint(2, 9)
        return f"Forkort {grund_taeller * faktor}/{grund_naevner * faktor}"

    grund_taeller = random.randint(1, 6)
    grund_naevner = random.randint(2, 8)
    faktor = random.choice([2, 3, 4])
    return f"Udvid {grund_taeller}/{grund_naevner} med {faktor}"


def broeker_svaer():
    naevner1 = random.choice([2, 3, 4, 5, 6, 8, 10, 12])
    naevner2 = random.choice([2, 3, 4, 5, 6, 8, 10, 12])
    taeller1 = random.randint(1, naevner1 - 1)
    taeller2 = random.randint(1, naevner2 - 1)
    regnetegn = random.choice(["+", "-"])
    return f"{taeller1}/{naevner1} {regnetegn} {taeller2}/{naevner2} ="


def broeker(niveau="random"):
    if niveau == "random":
        type_opgave = random.choice(["let", "let", "mellem", "mellem", "svaer"])
    else:
        type_opgave = niveau

    if type_opgave == "let":
        return broeker_let()
    if type_opgave == "mellem":
        return broeker_mellem()
    if type_opgave == "svaer":
        return broeker_svaer()
    raise ValueError(f"Ukendt niveau for broeker: {niveau}")


def find_gitter_stoerrelse(antal_felter, max_raekker=10):
    bedste_raekker = 1
    bedste_kolonner = antal_felter

    for raekker in range(1, min(max_raekker, antal_felter) + 1):
        if antal_felter % raekker == 0:
            kolonner = antal_felter // raekker
            if kolonner <= 25 and kolonner - raekker < bedste_kolonner - bedste_raekker:
                bedste_raekker = raekker
                bedste_kolonner = kolonner

    if bedste_raekker > max_raekker or bedste_kolonner > 25:
        raise ValueError(f"Kan ikke lave et gitter for {antal_felter} felter inden for {max_raekker}x25.")

    return bedste_raekker, bedste_kolonner


def har_gyldigt_gitter(antal_felter):
    try:
        find_gitter_stoerrelse(antal_felter)
        return True
    except ValueError:
        return False


def lav_visuel_procent_opgave(antal_felter, farvede_felter, celle_stoerrelse):
    raekker, kolonner = find_gitter_stoerrelse(antal_felter)
    data = [[""] * kolonner for _ in range(raekker)]
    farve = random.choice(
        ["#e76f51", "#2a9d8f", "#e9c46a", "#457b9d", "#8d99ae", "#f4a261"]
    )
    felter = random.sample(range(antal_felter), farvede_felter)

    gitter = Table(
        data,
        colWidths=[celle_stoerrelse] * kolonner,
        rowHeights=[celle_stoerrelse] * raekker,
    )

    style = [
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.black),
    ]

    for felt in felter:
        raekke = felt // kolonner
        kolonne = felt % kolonner
        style.append(("BACKGROUND", (kolonne, raekke), (kolonne, raekke), colors.HexColor(farve)))

    gitter.setStyle(TableStyle(style))

    tekstbredde = max(140, kolonner * celle_stoerrelse)

    opgave_tabel = Table(
        [
            [Paragraph("Farvet procent: _____ %", styles["Normal"])],
            [gitter],
        ],
        colWidths=[tekstbredde],
    )
    opgave_tabel.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    return opgave_tabel


def visuel_procent_let():
    procent = random.choice([10, 20, 25, 30, 40, 50, 60, 70, 75, 80, 90])
    antal_felter = 100
    farvede_felter = antal_felter * procent // 100
    return lav_visuel_procent_opgave(antal_felter, farvede_felter, celle_stoerrelse=10)


def visuel_procent_mellem():
    antal_felter = random.choice([20, 25, 50, 100])
    farvede_felter = random.randint(1, antal_felter - 1)
    return lav_visuel_procent_opgave(antal_felter, farvede_felter, celle_stoerrelse=10)


def visuel_procent_svaer():
    muligheder = []

    for antal_felter in range(20, 201):
        if not har_gyldigt_gitter(antal_felter):
            continue
        gyldige_procenter = [procent for procent in range(5, 96) if (antal_felter * procent) % 100 == 0]
        if gyldige_procenter:
            muligheder.append((antal_felter, gyldige_procenter))

    antal_felter, gyldige_procenter = random.choice(muligheder)
    procent = random.choice(gyldige_procenter)
    farvede_felter = antal_felter * procent // 100
    celle_stoerrelse = 8 if antal_felter > 100 else 9
    return lav_visuel_procent_opgave(antal_felter, farvede_felter, celle_stoerrelse=celle_stoerrelse)


def visuel_procent(niveau="random"):
    if niveau == "random":
        type_opgave = random.choice(["let", "let", "mellem", "mellem", "svaer"])
    else:
        type_opgave = niveau

    if type_opgave == "let":
        return visuel_procent_let()
    if type_opgave == "mellem":
        return visuel_procent_mellem()
    if type_opgave == "svaer":
        return visuel_procent_svaer()
    raise ValueError(f"Ukendt niveau for visuel_procent: {niveau}")


def lav_visuel_broek_gitter(antal_felter, farvede_felter, celle_stoerrelse):
    raekker, kolonner = find_gitter_stoerrelse(antal_felter, max_raekker=5)
    data = [[""] * kolonner for _ in range(raekker)]
    farve = random.choice(
        ["#e76f51", "#2a9d8f", "#e9c46a", "#457b9d", "#8d99ae", "#f4a261"]
    )
    felter = random.sample(range(antal_felter), farvede_felter)

    gitter = Table(
        data,
        colWidths=[celle_stoerrelse] * kolonner,
        rowHeights=[celle_stoerrelse] * raekker,
    )

    style = [
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.black),
    ]

    for felt in felter:
        raekke = felt // kolonner
        kolonne = felt % kolonner
        style.append(("BACKGROUND", (kolonne, raekke), (kolonne, raekke), colors.HexColor(farve)))

    gitter.setStyle(TableStyle(style))
    return gitter, max(70, kolonner * celle_stoerrelse)


def lav_visuel_broek_opgave(antal_felter, farvede_felter1, farvede_felter2, celle_stoerrelse):
    gitter1, bredde1 = lav_visuel_broek_gitter(antal_felter, farvede_felter1, celle_stoerrelse)
    gitter2, bredde2 = lav_visuel_broek_gitter(antal_felter, farvede_felter2, celle_stoerrelse)
    plus_tegn = Paragraph("<b>+</b>", styles["Normal"])

    opgave_tabel = Table(
        [
            [gitter1, plus_tegn, gitter2],
            [Paragraph("Skriv svaret: ____________", styles["Normal"]), "", ""],
        ],
        colWidths=[bredde1, 20, bredde2],
    )
    opgave_tabel.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("SPAN", (0, 1), (2, 1)),
    ]))
    return opgave_tabel


def visuel_broek_let():
    antal_felter = random.choice([2, 4, 6, 8, 10])
    farvede_felter1 = random.randint(1, antal_felter - 1)
    farvede_felter2 = random.randint(1, antal_felter - 1)
    return lav_visuel_broek_opgave(antal_felter, farvede_felter1, farvede_felter2, celle_stoerrelse=14)


def visuel_broek_mellem():
    antal_felter = random.choice([6, 8, 9, 10, 12, 15, 16])
    farvede_felter1 = random.randint(1, antal_felter - 1)
    farvede_felter2 = random.randint(1, antal_felter - 1)
    return lav_visuel_broek_opgave(antal_felter, farvede_felter1, farvede_felter2, celle_stoerrelse=12)


def visuel_broek_svaer():
    antal_felter = random.choice([12, 15, 16, 18, 20, 24])
    farvede_felter1 = random.randint(1, antal_felter - 1)
    farvede_felter2 = random.randint(1, antal_felter - 1)
    return lav_visuel_broek_opgave(antal_felter, farvede_felter1, farvede_felter2, celle_stoerrelse=10)


def visuel_broek(niveau="random"):
    if niveau == "random":
        type_opgave = random.choice(["let", "let", "mellem", "mellem", "svaer"])
    else:
        type_opgave = niveau

    if type_opgave == "let":
        return visuel_broek_let()
    if type_opgave == "mellem":
        return visuel_broek_mellem()
    if type_opgave == "svaer":
        return visuel_broek_svaer()
    raise ValueError(f"Ukendt niveau for visuel_broek: {niveau}")


def lav_visuel_areal_tabel(spoergsmaal, tegning):
    opgave_tabel = Table(
        [
            [Paragraph(spoergsmaal, styles["Normal"])],
            [tegning],
        ],
        colWidths=[190],
    )
    opgave_tabel.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("VALIGN", (0, 0), (-1, 0), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 0),
        ("TOPPADDING", (0, 1), (-1, 1), 0),
        ("BOTTOMPADDING", (0, 1), (-1, 1), 2),
    ]))
    return opgave_tabel


def tegn_kvadrat_med_gitter(tegn, x, y, celler_pr_side, celle_stoerrelse, farve):
    samlet = celler_pr_side * celle_stoerrelse
    tegn.add(Rect(x, y, samlet, samlet, strokeColor=colors.black, fillColor=colors.HexColor(farve)))

    for indeks in range(1, celler_pr_side):
        offset = indeks * celle_stoerrelse
        tegn.add(Line(x + offset, y, x + offset, y + samlet, strokeColor=colors.white))
        tegn.add(Line(x, y + offset, x + samlet, y + offset, strokeColor=colors.white))

    return samlet


def tegn_trekant(tegn, punkter, farve):
    tegn.add(
        Polygon(
            punkter,
            strokeColor=colors.black,
            fillColor=colors.HexColor(farve),
        )
    )


def visuel_areal_let():
    lille_side = random.choice([2, 3, 4, 5])
    faktor = random.choice([2, 3, 4, 5])
    stor_side = lille_side * faktor
    celle_stoerrelse = 14
    stor_tegn_side = faktor * celle_stoerrelse

    tegning = Drawing(190, 108)
    tegning.add(String(12, 90, "1 kage", fontSize=10))
    tegning.add(Rect(18, 44, 24, 24, strokeColor=colors.black, fillColor=colors.HexColor("#f4d35e")))
    tegning.add(String(12, 28, f"{lille_side} cm", fontSize=9))

    tegning.add(String(86, 90, "Kagedej", fontSize=10))
    tegn_kvadrat_med_gitter(tegn=tegning, x=92, y=16, celler_pr_side=faktor, celle_stoerrelse=celle_stoerrelse, farve="#ee964b")
    tegning.add(String(92, 3, f"{stor_side} cm", fontSize=9))
    tegning.add(String(92 + stor_tegn_side + 6, 16 + (stor_tegn_side / 2), f"{stor_side} cm", fontSize=9))

    return lav_visuel_areal_tabel("Hvor mange firkantede kager? _____", tegning)


def visuel_areal_mellem():
    lille_side = random.choice([2, 3, 4, 5])
    faktor = random.choice([2, 3, 4, 5])
    stor_side = lille_side * faktor
    celle_stoerrelse = 14
    stor_tegn_side = faktor * celle_stoerrelse

    tegning = Drawing(190, 114)
    tegning.add(String(12, 90, "1 kage", fontSize=10))
    tegn_trekant(tegn=tegning, punkter=[18, 42, 18, 70, 46, 42], farve="#9c89b8")
    tegning.add(String(12, 28, f"{lille_side} cm", fontSize=9))

    tegning.add(String(86, 98, "Kagedej", fontSize=10))
    tegning.add(Rect(92, 18, stor_tegn_side, stor_tegn_side, strokeColor=colors.black, fillColor=colors.HexColor("#84a59d")))
    for række in range(faktor):
        for kolonne in range(faktor):
            x = 92 + (kolonne * celle_stoerrelse)
            y = 18 + (række * celle_stoerrelse)
            tegning.add(Line(x, y, x + celle_stoerrelse, y + celle_stoerrelse, strokeColor=colors.white))
            if kolonne > 0:
                tegning.add(Line(x, 18, x, 18 + stor_tegn_side, strokeColor=colors.white))
            if række > 0:
                tegning.add(Line(92, y, 92 + stor_tegn_side, y, strokeColor=colors.white))

    tegning.add(String(92, 1, f"{stor_side} cm", fontSize=9))
    tegning.add(String(92 + stor_tegn_side + 6, 18 + (stor_tegn_side / 2), f"{stor_side} cm", fontSize=9))

    return lav_visuel_areal_tabel("Hvor mange trekantede kager? _____", tegning)


def visuel_areal_svaer():
    lille_side = random.choice([2, 3, 4, 5])
    faktor = random.choice([2, 3, 4, 5])
    stor_side = lille_side * faktor
    trin = 16
    stor_tegn_side = faktor * trin
    start_x = 92
    start_y = 8

    tegning = Drawing(190, 118)
    tegning.add(String(12, 90, "1 kage", fontSize=10))
    tegn_trekant(tegn=tegning, punkter=[18, 38, 18, 66, 46, 38], farve="#e5989b")
    tegning.add(String(12, 24, f"{lille_side} cm", fontSize=9))

    tegning.add(String(86, 100, "Kagedej", fontSize=10))
    tegn_trekant(
        tegn=tegning,
        punkter=[start_x, start_y, start_x, start_y + stor_tegn_side, start_x + stor_tegn_side, start_y],
        farve="#a8dadc",
    )

    for indeks in range(1, faktor):
        offset = indeks * trin
        tegning.add(Line(start_x, start_y + offset, start_x + offset, start_y, strokeColor=colors.white))
        tegning.add(Line(start_x + offset, start_y, start_x + offset, start_y + stor_tegn_side - offset, strokeColor=colors.white))
        tegning.add(Line(start_x, start_y + offset, start_x + stor_tegn_side - offset, start_y + offset, strokeColor=colors.white))

    tegning.add(String(start_x, -2, f"{stor_side} cm", fontSize=9))
    tegning.add(String(start_x - 4, start_y + stor_tegn_side + 6, f"{stor_side} cm", fontSize=9))

    return lav_visuel_areal_tabel("Hvor mange trekantede kager? _____", tegning)


def visuel_areal(niveau="random"):
    if niveau == "random":
        type_opgave = random.choice(["let", "let", "mellem", "mellem", "svaer"])
    else:
        type_opgave = niveau

    if type_opgave == "let":
        return visuel_areal_let()
    if type_opgave == "mellem":
        return visuel_areal_mellem()
    if type_opgave == "svaer":
        return visuel_areal_svaer()
    raise ValueError(f"Ukendt niveau for visuel_areal: {niveau}")


def lav_opgave_med_billede(tekst, billede_sti, maks_bredde=90, maks_hoejde=42):
    elementer = [[Paragraph(tekst, styles["Normal"])]]

    if os.path.exists(billede_sti):
        billede = RLImage(billede_sti)
        skalering = min(maks_bredde / billede.imageWidth, maks_hoejde / billede.imageHeight)
        billede.drawWidth = billede.imageWidth * skalering
        billede.drawHeight = billede.imageHeight * skalering

        elementer = [[Paragraph(tekst, styles["Normal"]), billede]]
    else:
        elementer = [[Paragraph(tekst, styles["Normal"])]]

    opgave_tabel = Table(elementer, colWidths=[140, 100])
    opgave_tabel.setStyle(TableStyle([
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("ALIGN", (1, 0), (1, 0), "RIGHT"),  # image column
    ("LEFTPADDING", (0, 0), (-1, -1), 0),
    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
    ]))
    return opgave_tabel


def ligning_let():
    x = random.randint(1, 10)
    a = random.randint(1, 20)
    b = x + a
    return f"x + {a} = {b}"



def ligning_mellem():
    type_opgave = random.choice(["gange", "minus", "dividere"])

    if type_opgave == "gange":
        x = random.randint(2, 12)
        a = random.randint(2, 10)
        return f"{a}x = {a * x}"

    if type_opgave == "minus":
        x = random.randint(5, 30)
        a = random.randint(1, x - 1)
        return f"x - {a} = {x - a}"

    x = random.randint(2, 12)
    a = random.randint(2, 10)
    return f"x / {a} = {x}"



def ligning_svaer():
    while True:
        a1 = random.randint(1, 5)
        b1 = random.randint(1, 5)
        a2 = random.randint(1, 5)
        b2 = random.randint(1, 5)
        if a1 * b2 != a2 * b1:
            break

    x = random.randint(1, 10)
    y = random.randint(1, 10)
    c1 = a1 * x + b1 * y
    c2 = a2 * x + b2 * y
    return f"{a1}x + {b1}y = {c1}<br/>{a2}x + {b2}y = {c2}"



def ligning(niveau="random"):
    if niveau == "random":
        type_opgave = random.choice(["let", "let", "mellem", "mellem", "svaer"])
    else:
        type_opgave = niveau

    if type_opgave == "let":
        return ligning_let()
    if type_opgave == "mellem":
        return ligning_mellem()
    if type_opgave == "svaer":
        return ligning_svaer()
    raise ValueError(f"Ukendt niveau for ligning: {niveau}")



def klokke_let():
    tilladte_minutter = [0, 15, 30, 45]
    start_h = random.randint(1, 18)
    start_m = random.choice(tilladte_minutter)
    start_minutter = (start_h * 60) + start_m
    forskel_minutter = random.choice([15, 30, 45, 60, 75, 90, 105, 120])
    slut_minutter = start_minutter + forskel_minutter

    start_h, start_m = divmod(start_minutter, 60)
    slut_h, slut_m = divmod(slut_minutter, 60)
    return f"Fra kl. {start_h:02d}:{start_m:02d} til kl. {slut_h:02d}:{slut_m:02d}?"


def klokke_mellem():
    tilladte_minutter = [0, 10, 20, 25, 30, 40, 50, 55]
    start_h = random.randint(1, 18)
    start_m = random.choice(tilladte_minutter)
    start_minutter = (start_h * 60) + start_m
    forskel_minutter = random.choice([20, 25, 30, 40, 50, 55, 70, 80, 95, 110])
    slut_minutter = start_minutter + forskel_minutter

    start_h, start_m = divmod(start_minutter, 60)
    slut_h, slut_m = divmod(slut_minutter, 60)
    return f"Fra kl. {start_h:02d}:{start_m:02d} til kl. {slut_h:02d}:{slut_m:02d}?"


def klokke_svaer():
    start_minutter = random.randint(1, 18 * 60)
    forskel_minutter = random.choice([17, 23, 33, 48, 53, 69, 75, 88, 92, 103, 116])
    slut_minutter = start_minutter + forskel_minutter

    start_h, start_m = divmod(start_minutter, 60)
    slut_h, slut_m = divmod(slut_minutter, 60)
    return f"Fra kl. {start_h:02d}:{start_m:02d} til kl. {slut_h:02d}:{slut_m:02d}?"


def klokke(niveau="random"):
    if niveau == "random":
        type_opgave = random.choice(["let", "let", "mellem", "mellem", "svaer"])
    else:
        type_opgave = niveau

    if type_opgave == "let":
        return klokke_let()
    if type_opgave == "mellem":
        return klokke_mellem()
    if type_opgave == "svaer":
        return klokke_svaer()
    raise ValueError(f"Ukendt niveau for klokke: {niveau}")


def areal_firkant_let():
    laengde = random.randint(2, 12)
    bredde = random.randint(2, 12)
    tekst = f" Længde {laengde} m og bredde {bredde} m."
    return lav_opgave_med_billede(tekst, FIRKANT_AREAL_BILLEDE_STI)


def areal_firkant_mellem():
    laengde = random.randint(10, 35)
    bredde = random.randint(5, 25)
    tekst = f"Længde {laengde} m og bredde {bredde} m."
    return lav_opgave_med_billede(tekst, FIRKANT_AREAL_BILLEDE_STI)


def areal_firkant_svaer():
    laengde = random.randint(12, 40)
    bredde = random.randint(8, 30)
    tekst = f"Længde {laengde} m og bredde {bredde} m."
    return lav_opgave_med_billede(tekst, FIRKANT_AREAL_BILLEDE_STI)


def areal_firkant(niveau="random"):
    if niveau == "random":
        type_opgave = random.choice(["let", "let", "mellem", "mellem", "svaer"])
    else:
        type_opgave = niveau

    if type_opgave == "let":
        return areal_firkant_let()
    if type_opgave == "mellem":
        return areal_firkant_mellem()
    if type_opgave == "svaer":
        return areal_firkant_svaer()
    raise ValueError(f"Ukendt niveau for areal_firkant: {niveau}")


def omkreds_firkant_let():
    laengde = random.randint(5, 25)
    bredde = random.randint(5, 25)
    tekst = f"Længde {laengde} m og bredde {bredde} m."
    return lav_opgave_med_billede(tekst, FIRKANT_AREAL_BILLEDE_STI)

def omkreds_firkant_mellem():
    laengde = random.randint(10, 35)
    bredde = random.randint(5, 25)
    tekst = f"Længde {laengde} m og bredde {bredde} m."
    return lav_opgave_med_billede(tekst, FIRKANT_AREAL_BILLEDE_STI)


def omkreds_firkant_svaer():
    laengde = random.randint(12, 40)
    bredde = random.randint(13, 30)
    tekst = f"Længde {laengde} m og bredde {bredde} cm."
    return lav_opgave_med_billede(tekst, FIRKANT_AREAL_BILLEDE_STI)


def omkreds_firkant(niveau="random"):
    if niveau == "random":
        type_opgave = random.choice(["let", "let", "mellem", "mellem", "svaer"])
    else:
        type_opgave = niveau

    if type_opgave == "let":
        return omkreds_firkant_let()
    if type_opgave == "mellem":
        return omkreds_firkant_mellem()
    if type_opgave == "svaer":
        return omkreds_firkant_svaer()
    raise ValueError(f"Ukendt niveau for omkreds_firkant: {niveau}")

def areal_trekant_let():
    grundlinje = random.randint(2, 12)
    hoejde = random.randint(2, 12)
    tekst = f"Grundlinje {grundlinje} m og højde {hoejde} m."
    return lav_opgave_med_billede(tekst, TREKANT_AREAL_BILLEDE_STI)


def areal_trekant_mellem():
    grundlinje = random.randint(8, 24)
    hoejde = random.randint(6, 20)
    tekst = f"Grundlinje {grundlinje} m og højde {hoejde} m."
    return lav_opgave_med_billede(tekst, TREKANT_AREAL_BILLEDE_STI)


def areal_trekant_svaer():
    grundlinje = random.randint(12, 36)
    hoejde = random.randint(10, 28)
    tekst = f"Grundlinje {grundlinje} m og højde {hoejde} m."
    return lav_opgave_med_billede(tekst, TREKANT_AREAL_BILLEDE_STI)


def areal_trekant(niveau="random"):
    if niveau == "random":
        type_opgave = random.choice(["let", "let", "mellem", "mellem", "svaer"])
    else:
        type_opgave = niveau

    if type_opgave == "let":
        return areal_trekant_let()
    if type_opgave == "mellem":
        return areal_trekant_mellem()
    if type_opgave == "svaer":
        return areal_trekant_svaer()
    raise ValueError(f"Ukendt niveau for areal_trekant: {niveau}")


def areal_cirkel_let():
    radius = random.randint(2, 10)
    return f"Find arealet af en cirkel med radius {radius} cm. Brug π."


def areal_cirkel_mellem():
    diameter = random.randint(6, 24)
    return f"Find arealet af en cirkel med diameter {diameter} cm. Brug π."


def areal_cirkel_svaer():
    radius = random.randint(5, 20)
    return f"Find arealet af en cirkel med radius {radius} m. Giv svaret med π eller afrundet."


def areal_cirkel(niveau="random"):
    if niveau == "random":
        type_opgave = random.choice(["let", "let", "mellem", "mellem", "svaer"])
    else:
        type_opgave = niveau

    if type_opgave == "let":
        return areal_cirkel_let()
    if type_opgave == "mellem":
        return areal_cirkel_mellem()
    if type_opgave == "svaer":
        return areal_cirkel_svaer()
    raise ValueError(f"Ukendt niveau for areal_cirkel: {niveau}")


def omkreds_cirkel_let():
    radius = random.randint(2, 10)
    return f"Find omkredsen af en cirkel med radius {radius} cm. Brug π."


def omkreds_cirkel_mellem():
    diameter = random.randint(6, 30)
    return f"Find omkredsen af en cirkel med diameter {diameter} cm. Brug π."


def omkreds_cirkel_svaer():
    if random.choice([True, False]):
        radius = random.randint(5, 30)
        return f"Find omkredsen af en cirkel med radius {radius} m. Giv svaret med π eller afrundet."

    diameter = random.randint(12, 80)
    return f"Find omkredsen af en cirkel med diameter {diameter} m. Giv svaret med π eller afrundet."


def omkreds_cirkel(niveau="random"):
    if niveau == "random":
        type_opgave = random.choice(["let", "let", "mellem", "mellem", "svaer"])
    else:
        type_opgave = niveau

    if type_opgave == "let":
        return omkreds_cirkel_let()
    if type_opgave == "mellem":
        return omkreds_cirkel_mellem()
    if type_opgave == "svaer":
        return omkreds_cirkel_svaer()
    raise ValueError(f"Ukendt niveau for omkreds_cirkel: {niveau}")


def lav_pytagoras_opgave(a, b, c, ukendt):
    if ukendt == "c":
        return f"Retvinklet trekant: a = {a} cm og b = {b} cm. Find c. a² + b² = c²"
    if ukendt == "a":
        return f"Retvinklet trekant: b = {b} cm og c = {c} cm. Find a. a² + b² = c²"
    return f"Retvinklet trekant: a = {a} cm og c = {c} cm. Find b. a² + b² = c²"


def pytagoras_let():
    a, b, c = random.choice([(3, 4, 5), (5, 12, 13), (6, 8, 10), (8, 15, 17)])
    return lav_pytagoras_opgave(a, b, c, "c")


def pytagoras_mellem():
    a, b, c = random.choice([(7, 24, 25), (9, 12, 15), (10, 24, 26), (12, 16, 20), (15, 20, 25)])
    ukendt = random.choice(["c", "c", "a", "b"])
    return lav_pytagoras_opgave(a, b, c, ukendt)


def pytagoras_svaer():
    a, b, c = random.choice([(11, 60, 61), (12, 35, 37), (16, 30, 34), (20, 21, 29), (28, 45, 53)])
    ukendt = random.choice(["c", "a", "b"])
    enhed = random.choice(["cm", "m"])

    if ukendt == "c":
        return f"Retvinklet trekant: a = {a} {enhed} og b = {b} {enhed}. Find c. a² + b² = c²"
    if ukendt == "a":
        return f"Retvinklet trekant: b = {b} {enhed} og c = {c} {enhed}. Find a. a² + b² = c²"
    return f"Retvinklet trekant: a = {a} {enhed} og c = {c} {enhed}. Find b. a² + b² = c²"


def pytagoras(niveau="random"):
    if niveau == "random":
        type_opgave = random.choice(["let", "let", "mellem", "mellem", "svaer"])
    else:
        type_opgave = niveau

    if type_opgave == "let":
        return pytagoras_let()
    if type_opgave == "mellem":
        return pytagoras_mellem()
    if type_opgave == "svaer":
        return pytagoras_svaer()
    raise ValueError(f"Ukendt niveau for pytagoras: {niveau}")


def cykeltid_let():
    fart = random.choice([10, 12, 15, 20])
    afstand = random.choice([5, 10, 15, 20, 25, 30])
    return f"Hvor lang tid tager det at cykle {afstand} km, hvis man cykler {fart} km/t?"


def cykeltid_mellem():
    fart = random.choice([12, 14, 16, 18, 20, 24])
    afstand = random.choice([12, 18, 24, 30, 36, 42, 48])
    return f"Hvor lang tid tager det at cykle {afstand} km, hvis man cykler {fart} km/t?"


def cykeltid_svaer():
    fart = random.choice([9, 11, 13, 15, 18, 22])
    afstand = random.choice([14, 21, 28, 35, 44, 55, 66])
    return f"Hvor lang tid tager det at cykle {afstand} km, hvis man cykler {fart} km/t?"


def cykeltid(niveau="random"):
    if niveau == "random":
        type_opgave = random.choice(["let", "let", "mellem", "mellem", "svaer"])
    else:
        type_opgave = niveau

    if type_opgave == "let":
        return cykeltid_let()
    if type_opgave == "mellem":
        return cykeltid_mellem()
    if type_opgave == "svaer":
        return cykeltid_svaer()
    raise ValueError(f"Ukendt niveau for cykeltid: {niveau}")


RAEKKEFOELGE_DYR = ["🐯", "🐷", "🐮", "🐶", "🐱", "🐰"]


def lav_raekkefoelge_layout(led):
    emoji_font_findes = registrer_emoji_font()
    font_navn = EMOJI_FONT_NAVN if emoji_font_findes else "Helvetica"
    data = [[str(led_tekst) for led_tekst in led]]

    tabel = Table(data, colWidths=[26] * len(led), rowHeights=[24])
    tabel.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.75, colors.black),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("FONTNAME", (0, 0), (-1, -1), font_navn),
        ("FONTSIZE", (0, 0), (-1, -1), 12),
        ("LEFTPADDING", (0, 0), (-1, -1), 2),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2),
        ("TOPPADDING", (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
    ]))
    return tabel


def lav_raekkefoelge_svarraekke(svar, bredde):
    emoji_font_findes = registrer_emoji_font()
    font_navn = EMOJI_FONT_NAVN if emoji_font_findes else "Helvetica"
    antal = len(svar)
    data = [[str(svar_tekst) for svar_tekst in svar]]
    tabel = Table(data, colWidths=[bredde / antal] * antal, rowHeights=[18])
    tabel.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 0.75, colors.black),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("FONTNAME", (0, 0), (-1, -1), font_navn),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 2),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2),
        ("TOPPADDING", (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
    ]))
    return tabel


def lav_raekkefoelge_med_hul(fuld_raekke, hul_indeks=None):
    if hul_indeks is None:
        hul_indeks = random.randint(2, len(fuld_raekke) - 2)
    led = [str(v) for v in fuld_raekke]
    svar = str(fuld_raekke[hul_indeks])
    led[hul_indeks] = "?"
    opgave = lav_raekkefoelge_layout(led)
    opgave.raekkefoelge_svar = svar
    return opgave


def raekkefoelger_let():
    moenster_laengde = random.choice([2, 3])
    moenster = random.sample(RAEKKEFOELGE_DYR, moenster_laengde)
    fuld_raekke = [moenster[i % moenster_laengde] for i in range(6)]
    hul_indeks = random.choice([3, 4, 5])
    return lav_raekkefoelge_med_hul(fuld_raekke, hul_indeks)


def raekkefoelger_mellem():
    opgavetype = random.choice(["plus", "minus", "gange"])

    if opgavetype == "plus":
        start = random.randint(2, 25)
        trin = random.choice([2, 3, 4, 5, 10])
        fuld_raekke = [start + trin * i for i in range(6)]
    elif opgavetype == "minus":
        trin = random.choice([2, 3, 4, 5, 10])
        start = random.randint(35, 80)
        fuld_raekke = [start - trin * i for i in range(6)]
    else:
        start = random.choice([2, 3, 4, 5])
        faktor = random.choice([2, 3])
        fuld_raekke = [start * (faktor ** i) for i in range(6)]

    return lav_raekkefoelge_med_hul(fuld_raekke)


def raekkefoelger_svaer():
    opgavetype = random.choice(["skiftende_plus", "kvadrater", "fibonacci"])

    if opgavetype == "skiftende_plus":
        a = random.randint(3, 14)
        trin1 = random.choice([2, 3, 4, 5])
        trin2 = random.choice([6, 7, 8, 9])
        fuld_raekke = [a]
        for i in range(1, 6):
            fuld_raekke.append(fuld_raekke[-1] + (trin1 if i % 2 == 1 else trin2))
    elif opgavetype == "kvadrater":
        start = random.randint(2, 6)
        fuld_raekke = [(start + i) ** 2 for i in range(6)]
    else:
        a = random.randint(2, 8)
        b = random.randint(3, 10)
        fuld_raekke = [a, b]
        for _ in range(4):
            fuld_raekke.append(fuld_raekke[-1] + fuld_raekke[-2])

    return lav_raekkefoelge_med_hul(fuld_raekke)


def raekkefoelger(niveau="random"):
    if niveau == "random":
        type_opgave = random.choice(["let", "let", "mellem", "mellem", "svaer"])
    else:
        type_opgave = niveau

    if type_opgave == "let":
        return raekkefoelger_let()
    if type_opgave == "mellem":
        return raekkefoelger_mellem()
    if type_opgave == "svaer":
        return raekkefoelger_svaer()

    raise ValueError(f"Ukendt niveau for raekkefoelger: {niveau}")



def byg_faerdig_pyramide_4_3_2_1(bund):
    lag2 = [
        bund[0] + bund[1],
        bund[1] + bund[2],
        bund[2] + bund[3],
    ]

    lag3 = [
        lag2[0] + lag2[1],
        lag2[1] + lag2[2],
    ]

    top = [lag3[0] + lag3[1]]

    return [top, lag3, lag2, bund]


def byg_faerdig_gangepyramide_4_3_2_1(bund):
    lag2 = [
        bund[0] * bund[1],
        bund[1] * bund[2],
        bund[2] * bund[3],
    ]

    lag3 = [
        lag2[0] * lag2[1],
        lag2[1] * lag2[2],
    ]

    top = [lag3[0] * lag3[1]]

    return [top, lag3, lag2, bund]

def skjul_tal(pyramide, antal_synlige):
    alle_pos = [
        (r, c)
        for r, række in enumerate(pyramide)
        for c, val in enumerate(række)
        if val != ""
    ]

    antal_synlige = min(antal_synlige, len(alle_pos))
    synlige = set(random.sample(alle_pos, antal_synlige))

    ny = []
    for r, række in enumerate(pyramide):
        ny_række = []
        for c, val in enumerate(række):
            if val == "":
                ny_række.append("")
            elif (r, c) in synlige:
                ny_række.append(str(val))
            else:
                ny_række.append("")
        ny.append(ny_række)

    return ny

def talpyramide_let():
    bund = [random.randint(1, 9) for _ in range(4)]
    fuld = byg_faerdig_pyramide_4_3_2_1(bund)
    skjult = skjul_tal(fuld, 5)
    return lav_talpyramide_layout_4_3_2_1(skjult)


def talpyramide_mellem():
    bund = [random.randint(5, 15) for _ in range(4)]
    fuld = byg_faerdig_pyramide_4_3_2_1(bund)
    skjult = skjul_tal(fuld, 5)
    return lav_talpyramide_layout_4_3_2_1(skjult)


def talpyramide_svaer():
    bund = [random.randint(10, 30) for _ in range(4)]
    fuld = byg_faerdig_pyramide_4_3_2_1(bund)
    skjult = skjul_tal(fuld, 4)
    return lav_talpyramide_layout_4_3_2_1(skjult)


def talpyramide(niveau="random"):
    if niveau == "random":
        type_opgave = random.choice(["let", "let", "mellem", "mellem", "svaer"])
    else:
        type_opgave = niveau

    if type_opgave == "let":
        return talpyramide_let()
    if type_opgave == "mellem":
        return talpyramide_mellem()
    if type_opgave == "svaer":
        return talpyramide_svaer()

    raise ValueError("Ukendt niveau")


def gangepyramide_let():
    bund = [random.randint(1, 5) for _ in range(4)]
    fuld = byg_faerdig_gangepyramide_4_3_2_1(bund)
    skjult = skjul_tal(fuld, 5)
    return lav_talpyramide_layout_4_3_2_1(skjult)


def gangepyramide_mellem():
    bund = [random.randint(2, 6) for _ in range(4)]
    fuld = byg_faerdig_gangepyramide_4_3_2_1(bund)
    skjult = skjul_tal(fuld, 5)
    return lav_talpyramide_layout_4_3_2_1(skjult)


def gangepyramide_svaer():
    bund = [random.randint(2, 8) for _ in range(4)]
    fuld = byg_faerdig_gangepyramide_4_3_2_1(bund)
    skjult = skjul_tal(fuld, 4)
    return lav_talpyramide_layout_4_3_2_1(skjult)


def gangepyramide(niveau="random"):
    if niveau == "random":
        type_opgave = random.choice(["let", "let", "mellem", "mellem", "svaer"])
    else:
        type_opgave = niveau

    if type_opgave == "let":
        return gangepyramide_let()
    if type_opgave == "mellem":
        return gangepyramide_mellem()
    if type_opgave == "svaer":
        return gangepyramide_svaer()

    raise ValueError("Ukendt niveau")


def byg_tal_fra_primtal(antal_faktorer, mulige_primtal):
    valgte = [random.choice(mulige_primtal) for _ in range(antal_faktorer)]
    tal = 1
    for faktor in valgte:
        tal *= faktor
    return tal, sorted(valgte)


def find_tal_lavet_af_primtal(mindste, stoerste, mulige_primtal):
    muligheder = []

    for tal in range(mindste, stoerste + 1):
        rest = tal
        faktorer = []

        for primtal in mulige_primtal:
            while rest % primtal == 0:
                faktorer.append(primtal)
                rest //= primtal

        if rest == 1 and len(faktorer) >= 2:
            muligheder.append((tal, faktorer))

    return muligheder


def lav_tallet_i_interval(mindste, stoerste, mulige_primtal):
    muligheder = find_tal_lavet_af_primtal(mindste, stoerste, mulige_primtal)
    tal, faktorer = random.choice(muligheder)
    primtal_tekst = ", ".join(str(tal) for tal in mulige_primtal)
    return f"Lav tallet {tal} med gange. Du må kun bruge disse primtal: {primtal_tekst}."


def lav_tallet_let():
    mulige_primtal = [2, 3, 5, 7]
    return lav_tallet_i_interval(15, 50, mulige_primtal)


def lav_tallet_mellem():
    mulige_primtal = [2, 3, 5, 7, 11]
    return lav_tallet_i_interval(25, 100, mulige_primtal)


def lav_tallet_svaer():
    mulige_primtal = [2, 3, 5, 7, 11, 13]
    return lav_tallet_i_interval(75, 300, mulige_primtal)


def lav_tallet(niveau="random"):
    if niveau == "random":
        type_opgave = random.choice(["let", "let", "mellem", "mellem", "svaer"])
    else:
        type_opgave = niveau

    if type_opgave == "let":
        return lav_tallet_let()
    if type_opgave == "mellem":
        return lav_tallet_mellem()
    if type_opgave == "svaer":
        return lav_tallet_svaer()

    raise ValueError("Ukendt niveau")


def lav_find_primtal_opgave(antal_mulige, antal_primtal, primtal, sammensatte_tal):
    valgte_primtal = random.sample(primtal, antal_primtal)
    valgte_sammensatte = random.sample(sammensatte_tal, antal_mulige - antal_primtal)
    tal = valgte_primtal + valgte_sammensatte
    random.shuffle(tal)
    tal_tekst = ", ".join(str(t) for t in tal)

    if antal_primtal == 1:
        return f"Find primtallet: {tal_tekst}"
    return f"Find de {antal_primtal} primtal: {tal_tekst}"


def find_primtal_let():
    primtal = [2, 3, 5, 7, 11, 13]
    sammensatte_tal = [4, 6, 8, 9, 10, 12, 14, 15, 16, 18]
    return lav_find_primtal_opgave(4, 1, primtal, sammensatte_tal)


def find_primtal_mellem():
    primtal = [2, 3, 5, 7, 11, 13, 17, 19]
    sammensatte_tal = [4, 6, 8, 9, 10, 12, 14, 15, 16, 18, 20, 21, 22, 24, 25, 26, 27]
    return lav_find_primtal_opgave(5, 1, primtal, sammensatte_tal)


def find_primtal_svaer():
    primtal = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31]
    sammensatte_tal = [4, 6, 8, 9, 10, 12, 14, 15, 16, 18, 20, 21, 22, 24, 25, 26, 27, 28, 30, 32, 33, 34, 35, 36]
    antal_primtal = random.choice([1, 2])
    return lav_find_primtal_opgave(6, antal_primtal, primtal, sammensatte_tal)


def find_primtal(niveau="random"):
    if niveau == "random":
        type_opgave = random.choice(["let", "let", "mellem", "mellem", "svaer"])
    else:
        type_opgave = niveau

    if type_opgave == "let":
        return find_primtal_let()
    if type_opgave == "mellem":
        return find_primtal_mellem()
    if type_opgave == "svaer":
        return find_primtal_svaer()

    raise ValueError(f"Ukendt niveau for find_primtal: {niveau}")


def lav_overslags_regnestykke(mindste, stoerste, niveau):
    if niveau == "let":
        operationer = ["plus", "minus", "gange"]
    elif niveau == "mellem":
        operationer = ["plus", "minus", "gange", "division"]
    else:
        operationer = ["plus", "minus", "gange", "division"]

    operation = random.choice(operationer)
    resultat = random.randint(mindste, stoerste)

    if operation == "plus":
        a = random.randint(max(20, resultat // 3), max(21, (resultat * 2) // 3))
        b = resultat - a
        return f"{a} + {b}"

    if operation == "minus":
        b = random.randint(max(20, resultat // 3), max(30, resultat))
        return f"{resultat + b} - {b}"

    if operation == "gange":
        for _ in range(40):
            a = random.randint(12 if niveau == "let" else 17, 95)
            b = random.randint(8 if niveau == "let" else 13, 90)
            if mindste <= a * b <= stoerste:
                return f"{a} x {b}"
        return f"{resultat // 10} x 10"

    divisor = random.randint(3, 12)
    return f"{resultat * divisor} / {divisor}"


def lav_rangering_regnestykker_opgave(antal, niveau):
    if niveau == "let":
        intervaller = [(120, 190), (420, 590), (1300, 1800), (3600, 4900), (9000, 12000)]
    elif niveau == "mellem":
        intervaller = [(300, 480), (900, 1300), (2600, 3900), (7500, 10500), (18000, 26000), (42000, 60000)]
    else:
        intervaller = [(600, 950), (1800, 2800), (5200, 7600), (14000, 21000), (36000, 52000), (85000, 125000), (180000, 260000)]

    valgte_intervaller = sorted(random.sample(intervaller, antal))
    regnestykker = [lav_overslags_regnestykke(mindste, stoerste, niveau) for mindste, stoerste in valgte_intervaller]
    random.shuffle(regnestykker)

    bogstaver = ["A", "B", "C", "D", "E"]
    lille_style = styles["Normal"].clone("RangeringRegnestykker")
    lille_style.fontSize = 8
    lille_style.leading = 9
    overskrift_style = styles["Normal"].clone("RangeringOverskrift")
    overskrift_style.fontSize = 8
    overskrift_style.leading = 9
    overskrift_style.alignment = TA_CENTER
    rækker = [[
        Paragraph("<b>Overslag</b> - uden præcis udregning", overskrift_style),
        "",
        "",
    ]]

    svarfelter = "  ".join(["___"] * antal)
    for indeks, (bogstav, regnestykke) in enumerate(zip(bogstaver, regnestykker)):
        rækker.append([
            Paragraph(f"<b>{bogstav}</b>", lille_style),
            Paragraph(regnestykke, lille_style),
            Paragraph(f"<b>Mindst til størst</b><br/>{svarfelter}" if indeks == 0 else "", lille_style),
        ])

    tabel = Table(
        rækker,
        colWidths=[18, 88, 62],
        rowHeights=[18] + [20] * antal,
    )
    tabel.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 1),
        ("RIGHTPADDING", (0, 0), (-1, -1), 1),
        ("TOPPADDING", (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
        ("SPAN", (0, 0), (2, 0)),
    ]))
    return tabel


def rangering_regnestykker_let():
    return lav_rangering_regnestykker_opgave(3, "let")


def rangering_regnestykker_mellem():
    return lav_rangering_regnestykker_opgave(4, "mellem")


def rangering_regnestykker_svaer():
    return lav_rangering_regnestykker_opgave(5, "svaer")


def rangering_regnestykker(niveau="random"):
    if niveau == "random":
        type_opgave = random.choice(["let", "let", "mellem", "mellem", "svaer"])
    else:
        type_opgave = niveau

    if type_opgave == "let":
        return rangering_regnestykker_let()
    if type_opgave == "mellem":
        return rangering_regnestykker_mellem()
    if type_opgave == "svaer":
        return rangering_regnestykker_svaer()

    raise ValueError(f"Ukendt niveau for rangering_regnestykker: {niveau}")


def lav_rutespil_celle(tekst, bredde=52, hoejde=26, farve=None, font_size=8):
    paragraf = Paragraph(f'<font size="{font_size}">{tekst}</font>', styles["Normal"])
    celle = Table([[paragraf]], colWidths=[bredde], rowHeights=[hoejde])
    style = [
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
    ]
    if farve is not None:
        style.append(("BACKGROUND", (0, 0), (-1, -1), farve))
    celle.setStyle(TableStyle(style))
    return celle


def lav_rutespil_regnestykke(svar, niveau):
    if niveau == "let":
        valg = random.choice(["plus", "minus", "gange", "division"])
        if valg == "gange":
            divisorer = [faktor for faktor in [2, 3, 4] if svar % faktor == 0]
            if divisorer:
                faktor = random.choice(divisorer)
                return f"{faktor} x {svar // faktor}"
        if valg == "division":
            divisor = random.choice([2, 3, 4])
            return f"{svar * divisor} / {divisor}"
        if valg == "plus":
            a = random.randint(1, max(1, svar - 1))
            return f"{a} + {svar - a}"
        b = random.randint(1, min(9, svar - 1))
        return f"{svar + b} - {b}"

    if niveau == "mellem":
        valg = random.choice(["plus", "minus", "gange", "division"])
        if valg == "gange":
            divisorer = [faktor for faktor in [2, 3, 4, 5] if svar % faktor == 0]
            if divisorer:
                faktor = random.choice(divisorer)
                return f"{faktor} x {svar // faktor}"
        if valg == "division":
            divisor = random.choice([2, 3, 4, 5])
            return f"{svar * divisor} / {divisor}"
        if valg == "minus":
            b = random.randint(4, 18)
            return f"{svar + b} - {b}"
        a = random.randint(5, max(5, svar - 5))
        return f"{a} + {svar - a}"

    valg = random.choice(["plus", "minus", "gange", "division"])
    if valg == "gange":
        divisorer = [faktor for faktor in [3, 4, 5, 6] if svar % faktor == 0]
        if divisorer:
            faktor = random.choice(divisorer)
            return f"{faktor} x {svar // faktor}"
    if valg == "division":
        divisor = random.choice([2, 3, 4, 5, 6])
        return f"{svar * divisor} / {divisor}"
    if valg == "minus":
        b = random.randint(10, 35)
        return f"{svar + b} - {b}"
    a = random.randint(10, max(10, svar - 10))
    return f"{a} + {svar - a}"

    return f"{svar}"


def lav_rutespil_opgave(niveau, antal_raekker):
    if niveau == "let":
        mulige_bidrag = list(range(2, 9))
    elif niveau == "mellem":
        mulige_bidrag = list(range(3, 13))
    else:
        mulige_bidrag = list(range(4, 18))

    forsoeg = 0
    while True:
        ruter = [[random.choice(mulige_bidrag) for _ in range(antal_raekker)] for _ in range(3)]
        maaltaal = [sum(rute) for rute in ruter]
        forsoeg += 1
        if len(set(maaltaal)) == 3 or forsoeg > 20:
            break

    def spred_kolonner(celler):
        return [celler[0], "", celler[1], "", celler[2]]

    raekker = [spred_kolonner([lav_rutespil_celle("<b>Start 0</b>", hoejde=16, font_size=8) for _ in range(3)])]

    for raekke_indeks in range(antal_raekker):
        kolonne_indeks = list(range(3))
        random.shuffle(kolonne_indeks)
        data_raekke = []
        for kolonne in kolonne_indeks:
            bidrag = ruter[kolonne][raekke_indeks]
            tekst = lav_rutespil_regnestykke(bidrag, niveau)
            data_raekke.append(lav_rutespil_celle(f"{tekst} = ___"))
        raekker.append(spred_kolonner(data_raekke))

    random.shuffle(maaltaal)
    raekker.append(spred_kolonner([lav_rutespil_celle(f"<b>I alt {tal}</b>", hoejde=18, font_size=8) for tal in maaltaal]))

    spil = Table(
        raekker,
        colWidths=[52, 14, 52, 14, 52],
        rowHeights=[18] + [30] * antal_raekker + [20],
    )
    spil.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 1),
        ("RIGHTPADDING", (0, 0), (-1, -1), 1),
        ("TOPPADDING", (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
    ]))

    opgave_tabel = Table(
        [
            [Paragraph("Vælg én i hver række. Summen skal passe med tallet i bunden.", styles["Normal"])],
            [spil],
        ],
        colWidths=[190],
    )
    opgave_tabel.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    return opgave_tabel


def rutespil_let():
    return lav_rutespil_opgave("let", 4)


def rutespil_mellem():
    return lav_rutespil_opgave("mellem", 5)


def rutespil_svaer():
    return lav_rutespil_opgave("svaer", 5)


def rutespil(niveau="random"):
    if niveau == "random":
        type_opgave = random.choice(["let", "let", "mellem", "mellem", "svaer"])
    else:
        type_opgave = niveau

    if type_opgave == "let":
        return rutespil_let()
    if type_opgave == "mellem":
        return rutespil_mellem()
    if type_opgave == "svaer":
        return rutespil_svaer()

    raise ValueError(f"Ukendt niveau for rutespil: {niveau}")



def lav_talpyramide_celle(tekst="", bredde=42, hoejde=24, kant=False):
    celle = Table([[Paragraph(tekst, styles["Normal"])]], colWidths=[bredde], rowHeights=[hoejde])
    style = [
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
        ("LEFTPADDING", (0, 0), (-1, -1),17),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]
    if kant:
        style.append(("BOX", (0, 0), (-1, -1), 1, colors.black))
    celle.setStyle(TableStyle(style))

    return celle


def lav_talpyramide_layout_fra_data(data):
    tom = lav_talpyramide_celle("", bredde=42, hoejde=24, kant=False)

    rækker = []
    max_bredde = 5

    for række in data:
        padding = (max_bredde - len(række)) // 2
        ny_række = (
            [tom] * padding +
            [lav_talpyramide_celle(val, kant=True) for val in række] +
            [tom] * padding
        )
        rækker.append(ny_række)

    pyramide = Table(
        rækker,
        colWidths=[42]*5,
        rowHeights=[24]*5,
    )

    pyramide.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 1),
        ("RIGHTPADDING", (0, 0), (-1, -1), 1),
        ("TOPPADDING", (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
    ]))

    return pyramide



def lav_talpyramide_layout_4_3_2_1(data):
    top, lag3, lag2, bund = data

    def c(v):
        return lav_talpyramide_celle(str(v), kant=True)

    tom = lav_talpyramide_celle("", kant=False)

    


    rows = [
        # top (1 i midten)
        [tom, tom, tom, c(top[0]), tom, tom, tom],

        # lag 3 (2 centreret)
        [tom, tom, c(lag3[0]), tom, c(lag3[1]), tom, tom],

        # lag 2 (3 centreret)
        [tom, c(lag2[0]), tom, c(lag2[1]), tom, c(lag2[2]), tom],

        # bund (4 nederst)
        [c(bund[0]), tom, c(bund[1]), tom, c(bund[2]), tom, c(bund[3])],
    ]

    t = Table(
        rows,
        colWidths=[30]*7,
        rowHeights=[24, 24, 24, 24],
    )

    t.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 2),
        ("RIGHTPADDING", (0, 0), (-1, -1), 2),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))

    return t




def lav_labyrint_celle(indhold="", er_vaeg=False, bredde=30, hoejde=30):
    if er_vaeg:
        celle = Table([[""]], colWidths=[bredde], rowHeights=[hoejde])
        celle.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.black),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
    else:
        paragraf = Paragraph(f'<font size="8">{indhold}</font>', labyrint_celle_style)
        celle = Table([[paragraf]], colWidths=[bredde], rowHeights=[hoejde])
        celle.setStyle(TableStyle([
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("BOX", (0, 0), (-1, -1), 1, colors.black),
            ("LEFTPADDING", (0, 0), (-1, -1), 1),
            ("RIGHTPADDING", (0, 0), (-1, -1), 1),
            ("TOPPADDING", (0, 0), (-1, -1), 1),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
        ]))
    return celle


def lav_labyrint_regnestykke(niveau):
    if niveau == "let":
        operation = random.choice(["plus", "minus"])
        if operation == "plus":
            tal = random.randint(1, 10)
            return f"+ {tal}"
        else:
            tal = random.randint(1, 8)
            return f"- {tal}"
    
    elif niveau == "mellem":
        operation = random.choice(["plus", "minus", "gange"])
        if operation == "gange":
            tal = random.randint(2, 4)
            return f"x {tal}"
        elif operation == "plus":
            tal = random.randint(5, 20)
            return f"+ {tal}"
        else:
            tal = random.randint(3, 15)
            return f"- {tal}"
    
    else:  # svaer
        operation = random.choice(["plus", "minus", "gange", "division"])
        if operation == "gange":
            tal = random.randint(2, 5)
            return f"x {tal}"
        elif operation == "division":
            tal = random.randint(2, 4)
            return f"/ {tal}"
        elif operation == "plus":
            tal = random.randint(10, 35)
            return f"+ {tal}"
        else:
            tal = random.randint(5, 25)
            return f"- {tal}"


def lav_labyrint_sikker_bane(grid_stoerrelse):
    r, c = 0, 0
    bane = [(r, c)]

    while r < grid_stoerrelse - 1 or c < grid_stoerrelse - 1:
        mulige_traek = []
        if r < grid_stoerrelse - 1:
            mulige_traek.append((r + 1, c))
        if c < grid_stoerrelse - 1:
            mulige_traek.append((r, c + 1))

        r, c = random.choice(mulige_traek)
        bane.append((r, c))

    return set(bane)


def har_for_mange_sorte_i_3x3(grid, raekke, kolonne):
    grid_stoerrelse = len(grid)

    for start_r in range(max(0, raekke - 2), min(raekke, grid_stoerrelse - 3) + 1):
        for start_c in range(max(0, kolonne - 2), min(kolonne, grid_stoerrelse - 3) + 1):
            sorte = 0
            for r in range(start_r, start_r + 3):
                for c in range(start_c, start_c + 3):
                    if grid[r][c] == "vaeg":
                        sorte += 1
            if sorte > 2:
                return True

    return False


def har_for_stor_sort_klump(grid, raekke, kolonne):
    grid_stoerrelse = len(grid)
    besoegt = set()
    stak = [(raekke, kolonne)]

    while stak:
        r, c = stak.pop()
        if (r, c) in besoegt or grid[r][c] != "vaeg":
            continue
        besoegt.add((r, c))

        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < grid_stoerrelse and 0 <= nc < grid_stoerrelse:
                stak.append((nr, nc))

    return len(besoegt) > 2


def kan_placere_labyrint_vaeg(grid, raekke, kolonne):
    grid[raekke][kolonne] = "vaeg"
    ok = not har_for_mange_sorte_i_3x3(grid, raekke, kolonne) and not har_for_stor_sort_klump(grid, raekke, kolonne)
    grid[raekke][kolonne] = ""
    return ok


def lav_labyrint_med_bane(grid_stoerrelse, niveau):
    grid = [["" for _ in range(grid_stoerrelse)] for _ in range(grid_stoerrelse)]
    sikker_bane = lav_labyrint_sikker_bane(grid_stoerrelse)

    if niveau == "let":
        antal_vaegge = 8
    elif niveau == "mellem":
        antal_vaegge = 10
    else:
        antal_vaegge = 12

    mulige_vaegge = [
        (r, c)
        for r in range(grid_stoerrelse)
        for c in range(grid_stoerrelse)
        if (r, c) not in sikker_bane and (r, c) not in {(0, 0), (grid_stoerrelse - 1, grid_stoerrelse - 1)}
    ]
    random.shuffle(mulige_vaegge)

    placerede_vaegge = 0
    for r, c in mulige_vaegge:
        if placerede_vaegge >= antal_vaegge:
            break
        if kan_placere_labyrint_vaeg(grid, r, c):
            grid[r][c] = "vaeg"
            placerede_vaegge += 1

    return grid, sikker_bane


def lav_labyrint_medaljer(start_tal, niveau):
    if niveau == "let":
        bronze = start_tal + 10
        soelv = start_tal + 20
        guld = start_tal + 30
    elif niveau == "mellem":
        bronze = start_tal + 20
        soelv = start_tal + 40
        guld = start_tal + 65
    else:
        bronze = start_tal + 35
        soelv = start_tal + 75
        guld = start_tal + 120

    return bronze, soelv, guld


def lav_labyrint_opgave(niveau):
    # Opret en simpel 7x7 labyrint med vægge og regnestykker
    grid_stoerrelse = 7
    grid, sikker_bane = lav_labyrint_med_bane(grid_stoerrelse, niveau)
    if niveau == "let":
        start_tal = random.randint(5, 20)
    elif niveau == "mellem":
        start_tal = random.randint(10, 40)
    else:
        start_tal = random.randint(20, 80)
    
    # Tilføj regnestykker i nogle af de tomme celler (maks 1 pr celle som ønsket)
    tomme_celler = []
    for r in range(grid_stoerrelse):
        for c in range(grid_stoerrelse):
            if grid[r][c] == "" and not (r == 0 and c == 0) and not (r == grid_stoerrelse - 1 and c == grid_stoerrelse - 1):
                tomme_celler.append((r, c))
    
    # Vælg nogle celler til regnestykker (ca. 35% af tomme celler)
    antal_regnestykker = max(5, int(len(tomme_celler) * 0.35))
    regnestykke_positioner = random.sample(tomme_celler, min(antal_regnestykker, len(tomme_celler)))
    
    for r, c in regnestykke_positioner:
        tekst = lav_labyrint_regnestykke(niveau)
        grid[r][c] = tekst
    
    # Opret tabellen
    tabel_data = []
    for r in range(grid_stoerrelse):
        raekke = []
        for c in range(grid_stoerrelse):
            if grid[r][c] == "vaeg":
                raekke.append(lav_labyrint_celle(er_vaeg=True))
            elif grid[r][c] == "":
                # Markér start og slut
                if r == 0 and c == 0:
                    raekke.append(lav_labyrint_celle(f"START<br/><b>{start_tal}</b>"))
                elif r == 6 and c == 6:
                    raekke.append(lav_labyrint_celle("SLUT"))
                else:
                    raekke.append(lav_labyrint_celle())
            else:
                raekke.append(lav_labyrint_celle(grid[r][c]))
        tabel_data.append(raekke)
    
    labyrint_tabel = Table(tabel_data, colWidths=[30]*grid_stoerrelse, rowHeights=[30]*grid_stoerrelse)
    labyrint_tabel.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    
    bronze, soelv, guld = lav_labyrint_medaljer(start_tal, niveau)
    tekst = (
        f'<font size="8">Start: <b>{start_tal}</b>. Gå kun vandret/lodret. '
        'Ram hver celle maks 1 gang. Få størst tal ved SLUT.</font>'
    )
    resultat_tabel = Table(
        [
            [
                Paragraph("Resultat: __________", styles["Normal"]),
                Paragraph(f"Bronze: {bronze}+", styles["Normal"]),
                Paragraph(f"Sølv: {soelv}+", styles["Normal"]),
                Paragraph(f"Guld: {guld}+", styles["Normal"]),
            ]
        ],
        colWidths=[76, 44, 42, 42],
    )
    resultat_tabel.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 1),
        ("RIGHTPADDING", (0, 0), (-1, -1), 1),
        ("TOPPADDING", (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
    ]))
    opgave_tabel = Table([
        [Paragraph(tekst, styles["Normal"])],
        [labyrint_tabel],
        [resultat_tabel],
    ], colWidths=[210])
    
    opgave_tabel.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    
    return opgave_tabel


def labyrint_spil_let():
    return lav_labyrint_opgave("let")


def labyrint_spil_mellem():
    return lav_labyrint_opgave("mellem")


def labyrint_spil_svaer():
    return lav_labyrint_opgave("svaer")


def labyrint_spil(niveau="random"):
    if niveau == "random":
        type_opgave = random.choice(["let", "let", "mellem", "mellem", "svaer"])
    else:
        type_opgave = niveau

    if type_opgave == "let":
        return labyrint_spil_let()
    if type_opgave == "mellem":
        return labyrint_spil_mellem()
    if type_opgave == "svaer":
        return labyrint_spil_svaer()
    raise ValueError(f"Ukendt niveau for labyrint_spil: {niveau}")


def lav_laes_og_forstaa_layout(tekst, spoergsmaal, svar):
    svarlinje = Table(
        [[
            Paragraph("<b>Regn:</b> __________________", laes_og_forstaa_style),
            Paragraph("<b>Svar:</b> __________________", laes_og_forstaa_style),
        ]],
        colWidths=[104, 104],
        rowHeights=[18],
    )
    svarlinje.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))

    opgave_tabel = Table(
        [
            [Paragraph(tekst, laes_og_forstaa_style)],
            [Paragraph(f"<b>Opgave:</b> {spoergsmaal}", laes_og_forstaa_style)],
            [svarlinje],
        ],
        colWidths=[210],
        rowHeights=[None, None, 20],
    )
    opgave_tabel.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("LINEBELOW", (0, 0), (-1, 0), 0.5, colors.lightgrey),
    ]))
    opgave_tabel.laes_og_forstaa_svar = svar
    return opgave_tabel


def laes_og_forstaa_let():
    opgavetype = random.choice(["plus", "plus_sidste", "minus", "forskel"])

    if opgavetype == "plus":
        foerst = random.randint(8, 24)
        flere = random.randint(3, 12)
        irrelevant = random.randint(2, 5)
        tekst = (
            f"Alma laver armbånd i frikvarteret. Hun har {foerst} perler i en æske "
            f"og får {flere} nye perler af sin ven. Æsken har {irrelevant} små rum, "
            f"men rummene skal ikke bruges i regnestykket."
        )
        spoergsmaal = "Hvor mange perler har Alma nu?"
        svar = foerst + flere
    elif opgavetype == "plus_sidste":
        foerst = random.randint(8, 20)
        flere = random.randint(3, 10)
        ekstra = random.randint(2, 8)
        tekst = (
            f"Alma laver armbånd i frikvarteret. Hun har {foerst} perler i en æske "
            f"og får {flere} nye perler af sin ven. Lige før timen starter, finder hun "
            f"{ekstra} perler mere i sin taske."
        )
        spoergsmaal = "Hvor mange perler har Alma nu?"
        svar = foerst + flere + ekstra
    elif opgavetype == "minus":
        foerst = random.randint(18, 40)
        brugt = random.randint(4, foerst - 6)
        irrelevant = random.randint(20, 60)
        tekst = (
            f"Noah samler klistermærker til sin mappe. Han har {foerst} klistermærker "
            f"og giver {brugt} væk til en klassekammerat. Hans penalhus kostede "
            f"{irrelevant} kr., men prisen hører ikke til spørgsmålet."
        )
        spoergsmaal = "Hvor mange klistermærker har Noah tilbage?"
        svar = foerst - brugt
    else:
        den_ene = random.randint(12, 30)
        forskel = random.randint(3, 12)
        den_anden = den_ene + forskel
        irrelevant = random.randint(1, 6)
        tekst = (
            f"Ida og Omar læser den samme bog i læsetimen. Ida har læst {den_ene} sider, "
            f"og Omar har læst {den_anden} sider. Bogen har {irrelevant} kapitler, "
            f"men du skal sammenligne siderne."
        )
        spoergsmaal = "Hvor mange flere sider har Omar læst end Ida?"
        svar = forskel

    return lav_laes_og_forstaa_layout(tekst, spoergsmaal, svar)


def laes_og_forstaa_mellem():
    opgavetype = random.choice(["gange", "gange_sidste", "division", "to_trin", "to_trin_sidste"])

    if opgavetype == "gange":
        antal_pakker = random.randint(3, 9)
        i_hver = random.randint(4, 12)
        irrelevant = random.randint(15, 45)
        tekst = (
            f"Til en klassefest køber læreren {antal_pakker} poser med {i_hver} boller i hver. "
            f"Der står også {irrelevant} servietter på bordet. Festen begynder klokken "
            f"{irrelevant % 12 + 8}.00, men spørgsmålet handler om bollerne."
        )
        spoergsmaal = "Hvor mange boller er der i alt?"
        svar = antal_pakker * i_hver
    elif opgavetype == "gange_sidste":
        antal_pakker = random.randint(3, 7)
        i_hver = random.randint(4, 10)
        ekstra = random.randint(5, 15)
        tekst = (
            f"Til en klassefest køber læreren {antal_pakker} poser med {i_hver} boller i hver. "
            f"Der står også 24 servietter på bordet. Lige før festen kommer en forælder "
            f"med {ekstra} ekstra boller."
        )
        spoergsmaal = "Hvor mange boller er der i alt?"
        svar = antal_pakker * i_hver + ekstra
    elif opgavetype == "division":
        antal_boern = random.randint(4, 9)
        til_hver = random.randint(3, 10)
        samlet = antal_boern * til_hver
        irrelevant = random.randint(2, 6)
        tekst = (
            f"En gruppe børn spiller kort i matematikværkstedet. {samlet} kort skal deles "
            f"ligeligt mellem {antal_boern} børn. De spiller i {irrelevant} runder bagefter, "
            f"men runderne skal ikke bruges til delingen."
        )
        spoergsmaal = "Hvor mange kort får hvert barn?"
        svar = til_hver
    elif opgavetype == "to_trin":
        start = random.randint(25, 55)
        kommer = random.randint(8, 20)
        gaar = random.randint(4, 12)
        irrelevant = random.randint(1, 5)
        tekst = (
            f"Der er {start} personer i svømmehallen om eftermiddagen. {kommer} personer "
            f"kommer ind, og senere går {gaar} personer hjem. Hallen har {irrelevant} bassiner, "
            f"men du skal finde antallet af personer til sidst."
        )
        spoergsmaal = "Hvor mange personer er der derefter i svømmehallen?"
        svar = start + kommer - gaar
    else:
        start = random.randint(25, 50)
        kommer = random.randint(8, 18)
        gaar = random.randint(4, 10)
        ekstra_gaar = random.randint(2, 8)
        tekst = (
            f"Der er {start} personer i svømmehallen om eftermiddagen. {kommer} personer "
            f"kommer ind, og senere går {gaar} personer hjem. Til sidst går endnu "
            f"{ekstra_gaar} personer hjem fra børnebassinet."
        )
        spoergsmaal = "Hvor mange personer er der derefter i svømmehallen?"
        svar = start + kommer - gaar - ekstra_gaar

    return lav_laes_og_forstaa_layout(tekst, spoergsmaal, svar)


def laes_og_forstaa_svaer():
    opgavetype = random.choice(["penge", "penge_sidste", "procent", "afstand"])

    if opgavetype == "penge":
        antal = random.randint(3, 7)
        pris = random.choice([12, 15, 18, 20, 24])
        betaler = ((antal * pris + 49) // 50) * 50
        irrelevant = random.randint(8, 16)
        tekst = (
            f"Freja køber skoleartikler efter skoletid. Hun køber {antal} notesbøger til "
            f"{pris} kr. stykket og betaler med {betaler} kr. Butikken lukker klokken "
            f"{irrelevant}.00, men du skal kun bruge priserne."
        )
        spoergsmaal = "Hvor mange kroner får Freja tilbage?"
        svar = betaler - antal * pris
    elif opgavetype == "penge_sidste":
        antal = random.randint(3, 6)
        pris = random.choice([12, 15, 18, 20])
        ekstra_pris = random.choice([8, 10, 12, 15])
        betaler = ((antal * pris + ekstra_pris + 49) // 50) * 50
        tekst = (
            f"Freja køber skoleartikler efter skoletid. Hun køber {antal} notesbøger til "
            f"{pris} kr. stykket og betaler med {betaler} kr. Ved kassen lægger hun også "
            f"et viskelæder til {ekstra_pris} kr. i kurven."
        )
        spoergsmaal = "Hvor mange kroner får Freja tilbage?"
        svar = betaler - antal * pris - ekstra_pris
    elif opgavetype == "procent":
        samlet = random.choice([40, 60, 80, 100, 120])
        procent = random.choice([10, 20, 25, 50, 75])
        irrelevant = random.randint(2, 8)
        tekst = (
            f"På en skole deltager {samlet} elever i en undersøgelse om transport. "
            f"{procent}% vælger cyklen som deres vigtigste transportmiddel. Skolen har "
            f"{irrelevant} cykelskure, men spørgsmålet handler om eleverne."
        )
        spoergsmaal = "Hvor mange elever vælger cyklen?"
        svar = samlet * procent // 100
    else:
        km_pr_dag = random.randint(12, 28)
        antal_dage = random.randint(3, 6)
        ekstra = random.randint(4, 15)
        irrelevant = random.randint(7, 18)
        tekst = (
            f"En familie er på cykelferie. De cykler {km_pr_dag} km om dagen i {antal_dage} dage. "
            f"Den sidste dag cykler de yderligere {ekstra} km, fordi de tager en omvej. "
            f"De har {irrelevant} liter vand med, men vandet skal ikke regnes med."
        )
        spoergsmaal = "Hvor langt cykler familien i alt?"
        svar = km_pr_dag * antal_dage + ekstra

    return lav_laes_og_forstaa_layout(tekst, spoergsmaal, svar)


def laes_og_forstaa(niveau="random"):
    if niveau == "random":
        type_opgave = random.choice(["let", "let", "mellem", "mellem", "svaer"])
    else:
        type_opgave = niveau

    if type_opgave == "let":
        return laes_og_forstaa_let()
    if type_opgave == "mellem":
        return laes_og_forstaa_mellem()
    if type_opgave == "svaer":
        return laes_og_forstaa_svaer()
    raise ValueError(f"Ukendt niveau for laes_og_forstaa: {niveau}")


def lav_kode_opgave_layout(intro, kodelinjer, spoergsmaal, svar):
    kode_html = "<br/>".join(escape(linje).replace(" ", "&nbsp;") for linje in kodelinjer)
    kodefelt = Table(
        [[Paragraph(kode_html, kode_style)]],
        colWidths=[204],
    )
    kodefelt.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f5f0fb")),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#bda8d8")),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))

    opgave_tabel = Table(
        [
            [Paragraph(intro, kode_tekst_style)],
            [kodefelt],
            [Paragraph(f"<b>Opgave:</b> {spoergsmaal}", kode_tekst_style)],
            [Paragraph("<b>Svar:</b> __________________", kode_tekst_style)],
        ],
        colWidths=[210],
        rowHeights=[None, None, None, 16],
    )
    opgave_tabel.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
    ]))
    opgave_tabel.kode_opgave_svar = svar
    return opgave_tabel


def kode_opgaver_let():
    opgavetype = random.choice(["plus", "gange_plus", "minus"])

    if opgavetype == "plus":
        start = random.randint(4, 18)
        laeg_til = random.randint(3, 12)
        svar = start + laeg_til
        kodelinjer = [
            f"tal = {start}",
            f"tal = tal + {laeg_til}",
            "vis tal",
        ]
    elif opgavetype == "gange_plus":
        start = random.randint(2, 8)
        gange_med = random.randint(2, 4)
        laeg_til = random.randint(1, 8)
        svar = start * gange_med + laeg_til
        kodelinjer = [
            f"tal = {start}",
            f"tal = tal * {gange_med}",
            f"tal = tal + {laeg_til}",
            "vis tal",
        ]
    else:
        start = random.randint(15, 35)
        traek_fra = random.randint(4, 12)
        svar = start - traek_fra
        kodelinjer = [
            f"point = {start}",
            f"point = point - {traek_fra}",
            "vis point",
        ]

    intro = "Gå linjerne igennem en ad gangen."
    spoergsmaal = "Hvilket tal vises til sidst?"
    return lav_kode_opgave_layout(intro, kodelinjer, spoergsmaal, svar)


def kode_opgaver_mellem():
    opgavetype = random.choice(["gentag_plus", "hvis_ellers", "gentag_gange"])

    if opgavetype == "gentag_plus":
        start = random.randint(2, 15)
        antal = random.randint(3, 6)
        laeg_til = random.randint(2, 8)
        svar = start + antal * laeg_til
        kodelinjer = [
            f"tal = {start}",
            f"gentag {antal} gange:",
            f"  tal = tal + {laeg_til}",
            "vis tal",
        ]
    elif opgavetype == "hvis_ellers":
        point = random.randint(8, 28)
        graense = random.randint(12, 22)
        bonus = random.randint(3, 10)
        straf = random.randint(2, 8)
        if point >= graense:
            svar = point + bonus
        else:
            svar = point - straf
        kodelinjer = [
            f"point = {point}",
            f"hvis point >= {graense}:",
            f"  point = point + {bonus}",
            "ellers:",
            f"  point = point - {straf}",
            "vis point",
        ]
    else:
        start = random.randint(2, 6)
        antal = random.randint(2, 4)
        faktor = random.choice([2, 3])
        svar = start * (faktor ** antal)
        kodelinjer = [
            f"tal = {start}",
            f"gentag {antal} gange:",
            f"  tal = tal * {faktor}",
            "vis tal",
        ]

    intro = "Læs indrykningen: linjer under gentag eller hvis hører med dér."
    spoergsmaal = "Hvilken værdi bliver vist?"
    return lav_kode_opgave_layout(intro, kodelinjer, spoergsmaal, svar)


def kode_opgaver_svaer():
    opgavetype = random.choice(["to_linjer_i_loop", "liste", "loop_og_hvis"])

    if opgavetype == "to_linjer_i_loop":
        start = random.randint(2, 7)
        antal = random.randint(2, 4)
        faktor = random.choice([2, 3])
        minus = random.randint(1, 5)
        tal = start
        for _ in range(antal):
            tal = tal * faktor
            tal = tal - minus
        svar = tal
        kodelinjer = [
            f"tal = {start}",
            f"gentag {antal} gange:",
            f"  tal = tal * {faktor}",
            f"  tal = tal - {minus}",
            "vis tal",
        ]
    elif opgavetype == "liste":
        tal = random.randint(3, 12)
        bonusser = [random.randint(1, 7) for _ in range(3)]
        faktor = random.choice([2, 3])
        svar = (tal + sum(bonusser)) * faktor
        bonus_tekst = ", ".join(str(bonus) for bonus in bonusser)
        kodelinjer = [
            f"tal = {tal}",
            f"for hver bonus i [{bonus_tekst}]:",
            "  tal = tal + bonus",
            f"tal = tal * {faktor}",
            "vis tal",
        ]
    else:
        tal = random.randint(5, 15)
        antal = random.randint(2, 5)
        laeg_til = random.randint(3, 8)
        graense = random.randint(25, 38)
        tal_efter_loop = tal + antal * laeg_til
        if tal_efter_loop > graense:
            svar = tal_efter_loop - 10
        else:
            svar = tal_efter_loop + 10
        kodelinjer = [
            f"tal = {tal}",
            f"gentag {antal} gange:",
            f"  tal = tal + {laeg_til}",
            f"hvis tal > {graense}:",
            "  tal = tal - 10",
            "ellers:",
            "  tal = tal + 10",
            "vis tal",
        ]

    intro = "Hold styr på værdien efter hver linje. Brug gerne mellemregninger."
    spoergsmaal = "Hvad ender tallet med at være?"
    return lav_kode_opgave_layout(intro, kodelinjer, spoergsmaal, svar)


def kode_opgaver(niveau="random"):
    if niveau == "random":
        type_opgave = random.choice(["let", "mellem", "mellem", "svaer"])
    else:
        type_opgave = niveau

    if type_opgave == "let":
        return kode_opgaver_let()
    if type_opgave == "mellem":
        return kode_opgaver_mellem()
    if type_opgave == "svaer":
        return kode_opgaver_svaer()
    raise ValueError(f"Ukendt niveau for kode_opgaver: {niveau}")


ALFABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
HEMMELIGE_ORD_LET = ["KAT", "HUS", "SOL", "BOG", "VEN", "KAGE", "SKOLE"]
HEMMELIGE_ORD_MELLEM = ["SKOLE", "KODER", "REGN", "TIMER", "BLYANT", "KLASSE"]
HEMMELIGE_ORD_SVAER = ["MATEMATIK", "FRIKVARTER", "PROGRAM", "HEMMELIG", "TALMESTER"]
SYMBOL_NOGLE = {
    "A": "△", "B": "□", "D": "◆", "E": "○", "G": "◇", "H": "★", "I": "♣",
    "K": "▲", "L": "●", "M": "■", "N": "☆", "O": "◆", "P": "⬟", "R": "⬢",
    "S": "✚", "T": "✦", "V": "✿",
}
EMOJI_NOGLE = {
    "A": "🍎", "D": "🐶", "E": "⭐", "G": "🌵", "H": "🏠", "I": "🍦",
    "K": "🔑", "L": "🌙", "M": "🎵", "N": "☁️", "O": "⚽", "R": "🚀",
    "S": "☀️", "T": "🌳",
}


def caesar_kode(tekst, skub):
    kodet = []
    for bogstav in tekst:
        if bogstav in ALFABET:
            kodet.append(ALFABET[(ALFABET.index(bogstav) + skub) % len(ALFABET)])
        else:
            kodet.append(bogstav)
    return "".join(kodet)


def tal_kode(tekst, separator=" "):
    return separator.join(str(ALFABET.index(bogstav) + 1) if bogstav in ALFABET else "|" for bogstav in tekst)


def omvendt_alfabet_kode(tekst):
    kodet = []
    for bogstav in tekst:
        if bogstav in ALFABET:
            kodet.append(ALFABET[-(ALFABET.index(bogstav) + 1)])
        else:
            kodet.append(bogstav)
    return "".join(kodet)


def hvert_andet_bogstav_kode(tekst):
    fyld = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    kodet = []
    for index, bogstav in enumerate(tekst):
        kodet.append(bogstav)
        kodet.append(fyld[(index * 5 + len(tekst)) % len(fyld)])
    return "".join(kodet)


def lav_symbol_nogle(tekst, noegle):
    brugte = []
    for bogstav in tekst:
        if bogstav in noegle and bogstav not in brugte:
            brugte.append(bogstav)
    return ", ".join(f"{noegle[bogstav]}={bogstav}" for bogstav in brugte)


def symbol_kode(tekst, noegle):
    return " ".join(noegle.get(bogstav, bogstav) for bogstav in tekst)


def lav_hemmelig_kode_layout(kodetype, hemmelig_besked, hint, svar):
    emoji_font_findes = registrer_emoji_font()
    lokal_style = hemmelig_kode_style.clone(f"HemmeligKode{random.randint(1, 100000)}")
    if emoji_font_findes and any(ord(tegn) > 10000 for tegn in hemmelig_besked):
        lokal_style.fontName = EMOJI_FONT_NAVN

    opgave_tabel = Table(
        [
            [Paragraph(f"<b>{escape(kodetype)}</b>", hemmelig_kode_style)],
            [Paragraph(f"<b>Hemmelig besked:</b> {escape(hemmelig_besked)}", lokal_style)],
            [Paragraph(f"<b>Hint:</b> {escape(hint)}", hemmelig_kode_style)],
            [Paragraph("<b>Svar:</b> ______________________________", hemmelig_kode_style)],
        ],
        colWidths=[210],
        rowHeights=[12, None, None, 15],
    )
    opgave_tabel.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
        ("LINEBELOW", (0, 0), (-1, 0), 0.4, colors.HexColor("#c8b6dc")),
    ]))
    opgave_tabel.hemmelig_kode_svar = svar
    return opgave_tabel


def hemmelige_koder_let():
    opgavetype = random.choice(["caesar_1", "tal", "baglaens", "symbol"])
    svar = random.choice(HEMMELIGE_ORD_LET)

    if opgavetype == "caesar_1":
        skub = random.choice([1, 2])
        return lav_hemmelig_kode_layout(
            f"Caesar +{skub}",
            caesar_kode(svar, skub),
            f"Alle bogstaver er flyttet {skub} plads frem i alfabetet.",
            svar,
        )
    if opgavetype == "tal":
        return lav_hemmelig_kode_layout(
            "Tal-kode",
            tal_kode(svar),
            "A=1, B=2, C=3 ...",
            svar,
        )
    if opgavetype == "baglaens":
        return lav_hemmelig_kode_layout(
            "Baglæns kode",
            svar[::-1],
            "Læs ordet bagfra.",
            svar,
        )
    return lav_hemmelig_kode_layout(
        "Symbolkode",
        symbol_kode(svar, SYMBOL_NOGLE),
        f"Nøgle: {lav_symbol_nogle(svar, SYMBOL_NOGLE)}",
        svar,
    )


def hemmelige_koder_mellem():
    opgavetype = random.choice(["caesar_3", "omvendt", "hvert_andet", "emoji", "mester"])
    svar = random.choice(HEMMELIGE_ORD_MELLEM)

    if opgavetype == "caesar_3":
        skub = random.choice([2, 3, 4])
        return lav_hemmelig_kode_layout(
            f"Caesar +{skub}",
            caesar_kode(svar, skub),
            f"Flyt hvert bogstav {skub} pladser tilbage for at læse beskeden.",
            svar,
        )
    if opgavetype == "omvendt":
        return lav_hemmelig_kode_layout(
            "Omvendt alfabet",
            omvendt_alfabet_kode(svar),
            "A byttes med Z, B med Y, C med X osv.",
            svar,
        )
    if opgavetype == "hvert_andet":
        return lav_hemmelig_kode_layout(
            "Hvert andet bogstav",
            hvert_andet_bogstav_kode(svar),
            "Læs bogstav nummer 1, 3, 5, 7 ...",
            svar,
        )
    if opgavetype == "emoji":
        emoji_ord = random.choice(["KODE", "REGN", "MAT"])
        return lav_hemmelig_kode_layout(
            "Emoji-kode",
            symbol_kode(emoji_ord, EMOJI_NOGLE),
            f"Nøgle: {lav_symbol_nogle(emoji_ord, EMOJI_NOGLE)}",
            emoji_ord,
        )
    return lav_hemmelig_kode_layout(
        "Mesterkode",
        tal_kode(svar, separator="-"),
        "Tal svarer til bogstaver. Bindestreger deler tallene.",
        svar,
    )


def hemmelige_koder_svaer():
    opgavetype = random.choice(["caesar_ord", "hvert_andet", "blandet_tal", "omvendt"])
    svar = random.choice(HEMMELIGE_ORD_SVAER)

    if opgavetype == "caesar_ord":
        skub = random.choice([3, 4, 5])
        return lav_hemmelig_kode_layout(
            f"Caesar +{skub}",
            caesar_kode(svar, skub),
            f"Find det rigtige ord ved at flytte hvert bogstav {skub} pladser tilbage.",
            svar,
        )
    if opgavetype == "hvert_andet":
        return lav_hemmelig_kode_layout(
            "Hvert andet bogstav",
            hvert_andet_bogstav_kode(svar),
            "De rigtige bogstaver står på pladserne 1, 3, 5, 7 ...",
            svar,
        )
    if opgavetype == "blandet_tal":
        besked = f"{tal_kode(svar[:len(svar)//2], separator='-')} | {tal_kode(svar[len(svar)//2:], separator='-')}"
        return lav_hemmelig_kode_layout(
            "Mesterkode",
            besked,
            "A=1. Lodret streg deler beskeden i to dele.",
            svar,
        )
    return lav_hemmelig_kode_layout(
        "Omvendt alfabet",
        omvendt_alfabet_kode(svar),
        "Brug A↔Z, B↔Y, C↔X osv.",
        svar,
    )


def hemmelige_koder(niveau="random"):
    if niveau == "random":
        type_opgave = random.choice(["let", "mellem", "mellem", "svaer"])
    else:
        type_opgave = niveau

    if type_opgave == "let":
        return hemmelige_koder_let()
    if type_opgave == "mellem":
        return hemmelige_koder_mellem()
    if type_opgave == "svaer":
        return hemmelige_koder_svaer()
    raise ValueError(f"Ukendt niveau for hemmelige_koder: {niveau}")


GENERATORS = {
    "gange": gange,
    "visuel_gange": visuel_gange,
    "division": division,
    "visuel_division": visuel_division,
    "visuel_division_2": visuel_division_2,
    "plus": plus,
    "visuel_plus": visuel_plus,
    "minus": minus,
    "visuel_minus": visuel_minus,
    "klokke": klokke,
    "procent": procent,
    "broeker": broeker,
    "visuel_procent": visuel_procent,
    "visuel_broek": visuel_broek,
    "visuel_areal": visuel_areal,
    "areal_firkant": areal_firkant,
    "omkreds_firkant": omkreds_firkant,
    "areal_trekant": areal_trekant,
    "areal_cirkel": areal_cirkel,
    "omkreds_cirkel": omkreds_cirkel,
    "pytagoras": pytagoras,
    "cykeltid": cykeltid,
    "talpyramide": talpyramide,
    "gangepyramide": gangepyramide,
    "lav_tallet": lav_tallet,
    "find_primtal": find_primtal,
    "rangering_regnestykker": rangering_regnestykker,
    "rutespil": rutespil,
    "vinkel_trekant": vinkel_trekant,
    "vinkel_firkant": vinkel_firkant,
    "labyrint_spil": labyrint_spil,
    "raekkefoelger": raekkefoelger,
    "kode_opgaver": kode_opgaver,
    "hemmelige_koder": hemmelige_koder,
    "laes_og_forstaa": laes_og_forstaa,
}



def hent_generator(generator_valg):
    if isinstance(generator_valg, tuple):
        navn, niveau = generator_valg

        if navn == "ligning":
            return lambda: ligning(niveau)
        if navn == "gange":
            return lambda: gange(niveau)
        if navn == "visuel_gange":
            def gen():
                return visuel_gange(niveau)

            gen.__name__ = "visuel_gange"
            return gen
        if navn == "division":
            return lambda: division(niveau)
        if navn == "visuel_division":
            def gen():
                return visuel_division(niveau)

            gen.__name__ = "visuel_division"
            return gen
        if navn == "visuel_division_2":
            def gen():
                return visuel_division_2(niveau)

            gen.__name__ = "visuel_division_2"
            return gen
        if navn == "plus":
            return lambda: plus(niveau)
        if navn == "visuel_plus":
            def gen():
                return visuel_plus(niveau)

            gen.__name__ = "visuel_plus"
            return gen
        if navn == "minus":
            return lambda: minus(niveau)
        if navn == "visuel_minus":
            def gen():
                return visuel_minus(niveau)

            gen.__name__ = "visuel_minus"
            return gen
        if navn == "klokke":
            return lambda: klokke(niveau)
        if navn == "procent":
            return lambda: procent(niveau)
        if navn == "broeker":
            return lambda: broeker(niveau)
        if navn == "visuel_procent":
            def gen():
                return visuel_procent(niveau)

            gen.__name__ = "visuel_procent"
            return gen
        if navn == "visuel_broek":
            def gen():
                return visuel_broek(niveau)

            gen.__name__ = "visuel_broek"
            return gen
        if navn == "visuel_areal":
            def gen():
                return visuel_areal(niveau)

            gen.__name__ = "visuel_areal"
            return gen
        if navn == "areal_firkant":
            return lambda: areal_firkant(niveau)
        if navn == "omkreds_firkant":
            return lambda: omkreds_firkant(niveau)
        if navn == "areal_trekant":
            return lambda: areal_trekant(niveau)
        if navn == "areal_cirkel":
            return lambda: areal_cirkel(niveau)
        if navn == "omkreds_cirkel":
            return lambda: omkreds_cirkel(niveau)
        if navn == "pytagoras":
            return lambda: pytagoras(niveau)
        if navn == "cykeltid":
            return lambda: cykeltid(niveau)
        if navn == "talpyramide":
            def gen():
                return talpyramide(niveau)

            gen.__name__ = "talpyramide"
            return gen
        if navn == "gangepyramide":
            def gen():
                return gangepyramide(niveau)

            gen.__name__ = "gangepyramide"
            return gen
        if navn == "lav_tallet":
            return lambda: lav_tallet(niveau)
        if navn == "find_primtal":
            return lambda: find_primtal(niveau)
        if navn == "rangering_regnestykker":
            def gen():
                return rangering_regnestykker(niveau)

            gen.__name__ = "rangering_regnestykker"
            return gen
        if navn == "rutespil":
            def gen():
                return rutespil(niveau)

            gen.__name__ = "rutespil"
            return gen
        if navn == "vinkel_trekant":
            return lambda: vinkel_trekant(niveau)
        if navn == "vinkel_firkant":
            return lambda: vinkel_firkant(niveau)
        if navn == "labyrint_spil":
            def gen():
                return labyrint_spil(niveau)

            gen.__name__ = "labyrint_spil"
            return gen
        if navn == "raekkefoelger":
            def gen():
                return raekkefoelger(niveau)

            gen.__name__ = "raekkefoelger"
            return gen
        if navn == "kode_opgaver":
            def gen():
                return kode_opgaver(niveau)

            gen.__name__ = "kode_opgaver"
            return gen
        if navn == "hemmelige_koder":
            def gen():
                return hemmelige_koder(niveau)

            gen.__name__ = "hemmelige_koder"
            return gen
        if navn == "laes_og_forstaa":
            def gen():
                return laes_og_forstaa(niveau)

            gen.__name__ = "laes_og_forstaa"
            return gen
        raise ValueError(f"Ukendt generator: {navn}")

    if generator_valg == "ligning":
        return ligning

    if generator_valg in GENERATORS:
        return GENERATORS[generator_valg]

    raise ValueError(f"Ukendt generator: {generator_valg}")


# ---------- BILLEDER OG SIDEHOVED ----------

HEADER_HOEJDE = 60
NAVN_TEKST = "Navn: ____________________"
EMOJI_FONT_NAVN = "SegoeUIEmoji"
DYRE_EMOJIS = ["🐵", "🐥", "🐉", "🐶", "🐱", "🦊", "🐼", "🐸", "🦁", "🐨",
"🐯", "🐮", "🐷", "🐭", "🐹", "🐰", "🐻", "🐔", "🐧", "🐦",
"🐤", "🦆", "🦅", "🦉", "🐺", "🐗", "🐴", "🦄", "🐝", "🐛",
"🦋", "🐌", "🐞", "🐜", "🪲", "🐢", "🐍", "🦎", "🦂", "🦀"]


def registrer_emoji_font():
    skrifttype_sti = r"C:\Windows\Fonts\seguiemj.ttf"
    if os.path.exists(skrifttype_sti):
        if EMOJI_FONT_NAVN not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont(EMOJI_FONT_NAVN, skrifttype_sti))
        return True
    return False


def vaelg_sideikon():
    return {"type": "emoji", "vaerdi": random.choice(DYRE_EMOJIS)}


def tegn_sidehoved(canvas, doc, sideikon):
    side_top = doc.pagesize[1]
    header_bund = side_top - doc.topMargin + 10

    canvas.saveState()
    canvas.setFont("Helvetica", 12)
    canvas.drawString(doc.leftMargin, side_top - 32, NAVN_TEKST)

    emoji_font_findes = registrer_emoji_font()
    canvas.setFont(EMOJI_FONT_NAVN if emoji_font_findes else "Helvetica", 26)
    x = doc.pagesize[0] - doc.rightMargin - 28
    y = header_bund + 8
    canvas.drawString(x, y, sideikon["vaerdi"])

    canvas.restoreState()



def lav_tegnefunktion(sideikon):
    def tegn(canvas, doc):
        tegn_sidehoved(canvas, doc, sideikon)

    return tegn


#%% ---------- LAYOUT ----------


def render_opgave(opgave):
    if isinstance(opgave, str):
        return Paragraph(opgave, styles["Normal"])
    return opgave


def byg_boks_opsaetning(boks_valg, boks_skabeloner):
    bokse = []

    for valgt in boks_valg:
        if valgt is None:
            bokse.append(
                {
                    "titel": "",
                    "forklaring": "",
                    "generator": None,
                }
            )
            continue

        niveau = None
        if isinstance(valgt, tuple):
            valgt_navn, niveau = valgt
        else:
            valgt_navn = valgt

        if valgt_navn not in boks_skabeloner:
            raise ValueError(f"Ukendt boksvalg: {valgt_navn}")

        boks = dict(boks_skabeloner[valgt_navn])

        if niveau is not None:
            generator = boks["generator"]
            if isinstance(generator, tuple):
                generator_navn, _ = generator
                boks["generator"] = (generator_navn, niveau)
            elif isinstance(generator, str):
                boks["generator"] = (generator, niveau)

        bokse.append(boks)

    return bokse


def lav_boks(titel, forklaring, opgavefunktion, antal=8, boksbredde=230, bokshoejde=250,MAX_PYRAMIDE_OPGAVER=3):
    if opgavefunktion.__name__ in {"talpyramide", "gangepyramide"}:
        antal = min(antal, MAX_PYRAMIDE_OPGAVER)
    if opgavefunktion.__name__ == "rangering_regnestykker":
        antal = min(antal, 2)
    if opgavefunktion.__name__ == "rutespil":
        antal = min(antal, 1)
    if opgavefunktion.__name__ == "visuel_procent":
        antal = min(antal, 2)
    if opgavefunktion.__name__ == "visuel_broek":
        antal = min(antal, 2)
    if opgavefunktion.__name__ == "visuel_plus":
        antal = min(antal, 2)
    if opgavefunktion.__name__ == "visuel_minus":
        antal = min(antal, 2)
    if opgavefunktion.__name__ == "visuel_gange":
        antal = min(antal, 2)
    if opgavefunktion.__name__ == "visuel_division":
        antal = min(antal, 2)
    if opgavefunktion.__name__ == "visuel_division_2":
        antal = min(antal, 2)
    if opgavefunktion.__name__ == "visuel_areal":
        antal = min(antal, 2)
    if opgavefunktion.__name__ == "kode_opgaver":
        antal = min(antal, 2)
    if opgavefunktion.__name__ == "hemmelige_koder":
        antal = min(antal, 4)
    if opgavefunktion.__name__ == "laes_og_forstaa":
        antal = min(antal, 2)
    overskrift = f"<b>{titel}</b>"
    raekker = [
        [Paragraph(overskrift, styles["Normal"])],
        [Paragraph(forklaring, styles["Normal"])],
    ]

    if opgavefunktion.__name__ == "raekkefoelger":
        opgaver = [opgavefunktion() for _ in range(antal)]
        svar = [getattr(opgave, "raekkefoelge_svar", "?") for opgave in opgaver]
        random.shuffle(svar)
        raekker.extend([[render_opgave(opgave)] for opgave in opgaver])
        raekker.append([lav_raekkefoelge_svarraekke(svar, boksbredde - 16)])

        svarhoejde = 18
        opgavehoejde = (bokshoejde - 52 - svarhoejde) / antal
        raekkehoejder = [18, 20] + [opgavehoejde] * antal + [svarhoejde]
        indre_tabel = Table(raekker, colWidths=[boksbredde], rowHeights=raekkehoejder)
        indre_tabel.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("VALIGN", (0, 0), (-1, 1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ("LINEBELOW", (0, 2), (-1, -3), 0.5, colors.black),
        ]))
        return indre_tabel

    raekker.extend([[render_opgave(opgavefunktion())] for _ in range(antal)])

    opgavehoejde = (bokshoejde - 40) / antal
    raekkehoejder = [18, 22] + [opgavehoejde] * antal
    indre_tabel = Table(raekker, colWidths=[boksbredde], rowHeights=raekkehoejder)
    tabel_style = [
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("VALIGN", (0, 0), (-1, 1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("LINEBELOW", (0, 2), (-1, -2), 0.5, colors.black),
    ]

    if antal == 1:
        tabel_style.append(("VALIGN", (0, 2), (-1, 2), "TOP"))

    indre_tabel.setStyle(TableStyle(tabel_style))
    return indre_tabel



def lav_side(boks_opsaetning, antal_opgaver_i_boks, sidebredde, sidehoejde):
    lodret_luft = 28
    vandret_luft = 12
    kolonnebredde = (sidebredde - vandret_luft) / 2
    raekkehoejde = (sidehoejde - lodret_luft) / 2
    boksbredde = kolonnebredde - 24

    bokse = []
    for boks in boks_opsaetning:
        if boks["generator"] is None:
            bokse.append(lav_boks("", "", lambda: "", antal=antal_opgaver_i_boks, boksbredde=boksbredde, bokshoejde=raekkehoejde))
            continue

        generator = hent_generator(boks["generator"])
        antal_i_boks = min(antal_opgaver_i_boks, boks.get("maks_antal", antal_opgaver_i_boks))

        
        bokse.append(
            lav_boks(
                boks["titel"],
                boks["forklaring"],
                generator,
                antal=antal_i_boks,
                boksbredde=boksbredde,
                bokshoejde=raekkehoejde,
            )
        )

    data = [
        [bokse[0], bokse[1]],
        [bokse[2], bokse[3]],
    ]

    tabel = Table(
        data,
        colWidths=[kolonnebredde, kolonnebredde],
        rowHeights=[raekkehoejde, raekkehoejde],
    )
    tabel.setStyle(TableStyle([
        ("BOX", (0, 0), (-1, -1), 2, colors.black),
        ("INNERGRID", (0, 0), (-1, -1), 1, colors.black),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    return tabel



def byg_pdf(filnavn, antal_sider, boks_opsaetning, antal_opgaver_i_boks, brug_billede=False, billede_sti=""):
    if len(boks_opsaetning) not in {4, 8}:
        raise ValueError("BOKS_OPSAETNING skal indeholde 4 bokse eller 8 bokse til dobbeltsidet print.")

    doc = SimpleDocTemplate(
        filnavn,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=HEADER_HOEJDE + 20,
        bottomMargin=36,
    )
    elements = []
    sideikon = vaelg_sideikon()
    tegn_funktion = lav_tegnefunktion(sideikon)

    for side_nr in range(antal_sider):
        if len(boks_opsaetning) == 8:
            start = 0 if side_nr % 2 == 0 else 4
            side_bokse = boks_opsaetning[start:start + 4]
        else:
            side_bokse = boks_opsaetning

        elements.append(lav_side(side_bokse, antal_opgaver_i_boks, doc.width, doc.height))
        if side_nr < antal_sider - 1:
            elements.append(PageBreak())

    doc.build(elements, onFirstPage=tegn_funktion, onLaterPages=tegn_funktion)

#%% Main

def main():
    os.makedirs(PDF_MAPPE, exist_ok=True)
    filsti = os.path.join(PDF_MAPPE, FILNAVN)
    boks_opsaetning = byg_boks_opsaetning(BOKS_VALG, BOKS_SKABELONER)
    byg_pdf(
        filsti,
        ANTAL_SIDER,
        boks_opsaetning,
        ANTAL_OPGAVER_I_BOKS,
    )


if __name__ == "__main__":
    main()
