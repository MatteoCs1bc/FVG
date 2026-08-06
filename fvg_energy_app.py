"""
FVG Energy Explorer - versione a file singolo, dati incorporati.

GENERATO AUTOMATICAMENTE da src/build_single.py: non modificare a mano,
le modifiche vanno in app.py / src/. Rigenera con `python -m src.build_single`.

Per pubblicarlo: metti questo file in un repository GitHub (da solo, non serve
altro tranne requirements.txt) e su share.streamlit.io indicalo come main file.

Fonti: Terna - Dati Statistici (dati.terna.it) e Piano Energetico Regionale FVG 2024.
"""

from __future__ import annotations

import base64
import gzip
import io
import sys

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# --------------------------------------------------------------------- dati
_DATI: dict[str, str] = {
    "aree_cabine_primarie":
        "H4sIAHp9dGoC/22WzY4TQQyE7zxL07L7x9M+hlV4AbivhuwQjdglaGZz4elxFBDpLueaT267quzk"
        "dHlZT0s4L/v7ZVvCvC3z84+3FL5fL9v6vC3n9fJz+XB4IuIjMVENy8eXdX/f1m/X37fvgmiU8Hl+"
        "3R8xBSynGuvIcQautpgBK4AlabH95zgp2YfDl+PT4VNg6avk4+1bCofTcp73w6/98HaeQ5aYAOIB"
        "Yn585y+UBihRN9sdygNU2OmpjM+Jo2aD8bVFAmwCbJLII5YIvcnUDXkXHV8VEodDr4t6JmJ0eMpY"
        "L7FjtsYycEKYnZbM0K/b9ZHCaUut0J0QvmotRx3LJRTlpklHVUUnGpsTA4W1ElU0jLFaytVa67mq"
        "giPIKEhVlI05YbWGtrIluAKHMTFXe92oTbjBjBAO0CROwwDNEZeM6vqiVp3TAkY1fFG5Owp3zfxw"
        "EHAYtqZj1qy14pYb8mFpczB1FsvpLqmzqOTkI+NRJqc9y1sCDhVO9q7CuN7ii83Ru18wSJlt7XtR"
        "nAXkVuA6kLP3dpTwtDraZTjBpOpsA02jxsZNbj0Grjn1BFNc1K03QT3UOMMNNky8ZU2AYQJqdobN"
        "3qMMW+H8GeA6+G/xdE8rGiver9w/7A+oEe0CzwgAAA==",
    "bilancio_2021":
        "H4sIAHp9dGoC/42Uz46bMBDG7/sU1p5aya0wCQSO2dW2yqlR2hdwYBKN1nioPUZVn74GirogSnsC"
        "i9/8+77BV0NVRbKjCmSnDTmQ2lqSwSLrh1PTkmP5TM01eMYrGhSeDNYo1U59TGSapEq+MrQTegZ2"
        "ESCpkkOxBsxy3bX35GOyYp+uwS8W3B1BOIw9dbqPkWmZr6EXvGFgFJbsDE9WmxgmFTU47DTTOjQW"
        "1wIMMDustEzzOXhBT86DQMvgLMhT7WiiowJ5uUl/IqaODOseztJN9isZHRuOh2ZIrTbpz0ATudsE"
        "n5CaaAHIIv8XF62SZbZJTRa8lV9tz3U0UStxRboFMMLg99DvVrot85maNpqHohoXtiz/q63lZqj5"
        "fj4F+wpO3+8ojx3qn0h2yjEctIGFmn3zJB+Hh3jnq7g0IEXwYylt4q+lGd8/ylTNhftGrGMD454J"
        "7k8xd54c1qiXH2+pZA1ZTDyxWb5a9pmsDw39pklEDeu4KGW2KO+0v5FrRiXkybaB+6G04PmXeBPs"
        "tiK/BO5Da1iJXf73i9AzuBp58HoRuD+orcBjYKqGOVGAaP+kcRA9Koq/64LihtHr0UPorwBgrFDu"
        "y616F7A1NmCHuyTfq/RQZirN8jy+78awDw+/AIVMnrNsBQAA",
    "biomassa_province":
        "H4sIAHp9dGoC/42PMQ7CMAxFd07RA0QoTZukrCyMMJQDhNQCS5FdJVEHTk9QVYmhFd3+8Pz8f/JA"
        "LiKLMfKE5NGJzEQQgstwOHPyL6yc95ASPjCUHKoxQkCYWNw4DkBMIExTd/Io/x1cOOK7vGg7s4O+"
        "D1jUtdGq3UH3ESFlEFad9tDXXhSttl+25+wCVBGeyFTSzzAljZSrzLKl1tqsAnN93bQbgqWwaraA"
        "0tHabtZ/AEr5VoOpAQAA",
    "bosco":
        "H4sIAHp9dGoC/3WQPW/DIBCG9/4KlKmVaHR8HTBm8uYu3i3qUgfJDlVM+vt70A5Woi4nAc9z9x5T"
        "KHHO1xT4luaF6u0rXj/TlOJ4Dvw7L7c1jmv8SHlc1e6q5BIWelFPhz5f2By3kkrm7EKHME1x29J7"
        "WuKB9x17Zf2JI4JQR+BSSKpCSe/RiyPc+Y/uiQvQTutqudZBovEokNydyp5/I72QxYUFZ2xlAagq"
        "441XYOu07t+kf0G9coBV1a0CGpB17k590Gg9KcFVXrX1PEhrdbW6+3iUztBf6Ab7ms6jdcQTPDSG"
        "D28DR6Osrr0IF9JqxAr8AGvdHxGvAQAA",
    "consumi_finali_2021":
        "H4sIAHp9dGoC/42UQW7DIBBF9zkFB0AVxqZJlpHVRXdV1QtMYmqNSsACzPlLWre0ERivkOz3Rw/8"
        "MWhtaJDeGyupW9YA6rbMGj3sOOMN7c31PDuPZ1RInFE4ID2NFi9G+dkCkWSS7gKUPTD64eVUTvUY"
        "UMkN4LMe4iOLQPmxCr9ZcJOxHu8Gv0hvI2Gyso88zy6KDevy75PZYZ8nko4QK/IjOGdc/iSbemzx"
        "FILV2eQsGK/jaQP8/yE8aWlHlMRiLE6AW2iDfi612Lcdq6JJfl+fW1R/xXecPRJtdFWfbUpmu1yC"
        "0ybaTXyp0v3X5SSDtBjAmy3X8C7x0+9mlUq+DWtXyZLp99eJVir+V6Ik5JvCK6FFlx9q4J+Ot8cK"
        "m5y737GfM88a7gwFAAA=",
    "demografia_scenari":
        "H4sIAHp9dGoC/y3MOwrAIBBF0T5rGcJ8HHFWIxYpBKMSSJPVZwyp3uUUr/Q+YI45Wnnq6AfM2vLZ"
        "ej7uKzOSboxMQCsJdwSJwXydBYEooZEtTpbCx2GxWmJ1DkzyszqL+M9iZY3OL4kTO1p+AAAA",
    "geo_indicatori":
        "H4sIAHp9dGoC/5XOwQ6CMAwG4DtPwQPUZSCiHPGgb+B1qdBok7GROnbg6R2YGONJT+3ftF8aURiv"
        "bAkocHenENDE98xyJGs9oBBCROuFAJ3zqRfDPXS+N0K3tY7iYzb6QG5GE0gGTzZxwh0a4XQUV9Mk"
        "pEf4eTHx7B3BSXiyvLmQo5kxPy8Joai0qqHUZQX7A9RKQxboEcww2cBmffs7L3+y69Jxm2LeQlGq"
        "3YtoGoCtVvpf4whVpYoPo0jGE/JEJVxaAQAA",
    "parco_impianti_2023":
        "H4sIAHp9dGoC/42RTWrDMBCF9z2FodtBeCTrxwcIJYtCoIWsVVtJB2wpCDkLn6Z36cUq27gNIQld"
        "aCQxb0bzPSXX+NCFI1k4RutbN44WBk/JwimGdkgpRAI7pHBxPZyPYL0PT9s2Bte5lCI1Abb9iaxP"
        "BM/AVclKMHlxNceSiyv1LiTnR1u4w4Eacj65oguxtfC6B8kFUyAZzyfD9D/Lfc4t5aiZXCPnudWt"
        "BhNPQx/UUfr+KnrXki0y1WDhZf8JaBBZ/beJkpmlzbuL/W1q1DyzLpFX1cp9VfDmRgp+dqmclHWd"
        "gyjxjvyRTyi1msZa3jWVuTPjI7NQinlSJbLRqGu9+r0J3RXfpINfrN35Mpe7cJlTusZpGIVC6Avl"
        "IwqtFBOAKPN3GYMrww+AYRR3mwIAAA==",
    "pv_province":
        "H4sIAHp9dGoC/2VPy2rEMAy8+1uEkeX49QPd6x7aXkOauF2xrB2StIF8feVAaaEGm2FGmhnPS/3i"
        "MvIA/Jh5KBvDvNTp8+Bacv+x33pCIpjrlssx9I8dplxW3ob+h9r74e0fed/7+4P+Wq1zHvmdx6bd"
        "5KrnhfO6ZSDvrEawpAPYTpDpkjZgPApO3uioLnXhQyo6CkHILoruTFsK2EYxaAups9qol4mLeKaE"
        "zcomEt36FhCQtIPQoMGImtS1LtJbykmkOecJo07ni+CDREMyupN5Ua16er1IbLKnGkXF32PAO9+6"
        "kROH2D5j0Cbt1TcyexuAYgEAAA==",
    "pv_traiettoria":
        "H4sIAHp9dGoC/42RsQqDMBRF935FPuAhydPEuBc6FQodnB8xbQOSSGo6+PWNVDtV6XwO3AP3Hsl3"
        "dpoIyPsAL+pDtJC8G+lwiaFLkwvesgwTAXJEUBoLDqf28YuXHISqqm2h4oCo9Y4gAZXiqxBG6ydi"
        "nWODMyYsCVJlfm6HX3xOKIXcFnKC0CXfEXKCQL0IR2LOP0fqe4qWeduzwUYXumVLyeYPMW/Kb9Ou"
        "mLebdfqaMrg54ywLxqSBxuUDrOtCw4M2jJxVYlOobWO+Qda7hgRR6c/KGw3m+bwlAgAA",
    "scenari_fer_elettriche":
        "H4sIAHp9dGoC/4WQQQrCMBBF956iBxhkMknTZCtYcSuC61CjDZQMhNjzG7HZtXT9/rz/mRfH7MHF"
        "yDC7iZOHTwzZHe6c3eSb/nxr/ORzTmEYPRCSAKmEOiJcHuNmSiIoq3EnpRA0UbuXakEbqo09Z555"
        "yi4M/J+j0a6zMkJ0tluHxUoWK7w+E9fSRSusNhu0iEmg3qA/M0mx0FNgH316h+V5Ruo1Uo6ENhV9"
        "AasMBmqVAQAA",
    "scenari_industria_vettori":
        "H4sIAHp9dGoC/42STW7CMBBG95wiBxih8V/jbkGULSonsBIjWY1iZKaRuA134WJMGqQugol3lt8n"
        "z/PMDJ4oJg+u7yMMrhvPv30gB5fG9y6FuDrGLrQBJEoBSq4Rfsif4cC3zbXa/GOFIEwea4T6DTWA"
        "M7rr2C6FJtD9NtU36nMpxRpaiaUU22ixWJGttLSz1PavT1XrUxgcxUlNoCoIsp3VBTn2s1iSM6/e"
        "+9p9T1K1yLBxWLXJQC4uPzAHDSicT2HvLs8RocxArimtyEA9CqkcNCBerN4hxTYShersKfHlifsy"
        "Sdi6NMxSpjg8bo0uDvPyzH/7AP3i63xxAwAA",
    "scenari_settori":
        "H4sIAHp9dGoC/33UTW7CMBAF4H1PwQGsaPxLvIQolbpqRXsBC9Jq1GCjOLDg9AUBqsiMs4zyxfPs"
        "ZyV345iGTuRtF8OASYQYk/gZQtx153MQp9BfXx8jjuGlwRP2nfi8fIHbJBQoKZoU83GPi2+MoUch"
        "VV1XIH7H7vDgm/b1QjVQKoGlhlLpPU8tpfV01RU/XkrFQGY4LDUH6WhQ072v+dHgHAPpaO8U58hk"
        "r5YP9xZ3xzwOGO4nxFSktS5ptiVZ0lxRYIrazp3Dvy7V5YG3XGPeFiyXgVm31Jv0vGWq07JAaXva"
        "z7TX7jFnTBEXzbsS0vpbedcnrr5n7gHK2ky1dXJG24k299s+0SsuR122NIWFoqUZ2MRrNgPYkqUZ"
        "THHd+QxfQ8iHNIwoPtoNe4mUN5Wsb3VPNXM9ja2U4TXZoQNdeVuKQoJbVzm6x9m/O/vrePpi7rr+"
        "AZui5jptBgAA",
    "terna_long":
        "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",
    "trasporti_alimentazione":
        "H4sIAHp9dGoC/3VVy3KbQBC85yv8AWiyDxaWo4zXCikVpCScQ26kQrkoW5Cy5Bx0y7flx7ISeLWz"
        "DBc4TO90M907NK/doe1Pzbkb+jZq+n6Int+a/ld7PjfRn+Z1eGuj9747NZ/M1tT1rsiL+t/fSDDJ"
        "onzoj++HLpISYhG9nNrfIShWDqQVZDTIdjKH7ni0CrqIAbOgu7wSRC8SVjzsqo0pK6wpBh2PbF7d"
        "kyMSkGIGWJKCe5CQe1P+KMo1VsE5A6FGmhvAnwqkPCwjEVKmINM5CZJhPyZRH5jNel9ti3AcHLJ0"
        "JLrVPR0M+KyMdHCRAddzjmAcijvIty2WoIFnE8W1hNiZX0HEQkAicNMlCzZl/nlTBrRW9jThW9mj"
        "VqB1WA755ZwASeAxxO678/Xuvqqf7COIgh3ONGIE8bRw4IpAYB8YaJormEriMlNUZDYVxMkUPR+B"
        "bdEEAuuxbSRJFbrEPdRDYfYmMMp2SrijcwikJ9ZzAJbjWxG08dVwd12+fA+MEiAmlrHkLw0XFneK"
        "DKI7SG+KbrgE6eflFcxA2nXxMYMAhTKbLYBCa4RaIl0St18/Ltoy1khD3DGP3i4ujdsukZoVmdDk"
        "evMuP4wVmU8J6byONWjQimLB95cDS28ocoEykE4MuUEFpMkcECREUix4lY8jvYK+mvrOrB6fwpti"
        "JzftCYRAxmgCEMY1JokCk1K3fP8Dih8TBCsIAAA=",
    "trasporti_modo":
        "H4sIAHp9dGoC/32Sy2rDMBBF9/0Kf4AY9LSkZQjtqqWF9gcEFkE0loofWfjr6za2o1FMVgaf67nH"
        "GrWpScTFmMipc7Hx0+TIxZ1T58kYw+CePofONY5wKig5ptiPbSC8llBL8j34nxuXauOMWbCs4PP3"
        "z23o+5BiIEopEH8TquM7RzNuGaFB2zVyGIdUSAgFjF9LFpopWAUWMVQvLQcjitmonDGQW/lbKsuZ"
        "BqWv8xeY/74ELhHE5Qx0XYzG3QYMXwNfH6/VKbVtsYLZzy4deSI/AdD6PoBMOAWt9oqQjgZp1tCL"
        "77p0CYWMgXrZdsYzFQPM3nFkQoGJnQ7kQYFux3aY+TS/9VX8f7qzx0o11GbZ/240s9PA1aMoEp1v"
        "NrOPLfAu57ug1/wvTrn4XG0DAAA=",
    "geo__aree_cabine_primarie":
        "H4sIAHp9dGoC/7W9TY8uu3Em+F+01lyQQQaD9E5jeHYNNDBLQ2ho5NuCMHLLuLpauA3/98lMPlEV"
        "T76Rp+qUz5xlHBZfJj/iO574j9/8+u//9vNv/uE3/9fPf/j177/8/I9//ctffv7jr3/+6//6zW9/"
        "8z837W+/+Yd//o/f/PlfjlG/+8dS6j+VWooe/89/ehD+7Ze//tvPv/z65/NP/uM3f/zrv/z5jz+/"
        "/NWffv7br3/95aT//H/8y5//9usvf/5//v6/jx88J/jDLz//4X/8v/8qv/mHsX4axwr+/tdf/vw/"
        "fvn5T9f//8P//MNf/vbzf55T/PVff/71l38/fwWL+O9//cu//+la9R//+tdf/uXP/+sPv14L/+d/"
        "ru2nPur4bR8/FW3jt+Wn8vvfbmqbF7VPDVQbtqkSidYvYps1UOeomCBOu3TtH6txhjXbHnvM9EbV"
        "cvz0RT3+JlL3cltfcYax562Dlrv22Fojde6FlTXoy2RTB33EuVz9aS0au47PP6mzzzh27bGzLpp3"
        "bKrFea0aZuhxz/Fr0yLxGLKHxh1TS1agWJdpo6F7VqMvG22PHUxddVM7Uevc1DaJihnoIEbbRI07"
        "PmRvwqBN8IUN/t5imIGGKlZAd7RgghLX1X0CGttlb6PSEloFNV6xg7q/VyVSRff3aiPqXsJx1QKx"
        "Yhdaj19WO6grflrZO97ot4ruDZMVT/K485tqRNU9rZRAbWvtXZAedqFNDG1x6JSJaXukFvxY3Jpm"
        "3fBlgThs70wzjdSJramROPbn9h5XYLJn7cNoXXtspK2212pM1X09Jt26gis+eROx4ce1i2ezF3A8"
        "qHgPymZshajSEp4im3vURZPqHir0SgX8ttFrOv9yc9ZIbXNTW/zc3isYrhJ1/xbdoz723wvR9h8T"
        "B1Yw63iHegez7vTrd3nx+9//53/+9kUGri/JwPVpGdhEf9IfJwRruTbqeEO8fdexShXa6AnqeN1W"
        "ESWZ0NemEp+HsBKpcexafU+7SDQafiy+LS2yZ6jxBmhV3dTIkQ8mVjd1MhW/JuHXtPsMRB11/xqJ"
        "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"
        "FS8QAztZ8u//8/8DGBt44AXNAQA=",
}


