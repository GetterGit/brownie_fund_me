from brownie import accounts, network, config, MockV3Aggregator
from web3 import Web3

# adding forked local environments for which we want to create a mock account with some ether in them but don't wanna to deploy mock contracts
FORKED_LOCAL_ENVIRONMENTS = ["ethereum-mainnet-fork", "ethereum-mainnet-fork-dev"]
# adding persistant ganache-local to our development environments
LOCAL_BLOCKCHAIN_ENVIRONMENTS = ["development", "ganache-local"]

# parameritizing function values
DECIMALS = 8
STARTING_PRICE = 200000000000


def get_account():
    if (
        network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS
        or network.show_active() in FORKED_LOCAL_ENVIRONMENTS
    ):
        # to get accounts[0] from the ethereum-mainnet-fork, do brownie_fund_me % brownie networks add development ethereum-mainnet-fork-dev cmd=ganache-cli host=http://127.0.0.1 fork='https://mainnet.infura.io/v3/$WEB3_INFURA_PROJECT_ID' accounts=10 mnemonic=brownie port=8545 to use these settings at the ganache-cli command
        # using single quotes at fork definition to use it as it is rather than having to constantly use the current env variable
        # performance-wise, better to fork Ethereum Mainnet from Alchemy, not infura, hence using https://eth-mainnet.alchemyapi.io/v2/s50JMrb0IHBfrZRQ5LATAN9vSB634O88 instead of '<infura> + <env var>'
        return accounts[0]
    else:
        return accounts.add(config["wallets"]["from_key"])


def deploy_mocks():
    print(f"The active network is {network.show_active()}")
    print("Deploying Mocks ...")
    # not deployng the mock if it has been deployed to the network before
    # checking <= since MockV3Aggregator will be a list of all MockV3Aggregators deployed
    if len(MockV3Aggregator) <= 0:
        # deploying the mock and adding 2 constructor params as per the contract design: _decimals and _initialAnswer
        # toWei() will just add 18 decimals to 2000
        MockV3Aggregator.deploy(
            DECIMALS, Web3.toWei(STARTING_PRICE, "ether"), {"from": get_account()}
        )
    print("Mocks deployed!")
