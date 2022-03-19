// SPDX-License-Identifier: MIT

pragma solidity ^0.6.6;

//importing Chainlink's npm package for price feeds
import "@chainlink/contracts/src/v0.6/interfaces/AggregatorV3Interface.sol";
//a library is deployed only once at a specific address and then reused
import "@chainlink/contracts/src/v0.6/vendor/SafeMathChainlink.sol";

contract FundMe {
    //using SafeMath for all uint256
    using SafeMathChainlink for uint256;

    //who send us how much
    mapping(address => uint256) public addressToAmountFunded;
    //creating an array of the funders' addresses to loop thru it to reset the mapping after withdraw() gets executed
    address[] public funders;
    address public owner;
    //setting a global variable to switch between Rinkeby and Ganache since for Ganache we will have to mock the price feed interface
    AggregatorV3Interface public priceFeed;

    //constructor is the function which gets executed at the contract's deployment
    //adding _priceFeed to switch between Rinkeby and Ganache since for Ganache we will have to mock the price feed interface
    constructor(address _priceFeed) public {
        priceFeed = AggregatorV3Interface(_priceFeed);
        owner = msg.sender;
    }

    //modifier is used to change the behavior of a function in a declarative way. E.g. define the only address(es) which can call the function.
    modifier onlyOwner() {
        require(
            msg.sender == owner,
            "You can't do this action because you are not the contract owner."
        );
        _;
    }

    // adding the entrance fee function to return the min payable fee
    // ??? why do we do (1e18 * 1e18) / 1e10 ? actually, we receive the price with 8 decimals, so it's (1e18 * 1e18) / (1e8 * 1e10) = 1e18 which makes sense
    function getEntranceFee() public view returns (uint256) {
        // minimum USD
        uint256 minimumUSD = 50 * 1e18;
        uint256 price = getPrice();
        uint256 precision = 1 * 1e18;
        // adding 1 to avoid the rounding error
        return ((minimumUSD * precision) / price) + 1;
    }

    //adding a function to accept the payments
    //payable means that the function call will be a transaction of funds
    function fund() public payable {
        //setting the funding min value at $50
        uint256 minUsd = 50 * 1e18;
        //if the require condition is not met, the tx is reverted as well as its unspent gas
        require(
            getConversionRate(msg.value) >= minUsd,
            "You need to send at least $50."
        );
        //msg.value accounts for the amount sent
        addressToAmountFunded[msg.sender] += msg.value;
        funders.push(msg.sender);
    }

    //getting version from AggregatorV3Interface
    function getVersion() public view returns (uint256) {
        return priceFeed.version();
    }

    //getting the ETH-in-terms-of-USD price data from AggregatorV3Interface
    function getPrice() public view returns (uint256) {
        //getting the tuple from latestRoundData();
        //using blanks to avoid unsued local variables
        (, int256 answer, , , ) = priceFeed.latestRoundData();
        //casting the return type from int256 to uint256 and returning the value in wei
        return uint256(answer * 1e10);
    }

    //making the function which converts the value sent by the sender into USD
    function getConversionRate(uint256 ethAmount)
        public
        view
        returns (uint256)
    {
        uint256 ethPrice = getPrice();
        //dividing into 1e18 since both ethPrice and ethAmount have 18 decimals
        uint256 ethAmountInUsd = (ethPrice * ethAmount) / 1e18;
        return ethAmountInUsd;
    }

    //getting all money senders have sent to us
    function withdraw() public payable onlyOwner {
        //transferring all balance of this address to the message sender
        msg.sender.transfer(address(this).balance);

        //resetting the funders' funding amounts to zero within our mapping
        for (
            uint256 funderIndex = 0;
            funderIndex < funders.length;
            funderIndex++
        ) {
            //grabbing each funder's address from the funders array and updating the mapping
            address funder = funders[funderIndex];
            addressToAmountFunded[funder] = 0;
        }

        //resetting the funders array to an empty address array
        funders = new address[](0);
    }
}
