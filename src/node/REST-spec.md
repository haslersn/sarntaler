# Specification of the REST API offerred by the node
The node stores and verifies the blockchain and offers and interface for the miner and wallet to easily access blockchain data.

## High-level specification: offered functionality
`()` = redundant but might be useful as a shortcut
### Transactions
- create new transaction
- get transaction data by hash
- get all transactions to / from an address
- get all transactions

### Account
- (get balance of specific address)
- get account by address (i.e. public key, balance, owner access, code, state)
- (check key for account)

### Blockchain
- (get last block)
- get any block specified by hash or by index (depth)
- get all blocks
- get chain difficulty
- compute hash

