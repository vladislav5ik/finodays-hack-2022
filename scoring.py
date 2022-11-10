from db import Filter
import re

def score(filters, filter_values):
    result = True
    for filter in filters:
        value = filter_values[filter.id]
        value = apply_formula(filter, filters, filter_values)
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

def apply_formula(target_filter, all_filters, filter_values):
    # find MIN MAX formula containing names of filters (e.g. MIN(roi, term))
    m = re.search(r'(?P<operation>MIN|MAX)\((?P<filters>(\w+,?)+)\)', target_filter.name)
    if m is None:
        return filter_values[target_filter.id]
    
    operation = m.group('operation')
    filters_in_formula = m.group('filters').split(',')
    
    # print(', '.join(filters_in_formula))

    # find values of filters
    for filter in all_filters:
        if filter.name in filters_in_formula:
            filters_in_formula[filters_in_formula.index(filter.name)] = filter_values[filter.id]
    
    # print(', '.join(filters_in_formula))
    
    # apply formula
    if operation == 'MIN':
        result = min(filters_in_formula)
    elif operation == 'MAX':
        result = max(filters_in_formula)

    return result