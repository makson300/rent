CITY_MAP = {
    0: "Москва",
    1: "Санкт-Петербург",
    2: "Казань",
    3: "Екатеринбург",
    4: "Новосибирск"
}

# Mapping to database Category names for consistency in queries
CATEGORY_MAP = {
    0: "Дроны",
    1: "Техника для съемки",
    2: "Другое",
    3: "Операторы"
}

# For backward compatibility and ease of use in creation flow
CITIES = list(CITY_MAP.values())
CATEGORIES = ["Дроны", "Техника для съемки", "Другое"]