def _leggi(nome: str) -> pd.DataFrame:
    """Ricostruisce una tabella dal blocco compresso."""
    if nome not in _DATI:
        return pd.DataFrame()
    grezzo = gzip.decompress(base64.b64decode(_DATI[nome]))
    return pd.read_csv(io.BytesIO(grezzo))

# ------------------------------------------------------------- costanti
REGIONE = "Friuli-Venezia Giulia"
POPOLAZIONE = {  # ISTAT, residenti al 1 gennaio - serve per gli indicatori pro capite
    2015: 1_227_122, 2016: 1_221_218, 2017: 1_217_872, 2018: 1_215_538,
    2019: 1_215_220, 2020: 1_211_357, 2021: 1_206_216, 2022: 1_194_095,
    2023: 1_192_191, 2024: 1_193_000, 2025: 1_194_000,
}

# Palette per fonte / combustibile. Fossili in scala di grigi, rinnovabili a colori.
COLORI = {
    # fonti
    "Termoelettrico": "#4B5563",
    "Idrico": "#2563EB",
    "Fotovoltaico": "#FACC15",
    "Eolico": "#22C55E",
    "Geotermoelettrico": "#DC2626",
    "Bioenergie": "#8B4513",
    "Accumulo Stand Alone": "#A855F7",
    "Accumulo stand alone": "#A855F7",
    # combustibili
    "Gas Naturale": "#9CA3AF",
    "Petroliferi": "#4B5563",
    "Solidi": "#111827",
    "Altri": "#D1D5DB",
    # categorie
    "Cogenerative": "#F97316",
    "Non cogenerative": "#6B7280",
    # impianti idrici
    "Fluente": "#60A5FA",
    "Bacino": "#2563EB",
    "Serbatoio (compresi eventuali pompaggi)": "#1E3A8A",
}
COLORE_DEFAULT = "#9CA3AF"

RINNOVABILI = {"Idrico", "Fotovoltaico", "Eolico", "Geotermoelettrico", "Bioenergie"}
FOSSILI = {"Gas Naturale", "Petroliferi", "Solidi"}

ORDINE_FONTI = [
    "Termoelettrico", "Idrico", "Fotovoltaico", "Eolico",
    "Geotermoelettrico", "Bioenergie", "Accumulo Stand Alone",
]

# Sigle Terna degli impianti cogenerativi
IMPIANTI_COGEN = {
    "CCC": "Ciclo combinato",
    "CIC": "Combustione interna",
    "CPC": "Contropressione",
    "CSC": "Condensazione e spillamento",
    "TGC": "Turbina a gas",
}

# Fattori di conversione
GWH_TO_TJ = 3.6
GWH_TO_KTEP = 0.086


# --------------------------------------------- dati da documenti
# ---------------------------------------------------------------- reti
FONTE_EDIST = "E-Distribuzione, audizione IV Commissione, 21/04/2026 (dati al 31/12/2025)"
FONTE_TERNA_RETE = "Terna, Programmazione Territoriale Efficiente, Trieste 21/04/2026"

RETE_CONSISTENZA = {
    "Clienti in bassa tensione": (630_000, ""),
    "Clienti in media tensione": (2_700, ""),
    "Impianti primari": (45, ""),
    "Cabine secondarie": (10_607, ""),
    "Linee in media tensione": (7_940, "km"),
    "Linee in bassa tensione": (13_400, "km"),
}

RETE_POTENZA = {
    "Potenza installata totale": 2.7,
    "Potenza installata da fonti rinnovabili": 1.6,
}
RETE_FER_DETTAGLIO = {"Solare": 1.25, "Termica": 0.20, "Idraulica": 0.15}  # GW

HOSTING_CAPACITY_MW = 485  # 2025, senza richieste in pipeline

# Saturazione dei trasformatori AT/MT, effetto richieste in pipeline
TRASFORMATORI_STATO = {
    "Verde (sotto soglia)": 35,
    "Arancione (oltre 65%)": 27,
    "Giallo (sotto 65%)": 9,
    "Rosso (oltre 90%)": 4,
}
TRASFORMATORI_PROVINCIA = {"Udine": 44, "Pordenone": 21, "Gorizia": 7, "Trieste": 3}

# Aree "virtualmente" critiche, dicembre 2025
AREE_CRITICHE_COMUNI = {"Rosso": 65, "Arancio": 136, "Giallo": 1, "Bianco": 4}

RETE_SVILUPPO = {
    "Udine": {"ampliamenti": 15, "mva_ampliamenti": 620, "nuovi": 8, "mva_nuovi": 430},
    "Pordenone": {"ampliamenti": 7, "mva_ampliamenti": 240, "nuovi": 5, "mva_nuovi": 340},
    "Gorizia": {"ampliamenti": 1, "mva_ampliamenti": 60, "nuovi": 1, "mva_nuovi": 50},
}
RETE_CONNESSIONI = {"potenza_connessa_mw_2022_2025": 820, "richieste_2022_2025": 61_000}

# Burden sharing regionale: dove siamo rispetto al target 2030 (GW)
BURDEN_SHARING = {
    "Target 2030 (Decreto Aree Idonee)": 1.96,
    "In esercizio o autorizzato dal 2021": 1.60,
    "Richieste AAT/AT autorizzate": 0.31,
    "Richieste MT/BT autorizzate": 0.35,
    "Quota residua per il target": 0.36,
}

# ---------------------------------------------------------------- clima
FONTE_CLIMA = "ARPA FVG, «Segnali dal clima in FVG», edizioni 2024, 2025 e 2026"

MESI = ["gen", "feb", "mar", "apr", "mag", "giu", "lug", "ago", "set", "ott", "nov", "dic"]
# Anomalia termica mensile a Udine rispetto alla serie 1901-(anno-1)
ANOMALIE_MENSILI = {
    2024: [1.2, 3.8, 2.4, 1.3, 0.3, 1.8, 3.3, 4.3, 0.7, 2.2, 0.2, 1.0],
    2025: [3.3, 2.0, 1.9, 2.1, 0.1, 4.2, 0.7, 1.5, 1.3, -0.3, 0.6, 2.6],
}
ANOMALIA_ANNUA = {2023: 1.7, 2024: 1.9, 2025: 1.7}

CLIMA_SINTESI = {
    "anno_ultimo": 2025,
    "posizione_classifica": "terzo anno più caldo dal 1900",
    "superato_da": "2024 e 2022",
    "anomalia_vs_1991_2020": 1.2,
    "anomalia_vs_novecento": 1.8,
    "anomalia_vs_preindustriale": 2.2,  # rispetto al 1850-1900
    "soglia_globale_superata": 1.5,
}

CLIMA_2024 = {
    "giorni_caldi": 67,          # Tmax > 30 °C, media 14 stazioni di pianura
    "giorni_caldi_media": 42,    # media 1991-2020
    "mare_anomalia": 1.9,        # °C vs 1995-2023, Trieste a 2 m
    "piogge_vs_media": 25,       # % in più rispetto al 1991-2020
    "piogge_estive_mm": 251,     # media 29 stazioni pianura e costa
}

PIOGGE_ESTIVE_TREND = -20  # mm per decennio dal 1961, statisticamente significativo

CRIOSFERA = {
    "Alpi Giulie (volume, un secolo)": -96,
    "Ghiacciaio del Canin (volume)": -99,
    "Occidentale del Montasio (volume)": -78,
}

# ---------------------------------------------------------------- idroelettrico
FONTE_IDRO = "PER FVG 2024, situazione impianti al 31/12/2023"

IDRO_PARCO = {
    "Impianti": 268,
    "Potenza efficiente lorda (MW)": 528.7,
    "Producibilità media annua (GWh)": 1830.8,
}

# ---------------------------------------------------------------- province
FONTE_PROVINCE = "Terna, Statistiche Regionali 2024 (dati al 31/12/2024)"

# Produzione lorda totale e rinnovabile per fonte, GWh, 2024
PRODUZIONE_PROVINCE = {
    "Gorizia": {"totale": 500.5, "Idrico": 52.2, "Fotovoltaico": 74.1, "Bioenergie": 191.4},
    "Pordenone": {"totale": 1511.8, "Idrico": 946.5, "Fotovoltaico": 286.9, "Bioenergie": 196.3},
    "Trieste": {"totale": 379.7, "Idrico": 0.0, "Fotovoltaico": 41.0, "Bioenergie": 70.9},
    "Udine": {"totale": 4342.7, "Idrico": 1164.4, "Fotovoltaico": 559.4, "Bioenergie": 223.3},
}

POTENZA_PROVINCE = {  # MW lordi, 2024
    "Gorizia": {"totale": 253.9, "rinnovabile": 147.1},
    "Pordenone": {"totale": 616.4, "rinnovabile": 600.8},
    "Trieste": {"totale": 349.4, "rinnovabile": 68.9},
    "Udine": {"totale": 2262.8, "rinnovabile": 1063.5},
}

# Consumi elettrici 2024, GWh
CONSUMI_ELETTRICI_PROVINCE = {"Gorizia": 691.9, "Pordenone": 2059.3,
                              "Trieste": 1042.9, "Udine": 5510.4}
CONSUMI_ELETTRICI_SETTORE = {"Industria": 5751.7, "Servizi": 2187.1, "Domestico": 1365.8}
CONSUMI_ELETTRICI_TOTALE = 9304.6
CONSUMI_FS_TRAZIONE = 190.9

POTENZA_FONTE_2024 = {  # MW lordi
    "Fotovoltaico": 1210.8, "Idrico": 528.9, "Termoelettrico": 1530.9,
    "Accumuli stand alone": 212.0,
}

# ---------------------------------------------------------------- reti, dettaglio
FONTE_RETI_REPORT = "Audizioni IV Commissione consiliare, 21/04/2026 (Terna, e-distribuzione, AcegasApsAmga, SECAB)"

# Avanzamento verso il target 2030, in MW
BURDEN_SHARING_MW = {
    "In esercizio (2021–2025)": 940,
    "Autorizzato in alta tensione": 310,
    "Autorizzato in media tensione": 350,
    "Quota residua al 2030": 360,
}
BURDEN_SHARING_TARGET_MW = 1960

BESS = {
    "Impianti autorizzati o in istruttoria": 26,
    "Potenza richiesta (MW)": 1405.5,
    "Fabbisogno stimato dal piano (MW)": 300,
    "Impianto già attivo a Pavia di Udine (MW)": 200,
}

INTERCONNESSIONI = {
    "Redipuglia–Divaccia (Slovenia), 380 kV": {"attuale": 700, "prevista": 1200},
    "Merchant line Tarvisio–Arnoldstein (Austria), 132 kV": {"attuale": 160, "prevista": 160},
}

