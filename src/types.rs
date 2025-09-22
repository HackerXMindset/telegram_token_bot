use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TokenData {
    pub mint_address: String,
    pub metadata: Option<MetadataResponse>,
    pub dexscreener_data: Option<DexScreenerData>,
    pub holders: Option<HoldersData>,
    pub supply_info: Option<SupplyInfo>,
    pub creator_info: Option<CreatorInfo>,
    pub pump_fun_data: Option<PumpFunData>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct MetadataResponse {
    #[serde(rename = "onChainMetadata")]
    pub on_chain_metadata: Option<OnChainMetadata>,
    #[serde(rename = "offChainMetadata")]
    pub off_chain_metadata: Option<OffChainMetadata>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OnChainMetadata {
    pub metadata: Option<TokenMetadata>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TokenMetadata {
    pub data: TokenMetadataData,
    #[serde(rename = "isMutable")]
    pub is_mutable: Option<bool>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TokenMetadataData {
    pub name: Option<String>,
    pub symbol: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OffChainMetadata {
    pub metadata: Option<OffChainTokenData>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct OffChainTokenData {
    pub name: Option<String>,
    pub symbol: Option<String>,
    pub description: Option<String>,
    pub image: Option<String>,
    pub twitter: Option<String>,
    pub telegram: Option<String>,
    pub website: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DexScreenerData {
    pub pairs: Option<Vec<TokenPair>>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TokenPair {
    #[serde(rename = "chainId")]
    pub chain_id: Option<String>,
    #[serde(rename = "dexId")]
    pub dex_id: Option<String>,
    pub url: Option<String>,
    #[serde(rename = "pairAddress")]
    pub pair_address: Option<String>,
    #[serde(rename = "baseToken")]
    pub base_token: Option<BaseToken>,
    #[serde(rename = "quoteToken")]
    pub quote_token: Option<QuoteToken>,
    #[serde(rename = "priceNative")]
    pub price_native: Option<String>,
    #[serde(rename = "priceUsd")]
    pub price_usd: Option<String>,
    pub txns: Option<Transactions>,
    pub volume: Option<Volume>,
    #[serde(rename = "priceChange")]
    pub price_change: Option<PriceChange>,
    pub liquidity: Option<Liquidity>,
    pub fdv: Option<f64>,
    #[serde(rename = "marketCap")]
    pub market_cap: Option<f64>,
    #[serde(rename = "pairCreatedAt")]
    pub pair_created_at: Option<i64>,
    pub info: Option<Info>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BaseToken {
    pub address: Option<String>,
    pub name: Option<String>,
    pub symbol: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct QuoteToken {
    pub address: Option<String>,
    pub name: Option<String>,
    pub symbol: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Transactions {
    pub m5: Option<TxnData>,
    pub h1: Option<TxnData>,
    pub h6: Option<TxnData>,
    pub h24: Option<TxnData>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TxnData {
    pub buys: Option<i64>,
    pub sells: Option<i64>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Volume {
    pub h24: Option<f64>,
    pub h6: Option<f64>,
    pub h1: Option<f64>,
    pub m5: Option<f64>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PriceChange {
    pub m5: Option<f64>,
    pub h1: Option<f64>,
    pub h6: Option<f64>,
    pub h24: Option<f64>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Liquidity {
    pub usd: Option<f64>,
    pub base: Option<f64>,
    pub quote: Option<f64>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Info {
    #[serde(rename = "imageUrl")]
    pub image_url: Option<String>,
    pub websites: Option<Vec<Website>>,
    pub socials: Option<Vec<Social>>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Website {
    pub url: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Social {
    pub platform: Option<String>,
    pub handle: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HoldersData {
    pub result: Option<HoldersResult>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HoldersResult {
    pub value: Option<Vec<TokenHolder>>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TokenHolder {
    pub address: Option<String>,
    #[serde(rename = "uiAmount")]
    pub ui_amount: Option<f64>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SupplyInfo {
    pub result: Option<SupplyResult>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SupplyResult {
    pub value: Option<SupplyValue>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SupplyValue {
    #[serde(rename = "uiAmount")]
    pub ui_amount: Option<f64>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CreatorInfo {
    pub address: String,
    pub balance: Option<f64>,
    pub sol_balance: Option<f64>,
}



#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct PumpFunData {
    pub mint: Option<String>,
    pub name: Option<String>,
    pub symbol: Option<String>,
    pub description: Option<String>,
    pub image_uri: Option<String>,
    pub metadata_uri: Option<String>,
    pub twitter: Option<String>,
    pub telegram: Option<String>,
    pub website: Option<String>,
    pub bonding_curve: Option<String>,
    pub associated_bonding_curve: Option<String>,
    pub creator: Option<String>,
    pub created_timestamp: Option<i64>,
    pub last_trade_timestamp: Option<i64>,
    pub ath_market_cap_timestamp: Option<i64>,
    pub king_of_the_hill_timestamp: Option<i64>,
    pub total_supply: Option<u64>,
    pub market_cap: Option<f64>,
    pub usd_market_cap: Option<f64>,
    pub ath_market_cap: Option<f64>,
    pub real_sol_reserves: Option<f64>,
    pub virtual_sol_reserves: Option<f64>,
    pub virtual_token_reserves: Option<f64>,
    pub real_token_reserves: Option<f64>,
    pub reply_count: Option<u64>,
    pub num_participants: Option<u64>,
    pub is_currently_live: Option<bool>,
    pub complete: Option<bool>,
    pub raydium_pool: Option<String>,
    pub pump_swap_pool: Option<String>,
    pub hidden: Option<bool>,
    pub show_name: Option<bool>,
    pub nsfw: Option<bool>,
    pub inverted: Option<bool>,
    pub is_banned: Option<bool>,
    pub initialized: Option<bool>,
    pub hide_banner: Option<bool>,
    pub livestream_ban_expiry: Option<i64>,
    pub livestream_downrank_score: Option<f64>,
    pub downrank_score: Option<f64>,
    pub program: Option<String>,
    pub platform: Option<String>,
    pub market_id: Option<String>,
    pub updated_at: Option<i64>,
    pub last_reply: Option<i64>,
    pub thumbnail_updated_at: Option<i64>,
    pub banner_uri: Option<String>,
    pub thumbnail: Option<String>,
    pub video_uri: Option<String>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ApiError {
    pub error: String,
}