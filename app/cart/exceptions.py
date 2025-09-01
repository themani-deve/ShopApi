class CartError(Exception):
    pass


class CartNotFoundError(CartError):
    pass


class AlreadyPaidError(CartError):
    pass


class EmptyCartError(CartError):
    pass


class GatewayError(CartError):
    pass


class PaymentFailed(CartError):
    pass


class ItemNotFoundError(CartError):
    pass