DISTRIBUTORI = {
    "e-distribuzione": {"clienti": 630_000, "energia_gwh": None,
                        "nota": "quasi tutto il territorio non urbano"},
    "AcegasApsAmga – Trieste": {"clienti": 142_000, "energia_gwh": 615,
                                "nota": "picco 130–140 MW; il porto chiede 160 MW, di cui 80 per il cold ironing"},
    "AcegasApsAmga – Gorizia": {"clienti": 22_500, "energia_gwh": 120,
                                "nota": "oltre 40 MW di richieste fotovoltaiche, più della punta cittadina"},
    "SECAB (Alto Bût)": {"clienti": 5_500, "energia_gwh": 45,
                         "nota": "5 centrali idroelettriche, surplus strutturale immesso in rete"},
}

SATURAZIONE_PROVINCE = {"Udine": 50, "Pordenone": 25}  # % di trasformatori in zona rossa
TASSO_REALIZZAZIONE = 50  # % di impianti autorizzati che viene davvero costruito

DECRETO_BOLLETTE = {
    "riferimento": "D.L. 21/2026, art. 7",
    "misure": [
        ("First ready, first connect",
         "La priorità di allacciamento premia i progetti già autorizzati e pronti a partire, "
         "non chi ha presentato domanda per primo. Le istanze speculative decadono."),
        ("Overbooking",
         "Terna e i distributori possono rilasciare preventivi oltre la capacità reale del nodo, "
         "contando statisticamente sul 50% di rinunce."),
        ("Open season",
         "Assegnazione competitiva della capacità di rete a cadenza trimestrale, "
         "prima edizione attesa a novembre 2026."),
    ],
}

# ---------------------------------------------------------------- idrogeno
FONTE_H2 = "Regione FVG, Strategia Regionale per l'Idrogeno"

H2_NAHV = {
    "Finanziamento europeo (mln €)": 25,
    "Organizzazioni partner": 37,
    "Durata (mesi)": 72,
    "Paesi coinvolti": 3,
}

H2_PROGETTI = [
    {"nome": "Hydrogen Hub Trieste", "soggetto": "AcegasApsAmga",
     "finanziamento_mln": 15.8, "elettrolisi_mw": 5.0, "fv_dedicato_mwp": 4.85,
     "produzione_ton_anno": 370, "da_fv_ton_anno": 116, "stoccaggio_ton": 2,
     "stato": "AIA rilasciata a febbraio 2025, avvio previsto entro metà 2026",
     "nota": "Area ex Esso sul Canale Navigabile, acqua dal termovalorizzatore vicino."},
    {"nome": "Stazione di rifornimento di Monfalcone", "soggetto": "APT Gorizia",
     "finanziamento_mln": None, "elettrolisi_mw": None, "fv_dedicato_mwp": None,
     "produzione_ton_anno": None, "da_fv_ton_anno": None, "stoccaggio_ton": None,
     "stato": "PNRR investimento 3.3",
     "nota": "Alimenta 15 autobus a idrogeno sulla linea Monfalcone–Staranzano–Ronchi."},
    {"nome": "Stazione di rifornimento di Porpetto", "soggetto": "PNRR",
     "finanziamento_mln": None, "elettrolisi_mw": None, "fv_dedicato_mwp": None,
     "produzione_ton_anno": None, "da_fv_ton_anno": None, "stoccaggio_ton": None,
     "stato": "PNRR investimento 3.3", "nota": "Attivazione della domanda locale di idrogeno."},
]

H2_MEZZI_TPL = {"Trieste": 10, "Monfalcone": 15}

H2_CRITICITA = [
    ("Rinnovabili insufficienti",
     "La capacità FER regionale potrebbe non bastare per produrre idrogeno rinnovabile "
     "senza sottrarlo ad altri usi: serve coordinare nuova capacità, flessibilità di rete "
     "e priorità d'impiego."),
    ("Competenze nelle PMI",
     "Gestione e manutenzione di impianti complessi richiedono formazione mirata, "
     "che oggi manca soprattutto nelle piccole imprese."),
    ("Localizzazione e accettabilità",
     "Servono aree idonee individuate in anticipo, riuso di siti industriali e "
     "co-localizzazione con infrastrutture esistenti."),
    ("Rete gas disomogenea",
     "In alcune porzioni di territorio l'accesso alla rete gas è irregolare, "
     "il che impone soluzioni logistiche alternative con costi maggiori."),
]

# Consumi elettrici industriali per settore merceologico, GWh (Terna, elaborazione Regione FVG)
CONSUMI_INDUSTRIA_MERCEOLOGICO = {
    2022: {"Siderurgia": 1980.0, "Legno e mobilio": 741.1, "Cartaria": 514.1,
           "Prodotti in metallo": 348.4, "Plastica e gomma": 320.5, "Alimentari": 298.2,
           "Chimica": 258.9, "Ceramiche e vetrarie": 235.7},
    2023: {"Siderurgia": 2018.4, "Legno e mobilio": 650.0, "Cartaria": 277.8,
           "Prodotti in metallo": 337.3, "Plastica e gomma": 305.2, "Alimentari": 293.2,
           "Chimica": 246.0, "Ceramiche e vetrarie": 274.6},
}
INDUSTRIA_TOTALE_GWH = {2022: 5827.9, 2023: 5536.9}

# ---------------------------------------------------------------- contesto regionale
CONTESTO = {
    "popolazione_2021": 1_201_510,
    "popolazione_2045": 1_133_201,
    "aziende_manifatturiere": 8_300,
    "quota_export_top5": 75,  # % del valore dell'export da siderurgia, meccanica, mezzi di trasporto, ...
}


# ------------------------------------------------- funzioni di supporto
def serie(
    df: pd.DataFrame,
    dataset: str,
    *,
    anno: int | None = None,
    tipo_capacita: str | None = None,
    tipo_produzione: str | None = None,
    escludi: set[str] | None = None,
) -> pd.DataFrame:
    """Estrae un dataset filtrato, aggregato per anno e voce."""
    out = df[df["dataset"] == dataset]
    if anno is not None:
        out = out[out["anno"] == anno]
    if tipo_capacita is not None:
        out = out[out["tipo_capacita"] == tipo_capacita]
    if tipo_produzione is not None:
        out = out[out["tipo_produzione"] == tipo_produzione]
    if escludi:
        out = out[~out["voce"].isin(escludi)]
    if out.empty:
        return pd.DataFrame(columns=["anno", "voce", "valore", "unita"])
    return (
        out.groupby(["anno", "voce"], dropna=False, as_index=False)["valore"]
        .sum()
        .assign(unita=out["unita"].iat[0])
    )


def senza_zeri(s: pd.DataFrame, col: str = "valore", voce: str = "voce") -> pd.DataFrame:
    """Toglie le voci che valgono zero su tutto il periodo.

    In FVG serve soprattutto per l'eolico, che è a zero in ogni anno della serie:
    tenerlo produce legende e assi con una categoria sempre invisibile.
    """
    if s.empty:
        return s
    vive = s.groupby(voce)[col].sum()
    return s[s[voce].isin(vive[vive != 0].index)]


def totale(df: pd.DataFrame, dataset: str, anno: int, **kwargs) -> float:
    s = serie(df, dataset, anno=anno, **kwargs)
    return float(s["valore"].sum())


def carica_geojson(nome: str) -> dict | None:
    """Legge un GeoJSON da data/processed/geo/. None se non c'e'."""
    path = PROCESSED / "geo" / f"{nome}.geojson"
    if not path.exists():
        return None
    import json
    return json.loads(path.read_text())


def anni_disponibili(df: pd.DataFrame) -> list[int]:
    return sorted(int(a) for a in df["anno"].dropna().unique())


def mappa_colori(voci) -> dict[str, str]:
    return {str(v): COLORI.get(str(v), COLORE_DEFAULT) for v in voci}


def variazione(serie_annuale: pd.DataFrame, anno: int) -> float | None:
    """Variazione % rispetto all'anno precedente, o None se non calcolabile."""
    tot = serie_annuale.groupby("anno")["valore"].sum()
    if anno not in tot.index or (anno - 1) not in tot.index or tot.get(anno - 1, 0) == 0:
        return None
    return (tot[anno] / tot[anno - 1] - 1) * 100

# ----------------------------------------------------- accesso ai dati
def carica_lungo() -> pd.DataFrame:
    return _leggi("terna_long")


def carica_per(nome: str) -> pd.DataFrame:
    return _leggi(nome)


def carica_geojson(nome: str):
    chiave = f"geo__{nome}"
    if chiave not in _DATI:
        return None
    import json
    return json.loads(gzip.decompress(base64.b64decode(_DATI[chiave])).decode())


# L'app chiama `D.serie(...)` e `DOC.FONTE_EDIST`: nel file singolo vive tutto
# in questo stesso modulo, quindi entrambi i nomi puntano qui.
D = DOC = sys.modules[__name__]


# ------------------------------------------------------------- interfaccia
st.set_page_config(page_title="FVG Energy Explorer", page_icon="⚡", layout="wide")

PLOT = dict(
    template="plotly_white",
    margin=dict(t=30, b=10, l=10, r=10),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
)


@st.cache_data(show_spinner="Carico i dati Terna...")
def get_data() -> pd.DataFrame:
    return D.carica_lungo()


df = get_data()
anni = D.anni_disponibili(df)

# ---------------------------------------------------------------- sidebar
with st.sidebar:
    st.markdown(f"### {REGIONE}")
    anno = st.select_slider("Anno di riferimento", options=anni, value=max(anni))
    st.caption(f"Serie storica {min(anni)}–{max(anni)}")
    st.divider()
    tipo_cap = st.radio("Potenza efficiente", ["Lorda", "Netta"], horizontal=True)
    st.divider()
    st.caption(
        "Dati: **Terna – Dati Statistici** (dati.terna.it), export regionali. "
        "Per aggiornare: scarica i nuovi XLSX in `data/raw/terna/` e lancia "
        "`python -m src.etl_terna`."
    )

# ---------------------------------------------------------------- serie base
prod_fonte = D.serie(df, "produzione_per_fonte_gwh")
prod_fer = D.serie(df, "produzione_per_fonte_rinnovabile_gwh")
prod_comb = D.serie(df, "produzione_lorda_per_combustibile_gwh")
prod_cat = D.serie(df, "produzione_termoelettrica_per_categoria_gwh")
pot_fonte = D.serie(df, "potenza_efficiente_per_fonte_mw")
pot_fer = D.serie(df, "potenza_efficiente_nazionale_per_fonte_rinnovabile_mw", tipo_capacita=tipo_cap)
pot_cat = D.serie(df, "potenza_efficiente_per_categoria_mw")
calore = D.serie(df, "produzione_di_calore_per_impianto_cogenerativo_gwh")
emissioni = D.serie(df, "emissione_per_combustibile_mln_di_tonnellate")
idrico = D.serie(df, "produzione_per_impianto_idrico_gwh")

# L'eolico in FVG è a zero in tutta la serie: fuori dai grafici, ma detto a parole
# nella panoramica, perché la sua assenza è essa stessa un dato.
prod_fonte, prod_fer, pot_fonte, pot_fer = (
    D.senza_zeri(x) for x in (prod_fonte, prod_fer, pot_fonte, pot_fer)
)
prod_comb, prod_cat, idrico = (D.senza_zeri(x) for x in (prod_comb, prod_cat, idrico))


def anno_di(s: pd.DataFrame, a: int = None) -> pd.DataFrame:
    return s[s["anno"] == (a or anno)]


# ---------------------------------------------------------------- intestazione
st.title("⚡ FVG Energy Explorer")
st.markdown(
    f"<p style='margin-top:-12px;color:#6B7280'>Il sistema elettrico del "
    f"{REGIONE} — produzione, capacità, emissioni. Anno selezionato: "
    f"<b>{anno}</b>.</p>",
    unsafe_allow_html=True,
)

p_tot = anno_di(prod_fonte)["valore"].sum()
p_fer = anno_di(prod_fer)["valore"].sum()
pot_tot = anno_di(pot_fonte)["valore"].sum()
em_tot = anno_di(emissioni)["valore"].sum()
cal_tot = anno_di(calore)["valore"].sum()
pop = POPOLAZIONE.get(anno)

quota_fer = p_fer / p_tot * 100 if p_tot else 0
intensita = em_tot * 1e6 / p_tot if p_tot else 0  # tCO2 / GWh = gCO2/kWh

k = st.columns(5)
k[0].metric("Produzione lorda", f"{p_tot:,.0f} GWh".replace(",", "."),
            f"{D.variazione(prod_fonte, anno) or 0:+.1f}%" if D.variazione(prod_fonte, anno) else None)
k[1].metric("Quota rinnovabile", f"{quota_fer:.1f}%")
k[2].metric("Potenza efficiente", f"{pot_tot:,.0f} MW".replace(",", "."))
k[3].metric("Emissioni CO₂ (elettrico)", f"{em_tot:.2f} Mt")
k[4].metric("Intensità carbonica", f"{intensita:.0f} g/kWh")

if pop:
    st.caption(
        f"Pro capite ({pop:,.0f} abitanti): ".replace(",", ".")
        + f"**{p_tot * 1000 / pop:,.0f} kWh** prodotti · ".replace(",", ".")
        + f"**{em_tot * 1e6 / pop:.2f} t CO₂** dal settore elettrico · "
        + f"**{p_tot * GWH_TO_KTEP:,.0f} ktep** di produzione totale".replace(",", ".")
    )

st.divider()

tabs = st.tabs([
    "📊 Panoramica",
    "🔄 Bilancio",
    "🏭 Consumi finali",
    "⚡ Elettricità",
    "🔌 Reti",
    "☀️ Fotovoltaico",
    "🌱 Rinnovabili",
    "💧 Idroelettrico",
    "🔥 Gas",
    "🔥 Termo & CO₂",
    "🧪 Idrogeno",
    "🔮 Scenari",
    "🌡️ Clima",
    "📈 Transizione",
    "🗂 Dati",
])

