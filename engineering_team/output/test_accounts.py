import unittest
from unittest.mock import patch

# Import the Account class and get_share_price function from the accounts module
from accounts import Account, get_share_price


class TestGetSharePrice(unittest.TestCase):
    """Test cases for get_share_price function."""
    
    def test_get_existing_share_price(self):
        """Test getting price for existing symbols."""
        self.assertEqual(get_share_price("AAPL"), 150.00)
        self.assertEqual(get_share_price("TSLA"), 800.00)
        self.assertEqual(get_share_price("GOOGL"), 2800.00)
    
    def test_get_nonexistent_share_price(self):
        """Test getting price for non-existent symbol."""
        self.assertEqual(get_share_price("NONEXISTENT"), 0.0)


class TestAccountInitialization(unittest.TestCase):
    """Test cases for Account initialization."""
    
    def test_valid_initialization(self):
        """Test initializing with valid parameters."""
        account = Account("ACC123", 1000.0)
        self.assertEqual(account.account_id, "ACC123")
        self.assertEqual(account.initial_deposit, 1000.0)
        self.assertEqual(account.balance, 1000.0)
        self.assertEqual(account.holdings, {})
        self.assertEqual(len(account.transactions), 1)
        self.assertEqual(account.transactions[0]["type"], "DEPOSIT")
        self.assertEqual(account.transactions[0]["amount"], 1000.0)
    
    def test_invalid_initialization(self):
        """Test initializing with invalid parameters."""
        with self.assertRaises(ValueError):
            Account("ACC123", 0.0)
        with self.assertRaises(ValueError):
            Account("ACC123", -100.0)


class TestAccountDeposit(unittest.TestCase):
    """Test cases for deposit method."""
    
    def setUp(self):
        """Set up a test account."""
        self.account = Account("ACC123", 1000.0)
    
    def test_valid_deposit(self):
        """Test valid deposit."""
        self.account.deposit(500.0)
        self.assertEqual(self.account.balance, 1500.0)
        self.assertEqual(len(self.account.transactions), 2)
        self.assertEqual(self.account.transactions[1]["type"], "DEPOSIT")
        self.assertEqual(self.account.transactions[1]["amount"], 500.0)
    
    def test_invalid_deposit(self):
        """Test invalid deposit."""
        with self.assertRaises(ValueError):
            self.account.deposit(0.0)
        with self.assertRaises(ValueError):
            self.account.deposit(-100.0)
        # Balance should remain unchanged
        self.assertEqual(self.account.balance, 1000.0)


class TestAccountWithdraw(unittest.TestCase):
    """Test cases for withdraw method."""
    
    def setUp(self):
        """Set up a test account."""
        self.account = Account("ACC123", 1000.0)
    
    def test_valid_withdraw(self):
        """Test valid withdrawal."""
        result = self.account.withdraw(500.0)
        self.assertTrue(result)
        self.assertEqual(self.account.balance, 500.0)
        self.assertEqual(len(self.account.transactions), 2)
        self.assertEqual(self.account.transactions[1]["type"], "WITHDRAW")
        self.assertEqual(self.account.transactions[1]["amount"], 500.0)
    
    def test_withdraw_exact_balance(self):
        """Test withdrawing the exact balance."""
        result = self.account.withdraw(1000.0)
        self.assertTrue(result)
        self.assertEqual(self.account.balance, 0.0)
    
    def test_withdraw_insufficient_funds(self):
        """Test withdrawing more than the balance."""
        result = self.account.withdraw(1500.0)
        self.assertFalse(result)
        # Balance should remain unchanged
        self.assertEqual(self.account.balance, 1000.0)
        # No transaction should be recorded
        self.assertEqual(len(self.account.transactions), 1)
    
    def test_invalid_withdraw(self):
        """Test invalid withdrawal."""
        with self.assertRaises(ValueError):
            self.account.withdraw(0.0)
        with self.assertRaises(ValueError):
            self.account.withdraw(-100.0)
        # Balance should remain unchanged
        self.assertEqual(self.account.balance, 1000.0)


