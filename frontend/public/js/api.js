/**
 * Predicta Mini - API Client
 * Communicates with the Flask backend.
 */
const API = {
    /**
     * Fetch crypto markets with filters.
     */
    async getMarkets(params = {}) {
        const query = new URLSearchParams({
            limit: params.limit || APP_CONFIG.PAGE_SIZE,
            offset: params.offset || 0,
            sort_by: params.sort_by || 'volume',
            order: params.order || 'desc',
            search: params.search || '',
            min_volume: params.min_volume || 0,
            min_liquidity: params.min_liquidity || 0,
            active: params.active !== undefined ? params.active : true,
            closed: params.closed !== undefined ? params.closed : false,
        });
        const resp = await fetch(`${APP_CONFIG.API_BASE}/markets/?${query}`);
        if (!resp.ok) throw new Error('Failed to fetch markets');
        return resp.json();
    },

    /**
     * Search markets by keyword.
     */
    async searchMarkets(query, limit = 20) {
        const params = new URLSearchParams({ q: query, limit });
        const resp = await fetch(`${APP_CONFIG.API_BASE}/markets/search?${params}`);
        if (!resp.ok) throw new Error('Search failed');
        return resp.json();
    },

    /**
     * Get event details with all markets.
     */
    async getEventDetail(eventId) {
        const resp = await fetch(`${APP_CONFIG.API_BASE}/markets/event/${eventId}`);
        if (!resp.ok) throw new Error('Failed to fetch event');
        return resp.json();
    },

    /**
     * Get orderbook for a token.
     */
    async getOrderbook(tokenId) {
        const resp = await fetch(`${APP_CONFIG.API_BASE}/markets/orderbook/${tokenId}`);
        if (!resp.ok) throw new Error('Failed to fetch orderbook');
        return resp.json();
    },

    /**
     * Get price for a token.
     */
    async getPrice(tokenId) {
        const resp = await fetch(`${APP_CONFIG.API_BASE}/trading/price/${tokenId}`);
        if (!resp.ok) throw new Error('Failed to fetch price');
        return resp.json();
    },

    /**
     * Place a limit order.
     */
    async placeLimitOrder({ privateKey, funder, tokenId, price, size, side, orderType }) {
        const resp = await fetch(`${APP_CONFIG.API_BASE}/trading/order/limit`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                private_key: privateKey,
                funder: funder,
                token_id: tokenId,
                price: price,
                size: size,
                side: side,
                order_type: orderType || 'GTC',
            }),
        });
        if (!resp.ok) {
            const err = await resp.json();
            throw new Error(err.error || 'Order failed');
        }
        return resp.json();
    },

    /**
     * Place a market order.
     */
    async placeMarketOrder({ privateKey, funder, tokenId, amount }) {
        const resp = await fetch(`${APP_CONFIG.API_BASE}/trading/order/market`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                private_key: privateKey,
                funder: funder,
                token_id: tokenId,
                amount: amount,
            }),
        });
        if (!resp.ok) {
            const err = await resp.json();
            throw new Error(err.error || 'Order failed');
        }
        return resp.json();
    },

    /**
     * Cancel an order.
     */
    async cancelOrder(orderId, privateKey, funder) {
        const resp = await fetch(`${APP_CONFIG.API_BASE}/trading/order/${orderId}`, {
            method: 'DELETE',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ private_key: privateKey, funder: funder }),
        });
        if (!resp.ok) throw new Error('Cancel failed');
        return resp.json();
    },

    /**
     * Get open orders.
     */
    async getOpenOrders(privateKey, funder) {
        const resp = await fetch(`${APP_CONFIG.API_BASE}/trading/orders`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ private_key: privateKey, funder: funder }),
        });
        if (!resp.ok) throw new Error('Failed to fetch orders');
        return resp.json();
    },

    /**
     * Get trade history.
     */
    async getTradeHistory(privateKey, funder) {
        const resp = await fetch(`${APP_CONFIG.API_BASE}/trading/trades`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ private_key: privateKey, funder: funder }),
        });
        if (!resp.ok) throw new Error('Failed to fetch trades');
        return resp.json();
    },

    /**
     * Get predicted Safe address.
     */
    async getSafeAddress(ownerAddress) {
        const resp = await fetch(`${APP_CONFIG.API_BASE}/wallet/safe/address`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ owner_address: ownerAddress }),
        });
        if (!resp.ok) throw new Error('Failed to get safe address');
        return resp.json();
    },

    /**
     * Deploy a Safe wallet.
     */
    async deploySafe(ownerAddress) {
        const resp = await fetch(`${APP_CONFIG.API_BASE}/wallet/safe/deploy`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ owner_address: ownerAddress }),
        });
        if (!resp.ok) throw new Error('Safe deployment failed');
        return resp.json();
    },

    /**
     * Approve all tokens for trading.
     */
    async approveTokens(safeAddress) {
        const resp = await fetch(`${APP_CONFIG.API_BASE}/wallet/safe/approve`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ safe_address: safeAddress }),
        });
        if (!resp.ok) throw new Error('Token approval failed');
        return resp.json();
    },

    /**
     * Check transaction status.
     */
    async getTransactionStatus(txId) {
        const resp = await fetch(`${APP_CONFIG.API_BASE}/wallet/transaction/${txId}`);
        if (!resp.ok) throw new Error('Failed to check transaction');
        return resp.json();
    },
};
