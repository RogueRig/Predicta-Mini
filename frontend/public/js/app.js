/**
 * Predicta Mini - Main Application
 * Initializes all modules and handles navigation.
 */

// Toast notification utility
const Toast = {
    show(message, type = 'info', duration = 4000) {
        const container = document.getElementById('toast-container');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.textContent = message;
        container.appendChild(toast);

        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateX(20px)';
            toast.style.transition = '200ms ease';
            setTimeout(() => toast.remove(), 200);
        }, duration);
    },
};

// Application initialization
document.addEventListener('DOMContentLoaded', () => {
    // Initialize modules
    WalletManager.init();
    MarketBrowser.init();
    TradingUI.init();

    // Navigation
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const view = btn.dataset.view;
            switchView(view);
        });
    });

    // Back to markets button
    document.getElementById('back-to-markets').addEventListener('click', () => {
        MarketBrowser.backToMarkets();
    });

    // Connect wallet button
    document.getElementById('connect-wallet-btn').addEventListener('click', () => {
        WalletManager.connect();
    });

    // Disconnect button
    document.getElementById('disconnect-btn').addEventListener('click', () => {
        WalletManager.disconnect();
    });
});

/**
 * Switch between main views (markets, portfolio).
 */
function switchView(viewName) {
    // Update nav buttons
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.view === viewName);
    });

    // Hide all views
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));

    // Show selected view
    const viewId = `${viewName}-view`;
    const viewEl = document.getElementById(viewId);
    if (viewEl) {
        viewEl.classList.add('active');
    }

    // Load portfolio data when switching to portfolio
    if (viewName === 'portfolio' && WalletManager.isSetup) {
        TradingUI.loadOpenOrders();
        TradingUI.loadTradeHistory();
    }
}
