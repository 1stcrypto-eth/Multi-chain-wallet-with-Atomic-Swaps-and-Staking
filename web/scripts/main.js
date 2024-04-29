var word_dict = {};
let password;
var seed_index;
var coin_purse = {};
var price_dict = {};
var currency;
var xmlDoc;
var auditedTx;
var BTCBalance;
var BCHBalance;
var LTCBalance;
var DASHBalance;
var DOGEBalance;

async function setSeedIndex(index) {
    window.seed_index = index;
    console.log("seed_index:" +seed_index);
}

async function getCryptoPrices() {
    window.price_dict = await eel.get_prices()();
}

async function getCoinPurse() {
    const seed = await eel.decrypt_seed(seed_index)();
    window.coin_purse = await eel.get_wallets(seed)();
    console.log(coin_purse);
}


async function getWords() {
// Create the JAVA containers (variable) and link them to the HTML container.
// There needs to be a container with the id= to the getElementById() argument.  (HTML Example for the argument used below <div id="word1_box"></div>)
    let word1_container = document.getElementById('word1_box');
    let word2_container = document.getElementById('word2_box');
    let word3_container = document.getElementById('word3_box');
    let word4_container = document.getElementById('word4_box');
    let word5_container = document.getElementById('word5_box');
    let word6_container = document.getElementById('word6_box');
    let word7_container = document.getElementById('word7_box');
    let word8_container = document.getElementById('word8_box');
    let word9_container = document.getElementById('word9_box');
    let word10_container = document.getElementById('word10_box');
    let word11_container = document.getElementById('word11_box');
    let word12_container = document.getElementById('word12_box');


// Call into Python and set the JAVA container equal to the Python variable
// Note the double ()() the first is for arguments intered into the function and the second is for callback function.

// In this case the function returns an object (Python Dict) which we can then access the "key/value" pairs

    word_dict = await eel.create_seed()();

    word1_container.innerHTML = word_dict.word1;
    word2_container.innerHTML = word_dict.word2;
    word3_container.innerHTML = word_dict.word3;
    word4_container.innerHTML = word_dict.word4;
    word5_container.innerHTML = word_dict.word5;
    word6_container.innerHTML = word_dict.word6;
    word7_container.innerHTML = word_dict.word7;
    word8_container.innerHTML = word_dict.word8;
    word9_container.innerHTML = word_dict.word9;
    word10_container.innerHTML = word_dict.word10;
    word11_container.innerHTML = word_dict.word11;
    word12_container.innerHTML = word_dict.word12;

}


async function getWallet(coin) {
    let QR = document.getElementById('QR');
    let address = document.getElementById('address');
    let balance = document.getElementById('balance');
    let USDbalance = document.getElementById('USDbalance');
    let titleContainer = document.getElementById('title');
    let descrContainer  = document.getElementById('description');


    QRloaded =  eel.make_qr(coin_purse[coin][0].address)();
    var QRcode = new Image;

    let title = xmlDoc.getElementsByTagName(coin)[0].children[0].innerHTML;

    let description = xmlDoc.getElementsByTagName(coin)[0].children[1].innerHTML;

    titleContainer.innerHTML = title;
    descrContainer.innerHTML = description;
    QRcode.onload = function()
        {

        QR.src = this.src;
        }
    QR.src = "images/QR.png";
    address.innerHTML = coin_purse[coin][0].address;

    //let acc_balance = await eel.get_balance(coin, coin_purse[coin][0].privkey)();//old version
    //donn't know why this doesn't work:
    //const acc_balance = getBalanceJS(coin)();
    //I'll try a much worse solution:
    const coin_list = ["BCH","BTC","LTC","DASH","DOGE","ZEC"];
    coin_list.forEach(getBalanceJS);
    if (coin == "BTC"){ acc_balance = BTCBalance} 
    else if (coin == "BCH"){ acc_balance = BCHBalance} 
    else if (coin == "LTC"){ acc_balance = LTCBalance} 
    else if (coin == "DASH"){ acc_balance = DASHBalance} 
    else if (coin == "DOGE"){ acc_balance = DOGEBalance} 
    console.log(acc_balance);

    let usd_balance = acc_balance*price_dict[coin].USD;

    balance.innerHTML = acc_balance;
    USDbalance.innerHTML = usd_balance;

}


