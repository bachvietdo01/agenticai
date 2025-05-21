import gradio as gr
import json
from accounts import Account, get_share_price

# Initialize a global account variable
account = None

def create_account(account_id, initial_deposit):
    """Create a new account with the given ID and initial deposit."""
    global account
    try:
        initial_deposit = float(initial_deposit)
        account = Account(account_id, initial_deposit)
        return f"Account created with ID: {account_id} and initial deposit: ${initial_deposit:.2f}"
    except ValueError as e:
        return f"Error: {str(e)}"

def deposit_funds(amount):
    """Deposit funds into the account."""
    global account
    if account is None:
        return "Error: No account created yet."
    
    try:
        amount = float(amount)
        account.deposit(amount)
        return f"Successfully deposited ${amount:.2f}. New balance: ${account.balance:.2f}"
    except ValueError as e:
        return f"Error: {str(e)}"

def withdraw_funds(amount):
    """Withdraw funds from the account."""
    global account
    if account is None:
        return "Error: No account created yet."
    
    try:
        amount = float(amount)
        if account.withdraw(amount):
            return f"Successfully withdrew ${amount:.2f}. New balance: ${account.balance:.2f}"
        else:
            return f"Error: Insufficient funds. Current balance: ${account.balance:.2f}"
    except ValueError as e:
        return f"Error: {str(e)}"

def buy_shares(symbol, quantity):
    """Buy shares of the specified stock."""
    global account
    if account is None:
        return "Error: No account created yet."
    
    try:
        quantity = int(quantity)
        price = get_share_price(symbol)
        
        if price == 0.0:
            return f"Error: Invalid stock symbol '{symbol}'"
        
        if account.buy_shares(symbol, quantity):
            return f"Successfully bought {quantity} shares of {symbol} at ${price:.2f} per share. Total cost: ${price * quantity:.2f}. New balance: ${account.balance:.2f}"
        else:
            return f"Error: Insufficient funds to buy {quantity} shares of {symbol} at ${price:.2f} per share (total: ${price * quantity:.2f}). Current balance: ${account.balance:.2f}"
    except ValueError as e:
        return f"Error: {str(e)}"

def sell_shares(symbol, quantity):
    """Sell shares of the specified stock."""
    global account
    if account is None:
        return "Error: No account created yet."
    
    try:
        quantity = int(quantity)
        price = get_share_price(symbol)
        
        if account.sell_shares(symbol, quantity):
            return f"Successfully sold {quantity} shares of {symbol} at ${price:.2f} per share. Total value: ${price * quantity:.2f}. New balance: ${account.balance:.2f}"
        else:
            holdings = account.holdings_report()
            current_quantity = holdings.get(symbol, 0)
            return f"Error: Insufficient shares to sell. You have {current_quantity} shares of {symbol}."
    except ValueError as e:
        return f"Error: {str(e)}"

def get_portfolio_value():
    """Get the total value of the portfolio."""
    global account
    if account is None:
        return "Error: No account created yet."
    
    total_value = account.total_portfolio_value()
    profit_loss = account.profit_or_loss()
    
    result = f"Total Portfolio Value: ${total_value:.2f}\n"
    result += f"Profit/Loss: ${profit_loss:.2f} "
    
    if profit_loss > 0:
        result += "(Profit)"
    elif profit_loss < 0:
        result += "(Loss)"
    else:
        result += "(Breakeven)"
    
    return result

def get_holdings():
    """Get the current share holdings."""
    global account
    if account is None:
        return "Error: No account created yet."
    
    holdings = account.holdings_report()
    
    if not holdings:
        return "No shares held currently."
    
    result = "Current Holdings:\n"
    total_value = 0.0
    
    for symbol, quantity in holdings.items():
        price = get_share_price(symbol)
        value = price * quantity
        total_value += value
        result += f"{symbol}: {quantity} shares at ${price:.2f} per share = ${value:.2f}\n"
    
    result += f"\nTotal value of shares: ${total_value:.2f}"
    result += f"\nCash balance: ${account.balance:.2f}"
    result += f"\nTotal portfolio value: ${account.total_portfolio_value():.2f}"
    
    return result

def get_transactions():
    """Get the transaction history."""
    global account
    if account is None:
        return "Error: No account created yet."
    
    transactions = account.transaction_history()
    
    if not transactions:
        return "No transactions recorded."
    
    result = "Transaction History:\n\n"
    
    for i, transaction in enumerate(transactions, 1):
        result += f"Transaction {i}:\n"
        result += f"Type: {transaction['type']}\n"
        
        if transaction['type'] in ["BUY", "SELL"]:
            result += f"Symbol: {transaction['symbol']}\n"
            result += f"Quantity: {transaction['quantity']}\n"
            price = transaction['amount'] / transaction['quantity']
            result += f"Price per share: ${price:.2f}\n"
        
        result += f"Amount: ${transaction['amount']:.2f}\n\n"
    
    return result

