"""
Seeds realistic IDV player + match data into parsed directories
so the pipeline can build fully populated Silver/Gold artifacts.
Run: python3 scripts/seed_idv_data.py
"""
from __future__ import annotations
import json
from pathlib import Path

PARSED_TM = Path("data/parsed/transfermarkt")
PARSED_FB = Path("data/parsed/fbref")
PARSED_TM.mkdir(parents=True, exist_ok=True)
PARSED_FB.mkdir(parents=True, exist_ok=True)


def write(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")


# ── IDV Squad ─────────────────────────────────────────────────────────────────
PLAYERS = [
    # name, preferred, position, dob, nationality, club, market_value, slug
    ("Luis Segovia", "Segovia", "Midfielder", "2001-03-15", "Ecuador", "Independiente del Valle", "€2.5m", "luis-segovia"),
    ("Renato Ibarra", "Ibarra", "Forward", "1991-08-20", "Ecuador", "Independiente del Valle", "€1.8m", "renato-ibarra"),
    ("Alexis Zapata", "Zapata", "Defender", "1999-11-04", "Ecuador", "Independiente del Valle", "€1.2m", "alexis-zapata"),
    ("Kendry Páez", "Páez", "Midfielder", "2007-05-11", "Ecuador", "Independiente del Valle", "€8.0m", "kendry-paez"),
    ("Willian Pacho", "Pacho", "Defender", "2001-10-16", "Ecuador", "Independiente del Valle", "€15.0m", "willian-pacho"),
    ("Piero Hincapié", "Hincapié", "Defender", "2002-01-09", "Ecuador", "Bayer Leverkusen", "€28.0m", "piero-hincapie"),
    ("Alan Minda", "Minda", "Forward", "2000-07-22", "Ecuador", "Independiente del Valle", "€1.5m", "alan-minda"),
    ("Sebastián Rodríguez", "Rodríguez", "Midfielder", "1998-04-17", "Ecuador", "Independiente del Valle", "€900k", "sebastian-rodriguez"),
    ("Carlos Gutiérrez", "Gutiérrez", "Defender", "1997-09-03", "Ecuador", "Independiente del Valle", "€700k", "carlos-gutierrez"),
    ("Jordy Caicedo", "Caicedo", "Forward", "1995-03-31", "Ecuador", "Independiente del Valle", "€800k", "jordy-caicedo"),
    ("Michael Espinoza", "Espinoza", "Midfielder", "2003-12-01", "Ecuador", "Independiente del Valle", "€1.1m", "michael-espinoza"),
    ("Pedro Velasco", "Velasco", "Goalkeeper", "1996-06-14", "Ecuador", "Independiente del Valle", "€600k", "pedro-velasco"),
    ("Óscar Zambrano", "Zambrano", "Midfielder", "2000-08-05", "Ecuador", "Independiente del Valle", "€1.3m", "oscar-zambrano"),
    ("Dylan Borrero", "Borrero", "Forward", "2000-09-10", "Ecuador", "Independiente del Valle", "€3.5m", "dylan-borrero"),
    ("Moisés Caicedo", "M. Caicedo", "Midfielder", "2001-11-02", "Ecuador", "Chelsea", "€120.0m", "moises-caicedo"),
    ("Cristian Pellerano", "Pellerano", "Midfielder", "1988-02-28", "Argentina", "Independiente del Valle", "€400k", "cristian-pellerano"),
    ("Gabriel Villamil", "Villamil", "Defender", "2002-04-19", "Ecuador", "Independiente del Valle", "€800k", "gabriel-villamil"),
    ("Tomás Molina", "Molina", "Forward", "2003-08-23", "Ecuador", "Independiente del Valle", "€1.0m", "tomas-molina"),
]

# Transfer history per player
TRANSFER_HISTORY = {
    "luis-segovia": [
        {"season": "2021/2022", "from_club": "Liga Deportiva Universitaria", "to_club": "Independiente del Valle", "fee": "€300k"},
    ],
    "piero-hincapie": [
        {"season": "2019/2020", "from_club": "Independiente del Valle", "to_club": "Talleres", "fee": "€1.5m"},
        {"season": "2021/2022", "from_club": "Talleres", "to_club": "Bayer Leverkusen", "fee": "€6m"},
        {"season": "2023/2024", "from_club": "Bayer Leverkusen", "to_club": "Bayer Leverkusen", "fee": "-"},
    ],
    "moises-caicedo": [
        {"season": "2020/2021", "from_club": "Independiente del Valle", "to_club": "Brighton & Hove Albion", "fee": "€5m"},
        {"season": "2023/2024", "from_club": "Brighton & Hove Albion", "to_club": "Chelsea", "fee": "€115m"},
    ],
    "willian-pacho": [
        {"season": "2022/2023", "from_club": "Independiente del Valle", "to_club": "Royal Antwerp", "fee": "€3m"},
        {"season": "2023/2024", "from_club": "Royal Antwerp", "to_club": "Eintracht Frankfurt", "fee": "€12m"},
    ],
    "kendry-paez": [
        {"season": "2024/2025", "from_club": "Independiente del Valle", "to_club": "Chelsea", "fee": "€16m", "transfer_type": "pre-contract"},
    ],
    "dylan-borrero": [
        {"season": "2021/2022", "from_club": "Independiente del Valle", "to_club": "Fluminense", "fee": "€1.8m"},
        {"season": "2022/2023", "from_club": "Fluminense", "to_club": "Independiente del Valle", "fee": "loan"},
    ],
}

# ── Match data ─────────────────────────────────────────────────────────────────
MATCH_STATS_BY_PLAYER: dict[str, list[dict]] = {
    "luis-segovia": [
        {"date": "2026-03-08", "competition": "Liga Pro Ecuador", "opp": "Barcelona SC", "mins": 90, "goals": 1, "assists": 2, "shots": 4, "passes": 52, "yc": 0, "rc": 0, "xg": 0.7, "xa": 0.6},
        {"date": "2026-03-15", "competition": "Copa Libertadores", "opp": "Palmeiras", "mins": 87, "goals": 0, "assists": 1, "shots": 2, "passes": 48, "yc": 1, "rc": 0, "xg": 0.2, "xa": 0.4},
        {"date": "2026-03-22", "competition": "Liga Pro Ecuador", "opp": "El Nacional", "mins": 90, "goals": 2, "assists": 0, "shots": 5, "passes": 44, "yc": 0, "rc": 0, "xg": 1.1, "xa": 0.1},
        {"date": "2026-03-29", "competition": "Copa Libertadores", "opp": "Flamengo", "mins": 72, "goals": 0, "assists": 1, "shots": 3, "passes": 41, "yc": 0, "rc": 0, "xg": 0.3, "xa": 0.5},
        {"date": "2026-04-05", "competition": "Liga Pro Ecuador", "opp": "Aucas", "mins": 90, "goals": 1, "assists": 1, "shots": 3, "passes": 55, "yc": 0, "rc": 0, "xg": 0.8, "xa": 0.3},
        {"date": "2026-04-12", "competition": "Copa Libertadores", "opp": "Atletico Mineiro", "mins": 90, "goals": 0, "assists": 2, "shots": 2, "passes": 50, "yc": 1, "rc": 0, "xg": 0.2, "xa": 0.9},
        {"date": "2026-04-19", "competition": "Liga Pro Ecuador", "opp": "Deportivo Cuenca", "mins": 90, "goals": 3, "assists": 0, "shots": 6, "passes": 47, "yc": 0, "rc": 0, "xg": 2.1, "xa": 0.0},
        {"date": "2026-04-26", "competition": "Copa Libertadores", "opp": "River Plate", "mins": 85, "goals": 0, "assists": 1, "shots": 4, "passes": 43, "yc": 0, "rc": 0, "xg": 0.5, "xa": 0.4},
    ],
    "renato-ibarra": [
        {"date": "2026-03-08", "competition": "Liga Pro Ecuador", "opp": "Barcelona SC", "mins": 78, "goals": 1, "assists": 1, "shots": 5, "passes": 32, "yc": 1, "rc": 0, "xg": 0.9, "xa": 0.4},
        {"date": "2026-03-15", "competition": "Copa Libertadores", "opp": "Palmeiras", "mins": 61, "goals": 0, "assists": 0, "shots": 2, "passes": 28, "yc": 0, "rc": 0, "xg": 0.3, "xa": 0.1},
        {"date": "2026-03-22", "competition": "Liga Pro Ecuador", "opp": "El Nacional", "mins": 90, "goals": 2, "assists": 1, "shots": 7, "passes": 30, "yc": 0, "rc": 0, "xg": 1.8, "xa": 0.3},
        {"date": "2026-04-05", "competition": "Liga Pro Ecuador", "opp": "Aucas", "mins": 90, "goals": 1, "assists": 0, "shots": 4, "passes": 33, "yc": 0, "rc": 0, "xg": 0.7, "xa": 0.0},
        {"date": "2026-04-12", "competition": "Copa Libertadores", "opp": "Atletico Mineiro", "mins": 68, "goals": 0, "assists": 1, "shots": 3, "passes": 27, "yc": 1, "rc": 0, "xg": 0.4, "xa": 0.5},
        {"date": "2026-04-19", "competition": "Liga Pro Ecuador", "opp": "Deportivo Cuenca", "mins": 90, "goals": 2, "assists": 2, "shots": 6, "passes": 35, "yc": 0, "rc": 0, "xg": 1.5, "xa": 0.6},
    ],
    "kendry-paez": [
        {"date": "2026-03-08", "competition": "Liga Pro Ecuador", "opp": "Barcelona SC", "mins": 90, "goals": 2, "assists": 3, "shots": 5, "passes": 68, "yc": 0, "rc": 0, "xg": 1.2, "xa": 1.1},
        {"date": "2026-03-15", "competition": "Copa Libertadores", "opp": "Palmeiras", "mins": 90, "goals": 1, "assists": 1, "shots": 4, "passes": 71, "yc": 0, "rc": 0, "xg": 0.8, "xa": 0.7},
        {"date": "2026-03-22", "competition": "Liga Pro Ecuador", "opp": "El Nacional", "mins": 90, "goals": 3, "assists": 1, "shots": 6, "passes": 65, "yc": 0, "rc": 0, "xg": 2.3, "xa": 0.4},
        {"date": "2026-03-29", "competition": "Copa Libertadores", "opp": "Flamengo", "mins": 90, "goals": 0, "assists": 2, "shots": 3, "passes": 73, "yc": 1, "rc": 0, "xg": 0.4, "xa": 1.2},
        {"date": "2026-04-05", "competition": "Liga Pro Ecuador", "opp": "Aucas", "mins": 90, "goals": 2, "assists": 2, "shots": 5, "passes": 70, "yc": 0, "rc": 0, "xg": 1.6, "xa": 0.8},
        {"date": "2026-04-12", "competition": "Copa Libertadores", "opp": "Atletico Mineiro", "mins": 90, "goals": 1, "assists": 0, "shots": 4, "passes": 66, "yc": 0, "rc": 0, "xg": 0.9, "xa": 0.3},
        {"date": "2026-04-19", "competition": "Liga Pro Ecuador", "opp": "Deportivo Cuenca", "mins": 90, "goals": 2, "assists": 3, "shots": 7, "passes": 72, "yc": 0, "rc": 0, "xg": 1.8, "xa": 1.3},
        {"date": "2026-04-26", "competition": "Copa Libertadores", "opp": "River Plate", "mins": 90, "goals": 1, "assists": 1, "shots": 5, "passes": 69, "yc": 0, "rc": 0, "xg": 1.1, "xa": 0.6},
    ],
    "willian-pacho": [
        {"date": "2026-03-08", "competition": "Liga Pro Ecuador", "opp": "Barcelona SC", "mins": 90, "goals": 0, "assists": 0, "shots": 1, "passes": 61, "yc": 1, "rc": 0, "xg": 0.1, "xa": 0.0},
        {"date": "2026-03-15", "competition": "Copa Libertadores", "opp": "Palmeiras", "mins": 90, "goals": 0, "assists": 1, "shots": 1, "passes": 58, "yc": 0, "rc": 0, "xg": 0.1, "xa": 0.2},
        {"date": "2026-03-22", "competition": "Liga Pro Ecuador", "opp": "El Nacional", "mins": 90, "goals": 1, "assists": 0, "shots": 2, "passes": 65, "yc": 0, "rc": 0, "xg": 0.4, "xa": 0.0},
        {"date": "2026-03-29", "competition": "Copa Libertadores", "opp": "Flamengo", "mins": 90, "goals": 0, "assists": 0, "shots": 1, "passes": 60, "yc": 1, "rc": 0, "xg": 0.1, "xa": 0.1},
        {"date": "2026-04-05", "competition": "Liga Pro Ecuador", "opp": "Aucas", "mins": 90, "goals": 0, "assists": 0, "shots": 0, "passes": 70, "yc": 0, "rc": 0, "xg": 0.0, "xa": 0.0},
        {"date": "2026-04-12", "competition": "Copa Libertadores", "opp": "Atletico Mineiro", "mins": 90, "goals": 0, "assists": 0, "shots": 1, "passes": 62, "yc": 0, "rc": 0, "xg": 0.1, "xa": 0.1},
    ],
    "alexis-zapata": [
        {"date": "2026-03-08", "competition": "Liga Pro Ecuador", "opp": "Barcelona SC", "mins": 90, "goals": 0, "assists": 1, "shots": 1, "passes": 55, "yc": 0, "rc": 0, "xg": 0.1, "xa": 0.3},
        {"date": "2026-03-22", "competition": "Liga Pro Ecuador", "opp": "El Nacional", "mins": 90, "goals": 1, "assists": 0, "shots": 2, "passes": 52, "yc": 1, "rc": 0, "xg": 0.5, "xa": 0.0},
        {"date": "2026-04-05", "competition": "Liga Pro Ecuador", "opp": "Aucas", "mins": 90, "goals": 0, "assists": 0, "shots": 0, "passes": 59, "yc": 0, "rc": 0, "xg": 0.0, "xa": 0.0},
        {"date": "2026-04-19", "competition": "Liga Pro Ecuador", "opp": "Deportivo Cuenca", "mins": 90, "goals": 0, "assists": 1, "shots": 1, "passes": 54, "yc": 0, "rc": 0, "xg": 0.1, "xa": 0.2},
    ],
    "alan-minda": [
        {"date": "2026-03-08", "competition": "Liga Pro Ecuador", "opp": "Barcelona SC", "mins": 82, "goals": 1, "assists": 0, "shots": 4, "passes": 28, "yc": 0, "rc": 0, "xg": 0.8, "xa": 0.0},
        {"date": "2026-03-22", "competition": "Liga Pro Ecuador", "opp": "El Nacional", "mins": 90, "goals": 1, "assists": 1, "shots": 5, "passes": 30, "yc": 0, "rc": 0, "xg": 0.9, "xa": 0.4},
        {"date": "2026-04-05", "competition": "Liga Pro Ecuador", "opp": "Aucas", "mins": 74, "goals": 0, "assists": 0, "shots": 2, "passes": 25, "yc": 1, "rc": 0, "xg": 0.3, "xa": 0.0},
        {"date": "2026-04-19", "competition": "Liga Pro Ecuador", "opp": "Deportivo Cuenca", "mins": 90, "goals": 2, "assists": 1, "shots": 6, "passes": 32, "yc": 0, "rc": 0, "xg": 1.6, "xa": 0.5},
        {"date": "2026-04-26", "competition": "Copa Libertadores", "opp": "River Plate", "mins": 60, "goals": 0, "assists": 0, "shots": 2, "passes": 22, "yc": 0, "rc": 0, "xg": 0.2, "xa": 0.1},
    ],
    "oscar-zambrano": [
        {"date": "2026-03-08", "competition": "Liga Pro Ecuador", "opp": "Barcelona SC", "mins": 90, "goals": 1, "assists": 1, "shots": 3, "passes": 58, "yc": 0, "rc": 0, "xg": 0.6, "xa": 0.4},
        {"date": "2026-03-15", "competition": "Copa Libertadores", "opp": "Palmeiras", "mins": 90, "goals": 0, "assists": 0, "shots": 2, "passes": 61, "yc": 1, "rc": 0, "xg": 0.2, "xa": 0.1},
        {"date": "2026-03-22", "competition": "Liga Pro Ecuador", "opp": "El Nacional", "mins": 90, "goals": 0, "assists": 2, "shots": 2, "passes": 64, "yc": 0, "rc": 0, "xg": 0.3, "xa": 0.7},
        {"date": "2026-04-05", "competition": "Liga Pro Ecuador", "opp": "Aucas", "mins": 90, "goals": 1, "assists": 0, "shots": 4, "passes": 55, "yc": 0, "rc": 0, "xg": 0.7, "xa": 0.0},
        {"date": "2026-04-19", "competition": "Liga Pro Ecuador", "opp": "Deportivo Cuenca", "mins": 90, "goals": 0, "assists": 1, "shots": 1, "passes": 60, "yc": 0, "rc": 0, "xg": 0.2, "xa": 0.4},
    ],
    "dylan-borrero": [
        {"date": "2026-03-08", "competition": "Liga Pro Ecuador", "opp": "Barcelona SC", "mins": 90, "goals": 2, "assists": 1, "shots": 6, "passes": 35, "yc": 0, "rc": 0, "xg": 1.5, "xa": 0.5},
        {"date": "2026-03-15", "competition": "Copa Libertadores", "opp": "Palmeiras", "mins": 79, "goals": 1, "assists": 0, "shots": 4, "passes": 30, "yc": 0, "rc": 0, "xg": 0.9, "xa": 0.1},
        {"date": "2026-03-22", "competition": "Liga Pro Ecuador", "opp": "El Nacional", "mins": 90, "goals": 1, "assists": 2, "shots": 5, "passes": 38, "yc": 0, "rc": 0, "xg": 1.1, "xa": 0.8},
        {"date": "2026-04-05", "competition": "Liga Pro Ecuador", "opp": "Aucas", "mins": 88, "goals": 0, "assists": 1, "shots": 3, "passes": 33, "yc": 1, "rc": 0, "xg": 0.4, "xa": 0.3},
        {"date": "2026-04-19", "competition": "Liga Pro Ecuador", "opp": "Deportivo Cuenca", "mins": 90, "goals": 3, "assists": 0, "shots": 7, "passes": 40, "yc": 0, "rc": 0, "xg": 2.2, "xa": 0.0},
        {"date": "2026-04-26", "competition": "Copa Libertadores", "opp": "River Plate", "mins": 90, "goals": 1, "assists": 1, "shots": 5, "passes": 36, "yc": 0, "rc": 0, "xg": 1.0, "xa": 0.4},
    ],
    "sebastian-rodriguez": [
        {"date": "2026-03-08", "competition": "Liga Pro Ecuador", "opp": "Barcelona SC", "mins": 90, "goals": 0, "assists": 1, "shots": 2, "passes": 62, "yc": 1, "rc": 0, "xg": 0.2, "xa": 0.4},
        {"date": "2026-03-22", "competition": "Liga Pro Ecuador", "opp": "El Nacional", "mins": 90, "goals": 0, "assists": 0, "shots": 1, "passes": 65, "yc": 0, "rc": 0, "xg": 0.1, "xa": 0.0},
        {"date": "2026-04-05", "competition": "Liga Pro Ecuador", "opp": "Aucas", "mins": 83, "goals": 1, "assists": 0, "shots": 3, "passes": 59, "yc": 0, "rc": 0, "xg": 0.6, "xa": 0.0},
        {"date": "2026-04-19", "competition": "Liga Pro Ecuador", "opp": "Deportivo Cuenca", "mins": 90, "goals": 0, "assists": 2, "shots": 2, "passes": 68, "yc": 0, "rc": 0, "xg": 0.2, "xa": 0.6},
    ],
    "michael-espinoza": [
        {"date": "2026-03-08", "competition": "Liga Pro Ecuador", "opp": "Barcelona SC", "mins": 67, "goals": 0, "assists": 0, "shots": 2, "passes": 41, "yc": 0, "rc": 0, "xg": 0.3, "xa": 0.1},
        {"date": "2026-03-22", "competition": "Liga Pro Ecuador", "opp": "El Nacional", "mins": 90, "goals": 1, "assists": 1, "shots": 3, "passes": 45, "yc": 0, "rc": 0, "xg": 0.7, "xa": 0.4},
        {"date": "2026-04-05", "competition": "Liga Pro Ecuador", "opp": "Aucas", "mins": 90, "goals": 0, "assists": 0, "shots": 1, "passes": 44, "yc": 1, "rc": 0, "xg": 0.1, "xa": 0.0},
        {"date": "2026-04-19", "competition": "Liga Pro Ecuador", "opp": "Deportivo Cuenca", "mins": 75, "goals": 1, "assists": 0, "shots": 3, "passes": 40, "yc": 0, "rc": 0, "xg": 0.6, "xa": 0.1},
    ],
    "carlos-gutierrez": [
        {"date": "2026-03-08", "competition": "Liga Pro Ecuador", "opp": "Barcelona SC", "mins": 90, "goals": 0, "assists": 0, "shots": 0, "passes": 50, "yc": 0, "rc": 0, "xg": 0.0, "xa": 0.0},
        {"date": "2026-03-22", "competition": "Liga Pro Ecuador", "opp": "El Nacional", "mins": 90, "goals": 0, "assists": 1, "shots": 1, "passes": 54, "yc": 1, "rc": 0, "xg": 0.1, "xa": 0.2},
        {"date": "2026-04-05", "competition": "Liga Pro Ecuador", "opp": "Aucas", "mins": 90, "goals": 0, "assists": 0, "shots": 1, "passes": 52, "yc": 0, "rc": 0, "xg": 0.1, "xa": 0.0},
        {"date": "2026-04-19", "competition": "Liga Pro Ecuador", "opp": "Deportivo Cuenca", "mins": 90, "goals": 0, "assists": 0, "shots": 0, "passes": 58, "yc": 0, "rc": 0, "xg": 0.0, "xa": 0.0},
    ],
    "jordy-caicedo": [
        {"date": "2026-03-08", "competition": "Liga Pro Ecuador", "opp": "Barcelona SC", "mins": 72, "goals": 1, "assists": 0, "shots": 3, "passes": 22, "yc": 0, "rc": 0, "xg": 0.8, "xa": 0.0},
        {"date": "2026-03-22", "competition": "Liga Pro Ecuador", "opp": "El Nacional", "mins": 90, "goals": 2, "assists": 0, "shots": 5, "passes": 25, "yc": 1, "rc": 0, "xg": 1.4, "xa": 0.0},
        {"date": "2026-04-05", "competition": "Liga Pro Ecuador", "opp": "Aucas", "mins": 81, "goals": 0, "assists": 1, "shots": 2, "passes": 20, "yc": 0, "rc": 0, "xg": 0.3, "xa": 0.4},
        {"date": "2026-04-19", "competition": "Liga Pro Ecuador", "opp": "Deportivo Cuenca", "mins": 90, "goals": 1, "assists": 1, "shots": 4, "passes": 24, "yc": 0, "rc": 0, "xg": 0.9, "xa": 0.5},
    ],
    "pedro-velasco": [
        {"date": "2026-03-08", "competition": "Liga Pro Ecuador", "opp": "Barcelona SC", "mins": 90, "goals": 0, "assists": 0, "shots": 0, "passes": 35, "yc": 0, "rc": 0, "xg": 0.0, "xa": 0.0},
        {"date": "2026-03-15", "competition": "Copa Libertadores", "opp": "Palmeiras", "mins": 90, "goals": 0, "assists": 0, "shots": 0, "passes": 30, "yc": 0, "rc": 0, "xg": 0.0, "xa": 0.0},
        {"date": "2026-03-22", "competition": "Liga Pro Ecuador", "opp": "El Nacional", "mins": 90, "goals": 0, "assists": 0, "shots": 0, "passes": 40, "yc": 1, "rc": 0, "xg": 0.0, "xa": 0.0},
        {"date": "2026-04-05", "competition": "Liga Pro Ecuador", "opp": "Aucas", "mins": 90, "goals": 0, "assists": 0, "shots": 0, "passes": 38, "yc": 0, "rc": 0, "xg": 0.0, "xa": 0.0},
        {"date": "2026-04-12", "competition": "Copa Libertadores", "opp": "Atletico Mineiro", "mins": 90, "goals": 0, "assists": 0, "shots": 0, "passes": 33, "yc": 0, "rc": 0, "xg": 0.0, "xa": 0.0},
        {"date": "2026-04-19", "competition": "Liga Pro Ecuador", "opp": "Deportivo Cuenca", "mins": 90, "goals": 0, "assists": 0, "shots": 0, "passes": 42, "yc": 0, "rc": 0, "xg": 0.0, "xa": 0.0},
    ],
    "gabriel-villamil": [
        {"date": "2026-03-08", "competition": "Liga Pro Ecuador", "opp": "Barcelona SC", "mins": 90, "goals": 0, "assists": 0, "shots": 1, "passes": 48, "yc": 0, "rc": 0, "xg": 0.1, "xa": 0.0},
        {"date": "2026-03-22", "competition": "Liga Pro Ecuador", "opp": "El Nacional", "mins": 90, "goals": 0, "assists": 1, "shots": 1, "passes": 52, "yc": 1, "rc": 0, "xg": 0.1, "xa": 0.3},
        {"date": "2026-04-05", "competition": "Liga Pro Ecuador", "opp": "Aucas", "mins": 85, "goals": 1, "assists": 0, "shots": 2, "passes": 46, "yc": 0, "rc": 0, "xg": 0.5, "xa": 0.0},
        {"date": "2026-04-19", "competition": "Liga Pro Ecuador", "opp": "Deportivo Cuenca", "mins": 90, "goals": 0, "assists": 0, "shots": 0, "passes": 55, "yc": 0, "rc": 0, "xg": 0.0, "xa": 0.0},
    ],
    "tomas-molina": [
        {"date": "2026-03-08", "competition": "Liga Pro Ecuador", "opp": "Barcelona SC", "mins": 55, "goals": 1, "assists": 0, "shots": 3, "passes": 18, "yc": 0, "rc": 0, "xg": 0.7, "xa": 0.0},
        {"date": "2026-03-22", "competition": "Liga Pro Ecuador", "opp": "El Nacional", "mins": 68, "goals": 0, "assists": 1, "shots": 2, "passes": 22, "yc": 0, "rc": 0, "xg": 0.3, "xa": 0.4},
        {"date": "2026-04-05", "competition": "Liga Pro Ecuador", "opp": "Aucas", "mins": 72, "goals": 1, "assists": 0, "shots": 4, "passes": 19, "yc": 1, "rc": 0, "xg": 0.8, "xa": 0.0},
        {"date": "2026-04-19", "competition": "Liga Pro Ecuador", "opp": "Deportivo Cuenca", "mins": 80, "goals": 0, "assists": 1, "shots": 2, "passes": 24, "yc": 0, "rc": 0, "xg": 0.2, "xa": 0.5},
    ],
    "cristian-pellerano": [
        {"date": "2026-03-08", "competition": "Liga Pro Ecuador", "opp": "Barcelona SC", "mins": 90, "goals": 0, "assists": 1, "shots": 1, "passes": 72, "yc": 1, "rc": 0, "xg": 0.1, "xa": 0.3},
        {"date": "2026-03-22", "competition": "Liga Pro Ecuador", "opp": "El Nacional", "mins": 90, "goals": 0, "assists": 0, "shots": 1, "passes": 75, "yc": 0, "rc": 0, "xg": 0.1, "xa": 0.1},
        {"date": "2026-04-05", "competition": "Liga Pro Ecuador", "opp": "Aucas", "mins": 90, "goals": 0, "assists": 1, "shots": 0, "passes": 78, "yc": 0, "rc": 0, "xg": 0.0, "xa": 0.2},
        {"date": "2026-04-19", "competition": "Liga Pro Ecuador", "opp": "Deportivo Cuenca", "mins": 90, "goals": 0, "assists": 0, "shots": 1, "passes": 71, "yc": 0, "rc": 0, "xg": 0.1, "xa": 0.0},
    ],
    # Moises Caicedo / Piero Hincapie (at other clubs but historically IDV)
    "moises-caicedo": [
        {"date": "2025-10-05", "competition": "Premier League", "opp": "Arsenal", "mins": 90, "goals": 0, "assists": 1, "shots": 3, "passes": 88, "yc": 0, "rc": 0, "xg": 0.2, "xa": 0.5},
        {"date": "2025-10-19", "competition": "Premier League", "opp": "Man City", "mins": 90, "goals": 1, "assists": 0, "shots": 4, "passes": 92, "yc": 1, "rc": 0, "xg": 0.6, "xa": 0.1},
        {"date": "2025-11-02", "competition": "Premier League", "opp": "Tottenham", "mins": 90, "goals": 0, "assists": 2, "shots": 2, "passes": 85, "yc": 0, "rc": 0, "xg": 0.2, "xa": 0.8},
        {"date": "2025-11-23", "competition": "Champions League", "opp": "Real Madrid", "mins": 90, "goals": 0, "assists": 0, "shots": 2, "passes": 79, "yc": 1, "rc": 0, "xg": 0.2, "xa": 0.1},
        {"date": "2025-12-07", "competition": "Premier League", "opp": "Liverpool", "mins": 85, "goals": 0, "assists": 1, "shots": 1, "passes": 86, "yc": 0, "rc": 0, "xg": 0.1, "xa": 0.4},
    ],
    "piero-hincapie": [
        {"date": "2025-10-05", "competition": "Bundesliga", "opp": "Bayern Munich", "mins": 90, "goals": 0, "assists": 0, "shots": 1, "passes": 70, "yc": 1, "rc": 0, "xg": 0.1, "xa": 0.0},
        {"date": "2025-10-19", "competition": "Bundesliga", "opp": "Dortmund", "mins": 90, "goals": 1, "assists": 0, "shots": 2, "passes": 68, "yc": 0, "rc": 0, "xg": 0.5, "xa": 0.0},
        {"date": "2025-11-02", "competition": "Champions League", "opp": "Barcelona", "mins": 90, "goals": 0, "assists": 1, "shots": 1, "passes": 72, "yc": 0, "rc": 0, "xg": 0.1, "xa": 0.3},
        {"date": "2025-11-23", "competition": "Bundesliga", "opp": "RB Leipzig", "mins": 90, "goals": 0, "assists": 0, "shots": 1, "passes": 65, "yc": 1, "rc": 0, "xg": 0.1, "xa": 0.1},
    ],
}


def make_fbref_payload(player_name: str, club: str, stat: dict, match_id: str, competition: str) -> dict:
    return {
        "match": {
            "source_url": f"https://fbref.com/en/matches/{match_id}",
            "external_id": match_id,
            "competition": competition,
            "season": "2025-2026",
            "match_date": stat["date"],
            "home_club": club,
            "away_club": stat["opp"],
            "home_score": stat["goals"] + 1,
            "away_score": 0,
            "venue": "Estadio Banco Guayaquil",
        },
        "player_match_stats": [
            {
                "source_url": f"https://fbref.com/en/matches/{match_id}",
                "table_id": "stats_standard",
                "player_name": player_name,
                "club_name": club,
                "minutes": stat["mins"],
                "goals": stat["goals"],
                "assists": stat["assists"],
                "yellow_cards": stat["yc"],
                "red_cards": stat["rc"],
                "shots": stat["shots"],
                "passes_completed": stat["passes"],
                "xg": stat["xg"],
                "xa": stat["xa"],
                "progressive_carries": max(0, stat["shots"] - 1),
                "progressive_passes": max(0, stat["passes"] // 10),
                "progressive_receptions": max(0, stat["passes"] // 15),
                "carries_into_final_third": max(0, stat["shots"] // 2),
                "passes_into_final_third": max(0, stat["passes"] // 12),
                "carries_into_penalty_area": max(0, stat["shots"] // 3),
                "passes_into_penalty_area": max(0, stat["passes"] // 20),
            }
        ],
        "player_per_90": [
            {
                "source_url": f"https://fbref.com/en/matches/{match_id}",
                "table_id": "stats_per90",
                "player_name": player_name,
                "club_name": club,
                "metrics": {
                    "goals": round(stat["goals"] / max(stat["mins"], 1) * 90, 3),
                    "assists": round(stat["assists"] / max(stat["mins"], 1) * 90, 3),
                    "xg": round(stat["xg"] / max(stat["mins"], 1) * 90, 3),
                    "xa": round(stat["xa"] / max(stat["mins"], 1) * 90, 3),
                },
            }
        ],
    }


def main() -> None:
    # Build lookup
    player_by_slug = {p[7]: p for p in PLAYERS}

    # Write Transfermarkt profile payloads
    for name, preferred, position, dob, nationality, club, market_value, slug in PLAYERS:
        transfers = TRANSFER_HISTORY.get(slug, [])
        tm_transfers = []
        for t in transfers:
            tm_transfers.append({
                "source_url": f"https://www.transfermarkt.com/{slug}/transfers/spieler/1000",
                "season": t.get("season", "2025/2026"),
                "date": "2025-01-01",
                "from_club": t.get("from_club", club),
                "to_club": t.get("to_club", club),
                "market_value": market_value,
                "fee": t.get("fee", "-"),
            })
        if not tm_transfers:
            tm_transfers.append({
                "source_url": f"https://www.transfermarkt.com/{slug}/transfers/spieler/1000",
                "season": "2025/2026",
                "date": "2025-01-01",
                "from_club": club,
                "to_club": club,
                "market_value": market_value,
                "fee": "-",
            })

        payload = {
            "profile": {
                "source_url": f"https://www.transfermarkt.com/{slug}/profil/spieler/1000",
                "player_name": name,
                "preferred_name": preferred,
                "position": position,
                "date_of_birth": dob,
                "nationality": nationality,
                "current_club": club,
                "market_value": market_value,
            },
            "transfers": tm_transfers,
        }
        write(PARSED_TM / f"{slug}.json", payload)

    # Write FBref match payloads
    total_matches = 0
    for slug, stats in MATCH_STATS_BY_PLAYER.items():
        if slug not in player_by_slug:
            continue
        p = player_by_slug[slug]
        name, preferred, position, dob, nationality, club, market_value, _ = p
        for i, stat in enumerate(stats):
            match_id = f"{slug}-match-{i+1:03d}"
            payload = make_fbref_payload(name, club, stat, match_id, stat["competition"])
            write(PARSED_FB / f"{match_id}.json", payload)
            total_matches += 1

    print(f"Seeded {len(PLAYERS)} player profiles → {PARSED_TM}")
    print(f"Seeded {total_matches} match payloads → {PARSED_FB}")


if __name__ == "__main__":
    main()
