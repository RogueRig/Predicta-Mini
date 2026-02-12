/**
 * Predicta Mini - Trading Interface
 * Handles the trading modal, order placement, and order management.
 */
const TradingUI = {
    currentMarket: null,
    selectedSide: 'BUY',
    selectedOutcome: 'yes',
    orderType: 'market',

    /**
     * Initialize trading UI.
     */
    init() {
        this._bindModalEvents();
        this._bindTradeFormEvents();
    },

    /**
     * Open the trading modal for a market.
     */
    openTradeModal(market) {
        this.currentMarket = market;
        this.selectedSide = 'BUY';
        this.selectedOutcome = 'yes';
        this.orderType = 'market';

        // Populate modal
        document.getElementById('trade-market-question').textContent = market.question;
        document.getElementById('trade-yes-price').textContent =
            (market.yesPrice * 100).toFixed(1) + '%';
        document.getElementById('trade-no-price').textContent =
            (market.noPrice * 100).toFixed(1) + '%';

        // Reset form
        document.getElementById('trade-amount').value = '';
        document.getElementById('limit-price').value = '';
        this._updateSideButtons();
        this._updateTypeButtons();
        this._updateSummary();
        this._updatePlaceButton();

        // Show modal
        document.getElementById('trade-modal').classList.remove('hidden');
    },

    /**
     * Close the trading modal.
     */
    closeTradeModal() {
        document.getElementById('trade-modal').classList.add('hidden');
        this.currentMarket = null;
    },

    /**
     * Bind modal open/close events.
     */
    _bindModalEvents() {
        document.getElementById('close-trade-modal').addEventListener('click', () => {
            this.closeTradeModal();
        });

        document.querySelector('.modal-backdrop').addEventListener('click', () => {
            this.closeTradeModal();
        });

        // ESC key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') this.closeTradeModal();
        });
    },

    /**
     * Bind trade form events.
     */
    _bindTradeFormEvents() {
        // Side toggle
        document.querySelectorAll('.side-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                this.selectedSide = btn.dataset.side;
                this.selectedOutcome = btn.dataset.outcome;
                this._updateSideButtons();
                this._updateSummary();
            });
        });

        // Type toggle
        document.querySelectorAll('.type-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                this.orderType = btn.dataset.type;
                this._updateTypeButtons();
                this._updateSummary();
            });
        });

        // Amount input
        document.getElementById('trade-amount').addEventListener('input', () => {
            this._updateSummary();
        });

        // Limit price input
        document.getElementById('limit-price').addEventListener('input', () => {
            this._updateSummary();
        });

        // Place order button
        document.getElementById('place-order-btn').addEventListener('click', () => {
            this._placeOrder();
        });
    },

    /**
     * Update side button active states.
     */
    _updateSideButtons() {
        document.querySelectorAll('.side-btn').forEach(btn => {
            const isActive = btn.dataset.side === this.selectedSide &&
                             btn.dataset.outcome === this.selectedOutcome;
            btn.classList.toggle('active', isActive);
        });
    },

    /**
     * Update type button active states.
     */
    _updateTypeButtons() {
        document.querySelectorAll('.type-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.type === this.orderType);
        });

        const limitGroup = document.getElementById('limit-price-group');
        const amountLabel = document.getElementById('amount-label');

        if (this.orderType === 'limit') {
            limitGroup.classList.remove('hidden');
            amountLabel.textContent = 'Shares';
        } else {
            limitGroup.classList.add('hidden');
            amountLabel.textContent = 'Amount (USD)';
        }
    },

    /**
     * Update the order summary display.
     */
    _updateSummary() {
        if (!this.currentMarket) return;

        const amount = parseFloat(document.getElementById('trade-amount').value) || 0;
        const limitPrice = parseFloat(document.getElementById('limit-price').value) || 0;

        const price = this.selectedOutcome === 'yes'
            ? this.currentMarket.yesPrice
            : this.currentMarket.noPrice;

        let estShares = 0;
        let maxPayout = 0;

        if (this.orderType === 'market' && amount > 0) {
            estShares = amount / price;
            maxPayout = estShares; // Each share pays $1 if correct
        } else if (this.orderType === 'limit' && amount > 0 && limitPrice > 0) {
            estShares = amount;
            maxPayout = amount;
        }

        document.getElementById('est-shares').textContent =
            estShares > 0 ? estShares.toFixed(2) : '--';
        document.getElementById('max-payout').textContent =
            maxPayout > 0 ? '$' + maxPayout.toFixed(2) : '--';
    },

    /**
     * Update place order button state.
     */
    _updatePlaceButton() {
        const btn = document.getElementById('place-order-btn');
        if (WalletManager.walletAddress) {
            btn.disabled = false;
            btn.textContent = 'Place Order';
        } else {
            btn.disabled = true;
            btn.textContent = 'Connect Wallet to Trade';
        }
    },

    /**
     * Place the order.
     */
    async _placeOrder() {
        if (!WalletManager.walletAddress) {
            Toast.show('Connect your wallet first', 'error');
            return;
        }

        if (!WalletManager.isSetup) {
            Toast.show('Complete wallet setup first (Portfolio tab)', 'error');
            return;
        }

        const amount = parseFloat(document.getElementById('trade-amount').value);
        if (!amount || amount <= 0) {
            Toast.show('Enter a valid amount', 'error');
            return;
        }

        const tokenId = this.selectedOutcome === 'yes'
            ? this.currentMarket.tokenYes
            : this.currentMarket.tokenNo;

        if (!tokenId) {
            Toast.show('Token ID not available for this market', 'error');
            return;
        }

        const btn = document.getElementById('place-order-btn');
        btn.disabled = true;
        btn.textContent = 'Placing order...';

        try {
            const creds = WalletManager.getCredentials();
            let result;

            if (this.orderType === 'market') {
                result = await API.placeMarketOrder({
                    privateKey: creds.privateKey,
                    funder: creds.safeAddress,
                    tokenId: tokenId,
                    amount: amount,
                });
            } else {
                const limitPrice = parseFloat(document.getElementById('limit-price').value);
                if (!limitPrice || limitPrice <= 0 || limitPrice >= 1) {
                    Toast.show('Limit price must be between 0.01 and 0.99', 'error');
                    btn.disabled = false;
                    btn.textContent = 'Place Order';
                    return;
                }

                result = await API.placeLimitOrder({
                    privateKey: creds.privateKey,
                    funder: creds.safeAddress,
                    tokenId: tokenId,
                    price: limitPrice,
                    size: amount,
                    side: this.selectedSide,
                });
            }

            Toast.show('Order placed successfully!', 'success');
            this.closeTradeModal();

        } catch (err) {
            console.error('Order failed:', err);
            Toast.show('Order failed: ' + err.message, 'error');
        } finally {
            btn.disabled = false;
            btn.textContent = 'Place Order';
        }
    },

    /**
     * Load and display open orders in the portfolio.
     */
    async loadOpenOrders() {
        const creds = WalletManager.getCredentials();
        if (!creds.privateKey) return;

        try {
            const result = await API.getOpenOrders(creds.privateKey, creds.safeAddress);
            const container = document.getElementById('open-orders');

            if (!result.orders || result.orders.length === 0) {
                container.innerHTML = '<p class="empty-state">No open orders</p>';
                return;
            }

            container.innerHTML = result.orders.map(order => `
                <div class="order-item">
                    <div class="order-item-info">
                        <div class="order-item-market">${order.side} @ $${order.price}</div>
                        <div class="order-item-detail">Size: ${order.size} | Status: ${order.status}</div>
                    </div>
                    <button class="btn btn-red btn-sm"
                        onclick="TradingUI.cancelOrder('${order.id}')">Cancel</button>
                </div>
            `).join('');

        } catch (err) {
            console.error('Failed to load orders:', err);
        }
    },

    /**
     * Cancel an order.
     */
    async cancelOrder(orderId) {
        try {
            const creds = WalletManager.getCredentials();
            await API.cancelOrder(orderId, creds.privateKey, creds.safeAddress);
            Toast.show('Order cancelled', 'success');
            this.loadOpenOrders();
        } catch (err) {
            Toast.show('Cancel failed: ' + err.message, 'error');
        }
    },

    /**
     * Load and display trade history.
     */
    async loadTradeHistory() {
        const creds = WalletManager.getCredentials();
        if (!creds.privateKey) return;

        try {
            const result = await API.getTradeHistory(creds.privateKey, creds.safeAddress);
            const container = document.getElementById('trade-history');

            if (!result.trades || result.trades.length === 0) {
                container.innerHTML = '<p class="empty-state">No trades yet</p>';
                return;
            }

            container.innerHTML = result.trades.map(trade => `
                <div class="order-item">
                    <div class="order-item-info">
                        <div class="order-item-market">${trade.side} ${trade.size} @ $${trade.price}</div>
                        <div class="order-item-detail">${new Date(trade.timestamp).toLocaleString()}</div>
                    </div>
                </div>
            `).join('');

        } catch (err) {
            console.error('Failed to load trades:', err);
        }
    },
};
