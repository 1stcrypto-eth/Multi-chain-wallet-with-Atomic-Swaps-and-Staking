from py_hd_wallet import wallet
import eel
import re
from urllib.request import Request, urlopen
import json
import hashlib
import os
import scrypt
import qrcode
from constants import *
from web3 import Web3
from dotenv import load_dotenv
from eth_account import Account 
import subprocess
from bit import Key, PrivateKey, PrivateKeyTestnet
from bit.crypto import ECPrivateKey
from bit.curve import Point
from bit.format import (
    bytes_to_wif, public_key_to_address, public_key_to_coords, wif_to_bytes
)
from bit.network import NetworkAPI, get_fee_cached, satoshi_to_currency_cached
from bit.network.meta import Unspent
#from bit.transaction import calc_txid, create_p2pkh_transaction, sanitize_tx_data
from web3.middleware import geth_poa_middleware
from path import Path
import pandas as pd
from ML.ml_functions import get_arima_forecast_plot, get_rf_ensemble_plot
import pprint as pp
import requests
import hmac
from threading import Thread

if __name__ == '__main__':
    Thread(target=get_rf_ensemble_plot).start()
    Thread(target=get_arima_forecast_plot).start()

eel.init('web')

load_dotenv()

#Wallet Functions


@eel.expose
def create_seed():
    seed = re.sub("[^\w]", " ",  wallet.generate_mnemonic()).split()
    count = 0
    seed_dict = {}
    for word in seed:
        count += 1
        word_count = "word" + str(count)
        seed_dict.update( {word_count : word} )
        os.environ[word_count] = word
    return seed_dict

@eel.expose
def derive_wallets(mnemonic, coin, nkeys):

    command = f'php ./hd-wallet-derive/hd-wallet-derive.php --mnemonic="{mnemonic}" --coin={coin} --numderive={nkeys}  --format=json -g'
    available_coins = "./hd-wallet-derive.php --help-coins" # --> currently not in use
    new_process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)

    (output, err) = new_process.communicate()

    p_status = new_process.wait()

    if err:
        print("\nError:###\n\n")
        return err
    return json.loads(output)

coin_purse = {}


@eel.expose
def get_wallets(seed):
    #print(f"get_wallet. seed: \n{seed}")
    """
    coins = ['BTC','BTG','BCH','LTC','DASH','DOGE','XRP','ZCASH','XLM']
    global coin_purse 
    for coin in coins:
        w = wallet.create_wallet(network=coin, seed=seed, children=1)
        coin_purse.update({
            coin : {"address": w['address'],
                   "privatek": w["xprivate_key"],
                   "publick" : w["xpublic_key"],
                   "children": w["children"]
                   }
                   # a disadvantage of hd_derive_wallet is that it doesn't generate 
                   # a specific child. For instance, like the child with index 19384.
                   # So you are forced to create the whole chain of child addresses
                   # from 0 to 19384.
        })"""
    coin_purse = {  #We'll have to add more coins, specially ERC20 tokens
    "ETH"     : derive_wallets(seed, "ETH", 2), 
    "BTC-test": derive_wallets(seed, "BTC-test", 2),
    "BTC"     : derive_wallets(seed, "BTC", 2),
    "BTG"     : derive_wallets(seed, "BTG", 2),
    "BCH"     : derive_wallets(seed, "BCH", 2),
    "LTC"     : derive_wallets(seed, "LTC", 2),
    "DASH"    : derive_wallets(seed, "DASH", 2),
    "DOGE"   : derive_wallets(seed, "DOGE", 2),
    #"XRP"     : derive_wallets(seed, "XRP", 10), #https://bitcoin.stackexchange.com/questions/75385/does-ripple-has-support-for-hd-wallets
    "ZCASH"   : derive_wallets(seed, "ZEC", 2),
    #"XML"     : derive_wallets(seed, "XML", 10),
}
    return coin_purse

