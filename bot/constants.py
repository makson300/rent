# City and category mappings for UI consistency and compact callback data

CITY_MAP = {
    "1": "Москва",
    "2": "Санкт-Петербург",
    "3": "Казань",
    "4": "Екатеринбург",
    "5": "Новосибирск"
}

CATEGORY_MAP = {
    "1": "Дроны",
    "4": "Съемочное оборудование",
    "5": "Прочее",
    "6": "Операторы",
    "7": "ЧП"
}

# Inverse maps for easy lookup
CITY_REVERSE_MAP = {v: k for k, v in CITY_MAP.items()}
CATEGORY_REVERSE_MAP = {v: k for k, v in CATEGORY_MAP.items()}
