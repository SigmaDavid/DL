"""Aramark config block for sigma-company-dashboard-v2.

Append this to scripts/company.py in a fresh clone of
github.com/cmiller-coder/millersigma, then run:
    cd skills/sigma-company-dashboard-v2/scripts
    COMPANY=aramark python3 build_sofi.py create
"""

# ---------------------------------------------------------------------------
# Aramark — food & facilities services, post-Vestis-spin (FY calibrated to the
# continuing food & support services business, ~$18-19B managed revenue).
#
# Aramark is NOT a spread business the way a bank is, but it IS a real
# cost-of-services business (food + labor + operating cost are real COGS), so
# the generator's income-minus-cost formula genuinely computes Aramark's margin
# -- see HANDOFF.md sec 8. Modelled the fee-only way (funding_rate = 0,
# yield_rate = the true AOI margin) so "Net Revenue" (the spread) reads as
# adjusted operating income and the volume KPI reads as managed revenue:
#
#   products      -> food & facilities sectors (5 US sectors + International)
#   bal_base      -> annual managed revenue by sector, $MM (the wow number)
#   yield_rate    -> adjusted operating income (AOI) margin on that revenue
#   funding_rate  -> 0 (cost of services is already netted into the AOI margin)
#   fee_base      -> management & incentive fees layered on top, $MM MONTHLY
#   balance_type  -> contract structure: P&L vs Client-interest (management fee)
#   delinq        -> share of accounts running below plan (the quality signal)
#   units_base    -> client accounts (institutional contracts), the count metric
#
# The scenario modeler needs no change: a "rate shock" becomes a food & labor
# cost shock against the same editable driver grid.
# ---------------------------------------------------------------------------
ARAMARK = {
    "key": "aramark",
    "name": "Aramark",
    "title": "Food & Facilities Command Center",
    "domain": "food & facilities services",
    "unit_noun": "client account",
    "volume_noun": "managed revenue",
    "logo_domain": "aramark.com",
    # the page-1 copilot writes its greeting from the base table's NAME, so this
    # must read as a book of business, not a "loan book"
    "base_table": "Book of Business",
    # #D71712 is sampled straight from Aramark's own logo SVG (the flame mark);
    # the deep maroons are darkenings of it for the header gradient, the amber
    # and orange are the warm hospitality accents, and the green nods to
    # Aramark's "Green Thread" sustainability mark.
    "palette": {
        "navy": "#4A1210", "navy_deep": "#2A0A08",
        "primary": "#D71712", "secondary": "#E8722A",
        "accent": "#F5A623", "mint": "#2E9E6B",
    },
    "products": [
        # name, order, balance_type, bal_base($MM rev), yield(=AOI margin),
        # funding(0), fee_base($MM/mo), provision, delinq(below-plan share),
        # opex_ratio, growth, units_base(accounts), phase, tagline, rate_label,
        # goal_pct, status
        ("Business & Industry", 1, "P&L", 2600, .0650, 0.0, 5.0, .0025, .034,
         .140, .028, 3400, 0.0, "Workplace dining & refreshments",
         "AOI margin", .992, "On plan"),
        ("Education", 2, "Client interest", 4300, .0500, 0.0, 6.0, .0020, .028,
         .150, .034, 2600, 2.0, "K-12 and higher ed dining",
         "AOI margin", .965, "On plan"),
        ("Healthcare & Senior Living", 3, "Client interest", 1900, .0550, 0.0, 4.0,
         .0022, .030, .145, .041, 1500, 1.1, "Patient dining & senior living",
         "AOI margin", 1.058, "Ahead"),
        ("Sports, Leisure & Corrections", 4, "P&L", 3100, .0850, 0.0, 7.0, .0035,
         .052, .160, .052, 900, 1.6, "Stadiums, arenas, parks & corrections",
         "AOI margin", 1.041, "Ahead"),
        ("Facilities & Other", 5, "Client interest", 2000, .0700, 0.0, 4.0, .0020,
         .026, .135, .038, 1900, 0.6, "Custodial, grounds & maintenance",
         "AOI margin", .938, "Behind"),
        ("International", 6, "P&L", 4600, .0450, 0.0, 5.0, .0030, .046,
         .155, .045, 3200, 1.3, "Food & facilities outside the US",
         "AOI margin", .706, "Behind"),
    ],
    "subs": {
        "Business & Industry": [("Workplace Dining", .48, -20, 3.2, "On plan"),
                                ("Refreshment Services", .22, 15, 4.6, "Ahead"),
                                ("Catering & Events", .18, 40, 1.1, "On plan"),
                                ("Facilities (B&I)", .12, 60, -0.8, "Behind")],
        "Education": [("Higher Education Dining", .52, -15, 2.8, "On plan"),
                      ("K-12 Nutrition", .30, 20, 1.4, "On plan"),
                      ("Campus Retail & Brands", .12, 55, 5.2, "Ahead"),
                      ("Athletics Concessions", .06, 90, -1.2, "Behind")],
        "Healthcare & Senior Living": [("Patient Dining", .44, -25, 2.1, "On plan"),
                                       ("Senior Living Dining", .31, 30, 4.4, "Ahead"),
                                       ("Environmental Services", .17, 60, 1.1, "On plan"),
                                       ("Clinical Nutrition", .08, 40, -0.6, "Behind")],
        "Sports, Leisure & Corrections": [("Stadiums & Arenas", .46, 35, 8.2, "Ahead"),
                                          ("Convention Centers", .24, 20, 3.6, "Ahead"),
                                          ("Destinations & Parks", .18, 55, 6.1, "Ahead"),
                                          ("Corrections", .12, -20, 0.9, "On plan")],
        "Facilities & Other": [("Custodial Services", .42, -30, 2.4, "On plan"),
                               ("Grounds & Landscaping", .28, 25, 3.8, "Ahead"),
                               ("Facilities Maintenance", .22, 15, 1.6, "On plan"),
                               ("Energy & Engineering", .08, 60, 5.4, "Ahead")],
        "International": [("Europe", .38, -10, 2.8, "On plan"),
                         ("Canada", .24, 15, 3.6, "Ahead"),
                         ("Latin America", .22, 40, 4.2, "Ahead"),
                         ("Rest of World", .16, 20, 1.1, "On plan")],
    },
    "alerts": [
        ("critical", "Food cost spike at flagship venues",
         "Beef and dairy inflation pushed food cost 210 bps over plan across 46 "
         "sports & leisure venues", "22m ago", "Supply Chain", 210, "bps over plan"),
        ("critical", "Contract retention risk",
         "Three higher-education dining contracts worth $84M in annual revenue "
         "enter rebid inside 60 days", "1h ago", "Client Retention", 84,
         "$M up for rebid"),
        ("warning", "Front-line labor coverage gap",
         "1,180 open positions across healthcare accounts are running above the "
         "8% vacancy ceiling", "3h ago", "Field HR", 1180, "open positions"),
        ("warning", "International margin drift",
         "International food & facilities AOI margin down 74 bps quarter over "
         "quarter on FX and wage inflation", "6h ago", "Finance", 74, "bps QoQ"),
        ("info", "New account mobilization",
         "A 22-site business & industry dining account goes live next month, "
         "adding an estimated $31M in annual revenue", "1d ago", "Growth", 31,
         "$M annualized"),
    ],
    "agent": ("You are an analyst covering Aramark's food and facilities services "
              "across its US sectors -- Business & Industry, Education, Healthcare "
              "& Senior Living, Sports, Leisure & Corrections, and Facilities -- "
              "and its International segment. Answer with numbers from the "
              "workbook, in terms of managed revenue, adjusted operating income "
              "(AOI), AOI margin and client accounts."),
}

