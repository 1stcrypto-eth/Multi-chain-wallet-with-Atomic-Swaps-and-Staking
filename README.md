# Multi_Chain_GUI_Wallet
### Multi-Chain GUI Wallet with Atomic Swaps and Staking

To start the wallet during development enter
`python wallet.py`

Check the requirements.txt for dependencies 

## Description

This crypto wallet is not just another crypto wallet. Even though it can carry out the same functionality of most wallets out there, this wallet has also the power to carry out real P2P atomic transactions, exchange between cryptocurrencies through atomic transaction in a market, and it also has a section that predicts price for the cryptocurrecnies listed in the wallet through Machine Learning algorithms.

This wallet is Bip32, Bip44, and Bip39 compliant. Therefore, to start using the wallet, you will have to create a mnemonic seed. Remember not to share this with anyone else since this will give them total access to your funds in this wallet.

![Wallet Creation][mnemonic]

[mnemonic]: images/mnemonic.png

You can create as many mnemonic as you want and store them with different passwords. However, if you forget your password, the mnemonic seed attached to that password will be lost for ever since there is no password recovery method. 

The **security approach** to this wallet is to store password and mnemonic locally in the user's machine. There is no server storing menomics seeds for anybody since this is a major security hole. In this way, each mnenomic is locally encrypted with the user's password. 

If you have already created your wallet, simply enter your password to retreive your wallet.

![Log in][login]

[login]: images/login.png

Once you are logged in, you have access to your different cryptocurrency wallets all at once. The middel section will give you the main information about your balances and the cryptocurrency price for all of our supported coins.

![Main Wallet][mainwallet]

[mainwallet]: images/mainwallet.png

 The section in the right will be your actual wallet where you have your address, your QR code for your address, your balance, and the option to send money out from your wallet.

![Wallet][sned]

[sned]: images/sned.png

In the left section we have different options for our atomic swaps and the predictions.

For P2P atomic swaps you will need to find someone who is willing to exchange their coins for the same value you wish the make the transaction. This will have a very low cost in transactions since only miners will take a cut in it.

![Start a new swap][start_swap]

[start_swap]: images/start_swap.png

![Participate in a swap][participate]

[participate]: images/participate.png

However it is also difficult to find somebody willing to exchange the same currencies your trying to exchange for the same value. This is where the "Exchange" secion comes into play. To exchange in a pool of atomic swaps go to the "Exchange" section. This opperation has a higher cost than P2P atomic swaps since there is a fee paid to intermediaries. This section is powered by our partner Changelly.

![Exchange][exchange]

[exchange]: images/exchange.png

Cryptocurrencies have created large and fast fortunes for traders. This is why we dedicated a whole section to predict future prices for our cryptocurrencies. To get this predictions simply go to the "Predictions" section.


![Predictions][predictions]

[predictions]: images/predictions.png

Here, you will have the option to choose between different Machine Learning models and different currencies.
