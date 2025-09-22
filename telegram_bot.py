import re
import json
import asyncio
import aiohttp
import os
from dotenv import load_dotenv
from io import BytesIO
from datetime import datetime
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from s import analyze_token

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

user_states = {}

def format_data_for_display(data: dict) -> str:
    message_parts = []

    # Mint Address (always first)
    if 'mint_address' in data and data['mint_address']:
        message_parts.append(f"*Mint Address*: `{data['mint_address']}`")

    # Metadata
    if 'metadata' in data and data['metadata'] and data['metadata'].get('off_chain_metadata') and data['metadata']['off_chain_metadata'].get('metadata'):
        meta = data['metadata']['off_chain_metadata']['metadata']
        if meta.get('name'):
            message_parts.append(f"*Name*: `{meta['name']}`")
        if meta.get('symbol'):
            message_parts.append(f"*Symbol*: `{meta['symbol']}`")
        if meta.get('description'):
            message_parts.append(f"*Description*: {meta['description']}")
        if meta.get('website'):
            message_parts.append(f"*Website*: {meta['website']}")
        if meta.get('twitter'):
            message_parts.append(f"*Twitter*: {meta['twitter']}")
        if meta.get('telegram'):
            message_parts.append(f"*Telegram*: {meta['telegram']}")

    # DexScreener Data
    if 'dexscreener_data' in data and data['dexscreener_data'] and data['dexscreener_data'].get('pairs'):
        message_parts.append("\n*DexScreener Data*:")
        for pair in data['dexscreener_data']['pairs']:
            if pair.get('base_token') and pair['base_token'].get('symbol'):
                message_parts.append(f"  - Pair: `{pair['base_token']['symbol']}/{pair['quote_token']['symbol'] if pair.get('quote_token') else '?'}`")
            if pair.get('priceUsd'):
                message_parts.append(f"    Price USD: `{float(pair['priceUsd']):,.6f}`")
            if pair.get('marketCap'):
                message_parts.append(f"    Market Cap: `{int(pair['marketCap']):,}`")
            if pair.get('volume') and pair['volume'].get('h24'):
                message_parts.append(f"    Volume (24h): `{int(pair['volume']['h24']):,}`")
            if pair.get('liquidity') and pair['liquidity'].get('usd'):
                message_parts.append(f"    Liquidity USD: `{int(pair['liquidity']['usd']):,}`")
            if pair.get('fdv'):
                message_parts.append(f"    FDV: `{int(pair['fdv']):,}`")
            if pair.get('priceChange') and pair['priceChange'].get('h24'):
                message_parts.append(f"    Price Change (24h): `{pair['priceChange']['h24']:.2f}%`")

    # Pump.fun Data
    if 'pump_fun_data' in data and data['pump_fun_data']:
        pump_data = data['pump_fun_data']
        message_parts.append("\n*Pump.fun Data*:")
        if pump_data.get('market_cap'):
            message_parts.append(f"  Market Cap: `{int(pump_data['market_cap']):,}`")
        if pump_data.get('usd_market_cap'):
            message_parts.append(f"  USD Market Cap: `{int(pump_data['usd_market_cap']):,}`")
        if pump_data.get('total_supply'):
            message_parts.append(f"  Total Supply: `{int(pump_data['total_supply']):,}`")
        if pump_data.get('num_participants'):
            message_parts.append(f"  Participants: `{int(pump_data['num_participants']):,}`")
        if pump_data.get('website'):
            message_parts.append(f"  Website: {pump_data['website']}")
        if pump_data.get('twitter'):
            message_parts.append(f"  Twitter: {pump_data['twitter']}")
        if pump_data.get('telegram'):
            message_parts.append(f"  Telegram: {pump_data['telegram']}")

    # Jupiter Data
    if 'jupiter_data' in data and data['jupiter_data']:
        jupiter_data = data['jupiter_data']
        message_parts.append("\n*Jupiter Data*:")
        if jupiter_data.get('mcap'):
            message_parts.append(f"  Market Cap: `{int(jupiter_data['mcap']):,}`")
        if jupiter_data.get('usd_price'):
            message_parts.append(f"  USD Price: `{jupiter_data['usd_price']:.6f}`")
        if jupiter_data.get('liquidity'):
            message_parts.append(f"  Liquidity: `{int(jupiter_data['liquidity']):,}`")
        if jupiter_data.get('holder_count'):
            message_parts.append(f"  Holder Count: `{int(jupiter_data['holder_count']):,}`")
        if jupiter_data.get('website'):
            message_parts.append(f"  Website: {jupiter_data['website']}")
        if jupiter_data.get('twitter'):
            message_parts.append(f"  Twitter: {jupiter_data['twitter']}")
        if jupiter_data.get('telegram'):
            message_parts.append(f"  Telegram: {jupiter_data['telegram']}")
        if jupiter_data.get('stats_24h') and jupiter_data['stats_24h'].get('price_change'):
            message_parts.append(f"  Price Change (24h): `{jupiter_data['stats_24h']['price_change']:.2f}%`")
        if jupiter_data.get('stats_24h') and jupiter_data['stats_24h'].get('volume_change'):
            message_parts.append(f"  Volume Change (24h): `{jupiter_data['stats_24h']['volume_change']:.2f}%`")

    # Holders Data
    if 'holders' in data and data['holders'] and data['holders'].get('result') and data['holders']['result'].get('value'):
        message_parts.append("\n*Top Holders*:")
        for i, holder in enumerate(data['holders']['result']['value'][:5]): # Limit to top 5
            if holder.get('address') and holder.get('ui_amount'):
                message_parts.append(f"  {i+1}. `{holder['address']}`: `{holder['ui_amount']:,.2f}`")

    # Supply Info
    if 'supply_info' in data and data['supply_info'] and data['supply_info'].get('result') and data['supply_info']['result'].get('value'):
        supply_value = data['supply_info']['result']['value']
        message_parts.append("\n*Supply Info*:")
        if supply_value.get('ui_amount'):
            message_parts.append(f"  Total Supply: `{supply_value['ui_amount']:,.0f}`")

    # DexScreener Orders Data
    if 'dexscreener_orders_data' in data and data['dexscreener_orders_data']:
        message_parts.append("\n*DexScreener Orders*:")
        for i, order in enumerate(data['dexscreener_orders_data'][:5]): # Limit to 5 orders
            if order.get('type') and order.get('status'):
                message_parts.append(f"  {i+1}. Type: `{order['type']}`, Status: `{order['status']}`")

    return "\n".join(message_parts)


