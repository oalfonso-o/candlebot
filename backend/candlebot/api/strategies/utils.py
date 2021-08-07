def add_open_close_points_to_chart_positions(
    position, balance_origin, balance_long, balance_short, time,
    chart_positions
):
    point_balance_origin = {'time': time, 'value': position.balance_origin}
    point_balance_long = {'time': time, 'value': position.balance_long}
    point_balance_short = {'time': time, 'value': position.balance_short}
    balance_origin.append(point_balance_origin)
    balance_long.append(point_balance_long)
    balance_short.append(point_balance_short)
    if position.action == 'open':
        point_open_position = {
            'time': time,
            'text': str(round(position.amount, 4)),
            'position': 'belowBar',
            'color': 'blue',
            'shape': 'arrowUp',
        }
        chart_positions.append(point_open_position)
    if position.action == 'close':
        point_close_position = {
            'time': time,
            'text': str(round(position.amount, 4)),
            'position': 'aboveBar',
            'color': 'green',
            'shape': 'arrowDown',
        }
        chart_positions.append(point_close_position)


def basic_charts_dict(
    candles, chart_positions_long, balance_origin, balance_long
):
    return [
        {
            'id': 'open/close long positions',
            'series': [
                {
                    'type': 'candles',
                    'values': candles,
                    'markers': chart_positions_long,
                },
            ],
            'width': 1200,
            'height': 500,
        },
        {
            'id': 'balance_origin',
            'series': [
                {'type': 'lines', 'values': balance_origin, 'color': '#39f'},
            ],
            'width': 1200,
            'height': 100,
        },
        {
            'id': 'balance_long',
            'series': [
                {'type': 'lines', 'values': balance_long, 'color': '#f5a'},
            ],
            'width': 1200,
            'height': 100,
        },
    ]
