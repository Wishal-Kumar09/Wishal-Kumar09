import json
import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_FILE = BASE_DIR / "data" / "contributions.json"
OUTPUT_FILE = BASE_DIR / "data" / "wishal_github_animation.gif"


# ============================================================
# LOAD DATA
# ============================================================

with open(DATA_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)


# Find daily contribution data automatically
contributions = next(
    value
    for value in data.values()
    if isinstance(value, list)
    and value
    and isinstance(value[0], dict)
    and "date" in value[0]
    and "count" in value[0]
)


total_contributions = data["total_contributions"]

current_streak = data["current_streak"]["length"]

longest_streak = data["longest_streak"]["length"]


# ============================================================
# IMAGE SETTINGS
# ============================================================

WIDTH = 900
HEIGHT = 360

CELL_SIZE = 13
GAP = 4

LEFT = 80
TOP = 150

BACKGROUND = "#0d1117"

TEXT = "#f0f6fc"
SECONDARY = "#8b949e"

EMPTY = "#161b22"


# ============================================================
# CONTRIBUTION COLORS
# ============================================================

def get_color(count):

    if count == 0:
        return "#161b22"

    if count <= 2:
        return "#0e4429"

    if count <= 4:
        return "#006d32"

    if count <= 6:
        return "#26a641"

    return "#39d353"


# ============================================================
# FONTS
# ============================================================

def get_font(size):

    possible_fonts = [
        "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ]

    for font_path in possible_fonts:

        if Path(font_path).exists():

            return ImageFont.truetype(
                font_path,
                size
            )

    return ImageFont.load_default()


TITLE_FONT = get_font(32)
STAT_FONT = get_font(18)
SMALL_FONT = get_font(14)


# ============================================================
# CALCULATE POSITIONS
# ============================================================

def get_position(date):

    weekday = date.weekday()

    start_date = datetime.date.fromisoformat(
        data["range"]["start"]
    )

    days_since_start = (
        date - start_date
    ).days

    week = days_since_start // 7

    x = LEFT + week * (CELL_SIZE + GAP)

    y = TOP + weekday * (CELL_SIZE + GAP)

    return x, y


# ============================================================
# CREATE FRAME
# ============================================================

def create_frame(visible_count):

    image = Image.new(
        "RGB",
        (WIDTH, HEIGHT),
        BACKGROUND
    )

    draw = ImageDraw.Draw(image)


    # --------------------------------------------------------
    # Title
    # --------------------------------------------------------

    draw.text(
        (LEFT, 35),
        "Hi, I'm Wishal",
        fill=TEXT,
        font=TITLE_FONT
    )


    draw.text(
        (LEFT, 82),
        "My GitHub contribution journey",
        fill=SECONDARY,
        font=STAT_FONT
    )


    # --------------------------------------------------------
    # Stats
    # --------------------------------------------------------

    stats_text = (
        f"{total_contributions} contributions   •   "
        f"{current_streak} day current streak   •   "
        f"{longest_streak} day longest streak"
    )

    draw.text(
        (LEFT, 112),
        stats_text,
        fill=SECONDARY,
        font=STAT_FONT
    )


    # --------------------------------------------------------
    # Contribution calendar
    # --------------------------------------------------------

    for index, item in enumerate(contributions):

        date = datetime.date.fromisoformat(
            item["date"]
        )

        count = item["count"]

        x, y = get_position(date)


        # Only reveal contribution squares
        # progressively.

        if index < visible_count:

            color = get_color(count)

        else:

            color = EMPTY


        draw.rounded_rectangle(
            [
                x,
                y,
                x + CELL_SIZE,
                y + CELL_SIZE
            ],
            radius=3,
            fill=color
        )


    # --------------------------------------------------------
    # Legend
    # --------------------------------------------------------

    legend_y = TOP + 7 * (CELL_SIZE + GAP) + 15

    draw.text(
        (LEFT, legend_y),
        "Less",
        fill=SECONDARY,
        font=SMALL_FONT
    )


    for i, count in enumerate([0, 1, 3, 5, 7]):

        x = LEFT + 40 + i * 22

        draw.rounded_rectangle(
            [
                x,
                legend_y + 2,
                x + CELL_SIZE,
                legend_y + 2 + CELL_SIZE
            ],
            radius=3,
            fill=get_color(count)
        )


    draw.text(
        (LEFT + 160, legend_y),
        "More",
        fill=SECONDARY,
        font=SMALL_FONT
    )


    return image


# ============================================================
# BUILD FRAMES
# ============================================================

frames = []


# Intro frames
for _ in range(15):

    frames.append(
        create_frame(0)
    )


# Contribution animation
for visible_count in range(
    0,
    len(contributions) + 1
):

    frames.append(
        create_frame(
            visible_count
        )
    )


# Hold final frame
for _ in range(30):

    frames.append(
        create_frame(
            len(contributions)
        )
    )


# ============================================================
# SAVE GIF
# ============================================================

frames[0].save(
    OUTPUT_FILE,
    save_all=True,
    append_images=frames[1:],
    duration=40,
    loop=0
)


print()
print("========================================")
print(" Animation created successfully!")
print("========================================")
print()
print(f"Output:")
print(OUTPUT_FILE)
print()
print(f"Contributions: {total_contributions}")
print(f"Current streak: {current_streak}")
print(f"Longest streak: {longest_streak}")
print()