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
        "H4sIAKS4dWoC/22WzY4TQQyE7zxL07L7x9M+hlV4AbivhuwQjdglaGZz4elxFBDpLueaT267quzk"
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
        "H4sIAKS4dWoC/42Uz46bMBDG7/sU1p5aya0wCQSO2dW2yqlR2hdwYBKN1nioPUZVn74GirogSnsC"
        "i9/8+77BV0NVRbKjCmSnDTmQ2lqSwSLrh1PTkmP5TM01eMYrGhSeDNYo1U59TGSapEq+MrQTegZ2"
        "ESCpkkOxBsxy3bX35GOyYp+uwS8W3B1BOIw9dbqPkWmZr6EXvGFgFJbsDE9WmxgmFTU47DTTOjQW"
        "1wIMMDustEzzOXhBT86DQMvgLMhT7WiiowJ5uUl/IqaODOseztJN9isZHRuOh2ZIrTbpz0ATudsE"
        "n5CaaAHIIv8XF62SZbZJTRa8lV9tz3U0UStxRboFMMLg99DvVrot85maNpqHohoXtiz/q63lZqj5"
        "fj4F+wpO3+8ojx3qn0h2yjEctIGFmn3zJB+Hh3jnq7g0IEXwYylt4q+lGd8/ylTNhftGrGMD454J"
        "7k8xd54c1qiXH2+pZA1ZTDyxWb5a9pmsDw39pklEDeu4KGW2KO+0v5FrRiXkybaB+6G04PmXeBPs"
        "tiK/BO5Da1iJXf73i9AzuBp58HoRuD+orcBjYKqGOVGAaP+kcRA9Koq/64LihtHr0UPorwBgrFDu"
        "y616F7A1NmCHuyTfq/RQZirN8jy+78awDw+/AIVMnrNsBQAA",
    "bioenergie_comuni":
        "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"
        "EKQhVR4UxDX+D5LFs4QOLgAA",
    "biomassa_province":
        "H4sIAKS4dWoC/4WQQWrDMBBF9zlFDiAGzWg0I2+76bJduAdwHZGKGivYJoWevuO4gUIK1kJIoP/0"
        "5819HrupVHeZ6rWMfencUscxD0O3ZHf++nCfS74cnurcf5Rj1/d5nst7Gew8HC9THkq+Vvdap1Me"
        "65idBEwevCNkSEgOE7B68U0if1u8x3quU/m2GpxkBaFAJHYITD6hIG8Yj3uct1OxPiiWXjlR0AqJ"
        "YSF4VU4qe4R2Knk2C0rNbSQGTeIIMCAR026D9qW1kI+6phMqNCE5u4TgQ5OacGjr0g35OOVzqaOd"
        "/ngkc+bXnNrOzlQQhdTwY+buC2O8CYsEjWfHEDk10fNdWHyMbopi4O0rTBhBDCSAyEHkMXFXQuG3"
        "XQJyAmpjkv7z3Ayopq0YCSugVSNSEEQKynz4AbhMiB+BAgAA",
    "bosco":
        "H4sIAKS4dWoC/3WQvW7DIBSF9z4FypRI1Lpw+R0zeXMX7xZ1aYKEQ2WTPn+BdrASdTkS3PNxzmV2"
        "2V/SGhzdwiUWvX/59TPMwU9XR79TvC9+WvxHSNOCu6ucsotlgi+HId3IxW855ETJrRzcPPttC+8h"
        "+gMdevJKhjNVChh2QDnjRRlya5VlHTzwz+yZMhBGiEqZ9gJX0iqmCrtDyfG30qlQlGkwUlcvQFGU"
        "VloEXdP6f5v+FbVoQFVUNAUlgdfcHfqElfU4B1P92NazwLUWleof65V2svyFaGZb21mlTfEX89g8"
        "5LiG2cU5RZfTiY5vI0WujGYNYR1aw5jgArRRDKmWCjViDfsBveRVws4BAAA=",
    "centrali_idro":
        "H4sIAKS4dWoC/51YTW8bNxS876/YWy/Egnz8ejw6NhwYSBo3SXPoJaCljcNitVRXkgvk13fIlVNb"
        "diTDCGI5K1vz3vC9mWHGvOrFIq92Yy/WU75L4yJFsc7bfvwRv67+LQ+Xu0W6SUPaxq+3/34X27TO"
        "Io5jFps4bPPXFX582ka8u9Ib8S2P214MeRRD3DZnq3X/40cW969/XghrOymUsV0QZ+2mn27iNqcs"
        "VDAsDMvOWaFcZ8V5P27Sqh+3ub2d4rhMbVqtUxy3qSVJ+AjqPGvN3mjjyBphXGc0ac9OhWCUds2b"
        "OC3SRrwvJU19HPr2SxwWnbj+XSiJKuxcxE1cpLFUgA+x3BlB1PFL8J2UXmrybJmVcaUCFWRgI732"
        "VhI373dDGuO0EedD3P3ot9tcwGVnvaCCvWzj4p9dbL8Nu77wpgKRID+//yIOOFjntJcBNFjWpQZC"
        "LWQ4oCGrTPMpr9ZDvM3iPN5FHEJ7HqcxLephKOvAg7EKYA+JADyXc3Ll7ZNV6E46tgY0aKMLdKlC"
        "GyltcMorx3jafJ7i6iaKz3lY1VF4d3UBIsgL1anniEANjjuNnzEvqsBINIwjDF5ZmodBMqApeO8k"
        "N5/i2F4OGXOAFt/s/o6lf9kpI8ooXP7EDQ7Ue2Hw8Hpeg7Zvy8wP+TbFgmcqHmYsBCZprAzazLyT"
        "JqOt1ZYDN+dpg7EbozjPmwo649lDQOWE7kwQ9igixoWNct4oxsiD64IoMS5eKmeJPSppPuZlRfqY"
        "7vr24rezafETlw5QpQWg1/iij6MGclJp/KEgVUVV0npiwJK3ONj3GTOe26v0uFGS/gBSY0PA7Av6"
        "JFKaLCTBOV/7ZIcnkgnTLgtkhHBgsx8DcjgANCQwBgREdQLR6yC9BysK4zMzGzTjQI2zmODmDAIn"
        "ypf2cz9BMSugNuoAEGersErh9PQoz4qt1xRIyXlcvQ+MhcUQaUxsc53GfhnFh01er/cdOnd4iHMB"
        "8vSsevbeFI2QYKnMqtMklcIAY19Dcx5X+KV+s0nibb/KY2wv+qG9nBL0a8Z+zC1+1xduvQhQjuPY"
        "XkttmPBgrww4WRwmWY8DMhU63o55iM9Dq04/gx1c7ZuOgytpjCEJYVIQxUozMTPAMdLGmubdrhje"
        "Rny4i9MsiJ07HFuoiQ14Qkc7hRI7hQN1EEGnpK6dgnFbVCg4qISCBN3l6XaM0IR7AaJnuoMB2q5+"
        "YTrOLQcdXCDot+d5ikCzVySxKsqj7+avMj2g9v61uo8+HCMnfKHy1GZi3aE8RgelDOZWFBMv8IEg"
        "veDUm+ZLGobYfoTpDcskiub+sUtTcZV7032yMbY8IXeCXS8d1D3gJFmC0rqjBHGC/mKq8VPYmOLz"
        "7dsyOPnQ9PuhGPG+CDokgFlo3WkSWp6gwHlw7nxwrJA9qt0qDcHXUButsMKzz+RFfNK8ebZ5AxmB"
        "2Z5iHutiCIcKUeRZoCw7RAxZpItsRX3XY3um5ZHeST2pAa0zJEufbh0Zw0KfGA7LVtPef2zgUNwA"
        "xTXneRh6yORNBdMlxRwIchCa8CScEGQujeFDi90FNbMMg4PHwwGBrZurzXYqmeb+FXj+Kb+6RAgp"
        "+ITHwTy9seQVZALzVOHQmHIIMAQBsehsWvZjHovl3H93fVFmKRwaa4DDefRH5hSfBELZY5cUVFnX"
        "bWJAWgvTgb1CGr+n/g7uuhElPOUSdy5S+ymvp1jRXQnLBf3TgxjtNN4oXUM+juPDZxCVERGVgjvM"
        "yozvA2kJUwAj0Oaxv0OAmV8Aqd2e5DdzVJQv8B/qDNI4BMIgJcJfadYNFyCSOOeAk23eIbDgt7Ez"
        "i4QRAhL04DGzL4Oy0iEOKaQEqIUMFQpdeS77imxODTaibMOzjPrOuKeEWhFs1X9/XBqCB30engYL"
        "8HMSd9Zbh8QCnp1qLvPtkEpeuf+m/dgv03pX/iHefih+pg7NgMoxa1vl/qgZoEfHHncB7IcvfeOf"
        "ARzD98AJouG4+I5u+wSduE1FKZJ49mEtRL+6DogSCMD6INzoskyoRCNlIAM4CABKgTx9gyzlsW/P"
        "xvKyRbj6/+G+APP6ClAA2EAy1uXuUStQEhcyTDWuayo8rOAad9f8BN3Q69FhAw5/EeuUC3WtWVol"
        "MQMOUg1Rax6c+i8nwb6+fxCNeUfCd7BrW9eNjcc1qBxAOYdfXIwfeaSs1nS/59WrTL0RqlMbGLyU"
        "2ptizBxm7WbGHcmRQ1WMyPe+X+7wofsX7F3Yb/bDtUOKdrrDByBRm+NChmRrQwm54Fjtr8CQdItI"
        "j7zg/ZwMbm5ie7WccB8tqWp+sA+Yh0pT/4/iVKrWsmoNQT2hYm7Oe87gumSQO51B3uuKJ+P34MkP"
        "ESWU5MHJQqbEUSQKrIHG0FEvbW0QERopEzEa9wiH28J/CNgJKsgRAAA=",
    "consumi_finali_2021":
        "H4sIAKS4dWoC/42UQW7DIBBF9zkFB0AVxqZJlpHVRXdV1QtMYmqNSsACzPlLWre0ERivkOz3Rw/8"
        "MWhtaJDeGyupW9YA6rbMGj3sOOMN7c31PDuPZ1RInFE4ID2NFi9G+dkCkWSS7gKUPTD64eVUTvUY"
        "UMkN4LMe4iOLQPmxCr9ZcJOxHu8Gv0hvI2Gyso88zy6KDevy75PZYZ8nko4QK/IjOGdc/iSbemzx"
        "FILV2eQsGK/jaQP8/yE8aWlHlMRiLE6AW2iDfi612Lcdq6JJfl+fW1R/xXecPRJtdFWfbUpmu1yC"
        "0ybaTXyp0v3X5SSDtBjAmy3X8C7x0+9mlUq+DWtXyZLp99eJVir+V6Ik5JvCK6FFlx9q4J+Ot8cK"
        "m5y737GfM88a7gwFAAA=",
    "demografia_scenari":
        "H4sIAKS4dWoC/y3MOwrAIBBF0T5rGcJ8HHFWIxYpBKMSSJPVZwyp3uUUr/Q+YI45Wnnq6AfM2vLZ"
        "ej7uKzOSboxMQCsJdwSJwXydBYEooZEtTpbCx2GxWmJ1DkzyszqL+M9iZY3OL4kTO1p+AAAA",
    "dighe_fvg":
        "H4sIAKS4dWoC/42TTW7cMAyF9z7F7LoRDEoUSWmZToEiQJAGSdtFNwNlxg1U+CdwPLOY0/QuvVgp"
        "JWnTTBbdEIZhP358j9zlu2T2S+7z8TiZ+3k65HGbk0n90h2PaTOYw9Tvh24z9ONmQLPk+6mf7soX"
        "4zht8piPeXp8/p7HzvTTaPq0NGf9bTLnu3nq+m5Z5rydzJcPxrkWDLTgzMc5HfLy6+fq07zLY5pz"
        "Wp2Pq3Xqt93DMu8LjI0OSyFjsXWWJJCQiCNvPLcePZN+Qd5HdL45G26z/vpGUxJtim2IZr1X+KSa"
        "KqElGutaYQyOJUYL3mNVZlJJ4OCAbWjep3mbH17JXl0aH1qpaPRS2JVCRVhhQRxHQUZmLso2CDsF"
        "DyxoqVmnd6ubrj+kU/EYldkXt87m7bR6dkvFGUrBig5AVrxjry5YKh0cBUKkGED7Pnb4tu9P9Tmo"
        "dGzDX3Iu5FzJxZK6rYweKFpXdaONMURxzkmwzXqeHk48UauRn/N9hR1iUHmwNUoEsCgRUJhRqjyK"
        "jyxAKJZdc7EfcpdP5a0r2IJa/nB7W4pUbmTQ2MRaCgGqH94H8g5V3hMQNZfTIc3Htzaz5P4C/aYb"
        "7vu87Yo4PnXAVt0Gq9TMHiLXPSyJ6OLoS6WPzdU0Lt3qOm37fOo6QcvG0T/4xReyFZ9Ap4lCZY2k"
        "rqLz4AQCs+6UgG+u06HbqfEXadCj0cvTi3tOU2+L/++sgjcOoFrGxBYDxhj1Buo4ojEhx8BRQ2s+"
        "v7U87jFlZ0+tKtP4eldBjwx1f0Cih1CHsRw0Xwu6nJ6ar+mHemW+KmQdwhG1pLJiX5xTeNp416IL"
        "kdlqjnqYWK1XZLLoQNQuYt/8BnVNt8XMBAAA",
    "geo_indicatori":
        "H4sIAKS4dWoC/42MMQ7CMBAE+7yCBxyRiaLAC+AHtNZhr+Ckw4dOjou8HkNBTbe7mp3GLnwTBaFK"
        "eqBWju23qTSoGrGDqbGag7gU69mjZEqWo+M+vKyibBwr/GnQbnFJHF06276q2L+Z6W+wW8UK6Oyy"
        "quyvKNiEd5dPYzrMYVxoCtNMxxMtYxjenBpBvMgAAAA=",
    "idro_comuni":
        "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"
        "1j64KwAA",
    "inversioni_flusso":
        "H4sIAKS4dWoC/5WVu3LbMBBF+3yFujQYjSVLlFz6EatJbEaUGzeeNYlQOwNiOQDIQl8f6GGKcYiF"
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
        "H4sIAKS4dWoC/42RTWrDMBCF9z2FodtBeCTrxwcIJYtCoIWsVVtJB2wpCDkLn6Z36cUq27gNIQld"
        "aCQxb0bzPSXX+NCFI1k4RutbN44WBk/JwimGdkgpRAI7pHBxPZyPYL0PT9s2Bte5lCI1Abb9iaxP"
        "BM/AVclKMHlxNceSiyv1LiTnR1u4w4Eacj65oguxtfC6B8kFUyAZzyfD9D/Lfc4t5aiZXCPnudWt"
        "BhNPQx/UUfr+KnrXki0y1WDhZf8JaBBZ/beJkpmlzbuL/W1q1DyzLpFX1cp9VfDmRgp+dqmclHWd"
        "gyjxjvyRTyi1msZa3jWVuTPjI7NQinlSJbLRqGu9+r0J3RXfpINfrN35Mpe7cJlTusZpGIVC6Avl"
        "IwqtFBOAKPN3GYMrww+AYRR3mwIAAA==",
    "progetti_bess":
        "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",
    "progetti_bioenergie":
        "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",
    "progetti_fer":
        "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"
        "fr7Q/w/BYUJIHLYAAA==",
    "progetti_idroelettrico":
        "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",
    "progetti_solare":
        "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"
        "z2bI/he8WSh9bW0AAA==",
    "pv_province":
        "H4sIAKS4dWoC/2VPy2rEMAy8+1uEkeX49QPd6x7aXkOauF2xrB2StIF8feVAaaEGm2FGmhnPS/3i"
        "MvIA/Jh5KBvDvNTp8+Bacv+x33pCIpjrlssx9I8dplxW3ob+h9r74e0fed/7+4P+Wq1zHvmdx6bd"
        "5KrnhfO6ZSDvrEawpAPYTpDpkjZgPApO3uioLnXhQyo6CkHILoruTFsK2EYxaAups9qol4mLeKaE"
        "zcomEt36FhCQtIPQoMGImtS1LtJbykmkOecJo07ni+CDREMyupN5Ua16er1IbLKnGkXF32PAO9+6"
        "kROH2D5j0Cbt1TcyexuAYgEAAA==",
    "pv_traiettoria":
        "H4sIAKS4dWoC/42RsQqDMBRF935FPuAhydPEuBc6FQodnB8xbQOSSGo6+PWNVDtV6XwO3AP3Hsl3"
        "dpoIyPsAL+pDtJC8G+lwiaFLkwvesgwTAXJEUBoLDqf28YuXHISqqm2h4oCo9Y4gAZXiqxBG6ydi"
        "nWODMyYsCVJlfm6HX3xOKIXcFnKC0CXfEXKCQL0IR2LOP0fqe4qWeduzwUYXumVLyeYPMW/Kb9Ou"
        "mLebdfqaMrg54ywLxqSBxuUDrOtCw4M2jJxVYlOobWO+Qda7hgRR6c/KGw3m+bwlAgAA",
    "scenari_fer_elettriche":
        "H4sIAKS4dWoC/4WQQQrCMBBF956iBxhkMknTZCtYcSuC61CjDZQMhNjzG7HZtXT9/rz/mRfH7MHF"
        "yDC7iZOHTwzZHe6c3eSb/nxr/ORzTmEYPRCSAKmEOiJcHuNmSiIoq3EnpRA0UbuXakEbqo09Z555"
        "yi4M/J+j0a6zMkJ0tluHxUoWK7w+E9fSRSusNhu0iEmg3qA/M0mx0FNgH316h+V5Ruo1Uo6ENhV9"
        "AasMBmqVAQAA",
    "scenari_industria_vettori":
        "H4sIAKS4dWoC/42STW7CMBBG95wiBxih8V/jbkGULSonsBIjWY1iZKaRuA134WJMGqQugol3lt8n"
        "z/PMDJ4oJg+u7yMMrhvPv30gB5fG9y6FuDrGLrQBJEoBSq4Rfsif4cC3zbXa/GOFIEwea4T6DTWA"
        "M7rr2C6FJtD9NtU36nMpxRpaiaUU22ixWJGttLSz1PavT1XrUxgcxUlNoCoIsp3VBTn2s1iSM6/e"
        "+9p9T1K1yLBxWLXJQC4uPzAHDSicT2HvLs8RocxArimtyEA9CqkcNCBerN4hxTYShersKfHlifsy"
        "Sdi6NMxSpjg8bo0uDvPyzH/7AP3i63xxAwAA",
    "scenari_settori":
        "H4sIAKS4dWoC/33UTW7CMBAF4H1PwQGsaPxLvIQolbpqRXsBC9Jq1GCjOLDg9AUBqsiMs4zyxfPs"
        "ZyV345iGTuRtF8OASYQYk/gZQtx153MQp9BfXx8jjuGlwRP2nfi8fIHbJBQoKZoU83GPi2+MoUch"
        "VV1XIH7H7vDgm/b1QjVQKoGlhlLpPU8tpfV01RU/XkrFQGY4LDUH6WhQ072v+dHgHAPpaO8U58hk"
        "r5YP9xZ3xzwOGO4nxFSktS5ptiVZ0lxRYIrazp3Dvy7V5YG3XGPeFiyXgVm31Jv0vGWq07JAaXva"
        "z7TX7jFnTBEXzbsS0vpbedcnrr5n7gHK2ky1dXJG24k299s+0SsuR122NIWFoqUZ2MRrNgPYkqUZ"
        "THHd+QxfQ8iHNIwoPtoNe4mUN5Wsb3VPNXM9ja2U4TXZoQNdeVuKQoJbVzm6x9m/O/vrePpi7rr+"
        "AZui5jptBgAA",
    "terna_long":
        "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",
    "trasporti_alimentazione":
        "H4sIAKS4dWoC/3VVy3KbQBC85yv8AWiyDxaWo4zXCikVpCScQ26kQrkoW5Cy5Bx0y7flx7ISeLWz"
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
        "H4sIAKS4dWoC/32Sy2rDMBBF9/0Kf4AY9LSkZQjtqqWF9gcEFkE0loofWfjr6za2o1FMVgaf67nH"
        "GrWpScTFmMipc7Hx0+TIxZ1T58kYw+CePofONY5wKig5ptiPbSC8llBL8j34nxuXauOMWbCs4PP3"
        "z23o+5BiIEopEH8TquM7RzNuGaFB2zVyGIdUSAgFjF9LFpopWAUWMVQvLQcjitmonDGQW/lbKsuZ"
        "BqWv8xeY/74ELhHE5Qx0XYzG3QYMXwNfH6/VKbVtsYLZzy4deSI/AdD6PoBMOAWt9oqQjgZp1tCL"
        "77p0CYWMgXrZdsYzFQPM3nFkQoGJnQ7kQYFux3aY+TS/9VX8f7qzx0o11GbZ/240s9PA1aMoEp1v"
        "NrOPLfAu57ug1/wvTrn4XG0DAAA=",
    "geo__aree_cabine_primarie":
        "H4sIAKS4dWoC/7W9TY8uu3Em+F+01lyQQQaD9E5jeHYNNDBLQ2ho5NuCMHLLuLpauA3/98lMPlEV"
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
        "H4sIAKS4dWoC/6S9y44kSXYk+iuJ3nBDEPp+zI5DXhIDNDkEu28vhpeL6ExnthOREXkjIwtgEfz3"
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
    "geo__comuni_fvg":
        "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",
    "geo__progetti_bess":
        "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",
    "geo__progetti_bioenergie":
        "H4sIAKW4dWoC/61Z207cSBD9ldY8RIk0afX9whsgErEiS5ZB+5AsijqDQywZe2R7dgUR/77l6cv0"
        "hNmsMTwRTqqr3UdVdaqKH7P+blXMDmbvCtev2+K4qapi2ZdNPZvPvnmsmx18/jErr2cHZP6TORit"
        "2mZVtH05mP2Y1c3t8N/vfztHHw4vTk/Q4vwYo8P3F6fH52eHaIEv8Bkc6stVA2ZHJZj3rm4A6nrX"
        "D9jhum/a8v5++A28N31R37svt//A7ZgbsFvDdd/KZVl8+e5mBwyLh/nsphgctXfDJ4Qv/NhUdzeb"
        "Zyybpr0ua9dvXvL5M2XYcqHYXEhstaHyau4xHjErVcQkUQGzJmJKhKOSR2jH3dXVw8PcM0ZHM3Z6"
        "/ucJOqmL9uYOLZolkHbTYiCsxRVGrz8eLt78mrfTGpVd3677gT73E3X1uqoeUUeweTJ1HDNDBd28"
        "1SjJhvcPGJGeE6OlCZi2xkQ7Gu12zmY8sbE8XRS3Dl61XDYosTDwVRb9X2tCCjLwVi6byqHjpu4a"
        "OF8VyCGIu1E0/jL8HlHIsZ5AIeeS67lQmAirA4UQfFRtMEmFjJjh3GPEqohpocJZyiO24y+jlY+l"
        "9aiogdPvZYPOmhae3MxP6oFG9ApB/na4w7u0ua4rJrNGp7FGKLVD8BiplQ0vJ8RKj1lmIsa4CRjP"
        "sHjWiojt+MtYE6NZG5io0WLlJrKzNy+ZxXRCTdNUGjtEATwr1i8NseQxRomImNLSY4zqiEkrPAZU"
        "BYzxaKdFPMsUYx6TLN2xc2/GoxzN4+n57yeXodhNpJJi8ohJhe2UCscZ2TyIMBniDCBpPKQTxiwN"
        "ZoZvMRbsrJTxrIjujIjFEdLYZzFTItnl12Y0qrE0ntTl17JZfhdljQ7runRo0VZTy93+0MR8CqEQ"
        "ND5LldDxtYAxj8nEKPwzYXKLxaNqezRzlzGlxzK1XzAWfyQBHiJxulDIR8TJCcQxrKzZZCCBIAld"
        "irJa+AhTKnQfGgIrmEkbE5UQycJRQePR3FtGmxndpJwcfkDd/8XULzsRgtljdvSEggcFXGvKN3EA"
        "NSsKgiGcBiyqIzQimx7OQJ7SZOabE8O00QlT2mNKRVXWWgbMqORv59qMR/tU3cArfIifReaeloRg"
        "NUU9GFc6VHuuUrXnKlT7pApQ7fVjlVE8qMxWY0zUGL7VmOCNWZs0Jr81b5zHzxptUdRH5Utmq8Fy"
        "AoVSEJ+ZVIjAjBQQcx4zUX+lkMx3a1QZnuxksIP+LmK5u5ya0UPFcdEWrsoKHHa4m0rUPoHl0wQW"
        "mhJfwKmKk4Hg0gYoiaQQ0ucy1VsrHpAkJEKS4Mykg7n/nDk2RUrfVa78uhkz/DC2Ix4ucvt65bo3"
        "Lyq2dBK5hIggENLI0OoSwkP7oghXERNaBCyWOxANKcJZu7XL/eVsjp4uFreu7Td5StQTRtqnJu0U"
        "ugToRQg8QkNICZgWQphRyyIGo1WwEyJiJigGsTxhO/5yukaPFZdNXVRVg46rAlSCP6eL27szmTJ/"
        "DUsOYv0uZMjRuPgghnuMWR0x6GQ9xkmyY0KHs5qls7m/nCk5qY9Lqejuy6K+LhBE2deihkeUQ9MC"
        "EfcoQ583xk5LUKFhyBrerXXQBMCUMgHTsfwBxgNmtY6YpgEyCVLWY9C/hJwVmvg6qSGCecR2rs3p"
        "Vs+j+/Tvpr0bgvTlc1pNmoQtMdp3fIqTuMmD5i7MFjxFKtlMawOmWIxUIEyHGYSnszv+cupGTxxn"
        "Dn0r2tb1Dl2XEJZt7eCzO3RTurpaLx16hZYYdZ17wQBlEwVEa1/9tOBRA3zYAWIjYiOkWFIKK4TH"
        "0haQUBJo14psvWUX5GyOHkQuX13ujGrPlpM9Q8mUzTLHVBjmK53WJJBAhSU2YHEVCnYyYCZmN4VO"
        "xq9MtdraWRbsZJTkn+7IGbTjNaZtC/RpDV8fGhq37RMBujh7WW2m01bNNAxz3Ii0Qg7DV7ZVBsEO"
        "WFwMwkRsbDyaTube8uUzeeLg9hbdNtclPM+hrgFG6vvSVQX6mhbSbwEHAT9at1NZZHu6bWYmbOz/"
        "YzxL09l2i2fZng0g27MBlHEDKLdnw0ioxJ6RMKeaPm9F86lZrYafQOaN6/ZuDJ+rOFMWNdpI5v8A"
        "osL2fsD8GtoqlrYyRgnfLikRp2Jj/DILzKiJmK+t4IzFBe3uBQOjVw//Akx93JG9GwAA",
    "geo__progetti_idroelettrico":
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
# Media FVG 2019-2022 (Terna), anni in cui il parco era stabile e il rapporto
# produzione/potenza non e' falsato dalla crescita. Dal 2023 il fotovoltaico
# regionale e' raddoppiato in due anni: dividere per la potenza di fine anno
# darebbe 794 kWh/kWp, che non e' la resa ma l'effetto degli impianti entrati
# in esercizio a dicembre. Coerente con le 1.100 kWh/kWp indicate da Giusti
# per il Nord Italia su tetto.
PV_ORE_EQUIVALENTI = 1040      # kWh per kWp installato, all'anno
PV_ETTARI_PER_MWP = 1.38       # da progetti autorizzati: 2.268 ha per 1.645,8 MW
H2_KWH_PER_KG = 55             # consumo elettrico dell'elettrolisi, stima corrente

