from web3 import Web3
import json

class BlockchainTools:
    NETWORKS = {
        "ethereum": "https://mainnet.infura.io/v3/YOUR_PROJECT_ID",
        "polygon": "https://polygon-mainnet.infura.io/v3/YOUR_PROJECT_ID",
        "test": "http://localhost:8545"
    }
    
    def __init__(self, network="test"):
        self.w3 = Web3(Web3.HTTPProvider(self.NETWORKS[network]))
    
    def compile_solidity(self, contract_path):
        # Requires solc installed
        cmd = f"solc --combined-json abi,bin {contract_path}"
        result = subprocess.run(cmd, shell=True, capture_output=True)
        return json.loads(result.stdout)
    
    def deploy_contract(self, abi, bytecode, private_key):
        contract = self.w3.eth.contract(abi=abi, bytecode=bytecode)
        account = self.w3.eth.account.from_key(private_key)
        tx = contract.constructor().build_transaction({
            'from': account.address,
            'nonce': self.w3.eth.get_transaction_count(account.address),
            'gas': 1728712,
            'gasPrice': self.w3.to_wei('21', 'gwei')
        })
        signed_tx = account.sign_transaction(tx)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        return self.w3.eth.wait_for_transaction_receipt(tx_hash)
    
    def generate_dapp_scaffold(self, framework="react"):
        return {
            "react": "npx create-react-app my-dapp",
            "vue": "npm init vue@latest",
            "svelte": "npm create svelte@latest my-dapp"
        }.get(framework, "")