class TestAccountBuyShares(unittest.TestCase):
    """Test cases for buy_shares method."""
    
    def setUp(self):
        """Set up a test account."""
        self.account = Account("ACC123", 10000.0)
    
    def test_buy_valid_shares(self):
        """Test buying valid shares."""
        result = self.account.buy_shares("AAPL", 10)
        self.assertTrue(result)
        self.assertEqual(self.account.balance, 8500.0)  # 10000 - (150 * 10)
        self.assertEqual(self.account.holdings["AAPL"], 10)
        self.assertEqual(len(self.account.transactions), 2)
        self.assertEqual(self.account.transactions[1]["type"], "BUY")
        self.assertEqual(self.account.transactions[1]["symbol"], "AAPL")
        self.assertEqual(self.account.transactions[1]["quantity"], 10)
        self.assertEqual(self.account.transactions[1]["amount"], 1500.0)
    
    def test_buy_additional_shares(self):
        """Test buying additional shares of an existing holding."""
        self.account.buy_shares("AAPL", 10)
        result = self.account.buy_shares("AAPL", 5)
        self.assertTrue(result)
        self.assertEqual(self.account.balance, 7750.0)  # 10000 - (150 * 10) - (150 * 5)
        self.assertEqual(self.account.holdings["AAPL"], 15)
    
    def test_buy_multiple_symbols(self):
        """Test buying shares of multiple symbols."""
        self.account.buy_shares("AAPL", 10)
        result = self.account.buy_shares("TSLA", 5)
        self.assertTrue(result)
        self.assertEqual(self.account.balance, 4500.0)  # 10000 - (150 * 10) - (800 * 5)
        self.assertEqual(self.account.holdings["AAPL"], 10)
        self.assertEqual(self.account.holdings["TSLA"], 5)
    
    def test_buy_invalid_symbol(self):
        """Test buying shares with an invalid symbol."""
        result = self.account.buy_shares("INVALID", 10)
        self.assertFalse(result)
        # Balance should remain unchanged
        self.assertEqual(self.account.balance, 10000.0)
        # No holding should be created
        self.assertEqual(self.account.holdings, {})
        # No transaction should be recorded
        self.assertEqual(len(self.account.transactions), 1)
    
    def test_buy_insufficient_funds(self):
        """Test buying shares with insufficient funds."""
        result = self.account.buy_shares("TSLA", 20)  # 800 * 20 = 16000 > 10000
        self.assertFalse(result)
        # Balance should remain unchanged
        self.assertEqual(self.account.balance, 10000.0)
        # No holding should be created
        self.assertEqual(self.account.holdings, {})
        # No transaction should be recorded
        self.assertEqual(len(self.account.transactions), 1)
    
    def test_buy_invalid_quantity(self):
        """Test buying with invalid quantity."""
        with self.assertRaises(ValueError):
            self.account.buy_shares("AAPL", 0)
        with self.assertRaises(ValueError):
            self.account.buy_shares("AAPL", -5)
        # Balance should remain unchanged
        self.assertEqual(self.account.balance, 10000.0)
        # No holding should be created
        self.assertEqual(self.account.holdings, {})


class TestAccountSellShares(unittest.TestCase):
    """Test cases for sell_shares method."""
    
    def setUp(self):
        """Set up a test account with some shares."""
        self.account = Account("ACC123", 10000.0)
        self.account.buy_shares("AAPL", 20)  # 10000 - (150 * 20) = 7000
        self.account.buy_shares("TSLA", 5)   # 7000 - (800 * 5) = 3000
    
    def test_sell_partial_shares(self):
        """Test selling a portion of shares."""
        result = self.account.sell_shares("AAPL", 10)
        self.assertTrue(result)
        self.assertEqual(self.account.balance, 4500.0)  # 3000 + (150 * 10)
        self.assertEqual(self.account.holdings["AAPL"], 10)
        self.assertEqual(len(self.account.transactions), 4)  # Initial deposit + 2 buys + 1 sell
        self.assertEqual(self.account.transactions[3]["type"], "SELL")
        self.assertEqual(self.account.transactions[3]["symbol"], "AAPL")
        self.assertEqual(self.account.transactions[3]["quantity"], 10)
        self.assertEqual(self.account.transactions[3]["amount"], 1500.0)
    
    def test_sell_all_shares(self):
        """Test selling all shares of a symbol."""
        result = self.account.sell_shares("AAPL", 20)
        self.assertTrue(result)
        self.assertEqual(self.account.balance, 6000.0)  # 3000 + (150 * 20)
        self.assertNotIn("AAPL", self.account.holdings)
    
    def test_sell_insufficient_shares(self):
        """Test selling more shares than owned."""
        result = self.account.sell_shares("AAPL", 30)
        self.assertFalse(result)
        # Balance and holdings should remain unchanged
        self.assertEqual(self.account.balance, 3000.0)
        self.assertEqual(self.account.holdings["AAPL"], 20)
        # No transaction should be recorded
        self.assertEqual(len(self.account.transactions), 3)  # Initial deposit + 2 buys
    
    def test_sell_nonexistent_symbol(self):
        """Test selling shares of a symbol not owned."""
        result = self.account.sell_shares("GOOGL", 5)
        self.assertFalse(result)
        # Balance should remain unchanged
        self.assertEqual(self.account.balance, 3000.0)
        # No transaction should be recorded
        self.assertEqual(len(self.account.transactions), 3)  # Initial deposit + 2 buys
    
    def test_sell_invalid_quantity(self):
        """Test selling with invalid quantity."""
        with self.assertRaises(ValueError):
            self.account.sell_shares("AAPL", 0)
        with self.assertRaises(ValueError):
            self.account.sell_shares("AAPL", -5)
        # Balance and holdings should remain unchanged
        self.assertEqual(self.account.balance, 3000.0)
        self.assertEqual(self.account.holdings["AAPL"], 20)