# ---------------------------------------------------------------- costi ed energia
FONTE_PREZZI = "ARERA, Relazione annuale (PUN medio 2025); GSE, prezzi minimi garantiti"

PUN_MEDIO_2025 = 115.9      # €/MWh, il più alto tra le principali borse europee
PREZZO_MINIMO_GARANTITO = {2025: 46.4, 2026: 47.5}   # €/MWh, ritiro dedicato ARERA
RITIRO_DEDICATO_FV_NORD = (75, 115)                  # €/MWh percepiti al Nord nel 2026

# CAPEX di riferimento, €/kW. Valori d'uso corrente sul mercato italiano:
# vanno cambiati dall'interfaccia, non sono un dato ufficiale.
CAPEX_DEFAULT = {
    "Fotovoltaico utility scale": 700,
    "Fotovoltaico su capannoni": 1000,
    "Fotovoltaico residenziale": 1300,
    "Eolico onshore": 1500,
}
# Ore equivalenti annue. Il fotovoltaico è misurato sul FVG (Terna 2024);
# l'eolico è un valore di letteratura, perché in regione non ce n'è.
ORE_EQUIVALENTI = {
    "Fotovoltaico utility scale": 1200,     # a terra al Nord, con tracker su una parte
    "Fotovoltaico su capannoni": 1040,      # misurato in FVG, 2019-2022
    "Fotovoltaico residenziale": 1000,      # falde non ottimali, ombreggiamenti
    "Eolico onshore": 2200,                 # sito di crinale a 5,5 m/s su 100 m
}
OPEX_QUOTA = {  # % del CAPEX all'anno
    "Fotovoltaico utility scale": 1.5, "Fotovoltaico su capannoni": 1.8,
    "Fotovoltaico residenziale": 2.0, "Eolico onshore": 2.5,
}
# Suolo occupato, ha/MW. Il PV a terra viene dai 175 progetti autorizzati in FVG.
# Per l'eolico si contano solo piazzole e viabilità, non l'area interclusa.
SUOLO_HA_MW = {
    "Fotovoltaico utility scale": 1.38, "Fotovoltaico su capannoni": 0.0,
    "Fotovoltaico residenziale": 0.0, "Eolico onshore": 0.024,
}
# Per l'eolico il suolo davvero sottratto ad altri usi e' plinto piu' piazzola:
# circa 1.000 m2 per un aerogeneratore da 4,2 MW. La "servitu' di sorvolo" -
# la proiezione a terra del rotore - e' 15.000 m2, ma resta terreno coltivabile.
EOLICO_SERVITU_HA_MW = 0.36

