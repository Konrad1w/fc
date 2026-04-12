import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# --- Parametry ---
monthly_investment_pln = 7000
years = 10
annual_interest = 0.05  # lokata 5% rocznie
monthly_interest = (1 + annual_interest) ** (1/12) - 1
end_date = datetime.today()
start_date = end_date - timedelta(days=years*365)

# --- Pobranie danych ETF z Yahoo Finance ---
etf_raw = yf.download("SPOL.L", start=start_date, end=end_date, interval="1mo", multi_level_index=False)
data = pd.DataFrame({"ETF": etf_raw["Close"]}).dropna()

# --- Symulacja DCA co miesiąc ---
total_units = 0
portfolio_values = []

for date, row in data.iterrows():
    units_bought = monthly_investment_pln / row["ETF"]
    total_units += units_bought
    current_value = total_units * row["ETF"]
    portfolio_values.append(current_value)

data["PortfolioDCA"] = portfolio_values
data["TotalInvestedPLN"] = [monthly_investment_pln * (i + 1) for i in range(len(data))]

# --- Symulacja lokaty 5% rocznie ---
savings_value = 0
savings_values = []
for i in range(len(data)):
    savings_value = savings_value * (1 + monthly_interest) + monthly_investment_pln
    savings_values.append(savings_value)
data["SavingsAccount"] = savings_values

# --- Wyniki ---
final_value_etf = data["PortfolioDCA"].iloc[-1]
final_value_savings = data["SavingsAccount"].iloc[-1]
total_invested = monthly_investment_pln * len(data)

gain_etf = final_value_etf - total_invested
gain_savings = final_value_savings - total_invested

cagr_etf = (final_value_etf / total_invested) ** (1/years) - 1
cagr_savings = (final_value_savings / total_invested) ** (1/years) - 1

print(f"📅 Okres: {years} lata")
print(f"💰 Suma wpłat: {total_invested:,.0f} PLN")

print("\n--- iShares MSCI Poland ETF ---")
print(f"📈 Wartość końcowa: {final_value_etf:,.0f} PLN")
print(f"🚀 Zysk: {gain_etf:,.0f} PLN ({gain_etf/total_invested*100:.2f}%)")
print(f"📆 CAGR: {cagr_etf*100:.2f}%")

print("\n--- Lokata 5% rocznie ---")
print(f"🏦 Wartość końcowa: {final_value_savings:,.0f} PLN")
print(f"💤 Zysk: {gain_savings:,.0f} PLN ({gain_savings/total_invested*100:.2f}%)")
print(f"📆 CAGR: {cagr_savings*100:.2f}%")

# --- Wykres porównawczy ---
plt.figure(figsize=(12,7))
plt.plot(data.index, data["PortfolioDCA"], label="ETF DCA co miesiąc")
plt.plot(data.index, data["SavingsAccount"], label="Lokata 5% rocznie", linestyle='--')
plt.plot(data.index, data["TotalInvestedPLN"], color='gray', alpha=0.5, label="Suma wpłat")
plt.title("Porównanie: Inwestowanie w iShares MSCI Poland ETF vs Lokata 5%")
plt.xlabel("Data")
plt.ylabel("Wartość portfela [PLN]")
plt.legend()
plt.grid(True)
plt.show()