# ================================================================ 1. PANORAMICA
with tabs[0]:
    st.markdown(
        """
Il Friuli-Venezia Giulia è una regione piccola e industriale. Poco meno di
**1,2 milioni di abitanti** su un territorio che va dalla laguna alle Alpi Giulie,
e una struttura produttiva che pesa molto più della sua taglia demografica:
oltre **8.300 imprese manifatturiere**, con siderurgia, meccanica, mezzi di
trasporto, legno-arredo e cartario a fare circa tre quarti dell'export.

Questo si vede nei consumi. L'industria assorbe da sola circa **il 62% dell'elettricità**
regionale, e la sola siderurgia vale più di 2 TWh l'anno — più di tutto il settore
domestico del Friuli-Venezia Giulia messo insieme. È un profilo energetico da regione
manifatturiera, non da regione di servizi.

Sul lato dell'offerta il quadro è particolare. L'**idroelettrico** alpino è la
dorsale storica, il **fotovoltaico** è cresciuto in fretta fino a superarlo per
potenza installata, le **bioenergie** hanno un peso non banale. E poi c'è
un'assenza: **l'eolico in FVG è sostanzialmente zero**. Non pochi impianti —
zero produzione in tutta la serie storica. È il motivo per cui non lo trovi nei
grafici di questa app: non c'è una barra da disegnare. Per una regione che deve
aggiungere quasi 2 GW di rinnovabili entro il 2030, significa che il peso ricade
quasi interamente su solare e su quel poco di margine che resta all'idroelettrico.

Infine il dato che tiene insieme tutto: il FVG **importa circa il 91%** della
sua energia primaria, e consuma più elettricità di quanta ne produca.
        """
    )
    st.divider()

    c1, c2 = st.columns([1, 1.4])

    with c1:
        st.subheader(f"Mix di produzione {anno}")
        m = anno_di(prod_fonte)
        m = m[m["valore"] > 0]
        if not m.empty:
            fig = px.pie(m, values="valore", names="voce", hole=0.55,
                         color="voce", color_discrete_map=D.mappa_colori(m["voce"]))
            fig.update_traces(textinfo="percent+label", textposition="outside")
            fig.update_layout(showlegend=False, height=380, **PLOT)
            st.plotly_chart(fig, width="stretch")

    with c2:
        st.subheader("Produzione lorda per fonte")
        fig = px.area(prod_fonte.sort_values("anno"), x="anno", y="valore", color="voce",
                      color_discrete_map=D.mappa_colori(prod_fonte["voce"]))
        fig.update_layout(height=380, yaxis_title="GWh", xaxis_title=None, **PLOT)
        fig.add_vline(x=anno, line_dash="dot", line_color="#111827")
        st.plotly_chart(fig, width="stretch")

    st.subheader("Quota rinnovabile sulla produzione lorda")
    tot_y = prod_fonte.groupby("anno")["valore"].sum()
    fer_y = prod_fer.groupby("anno")["valore"].sum()
    quota = (fer_y / tot_y * 100).dropna().reset_index(name="quota")
    fig = px.line(quota, x="anno", y="quota", markers=True,
                  color_discrete_sequence=["#22C55E"])
    fig.update_layout(height=300, yaxis_title="% FER", xaxis_title=None,
                      yaxis_range=[0, 100], **PLOT)
    fig.add_hline(y=quota["quota"].mean(), line_dash="dot", line_color="#9CA3AF",
                  annotation_text=f"media {quota['quota'].mean():.0f}%")
    st.plotly_chart(fig, width="stretch")

# ================================================================ 2. ELETTRICITÀ
with tabs[3]:
    c1, c2 = st.columns(2)

    with c1:
        st.subheader(f"Produzione per fonte, {anno}")
        m = anno_di(prod_fonte).sort_values("valore", ascending=True)
        fig = px.bar(m, x="valore", y="voce", orientation="h", color="voce",
                     color_discrete_map=D.mappa_colori(m["voce"]), text_auto=".0f")
        fig.update_layout(showlegend=False, height=340, xaxis_title="GWh",
                          yaxis_title=None, **PLOT)
        st.plotly_chart(fig, width="stretch")

    with c2:
        st.subheader(f"Potenza efficiente {tipo_cap.lower()}, {anno}")
        m = anno_di(pot_fonte).sort_values("valore", ascending=True)
        fig = px.bar(m, x="valore", y="voce", orientation="h", color="voce",
                     color_discrete_map=D.mappa_colori(m["voce"]), text_auto=".0f")
        fig.update_layout(showlegend=False, height=340, xaxis_title="MW",
                          yaxis_title=None, **PLOT)
        st.plotly_chart(fig, width="stretch")

    st.subheader("Potenza installata nel tempo")
    fig = px.area(pot_fonte.sort_values("anno"), x="anno", y="valore", color="voce",
                  color_discrete_map=D.mappa_colori(pot_fonte["voce"]))
    fig.update_layout(height=340, yaxis_title="MW", xaxis_title=None, **PLOT)
    st.plotly_chart(fig, width="stretch")

    st.subheader("Ore equivalenti di utilizzo")
    st.caption("Produzione annua / potenza efficiente. Indica quanto intensamente lavora ogni parco.")
    merge = prod_fonte.merge(pot_fonte, on=["anno", "voce"], suffixes=("_gwh", "_mw"))
    merge = merge[merge["valore_mw"] > 1]
    merge["ore"] = merge["valore_gwh"] * 1000 / merge["valore_mw"]
    fig = px.line(merge.sort_values("anno"), x="anno", y="ore", color="voce", markers=True,
                  color_discrete_map=D.mappa_colori(merge["voce"]))
    fig.update_layout(height=340, yaxis_title="ore/anno", xaxis_title=None, **PLOT)
    st.plotly_chart(fig, width="stretch")

# ================================================================ 3. RINNOVABILI
with tabs[6]:
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Produzione rinnovabile per fonte")
        fig = px.area(prod_fer.sort_values("anno"), x="anno", y="valore", color="voce",
                      color_discrete_map=D.mappa_colori(prod_fer["voce"]))
        fig.update_layout(height=360, yaxis_title="GWh", xaxis_title=None, **PLOT)
        st.plotly_chart(fig, width="stretch")

    with c2:
        st.subheader(f"Potenza rinnovabile ({tipo_cap.lower()})")
        fig = px.area(pot_fer.sort_values("anno"), x="anno", y="valore", color="voce",
                      color_discrete_map=D.mappa_colori(pot_fer["voce"]))
        fig.update_layout(height=360, yaxis_title="MW", xaxis_title=None, **PLOT)
        st.plotly_chart(fig, width="stretch")

    st.subheader("Idroelettrico per tipologia di impianto")
    st.caption("Il fluente segue la piovosità, bacini e serbatoi modulano.")
    fig = px.bar(idrico.sort_values("anno"), x="anno", y="valore", color="voce",
                 color_discrete_map=D.mappa_colori(idrico["voce"]))
    fig.update_layout(height=340, yaxis_title="GWh", xaxis_title=None, barmode="stack", **PLOT)
    st.plotly_chart(fig, width="stretch")

# ================================================================ 4. TERMO & CO2
with tabs[9]:
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Produzione termoelettrica per combustibile")
        fig = px.area(prod_comb.sort_values("anno"), x="anno", y="valore", color="voce",
                      color_discrete_map=D.mappa_colori(prod_comb["voce"]))
        fig.update_layout(height=340, yaxis_title="GWh", xaxis_title=None, **PLOT)
        st.plotly_chart(fig, width="stretch")

    with c2:
        st.subheader("Emissioni di CO₂ per combustibile")
        fig = px.area(emissioni.sort_values("anno"), x="anno", y="valore", color="voce",
                      color_discrete_map=D.mappa_colori(emissioni["voce"]))
        fig.update_layout(height=340, yaxis_title="Mt CO₂", xaxis_title=None, **PLOT)
        st.plotly_chart(fig, width="stretch")

    st.subheader("Intensità carbonica della generazione")
    st.caption("Emissioni totali del parco termoelettrico divise per la produzione elettrica lorda regionale.")
    tot_em = emissioni.groupby("anno")["valore"].sum()
    inten = (tot_em * 1e6 / tot_y).dropna().reset_index(name="g_kwh")
    fig = px.line(inten, x="anno", y="g_kwh", markers=True, color_discrete_sequence=["#DC2626"])
    fig.update_layout(height=300, yaxis_title="g CO₂/kWh", xaxis_title=None, **PLOT)
    st.plotly_chart(fig, width="stretch")

    c3, c4 = st.columns(2)
    with c3:
        st.subheader("Cogenerative vs non cogenerative")
        fig = px.bar(prod_cat.sort_values("anno"), x="anno", y="valore", color="voce",
                     color_discrete_map=D.mappa_colori(prod_cat["voce"]))
        fig.update_layout(height=340, yaxis_title="GWh elettrici", xaxis_title=None, **PLOT)
        st.plotly_chart(fig, width="stretch")

    with c4:
        st.subheader("Calore utile da cogenerazione")
        cal = calore.copy()
        cal["voce"] = cal["voce"].map(IMPIANTI_COGEN).fillna(cal["voce"])
        fig = px.bar(cal.sort_values("anno"), x="anno", y="valore", color="voce")
        fig.update_layout(height=340, yaxis_title="GWh termici", xaxis_title=None, **PLOT)
        st.plotly_chart(fig, width="stretch")

# ================================================================ 5. SANKEY
with tabs[1]:
    bil = D.carica_per("bilancio_2021")
    consumi_f = D.carica_per("consumi_finali_2021")

    if not bil.empty:
        v = bil.set_index("voce")["valore"]
        cil = v.get("Consumo interno lordo", 0)
        trasf_in = v.get("Input alla trasformazione", 0)
        trasf_out = v.get("Output della trasformazione", 0)
        perdite_t = v.get("Perdite di trasformazione", 0)
        autocons = v.get("Autoconsumi e perdite di rete", 0)
        cfe = consumi_f["valore"].sum()
        cfne = v.get("Consumi finali non energetici", 0)
        rendimento = v.get("Rendimento", 0)

        st.subheader("Bilancio energetico regionale 2021")
        st.caption(
            "Tutto il sistema energetico, non solo l'elettrico. Valori in ktep, "
            "dal Piano Energetico Regionale."
        )
        b = st.columns(5)
        b[0].metric("Consumo interno lordo", f"{cil:,.0f} ktep".replace(",", "."))
        b[1].metric("Import netto", f"{v.get('Import totale', 0) - v.get('Export totale', 0):,.0f} ktep".replace(",", "."))
        b[2].metric("Risorse interne", f"{v.get('Risorse interne totale', 0):,.0f} ktep".replace(",", "."))
        b[3].metric("Consumi finali", f"{cfe:,.0f} ktep".replace(",", "."))
        b[4].metric("Perdite di trasformazione", f"{perdite_t:,.0f} ktep".replace(",", "."))

        dip = (v.get("Import totale", 0) - v.get("Export totale", 0)) / cil * 100 if cil else 0
        st.caption(
            f"Dipendenza dall'estero e dalle altre regioni: **{dip:.0f}%** del consumo interno lordo. "
            f"Rendimento del sistema di trasformazione: **{rendimento * 100:.0f}%**."
        )

        # ---- Sankey del bilancio
        fonti = bil[bil["blocco"].isin(["Import", "Risorse interne"])]
        fonti = fonti[fonti["valore"] > 0]

        nodi_b = (
            [f"{r.voce} (import)" if r.blocco == "Import" else r.voce
             for r in fonti.itertuples()]
            + ["Consumo interno lordo", "Trasformazione", "Uso diretto",
               "Perdite di trasformazione", "Vettori derivati",
               "Autoconsumi e perdite di rete", "Consumi finali energetici",
               "Usi non energetici"]
        )
        ib = {n: i for i, n in enumerate(nodi_b)}
        colori_b = [
            "#EF4444" if r.blocco == "Import" else "#22C55E" for r in fonti.itertuples()
        ] + ["#111827", "#4B5563", "#9CA3AF", "#EF4444", "#FACC15", "#F97316", "#2563EB", "#A855F7"]

        sb, tb, vb, cb = [], [], [], []

        def lb(a, b_, val, colore):
            if val and val > 0:
                sb.append(ib[a]); tb.append(ib[b_]); vb.append(float(val)); cb.append(colore)

        for r in fonti.itertuples():
            nome = f"{r.voce} (import)" if r.blocco == "Import" else r.voce
            lb(nome, "Consumo interno lordo", r.valore,
               "rgba(239,68,68,0.28)" if r.blocco == "Import" else "rgba(34,197,94,0.35)")

        uso_diretto = max(0.0, cil - trasf_in)
        lb("Consumo interno lordo", "Trasformazione", trasf_in, "rgba(75,85,99,0.3)")
        lb("Consumo interno lordo", "Uso diretto", uso_diretto, "rgba(156,163,175,0.3)")
        lb("Trasformazione", "Perdite di trasformazione", perdite_t, "rgba(239,68,68,0.3)")
        lb("Trasformazione", "Vettori derivati", trasf_out, "rgba(250,204,21,0.45)")
        lb("Vettori derivati", "Autoconsumi e perdite di rete", autocons, "rgba(249,115,22,0.4)")
        lb("Vettori derivati", "Consumi finali energetici", max(0.0, trasf_out - autocons),
           "rgba(250,204,21,0.45)")
        lb("Uso diretto", "Consumi finali energetici", max(0.0, uso_diretto - cfne),
           "rgba(37,99,235,0.3)")
        lb("Uso diretto", "Usi non energetici", cfne, "rgba(168,85,247,0.4)")

        fig = go.Figure(go.Sankey(
            node=dict(pad=15, thickness=18, label=nodi_b, color=colori_b,
                      line=dict(color="rgba(0,0,0,0.15)", width=0.5)),
            link=dict(source=sb, target=tb, value=vb, color=cb,
                      hovertemplate="%{value:.0f} ktep<extra></extra>"),
        ))
        fig.update_layout(height=600, font_size=12, margin=dict(t=20, b=20, l=10, r=10))
        st.plotly_chart(fig, width="stretch")

        st.caption(
            "In rosso ciò che entra da fuori regione, in verde le risorse interne. "
            "Il bilancio chiude con uno scarto di pochi ktep dovuto ai bunkeraggi "
            "dell'aviazione internazionale."
        )
        st.divider()

    st.subheader(f"Dal combustibile agli usi finali — {anno}")
    rend = st.slider(
        "Rendimento complessivo stimato del parco termoelettrico (elettrico + termico)",
        0.30, 0.85, 0.52, 0.01,
        help="Terna pubblica la produzione, non l'energia entrante. Questo parametro "
             "stima l'input di combustibile e quindi le perdite di conversione.",
    )

    comb_y = anno_di(prod_comb).set_index("voce")["valore"].to_dict()
    cat_y = anno_di(prod_cat).set_index("voce")["valore"].to_dict()
    fonte_y = anno_di(prod_fonte).set_index("voce")["valore"].to_dict()

    el_termo = sum(comb_y.values())
    cal_y = anno_di(calore)["valore"].sum()
    input_comb = (el_termo + cal_y) / rend if rend else 0
    perdite = max(0.0, input_comb - el_termo - cal_y)

    combustibili = [c for c, v in comb_y.items() if v > 0]
    fer_dirette = [f for f in ("Idrico", "Fotovoltaico", "Eolico") if fonte_y.get(f, 0) > 0]
    categorie = [c for c, v in cat_y.items() if v > 0]

    nodi = combustibili + ["Parco termoelettrico"] + categorie + fer_dirette + [
        "Energia elettrica", "Calore utile", "Perdite di conversione"
    ]
    idx = {n: i for i, n in enumerate(nodi)}
    colori_nodi = [COLORI.get(n, "#9CA3AF") for n in nodi]
    for n, c in {"Parco termoelettrico": "#4B5563", "Energia elettrica": "#FACC15",
                 "Calore utile": "#F97316", "Perdite di conversione": "#EF4444"}.items():
        colori_nodi[idx[n]] = c

    src, tgt, val, col = [], [], [], []

    def link(a: str, b: str, v: float, colore: str) -> None:
        if v and v > 0:
            src.append(idx[a]); tgt.append(idx[b]); val.append(float(v)); col.append(colore)

    # combustibile -> parco termoelettrico (scalato all'input stimato)
    scala = input_comb / el_termo if el_termo else 0
    for c in combustibili:
        link(c, "Parco termoelettrico", comb_y[c] * scala, "rgba(75,85,99,0.35)")

    # parco -> categorie di impianto (pro quota sulla produzione elettrica)
    tot_cat = sum(cat_y.get(c, 0) for c in categorie)
    for c in categorie:
        quota_c = cat_y[c] / tot_cat if tot_cat else 0
        link("Parco termoelettrico", c, (el_termo + cal_y) * quota_c, "rgba(75,85,99,0.35)")
    link("Parco termoelettrico", "Perdite di conversione", perdite, "rgba(239,68,68,0.3)")

    # categorie -> elettricità / calore
    for c in categorie:
        quota_c = cat_y[c] / tot_cat if tot_cat else 0
        link(c, "Energia elettrica", cat_y[c], "rgba(250,204,21,0.45)")
        if "Cogenerative" in c and "Non" not in c:
            link(c, "Calore utile", cal_y, "rgba(249,115,22,0.45)")

    # rinnovabili non termiche -> elettricità
    for f in fer_dirette:
        link(f, "Energia elettrica", fonte_y[f], "rgba(37,99,235,0.35)")

    fig = go.Figure(go.Sankey(
        node=dict(pad=18, thickness=20, label=nodi, color=colori_nodi,
                  line=dict(color="rgba(0,0,0,0.15)", width=0.5)),
        link=dict(source=src, target=tgt, value=val, color=col,
                  hovertemplate="%{value:.0f} GWh<extra></extra>"),
    ))
    fig.update_layout(height=520, font_size=13, margin=dict(t=20, b=20, l=10, r=10))
    st.plotly_chart(fig, width="stretch")

    st.info(
        f"Input di combustibile stimato: **{input_comb:,.0f} GWh** · "
        f"elettricità termoelettrica **{el_termo:,.0f} GWh** · "
        f"calore utile **{cal_y:,.0f} GWh** · "
        f"perdite **{perdite:,.0f} GWh**. "
        "L'input non è misurato da Terna: dipende dal rendimento impostato sopra."
        .replace(",", ".")
    )

