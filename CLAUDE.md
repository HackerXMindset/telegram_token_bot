# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Telegram bot for comprehensive Solana token analysis. The bot detects contract addresses in messages and provides detailed token analysis including market data, holder breakdown, security information, and social links with clickable Solscan integration.

## Core Architecture

- **`telegram_bot.py`** - Main Telegram bot application using python-telegram-bot library
- **`s.py`** - Token analysis engine with multiple API integrations (Helius, DexScreener, pump.fun)
- **Two-layer design**: Bot handles UI/formatting, analysis module handles data fetching

## API Dependencies

The project integrates with multiple external APIs:
- **Helius API** - Comprehensive Solana blockchain data (metadata, holders, transactions, account info)
- **DexScreener API** - Price data, market cap, volume, liquidity information
- **pump.fun APIs** - Advanced analytics, livestream status, bonding curve data

## Key Features

- **Smart contract detection** - Automatic base58 address detection in messages
- **Multi-API data aggregation** - Combines data from 3+ sources for comprehensive analysis
- **pump.fun specialization** - Enhanced analytics for pump.fun tokens including bonding curves, sniper detection
- **HTML formatting** - Rich text with clickable Solscan links for all addresses/transactions
- **Image handling** - Downloads and sends token logos when available

## Development Commands

### Run the bot
```bash
python telegram_bot.py
```

### CLI analysis tool
```bash
python s.py
```

### Install dependencies
```bash
pip install python-telegram-bot requests
```

## Configuration Requirements

Before running, update these credentials:

1. **Bot token** in `telegram_bot.py`:
   ```python
   BOT_TOKEN = "your_bot_token_here"
   ```

2. **Helius API key** in `s.py`:
   ```python
   API_KEY = "your_helius_api_key_here"
   ```

## Code Structure Patterns

### Data Flow
1. Message received → Contract address detected → `analyze_token()` called
2. Multiple API calls executed in parallel for comprehensive data
3. Data aggregated and formatted with HTML markup
4. Response sent with clickable links and optional token image

### API Integration Pattern
All API functions follow consistent error handling:
```python
try:
    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response.json()
except Exception as e:
    return {"error": str(e)}
```

### Formatting Strategy
- HTML parsing enabled for rich text formatting
- All user data escaped to prevent injection
- Solscan links auto-generated for addresses/transactions
- Progress bars for bonding curve visualization

## pump.fun Integration

Special handling for pump.fun tokens (addresses ending in 'pump'):
- Advanced analytics from pump.fun APIs
- Bonding curve progress tracking
- Sniper detection and risk assessment
- Enhanced developer holdings analysis
- Social verification checks

## Security Considerations

- All user input properly escaped for HTML rendering
- API keys should be environment variables in production
- Rate limiting built into external API calls
- No sensitive data stored or logged

## Testing Approach

Manual testing workflow:
1. Send various contract addresses to bot
2. Verify data accuracy against blockchain explorers
3. Test HTML formatting renders correctly
4. Confirm all Solscan links work properly

## Common Issues

- **API rate limits** - Helius/DexScreener may throttle requests
- **Missing token data** - New tokens may not have complete metadata
- **pump.fun detection** - Only tokens ending in 'pump' get enhanced analytics
- **Image downloads** - Network timeouts can prevent logo display
## Sessions System Behaviors

@CLAUDE.sessions.md