# US footprint weighted toward Aramark's account base: California, Texas, its
# Philadelphia home state of Pennsylvania, Florida and the big education /
# healthcare states carry the count. Partial sum (~0.82) is fine.
FOOTPRINTS["aramark"] = [("CA", .118), ("TX", .104), ("PA", .086), ("FL", .078),
                         ("NY", .072), ("IL", .052), ("OH", .046), ("NC", .042),
                         ("GA", .040), ("MI", .036), ("NJ", .034), ("MA", .032),
                         ("VA", .030), ("WA", .026), ("AZ", .024)]

LABELS["aramark"] = {
    "personas": ["Executive", "Field Operations"],
    "modeler_page": "Margin Planning",
    "cohort_page": "Account Segments",
    "modeler_title": "Food Cost & Margin Scenario Modeler",
    "shock_label": "Food & labor cost shock (bps)",
    "kpi_revenue": "Adj. operating income ($M)",
    "kpi_margin": "Segment operating income ($M)",
    "kpi_volume": "Managed revenue ($M)",
    "kpi_units": "Client accounts (K)",
    "driver_nim": "AOI margin",
    "driver_risk": "Accounts below plan",
    "driver_cost": "Cost of services rate",
    "driver_eff": "Overhead ratio",
    "seg_product": "Sector",
    "seg_credit": "Account tier",
    "seg_dd": "Managed services client",
    "seg_engage": "Dining frequency",
    "seg_type": "Contract type",
    "seg_held": "Services purchased",
    "cohort_name": "Segment name",
    "kpi_cohort_size": "Accounts in segment",
    "kpi_cohort_vol": "Annual account revenue",
    "kpi_cohort_rev": "AOI per account",
    "kpi_cohort_risk": "Avg attrition risk",
    "col_volume": "Baseline revenue",
    "col_growth": "Revenue growth %",
    "col_yield": "AOI margin Δ bps",
    "col_cost": "Cost of services Δ bps",
}