# ================================================================ 6. TREND
with tabs[13]:
    st.subheader("Sostituzione tra fonti (grafico di Marchetti)")
    st.caption("Asse y: log₁₀(f / (1−f)), con f = quota della fonte. Una retta = sostituzione a ritmo costante.")

    m = prod_fonte.merge(tot_y.rename("tot"), on="anno")
    m = m[(m["tot"] > 0) & (m["valore"] > 0)]
    m["f"] = np.clip(m["valore"] / m["tot"], 1e-4, 1 - 1e-4)
    m["marchetti"] = np.log10(m["f"] / (1 - m["f"]))
    fig = px.line(m.sort_values("anno"), x="anno", y="marchetti", color="voce", markers=True,
                  color_discrete_map=D.mappa_colori(m["voce"]))
    fig.update_layout(height=400, yaxis_title="log(f / 1−f)", xaxis_title=None, **PLOT)
    st.plotly_chart(fig, width="stretch")

    st.subheader("Traiettoria del mix elettrico (diagramma ternario)")
    st.caption("Ogni punto è un anno. Le tre componenti sommano a 100% della produzione lorda.")

    piv = prod_fonte.pivot_table(index="anno", columns="voce", values="valore", aggfunc="sum").fillna(0)
    fer_piv = prod_fer.pivot_table(index="anno", columns="voce", values="valore", aggfunc="sum").fillna(0)
    bio = fer_piv.get("Bioenergie", pd.Series(0, index=piv.index)).reindex(piv.index).fillna(0)

    t = pd.DataFrame(index=piv.index)
    t["Rinnovabili variabili"] = piv.get("Fotovoltaico", 0) + piv.get("Eolico", 0)
    t["Idroelettrico"] = piv.get("Idrico", 0)
    t["Termoelettrico"] = piv.get("Termoelettrico", 0)
    tot_t = t.sum(axis=1)
    t = (t.div(tot_t, axis=0) * 100).dropna().reset_index()

    fig = px.scatter_ternary(t, a="Termoelettrico", b="Rinnovabili variabili", c="Idroelettrico",
                             hover_name="anno", color="anno", color_continuous_scale="Viridis")
    fig.update_traces(mode="lines+markers", line=dict(color="#22C55E", width=1.5), marker=dict(size=9))
    fig.update_layout(height=520, margin=dict(t=40, b=20))
    st.plotly_chart(fig, width="stretch")

# ================================================================ 7. DATI
with tabs[14]:
    st.subheader("Dati sottostanti")
    st.caption(
        "Tutto quello che vedi nell'app viene da questa tabella unica, prodotta da "
        "`src/etl_terna.py` a partire dagli export XLSX di Terna."
    )
    ds = st.multiselect("Dataset", sorted(df["dataset"].unique()),
                        default=sorted(df["dataset"].unique())[:2])
    vista = df[df["dataset"].isin(ds)] if ds else df
    st.dataframe(vista, width="stretch", height=420)
    st.download_button("Scarica CSV", vista.to_csv(index=False).encode("utf-8"),
                       file_name=f"fvg_energia_{anno}.csv", mime="text/csv")

    with st.expander("Copertura e limiti dei dati"):
        st.markdown(
            "- I dati Terna coprono **solo il settore elettrico**: produzione, potenza, "
            "combustibili e CO₂ della generazione.\n"
            "- Non ci sono ancora: **richiesta elettrica regionale**, **consumi finali per settore** "
            "(industria, civile, trasporti), **vettori non elettrici** (gas, prodotti petroliferi), "
            "**saldo import/export** con le altre regioni e con la Slovenia/Austria.\n"
            "- Le emissioni sono quelle della sola generazione termoelettrica, non l'inventario "
            "regionale completo (ISPRA stima ~11,3 Mt CO₂eq per il FVG al 2019).\n"
            "- Il dataset `potenza_efficiente_per_sottocategoria_mw` non ha la dimensione anno: "
            "è un aggregato sull'intero periodo, quindi non è usato nei grafici temporali."
        )

st.divider()
st.caption("Fonte: Terna – Dati Statistici (dati.terna.it) · Elaborazione: FVG Energy Explorer")

# ================================================================ CONSUMI FINALI
with tabs[2]:
    consumi_f = D.carica_per("consumi_finali_2021")
    if consumi_f.empty:
        st.info("Lancia `python -m src.etl_per` per generare i dati del Piano Energetico Regionale.")
    else:
        tot_cf = consumi_f["valore"].sum()
        st.subheader("Consumi finali energetici 2021, per settore e vettore")
        st.caption(f"{tot_cf:,.0f} ktep complessivi. Fonte: Piano Energetico Regionale.".replace(",", "."))

        per_settore = consumi_f.groupby("settore")["valore"].sum().sort_values(ascending=False)
        per_vettore = consumi_f.groupby("vettore")["valore"].sum().sort_values(ascending=False)

        c1, c2 = st.columns(2)
        with c1:
            fig = px.pie(per_settore.reset_index(), values="valore", names="settore", hole=0.55,
                         color_discrete_sequence=["#2563EB", "#F97316", "#22C55E", "#A855F7"])
            fig.update_traces(textinfo="percent+label", textposition="outside")
            fig.update_layout(showlegend=False, height=380, title="Per settore", **PLOT)
            st.plotly_chart(fig, width="stretch")
        with c2:
            fig = px.pie(per_vettore.reset_index(), values="valore", names="vettore", hole=0.55,
                         color="vettore", color_discrete_map={
                             "Combustibili gassosi": "#9CA3AF", "Energia elettrica": "#FACC15",
                             "Petrolio": "#4B5563", "Energie rinnovabili": "#22C55E",
                             "Calore derivato": "#F97316", "Combustibili solidi": "#111827",
                             "Rifiuti non rinnovabili": "#D1D5DB"})
            fig.update_traces(textinfo="percent+label", textposition="outside")
            fig.update_layout(showlegend=False, height=380, title="Per vettore", **PLOT)
            st.plotly_chart(fig, width="stretch")

        st.subheader("Chi consuma cosa")
        nodi_c = list(per_vettore.index) + list(per_settore.index)
        ic = {n: i for i, n in enumerate(nodi_c)}
        colori_c = ["#9CA3AF"] * len(per_vettore) + ["#2563EB"] * len(per_settore)
        for n, col in {"Energia elettrica": "#FACC15", "Energie rinnovabili": "#22C55E",
                       "Petrolio": "#4B5563", "Combustibili solidi": "#111827",
                       "Calore derivato": "#F97316"}.items():
            if n in ic:
                colori_c[ic[n]] = col

        att = consumi_f[consumi_f["valore"] > 0]
        fig = go.Figure(go.Sankey(
            node=dict(pad=18, thickness=20, label=nodi_c, color=colori_c,
                      line=dict(color="rgba(0,0,0,0.15)", width=0.5)),
            link=dict(source=[ic[r.vettore] for r in att.itertuples()],
                      target=[ic[r.settore] for r in att.itertuples()],
                      value=list(att["valore"]),
                      color=["rgba(37,99,235,0.25)"] * len(att),
                      hovertemplate="%{value:.0f} ktep<extra></extra>"),
        ))
        fig.update_layout(height=460, font_size=13, margin=dict(t=20, b=20, l=10, r=10))
        st.plotly_chart(fig, width="stretch")

        st.subheader("Composizione di ogni settore")
        fig = px.bar(consumi_f[consumi_f["valore"] > 0], x="settore", y="valore", color="vettore",
                     color_discrete_map={
                         "Combustibili gassosi": "#9CA3AF", "Energia elettrica": "#FACC15",
                         "Petrolio": "#4B5563", "Energie rinnovabili": "#22C55E",
                         "Calore derivato": "#F97316", "Combustibili solidi": "#111827"})
        fig.update_layout(height=400, yaxis_title="ktep", xaxis_title=None, **PLOT)
        st.plotly_chart(fig, width="stretch")

        el_share = per_vettore.get("Energia elettrica", 0) / tot_cf * 100
        st.info(
            f"L'elettricità copre il **{el_share:.0f}%** dei consumi finali. "
            "Industria e civile pesano quasi uguale (~40% ciascuno), ma con vettori diversi: "
            "l'industria va a elettricità e gas, il civile quasi solo a gas. "
            "I trasporti restano il settore meno elettrificato: petrolio all'86%."
        )

# ================================================================ SCENARI
with tabs[11]:
    sc = D.carica_per("scenari_settori")
    fer_sc = D.carica_per("scenari_fer_elettriche")
    ind_v = D.carica_per("scenari_industria_vettori")
    demo = D.carica_per("demografia_scenari")

    if sc.empty:
        st.info("Lancia `python -m src.etl_per` per generare gli scenari del PER.")
    else:
        st.subheader("Traiettorie di consumo al 2045")
        st.caption(
            "REF = scenario di riferimento (politiche vigenti); A = allineato al PNIEC; "
            "B = allineato a RePowerEU. I trasporti hanno un solo percorso nel PER."
        )

        cons = sc[sc["grandezza"] == "Consumi finali"]
        settore_sel = st.selectbox("Settore", sorted(cons["settore"].unique()))
        s = cons[cons["settore"] == settore_sel].sort_values("anno")
        fig = px.line(s, x="anno", y="valore", color="scenario", markers=True,
                      color_discrete_map={"Storico": "#111827", "REF": "#6B7280",
                                          "A": "#2563EB", "B": "#22C55E", "PER": "#F97316"})
        fig.update_layout(height=380, yaxis_title="ktep", xaxis_title=None, **PLOT)
        st.plotly_chart(fig, width="stretch")

        emis = sc[sc["grandezza"] == "Emissioni CO2"]
        if not emis.empty:
            st.subheader("Emissioni di CO₂ per settore")
            fig = px.line(emis.sort_values("anno"), x="anno", y="valore",
                          color="scenario", line_dash="settore", markers=True,
                          color_discrete_map={"Storico": "#111827", "REF": "#6B7280",
                                              "A": "#2563EB", "B": "#22C55E", "PER": "#F97316"})
            fig.update_layout(height=380, yaxis_title="kt CO₂", xaxis_title=None, **PLOT)
            st.plotly_chart(fig, width="stretch")

        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Rinnovabili elettriche")
            f = fer_sc[fer_sc["fonte"] != "Totale FER elettriche"].sort_values("anno")
            tot_f = fer_sc[fer_sc["fonte"] == "Totale FER elettriche"].sort_values("anno")
            fig = px.bar(f, x="anno", y="valore", color="fonte",
                         color_discrete_map={"Fotovoltaico": "#FACC15", "Idroelettrico": "#2563EB",
                                             "Bioenergie": "#8B4513"})
            fig.add_scatter(x=tot_f["anno"], y=tot_f["valore"], mode="lines+markers",
                            name="Totale", line=dict(color="#111827", dash="dot"))
            fig.update_layout(height=380, yaxis_title="GWh", xaxis_title=None, **PLOT)
            st.plotly_chart(fig, width="stretch")

        with c2:
            st.subheader("Industria: sostituzione dei vettori")
            fig = px.area(ind_v.sort_values("anno"), x="anno", y="valore", color="vettore",
                          color_discrete_map={"Gas": "#9CA3AF", "Elettricità": "#FACC15",
                                              "FER": "#22C55E", "Calore derivato": "#F97316",
                                              "Prodotti petroliferi": "#4B5563",
                                              "Solidi": "#111827"})
            fig.update_layout(height=380, yaxis_title="ktep", xaxis_title=None, **PLOT)
            st.plotly_chart(fig, width="stretch")

        if not demo.empty:
            st.subheader("Il contesto: popolazione in calo, PIL in crescita")
            fig = go.Figure()
            fig.add_bar(x=demo["anno"], y=demo["popolazione"], name="Popolazione",
                        marker_color="#9CA3AF", yaxis="y")
            fig.add_scatter(x=demo["anno"], y=demo["pil_mln_eur_2015"], name="PIL (mln € 2015)",
                            mode="lines+markers", line=dict(color="#2563EB", width=3), yaxis="y2")
            fig.update_layout(
                height=340, template="plotly_white",
                yaxis=dict(title="abitanti", range=[1_050_000, 1_250_000]),
                yaxis2=dict(title="mln € 2015", overlaying="y", side="right"),
                margin=dict(t=30, b=10, l=10, r=10),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
            )
            st.plotly_chart(fig, width="stretch")
            st.caption(
                "Il PER assume −68.000 abitanti e +24% di PIL reale tra il 2021 e il 2045: "
                "il disaccoppiamento tra economia ed energia deve reggere su una base demografica "
                "che si assottiglia."
            )

