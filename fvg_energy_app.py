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
        "H4sIAF7EdGoC/22WzY4TQQyE7zxL07L7x9M+hlV4AbivhuwQjdglaGZz4elxFBDpLueaT267quzk"
        "dHlZT0s4L/v7ZVvCvC3z84+3FL5fL9v6vC3n9fJz+XB4IuIjMVENy8eXdX/f1m/X37fvgmiU8Hl+"
        "3R8xBSynGuvIcQautpgBK4AlabH95zgp2YfDl+PT4VNg6avk4+1bCofTcp73w6/98HaeQ5aYAOIB"
        "Yn585y+UBihRN9sdygNU2OmpjM+Jo2aD8bVFAmwCbJLII5YIvcnUDXkXHV8VEodDr4t6JmJ0eMpY"
        "L7FjtsYycEKYnZbM0K/b9ZHCaUut0J0QvmotRx3LJRTlpklHVUUnGpsTA4W1ElU0jLFaytVa67mq"
        "giPIKEhVlI05YbWGtrIluAKHMTFXe92oTbjBjBAO0CROwwDNEZeM6vqiVp3TAkY1fFG5Owp3zfxw"
        "EHAYtqZj1qy14pYb8mFpczB1FsvpLqmzqOTkI+NRJqc9y1sCDhVO9q7CuN7ii83Ru18wSJlt7XtR"
        "nAXkVuA6kLP3dpTwtDraZTjBpOpsA02jxsZNbj0Grjn1BFNc1K03QT3UOMMNNky8ZU2AYQJqdobN"
        "3qMMW+H8GeA6+G/xdE8rGiver9w/7A+oEe0CzwgAAA==",
    "aree_disponibili_fv":
        "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",
    "bilancio_2021":
        "H4sIAF7EdGoC/42Uz46bMBDG7/sU1p5aya0wCQSO2dW2yqlR2hdwYBKN1nioPUZVn74GirogSnsC"
        "i9/8+77BV0NVRbKjCmSnDTmQ2lqSwSLrh1PTkmP5TM01eMYrGhSeDNYo1U59TGSapEq+MrQTegZ2"
        "ESCpkkOxBsxy3bX35GOyYp+uwS8W3B1BOIw9dbqPkWmZr6EXvGFgFJbsDE9WmxgmFTU47DTTOjQW"
        "1wIMMDustEzzOXhBT86DQMvgLMhT7WiiowJ5uUl/IqaODOseztJN9isZHRuOh2ZIrTbpz0ATudsE"
        "n5CaaAHIIv8XF62SZbZJTRa8lV9tz3U0UStxRboFMMLg99DvVrot85maNpqHohoXtiz/q63lZqj5"
        "fj4F+wpO3+8ojx3qn0h2yjEctIGFmn3zJB+Hh3jnq7g0IEXwYylt4q+lGd8/ylTNhftGrGMD454J"
        "7k8xd54c1qiXH2+pZA1ZTDyxWb5a9pmsDw39pklEDeu4KGW2KO+0v5FrRiXkybaB+6G04PmXeBPs"
        "tiK/BO5Da1iJXf73i9AzuBp58HoRuD+orcBjYKqGOVGAaP+kcRA9Koq/64LihtHr0UPorwBgrFDu"
        "y616F7A1NmCHuyTfq/RQZirN8jy+78awDw+/AIVMnrNsBQAA",
    "biomassa_province":
        "H4sIAF7EdGoC/42PMQ7CMAxFd07RA0QoTZukrCyMMJQDhNQCS5FdJVEHTk9QVYmhFd3+8Pz8f/JA"
        "LiKLMfKE5NGJzEQQgstwOHPyL6yc95ASPjCUHKoxQkCYWNw4DkBMIExTd/Io/x1cOOK7vGg7s4O+"
        "D1jUtdGq3UH3ESFlEFad9tDXXhSttl+25+wCVBGeyFTSzzAljZSrzLKl1tqsAnN93bQbgqWwaraA"
        "0tHabtZ/AEr5VoOpAQAA",
    "bosco":
        "H4sIAF7EdGoC/3WQPW/DIBCG9/4KlKmVaHR8HTBm8uYu3i3qUgfJDlVM+vt70A5Woi4nAc9z9x5T"
        "KHHO1xT4luaF6u0rXj/TlOJ4Dvw7L7c1jmv8SHlc1e6q5BIWelFPhz5f2By3kkrm7EKHME1x29J7"
        "WuKB9x17Zf2JI4JQR+BSSKpCSe/RiyPc+Y/uiQvQTutqudZBovEokNydyp5/I72QxYUFZ2xlAagq"
        "441XYOu07t+kf0G9coBV1a0CGpB17k590Gg9KcFVXrX1PEhrdbW6+3iUztBf6Ab7ms6jdcQTPDSG"
        "D28DR6Osrr0IF9JqxAr8AGvdHxGvAQAA",
    "centrali_idro":
        "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",
    "consumi_finali_2021":
        "H4sIAF7EdGoC/42UQW7DIBBF9zkFB0AVxqZJlpHVRXdV1QtMYmqNSsACzPlLWre0ERivkOz3Rw/8"
        "MWhtaJDeGyupW9YA6rbMGj3sOOMN7c31PDuPZ1RInFE4ID2NFi9G+dkCkWSS7gKUPTD64eVUTvUY"
        "UMkN4LMe4iOLQPmxCr9ZcJOxHu8Gv0hvI2Gyso88zy6KDevy75PZYZ8nko4QK/IjOGdc/iSbemzx"
        "FILV2eQsGK/jaQP8/yE8aWlHlMRiLE6AW2iDfi612Lcdq6JJfl+fW1R/xXecPRJtdFWfbUpmu1yC"
        "0ybaTXyp0v3X5SSDtBjAmy3X8C7x0+9mlUq+DWtXyZLp99eJVir+V6Ik5JvCK6FFlx9q4J+Ot8cK"
        "m5y737GfM88a7gwFAAA=",
    "demografia_scenari":
        "H4sIAF7EdGoC/y3MOwrAIBBF0T5rGcJ8HHFWIxYpBKMSSJPVZwyp3uUUr/Q+YI45Wnnq6AfM2vLZ"
        "ej7uKzOSboxMQCsJdwSJwXydBYEooZEtTpbCx2GxWmJ1DkzyszqL+M9iZY3OL4kTO1p+AAAA",
    "geo_indicatori":
        "H4sIAF7EdGoC/42MMQ7CMBAE+7yCBxyRiaLAC+AHtNZhr+Ckw4dOjou8HkNBTbe7mp3GLnwTBaFK"
        "eqBWju23qTSoGrGDqbGag7gU69mjZEqWo+M+vKyibBwr/GnQbnFJHF06276q2L+Z6W+wW8UK6Oyy"
        "quyvKNiEd5dPYzrMYVxoCtNMxxMtYxjenBpBvMgAAAA=",
    "inversioni_flusso":
        "H4sIAF7EdGoC/5WVu3LbMBBF+3yFujQYjSVLlFz6EatJbEaUGzeeNYlQOwNiOQDIQl8f6GGKcYiF"
        "3HBAzuG9+wJQG2pR5wjCYqlA5PCO2r/IHZKWgpQz8m3yVufutJ4f1qA1fVuRwZ3/c/Us7slUpK2Y"
        "LMTGNFI8grJSTK+m8z71sVzMj9ThEYQSBlrLAuumVD2xYcs+yAlm+Rahlc7hkGBKppB6X5D0SdyB"
        "ydFGsRXCnlp8Nh2ClpdANyz0CzRCSWI6uwib8XGlpJ00ZC0NNCtIJhHS7OcsueHrdsJi5T2/fIFM"
        "IqQBB2J5xadxhCYslI1/N2hQUzcAIc8MclQyVuUPKpJAJq2j0VqWW6khTteosHqXpox2+R+Ub/PG"
        "+H1kkaL2r1TXpOKd7rj/fDcGfcL+SyZeoenV54y8FOhVXh7EbVXL3Y4GNmSH3DXDc/cJCHvcw/dR"
        "Sp65ZkTOECO0xcbCHzJuaDLOGLZYgLqQYeyoMIQ1sTodE9Z5hBLK/eDNwul3zDLM/ASHFjRw8ZyZ"
        "cDz+sNuBZtPqkLDKcwuG1TgBYYUUVOVNWjahHsQoKZ9y7/LhkLDKWkaKewKScIuy8YO/SaSS7IbJ"
        "xiv0GWmNnFufCgedOQN+kB0beA8KK23AtHg4oeYXMJxOux/lPCe2CBtS1fHoCdsdFqMnf+yNflj3"
        "FTKJkFlTDDXyL5+6qMf4CQAA",
    "parco_impianti_2023":
        "H4sIAF7EdGoC/42RTWrDMBCF9z2FodtBeCTrxwcIJYtCoIWsVVtJB2wpCDkLn6Z36cUq27gNIQld"
        "aCQxb0bzPSXX+NCFI1k4RutbN44WBk/JwimGdkgpRAI7pHBxPZyPYL0PT9s2Bte5lCI1Abb9iaxP"
        "BM/AVclKMHlxNceSiyv1LiTnR1u4w4Eacj65oguxtfC6B8kFUyAZzyfD9D/Lfc4t5aiZXCPnudWt"
        "BhNPQx/UUfr+KnrXki0y1WDhZf8JaBBZ/beJkpmlzbuL/W1q1DyzLpFX1cp9VfDmRgp+dqmclHWd"
        "gyjxjvyRTyi1msZa3jWVuTPjI7NQinlSJbLRqGu9+r0J3RXfpINfrN35Mpe7cJlTusZpGIVC6Avl"
        "IwqtFBOAKPN3GYMrww+AYRR3mwIAAA==",
    "progetti_bioenergie":
        "H4sIAF7EdGoC/41Wy27bRhTd5ysGWQQpMBnM+7GUDTVQ4dStZXSRjTGWJ84AFEcgqRbR1/Rf+mM9"
        "Q/oJS2wJG6YImffec89jNnFI96XLkQ55V2hbtonuypDaQ7zZ/kX7/S513/Imp5vvkfZDHMrNfZcO"
        "hzJ9oE1paROHd2e5pDZ19zlR3G7TENtCP/9ySb4srlZLsr48Z2Tx+Wp1fnmxIGt2xS4oZ8pTybTw"
        "2jga9wPaOBzqSxcv7oVkQWnP6480xlpLtWHBBWGNMNLJ4OyJ6qvLP5ZkWZ//IOuyQQP3HUPxjjWM"
        "fPxtsf6JogkvfBCG5pZsStcXumpJ7oduPwwjLEIx6bk1BnUCD9qN5b3j3hmvuTQ8HC9/lbYRKG42"
        "hTw9rG3kNPzzd20lb0oTyXlp+9INuUkkEsDy2BnQoYpZKzl3dFPaTbPv42tkFFPKeq2k4M5KCxC1"
        "ZdxwpYKxTmsv30IT+z7R92epRWPfcyEXpcOuC122tR/ygWBPPevZezQgQ6CCOcU5mni8xOlNoR8u"
        "HPaCpWCnVleovPFGKaWlEk7Ko+2MNy1Z7yKlMjBurTZijhBOCsGVcyEILbiuYwupheZaK407d7zM"
        "6vLX5fXD/jFewHiWBTSq3NxQUikeQm3fCefsCDKQtdKLECQocHz/yzbf5rL5rsGsRdvmSNZdgwFB"
        "J++AzVxFqzzAAmbaGDmiWMlughUSlzpe8C231r8/0b8OjZkNNUxhFUHP4ouNO7CHg1XSTBNbo5xW"
        "ylmIQZwQ3HLxhfRdrSMNdYwH0NPPKUs57wKH/JXhBm5QJ5XeaINyPkBfxws9Eobt2IJNSsFoljsQ"
        "7+GaKTvxB4NpEC0E+0AfzOxlsHjFKT/pUmrP8oiiZ5AZ3jKHotFKaAPpKM/x/hFFYbn1BsUdpHti"
        "uvPUpdi82CKLrH/gq4IZWqh7lj1QvuFOgrTeCjWCKhxAdio4XNb8N2F/bmK+HQ1rcssnbsXHrj7u"
        "Yg//FMwH6GK2Ic6rxrwA7ax3ExDgssVnKQD4iX7W29gNI+jcvnbtaQMeb1RzdTWHEzkdpAlIDzMB"
        "wa0KimteXerEAq5Lm5qmkPMmgWVq1O0YVjBDCd8J82ElrMYGYBfIKj+lRRUyiB7wVBz1prf4xkNO"
        "7V0iGPo2tW0ccpUWAKiwV8oLQO/NPBU08Ea6KSGct3ZEwLn6X9CYF+YUA992s/qzdD8qEC82UFUD"
        "s58Fg4/qFso6pKydnAyyMxqZ6vVbJo5gXETyLXVdHCK5y5i+a2N3l3tyn2Pb7DcRKYUw7xGHFQdU"
        "gRtrMc/AYDV3XuE3TLGE9B6PE2hMnSDg9YfrV/75TD/Ym4R5YcWzPi50UNIFZDiswE9ccE5LuKrS"
        "XCCmTxGw6xL5us9tfFBefLYDPLq6eJBAzX3EwuM16wpeCR4EDk7wBh1GDBQ2oGH0ygevZq32E9mW"
        "u4yDYCR9wcmvPeSIE8vt08HmE55DMmf7DshwKj1zXjvtn/14Lm/QltI6IMwhVTUZMrIGngwNgan/"
        "N/C+lt2u/sV37mP/HPWVrDiDYNezbXjLlYH/I7VkGHMXuzM4gBkcQYUL7/4FgEPpkC4LAAA=",
    "progetti_fer":
        "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"
        "P/0PaVYk8hhgAAA=",
    "progetti_solare":
        "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",
    "pv_province":
        "H4sIAF7EdGoC/2VPy2rEMAy8+1uEkeX49QPd6x7aXkOauF2xrB2StIF8feVAaaEGm2FGmhnPS/3i"
        "MvIA/Jh5KBvDvNTp8+Bacv+x33pCIpjrlssx9I8dplxW3ob+h9r74e0fed/7+4P+Wq1zHvmdx6bd"
        "5KrnhfO6ZSDvrEawpAPYTpDpkjZgPApO3uioLnXhQyo6CkHILoruTFsK2EYxaAups9qol4mLeKaE"
        "zcomEt36FhCQtIPQoMGImtS1LtJbykmkOecJo07ni+CDREMyupN5Ua16er1IbLKnGkXF32PAO9+6"
        "kROH2D5j0Cbt1TcyexuAYgEAAA==",
    "pv_traiettoria":
        "H4sIAF7EdGoC/42RsQqDMBRF935FPuAhydPEuBc6FQodnB8xbQOSSGo6+PWNVDtV6XwO3AP3Hsl3"
        "dpoIyPsAL+pDtJC8G+lwiaFLkwvesgwTAXJEUBoLDqf28YuXHISqqm2h4oCo9Y4gAZXiqxBG6ydi"
        "nWODMyYsCVJlfm6HX3xOKIXcFnKC0CXfEXKCQL0IR2LOP0fqe4qWeduzwUYXumVLyeYPMW/Kb9Ou"
        "mLebdfqaMrg54ywLxqSBxuUDrOtCw4M2jJxVYlOobWO+Qda7hgRR6c/KGw3m+bwlAgAA",
    "scenari_fer_elettriche":
        "H4sIAF7EdGoC/4WQQQrCMBBF956iBxhkMknTZCtYcSuC61CjDZQMhNjzG7HZtXT9/rz/mRfH7MHF"
        "yDC7iZOHTwzZHe6c3eSb/nxr/ORzTmEYPRCSAKmEOiJcHuNmSiIoq3EnpRA0UbuXakEbqo09Z555"
        "yi4M/J+j0a6zMkJ0tluHxUoWK7w+E9fSRSusNhu0iEmg3qA/M0mx0FNgH316h+V5Ruo1Uo6ENhV9"
        "AasMBmqVAQAA",
    "scenari_industria_vettori":
        "H4sIAF7EdGoC/42STW7CMBBG95wiBxih8V/jbkGULSonsBIjWY1iZKaRuA134WJMGqQugol3lt8n"
        "z/PMDJ4oJg+u7yMMrhvPv30gB5fG9y6FuDrGLrQBJEoBSq4Rfsif4cC3zbXa/GOFIEwea4T6DTWA"
        "M7rr2C6FJtD9NtU36nMpxRpaiaUU22ixWJGttLSz1PavT1XrUxgcxUlNoCoIsp3VBTn2s1iSM6/e"
        "+9p9T1K1yLBxWLXJQC4uPzAHDSicT2HvLs8RocxArimtyEA9CqkcNCBerN4hxTYShersKfHlifsy"
        "Sdi6NMxSpjg8bo0uDvPyzH/7AP3i63xxAwAA",
    "scenari_settori":
        "H4sIAF7EdGoC/33UTW7CMBAF4H1PwQGsaPxLvIQolbpqRXsBC9Jq1GCjOLDg9AUBqsiMs4zyxfPs"
        "ZyV345iGTuRtF8OASYQYk/gZQtx153MQp9BfXx8jjuGlwRP2nfi8fIHbJBQoKZoU83GPi2+MoUch"
        "VV1XIH7H7vDgm/b1QjVQKoGlhlLpPU8tpfV01RU/XkrFQGY4LDUH6WhQ072v+dHgHAPpaO8U58hk"
        "r5YP9xZ3xzwOGO4nxFSktS5ptiVZ0lxRYIrazp3Dvy7V5YG3XGPeFiyXgVm31Jv0vGWq07JAaXva"
        "z7TX7jFnTBEXzbsS0vpbedcnrr5n7gHK2ky1dXJG24k299s+0SsuR122NIWFoqUZ2MRrNgPYkqUZ"
        "THHd+QxfQ8iHNIwoPtoNe4mUN5Wsb3VPNXM9ja2U4TXZoQNdeVuKQoJbVzm6x9m/O/vrePpi7rr+"
        "AZui5jptBgAA",
    "terna_long":
        "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",
    "trasporti_alimentazione":
        "H4sIAF7EdGoC/3VVy3KbQBC85yv8AWiyDxaWo4zXCikVpCScQ26kQrkoW5Cy5Bx0y7flx7ISeLWz"
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
        "H4sIAF7EdGoC/32Sy2rDMBBF9/0Kf4AY9LSkZQjtqqWF9gcEFkE0loofWfjr6za2o1FMVgaf67nH"
        "GrWpScTFmMipc7Hx0+TIxZ1T58kYw+CePofONY5wKig5ptiPbSC8llBL8j34nxuXauOMWbCs4PP3"
        "z23o+5BiIEopEH8TquM7RzNuGaFB2zVyGIdUSAgFjF9LFpopWAUWMVQvLQcjitmonDGQW/lbKsuZ"
        "BqWv8xeY/74ELhHE5Qx0XYzG3QYMXwNfH6/VKbVtsYLZzy4deSI/AdD6PoBMOAWt9oqQjgZp1tCL"
        "77p0CYWMgXrZdsYzFQPM3nFkQoGJnQ7kQYFux3aY+TS/9VX8f7qzx0o11GbZ/240s9PA1aMoEp1v"
        "NrOPLfAu57ug1/wvTrn4XG0DAAA=",
    "geo__aree_cabine_primarie":
        "H4sIAF7EdGoC/7W9TY8uu3Em+F+01lyQQQaD9E5jeHYNNDBLQ2ho5NuCMHLLuLpauA3/98lMPlEV"
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
    "geo__aree_disponibili_fv":
        "H4sIAF7EdGoC/6S9y44kSXYk+iuJ3nBDEPp+zI5DXhIDNDkEu28vhpeL6ExnthOREXkjIwtgEfz3"
        "UXcVkWNm6sEZd26qKrRMzc3U9HEeckT+/Tfv//b99Jv/9pu/OT29/3w7/dXr8/Pp8/v59eU3f/6b"
        "f5ltP37z3/7p339z/jKu+n/e3l8/nT791dOPH6/jgn3f0fD97fX76e39fOnz77/5/Prt58vp2O0/"
        "/vw3X0+v307vb/92uQj3+IfX53/7ev3Vz6+vb1/OL0/v1x/+p3/y4S9iS/HPU/mLGPo///mlIbnQ"
        "0ZDYktq1xbsyW2Jr9dISegts8Wm2FM+WHmaLx30iGmrVT0U04G8f521LDWzBbbPjNa7OllQaW9r1"
        "8UJskS15NoTCBjdvHFrGs9QybxP43rFkXNNxm5jn0ITo+U45oqXwmoT7jJdDy3gMtLAh+vnElQ0Z"
        "r2B98OI58JqA9068S3B9jk1TS5/v3WLjw2BA9ZYp4xOwIed5lx75Qzlcr4mO4xnzHOHoOXzjtWdD"
        "4yWFkybz21bX0MJOtV1fe7y9Zo1NtX/+5//4jz/HzP/d0+fz8+mOOY8OD8z2fP04+S96LXionEOb"
        "LRFjlMd8v7aUUtni62zRNXF2yhzpPCb+bKlqSbiNi7pm/nguuk2q6BXYEq4NKfH5YiloYYOfvx3V"
        "J8U8WxyvCWG2eOfZ4ufTuMJeAT/lkp44zqdxnBx2TeR9fG7oxRbX+mzpjS159gqRO0jF6ASum1TC"
        "/K0YuUYLxiI5bg85oyWqpczfSlwE6TrvLiOYuB2U7vFteOcaPD6ofr3P8SlcganWimnAZx6LZrZw"
        "3Y4fRYtnrx7mmxZtYR2ziWsnj01ztmROA49rSu+Hga9BA98webgZ7WbufvW8jN3/5dfz+PeXP/sf"
        "P15ffn29ay3d6H73yopjSOP1iVuo14kR9SEatoTRUudEbb5ntsxp2fzcuy8t86M3N4+W0dLmQmou"
        "qGX2qn3ufJeWOYIV+9q15frrtc1j7HLnPnu1atf02ZL5zC3MlmotPcyWpF+v886l8c695dmSilrm"
        "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"
        "X+xXINwYNgIA",
    "geo__progetti_bioenergie":
        "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",
    "geo__progetti_solare":
        "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",
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

