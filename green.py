
import datetime
import os
from calendar import monthrange
from PIL import Image, ImageDraw, ImageFont

# --- 1. Константы и настройки ---
IMG_WIDTH = 1600
IMG_HEIGHT = 900
OUTPUT_DIR = "output" # Изменена папка вывода
TARGET_YEAR = 2030 # Год, для которого генерируем календарь

# Новые зеленые цвета из вашей палитры (преобразованы из HEX в RGB)
BACKGROUND_COLOR = (0, 0, 0) # color-bg

# Обновленные цвета для неактивных элементов - сделаны светлее
INACTIVE_TEXT_COLOR = (0, 115, 61) # color-darker (для очень темного, но различимого текста)
INACTIVE_LINE_COLOR = (0, 115, 61) # color-darkest (для самых темных, едва заметных линий)
INACTIVE_DOT_COLOR = (0, 115, 61) # color-bg-alt (немного темнее текста, но светлее линий)

HIGHLIGHT_DOT_COLOR = (0, 255, 136) # color-hl (самый яркий зеленый для активных точек)
HIGHLIGHT_YEAR_TEXT_COLOR = (0, 229, 122) # color-bright (яркий зеленый для активного года)

# Цвета для активных Месяцев (12 уникальных оттенков зеленого/близких к зеленому)
MONTH_COLORS = {
    1: (0, 255, 136),
    2: (0, 255, 136),
    3: (0, 255, 136),
    4: (0, 255, 136),
    5: (0, 255, 136),
    6: (0, 255, 136),
    7: (0, 255, 136),
    8: (0, 255, 136),
    9: (0, 255, 136),
    10: (0, 255, 136),
    11: (0, 255, 136),
    12: (0, 255, 136)
}

# Цвета для активных Дней недели и соответствующего числа (оттенки зеленого)
DAY_COLORS = {
    "Monday": (0, 255, 136),
    "Tuesday": (0, 255, 136),
    "Wednesday": (0, 255, 136),
    "Thursday": (0, 255, 136),
    "Friday": (0, 255, 136),
    "Saturday": (0, 255, 136),
    "Sunday": (0, 255, 136)
}


# Шрифты
try:
    FONT_PATH = "unifont-all.ttf" # Замените на путь к вашему шрифту 
    font_large = ImageFont.truetype(FONT_PATH, 30*1.2)
    font_medium = ImageFont.truetype(FONT_PATH, 24*1.5)
    font_small = ImageFont.truetype(FONT_PATH, 18*1.2)
    font_date_display = ImageFont.truetype(FONT_PATH, 24*1.2)
    font_bottom_left_label = ImageFont.truetype(FONT_PATH, 20*1.2)

except IOError:
    print(f"Warning: Could not load {FONT_PATH}. Using default PIL fonts.")
    font_large = ImageFont.load_default()
    font_medium = ImageFont.load_default()
    font_small = ImageFont.load_default()
    font_date_display = ImageFont.load_default()
    font_bottom_left_label = ImageFont.load_default()

DOT_RADIUS = 4 # Радиус круга для точек
TEXT_OFFSET_X = 15 # Смещение текста от точки

# Константы для даты в верхнем правом углу
DATE_DISPLAY_TEXT_COLOR = (0, 255, 136) # Яркий зеленый (color-hl)
DATE_DISPLAY_MARGIN_X = 40 # Отступ от правого края
DATE_DISPLAY_MARGIN_Y = 30 # Отступ от верхнего края

# Константы для надписи в левом нижнем углу
BOTTOM_LEFT_LABEL_TEXT = "Слов’їніка" # Текст надписи
BOTTOM_LEFT_LABEL_COLOR = (0, 178, 95) # color-fg, соответствует цвету неактивного текста
BOTTOM_LEFT_LABEL_MARGIN_X = 40 # Отступ от левого края
BOTTOM_LEFT_LABEL_MARGIN_Y = 30 # Отступ от нижнего края