@eel.expose
def priv_key_to_account(coin, priv_key):
    """Use it like this: my_btctest_account = priv_key_to_account("btc-test",coin_purse["btc-test"][0]["privkey"])"""
    if coin == "ETH":        
        return Account.privateKeyToAccount(priv_key)       
    elif coin == "BTC-test": 
        return PrivateKeyTestnet(priv_key)  
    elif coin == "BTC":
        print("a btc account is being created")
        acc = PrivateKey(priv_key) 
        return acc 
    else:                    
        return "Not a supported coin"

    
def create_tx(coin, account, to, amount):
    """
    coin options: eth, btc-test, btc.
    account: account containing all the info like private and public 
    key as well as address of a certain account. This must be obtained
    trough the method priv_key_to_account().
    to: address to transfer funds.
    amount: amount of the currency. Take into account that Ether must 
    be expressed in weis.
    """
    if coin == "ETH":
        gas_estimate = w3.eth.estimateGas(
            {
                "from": account.address,
                "to": to,
                "value": amount
            }
        )

        return {
            "from": account.address,
            "to": to,
            "value": amount,
            "gasPrice": w3.eth.gasPrice,
            "gas": gas_estimate,
            "nonce":w3.eth.getTransactionCount(account.address)
        }

    elif coin == "btc-test":
        return PrivateKeyTestnet.prepare_transaction(account.address, [(to, amount, BTC)])
    
    elif coin == "BTC":
        return PrivateKey.prepare_transaction(account.address, [(to, amount, BTC)])
    
    else:
        return "Not a supported coin"

@eel.expose
def send_tx(coin, privkey, to, amount):
    """
    coin options: eth, btc-test.
    privkey: ignore this (have to fix it): account containing all the info like private and public 
    key as well as address of a certain account. This must be obtained
    trough the method priv_key_to_account().
    to: address to transfer funds.
    amount: amount of the currency. Take into account that Ether must 
    be expressed in weis.
    Example: send_tx(coin = "btc-test",account = my_btctest_account, to = coin_purse["btc-test"][1]["address"],amount= 0.01)
    """  
    #print(f"{coin}, {privkey}, {to}, {amount}")
    tx = create_tx(coin, priv_key_to_account(coin, privkey), to, amount)
    print(tx)
    signed_tx = priv_key_to_account(coin, privkey).sign_transaction(tx) #how to do this tho
    
    if coin == "ETH": 
        result = w3.eth.sendRawTransaction(signed_tx.rawTransaction)
        return result.hex()
    
    elif coin == "btc-test":
        result = NetworkAPI.broadcast_tx_testnet(signed_tx)
        return result
    
    elif coin == "BTC":
        result = NetworkAPI.broadcast_tx(signed_tx)
        print(result)
        return result
    
    else:
        return "Not a supported coin"
    

@eel.expose
def get_balance(coin, privkey):
    
    balance = -1
    
    if coin == "ETH": 
        return w3.eth.getBalance(priv_key_to_account(coin, privkey).address)
            
    elif coin == "BTC-test" or coin == "BTC":        
        balance = priv_key_to_account(coin, privkey).get_balance("btc")
        return balance
    
    else:
        return "Not a supported coin"
    
@eel.expose
def make_qr(address):
    """
    address: string format of address
    """
    qrcode.make(address).save("web/images/QR.png")
    return True



@eel.expose
def get_seed():
    seed_phrase = ""
    for i in range(12):
        word = "word" + str(i + 1)
        seed_phrase += os.environ[word] + " "
    return seed_phrase
    

