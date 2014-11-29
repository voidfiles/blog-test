from dateparser.date import DateDataParser

ddp = DateDataParser()


def get_date(date_string):
    result = ddp.get_date_data(date_string)

    return result.get('date_obj')
