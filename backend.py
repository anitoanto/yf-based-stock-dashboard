import pandas as pd
from pprint import pprint
from bs4 import BeautifulSoup
from yf_methods import YFTickerInstance


def web_scrap_yf(ticker_id):
    import subprocess
    import sys

    URL = f'"https://finance.yahoo.com/quote/{ticker_id}.NS/key-statistics"'

    with open("./__command.ps1", "w") as f:
        f.write(f"wget {URL} -o __{ticker_id}.html")

    p = subprocess.Popen(["powershell.exe", ".\__command.ps1"], stdout=sys.stdout)
    (output, err) = p.communicate()
    p_status = p.wait()
    if p_status == 0:
        pprint("[STATUS] Web scraping: DONE")


class WSResult:
    def __init__(self, ticker_id):
        with open(f"./__{ticker_id}.html", "r", encoding="utf-8") as file:
            self.html_content = file.read()
        self.soup = BeautifulSoup(self.html_content, "html.parser")
        self.title = self.soup.find("title").string
        self.kv_pairs = []

        tables = self.soup.find_all("table")

        for table in tables:
            rows = table.find_all("tr")
            for row in rows:
                cells = row.find_all(["th", "td"])
                row_data = [cell.get_text(strip=True) for cell in cells]
                if len(row_data) == 2:
                    self.kv_pairs.append(row_data)

        self.kv_pairs = pd.DataFrame(columns=["Key", "Value"], data=self.kv_pairs)

    def get_available_kv(self):
        return self.kv_pairs

    def get_kv(self, key):
        return self.kv_pairs[self.kv_pairs["Key"] == key].values[0][1]

    def get_title(self):
        return self.title.split("(")[0]


def load_metrics(ticker):
    yft = YFTickerInstance(ticker)

    web_scrap_yf(ticker)
    results = WSResult(ticker)

    df = yft.get_cmp()
    change_percent = (
        (df.iloc[0]["Close"] - df.iloc[0]["Open"]) / df.iloc[0]["Open"]
    ) * 100

    pe = results.get_kv("Trailing P/E")
    bvps = float(results.get_kv("Book Value Per Share(mrq)").replace(",", ""))
    margin_of_safety_BVPS = 1 - (df.iloc[0]["Close"] / bvps)

    cf = yft.get_cashflow_yearly()
    mean_fcf = cf.loc["Free Cash Flow"].values.mean()

    metrics = {
        "Name": results.get_title(),
        "Symbol": ticker,
        "BVPS": bvps,
        "Margin of safety (BVPS)": margin_of_safety_BVPS,
        "P/E": pe,
        "Mean Free Cash Flow (past 4 years)": mean_fcf,
        "CMP": df.iloc[0]["Close"],
        "% Change": change_percent,
    }

    metrics = pd.DataFrame.from_dict([metrics])

    mdf = yft.get_major_holders()
    major_holders = {
        "Insider": mdf[mdf[1] == "% of Shares Held by All Insider"].values[0][0],
        "Institutions": mdf[mdf[1] == "% of Shares Held by Institutions"].values[0][0],
        "Number of Institutions": mdf[
            mdf[1] == "Number of Institutions Holding Shares"
        ].values[0][0],
    }
    major_holders["Others"] = (
        str(
            round(
                100
                - (
                    float(major_holders["Insider"][:-1])
                    + float(major_holders["Institutions"][:-1])
                ),
                2,
            )
        )
        + "%"
    )

    major_holders = pd.DataFrame.from_dict([major_holders])

    response = {
        "metrics": metrics,
        "dfs": {
            "cf_yearly": cf,
            "bls_yearly": yft.get_balance_sheet_yearly(),
            "inc_yearly": yft.get_income_stmt_yearly(),
            "major_holders": major_holders,
        },
    }
    return response