@eel.expose
def decrypt_seed(seed_index, ecnrypted=True): #set ecnrypted=False ONLY for developing purposes
    print(f"seed index: {seed_index}")
    password = "Wallet #1 in 2020" # For right now, the password doesn't count.
    seed_path = Path(f".pwd.csv")
    seed_df = pd.read_csv(seed_path)

    if ecnrypted: 
        ecnrypted_seed =bytes.fromhex(seed_df["seed"].iloc[int(seed_index)]) 
        decrypted = scrypt.decrypt(ecnrypted_seed, password, maxtime=0.4)

    else: decrypted =  seed_df["seed"].iloc[int(seed_index)]

    #print(f"decrypted seed: \n{decrypted}")
    return decrypted
  

    
#Dashboard Functions

def read_json(url):
    request = Request(url)
    response = urlopen(request)
    data = response.read()
    url2 = json.loads(data)
    return url2

@eel.expose
def get_prices(ticker_list = ['BTC','BTG','BCH','LTC','DASH','DOGE','XRP','ZEC','XLM']): 
    # Leaving this an argument instead of fixed string for flexibility, can be simpler/faster with fixed url input
    ticker_string=""
    for ticker in ticker_list:
        ticker_string += ticker+","
    url = f"https://min-api.cryptocompare.com/data/pricemulti?fsyms={ticker_string}&tsyms=USD"
    price_data = read_json(url)
    return price_data


# Password Functions

def hash_pass(pass_w, salt):
    return scrypt.encrypt(pass_w , salt, maxtime=0.2)

@eel.expose
def set_password(pass_w, seed, ecnrypted=True): #set ecnrypted=False ONLY for developing purposes
    
    if ecnrypted:  
        password = {"seed": [hash_pass(seed ,"Wallet #1 in 2020").hex()], #we encrypt the mnemonic seed with the password
               "password": [hash_pass(pass_w,"super wallet").hex()]} #ecnryption of the password with a salt
    else:
        password = {"seed": [seed],
               "password": [pass_w]} 

    psw_df = pd.DataFrame(password)    
    pass_path = Path(f".pwd.csv")
    
    try:
        current_df = pd.read_csv(pass_path)
        print("found file")
        current_df.drop(columns=["Unnamed: 0"], inplace = True)        
        updated_df = pd.concat([current_df, psw_df], axis = 0, ignore_index=True, sort=True)
        print("concatenated succesfully")
        print(updated_df)
        updated_df.to_csv(pass_path)
        
    except:
        print("no password db found")
        psw_df.to_csv(pass_path)

    return True

@eel.expose
def check_password(pass_w, ecnrypted=True): #set ecnrypted=False ONLY for developing purposes
   
    pass_path = Path(f".pwd.csv")
    password = pd.read_csv(pass_path)
    if ecnrypted:
        for row in range(password.shape[0]):
            ecnrypted_pass =bytes.fromhex(password["password"].iloc[row])   
            decrypted = scrypt.decrypt(ecnrypted_pass,'super wallet',maxtime=0.4)
            if decrypted == pass_w: 
                return row
        print("no password found")
        return -1
    else:
        for row in range(password.shape[0]):
            decrypted =password["password"].iloc[row]  
            if decrypted == pass_w: 
                return row
        print("no password found")
        return -1

API_URL = 'https://api.changelly.com'

@eel.expose
def getCurrencies():
    '''
    Should be called when the user goes to the exchange screen. No Parameters.
    
    Should return a list of possible swaps.
    
    120 X 119 pairs, at 14280 possibiliy pairs
    '''
    #API CALL
    message = {
    'jsonrpc': '2.0',
    'id': 1,
    'method': 'getCurrencies', #getCurrenciesFull will return all available and their state
    'params': []
    }

    serialized_data = json.dumps(message)

    sign = hmac.new(API_SECRET.encode('utf-8'), serialized_data.encode('utf-8'), hashlib.sha512).hexdigest()

    headers = {'api-key': API_KEY, 'sign': sign, 'Content-type': 'application/json'}
    
    response_getcurrencies = requests.post(API_URL, headers=headers, data=serialized_data)
    
    #Error handling if serve is down or crashes
    if '<Response [200]>' == str(response_getcurrencies) :
        pass
    else:
        raise ValueError("Serve may have crashed or is down for repairs. Please try again later.")
    
    #List of possible currencies
    list_of_currencies = response_getcurrencies.json()['result']
    
    return list_of_currencies