def detect_contract_address(text):
    """Detect Solana contract address in text (base58, 32-44 chars)"""
    pattern = r'\b[1-9A-HJ-NP-Za-km-z]{32,44}\b'
    matches = re.findall(pattern, text)
    return matches[0] if matches else None

def escape_html(text):
    """Escape HTML special characters"""
    if not text:
        return text
    return str(text).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def format_token_data(data):
    """Formats token data into a clean, compact, and structured layout based on user templates."""
    try:
        # --- Data Extraction ---
        ca = data.get('mint_address', 'N/A')
        metadata = data.get('metadata_v1', {})
        asset_data = data.get('asset_data', {}).get('result', {})
        holders_data = data.get('largest_accounts', {}).get('result', {}).get('value', [])
        supply_info = data.get('supply_info', {}).get('result', {})
        price_data = data.get('price_data', {})
        creator_balance_data = data.get('creator_balance', {})
        creator_sol_balance_data = data.get('creator_sol_balance', {})
        pump_fun_data = data.get('pump_fun_data', {})

        # --- Data Processing ---
        name, symbol, description, image_url = "Unknown", "N/A", "", None
        supply, price, fdv, market_cap = 0, 0, 0, 0
        is_mutable = False

        # Get metadata from the first item in the metadata_v1 list
        metadata_v1 = data.get('metadata_v1', [])
        if metadata_v1 and len(metadata_v1) > 0:
            metadata = metadata_v1[0]
            if metadata.get('onChainMetadata', {}).get('metadata'):
                meta = metadata['onChainMetadata']['metadata']
                name = meta['data'].get('name', 'Unknown').strip()
                symbol = meta['data'].get('symbol', 'N/A').strip()
                is_mutable = meta.get('isMutable', False)

        # Prioritize pump.fun supply
        supply = pump_fun_data.get('total_supply', supply_info.get('value', {}).get('uiAmount', 0))

        if asset_data.get('content', {}).get('links', {}).get('image'):
            image_url = asset_data['content']['links']['image']

        volume_6h, volume_1h, volume_24h, volume_5m = 0, 0, 0, 0
        price_change_6h, price_change_1h, price_change_24h, price_change_5m = 0, 0, 0, 0
        liquidity_usd, liquidity_base, liquidity_quote = 0, 0, 0
        dex_name, pool_age, price_native = "N/A", "N/A", 0
        buys_6h, sells_6h, buys_1h, sells_1h = 0, 0, 0, 0
        pair_labels, boost_active = [], 0
        ath_market_cap = pump_fun_data.get('allTimeHighMarketCap', 0)

        if price_data.get('pairs'):
            pair = price_data['pairs'][0]
            price = float(pair.get('priceUsd', 0))
            price_native = float(pair.get('priceNative', 0))

            # Use pump.fun's market cap when available
            market_cap = pump_fun_data.get('usd_market_cap', float(pair.get('marketCap', 0)))
            fdv = price * supply if supply > 0 else 0

            # Volume data for multiple timeframes
            volume_data = pair.get('volume', {})
            volume_5m = float(volume_data.get('m5', 0))
            volume_1h = float(volume_data.get('h1', 0))
            volume_6h = float(volume_data.get('h6', 0))
            volume_24h = float(volume_data.get('h24', 0))

            # Price change data for multiple timeframes
            price_change_data = pair.get('priceChange', {})
            price_change_5m = float(price_change_data.get('m5', 0))
            price_change_1h = float(price_change_data.get('h1', 0))
            price_change_6h = float(price_change_data.get('h6', 0))
            price_change_24h = float(price_change_data.get('h24', 0))

            # Liquidity breakdown
            liquidity_data = pair.get('liquidity', {})
            liquidity_usd = float(liquidity_data.get('usd', 0))
            liquidity_base = float(liquidity_data.get('base', 0))
            liquidity_quote = float(liquidity_data.get('quote', 0))

            # Transaction activity
            txns_data = pair.get('txns', {})
            if txns_data:
                # Get 6h and 1h transaction data
                h6_txns = txns_data.get('h6', {})
                h1_txns = txns_data.get('h1', {})
                buys_6h = h6_txns.get('buys', 0)
                sells_6h = h6_txns.get('sells', 0)
                buys_1h = h1_txns.get('buys', 0)
                sells_1h = h1_txns.get('sells', 0)

            # DEX and pair info
            dex_name = pair.get('dexId', 'N/A')
            pair_labels = pair.get('labels', [])

            # Boost information
            boosts_data = pair.get('boosts', {})
            boost_active = boosts_data.get('active', 0)

            # Pair creation time
            created_at = pair.get('pairCreatedAt')
            if created_at:
                try:
                    created_time = datetime.fromtimestamp(created_at / 1000)
                    time_diff = datetime.utcnow() - created_time
                    days, seconds = time_diff.days, time_diff.seconds
                    if days > 0: pool_age = f'{days}d'
                    elif seconds >= 3600: pool_age = f'{seconds // 3600}h'
                    else: pool_age = f'{seconds // 60}m'
                except: pool_age = "N/A"

        # --- Formatting ---
        parts = []
        name_esc, symbol_esc, ca_esc = escape_html(name), escape_html(symbol), escape_html(ca)

        # Header
        parts.append(f'🚀 <b>{name_esc} ({symbol_esc})</b>')
        parts.append(f'<code>{ca_esc}</code>')
        parts.append(f'<a href="https://solscan.io/token/{ca}">Solscan</a> | <a href="https://dexscreener.com/solana/{ca}">DexScreener</a> | <a href="https://birdeye.so/token/{ca}?chain=solana">Birdeye</a>')
        parts.append('')

        # Market Data
        ath_market_cap = pump_fun_data.get('ath_market_cap', 0)
        parts.append("💰 <b>Price & Market Data</b>")

        # Price with native price if available
        price_line = f"💵 <b>Price (Dex):</b> ${price:.8f}"
        if price_native > 0:
            price_line += f" | <b>Native (Dex):</b> {price_native:.8f}"
        parts.append(price_line)

        parts.append(f"🧢 <b>MC (pf):</b> ${market_cap:,.0f} | 💎 <b>FDV (calc):</b> ${fdv:,.0f}")
        if ath_market_cap > 0:
            parts.append(f"🔥 <b>ATH (pf):</b> ${ath_market_cap:,.0f}")
        parts.append(f'⏱️ <b>Pool Age (Dex):</b> {pool_age} | 🏢 <b>DEX (Dex):</b> {dex_name}')

        # Pair labels if available
        if pair_labels:
            labels_str = ", ".join(pair_labels[:3])  # Show max 3 labels
            parts.append(f"🏷️ <b>Labels:</b> {labels_str}")

        # Boost status
        if boost_active > 0:
            parts.append(f"🚀 <b>Active Boosts:</b> {boost_active}")

        parts.append('')

        # Volume Data
        parts.append("📊 <b>Volume Data (Dex)</b>")
        parts.append(f'<b>5m:</b> ${volume_5m:,.0f} | <b>1h:</b> ${volume_1h:,.0f}')
        parts.append(f'<b>6h:</b> ${volume_6h:,.0f} | <b>24h:</b> ${volume_24h:,.0f}')
        parts.append('')

        # Price Changes
        parts.append("📈 <b>Price Changes (Dex)</b>")
        def format_change(change):
            sign = "+" if change >= 0 else ""
            return f"{sign}{change:.2f}%"

        parts.append(f'<b>5m:</b> {format_change(price_change_5m)} | <b>1h:</b> {format_change(price_change_1h)}')
        parts.append(f'<b>6h:</b> {format_change(price_change_6h)} | <b>24h:</b> {format_change(price_change_24h)}')
        parts.append('')

        # Liquidity Breakdown
        parts.append("💧 <b>Liquidity (Dex)</b>")
        parts.append(f"<b>USD:</b> ${liquidity_usd:,.0f}")
        if liquidity_base > 0 or liquidity_quote > 0:
            parts.append(f"<b>Base:</b> {liquidity_base:,.0f} | <b>Quote:</b> {liquidity_quote:,.0f}")
        parts.append('')

        # Transaction Activity
        if buys_6h > 0 or sells_6h > 0 or buys_1h > 0 or sells_1h > 0:
            parts.append("🔄 <b>Transaction Activity (Dex)</b>")
            parts.append(f'<b>6h:</b> {buys_6h} buys / {sells_6h} sells')
            parts.append(f'<b>1h:</b> {buys_1h} buys / {sells_1h} sells')

            # Calculate buy/sell ratios if we have data
            if buys_6h + sells_6h > 0:
                buy_ratio_6h = (buys_6h / (buys_6h + sells_6h)) * 100
                parts.append(f'<b>6h Buy Ratio:</b> {buy_ratio_6h:.1f}%')
            parts.append('')

        # Timestamps (pf)
        parts.append("🗓️ <b>Timestamps (pf)</b>")
        created_ts = pump_fun_data.get('created_timestamp')
        if created_ts:
            parts.append(f"<b>Created:</b> {datetime.fromtimestamp(created_ts / 1000).strftime('%Y-%m-%d %H:%M')}")
        last_trade_ts = pump_fun_data.get('last_trade_timestamp')
        if last_trade_ts:
            parts.append(f"<b>Last Trade:</b> {datetime.fromtimestamp(last_trade_ts / 1000).strftime('%Y-%m-%d %H:%M')}")
        ath_ts = pump_fun_data.get('ath_market_cap_timestamp')
        if ath_ts:
            parts.append(f"<b>ATH Date:</b> {datetime.fromtimestamp(ath_ts / 1000).strftime('%Y-%m-%d %H:%M')}")
        parts.append('')

        # Price Change
        change_1h_emoji = "🚀" if price_change_1h > 0 else "📉" if price_change_1h < 0 else "😐"
        change_6h_emoji = "🔥" if price_change_6h > 0 else "💀" if price_change_6h < 0 else "😐"
        parts.append(f'📉 <b>Price Change (1h/6h)</b>')
        parts.append(f'{change_1h_emoji} {price_change_1h:+.1f}% / {change_6h_emoji} {price_change_6h:+.1f}%')
        parts.append('')

        # Holders
        num_holders = pump_fun_data.get('numHolders')
        total_holders = num_holders if num_holders is not None else len(holders_data)
        top10_holders_data = holders_data[:10]
        top10_dist_percent = [ (h.get('uiAmount', 0) / supply * 100) for h in top10_holders_data ]
        top10_sum = sum(top10_dist_percent)
        parts.append(f'👥 <b>Holders (pf/Helius):</b> {total_holders} | <b>Top 10:</b> {top10_sum:.1f}%')
        parts.append('')

        # Security & Dev
        parts.append('🔒 <b>Security & Dev</b>')

        sniper_count = pump_fun_data.get('sniperCount')
        if sniper_count is not None:
            sniper_percentage = pump_fun_data.get('sniperOwnedPercentage', 0)
            parts.append(f"⚠️ <b>Risk (pf):</b> Snipers: {sniper_count} ({sniper_percentage:.2f}%)")

        creators = asset_data.get('creators', [])
        if creators:
            addr = creators[0].get('address', 'N/A')
            creator_link = f"https://solscan.io/account/{addr}"
            short_addr = f'{addr[:6]}...{addr[-6:]}' if len(addr) > 12 else addr
            stats_link = f"https://t.me/phanes_bot?start=pfdev_{addr}"
            
            dev_status, dev_dot, sol_balance_text = "N/A", "", ""
            dev_holdings_percentage = pump_fun_data.get('devHoldingsPercentage')
            
            holding_percentage = -1
            if 'pump' in ca and dev_holdings_percentage is not None:
                holding_percentage = dev_holdings_percentage
            elif creator_balance_data.get('result', {}).get('value'):
                token_accounts = creator_balance_data['result']['value']
                total_bal = sum(float(acc['account']['data']['parsed']['info'].get('tokenAmount', {}).get('uiAmount', 0)) for acc in token_accounts)
                if total_bal > 0:
                    holding_percentage = (total_bal / supply * 100) if supply > 0 else 0
                else:
                    holding_percentage = 0
            
            if holding_percentage > 0:
                dev_status = f"holding {holding_percentage:.1f}%"
                dev_dot = "🔴"
            elif holding_percentage == 0:
                dev_status = "Sold"
                dev_dot = "🟢"

            sol_balance_str = ""
            if creator_sol_balance_data.get('result', {}).get('value') is not None:
                sol_lamports = creator_sol_balance_data['result']['value']
                sol_balance_str = f'| <b>Balance:</b> {(sol_lamports / 1_000_000_000):.2f} SOL'

            parts.append(f'🧑‍💻 <b>Dev (pf/Helius):</b> <a href="{creator_link}">{escape_html(short_addr)}</a> {dev_dot} ({escape_html(dev_status)}) <a href="{stats_link}">[Stats]</a> {sol_balance_str}')

        dex_paid_dot = "🔴"
        if price_data.get('pairs') and price_data['pairs'][0].get('info', {}):
            dex_paid_dot = "🟢"
        info_link = f"https://t.me/phanespurplebot?start=dp_{ca}"
        parts.append(f'├ <b>DEX (Dex):</b> {escape_html(dex_name)} | <b>DEX Paid (Dex):</b> {dex_paid_dot} <a href="{info_link}">[info]</a>')
        
        parts.append(f'🔧 <b>Mutable (Helius):</b> {"✅" if is_mutable else "❌"}')
        parts.append('')

        # Socials
        parts.append("🌐 <b>Socials (Helius/pf)</b>")
        social_links = {}
        if metadata.get('offChainMetadata', {}).get('metadata'):
            off_meta = metadata['offChainMetadata']['metadata']
            for field in ['twitter', 'telegram', 'website']:
                if off_meta.get(field): social_links[field] = off_meta[field]
        if pump_fun_data.get("found"):
            if pump_fun_data.get('twitter'): social_links['twitter'] = pump_fun_data['twitter']
            if pump_fun_data.get('telegram'): social_links['telegram'] = pump_fun_data['telegram']
            if pump_fun_data.get('website'): social_links['website'] = pump_fun_data['website']

        social_parts = []
        if social_links.get('twitter'): social_parts.append(f'<a href="{social_links["twitter"]}">X/Twitter</a>')
        if social_links.get('telegram'): social_parts.append(f'<a href="{social_links["telegram"]}">Telegram</a>')
        if social_links.get('website'): social_parts.append(f'<a href="{social_links["website"]}">Website</a>')
        
        if social_parts:
            parts.append(" | ".join(social_parts))
        else:
            parts.append("No social links found.")

        parts.append('')

        # Bonding Curve (pf)
        parts.append("🎢 <b>Bonding Curve (pf)</b>")
        real_sol = pump_fun_data.get('real_sol_reserves', 0)
        virtual_sol = pump_fun_data.get('virtual_sol_reserves', 0)
        bonding_curve_addr = pump_fun_data.get('bonding_curve')
        parts.append(f"Real SOL: {real_sol / 1e9:.2f} | Virtual SOL: {virtual_sol / 1e9:.2f}")
        if bonding_curve_addr:
            parts.append(f"Address: <code>{bonding_curve_addr}</code>")
        parts.append('')

        # Engagement (pf)
        parts.append("💬 <b>Engagement (pf)</b>")
        replies = pump_fun_data.get('reply_count', 0)
        participants = pump_fun_data.get('num_participants', 0)
        parts.append(f"Replies: {replies} | Participants: {participants}")
        parts.append('')

        # Description
        if description:
            parts.append(f"📝 {escape_html(description)}")
            parts.append('')

        # Holder Table
        if holders_data:
            dist_links = [f'<a href="https://solscan.io/account/{h.get("address")}">{p:.1f}</a>' for h, p in zip(top10_holders_data, top10_dist_percent)]
            parts.append(f'<code>{"|".join(dist_links)}</code>')

            table_parts = ["<b>Top 10 Holders</b>", "<code>User      | %Hold    | Amount", "---------------------------"]
            for i, holder in enumerate(top10_holders_data, 1):
                address = holder.get('address', 'N/A')
                ui_amount = holder.get('uiAmount', 0)
                short_addr = f'{address[:4]}..{address[-4:]}' if len(address) > 8 else address
                percentage = (ui_amount / supply * 100) if supply > 0 else 0
                amount_str = f'{ui_amount/1000000:.1f}M' if ui_amount >= 1000000 else f'{ui_amount/1000:.1f}K'
                table_parts.append(f'{i:<2}.{short_addr:<8} | {percentage:<7.2f}% | {amount_str}')
            table_parts.append("</code>")
            table_content = "\n".join(table_parts)
            parts.append(f'<blockquote expandable>{table_content}</blockquote>')

        return "\n".join(parts), image_url

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return f"❌ Error formatting data: {str(e)}", None


