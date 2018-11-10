import re

from utils.logger import get_local_logger

logger = get_local_logger(__name__)

__all__ = ['is_chinese_character', 'is_valid_name', 'is_valid_phone',
           'is_valid_id_card', 'get_gender_from_id_card', 'get_age_from_id_card',
           'is_valid_bank_card']


def is_chinese_character(characters):
    assert isinstance(characters, str)
    p = re.compile(r'^[\u4e00-\u9fa5]+$')  # Chinese characters
    if p.match(characters):
        return True
    else:
        logger.debug('Character not match regex: %(characters)s' % locals())
        return False


def is_valid_name(name):
    assert isinstance(name, str)
    p = re.compile(r'^[\u4e00-\u9fa5]+(·[\u4e00-\u9fa5]+)*$')
    if p.match(name):
        return True
    logger.debug('Name not match regex: %(name)s' % locals())
    return False


def is_valid_phone(phone):
    assert isinstance(phone, str)
    p = re.compile(r'^1[^012][0-9]{9}$')
    if p.match(phone):
        return True
    logger.debug('Phone not match regex: %(phone)s' % locals())
    return False


def is_valid_id_card(id_card):
    assert isinstance(id_card, str)
    weight = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
    validate = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']

    # 只允许 18 位身份证且出生年在 1900 年至 2999 年之间的情况，日期合法性在正则里只初步校验，后面需要进一步校验
    p = re.compile(r'^[1-9]\d{5}(19|(2\d))\d{2}((0[1-9])|(10|11|12))(([0-2][1-9])|10|20|30|31)\d{3}[0-9Xx]$')
    if not p.match(id_card):
        logger.debug('ID card not match regex: %(id_card)s' % locals())
        return False

    year = int(id_card[6:10])
    month = int(id_card[10:12])
    day = int(id_card[12:14])
    from datetime import datetime
    try:
        dt = datetime(year=year, month=month, day=day)
        if dt >= datetime.now() or dt < datetime(year=1900, month=1, day=1):
            logger.debug('Birthday in ID card not allowed: %(id_card)s' % locals())
            return False
    except ValueError:
        logger.debug('Birthday in ID card not legal: %(id_card)s' % locals())
        return False

    id17 = id_card[:-1]
    sum17 = 0
    for i in range(17):
        sum17 += int(id17[i]) * weight[i]
    code = validate[sum17 % 11]
    if code == id_card[-1].upper():
        return True
    else:
        logger.debug('ID card validation failed: %(id_card)s' % locals())
        return False


def get_gender_from_id_card(id_card):
    if not is_valid_id_card(id_card):
        logger.debug('Illegal ID card: %(id_card)s' % locals())
        return None

    if len(id_card) == 15:
        gender_digit = int(id_card[14])  # Last digit
    elif len(id_card) == 18:
        gender_digit = int(id_card[16])  # Last second digit
    else:
        logger.debug('Illegal ID card: %(id_card)s' % locals())
        return None

    return u'女' if gender_digit % 2 == 0 else u'男'


def get_age_from_id_card(id_card):
    if not is_valid_id_card(id_card):
        return None

    year = int(id_card[6:10])
    month = int(id_card[10:12])
    day = int(id_card[12:14])
    from datetime import datetime
    try:
        birthday = datetime(year=year, month=month, day=day)
        today = datetime.now()
        age = today.year - birthday.year
        if (today.month, today.day) < (birthday.month, birthday.day):
            return age - 1
        return age
    except ValueError:
        logger.debug('Birthday in ID card not legal: %(id_card)s' % locals())
        return None


def is_valid_bank_card(card_no):
    assert isinstance(card_no, str)
    heads = ['10', '18', '30', '35', '37', '40', '41', '42', '43', '44', '45', '46', '47',
             '48', '49', '50', '51', '52', '53', '54', '55', '56', '58', '60', '62', '65',
             '68', '69', '84', '87', '88', '94', '95', '98', '99']

    p = re.compile(r'^[1-9][0-9]+$')
    if not p.match(card_no):
        logger.debug('Bank card contains non digital characters: %(card_no)s' % locals())
        return False

    if not 16 <= len(card_no) <= 19:
        logger.debug('Bank card length not within 16 to 19: %(card_no)s' % locals())
        return False

    if card_no[0:2] not in heads:
        logger.debug('First two digits of bank card not allowed: %(card_no)s' % locals())
        return False

    if not luhn(card_no):
        logger.debug('Bank card failed on Luhn algorithm: %(card_no)s' % locals())
        return False

    return True


def luhn(in_str):
    if len(in_str) < 2:
        return False
    o_sums = 0
    e_sums = 0
    for i, c in enumerate(in_str[::-1]):
        if i % 2 == 0:
            o_sums += int(c)
        else:
            p = int(c) * 2
            p = p if p < 10 else p - 9
            e_sums += p
    return (o_sums + e_sums) % 10 == 0

