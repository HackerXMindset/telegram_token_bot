use crate::api::ApiClient;
use crate::types::*;
use anyhow::Result;
use regex::Regex;
use std::sync::Arc;
use std::time::Instant;
use teloxide::{prelude::*, utils::html};

pub async fn start_bot(bot_token: String, api_client: ApiClient) -> Result<()> {
    let bot = Bot::new(bot_token);
    let api_client = Arc::new(api_client);

    teloxide::repl(bot, move |bot: Bot, msg: Message| {
        let api_client = Arc::clone(&api_client);
        async move {
            handle_message(bot, msg, api_client).await
        }
    })
    .await;

    Ok(())
}

async fn handle_message(
    bot: Bot,
    msg: Message,
    api_client: Arc<ApiClient>,
) -> ResponseResult<()> {
    if let Some(text) = msg.text() {
        if let Some(contract_address) = detect_contract_address(text) {
            // Start timing
            let start_time = Instant::now();

            // Analyze token
            match api_client.analyze_token(&contract_address).await {
                Ok(token_data) => {
                    let elapsed = start_time.elapsed();
                    let timing_text = format!("⚡ {}ms!", elapsed.as_millis());
                    let (formatted_text, _image_url) = format_token_data(&token_data);
                    let final_text = format!("{}\n\n{}", timing_text, formatted_text);

                    if final_text.len() > 4000 {
                        let mut start = 0;
                        while start < final_text.len() {
                            let end = std::cmp::min(start + 4000, final_text.len());
                            let chunk = &final_text[start..end];
                            bot.send_message(msg.chat.id, chunk)
                                .parse_mode(teloxide::types::ParseMode::Html)
                                .disable_web_page_preview(true)
                                .await?;
                            start = end;
                        }
                    } else {
                        bot.send_message(msg.chat.id, final_text)
                            .parse_mode(teloxide::types::ParseMode::Html)
                            .disable_web_page_preview(true)
                            .await?;
                    }
                }
                Err(e) => {
                    let elapsed = start_time.elapsed();
                    let timing_text = format!("⚡ {}ms!", elapsed.as_millis());
                    let error_text = format!("{}\n\n❌ Error analyzing token: {}", timing_text, e);

                    bot.send_message(msg.chat.id, error_text)
                        .await?;
                }
            }
        } else {
            bot.send_message(msg.chat.id, "🪙 Send me a contract address to analyze token data!")
                .await?;
        }
    }

    Ok(())
}

fn detect_contract_address(text: &str) -> Option<String> {
    // #COMPLETION_DRIVE: Assuming Solana address regex pattern is correct
    // #SUGGEST_VERIFY: Test with various Solana address formats to ensure accuracy

    let pattern = Regex::new(r"\b[1-9A-HJ-NP-Za-km-z]{32,44}\b").ok()?;
    pattern.find(text).map(|m| m.as_str().to_string())
}