def getNetwork(coin):

    network=None

    if coin == "BTG": 
        from clove.network import BitcoinGold
        network = BitcoinGold()
    elif coin == "LTC": 
        from clove.network import Litecoin
        network = Litecoin()
    elif coin == "BTC": 
        from clove.network import Bitcoin
        network = Bitcoin()
    elif coin == "DASH": 
        from clove.network import Dash
        network = Dash()
    else: return "Coin not supported"

    return network


@eel.expose
def get_Currencies():
    '''
    Should be called when the user goes to the exchange screen. No Parameters.
    
    Should return a list of possible swaps.
    
    120 X 119 pairs, at 14280 possibiliy pairs
    '''
    #API CALL
    message = {
    'jsonrpc': '2.0',
    'id': 1,
    'method': 'getCurrencies', #getCurrenciesFull will return all available and their state
    'params': []
    }

    serialized_data = json.dumps(message)

    sign = hmac.new(API_SECRET.encode('utf-8'), serialized_data.encode('utf-8'), hashlib.sha512).hexdigest()

    headers = {'api-key': API_KEY, 'sign': sign, 'Content-type': 'application/json'}
    
    response_getcurrencies = requests.post(API_URL, headers=headers, data=serialized_data)
    
    #Error handling if serve is down or crashes
    if '<Response [200]>' == str(response_getcurrencies) :
        pass
    else:
        raise ValueError("Serve may have crashed or is down for repairs. Please try again later.")
    
    #List of possible currencies
    list_of_currencies = response_getcurrencies.json()['result']
    
    return list_of_currencies

@eel.expose
def getMinAmount(currency1,currency2):
    """
    Currencies must be strings for now
    
    Function should take in two arguments, from and to currencies from the above
    
    Should check against the getCurrencies function and return invalids
    
    Should return the minimum amount that Changelly will take to execute the swap
    """
    currencies = get_Currencies()

    if currency1 == currency2:
        raise ValueError("You already have this currency. Duh.")
    else:
        pass
    
    if (currency1 in currencies):
        pass
    else:
        raise ValueError("See getCurrencies(). Currency is not accepted by this Wallet's Exchange Engine. Please enter a valid currency from our list.")
        
    if (currency2 in currencies):
        pass
    else:
        raise ValueError("See getCurrencies(). Currency is not accepted by this Wallet's Exchange EnginePlease enter a valid currency from our list.")

    message = {
   "jsonrpc": "2.0",
   "id": "test", #test?
   "method": "getMinAmount",
   "params": {
      "from": f"{currency1}",
      "to": f"{currency2}", }}

    serialized_data = json.dumps(message)

    sign = hmac.new(API_SECRET.encode('utf-8'), serialized_data.encode('utf-8'), hashlib.sha512).hexdigest()

    headers = {'api-key': API_KEY, 'sign': sign, 'Content-type': 'application/json'}
    
    response_minamount = requests.post(API_URL, headers=headers, data=serialized_data)
    
    #Just in case
    if '<Response [200]>' == str(response_minamount) :
        pass
    else:
        raise ValueError("Serve may have crashed or is down for repairs. Please try again later.")
    
    minamount = response_minamount.json()['result']
    
    minamount = float(minamount)
    
    return minamount

