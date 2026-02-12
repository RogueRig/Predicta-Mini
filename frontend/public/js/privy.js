/**
 * Predicta Mini - Privy Wallet Integration
 *
 * Handles wallet connection, Safe deployment, and token approvals
 * using Privy as the wallet provider.
 */
const WalletManager = {
    privyClient: null,
    user: null,
    walletAddress: null,
    safeAddress: null,
    isSetup: false,

    /**
     * Initialize the Privy client.
     */
    init() {
        // Privy will be initialized when the user clicks connect.
        // The SDK is loaded via CDN in index.html.
        this._updateUI();
    },

    /**
     * Connect wallet using Privy.
     */
    async connect() {
        try {
            Toast.show('Connecting wallet...', 'info');

            // Initialize Privy if needed
            if (!this.privyClient && window.PrivyJs) {
                this.privyClient = new window.PrivyJs.PrivyClient({
                    appId: APP_CONFIG.PRIVY_APP_ID,
                    config: {
                        appearance: {
                            theme: 'dark',
                            accentColor: '#6c5ce7',
                        },
                        embeddedWallets: {
                            createOnLogin: 'all-users',
                        },
                        supportedChains: [
                            { id: 137, name: 'Polygon' },
                        ],
                    },
                });
            }

            // For demo/development: use a simulated wallet flow
            // In production, replace with actual Privy login
            if (this.privyClient) {
                const authResult = await this.privyClient.login();
                this.user = authResult.user;
                const wallet = this.user.wallet;
                if (wallet) {
                    this.walletAddress = wallet.address;
                }
            } else {
                // Fallback: prompt for address if SDK not loaded
                const addr = prompt('Enter your Polygon wallet address:');
                if (!addr) return;
                this.walletAddress = addr;
            }

            Toast.show('Wallet connected!', 'success');
            this._updateUI();
            this._checkSetupStatus();

        } catch (err) {
            console.error('Wallet connection failed:', err);
            Toast.show('Failed to connect wallet', 'error');
        }
    },

    /**
     * Disconnect wallet.
     */
    async disconnect() {
        try {
            if (this.privyClient) {
                await this.privyClient.logout();
            }
            this.user = null;
            this.walletAddress = null;
            this.safeAddress = null;
            this.isSetup = false;
            this._updateUI();
            Toast.show('Wallet disconnected', 'info');
        } catch (err) {
            console.error('Disconnect failed:', err);
        }
    },

    /**
     * Check and update wallet setup status.
     */
    async _checkSetupStatus() {
        if (!this.walletAddress) return;

        // Step 1: Connected
        document.getElementById('step-connect').classList.add('step-complete');
        document.getElementById('step-connect-status').textContent = '●';

        try {
            // Check for existing Safe
            const result = await API.getSafeAddress(this.walletAddress);
            if (result && result.address) {
                this.safeAddress = result.address;
                document.getElementById('step-deploy').classList.add('step-complete');
                document.getElementById('step-deploy-status').textContent = '●';

                // Mark approvals as done (we assume if safe exists, approvals may be done)
                document.getElementById('step-approve').classList.add('step-complete');
                document.getElementById('step-approve-status').textContent = '●';
                this.isSetup = true;

                this._updateSetupButton('ready');
            } else {
                this._updateSetupButton('deploy');
            }
        } catch {
            this._updateSetupButton('deploy');
        }
    },

    /**
     * Deploy Safe wallet for gasless trading.
     */
    async deploySafe() {
        if (!this.walletAddress) {
            Toast.show('Connect wallet first', 'error');
            return;
        }

        try {
            Toast.show('Deploying Safe wallet (gasless)...', 'info');
            const result = await API.deploySafe(this.walletAddress);
            if (result.success) {
                this.safeAddress = result.deployment.address || result.deployment.safe;
                document.getElementById('step-deploy').classList.add('step-complete');
                document.getElementById('step-deploy-status').textContent = '●';
                Toast.show('Safe wallet deployed!', 'success');
                this._updateSetupButton('approve');
            }
        } catch (err) {
            Toast.show('Safe deployment failed: ' + err.message, 'error');
        }
    },

    /**
     * Approve all tokens for trading.
     */
    async approveTokens() {
        if (!this.safeAddress) {
            Toast.show('Deploy Safe wallet first', 'error');
            return;
        }

        try {
            Toast.show('Approving tokens for trading (gasless)...', 'info');
            const result = await API.approveTokens(this.safeAddress);
            if (result.success) {
                document.getElementById('step-approve').classList.add('step-complete');
                document.getElementById('step-approve-status').textContent = '●';
                this.isSetup = true;
                this._updateSetupButton('ready');
                Toast.show('Tokens approved! Ready to trade.', 'success');
            }
        } catch (err) {
            Toast.show('Token approval failed: ' + err.message, 'error');
        }
    },

    /**
     * Update setup button state.
     */
    _updateSetupButton(state) {
        const btn = document.getElementById('setup-action-btn');
        if (!btn) return;

        btn.disabled = false;
        switch (state) {
            case 'deploy':
                btn.textContent = 'Deploy Safe Wallet';
                btn.onclick = () => this.deploySafe();
                break;
            case 'approve':
                btn.textContent = 'Approve Tokens';
                btn.onclick = () => this.approveTokens();
                break;
            case 'ready':
                btn.textContent = 'Setup Complete';
                btn.disabled = true;
                btn.classList.remove('btn-primary');
                btn.classList.add('btn-ghost');
                document.getElementById('positions-section').classList.remove('hidden');
                break;
        }
    },

    /**
     * Update UI based on wallet state.
     */
    _updateUI() {
        const connectBtn = document.getElementById('connect-wallet-btn');
        const walletInfo = document.getElementById('wallet-info');
        const addressEl = document.getElementById('wallet-address');
        const placeOrderBtn = document.getElementById('place-order-btn');

        if (this.walletAddress) {
            connectBtn.classList.add('hidden');
            walletInfo.classList.remove('hidden');
            addressEl.textContent = this.walletAddress.slice(0, 6) + '...' + this.walletAddress.slice(-4);

            if (placeOrderBtn) {
                placeOrderBtn.disabled = false;
                placeOrderBtn.textContent = 'Place Order';
            }
        } else {
            connectBtn.classList.remove('hidden');
            walletInfo.classList.add('hidden');

            if (placeOrderBtn) {
                placeOrderBtn.disabled = true;
                placeOrderBtn.textContent = 'Connect Wallet to Trade';
            }
        }
    },

    /**
     * Get wallet credentials for trading.
     */
    getCredentials() {
        return {
            walletAddress: this.walletAddress,
            safeAddress: this.safeAddress,
            // In production, the private key would come from Privy's
            // embedded wallet export or server-side signing
            privateKey: null,
        };
    },
};
