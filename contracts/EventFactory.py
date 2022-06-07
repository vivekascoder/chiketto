import smartpy as sp
event = sp.io.import_script_from_url("file:./contracts/Event.py")
fa2 = event.fa2


class EventFactory(sp.Contract):
    def __init__(self, _admin, _cost):
        self.init(
            admin=_admin,
            cost = _cost,
            userEvents = sp.map(l={}, tkey=sp.TAddress, tvalue=sp.TList(sp.TAddress)),
            eventsToFA2 = sp.map(l={}, tkey=sp.TAddress, tvalue=sp.TAddress),
        )
    
    @sp.entry_point
    def createEvent(self):
        """ Create Event """
        sp.verify(sp.amount == self.data.cost, 'NOT_CORRECT_AMOUNT')
        
        # Create new FA2 contract.
        newFA2 = event.TokenFA2(
            config = fa2.FA2_config(
                non_fungible = True,
                assume_consecutive_token_ids=False
            ),
            admin = sp.sender,
            metadata = sp.big_map({
                "": sp.utils.bytes_of_string("tezos-storage:content"),
                "content": sp.utils.bytes_of_string("""{"name": "FA2 for Event"}""")
            })
        )
        newFA2Address = sp.create_contract(contract=newFA2)

        newEvent = event.Event(_admin=sp.sender, _fa2=newFA2Address)
        newEventAddress = sp.create_contract(contract=newEvent)

        # Storing the info in the storage.
        self.data.eventsToFA2[newEventAddress] = newFA2Address
        sp.if self.data.userEvents.contains(sp.sender):
            self.data.userEvents[sp.sender].push(newEventAddress)
        sp.else:
            self.data.userEvents[sp.sender] = [newEventAddress,]

@sp.add_test(name="Test EventFactory")
def test():
    scenario = sp.test_scenario()
    admin = sp.address('tz1-admin')
    alice = sp.address('tz1-alice')

    factory = EventFactory(_admin=admin, _cost=sp.tez(1))
    scenario += factory

    factory.createEvent().run(sender=alice, amount=sp.tez(1))