# --- 2. Расположение элементов ---
# X-координаты для колонок
x_year = IMG_WIDTH * 0.08
x_all_months = IMG_WIDTH * 0.28
x_dow_start = IMG_WIDTH * 0.6
x_day_num_start = IMG_WIDTH * 0.9

# Y-координаты
y_year = IMG_HEIGHT // 2

# Для всех 12 месяцев
y_margin_months = 60
y_month_spacing = (IMG_HEIGHT - 2 * y_margin_months) / 11
y_month_start = y_margin_months

# Для дней недели
y_dow_spacing = 60
y_dow_start = IMG_HEIGHT // 2 - (3 * y_dow_spacing) + 30

# Для чисел месяца (до 31 дня)
y_day_num_spacing = 27
y_day_num_start = IMG_HEIGHT // 2 - (15 * y_day_num_spacing)

# --- 3. Вспомогательные функции ---

def draw_dot(draw, center_x, center_y, color, radius=DOT_RADIUS):
    draw.ellipse((center_x - radius, center_y - radius, center_x + radius, center_y + radius), fill=color, outline=color)

def draw_line(draw, x1, y1, x2, y2, color, width=1):
    draw.line((x1, y1, x2, y2), fill=color, width=width)

def get_formatted_month_name(month_num):
    return f"{month_num:02d} {datetime.date(TARGET_YEAR, month_num, 1).strftime('%B')}"

DOW_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

def get_formatted_day_of_week_name(day_name_raw):
    day_num_in_week = DOW_ORDER.index(day_name_raw) + 1
    #return f"{day_num_in_week:02d} {day_name_raw}"
    return f"{day_name_raw}"

# --- 4. Предварительный расчет позиций узлов ---
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


