from algosdk.v2client import algod
from algosdk import account, transaction
from algosdk.future.transaction import StateSchema, ApplicationCreateTxn
from algosdk import mnemonic
from pyteal import compileTeal, Mode
import rock_paper_scissors

algod_address = "https://testnet-algorand.api.purestake.io/ps2"
algod_token = "Your PureStake API Key"
headers = {
    "X-API-Key": algod_token,
}

algod_client = algod.AlgodClient(algod_token, algod_address, headers)

creator_mnemonic = "your 25-word mnemonic here"
creator_private_key = mnemonic.to_private_key(creator_mnemonic)
creator_address = account.address_from_private_key(creator_private_key)

approval_program_teal = compileTeal(rock_paper_scissors.approval_program(), mode=Mode.Application, version=5)
clear_program_teal = compileTeal(rock_paper_scissors.clear_state_program(), mode=Mode.Application, version=5)

def compile_program(client, source_code):
    compile_response = client.compile(source_code)
    return bytes.fromhex(compile_response['result'])

def create_app():
    approval_program_compiled = compile_program(algod_client, approval_program_teal)
    clear_program_compiled = compile_program(algod_client, clear_program_teal)

    global_schema = StateSchema(num_uints=4, num_byte_slices=6)
    local_schema = StateSchema(num_uints=0, num_byte_slices=0)

    params = algod_client.suggested_params()

    txn = ApplicationCreateTxn(
        sender=creator_address,
        sp=params,
        on_complete=transaction.OnComplete.NoOpOC.real,
        approval_program=approval_program_compiled,
        clear_program=clear_program_compiled,
        global_schema=global_schema,
        local_schema=local_schema,
    )

    signed_txn = txn.sign(creator_private_key)
    txid = algod_client.send_transaction(signed_txn)

    confirmed_txn = transaction.wait_for_confirmation(algod_client, txid, 4)

    app_id = confirmed_txn['application-index']
    print("Created app-id:", app_id)
    return app_id

if __name__ == "__main__":
    create_app()
