
from PIL import Image, ImageDraw, ImageFont
import datetime
import os
from calendar import monthrange

# --- 1. РљРѕРЅСЃС‚Р°РЅС‚С‹ Рё РЅР°СЃС‚СЂРѕР№РєРё ---
IMG_WIDTH = 1600
IMG_HEIGHT = 900
OUTPUT_DIR = "output" # РР·РјРµРЅРµРЅР° РїР°РїРєР° РІС‹РІРѕРґР°
TARGET_YEAR = 2044 # Р“РѕРґ, РґР»СЏ РєРѕС‚РѕСЂРѕРіРѕ РіРµРЅРµСЂРёСЂСѓРµРј РєР°Р»РµРЅРґР°СЂСЊ

BACKGROUND_COLOR = (0, 0, 0) # Р§РµСЂРЅС‹Р№ С„РѕРЅ
INACTIVE_TEXT_COLOR = (120, 120, 120) # РћС‡РµРЅСЊ С‚РµРјРЅРѕ-СЃРµСЂС‹Р№ РґР»СЏ РЅРµР°РєС‚РёРІРЅРѕРіРѕ С‚РµРєСЃС‚Р°
INACTIVE_LINE_COLOR = (60, 60, 60) # РћС‡РµРЅСЊ С‚РµРјРЅРѕ-СЃРµСЂС‹Р№ РґР»СЏ РЅРµР°РєС‚РёРІРЅС‹С… Р»РёРЅРёР№
INACTIVE_DOT_COLOR = (60, 60, 60) # РћС‡РµРЅСЊ С‚РµРјРЅРѕ-СЃРµСЂС‹Р№ РґР»СЏ РЅРµР°РєС‚РёРІРЅС‹С… С‚РѕС‡РµРє

HIGHLIGHT_DOT_COLOR = (200, 200, 200) # РЎРІРµС‚Р»Рѕ-СЃРµСЂС‹Р№ РґР»СЏ Р°РєС‚РёРІРЅС‹С… С‚РѕС‡РµРє
HIGHLIGHT_YEAR_TEXT_COLOR = (255, 255, 255) # Р‘РµР»С‹Р№ РґР»СЏ Р°РєС‚РёРІРЅРѕРіРѕ РіРѕРґР°

# Р¦РІРµС‚Р° РґР»СЏ Р°РєС‚РёРІРЅС‹С… РњРµСЃСЏС†РµРІ (12 СѓРЅРёРєР°Р»СЊРЅС‹С… С†РІРµС‚РѕРІ)
MONTH_COLORS = {
    1: (135, 206, 250),
    2: (255, 182, 193),
    3: (152, 251, 152),
    4: (197, 164, 255),
    5: (255, 228, 100),
    6: (127, 255, 212),
    7: (255, 178, 102),
    8: (255, 160, 122),
    9: (255, 204, 51),
    10: (255, 153, 102),
    11: (255, 102, 178),
    12: (0, 153, 255)
}

# Р¦РІРµС‚Р° РґР»СЏ Р°РєС‚РёРІРЅС‹С… Р”РЅРµР№ РЅРµРґРµР»Рё Рё СЃРѕРѕС‚РІРµС‚СЃС‚РІСѓСЋС‰РµРіРѕ С‡РёСЃР»Р°
DAY_COLORS = {
    "Monday": (102, 178, 255),
    "Tuesday": (128, 255, 178),
    "Wednesday": (255, 223, 102),
    "Thursday": (204, 153, 255),
    "Friday": (255, 153, 204),
    "Saturday": (102, 255, 204),
    "Sunday": (255, 178, 153)
}

# РЁСЂРёС„С‚С‹
try:
    FONT_PATH = "unifont-all.ttf" # Р—Р°РјРµРЅРёС‚Рµ РЅР° РїСѓС‚СЊ Рє РІР°С€РµРјСѓ С€СЂРёС„С‚Сѓ РёР»Рё СЃРєР°С‡Р°Р№С‚Рµ arial.ttf
    font_large = ImageFont.truetype(FONT_PATH, 30*1.5)
    font_medium = ImageFont.truetype(FONT_PATH, 24*1.5)
    font_small = ImageFont.truetype(FONT_PATH, 18*1.2)
except IOError:
    print(f"Warning: Could not load {FONT_PATH}. Using default PIL fonts.")
    font_large = ImageFont.load_default()
    font_medium = ImageFont.load_default()
    font_small = ImageFont.load_default()