class TestAccountPortfolioValue(unittest.TestCase):
    """Test cases for total_portfolio_value method."""
    
    def setUp(self):
        """Set up a test account with some shares."""
        self.account = Account("ACC123", 10000.0)
        self.account.buy_shares("AAPL", 20)  # 10000 - (150 * 20) = 7000
        self.account.buy_shares("TSLA", 5)   # 7000 - (800 * 5) = 3000
    
    def test_portfolio_value(self):
        """Test calculating the total portfolio value."""
        # Cash: 3000
        # AAPL: 20 * 150 = 3000
        # TSLA: 5 * 800 = 4000
        # Total: 10000
        expected_value = 3000.0 + (20 * 150.0) + (5 * 800.0)
        self.assertEqual(self.account.total_portfolio_value(), expected_value)
    
    def test_portfolio_value_after_transactions(self):
        """Test portfolio value after additional transactions."""
        self.account.sell_shares("AAPL", 10)  # 3000 + (150 * 10) = 4500
        # Cash: 4500
        # AAPL: 10 * 150 = 1500
        # TSLA: 5 * 800 = 4000
        # Total: 10000
        expected_value = 4500.0 + (10 * 150.0) + (5 * 800.0)
        self.assertEqual(self.account.total_portfolio_value(), expected_value)


class TestAccountProfitLoss(unittest.TestCase):
    """Test cases for profit_or_loss method."""
    
    def setUp(self):
        """Set up a test account."""
        self.account = Account("ACC123", 10000.0)
    
    def test_initial_profit_loss(self):
        """Test profit/loss immediately after initialization."""
        self.assertEqual(self.account.profit_or_loss(), 0.0)
    
    def test_profit_scenario(self):
        """Test a scenario with profit."""
        # Buy shares and then assume they increased in value
        self.account.buy_shares("AAPL", 100)  # 10000 - (150 * 100) = -5000
        
        # Mock a higher price when getting portfolio value
        with patch("accounts.get_share_price", return_value=200.0):
            # Initial deposit: 10000
            # Current value: 5000 (cash) + (100 * 200) = 25000
            # Profit: 25000 - 10000 = 15000
            self.assertEqual(self.account.profit_or_loss(), 15000.0)
    
    def test_loss_scenario(self):
        """Test a scenario with loss."""
        # Buy shares and then assume they decreased in value
        self.account.buy_shares("AAPL", 100)  # 10000 - (150 * 100) = -5000
        
        # Mock a lower price when getting portfolio value
        with patch("accounts.get_share_price", return_value=100.0):
            # Initial deposit: 10000
            # Current value: 5000 (cash) + (100 * 100) = 15000
            # Profit: 15000 - 10000 = 5000
            self.assertEqual(self.account.profit_or_loss(), 5000.0)


class TestAccountHoldingsReport(unittest.TestCase):
    """Test cases for holdings_report method."""
    
    def setUp(self):
        """Set up a test account with some shares."""
        self.account = Account("ACC123", 10000.0)
        self.account.buy_shares("AAPL", 20)
        self.account.buy_shares("TSLA", 5)
    
    def test_holdings_report(self):
        """Test getting the holdings report."""
        expected_report = {"AAPL": 20, "TSLA": 5}
        self.assertEqual(self.account.holdings_report(), expected_report)
    
    def test_holdings_report_after_selling(self