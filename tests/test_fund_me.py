# importing exceptions from brownie to make sure that an exception rise, the test is passed given this exception is the expected test result
from brownie import network, accounts, exceptions
from scripts.helpful_scripts import get_account, LOCAL_BLOCKCHAIN_ENVIRONMENTS
from scripts.deploy import deploy_fund_me
import pytest


def test_can_fund_and_withdraw():
    account = get_account()
    fund_me = deploy_fund_me()
    # adding +100 just in case we need a little bit more money for whatever reason
    entrance_fee = fund_me.getEntranceFee() + 100
    tx1 = fund_me.fund({"from": account, "value": entrance_fee})
    tx1.wait(1)
    # asserting that the mapping recorded our funding of a min entrance fee
    assert fund_me.addressToAmountFunded(account.address) == entrance_fee
    tx2 = fund_me.withdraw({"from": account})
    tx2.wait(1)
    # asserting we cleaned the mapping after successfully withdrawing
    assert fund_me.addressToAmountFunded(account.address) == 0


# test to make sure that only the owner can withdraw
def test_only_owner_can_withdraw():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        # skipping the test if the network is not local
        pytest.skip("This function is only for local testing")
    fund_me = deploy_fund_me()
    bad_actor_account = accounts.add()
    # telling python that if this test reverts with a VM error, it's good and expected
    with pytest.raises(exceptions.VirtualMachineError):
        fund_me.withdraw({"from": bad_actor_account})
