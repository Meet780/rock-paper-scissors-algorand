from algosdk.v2client import algod
from algosdk.future.transaction import ApplicationNoOpTxn
from algosdk import mnemonic, account, transaction
import sys

algod_address = "https://testnet-algorand.api.purestake.io/ps2"
algod_token = "Your PureStake API Key"
headers = {
    "X-API-Key": algod_token,
}

algod_client = algod.AlgodClient(algod_token, algod_address, headers)

def get_private_key_from_mnemonic(mn):
    return mnemonic.to_private_key(mn)

def call_app(client, private_key, app_id, app_args, accounts=[]):
    sender = account.address_from_private_key(private_key)
    params = client.suggested_params()
    txn = ApplicationNoOpTxn(sender, params, app_id, app_args, accounts=accounts)
    signed_txn = txn.sign(private_key)
    txid = client.send_transaction(signed_txn)
    transaction.wait_for_confirmation(client, txid, 4)
    return txid

def main():
    if len(sys.argv) < 4:
        print("Usage:")
        print("python client.py <mnemonic> <app_id> <action> [args...]")
        print("Actions: commit_init <p1_addr> <p2_addr>")
        print("         p1_commit <commit_hash>")
        print("         p2_commit <commit_hash>")
        print("         reveal <move> <nonce>")
        print("         decide")
        print("         reset")
        sys.exit(1)

    mn = sys.argv[1]
    app_id = int(sys.argv[2])
    action = sys.argv[3]

    private_key = get_private_key_from_mnemonic(mn)

    if action == "commit_init":
        p1_addr = sys.argv[4]
        p2_addr = sys.argv[5]
        app_args = [action.encode(), bytes(p1_addr, 'utf-8'), bytes(p2_addr, 'utf-8')]
        accounts = [p1_addr, p2_addr]
        call_app(algod_client, private_key, app_id, app_args, accounts)
    elif action == "p1_commit":
        commit_hash = sys.argv[4]
        app_args = [action.encode(), bytes.fromhex(commit_hash)]
        call_app(algod_client, private_key, app_id, app_args)
    elif action == "p2_commit":
        commit_hash = sys.argv[4]
        app_args = [action.encode(), bytes.fromhex(commit_hash)]
        call_app(algod_client, private_key, app_id, app_args)
    elif action == "reveal":
        move = sys.argv[4]
        nonce = sys.argv[5]
        app_args = [action.encode(), move.encode(), nonce.encode()]
        call_app(algod_client, private_key, app_id, app_args)
    elif action == "decide":
        app_args = [action.encode()]
        call_app(algod_client, private_key, app_id, app_args)
    elif action == "reset":
        app_args = [action.encode()]
        call_app(algod_client, private_key, app_id, app_args)
    else:
        print("Unknown action")

if __name__ == "__main__":
    main()
