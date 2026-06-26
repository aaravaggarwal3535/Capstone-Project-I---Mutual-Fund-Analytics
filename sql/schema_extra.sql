-- Aggregate Table: AUM by Fund House
CREATE TABLE IF NOT EXISTS aum_by_fund_house (
    date DATE,
    fund_house TEXT,
    aum_lakh_crore REAL,
    aum_crore REAL,
    num_schemes INTEGER
);

-- Aggregate Table: Monthly SIP Inflows
CREATE TABLE IF NOT EXISTS monthly_sip_inflows (
    month DATE,
    sip_inflow_crore REAL,
    active_sip_accounts_crore REAL,
    new_sip_accounts_lakh REAL,
    sip_aum_lakh_crore REAL,
    yoy_growth_pct REAL
);

-- Aggregate Table: Category Inflows
CREATE TABLE IF NOT EXISTS category_inflows (
    month DATE,
    category TEXT,
    net_inflow_cr REAL
);

-- Aggregate Table: Industry Folio Count
CREATE TABLE IF NOT EXISTS industry_folio_count (
    month DATE,
    total_folios_crore REAL,
    equity_folios_crore REAL,
    debt_folios_crore REAL,
    hybrid_folios_crore REAL,
    others_folios_crore REAL
);