# Emissioni di ciclo di vita, gCO2/kWh (Politecnico di Milano, Renewable Energy
# Report 2022). Piu' basse dei valori IPCC usati nel simulatore nazionale.
LCA_POLIMI = {
    "Carbone": 1023, "Gas": 436, "Fotovoltaico": 19,
    "Eolico": 12, "Idroelettrico": 11, "Nucleare": 5,
}
EPBT_ANNI = {"Fotovoltaico": 0.43, "Eolico": 1.04}   # tempo di ritorno energetico

# Bilancio elettrico regionale 2024 (Terna): la regione consuma molto piu' di
# quanto produce, ed e' il dato che rende concreta la parola "import".
RICHIESTA_ELETTRICA_2024 = 9814.7      # GWh
DEFICIT_ELETTRICO_2024 = -3341.4       # GWh, pari al -34,0% della richiesta
IMPIANTI_EOLICI_FVG = 4                # potenza non rilevabile nelle statistiche Terna

# ---------------------------------------------------------------- eolico misurato
FONTE_EOLICO = "RSE, Atlante Eolico (dbeta.rse-web.it), dati a 100 m sul livello del terreno"

# Punti campionati sull'Atlante Eolico RSE. `prod_100` e' la producibilita'
# specifica in ore equivalenti annue a 100 m, `dens_100` la densita' di potenza
# in W/m2, `weib_100` il fattore di forma di Weibull.
EOLICO_PUNTI = [
    {"nome": "Carso triestino", "lat": 45.607, "lon": 13.813, "quota": 0,
     "vento_100": 6.46, "dens_100": 591.34, "prod_100": 3168.9, "weib_100": 1.18, "dist_cp": 1.4},
    {"nome": "Colli Orientali (alto)", "lat": 46.091, "lon": 13.542, "quota": 470,
     "vento_100": 6.18, "dens_100": 448.64, "prod_100": 2994.0, "weib_100": 1.31, "dist_cp": 11.0},
    {"nome": "Colli Orientali", "lat": 46.079, "lon": 13.541, "quota": 185,
     "vento_100": 6.11, "dens_100": 439.13, "prod_100": 2945.1, "weib_100": 1.31, "dist_cp": 11.0},
    {"nome": "Laguna di Grado", "lat": 45.710, "lon": 13.474, "quota": 3,
     "vento_100": 5.25, "dens_100": 296.40, "prod_100": 2279.6, "weib_100": 1.33, "dist_cp": 7.7},
    {"nome": "Alpi Giulie", "lat": 46.352, "lon": 13.416, "quota": 1304,
     "vento_100": 4.67, "dens_100": 289.60, "prod_100": 2098.2, "weib_100": 1.05, "dist_cp": 9.6},
    {"nome": "Alpi Carniche", "lat": 46.571, "lon": 13.044, "quota": 1897,
     "vento_100": 4.87, "dens_100": 232.70, "prod_100": 2032.9, "weib_100": 1.20, "dist_cp": 15.5},
    {"nome": "Pianura isontina", "lat": 45.900, "lon": 13.526, "quota": 26,
     "vento_100": 3.28, "dens_100": 64.42, "prod_100": 1009.7, "weib_100": 1.31, "dist_cp": 5.4},
    {"nome": "Bassa friulana", "lat": 45.901, "lon": 13.508, "quota": 44,
     "vento_100": 3.29, "dens_100": 63.17, "prod_100": 977.3, "weib_100": 1.34, "dist_cp": 5.5},
]

# ---------------------------------------------------------------- centrali termoelettriche
FONTE_CENTRALI = "Piano Energetico Regionale FVG, cap. 4, integrato con documentazione di impianto"

# Le coordinate sono al centro del sito, non rilevate: servono a collocare
# l'impianto sul territorio, non a identificarne il perimetro.
CENTRALI_TERMO = [
    {"nome": "Torviscosa (Edison)", "comune": "Torviscosa", "prov": "UD",
     "mw": 790, "combustibile": "Gas naturale", "tecnologia": "Ciclo combinato cogenerativo",
     "lat": 45.817, "lon": 13.283, "stato": "In esercizio",
     "nota": "Il 54,1% del termoelettrico tradizionale regionale. Fornisce vapore allo "
             "stabilimento Caffaro e alle industrie chimiche limitrofe."},
    {"nome": "Monfalcone (A2A)", "comune": "Monfalcone", "prov": "GO",
     "mw": 336, "combustibile": "Carbone", "tecnologia": "Termoelettrico tradizionale",
     "lat": 45.795, "lon": 13.545, "stato": "Dismissione",
     "nota": "Da maggio 2024 non più abilitata ai mercati dell'energia. Accordo con la Regione "
             "per la conversione a ciclo combinato a gas, predisposto per l'idrogeno."},
    {"nome": "Servola (Elettra Produzione)", "comune": "Trieste", "prov": "TS",
     "mw": 175, "combustibile": "Gas naturale e off-gas siderurgico",
     "tecnologia": "Ciclo combinato cogenerativo", "lat": 45.617, "lon": 13.800,
     "stato": "In esercizio",
     "nota": "Brucia una miscela di metano e gas di processo dell'ex stabilimento siderurgico."},
    {"nome": "Elettrogorizia", "comune": "Gorizia", "prov": "GO",
     "mw": 49.9, "combustibile": "Gas naturale", "tecnologia": "Ciclo combinato",
     "lat": 45.933, "lon": 13.617, "stato": "In esercizio",
     "nota": "In esercizio dal 2004, immette direttamente in alta tensione a 132 kV."},
    {"nome": "Termovalorizzatore di Trieste (Hestambiente)", "comune": "Trieste", "prov": "TS",
     "mw": 14.9, "combustibile": "Rifiuti urbani e speciali", "tecnologia": "Co-incenerimento a griglia",
     "lat": 45.633, "lon": 13.800, "stato": "In esercizio",
     "nota": "Tre linee, 197.000 t/anno autorizzate."},
    {"nome": "Cartiera di Tolmezzo", "comune": "Tolmezzo", "prov": "UD",
     "mw": 17.1, "combustibile": "Gas naturale", "tecnologia": "Cogenerazione industriale",
     "lat": 46.400, "lon": 13.017, "stato": "In esercizio", "nota": "Autoproduzione di stabilimento."},
    {"nome": "Cartiera di Ovaro", "comune": "Ovaro", "prov": "UD",
     "mw": 11.2, "combustibile": "Gas naturale", "tecnologia": "Cogenerazione industriale",
     "lat": 46.483, "lon": 12.888, "stato": "In esercizio", "nota": "Autoproduzione di stabilimento."},
    {"nome": "Mistral FVG (Spilimbergo)", "comune": "Spilimbergo", "prov": "PN",
     "mw": 3.0, "combustibile": "Rifiuti speciali", "tecnologia": "Forno a tamburo rotante",
     "lat": 46.117, "lon": 12.900, "stato": "In esercizio",
     "nota": "Il 20% della produzione copre l'autoconsumo, il resto va in rete."},
]

