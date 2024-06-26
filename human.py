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
    exit_conditions = describe_conditions(schema['exit_conditions']['all'], "all", 1)
    description = (
        "Trading Strategy:\n\n"
        "Entry Conditions:\n"
        f"{entry_conditions}\n\n"
        "Exit Conditions:\n"
        f"{exit_conditions}\n"
    )
    return description

# Example usage:
schema = {
    "entry_conditions": {
        "all": [
            {
                "indicator": {"indicator": "MA", "params": {"period": 10}},
                "comparator": "crosses_above",
                "value": {"indicator": "MVA", "params": {"period": 50}}
            },
            {
                "any": [
                    {
                        "indicator": {"indicator": "RSI", "params": {"period": 14}},
                        "comparator": "less_than",
                        "value": 30
                    },
                    {
                        "indicator": {"indicator": "RSI", "params": {"period": 14}},
                        "comparator": "greater_than",
                        "value": 70
                    },
                    {
                        "all": [
                            {
                                "indicator": {"indicator": "RSI", "params": {"period": 14}},
                                "comparator": "greater_than",
                                "value": 30
                            },
                            {
                                "indicator": {"indicator": "RSI", "params": {"period": 14}},
                                "comparator": "less_than",
                                "value": 70
                            }
                        ]
                    }
                ]
            },
            {
                "indicator": {"indicator": "MVA", "params": {"period": 20}},
                "comparator": ">",
                "value": {"indicator": "Price", "params": {"type": "Close"}}
            },
        ]
    },
    "exit_conditions": {
        "all": [
            {
                "indicator": {"indicator": "MA", "params": {"period": 10}},
                "comparator": "crosses_below",
                "value": {"indicator": "MVA", "params": {"period": 50}}
            },
            {
                "indicator": {"indicator": "RSI", "params": {"period": 14}},
                "comparator": "greater_than",
                "value": 70
            }
        ]
    }
}

description = describe_trading_strategy(schema)
print(description)