DOT_RADIUS = 4 # Р Р°РґРёСѓСЃ РєСЂСѓРіР° РґР»СЏ С‚РѕС‡РµРє
TEXT_OFFSET_X = 15 # РЎРјРµС‰РµРЅРёРµ С‚РµРєСЃС‚Р° РѕС‚ С‚РѕС‡РєРё

# --- 2. Р Р°СЃРїРѕР»РѕР¶РµРЅРёРµ СЌР»РµРјРµРЅС‚РѕРІ ---
# X-РєРѕРѕСЂРґРёРЅР°С‚С‹ РґР»СЏ РєРѕР»РѕРЅРѕРє
x_year = IMG_WIDTH * 0.08
x_all_months = IMG_WIDTH * 0.28
x_dow_start = IMG_WIDTH * 0.6
x_day_num_start = IMG_WIDTH * 0.9

# Y-РєРѕРѕСЂРґРёРЅР°С‚С‹
y_year = IMG_HEIGHT // 2

# Р”Р»СЏ РІСЃРµС… 12 РјРµСЃСЏС†РµРІ
y_margin_months = 60
y_month_spacing = (IMG_HEIGHT - 2 * y_margin_months) / 11
y_month_start = y_margin_months

# Р”Р»СЏ РґРЅРµР№ РЅРµРґРµР»Рё
y_dow_spacing = 60
y_dow_start = IMG_HEIGHT // 2 - (3 * y_dow_spacing) + 30

# Р”Р»СЏ С‡РёСЃРµР» РјРµСЃСЏС†Р° (РґРѕ 31 РґРЅСЏ)
y_day_num_spacing = 27
y_day_num_start = IMG_HEIGHT // 2 - (15 * y_day_num_spacing)
#y_day_num_spacing = 20
#y_day_num_start = IMG_HEIGHT // 2 - (15 * y_day_num_spacing)

# --- 3. Р’СЃРїРѕРјРѕРіР°С‚РµР»СЊРЅС‹Рµ С„СѓРЅРєС†РёРё ---

def draw_dot(draw, center_x, center_y, color, radius=DOT_RADIUS):
    draw.ellipse((center_x - radius, center_y - radius, center_x + radius, center_y + radius), fill=color, outline=color)

def draw_line(draw, x1, y1, x2, y2, color, width=1):
    draw.line((x1, y1, x2, y2), fill=color, width=width)

def get_formatted_month_name(month_num):
    return f"{month_num:02d} {datetime.date(TARGET_YEAR, month_num, 1).strftime('%B')}"

DOW_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

def get_formatted_day_of_week_name(day_name_raw):
    day_num_in_week = DOW_ORDER.index(day_name_raw) + 1
    return f"{day_name_raw}"
    #return f"{day_num_in_week:02d} {day_name_raw}"

# --- 4. РџСЂРµРґРІР°СЂРёС‚РµР»СЊРЅС‹Р№ СЂР°СЃС‡РµС‚ РїРѕР·РёС†РёР№ СѓР·Р»РѕРІ ---
node_positions = {}

node_positions['year'] = (int(x_year), int(y_year))

node_positions['all_months'] = {}
for i in range(1, 13):
    y = int(y_month_start + (i - 1) * y_month_spacing)
    node_positions['all_months'][i] = (int(x_all_months), y)

node_positions['dow'] = {}
for i, day_name in enumerate(DOW_ORDER):
    y = int(y_dow_start + i * y_dow_spacing)
    node_positions['dow'][day_name] = (int(x_dow_start), y)

node_positions['day_num'] = {}
for i in range(1, 32):
    y = int(y_day_num_start + (i - 1) * y_day_num_spacing)
    node_positions['day_num'][i] = (int(x_day_num_start), y)