@eel.expose
def getExchangeAmount(currency1, currency2, amount):
    '''
    Should be just like the getMinAmount function. Will additionally take the amount the user wants to send in the from coin.
    
    Will take two currencies and return what what the user should expect in the returning coin
    
    For example, if the user is sending BTC for ETH, this function will tell the user how much ETH to expect in return.
    
    For example, if the user wants to send .001 BTC for ETH this will return 0.051771200000000000 as of 1/19/20 at 4:00 pm Centeral
    '''
    currencies = get_Currencies()
    
    if currency1 == currency2:
        raise ValueError("You already have this currency. Duh.")
    else:
        pass
    
    if (currency1 in currencies):
        pass
    else:
        raise ValueError("See getCurrencies(). Currency is not accepted by this Wallet's Exchange Engine. Please enter a valid currency from our list.")
        
    if (currency2 in currencies):
        pass
    else:
        raise ValueError("See getCurrencies(). Currency is not accepted by this Wallet's Exchange EnginePlease enter a valid currency from our list.")

    minamount = getMinAmount(currency1,currency2)
    
    if amount >= minamount:
        pass
    else:
        raise ValueError(f"This amount needs to be greater than or equal to {minamount}")
    
    message = {
   "jsonrpc": "2.0",
   "id": "test",
   "method": "getExchangeAmount",
   "params": {
      "from": f"{currency1}",
      "to": f"{currency2}",
      "amount": f"{amount}"},}

    serialized_data = json.dumps(message)

    sign = hmac.new(API_SECRET.encode('utf-8'), serialized_data.encode('utf-8'), hashlib.sha512).hexdigest()

    headers = {'api-key': API_KEY, 'sign': sign, 'Content-type': 'application/json'}

    response_estXamount = requests.post(API_URL, headers=headers, data=serialized_data)
    
        #Just in case
    if '<Response [200]>' == str(response_estXamount) :
        pass
    else:
        raise ValueError("Serve may have crashed or is down for repairs. Please try again later.")
    
    est_exch_amount = response_estXamount.json()['result']
    
    est_exch_amount = float(est_exch_amount)
    
    return est_exch_amount

#Create Transaction Function