# ================================================================ RETI
with tabs[4]:
    st.subheader("La rete di distribuzione")
    st.caption(f"Fonte: {DOC.FONTE_EDIST}.")

    r = st.columns(4)
    r[0].metric("Potenza installata", f"{DOC.RETE_POTENZA['Potenza installata totale']:.1f} GW")
    r[1].metric("di cui rinnovabile", f"{DOC.RETE_POTENZA['Potenza installata da fonti rinnovabili']:.1f} GW")
    r[2].metric("Hosting capacity 2025", f"{DOC.HOSTING_CAPACITY_MW} MW", help="Senza le richieste già in pipeline.")
    r[3].metric("Connessi 2022–2025", f"{DOC.RETE_CONNESSIONI['potenza_connessa_mw_2022_2025']} MW",
                f"{DOC.RETE_CONNESSIONI['richieste_2022_2025']:,} richieste".replace(",", "."))

    c1, c2 = st.columns([1, 1])
    with c1:
        st.markdown("**Consistenza dell'infrastruttura**")
        cons = pd.DataFrame(
            [{"Voce": k, "Valore": f"{v:,.0f} {u}".replace(",", ".").strip()}
             for k, (v, u) in DOC.RETE_CONSISTENZA.items()]
        )
        st.dataframe(cons, hide_index=True, width="stretch")

        fer_d = pd.DataFrame(DOC.RETE_FER_DETTAGLIO.items(), columns=["Fonte", "GW"])
        fig = px.bar(fer_d, x="GW", y="Fonte", orientation="h", text_auto=".2f",
                     color="Fonte", color_discrete_map={"Solare": "#FACC15", "Idraulica": "#2563EB",
                                                        "Termica": "#4B5563"})
        fig.update_layout(showlegend=False, height=220, title="Rinnovabili connesse (GW)",
                          yaxis_title=None, **PLOT)
        st.plotly_chart(fig, width="stretch")

    with c2:
        st.markdown("**Saturazione dei trasformatori AT/MT**")
        st.caption("Effetto delle richieste in pipeline, dicembre 2025. 75 trasformatori in tutto.")
        tr = pd.DataFrame(DOC.TRASFORMATORI_STATO.items(), columns=["Stato", "Numero"])
        fig = px.pie(tr, values="Numero", names="Stato", hole=0.5, color="Stato",
                     color_discrete_map={"Verde (sotto soglia)": "#22C55E",
                                         "Giallo (sotto 65%)": "#FACC15",
                                         "Arancione (oltre 65%)": "#F97316",
                                         "Rosso (oltre 90%)": "#EF4444"})
        fig.update_traces(textinfo="value+percent")
        fig.update_layout(height=330, **PLOT)
        st.plotly_chart(fig, width="stretch")

    st.subheader("Dove la rete è già satura")
    st.caption(
        "Un'area è **rossa** quando la potenza in immissione richiesta supera il 90% "
        "della potenza nominale dei trasformatori che la alimentano: lì connettere "
        "nuovi impianti diventa difficile senza potenziare la rete."
    )
    c3, c4 = st.columns(2)
    with c3:
        ac = pd.DataFrame(DOC.AREE_CRITICHE_COMUNI.items(), columns=["Criticità", "Comuni"])
        fig = px.bar(ac, x="Criticità", y="Comuni", color="Criticità", text_auto=True,
                     color_discrete_map={"Rosso": "#EF4444", "Arancio": "#F97316",
                                         "Giallo": "#FACC15", "Bianco": "#D1D5DB"})
        fig.update_layout(showlegend=False, height=320, xaxis_title=None,
                          title="Comuni per livello di criticità", **PLOT)
        st.plotly_chart(fig, width="stretch")
    with c4:
        pr = pd.DataFrame(DOC.TRASFORMATORI_PROVINCIA.items(), columns=["Provincia", "Trasformatori"])
        fig = px.bar(pr, x="Provincia", y="Trasformatori", text_auto=True,
                     color_discrete_sequence=["#6B7280"])
        fig.update_layout(height=320, xaxis_title=None,
                          title="Trasformatori AT/MT per provincia", **PLOT)
        st.plotly_chart(fig, width="stretch")

    st.subheader("Il potenziamento in programma")
    sv = pd.DataFrame([
        {"Provincia": p, "Tipo": "Ampliamenti", "Impianti": d["ampliamenti"], "MVA": d["mva_ampliamenti"]}
        for p, d in DOC.RETE_SVILUPPO.items()
    ] + [
        {"Provincia": p, "Tipo": "Nuovi impianti", "Impianti": d["nuovi"], "MVA": d["mva_nuovi"]}
        for p, d in DOC.RETE_SVILUPPO.items()
    ])
    fig = px.bar(sv, x="Provincia", y="MVA", color="Tipo", text="Impianti", barmode="group",
                 color_discrete_map={"Ampliamenti": "#2563EB", "Nuovi impianti": "#22C55E"})
    fig.update_traces(textposition="outside")
    fig.update_layout(height=340, xaxis_title=None,
                      yaxis_title="MVA di incremento", **PLOT)
    st.plotly_chart(fig, width="stretch")
    st.caption(
        f"In totale {sv['Impianti'].sum()} interventi per {sv['MVA'].sum():,.0f} MVA. "
        "L'etichetta sopra ogni barra è il numero di impianti.".replace(",", ".")
    )

    st.divider()
    st.subheader("Il target regionale al 2030")
    st.caption(f"Fonte: {DOC.FONTE_TERNA_RETE}. Valori in GW di capacità rinnovabile.")
    bs = pd.DataFrame(DOC.BURDEN_SHARING.items(), columns=["Voce", "GW"])
    target = bs.iloc[0]["GW"]
    fig = px.bar(bs.iloc[1:], x="Voce", y="GW", text_auto=".2f",
                 color="Voce", color_discrete_sequence=["#22C55E", "#2563EB", "#60A5FA", "#D1D5DB"])
    fig.add_hline(y=target, line_dash="dash", line_color="#111827",
                  annotation_text=f"Target 2030: {target} GW")
    fig.update_layout(showlegend=False, height=360, xaxis_title=None, **PLOT)
    st.plotly_chart(fig, width="stretch")
    st.info(
        f"Il Decreto Aree Idonee assegna al FVG **+{target} GW** di nuova capacità rinnovabile "
        f"al 2030 rispetto al 2021. Ne risultano in esercizio o autorizzati "
        f"**{DOC.BURDEN_SHARING['In esercizio o autorizzato dal 2021']} GW**: l'82% del percorso. "
        "Il collo di bottiglia non è più autorizzare impianti, è avere rete che li accolga."
    )

# ================================================================ IDROELETTRICO
with tabs[7]:
    st.subheader("Il parco idroelettrico regionale")
    st.caption(f"Fonte: {DOC.FONTE_IDRO}, integrata con la serie storica Terna.")

    i = st.columns(4)
    i[0].metric("Impianti", f"{DOC.IDRO_PARCO['Impianti']}")
    i[1].metric("Potenza efficiente lorda", f"{DOC.IDRO_PARCO['Potenza efficiente lorda (MW)']:.0f} MW")
    i[2].metric("Producibilità media", f"{DOC.IDRO_PARCO['Producibilità media annua (GWh)']:,.0f} GWh".replace(",", "."))
    idro_anno = anno_di(idrico)["valore"].sum()
    i[3].metric(f"Prodotto nel {anno}", f"{idro_anno:,.0f} GWh".replace(",", "."))

    idro_tot = idrico.groupby("anno")["valore"].sum()
    if len(idro_tot) > 1:
        mn, mx = idro_tot.min(), idro_tot.max()
        st.caption(
            f"Tra il {idro_tot.idxmin()} e il {idro_tot.idxmax()} la produzione è oscillata da "
            f"**{mn:,.0f}** a **{mx:,.0f} GWh**: un fattore {mx / mn:.1f}. ".replace(",", ".")
            + "L'idroelettrico è rinnovabile ma non è costante — dipende da quanta acqua arriva."
        )

    c1, c2 = st.columns([1.5, 1])
    with c1:
        st.markdown("**Produzione per tipologia di impianto**")
        fig = px.bar(idrico.sort_values("anno"), x="anno", y="valore", color="voce",
                     color_discrete_map=D.mappa_colori(idrico["voce"]))
        prod_media = DOC.IDRO_PARCO["Producibilità media annua (GWh)"]
        fig.add_hline(y=prod_media, line_dash="dash", line_color="#111827",
                      annotation_text=f"producibilità media {prod_media:.0f} GWh")
        fig.update_layout(height=400, yaxis_title="GWh", xaxis_title=None, **PLOT)
        st.plotly_chart(fig, width="stretch")

    with c2:
        st.markdown("**Composizione nell'anno selezionato**")
        m = anno_di(idrico)
        m = m[m["valore"] > 0]
        if not m.empty:
            fig = px.pie(m, values="valore", names="voce", hole=0.5,
                         color="voce", color_discrete_map=D.mappa_colori(m["voce"]))
            fig.update_traces(textinfo="percent")
            fig.update_layout(height=400, **PLOT)
            st.plotly_chart(fig, width="stretch")

    st.subheader("Quanto lavora il parco idroelettrico")
    st.caption(
        "Ore equivalenti annue: produzione divisa per la potenza installata. "
        "Sono la firma della variabilità idrologica, non dell'efficienza degli impianti."
    )
    pot_idro = pot_fonte[pot_fonte["voce"] == "Idrico"]
    ore_idro = (idro_tot / pot_idro.set_index("anno")["valore"] * 1000).dropna().reset_index(name="ore")
    fig = px.bar(ore_idro, x="anno", y="ore", color_discrete_sequence=["#2563EB"])
    fig.add_hline(y=ore_idro["ore"].mean(), line_dash="dot", line_color="#111827",
                  annotation_text=f"media {ore_idro['ore'].mean():.0f} ore")
    fig.update_layout(height=340, yaxis_title="ore/anno", xaxis_title=None, **PLOT)
    st.plotly_chart(fig, width="stretch")

    st.info(
        "Il PER stima una producibilità media di "
        f"{DOC.IDRO_PARCO['Producibilità media annua (GWh)']:,.0f} GWh e prevede di arrivare a ".replace(",", ".")
        + "2.231 GWh al 2045: un margine di crescita limitato, perché i siti migliori sono già "
        "sfruttati. L'espansione passa da efficientamento degli impianti esistenti e "
        "mini-idro, non da nuovi grandi invasi."
    )

# ================================================================ CLIMA
with tabs[12]:
    st.subheader("Il clima che cambia il sistema energetico")
    st.caption(f"Fonte: {DOC.FONTE_CLIMA}.")

    s = DOC.CLIMA_SINTESI
    k = st.columns(4)
    k[0].metric(f"Anno {s['anno_ultimo']}", s["posizione_classifica"].replace("terzo", "3°").title(),
                help=f"Superato solo dal {s['superato_da']}.")
    k[1].metric("Rispetto al 1991–2020", f"+{s['anomalia_vs_1991_2020']} °C")
    k[2].metric("Rispetto al Novecento", f"+{s['anomalia_vs_novecento']} °C")
    k[3].metric("Rispetto al preindustriale", f"+{s['anomalia_vs_preindustriale']} °C",
                help="Periodo 1850-1900, serie di Udine.")

    st.warning(
        f"In FVG la soglia di **+{s['soglia_globale_superata']} °C** sul preindustriale è già stata "
        f"superata più volte, e nel 2025 l'anomalia ha toccato **+{s['anomalia_vs_preindustriale']} °C**. "
        "A livello globale quella soglia è stata superata per la prima volta nel 2024. "
        "La regione si scalda più in fretta della media perché sta a cavallo di due hot spot: "
        "il Mediterraneo e le Alpi."
    )

    st.subheader("Anomalie termiche mensili a Udine")
    st.caption("Scostamento delle temperature medie mensili rispetto alla serie dal 1901.")
    an = pd.DataFrame([
        {"mese": DOC.MESI[i], "ordine": i, "anno": str(a), "anomalia": v}
        for a, vals in DOC.ANOMALIE_MENSILI.items() for i, v in enumerate(vals)
    ]).sort_values("ordine")
    fig = px.bar(an, x="mese", y="anomalia", color="anno", barmode="group",
                 color_discrete_map={"2024": "#F97316", "2025": "#EF4444"})
    fig.add_hline(y=0, line_color="#111827", line_width=1)
    fig.update_layout(height=360, yaxis_title="°C rispetto alla media", xaxis_title=None, **PLOT)
    st.plotly_chart(fig, width="stretch")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Il 2024 in cifre**")
        d24 = DOC.CLIMA_2024
        st.markdown(
            f"- **{d24['giorni_caldi']} giorni caldi** in pianura (massima oltre 30 °C), "
            f"contro i {d24['giorni_caldi_media']} della media 1991–2020: quasi un mese in più.\n"
            f"- Mare a Trieste **+{d24['mare_anomalia']} °C** rispetto al 1995–2023.\n"
            f"- Piogge annue **+{d24['piogge_vs_media']}%** sopra la norma…\n"
            f"- …ma solo **{d24['piogge_estive_mm']} mm** d'estate."
        )
        st.caption(
            f"Le piogge estive calano di circa {abs(DOC.PIOGGE_ESTIVE_TREND)} mm ogni decennio "
            "dal 1961: il trend è statisticamente significativo. Più acqua in totale, "
            "meno acqua quando serve ai fiumi e all'agricoltura."
        )

    with c2:
        st.markdown("**Perdita di volume dei ghiacciai**")
        cr = pd.DataFrame(DOC.CRIOSFERA.items(), columns=["Corpo glaciale", "Variazione %"])
        fig = px.bar(cr, x="Variazione %", y="Corpo glaciale", orientation="h", text_auto=".0f",
                     color_discrete_sequence=["#60A5FA"])
        fig.update_layout(height=260, yaxis_title=None, xaxis_title="% di volume perso", **PLOT)
        st.plotly_chart(fig, width="stretch")
        st.caption(
            "Perdite misurate su circa un secolo. Il Canin è di fatto scomparso come ghiacciaio; "
            "il Montasio occidentale resiste grazie all'esposizione a nord e agli apporti di valanga."
        )

    st.divider()
    st.subheader("Perché tutto questo riguarda l'energia")
    st.markdown(
        "- **Idroelettrico**: la produzione regionale oscilla di un fattore due tra anni "
        "piovosi e anni secchi. Estati più asciutte spostano la produzione fuori dai mesi "
        "di maggior consumo per il condizionamento.\n"
        "- **Domanda**: più giorni sopra i 30 °C significa più raffrescamento estivo, cioè "
        "un picco di domanda elettrica che si sposta da inverno a estate.\n"
        "- **Termoelettrico**: acqua di raffreddamento più calda e più scarsa riduce il "
        "rendimento degli impianti proprio quando servono di più.\n"
        "- **Reti**: eventi intensi e concentrati mettono sotto stress le linee aeree, "
        "in una regione che ha 13.400 km di bassa tensione da mantenere."
    )

