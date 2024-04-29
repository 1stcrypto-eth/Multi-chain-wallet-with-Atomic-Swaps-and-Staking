import subprocess
import sys

def install(package):
    print(f"Installing {package} ...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    
packages = ["py_hd_wallet", "eel", "qrcode", "clove", "web3", "python-dotenv", "bit", "plotly", "scikit-garden", "scrypt", "cryptos", "multicrypto"]


def install_hdderive():
    print("Installing HD Derive")
    url = "https://github.com/dan-da/hd-wallet-derive"
    subprocess.check_call([sys.executable, "-m", "cd", "hd-wallet-derive"])
    subprocess.check_call([sys.executable, "-m", "php", "-r", "readfile('https://getcomposer.org/installer')";])
    subprocess.check_call([sys.executable, "-m", "export", "PATH=/usr/local/opt/php@7.3/bin:$PATH"])
    subprocess.check_call([sys.executable, "-m", "echo", '"export PATH=/usr/local/opt/php@7.3/bin:$PATH"', ">>", "~/.bash_profile"])
    subprocess.check_call([sys.executable, "-m", "php", "composer.phar", install])


for package in packages:
    try: 
        install(package)
    except:
        pass

print(f"Finished Installing {len(packages)} Packages")

install_hdderive()

print(f"Finished Installing HD Derive")