# GEMINI.md

## Project Overview

This project contains two independent implementations of a Solana token analysis bot for Telegram. Both bots can take a Solana contract address and return a detailed analysis of the token, but they are built with different technologies and have slightly different features.

Both bots share a common `.env` file for configuration.

---

## 1. Python Implementation

A feature-rich token analysis bot with detailed, formatted output, including image previews.

-   **Entry Point:** `telegram_bot.py`
-   **Core Logic:** The main analysis logic is in `s.py`. It concurrently fetches data from multiple Helius endpoints (`query_metadata_v1`, `getAsset`, `getTokenLargestAccounts`, `getTokenSupply`, etc.), DexScreener, and pump.fun.
-   **Features:**
    -   Rich HTML-formatted messages in Telegram.
    -   Downloads and displays the token's image directly in the chat.
    -   Detailed market data: Market Cap, FDV, liquidity, volume, and price changes.
    -   In-depth holder analysis: Top 10 holders, distribution percentages, and total holder count.
    -   Social media link extraction (Twitter, Telegram, Website).
    -   Security and developer information: Checks for mutability and analyzes the developer's wallet holdings and SOL balance.
    -   Data from pump.fun, including bonding curve status, engagement metrics, and creation timestamps.
    -   Clickable links to Solscan, DexScreener, and Birdeye.
-   **Libraries:** `python-telegram-bot`, `aiohttp`, `orjson`, `python-dotenv`.

### Building and Running (Python)

1.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

2.  **Configure Environment:**
    Create a `.env` file and add your bot token and API keys:
    ```
    BOT_TOKEN="your_telegram_bot_token"
    HELIUS_API_KEY="your_helius_api_key"
    PUMP_FUN_JWT="your_pump_fun_jwt" # Optional, for authenticated pump.fun requests
    ```

3.  **Run the Bot:**
    ```bash
    python telegram_bot.py
    ```

---

## 2. Rust Implementation

A high-performance, concurrent token analysis bot focused on speed and efficiency.

-   **Entry Point:** `src/main.rs`
-   **Core Logic:** The `src/api.rs` file handles concurrent API calls to Helius, DexScreener, and pump.fun using `tokio`. It also includes an in-memory cache (`moka`) to reduce redundant API calls for frequently requested tokens.
-   **Features:**
    -   High performance due to Rust's concurrency and optimized async runtime.
    -   In-memory caching of results for 60 seconds.
    -   Clean, formatted HTML output with key token details.
    -   Extensive data from pump.fun, including market cap, ATH, timestamps, engagement, bonding curve details, and creator info.
    -   Clickable links to Solscan, DexScreener, and Birdeye.
-   **Libraries (Crates):** `teloxide` (Telegram), `reqwest` (HTTP), `tokio` (async), `moka` (caching), `serde` (serialization), `regex` (address detection), `chrono` (time), `dotenv` (config), `tracing-subscriber` (logging).

### Building and Running (Rust)

1.  **Build the project:**
    ```bash
    cargo build --release
    ```

2.  **Configure Environment:**
    Create a `.env` file (if you haven't already for the Python bot) and add your bot token and API key:
    ```
    BOT_TOKEN="your_telegram_bot_token"
    HELIUS_API_KEY="your_helius_api_key"
    PUMP_FUN_JWT="your_pump_fun_jwt" # Optional, for authenticated pump.fun requests
    ```

3.  **Run the Bot:**
    ```bash
    ./target/release/telegram-token-bot
    ```

## Development Conventions

-   **Configuration:** Both bots read credentials (`BOT_TOKEN`, `HELIUS_API_KEY`, `PUMP_FUN_JWT`) from a single `.env` file at the project root.
-   **Modular Design:**
    -   The Python bot separates its API logic (`s.py`) from its Telegram bot logic (`telegram_bot.py`).
    -   The Rust bot separates its API logic (`src/api.rs`), bot interaction logic (`src/bot.rs`), and data types (`src/types.rs`).
-   **Dependencies:** Python dependencies are in `requirements.txt`. Rust dependencies are in `Cargo.toml`.