# --- 5. Функция для генерации одной картинки ---
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

    # --- Рисуем все неактивные линии ПЕРВЫМИ (самый нижний слой) ---

    # Линии от года до всех месяцев
    for month_num_iter, month_pos_iter in node_positions['all_months'].items():
        draw_line(draw, *node_positions['year'], *month_pos_iter, INACTIVE_LINE_COLOR)
        
        # Линии от ТЕКУЩЕГО месяца (даже если он неактивен) до всех дней недели
        # Это создает "паутину" только для активного месяца
        if month_num_iter == current_month_num:
            for day_name_raw_iter in DOW_ORDER:
                dow_pos_iter = node_positions['dow'][day_name_raw_iter]
                draw_line(draw, *month_pos_iter, *dow_pos_iter, INACTIVE_LINE_COLOR)

    # УБРАНЫ неактивные линии от дней недели до чисел месяца, как было запрошено.
    # Теперь они рисуются только для АКТИВНОГО пути.


    # --- Рисуем все неактивные точки и текст ВТОРЫМИ (поверх линий) ---

    # Год
    draw_dot(draw, *node_positions['year'], INACTIVE_DOT_COLOR)
    draw.text((node_positions['year'][0] + TEXT_OFFSET_X - 105, node_positions['year'][1] - font_large.size // 2),
              current_year_str, fill=INACTIVE_TEXT_COLOR, font=font_large)

    # Все 12 месяцев
    for month_num_iter, month_pos_iter in node_positions['all_months'].items():
        m_name_formatted = get_formatted_month_name(month_num_iter)
        draw_dot(draw, *month_pos_iter, INACTIVE_DOT_COLOR)
        draw.text((month_pos_iter[0] + TEXT_OFFSET_X, month_pos_iter[1] - font_medium.size // 2),
                  m_name_formatted, fill=INACTIVE_TEXT_COLOR, font=font_medium)

    # Дни недели
    for day_name_raw_iter in DOW_ORDER:
        dow_pos_iter = node_positions['dow'][day_name_raw_iter]
        formatted_dow_name_iter = get_formatted_day_of_week_name(day_name_raw_iter)
        draw_dot(draw, *dow_pos_iter, INACTIVE_DOT_COLOR)
        draw.text((dow_pos_iter[0] + TEXT_OFFSET_X, dow_pos_iter[1] - font_medium.size // 2),
                  formatted_dow_name_iter, fill=INACTIVE_TEXT_COLOR, font=font_medium)

    # Числа месяца
    for i_day_num in range(1, num_days_in_current_month + 1):
        day_num_pos_iter = node_positions['day_num'][i_day_num]
        draw_dot(draw, *day_num_pos_iter, INACTIVE_DOT_COLOR)
        draw.text((day_num_pos_iter[0] + TEXT_OFFSET_X, day_num_pos_iter[1] - font_small.size // 2),
                  f"{i_day_num:02d}", fill=INACTIVE_TEXT_COLOR, font=font_small)


    # --- Рисуем активный путь (ПОСЛЕДНИМ, чтобы он был поверх всего) ---
    
    # Год (активный)
    draw_dot(draw, *node_positions['year'], HIGHLIGHT_DOT_COLOR)
    draw.text((node_positions['year'][0] + TEXT_OFFSET_X - 105, node_positions['year'][1] - font_large.size // 2),
              current_year_str, fill=HIGHLIGHT_YEAR_TEXT_COLOR, font=font_large)

    # Активный месяц из колонки (активный)
    active_month_pos = node_positions['all_months'][current_month_num]
    active_month_color = MONTH_COLORS[current_month_num]

    draw_line(draw, *node_positions['year'], *active_month_pos, active_month_color, width=2)
    draw_dot(draw, *active_month_pos, HIGHLIGHT_DOT_COLOR)
    draw.text((active_month_pos[0] + TEXT_OFFSET_X, active_month_pos[1] - font_medium.size // 2),
              current_formatted_month_name, fill=active_month_color, font=font_medium)

    # День недели (активный)
    active_dow_pos = node_positions['dow'][current_raw_day_name]
    active_day_color = DAY_COLORS[current_raw_day_name]

    draw_line(draw, *active_month_pos, *active_dow_pos, active_day_color, width=2)
    draw_dot(draw, *active_dow_pos, HIGHLIGHT_DOT_COLOR)
    draw.text((active_dow_pos[0] + TEXT_OFFSET_X, active_dow_pos[1] - font_medium.size // 2),
              current_formatted_day_name, fill=active_day_color, font=font_medium)

    # Число месяца (активное)
    active_day_num_pos = node_positions['day_num'][current_day_number]
    draw_line(draw, *active_dow_pos, *active_day_num_pos, active_day_color, width=2)
    draw_dot(draw, *active_day_num_pos, HIGHLIGHT_DOT_COLOR)
    draw.text((active_day_num_pos[0] + TEXT_OFFSET_X, active_day_num_pos[1] - font_small.size // 2),
              f"{current_day_number:02d}", fill=active_day_color, font=font_small)

    # --- Добавляем текущую дату YYYY-MM-DD в верхний правый угол ---
    date_text = current_date.strftime("%Y-%m-%d")
    bbox = draw.textbbox((0, 0), date_text, font=font_date_display)
    text_width = bbox[2] - bbox[0]
    #text_x = IMG_WIDTH - text_width - DATE_DISPLAY_MARGIN_X
    text_x = BOTTOM_LEFT_LABEL_MARGIN_X
    text_y = DATE_DISPLAY_MARGIN_Y
    draw.text((text_x, text_y), date_text, fill=DATE_DISPLAY_TEXT_COLOR, font=font_date_display)

    # --- Добавляем надпись в левый нижний угол ---
    bbox_label = draw.textbbox((0, 0), BOTTOM_LEFT_LABEL_TEXT, font=font_bottom_left_label)
    label_height = bbox_label[3] - bbox_label[1]
    label_x = BOTTOM_LEFT_LABEL_MARGIN_X
    label_y = IMG_HEIGHT - label_height - BOTTOM_LEFT_LABEL_MARGIN_Y
    draw.text((label_x, label_y), BOTTOM_LEFT_LABEL_TEXT, fill=BOTTOM_LEFT_LABEL_COLOR, font=font_bottom_left_label)


    img.save(output_path)


# --- 6. Основной цикл генерации ---
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