# ================================================================ FOTOVOLTAICO
with tabs[5]:
    pv_prov = D.carica_per("pv_province")
    pv_tra = D.carica_per("pv_traiettoria")

    pv_serie = prod_fer[prod_fer["voce"] == "Fotovoltaico"]
    pv_pot = pot_fonte[pot_fonte["voce"] == "Fotovoltaico"]
    pv_gwh = anno_di(pv_serie)["valore"].sum()
    pv_mw = anno_di(pv_pot)["valore"].sum()

    st.subheader("Il fotovoltaico in Friuli-Venezia Giulia")
    k = st.columns(4)
    k[0].metric(f"Potenza {anno}", f"{pv_mw:,.0f} MW".replace(",", "."))
    k[1].metric(f"Produzione {anno}", f"{pv_gwh:,.0f} GWh".replace(",", "."))
    if pv_mw:
        k[2].metric("Ore equivalenti", f"{pv_gwh * 1000 / pv_mw:,.0f} h".replace(",", "."))
    k[3].metric("Quota sulla produzione regionale", f"{pv_gwh / p_tot * 100:.1f}%" if p_tot else "—")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Crescita della potenza installata**")
        fig = px.bar(pv_pot.sort_values("anno"), x="anno", y="valore",
                     color_discrete_sequence=["#FACC15"])
        fig.update_layout(height=340, yaxis_title="MW", xaxis_title=None, **PLOT)
        st.plotly_chart(fig, width="stretch")
    with c2:
        st.markdown("**Produzione annua**")
        fig = px.bar(pv_serie.sort_values("anno"), x="anno", y="valore",
                     color_discrete_sequence=["#F59E0B"])
        fig.update_layout(height=340, yaxis_title="GWh", xaxis_title=None, **PLOT)
        st.plotly_chart(fig, width="stretch")

    st.subheader("Distribuzione sul territorio")
    st.caption(f"Fonte: {DOC.FONTE_PROVINCE}, integrata con il PER FVG 2024.")

    prov_pv = pd.DataFrame([
        {"Provincia": p, "Produzione (GWh)": v["Fotovoltaico"]}
        for p, v in DOC.PRODUZIONE_PROVINCE.items()
    ])
    c3, c4 = st.columns(2)
    with c3:
        fig = px.bar(prov_pv.sort_values("Produzione (GWh)"), x="Produzione (GWh)", y="Provincia",
                     orientation="h", text_auto=".0f", color_discrete_sequence=["#FACC15"])
        fig.update_layout(height=300, yaxis_title=None,
                          title="Produzione fotovoltaica 2024", **PLOT)
        st.plotly_chart(fig, width="stretch")
    with c4:
        if not pv_prov.empty:
            dens = pv_prov.dropna(subset=["densita_potenza_w_ab"])
            fig = px.bar(dens.sort_values("densita_potenza_w_ab"), x="densita_potenza_w_ab",
                         y="provincia", orientation="h", text_auto=".0f",
                         color_discrete_sequence=["#F59E0B"])
            fig.update_layout(height=300, yaxis_title=None, xaxis_title="W per abitante",
                              title="Potenza per abitante", **PLOT)
            st.plotly_chart(fig, width="stretch")

    if not pv_prov.empty:
        st.markdown("**Dettaglio provinciale**")
        tab = pv_prov.rename(columns={
            "provincia": "Provincia", "impianti": "Impianti",
            "produzione_gwh_2022": "Produzione 2022 (GWh)", "potenza_mw": "Potenza (MW)",
            "densita_potenza_w_ab": "W/abitante", "densita_potenza_kw_km2": "kW/km²",
            "produzione_specifica_kwh_kw": "kWh per kW installato"})
        st.dataframe(tab, hide_index=True, width="stretch")
        st.caption(
            "L'ultima colonna è la produttività specifica: quanto rende un kW installato. "
            "Varia poco tra province — l'irraggiamento in regione è abbastanza uniforme, "
            "le differenze vere sono di quanto si è installato, non di quanto rende."
        )

    if not pv_tra.empty:
        st.subheader("La traiettoria del PER")
        prod = pv_tra[pv_tra["grandezza"] == "Produzione annua"]
        pot = pv_tra[pv_tra["grandezza"] == "Potenza di picco"]
        sup = pv_tra[pv_tra["grandezza"] == "Superficie occupata"]
        fig = go.Figure()
        fig.add_bar(x=pot["anno"], y=pot["valore"], name="Potenza di picco (MWp)",
                    marker_color="#FACC15")
        fig.add_scatter(x=prod["anno"], y=prod["valore"], name="Produzione (GWh)",
                        mode="lines+markers", line=dict(color="#111827", width=3), yaxis="y2")
        fig.update_layout(height=380, template="plotly_white",
                          yaxis=dict(title="MWp"),
                          yaxis2=dict(title="GWh", overlaying="y", side="right"),
                          margin=dict(t=30, b=10, l=10, r=10),
                          legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0))
        st.plotly_chart(fig, width="stretch")
        if not sup.empty:
            st.caption(
                "Superficie stimata dal PER per ospitare questa crescita: "
                + " · ".join(f"**{int(r.anno)}: {r.valore:,.0f} ha**".replace(",", ".")
                             for r in sup.itertuples())
            )

    st.info(
        "**Cosa manca ancora.** Qui c'è la distribuzione per provincia, ma non la "
        "mappatura vera: georeferenziazione degli impianti, distinzione tra tetti "
        "e impianti a terra, superficie agricola occupata, prossimità alle cabine "
        "primarie. Quei dati stanno in Atlaimpianti del GSE e nel catasto regionale "
        "degli impianti: quando li recuperiamo, questa scheda diventa una mappa."
    )

# ================================================================ GAS
with tabs[8]:
    st.subheader("Il gas naturale nel sistema energetico regionale")
    bil = D.carica_per("bilancio_2021")
    consumi_f = D.carica_per("consumi_finali_2021")

    if not bil.empty:
        v = bil.set_index("voce")["valore"]
        gas_import = v.get("Combustibili gassosi", 0)
        gas_finali = consumi_f[consumi_f["vettore"].str.contains("gassos", case=False, na=False)]
        gas_fin_tot = gas_finali["valore"].sum()
        gas_trasf = max(0.0, gas_import - gas_fin_tot)

        g = st.columns(4)
        g[0].metric("Gas in ingresso (2021)", f"{gas_import:,.0f} ktep".replace(",", "."))
        g[1].metric("Agli usi finali", f"{gas_fin_tot:,.0f} ktep".replace(",", "."),
                    f"{gas_fin_tot / gas_import * 100:.0f}% del totale" if gas_import else None)
        g[2].metric("Alla trasformazione", f"{gas_trasf:,.0f} ktep".replace(",", "."),
                    f"{gas_trasf / gas_import * 100:.0f}% del totale" if gas_import else None)
        g[3].metric("Quota sul consumo interno lordo",
                    f"{gas_import / v.get('Consumo interno lordo', 1) * 100:.0f}%")

        st.caption(
            "Il gas è il primo vettore del sistema regionale. Circa due terzi vanno "
            "direttamente agli usi finali — soprattutto riscaldamento civile e calore "
            "di processo — e un terzo entra in centrale per produrre elettricità e calore."
        )

        # Sankey del solo gas
        nodi_g = ["Gas naturale in ingresso", "Usi finali diretti", "Generazione e cogenerazione"]
        nodi_g += [f"{r.settore} (diretto)" for r in gas_finali.itertuples() if r.valore > 0]
        nodi_g += ["Elettricità e calore", "Perdite di conversione"]
        ig = {n: i for i, n in enumerate(nodi_g)}
        colori_g = ["#9CA3AF", "#6B7280", "#F97316"] + \
                   ["#2563EB"] * len([r for r in gas_finali.itertuples() if r.valore > 0]) + \
                   ["#FACC15", "#EF4444"]
        sg, tg, vg, cg = [], [], [], []

        def lg(a, b_, val, col):
            if val and val > 0:
                sg.append(ig[a]); tg.append(ig[b_]); vg.append(float(val)); cg.append(col)

        lg("Gas naturale in ingresso", "Usi finali diretti", gas_fin_tot, "rgba(107,114,128,0.35)")
        lg("Gas naturale in ingresso", "Generazione e cogenerazione", gas_trasf, "rgba(249,115,22,0.35)")
        for r in gas_finali.itertuples():
            lg("Usi finali diretti", f"{r.settore} (diretto)", r.valore, "rgba(37,99,235,0.3)")
        rend_gas = v.get("Rendimento", 0.64)
        utile = gas_trasf * rend_gas
        lg("Generazione e cogenerazione", "Elettricità e calore", utile, "rgba(250,204,21,0.45)")
        lg("Generazione e cogenerazione", "Perdite di conversione", gas_trasf - utile,
           "rgba(239,68,68,0.3)")

        fig = go.Figure(go.Sankey(
            node=dict(pad=18, thickness=20, label=nodi_g, color=colori_g,
                      line=dict(color="rgba(0,0,0,0.15)", width=0.5)),
            link=dict(source=sg, target=tg, value=vg, color=cg,
                      hovertemplate="%{value:.0f} ktep<extra></extra>"),
        ))
        fig.update_layout(height=440, font_size=12, margin=dict(t=20, b=20, l=10, r=10))
        st.plotly_chart(fig, width="stretch")
        st.caption(
            f"Il rendimento applicato al ramo di trasformazione è quello medio del "
            f"sistema regionale ({rend_gas * 100:.0f}%), non misurato sul solo gas."
        )

        st.subheader("Dove va il gas che non passa dalla centrale")
        fig = px.bar(gas_finali.sort_values("valore"), x="valore", y="settore", orientation="h",
                     text_auto=".0f", color_discrete_sequence=["#9CA3AF"])
        fig.update_layout(height=300, xaxis_title="ktep", yaxis_title=None, **PLOT)
        st.plotly_chart(fig, width="stretch")

    st.divider()
    st.subheader("Il lato elettrico: produzione da gas")
    gas_el = prod_comb[prod_comb["voce"].str.contains("gas", case=False, na=False)]
    if not gas_el.empty:
        c1, c2 = st.columns(2)
        with c1:
            fig = px.area(gas_el.sort_values("anno"), x="anno", y="valore",
                          color_discrete_sequence=["#9CA3AF"])
            fig.update_layout(height=340, yaxis_title="GWh elettrici", xaxis_title=None,
                              title="Produzione elettrica da gas naturale", **PLOT)
            st.plotly_chart(fig, width="stretch")
        with c2:
            em_gas = emissioni[emissioni["voce"].str.contains("gas", case=False, na=False)]
            fig = px.area(em_gas.sort_values("anno"), x="anno", y="valore",
                          color_discrete_sequence=["#EF4444"])
            fig.update_layout(height=340, yaxis_title="Mt CO₂", xaxis_title=None,
                              title="Emissioni dalla generazione a gas", **PLOT)
            st.plotly_chart(fig, width="stretch")

        picco = gas_el.loc[gas_el["valore"].idxmax()]
        ultimo = gas_el[gas_el["anno"] == gas_el["anno"].max()]["valore"].sum()
        st.info(
            f"La generazione elettrica a gas ha toccato il massimo nel **{int(picco['anno'])}** "
            f"con {picco['valore']:,.0f} GWh ed è scesa a **{ultimo:,.0f} GWh** nell'ultimo anno "
            "disponibile: circa ".replace(",", ".")
            + f"{(1 - ultimo / picco['valore']) * 100:.0f}% in meno. "
            "È il singolo fattore che spiega quasi tutto il calo delle emissioni elettriche "
            "regionali. La scheda «Termo & CO₂» disaggrega per categoria di impianto."
        )

# ================================================================ IDROGENO
with tabs[10]:
    st.subheader("Idrogeno: a che punto è il Friuli-Venezia Giulia")
    st.caption(f"Fonte: {DOC.FONTE_H2}.")

    n = DOC.H2_NAHV
    h = st.columns(4)
    h[0].metric("Finanziamento NAHV", f"{n['Finanziamento europeo (mln €)']} mln €")
    h[1].metric("Organizzazioni partner", n["Organizzazioni partner"])
    h[2].metric("Durata del progetto", f"{n['Durata (mesi)']} mesi")
    h[3].metric("Autobus a idrogeno previsti", sum(DOC.H2_MEZZI_TPL.values()))

    st.markdown(
        "La **North Adriatic Hydrogen Valley** è il progetto che tiene insieme "
        "Friuli-Venezia Giulia, Slovenia e Croazia, finanziato da Horizon Europe e "
        "avviato a settembre 2023. Attorno ci sono i progetti PNRR e una filiera "
        "industriale regionale già interessata: siderurgia, trasporti, chimica, "
        "oltre 120 attori mappati nella consultazione del 2022, polarizzati su Udine e Trieste."
    )

    st.subheader("I progetti concreti")
    prog = pd.DataFrame(DOC.H2_PROGETTI)
    hub = DOC.H2_PROGETTI[0]
    p1, p2, p3, p4 = st.columns(4)
    p1.metric("Elettrolisi Hydrogen Hub Trieste", f"{hub['elettrolisi_mw']:.0f} MW")
    p2.metric("Fotovoltaico dedicato", f"{hub['fv_dedicato_mwp']:.2f} MWp")
    p3.metric("Produzione attesa", f"{hub['produzione_ton_anno']} t/anno",
              f"di cui {hub['da_fv_ton_anno']} t da FV")
    p4.metric("Finanziamento PNRR", f"{hub['finanziamento_mln']} mln €")

    for pr in DOC.H2_PROGETTI:
        with st.expander(f"{pr['nome']} — {pr['soggetto']}"):
            st.markdown(f"**Stato:** {pr['stato']}\n\n{pr['nota']}")

    st.subheader("Le criticità dichiarate dalla Regione")
    for titolo, testo in DOC.H2_CRITICITA:
        st.markdown(f"**{titolo}** — {testo}")

    st.warning(
        "Il vincolo più stringente è il primo: l'idrogeno rinnovabile richiede elettricità "
        "rinnovabile in eccesso, e il FVG non ne ha. Con 5 MW di elettrolisi si producono "
        "370 tonnellate l'anno; per confronto, la sola siderurgia regionale consuma oltre "
        "2 TWh elettrici. L'idrogeno qui è una scommessa industriale e infrastrutturale "
        "di lungo periodo, non una voce del bilancio energetico di oggi."
    )