# ---------------------------------------------------------------- intestazione e note
AUTORE = {
    "nome": "Matteo De Piccoli",
    "ente": "APE FVG",
    "sito": "https://www.ape.fvg.it/",
    "email": "matteo.depiccoli@ape.fvg.it",
    "github": "https://github.com/matteo-dep",
    "linkedin": "https://www.linkedin.com/in/matteo-de-piccoli-2a17a5163",
}

# Etichette di fonte usate sotto i grafici
F_TERNA = "Terna, Dati Statistici (dati.terna.it)"
F_TERNA_REG = "Terna, Statistiche Regionali 2024"
F_PER = "Piano Energetico Regionale FVG 2024"
F_RSE = "RSE, Geoportale ETA (dbeta.rse-web.it) — CC BY-SA 4.0"
F_REGIONE = "Portale cartografico regionale FVG (EAGLE)"
F_AUDIZIONI = "Audizioni IV Commissione consiliare, 21/04/2026"
F_ARPA = "ARPA FVG, «Segnali dal clima in FVG»"
F_ISPRA = "ISPRA, annuario statistico; ARPA FVG, inventario GHG"
F_ELAB = "elaborazione propria sui dati citati"

# Alias di comodo usati dall'app
F_H2 = FONTE_H2
F_EOLICO = FONTE_EOLICO
F_CENTRALI = FONTE_CENTRALI
F_CLIMA = FONTE_CLIMA
F_PROVINCE = FONTE_PROVINCE


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


def grafico(fig, fonte: str, nota: str = "") -> None:
    """Disegna un grafico e ne dichiara la fonte, sempre, subito sotto."""
    st.plotly_chart(fig, width="stretch")
    st.caption(f"Fonte: {fonte}." + (f" {nota}" if nota else ""))


def tabella(df, fonte: str, **kwargs) -> None:
    st.dataframe(df, width="stretch", **kwargs)
    st.caption(f"Fonte: {fonte}.")


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
st.markdown(
    f"""
<div style="border-bottom:1px solid #E5E7EB;padding-bottom:10px;margin-bottom:6px">
<span style="font-size:0.95em">Sviluppato da <b>{DOC.AUTORE['nome']}</b> —
<a href="{DOC.AUTORE['sito']}" target="_blank">{DOC.AUTORE['ente']}</a></span><br>
<span style="font-size:0.85em;color:#6B7280">
🏠 <a href="{DOC.AUTORE['sito']}" target="_blank">Sito dell'ente</a> ·
📧 <a href="mailto:{DOC.AUTORE['email']}">{DOC.AUTORE['email']}</a> ·
💼 <a href="{DOC.AUTORE['linkedin']}" target="_blank">LinkedIn</a> ·
🐙 <a href="{DOC.AUTORE['github']}" target="_blank">GitHub</a>
</span>
</div>
""",
    unsafe_allow_html=True,
)

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
    "⚡ Elettricità",
    "🔌 Reti",
    "☀️ Fotovoltaico",
    "🌱 Rinnovabili",
    "🌲 Biomasse",
    "♻️ Biometano",
    "💧 Idroelettrico",
    "🔥 Gas",
    "🔥 Termo & CO₂",
    "🧪 Idrogeno",
    "🔮 Scenari",
    "🌍 Emissioni",
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
            grafico(fig, DOC.F_TERNA)

    with c2:
        st.subheader("Produzione lorda per fonte")
        fig = px.area(prod_fonte.sort_values("anno"), x="anno", y="valore", color="voce",
                      color_discrete_map=D.mappa_colori(prod_fonte["voce"]))
        fig.update_layout(height=380, yaxis_title="GWh", xaxis_title=None, **PLOT)
        fig.add_vline(x=anno, line_dash="dot", line_color="#111827")
        grafico(fig, DOC.F_TERNA)

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
    grafico(fig, DOC.F_TERNA)

# ================================================================ 2. ELETTRICITÀ
with tabs[1]:
    c1, c2 = st.columns(2)

    with c1:
        st.subheader(f"Produzione per fonte, {anno}")
        m = anno_di(prod_fonte).sort_values("valore", ascending=True)
        fig = px.bar(m, x="valore", y="voce", orientation="h", color="voce",
                     color_discrete_map=D.mappa_colori(m["voce"]), text_auto=".0f")
        fig.update_layout(showlegend=False, height=340, xaxis_title="GWh",
                          yaxis_title=None, **PLOT)
        grafico(fig, DOC.F_TERNA)

    with c2:
        st.subheader(f"Potenza efficiente {tipo_cap.lower()}, {anno}")
        m = anno_di(pot_fonte).sort_values("valore", ascending=True)
        fig = px.bar(m, x="valore", y="voce", orientation="h", color="voce",
                     color_discrete_map=D.mappa_colori(m["voce"]), text_auto=".0f")
        fig.update_layout(showlegend=False, height=340, xaxis_title="MW",
                          yaxis_title=None, **PLOT)
        grafico(fig, DOC.F_TERNA)

    st.subheader("Potenza installata nel tempo")
    fig = px.area(pot_fonte.sort_values("anno"), x="anno", y="valore", color="voce",
                  color_discrete_map=D.mappa_colori(pot_fonte["voce"]))
    fig.update_layout(height=340, yaxis_title="MW", xaxis_title=None, **PLOT)
    grafico(fig, DOC.F_TERNA)

    st.subheader("Ore equivalenti di utilizzo")
    st.caption("Produzione annua / potenza efficiente. Indica quanto intensamente lavora ogni parco.")
    merge = prod_fonte.merge(pot_fonte, on=["anno", "voce"], suffixes=("_gwh", "_mw"))
    merge = merge[merge["valore_mw"] > 1]
    merge["ore"] = merge["valore_gwh"] * 1000 / merge["valore_mw"]
    fig = px.line(merge.sort_values("anno"), x="anno", y="ore", color="voce", markers=True,
                  color_discrete_map=D.mappa_colori(merge["voce"]))
    fig.update_layout(height=340, yaxis_title="ore/anno", xaxis_title=None, **PLOT)
    grafico(fig, DOC.F_TERNA)

# ================================================================ 3. RINNOVABILI
with tabs[4]:
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Produzione rinnovabile per fonte")
        fig = px.area(prod_fer.sort_values("anno"), x="anno", y="valore", color="voce",
                      color_discrete_map=D.mappa_colori(prod_fer["voce"]))
        fig.update_layout(height=360, yaxis_title="GWh", xaxis_title=None, **PLOT)
        grafico(fig, DOC.F_TERNA)

    with c2:
        st.subheader(f"Potenza rinnovabile ({tipo_cap.lower()})")
        fig = px.area(pot_fer.sort_values("anno"), x="anno", y="valore", color="voce",
                      color_discrete_map=D.mappa_colori(pot_fer["voce"]))
        fig.update_layout(height=360, yaxis_title="MW", xaxis_title=None, **PLOT)
        grafico(fig, DOC.F_TERNA)

    st.subheader("Idroelettrico per tipologia di impianto")
    st.caption("Il fluente segue la piovosità, bacini e serbatoi modulano.")
    fig = px.bar(idrico.sort_values("anno"), x="anno", y="valore", color="voce",
                 color_discrete_map=D.mappa_colori(idrico["voce"]))
    fig.update_layout(height=340, yaxis_title="GWh", xaxis_title=None, barmode="stack", **PLOT)
    grafico(fig, DOC.F_TERNA)

# ================================================================ 4. TERMO & CO2
with tabs[9]:
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Produzione termoelettrica per combustibile")
        fig = px.area(prod_comb.sort_values("anno"), x="anno", y="valore", color="voce",
                      color_discrete_map=D.mappa_colori(prod_comb["voce"]))
        fig.update_layout(height=340, yaxis_title="GWh", xaxis_title=None, **PLOT)
        grafico(fig, DOC.F_TERNA)

    with c2:
        st.subheader("Emissioni di CO₂ per combustibile")
        fig = px.area(emissioni.sort_values("anno"), x="anno", y="valore", color="voce",
                      color_discrete_map=D.mappa_colori(emissioni["voce"]))
        fig.update_layout(height=340, yaxis_title="Mt CO₂", xaxis_title=None, **PLOT)
        grafico(fig, DOC.F_TERNA)

    st.subheader("Intensità carbonica della generazione")
    st.caption("Emissioni totali del parco termoelettrico divise per la produzione elettrica lorda regionale.")
    tot_em = emissioni.groupby("anno")["valore"].sum()
    inten = (tot_em * 1e6 / tot_y).dropna().reset_index(name="g_kwh")
    fig = px.line(inten, x="anno", y="g_kwh", markers=True, color_discrete_sequence=["#DC2626"])
    fig.update_layout(height=300, yaxis_title="g CO₂/kWh", xaxis_title=None, **PLOT)
    grafico(fig, DOC.F_TERNA)

    c3, c4 = st.columns(2)
    with c3:
        st.subheader("Cogenerative vs non cogenerative")
        fig = px.bar(prod_cat.sort_values("anno"), x="anno", y="valore", color="voce",
                     color_discrete_map=D.mappa_colori(prod_cat["voce"]))
        fig.update_layout(height=340, yaxis_title="GWh elettrici", xaxis_title=None, **PLOT)
        grafico(fig, DOC.F_TERNA)

    with c4:
        st.subheader("Calore utile da cogenerazione")
        cal = calore.copy()
        cal["voce"] = cal["voce"].map(IMPIANTI_COGEN).fillna(cal["voce"])
        fig = px.bar(cal.sort_values("anno"), x="anno", y="valore", color="voce")
        fig.update_layout(height=340, yaxis_title="GWh termici", xaxis_title=None, **PLOT)
        grafico(fig, DOC.F_TERNA)

# ================================================================ 5. SANKEY
with tabs[0]:
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
        grafico(fig, DOC.F_TERNA)

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
    grafico(fig, DOC.F_TERNA)

    st.info(
        f"Input di combustibile stimato: **{input_comb:,.0f} GWh** · "
        f"elettricità termoelettrica **{el_termo:,.0f} GWh** · "
        f"calore utile **{cal_y:,.0f} GWh** · "
        f"perdite **{perdite:,.0f} GWh**. "
        "L'input non è misurato da Terna: dipende dal rendimento impostato sopra."
        .replace(",", ".")
    )

# ================================================================ 6. TREND
with tabs[14]:
    st.subheader("Sostituzione tra fonti (grafico di Marchetti)")
    st.caption("Asse y: log₁₀(f / (1−f)), con f = quota della fonte. Una retta = sostituzione a ritmo costante.")

    m = prod_fonte.merge(tot_y.rename("tot"), on="anno")
    m = m[(m["tot"] > 0) & (m["valore"] > 0)]
    m["f"] = np.clip(m["valore"] / m["tot"], 1e-4, 1 - 1e-4)
    m["marchetti"] = np.log10(m["f"] / (1 - m["f"]))
    fig = px.line(m.sort_values("anno"), x="anno", y="marchetti", color="voce", markers=True,
                  color_discrete_map=D.mappa_colori(m["voce"]))
    fig.update_layout(height=400, yaxis_title="log(f / 1−f)", xaxis_title=None, **PLOT)
    grafico(fig, DOC.F_ELAB)

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
    grafico(fig, DOC.F_ELAB)