@eel.expose
def createTransaction(currency1, currency2, TOaddress, amount, extraId = 'NULL', refund_address = 'NULL'):
    '''
    This function will take:
    From currency, lower case ticker, string
    To currency, lower case ticker, string
    Address for the currency to be sent To, string
    Extraid for currencies that need this extra address, default null, string  ((XRP, XLM, EOS, IGNIS, BNB, XMR, ARDOR, DCT, XEM))
    Amount to send From Currency to To currency, function will check against exchange amount
    
    This function CAN return (more info at https://old.changelly.com/developers)
    amountExpectedFrom - amount from createTransaction
    amountExpectedTo - result from getExchangeAmount at the moment of createTransaction
    amountTo - Real amount after the exchange that was sent to payoutAddress 
    apiExtraFee - Your API Extra fee in percents
    changellyFee - Changelly fee in percents
    createdAt - Point of time when the transaction was created
    currencyFrom - Ticker of output currency
    currencyTo - Ticker of input currency
    id - Transaction ID. Could be used in getStatus method
    payinAddress - Address for a user to send coins to
    payinExtraId - ExtraId for payinAddress in case it is required
    payoutAddress - Address where the exchange result will be sent to
    payoutExtraId - ExtraId for payoutAddress in case it is required
    status - Transaction status
    
    This will produce the Changely Wallet that the user will send their FROM coins to. 
    
    Changely will send their currency (matching TO currency) to the TOO currency IF funds are sent.
    
    Changely does charge a fee in percent (o.5 as of this writting).

    '''
    refund_address = TOaddress
    
    currencies = get_Currencies()
    
    if currency1 == currency2:
        raise ValueError("You already have this currency. Duh.")
    else:
        pass
    
    if (currency1 in currencies):
        pass
    else:
        raise ValueError("See getCurrencies(). Currency is not accepted by this Wallet's Exchange Engine. Please enter a valid currency from our list.")
        
    if (currency2 in currencies):
        pass
    else:
        raise ValueError("See getCurrencies(). Currency is not accepted by this Wallet's Exchange EnginePlease enter a valid currency from our list.")

    minamount = getMinAmount(currency1,currency2)
    
    if amount >= minamount:
        pass
    else:
        raise ValueError(f"This amount needs to be greater than or equal to {minamount}")

    message = {
   "jsonrpc": "2.0",
   "id": "test",
   "method": "createTransaction",
   "params": {
      "from": f"{currency1}",
      "to": f"{currency2}",
      "address": f"{TOaddress}", #valid to address... in this case XLM
      "extraId": f"{extraId}",
      "amount": f"{amount}",
       "refund": f"{refund_address}"}}

    serialized_data = json.dumps(message)

    sign = hmac.new(API_SECRET.encode('utf-8'), serialized_data.encode('utf-8'), hashlib.sha512).hexdigest()

    headers = {'api-key': API_KEY, 'sign': sign, 'Content-type': 'application/json'}
    
    response_create_tran = requests.post(API_URL, headers=headers, data=serialized_data)
    
    #Just in case
    if '<Response [200]>' == str(response_create_tran) :
        pass
    else:
        raise ValueError("Serve may have crashed or is down for repairs. Please try again later. Please do not transact any funds until you can verify (by re-examining this page) that the server is up and running.")
    
    result = response_create_tran.json()['result']
    
    #all the results listed below
    
    amountExpectedFrom = float(result['amountExpectedFrom']) #Should match to amount
    amountExpectedTo = float(result['amountExpectedTo']) #amount user will expect in return
    amountTo = float(result['amountTo']) #Real amount after the exchange that was sent to payoutAddress
    apiExtraFee = float(result['apiExtraFee']) #amount our wallet will charge
    changellyFee = float(result['changellyFee']) 
    createdAt = result['createdAt'] 
    currencyFrom = result['currencyFrom'] 
    currencyTo = result['currencyTo'] 
    ID = result['id'] 
    kycRequired = result['kycRequired'] 
    payinAddress = result['payinAddress'] #address to send funds to for Graphly to complete the exchange.
    payinExtraId = result['payinExtraId'] 
    payoutAddress = result['payoutAddress'] #users address Graphly will send to. Same as ToAddress
    payoutExtraId = result['payoutExtraId'] 
    status = result['status'] 
    
    if kycRequired == False:
        pass
    else:
        raise ValueError('This currency requires an additional property address. Those currencies are (XRP, XLM, EOS, IGNIS, BNB, XMR, ARDOR, DCT, XEM)')
    
    if payoutAddress == TOaddress:
        pass
    else:
        raise ValueError("Unknown Error. TOaddress and Changelly poyout address Mismatch. Dangerous, do not send.")
    
    if amount == float(amountExpectedFrom):
        pass
    else:
        raise ValueError(f"Unknown Error. Amount ({amount}) the amount expend ({amountExpectedFrom}) mismatch. Dangerous, do not send.")
    
    floating_expected = getExchangeAmount(currency1,currency2, amount)
    
    floating_fee = (float(changellyFee)/100)*floating_expected
    
    floating_fee_wallet = floating_expected * .04
    
    fee = floating_fee + floating_fee_wallet
    
    floating_return = floating_expected - floating_fee
    
    difference = float(amountExpectedTo) - floating_return
    
    Status = getStatus(ID)
    
    get_transaction = getTransactions(currencyFrom,currencyFrom)
    
    #get_transaction, Status, fee, amountExpectedFrom, amountExpectedTo, amountTo, apiExtraFee,changellyFee,createdAt, currencyFrom, currencyTo, ID, kycRequired, payinAddress, payinExtraId,payoutAddress, payoutExtraId, status
    
    return payinAddress



