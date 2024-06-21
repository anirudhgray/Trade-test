import json

def describe_indicator(indicator):
    if isinstance(indicator, str):
        return indicator
    params = ', '.join([f"{k}: {v}" for k, v in indicator['params'].items()])
    return f"{indicator['indicator']} with a period of {params.split(': ')[1]}"

def describe_condition(condition):
    indicator = describe_indicator(condition['indicator'])
    comparator = condition['comparator'].replace('_', ' ')
    if isinstance(condition['value'], dict):
        value = describe_indicator(condition['value'])
    else:
        value = condition['value']
    return f"{indicator} {comparator} {value}"

def describe_conditions(conditions, condition_type="all", indent=0):
    descriptions = []
    for condition in conditions:
        if "any" in condition:
            descriptions.append(f"{'  ' * indent}- Any of the following conditions:\n{describe_conditions(condition['any'], 'any', indent + 1)}")
        elif "all" in condition:
            descriptions.append(f"{'  ' * indent}- All of the following conditions:\n{describe_conditions(condition['all'], 'all', indent + 1)}")
        else:
            descriptions.append(f"{'  ' * indent}- {describe_condition(condition)}")
    return '\n'.join(descriptions)

def describe_trading_strategy(schema):
    entry_conditions = describe_conditions(schema['entry_conditions']['all'], "all", 1)
    exit_conditions