async def download_and_send_image(update, image_url):
    """Download image and send to Telegram"""
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(image_url, timeout=20) as response: # Increased timeout
                response.raise_for_status()
                image_data = BytesIO(await response.read())
                image_data.name = 'token_logo.jpg'
                await update.message.reply_photo(photo=image_data)
                return True
        except Exception as e:
            print(f"Error downloading/sending image: {e}")
            return False

async def process_analysis(update: Update, ca: str):
    """Process the token analysis and send the result."""
    try:
        result = await analyze_token(ca)
        formatted_data, image_url = format_token_data(result)

        if image_url:
            image_sent = await download_and_send_image(update, image_url)
            if not image_sent:
                # If image fails, add a link to the text message
                formatted_data = f'<a href="{image_url}">🖼️</a>\n{formatted_data}'

        await update.message.reply_text(formatted_data, parse_mode='HTML', disable_web_page_preview=True)

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        await update.message.reply_text(f"❌ Error analyzing token: {str(e)}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming messages, analyze token, and send a single message with image and caption."""
    if not update.message or not update.message.text:
        return

    ca = detect_contract_address(update.message.text)
    if not ca:
        await update.message.reply_text("🪙 Send me a contract address to analyze token data!")
        return

    await update.message.reply_text(f"🔍 Analyzing token: `{ca}`", parse_mode='MarkdownV2')

    # Run the analysis in the background
    asyncio.create_task(process_analysis(update, ca))

def main():
    """Start the Telegram bot"""
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN not found. Please set it in your .env file.")
        return

    print("🤖 Starting Telegram bot...")
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ Bot is running! Send contract addresses to analyze tokens.")
    application.run_polling()

if __name__ == "__main__":
    main()
