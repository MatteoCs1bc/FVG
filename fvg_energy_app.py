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
        "H4sIAHvedmoC/22WzY4TQQyE7zxL07L7x9M+hlV4AbivhuwQjdglaGZz4elxFBDpLueaT267quzk"
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
        "H4sIAHvedmoC/42Uz46bMBDG7/sU1p5aya0wCQSO2dW2yqlR2hdwYBKN1nioPUZVn74GirogSnsC"
        "i9/8+77BV0NVRbKjCmSnDTmQ2lqSwSLrh1PTkmP5TM01eMYrGhSeDNYo1U59TGSapEq+MrQTegZ2"
        "ESCpkkOxBsxy3bX35GOyYp+uwS8W3B1BOIw9dbqPkWmZr6EXvGFgFJbsDE9WmxgmFTU47DTTOjQW"
        "1wIMMDustEzzOXhBT86DQMvgLMhT7WiiowJ5uUl/IqaODOseztJN9isZHRuOh2ZIrTbpz0ATudsE"
        "n5CaaAHIIv8XF62SZbZJTRa8lV9tz3U0UStxRboFMMLg99DvVrot85maNpqHohoXtiz/q63lZqj5"
        "fj4F+wpO3+8ojx3qn0h2yjEctIGFmn3zJB+Hh3jnq7g0IEXwYylt4q+lGd8/ylTNhftGrGMD454J"
        "7k8xd54c1qiXH2+pZA1ZTDyxWb5a9pmsDw39pklEDeu4KGW2KO+0v5FrRiXkybaB+6G04PmXeBPs"
        "tiK/BO5Da1iJXf73i9AzuBp58HoRuD+orcBjYKqGOVGAaP+kcRA9Koq/64LihtHr0UPorwBgrFDu"
        "y616F7A1NmCHuyTfq/RQZirN8jy+78awDw+/AIVMnrNsBQAA",
    "bio_impianti_dieta":
        "H4sIAHvedmoC/22SP28bMQzFd38KwpMNyLFj1B06FHASJ8iQ1I2RdCxone5KwBIP+uPhhn72PjlO"
        "0gJdBB2PfPzxUeJ74ZDVWPUlONNHPUqwwiZLrwftcOs1uzDwz4cfzjTiMpuUGSUBcdNqwMltKw3v"
        "5SCZR98LN7EcpXiaXGsTFUpT83YzzzdmL+qhE9QY7qJYNPpCnjOuQueII0eNULIc0UsCueSilUEU"
        "kOKV5IxOty93xPiEZHbREXKjy6fqRhJE9wVVGG4TZL62ruO07tPad2y8a4RH21hH7ms6bRVNGL2v"
        "YumCi2zWwwBSunEWXc328X/0//K9J1ADfQuvwHcXS98rXWuwGhtHEwtxj7/TaqfvmZaL5ecz0ept"
        "OqH7zY6uRAE93wX2sA9w20eaLCkVWk0RmL9CIWX29QPu8mJhxtG1hyI0KHZlA+w1r46+24wAzlzg"
        "21Ipsq1fOsZ7CEcX08m336vFgnbezn8RvEm2hDpQdJ14ZyrUp004StTgXcjnCYDsOZgHidWHyctm"
        "SjMS7Keuy8z+NvH229PuGUO1kU97IjRuTk+xw0bVjC8vKkCedxSllZLB/GFxD0kuWfO5emx292t6"
        "AlyVqs32nBKP/gDnXvJN6gIAAA==",
    "bioenergie_comuni":
        "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"
        "EKQhVR4UxDX+D5LFs4QOLgAA",
    "biomassa_comuni_2015":
        "H4sIAHvedmoC/31XyW4cNxC96yvmlgshkCyuR1mIjQC2I1iKDrkY1Kg9ZtLTLfQsAfT1eUX2MtLI"
        "6tE01MR0sZZXrx7X/fbQNaLtO9Gmvcjbp5y6fRb//ie2abdL3/fi2LeHbfN9S2Ldbx8Ou31+yG1z"
        "cbV9ap6fe6H0pbfSRB+0k8FFG4Rxl0YGW56c1coLLazXQmsltPfiOj89pX1/cTXs0+quGbaNUHQp"
        "rfHkIylJxgQqVnzU0VmrvDbKCKxp64XVOgpnyZ0aajZdYivKRKfifLEVvGtJKEFGaBiR4jP/eJVW"
        "69yv1z/zxYfDY58TRwKfo5FOW8mX4relU8aS0hZBBGeFjVp4I+e9Pxz2+yH3vDeRsfxDfktppYK3"
        "2FZ5KbBI6mzf67R96pH6Tb+6S0/9pkXuiyEjydNyCWMvkcs4+QXHlMBOgjjZJsy+XKeuOZZAjJM+"
        "emV0sHxnCzFSGB9x55IgJBQlvOHX05CPafXYtKuPQz60mZ2yMmpN0rtY7sWkiWZZcRyskgIVju7E"
        "p92+abv+2L+wpy9DRKKjJK1tkK5kTcsYLGofvIzOG64ZcgfQuHMfm2Gdj023LwgE+uCD1dEoxY7A"
        "lqWoypPx0sZ3Tf3Mh1360QNEpYpGE41YBsoKDhWKKQ0ZBjlsoJ6orAOepF0Czcf8mNrmVdoMzDkz"
        "XcWcDIbIzhdwDd8RhhbK6sVemw7PzX4MEIiIr2CNcOcCRxhRWooQhJLxPMR+2xR47Urmg5a65AX/"
        "ka3ZknFeoMkYKoAAXxv7vWu2fVdbP7jguF21t8HpmiunXJi6FikSWCeGy5mhj2kYgLLf/thVc8AY"
        "IdWWgnF8twVjgN20YJwtyHcwiOY8SdbHfujy6gpchWYsnAS009wAJe02RoV+EcSoR1chfa/ef8yr"
        "2/5pqFTgImk7WyihaWXmBoIT6B8JVOGZu9y7t6yN9XMmRO+RE6kluJGtUUS0WI0WbhkYU5bz7ZEH"
        "c5aqT5zy1x2pbLWkgwE+ZrZ4B+qf+iE/50KUFh0TnJqusZ1jkAsuYSIiRGavM0ND3qb1uhTNSR1K"
        "6ZUjf5JyxS+6wDCaEvM5HdYVz0wYE3hDaVhjIkbFlF/uCrJIbkShzFLoL+mfkSSlA7/K6SpcrQIh"
        "gJGPfE0EyOjM+y+pfeiHzU/urtU9HoZDnR6GMD+AZ+0wY2yxCZ4NMijwkVaEoiPjCAjtC+Y1J24N"
        "+4xNxpQoW8egDD5KWx1BjhWdu9JvNrlf/fWYu2ZX+EcjGKDJIHJwYe0pZ2heeZcWv/Tdj9Su+66Y"
        "sgYAnYaw4RJjoPppgSorsil8HS3B9EMa6iCK0Zb38BoPHQyLt/HwNW/zrniPItqXfacxgN1S6hPv"
        "pw3/PJb9QCcWw91i3ILZQqzcG6X2wWsyEtMf5XTICUokmPQmAzepPTw/l76NUaoAUqofX0rogBU1"
        "fjC9BQXgGvRNtDDATd/tm4eHAgPiqbR0+ggDHT2khTS4MzpZBLwcdTcYcm1lbE4Eer7MsVK4Ak/8"
        "My/YkglgQ74Fi5sBBlfXCTyyHjWWAk+46aouYVzOHewECIk7yYAh7aJPboZmm4Y8IZMC2i5qJJFv"
        "hdakgVIhyJRys1UpoXPPnTq0P5oRGN5LYxw6A164Yga9G0rVHKzoYiWUMaJOvPmWNn1RaihUcE7G"
        "6VP7F6mxy0fUSMogCOrExjHt1u08GjVm80sesGAOpyZx8V6/wFYzIg9EjEEjy73yEZyf1xwPMo4T"
        "SlbcNC22v/iWNz1U8/g+wfeyOXwOMzHZSoMYPJg6Z7v3W4zkFxPQnGgPVs4s/aKL8xJGl0BXFm4E"
        "KUyu3KY1RHmVsJhEhB6EkvUcCZrXgrkCppS03ObFoch89Nqf29StPmUwYy5irU2rbxnr3bFpH0vN"
        "IM30aIZ3qOgJy37MTR6MwqxCftFGo+Fj6jAXU7v6mvZ5N5KUUQS2na4idqNDo0Ecjn8wamCQv8jr"
        "C6OfG4zF4XEUD0wTJ6oZgEL/njTNLwfCbToyLF9qEYd+n7NWRTg0K2e1Lr8g4qkOm752LF166Kky"
        "VvF7WqQbA0kR1LdkYTTHUvxojqWEQYJrZqkdR7FgWUuBc8DBdA7k2/0wHYEwj3Whd0XQrDUPmFcL"
        "rFhrcKm4S09cP9RzDDoKMrAgGSrROj7QAPo8BpD/kzFxl4Zj3tWjDyS8Xaaxqoc3rT2yrQkHIEgD"
        "lhInZ5W7vt3WAyRGORm3kJuvWisoCuNVBpX+xWnlbsjNrkp3VlhRoxMJGorKqQcK3kzPgYUtUMsZ"
        "PB9h983wjKVcJDIOkWE610Rd+A397WdxahCYBX1qnohhGQH3mbvmls/QI8tRSR2fiOEdMqlwflQK"
        "EZlzGN5nkP7jb1e7sQ7k62lS+6jmU+msJ9DJ5zj4+wCdX98OqOOrc4wDouelKs0xo+253vwfxXVo"
        "qRgQAAA=",
    "biomassa_impianti_2015":
        "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",
    "biomassa_province":
        "H4sIAHvedmoC/4WQQWrDMBBF9zlFDiAGzWg0I2+76bJduAdwHZGKGivYJoWevuO4gUIK1kJIoP/0"
        "5819HrupVHeZ6rWMfencUscxD0O3ZHf++nCfS74cnurcf5Rj1/d5nst7Gew8HC9THkq+Vvdap1Me"
        "65idBEwevCNkSEgOE7B68U0if1u8x3quU/m2GpxkBaFAJHYITD6hIG8Yj3uct1OxPiiWXjlR0AqJ"
        "YSF4VU4qe4R2Knk2C0rNbSQGTeIIMCAR026D9qW1kI+6phMqNCE5u4TgQ5OacGjr0g35OOVzqaOd"
        "/ngkc+bXnNrOzlQQhdTwY+buC2O8CYsEjWfHEDk10fNdWHyMbopi4O0rTBhBDCSAyEHkMXFXQuG3"
        "XQJyAmpjkv7z3Ayopq0YCSugVSNSEEQKynz4AbhMiB+BAgAA",
    "biometano_pipeline":
        "H4sIAHvedmoC/x2PsW7DMAxEd36FfqVpkCkBUtvN0O0iEc4BsmhItgd/fWkvJHHEke+iTWtR+dp3"
        "FAtXjZxMLmjMdEEuazJCvi1V42xyy+D7WNyxsKFA7toWulseKMRo8tCkkCfGghjNh4x9t2whafba"
        "L96O/UaExPCb6P+fFtXt0umEsp/Gjhv9hlMNalU6K/HDJt2aID1KuPo/zXqcDbfKNfOUf1ZWOuAx"
        "v7hYQA4DRo8zaVlcd95T7HT8qAfoZ886vbU6+2B1Y4vWIC9uqCZ/Ns/mvP9sADfZKAEAAA==",
    "bosco":
        "H4sIAHvedmoC/3WQvW7DIBSF9z4FypRI1Lpw+R0zeXMX7xZ1aYKEQ2WTPn+BdrASdTkS3PNxzmV2"
        "2V/SGhzdwiUWvX/59TPMwU9XR79TvC9+WvxHSNOCu6ucsotlgi+HId3IxW855ETJrRzcPPttC+8h"
        "+gMdevJKhjNVChh2QDnjRRlya5VlHTzwz+yZMhBGiEqZ9gJX0iqmCrtDyfG30qlQlGkwUlcvQFGU"
        "VloEXdP6f5v+FbVoQFVUNAUlgdfcHfqElfU4B1P92NazwLUWleof65V2svyFaGZb21mlTfEX89g8"
        "5LiG2cU5RZfTiY5vI0WujGYNYR1aw5jgArRRDKmWCjViDfsBveRVws4BAAA=",
    "centrali_idro":
        "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",
    "centrali_idro_catasto":
        "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"
        "AV+10reJ0mapgC8cXpj9P5RwXWvbwAAA",
    "consumi_finali_2021":
        "H4sIAHvedmoC/42UQW7DIBBF9zkFB0AVxqZJlpHVRXdV1QtMYmqNSsACzPlLWre0ERivkOz3Rw/8"
        "MWhtaJDeGyupW9YA6rbMGj3sOOMN7c31PDuPZ1RInFE4ID2NFi9G+dkCkWSS7gKUPTD64eVUTvUY"
        "UMkN4LMe4iOLQPmxCr9ZcJOxHu8Gv0hvI2Gyso88zy6KDevy75PZYZ8nko4QK/IjOGdc/iSbemzx"
        "FILV2eQsGK/jaQP8/yE8aWlHlMRiLE6AW2iDfi612Lcdq6JJfl+fW1R/xXecPRJtdFWfbUpmu1yC"
        "0ybaTXyp0v3X5SSDtBjAmy3X8C7x0+9mlUq+DWtXyZLp99eJVir+V6Ik5JvCK6FFlx9q4J+Ot8cK"
        "m5y737GfM88a7gwFAAA=",
    "demografia_scenari":
        "H4sIAHvedmoC/y3MOwrAIBBF0T5rGcJ8HHFWIxYpBKMSSJPVZwyp3uUUr/Q+YI45Wnnq6AfM2vLZ"
        "ej7uKzOSboxMQCsJdwSJwXydBYEooZEtTpbCx2GxWmJ1DkzyszqL+M9iZY3OL4kTO1p+AAAA",
    "dighe_fvg":
        "H4sIAHvedmoC/42TTW7cMAyF9z7F7LoRDEoUSWmZToEiQJAGSdtFNwNlxg1U+CdwPLOY0/QuvVgp"
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
        "H4sIAHvedmoC/42MMQ7CMBAE+7yCBxyRiaLAC+AHtNZhr+Ckw4dOjou8HkNBTbe7mp3GLnwTBaFK"
        "eqBWju23qTSoGrGDqbGag7gU69mjZEqWo+M+vKyibBwr/GnQbnFJHF06276q2L+Z6W+wW8UK6Oyy"
        "quyvKNiEd5dPYzrMYVxoCtNMxxMtYxjenBpBvMgAAAA=",
    "idro_comuni":
        "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"
        "1j64KwAA",
    "idro_montagna":
        "H4sIAHvedmoC/6WTW0/jMBCF3/kVfgRpCLn28lgCRSttVxUgeIymqRtGiu2sY1er/PqdlBaBUpWt"
        "9ilybJ/vzMwxqYZQOwOlUV5LQLWi3cq2psDyt0eoZOuMldAYJ3WHxeIVGmvWvqQV1eSweHh9K1Br"
        "A44aU9BB0Xm7Io3QYu1MoaA/UshW2pI6MrAx2jFvs6E1vgtdPBnV1FgZyHGLXWdEjlZT2a/5izBj"
        "c2wGxY1Qck1GPGNVEyrZ42bxDKJxHEwgzcIgBAat0BkyNw3LYlWRuV5LxcZrZD7XOreoS2pF8ifL"
        "xOJVYNtKsZXWBZCEGUvA8v5RzF8exCUXXEnnzBVwMXgxU41kf3D47v399Ioksbu+4oG5URxEEH31"
        "JrgaNqaxlrCUfEuzmzj8cGMsdV0A6SQ8Zedeb6zkGbWwxNp3HR4M3XoHT/f57BbiIJskEEVBBrup"
        "ik3tZT8AgGiaTVl9wb2xhGJ3foD4ZQgttfDknSVzVH88gil3/6v8vseMOa2/8K3kY3mfju2uZQNE"
        "xOLjIB74/06ZZE3iWqylpW0g7mSFHNXcKNmPR7cH0H7jncWg6fFKbt7HdC72pQ8DP4Yh97CzB484"
        "JP8FnvO74kI43/swiMtnUuivhh0Ng2TCbR0fiUSUfBuJRyxLU6NGEUH+Rr7FjbF8PedfNdddi7m0"
        "1sDHOfjxMGdcyjUeS+FkxEiW8Eos96Q7qt4krPgpfMbFZ+EiyI7jJv+IS87AhcEIkqO4aXoS9wkh"
        "0vOAaQTp4N1B3A/wBPAvfpMIJ/kFAAA=",
    "inversioni_flusso":
        "H4sIAHvedmoC/5WVu3LbMBBF+3yFujQYjSVLlFz6EatJbEaUGzeeNYlQOwNiOQDIQl8f6GGKcYiF"
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
        "H4sIAHvedmoC/42RTWrDMBCF9z2FodtBeCTrxwcIJYtCoIWsVVtJB2wpCDkLn6Z36cUq27gNIQld"
        "aCQxb0bzPSXX+NCFI1k4RutbN44WBk/JwimGdkgpRAI7pHBxPZyPYL0PT9s2Bte5lCI1Abb9iaxP"
        "BM/AVclKMHlxNceSiyv1LiTnR1u4w4Eacj65oguxtfC6B8kFUyAZzyfD9D/Lfc4t5aiZXCPnudWt"
        "BhNPQx/UUfr+KnrXki0y1WDhZf8JaBBZ/beJkpmlzbuL/W1q1DyzLpFX1cp9VfDmRgp+dqmclHWd"
        "gyjxjvyRTyi1msZa3jWVuTPjI7NQinlSJbLRqGu9+r0J3RXfpINfrN35Mpe7cJlTusZpGIVC6Avl"
        "IwqtFBOAKPN3GYMrww+AYRR3mwIAAA==",
    "prelievi_fasce_fvg":
        "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"
        "EuiEvf/bg0Iv+FbTs6l9rmTw/T/Eye0vaKYAAA==",
    "prelievi_orari_fvg":
        "H4sIAHvedmoC/6y9S692O7Kl1edXpKqdQq/vdhOEVJ0qkACJ5lFStatI1alMlCcREr+ePOzPQ+y9"
        "4jKG16clrdYcMT3teJ/wJWz/h3/+07/8yy9//K+//Msv//SXP/71b3/6x///+svf/sOf/v7XP/7t"
        "l3/583/85S//z5/++Pc//59//af//Oe//u0vf/3jf/m//4//5t/8pz//5a9/+NMfyh/HH/7L//Zv"
        "/lj+8ffvf1X94d/9+X//5W9//eP//Kv477/88d/+f7p/+k+//O3Pf/rnX/74+W8/c0zDRFVMjL0N"
        "E00y0Q0LXbIwh2FiaN9xDBNTqs2PVRVLMbFqNUxsxcQpzTBxFBN7WXVRPpKNajVJkdxz7WLZkPxz"
        "f8xvaZoNq1WK5KJrmfUh+ehcZn1oTrrNb9G81LbxE9y0KH5aPsMqR1X8tJRh/WhrkWwUE6OSn55q"
        "2tD81DQhumnRgsr/8t/997+65tAiydXtpoWPq2tazPghG/NogeK+7jO16HB142gh4YdurabFgR+6"
        "Ywb0k+r2qSLxr9DGa+4wy/T3knvMFnF+ZbWJDIdQ5Pb9wE8TYX2F7YiEviUtW8Ty9Rqz71NStymf"
        "ekQA/xAW8/dUSy40m7HmbnN6F/mKn6JKVQiPhtL/4X/6936vp+a6z9BQ+kM3z9FYenXmL2PkuqGh"
        "9Mp601CKz+saSn/o9qdrKL26tUSUQiiS9OrsnnZ9/MKSe8w+Kkuv0EZb7jOrLBGm+DGJLL0lnSJK"
        "f+hOU1H6q7B8WhNReoXmz7emfvMPBlcRpfcbZxVRehtjVRGlQM1kUPo//vUvf4g6t6Uuhqy5GWrK"
        "IzczGO7mZigMp2ZKZ7Ccl4aB9FvVbNkMNROSWumFAnpqxxytFt2LB9dzzu1wMyO5HS4a5HY6FRwe"
        "63n+JDu6M0+uW57aIXvpqZ3DRZrcDhV38s/ievRv1Vx1d+6bClI5fIYes34MHWxt5bS96dEJ7+16"
        "SLpaMyoOTluOHnzw3oeQg+/VwwyquerB5WptYn448XyIIle7HiIHtPMhXKDQLzEC4v0QGFDX5yEa"
        "4M3lIQSgwtoD96/4rAfY/xDXz3ogPMTlgeso9gPLr3aPB4CHLVVJB+tHR/WPoUnpD2OKqx1FRzXe"
        "O3VUX207Oqqv1hxDTVK7dVSjzEVnNbQPAwHU8wur0cAPrIZ2P8D6imd/gDXeXB9gHRebdK7+0nUP"
        "K5v0rvWA6qu1107ON8SVdC+bmOU7Yta/XjrbaOWXHnbsIr/X/q//19///mejV16puXVX/aGA7ckL"
        "NdHuq6mJHlfOJbj4b18Mu/16Pwy+XfmgJuN9OTcn7+u5VU6t+IX3O3PGtTT+/ZMiuq/nFkFdvTmu"
        "LJPXT4rtfv0Niu+evn24ZBVXT66TunqzE1Jp/2tm56ny/rc53Pv1TwFfbH5bfocxlQc9JIen+9WY"
        "E9491JRzeJBDM3l6h8PAFWta4zl9NWbO0Ek0ApCvxp5ESPzARnfiCasLvEXxlgDZsB5iX6h9CDRF"
        "PVQBoXE9xO7QahVgeUVtC4S8IgmL8Ztih2ifIQAwdL2aOAQ3F/Gr5kefuHJzEL/VNAF20DQedldT"
        "Ow+7qyk8667kc3jWoWg86lADm0fd1YwjsO6KJNbFosQR7L5R4glmHmVJXGFOAXahz5XEG4bAuqux"
        "07VifzD7VSX2h2aWrsb+0BTShZrEG+zFwfbCnwwMywbdn/7zv25w+cM/Hv7ln/8UJis3MzxVyURz"
        "VssEE8WhomDi46ydCSbMeZGpmOg2QQUDy5mj5U2MM2zA8iam/ev/SDbs1DjJO4edOSy55yzewF+p"
        "DwfVwqfYuwKG9ine5pXvfsrSTHiZfbyNZSehS166mjfx+20bkpdOc2qmal768YKG4GLmL65Kbtpb"
        "1ULK7d2vqsWRqytbCx4YIXUtYmDocrQwAV3TYgPqZWsh4Yeu96PFAezO0dh/N9n0JQL/CksVKX8L"
        "upeIdgi3yHPskxoixa9wVhHdqNUt8hp7nlRKYw9ZFdF8haeJPL5bNOyNe7nn2BGgFqJypojb6zln"
        "ioy9P8azRbBe4dRgekcdZ2gwvbouwhQ6jaUYuYldbgyqhsbSH7qudq+vzkx936lujKbB9KbalyPC"
        "FNt6lgjTuytARCn29Ygkva/rKknvC9sWSXqFtYkkvW14pkjS+8ZPE0l6K8edu30S1txtlptGnDaH"
        "StJbq1vtrV6hvfewE79hhqRZQvFnTQasqRlzFq7pZgrD3dwMQ+EnK1O24m3WVguzGWKnZjY1E5J7"
        "Dcfz3A6H9zcvLvUnfZfux4sLB7mdTkWHx+/SnXkXKnY82nlwZyqwpGYOFWbSzRn2bIPszYUKQflH"
        "cX37t8rRXXl3PV79GDR8uCl5W2suoDdS2/VwBG3VgxC0RQ890OrhBtKhx5ir3VUPLNC2h2hyxac+"
        "hJD4zaRn2RAjXeuchwhx83Y+5SEsYFvUQyjAi/cD//HJ6wH6eHN7QD0+uT0AHlvBHqAe1XWt5BfX"
        "B36jrh+gDb9+IPWPQYndxpXU6qC+0l11UF+t2QcdpHbooIb2gdTQHp3UYV0dsonqA6lvkv3npbMP"
        "8XggNcTzgdT45hdS483tgdQQ9wdUx9/M+Vcp9QHVEL/0yiHuD6iG+DywGuIXWKO2X2Adeljt79T8"
        "8sXuBowPxWtP/jGPQWq03Fzx6rx8MOT2C8+w21cPBt9uxVNJLa7ayxhk5ZPCuK/n+tyuvh4K5v77"
        "B8VzsfydL/+kqO6/nwO7r18U2zX3Kbz72at4vP+NTUHe1U+O8/77uVl+//sPRXu//rk5f9//Cg99"
        "DCcGT/pwbN0STeGZHo1WRizZAr3xms4jO6y2HWta5emM0wKKgGSIlsBhlG4J8IWoCcQNDxXpiaYI"
        "aIVoCDyFqAsQxcEfCjnxJgWX4ckoNXGIXQUwhieh1MQhRhMQCC8qAvcw/9J52IVnQtRYUxYPO3T7"
        "Nw+7cEg4Ek3laYfv4WGHaqs87MIjNE6ssdeuP7FoDgF2ECmwi0WJK0yFdum5FrpovogSf5hNoB2O"
        "gCgC7XBUxhJoF76plod2qolHjCrQLjzkpfaHn1P58VCY61zsoXyu7NPu5hHKavOPUDY7U44prX1W"
        "EFFDztoYoTx29kWuXE76MaPsNiQJqXdEUC6d3ooY81ZnPYyROgNyosBeigQh7c5SGCEdTiIE8a0f"
        "59iIXLqLg1ZCepx51Vx67I14jDft5XQtiWqaTvrCqw9XypvsKfcvyps/be+6dB//NAq0N1d6HYqu"
        "9/ExKKTCeqE4esteDgVP7IJoFDFv6jtHSVyCUDg0IiO/cDxEPv3mIIitAoMj3y2PjXa3ZVcvHOOw"
        "52FyYEP5J0czlGdyCLt3iPTGces+vxoHq3sNx+dwhAovpqnV97fKsQj3CB0OQPf5ynX6kMFNQQcJ"
        "xpuCDh4vFHTu459KQecmLZ9OQQeFGRR0UDGFgg4uAKCggxT/w0HnPj/JThie7xx0UJ7NQedePlEO"
        "B51r37tWw6vNxTEHlX845qA4jWMObgWpHHNwUcrhmHPvqyiFYw7sF445uNaic8zBTTYkc7BhIerp"
        "5EmhUcfnKaW0seI9AkDl6hbw6i1veX7r3es7lbZJsT2BeGh1i9CXy2dEwly+IjDmd5BEmMxfPiJq"
        "PsrH9z590vIdMTavuXCk+naHTKGdLuwD5upw0JrLW0Tr/NNDeOcVXyOWPzqdqQ5zc2ssmTTFw/Xk"
        "Hkr2pnkdJnVPXbLibyk0j7GWPGkIh8nan1hyeNpCIyAWms2DFWt5jacpNItHaHhtSJmx5vCwjN8T"
        "e0HnqRheJVBjNxg8/8IchBp7QRNIF3pbjb3AyXO0JFgAnTTTwuzTFko+k2YaJIVmGrI8B800SCbN"
        "tDARdcffwncs4+TiT6ipnYcaNJOHGjSHh1qYdVz6w/eMh/fM+D2NhxqWIIVuX3hhSYn9oHeearEm"
        "9oPOUy3OH0ncYPNUi3I07seI2YeZqq0AbX6mYbTAq+X3jrSEAeK0VOaVqUYPQOdfdjAC1vmqcB3X"
        "l7WIeK5snQh6/ttmxD1fFq7b+oUMu3S+bEQAFN+W+sg+EQb92zxOREJXVmcEQ/8Q+3DlQ3xbTb9t"
        "RFjUfgE19RJ7Rvk3KnR2S4rEMGe2mY+2k8IvzI8d9qMl5VxYgGXXwEqJhiTRnWIMFwS0nF3xs3Z7"
        "7ZVTCnZLjiZcTtByHuHZkUMovjjPbLSawwYl6Dlhwmskitlq1R7HfexnZw4QXONAUANXWBCogDcQ"
        "fEBadE+hgJzCmUIhzC1t5qMj7xGFN/EN89E+UyhEN5It+6tKygTUVd61iW8m+1jPOr+xYj87cybE"
        "zzb72Z0zAc/WnAnIPj05E1BnI6dCdE9BMVvNOcb+2M+uHAo4er3kUIDdmkMhbIpq/84YKPgX7dWv"
        "t1uESaWmiaqYaIY/1K93X8RHz1fDRNdMdMPEkOriY5mYUimMmF2/XpwRlsLIZqtfL9KIDxi3TBzN"
        "hNUiX6/ZiA8HtyqjSP45htUmRXLQUS0HLZKHjmbWh+Siw0hcqcaNHXGyu1kfU7NhfsvSvsVysSK5"
        "6TSCWTXu+4izoK22rZKfWhm31bgOJCzHseqjSn46i1kOzU+HyXPJT7sJsaA6bmJtnVosuQejn6kF"
        "kKubXYsa0FUtVOCg+aPFh1svn6oFBRz83rRIgDOqm4b/m435KSLzkTa8RNAH53fHdEfiaBeRjm9s"
        "IsdvGvgoIrwhrCKxcbq9SGnUzRHRHJwYH/MYOe9ThDDav4vkRaJxFXEbtn9tj+1fCcfRWHrzhZvI"
        "UpwXvzWWXt0uGkuvzoydI9cNkaV4n9jBvvVp/gp3qhulaCxFRnYTWYqD35vIUuS1iii9OvtXn7vM"
        "FEEaljP3GDtUTOJ9ReQoDpovIkeRkaxyFKe3F5GjV/jZIkf93PUYo3CaI2IU2ya2iNH7A56NAWme"
        "YXgYruZ5joXB7EuiqUHd3ExjIPySPmkw+a00S69iiti5mckAPDXTO8Xz1A7ZVU7tmGOYUn+SHd2T"
        "BxUN8moeVHTI7WwqWuTVwwWP1M7iYklq51CRJTNTzRFp1b35HCrupHZ2p+JQXs1UVMqdeVJBKk+m"
        "n3rMCrJ/00AVZPSm0Sk4dSgNSchvnXocCvJc0+ATvneR31v0MBO20eG04yGeBIdx5UEkOF8rjxxB"
        "TkIeLoIl7DxI4LCu9RAZIK4P4QDFHg8xIP5m0r/MSeXCOVi1e9ofUjwfwB6LWQ/rDwwPfbuyHqbD"
        "GlkMRYc1so6XDuvg0KQU1kGqbwrrICM7hXWQmZ3CGtqhwzrUHrJ9zwOtg8PEclpD/NLPR8bMeaA1"
        "xC+0DtLic1r7ees5rIN8ohzWwfl3OayDk9xyWCPp4wXWELcHWEP8wOqwvmr7RkvV/g0X+b3UT7Dd"
        "DK59+WCI7efgLwbavnww3FZ2ABjoVk6wNujtp6RvBuB+HjY1G+/KyU63n3TOkdzPPl8UzH09N1nj"
        "fz+3+OnrK0V1v/m4WRn//dySqNh+vPtx+SqufHPT+67+cJz3i38o1rv6znXNNfetPPmOQH2MCBaP"
        "emgaz3cMHhoP9XAYP2JNHzy+gwO/XWaHg94da8xE0BNqam0CkpG7L2D4aux11dgT6lSAi9J1gbLY"
        "YlAEtKLyFJ6ieFWAKERbIOcV2XMfiUOsKUDyirYAxvhFLw5RE4doW+Ae9pFMHnZBZr4Lu6j/32IJ"
        "l62dHi3usi4cvs7kPY1nXXCctsu6sKpPqHG6b59Y1JU+Z7A3wYcdircE2EG0Bdhhp8cWYIc9FEeA"
        "Hd60BNihyqsAuysaCuyuyIyyNfGIJcDuasx1zJo4RBsC7IIdSj7ssE3I6dn99sD4cOfFcNgnmOhO"
        "UodgwpwY7ZKJj7ORRakLZ4zPm+jVybMTTBwngYM3MY4zZ/tdE1+v3HjY/CH5p7NxQ3LQ0b2sZ8WG"
        "t5FFsPHxOquCDXM6vkytXbpDd6U+pgN73oaTjS756dzeRhbBxvT6wUJ9mIPfqvlp9XrJAj2ml28t"
        "cNCs06A6wg0pNde1pgWQq/uIUePqxEhxZeto4eHuK2ldiwk4cF+LAzdxfhYN/jfF303VS1+4RMxD"
        "2ES2X6Gdi5F7zFQhjn0TIriDg9pjWscbdXKnsfeUlE00fxFhfA+7d5PiMmERqQu3OSJqscFri3y9"
        "wrlFqF5haRpJ73YNc6qg5roqkhS6qpH06rwM6kzXRZTebPZP01B6dXtrLL15/qZvn1Q3zEgYsRSb"
        "J47IUmzXqCJL46I2QthEmEJYRZpe4VD7vth2odIU90k0kaZojiPS1L9jIobp1bUj0hQuvkSa3k9s"
        "R6QptqSoXVRs0lsMTdOD8Sc15ZGboaY9UjNeWoNqZjMkzs1MBsxvZpZexRS283sUGIinVtahmJ7b"
        "mRTiH+3ofmyOXEv7SXZ0T16DCg+5nU1Fi9zOooLH43ftn2RH9+fNhZp0twYVd/LbSjYVhvKvWlRU"
        "yu10Kkg9emFs5l4ZsPQ4daWz6cHpasfRI1KoHaR26bEnfO8i6+roUQYXQeihBa07HuJJ9N5CupXd"
        "NyUd6/SHaBHcgZGHiPjNpG+d8RAMwj1WhfOuUvoD9oP7L3LWBwfH5oAPDqjNuR5vwqtkbe8HgodO"
        "UkkP2w+svlch7KHD+mrX0mENbdFhDW3VYX218+iwDt+7vlFXm9QendZh+2a0xqUX/QHXwY0ZOa6D"
        "Sz1yXAeXiOS4vsV+gDXe+8BqtNN8YHUsJr3r9AdWB7fC5KyG+IXVYbErS675wOrw51j7N9785ZO9"
        "nOjPoeaAXLl3disrHwy0fTk16+7LqX62X3XUHLybjV4KA3D//o7OMNyXVwrj/k0ljSK5ry8UzH19"
        "pXgu6jvfeofiuv/+TrFd1K9v6vc3/Yf3v0FhXttGVnn369wsi/b5tX3v51MF9+Ohj+FE50mPUQRP"
        "d4wdBKSHA/GhF20mkskDG6PWylM6PD7lxJo2BR5DJDA4uBrFBy92DTWBthBNAbHBjY0+V8OzUGJn"
        "8E9mCkVToGZ8YEriD0fgY3CRjA/FcLNarQ+tVBN/aFVgXjzxY2uCyyhd0oVDhxZqPmfxqAuHkuPh"
        "PTP5ns6zLjyVY8eaVnjWhSeWeKyLz6JIPGEovUycDbAF2MUHVvREpMAOtXcE2kG0BdqFbVsSh+hD"
        "oB12XU0BdxAJtAubqSYOUZtAu/DHVBOHsLt1vz4T3xtiEo8QTvvsfELZbfoxymIykFBuE4S5sJtH"
        "ky5GuexD9HPl2PYInVE6m5oJ6XIwSUjN7VqlUlJndpWROuAkpPZ5CowjjeJAlHmrs/+ZkHp7RXLp"
        "LM6kKiG1V/AZb1rFSaYj3toc0jI+XGzeMu3q9DGJH7q9semLEhnNlUIu7gzhOIudIBxc7+ODIyoe"
        "rxRH8amLgud93Mx5297jwzlg2Xl8epugvedL54CI5ytHwfs8Bz5YLxztcIfH4RCH5wfHtfjKliXW"
        "vtu4zgUtfuva1w/5rbs5PuFzKwclXNrRORLd5wtHH/xSDoUcJP0PCjm46qJSyMGNGo1CDnYuUMSB"
        "8UERB7eJVIo4SKQ+FHGQPs91zJCm3znixNc3uM3qXDBR/ec7xxyUn+xhwT7ZrUJ1bo452ISwOObE"
        "mxbc5p1lcMy5z5/JMQd3XkwOOvAHjjnRPSXVbd1u59u4rdtbNMbMs0GjgeZbLmmj1QGf3pLWB62O"
        "8PWW+rq+VeWbVZ8TsO7tRg+gL5fviIT5RSARFx9f3mh5i6j5KB+0fEZMfau5RatbBNy3u20K7XN2"
        "wiXtcy0csubysIeYf3sE77eKr7zP8WjHkmijeR4mh7ZY0ml0Q1JoXiOPfNOQDt+yYgmPY1Qyz2As"
        "1k8evFiqLjxtw9s6SugATupHe3hPjzUCQmPNjL9n8LSEZvGIxCp15bkYXjxRPw+a2A/G4bGHRWAB"
        "dmifyRMOfr1prMVZpLGk0FgL13J7LOk01pCLe2is4S2Vxlq4xrxjyaSxhvWtwmMNq2+Lxxo0k8ca"
        "NIXHGjQ81VAFm6daXG3zQbNizeGpFl4DUmI3aJunGjSTp1roOrXq9VZjN/gMnmohb+7n+HmDOwCb"
        "lmzbMlWJ8OarWkA47V0z/a4Ac37qZtSB8+9sKAHsfFXYjdPulyipc8ywMyfKUvewJ69T/xgr4p/4"
        "ttRD7AOr1lsDpE6yw0Va/1qDcIHWv82gR0T0T8HfERT9mzdOxEXNuWrqJXYW0W9U6Ir3FInh6KCZ"
        "j5rZRd1+dKXEC/fATrusPYUbamCnREM/v6cYQ2JozdkVp7ja7bVXTilktNYcTbA7cx7h2ZpDCM+W"
        "nDzxhXt2q52TMwaHua8cLDjUn6AJnj05QlCGkXMjrIfaeN+pdrvNlAphGmI1H209pULY2e32ozOl"
        "Ah6tKRVQ1hQKYQVs89ExUiiER/f/Dgrxodx2c+2ZQyG6caA0/lG7vdbOkYDM050jAXZzIsQ3wNlt"
        "dnIg4Az7nAc4fH3kPAibt9pNNonOQ3hvYO2sk7evl1yEKaWGR7evd17E+ayGhSZZMLjSvt6IEZuY"
        "hokhmWhWKaZkwujdt6/XZ4R5eMWwsBULw4hq7evdGrEJqyq+XrURZ7ZaX1Ik7+zLatUiuWefpg3J"
        "Qfs2v6Vr32L5Rhnat5g2JB+1maH5qOVgRXNSsxSak24TXZKTTqsYVfLRaeGvSi5qHaHajJtC5Aqt"
        "moeOpoWTm8dnAqemOitDL4wcOIC9aOECeb9HixF4nxYXIJtaMEC+cddCANIpu8b9m7X5aSLscfy6"
        "CHikiW6R6ldoRuiSe4xZM6UTJVWZjSPGuwjqK9wqnpGrW0Uo36TguUUUI5lbxC+SlrsIXWR3NxG1"
        "wQUDMV/x0zgiVXFng9gzR+bv0FCKBGOxE47LsKqGUqQ/Nw2lV9emxlK8b2ssxVHRGkpvlmgXu9DI"
        "Rq0iSm/Wq90ryx1m1CWy9AqL2i0O8rVjmKKoXYTprdV1RJiiOZYIU5xpvkSYBsndMUyRtT1FmuKg"
        "+CPSFHnZR6RpcG5/TFO0YxVpip0fnaHpS2amAdeHJEcDtXmy42HIm5tZDIgfMmYNLOdWqB7v2zdt"
        "vZ02A/HUjDkj85XpqR27g6Z7MTclkpvpFP/zz+L61rmdQkWHvLm4YJGXZ1OxI69nrl+e2jEHvUV3"
        "ZzteyO5czVFj1d35DCoM5d/F9fHz9uImUnI/1ENWcGBzGqeC7OQ0OgVr7mlIwtL+0eNQkLmdRp8g"
        "OzYNOUHmQhpngnOx0+CCLIT1EFGwXvwQRbCWPx5iR3C8Vh4wUOr9ECUgHg+hAWvm4yEe4M39IQj4"
        "Z5jl4L/ZBnaPl/OvarKncv5V6wPWg9yLnOX45PEA8CCLIqd27CKxNliuTVkNbdNZjfzZpbM6OEIr"
        "ZXVwKFbK6lC7vqHdpHbqrMbS/UvvH+L+AGukQ7zAOsg4yGENv1wPsA6dunzHuwrpXr0+wDo4GS2n"
        "tX8UWw7rsJkr6WDmdFMt3/CRyjrYC62DcwlzWgfHJxq0VlKiDWAr+dsGs3051cX25ZUht59WfBh4"
        "a9+++JrfDML9xO3FUNzPMuc63X66+aRY7usbhXNfPyii+3qK6WL1DV5fKbL7em46xv/8TfHd1Tcu"
        "YcXVm7+dyrvf4qb5fX2lYO+Xn5te8euPIr7/46889DHaFUiPcUTh8R6ciu0yPTh+2wU5pg0mT+9g"
        "M7SLbGgETqOuNw/nIKPeJ/IV2SkgsSdUu2cYu0K1J6RbUrwjYBaiKrA1GqeXmWgUiMb1EPtDtRfC"
        "z4OoJg5xFDDiTUOg4RWZyZe1PbRtTRyiCF3cIB/dpR32B2yeduFguscac4wzYs0UaBdsTHBph7JN"
        "nnb+7gMXdtiFoMDuiprAOmi6wLorqltgXVi6/lINQ6/uErtC/RQBdShdF1CHalBQd0WjCKi7otkE"
        "1OFNSscP33QE1KHKp4A6IKjYqPvtMfHhpgtzaFAVE9UDoWLCSUr+romh1YUzPSuYGE6XkTfRhzNZ"
        "y5sYXodSMDG8qVvBxsdDsFAb9hSy5KBOCpzkoU42nOSivXv8VrzDW5FTbEwH798ux9bq1EueVvx0"
        "O7GAtzE/Xi9YKIfZCaian7p9ZMHGx8vA+C7Eguq4ezbMZYCa6+rQAsjVmbOCPdeZ68ODKGfT4sPN"
        "Z/8sLShgT8rWIgEy9o+G/3BLyifXfYbIeST6LxHu940iz3FdgMjweJNP7jH9bJHW2MmyRETHVUo4"
        "jT0iYbymiATGjpQlYhe1OkTWhj+oSpBmqVQNd+kFn4gtG0dD6dWVpaEUAx2NpHjd1Eia7WRJdL0U"
        "jaTYy9A1kmJHggbS4NT8mKR3W0FVe8w4R/+IJMVOFrVvDGERYYq2KCJMsQNCZGm8A4bwmqOyNCwp"
        "4Tf2HEXuNzpK4zfmftP7FFGKn/AWUXqZUReD0vRQ+9kZsqZmzB9c081MBry5mcFw+K008+fUzdJb"
        "6jDQfrj6wWB4fg8DNx+S2+EI/3KrhAX83E6n+P9YP/0n2Rk/qX7mT2qvn+TMRfdmLrTkPwqu055f"
        "EVKpwJPb4br0+XdxYSm306go9eg+sRncSfAQqa52Dj08Qdv0mAStHocgrXrwCYu8yGoeepgJ7oBI"
        "g0twsUUeUYKbJPIwEpa6kJ6120PAgHg+RIn4zeM7YtK9zksQgLg8kB93eZQH3kO8HyAfnHebkx3i"
        "+oBzFHs9MDy4LyUHd/yrirW4akGH9ZV6eXOMduisvtJ5dFijyDqrw9cu8rVLZ3WoPZz2vPT+g3s7"
        "clYHR/3nrIb4pXOPYp8HVgfXm+Ssxk/ppe+OZj4PrIa4P7A6dLByvuEklfQwcvpH8O1Kouupv40K"
        "mw+sDjHy5ZO9nGgb9ZWXVwbZvpyhtqteFLj9l1NpLlrNLVZud0o2Lfe2jpPySnHcv2pkUyhXriqx"
        "aO7rJwV0X98ppvt6iuri6yev5/rhvu9xkzDi+3nva9ysi78FbVKc9/UU6f0fz6Bgr3lv5b3vU3nk"
        "YzDReM5jDCHAPRw69EQzeI4HN2i68Mb3LJ7YwW0jLqbDo1dOohkCkcNzWkriCbUK7IVoCMAN66H0"
        "5E1LYGtcvJkUT6FoXOWJQ/Qh8BI7tYYAyXDrWU08YhyBh/imJkAQ7bQF8oWn8zifhBHf5nEXXN/o"
        "4i4a//fkNZ2nXXBNpEu7cNC7Yk0ROqXBfS4u7XBQQhNohw3/AuzwoiPADiKldwmRAjvsgxoC7IJb"
        "cXzY+bds+qyDNyyBdaELlcwfqsC68ASamjhE2wLrUHkK64JLMH3WxfNFPx6KL1Cx72AhlGZ3tDHK"
        "j521wSjtLh+hrPaonVCaAXURyl5tLObKMexTgwhlc25PIaTFWRQjvnQ6vCSk5uEAhfEjOy2xdKrA"
        "zmIYI3V2PxPS4eCUqSZnapVo1+psEiSkXnJyLp3NSW0g3rqdjiXj/s6E6qs3Vcqb7LSSL8qb1Xw4"
        "5mJfSKdAGz7e3cdbp5AK64fi6H18bwqeN8O8DYqY2FjAYRJXeHSOjeHNHW6z9kNCMNxO0fzSc7DD"
        "9SEc4FD4xVEtuyvELc7m+HUv6viQ0Lr2T+VIde17vUDXFwrHJHzv4EB067Nvjj6496hRyLnZv/be"
        "OPfxtijkYHN4oZAD6xRxks0O3uNrUcS5+dRmYbb3uL1X67iPs8SJ77dwm3V4h8t4z5fNMQf2Dwed"
        "sHqK27bdSzP1nt+do068PcNv3ro56mCnSuOog3svyE4RbubgoIPik70f7EJYHHRAkRNAJ08KjRj0"
        "llLaaHUNCPWUAz9Y8doBv94yjRetPgHd0mPkA9TlGcknIl/6am9PLCsPu2JPN5KU9r2yd1oeDk1z"
        "eY+QmstXRNhcPiPgvlU863P2HQKV9rm2Ijjn8hHBOi982GF8u/6m9m/81O0Px6LopmEepgG3ULIX"
        "jW1IKg3rUDJjyaCxHCYy70hir9ifUFI6z914abfEms4TNl6jbQ/v6bGGB2hcbTN+zeRRiXVgHo/h"
        "immJvWAUnoThcZ019gJv/2v4PQLoomqriRPwTMPSC400LJZOGmlY+uV7oljd4fuf4Wrx1CVLL9iO"
        "a4zvVcZLg59QoyANa3yVRxrec3ikQSMgDXVweKbF6evzQbNijQC16KdWYjeog2daWNU1doMqMC1c"
        "8q5NZ0dNSBCt80pZuzUTlWjVwVdFM4FSXuzIRJ9oJUJLQV6ZKpwl9C8dCFCnXXQA2vmycPHWl82I"
        "eb4snEfUbqAoqXuEk4q+qkT482UtIqD4abmL9AiErmyHI13tIoSaOskJR7aubJ0IilqV1NRJekpG"
        "dCZXysMwQbTZj+bkw2BjprwLkxgnX9bF18A2Hx0jhRgGAycnFxJOV44rPNtyRsV27RZbM6dRePOh"
        "3WRz5NyJP81utF1zwuA+u5pjBc+enCU4xH/kAMFB8jWnBq4r7Dkq4lxlu9nGSakQ5pZW89GWUyFM"
        "Du6m1bpTKoSpnNMuawqFsAK2+agZ7I756Oo5FHAed8uhgGdHDgU8mzMhfNRuL/PA/2I32Kg5E8LK"
        "LXabjZUzIbzUoNittnfOBJyQ33ImwO7MmQDPqTkTskvdzF/E12f71wsu1FOC+9f7LuK8W6sUTTJh"
        "DCD719sw4hzebpgY2odYpZiaiWOYWJIJwwn715s04gxL60OOZML42XTjoo3QxrGKUTT/NHDTjXs4"
        "YhvLstG0KjXL0TUbZjkkH7Wyfbtxi0doo5ltu35CnUpuOj7WT7ZIfjqa1S5V8tNh/War5KazWq5e"
        "JTedH6tpa9OqwyyH5qajaVEFCbJLCyVI2z1a/MDh7U0LGri16miRAoe+Ly08QDe1mHB1o2iBAPmX"
        "XaN/cER5jPybIGqzoBBCFe44afyIRMdJ40fEOFKWq8huHMMu8jpujdxtxhTBjKpRaYzk7y4iGCVt"
        "InjhN1ukLYRHRCyaf4hcRV7/0WCKZF4RpjevcWssxZHKR2Pp1ZnDh5HruoZSyLqGUmR7bg2ltxVM"
        "fzmpziR3RFIkWR+RpHihSlKkRYsgxXn4RQQpjlKfIkivcFaRpEGmdUxSCEWS3roRORpkqMccvanV"
        "TeXoFZqBuxJes9WuapCVHnMUbVEZjqbJgZOa7kjNdKrLmpupDHVf0jUNCL+ZmboZqrub101nkJ03"
        "eGMInpqxh+4f2Y45uVN0P7Z7h7ojn0HxP7WzJxUO8nreVHTIy0PFitwM1wnP7RwqlOTNVajYktmx"
        "FtWsUJPaMeu5yu5cOzd9ktqxe83tJ31X/0k/09gMFjO3HqqCe+TT+BSsJadBCQvGeiAKVufT6ANt"
        "1UNOsK6axhlUc9eDy23eh3iCpevyEERwk/p5iBxXbHeJG/nm/RAjIB4PgQHF7g/hAOL5EANw2f18"
        "AD8mKtsD7SFeD4jH1Op84Dou49wPMA8ndSvnYe0B2mioppM6uIU8JTWujF86qYObwlNSB8viKar9"
        "zIKU1FgJbzqpoX0gNa6k3zqpcYv7fGA1zhMYD6yG+IXVV9wfUA2vrA+ohviB1Gin+UBqiM8DqVHq"
        "8UDqsK5Z93rgdPTeSjrXeulzx2LSu+yJLtK7GgVqP2+Ymlf3s5Ubg2s/j5gBtp9OTHWv/ZcXhtu+"
        "nEK3X3OTobfbbmbVHVreKIS78s5R3Nc3CuS+vlIw9z9/UTzXqo/2vGquLpXJv75QYPf1HNvF5ue9"
        "b3Az+67enPyutPs1c3Wo0u7Hdcnd0pupU7V/0/lteTjWrLGmDJ7tyPY+PNExa9B4jEMzeXZDU3hg"
        "43sqT2lMRwhovppRBSBf0ToCha/oKOjFKHQIvMWbtgBZDNOngFaIusBTiLYAUYzlp0BOJHQpuESW"
        "1BYYiRQpBYxXNItAQ7xJYCAOmCwC+MKpF+eLbp/Y9Icaa4ZAO4yRNk87TFIcnnbQLJ520Ai0w4Cx"
        "8LRDvR2edmH7eLS7OSulCbSDqAi0u8U7AuzwSVWAHeYztgC7sMJL4g2zC7CLi5f4AzlJ+zvREGCH"
        "XKslwA4ZU0rXL8wGq4lHnCPQDvMIy6bdb0+Ijzd+NBt+vAlvDlawMGwwKhaqzUnBhDmHPaXK9CjK"
        "m+gfB6q8iWEucB2pFHZf8SPZcLPxhArdXqKGUqPeqpvyLQ6ulWJ4E7uKDS8dWqjS5bFdseH1a7/d"
        "tJqbur1ewcb09q8INtyMasXFihM1lDr1gohgo28tpmAE0rVAgnFf0cIHhrNFCxrQaYECsq5FBwwB"
        "uxYSsB1oaHEAGx+GBn8c415E4l/hp4mYx+UHXWT7feM4ItAhrCLGwz1BZRBCFdgoqghpnAY/RDKj"
        "pEfEMUqqMhhbe4oIXrh4EWmLyjkiYq9QpCpmPYaGUgwgloZSjIvEnjiGEVtDKd63NZaGA/qZ10sR"
        "u9fY1bM1luJQerEjjX0vXWQp0vSXyFJsYFFZinP6VZZGuzRyl3G2oeQ+04tK0iv8TBGl12vMyfxC"
        "uE0pIkqvsC4RpTi+v4oohYcfEaWhi9dGVE4TYRpcXGLAND+OnmJrfp7+YFD7cqi/Qd78ZgGqU/tm"
        "Zv4cM0tvKQba+XHolWF4bmZRSM8Pd6cA/2am6l/VKPq/XDVghYOHU/+t4JCbOVSseLSzdDtcp/yx"
        "uc7P+a6qO3Pjpk5SO4MKQrkZbgYl/6xNhai8mrcesXCG49HDFI6KrHpswkUDDwEJ9xpMPQpBW/XQ"
        "A60ebsLP3WQ1bz2yYNvMQzTBLqH5EEOiLUaF9Cv3ICjqxeMhRGBTVX0IDHjzeogG8ZtJ73JXRN8r"
        "jPSvNR4Ijyym/YB1pIGtB5iHOWSV8zA7haGSHraLzmqcOdh0Vgfn0qesDi4IT1mNM+e3zmpoH4YJ"
        "wVn3KazxvUOHdXDXewrr4OTSnNZ3ruuB1WFOTiEd6zywGgeEtgdWQ/yAamhfUI1meiB1cIRrTurg"
        "PNWc1BC/9MWxlaw8kBru1R5IDfdaD6SOi92/Qdsvn+xf+0B1rP27Jihee/LPoWbafflgqO3LJwNu"
        "/9up6Xf/8pHK4Fu5V8EguC/nutzKbRAWyf1bCbhMFl/fKaD7F5dsium+/lBc98vPzcn4em4a39dz"
        "s/miXvC/SnHe3z/WKdT7G8gqRXtfT/He33w3KOSL1W/Lcb+cgHr/fjkX75gHODzToRFADk3h6R3c"
        "ZugiO6qCHUvG4tkc7snxgAzRESgM0RDQG78pcYXTBchGR5kkrnCmANPoPYkrnCFAMxbF3lA/Q8Aj"
        "tk5NgYk4kGQIIMSGuCngLzxopiZkOIcHXTTyqbGkFx50wRWHLuigWTzogvv9XNAFd6a4oEMddJ50"
        "4QkcJ9RU97SiSNSKQDqIukA6bEtqAukw/jsC6SAqAusgqgLrIBoC7eLi7RfReSheTTziswXahW5U"
        "M4/oAu3C43Rq4hF2IvmPh8I05WmnGxNKm3y5sDrJGozSXhkjCmsubk1GWe0sDEJ57LMmcqV9OvFh"
        "lNs5YoKQLoeUhLQ6u5sJaXP2OBPS4UyvElIvEZkpsHOoJyF1zo9gKthBKlNLzoCbcSYHr7nUuQGE"
        "cSb7OobKONOoTvfy1fsr5UwfDr7IZj4UccNz7Jr3uH2tSPcfp4AaHos33ccrRU5siF8ULm8u+eQY"
        "iWR3jovYxrE5GMbbPtxWtT21NP/5w7EOn9s4wKE2Oahhz8HgUHaLz9ErvMqjBG1Lcgr2KwensPKr"
        "37ifwmEItdk59mCPSaGAE6btV/fxxgEn3A/evcfrWRRxsFVhUMRB2Sni3KcXRxzk3HeKOPGFDx/v"
        "+VEmh5zssg3veRY54Z0c3f9cDjhhqn1xW7aTwIF5ssOEtuWIg+tDOkec+FINv23X5ogTtm1127av"
        "zREH9wBFxMmzrEcAoDz9Mxpo5inVM8BTri4Brd7U81vqRddaC9iWp+7WAHVvF4qAfE9pzIV2thGO"
        "RfOyr4iSbznPpX9PTjucd8I4K98RZHN52M3L5SGD39q90k63wj7h29Ualfa6vSJ+54UPB69vCf/2"
        "pyOrttBIxzJypzmOJdRCwxsJ/40mdpiAPmPJoNmMgg0ayKixSVM4zrP+hJp4rOvkNleesvFqa+wB"
        "p/M8DfOuS+wD5/DkxFpr5XEJzeEZGWZzl9AP7KPTa+gH9vHANfSDOjbPPWgKDzuUrfKEQ711GmtY"
        "UGo01sJc2xZKBo+1cJ15hJK2aKxB0mmsoWCVxhoWqwqNtSj7+xMq6uKhFp2BX8LWt89uLHHzb6GP"
        "CM3gmQbN4pkWL8OuB03sA0fo7EHTeabFq6mJGzSeaXC3wzMtPJO0Jn4QrTX4SZPRDKCW6toyVY0W"
        "IHzVCPimvWum3xWtS/h1WALQ+emeEet81YqA58q8ax2zt52Ie9pVCqU91UhJHWSdCIDaTRllvslS"
        "H9k1IqFYk6mXnB3x0L8GISKif3lB2NHzZTXion/PRtjd8ytypHTEoGelSAw3vjbzUXPSvJuP9px4"
        "eLSlmAsfXXZZVwq0cIR4rEertyXberbunFfIHC05pOLLBZvwbLefXTmD8GzPwROXwWw15x5As9nq"
        "ILiCZ08OkyhpoNrNdmaOjfASgmo322o5IMJM5d8WN7y7q1qPlpNCIRzvdPPRWVMo4NGSQgHjzZNC"
        "IczL3XZd5V0b9Kh3DgUcfz5zKODZlUMBB7i3HAoo78ihEN/YNuxnSw6F2O6yn+05FPBtNYdCmAdd"
        "7XYbORRwTuLJoRBePljtZuszh0LwSx9fL7gI8zuNRLXx9b6LOId2GCaaZMIw0L9rYCgGLMaPr/dk"
        "xPWwDRNLMmGwYHy9RUNNKB1fL9WIT8Eullt9tGJYTlEk37QSRodxA0ecrmrVaGmaDcuE5J9W7sEw"
        "ruuIi2Ha0Hx0m80iOWk3f21F9FLLhOaly6qOqnnpsn6yVfLS8TFtSF5qpU0N45aQuEpNGxpGTQoG"
        "1YFrqrQggtzapkUOpBNr8QL9+K6FCbyuaLEBtVK0gBAkEYdRACmVVUM/UjenyPsgZzWGfHCGekz2"
        "4NT2GOdIZ90ixK/Q7N2U3Gv63CKu4+ZYhFAFc5AbHOM4yACPGYxa7SJ4r7CLsA3SsWPColKXiNXw"
        "1xh8YXBGdQjTmwgs9sJxvvzQYAqdCFPoqgbT8H0r1/WjwRS5umI/Goeoq53nK2xbhGlwbHsMUyTc"
        "HhGmyNpuIkyDlOMYpjgNvYowxa9piTBFtvAWYQrHmSJMkb69RJiiVosI0yCjO6apn1YfwxQp22of"
        "Fe3fGZhmSYLV7MlV1Yw57dJkK4sib2rGHK0P2cygJkByM4PBdF43jaF23lCHgXjuNotiemqnHQrx"
        "uZ1BET+3Q/E/NWPDuet2uOiQ2zlUsMirZ1OxI7XTuX55asfskhTdnWelAk1qZ1FhJzVjhy/dm8+m"
        "olL+WZUKUo+/9tjMnaqYTQ9UWAUdengKUm7TmBSkH6eBKDiWK40+SBdfesgJzqdK4wxWvJseXLD0"
        "Ox4iCqbN1kMYicWVFM+HiIFptPUQJnAB/HyIDRD3h4CAb36JAhCPB/Sj2OuB91dMTo+bYnu4VTkP"
        "66U/8BwXQY4HiONUivZAbpwLUXVcB1e4p7gO1vRTXAcJ4imukfuxdVwjg7fruA6yf1Ncuyn0Kayx"
        "rK6z+s4gPZAaW/lfOvyY0NsPpMZ02QupcRxCeSA13rwfSB2/eX7jV1hI1zrrgdTB5Zc5qWN4kB5W"
        "HkCNyt4PoEZ9PXAayDsPnIZ4MJz2k3mp6XU/qZeitZLubABbSbI2mK2krRvY9uXUFLxbdebCxqbl"
        "nepuu3IyqcXVL2563n8/R3Nfz618unpzzrZ0/v0U1cXqn7y+UWz3m4+iuysnAe/q7bkJ2vuavShI"
        "e1+r3Ey/q29cgopffq5n7jf/5KEfjrFrrDF/pS3WtMUzPdhh4II8OBbbpXeoWbHG7CvvpK55NkdJ"
        "PB6PMcCbAoQxjFbIG4taUjwBsRinK2BFhtAUaBrcQO8jFKIigPOKdhNoiZH/ERCJJAsBi1fTtsBC"
        "zIgI/EPTKtCLp5tsDTryQp8W+euVJx0G0YMnXbBdwCVdcLq1S7pgI7JLumB7gks61NvmUYdpgCGw"
        "Dgf7DYF1OCaxC6zDbeoC6uKZjdgX2lgC68KEoTKTX0QXWIc3KawLDnf0WReKauIQvQiwi7LCauIP"
        "djpvwoazBNhh6sPp1v32mPj4UHSnl8ebsDuKTTIxHTIqJhxQKh+ybG4K1dmcMT5vopt+uiUTw5mu"
        "FUw0L6lZsGHnuWn+6XU+BRPHG/orn+LxWrDhwFv4EtNBi+ah7kyA0ijTIb3SKg73FRPerIDSsN7M"
        "gGCjOkFCKYaXEqi0SnFCiGDDzpHxTYTDsJrrzIzCluqsLaFhwAiTO0au21ULDdjDsrR4gIHZ1oIA"
        "NngsjfyhLsJ9cA55zHgscw+R7BhKThHn8Rtzp+n20vYg3thFXsczALnfNHcZLiuqPZ9EeM4eIoTD"
        "LUWV8Jy9Rd6GvlobUasiWDHPdDSahpsuaq6rIk0xKF8aTTH+EPvc0B2Npvi+ptEUuxhEmiLfXoNp"
        "cOp/DFNsmhBZivT+IrLUP/I+RimO1le7w/jCIaL0Nr29VzL3GbuDVxbxRhWlaI0pojTcpVEJvxlF"
        "ROkViiBF1VQRpME1JDFJ/Us9DJC+bdKoshlzbNxkM16ysGimTAbCuZnBMDk3cxhE51V8GGLn+2AY"
        "gOcnsxeK53lpDsX3vDyNwn1eHg7/j/Wje/Lh+tlP+8uK7sp7U5EjtzOoQJJ/VqPiSr4dq1JhJt8n"
        "1Kiok2/04OZP8vIMKio91k//Se0VmwkTDyqlLavr4QkHQj7EJJw7qcchXPKw9OAD7UPEwbGeWw8z"
        "wTH+aXAJjtnPI4p/9GIeRTBvth5CBybP+kO8QIrLfggS2FwwHiIDxOUhHgSHV+ZBIDwxp+zvfDPn"
        "YHb+TeUcrO31APZ44wznYfaRP7V9o51rJ92z6LAODn5PYR0caJ/CGsd/Th3Wwf0TKa1x38PDUAHa"
        "B1rjYNKh0zo4qTSlNc6ffOn/I5XipdMf76rgXKuOl+59uMegcM5Vd3/ANSYjxwOu42Jz/uVvNH8X"
        "kx7WX7rk4Y6OSnpYHw+4Bvj2A67xixwPuA7uNTFw7d8kUBli+/dAMMxW7tQwsK1cXWGQW5NPWm56"
        "6uIrnkpucfPYGYb7G2g2hXFf3ymSi3re686meK5tICq049XCUd1/PzcvI5Z/fVO/v/n9vP81DvL+"
        "Dq5Ocd7fwsTNs/jv5+ZX/O+neO9Xf+GRH57HUUNN2YenO+YROo90TLU0nuPB3SIuvINrOl1i41yP"
        "xWMa+3gmT+d4OuITi84WOIxJEwW+wQ0TPnFRvCpgFnlQU2ArRE0AKkbJCkXjuYidFO8IvETKRBMg"
        "Ge99iT3CzrGpsUe03gQGRlu1ak/8VaBdPIqINZ/N0w7j8MXTDnMVg6ddcL2JSztoNk+7+FiMSNE2"
        "zzoMiofAunj3RuwHzT3RNCreUnqXwS0ePuuiA0FGUndbIF08kZD4gj2BkLiDvbn8PIjqJ/mmKZAu"
        "flPiD1JvL7g200cdEGSfHPTrQ/FuC/s80lxp9yEao9x2V49R2h0+Rmlv6CNqqNobmHOlvYmZ0Dl7"
        "TxilzUdC2ZwT3Qjpx8mlYKTO/Coh9U6AZqTOJkDCGbwcOkLqHar//FbKl6oz4mZcwlkAe/TDSjnT"
        "sjnLKJ2FL6aSHOYyrboo8kb786v7tOmozXu8HgqrGJktiqXhkHG6RW+Noma4P2C7j/dDERIXYSyO"
        "i7hxoXAwjDP/q198jnoo/uRQh+cHx7f4LpTpf+7gSIbnD4cv7E6YHLPibRBu89qXB9TiPz85KKH8"
        "iyNRWD/Vb19nGu/3jyNjmGIO0oQ55oTb3Lv/+KSgE54PN93HKwed8HyD7T1uX0p33MdP56AT3qFQ"
        "3Gbti2MOzG8OOvEOjO7XzuGgg00FHHPweOGYg40AHHKwG6NyyMHzJHLQWJ1DTlj71W/dNTjkYBPJ"
        "4pATn+rx4/E8fTcgUL7jIBpnpmrnwBhS3UaAq1zdAnrl6h7ALK+1FrAtb7AaoC7P2g27W2nysLdI"
        "zMpHBMa3CzsK7W9nR9h8LPyg5Suiai4/EWQf5azT1bIjBuc58C1C8tsVGZX2uhEOXHP5jPidf3uI"
        "87zmG013LFXSSEeyN89xrCMXGt5YquWJjRXhRWMakkGzGVsKDg1kLL3TEEZ6uUDeO1LnYYupgMYT"
        "Fotxg8dq/J6w/e0hQBmxhodmeOhGCT2gfRaPRxSt80zEHNPmQYj5l8LTD6u/m0deXLYW10Hl4Ra7"
        "mynBslWlkYb8Sx5pSFavNNKwVlxppGEJt9JIg4TvbiKDdNBIQ7pro5kWnqzgMC1b89U1sQMoVIu/"
        "J3SB5h2fEpZt8ljDMqfQAYRm8FiLtwPEfjB5qoUL8jXGwKo81YCOzlMtW+cNeRNRzU/ajJZ4/TTj"
        "iG2uakbTgX4yeDQr6Kt6ADm/hAHmtFsPdlbxJVql0HJcwTtfFi7gim/LvKPWcOHWl4Xs8wvZI/yJ"
        "3zZTWdi3EwuZOkkPFzu02wxq6iUr7Of5lw+EKyC+LJyV1G5aqLmX5HTE5uGZIhGDsJZyECm/M4Uf"
        "RrYp8MK7BSdtdJkf5ZzmZD06SgqxuNP9sZ51BjZma7VCMCpOs2223Z3TCFmrNUdQeGJhmXY9rBw2"
        "8d2H2y7vyrGC/cYnZwnWHncOEAwqd04NlGHlqED97pwPyZ16//9H0fPL+0novM0UCmF2cLceLaek"
        "VMDQq6ZUCEdpyyxrqSkWwp2xx3q0eZvGrGc7gQU823Is4LjznmMB5R05FjBoHDkWYLflWIizde1W"
        "2yvHQjwoPPazI8dCmAZQ7Xb7lBwL4Tboav/SZsmxgB/wV+TNr3dcxOlxhoUqWfhYJppiwlqXnV/v"
        "w4hNWKUYkolllWJKJoxNB/Pr5RnqAePz610akYlhJNzNr1drhCaMgySncdNGXAyrPovknsOyULUv"
        "sUxI7jlMDy9dK8a0bAytQs3qkDzUSqCZxoUe8beY9aH56LB8tGhOOq36qJKTzo9VH1Vy0tnMclSt"
        "HFZ9VM1Pu4WOKvmplfUXhhRk/2lxxD9QOYwd6GdvLWBgU+HQogR0YmgI7lkL4wHGHEMLAjfH06TM"
        "yXVtibj/IZyfKjL+vtGMlKUSRR0i0K9wixC/unNEct+6sSt1EpV6REZfYakimFE3RaTxfeM8IoKv"
        "cKnc/SFcZq+i5o6zPl0k7C1qVbEKoYbSH7360bvG0qsrGkuRBFo0liKXVWQpzmBfGkuR57w0liJJ"
        "tGksvdVpdoFPrjOZH7H0Cu2uWe4wtoOW3GNmE1F6dUPtEENYRZbiE1WW3kpdQ2TpFdodoU0UdYos"
        "ReWo3dkrXCJKr84cM9f62Bq1EZXaRJSGP8YSX3Rv7eirDFpTM2b3rKlmrBMyDfKmZtpmQJyaKRSX"
        "UzNm3ayfU5otmzG7mUducHNS5ivTc//jpkRSO53rPad22qQiQP5diwoIqZ0zqPiQ2jEnFIvszH1x"
        "syV5eahYkpmxtvBZoSW1s6hAk5lxOsayN0973kL25mn2SKvszWYHrvaf1FqxGWzWLHqgwr7frkcn"
        "3KlW9ZAUTsoMTmvW+eS05iTSIt9b9DCDKa+pxxa0b38IKJiRmA9RJB7qc67lzGJzvjVWewgS4XxB"
        "4bxr2iNxzr2coccixeWB/FdsTqoWzsOW2VSV87BtOknlPOz0/oDz+2azT1w5D1v9hdxxO8daTNk0"
        "HddXa65ANEprnamQ4hrzN0fHdbCRNsX11c6i4xpzQFXHNeaBHoYCaN/xgOs7Wn7p82NOaDzQGqXe"
        "D7TGxEl9oDVmJF768fEk0SQrrD7QGlN3L7TG3MYDrO8nl/YA6x/iZfbZKudgazywGq18HliNhmoP"
        "rMZ0ENW19nJs7eFzpeUfqoPtyZvZD+q0vFPz7q68UtM8rrxQK5quvHUG4K7cdJpDN1zjMO7qzeXj"
        "wvudvTTAOx639CkWn/a8Tq6Euvp9KLD7+kKx3ddPCu+e3sl7od1vkIulnn7WQYHe1dvdY9r9nChF"
        "+98wQ2Sl/c+eFHE+/w7Sj4B6nDxWeL4Hd8q7UA+yxV2SY8Li8PhGFn3nmY2MF57TtwpG4eGMeZAt"
        "EBnzH0vAMGYfjsBezHdsgbh4UxcwiymKLrD1ioYCVIxzt0BRiIaATiTADIGXyO9YAiTvrEE/Ahnv"
        "PMXnCDjEm6bAQMzFLAF8qHKhj6uljvxWw80//EbTZ+Vp559l5sIO0wwC7DC9IMAO72k87XDVeuVp"
        "Fw/IP6Foti7Q7orsvLzEE8h8kN+K9hZoh5FjFWiHeZQt0A7DTAF2mAbYAuzieogdwvwZ1dgflt0L"
        "i/1hmUleNfYHJ7kv84cjsA7j+WGz7renxcenSzupHYKJ4YzrBRPdmZAVTDQHlIoJZzVNqU6boryF"
        "7s3VCiamM9xXTHjIFWzY26wk9+zeqptgont4/nZ1SA5qHcY+jYs7HhJqpmbDW5gTbAwvy0+x4YBf"
        "+a04cUBpWW9yQLCxvdlgwYY94Ja8dDgRRGmTpgUU7EcRo0hwIlgYOpC7IMaLYHN+GCQwFaAFhuBg"
        "+zAcYPalaTEAmzymBn6kvlSR9tH2pZL7Sy9V5DqER4Q5qrSKBMd57kPENrbqVJHVmEfbIqBxlH8T"
        "qRxckRCzGHNXXSQwTu3vInbh4ltk7RX2JQI2nMyqhOfY4yFfhxH/1GCK4XjRYIqjFJYG06sbGktx"
        "x4DG0nBSY+W1ecT+NCYdNJReWVNRGhz6HrMUG5GOyNL4jbnDdDPZqHTijVVkKd7YRJYGR/XHLA3u"
        "e4hZiqJOkaWho9bcc3SW4o1HZCm2zA2RpagclaVox8mwNN86shi0pmbqYUibnrx9NgPe1Mw6DIhT"
        "M3MxYM7NbIbTqZm9GGznm3yoHnG+c6lQVE/t1ElB/m0nVdEdeU8qBOTf1amIkG8c4TrbqR2b3lP/"
        "Li585BuhBhVN8o1HhQou+YYhrt+e7tVwE55VO1yvPt+CUqnAlNox67k++HPVwxYGnkePVeFBGI3S"
        "knPxzsn4VQ9FOPC/6PEnuCwgDTo4WPHokQb1vPTwghmJ8RBTsB2lPQSSKx71IXrALR8iRjh4L5xv"
        "zXYeYgPE/SEg4GCR9RAF4o1DmxSPB95j7095gPxN2LB383EOdsp8wDm2sowHht+UkXEewJ0cPBJJ"
        "MQabOqzDkzYapW276rAO530Gp61Hh3VwbGYKa5T5AdZXex5gjZX29gBrZGC8wBqJAfMB1ij2eqA1"
        "trK80BpJEP2B1sjdmQ+0RhrKeKA1Kuw80Bpzf+2B1mjn8UBrJLfUB1pfcesPtEYqzkuPGxX20s3G"
        "lFBncO1vJ6G61/6ODGqy3ZV/GsNt5Wx9A93+RQDUeqb/9sIA3P92amrHlQ+G4v4mJC6xxdXXTbHc"
        "fz83c+Nv5akU0cXy055n9hkK7XnOVp7JF5/rivt6Cu/+TiiO8P5WIG6O398KsynOu3p7/pv2Pju2"
        "Vtr72LVUzftsNXIbFs/5q+HRrk2a/O4GCgHimOhYPLlxC8LkcR3cIOEyOjwE5cSaUwUcI7NiCAyO"
        "z2pNHGF1gbZ4UxUQi7FnFcAa73WI3cHf6h1W+RLAGZ9cEnvEJJP6fru9pByBi5ho6AIMr6htgYB3"
        "VqI1AXvxGcG2Biu6k4cd0k0WjzscKLF53GnTDb+7YePwuEN+idA7DXe/7LjeSuNxh+FlF3AXn4wZ"
        "e8JYRcAdiqd0LrH9ZQm4i6dEYm+YZPYzsberrKQiioC7+HSFxCNWF3CHE0gV3N1h/mcLuEOVFwF3"
        "oZfX2CO6nQ/+46F4cdU+RShX2rOnjVFOO2eOUZoUJIRmOuFklMtOySCqttuJyITSOXKCUTqH6hNS"
        "e62FciJnlpV5qZNDwUidwfjzpzKO5CbTMbXk9B2ZZnVSIHLpcJIeCGV1DggipN3ZGEJIp5NXR0iH"
        "s3eQ+VZntzTjEZViL5LwOeCG5zU09/FJkRU7SBrFUzzeKYii6JMiJxLwO4VLDBQLxUgc+sBxMT50"
        "0m/VszkExhsj3HYdvXCwQ5YCBzgMlzpHNRRnciiL5w/Exi1+63odQfd7K8cnZEBMDkrhKRTVb949"
        "OPyg/jfFHIxsC8Wc8JiB5j5OIQdr7lwXDmPlRiEnPFRh+R+6KeRgxY0iDsZOk0NOfFCD26hjcMTB"
        "SJMkTnYWo/v84pATH3jgNu0oh0NOvJfEb1z71Aa/eTfZO8KhEItDTniaRvXbd20OOaifySEH208i"
        "5OQ5vAGA8gsVIh697TforNrE2yDV1TlMhlX3gGZpyQO0pdoRkC7Prz8R+PI07RNxMM86bxEX88Lv"
        "CJN54cNB6eMdEqy7OXvLWH/rIyJsfj9Ii4Cb7zrYEX/TpPO6Ihyn1zjEHcLHWyBYp7PT1CrrdM5J"
        "4LTTnUKTPTnhMJK0QUP8DiA3DW6svBaa1shgLzSisfbcaC7j7IRN4xgrwjSDsS+88eDFyGPztMV6"
        "ZucRezU8VTGEbTxKcTjh5PkZrpmW0APs33sJXcC503PH7yk8FK/mdJ6Ed2F2Lh5/N0+9Hp558apx"
        "6AdrCHTD2n6jkRYmKddIYp/80EJJ4TujGAIfmmk4XKDSTMMCM400vOTQSAuv7zxhs7TOMw3ro5Vn"
        "WnhmX42LtnioYZQ2eaiFR+KVEVdB46EWr3qvuA4EqGGk3XmohXdS1NANVpk81HBmIc80VLXQeQvv"
        "a62hG4RTfm7OXzTudtNkZ9RV047Z75nK2fQYq+zN/zNVrQBy/uUFAeb8KjwB6bQE20+m6j3CnZjM"
        "XFOPOhH1xEJm7tF3i9jnp7qGA2E/wTokoHZFwk7L2CIM+lnA4UDXlZ0ewdA9ft/Le0netmvERFfW"
        "S4RF30lyNGLdbaVAxPhrpxQMF2m7+WhvKe8wMh0p5PBoS8mGRdycZ+GQ/ViP2sfo/A5d8an4ZnuN"
        "MXNIYVJi5WQK10fNFps9J1D4qNli7rZoq7Cn5YCB3ZJTBXucT44SpO6WnB/32VNyaOBse4IUyATO"
        "6YCBc0uRgIWlnSIBA768Y4ShzkyRgEXLlAgYcuVEwHhupkQI11i3+VUtBUK4vPQ7ICBHlwAClt16"
        "DgSsqJYcCPHypdlgc6wcCdiNW3MmYIm250xA/e6cCfGmXrvd4oHWb5NicyLguriWEwE1tnMi4MsI"
        "JGD89NUb1te7LeI7rKdhokommlWKJpkwJlPX14sw1EOX19eLMdTMzfX1nox4yccysbS6sKpzSya2"
        "YeEoFqzsqWVcsRGvIJneqbmn0U9YxgUc8f3qpg3JQa3zYpZxPUdoY1nNUoZmw/KvIvnoPKaNpdmo"
        "lg3JS9fHbBfJT62dVMu4+iOyYfXXlnETSGhjmuWQ/HQXsxxNqw/LT6vmpybDgupA31uLJFiu06IH"
        "0lmXFjIwrBPjBHRicAjO0g4jAt4nhgFUZ9fgj4FeEYmPxNAtYh6D5iqyPTi8Kwb6HW2ZbV9yp7Fu"
        "gY/RjfHdEnmNO9irCOkrtKNM7jjrdBHHOBqsiwy+y602rHLPOSYzau45RwTsrRqzb1kJv+lNQ+kd"
        "MJhtUXNdEbviQaZlCNNg0SeEKXRLgykmNsTudTC0DGGKjNWlwRQXs00RptiUOUSYYmVQZKm/Ohij"
        "FO/bIkqvcKoo/SHcNvVzp1kmLUruNaupndwr3FtE6f1Gm1C53+w6RJT+EJ6iovS+cQ0RpqgctYsK"
        "KFKzHVlu4BqFYWuaHzmpfmuepUl1Y9N8yXEYEOcpp5vhcmrGpNiSzZTGUDs1Y7LxyC1VDsX01M7i"
        "+su5A3JTI6kdM4YX2ZNXrVREyOxsc+BTZF92ICw7sxOwlm6Hiya5nUEFl9SOOYVTZX8+XCc+MVM+"
        "djypsh1zXqDK7nzMWe2qu3N/iFp3ZPXZeqjC0OMhPiHf9iEoYZmy65EIMwJTDz/BfV5pzMHS+dAD"
        "DfJylx5dcEn7eAgpVzxf4kg8L8G61kPAgEuvhyiBq+bnQ2jApMF8iAfIDF8PQQDF3g/kj8Wcg539"
        "gPhftcVcNamUe5U2H1h+tbaYcq9ij2Yo7yrWmS8pqe8wipv8NrX2SKpR2vVCasw1LJ3USODWQY05"
        "qofBAeZjpg7qqMiHqyl7BuHDNa+5qlw4v9qjPnD6FtseaXCetft4APX9OZhj/ML51lkvHfcr7ucB"
        "1GiqF1Bfsd2/5zxsP5H6V/E/us77AdU/xOWp333F5rxqbVyxzQF1JT2sUt1qL7/WXHqqrHr2zhDb"
        "TyU+DLT9lGJq0t3Pti4Mu/0jqzeDb/fthVrW9A+srgzF3YYr3Ly8qzfDfCm84xwK56Ke9rxF9r5d"
        "/ToU11395NDu6kej6O7qOwd4//0c4109R3lPfsg+uaMvn3Yo1rvv39wCqqffZuZRpd3PXh5xPh9r"
        "t41HPZb7ebzfaYC5eaYjCX7xIA82qrv0xtFjnUd2cByay2n/viyXzcjIqAKQMf8wBQrjTUtAb+QI"
        "JfYEG5GxJ+zVBa7iVrUjwBQbGbpA0CvaCjbxJgGVcWJH6A7/GPMXgYp3duNMAYVXZGf5tbh4dlpf"
        "7BDHbiZbE3aJa6gx4dhCiTlH20PJNFtoxBozdWaGmqH0TaHpPOhQtsOTDokWTSAdhv9dIB1yARTS"
        "Ya5AQR3eVAXWYYS+BNZdkd3xm8kPQkAdRvFDQB2aqQisw2RDE1h3x8xtCKzDKL0IrLtvOkNgXTh1"
        "U3tSETbqfns4vJ5vUBUT9t6PJpnwuoCCCRMSQzLRHG4KJoaDUaFFvNQNwcSwGStY6F7nUrDRvBG/"
        "8iXeJK5gw/w5FslBnQwWyUPnx5sBEL7FneBVbBQH7kqdHof1365TyU/NlYn60Ux4e1gEG9ubCRZs"
        "LK+HLNhw97AITTuPFlSQgaAFEoywteCB7f1Nixg4xWBrYQLnPwwtNgR35oUBIbjfPYwCwXEKIfvx"
        "vikCPzgbP6Z8cJhDjPbwE0vuM7OpEMcGny6SO8xwKbnbOBtAc7+ZY4hgjoW550zTw+uHEA4RvJha"
        "OiJtw6ShSnjOPCJX4XJVgyl2lYjd8nCXR0t19hbwnuuOiFPolobTqzOD5CK+r2g4De7fCnEanJcf"
        "4xRpGkfEKY7CUHvKeKPaPcbRDEvEKU742CJOkf9SRZxC2EWc4huLiNNwbqwconKaiFMk6ag4xY4r"
        "kabhppJKOM4aIk2D6xsNmqbp241ha5r8XzeD2nSLhbkq1WUzdTEgzrefFIbL+cn1VK83N3MYar+c"
        "iG5APG9wCun55pNOET610yne51/VKfyndg7XuX7fwyLaKZ2KFfmeES505Ht8FhVJcjuFCixve3Oq"
        "7M72mkRV3bnYqfG1ynY6F5XS7xqTClL5Jpajxywcs3f0SIWxTtXDU3igRae0Yzc9ECFzouvRB/MQ"
        "Rw854Xs3V1et6sEF2RjjIaTAOdZDHEGmRXmIHtgBsx9Cxi12fQgTd2l/nofYgLyA+hAQsImlPkQB"
        "5IA8kD+4iyHH/S31ekD8zb047YHrdyOKnSRMuVeppz0Q/BZ79gdsYxvL0Fl912/b1FkdHkHQKK3N"
        "+U5pp5cOzWjL1lkdDo4Xqd06q4OjOlNWY7vQA6pxUsR4QDX2ONUHVF9xeendh2kWhfKt8iEneWxx"
        "2w+sxoayF1ZfsX16I+dfu+8HWN83P7A63cVCiOunPbD65se4B+9RrVweWB1U15cP9pP5qel1fy8E"
        "tWjp7sQY1JSPvw+EmnP3d6FQWS7+8foUu/23Vwbf/gYeaj7eb7hCUdzVcxx35Y0iuSuvFMtdOTdB"
        "42/A4CZmfP2hmO5vQGkU1l29+aMtm2cGl67ib4AZFOHdHSTm0l5lnc+jbaX1H25ixd+Bw9He3cFS"
        "BOTjyITDcx4neAhwxzr/4ImO7SgCxpGlUXh2Y2Kk8cDWJkR+VweLRzNW8qvAYzRqEyiMIz+GwN5s"
        "D0tUOgGyOMyzCmTFfo8i4DTejRI7wyZTSn53k0cXaImK2AIi74i/LYGLd4LiUwUY3omJegQCYg+L"
        "QD1MVQmowzb4xaMOY9rCow4bUhaPuuBKDxd14XkVM9QMs4uyEs3gURdcKemiDnt/toC6eASeeEIX"
        "SBd6QoldwQFD7AvHrO8SO8M5Cuywh6ULsMNsSxdgh/k7gXV4kYA6DJibgLo7RO9DQN1905wC6tBK"
        "VWAd6sE+jeLXh+JlfXsQTyidtbFc2Z3zJwjltBM0GKU9YGeU1eQhUUPOaUGEctrdQELpnfzMSJ2s"
        "OUbqdAxzqTObwPiRkwLHOJJzkAXjSdM7B5p5qzP6JqTDOb2TkNoHiDLeZG+Pr4w32SkflfGmtZ29"
        "0YR0OFOpRDUdp5PJOGKn8ItB3qaYixz/Q4H2Pu6sZTmP23srhv94pTiKxwsFT5R9UcQM0ySO+/gh"
        "2YjnOR5iLoKEILYncOBDpv/kaIcpGI5w4eNuw849OZRhFmBw/EJ6xOCghWtHFkcqZFCQeML4/XBM"
        "ijI0atM+twaNOyjiYKzVKeIg8Z4CDi63WBRw8HihgBM+Pr3HvePBPOulU8BBxRQKOHHi+8d93stq"
        "9Z73dn95z+/GIQfPdw45ONFzc8zBBRckdJAsvzjooPybgw7KT/aUcAfn4aCDczwXBx0kHlQOOpiA"
        "mBx1UP+Low78swXUyXcMnABCeab2DKCUZq/vFjAqz32PkPV2jcQk1f2MAGi5+gR8y2/1mAHuXlP9"
        "SfWKUJhfKhGBMVXbWaGsszmLnKy3ucn7rLxFUH283oF1OGeBedPyCMCpOu4E5ln4YZ/w+QYJUt5G"
        "BO+88GEPMs+wHzTa0cWdNM8xCtg0xLFreNLkTs41jCRj04wODxdY8VtoGCMxngYwRhKFx258KULY"
        "+s61NHHzt8Nz9ZatDB6md+mv8wBFlvfiqYl89s6jEqcSVp6PWHAePBXxPZ1H4V2atRM9IjcobW4e"
        "eldTKk+6uwK8Ko+3JBPdkoTHt9dIsvuimYZxAI007PZtNNLCneUzlHwajTRICs00jFo3DTWcDrh4"
        "qCEJufJQw+l7nYdaeAVGafF7Jg+1u5r4OTzVcMR94amGow4XT7Uwb6KEbuCcLRn6weGZhqzuxTPt"
        "LvYeHmlXYk8ntrBodfJIwyaIgGh+0mYNoOYnykZc8w/ID9DmisIpQVflJLfEqn6iFQn3XQHk/Az1"
        "aBHXz67uEer8pOod0c5Ppt4R8HxZOJHoJ0+HC7bSqfUlcw/nroDMP5wj+jMHWeGw178G5EQM9K8x"
        "CMe5fvJz2L/zc57Dca37tngy0pV9TkRFP7G5p2TEtt2d4hCHto+UgdjuPVPyYdkyx114DP40H3X2"
        "bptWc55hrbqlEMNm+ZaTK1yuK3Z7MYxKko1NN5g5jLKL/6xn28y5g9FgyWGDTcwnRwye7TlXMFie"
        "OUzuKGzsnCDYgXxybNxn+8hZgVzgkgMCOcAzpQKGCzkVcEv6TqmAFaKSUgHDop5SITzealqP2nc9"
        "Lf7RbRagj5QKGOvOnAoYFp2cCrg5oOdUwJXvJccChvMlx0J462Ix28yekClmo7kHJfB1toU6M9tt"
        "LwILWUqt8axzZVs17e6cCsiInjkVggsv99fLLdRcyf31rgv1sLH99e6LeHWvGSa6ZML8kKGZsEox"
        "JRPTqoslVefHatQtmTCi2/56rUZ8pLdl4ustG/HaZbdsSP45TROSf1rJK9u4kUNNPd3GBR3xkqBp"
        "Q3JRqwu5jes74uPJrV9KkZx0LrNdJC+1Ur+2cdmHulC6jbs/whXDZbVLldzU2rS3jZtB4vVusxxN"
        "8w8T511r26VFFSzxdS2UBJfGh/Hj6j5LCxo3lXdvLVIgBbhr4eHqRtViAr6vaYEAucci/ZHGO0Tk"
        "I4dziZxH7u0Q6R4k4cZIDxZuY45jZXmL8MYEgQhslLSKlA5mJGI0Iw1C5THqZogQ9nOLY/AGS+kx"
        "bYO0jRixyFnvIleR9aGxFOdaVY2lVzeOxlKkDx+NpUGWcsjSqzP7yTPXme2w8u+rIkuRtF01lmLN"
        "WmVpsD4esxTTE2pPGXMKR2RpMBkRsxTCKrIUO2u7CFNstx4iTDHtpfZzIdwiTDEn10WY4shBlaZI"
        "FdkiTYPF/5imwR2JMU2DPH4Dp2l65SkMXV8OXzZgmyfpToa9eWZ4YVCcp0pXhsypmUaBOjdDTYak"
        "VWz+qI5s5lBQz7N7D8X41I4NYN2PCxcBHr9L9uR9uL52mklMBYu0NGRHPE9nP1Qoye1w3fTUDjdz"
        "kmZ723ZUZy51FioKZXbKrFRQSr+rNCpG5c5c9JCFfNmux6kgFToNTsFCdRqRgsux0jCEGYijx56r"
        "/TwEHGiXHmUwMjx6aAnOXc8DCpbG60MUicWka5X6EC+u2J6eoJyrfMpDYLjaT32IBzhfbT0EgSve"
        "/YH8t9jzBfdXvMYD5G8ug03AwonPC85x2vx5YDiS5dcDuG9T2a4da7EoXXVaYwNr12kdnGOe0jq4"
        "Qy2lNfaQL53WmKd6oDXeu3VaI9/jgdaYRKgPtHYTvnNW49i3F1aH0wmF86xtr75yrmX+hgvnWsfs"
        "DBbOt7Y9hcY51+7rgdUgwHxgNfK25gOr77Ht9aUX/kPcnrre2GOwHliNbR3zgdXBvguD1f4JzBSu"
        "3RTwPRli+9nxDLPdjPxJYdvfpkCR25VXakHTlx+G367cTBs4dMXbdPjwbjMplCsHf1s09w8e5zrf"
        "/vs3xXQ3P31xfXBfT5HdlZuULLTzLbIv7uu57rhbfps6rPv9o3e7KdB7+movL7DuVwoFe3dPhDmY"
        "qf17ted8fHBtnst57AlvPNyRBbF5pCNlZvIcx6EAjYf31azFExubOwRM49p4Hs23qu2R9Sdp0yZA"
        "GNkGWyBvsLnCxy3OWCsCY7HRfQhgxR14Ak0xxt0CQrG5YgncvENxc9W9nER0BELeGYPeBSxigkNA"
        "ITZtbIGAmAAqAvaCu/5c1vnXkrmow1FhnUcdshs6j7owo2XEmiH0U6+mFx51VzM3j7rg2nqXdZjl"
        "2QLrMAgXUIeh0RFQB+c5Auri8XLsC8ceucXOcNoRWIeKULqLSDNRWIcj7pSOIaZ2tsC6O+JeTWDd"
        "nSAw3ajW+E3tCLDD/qAmwC7O7Pn9WfHxHhJnPC+Y6E72nGDC2cgiWDDTfsf3TUzJhIm3pTXItKnK"
        "mxhmhtGRTBSvf/ld1yrlJ5RD8k971rw0rUq9JI1vl0Py0dE9nAs2mjfTq9RHdWCv2OgO+5U69bq9"
        "vI1ZvFlgwcb0cqsFG91LDBTqY3vLeEqdFi2qBKe3h6Hk7vQ4S4sf2CFytKhxdUUMFdBtLT5g58zR"
        "gkK4U2fnutE1/Ie6iPkQFhH08Rtzl7EXM0vuM86uxtxppjm3VXKvsUc8JXebcURKQ6eiGZV6RB7j"
        "PBGRwcHZnjF4sSGlibTFTNsSERvv0uuEix8NptgiMjWYXt1uGkyvbmwNpldn5lUOQtc1mF5dKxpM"
        "wy0wO9UNsSsdySKUQrdElGKiqIkoxbEfIkkxy1RFkuITp0hSfGIRSQrhFFGKonYRpRBWEaVojS2y"
        "NDi7M2Yptk51kaVIghoiS8N5w0p4TqE6pvkh44NBa34jwWZIm+7VmJMBb2qmUhx+uW7AwHJqZlPz"
        "IG+l2XoVLwbi+ZUEm4L6yzH1FuPzo/o55OcbWQoVAvLybCoi5FssDhUgUjubixepncL1xPN2p4JJ"
        "amYMKrakn1UrFWrSLR922rHqzqWaU2xVdWfzrlYrLqX7oPahwlRaz3PoUStcsa+U1t5L2yitPRXV"
        "Ke3YU49EGEkWPfzgQoauxxyM0poeaDDA73p0QZ5Eewgp2BMyH+JInGxButYZDxEjzkLhnOu4m+AZ"
        "sZ3EyLnXqfMhCkD8wn5s3ykPwMe+jvlA+ZvqYc9qUx5WmrtBnnlzqQ8Qv988HsCN41t1WGN//tRh"
        "javVpg7rcGdH57St6LDGcGzpsA6Hcoss89ZhjfyTosMamR71AdbYm7EfYB1tg6lkoV8690hTGQ+o"
        "xpGc+wHV2Abz0nfH+anjAdXIqdgPqIb4BdXYyjIeUH0zVU59QPUPcW/9AdX3zeSypeMkL53sOOPo"
        "91r/XgxqvdK/IINCtn89RGGo7cq9LYicvG9q+t2XU/j2L+Gg5nX8fTzUpLzbcLNQHPeviBgUyv27"
        "IricFv8aDS6fxS//pKjubifo3FKor+8U2/3NJIvCu//9XGfcbz8ub8XVm33Myvqf16Vn/a/UT6Vo"
        "775/Hwr47naWzvXPXf9phcc+RqyHZz1u/yg84DEZMHmq38kHc3p6xJq6eX5Ds3hoBxeQuKQOT0Q9"
        "cV3PJTD5ziT0IoAYx3Acgb44HbQIyMWbisDZ4DoOH67BnSM+UXFMzhEwGotihzizCcDE3R1FoCSO"
        "wNgCGu9cwzoCD3EVShEgiMNUFPLhkhiednfQ1ydPu+BOD5d2WMkdPO3CWYMRaz5CbxWaytMunA3Z"
        "cb0ptMOZGFOgHUa1TaBdeNhkqUnxlkA77ORoAu1wiGYVaAeRQjvsGVFoF+/t2YmoCrTD6RsK7e7I"
        "m0xc/o2ojSLQDptnpkA7tFMTaBfX3o+H4tR4eydLruzH3sxHKJ3kDULZbQwySnubCqEcJhGJqv3Y"
        "XCSU055vZZTO0hgh3c4AnZE6u50J6XEy6XLprM48KyGdzqYSQjqczGSmwM7pnox02kwlpM64m1Bu"
        "J0U5ly5vDSyX7uKsgBFvbU6iMvGt3qH7TNs0Cr5Y6e8UcbFAXyjMYtvEotiK3SCTAup9vB+Kovfx"
        "eSh2YutGp4CJmqkUJcOdAR/vcedUfbdZZz0cA5HGXznw4ciPxtHuDr69IbH3vHeEsVcee3C//PIv"
        "jmBIxCkct2C/crDCWSCNIxQmMwaHJZTncCyKN1m47TvtkzW+PI7Ecwo6uMJiUdDBtotKQQe7Jg4F"
        "HWxe4KAD65OCTjji3e7jvVPQCRPMDeqEJz0Ut1ndW42c5+3Z2dJ8+yR17vOncNTB1RWDow7sk10o"
        "nFdK9pvi5932XYWkTphYUN323d5db579yUEndJ/qN28JmJNnOs+AQWke+Y76QWky+4m6Ram6R8DK"
        "NxkE+ErFnx3QLFWXFsAtv+UjYl3eYCH68rzvkIS5vERgzLP7R8TJ/O0hNvMc/B1RNJeHXbk8xX1E"
        "jM1vCgk7eo/7PFivs5fZK+l15XN6xOc8G39GuE6T8O0+Kel1JUJ5vn1k0WhHMjTPcyxYVhriuLdx"
        "0+TGUKzRuMYu7klDGgvQnSZzuAF/h9/iHCIeVbKXcRm15eJhGzZ/Cdt/293hFr+n8izFMmjnAYok"
        "+clTE+vOhUclrndoPB/vEmgbPBSRz715Et5F3V55/N2Mde9Ygeg9n8WDDjn5hwccdhBUmmo4xL7Q"
        "VMOgZNJUQ0e601QLN7mPUNI7TTUs5tJQw8zCpKEWnul4Iolz39cn0pwmdCFv85/KUw2DusVTDYcF"
        "Cj3EMO23hC5w1uaphpTqylMNA9XBUy1OGj9x2QZPtbviO4VO3U3u/hSeargYofNUu7cSfCpPNdT1"
        "CaimJWDWRDVHtMrr5hqvE+DNvypgBIRzVZ9oetBVBZjzs8ejBV1XtQPW+dnWM8Kdf+B+BDw/tbdH"
        "zPMzqkPsaXdhlMw5nO7meJNl7rG8w08SmXf0SVYlIQjdbwvnHv1E6BXR0M9/Drt57ttOyEQ323mE"
        "y7F+knxJyYg8053iEFcUpgjEIs5OuYflyJPCDvusd0o4PFpTsGH8OlOaYS20pgwLR/i/Axf2NM8c"
        "VzhQv+aMumXYNQcT7J6cRhi5nRxBGBnunDv32bi/9bsD9WdOGIyCc6ogx3bnLLlJvKvmAMGAcuXU"
        "uHbbyFERDvCr2WzOySi/eTTM4azWo5OgAk7SWikVMJgqKRWwRpv3e/BoCgWMGHcKhWRTsFWto+VQ"
        "wACM6MMgT7flULhlYKCAgQkBhfBG+zLsZ3sOhexmOevZUnMoYH6j5VRAGVZOBdzNNnMq3GzamkPh"
        "mh0nhwKO+l85FFANX589X2+8iKbMm9FC5+sNGKGJbplokgkjiJ6v92OEJoxx+Pl6XUZsYhgmpvYh"
        "VossxUT/WHWxJRPdKsWRTJgt8vXmjdiG1SSlaDYs5yr1J5Sj/YRySC7ajcyDY9ziESdyd8vG1NzD"
        "LIfmpcYU4zGu/IjTAkwbkp8O82dfJT+1ujbHuB/kwYbkp9ZM9zFuD4mPX7QYVjU/LVMLKzdT9tO1"
        "WPJD1+bUAsjVmfXVc10rWqiArmvx4epG04ICTp3XAsGVGTOrIf2vblUR+TjFv4ucxxu3CHcM+4dI"
        "9OC8+hjj/kHnMbqR391EXuNKhSpCGnu9u0jm+I2HeKOI4Dsj82kid5E23ETYBvvtY8Iiq7+JWMVm"
        "g6Gx9EfXvh2RpVe3usbSq+tVY+nVqd1u6JrG0qtTWXp1+2gwvYnY5vedXGcT6pMKhzmCKLnHjKH2"
        "lP2s+pilOHxuiSxFEkATYepPAcUsDVL7Y5biSoUtshQJ+UtkaZDtEMM0SNKPYRrcMxnDFJ56RJji"
        "Qga1j4ofIzXfkaUJ1nMYtqZmFjXvkZoZFHlTM2bndMhm6mG4nJvZDKZTM2b03HpLUT3izEyjiJ5a"
        "KdysSGrHnCcq9ef8Gorux2dT4SD/Li465HYGFS0e63np7c7NmOR2DhVaUjvmbFSV/bmXQgWe1E7l"
        "OvXpd22uj5/a6YeKUo/tFZvBzMHSIxVmK/TodKXmT6dTWpu1g9Oanzs5rdlci9Oaw8JN1lXTYwua"
        "tz6EFMy2zYc4AnF9CB632Hs+RIwrXi9h4orPfIgN+Ob2EBAgHg9RAOL1gH5M57UH3uMkhfkAeUyW"
        "jQeyY8KsPuAcJzrsB4Zj2nQ9gBu+/TDEwNzE0GmN+ZCi4/qHtp4HXF+t+b2D086u4/pqx9JxfbUP"
        "tL7V/Ck6rTEltx5oHez/z2mNGxNfuvrhjGDhXMtemimdrLDzQGsUez/QGsUuD7TGVOh5oDUYsB5o"
        "jXauD7QOZxwr6WEvfW9Mrc4HWKO+9gOsQ2h++WIv0bbZIxdWXs2l1kbLJ0VtVz4YbrvqTqW6+HKK"
        "3q7cRNKm2+1Dzcm7cnuB7EPrSZT77+dWPX19o4Du67k1UP/7uTQWUT95PcV2V26yrvDeZy8h8+53"
        "KMa7FyjYCwS09/XBod7VFy5Jxf38xa2k+q0/eOYjwaTzoMf0yeTpfjWFJ/qdejCD54g1i2c3Zjg2"
        "D+yrOYWn9K2Bung0Y0agCTy+g7wqMBgDwy6AF6Ip0BYD/i0gFm86AldRD0OAKURVQChER+BmcNai"
        "D0vkExUBkWFKUI09YphpPTXxiDUFAmIWR6AeZrsWjzqMfCqPuqtpPOkwjm486jBN0XnUYajfedZB"
        "03jWoWwC6zD66Dzr7jirKKzDYYBbgB1GdEWAXTzR0BJRFWAX5tWU8fKm2B3aVmCH2YciwC5+U+IR"
        "dQqwQ17KEWAXulFNPMJctawJHdYWaIdpFxt2vz0xPt584YznBRMfp9fHm6jHyecQTHidQqUUTidR"
        "qAtznLgUEzbutmTiOJQVTLjLbIKN6g36FRsOkQUT3Rv7K9Xh4FophgNvpTK8jSyKex0H7YKN5pFe"
        "seFwXzHh7WP57k+laj7q7mNRHMzrICtNW50QIgBsFS2kYOi/tDiC4X/RgkeWbpHo3A519j4tMmBo"
        "X7VwgGHt0GIARoFHA388Tv3kwiYSPh7j5v7S7ZnERgiXiPBYOAjhEWmNSt0iovHGKnIZwiHSGO1Y"
        "RAQjyULlLnbcTBG2wSUTMWHx49giVjEXIXbPsb53NJaG+0NaqpN738iDqBpLoZsaTe/3labRFOOx"
        "rtEUq8NNo+nVdbXvjHGt2mGOhbnLyF3jeFdB7jPOLG/uNE6SEeE1JmlK7jbN3HJRCL+xu+mE47Qp"
        "0hTCIdIU20pEmAZ3bcQwDZuxdqI1JgPTfHcEg9bUShkMaTMz5VCd2NTMHgyHczMMlXMrVJc3rWFz"
        "2nLLZtpiEJ6a2Y0iep7XvijAv+9jEb/rUPh/rJ6uf1ajgsPjtpqpfxcXOvK9VJuKJHl5DhVY0nq2"
        "t43o7kx24nM7hwpDqZ3BdfHz+hlUkMrba+gxCxMjS49UyFx4CE9Xa452OqctRw9EV/uZeviBdusx"
        "B9879UCDSaiiRxckzdeHkJLuY2HEpT4EDxS7P4SMeAdNJ8XjITjExZ6keD6EAWTqzAf2xxXGeVi3"
        "D+7gPMw+g6VyHjbqA87j3Tekg/X6AG601NFpjamJo9MaW0KmTuurrQ8jCGiLTuur/Qyd1ldbik7r"
        "q21LpzVyXB5ojRShB1hjcN4eYI25q5eePkrdHmAN8XiANYb5L7COc0I477I3lBXOvezTysom31we"
        "YB3njJAeZmOP9LC2H2gdT1WTHlZeaI1fM0VrfysIlffiymtnmO3KP5PBticvh8p18eWVgbcvXwy/"
        "/aqj1ja1LUCHldtd9q8k9zeCcFP0/v6pTfHcL/+ikC5+f/9m+Qev59juNv/h0ld8PTep79cft1Lq"
        "b8Xgpvj9nTCTQr27FcVs/8r7n50yzvufGWFr59uv89hHFobA+mi/SIslTYA6Zh8WT3LMsmwe33hP"
        "4ZmN00EWD2pUdePpHA+vP6GofxQOx/tSYk9opwjEjYvXk+IVga0oXhOAGn/TStqpC+iMj/GIPaLP"
        "LkASkw5bIKM2U/Hb0u0tIBAzEwL2UOE86sL9FTXUuGfyRZrWeNZhvkHotWKuYPCsw3sqzzocrSF0"
        "SpE2I7AOg+ojsE6cQPjdJoQlsA6L7ALq4m0fsS84zB+JSOk7hocllNgdnO3qO3nTEVCHZhoC6jDe"
        "LwLqYtGDQ9TEIezuVgIHezT/6zPxmp99gBChdPp4hLLYa2SM0kQgI7QzkAmlnTSXC+0+zGaU0866"
        "IJTdSbQgpM05UZ+QeqdLMAW2ifmqZJzISfMd1EsdhDL16+wJfPWHQrnSclbACKlzaESutI8Fr4WS"
        "DpuyhPTjwJbxCKd7SeDB2TD9eyUWyRaFW1w30ijGYvjIgRU5EoPCKaxTCEXRKW6Gi+rbfXx2ipDI"
        "z+8cFsOl31L85wcHQCThLw57eL5wsEOu/uAIF141Udy27btwLItva/Gb93DQQnEWhyocwUDy6T6/"
        "GgclLP4fjkThLTjVbV4nQfrL4+j3U8hBN7xTyEFvtVLIwSEOm0JO+Ph0HzenEJf7+OF6aBgBNAo6"
        "yPEeHHTiGyPcZh2fwkEH9g8HnWu/NA46sL856MTXlUy/+jcHHTzPMQep/GRPKazO6javmxHkPe+N"
        "N113GBx04nVrv3ntmPLj8TSV00zSqay6l4BJ+cUQJUBUnkm/AmLl6hIA7C2Lf33ruzerNreoHFZ9"
        "SgS/50R/Uu7l97OFD0elj2nmnS58iziay0uE1cdvX9+Tb7rwIYTz+xMiJKfqMyJCp5dJfHoE7Pxu"
        "jB3xO5XbC+O009Fsx4EFgwY6zg4YNMWRic+jG8uuneY1Vp5pRofrzksv1w7r2MmPjyTeAkmgcdYY"
        "y4MmbH8nqTF0gHYqz1KUrfAAzZaBQ83gUQkNj8fwMIsSuoFzXmDoBsM75TXStMIzD2VrPOiSowxD"
        "b+OZhuEjz7Rw738LJeaBGD2W0EjDAnOlmQYJjbSoWDtUbL5TiSW0xRMt3AhewsZ3skfC1m9z8UTL"
        "8sIjzeGBFk36lNABnAXY0AVaLzzQ8B6hkxeeElljLxiVBxo8R+jEhSv4NfaCJhANrIkWef2D708A"
        "NT+/O1p4cFWtB2jzM5qjVV1XVVZAOP9dAeT8qwd2ADrtroaTqJwE308m83JcElltEfT8QoYDZO3y"
        "i9LTQvYIf+KdA/Pt21Yq2xEI/ULOiIV+GnGJcOgfpL8jIrqyGi7KuoXc4YjWv+wgXA0R2+03KixN"
        "lhSJGILVlINRynM3nxw9BR5GjTWlHB5tKdvCo/m3WQE1pxh63CVHV3wufrGfHTmk4gv3mv3sznEU"
        "pz4Pwe60n505beId3GazOSk5Zrv1tXKYYJA4coJgcDhzbGAJt+WswGBw5oCAT+6UCujK1pQK99GU"
        "CdibPFIoYDB1UijcR3tJoYBHRwqFMI95m9/v3IZkPXpyJmDBbuRMiM8Is1trr5wJ8cZbs8Wc3+6w"
        "q4HojIRZxGab2Yv1ZfNmj127ORDCQ/6q3Wj95EBAQ5wcCPjlrhwIwSGI/3DHL8fYx5mvlomqmLCS"
        "3/9ho0k2tlmOrtmYlo2h2SiWjSlV6ccsx5JsHLMcW7Fh7RX4h40j2Sjmt3y9cUM9xv5fjWiOaqzG"
        "/auRqhkxbUiuanWJ/tVI14yY/l6G9jV2vWreakSUfzWytBa2P0fz12HakPx12AWpkr+ObrpJlfx1"
        "mG1TJXcdtqtVzV+dkkj+ah2IE4carK2qASZYYY2jCq6E62IogbCI8QNFFWMGBuRHDBTBPe5xdAiG"
        "qnFI8BetkjCAdOKqsh+Js0sFPgaBKuWD7ZwJ2vHKrvI8OBo+gTj2kQ6V3HinSuvkM3MHGrWrYMbQ"
        "e6s0DlLBEwbHjVIJF6pDpW2QUhAjNli3ihGL8YNIWCzebJGwWDIdImEh7CJiMbqvImIxGlURi8Ge"
        "2usONmUmjMXiYFEZG9xpljAWKcNdhWyQW51A9v9l7c+ObNtxJUpUlSfCJNiLU2alvwzv3MwArPYJ"
        "NO7c+b+ckw3WABuQsNp2FrJ2FCosZJOceQVk45jtArJ2en9YyFqY+2YhaxHdk4Ws5dITFrJJ0HwB"
        "2eSFtAKySQSGB9nyafNxIOaW5fgr0s7XByJyXR0M0HU5GK/rciB6170zIJiX5fi4vHx9Job6ukIY"
        "+OtyBPMDdcvAHZbXLuJNeoBO47Ug3qgHuOPyOPq8WQdrNN6uL+Z+6pwagnmj+tLJxZxT3bKF+aqX"
        "nBiu66oHbT54sp+1RvNnt4KJx3rwWSbeD57KxO3BPanYX0cuUDwfPJFV+8H72Ej1B5ej4nVe/Iyq"
        "/fOUBppYsGMI2tgZL37E1C++wyp+XhyGqdeLlzD1fHENpn7xB0WPY5Ymb+i3cJ/2wnu7wNJfIJ8k"
        "mwDIbur2gnPrc3lg+M9SJnAAgon99UvHxP5+wwC//LLEMPEDwlXb9wPC0w8fULsfEG6jPF4QrurT"
        "XhCu6r1fEG7ffiG4iZ+m/9Zp+wXhpn6a6Nuf474g3NTnheHFcGOmFrEMMzV5QrhW3N8TFNTSxgvC"
        "zcrPC8LNWBaE8PAF9YOdj4b6hW0gkfqB6zGcx/oOIT3WD4jq8Qv2HSJ7fHWjQXBnXtB3+R7nDwAR"
        "H9cAnKjHBUyM9HEBA4M9k8XA5X1cAEZ8tgL7bweBsMONoZ/JguHSP76ctTAPEBeA+YC4BeB5AnPl"
        "y/UETC6P2BnoIuA2wgPYUm8Q2DdRJ1if7yHMQrQJqpvoEijPe++kIvEP9W4uCiDx5aog5LAVqsMw"
        "2VQUiItvjUI1GOTaUp0Cbb7Ab7tQNQapSeaGhKN2X2oz8LS4sc0Q0761GE4m97QSOCYPfSRELHre"
        "FxVLgFy0mdlvujAdxYeEoKCtDQ5BQfsSAUFrkRAQtA5nIGirvMVAMEkRkEDQVI2BoKkuA0G7W9QZ"
        "CCZpExMIWh8KA8EkzWICwSTBYgJBaxc1mbQLYtQMMrmqlUDQbpgJA8EkZWQCQeuNzkDQxiuaC/75"
        "9D370uB/mUiU4e8+dqqMHoWXMGVEBGXaEt3OYfr0BIDFy+j+lOkwZQz/aPpyZYSbw0RjVjhDZQqJ"
        "UE2UEZ/5EV3SQpAzrQm5ThQyw21kopARQf/vK0KZa48jv5nBCW/nEIWMcNZMFBJvNjB90iN38tcs"
        "Ec5ggztpcRnJ6wm5h7H1hJBuJX6gMHclpmuk/7CaLtJp2PUc1lPYmxxCuge7nrNJn5A8FVE4giQ7"
        "XUF/S/8gLPOT7OoF6O12xWLpnjxOUSA9eXyv4Li187D0zi94tfOsRGzosHAubsvUNjSGsBi2dh6W"
        "vTYqnQWu5RjpJGVtZdRJyubLnF4L/a3AUQsHSdl8Ab1q4W4kZfNrT6cW+udVtxSOOGy7UgpNWbt/"
        "0ljKJk/5FZTNL2a02noiVtb206ewlE3euikoa89X0hNjG5XNUjZJzVBQNr+rJQ0w+MFSNslRWVDW"
        "cqlslrJ2K3FClK0CpL8rEHTLcs6EGFyXAxG5LMY/aph8OQMCdl3Ogvhdl3MhnNfDPiC6l/H1wcW/"
        "jy/oYOyvC5qYKygLwvzCY0833qQv6DXqgi7mRF5rxFv1bZiLeTVH3q7bwBxQWZAszB/VNQL3YuqC"
        "wDVBXZBgzuv1L5uXo6EN33pwYD/i7+4Hr2Xi9uCrVHxeHJSJ5cErmXg8uCITv/gfG6r74HRU/ORo"
        "THxfvItda+ovLqVQ97+q+QC/PV98ht3IenIU9u394h2KXgMtra8XP2C3yeQF/hag1V6Ib98eL5i3"
        "EesvbM97TUBbk/1AcQ2zeFmF/GiD+UzHxOc+QNzE8wHiJm4PEDfxC8Stw+QB4jpS38vKwYa5v1Dc"
        "rgi1F4oXagFrLi8UN3V7obipnyiu6iDmeYHqpzm+qdcLxa3d44XidpOtv1Dc1E/zdqv5eaG4qfcL"
        "xa3PxwvF7e+NnZGGIfqtQSQP9V+HYB7pgxn9wPXY1n6sx3b4yfpvvP+woJtQL9gcPdR3cPc/LmBj"
        "kI8LGBjn4wLArZ+4AAz28RiAOz1xASDy4wIaRv24AIz7cReCGzlhAWNj9I+vzIHT+LCACZ7axk1Y"
        "mBsg/0pCGCLjDGwdMAgPoKI2CeznWz+jEAkBeBM1guomOgTKrSM2we982Xdz0WwMqW11y9A5XxI3"
        "eflUYROLgq+pJkPc/HpZW0/f2k/tOk/fKizjMOi0K2aD4WX+eo4UlhEcD1emIQwO7b/FMNBWD5Ng"
        "YL5Y6rnomwQDTdQJBubbLOulervoiEswMF+w3Vw0L8PA/JpTK2xiXQaCVkMGgsX7GIVVTGraadsq"
        "nYGgjdZlIGjfGgwErV2DgWB6w0yeLEMKy5ibgWDeLClMAw2k/pfKZ+B/f5SnvQlCpwHpDrYCAOkK"
        "EuUg0oCNiDQIFkG6ycdkrQyCjw4gHRJMGwFpiyaPQI1v9B4roI1ufCPS6KkloLlfdAqHfDeaWwLa"
        "8J08xDCi8zekztEjeYhpRA9zA9odXY6stfOLbrwA3z0RgQFt8CQIZlfRiRswRhNjst3TmBiI8wv0"
        "Pfz9ahhy899Psj4rbi+IVAt4HxhHk/ygLjzt9xckpkX9NxCTRaaTcIij9/7DMY7S1Iy4Sgtkn11d"
        "2SDw8stAbbNfOOw4xCMdPnMRCOY3QXIVX0hGeoCMyq9KSTjSfYI4ShKKujiy3CYgjuzCBDgDtMsn"
        "G8OR/R7EkdUfxJFF+jcMR3an4GA4slsaHcRRkXglHOERnsOEX0BxZEk1Bogju2DSQRzZnYAD4siu"
        "kywQR3ZH4oA4sqweHcSRZZK5II40y8nXQRzlN34kHmmZII7ybpUR/30kw9FrsC0q/04Gq1q+M3bV"
        "8nQFW8tbRrbH6PL9d113ULlIhsFani9ra/1OIfkYLd7kL+sPW15bKVFrfb7WfYxNb+vv/rdt/6Ue"
        "N7+bwvkx6YnA9rdGiu7H1D0C29+UFOyP2WMEtr8gdMOV5xHWkmraxQGfH3GPXIOTPD91Xrlm4cy2"
        "qgkOauvqg9M5z2YSIDmPom65IcxOwDfPEdNyU5iNwKyJGLbmZ+jrpR9ycxiXIKd9aRO4tCPjRjDS"
        "TqcXAUb70iRoWJ5Np8M0Ce4VVuRq8nM3STWCsy4/yh65RnDY2fHyxmGXR7juvG4dh10eMX5TDQW7"
        "4rQ3N4S5Cdjl+VBabgvjErArTpVza+jM7DEPE2+5PfRB0K7ovdwi1iBol4caSHswI8ktYnaCdvng"
        "yngZpx9NHEQ5MuCRQcS9lKWHIGS87ixlM6MfGdW5y57cGQPjONqdYZDMWGEkJD/X2uP3SkNZ+Yo7"
        "1qVQjIOK80lgrMsngrFupHSMdflCOtTt/LCFzK4hlblIy49e4hwG+QlMXM+V8pJNgDMezfoPWXH1"
        "1P3t6DUf84vAw/9tr0lov5Uaf3kdtt8PUoPOZvutppstJzqANFuwIBzLVzfNH7owEQ1RjcH82B+9"
        "8BUS98cNwJD9GECP/fYAvLEX+xHIWFIAAchiJR8AJ5aX4wIMKVMvuhbaaloUE1P3twOYTeUr1OH/"
        "dtW0SEMYl//TWcMin9Qfv8t6DYsitd/n/TjObuWVfDcAC/sxMr2xH18AFkUD/cHbyPQljdxt/vDt"
        "CcDCqozAwnIKdAAW9uMDwMJGWwBY2Jh0ABZ5KkvxB9CLgGi/85fkMWzNK0OoMrzxbr+zm+QvQ1+v"
        "jMGVcbwyJlWGuP2xqDI8yrTfuVHymEa3jEOVcd0+vVQZx+3T34lU8oq4jWmUpQ7f2IUrw7XURpnq"
        "8OIUm5ODJa+JuIVMzkjcAW6UtY7hN2f/D0ytUfY6t18IZbDLh4BQBrsCKlIGO49rbEJZ7Oyu2Qtn"
        "sZ6nb05mmDyqfJDeJovrTV2MRTQu0q+osLPOxF7OHqQHMeEi3UYWtZn6CouiPaSDsEjUTnoFC5K9"
        "rCtQpSyW/1rZM1jqW20Xi3pV+mbXavOZh2W6NjNwkAtQsvAuWlkb0Oo0plXp11ZqC1ptskC2dtIU"
        "ViULXosNPyxt7a+5ScRadOYkEZs9Sp4i1l6/7iRiszDyFLH2RXZmbk98LxKx1quXRKwFXpOEtQft"
        "B0tYjRjmCavKxgLWPnlZwKqy0xNoq+xgCWsx2JslrL1n31jEWhg3PSlWZWAItQlN32FKbULRxBkw"
        "IZqw1kE0Yy09wWUZa5Hv2KbJU6Cxg9y6HAjAT3G7Do+f4ocdPNfldIjWT8+AO/Cu41InxPK6nA2x"
        "vR72iaH+tSDeoP11QeMtujfMMTz+xRpv1IGr4q3aX3Q13qy7YE7lKd7b8zFlQf4eQeMt2/e0wlu2"
        "vygS3rL9Kafwlr075q/qWwIdc19P4fqlN8sCu0sXZpHk88FxmXg9eKss9L90Uckj9qVbyl6GK32R"
        "xT+cBwdk4genk3+48jRmIy/eJQvNr11K9mZd7UeyeJPaeRTq+Tedtv5qvEAz2y/uIAsfqX2ABjq8"
        "YN/iHvYL6009XgCfRQXVVDcr3S8ozyKdSn7bDfv7wO8sn2HJbxP3B37bxf2XJYaJxwPAs/yWJcCt"
        "zS8rCPvyeSB4Ps4VwW3D7bwg3NRPq4Li26CVnSeE5xuNDbSzYDoMGtp5mt6r+p4XiNt259NE3tTt"
        "BeO2R3teMJ7vKQtma08Qz61cQEvb2MloHCKMcTwO9T4QyqmQdofmsb5BQKfe6XaYTt0AcLBOhYQ7"
        "ZI9D0RcE9/j74LY/FXvvIZ4tQP6yCxtug8EJ6PjbAnArvA0jPlsAbIfSwPOCsICFkT/U74XBPyzg"
        "gHEzcQtAFxAW4B9oCmyIIgNzBex/yddnF51DF2BLj0tw30SLgH2+kJ8volVUrxMszy5UhAC3Lr8E"
        "tS2Y/zCoVhW6i/Iv1WWgbBcZNkNi+9Zi8FvUcBZ9OBnQmmowdM3ugMRIVVUwfS9s42yGnvYK52WQ"
        "qao5GE5ab3QGjtmlm5iINl6LwKCtfDaBQZu8DwKDJmoEBvNV/MxFuxMYzJcUu+g9BoMmYjBoKzVq"
        "xqqq4NArt4kgfKfJ07d6oaJmoVZDCoOmGgwG8zVy20W7DoNBi39iKGiixlDQVIOhoKoWRUGLeWMg"
        "aKPFMNCeWI12d/986T99lz6aGBJFSBRHTZTRomkjU0YP8EmU0aP9X6KMHQUE4mV0/89xqDL8df9l"
        "yhhfi0hMVMSP4GqUoUYUpEy1x2d+TL9GECfKOOH9HKaQEPHM4ITEZ2oS8Z8wNQmDEolCRhifSBTS"
        "Q29BFOLHEwtnr3FEyF//c4SDa7D7FJdhS4lOehhbTZBeJbtqn7oSEzbSf1hNG+k0shQJqaewG0iD"
        "dA96BWCSLsF0tB+wh+YbC39tZHw5p1JeGvNW283CPUv/kBPdviksxu2S1mDZbVdBaGLrtZW+WEzb"
        "ZavOstmUmwWy2e1mKWyjslj02p27w/K22BiKhXnkgdTCcUjKmpCErOr6ICFrH9wkZPOj9l0Ku7Bz"
        "cHvBn5142wUdmrJ2JeiylLX8BJOlrOVO2Cxls8wROWXtesVhKWuL+cNS1r55WcqaIdCUtQsoLGRT"
        "oQAWdCfLWLODyzLWkjgMlrH5bT2pLah/HWJsmQZhNQi5ZTlzQwSuy8GI/FjO5MvpEK/rcjB81+MF"
        "wbwu5kJsr8vZGOrLgnbHyF8XBE63X2vEm/QC3URd0MS8Rt00zIfUFTqYS6kr1DAPUxZ0MIdTl9Mw"
        "B1QXBG7CvNaIt+sDbsbUBQnmvF5HPy/nZ7HxhWGBiHieB69l4vngqkzcH/xTLl6guD14orzNBxS/"
        "OJ18nCtPo+rz5F5MfV98imUtkRdHot+++8V7mLq9uAxr93hxFEWvbbDXxotLKNT3b9Tyger9gvws"
        "L07NeVW/oD3Vjr8a61xsr0q+INzEDwS3FypfFhvZY6YlwbMnSEuC65cf+J1X+oDi88BvFYu88Nv2"
        "2+SF36beL/y2mt8Xfuc7hQ00st5f+G01ny/8NvULvk38NKMvjOX+jbHI9zfDLaCpyXrBd/Ft0NTa"
        "eUG4qbFZeBTRHa0rYP2eEMljvUAwj/UYz2M9NimP9Rfieqi/GNrDiPwPO1SN9QMDPFmB1vACBMM8"
        "24SOF9Aw2IcFYLRnG7D+7vsb//7CqB8W0MANnDhpELhxExfQMfzHTQDPauMCwCPbuADMDcQkmYQn"
        "yFcAkov2JZhvokGA3kQM3U3EIN1Ei+C49d4k4J1vLNxc1BqDaVMdhs32jAwFZHvag6Jw+vhLG0UF"
        "NwPc9HWctp4+ldtFGwxPs8SoMUTtU4shp32LoaV9ikKkjfBkuJilTY5pmCQ0Dglok/dBENBm3YMg"
        "YL4QH4VoEATMRasQMTNZ6wiGgLbSawQB8xCciICqmtTs1FSLIWAeztT6Uw0Ls5iDQWAaN9UKuxid"
        "QaCphGFg0YWFaczDMLBQFaYxFgPBvDekMA0OgsUuzM+v8mQ3PgprZXDlsCPSHdxWRKQ+G5H6Bve3"
        "gU6S4KW8WjqiOBBAOoN3OBBpD8gJaHs0g0RaG+3fAtpgDxQxqBFt3SLNDaiK1DjKV4P0VBSRgYxu"
        "tGVba2eLwqkB7YiW7IB2Rav15zoLZFU7oDAyvFHYBECMIALol1RjuKN7kdHvv4vBVyO978CIq7/f"
        "E+OsRZKDcM0TzOzw9+diGNVo+oGh0wL+F8hLS4qxQEhahQZIRhUskIaWOWWBDNSLFW2C5LO7DQvE"
        "nTWhg4wrUvKEwzzvAWlmKW06iDAVwNyybkVhlfeSxCPdQSxZwiqQRXa7HkNRHuDco98H71uM8Pdr"
        "YCjKH0pccf0vhiILIt8YiiycH2SRXcpA524WSd9AFtkX0FmaBfmjUzOrEjohU8EBWaS/HxNkkQlQ"
        "Flmb0UmWJZCZIIssb8wBWWRpVFAWqQAkkfXRAElk900aiCJ7F2NnKCrjT29GpscI3w7Le8atx7Dg"
        "CcszqD1+fMP9LhnyavnNCPj4dQNirc/namVSghSWj41v/S9bD9vdzRe4tT4nba3fKXjL3v92yuE6"
        "x0m+4H1MbSLfX+ph65OdUrzW59PLx0xMMuDx6zjy0wDXTBEcavdcs3Cgm0Zwiuch7evhOzvVRHFF"
        "vObmmkvwOI+WbrkdBIfZqSlESY16/qVOULY4oZ+5iMBprkmtIUrJlJpDC+8B8yLJ7WEwWCwy/OT2"
        "EKacTkWNoF6eUMdvUnG4lGr6wWFnmonDzo6VDg67XLNyzcZhl0drn4c+uA/jE8DOzhk3AbtClJvC"
        "HATs8mPQlhvDXATsTMTQrjj23y/Vyw1iMbjLM81IbhHhs7ipaBK4M5EQuMsP4SW3iJHRjg3brGQt"
        "XbxzEZajUn03Ax/3sVWqTka/UJbyj8xNccuP5RSMdTkI2e/J4/dKMxn59C/WjRSKsS5fVLP1LI1l"
        "npSOoe6MFJBk9gop7cXfqpHSXk5OylC38x3POEVLfgYTj5/UzMwn8OL+Vmo45pPU4f+2xmC+gFr+"
        "b2dNvHz2ftzfDgBuFg67AaJZFgcBMJZnpGj+wO0DACtPhjiI3/pjNy9AozyjRfNH72yAO5Z+oQOw"
        "sR8LQJg8RYP443cXwJIi0UkwfgOghg3KrFFRxDW6vx27ZkUeBzrc3/ZZw8J+u2pYpLPM7XeD1KzI"
        "p8nX/e2+ACssAUEDWFEkFPRH7iCTG6uGALCwki9AC/sxAIs8yWTbTPvc8esfMjMpXm/7/B93ABZW"
        "jQbAIh9t8QdwNwAWZvnOAMrv7CR5uFvzyhCmjO4tqOV37pK0DM+Ly+9UJnkZ3StjcmUcr4xF9am3"
        "SpPfeU/SMq47tocpYy63LZcq47hj+ztJSlrIdge3UZY6A2unTHV6/kqcjCp5RKzfnMHVxC1jchVx"
        "Da0trl/9mlDm6obkiZObJStkLX9wKIPdzQcaZbB7ujURymC3dwlAnMQuaZ80vxDOYKdfCGWwYx/S"
        "21jkIutiLPz3kH5FhT7ERy3sl/QgJmTdhrWxk77CXmUn/YNFDLNOQUNc92I9gcXrdhb/P8rle9JW"
        "2848NOhNSdPd2jlYphffrO1njcbS+0e5WWCrrh2W0qqch0WzKsdmeaz9MxsLYRtNYclryQs6i1u7"
        "YEAiNguMTRFroZmTRGyWZC5FrC20NonYXLiANl4SsfaA/CEZm0VOp4y14GB6tv2jXB89xTblZhlr"
        "yssytlDW5jM3i1jrWhqxqgym+7UBRU6otqA1WMaq0P+k1Ba0O4tY/aS/MBMB+ueyiLWw+8Yi1v6b"
        "2DS2jvA8EHLrciAAPwW8OjyuAz8xPNfldIjWT4GoDrzLcvyl8uHLuRDa62GfGOnrCoGT67og0A+U"
        "BflTrsbbtL+Ma7xRBwTnrTrwz+t/1TTerje48VIVJME0gLZs97lgzwPVBTXMI9VNG5iDKjsbXRLU"
        "o7Yx91X/1/aDN7OT8/vgwuyI/jw4rizKofRWFvbQH1yURSGsB7+UBFyUvih7YKx0QDZS/cHrZO+N"
        "1a7G1O3Fv9jhd39xKlmcRO1JkmCI2ntkAQ+1yzD1k5+w8IIX32D5RV/8gaVRPS9OwBKNjhfyW37T"
        "9YJ7Vff1wniLK1kvYLfYkftCcxvt/oDw7Ay/RLgdNq8HhJu4PyA8yyRZIjyLeykRnr0rUDLc2iwP"
        "DDfxeWB4FoxSM9ziFeSF4Vm0Q81wVb8QPAtnqRGexeTUCC9ajZlZby8It5Sg94Xhqg5OBC6olheG"
        "m7q/MNza/TRPty4fLwzP/yKCmtqAGB5HQAuE8TiiGdvGjyObNwTzWN8gnlOR6g7SyfZvVC/+btWB"
        "9f7//cJ6AafocQELI3xcwMEgz9ag4wVMDPbxIB6M93EBC0N+3ISNYT8sYILkDwu4C4N/VEAPZsIf"
        "XsDBXEBYwAee2IZ9sEFHEI8C5gpYQ/T1Fq3eCRdga4dFcN/WxULAPl8Pz1xEYT1dtu+iHwbBb1v0"
        "MdC2deZgSG2qzeDZVuOXYXKh6oWKga8t2TdDXFMdBrP2NqUwbLUXJycDVIsfoyiqqnkZdNq3BsPL"
        "7CXNGJL2XudmyGjbOp3hoZn8JSBoc/hDQDCffPdcdBgI5nseMxctBoLZc4khBbPbESEF82XTzUWy"
        "GQraG4qHoaCpKAoW3+qFShgM2qp3Mhg0FTXbtBpOBoN5CFQrTONuBoMaYOEfJEpuG6MtBoNaQz9C"
        "WArbWBQGi72N8fRP+ffL/un55YoCqIkyRhRnQpQRntoRZfgTjcm1JSIqUcaNppl4Gf6Rw2GKGH4Z"
        "lyoj2PD7uIpEaCb644QbxUQhNwzcJlrj7+c0ylTHF4ZzE83Z4Ukg07HhFR3GTMKpMFHICWfGeCFz"
        "hDGKRCE93GommuMvKkQ4Y2uROyGGOIiNpyy2+wEKSZfYcmKQHiZflfVa6M/qRi30D/BmLfRn/Kvu"
        "HH9DatfCyToIe3O/kV4hS1CQuwK7TnRYB2CVZaFvwsuSvmjmAL65WaZnqRxykFttG0tvvUgSfPMA"
        "SmE5bZdXBgtnS5qwWCJbbTuLYUvhMVn25uMptQ314JpqLEwPhaXUyWXn7nnUwKiFNGTzL666b2SQ"
        "kLVFaiMha/kQLglZy1ogLGTtk8JC1pT01NquhtGUtW+ykDXhZCFruwCThaw187CQtdouFrJZCo4c"
        "snYZabGQVeW3WchaOw8L2SzhQw5Z259hGVts+v1bWL5Dv7CJbVnO3BCC63IaROS6HIEA/Vif9T+q"
        "z+bHC4J5XcyB2F6WszuG+rqggZH/tSD5XxXEm/S6mJ+oa9Qwt1HnPRHMizwlf/GcSl0Q6GNeC7r/"
        "o6YJb9kX80d1hTbmnuqCLuat6oJA71Ub9npwZpp3Yb94MBWv8eC2VAxu0TDiCYr3g1cy8XpwRSY+"
        "Dw7Iers9eB0T3xdXY5lDnvyL5faYL07F1P3Fk1jN94v7sG+/uIwspUntJ0x9XpyDZUaZLx7B1O3F"
        "DeTtlg/8trwQPzc1kb/pc+lgzccL0O3b8kBx3Rdp84HiKv7WA8VNLA8U/xG3Ox8obuL+QHETjweK"
        "m/hlGZF32P2boaoobilRXiBu4vUCcVM/LQfMvJ8gbuonilvNn2b7Ra/tv/r2+at2g6Ym54Xi9hjz"
        "fqF43m4Bba09UbxQj78B8a9mR7HdwQJMYP0+EMtjPbaBROonrsegHvcfhPVQfgdEdiZZi8P2WD4x"
        "vLMFwPbXvotRnuuB1vEKHAz1ZAUmrl8Y7+MCNob8OJkRuJsTFtDB6XtcABhBE6ckaRj+4xpgDiDu"
        "Q/DgNh7Fi7mB2JAH4QmKxU8qCpa4vRB1AvS5aBYiIZCebzjsXASe1f6ryxfB7CzZTAzq/GWZVthE"
        "nwySTTUYEJuKgW/+2k6bheoynLWXahi22j0xCqjFyzSFZYzDoNO+NRhe2rcWQ8ksoVGMxixLaszD"
        "wuJ9Ub5mklzUJgFBExEMtCU4w8BctArRJRiYL19OLurMvDVLGBszMEsKGTMwS8ITM7D4VmEUYzIQ"
        "zDIgxRAsvlUYxmwMBU3FQDAXFZaxOsPA/CKbtJe+kMIy+mUYmGWYihloKh+B//1RHrTtb6Ig0hbs"
        "A9RSuUF2A0S6fDYCFf6CSzeAdAWL/lo6omdba+lswSPcgFSiszjks9FLHEBrT/QIB6DdUZwfoA0C"
        "2QZU5wCrSJWjuzHIZ6N7kMAQ9Sj3AaC90cvctXaF914AbRhcDWjDxTrSV9E6/Xl8BTKrYJvol9Ty"
        "qCwMxXbtXjD+2g0ZwaBrv8dAm9/nX+HvJ0ZU/fkFMWpXFi7GTrs0sEFgqkA2SEm7InBBNOb3GFqP"
        "vwAy0D5wQfJZmxeIO8u400HGabKTfkCwWfaYA9JMBeuCCFPBHiC3VPBdEFbaSyigLAESSqXiatSv"
        "3+c3EiT8PYqiLK+lhyK7PgJO+vKn8Fb4+7kxGFk4+cVgZBkbBIORhsiHe3+RYKBTNhOg8zQTTBBG"
        "JrggjSwhBkoju8UyQRrZzQN0xmWXHFAaWToQEEaaeETQ+ZRlVWkgjKxGAsLIbG+DNMrvykg40EE2"
        "PW1CHa6bLlnfon07qvYPDQYsTydVdRjuzbj2+PX9dx1/QHkQL3hhuaRMrPU5Imv9TolZ6/PV7WP3"
        "tQHre4rX1/ajxteapPCt0wPlS946X0mK5sfsO/L9pR42v55PKh+z9Uj/u+6X8ZfD78rt3JQgvR3Q"
        "bpzv+aHuSDVn4yTPz7bXg2bnmouDOo+ovvn4LALJxbl2bgmdYG9xZpyaQpNBULY4gpwPTVq5ZhEM"
        "tYNfBpz5C6stt4fdCUbas6yLAGP+LKvkBjEbgUA7lGa4Z+PUcdjZOd3FYZeHwPZcQ8xg7bh84rDL"
        "A2zXw3d23p6Gw840xFS0PIvORHMTsDPRJWhXfCm3BWZKWZwM58YwD0G7/AmPlpsDA7v8UdSW28O+"
        "BOzyR1Elt4fFwM5EDOxsmBYBu9yIfiRx9GV62kEGXfZK1nYGvVg2Mu7FsnSeR7ZtV7KZ8S/Od3Ey"
        "BMayfMpHpudo7fF78qgrDWXl8z8yfUgrTWXl08BYd1M2xmlaUjyG+QC+mxIyTifRUkjGupyTcd6C"
        "lqIy7paV0jLUnZYCk8wW82fzbNpagzKP4+3ub33aDP+3NQZteXdq9uVV2H7TVo25PBj3ur/dAgDN"
        "foxQzHLqDQBd9uMO8MpyRRwAUnmCjeaP3gVolKf7aO7wBbP05o6fjAHQJs/FIJ//4w5wxfJQLgAm"
        "eSoO8QcwTLdIGN0fv01nv+L+dErNijyGdLi/7bOGRb4WXX4dRg2LfAV1/C5rNSxs+g6wIs0a6I5a"
        "/zpAiiKrnz9wdwKkKFLA+UN3BUBFUWd38ILggOaOXpcGoEJ/3JHZiP34AKiwOiOoyCxD/PE7GwCF"
        "WbLz49/pSvI31J3K/U5ekr9+7nTy71Qm+YvjTgnjr0uYXAnO8P9OeZL3hNeZmxoPb574Ox1K/lS5"
        "V4vLFTE9w/q4Mq5XBmWd05tbOmlU8sBor4jOFbG8MigDdSNLnHwreT28f1pbXJd6RWxuZIdXBmek"
        "17UwykqXF4TmJG3JytjeiZaTwiWth3cC6SR0ScvwJlFOepe0T7dbBmemn3AuxR4pn5wfUZ234ZY5"
        "D4udJl2G6kg/YbLFOQcLYhbOI9hL35NzAxpY6t14ydhvAamLBL4KzyIpby+vC4l2+yLJcwvSbSTE"
        "c2FtNG4sdIprE24S0lrVtkgyW4w0SeMstjpFsAq9C2Epdy04+5CwVaFckrBmqYfEqkXbkyy14OHL"
        "sdTCLDvHUgv+XhxL7aXsycHUdJ2DaRaknsHU+mVzMLW30jcHUw2onYOEqQrdD7YGCDsJU40u/iZJ"
        "U4tjFpKmVlV2HqzCLSRNbTgmSVP74iZpar16SZyqcG4Spz/C/XUSp/pFeu6qwr5InGqvegdnKU4t"
        "mL8hOK3iEt3tv990LYtxl7edLqYj6C1LaRCJy2I+aJZbFzMQTteNWgi264FCIF6W4k87P7qc0yDE"
        "1+Vg0+f634A5gLo+kDsoi3GnIo23ZH97gTdl37Hytux7PdqYe+uQZynL8elNm3P3txxocx7utoMI"
        "Xx9skl+W428t0fbcXaIW3aN7B+5/SjCt+90Oad2QtconWYrEwzsiO6oV3vvYafPmXY5998HPWC7J"
        "w3sXuz9/H1yKXaZ/8SMmHg/Ow14hOA8ew748H/xE9l5C6RxMfB48gokfvIBtAT6Q33ZH1wPubQ+x"
        "PzBe9y4esG5vBjyg3HIj7gd+q9gLLiihbUM8eFJbqvrBk9pu0g+e1NkhdEXq7IZ9ReosEroidRZ9"
        "UZHatIcntUUkTJ7U9lrAeCC17iI9cDrd8GqgYa39wGmz6P7AaW3xtx84bW1+mblbte8DqE08H0id"
        "7oW2C3bYC6ntNv54YHWWF7SEteWvfIF18reQAVo2tK8ehgy75BNYvhFeh2rXOw5YPhBoh2rXQS5c"
        "PhF0x02HzjRDuXfH9TfAI7nP/98MD/UyIZDHegjlodw9J2/97z4P2113LadNXA9BPa49diAafx7b"
        "yQ/1/u4fbnyudxDY+IbbfoGNLyA1bH3DjcMS3Po2doQaj9/CiZ88NxdR3nZcJs5222lpONBt12Dj"
        "GFeN9+hOxG7TDBzYtvvTcErbTsbB0WzDcwke21q6ERC2ld0l0JtvFxS24J/f5sYw3COgNgsRwdM0"
        "1Krl5uDuIbTcHMa8BC1t5d8JRFqExSS4aI8mHgKGKmpCENA6YhPYU5F/eOxrbNEkOOyydOUR7CxE"
        "HmddFtwfsc72JjbOOtM0nHW2J7Bw1mW3BCLW2eKQYZ1FrQyCdSryI5VzSxgfwzp7EXERrLMVI4E6"
        "a9IkWGe1I1BnmkawzmrXCdblC+fcHubHsM7e9rsE62xTgECd9QODOvtfBNO6P1++zw/qgmkeUUQL"
        "VvREEV8ARrwI9y7W7wwgeUN8ahIlzOACC17EcFeahyliRlu1RC1ch/g7jUhahr/NRJnnGNEOLlOP"
        "aCOXKONE525EGTPa1mXKiGDO9Gm0GcD0aRSPwdhYdDhHmLp/xk/ZqfsUsJPihL9ZJJydnshv/O3/"
        "RSg79W/hJd1hdzwa50pU1yfnP2zVPDmnYTsOh/MUtrtB+gfVuf+VXepoT2BLLY7+mSwjvuUNmCTm"
        "VbgOyXZb6g4S6NbEQ1LchINEtwkbyWt7sf6QkLYbTJcks+0FNBLHSRKFFMF2L+SS3LXLVp2EbToa"
        "0gFT7SRWbc+IZGl6fiy1bnAorQIhSt3kUGqPEHQOpXZy2TiUZg+oZyi1NaNwLLWX+VmYmpBkqVWU"
        "ZakJ2clx3sTaZvxbQa02mrFZlpqQZakJB8lS69VBstTyJ2wSppY8opMwTcdRasvxl0RSW04QVwdY"
        "TnS3+k9dfWVkIGytb2lA09byme8DzWLLYja0/VEWsw4C5rqYjXC6btRBsP12LefydoPtibzdfGq8"
        "HY8OMb9uV4dcQF0fbI/k7YJZm3w5A/IXZTkL8h71DSjIl9TFdMi11L2zIE9T34QZkOMpy1mQG6ov"
        "nmBT/PqikEBO6q2bi96x8IPDOyp7iu/y3sneKXxwSfZ44uX9kL3bd3nnk735V3kce1yw8W4me/Kw"
        "8i0WxtIeHIrtYvUHL6Jf9oOEQdPa58Ff2Jf3g5OwnUJ58Awm7g/uwPb++oMTsI3K/YD+9BZbwyzM"
        "j1EQzML8o1nBLGyMF56nkTaCWViwDQ1amGwe1+kNCYG0shaP6+z90ArXlj+i8bhWbes8rk0rPK6t"
        "zoPHdZYzpMK1je94wHWWMLPEdZYttMS17dG9TO9to2484NrafB5wnd8Zwsyr9/aAa+uw8YBrE8sD"
        "rq3a+wHXFsO2H3BtsTvnAdfpxR/pfzFUAuLrIrSOL4NsBNjx0/lQ3Ev8gv5BsB0/pA+dYsZyCN6x"
        "HJpux9kRJoLw+CLNQSgeyhfE8fgCE7ZJH38em3zH94Cw+Xdcf2znPr7/he3PxHpsIh5fZILYHjcf"
        "w3usvxDh44tUHYJ8fJcGC1ch75II/v0N0T6+i7Qg4HP32ILm25L14qS3Zy0ajnfLabBxpttui+Ag"
        "zzJlRPQ2zcGRnbbn5Jq5cTjnuwJfKurCcNjW4oOAr4oI3lrlCMbaal0IsOai3Bb6aARDbQPlEODM"
        "bpG13BoCQuXWMPolsGgXTBgW2r7IJABo96EaQT3r8YWjLl2ASKrxXWLPNaPjqMsyT0aoyzJcRqgz"
        "DYE6a8/CUWf9tnDU2YqaQV3+tEJhCYsgna3GBsE6256YBOzyFzJm0aRNwM6qtwnY5TsIpxAJQbt0"
        "l0Ryg/DjyiQ3iCGXoJ3dMWGme+mjPFJYhO9nf36URyz7ER2A0u38jihdfzMgpf9yEKAcfnQGoNz+"
        "0xO10r8tcAClH5t/IWWw0wpIWzApBFp6gnU5IL1BFB1Q4S+ISUakwXwRqXCwBke6KTgKQwbHZyqg"
        "nAFZAekN4pNr6erBliogDd4FAuob8Bbp3iB/CTCoE2OvHdBdCLjZ8389/PVcEFltLdMhnKbrpRVX"
        "XSBw2rEnBMs0Vv+GP+8Lw6L9/mAstIcHGwZAKx+kngX8Dwx19vuO8c0uIiwMavZ7wUiWXlho4fCu"
        "KAo4+n3rGKn09/4ju+H4LtetSjy++2AoMvsRjD92jwdiTpqdQ6Kf+0869PDnq0HQSU8nZ/zzDUHH"
        "1kYHgk760sGJfj4h5lhA+sWYY9kJBsYcSy6xMOZY+YIxJ89BMeL6DIw5Fj5/MObk1yZ23P+CMcf6"
        "p2PMSROYSDi+q3eMOZbnpGHMsfHCkGMXLS6GHP2rzIw5daT0SRBU52PoCZHKWPg7E0DVtwyySVId"
        "h78SfNXqbO1Z13wlcKv7XBLaPUbGf6g8emMclI+bobGWt4yUtTxdl9ZB8yfjaC2/GVZreUrZeuDS"
        "iV799ZUxuE4FcjIkPwfkg/J5M2DX8fcZv+t0DynOX4PtPXUaCS2pZOEct/QKF4a3Hb1emNh2krxh"
        "TJukw2y2ik0YyHYkDEPYhkVw8qavT7aWaxrOWIu8vzhY87Pq1AL8fZA2c83BuZknpNi5hiCkvYOx"
        "cSzai5ALZ2F+qJvaQZAyMrWD8PnutD0E4PITfldiB1ELppqdvjSYamkqgpFK0nVzELItMNXsnHnD"
        "VLOvHJhq6an5TTtZFo412wzYONZsN2PiWEuDj1tqAX0sHGt2oIhTLT8rTm3Af4qt7bw5DadaetTZ"
        "cjNYBNXs8JagWv5OYmoGfvIJyc1gCU41+ytkVItjXzOwxfHCCdri8G5J6BZHNrcEcHEseDZzC7+V"
        "QC5u1U04x2VduJVqpXuHcYBnz4AXx+XujHlkNHdpHenqmEud0WYpmxn/4jruDIFkgG1lI/4EolVG"
        "4s/apTKS/GQ2ziNwMiCGsrUyJsav7vcMi+Ro/6GyaNZW4jANge7uT+csyWcL21XiLr0pvfyfnhJt"
        "RfJB76dnlhDLl5Kf+9sJ4CpfarkD5gcYte7XYdY4yhO1Tf+3vQaPRe3Omjb2WwAx6ZKpueM2EJjk"
        "D+a74zburblhb8WNGhYWRzFrQtjy+ZZYsDnpLbGQ3g7t3k99vzzcn65TYsFWhPXUx366SizY2qyX"
        "WEiv9V73pxPAQv5YlT9et6ZClZXO+21+9vmv6gJUsOqOmgpWh1VTIW+bP2p71FSw+p6aCnZAOGsq"
        "2PNwNRTy0Ft/2KKrAu4//Z/f/r///d3/8//rUbKLZNO83f8LSP9VhDBFrP+7PfyriM4UMf6Pbr+K"
        "GFQR/4eyX0VMqgi3LxZTxLxeQzZRhLTuFXGYIrxmXKqA5hXxO+VGWsb/xRb8LoOxTvlPzNLvMoQq"
        "Y7pldKot0+2PQZXxf6u/32VMrgy3Let/0BbKRu9w28IYaR/ThRdjp/+g3fvTC2On4z8zgN9lMHY6"
        "/vPi4e8yGDvtvn0IY6e9+TSn7PQ/z54yTuW/M1T5z40jxpP8V9f2tzj38aObsjif8aP7T7Az4yhU"
        "N0jvoPVch3MJP7r7Hc4P/IzDcP+bt9RduSTz/yvs/4kPokCvwtFJuv8Iv3tIpOsX1yQ5rsLDwvtH"
        "KL4XXPUX3b9TK+2m/+dVborNP8J9Ngnk/wqH3zlSWs7oPjZLyxlup0ptOP+JmaYYm1qclIbzz/q2"
        "czT979Re2rwcTf+ra8cd/V7qVhscTX908yNp+qP7z5v6DE31e66H26VuN3JW/TMO3zkcTX90y//7"
        "fpWw+9P/VlpM7z6iSpPp/7nIQdHUhJ2kqVZVSJj+6ERIlmqfDnbKqxX110Gl2XT/X1+azWgfi9If"
        "obhflNJs/kFpJ1n608TFTld/dJ8775fSamT4C5c86f3vA5YrHSFrVcxx9xs6W8x2u3/QxchBMFwW"
        "A0G5LOVAjC4HCtsIKYpp3xkIwctisNlxVUyTBuG9LMfddGvC12dC8C/LwSbWZTELcw11dRbkKspy"
        "QM9RlSPgpLwqZ7j+odHWPN2NJKHNGfQ6VTHrYBP6slnuVEZoa+6CTffrf2njXdbPid89m/dTP9qz"
        "G++cfrTbXeoMTLsG74ZUOzfvfKzOwnsc7avDe5mfLZqvPbiWH21b68Gh/Ij/E+1Ee5Efsb/h2QQU"
        "v/gLFbt/qzYwsb9bNDFxlwd/oOK2HpyAitd6IL/uHfb5gPsf8ZrzgfG6K/sCdv2wuwMpmIHNbz0g"
        "3IZ5PHDb/pGdh/XP9sLXHxYVP6e416VIh7THNZABabfrdCemdTdSF6Z1Dxg21l538XawfpYHWuv4"
        "3v5A6x+x7PlA6x9xd4/GG2RabbQXWqvYZ+bAqu261TYx8RgPtFZxe5myq9jfuIEMrE1/fwqzsPUy"
        "IdfNzQdW22fbA6vVQtxoB8HMq0t7YPWPuPld/W9tEGTbNjS1jtTDnW12VN7die6A5a6DnLC8QdPs"
        "sO3uH2Sj8utu/h1QLv4Z7IXl/u7CB+snNu2O9AEUBf5+w0JZIv38sF2aUO+fTUxcj+3KkPVHrU+W"
        "H9qAml9v2K5+JF/uib6g5ud2vqDG1/fGYlQi/fA9BWx8Z0yI95HeDfcIWv8zoz9bcM7r+mMvHO4a"
        "GtI6TnRbzk4c46bB0W1RKxPnta793PXbyTQirje/qWZNBsc/orMPwWAVzU6AV0X+sr8X1dsEYlUE"
        "hgb+Ibr+3uIqOoIAqMY+uNhqqT300RlWWgQKA8gf0XWtSFKD6L4nkNQgev82QUDtcXemKrlB9Nlw"
        "2P1Mie8hYKez/z1w2NmkX3DY6Vz/Nhx2qpkE7bRu38Fpp6u2fXHaaV+7E5GbaaT7sbtfKjpjEbTT"
        "E3Zwy+APkXzM3DIXjbx6/gI9tQa5Mgnaae8tgnZWOyFoZ7E3DO00RsQNSZLUIPpZzCxQQzUo2lmQ"
        "DjPf++nx7f6ZJDUI+c/rGx7t/nwuPj2HjFb0eBHjBtdY8CL8eMZBFeH+OSZVRG8+OJm+CFb5cBHy"
        "SYBVvAh/Kn65Ik4AXaKMEYVs4GWM6MiNKSLayyWa4kexDKoM17zapMqQaO5K9EdId7yMtaL4PriM"
        "3mbEfryM5U8SGTPt1x0XYcy0Hz/ugbHTPvxYDspOz4r2CvAyZAvnVWzTYHGupNo4KHSjkU5DNwOi"
        "eyyljnQPWs81OJ+g/enOlU+lk+4ex95Sd4aQyNd17iAxrwtx/1KJ1DX1DxV7/cVwH7cUXpLddjlo"
        "kMDWNq5NUtpGY5Bo/hFOd1rdSsPpfrxVbTf3suDV7Q7ZJG11I2KwiLXNiEVyVf+M0U3zSKcLZXf+"
        "JaVurcnBVDcAzuFgahsUk4Opnc53DqZ2ts6xVLvFjW88lS64m3lL3TyLZKmuouk5s+4o+LPL0mJ6"
        "l03CVL+4GglTa6OQMNW9DP8YsbQaOf754a6r6rexNJw+9iZhqvsU7ZA0/RH611Cltpw9SZiq4exN"
        "wlT3Oi47SdX9jgnBtLof4Z9GC13MJwhqy8e790DIWxazoFltXcxCuFwWE8UVk128OoLtqpg5EYiX"
        "pWBIL4vZGOHr6mwI+HXnYPyvy8G2SB7bNflyBHIWdbsw31GWcybkSqpyFuZY6vtzF/Iz5XU+f+eD"
        "Nmf//rUI3y7MK5XdvBrkpGrzGbzPsvfzHhyVJfYevHdS7dd5l2RvH27eD5l28s7H6vzgcexJ+su7"
        "Gc3e5q6aL6Rd/nbEh4n9qPsGiseD87AEeufBY6h4yoObMPF58A15mxf45fngBezL+wH9djVMHoCv"
        "d7T6A+TtLtwD2FU7+gPNtcX+HRrQvs5+4Lb+md2VSdFkS4F3eVjrO4fn8rC21+onD2t7X5Fntb18"
        "eXlWWxr2w7M6be7BhujbPKst4197YLWK731gtV77GS+sNvF9YHX+Zcy2th9zPcEOWw+sVvHLhF1r"
        "HcbsIeJ9H1BtN7ReJuQqXu0B1vbl/QBra/MDq3Wg9nlgtaW8XAirowsVs0Fz60guB9r8ieTN3QQY"
        "sBza6wnVAzrIDJvudvxG5VsaAvAomt2/gnRh+cEwHuonNuuO9N/Gtulj/YB4Htbfvw0wYP3AqB7q"
        "+4TAHuo/LHglvAwxsal4eBNmYUEr0WWQD9x2ifRdIM5HcunYLkvU/Dsw3IcXsTq2qxJeg+sDh77e"
        "qv8WTvo01qOnGmkHZ7pdnR84yU2D01urNieObHtC4eCc/jntxsmsb65+QuDYnoYUgsEq8sOTJa+e"
        "f+DUcxF4Lvov0Sa4qiJ/vrlykX87fRddvghsauzLXgQr9d3XLQQgNa5jbwKL+lCsj+LcIk6/BADN"
        "ygdBPX3G+G4cdRrmcA+OOouoGDjq9GGGIzjqVPMJjjq9rb4nzjr9jutidt4Hbt1Oqtl94LjTx2nv"
        "JHBnsSQE7fSIfTC00yiJdgna6ZcWM6G0JjGzSBW1RtDO3r7sBO30S/cQtNPglMHQzqJ2CNhZwM4k"
        "YKcvuW5m4mfXgAYBO72uBS7q/7wXFjxL8d8fZTcugns9gHIGb73VyiF+1pVa2bf/BgWg9LdbgWZO"
        "f7O1VMp3/evMtdI/5LmIcgXvBQHSKHSuls7omjMg3UEsMtLW4CgMkN4AoIDUj4Vb0LAGMK2l/ryp"
        "AcbUew/AWkvPCB4HKqXDXWUJYEwjyOcBGFNfO4hPrqVfFKFcj033N9t/KXVi6l+KjH6+5oIwq7cl"
        "zoTYapdABgRU+zlEUcuUsiF06oWNdSBe6qogeAQz+Hnw1sEX/L43GRgO9d7ABhmov28HA5/+Pkoh"
        "EtbnYojLc5us8PcdhJkuTBsGMH0oIbrZ7P9+fAtE1c/vRQQDlF62kIlRSW+D+HFd0fDKde/kyAit"
        "318C/Pq5pZPApnm6OHO3eXv087kw6FgOjgZBR38uA6KOXcW4EHV0zX8w6mhHrgNRR9NxNJA6us74"
        "wEmYLWYWRh2Nq58Lo47+Pno5N/i9tI5RR9vbLkYdu/uwMepYfQ6GHX2xoAuGHb01cCeGHc2zMTDq"
        "aPHoXEgzo8yGUcduhAhGnXRxqtUvY0vdHQgB1UuyiVAdPtwSRL0FQ09YnQGsbPeXzaLqBB2S4K2M"
        "Kh4toV2tvhn8SvnOUFiqo/j+v5Kj5nZOujYt5bdlGK2/vjKq1h1/M8jWiW5S5pYJT3bLEFxnvEgn"
        "gnUGhgzQ5cfPzXhdpm04kuG77DkZGc3LYZ843C24tsNE1wDTdNvQl7QLs9siUTsMbJW4E8GVV2zA"
        "aLb42g7zWDv5XBjCmsOjNZy8qrkEby0RRcchq5qPIKtqCJqqJEr2ln7m4Ny0Lpg4LFUzCEJq2EK+"
        "IPbTdRwchZbJ4OAAtM80nHranN1w1NmQXpxvatX+HRFXovGcQWhjIvGD8nomWcFr3JmkHRhqFnaN"
        "Tz3tKw2GmrWlwVDTHusDhpoF6RLTSc2f0DoONdWcgUNNT9r98Jieay5ONasbQTXVTBxqKpGNQ001"
        "G2ea9oDf05kVNPHBkVpBbwTU8u/kVrA2DjXragJq+k/Y2eZfFPy30qPe8OH97yRoi+O7e0K3UNWz"
        "491QFSRIz1X+s6i7UJ3sSDd8fr9nE7hQNTPaxd9aGfDiR84lY14o2+khRty0kZEvTmOQwi+U7Z0B"
        "MJTlW41xroD0pDaODJ4ZCsN45pvBMEwIsDMcRip/E0wKG+ky0kPZMFL8ZFiM4+NLMOpj834eYe+n"
        "/ouP3ftp77PknuXS6yXs9KfrlISztG+3xJqeLLvbksf56T/d2kuCaahr9Li+89s9AVjpb9uuCaUP"
        "/O9WY8nKbTWL9LeyagDpb/utqaP19edB3qj941h3zRc9c52thooeWEZ3nZ3fbhk1QPRB/nVratiZ"
        "e6tRYUkcZg0ITRIRpEP9//70Zzp2dkkFe7+9nhhZfOwtqWBT1XoKZFHEvaSCltpPSQVt1ndLKmhf"
        "9V1SQQ+OGjCbseDbVlNBD7D6ramQJoBv3f1tr6FgT+XPGgoW7dtqKOjR8T01FKwOp4aCvZ1/ayjo"
        "eaLMGgp6dDqlhoI977ZqKOgRcXRlwOszqZmgseTOmlB+p7pIY2cdrMjvzBdpdKl4RXSmCO/VF/md"
        "FyN/ub07RUyqCGf05XfWDDaJtvxOopGF4jW3IYcpYrlFXKYI766UOBk30lfGffNk7FPECXkTJx9H"
        "GtwonnW1TrWlu/0xqDKcKZI4yTvYl9vFyeWRv4bvtoWyUi+dnTipPtJ41c8tg7HT7nkYcRKBpNG6"
        "2/vTCmOn/Q63Hoyddu/0TpysIdm4eGtwcZKIpP+Xtji3krz+nvoSe/29cw4kSR2Xeg1LBTc4V2E6"
        "0j/Y6++HcwranzI4T2AZsA6Hf12WfYNkvsbRyiVBn1wPzelu78YfEukW8ntJjufCWQt9L7jqNn6N"
        "xLQKO4lmvULrTuRaaTj/zN4mCWGNeHYtVUrD6d7TlTlutY1+VXv951hCglX/jVc4mtrz78LR1LJS"
        "T46musCfi6OpPeO+OJpaonKSppaXfXE0tfffyXm1RkvPwdHU1nGTpKmu208naZoECuc01QhsnzS9"
        "/uJiZ8VJHrucppbLjoSpPTi+SZjqtgQ90bXREJKm+vy7i2EpDce9dZbTVL9IslR3QL5NstRumW+S"
        "pfr6uz/RyNPeYyHBDlrLuGR3HtnZYta5CHjr14o3wuH6bWkIy2Xf9IFQug4iPgi0y6jS3hCGV8VA"
        "PH8phLbgezDU1+VsiPxlB38LcgRlOQ3bIqnLwSbddbswt1GW424PNNqQUadSleO9ieH5mKqceS/k"
        "cspy/PoI3a6GbaHU/XwgD1XbIe+v9P3ks3gnZeHWvGNSaZu8N7LA8MW7INM23u9YnRfvbLSb3U3I"
        "A2m9915Kt6KBwK5nq9yJBlN88uBGTDwefIe9cNcfHIaK3dORNjDxuA+uwb7cHvyBxnm7kGsb7LD2"
        "QP50x7FhFjbbC+NVfOcD2O3RhAeYa5OPPBBcO1v6A7b1H+luDRUt/olmvX5fQ1qfQB3S7v6wdrB3"
        "roWntb2v3XlaJy+hl7TWOi8e1hZw/ABrDXB297gqWGuMywurk1f2albrDts3H1ht4vbAaq32bA+s"
        "1gj0+zJ3T8LXa1Ynsfw1q7XN/kk1ZmDD3QMQzMC8V8xqVlus1HmAtRrJHg+wtt5eD7BW4GK76uE9"
        "Av/8AJVD+z7M4+kOs0O5HATb8U2DiZA7bLm7AN2o/HZoPyeOnof2ceJQf+yAM4zMvgNCefhy+20Q"
        "zcPv+7sjHW6/+19vA9a7q/Q2cf2EyB7q/cCEDZuP7xBh8/Nipz3EhzcdBnZOGt55OFigSnj7wXcU"
        "qP11cde7Atvf8t3FwO0fZ75ekZCGg17jNcbF+a7Llq/jULcVbcNJbgvZi+M7eck+ZLZdrJg4qO2G"
        "xcTprFct+iKQrPcSRiM4rMH2YCThv0SNIK5dCZkEZk10CLbaBY1NAFXb5B6Et52L5iXQqaEvYIDf"
        "n5ct/GlhahF9MWDUD/nHl5I3aQwCgdp5H8M9/TcdYoartxm+hdNOFwDMbNZiNwja6fpoCU47e8j9"
        "4LSzhevAaafLr7tw2mlfr4vTTq+QHAJ2FrlAsE6jJPxdWslFfmhxz0VTCNbZ7RgCdRpOMw6BOn3F"
        "fTQCdfFj+zHprMMJ0Nk7hp0And5QGYcgnX5pEKCzKKRNgE67bhGc0/gqN1Lg11P22SnbCqiHlzC+"
        "IAQZL8Jdlg+qhB7EJRNFjACYRFe0IFoZL+LeINQOLuKflUawW4sX4Tup35k20usnPYrFw8toXwRj"
        "oowWsZkow48LHlR/SIRuogx/F2NRbdnRNi9RDzfSqVFmuvwdIcZOew/P6fAygpU1Y6d9upfwhLHT"
        "HngAyk5XFBzI/OUu51N0t8A1TSl1Y5DuQ1fzblTqqHWko8hkq5T1uTiPYL1JugG96j5I9usyy52R"
        "Z8DX2P5wP6EQ7smi3V5suCTPbetjkRC3rQKW3CYkaa2jEc69K6F/Kai0m/75y6vScPp0+0ZKw+lr"
        "HxK7uvfQNsla2384JGB1o+2SVNVtiNU4lOrz+743KXXjHg6l9jzE4FBqR9WTY2m1NVHVMzpAK3T+"
        "zfJT6u6+HEx1KdcbCVN7zoJkqS44v0Oy1N7TZ+fGtncxSZba/sUiWaqbGP4u6qpHw9/92LXwkiy1"
        "URSSpbrXEF7ILoRrTpKlto8iJEtti+OSLLXRGCRMda/Dv/aUJ7v/HbUf7FyzxfR5EdSWxXRo56Ms"
        "RjYC4ro2CJbLUqAZbzlOfSDMLnMvtIEgvKzNxfZD6nIgwJfFhHe/yXIWNpWu6zMgb1CWc7CJdl0O"
        "NvGu23Uh11EP+4BcSZ1JpEOepb6otiBHU9/i65DfqW+8QV6ovg0I+aQ6Vww2369HXXiP9XM9YvTL"
        "u6kfrf8iVMe08/IOSbWj817ItLzrsSof3uFoN38PXka15/KuRZNNzPngTyy5xXrwInpX6JMH15Gk"
        "1aj9hX15PzgJS7Xx4BjyDy+wye3BBZj4PnBfq70eWK+3usJXRRDxbQ9Uty/fB5ar+IHfZiD7Ado6"
        "Tr3xpP6Jph5LeFKr9hs8qX+03Q1IHJh2Lp7Uqh2XR7VqV+NRrdr7gGobo4dVwI92zvGAar2v0x9I"
        "rdpxHkht4gdQW6XvA6gt48h5ILX29XkhtYrXfiC1iecDqbXN4eNPgHh//QHVdodtPaDavjwfUG05"
        "X+QB1tbbD6zW//I+CKvjSxjQMWUkb9gWeyT/7kSgHcoxbofyBe27h9dfIHiH14bOQvgd3v84HUF4"
        "eHnmQBAP835c7JQz0u8zIJaHenDiHdZ/Ykefof50iOqhfmNxK6He3TVusPFd6RDe49tPEyJ8ePvl"
        "Yhsu0e2RL3wrBNTLgFAf1n9CsGfSy3jAj82/4cy3l0MnDnq7ITJxuusLB9FLqonGnxfOQjNweGvd"
        "Fk5s7bZJYPpHc909hZtpRMBp9R+iQUBYn5DsjSCvisJH/TKRMIxVUfiYXypiaKod3i+BUBWtQ3BT"
        "wyV2I2CpD6+eQxBSE4a0RmBRI5buJFiobTqHIKD23tcJ7OnLxf3irNMAB1k465L0ISHr9Nr5IKav"
        "lhfw4qyzNyM6zjqtm/tm6E41fkDJSTUrukcda6SB4dR/iIKFTmoJwfF6k1y0mdmlisJHLhKRf1Dd"
        "Umv4x1UIgTvt8kXQTjWXmSXmw5QbxB2XoJ3FXDC0S68zSW4Qy+dqbhANXNX/8W/yo4Y1aUx2UWJP"
        "fyFfK4cbAN8BZQ/4Vyvl+qFywDebz0KgndcPlyuV4jP7AMq5XTjWwjGCFXot7SMAZS31H71qgkhH"
        "8EIQUuHg4h8gdc9224SkQVAEUuHgEAwY1x7MIGvpOcEV6FLap787CVhTvxLE0tXSEzwRUSuDQyTE"
        "mIIHmRFjCt4U/KXUmWmbEHHtJbsBYTbJXOmx1R6NWBBQ7ecDoqiugmVB6NTbGkcgXtr6bUGUzG9K"
        "fNHv7wR5aAuihkFQf78HRj6tjxwMd/b7gTFOf98wrlmqlo7BzDJudoxgmnWzDQxbmo+jd4xVP78P"
        "ZnTR8PYlF8OS1r9fjEVmnhcDkG2uYFM+DcL/BKKOLoUvBB1LiAExR5eLwd2x6OefQMyxB+E2xBxr"
        "6IKYo+HTgjEnjX3/gp93v/QWDaqb1NFFjiWtBJGj5UdXvYLm3gYiR7MwCIYcvfTwDQw5dkliYsjR"
        "5n4TQ47eF7gXQ44muXBXEhIO71oHQ44O71kYcrR/WseQY/svN0FOGVbq3xsD1VGGNlDde0KoOvo9"
        "myTV6pvwq45VznBW9rnr1A+oPgnqyljk6KFDVN4zEpbymYKxlq+Mk6V83Qybddt3RtFSfjKo1h+X"
        "jLGlyXwtQ26ZDEQkI3CV66D5oY+g0UUpFxr6dR+/oNH5DwYIanP+s6aC2xyOdkuXsGGeWwjxhCFu"
        "Id4LJreFoQqMa5UIzmirGA5mbb5cmMYayjs6DGFNJzEXTl5NI9EFx61pFs7YXJNawJ0Lp6lq1sAR"
        "at/pODhVIxunpfXBwRGpUQv94lzUqIXodlKi8beypKXfyffr/PZsAnY2PoITTv8Lvj9xJRrO2QTG"
        "mgWuHhhrGrq5J4w1lYwLY00lfcJYs68cGGsqSZfQQQIGgbGmyRP6wbGmT7TnW3jBs+4Hx5oetH8X"
        "x5ppNo41rRuDNdXIxLGmfR2lm8m+8xFYs74eONY0QKETczwN0sChpl+ZBNR0RKfgULNeWzjULANJ"
        "BrUo+M+/9CqFyk/I3AuVfNmkLQwKXy0BXKhy3dyq2uVuCOxCdUYCujhqcySsCx8az7cOw/june4g"
        "hoG9O2NeHA1+MuzFdczAF3ZIdCOmku0Mf1wddzloK2NgJJvptmMUjNzS845INWa6xg3zBsx0KzIM"
        "mM6RGHZIvjEZ2+MqwaiPy0sJQztQXSUBLffXLbFnk3MpWWc/Lfmm30+PPv746Ty9RNnPQZP/3vj1"
        "fuqf9/4LWvYi+a5JpWGjs9d8suf8AShZOCqAIvvtrPljobtSQ0f7bN8aNVqu32fusJ3oKbrfv+1+"
        "TnPxxu0fgLQaIFrut2pqaH3XqlGhfTZ2zQcz31tCQWNS7y6poCeeMksq2Kvz9WTI8o6VUNBf1lCw"
        "V+JGCYW0Ucf76b6zhILGnZ5TQ0EjJtepoaCnV+vWULCDxllDQcvdq4aChfwCkxKNcL2jhoIG+N5e"
        "Q0HLlVNDwU5EpYaCnibOVUNBH0CTXUNBy+2jhoIeKNdI0F74gCmDxUL8Lrf/zmuRhs06JO6/01yk"
        "caXdK6IzRXS3IYMpwvHY/XdKjLSE7RWxqK5w/Hv/nTAjf/B9OkUcogjpxxuQyxQhy6vF7/Qa+cPi"
        "wyuDMc9//K5bD6HKcLujdaotx63HoPrUOZvoTq6O/MF3ty2LaovblM11h9sUykrn59aDMdPuvRzb"
        "nbwfaZSuT0DGTLuXRas7aUHSmF+XgUKZ6T5ufwzub7s5p6JBr+tynkRjay/nPSyf9+Fchq4tD+ko"
        "Ut2qm9cG5xK0OyfpB/SSoTQO/pbKbJHE13hPGvP2xryQbFehsEDXqn5CUlyF0kl0W9K7S/LaVt4k"
        "pFU3FklmC4NuJI51HU0z+Ed4OsldfWJ+TBK2ej14HZKwSb7DHKt2yXpyLNWEaJ1kqb1sTsLUTnxI"
        "mFoEdOdgagm+JwdT/d68HEy1X1wnc0qddxaYwlQXcb2TMNX1vbuWaqXFeE/F5yxVnT/B7rWQRanu"
        "jLj/pVbajMwzSJTqYEx2wqvCwc5yrY3s1PZnS6G7vJDSbnwEl1bT12bnrVrRb5AoTUK1c5RqzLY/"
        "P8kz3HtBpYKQtY5HRjhbR5Ij1C1LEUEgXBcDTXDrR5chRJfxt+5wH7aYO6DZcFlMOxDPy3Jcf9Jo"
        "Kz4g7h/L6Xz/QM7gJWra8w11dTrkKuruuZDnqOszIUdSRlb70wrWnIOdTmHNuQ33vy6NLsevD2vO"
        "bi5lzyuVAfADm+/X9Om8z7KIz8s7Kg227o13Txrb7U4JBqYdi/dEpp28+7EI/sX7HO2rLbyj0Uhe"
        "dwvzItp//svy4FI0lMLfO22g+Dw4j/zLHROLPPgJFfcX52Cv8rUHj5AEedduQMXuNkc7WLXddXnD"
        "LKyv80B5javxJ/iYhY3+wnN7muE8QNw67IXcOlRum4sma6Sxu44WSLvXA64tzP0B1xq87u7cTkw7"
        "H3Bt3xUe19pXMnlcW+Q9T2sLcm8PtLZn8sYDrcOQ75rVKvVB30HxfGC1tfg+sFr7+twHVqvY3//e"
        "mLi/zNO1zeB5pivuD6TWYKf1AGrVglvpfp3lgdN2+UEeOK13DbCtoPgCAULqMOC+QVs/8Y2CjvA6"
        "vCTgboBPWL47Qu34sgEE7vDWgTsJO6Bc2oTCWsJI+IlNuOOrBRjF4zfPL4Ty+M15jOZxUHmHgB72"
        "n+t524T14BQ8rP9sENnj9jcI7vGb79gBaaS/7qm1oPbXR8c2W8KbD/7ON2p//0zLMd6HdyH89g98"
        "/ASnvt2OaDjrdf2xcb5rbAg2Cf/zNsQZOMlNM3F8a93uxZmti797cVBreHprOJ316a/DINnuDhyC"
        "wxpo78fNSVG9RRBXvzQZzNrdCSHYmlweiIFq798PgqL2QGEn0GmRKAQu7QF3ApEaf+KuniW1hy6t"
        "ETC0hw47QUCzByGwZ3c9cNTZO+QTR509d7dw1unke0+cdbqWFBx1doOEmKnqZ9wZwi664OCo0zsj"
        "7vrjZhoRN8o0Qp3dyiBIp7EHkyGdiijSqciNwGypKcjwZ3GpMYgf69lW3uP+YdnORcJMEi1OpBOo"
        "0ycSwTX/n9dTOoE6DdVwF6ySG8S9BOm0G1YnSKcRViNYy//5SHx2WucHdwlTRHeDdDtThHzBHBAv"
        "wt/tn1QRa/vYJPpCgjsseBHu1PYQJYhEJ2t4Ef7dqI9pxz3RMRvRFxGOiSL8DVHKPP2ou/E/6A3K"
        "Pu+M5qxEGV+0EUCU0SPOMzYazXDxMo7PLsZK/1nYR0d1RBkzmg/jZXz+xipjpm4Wme4kDclNfXAu"
        "RTcLPtKP6IbBXJzzsDfKOucxknfKUjeR6lZdz7s5h6D92Uk38LP4aa4zvqVuhmd0lfAOEvO6tluL"
        "hLu9LzFJotuaf5AcN2Ej4W1VJYFtGw0kpC1tHgnm5LmMnMa25zBIBNvFl0tyV794Lwlbe1pik4RN"
        "7U1qs/miG+aRTncjZuNYqmeKZ3MsTR7IS1mannLPUkezVL83SJbaQe3hWGoXich5tK64w+i0Qrg2"
        "y1K9GOBvTEot9MnW66rORrLUbvdckqXaq/OQMLW9jE3S1PYzLolT29OYJE6T1A85TnVvo5E01f0N"
        "kqV28YmdrdrosyzVrY4GbXVUQcU92ugli3H9ZaeLcQ9WBl3MB2191LURBMt130CUrooZ30KgXRaz"
        "oflwWcw8ENLrcrBNkbKcIRDwy3J6h/hf1wdzB3U52DZJ3a4LOYu6HMh1PHbzgzVj8/Qyn4h7AVVo"
        "c17nQH6nvhGIOaL6TiA2x6/zrXTITZXjtSbvtX7uRwzZvKv60Xb3sLVj2nF4p6Ta3nlPZNoH92N1"
        "vrzPUa27Q3OwMXrxLpag4j64FBXvFz9i4hfnYeL24DFMfB/chIqPPPgG+/J6cAiW5eM+uAEVj/vA"
        "fhXf/gB8vZ31zQfK29Wu8YB2u0N3HnhuF9IeGK7a9sBtS//ysMT42UIZD8uKH2m/jWf1j1b25Vmt"
        "352DZ7VqXZte4HcPz2rVnsuz2oZIeFZbCo0XVuuNnTYeWG1ZRV5YbV8+D6w2cX9gtXaYf3KLWdec"
        "8sBqFfttxuxrfi+sNiN5QLV19n5AtYr9TQ3QwE57QLWK+wOq7fKdPLA6/TP/anGc0ALBdXgRxP1P"
        "dlT+CbTrE8i/exFsx2qI3HHToYl2eHtoQnPt8BbHgqbbkdx/ZPE3xSP9OhjIw9afA7E8/L7/Ah9s"
        "eGthmzRx+7EJeKgHd/BDvX+fE7a+Fd5Q/Bvza6j9yfiww9JIf2aHOB/qBZuVh5dQwkssmL75wZS4"
        "/a2LQ98upEwc9RrrsQi+6/V37Az1T03rOMpNM3B+2/sNOLO12y7OaX1z9TYczmm0SkRkFfnheKkd"
        "yHcHwV4VzUsAV0X+E8CjEE0CrVa9TfD0Z5iCm2C5OdzdCHLqOE0Gl/paKIPIH81tg+Civkrri3KD"
        "8F/rl8Ig1iGwp/8m7LzzX9cxOs46uyrScNbpUxAycdbZ6wALZ51q3KXcyjXR8xiJRhja6aOoq+O0"
        "0zPsfQjaaRDCOgTtNFaiMTNNFUknaKfVG5eg3Y/o8+NcZi76OkE7DeG5m6CdiQjYae3c6LKWGoT4"
        "Gx2SG8TZDO00zucwtNPq+fvHveiITtBOI97cmakmjsnilf17VAIo+/VnebVSlr/rCiiDy3yAsvsP"
        "jNbK4Y7iBpS3+6v1Uin+takLKCWKQ66l7QuW50BLb7DLWn/Vn8S3DlU4eNENkAYABZQSvCQBNDV6"
        "Vx+Q+lsfkC1FR2CltH83uCZYS9cI4pNr6bzBA261VHZw9lV3U7CPixjTdzH62tQUIq4+Zzcgytr7"
        "dQtCq70dcSCe2s83BFHbO2gQObN+OcGvpR2IkEneSReLlqxjYyy0WxwY/ywVp2DQszSfCyOd/r5d"
        "jG9W/YVBTddxBwOZXVXB4GWdDxLr50pDjw5/gt+H5z3B7/33OyQa3fguWtj7E0OPbQxAuNEHA4LU"
        "SMHPx8GmdbpelAYBR5eK+0LAsUcVOgQcvcDRDgQcXYM2jDi6rMGIY8knF0YcS5gJEkeXMfNgyNHf"
        "HxA5+vt2MeTohQYMOLY0AmdR2pu7Y8TR36+OIUdrHyUg8n/f/acaJBrdvubCkPPz+xndLAh+39CJ"
        "j7X3YsjRVam/F/nz8zKs9MsQVAaTBo9iYepxs8VmqT4z4VWtPgm+6nZnC886lPckcCszlQSvzIDq"
        "tjP21fKMhHUs9MrAWMtTTpZ1j16uRZveM47WX0/ncXXbZ0bZx7bDNndTBpf5DnY6CyzTLvR0wVrL"
        "RwbsOrnGzfhd5wpJF6/1vx2nuwaK+mfpmcSPue6pRHB4q+S7MLFTyUol/cJs1h77cCBrGHDDKayZ"
        "Oxj0qsafXLVcM3DKmqbhaFXNIXiqmis4RK1uBDlVMwXHpWqiaPZEE2QUyuwgSBshmR0EL3xKSzUd"
        "x54lHxk466wLFg44/ff4EwFXYsGcONVUAjNNQy9lwUyzyNgBM00l0mGm2Vfw+aZK9oaZpv0VxCAm"
        "kn0vzjR9k8GPdUtH/46DM83efiCYZt9ZONNU8xFM0zgD/7JsagSnDZxpqmHmfVY3gmlpHgzJ7KC5"
        "ZiAtlUTPs2ZVawdnmnaBfxCdmoGfgUSbEwX+jXQLMMwWkB49hBHOPcNbGNN9M8KF3/qyQ92wXTPj"
        "XBj83EaCuvDd+TET2oWvjY+RAS+Or03ncXFYd4q9UHZmRr64khn74vwD6bo4TnuQzupCmaQTu1CW"
        "z+3isN6VoTCSbUnXu9FL+v7pgRRG0vMjkDBi2l+XFjYi/sGhlEaypISjPjIfXA53fipBhJ/z07Zb"
        "yT7LRlfyzqKPbwk5rarskmzaAe2WONPgVdklwzTl/L41uOyB+1vTSsuNUs56v12t5pLW4Ts1jewd"
        "+lsjyOp7a+7ob2vU2JF3r/mitc2jPv6M/+01SPTp+ik1PfQYVFrNDDvyXTUobNBmTQe1XX875I+f"
        "6mngKYmgx4y9BIKtQm4JBJ11zhIINqXdJRDspbheAkEbNWogaLRhzQPNmx6lrnZ+Gz7t4/zWx3cT"
        "97fj1jzQOlxgdqJHjD47vCGT4Mh+uX32zZoIeix3ASJofWse6NFvXzUQ9CDUnxh4o9Z9Gxd31E4U"
        "O+u1DJgt6Bm+s34av5Nb5BGzwylCmCK6My0dv1NfpPGszl7F+J0JIy3CKWBSBTSnhEV1xPCK2EwR"
        "3i7f+J1DIw3pdILcx++UGmkR3avF7wwbaRjhcm2TMs67vFFtlHVeZ2I2nHwceUikW4/B9aln4m1S"
        "ZTRvaNui2iJuWzbXp24ZnJl2ty2Una7PhRdjp13cf5wwdvrPZMMbWxGqHtuDh1B26hfBmWlbnEux"
        "cFfh/Ijlt26c89DF4Zmcx7BF5eAchera5NxDst5OfYKuaPvgHIEuESYHf12F+KT9SqH3hkOOectp"
        "Nkm2q3CxQNcw4nVIiutyzkfmrIWucbdVV9VZlOWQts7pJJnti0LiWJfbo5MM1jjkjwWvBkj7xC4t"
        "p/tuXADLGYsEq+6GuA4qaaJGObuTFil1w3XMvdS5gz9KmXeDIoWpJbHbHEwt3ppjqfaKHI6lOgpz"
        "cDC1S7qbhKm9+N5ImGq49WUnyhZ3vUiYJldIc5japgQ7D9Z18WEnvzocZ5EwtdvM7DTXHqe/JEy1"
        "V93Zl5SW40Zw5zDVJ98nC9Nk+yOHqRo5O0m13SEEpWVwoN9etpg1oT2POpQcmsWWsdUH4nBdzEWw"
        "XDaqQ1PecqTcKelhiznu7tTli5kQ08ty/KUzbcfH9zHCtwvifx2y2yF3UIY9f9hUu66PQM6i7mbM"
        "dzyWQ1uz382sNbfPtUJhrdm9oua5naqc0Qbkhcr6YBP8Ovwdm+/XoyW8z7LQZ+EdlT313HnvpIHd"
        "7npuYFp3TjAxrbtUWphWeIdjz0sv3ssk0emla9EQYH+q/yHi9vlbIA0Tn/PgOVR8X/yFRVefByeR"
        "PMNXewYV+xPyhYndI7K2wTaPB/Bbm9sD7nXnca4Hxuu2bLsPYFexuycomIV5J/c1w7XD/B0ezMI+"
        "f7cu12r063mgtUbBzsPT2kL8F09r1c6HVYNqxwOt7budx7X21fewKLBg8Mnj2oK1X6b/GreyxgOu"
        "dc/LP5ARUNwfcG0JHfcDri2s5zzg2p7t6w+4VvELre1dwvZA67zWmIH5E2nMvgJkYvY1+nmAtX55"
        "vky4tcn7ZZatsWgb2g4KH992Z8iCymVB++xhpL+7bz5g+QedYYZyd2Wx4LbLRfAdP7vdEYKHlwkO"
        "NOcO5R3bmo9D8A+E8viawYVoHn6/NQjoYfs/LJIlvsuBzcJDvXv83mDjO/1CdA/1H7YPE7d/QYwP"
        "7wIs7LQ00t/TIdSHFx8WRvvw+379UfuTAe7+x/ZDYF9DKdbFWa+rkLZwwCcXjkOq28WJjaM8uUIR"
        "8jut28774F6c1BoGRNBZ7wGMRiDZUts3gsN252EQ8FVRnwRxkyTxMWZV5B8xzFx0GgFUu06xCYpa"
        "RzDotC9dgpcabuF2hKQW0b/bCDKqyI+zyC3i+Ie0hUW4e4WSW8TnrgqCJul1hrFw2uk03j1M6qlG"
        "BIedXQoh5q2q6ROHnS0sBIedPbZHTEu1q7+F0y55GTymneVJF4J2dlNECNqp6C6CdirqDO0sKqMR"
        "tNPbJIeAnfb4YaaM9kJcI2CntZvM5FDHdg8Cdj+i6/oXSQ2if+6+m+QGcdwFk+QG0d3gIMnpcFtw"
        "meXPl+LTY0R3liNMEW7HdqYEd5IxmBI+N0RqUpXwoUn0gwRBHHgR/j7vIYqQz63FZWpxXafzO81G"
        "Vsbxd/Yo29w7wjFRRhT5zDQlQDVRxA3ATRSxAo4TfeH+1xtlodsPXj9UU06064ubuexoVwAv49wo"
        "FAMuo7cWeQi8Hleieyx4GSM6xWOMdHHeRDcLhnAuRBfLnNuwJxY65yzSLYAJ6Di/YLsHwjkDPQiW"
        "y3mAH90Zm8O+htsLiXq7/cLy3bYhFgl1E24S5fbOBMlvXX9+k6S2LVw7yWqtaRg2UQnDPdpyGBeJ"
        "Yt1wkEnyVy+/hJcHc2H3JzZSG85ek8Srds4cJFT1RhkJUnuAgpyL21UU4VBqB6iTQ2ny/kSKUtV9"
        "l2OpbYJ0jqVpv5xStzbJUl3MulfyM5jaBQ8hYarbCP4suzSZf/6+jYSpftGPrSiNRsQ/BppArw6S"
        "prZvtEiaqrCzNNWqyiVpmu5WSW05Z5Iw1d2Qu0mY2iWmTsJUNzg6yVJ9sGNCexzlS/zuPE7YYnoU"
        "eEYW4wbNDLoYbE5bF7MRLteNOgimy2LuQahdDri78r90Mf7S/aPLuRtCfF0fCPhlMQubTNe9PCB3"
        "UJeDeYfH+tC2POaFfEddDuRJ6mZNyLGU19UGNmsv76utBvmd8sIaOKev81ZcyCuV5WC7KGU3N+F9"
        "1s8th7GEd1Q/Wh+dHdOuybsk1Y4HP2TayTsf1bqnRxvsK+HdjI7RHrxv0cQRazw4FLu1Iw9exMTt"
        "wXfYPaX74DBUDG7BBLer5oNrMPF58AdW7fXgBEz8gn4Vh7dYAPFu/QHyekHLjWAXzMJOGBiNVPu2"
        "B4bnbQYtrPG0tiwLh6e15oGYjae1at2tlAFp+wOsVequ/hb4WeFhbSkzNg9rHaLGs1qv3cjL5N9e"
        "6h8PrFZxvw+sVnF7QLXdFnpBtaX22A+ots7eD6jWQb7jAdUqPg+kzj8M2td8IbXdgXuZg9vFLnkg"
        "tX559wdS2/W7+UBq7W3fwP6tDe9h7IHQOsxR4co7KP/ugTZ9QvmYCLdj+ULQHbZ9bITeYQKSbyEA"
        "j3NvQDvy4QWatSCOh/oPm3aHV6fahmge6jsE9FB+J8T0sPlNIKyH3z8Y2UO9YHAP9RDe48HHjkjj"
        "+1MY5MP7HxObkUf6NTDUh9/3IxNR6wteNRbc+mTgzNfQErk46O1eScfprvffscjF/6/mu2vjHDcN"
        "zm6r2sWBbS+9TpzSGv2zCTRrsMqdBI81sp9hsB7EX4K7pmkEbbVyfRGIVdG8BFdV5D8SvnKRP6vP"
        "reHuTYDTOoKApcYg+Zexc3OYaxJYVNFtBAs1DGQvAoBZP0hqD21dgnQa4+AOkqSaNnHQ2S3/joNO"
        "75sfwUGnmrVx0tlDEwMnnXbBIOajeu1/EKSz02sCdBbw0AnSWYKRTqDOYjImgTqtHkM6vajQJ0E6"
        "7bvBkE4foN2LIJ2KXAC13ByOMPNCu1nDTAYtOmQRqNNAnbUJ1NktFAZ12qZvEayzi2D+put/f5SF"
        "KU+/joCy+xO8WijBbmutbG6Y7ESUPgiByl5/pV4r9/Af0C+V4r8ieAHlF9ztq2t7b5AtpZYGT28i"
        "NnRbcNsPaKr/EMVApCN4GgiQRs9HAG2Nzr8Aqc9TpKXBfmotHRFbS2lv0V5qLfUjwkSQr45gZV23"
        "NUjjAtmSP6q/lDopnRBtdeF9MMbqgnNMCKx2qWJBNLWrIhhD7fW/BoFTb2rcCdHSEhFiiLSHFxoG"
        "RnvUYGE01N+viSEwfzQhGtkoq0Y0tP8Y9MYIp79vE8Oa1kcOxjLrHxBhWn5fGLf0RQT3tEui8e0S"
        "7QKGv78YlvRaRnSmE7UX5I++WBLcVP73z3VC3jDqWLaKAVEny4kxwl8HT4cFP/eXfCssXbDZmi73"
        "L8Qc7UbZEHN0OSgDY45eIvhA5liqBsGYo7/fIHO0PmdhzNF11bcw5mj/3IsxR3//gfMnW1lvjDla"
        "fhQVGvVPAydI+vrBWRhzLKPGwphjlxDA+Y8uad1dTAnH9wtSCf3353WiiZMwqAwBlZMgqY7yPgmi"
        "6mjhlhCrVksCsLLd30p4Vvf5SvhWRhN/M8FdqU4nXLU6ZWFd9ZahsY5/3hkp68qnk7VafjOO1nLJ"
        "sFq3vWWULeUnhW5Z+Z6uV8skF1MyJJdJKXpK6DJpQ0uBXX59pnPGMtVDS+eQdVoigemehtVKJvFv"
        "WPZUIh2Gt0o+nNgag35xTNtXcDZbtDrMY+3jDTPYAn83Tl6NNN4bx61qzsYZqxr/Zm46/lcImqpm"
        "4ARVSb84Nq1qG2elaXA+WmsWDkWNVxCChJajgsCf5TtoOPOyN0AkN4KzcbipsU0YaBYmDPPMomwX"
        "zLM06HKkkiEwz1TSG8wz+wqMM4v0HTDPLF61w0DT4Fr/APfLNHdPHGh68J2vp/3vMDNF0wgONNUI"
        "MSe0jCANJ5r19cGJpppOTPlUszaONO2DOXCk6Zj66VhSO2gbJ5o9xUFM3Sw2Y+FI0277sklaGC3c"
        "sqV3+Ej/lQRtYWDzyY4g4nDobFMwVGVbg2GzsklbGPI6TgK68Kn3sxLWxQ/Mzwx3YUz3HhnxwnDQ"
        "fBYXfu1Lz23j5AM7Q1+ccyA9rw2/dncGwFAm6Qo47MnbMgySbSusRPz4TSmsRHa+Bxk+ur/TWV78"
        "tRSLYYqC6PZh1ZOjhKMeNu5bEtHOVEeJQQt5LtFn6fNOyTv96bwl5ez7UrJND5b7KIFmYZS7pJhG"
        "aY5bo8sS05+aV3rcdaWGlJULkEl/6z9n6g2Z9HxX7l+5AVYNHq3DBGhjbQMQo7+N7jw7v51t1jDR"
        "k1b/lMEdt/v1Ght6Ah0lcnLHTWpAWHD8KqmgD8aNWVJBzxnPKqlgsbG3xILNVksqWKYvKamQPhO3"
        "3VbNEgrWVTUUNFj1rBoKGjApwCRGjxvbraGgv/VfiehuHe6ooWDvrUsNBXvQfdRQ0D7zn2p2B+32"
        "U0PBnmLrNRRsLHYNBT1aHq2Ggr6xhswl9IjVTxbkjlv4Zq/TZ97McP5Oa5HGzbpFCFNEd96mmb+T"
        "XpCPxc/fOTDyYNzuFDGZIprzTs78nSEjrYXzLtj8nTAjHZDt9eZhijjOFH7+TqeRvyvuNeR3do20"
        "DPGGpFHmuZdbBmWf3uMl00nFkXfp8MqgTPQOty2UjXrb+9NJ3JE/tO6ZR6Os9Dh77NNJ65H3h1sG"
        "Y6fiBbRNJ+lHVsZ2/3HC2Klc948vQpUxPfsQxk5liotzxk7l+y7nVXSFtTvnSnQV2wfnP3Tx95Fe"
        "w5bCi3MVyT3Y1D+ozv2/7bpfxuE8gaaOO53Dvy57/dnEVwplCgl6u+LZSLqr8JBEt0ubQmI8SfSW"
        "szvJ25YDW5vozkbaroWumbbzOhq14YzOQljfYD+LJK+u3vskcatfdJkhgOVckqt2P/1wMNWp/Scc"
        "TO066uRgqiHE7iRplDovj0IKU4ufJifb6fd23b6+OJjqDsFdHEyT6485TG29SrJU9wZkkCy1t9sb"
        "CVMVkii1J78niVJdGbvrzFbajLTNolSFfZMotS9uEqUWfN5IlOrWxRokSjXcum0SpboBsliU2i7W"
        "IllqW3DQxLQMEVwIWevHji8C2rKYdhDulgHWdyIYLotxe3jRjRKE0XX080CQXQbTNkEIXhbjg/mj"
        "yxnYrkhdH2xnpC4H2x0py9kN8gdlOWdA7qGuz4a8RR2LfSHnUZbjArrR5nz9XTXWntvn2rOw9tzE"
        "91iNLsddJYvQ5cwGuaUyCv7DdlLq8Zq807KXkx9clcZPu//rDmnXHrxTsre1O++J7C3yw7sf+y7v"
        "c1Tq7pcfbIja4L2Lvd92HlxKEntR+xEV+zNiwcSnPXiMJOFi7SZUPO6Db1Bxbw8OQcXucrxtsMP6"
        "A/pV7M7s2sWq7RqJYBbW2wvZLTLnBee6Y7ofEG7D/MJt/Ue6JChabDHHl4e1RuwP4WGtoejuemZg"
        "WnfLb2La9rBWsPsGDysEex5787TWfl6Lp7XFbbcHWlv0ygutVexOA5pgYn+90THxfoC11fo8wDoJ"
        "eK9hreLxMmU3cXuAtYrneYC1dpg7lRDMwMTdRxDMwMQ/ucMMzD82kA6O83igtd0m6Qitw/sE/gYW"
        "Khf3uLaj8ubiZMDyD9p3j+WCwDuUuzOaDfe8uwV8UPmGNnTimP8JcTx+Nh5DefxuOkbzUD8HBPSw"
        "/R07A41vaGD797EeQzs1+g22veUfyOLG5+9PoebnvtTsUT7ST8E2+sPLDL6jQM1Pltt+Qc1Puhuo"
        "J7D5nX5w6Otr5AMHvb0VP3G667IFC0j587LDbDjHbYlDwNseyROc2NYHB8e0BgF1nM32Bt4hgGwP"
        "ng+Cwva0+ibQqyL/1Ck1BWl7EpDVAAyCq3al5BIwVdF3CYTapZhJcDN5yz6GpXZDPwQh9e7HFAKL"
        "9vD7Jlio0S57EwBMrv7E1NM7H76N+xqNV/B3fFJNxwLw/rxjgcWL/OsKycBZZ4uihbPOvkOwzl7c"
        "uzjrNNZmDRx2+j54vwTsLIM8M+W0d/saATt7zG4SsDMRwTp7zn4RtNOgGvBM7w8RgTqNMwCP6v71"
        "3rkQqNNeuAzqNO6GIZ3eQJkM6ewlR4Z0dn/lEqSzV/ODfdc/34rPzuvGCCZ5eBH+TkZnivARN6gi"
        "viA8mSjCRyZRQBSyTIzHDNb4eBH+SvVSRQSwxUtY/rYvZZvzRrEaRD16tOwnesNdezXKPLf/V6Xs"
        "c7foKI7ojx2AnRnaiPNMd0TbAXgZoROAixA/7FcYK3VTwk0nN0haRo92B/Ay/I1Voaz0cO5E9wm+"
        "w/kQXShzbsOW5IfzFbb8v5yDsHcVJucXkgfzU2egvRLdXyl0a5PY132EuUjaJ8nTcsRbOq9Bct2+"
        "2EmY24vplyS4CmWQ2DbhIVmdr/13LWyNxLINRyNZbKvzRhI4yQeQY9cSA5Cotas2neSrNrEvEqq6"
        "CdE6x1LdiGiXY6luRnAstYPqzbFUdTI5ltp5/uJYmh6K71LnRzWeehSEZKkuyPwZ61cJpc1OstS2"
        "KzbJUr1P8jWSpbZS3SRLLV3bIllq71ZMkqW2I8GyVIXhrm0lDG+wVAYQnm8VwjEPyVLdD7mHhKkK"
        "/cvjteW0u0mYWh5CaJ+jfIzfj8xji+kL2u8oi+kTYW9ZjHQExXUxCJjrNkFz3rKYIwi2y/F2DfXS"
        "xZwJQb0s5x6I8XV9BEJ+nZsC2xqp6zMgh1D3j0D+oa7PgtxF3T8T8h51OZAvqbunQ66lvKw2B+Rp"
        "yttq4N5JnXIC2z+pc08syC29pKrxvFTZzw8+y9IRPDgq1crgvdOPtp/FuyTVrsH7IdXOyXsf++7k"
        "XY5q7+b9jPbz2bxz0UQQ9zx4FLtl9OJGLGlHf/AddlfoPjgMuy304CT0UlYbD57BPvziDqyz24MP"
        "SDKk1OTPhxkzsP2CeL2atR6wbtr5wHK7EzYfAK4tdnckBLMv/4WEXKpJEIQn9Y/UP3rtmJbn9I+y"
        "78VzWrXr8Jy27zae06q9h+e09pR7XHAh7ZKXmb+lE2kPnFaxvMzxtdovmNYPP1DaPvtCaRWv80Bp"
        "G6fxQGkVPzDaMqC8MDq9CCaYcfneQdpfDJSAxrVfKK3ibzxQWnv7Gwimw4snHdpZD9NNrI3QOpB/"
        "90DIDuVRvDMoH9C+e9j2Bs2xw55379IdVD4ggMfXlSCEh3LBNuYjfd/YhDv8/jchmMfNF4jooX4f"
        "COrx9y/E9fjOE4b2ePwgvMe2h52NxtdmsCCV8NrLwU5Kw0QhYQAjqB/YXn/U/ivYZkqcemfhzLcH"
        "Tg8OegvyWDjd9YmBjhM9SWQXYlw1W3B2a9XaxoFtjx7gkLYnaAk0a5jKuQSQ9W3WKwSFVbQGgV57"
        "BXYQvNXDfv+m+chFYxBkNdEkcGptmgRDVQQegf6ryzuBSw1A+gbBSA3MCMO5E1Hw6JLkX2qdQKCO"
        "01wE9zSObm8cdhr3IQ2HnUVTNBx2euNciPmrpWFcOO0sLx4OO5W4O1Y7b84hpqTa1Y2g3Y/Gf9Yp"
        "op1GkexG0M4SgRCws5chGdhZbEQnYKdNao2AnR77r0XAzl4AZiaMOkz7ErBL3xpuuUH4u6upPYgf"
        "NfX/Z+29smzZYSTLKTlBPf+J9c2VAVTHCwgzVv278bjA2aCAkNQeREQI1ukvgWdovx/pdIJ1FmHl"
        "H4/970VpVsDw6+XXyt782qO1UtximANQtuVHHSPK7qIQuNvpb7UC79anYi30K4tfRPkF88FaulfA"
        "SUD6BbgEpP6SBDGjI8E8EZCuYLYISGewtYp8nOXDFHhNJ8gSQZ41CKIrpdICvNbKNQPI1tLjV2YW"
        "RBrkfdTKEUC3fr3XD6f8o9QFm38sF13ez4Ygq8UfVofIarUiNoRT608PIdQ6nEyIm7r6bQLR0hZU"
        "A0KkFQ7YGBd1meJHPbXw+rUxAtraqWPYs14jgrFOO0VgeNOr/btZ4d344fg7fDvjYvSyt7kwZOn9"
        "z4aBSvtj+qXGwq+7BUSSju/vmcVf9x4MP5ZkJBBzdD7u17KILu9XIOZoVsCCkKOr5YvN4CylApu2"
        "WUGIDjHH+o0siDk6y94QcixcfmHIsc4S4PxLUw7mwJCjoe1RjfXo+tYw5OSZDNGnFb8YUFvh9dFS"
        "NLg+OLg/8fggdPT9+z0rwu+75sSgo60tvoFBR5tvzIlBR+/f3ReR8J97WwadusVEts4soz97ttas"
        "Y31vgqg6ADoBVh2tvBJ+lY/9ZUvPUr1uQre6tUhPaFeHD88MfnUU88lY+PjrAstHRsq6ZcjJwFnK"
        "2804WstTrNZvfmeUreUpdMubHz1jcN1GJCNy2STBncMLaHTt6z3jdSmPDkbAR4+ywcAXP2G2ZxHI"
        "kiq+CUNcQ7tnh8mtkiCZNpO0DkPafmXAZFbJ2jCOLWp5wQxOW0EE4NUz8W/itDVNxxGr93YvzlX9"
        "nX5xmFpLi4UTVDXj4NhUjeCozF/14X8mtQI/MkIyK2hNGo4/qwIyceZZ24+Lg86+aMfpZn1rBsw0"
        "DdcNUloTyWobhppGXi6YaRYWf2GmqcTlwMolC2aaSgY+xbRuDxdmmja1YJhmjRJwpNlhueBIs5/p"
        "ONLsIL/jSLPfERxpqvFfW2oDh5j9qWQSSFPNwpGmT/NNHGmquYIjzUIzLo401fh9clMrOOfgSLMO"
        "LTtBWhg0e7Kld1xdP5uthbHN2Uo7FGUztlA0ZgK48KmCni/FG1wzwVwYrRpUDixULd02DEM7d7pi"
        "DmWSnluEMh+VvXwjKfniZgfpfC6WZfiL3//MEBi+kbszCoa/ttMFbxgI3NMDj7Ds/Uq3IMNq/yNF"
        "YtwkIN2QjGRB7ZbKSIIEsV8qPWqcswSiHmJOKSlofeGkZJ+1U2sl8Wy23EvMpRP47T5Wuhb9HUY5"
        "b0kxC9wdNbr0CGvNmld6rX986H6w63PQ+2J+p4Q23Et3TSArq3dr7ujd3po1emkfNWDy80Hvo0nL"
        "gzx+V53/AH7otVNqaOj57Rg1KdLXK+7/bPvV/35dqmXU9y2ZYGXQbskEKwJfIsFCaEeJBOvvdUsk"
        "2KizRIKdtK4SCfquWkkEizndNRHyumTe1xL/xTZxrz3AXMXqhkmNBL3fPMgCKebufrOTbyvV8a/t"
        "EMNe99GiigfOtT2qPulcO6JWF961s9dMMHMApgxqks4ez/rbzyIvlXycIYQZYjvUXX+7XaTRpc7M"
        "YP1tfpGWR7/eg0xqiOW9zsXdhTPCZkZY4g1xmCGO889ff9topEM41r2crhqpaTmH/stpspGO4cy7"
        "l9NzI4uH/KZnXI0xUPGCKpfTkiMbow/3nU5qjO5ZR1vUs3h/lLa5IdxPy1ipuCMwRirekdJymn0k"
        "Y3Rvw2Y5zT+yMWR5zyJCjeFimLJRb7mwnEYh6UdZnfMoNqNfnBux0uSD8x26kpPNOQxdLruAnrXu"
        "u5xrUJ0sziHY8y3OC1g67ODQbysREvcWW0wi3gqEb5LrSfBwDvOk0HdOcK0sLo3EtgknyWq91bFI"
        "QquwkVS2d0OyWJ9wCwngH6G3u5JT90d43f+F1HbjRfzlgNV46XZJqupGwLocSnV9NS+HUks6bBxK"
        "NRLYtbZR6oY7y5y1rm0OpaoTjqS2GUKS1BI/N0fSJHM2R6nGHLvLqFYajHQfUKXFRJwpTUam6+3b"
        "qIXuv7DN+lZd0rRVC/1FyK7fqu+hzutbLS3HbfWT0/RHGECxtJz+ubMhkVq4WZpqILg7b5PackCa"
        "VpGJ3kGaA9cywNFdpHdyGLd2l4PecphvIyQuwy5dci1+GAjU5UNJR7hdR7JOBOOl3bizgL9UL8fZ"
        "E4J8bcfYvkh9PwdyAdU4sjCPUI3Tfc8y6XF8n7jo5zobch/l/XwCeZNynI1N1atx/PWl0Pbspa56"
        "rqca57jvR2h79neEaHNe7tJNaHMerfNeS8+13XmyQNrP3cbpiNYNHSydkoUEP3gijXHdD+7Hqktf"
        "3ufoPTfez9hrHrxzsbCF9uBRNJXexwBmWF6yZe07rAfheHAYFqzy4CSsBNaDY7C4j/XgDfSm74sL"
        "ULELpIaZ13QJ0DD7WuMB8Lqb66MHM6/rvi/BzMsHiGDmtf1NaNC+/JlHrrUoismj2hrfNR7VFhN8"
        "eVSrtj+gWuN97+ZRbbHCm0d1EgVeslrDR/rhWW1lAV5m/7oB1ccDq1U8Xub59sv9gdXWbnI/wFo3"
        "z76XabyVJpgPtNZnPvOB1vnbxgwsODrDLGye/oBrK6H3MglX8XyZeeue83zBtRlJe8C1lrvwv/N/"
        "tVGE7XFnX4LKF8TsuHI2dHgZF/5eCLnjuuOCwDuUX+hEM4wtb1B4SxwZ3RGKh3IfLR+svxDKQ6v7"
        "sFPPMFS+YRv2Yc3wCyE9jGZ3Y8XaxPUQ10O5YGgP9R07Ho0rnkN8j+T+OkJQ2xOvg7BH+UDf/Z1Q"
        "EVg/sD3/6P73wmbnYcIHznuN4Xc1kmrmwcluMSU4zXUV7a7OZq6RjXPbVusNh7WVbscBbZXbcShb"
        "wBBDYktyGAR/LbRlEdC17u6TIK3FphB41SiBLQRTTTQIkiaF2WJ8qmgNgpn2Hi5BSo1BEQaPWpzO"
        "3byT3CD2EQKEKvKX+LlBzDUJ5Onb6xcnnU7ix8VJZ9NvAnW2xmk462ym3nDWqcbdjFmF5uCss3sj"
        "ZqO2PN047axuuxC008yF2wnaWYbIIGinoSfnELSzmmubwF1SqC3GnYp6I3BnJQiFwJ3V/bsE7lR0"
        "O4E7C2ghaGdV8ZgZoEZcLIZ2JtoE7Sx+hZngWdRTsI7/XSE+P4MMdl/xIaZ7F50Zot/po5EYogcR"
        "dcQQX7C4Z+4iWODjQ4wbzCGJj/oFlCWG8JcMHzdGNONk7DMgMj7EcWNCG2Og8vnJYoMaI5ytEmPM"
        "KJSPGOOL5rLM+4g2e/Ex2hfF+uFj+P96YcxUtkTzYHyME0VWE0OcyG3gYyx/M5sy0zZJp6IHiJwf"
        "0QXz4XyHHcMfzmFo4MAdnJdI6umnrkF153D+wFJmDucELCVoceS3Q2uS9ro/4B5DtAYIFwl2FR4S"
        "5pZsM0mC65JykNTOl6KrvtPN8tmaty0Syvkv3voZL4tfXdyzyFXd2SRoVehvdtR2wwI1rhOSQtSS"
        "0oXDqO4t3MFxVNfwa3Mc1UP9KGG80rEcVZ179rSB5+MwatsUjcOobSWxHNXtisFyVLcseiM5qmvH"
        "zoLUVuyDBKntDyySpCr8BklSfTljkyQ1IUtS20FiSarbNIMEqSYFuZtwUhvOOoMkqW6ktEWSVHdt"
        "/DCN2nC+KK86627vlLaG0FoWNo+yV7hh5oYmsOUwYyMcrtsqDATLb8Ns/t0g0K77FkCbIHVB9Ash"
        "vczs8WcEvBXvDQG/fq4F8b98LoG8QZ341CHnUI7jfvW2+MfqkOuoxxHIk5TjTGyzpMwM25ijKXOf"
        "5oD8TjmOPy8X/n4O5JXKlLd1ISdVvud2eZ9lCRmd91Q/2t1576RNBsbmXZL2NMDWA752N975WC+F"
        "znsca0NxeD+jr3lM3rlYh4Hx4FE0awZcKMDdAGrfYQ0YXhyG3vaLl7B6qg+ewfoSvLiDNBGsbfCJ"
        "X8BvX3k/0N66c84HxFvtnPnAdUubuQ8w11/+1gPBLVbrPGDbDGzwrLZq9ItntVZx342HtXZPOJOH"
        "tWr74mFtbS54VquUJ7UqXaM82EsewpPami3sB1JrblJYkgQQf0+kVrF/WNkxcRiZgjzzeWG1iud4"
        "YLXe9jgPrLZGHC+stm4h54HV9p3PA6t1c/OJ1SqeLxNv3Y7t+4HV+sx3PLDastgawuowg2JAU+sw"
        "fwPaZY/U/ibfQOX+Kc2E5RNCN/frG35zrSEID7/bB1E8lHcsmoUzm4ab3YRoHmZMDYGAHmfuLIjp"
        "YepN3xDWQ33DjkLJzCPY+PzjTdj4ggAi1PrkW9ieS5j80rDT0rD/RsdQH7f9wGbmYfJJg3gfJ24R"
        "yLeE9IFzXtcQbixRTzV+nZGRavxqDDPXRPkrmWZMnNhJm5MQ01bjgWCzBgsJwWPNSPLr3+WGcMA4"
        "k9+iOQneWq+NSUBWwwSkE2Q1USNward3CYZaopEQ5LRfGgQuLV5iEozUVJ62CDBa7xKGhpY0dAgE"
        "Wp1eIcCntuefIPsaDVeYxKzW5v8E7WzaLzjtdFW3CNqpBjuO/E+HFcFpp8/TJk47jbTBYqt/Zwut"
        "TeDOagtcAndaQFWYmaaK7iJwp4fyFO6stcsicGe3twncqagTtFNNGwTtVDQOQbs0O0lSg5A+CNhp"
        "zIUIATsTDQJ2lotCsE5NPCgb9L8X5e0xfOLVyjX8hiu1cjY/f69WDj/oGBB+fiofoOx+pSDgMY8/"
        "BayV5/NTmQFlDwAJSKMDMUC6gtg5wP5OMEMspW5rqfV/WkulnUNmkAAISIO9VeB+o6JAgDRICARu"
        "9wZUraV+vToBbEnuDhbapbQ3CcLpAOkIcFvfcFB/CLGlPjH22pIIA66eBLqzpB5dPtaB0KordfeE"
        "c4aXzwtR1OpDXgidlsGyIF5aK8IBQdLyJA5GRuviuDEcWq0GkIEa8d8EA591dNwY7aySQccQZ9dP"
        "DGx6P7NjNNPro2P88HkFA5fefxSPFVy//Qld+H3PdzEu6fUYirSExHcw/lhFDAw6aea/RJcHdXuD"
        "q8cZEHNs3YcxxxIPOsQcvRybrVltQgw5+l4w4tjKaWDE0ZD3OTHi6EIhOgwJrg/qtUTf1e0X6RLH"
        "VjsYcOx2LgYcvb6B0ye7HuONXj43xhvrPtIw3mgxA3BGZN00BMONXj9A4GjyAQocK2TRE+CUQZwn"
        "408dijwSHpXx2TebEr1FrU9UPRJ2leKglAyo3jtB21sU+UU/d7oIrdua9IyDpfxLsfgo76j8pIvS"
        "Mvp6nAyipbynq9Py5u/KEFv++jcz5NbdRDIAlz0y7sl4XLai+FI+l/IoCAiUR33hMLlfDVVQowsq"
        "crpqjavdMM816lkmDHEN3+8dJreGkx+Y1haAfmFGm0RgMNt9TZjGFiaOI9iCtHHu6jl13zhsVfMN"
        "nLB6a5vAqv7ObjhLbUdDcICq5kycmqppB0dlWsOinfR3pONUtAYXC0eh7aYsnH+2lTVw6Onv+HGD"
        "qR34pdglt4ONz1ctzhifpFrIKg417TywGww1lbj/65lJtgvClUrWhammkrtgqlnY6YSpZgfSONV0"
        "F+AjppBWiWHjVLMqDDjUrEDkxKFm2xQE1GybRXCo2WsbONSs6wjONJNcnGm2r0NM73S7pgnONNvi"
        "WTjTrHctwTR9nttwpllSQDZPC2M2RzZXiyvkZ3uAcVn+hG2hSLJT3TAG/Gb7gnH0dLamDnsdjJFw"
        "Lgw2zkgXis7NaBd+5E8y4IWylq6V4zDkk3EvjD/dJ0NfHPWbnmSEstkyAIY3eW/GwPDX8rVv2A3g"
        "GxkKw0DgIRkNw+L3KQ/Dkv9zZkgMZSs9jY1k6+sZGMMXuUo0ZhGz4l05bisZaKX0W0k+q5xX0s5i"
        "iGeJuHSptP1bXSXM9PC59RJhthY4Nbc0rnXtGlZ6rT+P976XfH3WWNLj2jVqFlnhul0DyK49NXWs"
        "WtyuUaPXRoWU3Ge7NVT0mPUDSKKl3/I14u+a+Pk86ve1bniLuN9t9FbjwY7wRwkFLRfnh454l/ot"
        "ybp3qX/ENdxL01PR38G2a5RYsEvr6Y7lQO4SC+kbuO57vQAWNJaz1VSwsE+pqZDXovc+WFSufbjX"
        "5jFk/4nplJoKVjKt11TQa+XWVNBrESpYrftRU0Hrn32zpoKdOo6aCvkJpfvd/BAEcb/b5/wp99/O"
        "Fml1YMdU999GF2lcnnM0uP/2vUhLRx9viEEM4aba7L9dMfLYz+4MsaghxHuQTQ0xvS9yqHdxPLu4"
        "1Bdx9oO202CDLW6+nX4beWSsNwRln16/lO0040jrgTv/4O305kgjSbtnXm1SYyz3PhZ3H9sbY1Nj"
        "TPdZGCvtXvOp7bT5yMbwetRsp+1HNsZ27UMYM+13eXYqwo3hEUwYO+3L/dvK4L7L4ryKzakP50qS"
        "otip/9A10lic09B1mHCOQpeFXTjvoIv02ziXoL/HeQFbZAqH/mShlfPegmEbCXlb/rBoT9ZjOc9/"
        "hAE8S4vpXuXunNwq9N/qqoXu52+l1fR2Dwlm+8VG0vhH2IVF8I/Qa9Gcc/dHuNzvKFIL3dmZ9PoZ"
        "D0lVtTh/6hHrNCLzDg6l1neMI6muIw4HUktzbBxJrSL65EhqK/DFkVR17jLp1Pd5OJTq6tSfK36l"
        "sA+SpEn8bk5SXZdudmb8v8LuLhpbaTG9iZAgVeFkQapC19baroWb5OiPztvSyjn6Ixyur5DSbLoX"
        "IJFz9EfoQ0Zq3dkkRvVOheWovtQmCEer6MCNbXbUAZYLwWwZ6nig+Ws5TIMoXEZOurP+RQ/j/m82"
        "P4wgyK4jaRuC8GoYL8/HI3o5jj85o+14Yrwvh/E3JGhD9uqOeu6gGuf4E3valL0OnZ6zKMdp2EZJ"
        "OY7vLg//fjDXUo1zDzZjL8ZxD9w8x1ONMyY2ny/HEcgtVcME49DmfF2/XLwd3TQ4h/dUSYxp6Z6s"
        "V/3lfZLVW768I7J44s17H9WOxbsc0z74GYs+6Lxz0W/kI/yDxAvcV/fF7lFLw0xr+44Qs61z5MFN"
        "6GbfnQ++wRLa+4NDsCpk58ELWBzHfUC/bXDOB97bht58gLzuza3zQHbdn5P5gHPdRHb/VAJZmPRz"
        "HshtL6zzuLYqUYvHtYbpnsPj2sJ1eVpbIHbnaR130CthrdLWeFhbWPviYa2/62LvYm/5vkz/dfPJ"
        "9WwNs6sD7pEHYnmAtRVYe4F1EqdSw9o6++0HWCdRJDWsrafcfoC1idsDrPW298uMXCNG3B0ngSxM"
        "lvu2BbIwmXM/wNqKJrxMsy1qCjqjDKsnL2gjKIzQndAMOw4enwi249LTUKRLGCjv7jMuWN4Rfodq"
        "LLglfPQD7eeEL75DHA/l7oFVg63u8zexYbPzAnI9oMc1uy/E9DDmfmEBLKHe96ML/32B4B7qNxa0"
        "EqcBYPPxQN+bH5yB2l/3v5+g9vcPuBdifazH5uaRfnwXIn74/s/BoW9RBgcnvS0XF453K3AtONMt"
        "oqThILek443T21btC2e2alrHQa3PszdOZ1tdD4LJGjEExpz8pzA4Q19djhLA1Wpsl6HsT4DB1xm0"
        "qsg93WgrFw2CoaoBD0N/i9zDvpaaQ2+DQeSPaPhz2NQc+vwGAUP9JXDC+0skftRJahBy/OBIX2Oh"
        "4xdnna48Lo66pPZ2iDpdi66Oo87CNnDSqUQaTjrVuIZw8sf5Ok46XbLIIUhnmRmDIJ1Vr+sE6XQh"
        "KItgnVaCm41gndZ325NgXRpxsvIfOptgnYrAALrfd+faaksNoss6BOt+RHN3gnUad+FONERy0WJm"
        "e3p7bRKs07fnB6T/t0x8XgU7mObBQ/xblQezPnyI406aBjOEP1ebzBBRFgsxwhcEcRBD7GCh/3/7"
        "Ni81RI92bokxdhS0QdjWivZxcRMPNlUZA5Xhr4AZC5XVo2BoYowR7QQQY7QA7sQQErEeH2O7i9rG"
        "mKlcN/JTGDPt3TV1Ycy0R+d2xAhfNEHGx2gn2iYgvuxanEuxleXi/Igu/91leS91fu7RKHVrT85N"
        "WA3+wTkHiyk5nEfQ35POuYGkRVvK/p/vR9JeN3yERbyZyyW5bttSQsJcdxdaIwmuC8pLUltTGNol"
        "Ua0/uC4JaBOSUFbdZkmsj+jOVaS0m3+k6iRzdUvAP/uSWuimXEhtN/cuEqpWzp+cnOvKdVyOpLq7"
        "4L6aXurOJxxJLfyCnHCr7lscSTWYwH2+XeuucCS1LZHDkVS/QxihVnz4thoJUz0QpmFqx9CdhKnm"
        "v0wWprrv4TuMWQtHI2lqv9hJmtoWzSRxamX4hcSpZs6wNP3R9d1Imuqmw3dJmqqQpqlu3fi3WhvO"
        "3tC8tMxrEIStZY30eRHUliXy10XIWw7TEA7XDRYOguVymNEQStfDbATa5avBGF5/b2w3pK7sPyDC"
        "l+P42YC8Hd8F8b9OOpqQOygzsja2Q1IniAnkLMpxvgP5jvL9+PEX5//ROJd/zwvyNG/5S0Lb8/H3"
        "5ml79l220PbsR+sLbc8jKjOVDaMJJd/hXZUV5++8f7KuDot3StquwD3gnJh2CO9/VNsenI5qv8t7"
        "Gn1XbfPuRb+RyINPsYyh/uBIrG3Bg/PQu17y4DGsL8N+cBO2ISYPvkHFcz44BNvCGw9eQMUyH9Cf"
        "izEDW6c9QN6ii9oD2XVz7+4HnNvO4HlguN72HA/g1q1T6TytdZPhNJ7WmmExD09rzez4HmitpeRd"
        "DzMh7RdVIqm1342qkSDaw8Nab3k/rAUsgWY8wNp6Y94HWKt4v9Baxa090FpNussDrXXzrJ8HWqt4"
        "9QdaW/OG+0BrfeawOh8ibueB1nrbsh9obfWE7gOtLfNnPtBaY7Pc4heCWdjxgwIxC5v3ILSOUwo6"
        "AuwwHeMOhNlhh4cBYTtszDEgcoetLPZF4B3K3cnUhm/+g7Z2wlfXoTl33FsD252Ps3gEgnlsOAfi"
        "eZhK4x8OopYnfkxtQ00vyBRuE9ZfbCYe6ie2nR/rN0T4MAFOsC2YsLWFTIjzUSrI9x0I9WEqzT4Q"
        "7UM9NjsPM1EutrMSvv7ecOrromANHPVWe/TifNcF18CZrgu80XCQ68bQFpzeqhkLR7ZqjuCctldw"
        "cTjrsmssgshJS5AYw2nd25ZagsjXCOBqlAp4Pvq7BUZn0KqidQmeWrMNISCqGT13EeS0X2oELi1U"
        "h2Gk1agVAoyaakPRMEsEktwgzncI7pkVCQ47nc27W5KSaYLC+T3VrEPQLo3gmKlm3IXTTjXz4LSz"
        "dTZBO1uCELTTdy0E7PIEmMIQ5iVgZ5Eki4CdRpEwrNOkmSYE6yzTZhOss4rABOpMcwjU6d0tgnQa"
        "Y9IWQTrN+jiXIJ0GXoAxyr9FYxOoszwggnT6wv2QmZ+L0sD840/uaqVfkKHXyqDEywCUxz8fq4X7"
        "+OHHgNJfrANC/1wMeD3iYxFQroCO9df83I3whpjQd4PCbrW0tyC1pJYuCbKda2lQn2gi0qgcNCD1"
        "fcNGpCPYVq2lQc8VwJq6P3MXwJr8AoUCGFMPJnoCSa9P21o6djC9BF5wcOr1X6XOSd2DH4kub0GL"
        "Ev/ydueCyGp1IDCeWn97DKJWyeFA6LQCExAv9UndNc4N32MDyair1gniUGs8RHl2wfXBmXj0YcWv"
        "P9SiL9u/ezHEaULBxLCWD7/D6w8IMBsfpFbaJ0Wiz9vH2BigtGZD7xiVdPzbMRRZdsXF+FMUafjv"
        "5ZqXvzcEHSsKtyDo6OnZmRB0bLU8IOjYYSYGHcs6gJijV7cFQccWn9jMzA73OgadrIlKi7/qEow5"
        "usDy/1TRd/3n2QRjjq6rBJxW6fWzYdCxbP2JQUevj6JGg+v94not+ry9DxA6P9dH1RKDy3fUJSO4"
        "3i/ZKdHnjQo6xJ93Zcx5a10hoLrLTIj01hpigOoWVBfH1L6nXKh6ZavPWp1Nqd6C7S/6ztfI2Fd+"
        "8Kj8DCrvGRpr+cxIWXfbmBk4y6jwuTOOlvKoUycoby2jbPk/z2d65a9/J2NwGXg+0iVr1YDhm5Ih"
        "uuzfIC0jdiVvt2UAL29eZsbz8tUFCWKeWk8r+4SZroeiMmCQa8h0ulsYxO9vGNk/khaUN8wkDWaz"
        "KoLQnexRpMMU1nfcDo5ePUjvF+etaQjI5hHZqQH4idIttYD7DZyhVkoD56YVnhw4LNPim+3kmoFj"
        "UR8nausWa6T7s7TMDCRY60qqkY2jzrZkOs43jVgQHGpWNl9gqFnUKw41PS79Bgw1DXP/Ggw1Dbvu"
        "HYaaBrWfDlNNJQunmt7YajDV7IC541TTQ/a1caqlXTGa5L/TcKpZ2QhikqgbCgzV7PB741jTHZ18"
        "pR0EI18ca9aPVXCsWXmIiWPNillOHGu6u9IEx5oe/8+BY82qVhBY0/d2s6V4GLrpxx4Wqi9o7Zuq"
        "2snOIcLY3pFN28KI5JXN3OIw6JFwLv6tbL8wjlnOzirCVzjSI4tQ5i8+C+NoQYvyyjpaOp2Lo1BH"
        "xr4w9tefOc1KNtPDjVAWdUIvZLIzDoYtAlpGwkjl18qRwkZ6T2d5YReAKASmkkkGxUjmVziTykb8"
        "qkO/H80mu7vkoc4jWw1BC8ftJfr0xLOXuLP821YyTi9tswSbrd97STOL5z4lwnTdcUfNrbw/nvu5"
        "gswL93v5Haab98Fk7VXDyGrZzZpAGlA7eo0dO969NWus2lzNFxtWaqpYnbZRo0SPK/N9sl/X+nup"
        "Iu61rdWoyEOP3c+2m5RQsClcPUnSmfUumaDztbNLJthxZyuhoKuOPUooWHbkLaFgl9ZQsCTVXkIh"
        "nbX/Bwp2/AzMYPRzRcUYnGun1EzQalldaiZYZbVTM0Gv9VmziHG3e+08NRT0WLcDUw09Ev1uDYWf"
        "a8fXayjo2ePcNRT02gPMH/RItrcaCvrOnBOq87fRRbrh7wwgxADN8xHnbxeMPLJ1O0MMZghvy+P8"
        "7ZGRDiHeEIsbYjpDbGqI632RwwxxnI3w87fBRvpRm3cXf/ttsHXbj9N+Iz0QcrzpcbpxpGdS0/uu"
        "jbHQf5Mx91kYE5U53DEmNcZ0vwtjpDKu929rm7qPzzP0dqgx3L9sY+xUjsc/Ycy0y/Y+izBm2sfy"
        "XqkINUZz74Mx038TSo/FQpnp+oTzKUm4aepKdF36Nc5/2CJ1cE7DYnSF8xRJ1fjUPdi6d3A+wY4M"
        "O+cI7L1Mjv5WN4lFvn74RmI+OajL2a4nb3uTQNc1lLAU10Vo3yS69Rd3I3md5PTmkLYU3UOSWYVz"
        "kzi2nOVGQljfqmupUluOO0USAT7jJRGbpDDnXLUyaIeDqcUjHw6m1vaNnIxbxSQSpnpsvCYH06RO"
        "UgpT05ET7KSoUwpTOxUdHExtt+SQMLXe3JOkqXV+nyRNk+2HnKZ2usjSVH/xXpKmJmRnv7YjxtI0"
        "6bOe09TaCJIw1Q0e/49fG87ph4Splao/JE31F4+QNLXE70XS1JILLkLTl/hOB65lhO2FWFtGGbvr"
        "j0EP80HT2jJi2p0FLHqYDk166/jtiWC7fDfuFtVlhxkQ0kvr69h8uRxHLgT8chwM/2XUs/vFG23H"
        "+2JT7bIOuO8PaUv2+rZ7rqOuk34hT1Lfz4Q8S/l+zoQcTRkw7s6QhDVnGQeb1FfjdHeZLqw9S5MB"
        "OanyPfu7fvkwugVwG++orHTX5r2TFul+8Ega6+16s4lp3b/agrTt8v7GpMI7GX1T7o7ChbTTJ+8H"
        "ibd7cNMwu9r9xXUkKfG1w7DNqf3gJXSHqsuDa7BtxvPgDywU/zw4AX3mKQ/kV7F/8IBZ2HU3kQSy"
        "MPEnlNIw8T0PNNeImv1AcHvk/oBtKw7ReVbrDoM7HRNI2/sDqzUM3QXBgLTNfd6Jad3p8MK07pb/"
        "Bn/3gdb2rh7WARa7vx9ordtyX3+gtZUDmA+01g0sf+cDsy13KtUw2wp2wCYo3g+wtuyXF1jnLxuz"
        "r+0v7S74zOsB1unOiEAGJmO8wFp/eb3QWre5/Z38AX4qaDcoDPt2F4gCyttxowo6Kt8fFPISBvG7"
        "9J2ofE7oLJOpPe/wO7x599kP/OoGNOcOP1zHzjnj5IQLsTzMUujYsWfctQA7/Qyrv29sCh5XP8fA"
        "HidOYBszYQqQ75U2rt8Q4cP79yeJqP1JsKhH7a83f3qM2l/vDdtoCZMaJrbtH+Z7gBsr4fs/A8e+"
        "rijWwVmvKwlpOOB1AeEuuEaqcf3nzCVu5MRKNf6hxy5+hwC1vYKJ09kquU8CyZZ3MQgOW6zKIeCr"
        "gSpgAOHvUun+LDS1Bdl+uGNqDbLAmMDft8dAVONuXBNqJxe54U/t5ncnh2CkvrwxCDBqSIj7L5fc"
        "ILZrelIYRCOwZ+bacdbpnNr3D6lmu0DpqWZugnWqwQ4p/1PJnYCdaRoOO2vRNnHYWfV3YipqBfgG"
        "ATsNC+mTgJ0moXSCdbqc80PkUlOQ7v/SyEVCoM5+iJk76iP5MRy7EDWCdXZ7DOussOUlWKfJPe4k"
        "VHJ7OJthnf7S2QTrrB3AJWBnEUxB4PHvovFs2fHzt/MF2/f5/G2EkZ6ou0F4gxli3GBnlhhiBBu0"
        "xBARRol3EUVw4EOsG6SzEB81jG0mxrjRfBMf4/hzVspA744IDY/h9j04Tr+O9ODfn7RPagw/f21R"
        "Y7Rou5cYo0e0x8foX7T5i48xW7Q3gI/hp24JY6c98hP4CJ9/DkdZqb8XL5yV+icJ8RC6JD2kJ7Ej"
        "xMu5D2ttPjifYd3jOD9h0SGLcw6m4xxCUmYv9QIWa7A59Ftl/U3yPk+CKe3F7aCbk12XeOeQOLfV"
        "+CQZni79Z/2DvtMojUb6uSShVUhjOU8tusCtdhLA+lLDMLhCuAYLW2u/cEjC6jMOFqvWO/FwLE3q"
        "QaQsteQSkqVJ77eUpRqGcRcHU9XNw8FUdYucXltL983R1JJgSJpaUtEgaWoVMzpJU93uGIukqVWi"
        "I2Gqa8+2SZjqDx4haWp3OkmaWq92lqYqHELS1J7xkDS11CISprp94O+V1nbjVhyQ2mzWx85W9QkH"
        "iVKraNkQlJaJDR0ia1lk3531dHKY7w5BuFsN4+cVTXqYMREql8O4G6Kbv5uFMLt8xQtCeJlXsyZE"
        "9DIFqi0I8KUdH2xfpE6C6hD/y+f6BuQOyoyhcyHvUI+DTb3L5/I9+ebfz4JcSfm9/Fga2p7HgBxN"
        "mauxIbdTpo74t8Nas3zfhbxSmTI0MS9VW+HhnZYmSviVWiCtP8fqkNZ3bQPRfnd33hGpVhbvfVT7"
        "Dd7lqDYKj4be1YNzsUSYB4eiu0NtPHgR3ZHa58F1mFXOB39htz0fnITl77x4BssLWw/uQG97nwcf"
        "oOLvPoDfQpDOA+3tmR8Qn2/mQgYWxBkJZmB3ywPCLU1LHrit/4vbeVhba4MHWP9oP2zTxtN+F9u4"
        "cbUH27zxtUt4WKt2TB7W9rubh7W+Z/e0/GLf975M/5NOITWtVQxu7PhpUveF1mkYUYOMq/kljtrE"
        "xPIAawtKug+w1vflr6ow+wqCHjEDm30+0Fr3RlZ7oLWlo7zQ2qKsXibclo7SH2it39mP7/qvNu7O"
        "AO0DhfkceyHMjuR+/tBA5d0NS5qwHJtpx/KN8Dt89g/a14kTcQZC8bgDyIJAHurDXBbQ7sBTzzCX"
        "xs9iRy0vqB3ZUNMTv2xAm7Denw4v+P79EgAb1o8NET6+f4EgH+YSXWxWHna6+CaE+jCXBDs7jeRn"
        "Doj3kd4PaxDc/KIMRk+uBQGiVJZEs6IS3YnGtcyRSoZsHOS6At8Dp7eVJ5k4svXe3H/qyV/BWTic"
        "kyYjMZGta+MkMGw9SjbBXl3MfpcArhVzYChrkRSHQKuKhMCp9VTZBEMtIewS4DTRJGiptzcmgUhL"
        "miGwqPEgg2Ch/c4mAJg0sYmpp9baF446K74pOOqsTEPDUWdLnYuzzpbQBOtsWwVHnUrmxVFnTTYP"
        "jjp9bYNAnfVuuQTqNPtldwJ1GkcyGNRZo8lDoM7WnotAnTXR6QTqVDQXwTp7JiFYZ0UWGsE6C1Do"
        "BOus640QrNP8lzCVJRHNw8z89JeuELRLI4Mkp8P1iw/+XJSeHfoL+VLY/FYwHVBu9xxjAMol/gFZ"
        "rZzLLzOKKP14DOBuhx+EDLyh6++1Al9lBoyspUHNsYZI/ShmwIzku0F1iVraJZgm1tIRxSQj0oCj"
        "gPQLSnsC0hakQgPSG6y5a+kO4ulKZffzBAQwpt6jaIZaGlSBQ4zpzgC7yAteEHyL2hD+5e22C3FW"
        "14MbYqvVghgQUK1PpkAU1fXsnRA6rbWmQLzUjYkPg6TVY9wYGfUz+WVvws8q0UlTcH3wj44+rKwx"
        "MdpZdQLBEGctPRvGNUsHmBjMsnIE7YSvZ3eMWrYavRir9PVMwQBldRsWRiUbHyORFaAQDD9FoYb/"
        "Xm41GgRijpVnwOZ2evp2BIKOFWU4EHR0qbgGBB27vEPQSW/mRJf7PftudPkZ4HTM8hDAOZgugGbH"
        "oGNVBkDoWB8LjDlWYmFjzLH6BeBcyqoOCsYcvf4ODDoWXQ9OlXRV+DUMOlrbYDQMOtaiVDDoWO0E"
        "cP5j3V07Rh01N//47ufyOmi2JxAqQ3fnTphUN3bIEFXmK+yZEKtU954ArFS3lvCsVMtM8FZ31egJ"
        "7R6Dtj/YXGbGwlLeW4bG8uZPui4tm1z4G2eowfnz8jZh+c64WverGRlm64YjK6NuKZ8zg3AZfO7O"
        "8wW0OmnfzhBddoMYOyN22dxCbgbw6tnvThex9asbMN51iZcuZoNmDwsGuTZqCBpEJJI2cWSr5Bsw"
        "pzWCfU8Yzio5MJD16duFKaynz/k2oB/w3C/OW9NMHLJ2yj1xslpdhoHj1DZOGs5Q3VM4Awen7bhs"
        "nJb2PBNHpP1Ox7lorSAODkPd+GgEAXU56gemZHYgX3Q6kj3PbjjgLBgFn7TqGtI/cc4k0mGoWWOB"
        "DUNNY7Bng6GmkoZDTaPi74Whlv7KSR+/T5hq+ln8/fMv0/iHMC39/CtfVTNR6qkF+BueLTWBfSZO"
        "NdM0nGoWC3Fxqtk+0MGplu4dtdQOdhTiEmv++dCDU82acU6canYkvXCqWSeGgVNNv0+ThGphLfi7"
        "ErCFUbfZhC3uGHASvIXxydkBbxgTvVfCuFglCebiG8zmb+HL2NkULn7vI+NdHOScTuRC2RoZ9UKT"
        "isoDpjJpJz28DYvpSzqpi2WSETAMN17pgS0pO9VN9hSFYVDwTGkYhjLvmQEx7Aaw09PZuIlAeh4S"
        "xmufm5ExfJOrlXDUWeiaJRF18ik1B+1c9ZbwS4N+p3up1JyzvNlTws1q5dVE0yXIN0qM2eoLYJd9"
        "g1MDS1cnQ2pK6apkS40mq263ax7pUWmNID3W66fmjt5BvzVsNG55A4SxbgK9xordQ40SO4/uNT/0"
        "MFQAaOi4/daksDP0VuMhXdb+vl2dj/USCXYcOEsk2EHjKJFgyXlSIsFSLk+JBLt0lkhI17/HfaxR"
        "I6Eq6+ZcezeABIuhPTUS7MC01Uiw0vSnRoJe22cNhbzk/XLvdwNQsGtnDQWLMgWgYMsggApa2AyY"
        "VOhhZVQd3hv2jBoKGnXbZg0FNR1nq+P+7XeRx4eKM4QwQ3QnpPD+7YaRn44OZ4hBDeGcfNy/vTLS"
        "88LrPcii7sK7iU19EGd34P7tq5FG0Tbvm15miL1dy/qoMZzd2+s04cjbt3uP0oR7Fvc+KAM9/vug"
        "LNSrcXSdFh7pGM0zsEbZ6HGWF9dp8JG3aXffKWWm10VPY+z036LTuw9h7FTO9eAjjJ2K/yzC2Kns"
        "4dmYdO59ePQQyk7995G8DquUtDlXYlWlGuc/9GBxC+c07EBycp7CGt9vzj3o7w3hnIK+l9s4T2Cr"
        "dxL/SfGlnPnJojYHvQkvSXcVnkUi3dbUjeS4JfUKCW8V+l5w1c84N4lpO5lk2WxrzEsC2QrPsxS2"
        "lfUi0Wud/wbJW9soERKy+nKcAmE5We1QfnE4tSOSxeHUjhmFw6keAbsYHrWuHQ6neoJ6OZraz5FT"
        "7CTNN6Wp7hAISVPL3N0kTa3SeSNpqotidx3WSov59/ftJE0t4LiTNLX1O0tTK8reSJpa/rCQNLUc"
        "4kXSNMmNzmlqb7WRNNUticXSVAO12cmr7ms0FqZmqo2Eqf6r1kFg+lJe3GFrNYw/Y+/sMMvddxj0"
        "MAvaAamHQbhcjnIGgunyDS+I2uX3doe57DBepWGP6eU4PnBpM77g7kg9DuYAynH8KSttydffsaFN"
        "+S5st6Tu1HAg51G/nwn5kjqp4kCu5aWvgedpymwDcAflJenBc0R1nwVsJ6V+P5CXKj/7eXBaVty8"
        "8Z7qR7vdJUvHtJ13ST/SdR/8kGrdRcgCf1d4l6OPOxrvZ360ZwnvXDScXtqDR9ENKbkPbkTF/cF1"
        "qLadB3+hYn8KNzCxvzc5MfFuD+7AXvZ+8AH6md2/RDvgL8sD7S335D4gPqlQWHNdxe4kRzALE3cP"
        "S0ALc7fcZID/yMnD2oqqHx7WP1ovVqyEtWpl8LT+0a7zQGvVbh7WKl2Xh7U+rrvDdbBP9D2sBCyz"
        "oD/AWre7xn6AtYrPfKC1in3sdVB8H2id//LExH080FozOvwXtjHx6g+0VrFvJJCFNXG9smAW1t1p"
        "pmAWNl5m3rZzPB5gbZ+5PcBa/5Eb2ltnKrE7vI7kAsW9RGp/8TVguTtznLC8QRPtUL6hXfjwxQtE"
        "8DAfwd0iv7C8Y8Etod4P5IDNbvqTWNju1sCAHiZmdGzbPtTvCWE9TgyZENlDvbsub7D1bXBLP0w1"
        "adiEPEwecc8iBLU/WRPbbgnTEtwjNEHtT6aLHunw87tTIcHtb+LQ18WIO92UVCPYjPyXprmz6ZFr"
        "3InOzDVt4fi2ZdHCmW3v4OCg1jigITidLTmlEUi2PmWN4LCJNgFfDalwQ4Zaz0U+5lNjEP/Dtpn/"
        "0mGAagXxO0FRq0t+CHSqaF6Cl1ZnshOQtCp9myCjir5L4NDigTrBQP1OcgjwadbSODjuLFtDcNxZ"
        "gMTEcWcxHILjLl3XzVzzXRx39js47Wz5RUxLLdzm4rTTVJK+CNpZXfJL0E6DEA4z1bQgi0PQzlJT"
        "DkE7KxjI0E5fxGkE7TRwwH97uT2cuQnaWbHKRtDOgn4Y2mn9u7EI2qnoToJ2mpTyMTM+q/MvBO2s"
        "Ldz2afe7fHx6ihjBDx9CoqU9PkRzPeVghvADOSc1xAnASTzIDCI5iC/SgtM1fIjlpsVcaogwegMf"
        "Y+4IwsQYI4raIMa4AaGJ17Gi6SkxxomO45j7iII0iDEkCtBgxpAA9vgYu0Wbv/AY/yaJK3AF+Bjh"
        "BgE+xAo3CfAxRt+B2yBeh79yJ830cE5Fdw3cZZ+UOj/jo5c6r35M6jOs9B/pKOxY+nDewXYsFucS"
        "bDdBOD+gOwruzsUtdUdY4luHORbztj7uJNttjbxIotsynsW4dRRoJLstT2iSwE5KGuaUtiaOm0Sz"
        "Cm8jeawvZ7MQTvoi5OhVoTSSt9ZfTkjImsk1kqyWYLY4nFphiMHhVJflUZh1ofP32Uet+zqHUzt0"
        "7hxOrZQiR1N9Le7OwwE+g3A01aXZ3CRNbcHO0tS2By5JU11Of42kadKbLqepPuMkYWrF8y4JUxXK"
        "ImGqQhKlthfCotS2oCaJUut0R5LU2hpckqTW/6GTJLUcoUmS1MpUIiCt4oun73PYYYa7auj0MAJR"
        "txzmmwiE62EawuRymGg3mRzG/eCH/uCzIQQvc3TcV/wX6OU4XSC+1/eD4b58Pf6uROfvp0HOoBwn"
        "zHb8f3I/i38/ArmOcpyN+ZL6/WC7JmWy2HchT1Nmi80FeZ5ynDMgR1SO0xrkl8r30wRyU4/cyIf5"
        "SZaYZ/O+SrWt8w7qR+uTd2DaMXhXpFp3zbPA322801Htvryn0fe8D+9eNJGm7QefYglL+8GRqHiv"
        "B+9h+T8vLkPFqz/4CXvm9eAcVHxePIKleJ0HN6BiWQ/st7c9H4Bv6VbngfKW3SEPaFdxmw8819u+"
        "9wHiKn7gtr7r7/Cw1iSNKPkQ0PqhOB3SPsFate7e+8S07kR2gdrDw9qet/Ow1vfsnhlcSLv9zYAP"
        "Eh85D7A2sTzAWm/bL63SQfHLpN7E8wHWKu73Adb6V7ztAdaWp9UfYG2/fB9gbVlt7QHWlk53H2Bt"
        "YnmAtWWJ9QdY2wt7wbUhdyC4DlNSBNpij+Tfbgi0A/l370S4HcoXQu5QPSF4h4/uLmo2/uKho804"
        "IQY64QzlYGhLpO/YBn0onxOieag/WDhL+PgTY3rcSwWievzzAwJ7qG8XYnusHxDeQ/3F9l/ifJ4O"
        "QT5sOPJhZ6ahfmNHp2E+SsNOUMPnB4HPtPIJma+hFBPnvEV7LBzutuRZONG1ZMmeOMdV46aErVxz"
        "N05sq6WAU9oafjYczXpC/nWCx9ZV8RAUtp4mjUBv0r8x5m2ehzBy0SLIqpq+CZxaTMImGJr0DI3B"
        "qaKwbHUiOn0SiNQUmL4ILproEjC0UJBDEFC/kzQCexpSd4j5rQY6rIPDLo3h6KnG398ZmeaLah1l"
        "ktlx1tnPELNTa7d5cdjpq54Th531ULkE7CyYZBGw0xiEbxCws3Y4DOxU1DoBO32mNgnaWQhAI2in"
        "IoJ1+pX2IlhnDYIawTqLTGFYZzlHBOpUczaBOo3VaJdAnbXs7ATqNM7KPyX732vS4H7/HBNQ9uCE"
        "rFZKwL5a6Rd5mYhy+bEZwN12/2QMebd+Kkqt9MPfLqKMkptr6YqS/gDpCrZYgRtuQTByLT1fUC8I"
        "kEbJgIA0qhUEPGtUKQiQ7mDdDdxwUMCzVLqtuu7/aWeVNhjZQXZ0LfX7vQhgTLJGkAQCPGtUKAJ4"
        "wf755B+l9aYcEHJ1TdgXxFkrwtchuFoRCYyoVlBxQhjVm/k2xE591DkhYNqSakCU1IVHlKHhX//v"
        "3g/GQ7t+YxC08gsY+PTyDdLOmkiAiLMiCBPjWpq20HZ4vXSMYHq9HyYRfd6oznv4eZd0jFB6fZSk"
        "FlzfL8giM4eBAUiX+X70y5/LdU7uB5pFl/cpEHV0LefuBIzo8qCNR3T1XBB0bHCBoKO3vjHo6Ez7"
        "Ngg6tiLcGHQsm2Bi0LF1ycGgY90QNkYdu35g1NH7EZA61ivjYNSxbqcbo45eHxWRia6/C6NO+j4l"
        "/L7+TFnC7+tv1Er4fWc7GHWsGMTFqJNldPxcXMeEzgRBdeR3tt6s45BPAqhSvUYCrDqE/iT8qiOf"
        "szlU+dbGTehWNx3pCexK9UnZV4cipygsf/3ejIz1zd8MlPXN74ybpbyPDKOl3J9roSYX7H1uWL4y"
        "5tYh8TdDcN0BYWVELvswnBTQlVyiuE3w16MdQ/TZe0bz2uo2jHeLhN4w063vgsAgV4ksmN4aWB5E"
        "+GSSIKc2/ZUBw1mfxX3JJ33J48IYtl4egrPXDrkvDlzT4JC1M/uGk1VjA/KtPl/TN85Qi0HYODjt"
        "eQhaqsaPIjoPv3PT57kdh6Fu2qyDEzDXZHYQrHc7/3lk5P+EBkPNIklhpllnA5xpKglyVxOJ6xhn"
        "qtgLRppJLow0CyTFkWZ9FTaMNA2UPRNHmp5LS8ORppohONPsOH/hTDPNwZlmmo4zzc7zD8401XQc"
        "aSr5Lo40+5mDI80+D4E0qx06caRZyYuFI80aMhBM03ewGs40/Sv0BGlh5OvuCdbC6vs3O34IVd9O"
        "4BbGRa9szhaq5k4YFzclyDAXRx+PhHRhEf6T7RmGqnkz3oWykS6bQ1nUpKu6yRR8cVuEdHkcyqIm"
        "L4Vs3oyAoaylx7Wh7NsZCONOAen0LgooDmJMCisRPzZBWiVb6fI2kvWoE3rxbFEN6+pzzxKPeuJ4"
        "R8lEneLKKEGYNssb3qVfev76+9L07PX3DXxSws3Oi6UkmsVTlhSz+N1Vo8vqpknNK+tvf2tIWQW4"
        "XpPJysytGkd5ETz3k4VNYd1nWzVtLMQXQIxem2+n/S4an5+h/ro2bAHlXttrbOg56KlRkZ7oi/vZ"
        "Ah/w61I94pN6omTnnvXsyGrE9xIKOo3cp4SCBd6uEgrpqNu919VKKNhB8S6poBGeW2oqWGXzVVPB"
        "zuxqKFiVt1ZDwa6tmWCnjLNmgp6gRZ1BnWuDIhXuN9ur1UzIQ46v/xp2zQSr3X5rJljJtVUzQU9Z"
        "NzB/0G+xaiaoQTq+7585/ilqn9Ybd7zyvzGEGcMrOvlvjM6M4YUA/xtjUGN87vuYzBjejvC/MRZ1"
        "H9d9ls2M4R26/hvjMGN4/uXfGJcZwwsO/B8b+5hB9nIfplGWupxNnf8ZhDJVLx7hfwahbPU4i4//"
        "GYQy1tP9O5ncIP6dUOa6t4+RzX1i19YaZ7DTH4SxWJnNfSfCWGz//BcrjMWKl4n0P4MwFvvPdbh2"
        "IozFijihDP8zCGmxg3Q3GjHcSRejq1uf570UelHBuTOxle8kPYg1mRPSbVij9UH6Cn05Z5IOwvJM"
        "J+kVrEmbsK5AY1tXZ/mvysEy34Q06HWxF3i8USuHsEhXJY1xfcyPZreuU4PHPMBv0pS2mOXLovl/"
        "ld0rOVLw+Oc3gwmM1Cbk9YwqyKtvqNG4tV2UQzJW46P9P6eUwu5PvHsp9Gqq55C1nQR2mm7F3xsJ"
        "WYvAZiGrz3hJxurK7OskY3W1Kp1lrFbkboNlrCr3ZSGra+CAIb1WNhqyFrFMz5uTxnEFZfWrBMoN"
        "KA9LWX3OtVjKasx1wMrShv7NtzZL2Z/f9Ha2C8pqRHmbLGX1e97FUlb3mvz54Z/HLKOTF8TclxBp"
        "D8HlOB2b9tZF8iE+l8N82FZKOc7AtlPKrzUXRPMytNr/T196HP89/2X960C0PW9wtl2PI5hfqF/1"
        "xtxEOZC/FG+THwicqtcfbWI+pX5HHXMxZfh08NVYw26fP8ET1rDdZGDXH72EtbvuqQ5wF8xblaHu"
        "E1wi1Hki68GXWcXj/uDBNBLcn453SDzXi69SsW8XExP7U+yFif3/yMZemL9YP9inauPB62hR7NFf"
        "XI2GIPvLoIbZ2A12YuT/So1Z2fWnpQ0ys/YF+/wT/O314ikswl5e3IOqn1yC/XR/8QMWEXRf4J9E"
        "KQHEt33fF8rrje8ntNtLe+K5/j/BrXU/Fl1eIG5h/PcB4hZrLw8QV3HfDxBXsb/zsMBffllQ2DOf"
        "B4hbnsULxDVqejytFyxOe71AXINvvvsC8SRVAIC4JUE8QVyf+5wXiKs6mBNjhna//QLxJCMBoLg9"
        "d3uheL7VKpCtuUGZAMUt26G/YNxyGF4obp+7vVDc8q6wzfswOt/3AoLq/RliR+UfGIITl4VfENBj"
        "/YCYHur9mcdG9cO3+YPqd18Q3OO4b5DvceS+YIgPsyE6OFVncj5c0MeJFR1jfTjAAjd6mGQLl/hM"
        "/oQLffYz4oa4wQNapkq8S/9oAK9/i+sAogHWAafy0QBRXCNqifJt0BWwlujrLaFjES5Alz23EeBP"
        "Mjdi2ltOOkH4pC5+jHVbjDWC5VbofxMA1+CkOwhqF8f0X6aSbyyGz6rqDJNNtBkQa0zIdxj6WiTJ"
        "YJBr0USD4axlr1wGrqrqFFH1Dr/GYFRDefz1oeSmsdtkgKkRKpOipN6h76Aktw0vdTvhYdKoIYZg"
        "XA06ZqAuOcB9jP9UvmdmvLrA6Mw011bAm4CgJccMAoL6TL7zP8Ub7wQErTYgNV/ViAg/OL6lJiHN"
        "P7ttkqsuRUFTNYaCVgmwMRS0bI/JUNBycCZDQVUFOwKneK7NUFDje4LYudw2ghWU5LaxWmcoqFFP"
        "i6Kg5WpRFNRwsHYDCv6uiZ/Wqw9iJ5kx2ogCqvExPh8VgxrD36mY3BhRMCAxhv81NzPGkOhQDx8j"
        "WC5dZoxo5fwxg8wg3oKy1HHDvWLiTuItY2KQHe4cE4PcEOzMnZyI88QgwfbM5gYJ474JY7vhESE8"
        "iDQ/7E0Yi5W1wpBFYpAg7pGx2CikVRiL/bdum5F/Ib7OYN1NnlMipbCdSTqWcheiEvZJuhBra95J"
        "v2FbEod0FrotsTfpITTnX1i3YIUFWFdgOxSd5X+xWK5t557Nkt5K8i8W76YcLNOL51zAR5ksvXW3"
        "aQ8W2fqbQfRMaUJRLpPUNrQWC2TdzYjDNwql7M6iN6mcUvBW/5wsY5PqHDljdYejkYi1A1F2wm4b"
        "Hews3Q7sScImXfhywloqUiMJq1lTjQSsLaVpwlqDhMsS1tq+TZawtnlyWcKqstGEtUYH9KxZlSxf"
        "rZeesHy1jazD8tXStSbLV0udovmq2x1nsoDV5gr0LFf3SoTmq37MYIe6NqBo2fVfYRUf3bEpbTkM"
        "Rt9qGDkXgnE5jr+ynfw4B2J1OY5/brn5rzUhklfjBH+vS4/TDgb6eqCJcb8cKIgO4C062Ijv/B1N"
        "zEnUAy3MZ9QDdcyJ1O8I9Cn1QB1zMbVhgzP6MqsuzsXnBlodc0flODIx9/SYTim0Yc8P3IypP1p/"
        "8GU/seE9qN2CicEdf1/c+oOz+hHLPQ8eysT9wS3pbX/zwRepuJ8HB/QjHt958DoqRtcUQVbTk38x"
        "9YtPUXG7L47Ecrn2i/cw9XlxGfbY7cVP2HO3F+eg6jjK7//ic2OmttoL+lW87wvwVT2fKG/9ap7Q"
        "nhuLYKY29suC5Cc0fHzjAeI/4u4fuXZMLA8MV20Y7weIAwewwF9+YbiK+3hguH2pl5WDioM59Qep"
        "5xwvDDf1fIG4qoPkog6qn5YAlsw1XiBu73y/QFzVwd76BtXrBeL63G29QNy66fQXimsmWsBCzNZW"
        "kKYJ2trbBF3VX3+huH6xMCDxtzjMsekCgTzQu12wPJZH+nOxDaRQvxaE9FiPzczD5+8CgT16//Jh"
        "h6lhks8eEN7DHK0DbgjFSV7gRD18A/6/pwk8wBUM9eEjBEmRAx5gCgb8+A7AiXs4QJykgw4wMfKH"
        "htjBjZxogDMGxv8wy2eCJ7XhAKgXCHNsxsQcQZjpJODxbfgVPiHcgUW7dMIHWBoMA36rvLEI2msx"
        "gbMJxKtoL4LrdnsMzC3khyG4RSZ1Att6RN8ZVGvGQt8Mn1UVZ+lkN8iRWH8LDXv5j2owzLXnGgxo"
        "9bkGA1dLxDoMUfWnljAYtTSizrDTyhgLA0xNjwoiaXLTuEEueG4a61A81MZIYxAQtHCUQ0DQQko2"
        "AcGky2IMQeu2ycxzVbQHAUEr03AICFqIDANBfeU+OW8qCkrRRhS0zi2LoaCFYEyGghZ+QVHQ7vAy"
        "FNS3cRgIWvrGYSCoAQyTgaCKVmcgqO+CYqAl9lAMTFrZJAzUOKK9GQZaDBGDQP1YvvOR3C6CuAPt"
        "/JMngPgcrJUSTQlraVDrYwDSoM7VhKQ+HoH7XUE+dy2d/inkAaRnBYv9WrpXdBoHaMM6HLU2iPlu"
        "iD2tGYEUuGeJjuEA7YziNgDtiHZvgee9EWIB7YmKKyFmFS3dS62MLzp7q7W3RU1pau2JuiDU0igw"
        "AzArkXCzFjCN3TEmW39PkMSal7E6hl9d9o+DMVcXundioLWFccfwavcjGFN1DT0uBlJbMWLwtJIT"
        "EySmLoxuAzGpgtVANpqgg0DUFV64tI4EwW7BDAXfAXmnz9BAxlkKzwDBZuU7QJhpmkafIMG0A8tF"
        "saXFMMJ9xUAw5gYJpc/cN4glTcERkEU6jw8y2aPrQRJZjYeGkUivxzika9PTMA7p6NIxDukydmEY"
        "0le5G8YhWzUskEO6pAnL8gSCHm72RYKwGk8kaAfkkPU2EZBDuvrbC+SQvtbTQRBZqQQBQaTPcBZI"
        "Iiv8gM6lfgS3DZBEWpDioCTSFIt2QBJZhs0FSaRrfb+SjD5C3SPkZGAqI1l3y0hVyvvMwFUH0d+M"
        "ZI/B/AuV+0uVDb/5nXGvDrNOMVjKgyDN7/9Sj9pdVBVRYP1KEVpHl4+UqG9R7m3CP5/jtn79ktK3"
        "1u8UxqU+qKSBml9Q4FxQ87t3puQu9UdSkJf6YNmOmt/eOebL9x+VdPDkGu66CdRbVPLE+a6Bsavj"
        "UFfNwEGuki44ve1nDo5s1dyDc9rikgcOZ23oQfBYJZtgsGoOwV37nUPAViMIGgFY01wCqyoKs7se"
        "Hik1hb0aQU174ZNApT7TvQQfLaSEYKKGbOxOgNAiShZBP30PQUfS1CBWlPXraSwQduOcs5BjYh5r"
        "wb6Cc041DOhU0xcOOvudiYNONafhoLPQXQJ0WhY/iCH5MtH5BsE6FRWHJ76oE6wzzSFgZ4+0CNjp"
        "y1vMxFFFfROwM9EhYKeiewjYWcTEImCnonsI2lnTk0PQzkJHDkE7+07MBE/D6Ee6qxgG8K50czHu"
        "j5DuMoYR23dl2Atl82Tki2Up/MJn6yvjHxnJfArZGjujYNgdYbUUhKGu5QclYXDryHEY6lY+/Yvb"
        "R+Rr7LhrxEnBGOtSNIayLz82jnX5bDBuBJAiMgqODvbJpbAWCVy0tEqXTwwjWRdJaRm9laDLnJTG"
        "Emxc/5LpiWdUa8u5tvVW09FqCJ4aidYGsNUc1GvXreFn91ADTw+6a8ZpDK5IDTY9EgNYZmXoEIDp"
        "xe0A1LKLL4AqK/Z2AD5ZWUIESnrxagCKrJzfAvijF7cDQMfaUkwANXoSPTbAF+s0cAGo6HFsWwBK"
        "9Cj2APjQ1/w1gBlWPXPUoNDj16DZi3dtEN3evWu/AYDCGrbNGhT5vHa59/CNmhR2lDtqVug7u8Ak"
        "SA+tZgdoURwcel8uDHcQ9+LdAVpYfCxCC71nmQAtNOB5LIAW+urCZArv4i0ALfSehwC0sBPpBtDC"
        "Cs0dgBZaCW9NgBZ6Vt+R2Ube8EDcL+jWQ2p/O5WkoaqeybS/nUvSOv/eGXX728gkjbb1lmztb1+T"
        "vFeA+yyTGmO673RR78Obrbe/TVDSSMLrvtNDjCHi7Ri2vy1S0ornn3sffzumpCXCxX0hjbLUO/xB"
        "KFO9/j+mU6/EfattUGNs11TbpAbxvE5zOrG8DMJYq9+ZpDl9WrJB9vZfLGOv3Y0NbE4Xl2yQKe7j"
        "CGOv3c2Wbk6Pl2wQt5ptc1q+ZC92+mNQBvt9m/Q1lljZSQejK+G9Sa+ia8d+SVei6+k9SP+hQt/8"
        "V32rS0hPoaveSXoHa4nGugQtrn5pP6DrsM2yX4XfYoGvq7nbWcxrJfjvsnC3GvKLJboqz2YxrsrB"
        "olvDlWlc/6+wf+uyjP5R9sZy+UfonkfmMP5Rugv1nMAa/30Gi101vS0sbPWvGbi/WKjpg/uShNW6"
        "/vS8XcOhJztZ18X6aSRhVUhPyy3nm52L617BYRGrC9pxScRaUPdmEauL10szVuORJz2pVuWdLGOt"
        "GnxnGavPKcIy1pr70VNl3UXg58f6nIEvKU1IbsDn0oZ6/2jM/iiDNySlDXUJkFfbkFtZK8esfs8A"
        "7TWCrg+9P49Zhkf64wg7zvJn+J0dZy6MyeU4/jJ78uMsiNh1FHWDAF5+Lx/Lhx3n+IuES4/jLw//"
        "0r4cSED41wM1zBc8RU57rqEcKJhT00YdzOfa5Ae6mB+pBzqYWynDvKdgXqYYqLUGOp1qIDmgD6oG"
        "Gv7cTVjL/jeXW5iHKh9tTcxhVQN9G/RftR21B3em8a4+6wUSr/HiuDT6/Lx4KxXP8+CiTCwPfslu"
        "ez44I31hazx4IAvRvg9ux4revbgajdrwHXBrmNqfqDUB1fPFk6j6yXtYaQN5cRnWeVNe/ISq/fV1"
        "g+ysRUc2kKG1YNOkXUx95YX9Vu5hvABffzvYtMFMrfnbLwKaWn/iuf4//QPD4rEtjLc/QFzDedcL"
        "xFX8yQPENSzf30mcmHj2B4hbQsDLisLKiO8HiFu8+svaQWO8gw2XD1H7PYRriqt6PVFc1bu/UNya"
        "gY4XjFs403rBuAUirReMW3jUE8btnT9hPOsvWmNcNz/95xbM1nqwIY3ZWg9m/ZittXteMG7/kvGC"
        "cf2H+kedfx47DGL3F+CC6oNv3lF98E8bsH5iu/uhHtsxCvscXIzrYdC7j8gD6iWYKF/0988F9//D"
        "AUDEh6XJF7gBFN5AAB3YAi86ZQ8HCAJRYBu8G9zgiQcAN3bCJIq+MO6HWREo+qMBzgXpHwzQg2M+"
        "afAAX8d8QPgIrWNuIMwRQQ8Ywv+CMM5A6wH6CJBUFERY9FTUeidYb6vaQQDeVuGbwLrenj/B3/nb"
        "8+lxUtFpDLU1A2AKg2qNoWkUoK2Ee2eorKrgDnt+h0GwTmoWMj4Kuqry51pt5XdI0dXigS6DVA2S"
        "CU4fctMI5p+pZfTvXgaY+lMcJS3EiUJjVjUy5qFl9wgBQStESDBQlzv+vlNPRf5CY6Sa7zBzXFvK"
        "NQKBeneNmc5aoUIhEKgv3J843kwUxnR/qaoH/9+Wq+5kEKgxAnIZBJqqMwjU2J3gGGbmqu8wCMwK"
        "J8YM1Hc4N8NAi9XZDAMtfmUyEPyJI2nfZCCovzUpCOpz+dEAkttGuwwDLR4sQODv2v75+WUUa4KP"
        "0Xa004uP8e3o1I4Yo0dzSGKMEeCUeB0rmmDiYwSe9DBj3DCcBB/jzDCUBB9k73BySryRG+4gEHci"
        "4aEf8U5aiHHmxUZQZ8YITwKZQXaEfHgQiY4AGHuVYG+3MQYrO8ivYQy2fy2cM+N3cv2ZmTAGK+uG"
        "M2p8EPG/jlAGG5wFJq9El85zkh5GNx/kkG7FTqkP6UvscHySDkSFfnroqm/Vd1m7fqv+TtwphadP"
        "0ivoxsQerCvQBV4QJNJqpX8M3KS+28uC3gpBLJbuqtyLZbq9oMGC3H5zsPS2PZLGIls3L77Fctp6"
        "H7Bs1u0I/9VKbUH7LpbCeY6Y1CYUJItLDaBgxzB5TM232YeErOXbNBKytofATth1x4KGrJ23s3Nz"
        "O+Y/JGRty+OSkNW8KT+b5FZC+dZkIZt1Vcghq8pFz6xVuYWlrCqDiXhpPn7zvJyy1lxgsZTVrxLM"
        "1ksL+kd2emKs2wj+KUqrbSiI5pHahq4fOS61DZ1BT3Y18WrSmLXvOVnMJn0vHcpWAdIdm9iWw3zY"
        "9kk1jpwOEbkcZ2OAfhxn0eP4Jxibfs8b21OpO19AbC+HCdbMHz1Qmxj5y4G+iTmCeiDQL9SP1jA3"
        "Ub/shnmNeiDMh7x+fdqqR5ykww00pWEOpxzIX80Ibdhrbswd1f0iBuad6kfbmLMqB2ob8121Hb34"
        "sp/g8ICIgon9KVyHxAHTByY+Lw7KxOPBK+W3vbEXNuTB/2gfjiYPXsd6kpwXV2NdUNaLfzH1eHEq"
        "1n6kvXgS++394j5UHewhTVA9XzxF8duYpc2xX3yCJpO1J0dguXvthf6qfkO+qnt74bx1CLovcFe1"
        "rBeiq50HaVm5+Cc4PKgjIZjYjyzvmNg3lQGJxd+am6D4geKmPQ8U10cOs3QQsR/zcCFxsMdXUVxT"
        "k4a8UNzU+4Xipn6iuKlfIK7i9jTx11d+n6b71lLmheHWk+cF4So+TwjXRLS40CGi7uMF4fbbLwS3"
        "xL/2QnD72O2F4Kr+LkTwMMUEnIvHjUkuxPFQ3waE8kh/9oVoHuoPtlsU3v/BoB42P5nY7Dzua4FN"
        "0ON2KAuje5jidcEDgDhH7GKMDwcIJjEdfgfBYnbAA0xwyh5/BYz3sR48KQgTpT7wwCDKLsG4H6mD"
        "8wpBrVBmB48QogGC6EmBn2CB5wlhds0Gt2biP6IQnsAqyy4C/xZ20gnma0WA0QnQW0fGQ9DdRJ1A"
        "unV9GQTHNYzmLALeWuh2TILYekIvh8G0tuoI0JrbRBSalxvFGZOhsKoCox35c7XD8FZVwdHmKn5r"
        "MWjV0qeDwalF1VwGoxpR04Vhp4WZDAaYlk01GUxqYEobDBuzpjsxEPXf1RdBQYtG2QQFLQVmERTU"
        "AgpTCApaq8ZGUNCKaxAQ1B/qk4Cg1cLYBAStoAIzbbW8A2EgqOUxtzAQzPrfxBD8iQ1gCKg/tCgC"
        "aleVvhkC6gs8kyGg9Q26DAH1ubowCNTAlWD7OjWMfwhsDAI1BKQxBNQIonMYAmrMyGQAaF9rMADU"
        "kLygovDPVWnnnKDULiANQtY6IG0+fAcibQEYAWlQMw941BkcxtXS3YPFfimVFkR/1MqgAoy1/co7"
        "1EQpNLX2rIigwO9+UX0l4HlbBFRAu6NtW0AbbH4uSBslQNZamdFcs9YGrUwaYFf9m9Gavdb2KK66"
        "lsqJanPXjxtUIRfErEYU9QdYsywMyTqHDR4xur5HGSvB9WFnsuj6KMExul4OBlcr0AgSVd9PlIQS"
        "XH8nCE9d5QQhSV8kiI7IWij4NsjGollND3/hNpCCuiDsB0SfdSM9IO9UELzW6DvLmgskm+ZrTJBm"
        "P0UqosOP6EN3uQ0El5bBOCCsNG9kXpBQahhrgVyylrobg5EGLQd1h6Lr+8JYZN1MMBRp+gdIImul"
        "2jAS6fV+ws8OH3ZsjEQ6pf82RiJdN5wNksjWNAKSyOLgD0giFZwLkkgFa4Ik0tXcd0ESWQ7KBElk"
        "6REoifQZghDl6EPLCUpdRl+6Bw3XJPrSPUjekxb+QhilFD1DA1Fk3WkviKJiE+Pn+jKYdafL1TKE"
        "9Y6MVHUA9MzIVcr7zUj2lgywUPXpGebqBibpMrbsW/LNDILlr++VMrHUr5Uisg4Pz4lZ//5MAVrq"
        "z055Wr/+nuL18fO1BetXCt9SX8wK6/4S+Zq3bHTR8klj3ZXkpOAufz9MLQb130i5Xr6/eVLM199/"
        "4NTXCFsc9BYXi8Ndg2H3wIluAbQ4xVUyNs7u/NZ2+gb8Bd1J3/NoOJqt5YoQPNYz+m8TEFZRY8hr"
        "v3QJ3KpoDIKxKlpCgFVFsxM0tdvbBEJVdCbBTQ2LOAQrrXPEJgBphVgXQUUVySFQqI/UL8E/fXlh"
        "scjsnxGEX7gaC0Q9OOs0/rQfHHYWJHxw2KnGN/CZaiYOO/uZicPO4q1x1qnkXpx11u6iEazTk/g+"
        "CdapaE2CdSYaBOtUtJn5pD3TIlinom8QrNNXfhjW6S/NRrDOYjMY2Gn0Qx8E7Kzk6iZgZ790Cdjp"
        "Mw0Gdvr22iRgp+Da6bQujH8OwFrIgmLfvZB9UY3wVPZdP6JwFr+WkS98MP/4fheymZ8sh0GnfgDj"
        "LWRRHMlX6Vo+6wuD3MdNYRjqTr7UDu9znxSJcYX8fOcybnOxUzDGupOyMezocFM6hh0EeksBGelW"
        "2EIt1wUxuVKYS1iJRqr7lJPCMuxvsfKNz/jv0GpkWuG9U3MyD0vu3rVBH6zhXpufvvy+9rs1/qwx"
        "4amZp2fdvdWg+7l2S6vpZgG7AiBNA1pPBzimFwen/+Je3DpALCs2eAFMWYHBBrDJei0cAEh6sQyA"
        "QnpeOQbAHivsjwDHSu4NgDJWEvAAaNGRg6oZ7hccHYGIWt1dADnUnBcww9IowA7gwo5gAVzYzBWY"
        "QFnrsZoW1pWu17SwQn6tpoX1Trs1LbRnQANoYcGtACwspHUAsNCLi8OF/5ToR2ChF68NwELPnTsC"
        "i6J44HIvlgXAwl5dB2ChZ7RyAFj8XLwvwAotTxe0F3E/4F4NYIWedCOo0Bc3O4AKDdrwlgPyt0tJ"
        "Xnl5eGMIM8bw3rP8bWKStgrwthrkb1OTNGbXm9DL3x4neRN491kW9T48dsnfDihpNOF038chxhD3"
        "DEL+9kdJxxD3Pv62S0mLrx9/EMZSxS2PJE4zlfROuvtpWqfeyXLfa2OMVbzAAnEar6RjHNfg2+IG"
        "8d8rY67/gOg/DmOvvX3+x2EMto/tDiKMwfa93ccRxmD7uq6ZCGOwvftfRyiDdfemxWkAk0egT9Lb"
        "WM4o62Ish7aTfkWXj+uQzsRasW/Sg6jQN5hV3+oW0lf8CNdgHYSuJz/WK2hk7+msK9B12Bws/1UZ"
        "eI7SeOT2wZJeo3knS3cNNG6HZbqFKA8W5KY8LL1/lF0Gi+wf5Zw0p3+Uu3cWzqq8hyWy3m27LIb1"
        "3S4WvbqVMFjcWk7CIBmrS1XfdUopnJdlrO49+BgZpdDtJpoyVncwfP6s+hcny1h9OYNErH0NFrG2"
        "VKQRq8tX///RStPpMmjE/ij7mSxiVRn8Zmk9/ePnzfqG/NlEW7WybZaxerdLWMbqVwnWGKUN9XFY"
        "xP4IVzBPq01oBlivTcjti5szVrdg/M0PKU1IxP93/nnMOkQSm9eWoZIDInAdMX0hINeRzwLxuR4H"
        "w3UdSbohetefC5swV5G1ENmrm7kXBH0d5ysY9+s72pgbeIo89rxCOZDPhjbogQIKT3ogf5XXFj1Q"
        "4OdZo25tXMzBVAO5lcs9f1MN5Fam8PxPNZBbQctzR+VAAnqn8tH8mavQli1yMd9V/0UePJlFCvcH"
        "96VBr/vBZ6nWv+sBiZd/XjEx8bgPLknF/p9/Y88MLiWCL/XgcyxMe704Go0xmevFu1gFgvniUnRL"
        "7TsvfkTVc744D9sHfPIYqr7nxU3ojuD35BtUHaysIEtr0WkPZmvjrhf0626v7Bfe62+P/QJ5q60x"
        "X8hudv5Ccyuz+bIa0RhefwUukHjv9QBxFfsbTgMSr3kfIK7i8bKuyH95Y8/s+/+DfarvheIa4B3s"
        "8n6I+h/F5wvFrWzieaG47r0FNOuYuj1R3O58vFDcAqbkheKqfmF41ja1Zri+M59lDbI0v/VzzXDr"
        "FPuCcItmuy8ItyId8oJw/YsEk2HM0KJF+H/FYQS7v8EoqL5jII/k0jGWx90FsFPTUO+fui748TsW"
        "bxMnAmyI62FV8IZtCoWR5Vcwuseh6RjfI/2HnrKGN9DAk4DwFfo7yA21QenBpu6EBwBPYGM9OG0P"
        "i9tjzA/TIQJHi1phDygiqBX20TD4R/qI4KgV9s8/MxHYCid6cBv+kYL1sq/XSA5/fS+paPixBj0V"
        "ib8ROlJROwzdVeS/yZXfHjg5/10K3Pe9JxVdcDL+O6mhM5TWoBnft7TUJGR9lwGyVdIThsJWjG4z"
        "6NXAnEbxVlXBqebKVVsYtP5EbzA41cJ/HEM1kGYdBpw/qmCrRVLD6G1fhpEWf3UZMGqOiz8rkNww"
        "WmMQqBXzAt+TioZPs56K5HYCgSr6FoFAW1IQBNQf6gwBbcm2CALqG/ePIG4mEkE3k3+p1qWmpxp0"
        "IQwBNd5iDIaAqmrU5DPLAYkJqC9jMQBUUd8MAO0GqSmlvvfJIFCrDg6GgBr7EYQ2t/ynbmMIaNZ0"
        "GAImmTsxADWFx18N/mk4kB5Z9mhDAB8j+JKdGaPtKCuHGEOi+SMxRo/2fIn3sXvAVnyMwE8dYgwJ"
        "InYvNUawQ/gxg3xxVg7+Rm4QN0CZ6g1Sezr1ODekOPFiwx1j5uOEx3+MlUTEx8foI4zwxgdZoT/A"
        "x/BJJIy1dunh3jI+SDvh9Jl4GgnjwvFBxggn18T/ZnbS1eiWw9dJ/2LHy5t0Knaa30hPYm0JFuk+"
        "rD/BJn2GNSoYpKPQPZk9SO9g3ecm6RJsS0JYP5A1AsjhbwX+hSW+/WZjMa/Ku1i2655IF5boqjyL"
        "xbjuqHw0vG2nY7PE1o0BltK65REc2X210l+hSWlB/Vs0hW2varDo1X9KfMBXKD+ZJGQ1PX8cErJ6"
        "lHkGCVndPpBDQtYiBISErAp9w1u10I+R2sDLYafg1uBOSMjqrkcQ9fuVysXPsLUq/9wsZG39PljI"
        "6m8GU/lRP2ec+Fgop9BzZeuBMVnI2hbMZCGrb2jTmLWNKZay1jFisJTVn9zCUtZaQjSWstocYtOz"
        "Wk2Za9hUtmx60AYE3WqcMKSCHKYLRORynHYgQD+Os+hxBraZUn4uEYjmdZsPbFOlHmdhrC/blgS1"
        "LHiDjoOoyYECZ9T/H73rNvh3BLqNcqC2MS9SDhTkX9N2PSe49VJm0bWBuZw6PRDchCnz8eRgHqke"
        "qGEO6vXRaMueQcWWB8ueD97MWkf0Bxf2Iw7WOR0Tj/vgrVTsLwUmJvb31BZ42+3BGeUv7GCfClxT"
        "BK07+ouvUfXdLw6mUAuo7i+uRBOpguBozMyWf3DdMDtb/gF7wwwtWNE3zNLWkRefoBlkwYYdZms7"
        "rooFqdcL8u3O7wvnLe1uv8DdbO2+EF3tfLxgXBtcBAUKIHEPSyoi4rEeMK5iWQ8YN3F/wLiJ7wPG"
        "VTz3A8b1U4H77774nheMa3+S/YRxTWeSp8WBqvt9wbip5wvGrS/LfsG4vbXzgnFTP83y9bm//oJx"
        "y167Lxi39hvygnFV3/mCcVUH4YCgrT1N0e2DPVHcmiBdiOJheokfjCuovn1YIE7YzsTfPByg/rur"
        "Q0SP9dhBanj/BztPjfTDPy46qP74e3kX1jdw/z/ML1oDY3zc4QQ8cg0HuIKRPn6Ei8E+fInoXk/c"
        "dWViyCfNoMF2GPh51A7D6FnUEGWcg9E/GmALGEMT9k45G/MB4SOsi/mBMMMG3KEJ/wmTcQZWT3YT"
        "HsBqZ3QC+1mvw5D12utwCwF4Fa1BUD1r+hii3NJ6hOC3Rii1S0Bb42iC9JIvU0kbFJ6t4ctlmKyq"
        "IJK75yo0tPE/HVsWg1xVbQazKopriCeq0RmgaliOMBC1gqyDIaeqjjC4zGOVJDeMYPdUcsP4pDM4"
        "tI5Jg2BgURggFYVJionmAzeh//+iLwhDnrmImthav5tGIFDfw14EAq2YAoNAO0cfDAKzhjQxAjU9"
        "4hsMAi2pYjAIVJUcBoFW6pOadWZ9cWIGqso3jLbzOxybgaC9DQaCGjEzqemjRctQENTfCqaquWkE"
        "xfAlN40g4UZS02jR1tnPVVnY9QpSkADpaMG+bi0NKjQORCpBvSVA2oOSebW03yBGpJYGda1OLZVo"
        "sQ8ow+zGWisnAmitbeFZHPC7EsEUeN6wCHetHWH6N6Ad0eYtoJ1RlY1auyRawNfaKKoSsKvev2jT"
        "ttZG5261cvYo/K/WBn96Qaxqf9FeLfBPCKJe/0itV+LCQGwJGgejr677G4hcXen2g3FWr4+iHqL7"
        "ieaewfXTd1QnuF6+MTF46lLnayAxLX5fQEyqYKFs1AyKsN5cILhfBymogjDv2xf0ry2QdyqQCUIu"
        "rwrRog/dxzdBnGkTlTB6LBAEp4MSfenedwd5ZW9pg5CynYMOksk2UEAc/UwpTzsYjrS9iEwMR1bi"
        "7mA40nSQ1TAcWfWJgeHIajuCONIF7bkYjvR9TnAup6ui8KAmEJywMoUv6E1AGllvlQnSyKoboHMy"
        "603SQRrpM38XpJGWkTgLpJHeUu8gjfSh+wVppO1j+gZpZD1RDkgja20zQBpptsVFp0yWM7NAGun+"
        "QmB8P9eXQbJRuXdMHvaJAuUjnUnVcdk9I9mjfKFyf5q54Td/MuyVfUu+dFJWy/M5Wq3PV7a1Pmdm"
        "rc9XuKU+3DgE9SNf6dZtZ/LVbqlfOX7Lvi4tX/WWLSYkX/mWHUp6vvqte2Xk6C71LZ9XlvcfVg4C"
        "3/8ZKedr+1049jXitjWc9RZX3XDAa3zsWjjVLep94ChXjQyc33ns7k7fQWs4qe1dDxzP2tBjMEzW"
        "A/tglpRawl0MfU10CeRqaMC3CM5auMMl4GodEzpBVBNdAqMqOpdgp8Z9LIKXVnJkEZC03aZJkNEK"
        "szI41PewB8HA3IokpcOZxCTXWlFcnHYWOE1MZzUKdXWcdqoh5q0qaReHnf2M4LCzoNqFw86ieIm5"
        "qH6esLp5Irq9EbDTo/nGwM7CDSYBOxVNIWCnz3QZ2FmMwiRgp6K5Cdj9PBNBOn0LqxOo01CIdgjU"
        "WfwEQTrVjEWQTh9pd4J0+roHQzrrB9Mz0kXxizOqb5DLghomvZAFnWNGJYvq5Rayli7Tw2cbJ4Nf"
        "GAkaVetKZVHVxFvJVr43GepkpyAMg5WDCpGVodydn5/Ecbn5MjvsHDFSJsYdL3aKxVC38/PjsLuD"
        "rJSPYcB0yxEZ6W6Qt1iYS29hyGKhk3xaGHadWCvlZRgH7m9qSUWWKwA19fTztBqVdrJ6az5aQ4RR"
        "Q1GvbQAJ9doPwJ/dw6yZl7eKON61J2pl8/faMLju8y4exYTu98XjAvCyMvUAsPTAeiGU0vPCsKqV"
        "dzEEJL14L4BCdqJ9APTooeh3AN7osfE8AGS03F8DwKJH5MXpye+XcTqAkLQHh7j/vXtmzQqLBuw1"
        "K/TYc62aFdZErtWssFp6UrNCr/1uzQq9Nj+++P1scmtWWH3DWbPCgmMRVmjw6LgAK/R4cmyAFVZW"
        "bwGwsDJoG4CF3nNQJND7ev+Q1QFY6MULmbLobVwBYKGvbgsACz3VHROAhdWeOwAtdOSwKLP7uRtA"
        "C40nDnqRu3+/400X/vYtScNWvbOuv11M8q7nzgidGWF4KXJ/G5ykkbvet/7b7iQdwtuc/Nv9JH0Q"
        "75T/by+UtF7/9V7nIYYQdxvhb5+UdAgP1k7XlLS6vbdadXqopGN4Ts5pqZI3DXCfhbFQP67KabeS"
        "Bi9/7vuY3Bjep22Lepbpvo/N3cfxxqDMdA7321J2ej235HRxyUKH3eJlTk+XdAxv4uZ0eElDmI+L"
        "YspOfXoIZafu8iTzKroQW5NzJRbyOzkHYv3TJ+c1dOHsFZbKXEXWSCDzD3qfLkt3qVtebGDmCbJF"
        "RIZ/W6gskvm6RG2bBL0JJ0l3WxSTRLeF2yExbtm4l2R3Llz1ra5NUtpW6o1Es/VHvCSPdVH+sRC2"
        "AOpJkldX9t6mSIpbi8DuJGPtc5Bc1R0nF4rJE+rU/pIw1RWu+1/spc7d7Mpgqqtvb0GWwVR1LmwW"
        "8HuNg6k+nxelnMFUS/B7y8IMppbGu0mYWsorO2u2yv2DhGkWLZ3S1OKyO0lTvdXJzoQtR7eTNLXS"
        "+yRM7WuQLNV36m2MpSzVbYglJEs1/NsXtlrobU+kLLUYeBKl1lxzkizN/1P/1ZXhja5LFnaY423s"
        "/iVtWVLaizn6C95yGHfnYdLDeJuef7FcPxQC6TqOGNoKqcNZEYKXQcXuRtlfoNfByRfiez1Og3Bf"
        "jzMh+pfjbMwZlMHLLlba5McRyFWUz3Ux1/H4XKw1+8HhjmepxukHczTVONOdPQhtz0sEckPl/YAz"
        "/PL9DIG8VJ1MMHmnZbHGnfdUGpZ6N++eVCu8S7K624f3Q6qdD87Hfpf3OPa0m3czGjE8F+9cskCL"
        "0qNYHv54cCMWhr0efIeJ94PDUPG9D15CN+Bc+2gTE4MbMb64jQcnYOL2QP50s7JhFhbsSmMWtvoL"
        "2HMxZmFuknmJ8PSFCWZh8h0e1haVLTysNRy3PawlNCq3PSwgNND9TJ7Wql08rE0qPK0tNv/ytNbX"
        "/D3QWj+vu2qtaK0xNT65MMPq/lmsYGJ/Gtwx8dgPtM5KP5S0zm97YW/b3axtGxTPB1pbLNJ8oLVu"
        "UbovTDALW+0B1hZJdh9gbRVB5AHWZiPzAdaWLQFtB8UVyhFchxXevbpJf4kdFuhv0NllmD8wod0e"
        "Kv3gL7vDmx/QHnz44rFtnbimOQTxUI5NukO5P3WGre5cbNsm/P2Bzb7jpAeBkB4nP2Bb97F+Q2AP"
        "9R/G9lA/scCVMKvCP2VBzU82xvg4WeJCnI/04u8ooObXP/eYUGDzC3aLYPPzp0K+WivudcFBbwun"
        "gdM9DQ8ZqUY2wXGrTT9weOu9ueuanb+Di1NaI4DcPembaf4BQQgga6iKv6RuLyLJReMSvNX8jrUJ"
        "yGpMix9iOAvRInCqtweehv5HNAlw6u358Ta5RZwxCUZqYIe73SktF7kHipJbxHbZIP3h7UluEf4z"
        "BY+k8Qrz4rTTKfw3cdpZ/MbAaadLK6/mY0Q71YyJ085+Z+C00+c5E8edrpu88iYR7rTyt1wCd5oU"
        "MA6BO0vCmATuLN6hEbizRJJG4E5vzw1SbzN/EX7Cw8pF/onZLl75InCnL+JjcGdRNAzuNEzkdAJ3"
        "FltyCNzp7W0Gd5YtRNBO/xk9mNv9roifn0UG52X4EN090OnMEG6TmL/NQNJDwxtE1RFDnACcxIO4"
        "r3MzQyx3dneYIe4O1vvEEBLt3eJjHD++gbLPE85AiTFWRGjifbg7MI0xUfHnTo2y0euG5rTFPcsM"
        "6E48i7uH2RgzFenR1i8+xvqi3QF4jO62Y3N6n6Rj+Mxn7FTOjfwGPobbOsHpkpLjo3NuRU8wN+dK"
        "dNXcOfdhC/TG+QzdDBicn7DoAeGcg+pYj2B7CYdzA7qhsBvHfus+d0jgWw7MJCmvwm+SaM+6qKU8"
        "1yXld0iIW6kKEtxWD4OltT7iviSi9RdJKuuuA0tiK1uxSfxaVskimatVJ4aQoNVNCP8Xa6sJwv5q"
        "qwniTWOdLpIPCVI7DSVJqov/w4HUGgksjqSqc3ekV60bmyOp7VOQJNXPcDmQ6qLM9eIZSHX9fEmO"
        "Zq32Uo7azsUmOarCLiRHbTOCBWlW4yEFqSZALJKj+oPfIkmqX2NfEqVWp2OQKNU9inZJlKrwY+es"
        "VjOFJKm1kjwkSbXf5YJIWpb4d8+BhB0mPOoih4mSsclhZCIYLodpB6FyOUxvCKTrV7wQZtc9HTbC"
        "8LK3g7vU+Iv0chzBpsr1/VyI+HW7D4EcQP1cDfIH5ThhtDI7zoS8RTlO75D3qMfBNkvKccLIZm6c"
        "vTBXU6aJQX6nTi5ckBsqx/kwt1Tm0EE+qv5Wm3dZ2qFgdN5PaUeE+eCcVPsJ75F+tMPdNJqYdl7e"
        "96h2Dd7hqDYKjEbe1eU9iybehJWiEPF58SGW8tMeHIeK/SNVzLT2ffAQ1khjPLgFEz+4AtX6+0Ub"
        "fOLzAP2sd0hJeush8kB3zZ9b/QHqKr4PIFdtkwd66xP7vzzAf9TlSa2tEvzUGUg79+FJbe0jOk/q"
        "H63boLEitWr34EmdajemxXbD/Xd1Go9qTZ2RB1JrllF/IbWKxwOorenAfgC1iv0dkwHe9csE3n55"
        "P6BaP9R+QbWK/fJ+mHnt84Jqfea5H1ituVnnPLDa2qjsB1hbL4z9AGv7XzywWnl7IVaHaRhYtEvY"
        "uuJshNiR/DvQRnsoH9AMO5RH5aPAZ28LoXeY/NOgqJYwAcad01xYPrHDzVDvbz/DdudvtMN2B8av"
        "RPINAT1U+9HmsN3tjm3GhPpvQGQP9RNie9yL4kB4j9Iv/NA2QU1P1jchyIf6iZ2XhuknHzYvD7OH"
        "MNqHX09w3mvkRFRUNdEIFsP4uzvHEBzn1mtw4wy3vnw4t/XWBGd1WmbipBq/cuJNNfcTAsV2kr4I"
        "/v6ICOTqz7RFgFZFZxF81Wgb6QRUTdQIkurtrUXg055JCGhq3c5GgNICZBg6amHRvggkaoQLGKD3"
        "O5XpTAJ+9vIOgTxNudsTB53GexwCdJbo0XDQada4EPNWXV6cg4Mu6zQYkc5qTHQcdVm7lgh1+q6x"
        "aJDfvSYY0mn0yCFAp21XqOmlVYa8BOv0l24nWKePtA/BOkv6YWaNFiYwCdapCNyn/f0iBgM7C/Bh"
        "YKelPxsz/1MRuBP7OwPFDUCS3CK+sHp+8sq3H9T/c1Ha6sP3F4ByuP/GDij9/JYBKOX6sz1Aefxo"
        "DOBuj186H3i3wy/qVioDI7iI0g1Xt4ZRqbQF2SX1k94ZxE8AvxpETNTKFlUGqqUSFfhEpMGcEbjh"
        "FWypAr8qQf22WhpkWiPGdFaQC1JKe1CZuSHSGfQxqaVtBsStn3WdIDsa+a4YfXVm6qeJR5fPviHO"
        "ahbHnRBcrYPnhIhqOSIdwqhe7s4fdvioe0DA1JVv0GPKv1x8F+Cg0fLlQR5aToNgEEw6cHrk0/XW"
        "bRjudFEXbTOG14Ngs/4nG6OZrRc3hjBLL5gYt34SIDBSafOOCeLJen4OjEmaVNFAENnL7Bh9dOfi"
        "QMSxdRM2ydNaDMHeXXB53wcizv/H2rkmC8qzWnhKBsht/hM7XdVCnd2by8Lv/e+KGvFJQgik+elm"
        "dDldgohjrR+IOLoKnQcijs6zZUPE0UXN2hhxdMFwN0acdCkzog9L+1kYcuz6iyFHjzEsjDj2uoQR"
        "R68nxoiTZ584YXeKYMTRCpxRnQz/eiYhDDp6PYHQsXMLB4OOVT0FpzxWjTab55Qxsr4XD1SvOxIm"
        "1fHCO0FUqR4JsL6Fui9UTdkEquzy5yZ0K8N2R8K6ujJJOtmqy27MjISlfHIGxlIeJdwC5SfFZhl2"
        "HSXhQuUzo2od9C0ZZEv5WBlzS/lNF6tloQM/iyxodcM/o0YDlUdx95icVjpnrN89g3l9ZuDAbNeQ"
        "Wr8eXSbZc8IU19D9c2F0q2TiwFYJC0zp9EzBTiV3wDy2iOkJU1hjd6WBXt0SF8J5axrBIasat58H"
        "p5qoYGaiGe5RwDFTDV8cnKp5Jk5LC+o+OCL1PpNwLloIxsRhaN6jixNQw0MGTj0rR0E46rQL9sUB"
        "l5ubK9FgysY01UJlBaaahV0yTDWVLIapphIhmGomwalmIfsTppr1GD63tAhZHGq2Zc441HRrPl9S"
        "+xq/BiWnmujEf6bxPXQzf5+BQ83CBhpTQNXMxrxPnw1HmmW6YBxp6hGahCPNXFqNmZwl/RCcaakV"
        "UMoB3+ugrxMGzPopBgoVz4xsYWp/zqZscSz4SvgWqvZOEBc+4doJ5eI+pAR0cbZ9SlgXqlbKu1AW"
        "lQbIZcGJLSrvlq6TwwjgmbIvzLueb9rGstTLGD7kTmd24d0o5WAY1Mw3g2Ecy5xu0Eaym8/y4sT7"
        "6cZsdLczVwbGSCYsGRvj2hqrxGNeIMy7VB4uQWj59Lmkn5X6uiXydPabxq/8bDUojeK9FtVE011r"
        "OSXGNF5zzppduikbxec5144LUErbJQBNlv6uxlGaumxM/9pRg8fqAnBNG702jwX5J+c71VzRDeC7"
        "a5jo/iaPmiCa0i46MOE9g9SosG7gmg8aKXDqOZMmKVv1REk3D2mUULCKXiUT0lja6V06aiSkGeK2"
        "d6nfrce71D9vfb1L7wSmMxpIO6lGgkaAzlkjwbYPT40EC92cNRMst7vUTLB345oJut12Ts0EbRdh"
        "gj6vH4jhfTdaE2CCbodGgbXetQ/XTNBd6Hxb85+U+aOGgtrk22f850r5c31Q2iKLN9N8Tz+boE4T"
        "75/5swVutEDndQz9bEI6TWz3PWbrKd6/62cTq9MVw3uP3WhBnndd97OJ02hi6rHcn03czlPc5XXF"
        "7/oaWRuaB+OfNjrW+Ydhnm2NjnmKzmb/aaNjoCLLfRdptXG9zzI6JipzelY+Vuu7kNsfu2Vi7mN0"
        "rHTpaY5/2uiY6X5c9FDHTPd+vE9LHTPd7P601DHTpdV8/2mjY6bTtVLqWek5vSHlDS/cr3cbHkcs"
        "jLE3eOjs3cW9lLpzpDdMqO7e3tigUZdDeiOCducjvWHgr07mvj32/9VNPd2JA/8V6lFknPLvk+q2"
        "MI72V6gnjHGe6x2FmxBXoWs0Y9a96s4oxqp7lW6T0a9Q84TjZP4rXJNvE8d/hZt2E8Gvbjep+8qe"
        "KU3Uvi/Is8vXt0ulTVX9F/0BP9a9QZDX/YZU6oSbE/FXp0t7mKW6Apqzx9J/VlkwSzU4dDZn16+O"
        "Tw+l+hnG6aH0r060OCuO0r/CSe7qYZQGM/0PP0qLmXOeJkpf4drUROkr1KTtOEq1c1aTpHrDMZok"
        "fYXH/fyjtJs1/WGmNJxN7h2pNJw93a9BpeHsx53sUWk4S9ZqwlRN1Z+xl4Yj4kJj5CXuvV0qyN1R"
        "NaPBZgVqq4DH6w5m0m7GnRHNdjOEYLls5R6E0lUPszsDOt1mprv4v+1mzoWYXrbj9vFom7HvBmib"
        "sWYLqfhfPo4/JZf284AukrKdjblJvnVz25Y36C4p2mE9z1CNLFU7MqFxpmpmuV5b6hozT8Gm9FU7"
        "5HYPta35unMUaluz/15F91gSpNkfp2zjWPqDk25Qc39Asj3z1R+FVCv9oUelW/rjjaWn+jDI6Be6"
        "/YFFzwU/58Noop4o9+sOzKy2v2GE2dVa98NooXfmDyOEav3diAne+H4YC1S8z4cRQH2U/uYFZF5M"
        "635g/Sv2x2OCDIyX7A9Y1zt/Qbm5gukDv62zv0BbLXufPqmt1NoHUlslstsnte6t8+6jWjM0SZ/U"
        "loSrT+pMurGXxdzhfifv0ye1HQdfH0itJdF87wpmVsEOLGZX9/IHUqubzfWXDQHv/AXV5lA8H1Ct"
        "Yv6Can1n32cHGRjL4A+ofsW+c/nBtPfLBPwVzzk+oFpdqr6rCiOXlqLvodrS2EEhL1EAMC8E1mHU"
        "8YDcPpHcn/cJKl+uY3HCcncKtuB3Z8ivE3X8hsJaArUsd2l3UfmcmPsm0vPA5tyR/vFXgqjd8V3Y"
        "lmd0/0EY0kP9xDZAQ/2dENgjvQbVVmyP9PvBdkUD/ZyEOV4C/eKLxakEejREJbr9dgcoQs1vDdDb"
        "H3Wf67qnhvUtHPm6DlmCg17rj7uM4kxDRxaOdF1Udjiumkk4vC3CfePEfvvAdQ2eTCJEjLNZYzjc"
        "ro6A/Ir22A0KvyKR20CvvpIf8MH5nc5oQFZjBPxgvJn3Hq8GTrX3/B3U1Bz+cK8Dzld0/dV0ahFr"
        "0WkgUoNB3BgiSi1iCTjx/fFOh0YDgRr+w6MBPrW9dXDavdNxd2ZHqQTzEf+MeJ8bZ51Gvrsj38w1"
        "q8E6XWvvBus07sW9z0k1iw8Ou3fr2nfYPqnmPKfBundz/XEDv0dqCHOM22CdRmMQNVj3vtOlzixS"
        "O2J1po56p6czX9RIkdlA3RsH8TyrgToNEGnNBl/RfXYDdRqmcToTv7cfLp0G6rTHLzVQ94rGE8R0"
        "/MwTn25lRrFyeBPPEyzq4SZou+EB0mpiBKBsNDGDuLpGX7gL5d1o4s9aN5hCwk3MZwWrffwp9o22"
        "2PA2ZhiPh7cxTjT9bPTojqL08DYiXDdamFHkHt6Gnm37DXO8DRlRaDTeho+40TLS7a8ROla61or2"
        "6eA2NlPkHMDbeE60bdd4l4eDYQPv0yCssGWn7EalJN2h256nN5DoAY81e6OHpdfm3pBh2/+jN06o"
        "jqU3OKhTRJojgu0ir94woAti11l0K918/H2BpxZSE/K6nn6kSXZ7Q2ni3M4TSJPiJpxNdOvBlzCO"
        "rhDeI01Iv19jtsmsxzs2N3GcHygpDWdLl7vvkx7aTdi+QqLVJOzbqTy6WFWX1t09lurRiac5K9dt"
        "xSZLdfdWTo+l5jSYPZaqzmXwKnXXndfu8v3oSo+lr+7I6bFUT7DwarJUfQn+PltpMNPPITBKi5ny"
        "zCZMVeg/amk08/Fn9LPunHWaMFXhPU2Y6imd2YWp+g2oyVI9T+Lu1FBpOJtddxeVhrPuc5owfYXu"
        "dIhqu/G3gqm0GyE/9D8vce+UbJ8QWstk2di0tc65vRDy1gnfFwLishmXW6vdjBsMtNtf6hBC7TKn"
        "+oYgjqZmr5hetnOx+XLZDi2I+GXOeP/gOv9H7Ui7HT9UY7bb2QsaLcp2LkGDR22GDI0lVTvCmNuk"
        "asdPdEBte97gyFO1sxY2qy/fax1oYCr7mQY0TtX/6ekPW5YccvTHKs0W6UYYMqR9ouQgiFakPxSp"
        "lrg//qgWWxv4fUXSH2ks16f0hxfNvSn0YUxR8ZYPA4kl+T8fRg8V7w8jhpWDvB+GCasZwB/GBv1Q"
        "934YEPTO88MgYIljzwfya4Ja+kB7qzJ6PiD+FfvB94SZ1/4Ecy0BeuUDwbWzw2MsyFeWD6zWpJmP"
        "9FmtWTzvh8WEat0EUAJpXcOcmHSePqrtth/WB5Yuf/dRrSlQXdu42OddH0itSWLPlym/ird8ILWJ"
        "zwdUa27X8FA6cuf5gdSq9ae4mHFJGKaHvPIzP6Ba0wbL/cBqLSs6v0zHtbgrzw+s1juHwc1Ih931"
        "gdX6qfzz75iBke9G/FcbnsYgaLsykk9mhNiRnJcg0A7lD+TuCeWYmyd890MIvuMTRIwQPD4KgTA8"
        "PAhyMI7Hp3AwlEf6+WDz7kgvA/PWxPdfENNDvWBBLJF++TP4Bes3RvfwIFGY3g/T74PtkkYnOfwE"
        "LYTa33rcrD6E2t88jLn7w+cXbG4eHiTjCSE//P4ycOprhImfMivT0LqC890SWjSgrprBOMlNc3B8"
        "a3H522C2Rq6siYNa066uBp7fTfJxqMFkjfJ/pAHi9+mun1mO8le6o4HcV3QmNTirImmw9e2HZzZ4"
        "qh0upwFRjYE5DXDq6ZfTgKUeFBFpEPKN7BjMDSxqqlc/YXRqDXOsBv80CsQPWMmNYW/GSafhH09j"
        "UmtJFhqkszPkCyedpvlYhJNONWPipNOME4yDzs7YHBx0GlIycc5pNMkjDc69u948OhNOzfUI7g3+"
        "EAWBfJyLJjc4pzv5szOJ1I54boN0KuLRIN0r2g83UJfnZU0t4s9sbDdYp0dm5DRY994JXeT/PKQk"
        "pwE7s70O7PRUWJCU4u9Fae47P/8HoHyCCI5SScedhAqg3H6eUeCWj79kr19z+NtipVAeP/64FE7/"
        "7El9Qz9ftBWIyktyTJ+StZSDhG61kvzTgozc1M8bCpjQn/8r8KwC0oCgtXJG+SNqa3h8KWJIfnbf"
        "AdjSulFhk1IaOGIBU9oUnQKpn3f7KR4AW5pBwANkSxPDri3uMNZqOrrgiLR/Od11IarqeYw1IZbq"
        "5ftCANW1710QNu3sCwZLXUstjJF6wiLKvhNdH+03BY+z98QYaEvBjYHP2sdgp4cmML7ZSQnCqGad"
        "szCU6SqRL8YvzY5wBwYtLf/xbIxU7/XLX4FGH3fdKEV9cD1HK9ygf3xvFEls+xtijp6ECPLQBJf7"
        "/jSOLh8PQ8yxFHkDYo4urc+BmKOnMAhjjp31mBBzdPXpHkW5weUy98CYYzH2G2OOnTsgjDlaaWMw"
        "xhwN3R8Yc3SpEyXoiq5nxqij10d5cIPrg32m6Ouu6Sfoij7vHiB03svlTgw6eo7Bd/NHX3eJv60R"
        "fl0+hEFH/QBBftq/l5chrjdBUBnXyichUh2lKwmgSrVkc6RSPRN6la89dgKzSp1Op8raImclpCvV"
        "furXB5T7I8oY6N2ZMyzWtUNmRsny7iNdltZ3XxlES/mRjKnlw9PIEFt+OH/AQ41OokBNTL5lZUCu"
        "Ky7sjM+VPNwVxuTLd2OiVsdzZzCvSwldmO1aC34PmOgaDhsUaU4kDXRrsO/Gea2SeWBKq+QyjGZ7"
        "+wMDWctKMMMU1moSTDh6X42fSHmM9D4kOGS1rscZOFmtOsbGcWrPhiNUH+0enJt6G2nAUrt6T5yQ"
        "GkchB8eiuWoGzkJ1Hu2JA9Duwzj19H2i3F5Zv52L802/6d4w1KwmAQ41jRtNt0CCONUFU03jYveB"
        "qaaSBtVUsg5MNX0XgaGmHXYJhppWXhiN+eSrYcGZplvlz8KZphpinGm2jb9wptk2fmNeqF3QmQyq"
        "Zl0cavpstzHt03iBKNA70fjpiig1g+sfhEntwF37UGoGaw+caWZujTmb1SDJFuFRxB/5U9tcRdtd"
        "inChWg8lcItjwW/Ct1C1sg2JSHUoo1wcNZm5CuNYzYR1Yab/k+IujOqW1H0YvZi/qzMK62DfOkZh"
        "HuznAx9SyVa6YxuGKo+VETCOcOYMguHHHivjYBQP7GfWGYWVrEHpFC/Mwx+dNc9lIulEL3q3G8U6"
        "5z15o3LnhZXcXdJRc8wTl0i0ql6n5KDVeTsl/GxWTyXx7NIac5Zhb5Rse3vAj+s6zqXib4Ze79Lp"
        "h1Y87rXz1MDSWOUrNaU0NpepRpNl2Qd49F4bxBF630xkAuTRfpBT48YyBVLNmPfavbgGi25Znl3T"
        "5L1286oRovninlNzQ7eJx6lhoRvcIjUh1B58Lv+4VIPoSijorqdLX3YupSO3hIJOI+8soaCXplsL"
        "P2Nzd8kE3T6t5zhauWucEgmWYXvVSHivXf5v430r8U9sDu9zRcl2ve81Cw/+zzjXsWsk6LtdqZGg"
        "7RKABEt4VxNBt0TvqomgycnWrInwXutXBSPvsy2SWRPBQm5vTQQ1hzyI4of1Or8Z/S5vkYWEsjPS"
        "0+9yF+mOgTOq0u/yF+mugeNRpd/VMNImnFUo/S6Oke9deH2xOk1cZ6FEv0tnZF/EC9Kh35U0sli+"
        "s7wmbqcJdpwH5BTayN9EvDZa9rnY69DRMVBvT4mcohxZE9s10NGxUPYypJJTsiPtUvL+tbFabYhn"
        "HaNjpG68MzkFPtLYcP9dOma6+HomRh0z3eN4JkYdM11ecmdyioOk7+JsK5JTKyTrUy9LGDmlQ9Iy"
        "C9wcVXQp+jSHkiR7ezp+WKHp2xs09Pyr+70noJPe8KBrWXdk2nV/8u4NBFZDbvXor5XQZDSRbzG9"
        "o8l5vaPbM6M0GfFSF+RI1zv6Q5LUd7zUhLf16mwS27wK1MS0fo45mmzWfPEuTEdpOWve0aSw5osn"
        "aaLXMtSfJm/VlyC7CVmNLffvWFsODerhVFemW3o41bXvkh5OrVIc93CqC3gePZzawWHq4dR23KSH"
        "U/V0jCZO7TxiczKt7gJ3WZThVNfMq0nTpLpbTlN1Kvhz7NJkppejM6dpElGe01SFozv/1aOojzRp"
        "qt6Op0tTS4p/mjRVJ8Q4TZpapPVo0tQixrlJUz207IOfa1s9t0lT9XjQQGhaB4guBK5lbLK7lOJu"
        "M3sj5C1bcd0Xs92MLITLZdfMiWC6+lBEE6F2GZI7oTlxGZ7KmFekfCt3CTLaZjzcJdCgdjuCuUjq"
        "51nQgFC2s7DZdtmOPxVe7XYONnqU9uMPmG1zXi4xRteeeQjmPqnaYXd1RKPdzoO5Uap2vNRo3rhU"
        "9jM2Sn3ERt6MRn+O/kCloe2P9EcnjfLuj0ga6s7cH4ZS7cKe2J2nb6yn9odRRsOnZ39k0ext58No"
        "ot4o35uMGdXk/WHcULFrHIMxsYwPI4SJ94dhIe3shWn9jbYNPrV8gL6VqPwAek12CLplXDH73tyB"
        "3XmdDxxXf7B8gbcla+QPyLZsih8WFxrR6n4pQrTD9y0xpD2uC00g7T4fVgwW/N8ntUrd2cLGuuo5"
        "fVJb+P3uo9rC8L/M/DUP3V0fWJ0k2KtZrWLf+8yY+MtkXl95jg+otoMFX6btyamEmtX62PvLBF0D"
        "pPjLrFzdk+4ckSADY3ZthCADY3KniYQZ2JXxAdZm2l9g/YrJH1b/1UYxtmNAHqDwUIG7dcWofBLk"
        "8onk/g8yYfnZCLzDd1/QhmZ4AsH1/R1QLl6xUYfiYUw8Y5Pu8OkvNu8OU94fDOehnrDZd5i1HZt/"
        "h3LfEzLh7vM9IAvWu5PDARvf8T8fbH37wbz6YdJ1IQjz0fkF74CRR/pIT+6/S6j5/Vl1EsT7sP/8"
        "XU3Y/nzHqa/Wxcg5OOn1AIQwjndbVA+c6bricD/nzDWCw1tXRXxwYqfddlLNaaBZt8f9GdeTiqSB"
        "YL3P3A3uasS96wAcqR0I+3Ftkj+ez7WZi06DpZYsnxoA1Vfy/c2pMczhoz41h/WM1eCjRoNcaUBR"
        "k8uzNEioWez3aODPciTeBvO0PsGzcNLpMsBdgFCmoeNGtnKqWY/gpNNlGeZr+KmZB0edruAO46iz"
        "A9mEoy5JuReyTvPu7QbqNF3Z5QbsNNrBn6WlliBTVgN2Gh5B0oCdJn33wZUawx8WrwbtXtHjg2vn"
        "j7casEsO28Sw0/TtdBqw0/Ms9zRg9z7elQ7sNLPe7cAuKR0Qw05jrHzPyb954rMtP39aRI0maN/r"
        "oxBvwnfWSaeJKT4nGy3sYIaIN3GjmGW4CfGJiuuPa0i300TgwXw6duWH+IyWbUoYmYe3EUzBOtbJ"
        "c0bxengbgUe5Y6C8KUJ5pw0OyI63cW/k7W2Y6Qq4DzcReEE7Vrr2iWbAeBu+dVDHStd4oiEDbmM+"
        "O/IK41/l6Q4ouuvZHUV0m3ZSb+jQhbk7bZBSN13drHXuGaNV6vZsjgfan6s3DNi6u8l+y0DATeDr"
        "KY1wh64QyrpNtKtwrCbPVXh3E+K6iL9dcttpG27i2pJHdBmdHwwqDWfKliaONVV/G8Kv0A/Fo9Jy"
        "1lhd3Gp6iWc3Gau5JvwtxtpyxuAeTTUD/+3BVJfjm3swVbfEOT2Y2l717sHUysudHkztOakHUz3Z"
        "Ex0ILHRzN2mqK+45mjRVp4B7w1EajOzJTZqacDZpqgcRntmkqbpYZpemKvRjtkuzkSCKtLQbN5dR"
        "TlMrZNed3GoOf7dXqbSctbk7j1WvCO0mTa26Ajdpase0qElT9QJOQWhaBBU/1zVA6jZzotizZjNL"
        "EPbWzSwExfVLMULmsovd2fJuNjMeIYTbVTP0LATjVTN+5N5vqpft+Eus0e6djc2g617GHCR1O9CA"
        "UDbD0PBQNjMmNFrU7Rxo8CjbWdBQUtvyhkaWqh3xD3q0jTnYomsbsx+hTm1jlkPQqFS1w/5aoW3N"
        "g1Z/zHoPVzzr9geqv9rnntkfnVQruz8kqZb7w5DddvTHHntd6g842s08+6PMqx2zP7K8Ulrnw3Ci"
        "4jM+jCEqduNtBmFimh9GCxX7R7sF6+szP4wMKnanuWNhYr/DMPMKjnZi9sVumNPALGz6IWuYhflL"
        "UcIsbLqnhgmzMKH9AeHaYeN+4LZZGPVh/Z6v8LOHEKL9Q6/Vh7Vq6cP6QbXP7tP61Z7bh7XddvZh"
        "rdp5+7C2T8R9Wr9aevgDrVW8vtBaxWN9oLWK/VODjInDQ+mA2D/JNiYmZvpAa/3M+36gtd6Z+AOt"
        "7Tt/mZy/YmH+QGsVn/2B1q/Yj5Qi0MLu/UBr7e27PtBav7NMhNbhYYyB8DpSMzS9jtTjXgTaoRza"
        "wwzVeyPoDs/AuEjZoJzdqdRB1RdDeHgIQzAXTlhHZUwI5FHf+YcwB2x1J0w4Bd5/YUSP3t9fKo0J"
        "6y+2IRrrCUJ7aHx+/6PmJ094iAXT34nNyKNDJBOclEd6dpdQhNrfDNIOovYn4wrE+/D7zY0jXyNM"
        "3D1YSjV+jAGnGqKNM11zlMjCSW4awfGt1fOEcWZbvx2c1Jp5NTpimGi2P117UtG5pwFivdOQBn1f"
        "0dqjgVy9U5isI7uTH0Y+i3eaDaLaO50GRrXLW+y0CJgOMO2siDQoqTlYn9tAoxZTOafBQ42x4dGA"
        "oFbQGatBPktkjNNOQ0BIcNppOMZzcdrpIfK9cNppGgl39Jq5ZjJOO322dXHapWkXTt7XZ+G008ie"
        "xQ3a2fGX1aCdJXzszDVVxLNBOxWdDu305MI5Ddqp6J4G7SyKZzVo94q274FIDUL85MojtYhJMhu0"
        "e0VzNGCnZWL2asBOgzW4wTozogbqNIuH/2Xfi9L4/uHnDyqVdKYfwVEr1/TX77VyBqf5gHv6WZ9r"
        "4fXTPtc9e68fflEq5Yg/D6yVPAM+Ao8rweK8ls4otwQgHQExa+keQUByLT1PcOoZkK5gJwyQniCb"
        "W/1d/XF8AMY0HwmoWkoX3SBpRCn109QQYEx/JteBOxV43hlMLeteGu5RKRLk2/gxJb+UejTBD/kI"
        "LqdzF0RZPdixBoRWPZexBOKpXc4QRfX0xmWInTpfHxMCpmUUOBAldd0xQDRqOQs/M0L0XWWug0FQ"
        "DymcgZEvXTcNCZ+HN8Y4O/swMbBZpVLBaKb9OQaGMF2RLgxbWguED8aq9/rrBmJQ9Hn/9P7GsKQF"
        "P/zUaOHnvbwxAOnZCH8w+XW5zuInBB2L+MemdlYagyDo6DmEATHHEitMiDn6LLQh5uibXow52o0X"
        "Y46eZPCPBT3R9ZsXxhwr4SkYc6z8AWPM0QodizDmaMQ/yhw7tC8Yc3SFeEDmaPsHQ46WziAMOVq+"
        "Yl4MOe/1fmAgRV93ySQMOVoVw31dCr/umYwhRxemfgqf9/IqlHNRNu+pA1NvQqRSzZIAqlQHG8ag"
        "mrKVZxnY+2TLz7KmxlkJ3Sq1v4C9qPqZGfvqOh4nQ2Fd2mRkZKxrmtwMlKV8zoybdSkUyjBaP3wG"
        "1frZR8bY+rtJxtyy4oU/ywWNjvwNEwKNjvzkDgQaHS1//QkaHflH+4jRrtvpDLL8cGfDdNeyCcFu"
        "SSLxV5CcSfykUpJKGCe2SS6MaX0XmMwaFEw4jrW6hDDM4HfV/TDOXZXchcNWNVNwwtqjNbCqmijo"
        "JtN0AGq1OA6OTdWci7PS+mDhgNTgiI1D0arGXpyE6q95Bo4/qwfSYJ7GUxzBQadxG4dwuunn8X0I"
        "rkRrBPhB/5lkPfjUVONNL0w0VaSL5iAiFgaa3QSfbL4SP4fBSbs4qBOcSILy40+iofEQzrRX89zG"
        "rFHv4/vBONVIg2n6bHxwpmm/5ZsVviaq/5s+28SZpmEGc+JQs1ALwaGW1oml1A4mEw41rdTBhENN"
        "++0MHGpWxeQmUAtDV2/mAIxU2dZDGOBMGdzCgPCVbeyGqpv5BsO3yjyEYezzzuZuUcQmu07vW9zL"
        "L29quAsfcabEC6OyhTPohYUs8v2LMAZVToa+SCY0MvqFspVuaoSywxkDI9mmjIJhYYl7MxDGwczp"
        "UjdMxJ9ue0SqJ6rVUjwjpxO9qEf82sdU2Yhf4OPnq71bjY8fzONcSn5cKXuXipTk0xnwHCXu7NIS"
        "cToVnyXX7PVPCTONkF1UEky3pGjV2LK0+DWqNPbzzppPeq0/UWT3cRESabvr1vixrGVUM0fblVWD"
        "Jt3vHt5XEz8ZwPA+29x31iDR5HFc00PTxY1RI8MCiWtMWP7CW7PBbHeWQNBiVENKIOgO47olEGy+"
        "uksi6PTxSkkEvXTtEglp9vvtXXoeKZmgnSWzZIIGgka1Rn9fKyQ1E3QjcNyaCXrt4poJmiSNqWaC"
        "5nhfu2aCXhtlHna67NKumaAbzA8w5dDtPpo1EzQ7GcKEd5tyRLnTvHbHrKGgAbeXaypYjjpgxqB7"
        "+M7GFP+ucJHWeT5OC9RogZaz98q/y1+k2wXeQ0irBQd6/Ls2Rr5nMZwmVqcJL8cv/66ckSYHd5s4"
        "jSZkeL15Ow/hbR6xU2YjzdjufpHRMs7hPga17Hu7v0jHPNmbjrJToSMPTve+65j/QRur9y5eEy0T"
        "ZfeHHy0bfcT72UbHSqcsrzuoY6XLc6mxUwoka8Nb0LNTGSR7l/t4fUodM3WDYNipG5IGdjP3RhQr"
        "dbZ740hSJS4dPKxSHPeGDF3Xrt4wobK5emODrriddXw6IFjd8dkbBV7dvD30a6Usd+jLeK/CvZqQ"
        "t3Ox0kS7nlj1H7W0GD5XmhBXoT+CzLpzxm3iWu/oD5212Zw2mTUCenRxrCXg3CGaSstZXox5Dt73"
        "jtenXGk5k13LodJyZPFscjU3gFini1InWi2Fqa573YGIS93j6qTUTff9ZqkT91dcpW65k5dd6u4z"
        "ejTVo4gyezjVw6muLsOproG7U2arBjeaNFXhQ02aqtA37dJm/kwwRpOmdg53NGmqi2R3DB67/ow+"
        "+Eu78TwvOUxfN4FXFDKHqYZvS5Olr47cJyWqn3R1p6tW12A3WWqfH3J1lKGB7q9J3Wa8YjcOaetA"
        "cmgWWzbjDsKz/zSEYLmMuiXICVLFgHrBcg60y1DSQwjDy6ehBSG9DkTHJsxlOwMjfvk/LGwA+NhO"
        "25TPEWh4qJ8HGy1qXixo8Ci/l2xoLCnN+R5obCnjuy821BTtsLeb6A09ZTt8oZGoeq8zFjQwlQHs"
        "Cxunyu/lcyNvRsNr6fbHKg22ZukPUBoL79qqYNpn94cijSk/oz/+6H1nf8zR0FrXX36gT+RFTJaj"
        "i0ZCy5chRUMpwKWCf2d3oB+EvfKcH0YMC33mD8OEPvazPowNemd/gFrgO58Po4A+Nn9Bv/kr7wfe"
        "v+LL6wPk1QUp8oHsr/gDyzVJBOgI9yP4facSaF73A6rVg+L6hwnRjuMuiRjSsru2FUi7B/VRrQcF"
        "vqBa7+u67jfWV7z7rNZo8C8rgSQCv2Z1Ek5ds1rF+3xgdS5mTOxOgQZkXH+gdz6w2s4h3A+sVvEH"
        "UqvUnTSNA/Y1fSC1BmK5/xNB9sVeteea1Cp+6AOs9bHdYAXC7Mud/pCA/+NBWB1mz4Y2K8NjARdy"
        "s4eR/q4nS1A5uf/0hO8OgTtST5ehG5QzH8inEx4mgCbbYSS8/3c/qH5sDOPhuRVw1h0arT8VRO2O"
        "H3edMwTWb8w1E+oXRvX4+QlCe/j9Bkb3+EgE5noJU75fbDYeHlxwd78Itb/pu7IItb/pTyYItT8R"
        "wVwqcckGwZmvKyBsJ/Xn2YOL011Xac/Aka4reCac46qhhdNbX4cujmzttr1xTmsywAacNZZjjQaR"
        "VeSGxozUDljcgWdQ/kb3NICrj/dwg7IWtsMNtOqdiBo81Tv58V07F+3bIKeeHVnSwKXGaBA3GKkR"
        "IUcaYHxFfrQvpRYhvquQUosQcudMlFvEEsZhp1N517lGmYaW6xbjTDPuaExgdXV0GKedatzVxUo1"
        "4k5Sdqpx53UnlVw5OO3ez8OHGrSzcAlu0M6ym90G7fROPoO4uNNq0E4DMnxXbGoMLOCG3s8u59Og"
        "nd6pNU/UjrijQTs9FkKdGeEr8mM1KbWIuQ41aKeP5+/tpRYh7E6FKLcIcf/0X0nssw1En3ywPnAd"
        "c6cJPsEssNGEuzyf//tTrE4TKzrGgn+OYJ0PNyBPFHuHP8OUGwAXb4Mo2mfDu/NKdIwFb8PfJBgd"
        "++QnCtFoNOHH0nUMlEcE8sZjSHSKpfEYvle+Y6RRUFrHSuczo0gMuI01whkw3sazowgM/F22H8DY"
        "sVLZI/ILd77L6I0nuuc5qDeO6DEPXr3BQ/0G1BwxLJHC6g0Tpju9scH2VZsDgiZnuM1xQBec7kG3"
        "W+rO6BJfI/XdsJVRW8ySJtr1DYWbPNeDMzSbFDe/yWqiW+94bhPY5t45TUrbo0oTze9Sm2k0eawZ"
        "+mU1IaxZJFzHEpWG8+ePWk3cak28JmGt/t5oYtX+qdNjqdVxmj2WWgb+2WOpeiWEeixVjwH1UKqy"
        "p4lSKy9HPZTq2Z7RRKl+hi5K9fDD00WprYRXE6WaWMLdlR1UC7tTY8tkwU2Uat9MaaLUhLOJUqt5"
        "IU2U6h3HbKJUjyKt7tRWKw+MJkn1LIo/9yrtZj2uL45Ku5mzPVvVWgzSRKn9UxBKi5ji50Rxwb1m"
        "9oJAWzYTJe9oNjMZ4XDdDITlshl362e3v1R0jLvVzHieizC8epqLEb1uBpsrl+2EhxabnXywqXTZ"
        "zoJGg7KZiblIynbc/2q0TfnwhYaOsp09oJGk/OxyoIGl+in8UHLqmnMQQkuj3Q7oPynbeRY0KpX9"
        "E55gaX6v82HQ+rt2eO4+/ZHq1Z57+8OTavfoj0mqXdQfiFTrepwX+My3P+RoP9PqjzPv8Rf/lNGF"
        "tOOZH4YUvfH9MIyodu0PY4eK94fxwh56fhglTLw+DA32yvRhPFDxXB8GAbuzfCD/K6bnfsC9VjKZ"
        "+wPj9TjZB6xrORReH1iuDy3nA8BfMft7rph9jc19VL/uE/+AMyHa59KHlcSr9cO5BNL6IQsTe+aH"
        "+qg2rfRRrVo3oONg38jd1riQdgh9QLWK7xdW253nB1ar+LkfYK1i2h9gbXfmD7DWL7X3B1i/4g+k"
        "VuM69wOp9ZmnfCD1K6Yvk3E7xDY/oFrFrn+TCHzq+QHVaiC8PqBavxSG6vAIyoFcQJF8RFn3IHmQ"
        "xEJgObR5Gd8cmmOHx2cGNM0OD3EsCN/hARhGAB7e3E8i8aD6BWI8tDpw1h3qwZl3ePrIDx0RWL8w"
        "v32o35hLJtQTNgsP9RfDe3yCB5uLRyc4fGwQan8zOCWN2p/40CTU/mSFAY1Y/50DAT/s/jNx5mtk"
        "ycA5b9kdNg53q4DYILpq3MX/LDSMw1uTL2wc2FYxcOKUtmQJhLPZst6OBpBfEQk3KKyRNDwb6NVX"
        "WqPBW32nZzcgq493OmS1DBMdnOqd5mww1IrEzAY4NUTnnAYtNcziSAORb0jHeDpcfO+0w4PbiSiY"
        "LecWsRc3uJdmMA5eSQ+j+J2Xavw34kwzFrZl+eM+zxo47SwrSIN2erJ9MY47Sz3QmJRaLtWF404P"
        "GNFt4M7OYOwG7lR0pYE7FW1u4E5F0plTakfMDu5UJLeBOz1oNLmBOxX5BxdTg2DxTxqlFiFCu4G7"
        "N+7i2R3cvXe67vlSSi1CZgN2lmf0NmCnHR7skf29KI1kn/4OWamk5S/ha6FMP+loreTrMxC4J/ve"
        "1lq5g+PLddcu8c/1lcpgnXORe+4gp1st5RWklwCMaAfn/QApBVPEWjpuQM5aGhRUmYg0OgeIPHAQ"
        "RAfc9QaHRWrpncE0spROjo6GlNI1nyCqoZYyBfF09QOfaOur/ufOCJLs1z18gipY/yp1ZuoHRgSX"
        "0x4YaHXp6e4NSXS5BFkgwsshjKrzwF3V77hjDgRMXR+tC1HSiiFMDI1Wk2RjPNRVylgYBC19AgY+"
        "DYOXi9FOr6eFIU6vPxPjmr7uBmGm7T8XI5gWp1wYtbTyJkiq99iELMHwpGVG9saYpHkknouBSJft"
        "d2P0sWIyBCFHC3qsBSFHY/0h4Oi5h3sh4FjtDYaAY/kUIODoovLBgKPvGaSZCXpx8IaAo9HWDAJH"
        "I94x3OjVZ2K4yePpOb5+YbzRdcthjDd6PTiNsiIaGG3soMPBaKPlRDY4SdLQ/Tkw3rxnBCRKmhBc"
        "P6J8CcHzLMJwo1UwBKONfquENVUYqOwMPWUw6sxYVIeyzgRNtTpbbdbqk5CrVLtrmw2q85VnWT9j"
        "rgRz5b2jUm6gnCXDYCX3/8uBmtuMNohBW78nY2Z590EZQuu7S4bUUn5Ghti653dG3NLoRDIAl2UO"
        "ovOzmFxWRudSHUVrYnJa6aL1W0UXQo3OX176r66BrXJgpGtM6hWY4yphmN0au3ovDGyV7AtT2p5L"
        "YDRrOO88MI+1ngThELaSG4yTVzUbp61KHsIRq2+TL3Z9zbk4TPNnm/mzNbBp1T42zkp9tjFwQGq4"
        "wiCciuqiwUFo0QqM48/qQhyceVYzZOCg0+ALJpxu2tO+5bgSqydAMNJeyeQBIy2N2JRMImPCTNOI"
        "1LthpuldmGCm6es/ONO0k9P1s1+rYTaYpg4JIhxqquHGvNHSUB4carkmNYFDG4ea9lsU2pJpnsYE"
        "0Gp4HBxq+j6XcahpOQc3apYyOyA/YyNldkBRFbDs0aLzkpkZnIFTTf+eoDzMX0kUspmuvsMc/TdD"
        "WxjZzDuhWxgKflYCuPBe2XZuGP67d0K5KGqS3PnBKVTrUsK68F43xV0Y2MkrI15oG+mubajyb1ZZ"
        "x9mUkS8uWpDCrylb5UOmCIyD8ldGwTih/MhAGEURb0lZGAU/+3mNqDCSOa9kSIxk/lFAKqxE6HAG"
        "xrC0hj+3/qHS+l7pTO9nVv2zSgzq1DZIwO9c6lcmmv6lXGLOMvnNkm3aAwDQNFSYaorpbixRjS7b"
        "uZWaV5oEf66aUvq4m2o0aUb+eWse6bUCQCjP9L/cd7uzxo2266/u3c9276nBYrG/AE10k5VHjRBN"
        "E8cANzSUWKSGhab1Z4AQlsZRSixoBN06JRY0g1qQsv73pUG5OPFapVtSQa9ct6SCZb2vqWDxuCUU"
        "dNd0zhIKuu98aibojt25NRN0P2qNmgl6rQBMyK/1vhf7C/PhfbEoxne5XUa7ZoJeG+WpdK71k3YN"
        "77PJzZ1IPzO731szQVOzrV0zQZ9hz5oJulcdxcx638I5KSy/C1ukubAd85PfdS7SLQP3KbjThDeP"
        "kN9VMNJdk+k1MVtNOEOu/K6RkfaF8yfJ75IZaWTl8po4nSa218LttCDsmcXv+hr5i4jXRss8r2vg"
        "LfP0EkyIU4sjDwpeXhvS6g72rGvM1nP4/dEyUS9VnDh1PFJqOJASp6xH2h/O/rQ4VT7ywgYevDpW"
        "OufwPi11rHR6nUHUeorpfVjqGKl4NazEqRaSxtw3BxQ7HNkbRCy+d/VGDl1LbukNF1a3fPXGCNXJ"
        "7A0M9pzN0cBijaU3BFjQ8e2B35KLzybtNXTT5+Kohe6XH6XJ8PYJWNqMeJltc4Rb7bUmtrVUmawm"
        "q/VJ92kC2hLvU5PKesdBTRS/Qi/hVA5gzdh+utQ1ITVhG6Z6z/lqqd5vE6pmqLOHUg3M7ZHUgoVv"
        "j6RWl7xJUl23C/VIqjraPZLqc7prjF3q5hk9kppfoElSW0mfJkk107s7ARilvcjjrnsG1UJ3cBoM"
        "3FGaJLUgcm6iVAOmx22i1E4x3yZKzRvRneBaPb4mSS1oezdJ+vohvLM3OUnV2bF2k6SvkNx/imrD"
        "EX+SWxvOdKE/8ur2TjyuP3Z0m5ELsbZs5pkIeuuUy4KQ+Fszq/1SrhnvbjMbcoGU0aTuIHXbzQxs"
        "dly1c9zZ+Wib8fFna2073uAAULZzNjQelO/1HGh4qN9LoNGiNkLMUVKHgx9oLCn751xobCnjy/3V"
        "eteeCZ3DV+14gQreQFS1s91ZAnXtmfhifpSSG4f7o1YSYFsOVRqh7a48GNLKPv1BSbVu/09M+4z+"
        "8GNB7KM/5mhfye6PNBo47Y51F9HSw+fDmGKhFPRhIFGx73aFTOsPOs6HIUPvLOPDOKFif5CZmHjx"
        "hxHBUgDyh2FAxWN/YL/FmJ8PwFff6h0fKK/+XPfOhFmYP+0izMK2a2GEWdh0R1oCLWx8wLXVy+M+"
        "rjXs2N2PYUg7XW+oYFru01qlLukXpp2zT2sNG54f1gXazfcDrTX33PmyAlDX1fwy7bcYbv5Aa3Pu"
        "fYC1pcGjD7BWL5/7nQZkXDS+zN5VO76wWsX+nvcBX3l9YLV6KX0nM2Zf535htWUh/MJqvTPRB1bb"
        "O48PrNZP5S8V/9WGubuxoJcwYN/1nDEqfy40xw7lBAW6hHKG2B2++4QcPJ1YdofgYWy0CALxSO77"
        "lX5zPM4Zj0W0hMcN/BkwbHh7YJuf4ZEAfyiCTe+CHprw/gvz44fvD07Fw//eH5cO/v7YPmlkf9v9"
        "dQm1v/nwhlAf6dn32BB8/41FqYQnIgTbAAgrPvgeOV+uC4q1cNbrwsvdLeZUM1yuSqp5BCe5naJu"
        "4NsejXFmJ2eiQ1Bb1vcGnfXYgO/UfFLRdOfyY+Qing342kmQ2SCubv0LNTBrOfGkwVbLAzgaQLUU"
        "5NKgqIYIgY6Mn3ei3eClplXn24CkRne4ezQ0CtFu4FDPd1xqMFBjiNwtCZLC9jZOOz364UdEphqZ"
        "F6edLnd44rTTSTsRjrt0or9yzRUcd9oHNHHcWYZ9nHYa3OMv559UtA43aKfHP/Zu0M7y3nVoZ3dq"
        "wE7DZNzF30htgQMX8Mp73B3+x85FDzdglxyMiWGnYT+7Azs9TiId2GnUxrgN2L13Ou5QQalByADj"
        "kP+pbCA+7H5mik/3Ed2dDeo04ccLcaeJEUwDGy24gSGz1QQFAcuNrnB96bvRBI+AqXgLiwKnLd6E"
        "H630u85GeuxiRATG+3PPKOK50YY/3WvZ54nCoPEmLkfu3UYb/lK6ZaJ7RdF9eBvrRPPaRpfeKDAD"
        "N7Ht7ulSx0ynv86jjpnO6QYAUMdMp793QB0zFTlR3DXep+EEOmpCkwpc6Q0ktmbm3uhhO4+rN2bo"
        "un5Ib6BQH8Jtjg4Wd7B6Q4LV3bu9gUCPs9Dt0V/Xqv5c4imFh6TJeb3jHk24q/B0iW7uAm5yPCkd"
        "kMPbDtBIk9h2SGg2MW2Oiiaa9Ya+g6M0HBE+TQhrinyeTfK+Qv+8AJWGM58uYtW7QqvJVbXUyPca"
        "6axSV4+luj0oq8dS3bfukdRcBtQjqRWYGz2SWtqLHkjVS+H670+p86MJb/nt/P2CDKSaoGF2J8wq"
        "PNwEqS6kiZsg1Tv6dCpthuezmyC14nCrCVJL9zCaILU8HLdJUn1UOU2S6hmh2yXp66bwIziotJwp"
        "PoIJuKM0Ufq+Iz9dlFqvXgSlRXzxcxYjaK2a8cPlud2MGz0j7WawOW3dzEXAXDYjgoC6/FLRee5e"
        "M/cSgvEqLv1xQzh+U71sx3WAj9Fu55kQ88vukQkNAWU7TNCI8LGdti1faLSoaYENHnU7Ao0l5Vv5"
        "PrW+NYtAI82XGifewFOegOMLjUP1gbwFDUtVOzQJGqVqasz+oPV37fBcfzYAaf3TQQxpdxRph2jP"
        "7Q9Eqt2jP/rYM1N/yNG+ktkfZ/QbRduZtdafQVUDyqsN4n0HdmP31Oog8Knpw3ihj/3Ih0HCxF9G"
        "Bntn/jAgqDjcDoUe+35Av4rX+cB7O1p2PkBeS7ysL2RPD3kRZmHbndkQZmHuLI0wA+Mx+rB+D0oE"
        "UTGQ9jnch/VfbTBICKZd3Ie1ann3Ya1adyW3Me25fVhr8Q3XgXQhbZDj64HEcr7M+VW8PsBan3qv"
        "D7DWG39Atd7Xz3Q3sV9pygdU6ze+X1Ct4nM+oFrF88vUXN95fZmP6+Ew+UDq9HAYYebl508i0LzC"
        "vCZIfwmE6rC8hUC0juQIrQPt8Gebgsr3XgizQ/klBNuR/C6I3OFJgmcj8A6LXDyC8Ds8BzEnhPBI"
        "P0H3fGx0BJE8PER0BYJ5WPwEc9CE8jUgpse3x1wyYfcNLG4lPoOFbYyGz4/hPTTeMH8IpBd/N4JQ"
        "65MFYT5SC0Ogj4/wCMT6+AgZ47jXuBJZOOM1xuMsnO1Wa27gQLcqhQOnuFVDbKBb73MnzmvLVnFx"
        "SFusysHJ/G6NB5ERTyoK8nCM/E7g9ug/ogZs9enGaSDWSpZIg6t6AGitBkz1TjwbBNVwohY29U5z"
        "NGBp516kQUgNPgHdFD9Ec54GDTUzrX+MMLeI5e6TU24Rz9047dJUppRqGvNYzdjhTh8l13RYp1VT"
        "doN1ep8G6ix3AeOo02gSdwfmppr73AbqktIeMeo02GGMBuryCAkuHq+BOu2HOxuoUxE1SGehO6dB"
        "ule0ZTdIZ592NkinoQx0GqTTXKerMwF8RVNGg3R6pzMbpLM0tdQgnX1bPyPF34vS6PFgdlcrZfhb"
        "Y7WSyF+618ohfnwGoFwuCGshXz/lRKlkPzzvAMo9/IMntdLPHmh1otLHjcKPASOKNsIA6Qwi5+oH"
        "fiiInQOkQSYJQCkBRpFeCmIgaumOEkIDDxy5U2vpnQFeS+mU6ER0LT0j8KTWUr+iBwHGJPMEG151"
        "Ny3/vOYvpSWoY4i4uvy+AmFWT0nMC7FVF6mTIKAmNeQ9jFrmQ4HYqavfIIDAv5z9PcobXb6iwLPg"
        "+rMI46Euu6JTGNH1SzDyWSlKxnCnJybuxiCnWQKi6k5R+zQxnFl/Toxh+r4bBJdWA6GN0eo9w+Bn"
        "L6To+87lxwZH33eOqOhH8Py+X5gktB/fnn9drichjkDY0RMQlyDs6MEHd84v0eW+E3aGlz8Xwo4+"
        "zINN2fRV54Kwo2siWRB2rCYHRh07SbAx6mioe5SOPbqeJ0Ydvf7ZGHV0+RLlVoi6x8/pG31bDuIH"
        "oo/LdDDo6LEKkDm6wmMMOZoF4S4MOVok4wGnQto+g/MfLYkxBEOO9o5ky8wyptTPCQyq/Z1qBtV+"
        "5Jmgapdu839SL/S9RwazOh6YEraVJUuemaCuVI8UfZV8+ulgUGsLcmeh5ibR0VhULhk26yIv6QK1"
        "lC/JoFobTTqz+yhHjW5KyuBv9UAItDoad2eILqs3rHSSWMn9qn2EWt3NF7HlD+sHjLlqDRMlhpmu"
        "0aF8YZBr9C7j9NZQ44sjWyUb53Qah71TyT0wkTX++A4Yw7rJPS7OXt3k3oQDVzXSoKxqSHC02rMx"
        "ztNXcx/GIWr3uTg5rQ8ujkvVLByR+joycS6qv2YvHIbqcNqCE1BLH9DBsaf3GTjqrHrIwPlmoRsM"
        "Q03DMc+CoaZBmEHVm0TCQbxLJgmSb2cS12uxUgnONH17fJJpdRgujDTdy2acaFo5oTGDVMkiHGiq"
        "GY25ompo40DTnfkGz7TTaOE801oV5+A8s/oWDaDps60G0OzzNGZ3FmmwcKCpT4gbQLNqGYQTzbKS"
        "Xpxo2m++i+WVhFG3O/P/RaqRugHjIgGZNzAMip7ZlC1UZZO28LX2ShgXJpDnnXAuTBtO2ewtDHPN"
        "dyviR0yRFwaU+1EolXX4td5GZR7bT0Eileyk/IvLHswMgWGXpJu1YY8IZxwMn3HdDIWRkcw5MhpG"
        "Qch+Bd3CRqbvQiOqbnY5o2IkC1K4FDbCfnDhz1fT3ca9SiDqvHPvkoIa+bxq9OmEflPJO710ckk5"
        "e4AabVpo4FLJM01KKLOEmMas5iEoP66Vs2tc6bUPwCi9tsaSJfOfNYssXd6sAWS7c7emjmW3XzVr"
        "rMduDRh7N66poru/a9Uo0exvz6oBotcy1dTQHdwoMti59mGp+WCWs0oo5EWlvEs5OOPgXJrvPvy4"
        "9FklE/RKoZIJNsusmWAbuVwywUKlayZoSvMoR4NzrT9RHd7n4iW7ZoJeO1dNBQvCBKiQJ4afbj8c"
        "qamgG/br1FTQax+pqaDPO4C5hqanczdRyPtu4qeYJu+7zYduTQVt9xk1FXT3/MyaCpaW7tel83d9"
        "izR7s2Op83e5i9Th78ws5u/qF1kT3kxp/i6GkTbhmMT8XRsjb2I6TaxOE8OZzc7flTOyJrysiPN3"
        "IY00NfjwPurtNLGna1pP602cxc50ym6kEdriPkfLQMUZuqZTlCP9T8jr0tEy0f24/TF7bbjv0jJS"
        "b642nYoe6bfdbhstM93s/bKjY6fMPr86dirz8f576tipW1FkOsVB0jbIbaNjp0LD+19IWn06V29Y"
        "0QXWM3pjia3hbm8AsdOp1Bs17GRvc6iwZSn3xgd9TuHeoKBLdvf9Tqlbt4l/PWs4Z5P5ulymJuct"
        "+rkLdxM2ga5HZfdsUlyXX+7sYsxaeJq4Tg715ozWrjm7CWb9iCJNGuvSf1ETwRYt3OWuLrLdgZRK"
        "uxG+q0lYDeTuUtUMrkdSXcKv0yOpbhOx9Ehq2dt3j6RW1r0H0mTZn4JUde5n2PXrPbcHUnUkjNMD"
        "qX0+aYLUDtKeJkntFOlqklSF7lg4SpNhr8xNjlLzNawmStPFbmk1PB5polQ9EjybKNU7+sLScNg7"
        "n5GjVKOgZTVRqvXp3LUAlYYj20dUaTji/4xUG463CenAtIwQRMhax4dCPo8ynNxdNUi7GXe9P7vN"
        "kDsKrPbTMDTdLbt4MwLtOoKbEYaXzciFkF62szDCl+1gM+e6dzDXSB12u6DRoGzHn73OfjsCDRb1"
        "52Jo7Cgjul3ojbY1H3d5P7rmTI/reqGuORMfaNipmnHXgdS1ZpKJOVDKEHbfIdS2Zu+0fDliafSz"
        "nP5ApRHtsz84aZy2uwoUSMuX+8OQavfojz2pdmPvy7c/ymhabLefL6S97tKiGk+S1HT1IKLi+WXo"
        "ULHvJIBsi8aaHwYJO+X/ZWSwM//7w3CQuv3GBsX0Afz62CQfaK/ew/OB8BoLzx+wrlp3O5Aw+/Ln"
        "1cTgG8sHbJtl91FtwcZ9Ulu65ttHtUasM/VRbcnAdx/Vqp3UR7UlA599VFtM/+qjWvvZdR5cSHt8"
        "V+yDiAPf/xiYeI0PqLY7f5naq3jTB1Sn7rYBWdef4Wl9QLWKQVdPIB4fUG0xT+MDqrXD3FUPYRYm"
        "4wusLW/E+QBrK6Z5PsBa82GMD6zWP9KdaP564zB784X2KcPAe8zJ3smb7mA7zBl/oc3LWA7BOzwV"
        "MaCpdpi3mweC8DCe/UIUDwPbQbd8nLV8QywP3/7BZt6h3neAMvz8mI8m7D7CsB7q3Y8/YNuTic3D"
        "O0nnPb6Hz38w30sU1+/l0PAoHx0n8KcShJqf+P1PBOtd8yXU/DjY1BS4/7Ap+s8DEsQ46i393MT5"
        "bsu8iUM9OTsRktwOUC8c3/psg3BmW8jKwkGtCz/Xl3xTzfGnTU8m4qfFYU1Z6MOfClGHuBqBsU6D"
        "s5bMnhtwtdTqDaDq04k0KKr9cFcDnRZOJA1earwMdSCpBz94NsioOdznauBQj2zM22CgBsjwbYDP"
        "vtPAaaenGdwRilINuUG6nGoed0UsmWa4FjRziev+WsVtGIedavbFYWdLtsZUVD/P7cw/LXphNGBn"
        "5yMarFNNi3W6J88d1lkax9lgnYqoM3vUnOJjN2Bn0TsN1umNWqzTznP3LSi1B5cKlFqDCDdA92r4"
        "NDj3vs8+s8E5/a47CJH7mSo+jWefwSQPb4LcuRh3mvCjiqXVhPuvz0YTw/UOrM5DjBG4aPEmfAfL"
        "6TRxdjCZbJjFibbY8DamvwPTMk/294+o18YO4Nx4F38kaVno9LezZuu7uA7L0TLS0BXQMVIOON94"
        "FXd5OTpmyoOjmD+4DQkcyB0zFdctSR0rlR0NGo03CefKeI/yGL0h5V3lBONXqeMrvcFDF9ln9kaM"
        "1Nkwa527Jbzq53TPnO1SR7s5DFhWC+qx3xacXeBbrbbVpLxV51pNtKuwi3NLTNFEuJ5D8MexWQsv"
        "NWFtx0lGE9G68KXV5HLu2ajtZo7TJLC6EKiLXT35MkYTtnrH2ySsFi7Yo4lVM5zVY6kW0Oqy1BKQ"
        "cY+ltlXenH3bURTusTTdLF61LgqOrnSTeiy1Iyy3x1JbBHOTpepG2N0Zs7kSpMlSPcLyrCZMrazB"
        "adI0SYGR09SEt0lTWyXPJk0tq8Zo0tRSd9wmTbVXZ3c+q4UIntWkqRa2u12avsJgd6i0HHmoSVP9"
        "OVgQmhZxxc9eEFyrZtZFUFu2Igh4y1YImtPWzUBYLpthQihdfqeHEWhXzZzoCEuvmftMCOllO8wQ"
        "4cvXugQBv2wHm0vXzUxoNKhfCxob6sfZ0FBRtuMvitq2fARzl5TthFEUTSs82KS9rGyysVGnPDy3"
        "GBqE6hoxBI1JdcUWbMZf9rN/8C1v5u/i4bnzwzj1ao8bgcCQdq/ZH5NUO7g/EL3adW5/9LH7rv6Q"
        "o1r3GOnB+vn2x5Y3GOUBHexBcYv1YRSxMhfnw9ChYp+IkGkNYvowSqhYvowNVqdjfRgQ8nfeoHh+"
        "QL899vnAe6uzsj9AXk/BnQ9gVy24pPDFriOKMAMTP7cJZmD+gjaXvkEQj9/ViPbxvUuMafukfpV7"
        "jj6pVcurT2rT9kGtUnexdCDtB06/n3bMLxN/K74xPnBaxc/4wOlX7O+tMaal8QHTduPzAdPa2Ys+"
        "YFrFY37AtP7BnzCt4k/Tcn1slg+Y1t5e/IHTZmDnA6ftzucDp/Wd5X7gtP7LkFM9CkSnKM8eJA9O"
        "zzAq30IIsiP5iqKeQfkiBNzhw0OT7PD0C4bv8PzGgfw44WcPY6UxfbA/Bpudf/ZnEKx/LgT08PkH"
        "NvUO9WDsSlxHBvPIxOfGILaH3efnBjs4NRZE+Li+CsT46PSGLGyvNDw9siHQR/LL2Jw8fHzCXP5x"
        "BZcG8jWuJEoBkmgeEhzuSQHEkOiWnqSBcdU8B2e3atztxJ1q7rNwTGusiiyczXrgxfc8P6loMzUo"
        "rBExfBroVZHPS84f754GZPUUD90GWVXUoak+nZ8NfOf9AM6Lf4rA+TBwTIZSg+DpRo9RahDsr18p"
        "NQhezA0GahzPGQ3w6bcdjNNOIxXWxmlnFQgvTjs9PO46xiXVbJ447VSDs04VNHDWqUYaU1I973Jw"
        "1OlR/ykN1GkMib/hmJvBkQ7qVHRWA3Uq8gOAU0ugPU4DdSp6pME6K02zG6yzmo8d1qnocoN11nun"
        "wTpNGusHTqQWwefpsM6qvjRQZxFI3ECdHepySff3mjR2PMjxXCtp+1tjtfK5/kwPUAYpRgFlMOur"
        "lUP8KIxaOYPAi1p5Hz93fq30h2SrD5WfqgiSgtZSf10yEDMSCQ78AQ8coRMx+yCPGyA9gWsVeeDg"
        "1DMgjaaPgEk8QQxdKWUewXK7lIpQcBq6lp7Am4ooA19qLR03wC7QS+7K9febposbii7nuyHOWjkS"
        "iK2WwxEDqmVtnBBFLeHhhNBpmfM2xEtbHB0IknYuAySjHce4GA418D9aHUfX08XApzHwE6SdnZmY"
        "GOI058HcGNe0fWYMZvq+mzCC5f0ffl8/dpOi7ysSBfoG188oU0NwPa+LsUiLe7gzbYq/78TmfLai"
        "WRB1dKkVePCCy0Hq6IJ5Q9CxwwoEQcca3xB0rJqHQNApinFEvR4l+/KvZ7/Y0oi+KssDTrz0+gVC"
        "R5dKUWaF6PkXxhzLEAHOpfQ4wN0Ycyxdw8KYY9VVQeZY+RFwfmT5DMBJkVUCvRhz9Ho/uVb0ecWP"
        "Wqb4896MOXWBiJEgqA6RvQmRSvVDCaEq9bNXQqxSvSQBWKm+I+FZGcj7ZHOquojGTmhXqi9l8CtL"
        "b4yZsbC8+0rnY6U8is8E5Wdl4KzfnTKQlvJnZlytHz5dp9YPn0G3VKcILktl7JURuZLfKAwIkgcp"
        "8YlQOa8M32WhB05pXsnnxOGuYaJB3eZE4h8650xCz4XZbcHCFwa2SnjClFaJTBjNFnB+YB5bQYsB"
        "Q1hrQvDAyWt73AfHre2/X5yxquEGWC02YOA0TeMJRmoDZzS4mffB/qBJzeBEIeyJJjj6ktkB+Tkg"
        "aaQa3jj3zDmEs85ylV4ccGmIiP82lqafYapZfPKEqaZxn0NgqllU74CpZkGxF6aaSginmoWhTphq"
        "aczszSSrMZ3Ubfa5cKhZpQXBoaYaxplmEQCCM001z8GZZnvzG2ea9vRdONNU46dcSI1gE+FM0z4g"
        "xpmmTp4xcaapS4smzrQ0JSkVdsA41JRQO2FamHl8ZFiLo42zZXdYXiA4UZOr/AnsLFUJ4cIHFEkg"
        "F0avzmz2FsasBqdmis91UtyF4d1zZMQL34w4g14o45WBL3zIla6Owy7hjH6hSkYGwOYzVibCnE7t"
        "4q+dgTCKB/YrzVBhI0H98cJEhKP6iIVM0j3Z6Bn9YYuk7JEajRo469/Bu3RcKiGoW6TPKsln1fdK"
        "2unc/4yScZab/5Rgs83fUdJMK6KJlAiz/IW75paGqsquYWWRuqsmlCX03zWWdF943ZpFuofpnySc"
        "7rX5vOvnM/CsWaN99kgNGL12Uo0V3U8cNUp0q9I9rk/eZxP/MCGR2250ZNm5dgrVfLCtfy6hYFGI"
        "q4SC1Y6SEgqWp22WULCqUrekgi1U6plP2ur2Lr1jlVSwKfIuqaABinRqKuRJ1r3vxcFxLHKvnbem"
        "gu1MnpoKmnb97JoKei3Pmgq6eZxHWPwM7s2jK3626y8frtsPwjUW3mtvVIf597XiHyMkcq8lYAbx"
        "PoN/MpP87+acoV+/i1ukoV/LaYEaLdBx4g/W78oXeeb56zQhnSYme10xO03I8ZpYrad4vO7crSac"
        "Hfb1u4pG+kWW15231YTzJyynxkYatun8IcspuZG2Qd6rjJ6B+n9Jx0J5HO/DDmn9auL9KGP22nD7"
        "tGOkTNNtY7fa2G5/dMyUvUMWyyn2kQa9Ov635dT+SNqYXjT/coqBZG2I2x/UsdM53Vfh1qsM77cl"
        "aXWpzN6gYlW0dm8o0aUO94YPOzW6emOGLQRPb6DQKOZzeqOD6nZzSFDd5N44YKX6Vg/+utIas0l8"
        "W/p1Ma9C39BKi+HR5bkGCD+3CfEks3lObhW6E5ux6keVLqN1Ebx3E8x6x7WbNLac6LeJYI1HJm5y"
        "9xWeZzdhq0KaTcRqqLU/RNSWc30DiHVJGG0KU1sZrR5N7ZTk6NHUDrQ2aWr56alHU9VN6dFUXR1r"
        "9Wiq7+f2yy112/0pMppaUbfdpKlajDt9GKXJRMQobYanL5Ra6IO/tBqW08WpvqNrbmPXwkNNnOo7"
        "unAbpeXwdZfTVFqObJYmTv8KpxdZnONUhbs7Y7Wo8C5OtXOOIDitwhQn5vWomvFqNDiwrZoZdBD2"
        "lrGX2MS2DCC9GyFz2Qw27S1fihBslz18GaF41YyXU9SDem1+B2J82Y77xUfbjoNZatuQl4uu0bbk"
        "7TtbZrsd3/Gz2u0wNhmv32tAg0nVjpdL3BtbinaYNjTSVM1sf/wY7XaWQONQ1c460KhUNeOuwKht"
        "zP54XnSOpZ76ME6p/2Cs/uBkka3UH5F0T164PwxZeOzqjz0WNjD7A45qXcs70Pt6kcPl2KLf113I"
        "VgOKncKnD6OIijd9GDpU7JrWwGzrPuvDIGGFAunDyKBuo/FhNNAbj/thCLB8Zl+4b1EY9AH26tTZ"
        "8gHx6rsA/eKeWIbb20TYncf+gHBLz7Y/gDtJ01bSOklPVdJa/RrufRnSjr36tLbD46NPa4tJpj6t"
        "NUbD3RvcmHbOPq2trz7Q2iJr6AOtdav+A6tVSl+m+Sp+5gdWWxzL/MBqK9L3hdUqdkfksbDH9tdF"
        "G+uwuz7A2uoLygdYq69pfZmPa6K2+WUSrm4V3y8OWdif6f/8AGurHbk+wNrClqCpdRRpS5CLPcxE"
        "fBFgR2p3r1RQtUyI2qHcdWovWO6OzhuWX4TeYbe78L+w3OfKA+t9ty5qc7QuxvJIf2hAOI9s3vf1"
        "DoH/Gd/1MHE9xvXw+RdDaA/1/mocNT8W33WH2h9fcLM0OotwXFcdofY3x8F8LJGe3NUbofYnWzDP"
        "f9h/c+DItxXUwUFvGbIZx7tGpDwXh7pFh1yc5ObZuTi+VfMIzmzLZtcgtfbBGjie7awDN5icr6lH"
        "IboN+trxig5yrd77bHDWgj5WA64qOtwgqkWJNChqxyu4gU59uiENXmpEie87SA1ChLlBxle0zm7g"
        "UEVueC2lBuEeIovBpx3h+358ja6c3B+DMg3tvXDa6WqYGrSzqI+F0041dHDaabSHG6u3c80QnHaW"
        "a59x2mlfy27QTteV7qx3VJawGrSzwKPVoJ3FZXRmlSbiBu1UxB3aWULy2cCdivyYv5M/Hrgz9zPH"
        "umutlFqEzEMN3L2i445/lFqEXGrQTp+OVoN22g8jOM3yM218uqPpTtuo0cSfdX2wsMebmIE/Fm9B"
        "OAAl3gS7M/3VasLtit3qCg6imPEmTjCjbHzSHYU2N9oY0W4b3sba0eK/0RtPNBvF/5JHojhovI2x"
        "o8MsjTbCqWujDX+CuVtt+ONDx0qZZ+QYwNs4Pr06dirbdRBRx07neCInAd4GnchRgL/LCUcRvE99"
        "h0vSHeo0mM2RxBwHvdFDT6W4v4KUOo48wYWOovjrSrd3b0hIMuOn44D6E/bq0T+uipYTv3QrVEL/"
        "+ERpMH+m9qcJdNuq5ibF08V/aTOR73PVN+wiWt/wcpPLVjlgNGGssQPnNgn8Lu/9OR+VdhPNlEu7"
        "keUGo1JpN8KhC7boHH9mnLyiZS3okVQXyu4eGZe66c4IpNTx5h5KVdcDqR1Iac6trU7B6YHU3q45"
        "jdavsG6TpPkmPGAu0p0ll66LQiizCVI7HHKbJLWd/iZIzSfRBKnq/IOPp+4ZanJUl/Lcncm+jgNZ"
        "3OSoHik5o8lRdW+M2eSo+jj2aHLUCvEJwtEyzThDXC3z6zM0Yy3LE7gbHtJt5lkTgXDZDENULpsh"
        "hNF17QUI2eWHWtBUuDSbzRDQyzz1vhW3zXguiPZlM8+F4F+/FkGDQdnOwfwjZTthwESzfy40dJTN"
        "7AGNJOVr0YRGlrJigLtlSl1rJj+/C3WtOTgNQNR+nou5T+p6DhcapMp+ptEfszSBeX+Y0uoM9GFs"
        "0poL68OApDUOzuqPQlaF4fSHHtX2hxtVRufboV6+/YFFv+2iD6OJHdn5MoRoRlHfOYAZ1j5fRgs7"
        "LTQ/DBF6PGqvD+OCikEPTNDbH0YA7ey5P2Bfb0znA+vVcTjoA+CTLKo11e2s0fyAcktqND/wW52e"
        "vD5AWztsfVhdaJLNIX1Wa0Z3d7+cIa3vIRRIS+4adULacW6f1aqdfVjbbbkPa+2q+2EVoMUKwH3Q"
        "oDIAfYC1Htk5X2b5Kv6Aan1oWh9Qra62D6C2Ep7rA6j1fZ8vpLZf+Aupk0oONan1necHUKvPlukD"
        "qFV81gdQJ+VQa1CrhbjZiAgD13kIAXV4EsBd8BIqF2IE12HZhAHNriP5eKAJdlzSA8F2rIb2MMNn"
        "x+gdl4CAZtuhHJxwx7UkFoTx+OzQhUgen/7B4lfCAzigfyb8bQY2/471WMxK+Pzh2URQPw/E90h/"
        "BdsajQ5g8BII89EBkDEw0kd6P6CcUPuTKdi2afj860DIDw8QLRz6upZ4CCe9xpN08G41QgbOdFvO"
        "DhzkqnHHjpVphp9FZRf32TioNZ4GZ7Pl8JAGkDVKiG+DwipqoVdFkxu8zYNZUlPgZ94GWa0eCTVw"
        "qnd6uMFQq9TSAafltr0NWmr0CXcQqSkviBtc1CQbhxowVNG+DQJaRo4G9TReiC7OOs1fSo1ZreUg"
        "vTjrNPyCcdTpZP9poE7XRNg+5M/yJVjU9U/NFBx1+j68cNjZOq3BOv2kYOT0T9HqsE7zAawG6jTa"
        "5OmgztI8dFBnZ3hGA3V5hY+di+Q2UGfxOg3SaXgIuOb/WWTl3gbptIKKH45LuagDOnu6Bug0vIb8"
        "lfzfi9Kocd/vUSvpbD9hUK1cgbO1Vvp77BNQ+oheiNI/yQc87PZThwJd68L0IkoKFue1dEswIwSk"
        "Iwg9Rl41QGZtumMGC3HA6p/g5B8iDeaLtZRGsPIGpBJEPdRSiUKRS+kfuAbzyFI6nyfIBV1LOcoQ"
        "UUt93xQB1iQ3CqarpSMIp/tXqUHlPCDk2uL7QJy1/AcQW22VLhBQdXG6JkRROxtCEDv1ct4QMC03"
        "KUOUTIo+umjUlRdhOLTLF8ZAywXJGPjszMTFaGdZGQaGOC0UwhjWLK3Cwlimjx/t30ftR+eYg+sP"
        "DwxVmqwhOi4RXO/7S4jC6zcGInucg9HHVsMXQo6VZlgQcqxqIkHIse0vCDm6WHb/8hldzgubuOnl"
        "7np3R5fThIhj2SOweVma1MIhji3qDoYc/aoocnSVEB30Cq6fsjDk6PXPwpBjpx4OxhyrE0IYc+yQ"
        "g2DM0ee5B2OOrtTmxJjzrgZXFAzkXz8fIow5VkbjYtDREwvPxaBjxUkz6JQBpf7BCkw9LmWrzUq9"
        "z04QVapHNkkqA413wq9SPEeCs/LBE7iV8bYujC74sZ/o+CsmJxoZCUv54AyMpfxJp2aVnIkzbJY1"
        "Pka6Ni3vfjOmlmqRDLGlPJ3klW9+0zlfXdxiZziuqi2Mk9K5LGUhK4N1efd8wljWePAXvqjNTd9x"
        "7aotn9+EcW7boQIzXMN++cDg1sjqICFBIllBLoJMMjcMZruLwDy2QG+GIazfhXDwWtpIwWmrjoPd"
        "QKxq/CU1p892Ng5Ty4CxcYKaZuHcVAfEbMDSNusXjkh9Nmpw0UqbNmCouQcG4wTUI/lr49izmqQD"
        "Z506zZbggFOPD+NUS6stUibxDzhxIvGDviVVPARDTWOtGYfaK/GTUe5UchmGmm4VDxxqFiM7capp"
        "QdGxcKpZEdKDU029H/4qk9P7nIVTzXaxJ0419UC4J0jGSp8tOqiZ9cFtUM3us3GqWSEKHGq2Qyw4"
        "1FSzBw41dcb4MTepGdxzcKiZs40TqIVZx0e2zRvniucEbWGA7c62ICIVr2zaFqpGBrlQRTPhXC/w"
        "+FR96DqtbqU6KfBC2cyQF6qIMuqFgcCcgi+M/73pjC60YE7xF8tGRsBI9uRTu1C2b8bBMKT5SVEY"
        "yfyTNlQYiaxFGREj2T2pNzLK1/9wOtkLo6Rd9FBlJdEp8f+vsmjRXSJRJ+2rxKDtp86SfZYA75bA"
        "swp/t6ScXkpUos0Otp6SZ/pal0uIWVHAVZNLJ+gkNa/sWq4hpdeeUZMp3Y0f3ifjwDs23WsP1eDR"
        "Z9gAbfTasWrEWML8WXPFEs+tGiaaay4KoHOunVNqbOi1fGtW6DMwAAhdpLKUVNA9uLtKKugEFpgd"
        "WYDwKLGQHgec3qV+KZzlXjq4xIJG5cossaDP+kiJBeusmgpW/4xqKmjw7KihoBP059RQsLxqXEPB"
        "diV3DQXLA881FGxBcWso2E7wqKGgzxClVHOu3QATNG8a10jQfUeuiaCXzlkT4b2Wz6yJ8L6YN7/e"
        "v+taZFFf3o+6f5e5yOtNs9MEd5pw3Jb7dw2MdOPCfYjZacKbZO/fFTLSjODOzHn/LpiR7oEc7ylO"
        "6ymcOeH+XU4jbeLxuvN3dY3+m4zRexWviZZ5ekkbt1OJIzXx43ZHx0JlDO+rjNlqY7nvslptONOI"
        "7VTxSNu47rt0rFTEA8/oWOkc0zMP6ljpGtfrUupY6Z+lqNsG/QdtdMx0PY6zfDvlQtKQZxdhSXfo"
        "THbP3kCis1ravdHDQjdHb8ywlcfsDRS60D7UGx2s4jn3hgTLvH5744Cdz5w9+GskL1GT+LantZqY"
        "t7UlN+Gui7w5mkTXI5tLmhjXwFb/pyitRuY+TWBbPvPbpLQJRxPNGuvrD/ml5Xh5wnMIv7rtfg0q"
        "DcdLLZrT9r2hdzgiR+wrnEeaXH371Is1TGGqiwAXGlTpeLtTLi51LjOklJFrpLPUPe6fv2qdy+5d"
        "6ei4Y8wpdV5YQMpS2xG7TZZqh7qGNkqD4em+4agt5rg/0yhNRujZTZaqbfNsslTX5j6gVn1Hf6DZ"
        "9R3d+eUoDUe2jCZL3+Dn4McvLWc99zRh+gq9whk5TV/hoiZMX91ow1T7hhGWViGKmyCHR9WMj0zu"
        "NjPGRchbBk4eCMRVM+dAHpCyGXdGsLvN+POD038pRiBefanHX/I+3XbI/VFH244ZA37VjFeMyON/"
        "1c46BxoOqna8DBze6FC2swkaLMp2/GFu/0ftdK1ZHtBtUrXD60ADTdHOfIihcadqhzY2DFXtDBFo"
        "WKr6Z/vjadeehdbtj1p6GnRLf6hS98ga/fFJXQF79wclO0DM/ZFIXR5uny9M63pXN6TdZ/UHGit0"
        "d/ujixW3vx+GFA0/pvFhHFGxa1kDM63F48OQoUd+J38YJ9THKPfD4KD12vjDgGDOzfFhFLCnnh/Q"
        "r2J/KQkZmCySD5B/nR7+nQkysDnn/YDzV8zu/0iQgc1n0gdwW4eNPq3fNd/AfDZu2K3v0WRIy+7O"
        "p0Bafy02Ie0zuU9rdZDM1ae1pTTjPq31md3F7oW04u+bPZB4u0PqgCyLj+9NIFC8PtBabXp+mdWr"
        "9+TMD7TWqnDP/YBr8xTdD7g236t8wLW5msYHXOvJenA70xNPdi2MIAuby2cXZGFT5viAa80OcL7g"
        "Wo1kLATXUXQuEUTsKEp3udNVRuXyHITbkZzc/bqJyp8rCL1DOeThCYPnJ0Lw8N7uLveF5YRxPL79"
        "hVAeH2KBYB5G2TPG80i/fccIanfiG85ADU98ui5Y/mAz8VA/MbrHedMJAnx4kMDdqCHU+tbzYJum"
        "kV7AzdNI77oLCbW+6e/EEWx9VxrE1yXUwCmfhJGHaLfUZhPnuXpa3PvMVPO4s4SVaeieBq+t6NfB"
        "Ka33ceeLN+8D11MV8djOBEgDwpZIu0HeZqzJz9TgvocktQXxYo9jsGq0h780WPmdbgOheQRMag6y"
        "+DZgaQv42yDkK/K3Hyi1h+nDhFKDmIFTNjWIKXc1sPf23rk46nRT/kycdRYdLzjrdC0sOOosVmTj"
        "qLM4kcYk1WJEBo46dSkITjo7x75w0umjrdsgXZIuLiadhoO448rIDeG40TWDc4vzI7RTWxBeu4E6"
        "XdT7IS4rv5O71Bg7vxN3WKeL99Nh3bv6pafDuld0/SVzahHLn51QahFLaDVYp5EobpgOpRYxh78r"
        "/m+6+Dyuffvsg5vgNYIVPd4Ej2AWiDcxgh00vIXnCeI44CbcrDP7d/WMPLV+EHXXeIo7fMo2mpAo"
        "bqPTRhSz0fgmI5p94m2Qe7BntAw04FTLQq+7WT86NioPR5HRjTZcF9rYrTZOFC+Nt8EuJ0fHTuU+"
        "0V4d3MY8HM2C4TYW+X7kjp2uwBfNrXcJPQV4n547eqPKO/N+LvWGEl0sus4VLnXkjuhS6h73/Wal"
        "+7NMv73xIakDng4KVqZt9kYCvR9xD//WL6fJfDvLcpugT50/AzAZ6iJdbXSOJsctDmI34a0ugNUE"
        "tt7wNiFtut0kszpF1mziWI9rhNPxXBhtgZV2M/ezmrQ1ITURq8EVs4lVOx4kPZa+66JnnR5LbQnL"
        "PZaqn2Fzj6WWtn73WGqhDNxjqYUx9FBqOfeak2rV7d1DqdVAW02U6ncQaqLU8td3UWpHWU4TpRrl"
        "sHYTpVYY7TRRqm6J2Z382uEZbsI0SSuRw9SCEqgJU13Scxemr/CM7iz29Tz4vigqLWf5TCwNZ15a"
        "TZhq1MNGWFrmKffj5LrN+G5JbjYzzka4Wyb7XwiFy4IDB2Fy2QoNhNFlM+7K/7R7xvVS3/bXlgEB"
        "vSwvwNhUuWwHo31Zl+NcCP5l9v7nQGNB1c66mIukbgcbKcrc+GEEc7N/NjYpL9sB5+jlIbEBDTLl"
        "aSre0JhTHoN6LjQEVe3MJdCQVJ82G9AIVR6i83eh8mZ09b/7o5SV3pv9oenVjkf6A5JWLODZH4a0"
        "2MOQ/uBjVR92f8RRLa3+MGMVGvpDS1ypoR5OtCyCu9UxMLOSMH0I8tT3y3ChiVSJPowRFr7zZWBQ"
        "8d4fRgPz+vGHISB1/Y2DiWV9gL3GB939AfHqJXO3sQiyMGE/1AOyMBlnfCC4FUakD9i2mpmrz2r1"
        "gjynD2vN6S4f1hGa2fNSH9ZauuLePqy1isP5sFKwChCnD2uthLE/rAn0fen2aa0pXOUDra0QJH2g"
        "tdVwOB9obWlX5QOt1YPF8oHW6sUa5wOtNXRnjA+01qNZIh9ore/sJucYmH35/pdxMYC4bj+CLIy3"
        "fKG1OpppfaC1FoUk+kBrPb3H/IHWdgQPonUYzj+grcrwFIlAO5bhQY4FRbuEtRdcKExUjnl5QvWA"
        "5tqRfEJ++LgmyUEYHnYcYUEtoX4vCOWR/oTppkC7uZirPjwEszEvTXh0a00I6/FfxxDZw/tPbE80"
        "PnqG8T0sMOGf/0ftT/ygVELtbxJj+6WRfjGE+lB+Me9K+PgD86qEh4iegTNf86TugYNeoxKegdPd"
        "ElosHOmWfGPgHNdF9Bk4vdVfcBvItqIfOKf10YbgcNZuGw0gW0rZDoV1OeyjozAEug3eqsWFod2x"
        "6M8srENWXSv7opXfSUaDofnjnfzx5DRoaYdsuIFITaX6nAYXLV1Gh4YqYmog8BU1oKe98BycdHYO"
        "AQedVaRoTGN1pcKCg06XRnxx0OnKd1wcdLrg5YGDTpf2p0E6ddmMi5POkqlyA3W6yqHTQJ1+VVoN"
        "1GncEHemlmpyqzOf1AUnrwbqNNbkkQbq9E4yG6izx7sN1OVZXVOLkNUhnSU6nQ3SaZqKvRqke0V7"
        "NUBnyTQaqNNe8NcE70VpjrggdX6pDJKZMqAU8lfutdKfu09A6U/4at0j/unlUhnkGTrQPf2TJ8A9"
        "g0N+gHIH22FfH3cgNkQ3iEAGzG/51KxN3j/ZOQArkhEdHAGkT8BRQLoCmtbS4GA3YEvzuUFGoFK6"
        "gnRkgDGtKcG+FyBdQRWT+l3vCbyoQDf5Lv5fSiu6B+FWI/TvghhrVS0GBFbLACEQTW33mCCI6qp0"
        "H4ictk87IVzamndCjNRXHRsjY1VYpNXzI/6wUWa0wGz8A6Yj+rR//vuJMc5qTGJcswXmwmCWZn2I"
        "Pq6sjUFLszYckFSasOFidKpSNUTXPwvjkOarpIPBR3MzHGyyp9PqiSFH98GYIeRYcfgNIUfXYpch"
        "5FieRww5uvUIIsf2hRlCjl4uGHLsYcDJmB0eEQw5VnYDI46dUGCMOLpYvCBxNMifNkYcy47AGHL0"
        "+o0Rx/IoHAw5WjVjXIw5mj0h2oXwr19PtOsQXO+XqKPo8645JwYdrYRBhEFH39f3UryXl6Gg+yQM"
        "KitMjGylWUbpPtmkqI5d3gmw6ojlm/CrVAclhzC1v0950PdO51dlnwtn7Cs/uKQoLOXRKS7MWKOq"
        "RKCpz5txswy+9mNaJyqXdCJXVuRIp3WlmtJpXvnsI532VfIzUiJXxRJkngzQZc2GsTNeV/I1UnyX"
        "lR5uun4tuy7YE/bUmsX/mTDR04wBnEiCcDDJJH54w8wk/rnklUn8Ehc7lTCMY3uVATPYdtBx7qZe"
        "gJF+fXoOTlgrfnpwrpqVbRymWrlk4gC1kGccmnoXOjgqdVP7EM5Hvc+zcCjanvHCSaiLyo3TTzeM"
        "o0iY5DZB/rDMCGT56/XMCIQEJ5oFgDJMNCuZSDDRLMhdYKLZpueAiWZByxsmmkqeCxNNd3B5wEiz"
        "ByMYaeoyeAbOtCxH5Eg/v1zCkaaaNXCkmZkdHGmWx2LgTLPN3oNDTSORz8ShZtvXDaipZh4calbi"
        "ZOJQezUnX3R3igJkdhCU2qXMDmRGaVkzO9gJ1OKk6ZRwLYrSnNmSO4zovhnc4qT0mU8wDOM9GeJC"
        "FWfztjDkeGZzt/BeshPWxaqT4S6URQdk8r5/olKOxYeeGffCyOE9MvRFspvv14Z2n/oX45ul87r4"
        "ZiujYFgFJIqFzmUnSlOdyuZ5ZobDKO0+Pek8L5ZJBsUwPjqf7YVd4s+Tf6gsw94ugajrj7NKDOry"
        "Zp+SfbYQLnlXJMtzLj1nlmSzQ/GjxJm2WiPMXmrV3NK+8rcbva/FPLkmlH6udWouWTQu1TCq0tY5"
        "1wrPmjt2yHfWsNFr83nWz8z8g2us6IpsSM0S3ankWwNEc9U/VFNDE8rxqlGhwcO7xoOmjVv1fMnS"
        "cHHJBKuXxyUTLDR4lUywINVdQkE3Fu8ooaCXDimhoLubs2SC7YOWTLDFLsAEO7BaI0F3PsepkWDL"
        "LamRYEuMWyPBqh1wjQTduhSpkaDXPgASLCHbrpGgy40o583va+ezaiJYvrRRE0G3HO+qiaDp1PLt"
        "zJ/PIKNGgr6aM7s+vwtbpGl2HPs/v+tcpHtETnD5+V32Io/X9JqQThPHfYrZaWI7C4Hzu0hG2gR7"
        "TexWE84u6/ldQyPtC/GauK0mnJ2741TYyD+J28bovQp7bbQM1EsYf5xyHGlaK/erjI6J8rxuG7P1"
        "vzo7c8ep3ZFvTXr//NitNvzv0jFT3u5fPzp2KuLaGHXsdIr3GNQx03ncp+hY6dyPZx3UsdI53C9L"
        "HSsVb5qXDiq6H7SoN5JYAbLdGz6S6m3pmKGr0N4woavMe3pjg+pOc0BQnfQGAZXN0yO/dsqaTdxb"
        "zTlpMt48DLMJdk3KtHeT5rovSqeJcDtUy01u66rc75xVP6rsJqHtHamJZRX6vXrrznEHNSotR9Y6"
        "Tezq5i7fJmz1juc0CaveCtpNrNq++u2x1M5rNmfllq1o9Fiqi2Buzr91A9Rl9yx1U3owVdmkHkyT"
        "rd2UpnoQ+I4eTe2g8mrS1KKsmzBVf0sTpbrjP7mJUt0q5iZJ1a7df37MWnhGk6TmtOImSa1a4G2S"
        "VP05rpGO0mrEO5yZk1Sjvf2ZY2k2ct01M5WGI547NCeppeu/TZImJRUdkpZBnQyBtQyq3YxwtswF"
        "zAfBbp25mRAKlwmyCaJyGWu9LgLpuhloBly+1IYQXgZhu1/qN9Erwxl3QoQv47J9z1/bkMn9Hwa3"
        "/6uLjQhVO3tjU+2yHcbGizILuesbGLvdDjYtL1/LnTiNrjnLcOeJ1DVnuc+ARp6inUm+34Laz+Ou"
        "m6hrziKuZ4ra5nx590ct3f51JyAEab3kI+X4lCS3Lgcl85Ls/kikWncWsyDtcr/7xrT9YcbedvXH"
        "FsvFPT8MKGoaND6MIlZa8X4YOvTOd38YL9TH4EMZMi0Z98PAkKQdq0cDy472ZQiwWPzzAfyWcv0L"
        "7TVmHHSM+0HqVz5wXf0zsj7A3I7ufyG4fef5Advqv6bVZ3WSn7pkta75XR8RQ9rtjr8Caafr3JiY"
        "lk6f1ZZdrY9qk54+rJNEcCWsLcHd+gBr85XIB1irM8GHD2F33ucDrDUw6KwPsLYk4OMDrZMUcjWt"
        "LTHA/EBrC6/5Mk23YwDjA60tP8H8QGsL2KcPtLbigvsDrdXzdPgDrTXoCNys9D/VgEJfwuBtyA0U"
        "Boxj0+swut11ggkqP4MRcIcZywcU5RLLBeF3KBcouiVOly4IxeOjD9isO9RfCOXhh/eDN2C78yoe"
        "eUCP9PIIxPTwr2HMOxP/dZhXJjzG4/N5w3p/Pxa1PvbHU9T6hN0hlVDrmz6pUeubG4tRieQTZH2k"
        "911FqO0J+Z5BX65TenfeRqmG3X+EU42/cyOZhs65OMXN4YCTWyXr4LhWDQnO6Lg0Ychl7TXfEfGk"
        "IqIOgvWb8mpw107rcwO25uLgBmEtHd5tYFWdA6eBUn26tRv8tJCS2YCmivz9gNQghJ7b4KNl11sN"
        "KpqLYjRYmJzcjwGo73RvA3saNjIWzjoLGdk463rhIj/PS2ChIj+TsI8G6yxERHDYmWbisEtdGafQ"
        "DJx2VvOtM/VMMgbGtNNgkH0atNNQENCx+0MUOBgkF63VoJ2JbgN3KvLXiDsXyW3gTp0lgxq4s/Pv"
        "p4E7XXFPauBOHQRrNXBnMR6d+Z4dDurM8nKfzb854rvZts7vUhfp1nwUhww3QSda2ONN7Cc4xvJ/"
        "rL1pli0trLQ3FY/AC0Q/HM9/Eq67TgZ2vaUmxP3+7yBJUvsRjZD4JmYzyPm/bWKlmtjGQj8xFss4"
        "X0s0sZdB3Uwb1pTzf92PjIHKGdZ2Lm/kelx5zZho6+oRTR2pNqzZK99EO9YtlkQ39IVBxkrbbBb7"
        "6TZ6VSfmkjHTUdV5umTMVL0SvZWyIG4bhtfgR0MPtpKeG9GT8yn3dLzmHMk9z28573GjLSTnMu69"
        "kpPzEzfKouacA6IkVtIjQNdyXuA+bufQfxPptyTv8f30qWxsMEYEXWwxfUkS51gd6sFkoc38LP9b"
        "EtwQjprENTbg0oyGcOwkmDE4rSZpfHcsRhLBSJGxk9jFdsKoSdbeEImeROzdXxlJrgKKe+Vgeisy"
        "J2GKHIGj52CKfYa+czC96/mRgyniEcbIwRS6OXIwha4l59TQSXIijfGcJ0lTbCypq5gaW0yZM0nT"
        "W16+JmmKfbNRkzS9OyYjSVOnGJ9PUzxR/xyL6GqWptgM2S1JUyzpd5amqHSws7NYbIx0SeIU1eaG"
        "JHF64xdqEqfYLeLmpmFKfKHoGjVTymRgGzRT9YvOPdvMVB3/yDYz9mHIHDZDTXrDVtQJ206P8BGG"
        "4tH3Nma6JdtO75VifNgOOYGO/w6N8gBhf86hHEJ4uatys+3wdpf62WvWlmXqMXkrPT6rUc4kbEeP"
        "xUnbsx6QJFl7bmNRjie88nE4PxRe9ambcktxsZpJeanYnEfead3rGTvvqT6ttJp3T/+09cyd90mf"
        "dg/JO6JPu9TtvMlp1dnh4rTl5B0Nxqr1vHe5xSDkwaUgEKa8+JEbEXMenAfMUk960rhu7/bgJrBp"
        "tPuDb8BWlZwHh4CgGzkPXgDvPOQB/bckZnvgPbq91gPkbxjYeED7DX9pDzxHDFFdDxDHdx4v5Pb/"
        "Vb72W70bh7iMVs8G0yjpmjNP6087Z8vT+tM+rRWgfVgg3Mf2PKw/rX5ifqivK2c+wBpRLHM9wPqG"
        "wLzAGnt0sz7A+m5kzQdYYzOrjwdYYyuzP7D6ppEZD6zGeNWXafq9aPXC6lvhZT6wGvc69ChjysB6"
        "1efMwj1ZXliNne4XVN9LfI1BtXkZRajQF/NKgzo3b6xcz2nZWXnnZtmWvKl5Fyctt1KVkJ2vkyG4"
        "OXSNOuO05LNxm/PmTZzSKZTb+krR3DS80imgm5dhNsd0S99KpbBu6nXATvp/WyZFd1vfKcCb/e+L"
        "Yryl1zcEhLW/vsiDU+s+iZ55Ulj7G8UM5+b6Pxp3mmqOX6889nGRIYF6p+iGyXesqmvjoY6yk9wM"
        "/Jemr87jG5reeWZDo97X3L7mLJ7ObpJYC8lY2u6V4LC/B+CaQhMzc6ojmvr1D9cYmjEQwxcNSQD1"
        "xmvtBEWxLG8ngc6b+kQSvMQ7qZvl4lpE149rxbWI3tX7BeJaRG9FEgx0o4HEtwgj2knX3GyYk8fd"
        "DQEZPO5uWMXgcYc9kjp53GHlrSZzmIGm8riDpgmPO2hWAndYYq7MDBSrwyUJ3N0iMSuBu3t5JjPB"
        "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",
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
    "pv_classi_2026":
        "H4sIAHzedmoC/12PwUoEMQyG7/sUvXkJJc04tYXZg3heEFE8l06RsN3psM0i+vRmdAWxlxTyJf+X"
        "nKS8tTMneKip92JmNmuTsnwmM5dab/i0clqkwekdlt19lXMDwuPr9Djto1ZAG3FwI4zR4rUfr33C"
        "H+CWxujAbcBT6Tzrdk61gP/FlCK0GDGgh4GC/08qpTAE65wP3oMbxqDMcxFhw8t86aI3VDbFrJxz"
        "019Oag7fChriDpvI3aAmfx5sSi/CleXD9LwlKTjtNc6hTjhLREhacfcFrHipuioBAAA=",
    "pv_province":
        "H4sIAHzedmoC/2VPy2rEMAy8+1uEkeX49QPd6x7aXkOauF2xrB2StIF8feVAaaEGm2FGmhnPS/3i"
        "MvIA/Jh5KBvDvNTp8+Bacv+x33pCIpjrlssx9I8dplxW3ob+h9r74e0fed/7+4P+Wq1zHvmdx6bd"
        "5KrnhfO6ZSDvrEawpAPYTpDpkjZgPApO3uioLnXhQyo6CkHILoruTFsK2EYxaAups9qol4mLeKaE"
        "zcomEt36FhCQtIPQoMGImtS1LtJbykmkOecJo07ni+CDREMyupN5Ua16er1IbLKnGkXF32PAO9+6"
        "kROH2D5j0Cbt1TcyexuAYgEAAA==",
    "pv_traiettoria":
        "H4sIAHzedmoC/42RsQqDMBRF935FPuAhydPEuBc6FQodnB8xbQOSSGo6+PWNVDtV6XwO3AP3Hsl3"
        "dpoIyPsAL+pDtJC8G+lwiaFLkwvesgwTAXJEUBoLDqf28YuXHISqqm2h4oCo9Y4gAZXiqxBG6ydi"
        "nWODMyYsCVJlfm6HX3xOKIXcFnKC0CXfEXKCQL0IR2LOP0fqe4qWeduzwUYXumVLyeYPMW/Kb9Ou"
        "mLebdfqaMrg54ywLxqSBxuUDrOtCw4M2jJxVYlOobWO+Qda7hgRR6c/KGw3m+bwlAgAA",
    "scenari_fer_elettriche":
        "H4sIAHzedmoC/4WQQQrCMBBF956iBxhkMknTZCtYcSuC61CjDZQMhNjzG7HZtXT9/rz/mRfH7MHF"
        "yDC7iZOHTwzZHe6c3eSb/nxr/ORzTmEYPRCSAKmEOiJcHuNmSiIoq3EnpRA0UbuXakEbqo09Z555"
        "yi4M/J+j0a6zMkJ0tluHxUoWK7w+E9fSRSusNhu0iEmg3qA/M0mx0FNgH316h+V5Ruo1Uo6ENhV9"
        "AasMBmqVAQAA",
    "scenari_industria_vettori":
        "H4sIAHzedmoC/42STW7CMBBG95wiBxih8V/jbkGULSonsBIjWY1iZKaRuA134WJMGqQugol3lt8n"
        "z/PMDJ4oJg+u7yMMrhvPv30gB5fG9y6FuDrGLrQBJEoBSq4Rfsif4cC3zbXa/GOFIEwea4T6DTWA"
        "M7rr2C6FJtD9NtU36nMpxRpaiaUU22ixWJGttLSz1PavT1XrUxgcxUlNoCoIsp3VBTn2s1iSM6/e"
        "+9p9T1K1yLBxWLXJQC4uPzAHDSicT2HvLs8RocxArimtyEA9CqkcNCBerN4hxTYShersKfHlifsy"
        "Sdi6NMxSpjg8bo0uDvPyzH/7AP3i63xxAwAA",
    "scenari_settori":
        "H4sIAHzedmoC/33UTW7CMBAF4H1PwQGsaPxLvIQolbpqRXsBC9Jq1GCjOLDg9AUBqsiMs4zyxfPs"
        "ZyV345iGTuRtF8OASYQYk/gZQtx153MQp9BfXx8jjuGlwRP2nfi8fIHbJBQoKZoU83GPi2+MoUch"
        "VV1XIH7H7vDgm/b1QjVQKoGlhlLpPU8tpfV01RU/XkrFQGY4LDUH6WhQ072v+dHgHAPpaO8U58hk"
        "r5YP9xZ3xzwOGO4nxFSktS5ptiVZ0lxRYIrazp3Dvy7V5YG3XGPeFiyXgVm31Jv0vGWq07JAaXva"
        "z7TX7jFnTBEXzbsS0vpbedcnrr5n7gHK2ky1dXJG24k299s+0SsuR122NIWFoqUZ2MRrNgPYkqUZ"
        "THHd+QxfQ8iHNIwoPtoNe4mUN5Wsb3VPNXM9ja2U4TXZoQNdeVuKQoJbVzm6x9m/O/vrePpi7rr+"
        "AZui5jptBgAA",
    "sorgenti_idro_catasto":
        "H4sIAHzedmoC/52SwWobMRCG734KHRMQRhqNZkbHUJqeWgptz0WphRHYUthd5+Cn76y9gT1ke6gu"
        "Euzq08x8f+vnYv/086UVO0556va1D7rn3+dyqNmeerOnPO0extKu2RxK6+fa8rX2Vh7tzzy81bF2"
        "+3ms41TaVGwAt3fWh30kYfTImDBCskh7RM/ghDA6L7x77vq/+VIu9rkPrZqnt36ahrpi0UyCPQeK"
        "ThclZBdpRsWImHS5EFD87lt+y6Pxphiwn7Sj46nmNq5I3t1RktjptcDoQHBBEfqUmCQmYLyVlVtv"
        "5qGb+zlfH+33udiXl7zudGkUmLUuLQzJi78hvQv6CmPQb3FrdkM+K7SaQzU/+uuwRituaT0BOnQS"
        "CUAEZ3hwHEN00aO+BxvwD8pN7+WqDXKzlxRi5JsYTkIMKTgITjaQX/vxWLv5daitjGUFhoALWRUJ"
        "AXlPUeAG9hyBSMV5IMD/mERYMkBJEBDYhSiUwgxXsKcQ0VEQoa1B5NPlel0TgeSO1P5F5lHohl5u"
        "4oRjEg6sqQLcMrcVV3mXFue+Z/mCieIMJk2+hktDK+rvn9wPhgAAC1pj7xIn0tjrSO/yQLyoVO9V"
        "YNr9BThtI8TRAwAA",
    "terna_long":
        "H4sIAHzedmoC/+Wd629cN5Lov9+/Qh/vBbREPVkkBvMh4zsJAuzMBkiw+Wh05I63AVltSO3sYv76"
        "Jbtlqfv0eUi2Ip/iGQxm19bD9WsW68Vi8d1qt7pb7y4/bO4+3a4uVzc328t3mw/rm7vN9mZ9+cf2"
        "an30Z9r/Rfnf1fX2dn356WazW13ert/vv3e3+bh9e7X6uLqqf7v/08fb7btP/9p/9ffN9e52U//P"
        "+v+sy7+2/31vP65v315tP/z26W63+a186e2H65u37zZvd9ubm/X19Wq3vvz7/TdvLgmALt8cfffl"
        "z9vrzbvN5eUlBQVRFb38x+7izX/Q5fe3m0/Xm3/7z/XN+l+b1cUP9U+r8o33wv61/+t/f4Zg4X+u"
        "7/7nK1BgEEUSa8x+SHCQhDGDkR8SOyX5YXV38c/VrmyM8oc9D2RhjH6A4vDSlP3C7GhteBCFUorK"
        "flaFaELNMClidrttjpYGo0W25AclTS0NSyJCN0AIU0DFSLiy0TKobMU4W4qOrLMOoxiKmiM1G3Y0"
        "wFmzn0XB8RgAQ84ldouONkyeAiruM0X2s0JD26aiMKA4QqFhlIgkjoKabnz203p3W2h+X9/e89Ts"
        "rGwuN0uDU9sGcvmPI13jQV1LlnJ2FKWhDaMoA6lfx3mmZokNMDkCmnI3qXxLJkeGIA0qmyWL0bG7"
        "OVubfbLGftO147VhNDZxq2bna8Mgngo2KINrE3OJBjwVbGBibUqsZpr8KBvxBJBmzpzUbZJzpGxa"
        "AjU2dVuzPV+bKCiOojWaiqRVSvoZxW1N7UjZJGH5b3KbFJytDWfLyuo2bTtaGyZgyX4NQTejJhUg"
        "TyeeMsFDKYlltwHO2d7Bkh+gmdvCWg9QJHCUHdC4wqHmmDw50imFgxKEQvZ7AHK6QBByhCTZUWTQ"
        "PQk9A6pFUHPbo9LFSWVtiFDdFqceooPCIlgcqqfwYNxaQzCRAuVp9+C4uhlGyp6OqnFihWIEi8nv"
        "2fs5kKQSkTo6FAGeIiIT46hum4uOTFxEU8rkNn47XxykaFnclqu7Bk5NUBx1fnZr1n/bbIsst+83"
        "h+XRmImT39aPLg6U6M08HWHHCR6uUQS7TbjPeZDZbx/LGQ4qi6fwDSbMdU3lygL5rY52Vkg4l0Vy"
        "VBztOtTv9lcyKgqrZjAgt9nPEQorg3mqgtgwCqkRstuS9REKKamjNpZu7nZEgjGpqyYJGUZhBEl+"
        "m/KOUcoXc/Tbi3OEAnVV1G8XzjFKcY8Uk9t6wCMK5Qhq2dzWOo9RsGRmngJ/GERJSALRb+fNUXmG"
        "Ur0q4agtqmvCOuExRYjs6ebH8N4XzQboNgzrLkzxMJk9+Uoc56GIJSLzeyXnSNMIY4zEbpOX7tJg"
        "EmCIbpemW6IlVBBXTR0wvkAl5DFIfvfOOQ+wq4hzvIaOGYvnQb89A4+2DTWWxAbUbePqUayGUtYl"
        "J7+9Q101kyhZHPGATvAoUPabFpzhQL2hF916na4bRTIwVb9FtO4CUSwRtadkZ9yNYjHW4OnwiWCK"
        "R8g8DVQYrKlh8T0QDfyeqx+xQIxMRH7ba7p6BpzAHOVvBMMxDrBiip4ufwweP0FOlkzN7zyFjqJB"
        "pjrsIrk9UDvnUWRHg5WApnhIo6dBURPNt2BiSpLdZm/dBTJWBU8n0uMRDmhOmtDRYCIarBSAYs6K"
        "5vc092z3CDETi7lttjtaneJ2IHq65DrYKwQUJRWvY24Pqc4UDU0EXBHJFBFxSsUk+I1De5CoZAno"
        "aCoB2iRS/a+jTA7TFFEdVISeFommvBDkSHXYl1vT3UNEaipu627nQFbSIGJHSDSVOZTgByGpo0NT"
        "gikkFCHQaG5PGHqQGBGyo4ESNBCixpAlFtOh639zfNr4mUZDiediYl8wA92tHKIWl+oMZqAxjAJb"
        "Niss5nbPnJkBtyRHletXh/i43a1v/rV6u/79983VZn2zW7+9WdV3T1bXh1/y+7b+3e3m5mb7x+rw"
        "m/778qfDT108/tShzPN9/ebLH9/dbq62RVhRCzXb/nUA59+3t+9WE0x/uTh5neWvh5/56fli/+PX"
        "t/TyzHjOnEKu9Z+GoekcOgfitqH5DDpygIxNQ8v5SmOosWPDzHrODAHbVu7Yt85S0+2Goe0cmoNS"
        "bBo69TlpsLah8xm0lXi+1mXbhcbzcCxjwJLftAx9Ho9lCZa1aTeN5wFZpnojo2mnhdy31rp/4aZh"
        "aumjTtz4vj4PynIMpNo29VlYplDf17G2qc/iMiUIaX9NrmHqdE5dotHYuDXL59RaEsy2rRnBOXV9"
        "XqbttSbs03Cmtq0Z0Tl1CmTYNjX3URs1XTki6YNObev3QxXl++1u+8f2erc6oHMAUNNF1FI66Eh1"
        "vnS9grSAkkqHnXKApGyLqKx02EvOnVJcRHnlbNU1WNJF1Fg66AIaQNMiCi1d9ERh38G2gGpLFz1b"
        "iMkWUXLpoCtU98Zoi6i8dOGx1lWrHVxCAaYLX5JUSosownTJGUvyIouoxHTRRQO1fVJGA/GcRghZ"
        "FlGS6ZLXk0LOi6jLdNCjxiCGiyjOdNBTqkXIZZRozlJ2hLCfkbqA5O3v2+sD9f6GQ15E1nbCnPMi"
        "0rUlMUsPc+NRui4POS4P2ZaHnJaHnBeH/JB0LQgZl4dMy0PuC79wEUnVCTG1ffb72XydDDNSCsrL"
        "uPB2wo0UcuPc1MsNoe2awcOtt4VhSx82Ye1tWMTdt6Vxx4Vy20K5U69ZSyEvomdrUdTYG6kRB5RF"
        "VPtPsC3Wh8cWUfHvBKgUrPEF7w/VSOuI/0XU/jvgMcTGm9O0HzyHrLqIc4BTcNYgbY+bQesHzyFp"
        "XsSZwDl4Tos4GTgFl/q+VlrE+cDiwHEIXNouuhANgTd+hYp4CLzt+1MkQ9za+Fgt6BsxRYnjiGX7"
        "53q3ey724We+DJtfZVgehghx7NJUA9g94/IoaKS2qc+ns2jc67g1jX0+nkVSEBgbxdMA9fl4Fokh"
        "JZGmqWPfWjMBY9PY1ue9WEe75hvATn3jAoWztL21z2fnxRQyRW06VumZnpdiQIvcNvZ5iJZyUNWx"
        "G2ANYFPfaqcSmDYdrPRM0CurDUbQtpJLH7aQ5raxe2boQUhK2LaSx77RgVFaxz6P0nJRcqbGLfn5"
        "GD2g+vBf49jnc/RA6sEvNl1k6BmkhxrMUtupSM8kPbRQDFrTFq1vkh4VHdex04EGsLkPW61xaumj"
        "tr0WLGFn/7AuX779sF1fF/luH25VLGLJF8j+xVMUG6qrPXuKYkPFtWdPUWyowvbMKYoNFdmeO0Wx"
        "oULbc6coNlRse+4UxYYKbs+dothQ0e35UxQbKr09f4piQwW4Z05RbKgG99wpig3V4Z47RbGhWtwz"
        "pyg2lLQ/d4piQzW5505RbKgu99wpig1Vap49RbGh5O3JUxQbytqePFGwoXRtSczPnaLYUH62IOS4"
        "PGRbHnJaHnJeHPKzpyg2lG0tCLkv/mr6XKx/ul69ZaCLuCHXna5nvIgbct0pc9b4lRJeKHf/eD0I"
        "KeIirsktjTsulNsWyj00Xs/SIrp5loU9MGCvBC2ZFlEJPp2wx0EavzXWH62hNd/GMjBhDwK2Ha8N"
        "TdirwzuW0b3TAZcSocsiasRnowVNaRGV4s6gOQ6Z4yLqxYsD74/aWAJCXkTteHHgOATOiRdRRz4D"
        "TyiL6NU5A4+Nt6bJELiSi0p6/ZGr1W79fnu7WY1hvvn8TZdvtu8r6mq3+eMAaxDAXmtm6KnA//j1"
        "a8l4jEwx5Cg+yUpsPUImHBJkdbpoNIZWx1S/3vsaL71qozuNrHgS9bpqOIYGuWw1r2g4akUAgyS3"
        "qwYjaFQH3ET2umpjZoQiBTS3Cjm216gYfxwd2DJrtDSKVmIRcmv88xgaW8jm1WWjTaGJWzMyaiGn"
        "st45k8G4PnIAjk7J4hhZCbPMqS6Oc1HI6tWCwKgFgRSEvW6z1CrZSVz8z+3NxVWHDgWDZmsgfuyl"
        "4xz01V7j/jNDyF66Yk4kpgacdh8dWAyWnNKBTtJpIK9rd+K826PLk3S1IaIFX9dLF1NIbulkko4d"
        "a6ZN0amE6JZu0iNw8Xfk1JvDlDcH1PE2q1nT0SRd2Xfg1arwJB0E80pHE3R1mnjCFo5zeuGKxfS6"
        "61Cn4KC4g9yAK+8k5cIa2BpIDc64JLitwk4kBUIWEKWB6vkQHLRw6tELFwNKbuD4tDU4TE+Ba6Fd"
        "oReuOIEmOmh64SSoWxc30o0hxAGtgRzujAsCam4gfeuCYQ5ez/MBxrnA67kOTdW5Isw1Zzv0x/aC"
        "XZSvX+y/fji6+qX88xc/fvi4Wd3stpe/dJ9MoNr4Gp9w97Snj/cvF6PoQ5QH4f/x61t8GUaaZmQM"
        "LOqYEScZKcdgT5gwOF9GmGYUCYkd6yrkaUYuWdAT7hvMlzE+gVECPOFS6HwZ0zQj5BDJMaJNImLW"
        "Jw2pmC0jTbpHtGzBiD37Dn0SJJDj/YgyzZg0SHbMSDTNiCV/ch3o0GSggzHFQNHzjiSYhozFe6hr"
        "s5OmIRmCoGtIm4akXAcSeobMT4BMZU9mz5BxGhI1gDmOzGnaS0pOAaJnbYXpcEcEinH1nH48YSGp"
        "ph+eGaedJCcM4jn/gOloh2M9pY+OGfkJjFzySM9lHXoS41MmpvhxHl/6rIufasAXvtnjJ4P8wveY"
        "/GSPX/jWlp/M8cueUfOTanzhC3l+suIvfP3Qj5v48d3t5yctqaBVI9SOhziBUzNqyDmcsCGpZ7iz"
        "Os2XPbfqx/E9Lh5asZhmDfm8IzYNZslzxHJWdvriR5D9+PTH9QMphiVibOhw7Ytf8PYTshytHwVg"
        "wJYK+A9wknMQ9h1sTqTski3EZA1Zz6PViyEKud53OgwHIalvuMGARVIOqtrUvjuBk+y52ZLH0KDk"
        "dy11kh7BxVqhjtZQe+UJHFrkltSy6+kSPendET+No4+rF1PIFDU1dET0CKex5OUcW2oVPYLjEmFm"
        "4YYOvo7gKGik2NDh7BFbfdOmuIOGunuP4OoDqq6PgQDG4Ko9SQ31fjzCSQpSXWE7VwdO2JiAsaHG"
        "pCO4El0mkYYi5278BRrAc4iCEyfLlDVY0obO7b67uvr04dP19uJut7p5d7G6LhLuL31gcJ3ATpyg"
        "ZypbMTaUKJwpaoA0eineXUB91ogUUo5RGgrOOoQcijOxlozN37fXBzQIxZe0VPo7IcOGqtHNgMVW"
        "waxVsNQqWG4U7KyFoxkwbBWMWgXjMbCGMvBjLsi5obOddsjGrAfMcZbL3Xa3205NVrr8+eS7Lt9s"
        "b96tb+72D3yux0YuoRFhyDQ92ezhl/+1+0sm+J81jqlDOzGT6cs+m83V9bYAfPhtc7MqGjD26RDE"
        "wJQW9OGUj+XT3a4KfLEp33B7sxr9gIAtUFyQ9vzy6bbozfpidfF+dTf20UQLsKyPZXuxvvu4urmb"
        "sjn1cRtZ0J767np3u73Yiz9ui+kpAwvbMTXr6+v13g5Xg/Pb5noz9uHU5xll5h/O7fbdp73Hfftu"
        "U37V9fb28P2b+2Dj7ZFA27fv//u/CnD9pov6k/V3XtS/2x+mfo5PjhmKq3rz5hCpXP7w638NfBIT"
        "wxEvf3qelOUfejW6H5um+6lpup9bpvvlhxbosGmrgk1bFWzaqmDTVgWbtirUtFWhpq0KNW1VqGmr"
        "Qk1bFW7aqnDTVoWbtirctFXhpq2KNG1VpGmrIk1bFWnaqkjTVkVHrQoqUz3v4JTbpNxbF+QUWAQg"
        "SZuUeyuTQOrFT+TYJuTe2AjkACqWqEnIg82JAKEQkrJryDhqeqJKsCje1TWOWx4qloeRsFHIveEx"
        "iIFY1axNyIPhUa6zjcy0SciD4anD4bT4EN/aaqN2p45+4CgRpE3Ig93RHBiBuFHIvd0hjUFLvNMm"
        "4sHqJAnVRzaJeG9zSgZCWHalb8OaxoOd2j5Voh3IbUIejI7kErZmaHUlD0aHLWRjtTYZD1ZHrESt"
        "oJGahLy3O/tJnJqSb23No3YnpeIiRTI1CnmwO6Yh50jOjWsetTv1vRBFEmyTcW93GFKIKWfnZbo8"
        "andyDpARzbWy4ngTcNmMIUJxIY1C7s0OSdFWUGsV8qdDvdUCKgi1yXgwOyXcyWK+C5E43h6MmILm"
        "5DqRxPEeYSwBa0jI0ahNyoPVyRJEBFXahLy3OnVad4zWJuPB6jAETUKxScb7WIeDFcvjfEPSRKxT"
        "H50kaxNxb3NYKSCqc1Ud7ydGLdFcFsXcJuS9zSkLaVgfFGsR8j7UqbO90Rhcp8rIU8GOhEjIvk94"
        "cLzZmBPXB52yNQp5sDxRAolqbJPxYHjUyp7MSm0u5L3hsRySanZda8XxNmQ1DaYsvhtacLwbWbQ+"
        "oSDe3aRMmJ36IDxxowt5MDuG9bW8bE0y3ludCCEa+E6xxruUi7UJkckopTYpD1Yn1S5lyjFzm5Q/"
        "fY7OOUffvYI43qTMdUsmKP9x7iZ1ItHiEu8w+VbX8S7lDDGgEhG2Cbm3PCoFMnN2XlOOE/GO1VGC"
        "1ibi/fk5FcScDLVJynuzk7FW6sh3VySOdylbToEiMVibkD8e7rlQMBZVSm1SPiRaXJ9nbZPxYHmo"
        "JJOFkWOjmAfTU1LJYBHEt3kdb1VOYkFryRXbhDxEPJaCljC9ZFttUv70+RYImcRGV/JgebD6kBIz"
        "xJybxPxseSRAjlF9m56JbmWCUF2Ic4XNE8mWBiFJ6LvLFfNktoVZnXe5TrQrI4eirZK4Tcr7dEsh"
        "mOaEvncljXcsS4SQNBGztkl5sD2UgmiJX33f7KHxnmVkCtka1dZ7y1NSSmY0FWsS8970SNmUYoTZ"
        "tauk8b5l3t8jQE7OTc9437LGHETYUpuMDz2EnI0aXcefP/eCJgMo8WuTlJ9rzFD2ZLYSprumHG9d"
        "ZtRgUOxPbhPycKxOFFiAtXiRRjnvjY8EYwVuk/Hnw+X7+qo6ODc9E+3L1cBm8F1Hp/HuZd4/zFVb"
        "etqEPBieepsZQZPvSUM00b2MoXYs5UZX8hDzBDU25+2gNN68nDAwqfpuB6Xx5mVWLu7DBHy3aNNU"
        "9zIHJFNqFPKz2TEhjdwm4yHaCUA5W2pzHT+XeLiOGhL4xpDX9Um9/c8cvfm33nM9/vbDMLM3R99w"
        "+cPq7uKfq92n21X5Q53zBVic/kt5wwGpvgagRJ9jAJrSfhjCbOVHGJffYgyRjGcLAGkcIJYcJ6b5"
        "fv7jG0C1pKE5vdQx9Z/x+edxAKlFkWwz3gE4DoBlB8eXiuP+DPnjhPxcUopsMwYYN6GSik9LZRXm"
        "C5AmAIhKnMzz3cM4vofFLIVE8/UBNO7EhIoGQYL5boHy2Y4DYAoZX+ra9p8BMG5EpR49RpqvG4Zx"
        "IyolzquDg+e7g8cViBPGIDBjBUIZB6h3MSTLjG2ojgNQkpBeqn/rz9gBHRv68/Z6825T0+YU90Oz"
        "56s7QIOiY9GaBDNOH8fVnhIUz/Vi9bU/47PvGJ6f1rvb8vH/vr7dL4BFC8ovdZv6FeR/1B0rLivn"
        "OGO1xyHRNacg2Y2zPRLctKr7fCWXIckl1xnfM1YWHZQ8QijuN7lJcI9E5xRAo7lJbR9F51wMe0zz"
        "TUm6ldlj0SkkITeR2JHklEs4gH7C+EfRKWkgMjd1zEfJMceAiH7KN0eiQ6rDYdVN1vQoeokOwpyr"
        "9nlAcMyp3hwQcXPgcCQ658Az3qMwnqJiLbTWg243h1WPH33C2mDKfmLe0zwJrXz0COgm8O2IH5ME"
        "YU5ucqWu6sdi6Y1idlPj6C4AxMCq6OaU7XHragknIwq70f2u7tQj2pgM3dQ4zgCYg+Q55yI0AYAa"
        "IGU/2Xdn91LWoHHGJ5zdZLArv2CINuPjkW5x+0z++kC0n9p8V/+JJWhJVtwcMD9af6ASOeQZny13"
        "I4dT1ckpB4oztv3do/G/bba1c+/9pipOLnqPc7abXb05lZ40pEjZTWGhI31JtmDWrY04In5KVCJ+"
        "Q3ZTkToVH2vCkthN0ftU+lqXSjGymxpsR3wLxWdlN029J9LXUYJRkvjppTgV3yCozbgdkEaljxBy"
        "2bjqpjx4Gi+Y1NuzFN2o/kOkZrSfW0NueuhO9QagzvtSNyc/J9JHqh2wec5tIB21+e56t9f3WLSG"
        "ecb63s3MPwteWyhU59z0ZEOCx5AhzrjnqVsKf5S8ZLGU/RTBHwSv8+kpqx+n9CC51vayGTdGd7Pv"
        "B8Elh6ji51bJg+CMAaIwu6kWP0oOQSTN2JZ3jwcfJC/5RopzPtcc8J6iudhymfE5Pg4oi9TajJqK"
        "mw6EB8kBA+U5X9YZS05ZS36UeMYtcTTU4sQigSjPWdnHCmIMGqKAH+t4In1tL8tJ59yoPVbOo5iC"
        "JUFyE/R2xC8OiihGN9ay0+Zf/BQCgx/5Tz/+/WsLPOMWBBxwVkQWzCz56ZY7/eCR63uCM+48wIHE"
        "ieqcppQTuTn++Cx5fWUMYcZ1PBwoD2C18fxi00Bf4cDs8ZS7iK4pg58xIJ0GCU4lJiYiN8fcjx89"
        "SShBMTlqDjoxkUgcJKUZn1TCQNaN9ak/TgzipqB3ekDPIZawLbtJRzonTfWMFQH8XNs9+fQ1BpBk"
        "2c/1y1PxJYCi+bn3eio9BVUzPwWzU9UXDWAy58t1NGAzRYLojMdk4MBpmVQnVWxlcuOlTvRdMChL"
        "8tPR8flzZwspq6qfPqbuvZdgmeOML76gTchf339hPwX6jvwaMDKrnx7KjvwSTCBFP61k3cQqpJjm"
        "PN4PdUJ+AcY5689o4RIhGPGc/RbKhPwRWKObksip+BoyU4p+uuEeyn8hR0XwM4/tUfBENOe+CeIh"
        "wU0zUPJTguockQRMBJH8fPJd+QFmPDiDBgJkLHmJ2jcYPlG/6fftza7/JPP7+pXLX9a3H7br6/Wu"
        "yHq1PZTMAMsOjTjeZfPvVY5xsf9ysdt83L59lOivhx/6qU/E8k+9xWchxCGETFDPFyiP98d/e4I0"
        "SACpPlCBnOa9BjioRqkO7Yas4+cN3x5gUImSxlrCKao08yWAYQLIgY1tPLT89tsgDxKUwCwY08wt"
        "EdIgANQ5VVrSk3lbIkzDBAlLfj5xsffbA+AQgMUsZR9HiDN3BjxMQMUSMQLTrAlocBuYkJTYs777"
        "Om8tGl4DLO5MTMf7c749wKApjTlaiJYxztwZDCpRLEYoMESmmZsiHSQQS4HjxOs/334JZBCA6xuq"
        "STHPG2B4BZggpJzyzHcBDi9BbcbgEnKkme/jQYesCSBgnmrV/PYEg4G1Sn2OBUXnHVHQMACrBCoY"
        "Mu8loEF/rLXbusRMaeYJMg1vg6JhoT5bOPPsjAZNEdcMWQ04Rx/G9Md395IX1YegMUoiH5/9o+Ro"
        "xfTkovbiI6c/krw4rvowufoopzwKDpJr+6ayE1PzIDnmxCGq0szTLjr7zLGO9uESicboo25yJLli"
        "IE4zD27wXFmSSMi5IEUfOfqj5CWrDSYydzWHc2Uxq80XJnOvMedzyYuaAxPOXHKQc8mJgsRk5qMO"
        "8ih4VAtF+NnXknskl3ptH2XuQcu5UYz1Wp5qSuLjGOtIcqh9RcKafGTZj5LX4DzC7GPzcz+kdQB2"
        "8UPsoz75KDhHrukQzltT7Fxu1PqBIycf9chHyeu05ZLFydyr8ed2hepLfCxRnXQmHEnOsR7oCzk5"
        "CHyUHHMOGZln7oUeyhXfb3fbP7bXu9V9N0vEIKAw82N8OgtcUrJAUbOXMmnncze2ovAlo0s+PveO"
        "+DGVtM5Q5i4+DogPOVCKjNFH8eVMfAhYYjGLPqKZjvi6f/QTkzlxU2fiUyAGNSd9Q2fiY4ioKTup"
        "a3TFL5m2cAZzkvV1xaeydTWZj1OZrvB7s2kRnZQhO+JLxgCZ594uN+BypT71HNWyk+p1R3ySGuHP"
        "vclswOEKhxyNFH3E+N9dXX368Ol6e/HzbnXz7uK76/r1OoKu5lhkPk4nO0uAKaBgNHZykNA1nUGz"
        "JpSsPgo53U8/1GvkQjOvzD8Yn79vrw+CF5UHsuwjRzyVunzBS//JieBoPPsePuoR3EdM40dicSex"
        "upM4upPY3Emc3EmcvUn8UOjyIzG6k3juPu92c3Oz/WM1OOfirFGUJMRIiV81pD6WshLRlxL1NZBG"
        "DkjplXsxXoyor7EUcqgHqj6B+hpOWQMXncs+ifoaUWMqROyWqKdBtV6nA8Xs0zD0Na5y3UZKTrdR"
        "T0MrUygaJ6977PxyRD2NrpZCskivW596Odvd0wAb61NEMb3uYcXLrVFPY2zZRpCyok+t62uYrS+9"
        "4tRM0PkS9fWjaqB6n96pZeghomIZiF/5xPLl1qin8xZj0EQTDwzPd43OO+c0lX1k4NTB9jXqUjV1"
        "Fp26o54OXsnFMAhmp3ahp7NXKaTE7HMT9bX8ggTV6NW79nQCJw1A9YqBT6KeDmGVGi+AT6vQ1zhM"
        "FjSTeg27exqKiysqe0iS76pWb5+x5OyT6rz9uKR72XfB5GTEfTIuhiEm8p3rnTLVd5cNM5LvOtAp"
        "VLHgORJn9l2APIXiejvrlWcXvXxsd8JUb+Fyzijm29eeQokFMjTynfh1mKheBnCazD64plMmNq/u"
        "aeLCjFO793B+ebpM9Q202lVnvoO9E6gSRAQArznG2I2n5HtHna4SYYhqr3ux+OXDiFlc7Hr52Hzg"
        "wpfX8HzqIpj4PgXsvExIdQ5nTL7Dvv5Lb9F3JjV0FU59Z70DV+Si8yh94Oqc1+Ll1KW65NsIDly2"
        "y8n3OW7/LbwE6BvrxGVRklA2lng9zx2/coheVbC3UEuCgaCWK6LvxepQQXFZSOT7LPSUCXMwVkRR"
        "38eHHSrYX8Qkp/oHvUcFmCAAJUTx3b13ChU5SERgrwrYW1evMTtl4qS+m/hOX5iOgZQF0benGrg2"
        "77vv7dT8abHppjGq736DLpTE/MoDnV++ibTLxFh0L/nu6DtlgkCmr/zQ0ct73qHJDuzb9w5MfPDa"
        "PDY1CYJ8px/fckLEyx/tfOPJES9/oviNJ0q8vCH/VrduX56kYxDc8/yw3u667+e4hcJm1A0bUzds"
        "Ud2oGXWjxtSNWlQ3bkbduDF14xbVTZpRN2lM3aRFddNm1E0bUzdtUd1iM+oWG1O32KK6WTPqZi0u"
        "T2pmeVKLy5ObWZ7c4PJgM1VebLEqii3W3rCZ2hu2WKvCZmpV2GJtB5up7WCLtRBsphaCLdYOsJna"
        "AbaYa2MzuTa2mGtjM7k2tphrYzO5NraYa1MzuTa1mGtTMx1I1GLVgJqpGlCLVQNqMdcmdxnq5sPH"
        "zepmt3272c977E26f7z/nov7mZDfX39aV8g6CDdhYGR5rStqXXGHX9qZBKNRMKIYtI5UFHdgkMfA"
        "MEpIJq81dPUFuRBGuUBCZvW4YDQBhgGQXm10y0uC4RgYmAVmyA5XDHkUrF7xjzEr+QMbXzGWwDnK"
        "a02mf0mjmEbBMAVKWIsw7lZsDCxnDpQjONxhY04sm4YkhOJPDzGOce1Hh9trPb7+kttrLJjKgiWW"
        "EiR/MQeNGfoMEIxYHVpDGsGqw8SzoZrD3TXKVV8hEY3RYUiPo1wYMJdgi/2tl45wWY4hx+Qx2LAx"
        "rKqGHF/rfYiXXK1zI/+31dXmZj+0WnJgSezQdY1lX1ZCeYsA4DCUH1VCoqAJJPrjgjGbEROHsv2i"
        "+Qs1II5ylZRy798aKLM9GI3IJdKQJP5MIYzFhZGqEkbCFkqHj4tVTEaC5DHKgBEqpMCajFoorj1Q"
        "abaQEgLHFuoZj1iaAsfk0bjDGBUVK6iRW8j6H6lKQCiEsYVc6wiqWAtTh/U0GsuMtb44Q0yJWyhY"
        "P64Wa8AIuYn6zBGVBCgrpi3UdI+o9k9TaRvHd49YVA8Wksf0kceoJKScUFooED5SoQXC5LE8mMap"
        "AE1TC0clD1RSogsogZPDjUUjG0uKuQAjbaIqc0SlAYQFW6jJPFKhhlzPVmMLhdyf17e/rXbbzfbi"
        "/15tP3y8Xd9tLtZ/lPjw0+p6c/Gx/NXq/fvN/9u/C5JDhlcbofznluUfVpNLxlyMJHsMFkcMCqcY"
        "SExaOBk6gsKgKVrUForyj1icgzKrtlA2fLo9KcSBlUhaqCs+B5tKBOPxMJq+xntwfdosMXEL9dZn"
        "YEMKIkwO+6R7CrJP56ZcbJoxNdEJ+Qxs01BW23ITLTTP4YbAZg7bKOGrsOtDqNnAYUBCIwURihiK"
        "yRKyFmpyz1jOeiCTs4q0cM70DG6JIeVMsYXK8nOwy3IDSxN1v2dgcwoaU8otnNA9BzsGyOCxyitf"
        "hY1BEoM2cdnmGdwUS0SSCbWFus7TuTFDiJrNmqj7P4+7xC2RtYUS+jO4k4XMxqmJUt9zuDUAAjtc"
        "b/qq/W0WVBJSEzXQ53BzyJqEpYXDpGdwx1QPpz1eDfuq5Y4STOp99RYy66dzpxQyCs2rTHoy0WK1"
        "/8Gr1W79fnu7WfWu+5vPX718s31fH/dc7TZ/HOZGoErQnHk8/RiHO6YYla38C18JUxZzGIYEqlES"
        "TeQCBmEMpj57nkXyeNVnPjBjakaYS25fS1jqAqYk9GMwoEHJKCpEHzh5BAcF6gkYjUes89GzOMbC"
        "YCFloehk0+AIDOScAtT/dWLOxjYNJK7d9VJSBB8wY1sGTErUDyDRCQyNwhSvWXyRZh8hQFGgR5h/"
        "bm8urrpAArEYtKncZD4xzUgYkGs/FJUVyk48zYh1zsQWBDmZDxbiERawHMxKaoA+WHCMpcQzbCWa"
        "8RGc4ci6pFRYSoCWLfvbLz3GLBlSiGZM4iRypgkgIgvAJfFMPnhknMcy1hv8pJh9WAKACSCrFS5V"
        "My8uxyaANNXepwzsZAfpBA9LDqksU1QfWwh12F4Xw6YhxkjJx+5BGWEhwpCNFHzka4DjihatxNGa"
        "S5DjJI4eWZtIJV7TSMDkrwDVszZaVqXsGzLMTkpqOBHpqFBtCCmJTmJ/Zq0PiIGq3xFzGFb38WC9"
        "Gpwnpj7Ms+bRh1MzOMSsgv6qaz08koXrEB8zcHhg0AtUMoVYEjkQf3Hbmy5LrUubsJm/A4O+tSlm"
        "LSCnJOQvbOvjiVmDRUYnPDBS0JUIdbJ8Lq7UXxjaZSlpaCBOLqsFXRZJqYRsoOjvcLpvy4jEEIlV"
        "2d+xQXdpuJizaGjI/o4N+9YGIgWmklyjv8O2Hp46uSUolmBazV+R7U0XxjRArD2D/lpu+han9nYg"
        "Ts1mneexTt/5IWkOwpApKvk73OklwnrZtyQ7kvydiPYBIdUxrFSyHSfVD5oIQGPKIVEEjCk5L7b9"
        "vN3ttlePX9tcXW8v3mw//La5We3q/3dz8fibLv7/5uLN6np7W34nQgqoEJ8yx391c7P9a5XiLxdf"
        "23c59UF9dQPm0z+q8iF9utvtP5cfb8o/crMa/riSQohI8pR5DW4/rbOd0qtcV5+V67JEcKGYhbjo"
        "z+RIizYHLdq3b0eEkhmmtNjNdfNufXO3Ouyj9cXdx8319erD+qaqDUvAhX4uv3y6LZtnffHdxQ+r"
        "u2FzU5QnlMgVl72zjlToEjVgziK23A21u93WyxN3h8+D66X1hHHBGlI30/ZiffdxdXP/oQRJ+qQ5"
        "HO3umvX19Xrvo6tX+m1zvXnaC6zf4AP5X7RyDSo8YgMA",
    "trasporti_alimentazione":
        "H4sIAHzedmoC/3VVy3KbQBC85yv8AWiyDxaWo4zXCikVpCScQ26kQrkoW5Cy5Bx0y7flx7ISeLWz"
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
        "H4sIAHzedmoC/32Sy2rDMBBF9/0Kf4AY9LSkZQjtqqWF9gcEFkE0loofWfjr6za2o1FMVgaf67nH"
        "GrWpScTFmMipc7Hx0+TIxZ1T58kYw+CePofONY5wKig5ptiPbSC8llBL8j34nxuXauOMWbCs4PP3"
        "z23o+5BiIEopEH8TquM7RzNuGaFB2zVyGIdUSAgFjF9LFpopWAUWMVQvLQcjitmonDGQW/lbKsuZ"
        "BqWv8xeY/74ELhHE5Qx0XYzG3QYMXwNfH6/VKbVtsYLZzy4deSI/AdD6PoBMOAWt9oqQjgZp1tCL"
        "77p0CYWMgXrZdsYzFQPM3nFkQoGJnQ7kQYFux3aY+TS/9VX8f7qzx0o11GbZ/240s9PA1aMoEp1v"
        "NrOPLfAu57ug1/wvTrn4XG0DAAA=",
    "geo__aree_cabine_primarie":
        "H4sIAHzedmoC/7W9TY8uu3Em+F+01lyQQQaD9E5jeHYNNDBLQ2ho5NuCMHLLuLpauA3/98lMPlEV"
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
        "fd2qQJ3xg9VsgRouki65llBXC7xA577ydc4wdpx7fVEXUatiXo3Uvel1Rm4yWtvUFbf3EEhtjw38"
        "cAx8ROR8Q/H3o8ZZte/Vanz3h3C+trE2i9M2rKvFhz9kq1RVIkccpe510R3TNTb1UH7ijrW9j4ey"
        "GPdc9iOfUVVT3Tt28C6ils2SZtwbBe+YkXccysSewKLE1NY3p7PIp7S1PcNYne7Y1hYt8h/wxBHl"
        "u4ri7/mWg3uNQmphBVXonewNKxov0/F6JtRN/VA1zdXYVOPNleNckc6ZaM5vM84MbnMw9risjmMQ"
        "Zu2ZCEiFRcNXFZZXe2hvUY5PqNatkSbhm0VKBw7s1AKjdPbdIq0DenxfNC2Uc9JabGIL44kf6gFO"
        "PG5B64pDoLGn1nfdmfhheNHHVYzrUnyZkd5y/sh+InFs77jgUey3thkuP6fWsATia8fYvYZFuld/"
        "o5LqBJYQ5UPbEqrWKLeOv998osar3Pq+4MRofLFVBu3i3tt67mb83D22W82opCj2sVlgp1/rpqBO"
        "OjNMS0dWNmvWRufgCzPamk2jCzr2OR7USddWwcXpKm07sSqr0Pit0yKJ6jbWRVaLc/EhpGtCvIzI"
        "EErHUONpBZIospQKkTELUW/KSqqB1fYVDez6q89pYDp/aj9MATu2c39p2Kk6FnYqCqtqW9c+VJ9w"
        "hHVCxYiX8NAsILPDrAfHVBxrHArti/7+2GDclkkj/bLQ3w+8glUjVbGqapHqz6glyyImd6xgjyXu"
        "LfCB1EZjTx6wdZFAlOIKSqRWfG2/TSCvyoxUrCBarQJRcUxQiSqvrECav8TICqQXrHbFsVCcot4k"
        "upVd5g/yxnYiPxXncRovkmhdyVgV3A7ahA5uopXW1fZVPNQqmhe/pjz25dIInE7H9er0DbiJknzC"
        "od3S0L21I8rmtwUMjTMoLgIpsKLFl0BjcZBqtOWKN0I/hnt7qKyBOgruYtzwsfbfS9QvZGz1oNYo"
        "P8RNhhKNf7EJaUeHY1sM19O0j79WIS5p7DYkyqLXP6BgLHolVqAsR6YuA1b9pHkHhP6kq69wVk4i"
        "DugSRN0KitGL7nvDyojsA6+hGH1t25yuGO2XdGjr0fAScW2fHrSviu5iqfiseOaHFQYqs0DolDMq"
        "0Ae33du1onA/RFfDhi9i4rBkOlFxl0pkQNXwdg7DKQoHXJtKYmDgmUiUw5dU3poPiRdc/RZFbn17"
        "04V+rYGHRa/RsQY89cjz3aZUpYWVmVBZ6uVyvH9JjvdPy/HjSfw0/38W5DhXK3QqmlInFCG6AjhW"
        "iybEcfJu/isdNsx/vgF7AvKtHyuYoNKpju0EKXSP91FLGXzl/bfo0WxdQAp92Nrm4UElvaFgbLxt"
        "03+M1IaJZS3+e8mo1R1XtFr4qCrdwdlApSdj8A9JJXVkP2ZyXB26xCY20r3W1gWkR9P72NM9tpMc"
        "LZt5SY92lMC7I6RoiTu5lGQTXLUHNbK/tkWpDGLgsrY7y+jT2uYGYqy7bBtRZiW+vpdgpFONbRjI"
        "jGxKYIa0QtPi5rZCC1tb2ZNFFq1srUxWJe86lkuurzZxdVeUu4cho68rO6h7e0e8OW1NbGSUOR3C"
        "4VCZoiWzV0u+cfgliaV2iCFpcRN73SaTSNyDXgf8qORyLVsMSeXYS/M3Wb9hHX3LksqtrgcLLTXm"
        "crsvsxFze/LB9szt1NEy81kLqFEaP9jP3b2Y7JuY0I87uQbceop/X+1F4rUGO0174hbQ6DlrzXcm"
        "/ry4cjyIqu1VYh5jIZ7jTWxSJXELQCc6Lk0c22DjxO2GfdAorFW387A2fo74KSGvUYWZJbTbZbvO"
        "jrFxAW5VCn1YgS4h9GEFBpEQF13DtZz+yj4qWx44ROL5By/Zx0CRApmwCgux4Ql7hAJeBy/ZM5R4"
        "6cSWzxsXhi/jCXJj4MFwyGyM3BzJLZfcyMkNotx4Sg2t3Ch7MuAyWy83CxMD8snUzMzS3ITNzd3c"
        "NM7N6NzkVjgIiP08Ge2JeZ87AnKnQe5geHBGpH6L3MWRukMeXCeZlyV3yDw4bzJHT+oTenIf5a6m"
        "zC315MHKfF2pWyzzoOW+ttwtl7vwvmn21EN7Of7V7zN7wl+9mz3/9z/94+/+TzJ2DvPiB3otC2JR"
        "WqL6fijJ10f3FV9P2dymB/+/nMlCY1PfpeRBhR3c7T2r5KCOLXn6LCNQ+w4Qd3uPRR3Utm38Pt81"
        "hYu6x64S19C2wtQXjZV9zzW4ZQ7qVnc0GOgHsezIhIZwg/w0YRZoEF0ndSsAV2zwnTrXtbAQOTuH"
        "7hesbdG0WyprCE2c69pRNu0r7kLd7FX1Xa6fy8WPKZ1EwdhhjdZwvQq1Gpe7tiqoNugjthalwdty"
        "jt1mm07ahS0SdQkN3VdE1+o07TV2lBEvw+nKOKm1xA/uewmHkImbo1unHmXQ1TO7/9pxS2XLmWOG"
        "wFxKE6w38pGCeXXFqG3RzWJ1xpBW0c1zdEYZXsBelPLgcOwWs24OPWNvLkV9y+o4yhF/C2xTNSrl"
        "ZfrFiapBgdKkkZ2XuR+wNl7sFpWkeRbbCvUhRomKC0IqzzHtXm2hHZ97xzVaBW+bWGgFSNq4MiPf"
        "qXXuH6OgaQHnVzI8C/TJQ/URYk3Mxu6OqPZPJ28t3+mIev+rd478uz/+/Kc//O13//a33/3rn/7A"
        "CT2HyfbDGPNsVz7X6FG/nW1tYqRdm3cQNZpUE5l2Y8Q7OGu5EsoODhE22tZqmxpVQ7tC4ecMUf2w"
        "ubNBj7FhXkP627CoF5lhDTPKFhs7229QOqidiZUXNRoadiV7HNQVb6whRXOQj8Da1E2Nb9la2euN"
        "qpn1gqFR/zj25FqCkRvfxvIJ6NOWYKzETd8Zh0a5FrN0H0sHpJsYbfx52ZHnj0VtZbadMkhZpvO8"
        "GHtz41Dd6xojHsS8XCLnvYla/rx4hJ65PvGKDBwaJezN8y8valTTD+peLimC95ubP8X6padYP/kU"
        "a/0+h/B/+/tffv3z83vcR173FkS+83bxybMfqC1SeYLfH2TMjG28Dd/Jn5+k8gxx7pYt8IO5lag8"
        "Q5zbx490LZ+h8gxx7o7/MRqv6dfkY5ka5u7pWrp8B7U+rbtrtpbev4Oqj+vGeDq07sez0mWv7Afv"
        "t6TtbO3RaOoGyUIBKrvczNfYTlSe4X3ugQX26DcwJGcP0mUOhQkMpbLM2VQhzr4wViZJLQGjItmw"
        "BtYc7/shOfcmSVzDrDvrezRirAIWKlEMHKrgHhsfzDxN6Jdtm3UXJowSlcpDCuxpKeo6K+R8jd5M"
        "OyXQNTZy5sNowiHFLCGbu15h1OhAOahYWaWxZSXMYJaRjvUrGyWn2cRYepaGi8wc03oydpaZMSTD"
        "3W70QPyDaVpoK7UR78oZg6VsbqSPMSMOXwHxhIHPbevjsSbJh70fDx2a84NOW77z/Qe5YI9zELxC"
        "SbhVazQDLk5TWplkQ5sPJUVugTqI6s+HljugNrboIDcnxoiGKU5SYkHKoW6u5MuG4F13Uu+WJl+m"
        "0KLonXTXqIlddGxjJ3aoeCedZnXuRpqvtoyP3Tlh4L/gI405LZ5VE9JzsT+3sbcZwtz+McTaoSe2"
        "6PK0BvWTh/LfB3GkuK6FHofiIdKOmq6Uivdd6Are5g2/6E+sZu/ue4lhXrxRFqyWzbC+NfJlh954"
        "XU05YM4X6zeoce50KfPTxNvfx5klHS8pj2/fHPsy90xnmS2lyieoUT3KObhTZ0q1b1Df556WjX+i"
        "6ifGhrldqSXR5dbZnToScXKf4cHmki/ZXPJJm0vK95UzfcbmuiIzF8uNV2DXyo2+iOhDJwkTCAiN"
        "IbaDGfkMxLSHU2ks+Bnzd0iCGBZ5n3WSjKtQdM0SwdUnyc46sIJG1Gyxy11Bkg2lFbhSzUMFGzNJ"
        "pGO76PchcNRaIsyUHDYDiraS8B5QynWR6MRq2RkF5m/RsXLICfiMSNQ0WHiLxorAs0JfVuGDIcOx"
        "boXLajRNxmbnFlWzYfsUrcd7tFU763FRl7tsU2OV1Zg+NtZT2VZJrA82sPbYQo63ru5FIlcYiJ1s"
        "sYGR+rHPK3OP5Z603OuWe+hyb17u+cu9hFYX/IxxucuppDcvc18n2XzQwcakGbo7yMgDCk2UCmkm"
        "Pm2QDQ1fqSqNrHg2ZNPMAccs/ZRzJLqJS0fC0yAWCVTArlTQF9VNBfygfkI7vXHVYKs7syKbGgXt"
        "L2xppiyMZ3ifW6E7UWW+Kb5xtOQTdWTKPqUKvEwbfxCshM7vnTpS6voG9X3udyajxHrwcmMmlMn+"
        "mpexPMP73GXzUCO158vEt3mH7Wr0Q/ePtaL/FeqDntG+pGe0T+oZvf7A+Lfq9usQU1PctEVJQAoh"
        "tChhSPu2mRYXHCugFqhSVlUAM6A0dgFVIb4B1a2LLqXqZAUkwYj+F31Dp7jX1F7wGETEwPhLCEWs"
        "QTW5a2tDixJ7hkM1GOGcLKyK0jNHcZCRGE8ZdYHauOIZGCGLapOBTUHl1W0BKoFEcfePiFrSaIbv"
        "jarP8WPAwSCx34DQQU6Og8ntbaQkr1GBbkFhzMuMvahUGTyxkeS2UxgJi5xQCkV+kRGoE3e0Tr4K"
        "dHPzp9i/9BT7Z8Ms4wfC+Mzurqf1kYc1d8bmjtvUyZs7hJ+cx6mjecIKIbPSTT9Z7MFLFmazyqs7"
        "aUHJ0g81hglrQ8kT+65zGKknrp9ooiBp5FFPSg/0IzIMHjSsXBvDhhuFIAs0C6N4Zxqlfopop9Hv"
        "LE7esIJOmlsewuweBKVwZx4azcOoMBiGkGNf4eYWDuXyxc/hSOaX4Ejmp4to1vyp/MAaGiBjEPBM"
        "HZ6eS9S8viqvxXqo28pqvPJ6sIfasbTMLK9Iy6vX0kK3vCYOFeDFCmf47hkGV44uEGmol/3Tjynw"
        "Izg/dxTgBtCXjQ7kAU5HBvBAp6FAiuD6TBxZ58RjIB9QKvEABBrlODfgV7Qhr8UuRRYXuziVqgVR"
        "McnJtQD8EKETL0BWK5TEurMDyUsgFcgcxWgCHFjpNAGgIgrn0ToOE6XGbiazJuXGTmBsLS5bagBs"
        "o7pCNdelqNIPGumN6vhQMfhQHT4sztoxMF65C0fhosZASa11vWLOXTAuG0oqfoLjm1RK50LK/5Xs"
        "Fanz9chq2Xl5dLoVlVdFKGvYl9CorK3gLhJTrqUlYFQHN5qvsCkVxT0M2VEbal/JQN5ZrYXrLSsu"
        "PsG51KYYGxXH6jBdxBEqajqKxVhcbQYqbVjbObRl0Jf1AnSPSt+wAIATNfDaAZ1idOwojCkW/Xm1"
        "VbDAePWvepKXYuPaOsqVqfa1A25nGv0arsiKgr86NBmXKHagAy26eg4XNumadvB8EjsOGURSp/s3"
        "xC1/QxeirXE2Pgc9VEUVNZXZOhe8PckGwcdCsqEuhdLY7wI1VxLsS0qCfVpJsGMFP0xJaM5X66Ki"
        "peKQl7GMqEJiFCrmqjByqW6+NXEjNRaZVRjqxr8GOL9JiEF1O+KPGWgNhhlIwi2HoYxSc/vRF1kH"
        "MmFLcrnOlZF+R3AUgB/GAMMupbqgGumnttGyeumvC2gxlHtonQswh0xtgDmkxcLEbaTmDMOHDdZS"
        "4JWgIh64e9cNbcEBOoW0DICMcn0T8g4YxlIQj1hKFa0DMvZWCwUfBG+uAm2RkJuk4ysofiN9YmWk"
        "RcJAuM3rrgnlUiQgTvJluOoY74iigg/mal94QayTTgGv0WjEPLBaSsStBjcIBVXqG9wrMbs3Xw59"
        "A0pHb8pOBW5buWHOZJpVqoTlCluq2+VqYK4y5uplropmSmuu3qaa8ID6QUZ0rl+bE6PcFYPAIMQx"
        "WeqYZ8QTHLKM+Bo+ijjFcJWGuBrUAVKKDmqiVsmC4CdXiMPhMdTWnY2noknKV0STlM/DabbyA0Eg"
        "2hAvm4mfansHlVBeUSCvjLdmAipjt+7KfSox6wUTULll7wM1IFSurVgXsbluKIrgeQ31MezYLR2/"
        "Rk7ggvIjqkPRisoOVaJ2lCqRI7zi0/pgDMZdmKHsCDesNyqFaqge6krgkFsfINBiBaKKtqiH69x6"
        "nnby2+PZKEHBXf7Ai1o5wrF/TCi5sGAGofBz3Zot1ehYRd0MjSxeC0MhTtTYd0L5NJRcchpDLSic"
        "I0DQtatk+4jK+Vi7zqjTJR1zv+fOAey5WXUn3ONh++Z10iiGbtSgTuWol/PwGkvh8n1BOqEhj4YJ"
        "ekxvHFIxNkrHAS9Nb+S4BwPrFOS8irf22E53AZ9W6YZIT6i2H2AnqGnd1Va9EOosMDLaIlf89vMc"
        "xEHRnrapQvGiigmiIqvAL2gzclaV/WWN8GW1bubeGCd0f22NRkNHYVan4tcOGMZOEAgoBO8M+N0a"
        "zpxgqXFpGFwcFeqdNDjwsE5O7o3yfhZ8DsKqxljy+h6230QhaSU2uokE5gGIjU5mWrNdRXYBGb9A"
        "UV6Q95GKx8uIi7sQLi62WUMR6CQq+E8TAjoxcBrCp3S22AnxokEQEA7kTRTlIEtf8g/Xz/uHRxk/"
        "EmTJJSmVLx0aBMpSqe6/YgMJZkmaeBEsKdAuHwlpAVIsFqGLgkrSUQZqNynZSeC4VoZUmBvfg6Xu"
        "oSMNzBvhNQRSTCuBp2K1o61X2BIdjcFMUN47xiuAK9mJYDy3kblGk1+59Ham9zi/8vnzyB5S/uTy"
        "55k+5fzZ5xwiZyY548mZVM7PUtaXcsmcoaa8N2fTOUvPuL9uL2wjL4jufWk2qPfIxFBufyKbWGgD"
        "gAY1CkFEb/QIymDoLtPI/gduc9NOuNHbJdkaiyT81g1Oemsch76f/ZgQpjZwrhrBzPS6QdMat1oB"
        "OlkrhH8Pw/dOdfQrAtaxrUPL4lsPxLE514foVylSVo6q9YDA1fep36xkQKwtY9gSfHBbr2AmjZz3"
        "DqfSCMRfcBKMsLa94Y3QherCBRHyYUxoMlR2Vm173htVkFTDWAIcr9jyRkAxF/LNRaXICjQ3Jfy8"
        "TSIfveIyDoYMgS7G6HmYgAEA59sjIwRAw3tajBCsoBICI+Zl0MpRoFBWhgDc8xIeqMNINsrhvCAh"
        "L52WogQ78tglPv+60W8OolFQRKCAx1nrduZ3yg+sslfblTzhCF90sj4r0Lo7RVprB2cnFlwRKO2L"
        "NIcBg4FgyOuE1K2MurhDy0qP5BgLBA8KX+DaKWVbVgOoRmuEhQkiRYyG+ASvF1Q7+fjBRclUrh3q"
        "RGfYTQjzboxKU18dCfXNDUCHBrhXpQTbF7Us1zW/1Bqlfr41yiGQfliO3wVG0+5gNCmazSPmRI5P"
        "0dyqnwQTAugOxr2Y8CtEb1oxuCCo3u8BjyOF7shRPnJAEFyNHi/X1XBje3LWh+gjKVJJjmpSqyOg"
        "KI3Fl03ahRRBpSiUTZKPT8gsKYrLZjRKkfgyt/rB4DC1wNW2KFrcHF7mFmEEDAyxCehVhCc1HDdn"
        "MhUvjHGDd2+F4wHbx2/04T1nbz/nEzlPSdlPzqlSppayv5xT5lz1gQM/cOuMs+dSIJcYuXTJJVEu"
        "tXIJl0vDXHKmQjaXx6nozqX8g0aQaw+5ppFqJbkGk2s7D5pRpkTl+laqmWUaXKrr5XqhUymmWdX1"
        "zfYam28Ua6kC64WwD2pdUG7p3uILCmfRwJpg9gMEZUJ9Odg47IZoFRYDsLJFpb0AKpVad5WO1l0a"
        "feSlmWMSd6LqK6pxadvYFDJMC/rACJlwpQOwmQpjSgeqMaGmFPSREioFKQ6nS+iyxb+MFoakHxka"
        "Ad8WfswaYYcpLCIhImyyiCcGHEiZEdltvQEoF6LiE6bWiGkG9OLQK/OkTpzkIng6QEaH9C/Z+eDb"
        "AiRoN1iLi/DPKmCr1+QZ9h0L5afnr8HYq7SGarClaWyB1Ryaf50objDsWsRrm9b66wxz7q9ova04"
        "Fg5xOrUJTt7GIMy4Dv5RJVLBAQgqcMIn0maLMHtondpWo3m316+tTuuFR2Aumhe7s4gKZ0kPb/gC"
        "G9z8vRAwIbLmeqjPu/Z3q55S6YQgeSR+8dpOzi6Tjg3xikZLqB7bKJPgCgcETyS6jCJ4RvhFouQ6"
        "b/qOxsdQzInTtzBD/LEFjNfeGdIPURuC/0OmVh8St0YROTJ6bO6LCyi1AU1yxE9bQyGUaawh1qbx"
        "2F8Mg9za+VIz5Pr5ZsjV2o/0rEuDz0s/FGep5LMJGdfqRw6c1NeTe4UeHEi5syl1TD04sTJ/F9qp"
        "tELZTzm8fYqEn4Pm5wD7D2D8KXB/DvKfNwTImwfkjQbSpgR5A4O82UHeFyFtofDQbiFvzZC3cchb"
        "PqTdIfJGEmnPibw9Rd7KIm97kXbIyJtpPDTeyJt0ZP088tYfeZuQtKPIQ/ORtFGJToDWk+L70Ocl"
        "bQmTdo/JO83A3KpkQTmqOen4Dg7Nri3MSUmxCsx6XUlabWWXBDodcueB2nwLIqupzZdFWwsGVNnC"
        "bjiFQV4CNMKsg12XgPmmYiWky1WqAmj74XEDh+qI88Zj0avB6HqJ4XaQWSbehZa+rKIp1Y2KuhzO"
        "mkbSSaVW2Vdno4TqvXSjwVjWciqB22INnAxdqv8aua2Q9ryUYGj3twkFDQvaaQqBAxa4GoTgs4qh"
        "gTGdRUEfWqmDxqIdB7UfLghZCeGzXO1I969FaoMBUCvZUTBtCGEX10mokUPpEF2EgwLXm1BJXZUt"
        "ug4lkFwVrBTkKXr1Syl69Tv6NK2f+o9z6+ZqNPqZRJ/KpcojR6iQQWJIiorm2mzwymiE0XY48miA"
        "TTT46AE+46CWzZU6mTm2PMocNflZgFw+o/lkayHQTYYSqld6yBGSjUdxEunv4dqOVpIht6KvaDQY"
        "HkJf0RKw8Yb/HqmIvPaQnnxQoSv1VeK8yGk8PiHOAB8W4bQbin36GjQBnMWhmFp+GjBCe7TQhy0M"
        "jZs4pjrUdI1UuHojwjkasWmAOjyIAy7ZSr+lFbjY8XoNPGWNuPYXrN01VGgB8HxGK+/CVNmez2Rj"
        "tNe4MegOpPRj1oBVH1H4DTU9ETD8HLq5Z0xbOanVHfk0LcDu+S43bIJF4w+qi1q0482d6HNGaseP"
        "LbodzZ3zEZTe1IAIr3GG4Sjv8XQNTtIIKHdSt2I4Qm7AtYY9NBr3JvgxoS1v+9YN6Tx2z9B47JZC"
        "Vwf18GOb/45mnZZ7HeUICa8CnJMREafO17tZzegSfRFl72OsPT6odWduHAuLYzFUJrE1bGOrRN18"
        "cUhc7USL9MHtEOAIG4V4IAI1I3RHPKhQWW9jJ049Xsen/gJZK4KHrgVph4O0G0LeOeGhy0LekSHt"
        "3pB3enjoCpE3kEh7TaR9KfIeFnm7i7wzRt5F46HjBsTGJOdl3skj7/qRBGUf/TS5Tyf3/+S+otyv"
        "lPugcn9V7tpKvWC5xyz1ruWeuNRpl/v3HnyBqdsw9zDe1ahMNxzlK724R/l8L+4pSfOEX3/5+1fB"
        "A0+pDkFZp30k6xGTrfqxAvGgbCR6Sa7CPKo7mWaUKVFXJwKuELi+IGm4M+B54Kd3yBCPhyqpK0hc"
        "iOIs12xQ+FBIM0K/K63xMfnQgE79qETdzwvIVc+S9kEqZxI8Ffa5XpDrEA/6Rqqb5HrMg86T60ep"
        "KpVqXU8aWqrNpZrfg5aYKZS57pnqqblOm6u/uaYseJVSiIrkZomaxajQAULJimxt69qxRlcS32tk"
        "WaDxUEw9P2+qj41LGB1aCLGA0b3gi9R9g3pUiAdMKEJ088oWUqPG7klWt8oyhO7N/Uk8sO3yJbb9"
        "+aq7Q3P9gZlao7iVHZ/0QMFL52MUT9BWId7mid90uDCoR+S5Q98MdTpdcaOexqob6vIR1zW0KOoz"
        "Ogse7OTcps7t79xWz+363AXw6it48irkHojcW5F7NhR6GOnfucckda6kbpjcY5N6d3JP0ENIFm1/"
        "Owk/twt64eB2GhZ+CCGn4eaH0HQaxn4Ieefh8TSU/hB2z0P0eTg/C/3naQIPKQUP6QdpqkKe1lCG"
        "h/8olI4WznPSPiCQM4X2Aen5FoXXHPs+yIhsZCJDLrS9PW9k9/wSocu7hxr1DhzLqf3VAJY5yCxG"
        "kGwaLczTQyKxI1S46CzxqmTRl5WF0Gih926YlogTm6vshkQ9QxT26PYcSxQEbcGu04ms6e3HiLcY"
        "llVJvcI5DnLceBh2xlkVYc3VWZnDHkR+YbB0ZXZm0N5kvJNe7ccQxTp6Xgux7QvCeI+NM6BXqBAP"
        "GGqIO2t/1Tdu86qXkETuNBRFKLWRfxHR+0pjmxe3xJc23P0fnVJgLBKZhY6B6P2MI8dEokCUfgpj"
        "/aDGGd6YRdT7FBHbFiqNT+p2E7VQhH1SURUS792hlGzeFvVRXQ1pfpExKSpuWiciyqGIN6LGt5G+"
        "cdX+XdQo0HSgwsiMd2Z/wYyiR61BGESeoJ4TOStRB0p/44MaCKj1UGF0akIKcUKHi7zIXiITHIIE"
        "96pMhVBk9Rm1zhIdYAOZDb2R3oW0997I/oTbs3e6op4VRQ6wAWdZV14DtBNy7o0KazngUSZ6Yq78"
        "1i8pv5+PZ9VSf1rf4bT4pu6rxTPIoqrQ3T8kUZ/tazOww5APY6EDxWukBcABLcoLrV60T28BySm9"
        "09OX4XACPNbuhZAHFWWQUY3TMaEix6U+HOvDFUivS3618muYX9n8ej88hfTZ5E8sf475002fec4S"
        "HthHzmpytpSzsJzdpZwxZ6Ipv01Z8wMXT/j9k2hIxUgucnLxlIuyXOylAhL7LVGrUhX8fWu0sx0z"
        "xFNoC/NG3UG7a+lRo9emXlgbZxDsmMYbpugX38gfrnhpTaOzTqsg577TvPgK0pC9jpjsYcXVb0YL"
        "A19uZCD25dUEcVZo7s3o1uAmWTyyvmBEWdzcg+qPhH4L5sdsTHUgDdqE7b1r1K36hQ/nskW+JFvk"
        "83ALGdrCF0VLR5jwsKijEKme/RnOteMG9BjX6eCJjaIyXVCerXQAMAopetk90ZQuVoeXo424/x2h"
        "mkYGRh9vbC4uDCVW8Q52t9mjx7kvuHoqX6yt8fcq+o0L8I3Lkl+sp0uYX9jscqfvIH8yD68re4gP"
        "jzZ/3zkrSNlGzmJydpSzrpzNPbDElH0Wp9K8kDYSgz0I77Ua19XhWGolmo9XIPOi0l1ErcyKGkKH"
        "BT3p3qOsT2ZUR/qbASv0RtYdUuAk4hgKPVJE11uNmtYxLYqLBj8cT7yOj8Q88TrK/D6q3vO5r4VB"
        "itHrV88oF/q0gmOgK9qQPF5j6PNSaV9kbn/LVCNmj5SGJjGq+zaWQjUAhj00VOZriVOpi9cGEWMU"
        "d4bQSK/L6cQYN5EYUMF+lRinacuT2okDFRTw1aglvfDrTAQdj+0LImj/1SdDsjUBe/0viiCJ+n4D"
        "0JgwFanVQhVbTZFfTjFAz8hv8cK2DryMHjfV8XOkRY/cVeVwjbVIxLrIU94avEYamUHzMi6NrrOG"
        "uy0WX0cDfqLMeF+au5L4G9zNFkVIU3eCRuF2FTnuGx8X5mo9ibym7fXdHyzaNd14ODA3JDrvGqpx"
        "GyUMPSgY6eV+egjZo8nfV/4U80ebPu+UFeRcI2cw32RGzLhyJpczxJx5PjDalCnnDPyB2aeCIRci"
        "DwKnJhLLD4KKKDtgf9hJ3nXnC8mYJPO8ZpR4YrsXw5ybiyzuUJXwrq0KhZPuDChnqfIllvp5rV6K"
        "fh+A9ifyXMzQOaLF+2yI75TaKIRoDqMd/eyGlhbSKAi5vQUHlXIWDb9GqRRgV6Xf8k+BmEtxUAMM"
        "Lk2A5IYyKJF5ABi/U+z7/sHviSLfDiMMoyWD84+Y2Ga9oOqqUe4GighUaIaB2mTK5AHkgoxK+aoI"
        "VA0KhWCCwbEQCASLTN4McsZ6ownwrihvCBskI7IiU68HX5Tu4h9hlHTr1dz0aR1VCHSlhryUR5xL"
        "2JxIiMOZfzBlsEwcWqEVzO51W5xFr6gd4Vgzip4qpcEKqngi650VFVa0NxOg85XSVYFZXWt0FU3A"
        "W9fSKIIGxGUOCiNEGhslXCE4tGV4DZcXpTygtRncYYk2ygV2dOd4kBPYzHTJDY00OIV8oFtNp2fi"
        "fSEGxfAgwMrkPGk8TLKBrOxDryQmBqBnaiPP50Qx1D09CGMpAWQ2UDlpD9VnjeJqXoLXKOMMkBiV"
        "PcDb5LotbKCcqlMyEiBea3x9460qTonqd4mygwS1bvQJaqBGtjkGPtdoBcivO6RbdEEDkfCq6gyp"
        "dNjcmGUxDFHi0iiFBQ+18I6jEJL2e/sUDuqic8Q75XREKOa18jmi4im+vYEEloNKJRENM3BqjddM"
        "UR49IMyFwptWt0ImLL9cBycFFvkCjROvJiwO4pdQ/oQSgT3r/yY2qlOV0ryct1JOJRrhCDk7BkAY"
        "ZdANM0S1R+SNV5PXzd9fI7+i0dsx6nK8kEZpeCujothuUAYo1kXSaLgTZFC+KjKyZVAerTbPxqCE"
        "VZwk5Wm/RcUHPRO3HikYMQxxdXIqDgC4CnnZIIyM+AcO3SisBIyqiMD4lDCQJxc8JCLkSQsPCQ5p"
        "MsRd43nAMPhSY5j6eV/BYfwkodCv5gFOhInqEkonQf5NqaQobIZQOFMOzIOUXBRsUo52rr2kik6u"
        "Ez3oT6muletlDzpcqu+Z4NWwGplqjKlymWunuSb7oPXmGnKqTeead66lZ2lBeQLRQ7JRmpiU5TDl"
        "6U4PmVFpElWecJUnZ6V5XE8pX2l6WJpKlqed5SlqaTZbnviWJ8mlCXV58t0TVlGKa5RjID3gJaXY"
        "SjkOU8NXcMmRewtno6Il8OA5PsSHypCkBoTmjLrWgkfttix728b6bdiqHOLqCQ0rB87KQba6qyQR"
        "MOUBvCsH+kKdiBCEdUExhhAyWkHASbgmbUENLFH1X4b7SLUUC6AtldImlk5Igk6gXtjeythBGEql"
        "UO5ILcKntn+LStK0u8lJQEVY1+x0bQDQQA7e5TAVRonIUBkjmMN1y7dNQs6v9YaUIVQ7toDUQaXu"
        "wJ+v9xTpBQM3MpEFC5dSa97GjsKlk244K3ERAGiQkd2xskElmWieWJWTvxvgOuK5T6jpVaNcnmgW"
        "coFdRh4N85/Sqe86RO7xG1/y+I3P54iN76pr+3YQpbsFFh9OR+seYdd1KW6BkRcUKqvU9ewb/ZYb"
        "NXe5opLqasIWvdGuP8R5geou8bg70Fmkz9eY/9VsLVCLm2U0a70jFZ6zQmTwtIK3H706HUYOBYq7"
        "QxpR+ADdFaRx/PgNt4MjvT4D7ZZrp3Rg98PN72v70n39fB1mPdnND1Pku+Ms1VtS43ZPUA5VX9sF"
        "fGgK8WAARlwpsuMQPxJ3UFH0VukSOPumLD9F84/a481QdcbHGV/ueKFMJWji1RplooEVzSgsRqmg"
        "Us6ZM2rjsS4AOHuwtVd2COjT2o3SGsVBkThdEvyU83Mn+CkZy4g41UHGPWBaK7sXHjxYqbcrd4yl"
        "PrTc3fbgmcuceKm/L/cN5n7Ed58jebvMbxN5dLCNVD1kqFiphZyh6Oi96CCBw12WsLus3VvnXg63"
        "7bwln8GAE70s1VfnXlnkWoP7mX/MvEWt8lWoaH1LRXboA2ixaG3gTZVbXaX3K2bHJzpHkoPRmwIb"
        "lUR078JOqcKiWEKjvHBBFIkySbECQndQABoWSlTTuTA2hi0UKFSFigoVxX/FCo1tlo5FH+XOqf/Y"
        "RhqK9pnkgVK4y2PbetngFrtdceR4Bkf+pOxw837Fi5JkERBcnFSMDt50RRQ10BfAfKB6g+dKdREF"
        "jZijR0EVIcWpVG+B6zSjYaUoEi9kLClkZ6HadUVnTs529jaiTAXiSSHLTFH/VyanmqEDN1VRKkyd"
        "QqasAvmrLM71xW2gOIl6h2dK+cO0ldzzCtCVSu55db5dowNYBSBsJVqtiryEYyx/MOal5SKsUwmg"
        "RYFaXaneX9+YHicT4tcKZUysfRRXB4CQMndTDlKNZ36l2cT+q09qPL3+pD9M43ngFUh6KYNUE8B8"
        "FKrMVIC+lFE4SR4zxFs3iqH9rBDHAwMgc1Hn0teo3zEveuXS41uIEDbi8IAZLeSke+N41SThr4Uy"
        "6ie6Py/ir7a8uzBl34Nvc22EoTMu1e/q5YU951ViIWinvDhXHz2S6SO8JTTzoNEE3cHXnbed1HrX"
        "HU8iZdyiifYkbnU2xNrUeueCV5Nm+rC+18Vqpq6RUDsaeVPoQ7V513Iq4JmYlw5N0OF8rHkvATrH"
        "0uZe1vzVT524WME+koyoaCpN9RnVu1JXZjb+Y40qllayZVfQXDdqUEyTBpWT/dFFe/JYMZwaZV+/"
        "fVpc7xW3O8cSLxcc5qKEqQvU6qJ2Sk3HwbPpiNsUGeZVyX1dR8ranYL7PCjJGN9gZCZjBVQX1K36"
        "DNHGGrimVHXaDdd8RefQNsqvL6NU/q1Zl0K2G6rJS5k0L9pFF1puBxOhpK+B9AXKy7igjnZv6vhj"
        "gCstSk4MJFCQK6t7ChIF4zp8AIUee8cEFIvrrksRlksfBhWAEgvnTl2rpbdvyL5vyMlcpgb5Oz+U"
        "1blcf9ABcn0h1y1SPSTXWR70m1QVSrWmBw0r1cZyze1Jy0s1wlx7zBTNXCd90F9zXTfVi3Md+kHf"
        "TnXzXI9/0Plz+yC3JZCBNGV+aKM82DOp6ZNbSQ8WlVtf8g1LLVcp55dUys/3yrX2A+uCc/ndwZwJ"
        "XkWvzrF6xkfo9UOHoNisXuWv51gu7IWgJYgovYCUTqrQY5C9MnaiXYHJiyrJ2GZ2r/s5qaxDrC2k"
        "GqmODRoa5fq/j6Urc3kSrl8jRyB+TJO/F9LwGnaXPL96RX1PKlddbhp9rUDxpMLgC5lxU0m1gd5X"
        "SUkVKCaVyl99LLHbAvlP6BB6gc9dH0YaCC6TKEvvPUOj1PUTFuk6SNI2XNMmJ9yF13hRSQe5Etqv"
        "q9DIrS4YyzLZXi9TPxPZL+qgvG/ZVFXOBt8zDOMqRWg89MV1J/SUQutFjXahet3mlkyn3PMCFtgp"
        "LT9VQnJ9Jddtcj0oVZly7SrXxHKt7UHDy7XBXHPMtcxUI8211ydNN9GJU+051bRzrfxBg3/Q9lPL"
        "4MGKSC2O3DrJLZkHqye3kDJjKre7chstt+dy2y+3E+8yKRGz5Tj87xez+KtPem5+pJSt13HPTub7"
        "hel3UjPre3aGEJDruGdb7GyYm0qKzthSY7ZBM+yrMTuDNhjG0jW6wh7n2Du0wUkjVXjsxzjbYIQa"
        "TEoQN1sYTsK+0KEYS2utuofSquBwmZRutfXjl689I1EXld0oYsnXnt1u9t6ybwRn9qp3h5PM7+b4"
        "0t38fNx/jp/sh13OXElRyOH+etirE8dw3k2ZSzqhjjB1gfUKo3msDtWFgHyKqyMUlQSPLAzXCOWp"
        "DIaX3b9WKOu542AXwW5e6VsHlZAKR988cpIEGlfDjJPKecRbgkxCCh9Xeo6eOHn0a7apYxL4Ea6y"
        "Vb1jkl7USPQJBlP3BLoYymt/BCd/CxamjOC0D2gqBSYv2K+TShG11hZ+jZB6wVEI2Hw0sITByJn7"
        "iOdojCA8MZa2bFsUcxAuahtYGc/QQRU+zL0GpTzrtsXrJCf3uMz2ax8Y/myP7cZ7Bm4pXDsBPk4z"
        "KK5ZEwaCBWskMGl13lq4BAW8sTG02/62Sid/ZbKdVMLOxY8VCsv3gQl4y7Y2MCvhFfmnCePhKoZG"
        "Gtg4bXh1Nk7vGteRvP8bwehi2ITW5kKLTLgFcUrov7omtpY42VnhdVEjbexZK8MP4XCrMtiaCyhG"
        "S8K+ENNc2ARycTSslZSkXJg+CN5MROfCPBf8qZLwpFCkyseyTGzm6kuq6nQ86U6OwytB5GJMNNR5"
        "GDkZwATJEm8DjIJBQLZSeeU7x7HgrRzwxVhjdRf7SFhjKjveM40AQ95mmEzdM8zOUCYKKiGjbRrt"
        "bQUbnhwqBdPnqMq+iiwmtW4BsyizVctyz8OH3oBvOw7YyZA7JHLnRe7nyDwiufPkrsPknrkvYVrM"
        "78C0KIla9mW4arflCrlBU13pQa/KdbBcX8t1u0wLTD1dqU8sd5994Gpjt1zu2PumE/DmMMydi6kj"
        "Mnda5g7O3BmaO04VcWnC63gMvmaB2oegbhr/TaPKeQQ6D1Zv/ruo1EUHSpALu/XTePlDbD2Nw+cx"
        "+zS+PwBhX4h9jYosMlJGkLVdCjXdqHD2F048QJ4TN+ioiE2Q6iSejUDwjQgHVaZasqy+S3tKkXZP"
        "Tbs8RwTLCyKjym+9n51qY/g5Um7bWca1nUz3dmQXkfLz3CVG2ZOz9GwCOHgm15JWe0lb2JWN18Wn"
        "bEI838El2+71Ib32jVpf+pGcM9COXfUGF5VzIpG3oPOeE3lSb4j7FWyBciK3/XSVdcTNAbOg1EOD"
        "p0xl3ktqLyoVk+JNKm3kwFGQUrSzWy9WLPcEypPaqPAcIpbbVXQwFoJyG+4up9ZhozewaLK1YK0t"
        "TnDtgrGVQVH3WMKQdZtzUT3kEBdpdJoNhr5Qlq6zfupO9SIqU6+Mtq94ZfTz2e3640AVh0JhZiMN"
        "mt496RfU9YI3fk5AW30dipGPfIxt6hrVEA5XuJlT3ZeV61lfKnuZn3d/rZqUvXxZzxrbOz6pvn8o"
        "rIiblZ3a6alNn9v/ua8g9ys8+CByfwUcVUpXo8NLRMBGDz6T3L+S+2Jyv03uO8r9TA8+qdR/9eDr"
        "ytxiuQct97blnrkHL17q8cu9gw+exNzrmHooc29mag88METXhaUnTsNVJ28vWHW1D9n6gwjIxUUq"
        "WnLhlAuyXOjlAjIXprk4zkX3FNf+I3VBtdKo4VoprhJQqyqEnun2LgRHSWfdEYdFVWZ2YtbtkQRg"
        "Al2nUeHDgtrcqPHTcruI0HSwtQQA4EFuwiu0Vvy3YqmJTNh2N1ASmJz2Asp1yX2C9Wp+SQkcyp0J"
        "3H9jgUjAWVDMGK8FMmpRjwrreCcU5LY3FwOhpSjyGCoDC0BtLVFBtQsjUncHmYhYhhm4gSzuXaXz"
        "UUSTqROZecIvg0xAd6e0C4OoWpRptwEa7v4b8ztWCJBC4QCirivwBa7C8CE4dkrgM4jAVXgfcUkL"
        "d4SDP3RxT7kK3xZVOQlc9oRKb3BjTeNuwgI/GoNEILhHnNsEesws9GtwypLX7v3XlGaAuKSuribw"
        "Ug4C/Lh6H1z+xJaMNWrIVuFrtUk8xAS/xlT8GmFwFPzaqNzXce8DVfNZhQ+XmJMVuGUZVwghTkI2"
        "gpOSWPzBsUClQrgFDYWaRbyoWXkFav1SBer3ddUoP053nGDutuRDIz036FPbP3cTpB6FB+dD5qdI"
        "PRoPzo/cUfLgVMn8L5mrJi/meCj8SItEHgpKHopPskKVp6KWrADmqVgmL6xJi3Dykr+8PDAtJUyr"
        "Dh8KFPNixrzwMa+RfCinTEsv8zLNtKQzL/9MK0XzotKHAtS8hDUvd81KY62gSpp68B1fD1TCm3K0"
        "t2GQ3EKv6kKwZg5CVKgG3VDcX5ow9BbGEuCi4JIJy0N/rSQH0DW8EB6eVeSuV+r/jhjSWq/S4fLY"
        "1ntD1nMsSd+Cl81FynithYzo9ZY+Ry2GoUJws5oFRz21LRxzgZWSSoy/Z/V9ebIgt05uoJLLpL9m"
        "342JDMJJTPPO4XOxVb4ktj7fCXWuH9gI1ax4Dk39WI3MVc5UO00V2SelN1WQU2X6QfF+UNJThT5V"
        "/nND4cGoSA2Q3FjJ7ZrUBMrNpdy0ejDDcpMtNe9SSzA3GguW0Aj+cMFVwD/2YLcmJm5qDKdmc25h"
        "vzn+2ZmEHI1F/cIeHP8PQYI0oPAQfMA5MIokmAd3SH9gKSn3yRlVytQe+F/GKVOm+sCAM2b9ztjZ"
        "HmmQF/QkU8mQC5EHgZMLp1yQpUIvF5C5MM0Fby6kDWsgoC9De7RCAIZIf46qnXXzbG3CpoZaRErC"
        "ggZFZQIOQl2oBMJcRyYo3mMGUIm3uuZcqA+yo0WXGwIh4N2jITyljRdFf6K1AQv+qbjNBBw8O7wP"
        "i2cAq6Hq6svFvi95veNrX3eUMLPxdBgd2w+CAbo9xb4TmHdvr+H1WdSPkk5ieDA/ToCcikFL8B8b"
        "/FuIPA76MDx0AqGdnsXDbsal7gAlmHJIvk4ybkFSMxi3sxVCIF1vkoQ+t3heBnXkXZ5ZQgvDp1Hr"
        "CoOcrow9DpZdycmwSn9NGTIk2y3CRLfZEkF/12zyQOCXSge0f5eT4Yc1tzk0Bs9rrATah1BUpz7W"
        "CC8J4REW8cz7CCdYChITI6Obq3si6bp3BL/yHamfNzxjQo8JuQQXyF7EGUW2IIHVGyIznbqSm6fv"
        "ci/tBWcV8QkkbSrxL89Xpr7oqAHjgNxsfby6sI79g2OL+sMLgmEtGs3T/XgUE5moo+HzmYibCfMZ"
        "eOGEbv3CBBRVnAX7RdJlYb9Ig/PfUoItH5iVEHMHXIOkF3rkj3BdN8D5lSDKut5EYLp+GJhOY9h5"
        "uFtxCozzrjhcoRlGxW2mYOkblbpYD89f5iQafzvUM8Dga6abD21vNgZZz/yeuY80d6fmntfcR5t6"
        "c1PP74OXOPcop97n3FP95NX2qOr6tF+cfehP/vbUN5/78VOff0fAmMrrD30N8V7ahzayWEIed/CQ"
        "PtXnmYhT64exD0SBJ+n+1pGhTRHjh0jLQ1QmjeDk0Z48MpR7ClLRO2H1lo8F+kK8uBJrmoixkwVj"
        "620XaF4EE8jzN/393KiQMaSa+dVb0SsxvQhikW7m+R0zCtXZu18cwqYFayEIWfU8AZIbwyNeDJwN"
        "Bs16rxXMwHDayGBgRG/Dm6BKjGOZGEvzTs9TN5L2SAWhqMaG6L1eIM2AOgSLxtmc4PJkI8+JL6Ye"
        "MKuAY1C37lVwFJSk8qIL5f0Ixpf6EXwH7G75ce64C/Ma8LAEeQ2Y8loJSrugoUCPYztwd4PB105/"
        "/0vzgZPqLQlGBO42AO+GOp+L6r8Wx05A1AY/4UUF7HaLiOJAzKgrwnlX9CipIVu8bWCbDYUdv2IB"
        "qjlUQpwzDKfWSIU3P3g72gkfIxl19+yoc41IxRoCcv5BFbGMCsBQoxlafQHevsaCGve3ttLu2K/n"
        "2Ano1zgSuK2hn0nb3Y0uKFUj6oZlqQTCXoFOQ8deAdGjFn+/KiBeO+0XWgGNGn+rAop1WLwLC12w"
        "el90FwASSyDu6BtUO8HAAwIm+GvbGW8DTK1EKPsBXHX6LR0NSKrxLjkub6P7rI4MXOOP9QkUYX5+"
        "GBq/wJskSe+vb7LWJcnYkIF1Uh2nKN7x0nARQsvHiy/g13QQbD6+N96PIrjjAQ37BPQHDrEQxL7f"
        "/FBWeM6AzQ21wScV+MrUJgBvr9L7r7tFR620WkSMaxXqPgDQ+xAoeO9UcNzfKAcQzTvWQFSAvdeo"
        "ny208eaWasu8xxhD/xfEJAk2v0/EGamlAE64EJLF5WjZOFKR2OcrfhKcd5V0q6UOZKXcHMJ3t2bU"
        "GJhd6hBbnRoNAL66Go8d2F3qOgFeIdy/wO8CfRmw+GXRJrwBGdNYMEECd1kKBDONtuMazgWpo4eC"
        "4RHU9VWCc2PP5wxo7RDthYU+MLHhQ9twKLs5RKU3RWI5VzXql1SN78hXkZVklX+59dEbFyelNW98"
        "kDdJyBsq5M0X8kYNeVOHhYYVg9osPDSL+GZjiVsTirRhRdrcIm+E8dA0I2+wkTfj8Fc2+flDf1Ca"
        "IAE8v6rfrm+Y3HAG8oG6wAieHtl8y6H0SiEq4IBo2orQjnXaGk9+oI4kZXgeSxxa0ZaV3JWIDQm5"
        "2WZB5g9bVvsYSifTTACTJOTnA6QSmUVvyUtdP4p0mGf4cBT5IYIyEJlRvXvvrn6Z5I03rHfKa3vQ"
        "QoWAszgYoFHwAGugzjDbBTm2khapFVef2o7eHnvOwcqXOFj5jh4l7QciID8InFQ25WIsF3lP4jEV"
        "pbnYzUV0Ks5Tyd/V86HsQ40k115yTSfXihINKte2HjWzXIt70PhS7TDTI3ONM9dOc00213pzDflB"
        "m04171xLf9Dov6n93ywFbEOTDy2NzCbJzZcHUyc1i1ILKje2UrssN+Fycy81DXMz8snkxGrZPE0t"
        "2dTmzc3jhic5RpyggysMMvEhn+pQMtEnOljRujoe1IhOjdrcxCaHgved0XiS1VWKUJTe9phbv5ST"
        "il2YPBQKW5xVfQW0ALAw+i5FAxMtcdKh/d5K+aRCKRL6ruE3XOK8w5zjxnXZdKYSf80KkIsHfQOc"
        "S4U+d/gzJVeJf1op9G3IG17kRuqeVkrzds9hpZPEPpbg2m1bgdxUWkMHFHBkgrUPjKUl9DtY9DUS"
        "VF4WwHL5inoWbY2f25F0sxpdxuFUmgFZw9MmPZN6z7g935l/Ah1lgyJojR7aAgov+aw6FDmjrfGe"
        "4dboKyARjZ5Jg8I1+Fl7QrPQFyNn3hoxhuJ50vxUvXU6+chwGULW77kPm0YPBZZRVATPv99ewhIq"
        "207/5fTW6+TVRJJRoy8rUJIbsRvI79JGPMskwf7yoSIpipywuE4i5IRFNn8lkbqAIM2iGg1FCysA"
        "urljEXIwD6BYy6zJ2EYu6uYzkOneoDT1ePVKA1CzsusM36bs+PLaATK50DazUGLCmiAu9ilA1aeo"
        "xtxduYqy3obkLiVP0sSpUfOrhZaxhSDTruqRXZIQFUpv20S56WsiGY7wkdby21/o1/xdkjfLs/HZ"
        "GPTGQNQH1n0rjJm9nGlR9HmJfxvpv5vzU4PNu7qf2jClf8WGKd+R0NP0B1acI9GKUF7zKFgeMXuK"
        "rqWRuIeoXRrhe4gGppHDPMr4EJFMo5d5pDOPiuYR1DTYmsdlH2K4abw3jw1nYWRbWAE14k6D0w+B"
        "7Iegdxog91Lk2j9Or8sz8bKsvYcMvzQb8CFxMMsxfMpHzHMXMS35FCsQZQhOYCLXXKlddZ49+ZBp"
        "mSZlpvmbaapnnhWaZ5Dm2aZ5ZmqexZomvOa5sXkebZ5z+5Cfm+bypmm/Ig7QFFfbFnxh9UPXncdJ"
        "yMmX+gNz3+EqEMYEsr4qdJJC4tHvIkHJTYdSG+SbKahM6TwvSgHKfHG2XixMye9kAArkns5g2iQ0"
        "FdldlCa09A3bwm5eo4so5J12aNZOeRIQMdRi3CEzCNl++dDG6RdRROVSt31J6n4eT+cw339gt9hc"
        "50i1k1yTybWeXEPKtakHzSvV0p40ulT7yzXFVKt80EBzbTXXbDMlONGXc936UQ9/0Nlz/T61BXK7"
        "4ds2xs0eSW2XhQpcdgeizfDdJkKUoU6iTq9gIQMM/XOClA8mXCXTveLqFDLzBZJ3kdksaK2xyNdR"
        "573vwpUbA+nAPwZmNzlpB8CEnfamezET5Ri53IzHg6zuFf1YxVs8kOOuWHcwF3I+oppKyacJRfQK"
        "x7/OEMJ+p0/SYWaUElPwDW3SGhbQa+gbIDJa68mPCR26w+rQlw1UadVBOSxQtjiBy1Hw6RyKY9gv"
        "o4QXJIWSw3qgQrJQDguArVb0WB3CGTrvrPckNIambdtpsdV5ck67hk0BhQ5c6sn5autuUVxDkTlM"
        "buR3LF4jbz5mKJwzZ/cM32uGdRfSl48ftgMdD/q5zNCQ6oooeN5v/GBxQ4Piwp56rER0+KjKQsLN"
        "F7mLjmvPyRDvvufkevDkZRZUAp3CKOZUXFchOxwXj2tL3oo/40e4KsqOEucgneRJ8TpN+jV/U4TD"
        "tar1134uF3LVxXQp9CaQXn3QeuE3Ux5L8j6vBNIvVQLp5x0HNpJM0S9VAl13tt2O8PnS5w8kfUza"
        "5O44OKmexx/ZxHDFlMS8m9wBNuKKViG7vzNTA8wcfYTX9gxmlniN4xaDck9Jv0emuBnBuySaFCZx"
        "Lj47ZS0CLXmOQqLbS4lkkUf13s/lkv2YlgKaQOqajaUpygMaucHR8mJ2csXDOD2sK9ITUGZFv1YL"
        "zIHGmkZzGH1aAxxGdxcy1kvxE2le+hSd0GAJh/YY9Y+Cfiq1T1IqXgApPZH3BJ9cjRzh1xGbcYhv"
        "Dx20MBj5puuexnsSK+3Y9bnWKeZV9+eS0HmbtFOgBAB8xs512aUX1tZL6FF3cUg8sz3v7XQ25KA1"
        "CnOgAt9YqVjbcDcKFqPS/Xh+RK2YgMS/bSvS6MgOdr2XwJnehh+rRsrKFv9Guplu/8fx3sg7v5xK"
        "0nTTSHsAdqQ1WlYd2HGKbfs5CCkKZTrViIq9JeG/TV5rnBeruB8UsIbaaxS/KWVzBWOjeeFzNV7m"
        "glotG5Sc4mMHyU2UkBn5cHcGx0kl7QE7Ptk1jx+jhmcHC8IrI5sPgqOQ8wIOSSPrDs3RjBqeHQbm"
        "fuecVAas40mARcCnn5X2CyVDkVFc6wLyLNmi0Io4W87aSxuPt9/nrJ/prTnoA1B1SOgbvlQC31hm"
        "7aW1xzI4ioXSXAcYPsFZLW/tQb6m4dyakvUGpHQnXU+d35OapPDedFqCwn3TKDVQoRPwwnQmZcC+"
        "2/RbeUlOFsxIXUq59+nBU5V6tVIHWO4re/CrpT64N6WGxlpz1Fk6MVdqlBOvEKahaKEBgplww5eh"
        "gpZV2Cm+ZY1cTlhDeUn+eimYQoRksAcHqLN8l70gdCZGA7V3fzAwcmPkwXBJjZzcIHq1nXIz69kk"
        "S8233NS7KdOpfdDnV+yD/vlevq3+1L/DPPhvf//Lr39+thHO75LeXRkIX/tfov7+oH9rbvTZtUp6"
        "JEJFVklds20CWo0qfUVFqRXKvrKtDVtplPUD6c9UuBQstJy4xl7vZ9wyefavjclK63XNBtkarqYP"
        "Tskqm0FfqNBR/R+gUhrc8BmIut/VUDIVgLJwYY9Ha2Vu6iItrGHoSz7F+RFExArIEzawM8bUzVmG"
        "LbIEsSxSxwvuwiD1tG+BPCgTqGgBlSoR4cgai91I2zYbi/agbyV7kKOzAO3bKKmrANfbCimoDeph"
        "ZffUll43tTVXZlO9dyzcffoIGDW1vqRJnt9A+aMAcxqLHaCKXSCtE2e+yHs5DHeceB4k0ljskcSs"
        "5Dq0HcMeAaX3us2Ck4yvJDmEtW21MdmC2/rOIF5+WBc48k5vV3xZ7Z5vd/0ajYVlRllLte9NNPJ0"
        "ViDEWaEcScOBcYIh+BqtyxaMIvrziVsQjTVxgzXeDSnO66KMkjbHq7EmbY0XSylhxGkcTr4Uh5PP"
        "O7FmT6TUV8udK+L6k9KYn5wGqYMhd0bkjosHJ0fuEMmdJ6mjJXfKOLWTfZ66gHJ30YNnKXNCPTis"
        "cufWgyMsd5qlDrbcGffguEudfLlDMHceKpKDjEIEw9FJ+oc+ydR9mXs6uzeNIK/oU5Aii2d4Xz/y"
        "yyLOwkLPldn1cfDlIVAD8L8i8mFQKA8gPQSb0sBUGsN6CHflobEsipYH3PLgXB7Iewj65QHCNJj4"
        "FHhMYpR5ODOLfOZB0jye+hB6zaK0eUBXPLOH8qs7hhIbhYRdlI3uTew5n92zkFgTR/+qRVUbcyCJ"
        "iPL6kVq46DUcej96xVMGvx+C0WoddMZoXr9fRgr6Ww4PyVh4X495ScbaPZ3rkrGISRlLXiSUxSOX"
        "hjdC/j1xBHeN91a69w0ZZFphc3pkCiLIxurRxBXP8mpkawFEvg36Xu8G0pmKFD5SKtAekNIhBC2B"
        "+LuKY9PSSOyXRP1c0Ed1kUtWxEH+KilADucXK6bkrWHpoBm8E06UpyJ4ZYWIAm4ZXgM2di4lIlwd"
        "K6rnUjzNNfqPpUABMYpauOg2qqlBfuYcVPXhXqsb1dvRUgmCp+UOnhfimBTsWV3wktHtnqH49xDc"
        "SnEPdP2anWYdb547qgsCKpjSM2267ihqJ9V9okpjoZsJ1UaIe0pJ7Xbcucoq372L83v6y6TStyoI"
        "olWjUJVjyRETvOuiuYL9pRLZ8vkS2TV/Gj9Mvx4F8o5KkhRwgmvGHRwF74tMe13D+VykAntwjcil"
        "1ATIyY2InnkbiMNHBhrUvDUii1IH/NZ4h1Qh8xv9lAqyl+OTUcdDk6gJHNcXOk6lGSDyiB+99Wyl"
        "iJgOCFJydekbzlpcLoIDq0ZdUyfUN/Kg6fR876hr6vR2XUJjcTgl6uy6kLLBHzGB1EaukLfm51T1"
        "5r/Gqqmaa8FRzVEDPN6ieeGommSxq7ugF10QKKaRJ3pL84Otx3U1ube3Poi12SsL1/KWzRKnRXh1"
        "URloN0fMiwpJx2JXiV6iPjyDKN7nrsgZp0LD3h3CPq6sI2VqUY1td2FOx37YQ0g1jq+v99qT9brQ"
        "jKfe4TGPEIEHtUK1LZ2oENwl3oXuummNsrAtHxuL3tqaDj1IVIcTJKpDp5fIhJu3mRUl6hsIfo9U"
        "6BmNp0VdQ7w4baEoQOiDneNJ1KV7gQ5H6aDvY+MSekHbZVk0FhpYtNC7VwVQbsDbnre4ux0qa48W"
        "XEdywdJG9wZWggpTEz20u+qvRncMffxGo3vu2PiRkXXvZnQfixmUhq47jP451Bk/LWHgI0b0JnYE"
        "Tw8DjMZCaR30hP3XjKndodYbjQWQvmbzUp1tdz5EH2He3zhy/g7f6Zr0aW8mUORDfeFZTmPuhM7L"
        "UTNy/rYsPhStZvfSk4Mqww2jKBAEL4XUzsMwdvs2ctMOu8ZoDcNbJMd9UDfkZiPhAYk9J+kRDv0f"
        "PVwv+kmuc30JWKl8B7BSGz9Q6ZLiHi/SWlM7IbcpHuyP3FZJzZrUAMpNpdyqSi2wB2stt+xSK/DB"
        "YvTuzvNjkzMxTlMrNjd4c+P4wZDObO7cPFc0HO1RoRXnPuwMQEbHoVDHDUf2x9Io/gU5LczcBZDV"
        "S6MjTd64ZZT0MrzxSXx2omBKI3JAARz3lYnyTp3qxX/xLqHsdPV4x2V5q5lOxHHv8npI5AIu0WM+"
        "WUO0bPW4sNb8x6K3prnC06Nl0Drq9GhhTeu8t7s5qMMdkoFmENMS31Ob3h4ouquRbbsKMfzitZ2T"
        "FAWvA41bA+1usr4Fb8Bk7cFht0nRqNC9SSdxdOwRteQu8P/SkffacqozMPow/Bj5Djri35MwEbqn"
        "B42bZgX3fryizdO5RjQrXGmcVogK9/yImm+bnnLDymj95ti4vc08YyYym2ZIaiO4lDaQr0JoOAe7"
        "Q0ZTfCZNkSqmkV00KCCTAvatIxmIGENr8FVoxP5tjh2uMW/h0Dc9TSkS1cvGhaiQO50mqOtVRjUH"
        "WqYAcqtWX6M9rQLhngIwrXhC0SRugZQ7UkdlwZVEYnIt34VGVJwPvUqPq1BJWfNn2eNyxTPWqChN"
        "0GRk9viEZb7F8165+ezR8BPPo+udua4H+SKHdibQifM3AMlTsol0nM/NkeznI+wyrq8xOheLk0Id"
        "UuE8owcvbyccNWJBPvTURTOgooR09RdNKEusWmt9IbFq/9VnIbrth+FmXlwMron6kT2c285Pdjak"
        "OnHM3HxPLf3cKZA7EB6cDaljIndi5A6P3DmSO1JSp0vuoHlw5uSOn9RHlLuTUs9T7qPK3VkPrq/M"
        "TbY8rku20oP7LXfVZW694UG+EpW2URxPY9Ea0CBnsQ8RIBvsWezt3vzj2jDoG43dvvXeuuPccpcl"
        "NwdrIqq1ez5BI7erOKchH6C3CaKvaJihk5u5IULfoyvnmGG8JmZoHd6GJc4gyMGg+LZWzNvI/V2R"
        "ZyBkkUt/jYFohdyhGIYW/7G4sL627jnJTdzRt29SspkWyChKKFJY2bOSL8cgNqg8uaP34AVBER8r"
        "8vCF/CBb3TdWdREgovyrPpCpuRY5jnDLCum6Y5+7UXJcd5nKC1NY1XfHaza247kW2oaOW1bIQYPc"
        "smMG4rH4tPhlDTeaoNh6hwpRFrloPbGJV4tMFALE7N4I5jaDd40y8hfi7pKt3OH2mZWcgFL8OpH0"
        "MZ9ByZRAYhNZIl6tRkYHvqyTS6y+pfnTDHh/yrYMtEHCTOzyZqDYq1hkjvP2DaS9dnlNW79+7Z6f"
        "HpZLAuUwW/uLQLgrAbliY19SbOy7/Fb1exSbz+SMt4b0RfLQNE9UpByI1rKh9PfvCeNjczcT0uFR"
        "bCbklMJbNwKkfZngfWpP6KW2KdI8Z5M0Vc+5FHZX3WZ4mzuPuC9w6kGlgmnQP3cHPijMD8p1roin"
        "Snuu4OfGQG44eKF/JxvDWwzGVy/D66OUjhTvm0/P25xxrqsrVnz+Nr1uLK4Bigq5W0A0djkhEG3s"
        "FDWvXCPXEISjrUoWa0FFHSX9LBSIkgSQuXmBGXvTvG610S6ginF0ttF38rqRCwQtBiktv3kiMXsq"
        "vK5Q2cBG0QSdjqHgkZwaAgXZlP2aFcT+ej8OLsvuWqzAOEUJKyDH6sAEUSVyz6oRN6moAzJy4tQF"
        "DYEQfoFoZgQ8OrGxXI5S/WiMqPX1aOrEMVJi7ftYocQ2cEm9ZedgD3gsLm7n5DqcrjCMLS6NUOYz"
        "QBwo5we8l9yntSF1nCuVsa9czJLVWrsewmAx5q1B64fpNg+pOWkWT5rvk6YG5WlEDylHbw1Saaz3"
        "R/0wvSlPhcrTptIMqzwXK03busmbB9Vifkm1mN/hMxk/2Q/zmeSsLOV6OYd84KY55025dM7Rc+6f"
        "S4oHqZIKoFRU5VLtQQKm0jKXrLkUziV2LtxTF2Tursxdm7kbNPWY5s7V1BGbO21zB2/uDH5yHKc+"
        "5swdnbuuH9zcuUs8d58/uNpzt3zuws+8/XlgIA8i5AGHPDiRBzLyoEceIMmDKXngJQ/SfBDQ4eBP"
        "Gih6CCplAag8WPVBYOseBMsCZhWuFEqd7BXfxsk9FStTIZvYfV3kLwDOyWxG+V9y778dliC8MM+K"
        "JUeGANW2NnJ6gGuS+dx34YlRtn9vsPAmObWaK2bGvhSocOzH2DfHqJK7Q9ewVdkP4Tya3Oj4Naoq"
        "7FJAFX2Nqdrik4CsWpy9BTCOxYFS3x3ydxd3VHFeWoXziZLrwMoKRbbh/52lUeTSUULowbsLzehR"
        "DCCVUBbdcE2QmMuAKhst2abAluFH1THp7M+2S15Rv75UUb++yz9iP9g/0oDkcCgknGDgRcmVOCyK"
        "WSMj7PJah9467K+iNBR3nApMW92C2Uh1bhDiRjdp4DJT3KOh1GbQxX/5sDcXSJteGU0ZHCgbN/Iq"
        "N0Wpv5A57UygUWgbsDeUjHNcMh9KEqHC9xP1v5eFvS+5wpBqsW7o0BywOBKvYHxG9klDdMmopVFD"
        "GgUFNZoUhyyIr0U6SpnpCaHsek465yavpfLHajEtf0N6UwrWVYz04/5aey7w5VshX4H6aWpKJVtf"
        "i1c4k74INl2jrBH1GutBKqvjUbEvEMBPDCmhb2X19qpxMtCEzNRx6F9M8k6cc8oinRWMnqoUBd7B"
        "ZqTJAlygsW4JztfodRZICiFNCde33TKj8CokcfvQslzhtGashvLdf38VD4IlE0KpvHoQbbkYfBCZ"
        "qXjNRfGD2M5FfK4OpKpDrmY8qCSp+tIdWmtSIGdCAaIsc3VRSOoair6MPLIKa8OollXdSd4a1cBg"
        "rHD9CR4AxWJR1mJCEzR/hBTjQiaDcSaDOX/hXGxxXBej3ADHdYnE9iKdeu8Jx+itgWuRGikQepUz"
        "1abj2pGy5mKTFXqcDmHgdVhyvDUdxc5GbqQ236gkmiAouBQCAfSxyNyZBqAUIQNkK1uD6rHaUkCt"
        "LK5ZAMSGcCYiZA0JKzSfMFY5BVga5IF2iI/bAwSjL9pfo4JWOj1AnDDVc3RAehmVWXWpDp9CWSku"
        "VjhqK9lhqgOwxOV2D/gQD1B9Fc4d6DjG0dXhyEHCJT8OLcMzYMspW0Zd5aMLvU+MuGMDuk7nfKEG"
        "dJ14tgtEUn1QVsfwPG5Oj9nodvSM6IhKnBHrMEsz0yKjo7OZaxecE+sHzlQ/LloVQn80crhQpfuN"
        "ihgjOPfmMQdKxj64mr0CdqIgxvpk+bvvLBXaNBT1GCcLF3HwR1IXsAlaKMbi8JHkezPcehX7MB5j"
        "+AglpScL6OSxn4c4UWqr5WZdagE+GIupXZmaoLm5mpu2d23lwRWuX3KFfx63uc0EtvnL2YN5WsdD"
        "CkieLpKnluRpKEnCylNqS5YGk6fX5Kk4edrOQ4pPmg6UZg6hdtYIMeMhIekheSlPdJru2OqkliGC"
        "RTkk7jekg3Blbdb49mEbTeqPm+dl9dU9QWd+lAWm1UFLKfUOzY4m6T+KnMBJmo4i7XRGFUwbjp3L"
        "oJu84LZeeXO4YZR450+3c5IexpJ22wHASxVIivtspLtogy24eGHD9Xka63lohVL34F4gU1sBhm4E"
        "Rvb2a6SXIVeRGJh6+gjZA9rwZZN3Yd5ReWkoUy2dtn1jBVTj9/4FvIIOatxwSD0qVPTieTOjcsAB"
        "Q4dK6l1F57HILLPRqPgQfimlxNcCMa9kggEZl2ROdzN7cP4jRtKbBrCBDcq3diDloWRqwTzVqIH5"
        "g+Jgvb6pFJO/DLZaJ6IPHfT2oH7Qj4muV6Brt9VaDCI9mHXwKfApALS5kXN/edJGJwYE/8GoNBZG"
        "PmfiKdQ1gjPq3R+ZsuDyqCrpwYjYk+/gLg9zGT++JOPHp2W8tR/W07GdmrrndoTNHoALth5tFld3"
        "e5RYQyy53QO8+kYF+i2F1gfqgI+hMVfcsc4JM02dH1EWvWfgUexWEQW8sUkPHxdCrPBMjMJ8Lpch"
        "qbhJRVNFLJRw6J8kXi4d3yTpJ/K0kRNOEt4zSgnP/yF/PM81f8hLz3PY03x3cIk5WJR6AmLl7Hok"
        "IFKpeJ6fn+f9T2/lSRcHfIKglHWaJNN6TQQ1LleUgEzlcoLhjS9oBkTnmepKXIsWkS4/y0bLxcoq"
        "oc54KgD13B6OKkkQwgB8IX/M8OMplZ4qvN6ECDcAkGgrcvHhXRhIexlAtTOCR73QWu/yfEx3Z8aD"
        "GO4KH4sm8Hy6TmPNJSTNq576xvOuV8v0WAPkS8waGBPyhVIFh8dyepRbw30vVOs8PO9HC23ZjcHm"
        "QqN/SWh8vhOwtu8rK/tEdDE9YHPzXCPNwOFjipJ58nXUqqypt0UJF8y6t62Ivj0DgKZpFF3mZr9G"
        "RmrLRVc4mol0QSNUlom+W1ai32ACNYwxiA8GCldkvGATwO2DettP5DWPFZWd6V7LyOAvc3cvIRIR"
        "dyjxlZk5hDBvwgI2cqwsM/dB0ZcNc3dTlFIPVzx/Dg9PJ39m+ZPMn2/61B/YQspCcnZzu7hvMafw"
        "H/UjRvYBsX7LC9S+9Njb93iB6g/TEBcMitGi5JtIEBw1aogOGk/O10MgXxdMCZ30EKSgxr2euvUz"
        "JYtzojpCSZczXDulLEkD/KzSQzXZF0FXnNcqwPNJ7zPkII8aL6N1w9ioDhr6mAxKLDDPsChGYzcX"
        "G/T8ruex56UZmlM7zTvxa5FnAmNjlBg4PB6NgkqMYSYfPBDpoRRQw5vUFd/6LPDlR+463/Yxfu8F"
        "XX2tlm4DUkoaMTxH2pdotE5wpkFoKRPm4SCf+cstzdB59Cvl2/irz/bF0B/VN09Om/nqGtgkNlfR"
        "sRu4NonNVXa72UYdgUbTTYxtsQ/i/vMamyqNMy/gosYmKEN3i99WY+eccWLEHFRZNPbS3MfOaA5j"
        "d19ZmbFF+hi7zbBQz/CBhttCDRXH3E0SZcVWLls0HNTYWmovVuz2U31T4x4Ow2Kpa8y4OiWcVBrr"
        "n0tN2sfYLb/F4imMMyVyU1ek4sNGbNQz+gQ19hUalxPrnCF2OD/M6f1tg05y9xcXakE0TqDQi2ov"
        "N0G00wL63llqtDwMnzBis+fDNvfFxt9auyOyjNgkxy4H8jlvbFltVxHFSY1t3q+8j4sam0hbxa/1"
        "rpE6ry7Hhy1MM4DWI213U6d3Y2ejqJMo9Es4RnojVz+Gk0p9pMaZNr+p8cBOiXJRG93P5tS4X1fC"
        "zkmtdO/3MxfqSX/s+B5bYo8t7HcZdDa7lbeUuFvjattxUmldJxb4Qa2L71zdRL5zu2F2DXBf573f"
        "nUxr6PhwPfM9Nhjz12tom0rzyn57Ventyd6wSk26Bs6sKm3ClQR3Umuc4apHvKjxgzdfqyEr/yJu"
        "qtKnnTt9LTf2ZdOrPc75wfRjZTcer0EjkRMlFdQ4Vk32vAGJ4GTjvr3x1PTCBjzXEBn5Tp85vyI2"
        "nFN8bwCulzNRZk/QYnu9Hac5qGLh1PraV6RKZMN97WdWA4jWNXbgfMKvdcWWUWf4rhhrkQf1vll2"
        "7FjfO05yxmfS+2ZBlfp09Y6DmPH5bZzI8+4azdv9oSit1h9wfV2tkEDsZ5nOZiFxDQp21SIjPX7N"
        "Z4i/1vYlu/2a+ND4EWfD4s2F6COwgniS/eqCcDG8OAF0ggvTPUw7NxPiWfe9kyglN9TlxYbjrLov"
        "uVB7uK7m0kzozCB9J+0MJOpcRru49ZrC865NjHK+X3GDsTMVw+HY3ppJhwN5Ojuf4/772FP6sF63"
        "ZkQtJLttWdJKlHF9QgWKJ677EJrEy6wnsvFFJf4B1tgksrAX1S4Fk6xf6pBTP98hZ4zva5DzmZr8"
        "K4h+NrXmHNqFTtf3ZNmx+3TFynn8PSEs3mZ9TxO9mrMw179S1MH1iWigUq4MnlmlRh073/tkgoug"
        "zNYeK1xUAOEnXLC0h1JmYNt6Ta2UO3K2PTuplCRxTLCbg98W4MROmIO7uzjBPvhiC2G8tL7VlWKL"
        "MuG3fDjGUiHVZhXFYqS46eatZdyKrvavDUqFUpwwpRCO/fpKp0/D6ZROS+j7TV4decOPbaZfGtWg"
        "K27OLfGqYixhQuOGFAZ6hN5ZOMu/Clq6c1XdnrauF6TIcyjVeGJr6NbIWlgXJbVBHy2yKEsaLeF5"
        "XWVrg4Xa0Xijear6X9jbxiX3CiqVeILYCU3V/PlR97D8qRdcBOoppvuOl8HYGX6VCNB1C4JC/j2B"
        "lC6EACyQx8UICmCPNEpHg+wvRsiriqtIxIEnQl5AgXFYqO5Bzh++qJPrbPceEFyn2DbiyuL9wjNd"
        "t3k3p2CoWwOzoyZKsp9IJU+c2BZG9VZzsJdQGRV3goHxDHNf0Ept6ORqyTx2U/GYWriJXKQKU4HL"
        "NBZ4IFcE4eFUQkVpBZ8mVJ1ZtjV7dTCPr2GBNw96OeDNVOskFWsgFlZtf0WjikvXpxtx3E0zqqxx"
        "fXyN5Kc65ckKlH8uOxXo41x2KvsyVequ2ZrCXlqJLKPMiTdZplyChb8nqYdzVKIt2B7ErTtGsnC5"
        "CeMHjOzxJYzs78iQGD+w71+b4CeUu7w3pXSRO57/xTuJOCDtXnLYr6Hzlvx8sWnKzt8XuzTKgaz4"
        "KbF7GctJbVTGAqWB9J6d7X5NS5W5CvnT560y95J1RNwjiWlszK+DWpa+4nitxRN4H67GvzXQnWsl"
        "OJScsFm8F9iggghHx1/c2QHw7cpJ6O0V479Z9XZXpLyhcxodL3CZqXluGw7s3ImKpjGkTQ1DHxiq"
        "w88xoHO86BxbOsehTjGrBalVjBWxsrYMggr2pSwUetJ1bHnvA+LH+FyjRPrq7eeo+LQCyJpeAzBL"
        "lpHehazKZVxyBhRKEq2tbm9XKcTm6jbpjus8PlT9Ui0x1yhz7TPXVHOttkPLu4GEQ0migHbT5sob"
        "FS8QAztZ8u//8/8DGBt44AXNAQA=",
    "geo__aree_disponibili_fv":
        "H4sIAHzedmoC/6S9y44kSXYk+iuJ3nBDEPp+zI5DXhIDNDkEu28vhpeL6ExnthOREXkjIwtgEfz3"
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
        "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",
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

# ---------------------------------------------------------------- emissioni, dettaglio
FONTE_INVENTARIO = "ARPA FVG, inventario regionale dei gas serra 2021 (metodologia IPCC)"

# Quote sul totale regionale, %. Le quattro macrocategorie IPCC.
EMISSIONI_MACRO = {"Energia": 86, "AFOLU (agricoltura e uso del suolo)": 7,
                   "IPPU (processi industriali)": 5, "Rifiuti": 2}

# Dettaglio della macrocategoria Energia, in % del totale regionale.
EMISSIONI_ENERGIA = {
    "Trasporti": 27.4,
    "Riscaldamento": 18.6,
    "Industrie manifatturiere": 18.6,
    "Industrie energetiche": 17.8,
    "Emissioni fuggitive": 2.1,
}

# Composizione del trasporto su strada, in % del solo trasporto su strada
# (che a sua volta vale il 25% del totale regionale).
TRASPORTO_STRADA = {
    "Autovetture": 69.3, "Veicoli industriali oltre 3,5 t e autobus": 13.4,
    "Veicoli industriali sotto 3,5 t": 10.8, "Motocicli": 6.6,
}
TRASPORTO_STRADA_QUOTA = 25   # % del totale regionale

# Gli assorbimenti forestali sono di segno opposto: si sottraggono.
ASSORBIMENTI_FORESTALI = 25   # % delle emissioni regionali compensate, 2021
ASSORBIMENTI_ITALIA = 10      # % media nazionale, per confronto

# Consumi finali per settore, ktep (EUROSTAT/ENEA, ripresi nel PER)
CONSUMI_SETTORE_STORICO = {
    2010: {"Industria": 1325, "Civile": 1307, "Trasporti": 715, "Agricoltura e pesca": 34},
    2015: {"Industria": 1152, "Civile": 1219, "Trasporti": 550, "Agricoltura e pesca": 55},
    2019: {"Industria": 1272, "Civile": 1285, "Trasporti": 604, "Agricoltura e pesca": 59},
    2020: {"Industria": 1202, "Civile": 1239, "Trasporti": 533, "Agricoltura e pesca": 61},
    2021: {"Industria": 1333, "Civile": 1288, "Trasporti": 649, "Agricoltura e pesca": 76},
}
QUOTE_SETTORE_CONFRONTO = {   # % dei consumi finali, FVG contro Italia (2021)
    "Industria": (40.0, 22.0), "Civile": (38.5, 43.7), "Trasporti": (19.4, 31.2),
}

# ---------------------------------------------------------------- clima, scenari
# Gradi giorno: quanto si scalda e quanto si raffresca, oggi e a fine secolo.
# HDD = riscaldamento, CDD = raffrescamento. Fonte: piattaforma CLiNE (ARPA FVG),
# riferimento 1976-2005.
GRADI_GIORNO = {
    "riscaldamento_pianura_oggi": 4500,
    "riscaldamento_pianura_2100_rcp85": 3000,
    "hdd_malborghetto_rcp85_2071_2100": -1381,   # anomalia, °C
    "cdd_fagagna_rcp85_2071_2100": 472,          # anomalia, °C
}
SCENARI_RCP = {
    "RCP2.6": "Forte riduzione delle emissioni, Accordo di Parigi rispettato",
    "RCP4.5": "Scenario intermedio",
    "RCP8.5": "Emissioni in continua crescita, «business as usual»",
}
ZONA_CLIMATICA = {
    "oggi": "E (zona fredda) — riscaldamento dal 15 ottobre al 15 aprile, fino a 14 ore al giorno",
    "rcp85_fine_secolo": "D (zona fresca) — dal 1° novembre al 15 aprile, fino a 12 ore",
}

# Eventi meteorologici rilevanti del 2025 in FVG (ARPA FVG)
EVENTI_2025 = [
    ("13 marzo", "Stagione convettiva precocissima", "Grandinate e quattro supercelle.", 2),
    ("22 maggio", "Temporali in pianura", "Piogge intense localizzate e alcune trombe d'aria.", 2),
    ("26 giugno", "Caldo intenso e temporali forti",
     "Grandine di grosse dimensioni su tutta la pianura, vento forte.", 3),
    ("11 e 27 luglio", "Temporali e grandinate in pianura", "", 2),
    ("29 agosto e 2 settembre", "Temporali stazionari nel Triestino",
     "Tra 100 e 200 mm in poche ore, allagamenti e danni.", 3),
    ("16 settembre", "Supercella temporalesca",
     "Raffiche forti e grandine media, danni notevoli da Udine a Trieste.", 3),
    ("24 ottobre", "Temporale a Trieste",
     "Grandine minuta con accumuli al suolo di alcuni centimetri.", 2),
    ("16-17 novembre", "Alluvione del bacino dello Judrio",
     "Oltre 200 mm in 12 ore da un sistema autorigenerante stazionario. "
     "Lo Judrio esonda e allaga Versa con 1-2 m d'acqua e fango; una collina frana "
     "su Brazzano di Cormòns causando due vittime e distruggendo tre abitazioni. "
     "Un evento simile non accadeva dal 29 agosto 2003, l'alluvione della Val Canale.", 5),
]

# Rischi climatici per il sistema energetico (EUCRA 2023, ripreso da ARPA FVG)
CATENA_IMPATTO = [
    ("Generazione", "Meno idroelettrico",
     "Siccità e riduzione delle precipitazioni estive tagliano la producibilità."),
    ("Generazione", "Meno termoelettrico",
     "Acqua di raffreddamento più calda e più scarsa abbassa il rendimento."),
    ("Generazione", "Danni agli impianti rinnovabili",
     "Grandine ed eventi estremi colpiscono soprattutto il fotovoltaico."),
    ("Trasmissione", "Meno capacità di linee e trasformatori",
     "Il calore riduce la portata delle linee proprio nelle ore di punta."),
    ("Trasmissione", "Danni all'infrastruttura",
     "Alluvioni e frane interrompono la fornitura."),
    ("Domanda", "Più energia per il raffrescamento",
     "Il picco di domanda si sposta dall'inverno all'estate."),
    ("Domanda", "Domanda in crescita per l'elettrificazione",
     "Mobilità, riscaldamento e industria aggiungono carico."),
]


# ---------------------------------------------------------------- uso del suolo
FONTE_SAU = "ISTAT, censimento generale dell'agricoltura 2020; ISPRA, consumo di suolo"

SAU_FVG_HA = 218_000          # superficie agricola utilizzata
SUPERFICIE_FVG_HA = 793_240   # superficie regionale
# Termini di paragone per capire quanto sia grande una superficie
PARAGONI_SUOLO = {
    "Un campo da calcio regolamentare": 0.71,
    "Un ipermercato con parcheggio": 2.5,
    "L'aeroporto di Ronchi dei Legionari": 200.0,
}

# Nuove installazioni fotovoltaiche per categoria, primi mesi del 2026 (Terna).
# Serve a rispondere alla domanda «il fotovoltaico mangia i campi?» con i numeri
# di cosa si sta installando davvero, non con le impressioni.
PV_NUOVE_2026 = {
    "Residenziale (fino a 20 kW)": {"mw": 28.21, "impianti": 4644},
    "Tetti commerciali e artigianali (20-200 kW)": {"mw": 1.33, "impianti": 78},
    "Tetti industriali e piccoli campi (200 kW-1 MW)": {"mw": 0.73, "impianti": 9},
    "Utility scale (oltre 1 MW)": {"mw": 1.22, "impianti": 1},
}

# Ore equivalenti per tipologia di installazione. Il residenziale rende meno:
# falde non ottimali, ombreggiamenti, nessun inseguimento. L'utility scale usa
# tracker su una parte del campo.
PV_ORE_PER_TIPO = {
    "Residenziale (fino a 20 kW)": 1000,
    "Tetti commerciali e artigianali (20-200 kW)": 1040,
    "Tetti industriali e piccoli campi (200 kW-1 MW)": 1100,
    "Utility scale (oltre 1 MW)": 1200,
}

FONTE_BIOMASSA_2015 = ("Regione FVG, Direzione risorse agricole e forestali, "
                       "database impianti a biomassa legnosa da finanziamenti pubblici, "
                       "settembre 2015")
FONTE_ARERA = "ARERA, dati di prelievo dei clienti domestici, anno 2022"


# Obiettivo di copertura elettrica rinnovabile al 2030 dichiarato nella
# Strategia Regionale per l'Idrogeno: e' il vincolo dentro cui l'idrogeno
# regionale deve trovare la propria elettricita'.
TARGET_FER_ELETTRICA_2030 = {
    "copertura_pct": 79,          # % dell'elettricita' da fonti rinnovabili
    "nuova_capacita_gw": 3.3,     # GW aggiuntivi rispetto al 2020
    "riferimento": "Strategia Regionale per l'Idrogeno, in coerenza con il PNIEC",
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


def grafico(fig, fonte: str, nota: str = "") -> None:
    """Disegna un grafico e ne dichiara la fonte, sempre, subito sotto."""
    st.plotly_chart(fig, width="stretch")
    st.caption(f"Fonte: {fonte}." + (f" {nota}" if nota else ""))


def tabella(df, fonte: str, **kwargs) -> None:
    st.dataframe(df, width="stretch", **kwargs)
    st.caption(f"Fonte: {fonte}.")


PLOT = dict(
    template="plotly_white",
    margin=dict(t=48, b=10, l=10, r=24),
    legend=dict(orientation="h", yanchor="bottom", y=1.04, x=0),
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

# Totali annui: servono in piu' schede (quota rinnovabile, intensita' carbonica,
# grafico di Marchetti), quindi stanno qui e non dentro una singola scheda.
tot_y = prod_fonte.groupby("anno")["valore"].sum()
fer_y = prod_fer.groupby("anno")["valore"].sum()


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


def _scheda_0():
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
    quota = (fer_y / tot_y * 100).dropna().reset_index(name="quota")
    fig = px.line(quota, x="anno", y="quota", markers=True,
                  color_discrete_sequence=["#22C55E"])
    fig.update_layout(height=300, yaxis_title="% FER", xaxis_title=None,
                      yaxis_range=[0, 100], **PLOT)
    fig.add_hline(y=quota["quota"].mean(), line_dash="dot", line_color="#9CA3AF",
                  annotation_text=f"media {quota['quota'].mean():.0f}%",
                  annotation_position="bottom right")
    grafico(fig, DOC.F_TERNA)

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

    # Parco -> categorie di impianto. L'input si ripartisce in proporzione
    # all'energia utile che ciascuna categoria produce (elettricita' piu' calore),
    # e le perdite si formano dentro la categoria, non prima: e' li' che avviene
    # la conversione. Cosi' ogni nodo chiude e spostare il rendimento fa vedere
    # subito le perdite crescere o calare.
    utile = {}
    for c in categorie:
        cogen = "Cogenerative" in c and "Non" not in c
        utile[c] = cat_y[c] + (cal_y if cogen else 0.0)
    tot_utile = sum(utile.values())

    for c in categorie:
        quota_c = utile[c] / tot_utile if tot_utile else 0
        input_c = input_comb * quota_c
        link("Parco termoelettrico", c, input_c, "rgba(75,85,99,0.35)")

        link(c, "Energia elettrica", cat_y[c], "rgba(250,204,21,0.45)")
        if "Cogenerative" in c and "Non" not in c:
            link(c, "Calore utile", cal_y, "rgba(249,115,22,0.45)")
        link(c, "Perdite di conversione", max(0.0, input_c - utile[c]),
             "rgba(239,68,68,0.3)")

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


def _scheda_1():
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



    # ------------------------------------------------- il profilo della domanda
    st.divider()
    st.subheader("Quando consumano le famiglie friulane")
    pre = D.carica_per("prelievi_orari_fvg")
    fas = D.carica_per("prelievi_fasce_fvg")

    if not pre.empty:
        st.caption(
            "Prelievo medio orario dei clienti domestici, misurato. È l'unico profilo "
            "orario reale disponibile per la regione, e riguarda il solo settore "
            f"domestico (circa il 15% dei consumi elettrici). Fonte: {DOC.FONTE_ARERA}."
        )

        prof = (pre.groupby(["tipo_giorno", "ora_n"])["kwh"].mean().reset_index())
        prof["tipo_giorno"] = prof["tipo_giorno"].str.replace("_", " ").str.capitalize()
        fig = px.line(prof, x="ora_n", y="kwh", color="tipo_giorno", markers=True,
                      color_discrete_map={"Giorno feriale": "#2563EB",
                                          "Giorno festivo": "#F97316"})
        fig.add_vrect(x0=10, x1=16, fillcolor="#FACC15", opacity=0.18, line_width=0,
                      annotation_text="ore di sole", annotation_position="top left")
        fig.update_layout(height=380, xaxis_title="ora del giorno",
                          yaxis_title="kWh medi per cliente", **PLOT)
        grafico(fig, DOC.FONTE_ARERA)

        picco = prof.loc[prof["kwh"].idxmax()]
        solare = prof[(prof["ora_n"] >= 10) & (prof["ora_n"] <= 16)]["kwh"].mean()
        st.info(
            f"**Il picco domestico è alle {int(picco['ora_n'])}**, quando il fotovoltaico "
            f"ha ormai finito. Nelle ore centrali, quando il sole produce, il consumo medio "
            f"è di {solare:.3f} kWh contro i {picco['kwh']:.3f} della punta serale: "
            f"**{(1 - solare / picco['kwh']) * 100:.0f}% in meno**. "
            + (f"Il {fas['f3'].mean() * 100:.0f}% dell'energia domestica viene prelevato in "
               "fascia F3, cioè di sera, di notte e nei festivi. " if not fas.empty else "")
            + "È la ragione per cui l'autoconsumo fotovoltaico senza accumulo si ferma "
            "intorno al 30%, e perché batterie e comunità energetiche non sono un "
            "accessorio ma la condizione perché il solare residenziale serva a qualcosa."
        )

        st.markdown("**Come cambia nell'arco dell'anno**")
        mens = pre.groupby(["mese_n", "ora_n"])["kwh"].mean().reset_index()
        fig = px.density_heatmap(mens, x="ora_n", y="mese_n", z="kwh",
                                 color_continuous_scale="YlOrRd", nbinsx=24, nbinsy=12)
        fig.update_layout(height=360, xaxis_title="ora del giorno", yaxis_title="mese",
                          coloraxis_colorbar=dict(title="kWh"), template="plotly_white",
                          margin=dict(t=48, b=10, l=10, r=24))
        fig.update_yaxes(autorange="reversed", tickmode="array", tickvals=list(range(1, 13)),
                         ticktext=["gen", "feb", "mar", "apr", "mag", "giu", "lug", "ago",
                                   "set", "ott", "nov", "dic"])
        grafico(fig, DOC.FONTE_ARERA,
                "Più scuro significa più consumo. Si vedono la punta serale invernale "
                "e la coda estiva del condizionamento.")

        classi = (pre.groupby("classe")["kwh"].mean().reset_index()
                  .sort_values("kwh"))
        fig = px.bar(classi, x="kwh", y="classe", orientation="h", text_auto=".3f",
                     color_discrete_sequence=["#2563EB"])
        fig.update_traces(cliponaxis=False)
        fig.update_layout(height=300, yaxis_title=None,
                          xaxis_title="kWh medi orari per cliente", **PLOT)
        grafico(fig, DOC.FONTE_ARERA,
                "Classe di potenza impegnata: chi ha più potenza consuma di più, ed è "
                "il cliente per cui una pompa di calore o un'auto elettrica cambiano il profilo.")


def _scheda_2():
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
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_layout(height=380, xaxis_title=None, yaxis_title="MVA di incremento",
                      yaxis_range=[0, sv["MVA"].max() * 1.18], **PLOT)
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
                  annotation_text=f"Target 2030: {target} GW",
                  annotation_position="top left")
    fig.update_layout(showlegend=False, height=360, xaxis_title=None, **PLOT)
    grafico(fig, DOC.F_AUDIZIONI)
    st.info(
        f"Il Decreto Aree Idonee assegna al FVG **+{target} GW** di nuova capacità rinnovabile "
        f"al 2030 rispetto al 2021. Ne risultano in esercizio o autorizzati "
        f"**{DOC.BURDEN_SHARING['In esercizio o autorizzato dal 2021']} GW**: l'82% del percorso. "
        "Il collo di bottiglia non è più autorizzare impianti, è avere rete che li accolga."
    )

    st.divider()
    st.subheader("Avanzamento verso il target 2030, in dettaglio")
    st.caption(f"Fonte: {DOC.FONTE_RETI_REPORT}.")

    bsm = pd.DataFrame(DOC.BURDEN_SHARING_MW.items(), columns=["Voce", "MW"])
    bsm["Quota"] = bsm["MW"] / DOC.BURDEN_SHARING_TARGET_MW * 100
    fig = px.bar(bsm, x="MW", y=["Target"] * len(bsm), color="Voce", orientation="h",
                 text=bsm.apply(lambda r: f"{r['Voce']}<br>{r['MW']} MW", axis=1),
                 color_discrete_sequence=["#22C55E", "#2563EB", "#60A5FA", "#E5E7EB"])
    fig.update_traces(textposition="inside", insidetextanchor="middle")
    fig.update_layout(height=260, barmode="stack", showlegend=False, yaxis_title=None,
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
            fig.update_traces(textposition="outside", texttemplate="%{text} aree", cliponaxis=False)
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


def _scheda_3():
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

    st.divider()
    aree_fv = D.carica_per("aree_disponibili_fv")
    geo_fv = D.carica_geojson("aree_disponibili_fv")

    if not aree_fv.empty:
        st.subheader("Il fotovoltaico occupa davvero il suolo agricolo?")
        st.caption(
            "È la domanda che blocca più progetti, e si può rispondere con i numeri. "
            f"Fonte del denominatore: {DOC.FONTE_SAU}."
        )

        prog_s = D.carica_per("progetti_solare")
        ha_terra = 0.0
        if not prog_s.empty:
            att = prog_s[prog_s["stato"].isin(
                ["Autorizzato", "In costruzione", "In istruttoria", "Realizzato"])]
            ha_terra = float(att["superficie_ha"].sum())

        q = st.columns(4)
        q[0].metric("Superficie agricola utilizzata",
                    f"{DOC.SAU_FVG_HA:,.0f} ha".replace(",", "."))
        q[1].metric("Suolo dei progetti fotovoltaici", f"{ha_terra:,.0f} ha".replace(",", "."),
                    "autorizzati, in costruzione o realizzati")
        q[2].metric("Quota sulla SAU", f"{ha_terra / DOC.SAU_FVG_HA * 100:.2f}%")
        q[3].metric("Quota sul territorio regionale",
                    f"{ha_terra / DOC.SUPERFICIE_FVG_HA * 100:.2f}%")

        st.success(
            f"**Tutti i progetti fotovoltaici della regione occupano lo "
            f"{ha_terra / DOC.SAU_FVG_HA * 100:.1f}% della superficie agricola.** "
            "Non è una quota trascurabile in assoluto, ma va confrontata con quello che "
            "sta davvero succedendo: nel 2026 il **89,6% della nuova potenza installata "
            "è residenziale**, su tetti. Il campo a terra che si vede dalla strada è "
            "l'eccezione visibile di un fenomeno che avviene quasi tutto sui tetti."
        )

        # ---- che cosa si sta installando davvero
        st.markdown("**Cosa si sta installando: le nuove connessioni del 2026**")
        nuove = pd.DataFrame([
            {"Categoria": k, "MW": v["mw"], "Impianti": v["impianti"],
             "kW medi": v["mw"] * 1000 / v["impianti"]}
            for k, v in DOC.PV_NUOVE_2026.items()
        ])
        cc1, cc2 = st.columns(2)
        with cc1:
            fig = px.pie(nuove, values="MW", names="Categoria", hole=0.5,
                         color_discrete_sequence=["#FACC15", "#F59E0B", "#F97316", "#65A30D"])
            fig.update_traces(textinfo="percent")
            fig.update_layout(height=340, title="Potenza per categoria",
                              legend=dict(orientation="h", yanchor="top", y=-0.05, x=0),
                              margin=dict(t=48, b=10, l=10, r=24), template="plotly_white")
            grafico(fig, DOC.F_TERNA)
        with cc2:
            fig = px.bar(nuove.sort_values("kW medi"), x="kW medi", y="Categoria",
                         orientation="h", text_auto=".0f", log_x=True,
                         color_discrete_sequence=["#F59E0B"])
            fig.update_traces(cliponaxis=False)
            fig.update_layout(height=340, yaxis_title=None,
                              xaxis_title="kW medi per impianto (scala log)", **PLOT)
            grafico(fig, DOC.F_TERNA)

        # ---- rese diverse per tipologia
        st.markdown("**Non tutti i tetti rendono uguale**")
        rese = pd.DataFrame([
            {"Tipologia": k, "Ore equivalenti": v} for k, v in DOC.PV_ORE_PER_TIPO.items()
        ])
        fig = px.bar(rese, x="Ore equivalenti", y="Tipologia", orientation="h",
                     text_auto=".0f", color="Ore equivalenti",
                     color_continuous_scale="YlOrRd")
        fig.update_traces(cliponaxis=False)
        fig.update_layout(height=300, yaxis_title=None, coloraxis_showscale=False,
                          xaxis_title="kWh per kWp all'anno", **PLOT)
        grafico(fig, "elaborazione su dati Terna 2019-2022 e letteratura",
                "Il residenziale rende meno per falde non ottimali e ombreggiamenti; "
                "l'utility scale usa inseguitori su una parte del campo.")

        st.caption(
            "La differenza tra 1.000 e 1.200 ore equivalenti è del 20%: per produrre la "
            "stessa energia servono il 20% di pannelli in più sui tetti residenziali che "
            "in un campo ben progettato. È il vero costo del «facciamoli solo sui tetti»."
        )

        # ---- termini di paragone
        st.markdown("**Quanto è grande quel suolo, in cose che si vedono**")
        par = pd.DataFrame([
            {"Termine di paragone": k, "Equivalenti": ha_terra / v}
            for k, v in DOC.PARAGONI_SUOLO.items()
        ])
        st.dataframe(par.round(0), hide_index=True, width="stretch")
        st.caption(
            f"Fonte: {DOC.FONTE_SAU}. I {ha_terra:,.0f} ettari dei progetti fotovoltaici "
            "equivalgono a circa 3.200 campi da calcio, o a un sesto della superficie "
            "già impermeabilizzata della regione (38.380 ettari). "
            "La competizione col cibo è reale solo se si guarda il singolo campo: "
            "sul totale regionale, il fattore che sottrae terreno all'agricoltura è "
            "l'urbanizzazione, non il solare.".replace(",", ".")
        )

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
            fig.update_traces(textposition="outside", texttemplate="%{text} progetti",
                              cliponaxis=False)
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


def _scheda_4():
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


def _scheda_5():
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



    # ---------------------------------------------------- gli impianti sul territorio
    st.divider()
    st.subheader("Le caldaie a biomassa finanziate con fondi pubblici")
    bio_c = D.carica_per("biomassa_comuni_2015")
    bio_i = D.carica_per("biomassa_impianti_2015")

    if not bio_i.empty:
        k = st.columns(4)
        k[0].metric("Impianti censiti", len(bio_i))
        k[1].metric("Potenza termica", f"{bio_i['kw'].sum() / 1000:.1f} MW")
        k[2].metric("Legname consumato",
                    f"{bio_i['massa_t'].sum():,.0f} t/anno".replace(",", "."))
        pub = bio_i[bio_i["proprietario"] == "Pubblico"]
        k[3].metric("Quota pubblica", f"{pub['kw'].sum() / bio_i['kw'].sum() * 100:.0f}%",
                    f"{len(pub)} impianti su {len(bio_i)}")

        if not bio_c.empty:
            mappa_b = bio_c.copy()
            fig = px.scatter_map(
                mappa_b, lat="lat", lon="lon", size="kw", color="combustibile",
                hover_name="comune",
                hover_data={"impianti": True, "kw": ":.0f", "massa_t": ":.0f",
                            "lat": False, "lon": False},
                size_max=34, zoom=7.1, center={"lat": 46.3, "lon": 13.1},
                map_style="carto-positron",
                color_discrete_map={"Cippato": "#8B4513", "Legna a ciocchi": "#A16207",
                                    "Pellet": "#D97706"},
                labels={"kw": "kW termici", "massa_t": "tonnellate/anno"})
            fig.update_layout(height=480, margin=dict(t=10, b=10, l=0, r=0),
                              legend=dict(orientation="h", yanchor="bottom", y=1.01,
                                          x=0, title=None))
            grafico(fig, DOC.FONTE_BIOMASSA_2015,
                    "Le coordinate sono i centroidi comunali: gli impianti dello stesso "
                    "comune sono aggregati in un punto.")

        c1, c2 = st.columns(2)
        with c1:
            per_comb = (bio_i.groupby("combustibile")
                        .agg(impianti=("kw", "count"), kw=("kw", "sum"),
                             legname=("massa_t", "sum")).reset_index())
            fig = px.bar(per_comb.sort_values("kw"), x="kw", y="combustibile",
                         orientation="h", text="impianti", color="combustibile",
                         color_discrete_map={"Cippato": "#8B4513",
                                             "Legna a ciocchi": "#A16207",
                                             "Pellet": "#D97706"})
            fig.update_traces(textposition="outside", texttemplate="%{text} impianti",
                              cliponaxis=False)
            fig.update_layout(showlegend=False, height=300, yaxis_title=None,
                              xaxis_title="kW termici", **PLOT)
            grafico(fig, DOC.FONTE_BIOMASSA_2015)
        with c2:
            grandi = bio_i.nlargest(10, "kw")[["comune", "kw", "combustibile", "proprietario"]]
            grandi.columns = ["Comune", "kW", "Combustibile", "Proprietà"]
            st.markdown("**Le dieci caldaie maggiori**")
            st.dataframe(grandi, hide_index=True, width="stretch", height=300)
            st.caption(f"Fonte: {DOC.FONTE_BIOMASSA_2015}.")

        st.info(
            f"**Diciannove impianti pubblici fanno il "
            f"{pub['kw'].sum() / bio_i['kw'].sum() * 100:.0f}% della potenza**, e sono quasi "
            "tutti a cippato: sono le reti di teleriscaldamento di valle — Arta Terme, "
            "Tarvisio, Forni di Sopra. Le 92 caldaie a legna a ciocchi sono quasi tutte da "
            "30 kW: singole abitazioni. Il cippato è la filiera vera, la legna è "
            "autoconsumo domestico incentivato.\n\n"
            "La geografia è netta: **Carnia, Canal del Ferro e Valli del Natisone**. "
            "Dove c'è bosco accessibile e non c'è metano."
        )

        st.warning(
            "**Il dato è fermo a settembre 2015 e copre solo gli impianti finanziati.** "
            "Non è il parco a biomassa regionale: le caldaie e le stufe domestiche non "
            "incentivate sono decine di migliaia e pesano molto di più sui consumi — e "
            "sulla qualità dell'aria invernale. Serve un censimento aggiornato."
        )


def _scheda_6():
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



    # ------------------------------------------------------- la dieta, per quel poco che si sa
    st.divider()
    st.subheader("Che cosa mangiano i digestori")
    dieta = D.carica_per("bio_impianti_dieta")
    pipe = D.carica_per("biometano_pipeline")

    st.caption(
        "È la domanda decisiva — colture dedicate o scarti — e la risposta oggi è "
        "parziale. Quella che segue è una ricognizione da fonti aperte, non un registro."
    )

    if not dieta.empty:
        tab = dieta[["impianto", "comune", "provincia", "tipologia", "dieta", "stato",
                     "fonte", "affidabilita"]].copy()
        tab.columns = ["Impianto", "Comune", "Prov.", "Tipologia", "Alimentazione",
                       "Stato", "Fonte", "Affidabilità"]
        st.dataframe(tab, hide_index=True, width="stretch")
        st.caption(
            "Fonte: ricognizione su fonti aperte (comunicati aziendali, stampa, "
            "documentazione regionale). La colonna «Affidabilità» dichiara quanto è solida "
            "ciascuna riga: nessuna arriva ad «alta»."
        )

        agri = dieta["dieta"].astype(str).str.contains("agricol|zootecnic|coltur", case=False).sum()
        scarti = dieta["dieta"].astype(str).str.contains("scart|FORSU|reflu|rifiut", case=False).sum()
        d1, d2, d3 = st.columns(3)
        d1.metric("Impianti tracciati", len(dieta))
        d2.metric("Con matrici agricole", int(agri))
        d3.metric("Con scarti o rifiuti", int(scarti))

    if not pipe.empty:
        st.markdown("**I comuni con progetti di biometano**")
        st.caption(
            f"{len(pipe)} comuni interessati da progetti in iter o realizzati. "
            "L'elenco dice dove, non con quale alimentazione."
        )
        st.dataframe(pipe.rename(columns={"comune": "Comune"}), hide_index=True,
                     width="stretch", height=240)

    st.error(
        "**Questo è il buco più serio dell'intera applicazione, e va detto chiaramente.** "
        "In regione ci sono **57 comuni con impianti a biogas per 120,6 MW**, ma di questi "
        "conosciamo l'alimentazione solo per una manciata. Senza sapere quanta parte va a "
        "**colture dedicate** e quanta a **reflui zootecnici e scarti**, la valutazione "
        "ambientale del biogas friulano resta sospesa: le due filiere hanno bilanci di "
        "suolo, di acqua e di carbonio completamente diversi, e il confronto per ettaro "
        "della sezione precedente colpisce solo la prima.\n\n"
        "**Tre strade per chiudere il buco**, in ordine di praticabilità:\n"
        "1. **Atlaimpianti del GSE** riporta la tipologia di alimentazione per gli impianti "
        "incentivati. L'accesso massivo richiede una richiesta formale, che APE FVG può "
        "presentare come ente pubblico.\n"
        "2. Le **autorizzazioni AIA regionali** contengono la matrice in ingresso impianto "
        "per impianto e sono pubbliche: 57 comuni sono un lavoro manuale ma finito.\n"
        "3. Il **registro biometano del GSE** copre gli impianti convertiti, che sono i più "
        "rilevanti per il futuro ma pochi per il presente."
    )


def _scheda_7():
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
                      annotation_text=f"producibilità media {prod_media:.0f} GWh",
                      annotation_position="top left")
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
                  annotation_text=f"media {ore_idro['ore'].mean():.0f} ore",
                  annotation_position="top left")
    fig.update_layout(height=340, yaxis_title="ore/anno", xaxis_title=None, **PLOT)
    grafico(fig, DOC.F_TERNA)

    st.info(
        "Il PER stima una producibilità media di "
        f"{DOC.IDRO_PARCO['Producibilità media annua (GWh)']:,.0f} GWh e prevede di arrivare a ".replace(",", ".")
        + "2.231 GWh al 2045: un margine di crescita limitato, perché i siti migliori sono già "
        "sfruttati. L'espansione passa da efficientamento degli impianti esistenti e "
        "mini-idro, non da nuovi grandi invasi."
    )

    st.divider()
    centrali = D.carica_per("centrali_idro")
    if not centrali.empty:
        st.subheader("Le centrali sul territorio")
        cat = D.carica_per("centrali_idro_catasto")
        mont = D.carica_per("idro_montagna")

        if not cat.empty:
            esist = cat[cat["stato"] == "Esistente"]
            st.caption(
                "Catasto regionale delle derivazioni idriche: ogni punto è una centrale "
                "con la sua concessione. Attenzione, la **potenza di concessione** non è "
                "la potenza efficiente — è la potenza nominale media legata alla portata "
                "derivabile, e la somma regionale sta molto sotto i 528,9 MW misurati da Terna."
            )
            c = st.columns(4)
            c[0].metric("Centrali censite", len(cat), f"{len(esist)} esistenti")
            c[1].metric("Potenza di concessione", f"{esist['potenza_mw'].sum():.0f} MW")
            c[2].metric("In progetto o realizzazione",
                        int((cat["stato"].isin(["In progetto", "In realizzazione"])).sum()),
                        f"{cat[cat['stato'].isin(['In progetto', 'In realizzazione'])]['potenza_mw'].sum():.1f} MW")
            mediana = esist["potenza_mw"].median()
            c[3].metric("Potenza mediana", f"{mediana * 1000:.0f} kW",
                        "metà delle centrali sta sotto")

            m = cat.copy()
            m["size_mw"] = m["potenza_mw"].fillna(0).clip(lower=0.01)
            fig = px.scatter_map(
                m, lat="lat", lon="lon", size="size_mw", color="stato",
                hover_name="nome",
                hover_data={"potenza_mw": ":.3f", "salto_m": ":.0f", "scadenza": True,
                            "lat": False, "lon": False, "size_mw": False},
                size_max=30, zoom=7.1, center={"lat": 46.3, "lon": 13.0},
                map_style="carto-positron",
                color_discrete_map={"Esistente": "#2563EB", "In progetto": "#F97316",
                                    "In realizzazione": "#FACC15", "Rinunciata": "#D1D5DB"},
                labels={"potenza_mw": "MW di concessione", "salto_m": "salto (m)"})
            fig.update_layout(height=540, margin=dict(t=10, b=10, l=0, r=0),
                              legend=dict(orientation="h", yanchor="bottom", y=1.01,
                                          x=0, title=None))
            grafico(fig, DOC.F_REGIONE + " — catasto derivazioni idriche")

            c1, c2 = st.columns(2)
            with c1:
                fig = px.histogram(esist[esist["potenza_mw"] > 0], x="potenza_mw", nbins=40,
                                   log_y=True, color_discrete_sequence=["#2563EB"])
                fig.update_layout(height=300, xaxis_title="MW di concessione",
                                  yaxis_title="centrali (scala log)",
                                  title="Quasi tutte piccolissime", **PLOT)
                grafico(fig, DOC.F_REGIONE)
            with c2:
                sal = esist.dropna(subset=["salto_m", "potenza_mw"])
                sal = sal[(sal["salto_m"] > 0) & (sal["potenza_mw"] > 0)]
                fig = px.scatter(sal, x="salto_m", y="potenza_mw", log_x=True, log_y=True,
                                 hover_name="nome", color_discrete_sequence=["#2563EB"],
                                 opacity=0.6)
                fig.update_layout(height=300, xaxis_title="salto (m, log)",
                                  yaxis_title="MW (log)",
                                  title="Il salto fa la potenza", **PLOT)
                grafico(fig, DOC.F_REGIONE)

            piccole = (esist["potenza_mw"] < 1).sum()
            st.info(
                f"**{piccole} centrali su {len(esist)} stanno sotto il megawatt**, e la "
                f"mediana è di {mediana * 1000:.0f} kW: il parco idroelettrico friulano è "
                "fatto di una lunga coda di micro-derivazioni su rogge, canali e acquedotti, "
                "più poche grandi centrali di montagna. "
                f"Le nuove concessioni in progetto valgono "
                f"{cat[cat['stato'] == 'In progetto']['potenza_mw'].sum():.1f} MW su 47 pratiche: "
                "meno di 200 kW l'una. Il grande idro è finito, resta il capillare."
            )

        if not mont.empty:
            st.markdown("**Le grandi centrali di montagna**")
            tab = mont[["impianto", "comune", "corso_acqua", "gestore", "potenza_MW",
                        "producibilita_GWh_anno", "tipo_impianto", "salto_m"]].copy()
            tab.columns = ["Impianto", "Comune", "Corso d'acqua", "Gestore", "MW",
                           "GWh/anno", "Tipo", "Salto (m)"]
            st.dataframe(tab.sort_values("MW", ascending=False), hide_index=True,
                         width="stretch")
            st.caption(
                f"Fonte: {DOC.F_PER}, dati di impianto. "
                f"Queste {len(mont)} centrali valgono {mont['potenza_MW'].sum():.0f} MW e "
                f"circa {mont['producibilita_GWh_anno'].sum():.0f} GWh l'anno: "
                "la dorsale storica del sistema, quasi tutta in Carnia e Canal del Ferro."
            )

def _scheda_8():
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


def _scheda_9():
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


def _scheda_10():
    st.subheader("Idrogeno: a che punto è il Friuli-Venezia Giulia")
    st.caption(f"Fonte: {DOC.FONTE_H2}.")

    n = DOC.H2_NAHV
    h = st.columns(4)
    h[0].metric("Finanziamento NAHV", f"{n['Finanziamento europeo (mln €)']} mln €")
    h[1].metric("Organizzazioni partner", n["Organizzazioni partner"])
    h[2].metric("Durata del progetto", f"{n['Durata (mesi)']} mesi")
    h[3].metric("Autobus a idrogeno previsti", sum(DOC.H2_MEZZI_TPL.values()))

    t = DOC.TARGET_FER_ELETTRICA_2030
    st.info(
        f"**Il contesto in cui l'idrogeno regionale deve stare.** La Strategia dichiara "
        f"l'obiettivo di coprire il **{t['copertura_pct']}%** dell'elettricità regionale con "
        f"fonti rinnovabili entro il 2030, installando circa **{t['nuova_capacita_gw']} GW** "
        f"in più rispetto al 2020, in prevalenza fotovoltaico. "
        f"Oggi la quota rinnovabile sulla produzione è del {quota_fer:.0f}%, ma sulla "
        f"**domanda** regionale è molto più bassa, perché un terzo dell'elettricità viene "
        "importata. L'idrogeno rinnovabile deve trovare posto dentro quel numero, non "
        f"accanto. ({t['riferimento']}.)"
    )

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


def _scheda_11():
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

    st.divider()
    st.subheader("Come cambiano i consumi finali: 2021 e 2045 a confronto")

    cons21 = D.carica_per("consumi_finali_2021")
    ind_v = D.carica_per("scenari_industria_vettori")
    tra_al = D.carica_per("trasporti_alimentazione")
    sc_all = D.carica_per("scenari_settori")

    if not (cons21.empty or ind_v.empty or tra_al.empty):
        st.caption(
            "A sinistra il vettore, a destra il settore. Il PER disaggrega i vettori al 2045 "
            "per industria e trasporti. Per il **civile** dà solo il totale: qui viene "
            "ripartito con le quote del 2021 e le voci sono marcate «(stima)» — è "
            "un'ipotesi di comodo, non uno scenario del piano. "
            "Scenario: Policy B per l'industria."
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
            # Il PER da' il totale del civile al 2045 ma non la sua composizione.
            # Invece di inventarla, la si ripartisce con le quote del 2021 e lo si
            # dichiara: cosi' il flusso resta leggibile e l'assunzione e' esplicita.
            quote_civ = cons21[cons21["settore"] == "Civile"].set_index("vettore")["valore"]
            if quote_civ.sum() > 0:
                for vettore, quota in (quote_civ / quote_civ.sum()).items():
                    c45.append((f"{vettore} (stima)", "Civile", civ45 * quota))
            else:
                c45.append(("Civile, composizione non nota", "Civile", civ45))

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
            "e la composizione del civile al 2045 è una ripartizione a quote 2021, "
            "non una previsione del piano."
        )


def _scheda_12():
    st.subheader("Le emissioni di tutta la regione, non solo dell'elettrico")
    st.caption(f"Fonti: {DOC.FONTE_EMISSIONI}; {DOC.FONTE_INVENTARIO}.")

    em_tot_df = pd.DataFrame(DOC.EMISSIONI_TOTALI_FVG.items(), columns=["anno", "kt"])
    ultimo_anno = int(em_tot_df["anno"].max())
    ultimo_val = float(em_tot_df.loc[em_tot_df["anno"].idxmax(), "kt"])
    netto = ultimo_val * (1 - DOC.ASSORBIMENTI_FORESTALI / 100)

    e = st.columns(5)
    e[0].metric(f"Gas serra lordi ({ultimo_anno})", f"{ultimo_val / 1000:.1f} Mt CO₂eq")
    e[1].metric("Assorbimenti forestali", f"−{DOC.ASSORBIMENTI_FORESTALI}%",
                f"media italiana −{DOC.ASSORBIMENTI_ITALIA}%")
    e[2].metric("Emissioni nette", f"{netto / 1000:.1f} Mt CO₂eq")
    e[3].metric("Pro capite", f"{DOC.EMISSIONI_PRO_CAPITE_2019:.1f} t/ab")
    e[4].metric("Neutralità", DOC.TARGET_FVGREEN["anno_neutralita"], "Legge FVGreen")

    # ------------------------------------------------------------ Sankey
    st.subheader("Da dove vengono, e cosa le compensa")
    st.caption(
        "Ogni flusso è una quota del totale regionale. A sinistra le attività, al centro "
        "le quattro macrocategorie IPCC, a destra il bilancio netto dopo gli assorbimenti "
        "forestali. Inventario ARPA FVG, anno 2021."
    )

    voci, macro = [], []
    for k, v in DOC.EMISSIONI_ENERGIA.items():
        voci.append((k, "Energia", v))
    voci.append(("Agricoltura e uso del suolo", "AFOLU (agricoltura e uso del suolo)",
                 DOC.EMISSIONI_MACRO["AFOLU (agricoltura e uso del suolo)"]))
    voci.append(("Processi industriali", "IPPU (processi industriali)",
                 DOC.EMISSIONI_MACRO["IPPU (processi industriali)"]))
    voci.append(("Trattamento dei rifiuti", "Rifiuti", DOC.EMISSIONI_MACRO["Rifiuti"]))

    attivita = [v[0] for v in voci]
    macrocat = list(DOC.EMISSIONI_MACRO)
    nodi_e = attivita + macrocat + ["Emissioni lorde", "Assorbimenti forestali",
                                    "Emissioni nette in atmosfera"]
    ie = {n: i for i, n in enumerate(nodi_e)}
    palette = {"Trasporti": "#EF4444", "Riscaldamento": "#F97316",
               "Industrie manifatturiere": "#4B5563", "Industrie energetiche": "#FACC15",
               "Emissioni fuggitive": "#9CA3AF", "Agricoltura e uso del suolo": "#22C55E",
               "Processi industriali": "#A855F7", "Trattamento dei rifiuti": "#78716C"}
    colori_e = [palette.get(a, "#9CA3AF") for a in attivita] + \
               ["#DC2626", "#16A34A", "#7C3AED", "#78716C"][:len(macrocat)] + \
               ["#111827", "#16A34A", "#DC2626"]

    se, te, ve, ce = [], [], [], []

    def le(a, b, v, colore):
        if v > 0:
            se.append(ie[a]); te.append(ie[b]); ve.append(float(v)); ce.append(colore)

    for nome, mcat, quota in voci:
        le(nome, mcat, quota, "rgba(220,38,38,0.22)")
    for m in macrocat:
        le(m, "Emissioni lorde", DOC.EMISSIONI_MACRO[m], "rgba(17,24,39,0.20)")
    le("Emissioni lorde", "Assorbimenti forestali", DOC.ASSORBIMENTI_FORESTALI,
       "rgba(22,163,74,0.35)")
    le("Emissioni lorde", "Emissioni nette in atmosfera",
       100 - DOC.ASSORBIMENTI_FORESTALI, "rgba(220,38,38,0.28)")

    fig = go.Figure(go.Sankey(
        node=dict(pad=16, thickness=18, label=nodi_e, color=colori_e,
                  line=dict(color="rgba(0,0,0,0.15)", width=0.5)),
        link=dict(source=se, target=te, value=ve, color=ce,
                  hovertemplate="%{value:.1f}% del totale<extra></extra>"),
    ))
    fig.update_layout(height=520, font_size=12, margin=dict(t=20, b=20, l=10, r=10))
    grafico(fig, DOC.FONTE_INVENTARIO,
            "Le quote della macrocategoria Energia sommano a 84,5% e non a 86% per arrotondamenti.")

    # ------------------------------------------------- dettaglio e trasporti
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**I quattro ambiti dell'Energia si equivalgono quasi**")
        en = pd.DataFrame(DOC.EMISSIONI_ENERGIA.items(), columns=["Ambito", "% del totale"])
        fig = px.bar(en.sort_values("% del totale"), x="% del totale", y="Ambito",
                     orientation="h", text_auto=".1f", color="Ambito",
                     color_discrete_map=palette)
        fig.update_traces(cliponaxis=False)
        fig.update_layout(showlegend=False, height=320, yaxis_title=None, **PLOT)
        grafico(fig, DOC.FONTE_INVENTARIO)

    with c2:
        st.markdown("**Dentro il trasporto su strada comandano le automobili**")
        tr = pd.DataFrame(DOC.TRASPORTO_STRADA.items(), columns=["Mezzo", "quota"])
        tr["% del totale regionale"] = tr["quota"] * DOC.TRASPORTO_STRADA_QUOTA / 100
        fig = px.pie(tr, values="quota", names="Mezzo", hole=0.5,
                     color_discrete_sequence=["#EF4444", "#F97316", "#FBBF24", "#FCD34D"])
        fig.update_traces(textinfo="percent")
        fig.update_layout(height=320, **PLOT)
        grafico(fig, DOC.FONTE_INVENTARIO,
                f"Il trasporto su strada vale il {DOC.TRASPORTO_STRADA_QUOTA}% del totale regionale.")

    st.info(
        f"**Le automobili private da sole fanno circa il "
        f"{DOC.TRASPORTO_STRADA['Autovetture'] * DOC.TRASPORTO_STRADA_QUOTA / 100:.0f}% "
        "delle emissioni regionali** — più del settore elettrico intero. È il numero che "
        "spiega perché la decarbonizzazione del FVG non si gioca sulle centrali: quelle "
        "pesano per il 17,8%, e stanno già calando da sole con la chiusura di Monfalcone. "
        "Si gioca su come ci si muove e su come si scaldano le case."
    )

    # ------------------------------------------------------------ serie storica
    st.subheader("La serie storica, con le sue cautele")
    fig = px.bar(em_tot_df, x="anno", y="kt", text_auto=".0f",
                 color_discrete_sequence=["#6B7280"])
    fig.add_scatter(x=[2045], y=[0], mode="markers+text", text=["neutralità 2045"],
                    textposition="top center", marker=dict(size=14, color="#22C55E"),
                    name="Obiettivo FVGreen")
    fig.update_traces(cliponaxis=False)
    fig.update_layout(height=360, yaxis_title="kt CO₂eq", xaxis_title=None, **PLOT)
    grafico(fig, DOC.FONTE_EMISSIONI)

    st.warning(
        "ISPRA avverte che la metodologia è cambiata nel tempo: i confronti fra anni "
        f"lontani sono indicativi. Il dato solido è l'ordine di grandezza — "
        f"**{ultimo_val / 1000:.1f} Mt CO₂eq lordi** contro gli "
        f"**{em_tot:.2f} Mt** del solo settore elettrico nel {anno}. "
        f"Gli assorbimenti forestali ne compensano circa un quarto, contro un decimo della "
        "media nazionale: è l'effetto dei 327.000 ettari di bosco. Ma ARPA avverte che gli "
        "alberi non bastano, perché la loro azione può ridursi di colpo per incendi o "
        "parassitosi."
    )

    # ------------------------------------------------ consumi finali per settore
    st.subheader("Perché il FVG emette così: la struttura dei consumi")
    conf = pd.DataFrame([
        {"Settore": k, "Friuli-Venezia Giulia": v[0], "Italia": v[1]}
        for k, v in DOC.QUOTE_SETTORE_CONFRONTO.items()
    ]).melt(id_vars="Settore", var_name="Area", value_name="% dei consumi finali")
    fig = px.bar(conf, x="Settore", y="% dei consumi finali", color="Area", barmode="group",
                 text_auto=".1f",
                 color_discrete_map={"Friuli-Venezia Giulia": "#2563EB", "Italia": "#9CA3AF"})
    fig.update_traces(cliponaxis=False)
    fig.update_layout(height=340, xaxis_title=None, **PLOT)
    grafico(fig, "EUROSTAT ed ENEA, ripresi nel Piano Energetico Regionale FVG")

    st.caption(
        "L'industria assorbe il **40%** dei consumi finali contro il 22% italiano, i "
        "trasporti il **19,4%** contro il 31,2%. Il FVG non emette poco nei trasporti: "
        "emette molto nell'industria, e questo comprime la quota relativa degli altri settori."
    )


def _scheda_13():
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

    # ------------------------------------------------------- scenari futuri
    st.divider()
    st.subheader("Cosa succede se: gli scenari climatici")
    st.caption(
        "Gli scenari RCP descrivono traiettorie di emissioni globali fino al 2100. "
        "Non sono previsioni: sono ipotesi su quanto il mondo deciderà di ridurre."
    )
    for nome, descr in DOC.SCENARI_RCP.items():
        st.markdown(f"- **{nome}** — {descr}")

    st.markdown("**L'effetto sull'energia si misura in gradi giorno**")
    st.caption(
        "I gradi giorno di riscaldamento (HDD) dicono quanta energia serve per scaldare, "
        "quelli di raffrescamento (CDD) quanta per raffrescare. Riferimento 1976-2005, "
        "proiezioni della piattaforma CLiNE di ARPA FVG."
    )

    gg = DOC.GRADI_GIORNO
    g = st.columns(4)
    g[0].metric("Riscaldamento in pianura, oggi",
                f"{gg['riscaldamento_pianura_oggi']:,} HDD".replace(",", "."))
    g[1].metric("A fine secolo (RCP8.5)",
                f"{gg['riscaldamento_pianura_2100_rcp85']:,} HDD".replace(",", "."),
                f"{gg['riscaldamento_pianura_2100_rcp85'] - gg['riscaldamento_pianura_oggi']:+,}"
                .replace(",", "."))
    g[2].metric("Raffrescamento a Fagagna", f"+{gg['cdd_fagagna_rcp85_2071_2100']} CDD",
                "anomalia 2071-2100, RCP8.5")
    g[3].metric("Riscaldamento a Malborghetto", f"{gg['hdd_malborghetto_rcp85_2071_2100']} HDD",
                "anomalia 2071-2100, RCP8.5")

    bilancio = pd.DataFrame([
        {"Voce": "Riscaldamento invernale (HDD)",
         "Variazione": gg["riscaldamento_pianura_2100_rcp85"] - gg["riscaldamento_pianura_oggi"]},
        {"Voce": "Raffrescamento estivo (CDD)", "Variazione": gg["cdd_fagagna_rcp85_2071_2100"]},
    ])
    fig = px.bar(bilancio, x="Variazione", y="Voce", orientation="h", text_auto="+.0f",
                 color="Variazione", color_continuous_scale=["#2563EB", "#F3F4F6", "#DC2626"],
                 color_continuous_midpoint=0)
    fig.add_vline(x=0, line_color="#111827")
    fig.update_traces(cliponaxis=False)
    fig.update_layout(height=240, yaxis_title=None, coloraxis_showscale=False,
                      xaxis_title="gradi giorno, anomalia a fine secolo (RCP8.5)", **PLOT)
    grafico(fig, "ARPA FVG, piattaforma CLiNE",
            "Le due grandezze sono misurate in punti diversi e non sono direttamente sommabili.")

    st.info(
        f"**Si scalderà molto meno e si raffrescherà molto di più.** In pianura i gradi "
        f"giorno di riscaldamento scendono da circa {gg['riscaldamento_pianura_oggi']:,} a "
        f"{gg['riscaldamento_pianura_2100_rcp85']:,} a fine secolo nello scenario peggiore. ".replace(",", ".")
        + "Sembra un risparmio, ed è un risparmio di **gas**. Ma l'aumento del raffrescamento "
        "è un aumento di **elettricità**, concentrato nelle ore più calde del pomeriggio "
        "estivo: proprio quando la rete è già sotto sforzo e il fotovoltaico comincia a "
        "calare. Il saldo energetico può migliorare mentre il saldo **di potenza** peggiora.\n\n"
        f"Sempre nello scenario RCP8.5, buona parte della pianura passerebbe dalla zona "
        f"climatica **{DOC.ZONA_CLIMATICA['oggi'].split('—')[0].strip()}** alla "
        f"**{DOC.ZONA_CLIMATICA['rcp85_fine_secolo'].split('—')[0].strip()}**, con due ore "
        "in meno di riscaldamento consentito al giorno e due settimane in meno di stagione."
    )

    # ------------------------------------------------------- eventi estremi
    st.divider()
    st.subheader("Il 2025, evento per evento")
    st.caption(
        "Cronologia dei fenomeni meteorologici rilevanti registrati da ARPA FVG. "
        "La colonna di destra indica la gravità relativa, non un indice ufficiale."
    )

    ev = pd.DataFrame(DOC.EVENTI_2025, columns=["quando", "cosa", "dettaglio", "gravita"])
    fig = px.bar(ev, x="gravita", y="quando", orientation="h", color="gravita",
                 color_continuous_scale=["#FCD34D", "#F97316", "#DC2626"],
                 hover_name="cosa", text="cosa")
    fig.update_traces(textposition="inside", insidetextanchor="start", cliponaxis=False)
    fig.update_yaxes(categoryorder="array", categoryarray=list(ev["quando"])[::-1])
    fig.update_layout(height=400, yaxis_title=None, xaxis_title="gravità relativa",
                      coloraxis_showscale=False, **PLOT)
    grafico(fig, DOC.FONTE_CLIMA)

    for r in ev.itertuples():
        if r.dettaglio:
            with st.expander(f"{r.quando} — {r.cosa}"):
                st.markdown(r.dettaglio)

    st.error(
        "**L'evento del 16-17 novembre 2025 merita di essere ricordato.** Un sistema "
        "convettivo autorigenerante è rimasto fermo quasi dodici ore sul bacino dello Judrio, "
        "scaricando oltre **200 mm di pioggia**. Il torrente ha esondato allagando Versa con "
        "uno-due metri d'acqua e fango; a Brazzano di Cormòns una collina è franata sul centro "
        "abitato, **due vittime** e tre case distrutte. I modelli non l'avevano previsto: "
        "attendevano piogge orografiche sulle Prealpi, non in pianura. "
        "Un evento simile non accadeva dal 29 agosto 2003, l'alluvione della Val Canale."
    )

    # --------------------------------------------- catena di impatto energia
    st.divider()
    st.subheader("Come il clima colpisce il sistema energetico")
    st.caption(
        "Catena di impatto per produzione, trasporto e consumo di energia in Europa "
        "(EUCRA 2023, ripresa da ARPA FVG)."
    )
    cat = pd.DataFrame(DOC.CATENA_IMPATTO, columns=["Sottosistema", "Rischio", "Meccanismo"])
    for sotto in cat["Sottosistema"].unique():
        st.markdown(f"**{sotto}**")
        for r in cat[cat["Sottosistema"] == sotto].itertuples():
            st.markdown(f"- *{r.Rischio}* — {r.Meccanismo}")

    st.caption(
        "Fonte: EUCRA 2023 (Agenzia europea dell'ambiente), rielaborazione ARPA FVG. "
        "Il punto che tiene insieme tutta la catena è che i rischi si presentano insieme: "
        "l'ondata di calore riduce l'idroelettrico, abbassa il rendimento del termoelettrico, "
        "taglia la portata delle linee e alza la domanda, tutto nello stesso pomeriggio."
    )


def _scheda_14():
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
                          annotation_text=f"prezzo di riferimento {prezzo_rif} €/MWh",
                          annotation_position="top left")
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
                  annotation_text="soglia indicativa",
                  annotation_position="top left")
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


def _scheda_15():
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


# ------------------------------------------------------------- navigazione
# Sedici schede in fila diventano illeggibili: si raggruppano in sezioni e
# viene eseguita solo quella scelta. Ogni scheda e' una funzione, cosi' il
# codice delle altre non gira nemmeno: la pagina si apre molto piu' in fretta.
SEZIONI = [
    ('📊 Quadro generale', [0]),
    ('⚡ Elettricità e rinnovabili', [1, 3, 4, 7]),
    ('🔥 Termico, gas e bioenergie', [8, 9, 5, 6]),
    ('🔌 Reti e territorio', [2]),
    ('🌍 Clima ed emissioni', [12, 13]),
    ('🔮 Scenari e transizione', [11, 14, 10]),
    ('🗂 Dati e fonti', [15]),
]
NOMI_SCHEDE = ['📊 Panoramica', '⚡ Elettricità', '🔌 Reti', '☀️ Fotovoltaico', '🌱 Rinnovabili', '🌲 Biomasse', '♻️ Biometano', '💧 Idroelettrico', '🔥 Gas', '🔥 Termo & CO₂', '🧪 Idrogeno', '🔮 Scenari', '🌍 Emissioni', '🌡️ Clima', '📈 Transizione', '🗂 Dati']

_schede = {n: globals()[f"_scheda_{n}"] for n in range(len(NOMI_SCHEDE))}

with st.sidebar:
    st.divider()
    st.markdown("**Sezione**")
    _sezione = st.radio("Sezione", [s[0] for s in SEZIONI], label_visibility="collapsed")

_indici = dict(SEZIONI)[_sezione]
if len(_indici) == 1:
    _schede[_indici[0]]()
else:
    for _t, _i in zip(st.tabs([NOMI_SCHEDE[i] for i in _indici]), _indici):
        with _t:
            _schede[_i]()


# ================================================================ 1. PANORAMICA

# ================================================================ 2. ELETTRICITÀ

# ================================================================ 3. RINNOVABILI

# ================================================================ 4. TERMO & CO2

# ================================================================ 5. SANKEY

# ================================================================ 6. TREND

# ================================================================ 7. DATI

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

# ================================================================ SCENARI

# ================================================================ RETI

# ================================================================ IDROELETTRICO

# ================================================================ CLIMA

# ================================================================ FOTOVOLTAICO

# ================================================================ GAS

# ================================================================ IDROGENO

# ---- aggiunte alla scheda Scenari: il Sankey 2045

# ---- aggiunte alla scheda Reti: avanzamento, accumuli, distributori

# ---- mappa delle aree di influenza delle cabine primarie

# ---- Fotovoltaico: dove si potrebbe installare (dati RSE)

# ---- Idroelettrico: la mappa delle centrali

# ---- Reti: le inversioni di flusso

# ---- Emissioni: il quadro completo

# ---- Fotovoltaico: la pipeline autorizzativa e il suolo

# ================================================================ BIOMASSE

# ================================================================ BIOMETANO

# ---- Ipotesi di copertura (scheda Transizione)

# ---- Eolico: perché in FVG non c'è, e cosa cambierebbe

# ---- Eolico misurato: l'Atlante RSE (scheda Transizione)

# ---- Centrali termoelettriche (scheda Termo & CO2)