# ---- aggiunte alla scheda Scenari: il Sankey 2045
with tabs[11]:
    st.divider()
    st.subheader("Come cambiano i consumi finali: 2021 e 2045 a confronto")

    cons21 = D.carica_per("consumi_finali_2021")
    ind_v = D.carica_per("scenari_industria_vettori")
    tra_al = D.carica_per("trasporti_alimentazione")
    sc_all = D.carica_per("scenari_settori")

    if not (cons21.empty or ind_v.empty or tra_al.empty):
        st.caption(
            "A sinistra il vettore, a destra il settore. Il PER disaggrega i vettori al 2045 "
            "per industria e trasporti; per il civile fornisce solo il totale, quindi resta "
            "un flusso unico. Scenario: Policy B per l'industria."
        )

        def sankey_consumi(coppie: list[tuple[str, str, float]], titolo: str) -> go.Figure:
            vettori = sorted({v for v, _, val in coppie if val > 0})
            settori = sorted({s for _, s, val in coppie if val > 0})
            nodi = vettori + settori
            idx_ = {n: i for i, n in enumerate(nodi)}
            palette = {"Gas": "#9CA3AF", "Combustibili gassosi": "#9CA3AF",
                       "Elettricità": "#FACC15", "Energia elettrica": "#FACC15",
                       "FER": "#22C55E", "Energie rinnovabili": "#22C55E",
                       "Calore derivato": "#F97316", "Solidi": "#111827",
                       "Combustibili solidi": "#111827", "Petrolio": "#4B5563",
                       "Prodotti petroliferi": "#4B5563", "Idrogeno": "#06B6D4"}
            colori = [palette.get(v, "#D1D5DB") for v in vettori] + ["#2563EB"] * len(settori)
            fig_ = go.Figure(go.Sankey(
                node=dict(pad=16, thickness=18, label=nodi, color=colori,
                          line=dict(color="rgba(0,0,0,0.15)", width=0.5)),
                link=dict(source=[idx_[v] for v, s, val in coppie if val > 0],
                          target=[idx_[s] for v, s, val in coppie if val > 0],
                          value=[val for _, _, val in coppie if val > 0],
                          color=["rgba(37,99,235,0.22)"] * len([c for c in coppie if c[2] > 0]),
                          hovertemplate="%{value:.0f} ktep<extra></extra>"),
            ))
            fig_.update_layout(height=420, font_size=12, title=titolo,
                               margin=dict(t=40, b=20, l=10, r=10))
            return fig_

        c21 = [(r.vettore, r.settore, r.valore) for r in cons21.itertuples()]

        # 2045: industria e trasporti per vettore, civile aggregato
        c45 = [(r.vettore, "Industria", r.valore)
               for r in ind_v[ind_v["anno"] == 2045].itertuples()]
        agg_tra = {"ELETTRICITÁ": "Elettricità", "IDROGENO": "Idrogeno"}
        for r in tra_al[(tra_al["anno"] == 2045) & (tra_al["grandezza"] == "Consumi")].itertuples():
            nome = agg_tra.get(r.alimentazione.upper())
            if nome is None:
                nome = "Biocarburanti ed e-fuel" if any(
                    x in r.alimentazione.upper() for x in ("BIO", "E-", "HVO", "SAF")
                ) else "Prodotti petroliferi"
            c45.append((nome, "Trasporti", r.valore))
        civ45 = sc_all[(sc_all["settore"] == "Civile") & (sc_all["anno"] == 2045)
                       & (sc_all["scenario"] == "B")]["valore"].sum()
        if civ45:
            c45.append(("Vettori non disaggregati", "Civile", civ45))

        agg45: dict[tuple[str, str], float] = {}
        for v_, s_, val in c45:
            agg45[(v_, s_)] = agg45.get((v_, s_), 0) + val
        c45 = [(v_, s_, val) for (v_, s_), val in agg45.items()]

        cc1, cc2 = st.columns(2)
        with cc1:
            st.plotly_chart(sankey_consumi(c21, "2021 — dato di bilancio"), width="stretch")
        with cc2:
            st.plotly_chart(sankey_consumi(c45, "2045 — scenario del PER"), width="stretch")

        tot21 = sum(v for _, _, v in c21)
        tot45 = sum(v for _, _, v in c45)
        st.info(
            f"I consumi finali passano da **{tot21:,.0f}** a **{tot45:,.0f} ktep**, "
            f"circa {(1 - tot45 / tot21) * 100:.0f}% in meno. ".replace(",", ".")
            + "Nei trasporti compare l'idrogeno, che oggi vale zero. Nell'industria il gas "
            "arretra e crescono elettricità e rinnovabili dirette. Il confronto non è "
            "perfettamente simmetrico: il 2021 è un bilancio consuntivo, il 2045 uno scenario, "
            "e il civile resta aggregato perché il PER non ne disaggrega i vettori."
        )

# ---- aggiunte alla scheda Reti: avanzamento, accumuli, distributori
with tabs[4]:
    st.divider()
    st.subheader("Avanzamento verso il target 2030, in dettaglio")
    st.caption(f"Fonte: {DOC.FONTE_RETI_REPORT}.")

    bsm = pd.DataFrame(DOC.BURDEN_SHARING_MW.items(), columns=["Voce", "MW"])
    bsm["Quota"] = bsm["MW"] / DOC.BURDEN_SHARING_TARGET_MW * 100
    fig = px.bar(bsm, x="MW", y=["Target"] * len(bsm), color="Voce", orientation="h",
                 text=bsm.apply(lambda r: f"{r['Voce']}<br>{r['MW']} MW", axis=1),
                 color_discrete_sequence=["#22C55E", "#2563EB", "#60A5FA", "#E5E7EB"])
    fig.update_traces(textposition="inside", insidetextanchor="middle")
    fig.update_layout(height=220, barmode="stack", showlegend=False, yaxis_title=None,
                      xaxis_title=f"MW sul target di {DOC.BURDEN_SHARING_TARGET_MW} MW", **PLOT)
    st.plotly_chart(fig, width="stretch")
    st.caption(
        f"Gli impianti già in esercizio coprono il {bsm.iloc[0]['Quota']:.0f}% del target. "
        "Sommando la pipeline autorizzata si arriva a poco più dell'80%: "
        f"mancano {DOC.BURDEN_SHARING_MW['Quota residua al 2030']} MW."
    )

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Accumuli: richieste contro fabbisogno**")
        b = DOC.BESS
        bess = pd.DataFrame([
            {"Voce": "Richiesto", "MW": b["Potenza richiesta (MW)"]},
            {"Voce": "Fabbisogno stimato", "MW": b["Fabbisogno stimato dal piano (MW)"]},
            {"Voce": "Già attivo (Pavia di Udine)", "MW": b["Impianto già attivo a Pavia di Udine (MW)"]},
        ])
        fig = px.bar(bess, x="Voce", y="MW", text_auto=".0f",
                     color="Voce", color_discrete_sequence=["#A855F7", "#22C55E", "#2563EB"])
        fig.update_layout(showlegend=False, height=320, xaxis_title=None, **PLOT)
        st.plotly_chart(fig, width="stretch")
        st.caption(
            f"{b['Impianti autorizzati o in istruttoria']} impianti tra autorizzati e in "
            "istruttoria. Le richieste valgono quasi cinque volte il fabbisogno stimato dal "
            "piano: è il segnale di una corsa a prenotare capacità più che di un bisogno reale."
        )

    with c2:
        st.markdown("**Interconnessioni transfrontaliere**")
        inter = pd.DataFrame([
            {"Linea": k.split(",")[0], "Attuale": v["attuale"], "Prevista": v["prevista"]}
            for k, v in DOC.INTERCONNESSIONI.items()
        ])
        fig = go.Figure()
        fig.add_bar(x=inter["Linea"], y=inter["Attuale"], name="Capacità attuale",
                    marker_color="#6B7280", text=inter["Attuale"])
        fig.add_bar(x=inter["Linea"], y=inter["Prevista"] - inter["Attuale"],
                    name="Incremento previsto", marker_color="#22C55E")
        fig.update_layout(barmode="stack", height=320, yaxis_title="MW", xaxis_title=None, **PLOT)
        st.plotly_chart(fig, width="stretch")
        st.caption(
            "Il FVG è un ponte elettrico verso Slovenia e Austria. La capacità di importazione "
            "da Redipuglia sale da 700 a 1.200 MW con la razionalizzazione della "
            "Redipuglia–Udine Ovest."
        )

    st.subheader("Chi distribuisce l'energia")
    st.caption(
        "La distribuzione non è di un solo operatore: accanto a e-distribuzione ci sono "
        "le utility urbane e le cooperative storiche alpine, con problemi opposti."
    )
    for nome, d in DOC.DISTRIBUTORI.items():
        riga = f"**{nome}** — {d['clienti']:,} utenze".replace(",", ".")
        if d["energia_gwh"]:
            riga += f", {d['energia_gwh']} GWh/anno"
        st.markdown(riga + f". {d['nota']}.")

    st.subheader("Il nodo della saturazione virtuale")
    sat = pd.DataFrame(DOC.SATURAZIONE_PROVINCE.items(),
                       columns=["Provincia", "% trasformatori in zona rossa"])
    fig = px.bar(sat, x="Provincia", y="% trasformatori in zona rossa", text_auto=".0f",
                 color_discrete_sequence=["#EF4444"])
    fig.update_layout(height=280, xaxis_title=None, yaxis_range=[0, 60], **PLOT)
    st.plotly_chart(fig, width="stretch")
    st.markdown(
        f"Una parte della saturazione è **virtuale**: capacità prenotata da richieste che non "
        f"diventeranno mai impianti. Storicamente solo il **{DOC.TASSO_REALIZZAZIONE}%** "
        "di quanto viene autorizzato si costruisce davvero. "
        f"Il **{DOC.DECRETO_BOLLETTE['riferimento']}** interviene proprio su questo:"
    )
    for titolo, testo in DOC.DECRETO_BOLLETTE["misure"]:
        st.markdown(f"- **{titolo}** — {testo}")

# ---- mappa delle aree di influenza delle cabine primarie
with tabs[4]:
    st.divider()
    st.subheader("Le aree di influenza delle cabine primarie")

    aree = D.carica_per("aree_cabine_primarie")
    geo_cp = D.carica_geojson("aree_cabine_primarie")

    if aree.empty or geo_cp is None:
        st.info("Lancia `python -m src.etl_cabine` per generare la mappa delle cabine primarie.")
    else:
        st.caption(
            "Ogni poligono è il territorio sotteso a una cabina primaria. È la base "
            "geografica su cui si definisce l'appartenenza a una comunità energetica: "
            "produttori e consumatori devono stare sotto la stessa cabina."
        )

        a = st.columns(4)
        a[0].metric("Aree convenzionali", len(aree))
        a[1].metric("Superficie coperta", f"{aree['area_km2'].sum():,.0f} km²".replace(",", "."))
        a[2].metric("Gestori", aree["gestore"].nunique())
        a[3].metric("Area mediana", f"{aree['area_km2'].median():,.0f} km²".replace(",", "."))

        colori_gestore = {"e-distribuzione": "#2563EB", "AcegasApsAmga": "#F97316",
                          "SECAB": "#22C55E"}
        fig = px.choropleth_map(
            aree, geojson=geo_cp, locations="codice", color="gestore",
            color_discrete_map=colori_gestore,
            hover_name="codice",
            hover_data={"gestore": True, "area_km2": ":.0f", "codice": False},
            map_style="carto-positron", zoom=7.2,
            center={"lat": 46.11, "lon": 13.10}, opacity=0.55,
        )
        fig.update_layout(height=560, margin=dict(t=10, b=10, l=0, r=0),
                          legend=dict(orientation="h", yanchor="bottom", y=1.01, x=0,
                                      title=None))
        st.plotly_chart(fig, width="stretch")

        c1, c2 = st.columns([1, 1])
        with c1:
            per_gest = (aree.groupby("gestore")
                        .agg(aree_n=("codice", "count"), km2=("area_km2", "sum"))
                        .reset_index().sort_values("km2"))
            fig = px.bar(per_gest, x="km2", y="gestore", orientation="h", text="aree_n",
                         color="gestore", color_discrete_map=colori_gestore)
            fig.update_traces(textposition="outside", texttemplate="%{text} aree")
            fig.update_layout(showlegend=False, height=280, xaxis_title="km²",
                              yaxis_title=None, title="Territorio per gestore", **PLOT)
            st.plotly_chart(fig, width="stretch")

        with c2:
            fig = px.histogram(aree, x="area_km2", nbins=25,
                               color_discrete_sequence=["#6B7280"])
            fig.update_layout(height=280, xaxis_title="km² per area", yaxis_title="aree",
                              title="Quanto sono grandi le aree", **PLOT)
            st.plotly_chart(fig, width="stretch")

        fuori = int(aree["fuori_regione"].sum())
        piu_grande = aree.loc[aree["area_km2"].idxmax()]
        st.info(
            f"Le aree sono **{len(aree)}** e coprono {aree['area_km2'].sum():,.0f} km². ".replace(",", ".")
            + f"Le dimensioni sono molto diseguali: la più estesa ({piu_grande['codice']}, "
            f"{piu_grande['area_km2']:,.0f} km²) vale quanto decine di aree urbane. ".replace(",", ".")
            + f"**{fuori}** sono a cavallo del confine regionale, cioè fanno capo a cabine "
            "che servono anche territorio fuori dal FVG. "
            "Questa geografia conta per le comunità energetiche: nelle aree montane, grandi e "
            "poco popolate, trovare produttori e consumatori sotto la stessa cabina è molto "
            "più difficile che in città."
        )

        with st.expander("Elenco delle aree"):
            st.dataframe(
                aree.rename(columns={"codice": "Codice", "gestore": "Gestore",
                                     "area_km2": "km²", "fuori_regione": "A cavallo del confine"})
                .sort_values("km²", ascending=False),
                hide_index=True, width="stretch", height=300,
            )

        st.caption(
            "Fonte: dataset regionale AREECONVENZIONALI_CP (aree di influenza delle cabine "
            "primarie di distribuzione). Geometrie semplificate a ~150 m per il web."
        )