async function getPrices() {

    await getCryptoPrices();
    let btc_usd_container = document.getElementById('btc_usd');
    let btg_usd_container = document.getElementById('btg_usd');
    let bch_usd_container = document.getElementById('bch_usd');
    let ltc_usd_container = document.getElementById('ltc_usd');
    let dash_usd_container = document.getElementById('dash_usd');
    let doge_usd_container = document.getElementById('doge_usd');
    let xrp_usd_container = document.getElementById('xrp_usd');
    let zec_usd_container = document.getElementById('zec_usd');
    let xlm_usd_container = document.getElementById('xlm_usd');

    //window.price_dict = await eel.get_prices()();
    btc_usd_container.innerHTML = '$' + price_dict.BTC.USD;
    btg_usd_container.innerHTML = '$' + price_dict.BTG.USD;
    bch_usd_container.innerHTML = '$' + price_dict.BCH.USD;
    ltc_usd_container.innerHTML = '$' + price_dict.LTC.USD;
    dash_usd_container.innerHTML = '$' + price_dict.DASH.USD;
    doge_usd_container.innerHTML = '$' + price_dict.DOGE.USD;
    xrp_usd_container.innerHTML = '$' + price_dict.XRP.USD;
    zec_usd_container.innerHTML = '$' + price_dict.ZEC.USD;
    xlm_usd_container.innerHTML = '$' + price_dict.XLM.USD;
}

async function getBalanceValue() {
    let btc_usd_value = document.getElementById('btc_usd_value');
    let btg_usd_value = document.getElementById('btg_usd_value');
    let bch_usd_value = document.getElementById('bch_usd_value');
    let ltc_usd_value = document.getElementById('ltc_usd_value');
    let dash_usd_value = document.getElementById('dash_usd_value');
    let doge_usd_value = document.getElementById('doge_usd_value');
    let xrp_usd_value = document.getElementById('xrp_usd_value');
    let zec_usd_value = document.getElementById('zec_usd_value');
    let xlm_usd_value = document.getElementById('xlm_usd_value');

    let btc_balance = document.getElementById('btc_balance');
    let btg_balance = document.getElementById('btg_balance');
    let bch_balance = document.getElementById('bch_balance');
    let ltc_balance = document.getElementById('ltc_balance');
    let dash_balance = document.getElementById('dash_balance');
    let doge_balance = document.getElementById('doge_balance');
    let xrp_balance = document.getElementById('xrp_balance');
    let zec_balance = document.getElementById('zec_balance');
    let xlm_balance = document.getElementById('xlm_balance');

    //price_dict = await eel.get_prices()();
    //console.log(price_dict);
    btc_usd_value.innerHTML = '$' + (Math.round((BTCBalance * price_dict.BTC.USD)*Math.pow(10,2))/Math.pow(10,2)).toFixed(2);
    btg_usd_value.innerHTML = '$' + (Math.round((btg_balance.innerHTML * price_dict.BTG.USD)*Math.pow(10,2))/Math.pow(10,2)).toFixed(2);
    bch_usd_value.innerHTML = '$' + (Math.round((BCHBalance * price_dict.BCH.USD)*Math.pow(10,2))/Math.pow(10,2)).toFixed(2);
    ltc_usd_value.innerHTML = '$' + (Math.round((LTCBalance * price_dict.LTC.USD)*Math.pow(10,2))/Math.pow(10,2)).toFixed(2);
    dash_usd_value.innerHTML = '$' + (Math.round((DASHBalance * price_dict.DASH.USD)*Math.pow(10,2))/Math.pow(10,2)).toFixed(2);
    doge_usd_value.innerHTML = '$' + (Math.round((DOGEBalance * price_dict.DOGE.USD)*Math.pow(10,2))/Math.pow(10,2)).toFixed(2);
    xrp_usd_value.innerHTML = '$' + (Math.round((xrp_balance.innerHTML * price_dict.XRP.USD)*Math.pow(10,2))/Math.pow(10,2)).toFixed(2);
    zec_usd_value.innerHTML = '$' + (Math.round((zec_balance.innerHTML * price_dict.ZEC.USD)*Math.pow(10,2))/Math.pow(10,2)).toFixed(2);
    xlm_usd_value.innerHTML = '$' + (Math.round((xlm_balance.innerHTML * price_dict.XLM.USD)*Math.pow(10,2))/Math.pow(10,2)).toFixed(2);
}

