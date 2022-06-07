import smartpy as sp 
fa2 = sp.io.import_script_from_url("file:./contracts/FA2.py")

class TokenFA2(fa2.FA2):
    pass

@sp.add_test(name="Test")
def test():
    scenario = sp.test_scenario()
    admin = sp.address("tz1-admin")
    user1 = sp.address("tz1-user1")

    scenario.h1("HEHE :)")
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

    token.mint(sp.record(token_id = 0, amount = 100, address=admin, metadata=sp.map({"": sp.utils.bytes_of_string("")}))).run(sender=admin)

    # Admin transfering one ticket to user1
    token.transfer([
        sp.record(
            from_ = admin,
            txs = [
                sp.record(
                    to_ = user1,
                    token_id = sp.nat(0),
                    amount = 1
                ),
            ]
        )
    ]).run(sender=admin)

    token.mint(sp.record(token_id = 0, amount = 100, address=admin, metadata=sp.map({"": sp.utils.bytes_of_string("ipfs://HOO")}))).run(sender=admin)