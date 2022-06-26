# Chiketto

Chiketto is a NFT-based ticketing platform on tezos for events. It creates new contracts for every single event and allows the admin to have multiple types of ticket for each event.
These tickets are standard NFTs and should be tradable on secondary marketplace like Objkt and Rarible.

# Chikettto Frontend and Contract addresses.

This is our frontend repo for our decentralized application.
https://github.com/KetanKudikyal/chiketto_frontend

Event Factory Contract Address: [KT1Mc47KFe9oj4xRBToNNKEPQmqKNf7LeDSz](https://better-call.dev/ithacanet/KT1Mc47KFe9oj4xRBToNNKEPQmqKNf7LeDSz/operations)

## Plan ?

- Plan is to make a v v cool NFT tickets on tezos with a fancy UI.
- Make a fancy or v v minimal ui (black, white, monospace font);
- Events Page (Generated from a EventFactory);
- Each event can have many tickets.
- These Events are going to have unique FA2 contract which will allow them to trade on secondary marketplace.
- Use typescript;

## Contract architecture.

![Architecture](https://i.ibb.co/Dz6qzpP/arch.png)

- Each event has it's own event contract and FA2 contract.
- Event factory stores the generated contract addresses.
- FA2 contract is responsible for storing NFTs.
- Since each Event has separate FA2 contract, this allow them to be tradable on secondary marketplaces like Objkt.
