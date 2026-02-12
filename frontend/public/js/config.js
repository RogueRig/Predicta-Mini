/**
 * Predicta Mini - Configuration
 */
const APP_CONFIG = {
    // API base URL - points to Flask backend
    API_BASE: window.location.origin + '/api',

    // Privy App ID (set via Firebase environment or directly)
    PRIVY_APP_ID: 'cmkhyc6vd026fjv0d5q4xmkqm',

    // Polymarket chain
    CHAIN_ID: 137, // Polygon mainnet

    // Builder attribution key
    BUILDER_KEY_ID: '019b99f0-0f93-7753-8dc3-d913cf44dcd4',

    // Pagination
    PAGE_SIZE: 20,

    // Polygon contract addresses
    CONTRACTS: {
        USDCE: '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174',
        CTF: '0x4d97dcd97ec945f40cf65f87097ace5ea0476045',
        CTF_EXCHANGE: '0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E',
        NEG_RISK_CTF_EXCHANGE: '0xC5d563A36AE78145C45a50134d48A1215220f80a',
        NEG_RISK_ADAPTER: '0xd91E80cF2E7be2e162c6513ceD06f1dD0dA35296',
    },
};