async function checkPassword() {
    console.log("Checking Password");
    let input = document.getElementById('loginpassword');
    var pass = input.value;
    let loginCheck = await eel.check_password(pass)();
    console.log("loginCheck");
    console.log(loginCheck);

    if (loginCheck > -1) {
        console.log("launching main window");
        window.seed_index = loginCheck;
        console.log(seed_index);
        return window.location.replace('mainWindow.html?index='+seed_index);

    } else {
        console.log("try again");
        return input.innerHTML = "Incorrect Password";
    }
}

function extractSeed() {

    var seed = "";
    for(var key in word_dict) {
      seed += word_dict[key] +  " ";
    }
    return seed;
}


async function setPassword() {

    let input = document.getElementById('newpassword');
    let pass = input.value;
    let seed = extractSeed();
    let loginCheck = await eel.set_password(pass, seed)();
    console.log(pass);
    console.log(seed);
    window.seed_index = -1;

    //let loginCheck = await eel.set_password(pass, seed)();

    return window.location.replace('mainWindow.html?index='+seed_index);
}


async function populateWallet(currency) {

    //reading xml doc
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = function() {
        if (this.readyState == 4 && this.status == 200) {
            console.log(xmlDoc);
            window.xmlDoc = xmlDoc.responseXML;

       }};
    xhttp.open("GET", "text.xml", true);
    xhttp.setRequestHeader("Content-Type", "text/xml");
    xhttp.send();
    window.xmlDoc = xhttp;

//console.log(seed_index);
//const seed = await eel.decrypt_seed(seed_index)();
//window.coin_purse = await eel.get_wallets(seed)();

    window.currency = currency

    await getCoinPurse();
    
    const coin_list = ["BCH","BTC","LTC","DASH","DOGE","ZEC"];
    coin_list.forEach(getBalanceJS);

    await getPrices();
    
    getBalanceValue();
    getWallet(currency);
}

