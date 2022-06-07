import smartpy as sp


class EventFactory(sp.Contract):
    def __init__(self, _admin):
        self.init(
            _admin=_admin,
        )


@sp.add_test(name="Test EventFactory")
def test():
    scenario = sp.test_scenario()
