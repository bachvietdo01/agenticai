def get_share_price(symbol: str) -> float:
    """Returns the current price of a share for testing purposes."""
    prices = {
        "AAPL": 150.00,
        "TSLA": 800.00,
        "GOOGL": 2800.00
    }
    return prices.get(symbol, 0.0)


class Account:
    """Manages a user account for a trading simulation platform."""

    def __init__(self, account_id: str, initial_deposit: float):
        """Initialize a new account.

        Args:
            account_id: Unique identifier for the account
            initial_deposit: Initial amount deposited
        """
        if initial_deposit <= 0:
            raise ValueError("Initial deposit must be positive")
            
        self.account_id = account_id
        self.initial_deposit = initial_deposit
        self.balance = initial_deposit
        self.holdings = {}  # Dictionary to store shares: {symbol: quantity}
        self.transactions = []  # List to store transaction history
        
        # Record the initial deposit as a transaction
        self._record_transaction("DEPOSIT", None, None, initial_deposit)

    def deposit(self, amount: float) -> None:
        """Deposit funds into the account.

        Args:
            amount: Amount to deposit
        """
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
            
        self.balance += amount
        self._record_transaction("DEPOSIT", None, None, amount)

    def withdraw(self, amount: float) -> bool:
        """Withdraw funds from the account if sufficient balance exists.

        Args:
            amount: Amount to withdraw

        Returns:
            True if withdrawal was successful, False otherwise
        """
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
            
        if amount > self.balance:
            return False
            
        self.balance -= amount
        self._record_transaction("WITHDRAW", None, None, amount)
        return True

    def buy_shares(self, symbol: str, quantity: int) -> bool:
        """Buy shares if sufficient funds are available.

        Args:
            symbol: Stock symbol to buy
            quantity: Number of shares to buy

        Returns:
            True if purchase was successful, False otherwise
        """
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
            
        price = get_share_price(symbol)
        if price == 0.0:
            return False  # Invalid symbol
            
        total_cost = price * quantity
        
        if total_cost > self.balance:
            return False  # Insufficient funds
            
        # Update balance
        self.balance -= total_cost
        
        # Update holdings
        if symbol in self.holdings:
            self.holdings[symbol] += quantity
        else:
            self.holdings[symbol] = quantity
            
        # Record transaction
        self._record_transaction("BUY", symbol, quantity, total_cost)
        
        return True

    def sell_shares(self, symbol: str, quantity: int) -> bool:
        """Sell shares if the user has enough shares.

        Args:
            symbol: Stock symbol to sell
            quantity: Number of shares to sell

        Returns:
            True if sale was successful, False otherwise
        """
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
            
        # Check if user has the shares
        if symbol not in self.holdings or self.holdings[symbol] < quantity:
            return False  # Insufficient shares
            
        price = get_share_price(symbol)
        total_value = price * quantity
        
        # Update balance
        self.balance += total_value
        
        # Update holdings
        self.holdings[symbol] -= quantity
        if self.holdings[symbol] == 0:
            del self.holdings[symbol]  # Remove if no shares left
            
        # Record transaction
        self._record_transaction("SELL", symbol, quantity, total_value)
        
        return True

    def total_portfolio_value(self) -> float:
        """Calculate the total value of the portfolio.

        Returns:
            Total value of cash and shares
        """
        total_value = self.balance
        
        # Add the value of all share holdings
        for symbol, quantity in self.holdings.items():
            price = get_share_price(symbol)
            total_value += price * quantity
            
        return total_value

    def profit_or_loss(self) -> float:
        """Calculate the profit or loss from the initial deposit.

        Returns:
            Profit (positive) or loss (negative) amount
        """
        return self.total_portfolio_value() - self.initial_deposit

    def holdings_report(self) -> dict:
        """Get a report of current share holdings.

        Returns:
            Dictionary of holdings with symbol as key and quantity as value
        """
        return self.holdings.copy()

    def transaction_history(self) -> list:
        """Get the transaction history.

        Returns:
            List of all transactions
        """
        return self.transactions.copy()
    
    def _record_transaction(self, transaction_type: str, symbol: str, quantity: int, amount: float) -> None:
        """Record a transaction in the transaction history.

        Args:
            transaction_type: Type of transaction (DEPOSIT, WITHDRAW, BUY, SELL)
            symbol: Stock symbol involved (None for deposits/withdrawals)
            quantity: Number of shares involved (None for deposits/withdrawals)
            amount: Amount of money involved
        """
        transaction = {
            "type": transaction_type,
            "symbol": symbol,
            "quantity": quantity,
            "amount": amount,
        }
        self.transactions.append(transaction)