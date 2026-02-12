/**
 * Predicta Mini - Market Browser
 * Handles market listing, filtering, search, and event detail views.
 */
const MarketBrowser = {
    currentPage: 0,
    currentFilters: {
        sort_by: 'volume',
        order: 'desc',
        search: '',
        min_volume: 0,
        min_liquidity: 0,
        active: true,
        closed: false,
    },
    searchTimeout: null,

    /**
     * Initialize market browser and load markets.
     */
    init() {
        this._bindFilterEvents();
        this.loadMarkets();
    },

    /**
     * Bind filter/search UI events.
     */
    _bindFilterEvents() {
        // Search with debounce
        const searchInput = document.getElementById('search-input');
        searchInput.addEventListener('input', () => {
            clearTimeout(this.searchTimeout);
            this.searchTimeout = setTimeout(() => {
                this.currentFilters.search = searchInput.value.trim();
                this.currentPage = 0;
                this.loadMarkets();
            }, 350);
        });

        // Sort
        document.getElementById('sort-select').addEventListener('change', (e) => {
            this.currentFilters.sort_by = e.target.value;
            this.currentPage = 0;
            this.loadMarkets();
        });

        // Min volume
        document.getElementById('min-volume-select').addEventListener('change', (e) => {
            this.currentFilters.min_volume = parseFloat(e.target.value);
            this.currentPage = 0;
            this.loadMarkets();
        });

        // Min liquidity
        document.getElementById('min-liquidity-select').addEventListener('change', (e) => {
            this.currentFilters.min_liquidity = parseFloat(e.target.value);
            this.currentPage = 0;
            this.loadMarkets();
        });

        // Show closed
        document.getElementById('show-closed').addEventListener('change', (e) => {
            this.currentFilters.closed = e.target.checked;
            this.currentPage = 0;
            this.loadMarkets();
        });

        // Pagination
        document.getElementById('prev-page').addEventListener('click', () => {
            if (this.currentPage > 0) {
                this.currentPage--;
                this.loadMarkets();
            }
        });

        document.getElementById('next-page').addEventListener('click', () => {
            this.currentPage++;
            this.loadMarkets();
        });
    },

    /**
     * Load and render markets.
     */
    async loadMarkets() {
        const grid = document.getElementById('markets-grid');
        grid.innerHTML = '<div class="loading-spinner">Loading markets...</div>';

        try {
            const result = await API.getMarkets({
                ...this.currentFilters,
                limit: APP_CONFIG.PAGE_SIZE,
                offset: this.currentPage * APP_CONFIG.PAGE_SIZE,
            });

            this._renderMarkets(result.events || []);
            this._updatePagination(result.count || 0);

        } catch (err) {
            console.error('Failed to load markets:', err);
            grid.innerHTML = '<div class="empty-state">Failed to load markets. Check backend connection.</div>';
        }
    },

    /**
     * Render market cards.
     */
    _renderMarkets(events) {
        const grid = document.getElementById('markets-grid');

        if (!events.length) {
            grid.innerHTML = '<div class="empty-state">No crypto markets found matching your filters.</div>';
            return;
        }

        grid.innerHTML = events.map(event => this._renderMarketCard(event)).join('');

        // Bind click events
        grid.querySelectorAll('.market-card').forEach(card => {
            card.addEventListener('click', () => {
                const eventId = card.dataset.eventId;
                this.showEventDetail(eventId);
            });
        });
    },

    /**
     * Render a single market card.
     */
    _renderMarketCard(event) {
        const outcomes = (event.markets_summary || []).slice(0, 3);

        return `
            <div class="market-card" data-event-id="${event.id}">
                <div class="market-card-header">
                    ${event.image
                        ? `<img src="${event.image}" alt="" class="market-card-image" onerror="this.style.display='none'">`
                        : '<div class="market-card-image"></div>'
                    }
                    <div class="market-card-title">${this._escapeHtml(event.title)}</div>
                </div>
                <div class="market-card-outcomes">
                    ${outcomes.map(m => `
                        <div class="outcome-row">
                            <span class="outcome-question">${this._escapeHtml(m.question)}</span>
                            <div class="outcome-prices">
                                <span class="outcome-yes">${this._formatPercent(m.outcome_yes)}</span>
                                <span class="outcome-no">${this._formatPercent(m.outcome_no)}</span>
                            </div>
                        </div>
                    `).join('')}
                </div>
                <div class="market-card-footer">
                    <span class="market-stat">Vol: <strong>${this._formatCurrency(event.total_volume)}</strong></span>
                    <span class="market-stat">Liq: <strong>${this._formatCurrency(event.total_liquidity)}</strong></span>
                    ${event.market_count > 1 ? `<span class="market-tag">${event.market_count} markets</span>` : ''}
                </div>
            </div>
        `;
    },

    /**
     * Show event detail with trading options.
     */
    async showEventDetail(eventId) {
        // Switch views
        document.getElementById('markets-view').classList.remove('active');
        document.getElementById('event-view').classList.add('active');

        const container = document.getElementById('event-detail');
        container.innerHTML = '<div class="loading-spinner">Loading event...</div>';

        try {
            const event = await API.getEventDetail(eventId);
            container.innerHTML = this._renderEventDetail(event);
            this._bindTradeButtons();
        } catch (err) {
            console.error('Failed to load event:', err);
            container.innerHTML = '<div class="empty-state">Failed to load event details.</div>';
        }
    },

    /**
     * Render event detail view.
     */
    _renderEventDetail(event) {
        const markets = event.markets || [];

        return `
            <div class="event-header">
                ${event.image
                    ? `<img src="${event.image}" alt="" class="event-image" onerror="this.style.display='none'">`
                    : ''
                }
                <div>
                    <h1 class="event-title">${this._escapeHtml(event.title)}</h1>
                    ${event.description ? `<p class="event-description">${this._escapeHtml(event.description)}</p>` : ''}
                </div>
            </div>

            <div class="event-stats">
                <div class="event-stat">
                    <div class="event-stat-value">${this._formatCurrency(event.total_volume)}</div>
                    <div class="event-stat-label">Total Volume</div>
                </div>
                <div class="event-stat">
                    <div class="event-stat-value">${this._formatCurrency(event.total_liquidity)}</div>
                    <div class="event-stat-label">Liquidity</div>
                </div>
                <div class="event-stat">
                    <div class="event-stat-value">${markets.length}</div>
                    <div class="event-stat-label">Markets</div>
                </div>
                ${event.end_date ? `
                <div class="event-stat">
                    <div class="event-stat-value">${new Date(event.end_date).toLocaleDateString()}</div>
                    <div class="event-stat-label">End Date</div>
                </div>` : ''}
            </div>

            <div class="market-list">
                ${markets.map(market => this._renderMarketItem(market)).join('')}
            </div>
        `;
    },

    /**
     * Render a single market item in the event detail.
     */
    _renderMarketItem(market) {
        const yesPrice = (market.outcome_yes_price * 100).toFixed(1);
        const noPrice = (market.outcome_no_price * 100).toFixed(1);

        return `
            <div class="market-item" data-market='${JSON.stringify(market).replace(/'/g, "&apos;")}'>
                <div class="market-item-info">
                    <div class="market-item-question">${this._escapeHtml(market.question)}</div>
                    <div class="market-item-meta">
                        Vol: ${this._formatCurrency(market.volume)} | Liq: ${this._formatCurrency(market.liquidity)}
                        ${market.end_date ? ` | Ends: ${new Date(market.end_date).toLocaleDateString()}` : ''}
                    </div>
                </div>
                <div class="market-item-prices">
                    <span class="price-pill yes">Yes ${yesPrice}%</span>
                    <span class="price-pill no">No ${noPrice}%</span>
                </div>
                <div class="market-item-actions">
                    <button class="trade-btn buy" data-action="trade"
                        data-token="${market.token_yes}"
                        data-question="${this._escapeHtml(market.question)}"
                        data-yes-price="${market.outcome_yes_price}"
                        data-no-price="${market.outcome_no_price}"
                        data-token-yes="${market.token_yes}"
                        data-token-no="${market.token_no}">
                        Trade
                    </button>
                </div>
            </div>
        `;
    },

    /**
     * Bind trade buttons in event detail.
     */
    _bindTradeButtons() {
        document.querySelectorAll('.trade-btn[data-action="trade"]').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                TradingUI.openTradeModal({
                    question: btn.dataset.question,
                    yesPrice: parseFloat(btn.dataset.yesPrice),
                    noPrice: parseFloat(btn.dataset.noPrice),
                    tokenYes: btn.dataset.tokenYes,
                    tokenNo: btn.dataset.tokenNo,
                });
            });
        });
    },

    /**
     * Go back to markets list.
     */
    backToMarkets() {
        document.getElementById('event-view').classList.remove('active');
        document.getElementById('markets-view').classList.add('active');
    },

    /**
     * Update pagination controls.
     */
    _updatePagination(count) {
        const prevBtn = document.getElementById('prev-page');
        const nextBtn = document.getElementById('next-page');
        const pageInfo = document.getElementById('page-info');

        prevBtn.disabled = this.currentPage === 0;
        nextBtn.disabled = count < APP_CONFIG.PAGE_SIZE;
        pageInfo.textContent = `Page ${this.currentPage + 1}`;
    },

    // --- Utility methods ---

    _formatCurrency(value) {
        if (!value && value !== 0) return '$0';
        if (value >= 1000000) return `$${(value / 1000000).toFixed(1)}M`;
        if (value >= 1000) return `$${(value / 1000).toFixed(1)}K`;
        return `$${parseFloat(value).toFixed(0)}`;
    },

    _formatPercent(value) {
        return (parseFloat(value) * 100).toFixed(0) + '%';
    },

    _escapeHtml(str) {
        if (!str) return '';
        const div = document.createElement('div');
        div.textContent = str;
        return div.innerHTML;
    },
};