fn format_token_data(data: &TokenData) -> (String, Option<String>) {
    let ca = &data.mint_address;
    let mut parts = Vec::new();

    // Default values
    let mut name = "Unknown".to_string();
    let mut symbol = "N/A".to_string();
    let mut description = "".to_string();
    let mut image_url: Option<String> = None;
    let mut social_links = std::collections::HashMap::new();

    // Extract from Helius Metadata if available
    if let Some(metadata) = &data.metadata {
        if let Some(on_chain) = &metadata.on_chain_metadata {
            if let Some(meta) = &on_chain.metadata {
                name = meta.data.name.clone().unwrap_or(name).trim().to_string();
                symbol = meta.data.symbol.clone().unwrap_or(symbol).trim().to_string();
            }
        }
        if let Some(off_chain) = &metadata.off_chain_metadata {
            if let Some(meta) = &off_chain.metadata {
                name = meta.name.clone().unwrap_or(name);
                symbol = meta.symbol.clone().unwrap_or(symbol);
                description = meta.description.clone().unwrap_or_default();
                image_url = meta.image.clone();
            }
        }
    }

    // Override with pump.fun data if available
    if let Some(pf) = &data.pump_fun_data {
        name = pf.name.clone().unwrap_or(name);
        symbol = pf.symbol.clone().unwrap_or(symbol);
        description = pf.description.clone().unwrap_or(description);
        image_url = pf.image_uri.clone();
        if pf.twitter.is_some() { social_links.insert("Twitter".to_string(), pf.twitter.clone()); }
        if pf.telegram.is_some() { social_links.insert("Telegram".to_string(), pf.telegram.clone()); }
        if pf.website.is_some() { social_links.insert("Website".to_string(), pf.website.clone()); }
    }

    // --- Formatting ---
    let name_esc = html::escape(&name);
    let symbol_esc = html::escape(&symbol);
    let ca_esc = html::escape(ca);

    // Header
    parts.push(format!("🚀 <b>{} ({})</b>", name_esc, symbol_esc));
    parts.push(format!("<code>{}</code>", ca_esc));
    parts.push(format!(
        "<a href=\"https://solscan.io/token/{}\">Solscan</a> | <a href=\"https://dexscreener.com/solana/{}\">DexScreener</a> | <a href=\"https://birdeye.so/token/{}?chain=solana\">Birdeye</a>",
        ca, ca, ca
    ));
    parts.push(String::new());

    // Market Data (from dexscreener)
    let (market_cap, fdv, liquidity_usd) = if let Some(dexscreener_data) = &data.dexscreener_data {
        if let Some(pair) = dexscreener_data.pairs.as_ref().and_then(|p| p.first()) {
            (pair.market_cap.unwrap_or(0.0), pair.fdv.unwrap_or(0.0), pair.liquidity.as_ref().map_or(0.0, |l| l.usd.unwrap_or(0.0)))
        } else {
            (0.0, 0.0, 0.0)
        }
    } else {
        (0.0, 0.0, 0.0)
    };

    if let Some(dexscreener_data) = &data.dexscreener_data {
        if let Some(pair) = dexscreener_data.pairs.as_ref().and_then(|p| p.first()) {
            parts.push("📈 <b>DexScreener Data</b>".to_string());
            if let Some(dex_id) = &pair.dex_id {
                parts.push(format!("<b>DEX:</b> {}", dex_id));
            }
            if let Some(pair_address) = &pair.pair_address {
                parts.push(format!("<b>Pair:</b> <code>{}</code>", pair_address));
            }
            if let Some(url) = &pair.url {
                parts.push(format!("<a href=\"{}\">View on DexScreener</a>", url));
            }
            if let (Some(base), Some(quote)) = (&pair.base_token, &pair.quote_token) {
                parts.push(format!("<b>Base:</b> {} ({}) - <code>{}</code>", base.name.as_deref().unwrap_or("N/A"), base.symbol.as_deref().unwrap_or("N/A"), base.address.as_deref().unwrap_or("N/A")));
                parts.push(format!("<b>Quote:</b> {} ({}) - <code>{}</code>", quote.name.as_deref().unwrap_or("N/A"), quote.symbol.as_deref().unwrap_or("N/A"), quote.address.as_deref().unwrap_or("N/A")));
            }

            parts.push(format!("🧢 <b>MC (dex):</b> ${:.0}", pair.market_cap.unwrap_or(0.0)));
            parts.push(format!("💎 <b>FDV (dex):</b> ${:.0}", pair.fdv.unwrap_or(0.0)));
            parts.push(format!("💧 <b>Liq (dex):</b> ${:.0}", pair.liquidity.as_ref().map_or(0.0, |l| l.usd.unwrap_or(0.0))));
            if let Some(liquidity) = &pair.liquidity {
                parts.push(format!("<b>Liq (base/quote):</b> {:.2} / {:.2}", liquidity.base.unwrap_or(0.0), liquidity.quote.unwrap_or(0.0)));
            }

            if let Some(price_native) = &pair.price_native {
                parts.push(format!("💰 <b>Price (native):</b> {}", price_native));
            }
            if let Some(volume) = &pair.volume {
                parts.push(format!("📊 <b>Volume (24h):</b> ${:.0}", volume.h24.unwrap_or(0.0)));
                parts.push(format!("<b>Volume (6h/1h/5m):</b> ${:.0} / ${:.0} / ${:.0}", volume.h6.unwrap_or(0.0), volume.h1.unwrap_or(0.0), volume.m5.unwrap_or(0.0)));
            }
            if let Some(price_change) = &pair.price_change {
                parts.push(format!("📉 <b>Price Change (24h/6h/1h/5m):</b> {:.2}% / {:.2}% / {:.2}% / {:.2}%", price_change.h24.unwrap_or(0.0), price_change.h6.unwrap_or(0.0), price_change.h1.unwrap_or(0.0), price_change.m5.unwrap_or(0.0)));
            }
            if let Some(created_at) = &pair.pair_created_at {
                parts.push(format!("<b>Created:</b> {}", chrono::DateTime::from_timestamp_millis(*created_at).unwrap().format("%Y-%m-%d %H:%M")));
            }
            if let Some(txns) = &pair.txns {
                if let (Some(h24), Some(h6), Some(h1), Some(m5)) = (&txns.h24, &txns.h6, &txns.h1, &txns.m5) {
                    parts.push("🔄 <b>Transactions</b>".to_string());
                    parts.push(format!("<b>24h:</b> {} buys / {} sells", h24.buys.unwrap_or(0), h24.sells.unwrap_or(0)));
                    parts.push(format!("<b>6h:</b> {} buys / {} sells", h6.buys.unwrap_or(0), h6.sells.unwrap_or(0)));
                    parts.push(format!("<b>1h:</b> {} buys / {} sells", h1.buys.unwrap_or(0), h1.sells.unwrap_or(0)));
                    parts.push(format!("<b>5m:</b> {} buys / {} sells", m5.buys.unwrap_or(0), m5.sells.unwrap_or(0)));
                }
            }
            if let Some(info) = &pair.info {
                if let Some(socials) = &info.socials {
                    let social_links: Vec<String> = socials.iter().filter_map(|s| s.handle.as_ref().map(|h| format!("<a href=\"{}\">{}</a>", h, s.platform.as_deref().unwrap_or("Social")))).collect();
                    if !social_links.is_empty() {
                        parts.push(format!("<b>Socials:</b> {}", social_links.join(" | ")));
                    }
                }
                if let Some(websites) = &info.websites {
                    let website_links: Vec<String> = websites.iter().filter_map(|w| w.url.as_ref().map(|u| format!("<a href=\"{}\">Website</a>", u))).collect();
                    if !website_links.is_empty() {
                        parts.push(format!("<b>Websites:</b> {}", website_links.join(" | ")));
                    }
                }
            }
            parts.push(String::new());
        }
    }

    let ath_market_cap = data.pump_fun_data.as_ref().and_then(|pf| pf.ath_market_cap).unwrap_or(0.0);
    let total_supply_pf = data.pump_fun_data.as_ref().and_then(|pf| pf.total_supply).unwrap_or(0);

    parts.push(format!("🧢 <b>MC (pf):</b> ${:.0}", market_cap));
    parts.push(format!("Market Cap (SOL): {:.2}", data.pump_fun_data.as_ref().and_then(|pf| pf.market_cap).unwrap_or(0.0)));
    parts.push(format!("🔥 <b>ATH (pf):</b> ${:.0}", ath_market_cap));
    parts.push(format!("📦 <b>Supply (pf):</b> {}", total_supply_pf));
    if fdv > 0.0 {
        parts.push(format!("💎 <b>FDV:</b> ${:.0}", fdv));
    }
    if liquidity_usd > 0.0 {
        parts.push(format!("💧 <b>Liq:</b> ${:.0}", liquidity_usd));
    }
    parts.push(String::new());

    // Timestamps (pf)
    if let Some(pf) = &data.pump_fun_data {
        parts.push("🗓️ <b>Timestamps (pf)</b>".to_string());
        if let Some(created_ts) = pf.created_timestamp {
            parts.push(format!("<b>Created:</b> {}", chrono::DateTime::from_timestamp_millis(created_ts).unwrap().format("%Y-%m-%d %H:%M")));
        }
        if let Some(last_trade_ts) = pf.last_trade_timestamp {
            parts.push(format!("<b>Last Trade:</b> {}", chrono::DateTime::from_timestamp_millis(last_trade_ts).unwrap().format("%Y-%m-%d %H:%M")));
        }
        if let Some(ath_ts) = pf.ath_market_cap_timestamp {
            parts.push(format!("<b>ATH Date:</b> {}", chrono::DateTime::from_timestamp_millis(ath_ts).unwrap().format("%Y-%m-%d %H:%M")));
        }
        if let Some(koth_ts) = pf.king_of_the_hill_timestamp {
            if koth_ts > 0 {
                parts.push(format!("<b>King of Hill:</b> {}", chrono::DateTime::from_timestamp_millis(koth_ts).unwrap().format("%Y-%m-%d %H:%M")));
            }
        }
        parts.push(String::new());
    }

    // Engagement (pf)
    if let Some(pf) = &data.pump_fun_data {
        parts.push("💬 <b>Engagement (pf)</b>".to_string());
        let replies = pf.reply_count.unwrap_or(0);
        let participants = pf.num_participants.unwrap_or(0);
        parts.push(format!("Replies: {} | Participants: {}", replies, participants));
        parts.push(String::new());
    }

    // Bonding Curve (pf)
    if let Some(pf) = &data.pump_fun_data {
        parts.push("🎢 <b>Bonding Curve (pf)</b>".to_string());
        let real_sol = pf.real_sol_reserves.unwrap_or(0.0) / 1e9;
        let virtual_sol = pf.virtual_sol_reserves.unwrap_or(0.0) / 1e9;
        let virtual_tokens = pf.virtual_token_reserves.unwrap_or(0.0);
        parts.push(format!("Real SOL: {:.2} | Virtual SOL: {:.2}", real_sol, virtual_sol));
        parts.push(format!("Virtual Tokens: {:.0}", virtual_tokens));
        let real_tokens = pf.real_token_reserves.unwrap_or(0.0);
        parts.push(format!("Real Tokens: {:.0}", real_tokens));
        if let Some(bonding_curve_addr) = &pf.bonding_curve {
            parts.push(format!("Address: <code>{}</code>", bonding_curve_addr));
        }
        if let Some(assoc_bonding_curve) = &pf.associated_bonding_curve {
            parts.push(format!("Assoc. Address: <code>{}</code>", assoc_bonding_curve));
        }
        parts.push(String::new());
    }

    // Status (pf)
    if let Some(pf) = &data.pump_fun_data {
        parts.push("🚦 <b>Status (pf)</b>".to_string());
        let live = if pf.is_currently_live.unwrap_or(false) { "🟢 Live" } else { "🔴 Not Live" };
    // Status (pf)
    if let Some(pf) = &data.pump_fun_data {
        parts.push("🚦 <b>Status (pf)</b>".to_string());
        let live = if pf.is_currently_live.unwrap_or(false) { "🟢 Live" } else { "🔴 Not Live" };
        let complete = if pf.complete.unwrap_or(false) { "✅ Complete" } else { "❌ Incomplete" };
        let banned = if pf.is_banned.unwrap_or(false) { "🚫 Banned" } else { "" };
        let nsfw = if pf.nsfw.unwrap_or(false) { "🔞 NSFW" } else { "" };
        let hidden = if pf.hidden.unwrap_or(false) { "| Hidden" } else { "" };
        let show_name = if pf.show_name.unwrap_or(false) { "| Show Name" } else { "" };
        let inverted = if pf.inverted.unwrap_or(false) { "| Inverted" } else { "" };
        let initialized = if pf.initialized.unwrap_or(false) { "| Initialized" } else { "" };
        parts.push(format!("{} | {} {} {} {} {} {} {}", live, complete, banned, nsfw, hidden, show_name, inverted, initialized));
        parts.push(String::new());
    }

    // Creator & Pools (pf)
    if let Some(pf) = &data.pump_fun_data {
        parts.push("🧑‍💻 <b>Creator & Pools (pf)</b>".to_string());
        if let Some(creator_addr) = &pf.creator {
            parts.push(format!("<b>Creator:</b> <code>{}</code>", creator_addr));
        }
        if let Some(raydium_pool) = &pf.raydium_pool {
            parts.push(format!("<b>Raydium Pool:</b> <code>{}</code>", raydium_pool));
        }
        if let Some(swap_pool) = &pf.pump_swap_pool {
            parts.push(format!("<b>Pump Swap Pool:</b> <code>{}</code>", swap_pool));
        }
        parts.push(String::new());
    }

    // Raw Financials (pf)
    if let Some(pf) = &data.pump_fun_data {
        parts.push("Raw Financials (pf)".to_string());
        parts.push(format!("Market Cap (SOL): {:.2}", pf.market_cap.unwrap_or(0.0)));
        parts.push(format!("Virtual Token Reserves: {:.0}", pf.virtual_token_reserves.unwrap_or(0.0)));
        parts.push(format!("Real Token Reserves: {:.0}", pf.real_token_reserves.unwrap_or(0.0)));
        parts.push(String::new());
    }

    // Asset Links (pf)
    if let Some(pf) = &data.pump_fun_data {
        parts.push("🔗 <b>Asset Links (pf)</b>".to_string());
        if let Some(uri) = &pf.image_uri { parts.push(format!("<a href=\"{}\">Image</a>", uri)); }
        if let Some(uri) = &pf.metadata_uri { parts.push(format!("<a href=\"{}\">Metadata</a>", uri)); }
        if let Some(uri) = &pf.metadata_uri { parts.push(format!("<a href=\"{}\">Metadata</a>", uri)); }
        if let Some(uri) = &pf.banner_uri { parts.push(format!("<a href=\"{}\">Banner</a>", uri)); }
        if let Some(uri) = &pf.thumbnail { parts.push(format!("<a href=\"{}\">Thumbnail</a>", uri)); }
        if let Some(uri) = &pf.thumbnail { parts.push(format!("<a href=\"{}\">Thumbnail</a>", uri)); }
        if let Some(uri) = &pf.video_uri { parts.push(format!("<a href=\"{}\">Video</a>", uri)); }
        parts.push(String::new());
    }

    // System Info (pf)
    if let Some(pf) = &data.pump_fun_data {
        parts.push("⚙️ <b>System Info (pf)</b>".to_string());
        if let Some(prog) = &pf.program { parts.push(format!("Program: {}", prog)); }
        if let Some(plat) = &pf.platform { parts.push(format!("Platform: {}", plat)); }
        if let Some(market) = &pf.market_id { parts.push(format!("Market ID: {}", market)); }
        if let Some(ts) = pf.last_reply { parts.push(format!("Last Reply: {}", chrono::DateTime::from_timestamp_millis(ts).unwrap().format("%Y-%m-%d %H:%M"))); }
        if let Some(ts) = pf.updated_at { parts.push(format!("Updated At: {}", chrono::DateTime::from_timestamp_millis(ts).unwrap().format("%Y-%m-%d %H:%M"))); }
        parts.push(String::new());
    }
    }

    // Socials
    parts.push("🌐 <b>Socials</b>".to_string());
    if !social_links.is_empty() {
        let social_parts: Vec<String> = social_links.iter().map(|(name, url)| format!("<a href=\"{}\">{}</a>", url.as_ref().unwrap_or(&"".to_string()), name)).collect();
        parts.push(social_parts.join(" | "));
    } else {
        parts.push("No social links found.".to_string());
    }
    parts.push(String::new());

    // Description
    if !description.is_empty() {
        parts.push(format!("📝 {}", html::escape(&description)));
        parts.push(String::new());
    }

    (parts.join("\n"), image_url)
}