# Translate the generic band literals AND the six hardcoded SoFi product names in
# member_population.sql into Aramark's own vocabulary (global string replace), so
# the cohort page never leaks a "Personal Loans" filter value. The six sectors
# map 1:1 onto the six product slots.
SEGMENTS["aramark"] = {
    "Near Prime": "Emerging", "Prime": "Core",
    "Super Prime": "Strategic", "Exceptional": "Flagship",
    "Daily": "Daily", "Weekly": "Weekly",
    "Monthly": "Occasional", "Dormant": "Seasonal",
    "Personal Loans": "Business & Industry",
    "SoFi Money": "Education",
    "SoFi Invest": "Healthcare & Senior Living",
    "Credit Card": "Sports, Leisure & Corrections",
    "Student Refinancing": "International",
    "Home Loans": "Facilities & Other",
}

VOCAB["aramark"] = {
    "econ": ("Aramark runs food and facilities services on a contract basis. On "
             "profit-and-loss (P&L) contracts it books the full client revenue "
             "and bears the food, labor and operating cost, so the spread between "
             "managed revenue and cost of services is the adjusted operating "
             "income (AOI) the account contributes. On client-interest "
             "(management-fee) contracts the client bears the cost and Aramark "
             "earns a management and incentive fee. Sports, Leisure & Corrections "
             "and Facilities carry the highest AOI margins; Education and "
             "International run leaner, so sector mix and food-cost inflation move "
             "AOI more than revenue growth does."),
    "metrics": ("managed revenue, adjusted operating income, AOI margin, client "
                "accounts and the share of accounts running below plan"),
    "bands": ("Account tiers: Emerging, Core, Strategic, Flagship. Dining "
              "frequency: Daily, Weekly, Occasional, Seasonal."),
    "cohort_report": ("segment size, annual account revenue and average "
                      "attrition risk"),
}

# Per-account economics for the cohort page, in DOLLARS. An Aramark client is an
# institution (a company, campus, hospital, stadium), so a single account's
# annual revenue runs from the low hundreds of thousands (Emerging) to the high
# single-digit millions (Flagship) -- orders of magnitude above a retail balance,
# which is what the default carries. rev_rate is AOI per dollar of account
# revenue; fee_per_product is the incremental AOI of each additional service line.
POP["aramark"] = {"bases": (180000, 650000, 2400000, 8500000), "rev_rate": 0.06,
                  "fee_per_product": 12000}

# No bespoke plugin and no ticker on this first build -- a new plugin has to be
# hosted on jsDelivr off the public millersigma repo (HANDOFF sec 9), which this
# checkout can't push to. Modelled plugin-clean like Marriott; a bespoke
# food-service day-part / commodity plugin is the natural follow-up.
PLUGINS["aramark"] = {"hero": None, "hero_label": None, "ticker": None}

COMPANIES["aramark"] = ARAMARK