# ================================================================ 7. DATI
with tabs[15]:
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
with st.expander("Fonti, licenze e limiti dei dati"):
    st.markdown(
        f"""
**Da dove vengono i numeri.** Ogni grafico dichiara la propria fonte subito sotto.
Le principali sono: **{DOC.F_TERNA}** per la serie storica del settore elettrico;
**{DOC.F_TERNA_REG}** per il dettaglio provinciale; **{DOC.F_PER}** per il bilancio
energetico e gli scenari; **{DOC.F_RSE}**; **{DOC.F_REGIONE}** per i progetti
autorizzati e le aree delle cabine primarie; **{DOC.F_AUDIZIONI}** per lo stato
delle reti; **{DOC.F_ARPA}** e **{DOC.F_ISPRA}** per clima ed emissioni.

**Licenza dei dati RSE.** I dataset del Geoportale ETA sono distribuiti da RSE S.p.A.
con licenza **Creative Commons BY-SA 4.0**: l'attribuzione va mantenuta e i dati
derivati vanno rilasciati con la stessa licenza.

**Sui dati GSE.** Il GSE è il detentore dei dati di dettaglio sugli impianti
incentivati — Atlaimpianti contiene la georeferenziazione puntuale del fotovoltaico,
la distinzione fra impianti a terra e su copertura, l'alimentazione dei digestori a
biogas e la potenza per classe di taglia. **Questi dati non sono stati usati qui**:
non sono liberamente scaricabili in forma massiva e richiedono una richiesta formale.
Dove servirebbero, l'app usa aggregazioni comunali o provinciali e lo dichiara.
Le conseguenze pratiche sono tre: la mappa del fotovoltaico si ferma al comune e non
arriva al singolo impianto; la distinzione tetto/terra è ricostruita per classe di
potenza e non per tipologia dichiarata; l'alimentazione degli impianti a biogas
(colture dedicate contro scarti e deiezioni) è nota solo come categoria di fonte.
Con l'accesso ai dati GSE queste tre limitazioni cadrebbero.

**Cosa questo strumento non è.** Non è un modello previsionale né un documento di
pianificazione. Gli scenari riproducono quelli del PER; i calcoli parametrici
(copertura, idrogeno, dispacciamento) servono a confrontare ordini di grandezza fra
opzioni, non a valutare investimenti. Dove un dato è stimato, è scritto.
        """
    )
st.caption(
    f"Sviluppato da {DOC.AUTORE['nome']} — [{DOC.AUTORE['ente']}]({DOC.AUTORE['sito']}) · "
    f"[{DOC.AUTORE['email']}](mailto:{DOC.AUTORE['email']}) · "
    f"[LinkedIn]({DOC.AUTORE['linkedin']}) · [GitHub]({DOC.AUTORE['github']})"
)

# ================================================================ CONSUMI FINALI
with tabs[0]:
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
            grafico(fig, DOC.F_TERNA)
        with c2:
            fig = px.pie(per_vettore.reset_index(), values="valore", names="vettore", hole=0.55,
                         color="vettore", color_discrete_map={
                             "Combustibili gassosi": "#9CA3AF", "Energia elettrica": "#FACC15",
                             "Petrolio": "#4B5563", "Energie rinnovabili": "#22C55E",
                             "Calore derivato": "#F97316", "Combustibili solidi": "#111827",
                             "Rifiuti non rinnovabili": "#D1D5DB"})
            fig.update_traces(textinfo="percent+label", textposition="outside")
            fig.update_layout(showlegend=False, height=380, title="Per vettore", **PLOT)
            grafico(fig, DOC.F_TERNA)

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
        grafico(fig, DOC.F_TERNA)

        st.subheader("Composizione di ogni settore")
        fig = px.bar(consumi_f[consumi_f["valore"] > 0], x="settore", y="valore", color="vettore",
                     color_discrete_map={
                         "Combustibili gassosi": "#9CA3AF", "Energia elettrica": "#FACC15",
                         "Petrolio": "#4B5563", "Energie rinnovabili": "#22C55E",
                         "Calore derivato": "#F97316", "Combustibili solidi": "#111827"})
        fig.update_layout(height=400, yaxis_title="ktep", xaxis_title=None, **PLOT)
        grafico(fig, DOC.F_TERNA)

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
        grafico(fig, DOC.F_PER)

        emis = sc[sc["grandezza"] == "Emissioni CO2"]
        if not emis.empty:
            st.subheader("Emissioni di CO₂ per settore")
            fig = px.line(emis.sort_values("anno"), x="anno", y="valore",
                          color="scenario", line_dash="settore", markers=True,
                          color_discrete_map={"Storico": "#111827", "REF": "#6B7280",
                                              "A": "#2563EB", "B": "#22C55E", "PER": "#F97316"})
            fig.update_layout(height=380, yaxis_title="kt CO₂", xaxis_title=None, **PLOT)
            grafico(fig, DOC.F_PER)

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
            grafico(fig, DOC.F_PER)

        with c2:
            st.subheader("Industria: sostituzione dei vettori")
            fig = px.area(ind_v.sort_values("anno"), x="anno", y="valore", color="vettore",
                          color_discrete_map={"Gas": "#9CA3AF", "Elettricità": "#FACC15",
                                              "FER": "#22C55E", "Calore derivato": "#F97316",
                                              "Prodotti petroliferi": "#4B5563",
                                              "Solidi": "#111827"})
            fig.update_layout(height=380, yaxis_title="ktep", xaxis_title=None, **PLOT)
            grafico(fig, DOC.F_PER)

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
            grafico(fig, DOC.F_PER)
            st.caption(
                "Il PER assume −68.000 abitanti e +24% di PIL reale tra il 2021 e il 2045: "
                "il disaccoppiamento tra economia ed energia deve reggere su una base demografica "
                "che si assottiglia."
            )

# ================================================================ RETI
with tabs[2]:
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
        grafico(fig, DOC.F_TERNA)

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
        grafico(fig, DOC.F_AUDIZIONI)

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
        grafico(fig, DOC.F_AUDIZIONI)
    with c4:
        pr = pd.DataFrame(DOC.TRASFORMATORI_PROVINCIA.items(), columns=["Provincia", "Trasformatori"])
        fig = px.bar(pr, x="Provincia", y="Trasformatori", text_auto=True,
                     color_discrete_sequence=["#6B7280"])
        fig.update_layout(height=320, xaxis_title=None,
                          title="Trasformatori AT/MT per provincia", **PLOT)
        grafico(fig, DOC.F_AUDIZIONI)

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
    grafico(fig, DOC.F_AUDIZIONI)
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
    grafico(fig, DOC.F_AUDIZIONI)
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
        grafico(fig, DOC.F_TERNA)

    with c2:
        st.markdown("**Composizione nell'anno selezionato**")
        m = anno_di(idrico)
        m = m[m["valore"] > 0]
        if not m.empty:
            fig = px.pie(m, values="valore", names="voce", hole=0.5,
                         color="voce", color_discrete_map=D.mappa_colori(m["voce"]))
            fig.update_traces(textinfo="percent")
            fig.update_layout(height=400, **PLOT)
            grafico(fig, DOC.F_TERNA)

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
    grafico(fig, DOC.F_TERNA)

    st.info(
        "Il PER stima una producibilità media di "
        f"{DOC.IDRO_PARCO['Producibilità media annua (GWh)']:,.0f} GWh e prevede di arrivare a ".replace(",", ".")
        + "2.231 GWh al 2045: un margine di crescita limitato, perché i siti migliori sono già "
        "sfruttati. L'espansione passa da efficientamento degli impianti esistenti e "
        "mini-idro, non da nuovi grandi invasi."
    )

# ================================================================ CLIMA
with tabs[13]:
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
    grafico(fig, DOC.F_ARPA)

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
        grafico(fig, DOC.F_ARPA)
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
with tabs[3]:
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
        grafico(fig, DOC.F_AUDIZIONI)
    with c2:
        st.markdown("**Produzione annua**")
        fig = px.bar(pv_serie.sort_values("anno"), x="anno", y="valore",
                     color_discrete_sequence=["#F59E0B"])
        fig.update_layout(height=340, yaxis_title="GWh", xaxis_title=None, **PLOT)
        grafico(fig, DOC.F_AUDIZIONI)

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
        grafico(fig, DOC.F_TERNA_REG)
    with c4:
        if not pv_prov.empty:
            dens = pv_prov.dropna(subset=["densita_potenza_w_ab"])
            fig = px.bar(dens.sort_values("densita_potenza_w_ab"), x="densita_potenza_w_ab",
                         y="provincia", orientation="h", text_auto=".0f",
                         color_discrete_sequence=["#F59E0B"])
            fig.update_layout(height=300, yaxis_title=None, xaxis_title="W per abitante",
                              title="Potenza per abitante", **PLOT)
            grafico(fig, DOC.F_TERNA_REG)

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
        grafico(fig, DOC.F_AUDIZIONI)
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
        grafico(fig, DOC.F_TERNA)
        st.caption(
            f"Il rendimento applicato al ramo di trasformazione è quello medio del "
            f"sistema regionale ({rend_gas * 100:.0f}%), non misurato sul solo gas."
        )

        st.subheader("Dove va il gas che non passa dalla centrale")
        fig = px.bar(gas_finali.sort_values("valore"), x="valore", y="settore", orientation="h",
                     text_auto=".0f", color_discrete_sequence=["#9CA3AF"])
        fig.update_layout(height=300, xaxis_title="ktep", yaxis_title=None, **PLOT)
        grafico(fig, DOC.F_TERNA)

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
            grafico(fig, DOC.F_TERNA)
        with c2:
            em_gas = emissioni[emissioni["voce"].str.contains("gas", case=False, na=False)]
            fig = px.area(em_gas.sort_values("anno"), x="anno", y="valore",
                          color_discrete_sequence=["#EF4444"])
            fig.update_layout(height=340, yaxis_title="Mt CO₂", xaxis_title=None,
                              title="Emissioni dalla generazione a gas", **PLOT)
            grafico(fig, DOC.F_TERNA)

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
    grafico(fig, DOC.F_H2)

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
            grafico(sankey_consumi(c21, "2021 — dato di bilancio"), DOC.F_PER)
        with cc2:
            grafico(sankey_consumi(c45, "2045 — scenario del PER"), DOC.F_PER)

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
with tabs[2]:
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
    grafico(fig, DOC.F_AUDIZIONI)
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
        grafico(fig, DOC.F_AUDIZIONI)
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
        grafico(fig, DOC.F_AUDIZIONI)
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
    grafico(fig, DOC.F_TERNA)
    st.markdown(
        f"Una parte della saturazione è **virtuale**: capacità prenotata da richieste che non "
        f"diventeranno mai impianti. Storicamente solo il **{DOC.TASSO_REALIZZAZIONE}%** "
        "di quanto viene autorizzato si costruisce davvero. "
        f"Il **{DOC.DECRETO_BOLLETTE['riferimento']}** interviene proprio su questo:"
    )
    for titolo, testo in DOC.DECRETO_BOLLETTE["misure"]:
        st.markdown(f"- **{titolo}** — {testo}")

