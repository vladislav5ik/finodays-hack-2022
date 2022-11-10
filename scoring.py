from db import Filter
def score(filters, filter_values):
    result = True
    for filter in filters:
        value = filter_values[filter.id]
        value_const = filter.value_const
        operation = filter.operation
        if operation == '>':
            if not int(value) > int(value_const):
                result = False
                break
        elif operation == '<':
            if not int(value) < int(value_const):
                result = False
                break
        elif operation == '=':
            if not value == value_const:
                result = False
                break
    if not result:
        return (False, f'Фильтр "{filter.name}" не пройден, условие неверно: {value} {operation} {value_const}.')
    else:
        return (True, 'Все фильтры пройдены.')