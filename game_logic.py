import random

LETTERS_RU = ['А','В','Е','К','М','Н','О','Р','С','Т','У','Х']
LETTERS_BY = ['A','B','C','E','I','K','M','H','O','P','T','X']

REGIONS_RU = [
  '01','02','03','04','05','06','07','08','09','10','11','12','13','14','15','16','17','18','19','20',
  '21','22','23','24','25','26','27','28','29','30','31','32','33','34','35','36','37','38','39','40',
  '41','42','43','44','45','46','47','48','49','50','51','52','53','54','55','56','57','58','59','60',
  '61','62','63','64','65','66','67','68','69','70','71','72','73','74','75','76','77','78','79','80',
  '81','82','83','84','85','86','87','88','89','90','91','92','93','94','95','96','97','98','99',
  '102','103','116','123','124','125','126','127','128','129','130','131','132','133','134','135','136',
  '138','139','142','150','152','154','156','159','161','163','164','166','172','173','174','177','178',
  '180','181','184','185','190','196','197','198','199','224','250','277','299','323','550','725','750',
  '777','778','790','799','977','997','999'
]
REGIONS_BY = ['1','2','3','4','5','6','7']


# ===== МНОЖИТЕЛИ ЦИФР =====
def digit_multiplier(digits):
    if digits == '777': return 9
    if digits == '001': return 8
    if digits == '007': return 7
    if digits in ('111','222','333','444','555','666','888','999'): return 5
    # круглые: 100, 200, ..., 900
    if digits[0] in '123456789' and digits[1:] == '00': return 3
    # ровные: 010, 020, ..., 090
    if digits[0] == '0' and digits[1] in '123456789' and digits[2] == '0': return 2
    return 0


# ===== МНОЖИТЕЛИ БУКВ (серии РФ) =====
SERIES_RU = {
    'АМР': 9,
    'ЕКХ': 8,
    'ААА': 8,
    'АММ': 5,
    'АМО': 5,
    'ВВВ': 5, 'ЕЕЕ': 5, 'ККК': 5, 'МММ': 5, 'ННН': 5,
    'РРР': 5, 'ССС': 5, 'ТТТ': 5, 'УУУ': 5, 'ХХХ': 5,
    'ВОО': 3, 'СММ': 3,
    'ООО': 2,
}

SERIES_BY = {
    'AA': 8,
    'BB': 5,
    'AB': 3,
}


# ===== МНОЖИТЕЛИ РЕГИОНОВ =====
def region_multiplier_ru(region):
    top = ['77','99','97','177','199','197','777','799','797']
    high = ['01','02','23','50','78','98','178','198','750','790','102','103']
    good = ['116','123','152','159','161','163','164','196']
    if region in top: return 9
    if region in high: return 7
    if region in good: return 5
    return 0

def region_multiplier_by(region):
    if region == '7': return 9  # Минск
    if region == '1': return 5  # Брест
    return 0


# ===== РЕДКОСТИ =====
RARITY = {
    'common':   {'name': 'Обычная',     'chance': 0.80,  'price': 1000,   'xp': 1,   'to_garage': False},
    'uncommon': {'name': 'Необычная',   'chance': 0.15,  'price': 5000,   'xp': 3,   'to_garage': False},
    'rare':     {'name': 'Редкая',      'chance': 0.04,  'price': 20000,  'xp': 10,  'to_garage': True},
    'epic':     {'name': 'Эпическая',   'chance': 0.008, 'price': 80000,  'xp': 30,  'to_garage': True},
    'legend':   {'name': 'Легендарная', 'chance': 0.002, 'price': 400000, 'xp': 100, 'to_garage': True},
}
ORDER = ['common', 'uncommon', 'rare', 'epic', 'legend']


def roll_rarity(guarantee='any'):
    min_index = {'any': 0, 'uncommon': 1, 'rare': 2, 'epic': 3}.get(guarantee, 0)
    pool = ORDER[min_index:]
    weights = [RARITY[r]['chance'] for r in pool]
    total = sum(weights)
    weights = [w / total for w in weights]
    r = random.random()
    acc = 0
    for i, rarity in enumerate(pool):
        acc += weights[i]
        if r < acc:
            return rarity
    return pool[0]