# ---- mappa delle aree di influenza delle cabine primarie
with tabs[2]:
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
        grafico(fig, DOC.F_REGIONE)

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
            grafico(fig, DOC.F_TERNA)

        with c2:
            fig = px.histogram(aree, x="area_km2", nbins=25,
                               color_discrete_sequence=["#6B7280"])
            fig.update_layout(height=280, xaxis_title="km² per area", yaxis_title="aree",
                              title="Quanto sono grandi le aree", **PLOT)
            grafico(fig, DOC.F_TERNA)

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
with tabs[3]:
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
        grafico(fig, DOC.F_AUDIZIONI)
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
            grafico(fig, DOC.F_AUDIZIONI)

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
            grafico(fig, DOC.F_AUDIZIONI)

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
        grafico(fig, DOC.F_RSE)

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
            grafico(fig, DOC.F_RSE)
        with c2:
            con_anno = centrali.dropna(subset=["anno"])
            if len(con_anno):
                fig = px.scatter(con_anno, x="anno", y="potenza_mw", color="tipo",
                                 hover_name="nome", log_y=True)
                fig.update_layout(height=300, xaxis_title=None, yaxis_title="MW (log)",
                                  title="Quando sono stati costruiti", showlegend=False, **PLOT)
                grafico(fig, DOC.F_RSE)

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
with tabs[2]:
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
            grafico(fig, DOC.F_AUDIZIONI)
        with c2:
            top_cab = (inv.groupby(["cabina", "provincia"])
                       .agg(sezioni=("sezione", "count"), oltre5=("oltre_5_pct", "sum"))
                       .reset_index().nlargest(10, "sezioni"))
            fig = px.bar(top_cab.sort_values("sezioni"), x="sezioni", y="cabina",
                         orientation="h", color="provincia", text="sezioni")
            fig.update_layout(height=320, yaxis_title=None, xaxis_title="sezioni",
                              title="Le cabine più interessate", **PLOT)
            grafico(fig, DOC.F_AUDIZIONI)

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

# ---- Emissioni: il quadro completo
with tabs[12]:
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
    grafico(fig, DOC.F_ISPRA)

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
with tabs[3]:
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
            grafico(fig, DOC.F_REGIONE)
        with c2:
            fv = prog[prog["superficie_ha"] > 0].copy()
            fv["ha_per_mw"] = fv["superficie_ha"] / fv["potenza_mw"].replace(0, pd.NA)
            fig = px.scatter(fv.dropna(subset=["ha_per_mw"]), x="potenza_mw", y="superficie_ha",
                             color="tipo", hover_name="nome", log_x=True, log_y=True,
                             color_discrete_map={"Fotovoltaico": "#FACC15",
                                                 "Agrivoltaico": "#65A30D"})
            fig.update_layout(height=320, xaxis_title="MW (log)", yaxis_title="ettari (log)",
                              title="Potenza contro suolo occupato", **PLOT)
            grafico(fig, DOC.F_AUDIZIONI)

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
            grafico(fig, DOC.F_AUDIZIONI)

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

# ================================================================ BIOMASSE
with tabs[5]:
    bosco = D.carica_per("bosco")
    disp = D.carica_per("biomassa_province")

    st.subheader("La risorsa forestale del Friuli-Venezia Giulia")
    st.caption(
        "Dati PRI.FOR.MAN dal portale dei consorzi forestali, ripresi nel PER FVG 2024. "
        "Il bosco è classificato su due assi: se è **gestito** (con un piano di gestione "
        "attivo) e se è **accessibile** al prelievo."
    )

    if not bosco.empty:
        tot = bosco[bosco["sigla"] == "TOT"].iloc[0]
        gest = bosco[bosco["sigla"] == "G"]["superficie_ha"].sum()
        acc = bosco[bosco["sigla"].isin(["G - A", "NG - A"])]["superficie_ha"].sum()

        b = st.columns(4)
        b[0].metric("Superficie boscata", f"{tot['superficie_ha']:,.0f} ha".replace(",", "."))
        b[1].metric("Volume in piedi", f"{tot['volume_totale_m3'] / 1e6:.1f} mln m³",
                    f"{tot['volume_medio_m3_ha']:.0f} m³/ha")
        b[2].metric("Bosco gestito", f"{gest / tot['superficie_ha'] * 100:.0f}%",
                    f"{gest:,.0f} ha".replace(",", "."))
        b[3].metric("Bosco accessibile", f"{acc / tot['superficie_ha'] * 100:.0f}%",
                    f"{acc:,.0f} ha".replace(",", "."))

        st.error(
            "**Due errori nel foglio di calcolo del PER, qui corretti.** Il totale sommava "
            "anche i subtotali, contando ogni categoria due volte: 653.742 ha invece di "
            f"{tot['superficie_ha']:,.0f}. ".replace(",", ".")
            + "E i ktep del potenziale erano sbagliati di un fattore mille (0,07 invece di 70). "
            "Vale la pena segnalarlo a chi ha curato il piano."
        )

        dett = bosco[bosco["sigla"].isin(["NG - NA", "NG - A", "G - NA", "G - A"])].copy()
        c1, c2 = st.columns(2)
        with c1:
            fig = px.bar(dett.sort_values("superficie_ha"), x="superficie_ha", y="categoria",
                         orientation="h", text_auto=".0f", color="categoria",
                         color_discrete_map={
                             "Gestito, accessibile": "#22C55E",
                             "Gestito, non accessibile": "#65A30D",
                             "Non gestito, accessibile": "#F97316",
                             "Non gestito, non accessibile": "#9CA3AF"})
            fig.update_layout(showlegend=False, height=320, yaxis_title=None,
                              xaxis_title="ettari", title="Superficie per categoria", **PLOT)
            grafico(fig, DOC.F_PER)
        with c2:
            fig = px.bar(dett.sort_values("volume_medio_m3_ha"), x="volume_medio_m3_ha",
                         y="categoria", orientation="h", text_auto=".0f",
                         color_discrete_sequence=["#8B4513"])
            fig.update_layout(height=320, yaxis_title=None, xaxis_title="m³ per ettaro",
                              title="Densità di massa legnosa", **PLOT)
            grafico(fig, DOC.F_PER)

        st.caption(
            "Il paradosso del bosco friulano: la densità più alta è nel **gestito ma non "
            "accessibile** (246 m³/ha), cioè dove il legname c'è ed è pianificato ma manca la "
            "viabilità per portarlo fuori. Il **non gestito accessibile** — 104.844 ha, la "
            "categoria più estesa — ha invece la densità più bassa: bosco raggiungibile ma "
            "abbandonato."
        )

    if not disp.empty:
        st.divider()
        st.subheader("Quanta energia ci sarebbe, e quanta se ne usa")
        st.caption(
            "Due scenari di prelievo dal PER. Conversione con i parametri dichiarati nel "
            "piano: 3,4 MWh per tonnellata, 0,085985 tep per MWh."
        )

        tot_sc = (disp[disp["provincia"] == "TOT"]
                  .set_index("scenario")[["tonnellate", "gwh", "ktep"]])
        prov = disp[disp["provincia"] != "TOT"]

        c1, c2 = st.columns([1.2, 1])
        with c1:
            fig = px.bar(prov, x="provincia", y="ktep", color="scenario", barmode="group",
                         text_auto=".0f",
                         color_discrete_map={"Boschi accessibili al prelievo": "#22C55E",
                                             "Totale regionale": "#065F46"})
            fig.update_layout(height=340, xaxis_title=None, yaxis_title="ktep/anno",
                              title="Potenziale per provincia", **PLOT)
            grafico(fig, DOC.F_PER)
        with c2:
            bil_b = D.carica_per("bilancio_2021")
            usato = 0.0
            if not bil_b.empty:
                usato = bil_b.set_index("voce")["valore"].get("Biomasse", 0)
            conf = pd.DataFrame([
                {"Voce": "Usato oggi (bilancio 2021)", "ktep": usato},
                {"Voce": "Scenario prudente", "ktep": tot_sc.loc["Boschi accessibili al prelievo", "ktep"]},
                {"Voce": "Scenario esteso", "ktep": tot_sc.loc["Totale regionale", "ktep"]},
            ])
            fig = px.bar(conf, x="ktep", y="Voce", orientation="h", text_auto=".0f",
                         color="Voce",
                         color_discrete_sequence=["#8B4513", "#22C55E", "#065F46"])
            fig.update_layout(showlegend=False, height=340, yaxis_title=None,
                              title="Potenziale contro consumo", **PLOT)
            grafico(fig, DOC.F_PER)

        prud = tot_sc.loc["Boschi accessibili al prelievo", "ktep"]
        est = tot_sc.loc["Totale regionale", "ktep"]
        st.info(
            f"Il bilancio 2021 registra **{usato:.0f} ktep** di biomasse tra le risorse interne. "
            f"Il potenziale forestale stimato va da **{prud:.0f} ktep** (solo boschi accessibili) "
            f"a **{est:.0f} ktep** (tutto il prelievo teorico). "
            f"Anche nell'ipotesi prudente ci sarebbe margine, ma il vincolo non è la risorsa: è "
            "l'accessibilità, la viabilità forestale e la filiera locale. Udine da sola vale i "
            "due terzi del potenziale regionale."
        )

    st.warning(
        "**Cautela su questi numeri.** Il potenziale teorico non è disponibilità reale: "
        "prelevare tutto l'incremento annuo non è sostenibile né dal punto di vista "
        "ecologico né economico, e una parte del legname ha usi più pregiati dell'energia "
        "(edilizia, arredo). Il PER non distingue tra incremento annuo e massa in piedi, "
        "distinzione che cambia radicalmente il senso della cifra."
    )

# ================================================================ BIOMETANO
with tabs[6]:
    bio = D.carica_per("progetti_bioenergie")
    st.subheader("Biogas e biometano")

    if not bio.empty:
        b = st.columns(4)
        b[0].metric("Progetti autorizzati o in corso", len(bio))
        b[1].metric("Di cui biometano", int((bio["tipo"] == "Biometano").sum()))
        b[2].metric("Potenza elettrica", f"{bio['potenza_mw'].sum():.1f} MW")
        b[3].metric("Superficie degli impianti",
                    f"{bio['superficie_ha'].sum():,.0f} ha".replace(",", "."))

        bil_b = D.carica_per("bilancio_2021")
        if not bil_b.empty:
            vb = bil_b.set_index("voce")["valore"]
            st.caption(
                f"Nel bilancio 2021 il biogas vale **{vb.get('Biogas', 0):.0f} ktep** tra le "
                f"risorse interne, più delle biomasse solide ({vb.get('Biomasse', 0):.0f} ktep). "
                "È la bioenergia più rilevante della regione, e quasi tutta di origine agricola."
            )

        mappa_bio2 = bio.copy()
        mappa_bio2["size_ha"] = mappa_bio2["superficie_ha"].fillna(0).clip(lower=0)
        fig = px.scatter_map(
            mappa_bio2, lat="lat", lon="lon", size="size_ha", color="tipo",
            hover_name="nome",
            hover_data={"potenza_mw": ":.2f", "superficie_ha": ":.0f", "stato": True,
                        "lat": False, "lon": False, "size_ha": False},
            size_max=28, zoom=7.4, center={"lat": 45.95, "lon": 13.10},
            map_style="carto-positron",
            color_discrete_map={"Biometano": "#8B4513", "Biomasse": "#A16207"})
        fig.update_layout(height=460, margin=dict(t=10, b=10, l=0, r=0),
                          legend=dict(orientation="h", yanchor="bottom", y=1.01, x=0, title=None))
        grafico(fig, DOC.F_REGIONE)

        elenco = bio[["nome", "tipo", "potenza_mw", "superficie_ha", "stato"]].copy()
        elenco.columns = ["Impianto", "Tipo", "MW", "Ettari", "Stato"]
        st.dataframe(elenco.sort_values("Ettari", ascending=False).round(2),
                     hide_index=True, width="stretch", height=320)

    st.divider()
    st.subheader("Il nodo del suolo: quanto rende un ettaro")
    st.caption(
        "Confronto tra produrre elettricità da mais insilato e produrla dal fotovoltaico "
        "sulla stessa superficie. I parametri sono modificabili: servono a mostrare "
        "l'ordine di grandezza, non a stimare un impianto specifico."
    )

    m1, m2, m3 = st.columns(3)
    with m1:
        resa_mais = st.slider("Resa del mais (t/ha di insilato)", 30, 70, 50)
    with m2:
        metano_t = st.slider("Biogas (m³ di metano per t di insilato)", 80, 130, 105)
    with m3:
        rend_cog = st.slider("Rendimento elettrico del cogeneratore (%)", 30, 45, 38) / 100

    kwh_m3_metano = 9.97  # potere calorifico del metano, kWh per m3
    mwh_ha_bio = resa_mais * metano_t * kwh_m3_metano * rend_cog / 1000
    mwh_ha_pv = DOC.PV_ORE_EQUIVALENTI * (1000 / DOC.PV_ETTARI_PER_MWP) / 1000

    r = st.columns(3)
    r[0].metric("Biogas da mais", f"{mwh_ha_bio:,.0f} MWh/ha".replace(",", "."))
    r[1].metric("Fotovoltaico", f"{mwh_ha_pv:,.0f} MWh/ha".replace(",", "."))
    r[2].metric("Rapporto", f"{mwh_ha_pv / mwh_ha_bio:.0f}×",
                "a favore del fotovoltaico")

    conf = pd.DataFrame([
        {"Tecnologia": "Biogas da mais insilato", "MWh per ettaro": mwh_ha_bio},
        {"Tecnologia": "Fotovoltaico a terra", "MWh per ettaro": mwh_ha_pv},
    ])
    fig = px.bar(conf, x="MWh per ettaro", y="Tecnologia", orientation="h", text_auto=".0f",
                 color="Tecnologia",
                 color_discrete_map={"Biogas da mais insilato": "#8B4513",
                                     "Fotovoltaico a terra": "#FACC15"})
    fig.update_layout(showlegend=False, height=240, yaxis_title=None, **PLOT)
    grafico(fig, DOC.F_PER)

    st.info(
        "È il calcolo che David Pimentel e altri hanno reso familiare nel dibattito sui "
        "biocarburanti: la fotosintesi converte in biomassa una frazione minima "
        "dell'energia solare incidente, e ogni passaggio successivo — insilamento, "
        "digestione, combustione — ne perde ancora. Un pannello salta tutti quei passaggi. "
        f"Sulla stessa superficie il fotovoltaico rende circa **{mwh_ha_pv / mwh_ha_bio:.0f} volte** "
        "l'elettricità del mais da biogas.\n\n"
        "Questo **non** rende il biogas inutile: i digestori che trattano deiezioni zootecniche "
        "e scarti agroindustriali non occupano suolo dedicato, gestiscono un rifiuto che "
        "altrimenti emette metano, e producono digestato che torna al campo. Il confronto "
        "colpisce le colture dedicate, non la filiera degli scarti."
    )

    st.warning(
        "**Manca il dato che servirebbe davvero**: l'alimentazione di ciascun impianto — "
        "mais e colture dedicate, deiezioni, fanghi, FORSU, scarti agroindustriali. "
        "Lo shapefile regionale riporta solo tipo, potenza e superficie. Senza quella "
        "colonna non si può dire quanta parte del biogas friulano stia sul lato "
        "«colture dedicate» e quanta sul lato «scarti», che è la distinzione decisiva."
    )