async function getBalanceJS(currency){
    //Current Wallet Balance from Blockchain Explorers
    //Get BTC Balance
    if (currency == "BTC"){
    let btc_balance_response = await fetch(`https://blockchain.info/q/addressbalance/${coin_purse['BTC'][0].address}`);
    let btc_balance = await btc_balance_response.text();
    let btc_balance_container = document.getElementById('btc_balance');
    //let btc_balance_container2 = document.getElementById('btc_balance2');
    window.BTCBalance = btc_balance / 100000000;
    btc_balance_container.innerHTML = BTCBalance;
    //btc_balance_container2.innerHTML = btc_balance / 100000000;
    return BTCBalance;
}
    
    //Get BCH Balance
    else if (currency == "BCH"){
    var bch_cashaddr = coin_purse['BCH'][0].address;
    let bch_cashaddr_balance_request = await fetch(`https://api.blockchair.com/bitcoin-cash/dashboards/address/${bch_cashaddr}`);
    let bch_cashaddr_balance_response = await bch_cashaddr_balance_request.json();
    let bch_legacy_addr = await bch_cashaddr_balance_response["data"][bch_cashaddr]["address"]["formats"]["legacy"];
    let bch_balance_request = await fetch(`https://api.blockchair.com/bitcoin-cash/dashboards/address/${bch_legacy_addr}`);
    let bch_balance_response = await bch_balance_request.json();
    let bch_balance = bch_balance_response["data"][bch_legacy_addr]["address"]["balance"];
    let bch_balance_container = document.getElementById('bch_balance');
    window.BCHBalance = bch_balance / 100000000;
    bch_balance_container.innerHTML = BCHBalance;
    return BCHBalance;
    }

    //Get LTC Balance
    else if (currency == "LTC"){
    let ltc_balance_request = await fetch(`https://api.blockcypher.com/v1/ltc/main/addrs/${coin_purse['LTC'][0].address}/balance`);
    let ltc_balance_response = await ltc_balance_request.json();
    let ltc_balance = await ltc_balance_response['balance'];
    let ltc_balance_container = document.getElementById('ltc_balance');
    window.LTCBalance = ltc_balance / 100000000;
    ltc_balance_container.innerHTML = LTCBalance;
    return LTCBalance;
    }

    //Get DASH Balance
    else if (currency == "DASH"){
    let dash_balance_request = await fetch(`https://api.blockcypher.com/v1/dash/main/addrs/${coin_purse['DASH'][0].address}/balance`);
    let dash_balance_response = await dash_balance_request.json();
    let dash_balance = await dash_balance_response['balance'];
    let dash_balance_container = document.getElementById('dash_balance');
    window.DASHBalance = dash_balance / 100000000;
    dash_balance_container.innerHTML = DASHBalance;
    return DASHBalance;
    }

    //Get DOGE Balance
    else if (currency == "DOGE"){
    let doge_balance_request = await fetch(`https://dogechain.info/api/v1/address/balance/${coin_purse['DOGE'][0].address}`);
    let doge_balance_response = await doge_balance_request.json();
    let doge_balance = await doge_balance_response['balance'];
    let doge_balance_container = document.getElementById('doge_balance');
    window.DOGEBalance = doge_balance;
    doge_balance_container.innerHTML = doge_balance;
    return DOGEBalance;
    }
    
    //Get XRP Balance - Commented out until we create an XRP address 
    //let xrp_balance_request = await fetch(`http://data.ripple.com/v2/accounts/${coin_purse['XRP'][0].address}/balances/`);
    //let xrp_balance_response = await xrp_balance_request.json();
    //let xrp_balance = await xrp_balance_response['balances'][0]['value'];
    //let xrp_balance_container = document.getElementById('xrp_balance');
    //xrp_balance_container.innerHTML = xrp_balance;
    
    //Get ZCash Balance
    else if (currency == "ZEC"){
    let zec_balance_request = await fetch(`https://api.zcha.in/v2/mainnet/accounts/${coin_purse['ZCASH'][0].address}`);
    let zec_balance_response = await zec_balance_request.json();
    let zec_balance = await zec_balance_response['balance'];
    let zec_balance_container = document.getElementById('zec_balance');
    zec_balance_container.innerHTML = zec_balance; 
    return zec_balance;
    }   
    else{
        //Not sure here
        return 0;
    }
    
}

async function sendTx(){

    let SendToInput = document.getElementById('sendTo');
    let amountInput = document.getElementById('amount');
    let to = SendToInput.value;
    let amount = amountInput.value;

    tx = await eel.send_tx(currency, coin_purse[currency][0].privkey, to, amount);
}

function windowClose() {
    window.open('','_parent','');
    window.close();
}

function myFunction() {
  //console.log("Row index is: " + x.rowIndex);
}



//comment
async function getCurrencies() {

    let currencies = document.getElementById('currencies');

    currencies = eel.getCurrencies();

    console.log(currencies);

}


async function updateUSDVal(){
    const cryptoFromCon = document.getElementById('swapSendCrypto');
    const amountCon = document.getElementById('sendCryptoAmount');
    const usdValtoSendCon = document.getElementById('USDswapSend');

    const cryptoFrom = cryptoFromCon[cryptoFromCon.selectedIndex].value;
    const amount = amountCon.value;
    const price = price_dict[cryptoFrom].USD;

    const USD = (price*amount).toFixed(2);

    usdValtoSendCon.innerHTML = "$"+USD;
}