# --- 5. Р¤СѓРЅРєС†РёСЏ РґР»СЏ РіРµРЅРµСЂР°С†РёРё РѕРґРЅРѕР№ РєР°СЂС‚РёРЅРєРё ---
def generate_calendar_image(current_date, output_path):
    img = Image.new('RGB', (IMG_WIDTH, IMG_HEIGHT), color=BACKGROUND_COLOR)
    draw = ImageDraw.Draw(img)

    current_year_str = str(current_date.year)
    current_month_num = current_date.month
    current_formatted_month_name = get_formatted_month_name(current_month_num)
    current_raw_day_name = current_date.strftime("%A")
    current_formatted_day_name = get_formatted_day_of_week_name(current_raw_day_name)
    current_day_number = current_date.day

    num_days_in_current_month = monthrange(current_date.year, current_date.month)[1]

    # --- Р РёСЃСѓРµРј РІСЃРµ РЅРµР°РєС‚РёРІРЅС‹Рµ Р»РёРЅРёРё РџР•Р Р’Р«РњР ---

    # Р›РёРЅРёРё РѕС‚ РіРѕРґР° РґРѕ РІСЃРµС… РјРµСЃСЏС†РµРІ
    for month_num_iter, month_pos_iter in node_positions['all_months'].items():
        draw_line(draw, *node_positions['year'], *month_pos_iter, INACTIVE_LINE_COLOR)
        
        # Р›РёРЅРёРё РѕС‚ РўР•РљРЈР©Р•Р“Рћ РјРµСЃСЏС†Р° (РґР°Р¶Рµ РµСЃР»Рё РѕРЅ РЅРµР°РєС‚РёРІРµРЅ) РґРѕ РІСЃРµС… РґРЅРµР№ РЅРµРґРµР»Рё
        # Р­С‚Рѕ СЃРѕР·РґР°РµС‚ "РїР°СѓС‚РёРЅСѓ" С‚РѕР»СЊРєРѕ РґР»СЏ Р°РєС‚РёРІРЅРѕРіРѕ РјРµСЃСЏС†Р°, РєР°Рє РІ РїСЂРёРјРµСЂРµ
        if month_num_iter == current_month_num:
            for day_name_raw_iter in DOW_ORDER:
                dow_pos_iter = node_positions['dow'][day_name_raw_iter]
                draw_line(draw, *month_pos_iter, *dow_pos_iter, INACTIVE_LINE_COLOR)

    # Р›РёРЅРёРё РѕС‚ РєР°Р¶РґРѕРіРѕ РґРЅСЏ РЅРµРґРµР»Рё РґРѕ РєР°Р¶РґРѕРіРѕ С‡РёСЃР»Р° РјРµСЃСЏС†Р° (РІ РїСЂРµРґРµР»Р°С… С‚РµРєСѓС‰РµРіРѕ РјРµСЃСЏС†Р°)
    for day_name_raw_iter in DOW_ORDER:
        dow_pos_iter = node_positions['dow'][day_name_raw_iter]
        for i_day_num in range(1, num_days_in_current_month + 1):
            day_num_pos_iter = node_positions['day_num'][i_day_num]
            draw_line(draw, *dow_pos_iter, *day_num_pos_iter, INACTIVE_LINE_COLOR)


    # --- Р РёСЃСѓРµРј РІСЃРµ РЅРµР°РєС‚РёРІРЅС‹Рµ С‚РѕС‡РєРё Рё С‚РµРєСЃС‚ Р’РўРћР Р«РњР (РїРѕРІРµСЂС… Р»РёРЅРёР№) ---

    # Р“РѕРґ
    draw_dot(draw, *node_positions['year'], INACTIVE_DOT_COLOR)
    draw.text((node_positions['year'][0] + TEXT_OFFSET_X, node_positions['year'][1] - font_large.size // 2),
              current_year_str, fill=INACTIVE_TEXT_COLOR, font=font_large)

    # Р’СЃРµ 12 РјРµСЃСЏС†РµРІ
    for month_num_iter, month_pos_iter in node_positions['all_months'].items():
        m_name_formatted = get_formatted_month_name(month_num_iter)
        draw_dot(draw, *month_pos_iter, INACTIVE_DOT_COLOR)
        draw.text((month_pos_iter[0] + TEXT_OFFSET_X, month_pos_iter[1] - font_medium.size // 2),
                  m_name_formatted, fill=INACTIVE_TEXT_COLOR, font=font_medium)

    # Р”РЅРё РЅРµРґРµР»Рё
    for day_name_raw_iter in DOW_ORDER:
        dow_pos_iter = node_positions['dow'][day_name_raw_iter]
        formatted_dow_name_iter = get_formatted_day_of_week_name(day_name_raw_iter)
        draw_dot(draw, *dow_pos_iter, INACTIVE_DOT_COLOR)
        draw.text((dow_pos_iter[0] + TEXT_OFFSET_X, dow_pos_iter[1] - font_medium.size // 2),
                  formatted_dow_name_iter, fill=INACTIVE_TEXT_COLOR, font=font_medium)

    # Р§РёСЃР»Р° РјРµСЃСЏС†Р°
    for i_day_num in range(1, num_days_in_current_month + 1):
        day_num_pos_iter = node_positions['day_num'][i_day_num]
        draw_dot(draw, *day_num_pos_iter, INACTIVE_DOT_COLOR)
        draw.text((day_num_pos_iter[0] + TEXT_OFFSET_X, day_num_pos_iter[1] - font_small.size // 2),
                  f"{i_day_num:02d}", fill=INACTIVE_TEXT_COLOR, font=font_small)


    # --- Р РёСЃСѓРµРј Р°РєС‚РёРІРЅС‹Р№ РїСѓС‚СЊ (РџРћРЎР›Р•Р”РќРРњ, С‡С‚РѕР±С‹ РѕРЅ Р±С‹Р» РїРѕРІРµСЂС… РІСЃРµРіРѕ) ---
    
    # Р“РѕРґ (Р°РєС‚РёРІРЅС‹Р№)
    draw_dot(draw, *node_positions['year'], HIGHLIGHT_DOT_COLOR)
    draw.text((node_positions['year'][0] + TEXT_OFFSET_X, node_positions['year'][1] - font_large.size // 2),
              current_year_str, fill=HIGHLIGHT_YEAR_TEXT_COLOR, font=font_large)

    # РђРєС‚РёРІРЅС‹Р№ РјРµСЃСЏС† РёР· РєРѕР»РѕРЅРєРё (Р°РєС‚РёРІРЅС‹Р№)
    active_month_pos = node_positions['all_months'][current_month_num]
    active_month_color = MONTH_COLORS[current_month_num]

    draw_line(draw, *node_positions['year'], *active_month_pos, active_month_color, width=2)
    draw_dot(draw, *active_month_pos, HIGHLIGHT_DOT_COLOR)
    draw.text((active_month_pos[0] + TEXT_OFFSET_X, active_month_pos[1] - font_medium.size // 2),
              current_formatted_month_name, fill=active_month_color, font=font_medium)

    # Р”РµРЅСЊ РЅРµРґРµР»Рё (Р°РєС‚РёРІРЅС‹Р№)
    active_dow_pos = node_positions['dow'][current_raw_day_name]
    active_day_color = DAY_COLORS[current_raw_day_name]

    draw_line(draw, *active_month_pos, *active_dow_pos, active_day_color, width=2)
    draw_dot(draw, *active_dow_pos, HIGHLIGHT_DOT_COLOR)
    draw.text((active_dow_pos[0] + TEXT_OFFSET_X, active_dow_pos[1] - font_medium.size // 2),
              current_formatted_day_name, fill=active_day_color, font=font_medium)

    # Р§РёСЃР»Рѕ РјРµСЃСЏС†Р° (Р°РєС‚РёРІРЅРѕРµ)
    active_day_num_pos = node_positions['day_num'][current_day_number]
    draw_line(draw, *active_dow_pos, *active_day_num_pos, active_day_color, width=2)
    draw_dot(draw, *active_day_num_pos, HIGHLIGHT_DOT_COLOR)
    draw.text((active_day_num_pos[0] + TEXT_OFFSET_X, active_day_num_pos[1] - font_small.size // 2),
              f"{current_day_number:02d}", fill=active_day_color, font=font_small)

    img.save(output_path)


# --- 6. РћСЃРЅРѕРІРЅРѕР№ С†РёРєР» РіРµРЅРµСЂР°С†РёРё ---
if __name__ == "__main__":
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    start_date = datetime.date(TARGET_YEAR, 1, 1)
    end_date = datetime.date(TARGET_YEAR, 12, 31)

    current_date = start_date
    while current_date <= end_date:
        filename = current_date.strftime("%Y-%m-%d") + ".png"
        output_path = os.path.join(OUTPUT_DIR, filename)

        print(f"Generating image for {current_date.strftime('%Y-%m-%d')}...")
        generate_calendar_image(current_date, output_path)

        current_date += datetime.timedelta(days=1)

    print(f"\nGenerated all images in the '{OUTPUT_DIR}' directory.")