# ---- Ipotesi di copertura (scheda Transizione)
with tabs[14]:
    st.divider()
    st.subheader("Ipotesi di copertura: quanto costa e quanto suolo serve")
    st.caption(
        "Un modello parametrico, non una previsione. Si sceglie quanta domanda elettrica "
        "coprire con produzione regionale e con quale mix, e si vede cosa comporta in "
        "investimento, costo dell'energia e suolo occupato. Tutti i parametri sono modificabili."
    )

    dom_att = DOC.CONSUMI_ELETTRICI_TOTALE
    prod_att = anno_di(prod_fonte)["valore"].sum()
    fer_att = anno_di(prod_fer)["valore"].sum()

    q = st.columns(4)
    q[0].metric("Domanda elettrica attuale", f"{dom_att:,.0f} GWh".replace(",", "."))
    q[1].metric("Produzione regionale", f"{prod_att:,.0f} GWh".replace(",", "."),
                f"{prod_att / dom_att * 100:.0f}% della domanda")
    q[2].metric("di cui rinnovabile", f"{fer_att:,.0f} GWh".replace(",", "."),
                f"{fer_att / dom_att * 100:.0f}% della domanda")
    q[3].metric("Importato", f"{max(0, dom_att - prod_att):,.0f} GWh".replace(",", "."))

    st.markdown("**1. Quanta domanda coprire con rinnovabili regionali**")
    cc = st.columns(2)
    with cc[0]:
        domanda_2045 = st.slider("Domanda elettrica al 2045 (GWh)", 8000, 20000,
                                 int(dom_att * 1.35), 500,
                                 help="L'elettrificazione di trasporti e calore fa crescere "
                                      "la domanda anche se i consumi finali totali calano.")
    with cc[1]:
        copertura = st.slider("Quota da coprire con nuove rinnovabili regionali (%)",
                              0, 100, 60, 5)

    da_produrre = domanda_2045 * copertura / 100
    nuovo_gwh = max(0.0, da_produrre - fer_att)

    st.markdown("**2. Con quale mix**")
    mx = st.columns(4)
    tecnologie = list(DOC.CAPEX_DEFAULT)
    quote = {}
    default_quote = [50, 25, 15, 10]
    for col, tec, dq in zip(mx, tecnologie, default_quote):
        with col:
            quote[tec] = st.slider(tec.replace("Fotovoltaico ", "FV "), 0, 100, dq, 5,
                                   key=f"q_{tec}")
    somma_q = sum(quote.values()) or 1

    with st.expander("Parametri economici e tecnici"):
        pc = st.columns(3)
        with pc[0]:
            wacc = st.slider("Costo del capitale (%)", 2.0, 12.0, 6.0, 0.5) / 100
        with pc[1]:
            vita = st.slider("Vita utile (anni)", 15, 35, 25)
        with pc[2]:
            prezzo_rif = st.number_input("Prezzo di riferimento (€/MWh)", 40, 250,
                                         int(DOC.PUN_MEDIO_2025))
        capex = {}
        cx = st.columns(4)
        for col, tec in zip(cx, tecnologie):
            with col:
                capex[tec] = st.number_input(f"CAPEX {tec.split()[-1]} (€/kW)", 300, 3000,
                                             DOC.CAPEX_DEFAULT[tec], 50, key=f"c_{tec}")

    def annualita(w: float, n: int) -> float:
        return w / (1 - (1 + w) ** -n) if w else 1 / n

    righe = []
    for tec in tecnologie:
        quota = quote[tec] / somma_q
        gwh = nuovo_gwh * quota
        ore = DOC.ORE_EQUIVALENTI[tec]
        mw = gwh * 1000 / ore if ore else 0
        capex_tot = mw * 1000 * capex[tec] / 1e6            # milioni di €
        opex_anno = capex_tot * DOC.OPEX_QUOTA[tec] / 100
        lcoe = ((capex_tot * annualita(wacc, vita) + opex_anno) * 1e6 / (gwh * 1000)
                if gwh else 0)
        righe.append({
            "Tecnologia": tec, "GWh/anno": gwh, "MW": mw,
            "Investimento (mln €)": capex_tot, "LCOE (€/MWh)": lcoe,
            "Suolo (ha)": mw * DOC.SUOLO_HA_MW[tec],
        })
    mix = pd.DataFrame(righe)
    mix = mix[mix["GWh/anno"] > 0]

    if not mix.empty:
        inv_tot = mix["Investimento (mln €)"].sum()
        suolo_tot = mix["Suolo (ha)"].sum()
        lcoe_medio = ((mix["LCOE (€/MWh)"] * mix["GWh/anno"]).sum() / mix["GWh/anno"].sum())
        import_res = max(0.0, domanda_2045 - da_produrre - (prod_att - fer_att))

        r = st.columns(4)
        r[0].metric("Nuova potenza", f"{mix['MW'].sum():,.0f} MW".replace(",", "."))
        r[1].metric("Investimento", f"{inv_tot / 1000:,.1f} mld €".replace(",", "."))
        r[2].metric("Costo medio dell'energia", f"{lcoe_medio:.0f} €/MWh",
                    f"{lcoe_medio - prezzo_rif:+.0f} vs riferimento")
        r[3].metric("Suolo occupato", f"{suolo_tot:,.0f} ha".replace(",", "."),
                    f"{suolo_tot / 100:.0f} km²")

        c1, c2 = st.columns(2)
        with c1:
            fig = px.bar(mix, x="Tecnologia", y="GWh/anno", color="Tecnologia",
                         text_auto=".0f",
                         color_discrete_sequence=["#FACC15", "#F59E0B", "#FBBF24", "#22C55E"])
            fig.update_layout(showlegend=False, height=320, xaxis_title=None,
                              title="Produzione per tecnologia", **PLOT)
            fig.update_xaxes(tickangle=-20)
            grafico(fig, DOC.F_ELAB)
        with c2:
            fig = px.bar(mix, x="Tecnologia", y="LCOE (€/MWh)", color="Tecnologia",
                         text_auto=".0f",
                         color_discrete_sequence=["#FACC15", "#F59E0B", "#FBBF24", "#22C55E"])
            fig.add_hline(y=prezzo_rif, line_dash="dash", line_color="#111827",
                          annotation_text=f"prezzo di riferimento {prezzo_rif} €/MWh")
            fig.update_layout(showlegend=False, height=320, xaxis_title=None,
                              title="Costo dell'energia per tecnologia", **PLOT)
            fig.update_xaxes(tickangle=-20)
            grafico(fig, DOC.F_ELAB)

        st.markdown("**Il conto del suolo**")
        suolo = mix[["Tecnologia", "Suolo (ha)", "MW"]].copy()
        suolo["Su superfici già costruite"] = suolo["Suolo (ha)"] == 0
        aree_fv_t = D.carica_per("aree_disponibili_fv")
        fig = px.bar(suolo, x="Suolo (ha)", y="Tecnologia", orientation="h", text_auto=".0f",
                     color="Su superfici già costruite",
                     color_discrete_map={True: "#22C55E", False: "#F97316"})
        fig.update_layout(height=280, yaxis_title=None, **PLOT)
        grafico(fig, DOC.F_RSE)

        if not aree_fv_t.empty:
            agri_disp = aree_fv_t["area2netta"].sum() * 100      # km² -> ha
            costruito = aree_fv_t["areacnkm2"].sum() * 100
            st.caption(
                f"Il suolo richiesto è **{suolo_tot:,.0f} ha**, il ".replace(",", ".")
                + f"**{suolo_tot / agri_disp * 100:.1f}%** delle aree agricole disponibili al "
                f"netto dei vincoli ({agri_disp:,.0f} ha) e il ".replace(",", ".")
                + f"**{suolo_tot / costruito * 100:.1f}%** della superficie già impermeabilizzata "
                f"({costruito:,.0f} ha). ".replace(",", ".")
                + "Spostare quote verso capannoni e tetti azzera il consumo di suolo ma alza "
                "il costo dell'energia: è il vero scambio di questa scheda."
            )

        st.dataframe(mix.round(1), hide_index=True, width="stretch")

        st.info(
            f"Con questo mix il FVG coprirebbe il **{copertura}%** di una domanda di "
            f"{domanda_2045:,.0f} GWh, importando ancora circa ".replace(",", ".")
            + f"**{import_res:,.0f} GWh**. ".replace(",", ".")
            + f"L'investimento è di **{inv_tot / 1000:.1f} miliardi**, spalmato su vent'anni "
            f"fa circa {inv_tot / 20:.0f} milioni l'anno. "
            f"Il costo medio dell'energia prodotta è **{lcoe_medio:.0f} €/MWh** contro un "
            f"prezzo di riferimento di {prezzo_rif}: "
            + ("**sotto** il mercato, quindi l'autoproduzione conviene anche senza incentivo."
               if lcoe_medio < prezzo_rif else
               "**sopra** il mercato, quindi servirebbe un contratto per differenza o un "
               "incentivo per colmare il divario.")
        )

    st.warning(
        "**Cosa questo modello non fa.** Non considera l'intermittenza: coprire il 60% della "
        "domanda su base annua non significa coprirla ora per ora, e la quota di accumulo "
        "necessaria non è nel conto. Non include i costi di rete, che nel FVG sono il collo "
        "di bottiglia vero. Non tiene conto della curva di apprendimento sui costi né "
        "dell'inflazione. E il LCOE non è il prezzo pagato: un contratto per differenza "
        "sposta il rischio, non il costo. Serve a confrontare ordini di grandezza tra "
        "opzioni, non a valutare un investimento."
    )