def make_number_ru(rarity):
    """Возвращает dict с данными о номере и множителях."""
    # Пробуем выбить особую серию
    series = None
    if random.random() < 0.01:  # 1% шанс особой серии
        series = random.choice(list(SERIES_RU.keys()))

    if series:
        l1 = random.choice(LETTERS_RU)
        l2, l3 = series[0], series[1]
        if rarity in ('epic', 'legend'):
            digits = random.choice(['001', '777', '111', '888', '007'])
        else:
            digits = f"{random.randint(0, 999):03d}"
        region = random.choice(REGIONS_RU)
        number = f"{l1}{digits}{l2}{l3} {region}"
        series_mult = SERIES_RU[series]
    else:
        # Обычная генерация
        if rarity == 'legend':
            letter = 'О' if random.random() < 0.5 else random.choice(LETTERS_RU)
            l1 = l2 = l3 = letter
            digits = random.choice(['001', '777'])
            region = random.choice(['777', '799', '77', '99', '01'])
        elif rarity == 'epic':
            l1 = random.choice(LETTERS_RU)
            if random.random() < 0.5:
                l2 = l3 = l1
            else:
                l2 = random.choice(LETTERS_RU)
                l3 = l2
            digits = random.choice(['111','222','333','444','555','666','888','999'])
            region = random.choice(['77','99','01','777','799','199'])
        elif rarity == 'rare':
            l1 = random.choice(LETTERS_RU)
            if random.random() < 0.5:
                l2 = l1; l3 = random.choice(LETTERS_RU)
            else:
                l2 = random.choice(LETTERS_RU); l3 = l2
            d = str(random.randint(0, 9))
            digits = d + d + str(random.randint(0, 9))
            region = random.choice(REGIONS_RU)
        else:
            l1 = random.choice(LETTERS_RU)
            l2 = random.choice(LETTERS_RU)
            l3 = random.choice(LETTERS_RU)
            digits = f"{random.randint(0, 999):03d}"
            region = random.choice(REGIONS_RU)
        number = f"{l1}{digits}{l2}{l3} {region}"
        series_mult = 0
        series = None

    dm = digit_multiplier(digits)
    rm = region_multiplier_ru(region)
    total_mult = 1 + dm + series_mult + rm

    base_price = RARITY[rarity]['price']
    final_price = base_price * total_mult

    return {
        'number': number,
        'digits': digits,
        'region': region,
        'series': series,
        'digit_mult': dm,
        'series_mult': series_mult,
        'region_mult': rm,
        'total_mult': total_mult,
        'base_price': base_price,
        'final_price': final_price,
    }


def make_number_by(rarity):
    series = None
    if random.random() < 0.01:
        series = random.choice(list(SERIES_BY.keys()))

    if series:
        letters = series
        digits = '7777' if rarity in ('epic', 'legend') else f"{random.randint(0, 9999):04d}"
        region = '7' if random.random() < 0.5 else '1'
        number = f"{digits} {letters}-{region}"
        series_mult = SERIES_BY[series]
    else:
        if rarity in ('legend', 'epic'):
            digits = '7777'
            letters = 'AB'
            region = '7'
        else:
            digits = f"{random.randint(0, 9999):04d}"
            letters = random.choice(LETTERS_BY) + random.choice(LETTERS_BY)
            region = random.choice(REGIONS_BY)
        number = f"{digits} {letters}-{region}"
        series_mult = 0
        series = None

    dm = 0
    rm = region_multiplier_by(region)
    total_mult = 1 + dm + series_mult + rm
    base_price = RARITY[rarity]['price']
    final_price = base_price * total_mult

    return {
        'number': number,
        'digits': digits,
        'region': region,
        'series': series,
        'digit_mult': dm,
        'series_mult': series_mult,
        'region_mult': rm,
        'total_mult': total_mult,
        'base_price': base_price,
        'final_price': final_price,
    }


def gen_number(rarity, country='ru'):
    if country == 'by':
        return make_number_by(rarity)
    return make_number_ru(rarity)