import smartpy as sp
fa2 = sp.io.import_script_from_url("file:./contracts/FA2.py")

class Types:
    FA2Mint = sp.TRecord(
        address=sp.TAddress,
        amount=sp.TNat,
        metadata=sp.TMap(sp.TString, sp.TBytes),
        token_id=sp.TNat,
    )

    FA2Transfer = sp.TList(
        sp.TRecord(
            from_ = sp.TAddress,
            txs = sp.TList(
                sp.TRecord(
                    amount = sp.TNat,
                    to_ = sp.TAddress,
                    token_id = sp.TNat
                ).layout(("to_", ("token_id", "amount")))
            )
        )
    )

class TokenFA2(fa2.FA2):
    pass


class Event(sp.Contract):
    def __init__(self, _admin, _factoryAdmin, _fa2, _metadata, _platformFee):
        self.init(
            admin=_admin,
            factoryAdmin = _factoryAdmin,
            fa2 = _fa2,
            ticketIndex = sp.nat(0),
            platformFee = _platformFee,

            # For tracking the price of each ticket.
            tickets = sp.map(l = {}, tkey=sp.TNat, tvalue=sp.TMutez),
            ticketBalance = sp.map(l = {}, tkey=sp.TNat, tvalue=sp.TRecord(total=sp.TNat, sold=sp.TNat)),

            # Metadata
            metadata = sp.big_map(l={
                "": sp.utils.bytes_of_string("tezos-storage:content"),
                "content": _metadata,
            }),
        )
    
    @sp.private_lambda(
        with_storage="read-write", with_operations=True, wrap_call=True
    )
    def mintNFT(self, params):
        """ Mint NFT """
        sp.set_type(params, sp.TRecord(
            address = sp.TAddress,
            amount = sp.TNat,
            uri = sp.TBytes,
            tokenId = sp.TNat,
        ))
        mintData = sp.record(
            address = params.address,
            amount = params.amount,
            metadata = sp.map({"": params.uri}),
            token_id = params.tokenId,
        )
        contract = sp.contract(Types.FA2Mint, self.data.fa2, 'mint').open_some("WRONG_FA2_CONTRACT")
        sp.transfer(mintData, sp.mutez(0), contract)

    
    @sp.entry_point
    def createTicket(self, params):
        """
        # This allows admins to create new tickets.
        - Admin only.
        - Can mint 1 ticket with n editions.
        - The admin of the ticket will be this contract.
        """
        sp.set_type(params, sp.TRecord(
            price = sp.TMutez,
            uri = sp.TBytes,
            amount = sp.TNat,
        ))

        # Only admin can access
        sp.verify(sp.sender == self.data.admin, "ONLY_ADMIN_CAN_ACCESS")
        ticketId = self.data.ticketIndex

        # Minting the NFT
        self.mintNFT(sp.record(address=sp.self_address, amount=params.amount, uri=params.uri, tokenId=ticketId))

        # Setting the price.
        self.data.tickets[ticketId] = params.price

        self.data.ticketBalance[ticketId] = sp.record(total=params.amount, sold=sp.nat(0))

        # Updating the ticket index
        self.data.ticketIndex += 1
   
    @sp.entry_point
    def purchaseTicket(self, params):
        """
        # This allow users to purchase tickets.
        - Can be called by anyone.
        - Provide XTZs for the tickets
        - We'll send one ticket to you.
        """
        sp.set_type(params, sp.TRecord(
            ticketId = sp.TNat,
        ))

        ticketBalance = sp.view('get_balance_of', self.data.fa2, sp.record(owner=sp.self_address, token_id=params.ticketId), sp.TNat).open_some("WRONG_ONCHAIN_VIEW")
        sp.verify(ticketBalance > sp.nat(0), 'ALL_TICKETS_SOLD_OUT')

        # If we've ticket then transfer to the user but before that 
        # verify the amount sent.
        sp.verify(self.data.tickets.contains(params.ticketId), 'PRICE_NOT_SET')
        sp.verify(sp.amount == self.data.tickets[params.ticketId], 'NOT_CORRECT_PRICE')

        # Transfer one ticket from this address to user's address.
        transferData = [sp.record(from_=sp.self_address, txs=[sp.record(to_=sp.sender, token_id = params.ticketId, amount = 1)])]
        contract = sp.contract(Types.FA2Transfer, self.data.fa2, 'transfer').open_some('WRONG_FA2_CONTRACT')
        sp.transfer(transferData, sp.mutez(0), contract)

        # Send the money to the admin and factory cut
        totalAmount = sp.utils.mutez_to_nat(sp.amount)
        platformShare = self.data.platformFee * totalAmount / 100
        sp.send(self.data.factoryAdmin, sp.utils.nat_to_mutez(platformShare), 'CANT_SEND_TO_PLATFORM_ADMIN')
        sp.send(self.data.admin, sp.utils.nat_to_mutez(sp.as_nat(totalAmount - platformShare)), 'CANT_SEND_TO_ADMIN')

        # Updating the amount
        self.data.ticketBalance[params.ticketId].sold += 1




@sp.add_test(name="Test Event")
def test():
    scenario = sp.test_scenario()
    admin = sp.address("tz1-admin")
    alice = sp.address("tz1-alice")

    token = TokenFA2(
        config = fa2.FA2_config(
            non_fungible = True,
            assume_consecutive_token_ids = True
        ),
        admin = admin,
        metadata = sp.big_map({
            "": sp.utils.bytes_of_string("tezos-storage:content"),
            "content": sp.utils.bytes_of_string("""{name: "Hello World"}"""),
        })
    )
    scenario += token

    event = Event(_admin=admin, _fa2=token.address, _metadata=sp.utils.bytes_of_string(""), _factoryAdmin=sp.address("tz1-factoryAdmin"), _platformFee=sp.nat(5))
    scenario += event

    # Make event the admin of FA2 contract.
    token.set_administrator(event.address).run(sender=admin)

    # Admin creating new ticket
    event.createTicket(sp.record(price=sp.tez(1), uri=sp.utils.bytes_of_string("ipfs://HEHE"), amount=sp.nat(100))).run(sender=admin)

    # Alice is buying ticket with wrong amount
    event.purchaseTicket(sp.record(ticketId=0)).run(sender=alice, amount=sp.mutez(100), valid=False)

    event.purchaseTicket(sp.record(ticketId=0)).run(sender=alice, amount=sp.tez(1))




sp.add_compilation_target("FA2_TOKEN", TokenFA2(config = fa2.FA2_config(
        ),
        admin = sp.address("tz1VRTputDyDYy4GjthJqdabKDVxkD3xCYGc"),
        metadata = sp.big_map({
            "": sp.utils.bytes_of_string("tezos-storage:content"),
            "content": sp.utils.bytes_of_string("""{name: "Hello World"}"""),
        })))