@eel.expose
def start_atom_swap(coin, privkey, to, amount):
    print(f"{coin},{privkey},{to},{amount}")
    network = getNetwork(coin)
    
    print(network)
    sendWallet = network.get_wallet(private_key=privkey)
    print(f"balance of sendWallet: {network.get_balance(sendWallet.address)}")
    initial_transaction = network.atomic_swap(
        sender_address=sendWallet.address,
        recipient_address=to,
        value=float(amount) 
        )
    initial_transaction.add_fee_and_sign(sendWallet)
    tx_details = initial_transaction.show_details()
    initial_transaction.publish()
    with open("startedSwap.json", "w") as write_file:
        json.dump(tx_details, fp=write_file, indent=4, sort_keys=True, default=str)
    #json_tx = json.dumps(tx_details, indent=4, sort_keys=True, default=str)
    #print(json_tx)
    return tx_details


@eel.expose
def audit_tx(coin, _contract, _transaction_address, local=True):

    network = getNetwork(coin)

    audited_contract = network.audit_contract(contract=_contract,transaction_address= _transaction_address)
    tx = audited_contract.show_details()
    if local: return audited_contract
    else: return tx

@eel.expose
def participateSwap(sendingCur, receivingCur, privkey, to, amount, _contract, _transaction_address):

    #contractNetwork = getNetwork(receivingCur)
    partNetwork = getNetwork(sendingCur)
    try:
        contract = audit_tx(receivingCur, _contract, _transaction_address)
    except:
        return "Contract with Tx address {_transaction_address} not found. Please retry later."

    wallet = partNetwork.get_wallet(private_key=privkey)
    print(f"balance of sendWallet: {partNetwork.get_balance(wallet.address)}")
    participate_transaction = contract.participate(
        symbol=sendingCur,
        sender_address=wallet.address,
        recipient_address=to,
        value=float(amount),)
    participate_transaction.add_fee_and_sign(wallet)
    tx_details = participate_transaction.show_details()
    
    with open("participatedSwap.json", "w") as write_file:
        json.dump(tx_details, fp=write_file, indent=4, sort_keys=True, default=str)
    json_tx = json.dumps(tx_details, indent=4, sort_keys=True, default=str)
    print(json_tx)

    participate_transaction.publish()

    return tx_details

@eel.expose
def redeem_tx(coin, privkey, _contract, _transaction_address):

    network = getNetwork(coin)
    
    print(network)
    wallet = network.get_wallet(private_key=privkey)
    print(f"balance of sendWallet: {network.get_balance(wallet.address)}")
    try:
        contract = audit_tx(coin, _contract, _transaction_address)
    except:
        return f"Contract with Tx address {_transaction_address} not found. Please retry later."

    with open('startedSwap.json') as f:
        data = json.load(f)

    redemption = contract.redeem(secret=data["secret"], wallet=wallet)
    print(data["secret"])

    redemption.add_fee_and_sign()
    redemption.publish()
    tx_details = redemption.show_details()
    with open("redeemedSwap.json", "w") as write_file:
        json.dump(tx_details, fp=write_file, indent=4, sort_keys=True, default=str)
    #json_tx = json.dumps(tx_details, indent=4, sort_keys=True, default=str)
    #print(json_tx)
    return tx_details

@eel.expose
def finish_swap(sendingCur, receivingCur, privkey, _contract, _transaction_address):
    """
    coin: is the currency that the initial transaction sent.
    privkey: the private key of the local account in the receiving currency 
    _contract: of the started transaction
    _transaction_address: transaction
    """
    #print(f"privkey :{privkey}")
    wallet_network = getNetwork(receivingCur)
    contract_network = getNetwork(sendingCur)

    wallet = wallet_network.get_wallet(private_key=privkey)

    with open('participatedSwap.json') as f:
        data = json.load(f)
    
    contract = audit_tx(receivingCur, _contract, _transaction_address)
    
    try:
        secret = contract_network.extract_secret_from_redeem_transaction(data["contract_address"])
        print(secret)
    except:
        return f"Transaction with address {data['contract_address']} not found. Please retry later."

    closing_tx = contract.redeem(secret=secret, wallet=wallet)
    closing_tx.add_fee_and_sign()
    closing_tx.publish()
    tx_details = closing_tx.show_details()

    return tx_details