async function displayDetails(tx){
    //coin_purse = await eel.get_wallets(seed)();

    const txLinkCon = document.getElementById('txLink');
    const txRecAddCon = document.getElementById('txRecAdd');
    const youWillReceiveCon = document.getElementById('youWillReceive');
    const USDreceivingCon = document.getElementById('USDreceiving');

    //seed = await eel.decrypt_seed(seed_index)();
    //let coin_purse = await eel.get_wallets(seed)();
  
    let msg = "";
    const cur = tx["value_text"].split(" ");
    console.log(cur[1]);
    //let myAddrss = eel.derive_wallets(seed, cur, 2);
    //const myAddr = myAddrss[0];
    
    const myAddr = coin_purse[cur[1]][0].address;
    const recipientAddr = tx["recipient_address"];

    if (myAddr == recipientAddr){msg = ". Address found successfuly. Everything looks good."}
    else {msg = ". ALERT: Address not found in this wallet!"}

    const usdVal = parseFloat(tx["value"])*price_dict[cur[1]].USD;

    txLinkCon.innerHTML = tx["transaction_link"];
    txRecAddCon.innerHTML = recipientAddr + msg;
    youWillReceiveCon.innerHTML = tx["value_text"];
    USDreceivingCon.innerHTML = "$" + usdVal.toFixed(2) + " USD.";
    
}
async function auditTx(){
    const receivingCryptoCon = document.getElementById('partReceiveCrypto');
    const contractCon = document.getElementById('particContractN');
    const partTxAddCon = document.getElementById('partTxAdd');

    const cryptoFrom = receivingCryptoCon[receivingCryptoCon.selectedIndex].value;

    window.auditedTx = await eel.audit_tx(cryptoFrom, contractCon.value, partTxAddCon.value, false)();
    console.log(auditedTx);
    displayDetails(auditedTx);

    return auditedTx;
}

async function participate(){
    const receivingCryptoCon = document.getElementById('partReceiveCrypto');
    const sendingCryptoCon = document.getElementById('partSendCrypto');
    const contractCon = document.getElementById('particContractN');
    const partTxAddCon = document.getElementById('partTxAdd');
    const partSendToAddCon = document.getElementById('partToAdd');
    //const contractDisplayCon = document.getElementById('partContractInfo');
    const contractAddCon = document.getElementById('partContractAdd');
    const starterTxCon = document.getElementById('partTxNum');

    const receivingCur = receivingCryptoCon[receivingCryptoCon.selectedIndex].value;
    const sendingCur = sendingCryptoCon[sendingCryptoCon.selectedIndex].value;
    const sendTo = partSendToAddCon.value;

    const amountToSend = auditedTx.value * price_dict[receivingCur].USD / price_dict[sendingCur].USD;

    tx = await eel.participateSwap(sendingCur, 
            receivingCur, 
            coin_purse[sendingCur][0].privkey, 
            sendTo, amountToSend, 
            contractCon.value, 
            partTxAddCon.value)();


    console.log(tx);
    //var details = "";
    //for(var key in tx) {
    //    details += key +": " + tx[key] + "\n";
   // }
    //contractDisplayCon.innerHTML = details;
    contractAddCon.innerHTML = tx.contract;
    starterTxCon.innerHTML = tx.transaction_address;
    return tx;

}

async function redeem(){
    const cryptoToCon = document.getElementById('swapReceiveCrypto');
    const contractNumCon = document.getElementById('incomingContractAdd');
    const txAddCon = document.getElementById('incomingTxNum');

    const cryptoTo = cryptoToCon[cryptoToCon.selectedIndex].value;

    redeem_tx = await eel.redeem_tx(cryptoTo,
        coin_purse[cryptoTo][0].privkey, // CHANGE [0] TO coin_purse[cryptoTo][0].privkey. ONLY FOR DEVELOPING PURPOSES
        contractNumCon.value, txAddCon.value)();

    console.log(redeem_tx);

}

async function finishSwap(){
    const receivingCryptoCon = document.getElementById('partReceiveCrypto');
    const sendingCryptoCon = document.getElementById('partSendCrypto');
    const contractCon = document.getElementById('particContractN');
    const partTxAddCon = document.getElementById('partTxAdd');

    const receivingCur = receivingCryptoCon[receivingCryptoCon.selectedIndex].value;
    const sendingCur = sendingCryptoCon[sendingCryptoCon.selectedIndex].value;

    tx = await eel.finish_swap(sendingCur, receivingCur, coin_purse[receivingCur][0].privkey,
        contractCon.value, partTxAddCon.value)
    console.log(tx)
}


