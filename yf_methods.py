import yfinance
import pandas as pd


class YFTickerInstance:
    def __init__(self, ticker_id):
        self.ticker_id = ticker_id
        self.yft = yfinance.Ticker(ticker_id + ".NS")

    def get_ticker_info(self):
        return self.yft.info

    def get_market_data(self, days):
        return self.yft.history(period=f"{days}d")

    def get_cmp(self):
        return self.yft.history(period="1d")

    def get_income_stmt_yearly(self):
        return self.yft.income_stmt

    def get_income_stmt_quarterly(self):
        return self.yft.quarterly_income_stmt

    def get_balance_sheet_yearly(self):
        return self.yft.balance_sheet

    def get_balance_sheet_quarterly(self):
        return self.yft.quarterly_balance_sheet

    def get_cashflow_yearly(self):
        return self.yft.cash_flow

    def get_cashflow_quarterly(self):
        return self.yft.quarterly_cashflow

    def get_major_holders(self):
        return pd.DataFrame(self.yft.major_holders)

    def get_news(self):
        return self.yft.news