@eel.expose
def getStatus(ID):
    '''
    Should take the ID from creatTransaction:
    
    Has to be the last instance of createTransaction called. Ideal this function would pipped inside of createTransaction.
    
    Takes:
    ID - last instance actually used by the user.
    
    Outputs
    Status 
    
    Possible Status (refere to Changelly's developer page @ https://old.changelly.com/developers) 
    waiting	Transaction is waiting for an incoming payment.
    confirming	We have received payin and are waiting for certain amount of confirmations depending of incoming currency.
    exchanging	Payment was confirmed and is being exchanged.
    sending	Coins are being sent to the recipient address.
    finished	Coins were successfully sent to the recipient address.
    failed	Transaction has failed. In most cases, the amount was less than the minimum. Please contact support and provide a transaction id.
    refunded	Exchange failed and coins were refunded to user's wallet. The wallet address should be provided by user.
    overdue	We did not receive any payment since 36 hours from transaction creation.
    hold	Due to AML/KYC procedure, exchange may be delayed
    expired	In case payin was not sent within the indicated timeframe
    '''
    message = {
       "jsonrpc": "2.0",
       "id": "test",
       "method": "getStatus",
       "params": {
          "id": f"{ID}"
       }
    }

    serialized_data = json.dumps(message)

    sign = hmac.new(API_SECRET.encode('utf-8'), serialized_data.encode('utf-8'), hashlib.sha512).hexdigest()

    headers = {'api-key': API_KEY, 'sign': sign, 'Content-type': 'application/json'}
    response_getstatus = requests.post(API_URL, headers=headers, data=serialized_data)

    status = response_getstatus.json()['result']
    
    if '<Response [200]>' == str(response_getstatus) :
        pass
    else:
        raise ValueError("Serve may have crashed or is down for repairs. Please try again later. Please do not transact any funds until you can verify (by re-examining this page) that the server is up and running.")
    
    return status

@eel.expose
def getTransactions(payinaddress, currencyfrom, extraID = 'NULL', limit = 10, offset = 10):
    '''
    Should Take
    Payin Address, str, the address Changelly will use to take in the currency. Can be called from createTransactions 
    CurrencyFrom, str, ticker of the from currency
    ExtraID, if needed, str, address.
    limit, int, how many records to recieve
    offset, int, records cursor
    '''
    message = {
   "jsonrpc": "2.0", #stays the same.
   "id": "test", #does not seem to change things. Unsure of any other parameters that require this.
   "method": "getTransactions", #method
   "params": {
      "currency": f"{currencyfrom}", #what was transfered out, in this case TRX
      "address": f"{payinaddress}", #<<payin address to search>>
      "extraId": f"{extraID}", #for coins that require it
      "limit": limit, #how many records to recieve
      "offset" : offset}}

    serialized_data = json.dumps(message)

    sign = hmac.new(API_SECRET.encode('utf-8'), serialized_data.encode('utf-8'), hashlib.sha512).hexdigest()

    headers = {'api-key': API_KEY, 'sign': sign, 'Content-type': 'application/json'}
    response_gettran = requests.post(API_URL, headers=headers, data=serialized_data)
    
    if '<Response [200]>' == str(response_gettran) :
        pass
    else:
        raise ValueError("Serve may have crashed or is down for repairs. Please try again later. Please do not transact any funds until you can verify (by re-examining this page) that the server is up and running.")
    
    result = response_gettran.json()['result']
    
    return result


@eel.expose
def get_price_dict(mltable):
    '''
    Takes a plot name from the predictionsWindow.html select option dropdown and returns values for the chosen cryptocurrency model. The values are
    current price, previous day price, upper limit of confidence interval, and lower limit of confidence interval.
    
    '''
    
    with open(f'./web/{mltable}') as json_file:
        price_dict = json.load(json_file)
    return price_dict




eel.start('loginWindow.html', size=(1350, 750))