async function startSwap(){
    const cryptoFromCon = document.getElementById('swapSendCrypto');
    const cryptoToCon = document.getElementById('swapReceiveCrypto');
    const amountCon = document.getElementById('sendCryptoAmount');
    const swapToAddCon = document.getElementById('swapToAdd');
    const contractAddCon = document.getElementById('myContractAdd');
    const starterTxCon = document.getElementById('myTxNum');
    const cryptoEquiCon = document.getElementById('cryptoEqui');


    const cryptoFrom = cryptoFromCon[cryptoFromCon.selectedIndex].value;
    const cryptoTo = cryptoToCon[cryptoToCon.selectedIndex].value;
    const amount = amountCon.value;
    const toAdd = swapToAddCon.value;
    const sending = price_dict[cryptoFrom].USD * amount;
    const receiving = sending / price_dict[cryptoTo].USD;

    //cryptoEquiCon.innerHTML = receiving;
    let tx = await eel.start_atom_swap(cryptoFrom, coin_purse[cryptoFrom][0].privkey, toAdd, amount)();
    contractAddCon.innerHTML = tx.contract;
    starterTxCon.innerHTML = tx.transaction_address;


}


async function loadSwapWindow(){
    getCoinPurse();
    getCryptoPrices();
}

async function swapWindow(){
    return window.location.replace('swapWindow.html?index='+seed_index);
}

async function launchMainWindow(){
    return window.location.replace('mainWindow.html?index='+seed_index);
}


async function predictionsWindow(){
    return window.location.replace('predictionsWindow.html?index='+seed_index);
}

async function stakingWindow(){
    return window.location.replace('stakingWindow.html?index='+seed_index);
}

async function exchangeWindow(){
    return window.location.replace('exchangeWindow.html?index='+seed_index);
}

async function loadJSON(file_name) {

    var xmlhttp = new XMLHttpRequest();
    xmlhttp.onreadystatechange = function() {
      if (this.readyState == 4 && this.status == 200) {
          console.log(this);
        //document.getElementById("demo").innerHTML = myObj.name;
      }
    };
    xmlhttp.open("GET", file_name, true);
    xmlhttp.send();
    return xmlhttp;
 }

 function openSwapTab(evt, option) {
    // Declare all variables
    var i, tabcontent, tablinks;

    // Get all elements with class="tabcontent" and hide them
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
      tabcontent[i].style.display = "none";
    }

    // Get all elements with class="tablinks" and remove the class "active"
    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
      tablinks[i].className = tablinks[i].className.replace(" active", "");
    }

    // Show the current tab, and add an "active" class to the button that opened the tab
    document.getElementById(option).style.display = "block";
    evt.currentTarget.className += " active";
}

async function get_ml_price_dict(mltable) {
    window.mltable = mltable;
    let results = await eel.get_price_dict(mltable)();
    console.log(results);
    todays_price.innerHTML = "$" + results.todays_price;
    tomorrows_prediction.innerHTML = "$" + results.tommorows_prediction;
    upper_limit.innerHTML = "$" + results.upper_limit;
    lower_limit.innerHTML = "$" + results.lower_limit;
}


async function createTransaction(){

    let fromCurrencyContainer = document.getElementById('from-currency');
    let sendAmountContainer = document.getElementById('send-amount');
    let toCurrencyContainer = document.getElementById('to-currency');
    let walletAddressContainer = document.getElementById('wallet-address');

    let changellyAddress = document.getElementById('changellyAddress')


    fromCurrency = fromCurrencyContainer.value
    sendAmount = sendAmountContainer.value
    toCurrency = toCurrencyContainer.value
    walletAddress = walletAddressContainer.value


    let changellyAddress2 = await eel.createTransaction(fromCurrency,toCurrency,walletAddress,sendAmount)();
    changellyAddress.innerHTML = changellyAddress2;

}
