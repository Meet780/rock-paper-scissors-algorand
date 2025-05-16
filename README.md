# Blockchain-Based Rock-Paper-Scissors Game on Algorand

This project implements a Rock-Paper-Scissors game using a commitment-reveal scheme with Algorand smart contracts written in PyTeal.

## Features

- Two players commit hashed moves
- Reveal moves with nonce to prove commitment
- Smart contract decides the winner on-chain
- Reset game for new rounds

## Project Structure

- `rock_paper_scissors.py` - PyTeal smart contract code  
- `deploy.py` - Compile and deploy the contract to Algorand TestNet  
- `client.py` - Client script for interacting with the smart contract  

## Prerequisites

- Python 3.7+  
- Algorand SDK for Python  
- PyTeal  
- Algorand TestNet account with ALGOs  
- PureStake API key (for TestNet access)

## 📄 License

MIT License. Use freely for learning and development.