# ---------------------------------------------------------------- emissioni totali
FONTE_EMISSIONI = "ISPRA, annuario statistico (serie regionale); ARPA FVG, inventario GHG 2021"

# Gas serra totali regionali, kt CO2eq. Attenzione: ISPRA avverte che la sequenza
# non e' una vera serie storica, perche' la metodologia e' cambiata nel tempo.
EMISSIONI_TOTALI_FVG = {
    1990: 15015.9, 1995: 15129.2, 2000: 14312.5, 2005: 16208.3,
    2010: 14895.0, 2015: 11706.5, 2017: 11772.5, 2019: 11297.2,
}
EMISSIONI_QUOTA_NAZIONALE = 3          # % del totale italiano
EMISSIONI_PRO_CAPITE_2019 = 9.3        # t CO2eq per abitante

# Inventario ARPA FVG 2021, metodologia IPCC
INVENTARIO_ARPA = {
    "anno": 2021,
    "quota_energia": 86,               # % del totale dalla macrocategoria Energia
    "quota_trasporto_strada": 25,      # % del totale dal solo trasporto su strada
    "ambiti": ["Trasporti", "Combustione nell'industria", "Riscaldamento",
               "Industrie energetiche"],
}

TARGET_FVGREEN = {
    "riferimento": "Legge regionale 4/2023 (FVGreen)",
    "anno_neutralita": 2045,
}

