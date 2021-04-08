class Position:

    def __init__(
        self,
        type_: str,
        action: str,
        price: float,
        timestamp: int,
        amount: float,
        balance_origin: float,
        balance_long: float,
        balance_short: float,
    ):
        self.type = type_
        self.action = action
        self.price = price
        self.timestamp = timestamp
        self.amount = amount
        self.balance_origin = balance_origin
        self.balance_long = balance_long
        self.balance_short = balance_short