# ---- Eolico: perché in FVG non c'è, e cosa cambierebbe
with tabs[14]:
    st.divider()
    st.subheader("La casella vuota: l'eolico")
    st.caption(
        "In FVG risultano 4 impianti eolici con potenza non rilevabile nelle statistiche "
        "Terna, e produzione nulla su tutta la serie. È l'unica regione del Nord con questa "
        "situazione, e pesa sul resto del ragionamento."
    )

    e1, e2, e3, e4 = st.columns(4)
    e1.metric("Impianti eolici in FVG", DOC.IMPIANTI_EOLICI_FVG, "potenza non rilevabile")
    e2.metric("Produzione eolica", "0 GWh")
    e3.metric("Deficit elettrico 2024", f"{DOC.DEFICIT_ELETTRICO_2024:,.0f} GWh".replace(",", "."),
              f"{DOC.DEFICIT_ELETTRICO_2024 / DOC.RICHIESTA_ELETTRICA_2024 * 100:.0f}% della richiesta")
    e4.metric("Richiesta 2024", f"{DOC.RICHIESTA_ELETTRICA_2024:,.0f} GWh".replace(",", "."))

    st.markdown("**Perché l'eolico cambierebbe il conto: il suolo**")
    energia_rif = st.slider("Energia annua da produrre (GWh)", 50, 2000, 500, 50,
                            key="suolo_eol")
    mw_eol = energia_rif * 1000 / DOC.ORE_EQUIVALENTI["Eolico onshore"]
    mw_pv = energia_rif * 1000 / DOC.ORE_EQUIVALENTI["Fotovoltaico utility scale"]
    ha_eol = mw_eol * DOC.SUOLO_HA_MW["Eolico onshore"]
    ha_eol_serv = mw_eol * DOC.EOLICO_SERVITU_HA_MW
    ha_pv = mw_pv * DOC.SUOLO_HA_MW["Fotovoltaico utility scale"]

    conf_suolo = pd.DataFrame([
        {"Opzione": "Eolico, suolo sottratto (plinti e piazzole)", "Ettari": ha_eol},
        {"Opzione": "Eolico, servitù di sorvolo", "Ettari": ha_eol_serv},
        {"Opzione": "Fotovoltaico a terra", "Ettari": ha_pv},
    ])
    fig = px.bar(conf_suolo, x="Ettari", y="Opzione", orientation="h", text_auto=".1f",
                 color="Opzione",
                 color_discrete_sequence=["#22C55E", "#86EFAC", "#FACC15"])
    fig.update_layout(showlegend=False, height=260, yaxis_title=None, **PLOT)
    grafico(fig, DOC.F_ELAB)

    s1, s2, s3 = st.columns(3)
    s1.metric("Potenza eolica", f"{mw_eol:,.0f} MW".replace(",", "."))
    s2.metric("Potenza fotovoltaica equivalente", f"{mw_pv:,.0f} MW".replace(",", "."))
    s3.metric("Suolo risparmiato", f"{ha_pv / max(ha_eol, 0.01):.0f}×",
              "a parità di energia")

    st.info(
        "A parità di energia prodotta, l'eolico sottrae al suolo una frazione minima di "
        "quello che serve al fotovoltaico a terra: contano solo plinti e piazzole, mentre "
        "la servitù di sorvolo resta terreno coltivabile. Ma il vantaggio più rilevante è un "
        "altro: **l'eolico produce d'inverno e di notte**, quando il fotovoltaico non c'è. "
        "In una regione che importa il 34% dell'elettricità e ha il picco di domanda nelle "
        "ore serali d'inverno, quella complementarità vale più del risparmio di suolo.\n\n"
        "Il costo è la visibilità: gli aerogeneratori si vedono da lontano, e i siti ventosi "
        "in FVG sono sui crinali alpini e prealpini, cioè in aree di pregio paesaggistico."
    )

    st.warning(
        "**Qui manca il dato decisivo e non l'ho voluto inventare.** Per dire se in FVG "
        "l'eolico sia possibile servono le mappe di ventosità e di producibilità specifica "
        "dell'**Atlante Eolico RSE** (atlanteeolico.rse-web.it), alle quote di 75, 100 e 125 m, "
        "incrociate con i vincoli. È lo stesso portale da cui provengono gli altri dati RSE "
        "già in questa app. Le 2.200 ore equivalenti usate qui sopra sono un valore di "
        "letteratura per un sito di crinale a 5,5 m/s su 100 metri: plausibile per le Prealpi "
        "Giulie e Carniche, ma da verificare sito per sito, non un dato regionale misurato."
    )

# ---- Eolico misurato: l'Atlante RSE (scheda Transizione)
with tabs[14]:
    st.divider()
    st.subheader("Quanto vento c'è davvero in Friuli-Venezia Giulia")
    st.caption(
        "Punti campionati sull'Atlante Eolico RSE a 100 metri sul livello del terreno. "
        "La producibilità specifica è espressa in ore equivalenti annue: quante ore "
        "all'anno un aerogeneratore lavorerebbe a piena potenza in quel punto."
    )

    eol = pd.DataFrame(DOC.EOLICO_PUNTI)
    e1, e2, e3, e4 = st.columns(4)
    best = eol.loc[eol["prod_100"].idxmax()]
    e1.metric("Sito migliore", best["nome"], f"{best['prod_100']:,.0f} h/anno".replace(",", "."))
    e2.metric("Velocità del vento", f"{best['vento_100']:.1f} m/s", "a 100 m")
    e3.metric("Densità di potenza", f"{best['dens_100']:.0f} W/m²")
    e4.metric("Siti sopra 2.000 h", f"{(eol['prod_100'] > 2000).sum()} su {len(eol)}")

    fig = px.bar(eol.sort_values("prod_100"), x="prod_100", y="nome", orientation="h",
                 color="prod_100", color_continuous_scale="Viridis", text_auto=".0f",
                 hover_data={"vento_100": ":.1f", "quota": True, "dens_100": ":.0f"},
                 labels={"prod_100": "ore equivalenti annue", "nome": ""})
    fig.add_vline(x=2000, line_dash="dash", line_color="#111827",
                  annotation_text="soglia di convenienza indicativa")
    fig.update_layout(height=380, coloraxis_showscale=False, **PLOT)
    grafico(fig, DOC.FONTE_EOLICO,
            "Le soglie di convenienza dipendono da costi e prezzi, non sono un dato tecnico.")

    c1, c2 = st.columns(2)
    with c1:
        fig = px.scatter(eol, x="vento_100", y="prod_100", size="dens_100", color="quota",
                         hover_name="nome", color_continuous_scale="Earth",
                         labels={"vento_100": "velocità media a 100 m (m/s)",
                                 "prod_100": "ore equivalenti", "quota": "quota (m)"})
        fig.update_layout(height=340, title="Vento, quota e resa", **PLOT)
        grafico(fig, DOC.FONTE_EOLICO)
    with c2:
        mappa_eol = eol.copy()
        fig = px.scatter_map(mappa_eol, lat="lat", lon="lon", size="prod_100",
                             color="prod_100", color_continuous_scale="Viridis",
                             hover_name="nome",
                             hover_data={"vento_100": ":.1f", "quota": True,
                                         "lat": False, "lon": False},
                             size_max=28, zoom=6.9, center={"lat": 46.05, "lon": 13.3},
                             map_style="carto-positron")
        fig.update_layout(height=340, margin=dict(t=30, b=10, l=0, r=0),
                          coloraxis_showscale=False, title="Dove sta il vento")
        grafico(fig, DOC.FONTE_EOLICO)

    st.success(
        f"**Il vento in FVG c'è, ma non dove ce lo si aspetta.** Il punto migliore non è "
        f"in montagna: è il **Carso triestino**, a quota zero, con **{best['prod_100']:,.0f} ore "
        "equivalenti".replace(",", ".")
        + f" e {best['vento_100']:.1f} m/s a 100 metri — è la bora. "
        "Subito dopo vengono i **Colli Orientali** con circa 2.950-2.990 ore. "
        "Le creste alpine, a 1.300 e 1.900 metri, rendono **meno** del Carso: "
        "circa 2.030-2.100 ore.\n\n"
        "Per confronto, il fotovoltaico regionale sta intorno alle 1.040-1.200 ore. "
        "Un aerogeneratore sul Carso produrrebbe quasi **tre volte** le ore di un impianto "
        "solare, e le produrrebbe soprattutto d'inverno e di notte."
    )
    st.warning(
        "**Attenzione a cosa dicono e cosa non dicono questi numeri.** Sono otto punti "
        "campionati, non una mappa continua: servono a dire dove vale la pena guardare, "
        "non a progettare un impianto. E producibilità tecnica non significa fattibilità: "
        "il Carso e i Colli Orientali sono aree di alto pregio paesaggistico e naturalistico, "
        "e la distanza dalla cabina primaria più vicina (da 1,4 a 15,5 km secondo il punto) "
        "pesa sul costo di connessione."
    )

# ---- Centrali termoelettriche (scheda Termo & CO2)
with tabs[9]:
    st.divider()
    st.subheader("Gli impianti termoelettrici della regione")
    cen = pd.DataFrame(DOC.CENTRALI_TERMO)

    t1, t2, t3, t4 = st.columns(4)
    t1.metric("Impianti censiti", len(cen))
    t2.metric("Potenza complessiva", f"{cen['mw'].sum():,.0f} MW".replace(",", "."))
    t3.metric("I due maggiori",
              f"{cen.nlargest(2, 'mw')['mw'].sum() / cen['mw'].sum() * 100:.0f}%",
              "della potenza termoelettrica")
    t4.metric("In dismissione",
              f"{cen[cen['stato'] == 'Dismissione']['mw'].sum():.0f} MW")

    fig = px.scatter_map(
        cen, lat="lat", lon="lon", size="mw", color="combustibile",
        hover_name="nome",
        hover_data={"comune": True, "mw": ":.1f", "tecnologia": True, "stato": True,
                    "lat": False, "lon": False},
        size_max=44, zoom=7.1, center={"lat": 45.95, "lon": 13.3},
        map_style="carto-positron",
        color_discrete_map={"Gas naturale": "#9CA3AF", "Carbone": "#111827",
                            "Rifiuti urbani e speciali": "#A855F7",
                            "Rifiuti speciali": "#C084FC",
                            "Gas naturale e off-gas siderurgico": "#4B5563"})
    fig.update_layout(height=500, margin=dict(t=10, b=10, l=0, r=0),
                      legend=dict(orientation="h", yanchor="bottom", y=1.01, x=0, title=None))
    grafico(fig, DOC.FONTE_CENTRALI,
            "Coordinate al centro del sito, non rilevate sul campo.")

    fig = px.bar(cen.sort_values("mw"), x="mw", y="nome", orientation="h", color="stato",
                 text_auto=".0f", log_x=True,
                 color_discrete_map={"In esercizio": "#2563EB", "Dismissione": "#EF4444"})
    fig.update_layout(height=380, yaxis_title=None, xaxis_title="MW (scala logaritmica)", **PLOT)
    grafico(fig, DOC.FONTE_CENTRALI)

    for r in cen.sort_values("mw", ascending=False).itertuples():
        with st.expander(f"{r.nome} — {r.mw:.0f} MW, {r.comune} ({r.prov})"):
            st.markdown(f"**{r.tecnologia}**, alimentata a {r.combustibile.lower()}. "
                        f"Stato: {r.stato.lower()}.\n\n{r.nota}")

    st.info(
        f"Il parco termoelettrico friulano è **concentratissimo**: Torviscosa e Monfalcone "
        f"insieme fanno {cen.nlargest(2, 'mw')['mw'].sum():.0f} MW su "
        f"{cen['mw'].sum():,.0f} censiti. ".replace(",", ".")
        + "La sola Torviscosa vale il 54% del termoelettrico tradizionale regionale. "
        "Monfalcone, a carbone, dal maggio 2024 non è più abilitata ai mercati: è la ragione "
        "principale del crollo delle emissioni elettriche che si vede nei grafici sopra. "
        f"Il censimento copre {cen['mw'].sum() / 1530.9 * 100:.0f}% della potenza "
        "termoelettrica che Terna registra per la regione: mancano gli autoproduttori minori."
    )
