def add_open_close_points_to_chart_positions(position, time, chart_positions):
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


def basic_charts_dict(candles, chart_positions_long, lines_series):
    return [
        {
            'id': 'open/close long positions',
            'series': [
                {
                    'title': 'candles',
                    'type': 'candles',
                    'values': candles,
                    'markers': chart_positions_long,
                },
                *lines_series,
            ],
            'width': 1200,
            'height': 500,
        },
    ]