# ---------------------------------------------------------------- idrogeno, conti
# Resa fotovoltaica regionale usata per i confronti: media FVG da Terna 2024
# (961,4 GWh su 1.210,8 MW installati). Serve a tradurre TWh in MWp e in ettari.
PV_ORE_EQUIVALENTI = 794       # kWh per kWp installato, all'anno
PV_ETTARI_PER_MWP = 1.38       # da progetti autorizzati: 2.268 ha per 1.645,8 MW
H2_KWH_PER_KG = 55             # consumo elettrico dell'elettrolisi, stima corrente


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

bil_kpi = D.carica_per("bilancio_2021")
if not bil_kpi.empty:
    _v = bil_kpi.set_index("voce")["valore"]
    _imp = _v.get("Import totale", 0) - _v.get("Export totale", 0)
    _cil = _v.get("Consumo interno lordo", 1)
    _em_tot = max(DOC.EMISSIONI_TOTALI_FVG.items())[1]
    _em_anno = max(DOC.EMISSIONI_TOTALI_FVG)
    k2 = st.columns(5)
    k2[0].metric("Energia importata", f"{_imp / _cil * 100:.0f}%",
                 f"{_imp:,.0f} ktep su {_cil:,.0f}".replace(",", "."),
                 help="Quota del consumo interno lordo che arriva da fuori regione. Bilancio 2021.")
    k2[1].metric("Risorse interne", f"{_v.get('Risorse interne totale', 0):,.0f} ktep".replace(",", "."))
    k2[2].metric(f"Emissioni totali ({_em_anno})", f"{_em_tot / 1000:.1f} Mt CO₂eq",
                 f"{DOC.EMISSIONI_QUOTA_NAZIONALE}% del totale italiano",
                 help="Tutti i settori e tutti i gas serra, non solo l'elettrico. Fonte ISPRA.")
    k2[3].metric("di cui settore elettrico", f"{em_tot:.2f} Mt CO₂",
                 f"{em_tot / (_em_tot / 1000) * 100:.0f}% del totale" if _em_tot else None)
    k2[4].metric("Neutralità carbonica", DOC.TARGET_FVGREEN["anno_neutralita"],
                 DOC.TARGET_FVGREEN["riferimento"].split("(")[0].strip())

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

    st.divider()
    st.subheader("Quanto fotovoltaico servirebbe")
    st.caption(
        "L'idrogeno rinnovabile è elettricità rinnovabile trasformata. Qui si può vedere "
        "cosa costa, in termini di nuovo solare, produrre una data quantità di idrogeno."
    )

    cc = st.columns(3)
    with cc[0]:
        target_t = st.number_input("Idrogeno da produrre (t/anno)", 100, 100_000, 5_000, 100)
    with cc[1]:
        kwh_kg = st.slider("Consumo dell'elettrolisi (kWh/kg)", 45, 70, DOC.H2_KWH_PER_KG)
    with cc[2]:
        ore_eq = st.slider("Resa del fotovoltaico (kWh per kWp)", 700, 1300,
                           DOC.PV_ORE_EQUIVALENTI, 10)

    fabbisogno_gwh = target_t * kwh_kg / 1000
    mwp = fabbisogno_gwh * 1000 / ore_eq
    ettari = mwp * DOC.PV_ETTARI_PER_MWP
    pv_att_gwh = anno_di(prod_fer[prod_fer["voce"] == "Fotovoltaico"])["valore"].sum()
    pv_att_mw = anno_di(pot_fonte[pot_fonte["voce"] == "Fotovoltaico"])["valore"].sum()

    r = st.columns(4)
    r[0].metric("Elettricità necessaria", f"{fabbisogno_gwh:,.0f} GWh".replace(",", "."))
    r[1].metric("Nuovo fotovoltaico", f"{mwp:,.0f} MWp".replace(",", "."),
                f"{mwp / pv_att_mw * 100:.0f}% dell'installato" if pv_att_mw else None)
    r[2].metric("Superficie", f"{ettari:,.0f} ha".replace(",", "."))
    r[3].metric("Sulla produzione FV attuale",
                f"{fabbisogno_gwh / pv_att_gwh * 100:.0f}%" if pv_att_gwh else "—")

    confronto = pd.DataFrame([
        {"Voce": "Produzione FV attuale", "GWh": pv_att_gwh},
        {"Voce": "Per l'idrogeno impostato sopra", "GWh": fabbisogno_gwh},
        {"Voce": "Consumo elettrico della siderurgia",
         "GWh": DOC.CONSUMI_INDUSTRIA_MERCEOLOGICO[2023]["Siderurgia"]},
        {"Voce": "Consumo elettrico regionale", "GWh": DOC.CONSUMI_ELETTRICI_TOTALE},
    ])
    fig = px.bar(confronto.sort_values("GWh"), x="GWh", y="Voce", orientation="h",
                 text_auto=".0f", color="Voce",
                 color_discrete_sequence=["#06B6D4", "#FACC15", "#4B5563", "#9CA3AF"])
    fig.update_layout(showlegend=False, height=300, yaxis_title=None, **PLOT)
    st.plotly_chart(fig, width="stretch")

    # i conti sull'Hydrogen Hub, con gli stessi parametri
    hub_t = hub["produzione_ton_anno"]
    hub_gwh = hub_t * kwh_kg / 1000
    hub_mwp = hub_gwh * 1000 / ore_eq
    sider = DOC.CONSUMI_INDUSTRIA_MERCEOLOGICO[2023]["Siderurgia"]
    sider_mwp = sider * 1000 / ore_eq
    sider_ha = sider_mwp * DOC.PV_ETTARI_PER_MWP

    st.warning(
        f"Il vincolo più stringente è il primo, e si può quantificare. L'Hydrogen Hub di "
        f"Trieste produrrà **{hub_t} tonnellate l'anno**: servono circa **{hub_gwh:.0f} GWh** "
        f"di elettricità, cioè **{hub_mwp:.0f} MWp** di solare su circa "
        f"**{hub_mwp * DOC.PV_ETTARI_PER_MWP:.0f} ettari**. Il progetto ne dedica "
        f"{hub['fv_dedicato_mwp']:.2f} MWp, che coprono {hub['da_fv_ton_anno']} tonnellate su "
        f"{hub_t}: il resto viene dalla rete.\n\n"
        f"Per capire la scala: la sola siderurgia regionale consuma **{sider:,.0f} GWh** "
        f"l'anno. ".replace(",", ".")
        + f"Coprirli con nuovo fotovoltaico richiederebbe circa **{sider_mwp:,.0f} MWp** — "
        f"{sider_mwp / pv_att_mw:.1f} volte tutto il solare oggi installato in regione — su "
        f"**{sider_ha:,.0f} ettari**, cioè {sider_ha / 100:.0f} km². ".replace(",", ".")
        + "L'idrogeno qui è una scommessa industriale e infrastrutturale di lungo periodo, "
        "non una voce del bilancio energetico di oggi."
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

# ---- Fotovoltaico: dove si potrebbe installare (dati RSE)
with tabs[5]:
    st.divider()
    aree_fv = D.carica_per("aree_disponibili_fv")
    geo_fv = D.carica_geojson("aree_disponibili_fv")

    if not aree_fv.empty:
        st.subheader("Dove si potrebbe installare")
        st.caption(
            "Elaborazione RSE sulla base della Corine Land Cover 2018, al netto dei vincoli "
            "ambientali, paesaggistici e culturali. Sono superfici *eleggibili*, non aree "
            "idonee ai sensi di legge: dicono dove il territorio lo permetterebbe, non dove "
            "è consentito o conveniente."
        )

        tot_com = aree_fv["areakmq"].sum()
        s = st.columns(4)
        s[0].metric("Superficie regionale", f"{tot_com:,.0f} km²".replace(",", "."))
        s[1].metric("Aree agricole", f"{aree_fv['areakmq2'].sum():,.0f} km²".replace(",", "."),
                    f"{aree_fv['areakmq2'].sum() / tot_com * 100:.0f}% del territorio")
        s[2].metric("Agricole al netto dei vincoli",
                    f"{aree_fv['area2netta'].sum():,.0f} km²".replace(",", "."))
        s[3].metric("Superficie costruita",
                    f"{aree_fv['areacnkm2'].sum():,.0f} km²".replace(",", "."),
                    "il potenziale sui tetti")

        categorie = [
            ("Aree agricole al netto dei vincoli", "area2netta", "#22C55E"),
            ("di cui seminativi non irrigui", "area211net", "#65A30D"),
            ("Superficie impermeabilizzata", "areacnkm2", "#6B7280"),
            ("Superficie costruita (CTR)", "areactrkm2", "#9CA3AF"),
            ("Aree industriali e commerciali", "areakmq121", "#4B5563"),
            ("Agricole entro 500 m da aree industriali", "areakmqaal", "#F97316"),
            ("Aree estrattive", "areakmq131", "#A855F7"),
            ("Discariche", "areakmq132", "#EF4444"),
        ]
        cat = pd.DataFrame([
            {"Categoria": nome, "km²": aree_fv[col].sum(), "colore": c}
            for nome, col, c in categorie
        ]).sort_values("km²")

        fig = px.bar(cat, x="km²", y="Categoria", orientation="h", text_auto=".0f",
                     color="Categoria",
                     color_discrete_map=dict(zip(cat["Categoria"], cat["colore"])))
        fig.update_layout(showlegend=False, height=380, yaxis_title=None,
                          xaxis_type="log", xaxis_title="km² (scala logaritmica)", **PLOT)
        st.plotly_chart(fig, width="stretch")
        st.caption(
            "Scala logaritmica: le categorie differiscono di tre ordini di grandezza. "
            "Cave e discariche insieme fanno 6,6 km², le agricole al netto dei vincoli 1.887."
        )

        vista = st.selectbox(
            "Cosa mostrare sulla mappa",
            ["Aree agricole al netto dei vincoli", "Seminativi non irrigui al netto dei vincoli",
             "Superficie impermeabilizzata", "Agricole entro 500 m da aree industriali"],
        )
        colmap = {"Aree agricole al netto dei vincoli": ("area2netta", "Greens"),
                  "Seminativi non irrigui al netto dei vincoli": ("area211net", "YlGn"),
                  "Superficie impermeabilizzata": ("areacnkm2", "Greys"),
                  "Agricole entro 500 m da aree industriali": ("areakmqaal", "Oranges")}
        col, scala = colmap[vista]
        mappa = aree_fv.copy()
        mappa["quota"] = mappa[col] / mappa["areakmq"] * 100

        if geo_fv is not None:
            fig = px.choropleth_map(
                mappa, geojson=geo_fv, locations="comune", color="quota",
                color_continuous_scale=scala, map_style="carto-positron", zoom=7.2,
                center={"lat": 46.11, "lon": 13.10}, opacity=0.7,
                hover_name="comune",
                hover_data={col: ":.1f", "quota": ":.1f", "provincia": True, "comune": False},
                labels={"quota": "% del comune"},
            )
            fig.update_layout(height=560, margin=dict(t=10, b=10, l=0, r=0),
                              coloraxis_colorbar=dict(title="% del<br>comune"))
            st.plotly_chart(fig, width="stretch")

        top = mappa.nlargest(10, col)[["comune", "provincia", col, "quota"]]
        top.columns = ["Comune", "Provincia", "km²", "% del comune"]
        c1, c2 = st.columns([1, 1])
        with c1:
            st.markdown(f"**I dieci comuni con più superficie: {vista.lower()}**")
            st.dataframe(top.round(1), hide_index=True, width="stretch")
        with c2:
            prov = mappa.groupby("provincia")[col].sum().reset_index()
            fig = px.bar(prov.sort_values(col), x=col, y="provincia", orientation="h",
                         text_auto=".0f", color_discrete_sequence=["#22C55E"])
            fig.update_layout(height=260, yaxis_title=None, xaxis_title="km²",
                              title="Per provincia", **PLOT)
            st.plotly_chart(fig, width="stretch")

        st.info(
            "Il confronto che conta è tra le due strade. Le **aree agricole disponibili** sono "
            f"**{aree_fv['area2netta'].sum():,.0f} km²**: sfruttarne anche solo l'1% con un ".replace(",", ".")
            + "coefficiente di 11 m²/kW darebbe circa 1,7 GW, cioè quasi l'intero target 2030. "
            f"La **superficie impermeabilizzata** è {aree_fv['areacnkm2'].sum():,.0f} km², ".replace(",", ".")
            + "un ottavo, ma non sottrae suolo agricolo. Le **aree agricole entro 500 m da zone "
            f"industriali** — la categoria che il D.Lgs. 199/2021 indica come prioritaria — sono "
            f"solo **{aree_fv['areakmqaal'].sum():.0f} km²**: da sole non bastano."
        )

# ---- Idroelettrico: la mappa delle centrali
with tabs[7]:
    st.divider()
    centrali = D.carica_per("centrali_idro")
    if not centrali.empty:
        st.subheader("Le centrali sul territorio")
        st.caption(
            "Censimento RSE: grandi impianti (rilevazione 2020) e impianti per potenza e "
            "tipologia (2024). Non è l'intero parco regionale — il PER conta 268 impianti — "
            "ma copre le centrali con dati tecnici documentati."
        )

        c = st.columns(4)
        c[0].metric("Impianti mappati", len(centrali))
        c[1].metric("Potenza mappata", f"{centrali['potenza_mw'].sum():,.1f} MW".replace(",", "."))
        c[2].metric("Il più grande", f"{centrali['potenza_mw'].max():,.0f} MW".replace(",", "."))
        anni = centrali["anno"].dropna()
        if len(anni):
            c[3].metric("Anno mediano di costruzione", f"{int(anni.median())}")

        mappa_cen = centrali.copy()
        mappa_cen["size_mw"] = mappa_cen["potenza_mw"].fillna(0).clip(lower=0)
        fig = px.scatter_map(
            mappa_cen, lat="lat", lon="lon", size="size_mw", color="tipo",
            hover_name="nome",
            hover_data={"comune": True, "potenza_mw": ":.2f", "anno": True,
                        "salto_m": ":.0f", "lat": False, "lon": False, "size_mw": False},
            size_max=32, zoom=7.2, center={"lat": 46.3, "lon": 13.0},
            map_style="carto-positron",
            labels={"potenza_mw": "MW", "salto_m": "salto (m)"},
        )
        fig.update_layout(height=560, margin=dict(t=10, b=10, l=0, r=0),
                          legend=dict(orientation="h", yanchor="bottom", y=1.01, x=0, title=None))
        st.plotly_chart(fig, width="stretch")

        c1, c2 = st.columns(2)
        with c1:
            per_tipo = (centrali.groupby("tipo")
                        .agg(n=("nome", "count"), mw=("potenza_mw", "sum"))
                        .reset_index().sort_values("mw"))
            fig = px.bar(per_tipo, x="mw", y="tipo", orientation="h", text="n",
                         color_discrete_sequence=["#2563EB"])
            fig.update_traces(textposition="outside", texttemplate="%{text} impianti")
            fig.update_layout(height=300, xaxis_title="MW", yaxis_title=None,
                              title="Potenza per tipologia", **PLOT)
            st.plotly_chart(fig, width="stretch")
        with c2:
            con_anno = centrali.dropna(subset=["anno"])
            if len(con_anno):
                fig = px.scatter(con_anno, x="anno", y="potenza_mw", color="tipo",
                                 hover_name="nome", log_y=True)
                fig.update_layout(height=300, xaxis_title=None, yaxis_title="MW (log)",
                                  title="Quando sono stati costruiti", showlegend=False, **PLOT)
                st.plotly_chart(fig, width="stretch")

        grandi = centrali.nlargest(8, "potenza_mw")[
            ["nome", "comune", "provincia", "potenza_mw", "tipo", "anno", "salto_m"]]
        grandi.columns = ["Impianto", "Comune", "Prov.", "MW", "Tipo", "Anno", "Salto (m)"]
        st.markdown("**Gli impianti maggiori**")
        st.dataframe(grandi.round(1), hide_index=True, width="stretch")

        vecchi = centrali[centrali["anno"] < 1960]["potenza_mw"].sum()
        st.info(
            f"Il parco è vecchio e concentrato: gli impianti costruiti prima del 1960 valgono "
            f"**{vecchi:,.0f} MW** dei {centrali['potenza_mw'].sum():,.0f} mappati. ".replace(",", ".")
            + "Accanto a poche grandi centrali a serbatoio e bacino, costruite tra gli anni "
            "Trenta e Cinquanta, c'è una lunga coda di impianti ad acqua fluente sotto il "
            "megawatt, spesso su canali e rogge. È il motivo per cui il margine di crescita "
            "è limitato: i siti buoni sono occupati da quasi un secolo."
        )

# ---- Reti: le inversioni di flusso
with tabs[4]:
    st.divider()
    inv = D.carica_per("inversioni_flusso")
    if not inv.empty:
        st.subheader("Quando la rete lavora al contrario")
        st.caption(
            "Elenco e-distribuzione delle sezioni AT/MT in cui, nel 2025, il flusso di energia "
            "si è invertito — la distribuzione ha immesso verso l'alta tensione invece di "
            "prelevare — per almeno l'1% o il 5% delle ore dell'anno."
        )

        i = st.columns(4)
        i[0].metric("Sezioni con inversione", len(inv))
        i[1].metric("Cabine primarie coinvolte", inv["cabina"].nunique())
        i[2].metric("Sezioni oltre il 5% del tempo", int(inv["oltre_5_pct"].sum()))
        i[3].metric("Province interessate", inv["provincia"].nunique())

        c1, c2 = st.columns(2)
        with c1:
            per_prov = (inv.groupby("provincia")
                        .agg(sezioni=("sezione", "count"),
                             oltre5=("oltre_5_pct", "sum"),
                             cabine=("cabina", "nunique")).reset_index())
            fig = go.Figure()
            fig.add_bar(x=per_prov["provincia"], y=per_prov["sezioni"],
                        name="Almeno l'1% del tempo", marker_color="#FACC15")
            fig.add_bar(x=per_prov["provincia"], y=per_prov["oltre5"],
                        name="Almeno il 5%", marker_color="#EF4444")
            fig.update_layout(height=320, barmode="overlay", yaxis_title="sezioni AT/MT",
                              xaxis_title=None, title="Sezioni per provincia", **PLOT)
            st.plotly_chart(fig, width="stretch")
        with c2:
            top_cab = (inv.groupby(["cabina", "provincia"])
                       .agg(sezioni=("sezione", "count"), oltre5=("oltre_5_pct", "sum"))
                       .reset_index().nlargest(10, "sezioni"))
            fig = px.bar(top_cab.sort_values("sezioni"), x="sezioni", y="cabina",
                         orientation="h", color="provincia", text="sezioni")
            fig.update_layout(height=320, yaxis_title=None, xaxis_title="sezioni",
                              title="Le cabine più interessate", **PLOT)
            st.plotly_chart(fig, width="stretch")

        with st.expander("Elenco completo delle sezioni"):
            tab = inv[["provincia", "cabina", "sezione", "oltre_1_pct", "oltre_5_pct"]].copy()
            tab.columns = ["Provincia", "Cabina primaria", "Sezione", "≥ 1% del tempo", "≥ 5% del tempo"]
            st.dataframe(tab.sort_values(["Provincia", "Cabina primaria"]),
                         hide_index=True, width="stretch", height=320)

        quota5 = inv["oltre_5_pct"].sum() / len(inv) * 100
        st.info(
            f"**{inv['cabina'].nunique()} cabine primarie su 45** hanno almeno una sezione che "
            f"si inverte, e nel **{quota5:.0f}%** dei casi succede per oltre il 5% delle ore. "
            "Non è un guasto: è la generazione distribuita che ha superato il consumo locale. "
            "Ma le cabine primarie sono state progettate per un flusso a senso unico, e "
            "l'inversione è il segnale fisico che il limite di quel progetto è stato raggiunto. "
            "Udine e Pordenone concentrano il fenomeno, le stesse province dove i trasformatori "
            "risultano più saturi."
        )

# ---- Emissioni totali regionali (scheda Termo & CO2)
with tabs[9]:
    st.divider()
    st.subheader("Le emissioni di tutta la regione, non solo dell'elettrico")
    st.caption(f"Fonte: {DOC.FONTE_EMISSIONI}.")

    em_tot_df = pd.DataFrame(DOC.EMISSIONI_TOTALI_FVG.items(), columns=["anno", "kt"])
    ultimo_anno = em_tot_df["anno"].max()
    ultimo_val = em_tot_df.loc[em_tot_df["anno"].idxmax(), "kt"]

    e = st.columns(4)
    e[0].metric(f"Gas serra totali ({ultimo_anno})", f"{ultimo_val / 1000:.1f} Mt CO₂eq")
    e[1].metric("Pro capite", f"{DOC.EMISSIONI_PRO_CAPITE_2019:.1f} t/ab",
                "tra i più alti in Italia")
    e[2].metric("Dalla macrocategoria Energia", f"{DOC.INVENTARIO_ARPA['quota_energia']}%",
                f"inventario ARPA {DOC.INVENTARIO_ARPA['anno']}")
    e[3].metric("Dal trasporto su strada", f"{DOC.INVENTARIO_ARPA['quota_trasporto_strada']}%")

    fig = px.bar(em_tot_df, x="anno", y="kt", text_auto=".0f",
                 color_discrete_sequence=["#6B7280"])
    fig.add_scatter(x=[2045], y=[0], mode="markers+text", text=["neutralità 2045"],
                    textposition="top center", marker=dict(size=14, color="#22C55E"),
                    name="Obiettivo FVGreen")
    fig.update_layout(height=380, yaxis_title="kt CO₂eq", xaxis_title=None, **PLOT)
    st.plotly_chart(fig, width="stretch")

    st.warning(
        f"Attenzione a leggerla come una serie storica: ISPRA avverte che la metodologia è "
        f"cambiata nel tempo, quindi i confronti fra anni lontani sono indicativi. "
        f"Il dato solido è l'ordine di grandezza: **{ultimo_val / 1000:.1f} Mt CO₂eq** contro "
        f"gli **{em_tot:.2f} Mt** del solo settore elettrico nel {anno}. "
        "L'elettrico è circa un decimo del problema: il resto sono trasporti, riscaldamento "
        "e combustione industriale. La Legge FVGreen fissa la neutralità al 2045, cinque anni "
        "prima del termine europeo."
    )

# ---- Fotovoltaico: la pipeline autorizzativa e il suolo
with tabs[5]:
    st.divider()
    prog = D.carica_per("progetti_solare")
    geo_prog = D.carica_geojson("progetti_solare")

    if not prog.empty:
        st.subheader("Cosa c'è in cantiere, e quanto suolo occupa")
        st.caption(
            "Progetti fotovoltaici e agrivoltaici passati per il procedimento autorizzativo "
            "regionale. Potenza convertita da kW in MW, superficie da m² in ettari."
        )

        attivi = prog[prog["stato"].isin(
            ["Autorizzato", "In costruzione", "In istruttoria", "Realizzato"])]
        p = st.columns(4)
        p[0].metric("Progetti", len(prog))
        p[1].metric("Potenza in pipeline", f"{attivi['potenza_mw'].sum():,.0f} MW".replace(",", "."),
                    help="Esclusi i procedimenti sospesi o archiviati.")
        p[2].metric("Superficie interessata",
                    f"{attivi['superficie_ha'].sum():,.0f} ha".replace(",", "."))
        p[3].metric("Quota agrivoltaico",
                    f"{(prog['tipo'] == 'Agrivoltaico').sum() / len(prog) * 100:.0f}%",
                    f"{(prog['tipo'] == 'Agrivoltaico').sum()} progetti")

        c1, c2 = st.columns(2)
        with c1:
            per_stato = (prog.groupby("stato")
                         .agg(n=("nome", "count"), mw=("potenza_mw", "sum"))
                         .reset_index().sort_values("mw"))
            fig = px.bar(per_stato, x="mw", y="stato", orientation="h", text="n",
                         color="stato",
                         color_discrete_map={"Autorizzato": "#22C55E", "Realizzato": "#2563EB",
                                             "In costruzione": "#FACC15",
                                             "In istruttoria": "#F97316",
                                             "Sospeso o archiviato": "#9CA3AF", "Altro": "#D1D5DB"})
            fig.update_traces(textposition="outside", texttemplate="%{text} progetti")
            fig.update_layout(showlegend=False, height=320, xaxis_title="MW", yaxis_title=None,
                              title="Potenza per stato del procedimento", **PLOT)
            st.plotly_chart(fig, width="stretch")
        with c2:
            fv = prog[prog["superficie_ha"] > 0].copy()
            fv["ha_per_mw"] = fv["superficie_ha"] / fv["potenza_mw"].replace(0, pd.NA)
            fig = px.scatter(fv.dropna(subset=["ha_per_mw"]), x="potenza_mw", y="superficie_ha",
                             color="tipo", hover_name="nome", log_x=True, log_y=True,
                             color_discrete_map={"Fotovoltaico": "#FACC15",
                                                 "Agrivoltaico": "#65A30D"})
            fig.update_layout(height=320, xaxis_title="MW (log)", yaxis_title="ettari (log)",
                              title="Potenza contro suolo occupato", **PLOT)
            st.plotly_chart(fig, width="stretch")

        if geo_prog is not None:
            st.markdown("**Dove sono**")
            # alcuni progetti non dichiarano la potenza: senza questo la mappa
            # riceve NaN come dimensione del marcatore e va in errore
            mappa_prog = attivi.copy()
            mappa_prog["size_mw"] = mappa_prog["potenza_mw"].fillna(0).clip(lower=0)
            fig = px.scatter_map(
                mappa_prog, lat="lat", lon="lon", size="size_mw", color="tipo",
                hover_name="nome",
                hover_data={"potenza_mw": ":.1f", "superficie_ha": ":.0f", "stato": True,
                            "lat": False, "lon": False, "size_mw": False},
                size_max=30, zoom=7.2, center={"lat": 45.95, "lon": 13.10},
                map_style="carto-positron",
                color_discrete_map={"Fotovoltaico": "#FACC15", "Agrivoltaico": "#65A30D"},
                labels={"potenza_mw": "MW", "superficie_ha": "ha"})
            fig.update_layout(height=520, margin=dict(t=10, b=10, l=0, r=0),
                              legend=dict(orientation="h", yanchor="bottom", y=1.01, x=0,
                                          title=None))
            st.plotly_chart(fig, width="stretch")

        installato = anno_di(pot_fonte[pot_fonte["voce"] == "Fotovoltaico"])["valore"].sum()
        ha_mw = attivi["superficie_ha"].sum() / attivi["potenza_mw"].sum()
        st.info(
            f"In pipeline ci sono **{attivi['potenza_mw'].sum():,.0f} MW**, ".replace(",", ".")
            + f"più di quanto sia installato oggi ({installato:,.0f} MW). ".replace(",", ".")
            + f"Occupano **{attivi['superficie_ha'].sum():,.0f} ettari**, ".replace(",", ".")
            + f"cioè circa **{ha_mw:.1f} ettari per MW**. "
            f"L'agrivoltaico è {(prog['tipo'] == 'Agrivoltaico').sum()} progetti su {len(prog)}: "
            "non marginale, ma neanche prevalente. Da tenere presente che una quota dei "
            "procedimenti non arriva mai in esercizio — le audizioni indicano storicamente "
            f"circa il {DOC.TASSO_REALIZZAZIONE}%."
        )

# ---- Bioenergie: i progetti (scheda Rinnovabili)
with tabs[6]:
    st.divider()
    bio = D.carica_per("progetti_bioenergie")
    if not bio.empty:
        st.subheader("Biomasse e biometano: i progetti in corso")
        b = st.columns(4)
        b[0].metric("Progetti", len(bio))
        b[1].metric("Potenza", f"{bio['potenza_mw'].sum():.1f} MW")
        b[2].metric("Superficie", f"{bio['superficie_ha'].sum():,.0f} ha".replace(",", "."))
        b[3].metric("Quota biometano",
                    f"{(bio['tipo'] == 'Biometano').sum()}/{len(bio)}")

        c1, c2 = st.columns([1.2, 1])
        with c1:
            mappa_bio = bio.copy()
            mappa_bio["size_ha"] = mappa_bio["superficie_ha"].fillna(0).clip(lower=0)
            fig = px.scatter_map(
                mappa_bio, lat="lat", lon="lon", size="size_ha", color="tipo",
                hover_name="nome",
                hover_data={"potenza_mw": ":.2f", "superficie_ha": ":.0f", "stato": True,
                            "lat": False, "lon": False, "size_ha": False},
                size_max=26, zoom=7.4, center={"lat": 45.95, "lon": 13.10},
                map_style="carto-positron",
                color_discrete_map={"Biometano": "#8B4513", "Biomasse": "#A16207"})
            fig.update_layout(height=400, margin=dict(t=10, b=10, l=0, r=0),
                              legend=dict(orientation="h", yanchor="bottom", y=1.01, x=0,
                                          title=None))
            st.plotly_chart(fig, width="stretch")
        with c2:
            per_tipo = bio.groupby(["tipo", "stato"]).size().reset_index(name="n")
            fig = px.bar(per_tipo, x="tipo", y="n", color="stato", text="n",
                         color_discrete_map={"Autorizzato": "#22C55E",
                                             "In istruttoria": "#F97316"})
            fig.update_layout(height=400, xaxis_title=None, yaxis_title="progetti",
                              title="Stato dei procedimenti", **PLOT)
            st.plotly_chart(fig, width="stretch")

        st.caption(
            "Il biometano domina per numero di progetti ma pesa poco in potenza elettrica: "
            "è pensato per essere immesso in rete gas o usato nei trasporti pesanti, non per "
            "produrre elettricità. Sono impianti piccoli e diffusi nella pianura agricola."
        )
