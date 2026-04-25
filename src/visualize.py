# src/visualize.py
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker

def plot_sentiment_vs_price(sentiment_pdf: pd.DataFrame, ticker: str, output_path: str = None):
    # --- Prep sentiment data ---
    df = sentiment_pdf[sentiment_pdf["ticker"] == ticker].copy()
    df["date"] = pd.to_datetime(df["publishedAt"]).dt.normalize()  # floor to midnight

    daily_sentiment = (
        df.groupby("date")["sentiment_score"]
        .mean()
        .reset_index()
        .sort_values("date")
    )

    # --- Fetch stock price ---
    start = (daily_sentiment["date"].min() - pd.Timedelta(days=1)).strftime("%Y-%m-%d")
    end   = (daily_sentiment["date"].max() + pd.Timedelta(days=2)).strftime("%Y-%m-%d")

    raw = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=True)

    # Fix MultiIndex columns (yfinance quirk)
    if isinstance(raw.columns, pd.MultiIndex):
        raw.columns = raw.columns.get_level_values(0)

    stock = raw[["Close"]].copy()
    stock.index = pd.to_datetime(stock.index)
    stock = stock.reset_index()
    stock.columns = ["date", "close"]
    stock["date"] = pd.to_datetime(stock["date"]).dt.tz_localize(None).dt.normalize()

    # --- Plot ---
    fig, ax1 = plt.subplots(figsize=(13, 5))
    fig.patch.set_facecolor("#0d1117")
    ax1.set_facecolor("#0d1117")

    # Sentiment bars — fixed width in days
    bar_width = 0.6  # days
    colors = [
        "#22c55e" if s > 0.05 else "#ef4444" if s < -0.05 else "#64748b"
        for s in daily_sentiment["sentiment_score"]
    ]
    ax1.bar(
        daily_sentiment["date"],
        daily_sentiment["sentiment_score"],
        color=colors,
        alpha=0.85,
        width=bar_width,
        zorder=2,
        label="Avg Sentiment"
    )

    # Zero line
    ax1.axhline(0, color="#475569", linewidth=0.8, linestyle="--", zorder=1)

    ax1.set_ylabel("Sentiment Score", color="#cbd5e1", fontsize=11)
    ax1.set_ylim(-1.3, 1.6)
    ax1.tick_params(colors="#cbd5e1", labelsize=9)
    for spine in ax1.spines.values():
        spine.set_color("#1e293b")
    ax1.yaxis.set_major_formatter(mticker.FormatStrFormatter("%.1f"))

    # Stock price line (right axis)
    ax2 = ax1.twinx()
    if not stock.empty:
        ax2.plot(
            stock["date"], stock["close"],
            color="#f59e0b", linewidth=2.2,
            marker="o", markersize=4,
            zorder=3, label=f"{ticker} Price"
        )
    ax2.set_ylabel("Stock Price (USD)", color="#f59e0b", fontsize=11)
    ax2.tick_params(colors="#f59e0b", labelsize=9)
    for spine in ax2.spines.values():
        spine.set_color("#1e293b")

    # X-axis formatting
    sent_dates = pd.to_datetime(daily_sentiment["date"]).dt.tz_localize(None)
    stock_dates = pd.to_datetime(stock["date"]).dt.tz_localize(None)
    all_dates = pd.concat([sent_dates, stock_dates]).dropna()
    if not all_dates.empty:
        ax1.set_xlim(all_dates.min() - pd.Timedelta(hours=12),
                    all_dates.max() + pd.Timedelta(hours=12))

    ax1.xaxis.set_major_locator(mdates.DayLocator(interval=1))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    plt.xticks(rotation=30, ha="right", color="#cbd5e1", fontsize=9)

    # Grid
    ax1.yaxis.grid(True, color="#1e293b", linewidth=0.6, zorder=0)
    ax1.set_axisbelow(True)

    # Title & Legend
    plt.title(f"{ticker} — News Sentiment vs. Stock Price",
              color="#f1f5f9", fontsize=14, fontweight="bold", pad=14)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2,
               facecolor="#1e293b", edgecolor="#334155",
               labelcolor="#e2e8f0", fontsize=9, loc="upper left")

    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=150, bbox_inches="tight",
                    facecolor=fig.get_facecolor())
        print(f"Chart saved → {output_path}")
        plt.close()
    else:
        plt.show()