def get_stock_price(symbol):
    """Get the current price of a stock."""
    price = get_share_price(symbol)
    
    if price == 0.0:
        return f"Error: Invalid stock symbol '{symbol}'"
    
    return f"Current price of {symbol}: ${price:.2f}"

def get_account_status():
    """Get the current status of the account."""
    global account
    if account is None:
        return "No account has been created yet."
    
    result = f"Account ID: {account.account_id}\n"
    result += f"Initial Deposit: ${account.initial_deposit:.2f}\n"
    result += f"Current Cash Balance: ${account.balance:.2f}\n"
    result += f"Total Portfolio Value: ${account.total_portfolio_value():.2f}\n"
    
    profit_loss = account.profit_or_loss()
    result += f"Profit/Loss: ${profit_loss:.2f} "
    
    if profit_loss > 0:
        result += "(Profit)"
    elif profit_loss < 0:
        result += "(Loss)"
    else:
        result += "(Breakeven)"
    
    return result

# Create the Gradio interface
with gr.Blocks(title="Trading Simulation Platform") as demo:
    gr.Markdown("# Trading Simulation Platform")
    
    with gr.Tab("Account Management"):
        gr.Markdown("## Create Account")
        with gr.Row():
            account_id_input = gr.Textbox(label="Account ID")
            initial_deposit_input = gr.Textbox(label="Initial Deposit ($)")
        create_account_btn = gr.Button("Create Account")
        create_account_output = gr.Textbox(label="Result")
        
        create_account_btn.click(
            fn=create_account,
            inputs=[account_id_input, initial_deposit_input],
            outputs=create_account_output
        )
        
        gr.Markdown("## Deposit Funds")
        deposit_amount_input = gr.Textbox(label="Deposit Amount ($)")
        deposit_btn = gr.Button("Deposit")
        deposit_output = gr.Textbox(label="Result")
        
        deposit_btn.click(
            fn=deposit_funds,
            inputs=[deposit_amount_input],
            outputs=deposit_output
        )
        
        gr.Markdown("## Withdraw Funds")
        withdraw_amount_input = gr.Textbox(label="Withdraw Amount ($)")
        withdraw_btn = gr.Button("Withdraw")
        withdraw_output = gr.Textbox(label="Result")
        
        withdraw_btn.click(
            fn=withdraw_funds,
            inputs=[withdraw_amount_input],
            outputs=withdraw_output
        )
    
    with gr.Tab("Trading"):
        gr.Markdown("## Check Stock Price")
        price_symbol_input = gr.Textbox(label="Stock Symbol (e.g., AAPL, TSLA, GOOGL)")
        get_price_btn = gr.Button("Get Price")
        price_output = gr.Textbox(label="Result")
        
        get_price_btn.click(
            fn=get_stock_price,
            inputs=[price_symbol_input],
            outputs=price_output
        )
        
        gr.Markdown("## Buy Shares")
        with gr.Row():
            buy_symbol_input = gr.Textbox(label="Stock Symbol")
            buy_quantity_input = gr.Textbox(label="Quantity")
        buy_btn = gr.Button("Buy Shares")
        buy_output = gr.Textbox(label="Result")
        
        buy_btn.click(
            fn=buy_shares,
            inputs=[buy_symbol_input, buy_quantity_input],
            outputs=buy_output
        )
        
        gr.Markdown("## Sell Shares")
        with gr.Row():
            sell_symbol_input = gr.Textbox(label="Stock Symbol")
            sell_quantity_input = gr.Textbox(label="Quantity")
        sell_btn = gr.Button("Sell Shares")
        sell_output = gr.Textbox(label="Result")
        
        sell_btn.click(
            fn=sell_shares,
            inputs=[sell_symbol_input, sell_quantity_input],
            outputs=sell_output
        )
    
    with gr.Tab("Portfolio"):
        gr.Markdown("## Account Status")
        status_btn = gr.Button("Get Account Status")
        status_output = gr.Textbox(label="Account Status", lines=6)
        
        status_btn.click(
            fn=get_account_status,
            inputs=[],
            outputs=status_output
        )
        
        gr.Markdown("## Portfolio Value")
        portfolio_btn = gr.Button("Get Portfolio Value")
        portfolio_output = gr.Textbox(label="Portfolio Value", lines=3)
        
        portfolio_btn.click(
            fn=get_portfolio_value,
            inputs=[],
            outputs=portfolio_output
        )
        
        gr.Markdown("## Current Holdings")
        holdings_btn = gr.Button("Get Holdings")
        holdings_output = gr.Textbox(label="Holdings", lines=10)
        
        holdings_btn.click(
            fn=get_holdings,
            inputs=[],
            outputs=holdings_output
        )
    
    with gr.Tab("Transaction History"):
        gr.Markdown("## Transaction History")
        transactions_btn = gr.Button("Get Transaction History")
        transactions_output = gr.Textbox(label="Transactions", lines=15)
        
        transactions_btn.click(
            fn=get_transactions,
            inputs=[],
            outputs=transactions_output
        )

if __name__ == "__main__":
    demo.launch()