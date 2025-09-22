use crate::types::*;
use anyhow::{Result, anyhow};
use reqwest::Client;
use serde_json::json;
use std::env;
use std::time::Duration;
use tokio::time::timeout;

pub struct ApiClient {
    client: Client,
    api_key: String,
}

impl ApiClient {
    pub async fn new(api_key: String) -> Result<Self> {
        let client = Client::builder()
            .pool_max_idle_per_host(30)
            .pool_idle_timeout(Duration::from_secs(60))
            .timeout(Duration::from_secs(5))
            .build()?;

        Ok(Self {
            client,
            api_key,
        })
    }

    pub async fn analyze_token(&self, mint_address: &str) -> Result<TokenData> {
        let (
            metadata_result,
            dexscreener_result,
            holders_result,
            supply_result,
            pump_fun_result,
            jupiter_result,
            dexscreener_orders_result,
        ) = tokio::join!(
            self.query_metadata_v1(mint_address),
            self.get_dexscreener_data(mint_address),
            self.get_token_largest_accounts(mint_address),
            self.get_token_supply_info(mint_address),
            self.get_pump_fun_data(mint_address),
            self.fetch_jupiter_token_data(mint_address),
            self.get_dexscreener_orders_data("solana", mint_address),
        );

        let token_data = TokenData {
            mint_address: mint_address.to_string(),
            metadata: metadata_result.ok(),
            dexscreener_data: dexscreener_result.ok(),
            holders: holders_result.ok(),
            supply_info: supply_result.ok(),
            creator_info: None,
            pump_fun_data: pump_fun_result.ok(),
            jupiter_data: jupiter_result.ok(),
            dexscreener_orders_data: dexscreener_orders_result.ok(),
        };

        Ok(token_data)
    }

    async fn query_metadata_v1(&self, mint_address: &str) -> Result<MetadataResponse> {
        let url = format!("https://api.helius.xyz/v0/token-metadata?api-key={}", self.api_key);
        let payload = json!({
            "mintAccounts": [mint_address],
            "includeOffChain": true,
            "disableCache": false
        });
        let response = timeout(
            Duration::from_secs(3),
            self.client.post(&url).json(&payload).send()
        ).await??;
        let data: Vec<MetadataResponse> = response.json().await?;
        data.into_iter().next().ok_or_else(|| anyhow!("No metadata found"))
    }

    async fn get_token_largest_accounts(&self, mint_address: &str) -> Result<HoldersData> {
        let url = format!("https://mainnet.helius-rpc.com/?api-key={}", self.api_key);
        let payload = json!({
            "jsonrpc": "2.0",
            "id": "1",
            "method": "getTokenLargestAccounts",
            "params": [mint_address]
        });
        let response = timeout(
            Duration::from_secs(3),
            self.client.post(&url).json(&payload).send()
        ).await??;
        let data: HoldersData = response.json().await?;
        Ok(data)
    }

    async fn get_token_supply_info(&self, mint_address: &str) -> Result<SupplyInfo> {
        let url = format!("https://mainnet.helius-rpc.com/?api-key={}", self.api_key);
        let payload = json!({
            "jsonrpc": "2.0",
            "id": "1",
            "method": "getTokenSupply",
            "params": [mint_address]
        });
        let response = timeout(
            Duration::from_secs(3),
            self.client.post(&url).json(&payload).send()
        ).await??;
        let data: SupplyInfo = response.json().await?;
        Ok(data)
    }

    async fn get_dexscreener_data(&self, mint_address: &str) -> Result<DexScreenerData> {
        let url = format!("https://api.dexscreener.com/latest/dex/tokens/{}", mint_address);
        let response = timeout(
            Duration::from_secs(3),
            self.client.get(&url).send()
        ).await??;
        let data: DexScreenerData = response.json().await?;
        Ok(data)
    }

    async fn get_pump_fun_data(&self, mint_address: &str) -> Result<PumpFunData> {
        let url = format!("https://frontend-api-v3.pump.fun/coins/{}?sync=true", mint_address);
        let jwt = env::var("PUMP_FUN_JWT").unwrap_or_default();
        let response = timeout(
            Duration::from_secs(5),
            self.client.get(&url).bearer_auth(jwt).send()
        ).await??;
        if response.status() == 404 {
            return Err(anyhow!("Token not found on pump.fun"));
        }
        let data: PumpFunData = response.json().await?;
        Ok(data)
    }

    async fn fetch_jupiter_token_data(&self, mint_address: &str) -> Result<JupiterTokenData> {
        let url = format!("https://lite-api.jup.ag/tokens/v2/search?query={}", mint_address);
        let response = timeout(
            Duration::from_secs(5),
            self.client.get(&url).send()
        ).await??;

        if response.status().is_client_error() || response.status().is_server_error() {
            if response.status() == reqwest::StatusCode::NOT_FOUND {
                return Err(anyhow!("Token not found on Jupiter (404)"));
            }
            return Err(anyhow!("Jupiter API returned an error: {}", response.status()));
        }
        let data: Vec<JupiterTokenData> = response.json().await?;
        data.into_iter().next().ok_or_else(|| anyhow!("No Jupiter data found"))
    }

    async fn get_dexscreener_orders_data(&self, chain_id: &str, token_address: &str) -> Result<Vec<DexScreenerOrder>> {
        let url = format!("https://api.dexscreener.com/orders/v1/{}/{}", chain_id, token_address);
        let response = timeout(
            Duration::from_secs(5),
            self.client.get(&url).send()
        ).await??;

        if response.status().is_client_error() || response.status().is_server_error() {
            if response.status() == reqwest::StatusCode::NOT_FOUND {
                return Err(anyhow!("DexScreener Orders: Token not found (404)"));
            }
            return Err(anyhow!("DexScreener Orders API returned an error: {}", response.status()));
        }

        let data: Vec<DexScreenerOrder> = response.json().await?;
        Ok(data)
    }
}
