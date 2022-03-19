from brownie import FundMe, MockV3Aggregator, network, config
from scripts.helpful_scripts import (
    get_account,
    deploy_mocks,
    LOCAL_BLOCKCHAIN_ENVIRONMENTS,
)
from web3 import Web3


def deploy_fund_me():
    account = get_account()
    # also, we need to pass the price feed address to our FundMe contract to smoothly switch between Rinkeby and Ganache
    # if we are on a persistent network like Rinkeby, use the associated price feed address
    # else, deploy mocks
    # deploying the contract and saying that we'd like to publish the src code using ETHERSCAN_TOKEN (API key) from .env
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        price_feed_address = config["networks"][network.show_active()][
            "eth_usd_price_feed"
        ]
    # else, mocking the price feed contract
    else:
        deploy_mocks()
        price_feed_address = MockV3Aggregator[-1].address

    fund_me = FundMe.deploy(
        price_feed_address,
        {"from": account},
        publish_source=config["networks"][network.show_active()].get("verify"),
    )
    print(f"Contract deployed to {fund_me.address}")
    # returning fund_me so our test could work with it
    return fund_me


def main():
    deploy_fund_me()
