# SHEtoken ($SHE)
### The World's First Women's Empowerment Index Token

> *"She was always the currency. We just never measured it."*

[![Website](https://img.shields.io/badge/Website-shetoken.org-6D2E46)](https://shetoken.org)
[![Twitter](https://img.shields.io/badge/Twitter-@ShetokenDAO-C9A84C)](https://twitter.com/ShetokenDAO)
[![Email](https://img.shields.io/badge/Email-contact@shetoken.org-blue)](mailto:contact@shetoken.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## What is SHEtoken?

SHEtoken is an Ethereum ERC-20 token whose value is algorithmically tied to the **Women's Empowerment Index (WEI)** — a composite annual score measuring:

- 📚 Female literacy and education
- 💼 Economic inclusion and wage equality
- 🛡️ Safety from violence and crime
- 🗳️ Political empowerment
- 🏥 Health and maternal outcomes

**When the global WEI score rises → tokens are minted**

**When the global WEI score falls → tokens are burned**

Progress is rewarded. Regression has a price.

---

## The WEI Formula

```
WEI = (Empowerment × 0.25)
    + (Education  × 0.20)
    + (Economic   × 0.20)
    + (Health     × 0.15)
    − (Crime Penalty × 0.20)
```

All sub-scores normalised 0–100.

Full methodology → [wei-index/methodology.md](wei-index/methodology.md)

---

## India Programs in the Index

| Program | State | Beneficiaries | WEI Pillar |
|---|---|---|---|
| Lakshmi Bhandar | West Bengal | 24.1M women | Economic Inclusion |
| Kanyashree | West Bengal | 10M girls | Education & Literacy |
| Kudumbashree | Kerala | 46 lakh members | Economic, Education, Health |
| JEEViKA | Bihar | 1.04M SHGs | Economic Inclusion |
| Educate Girls | Rajasthan/MP | 6.7M beneficiaries | Education & Literacy |

---

## Geographic Investment Tiers

| Tier | Token | Status |
|---|---|---|
| Global | `$SHE` | Available at launch |
| Country | `$SHE-IND`, `$SHE-NGA`, `$SHE-USA` | Year 2 |
| State / Province | `$SHE-WB`, `$SHE-KL`, `$SHE-MH` | Year 3 |

---

## Quick Start

```bash
git clone https://github.com/shetoken/shetoken
cd shetoken
pip install -r requirements.txt
python wei-index/formula.py
```

---

## Repository Structure

```
shetoken/
├── README.md                    ← You are here
├── WHITEPAPER.md                ← Full whitepaper
├── LICENSE
├── CONTRIBUTING.md
│
├── wei-index/
│   ├── methodology.md           ← WEI formula explained
│   ├── formula.py               ← Calculation code
│   ├── weights.json             ← Pillar weights
│   └── validate.py              ← Data validation
│
├── data/
│   ├── sources.md               ← Data source links
│   ├── baseline-2025.csv        ← Country baseline scores
│   └── india-states-2025.csv    ← India state scores
│
├── smart-contracts/
│   ├── SHEToken.sol             ← ERC-20 contract
│   ├── WEIOracle.sol            ← Chainlink data feed
│   └── ImpactFund.sol           ← DAO treasury
│
├── docs/
│   ├── how-to-invest.md
│   ├── government-registration.md
│   └── ngo-registration.md
│
└── reports/
    └── 2025-baseline-report.pdf
```

---

## Tokenomics

| Parameter | Value |
|---|---|
| Token Name | SHE (Women's Empowerment Index Token) |
| Ticker | $SHE |
| Blockchain | Ethereum ERC-20 + Polygon L2 |
| Total Supply | 1,000,000,000 SHE |
| Smart Contract | CertiK + OpenZeppelin audit (pre-launch) |

| Allocation | % |
|---|---|
| Public Sale / Community | 40% |
| WEI Impact Fund | 25% |
| Founding Team (3-year vesting) | 15% |
| Ecosystem & Partnerships | 10% |
| Reserve & Liquidity | 10% |

---

## Current Status

- ✅ Whitepaper complete — [WHITEPAPER.md](WHITEPAPER.md)
- ✅ WEI index methodology designed
- ✅ India program case studies documented
- ✅ Domain registered — [shetoken.org](https://shetoken.org)
- ✅ Brand identity complete — coin logo, colour palette
- ⏳ Smart contract development — in progress
- ⏳ Seeking seed partnership and institutional investors
- ⏳ NGO data partnerships — in outreach
- ⏳ CertiK audit — pre-launch

---

## We Are Seeking

🔷 **Institutional Partners** — Impact investors, ESG funds, and philanthropic foundations

🔷 **Blockchain Partners** — Ethereum, Polygon, Chainlink, and Web3 infrastructure providers

🔷 **Data Partners** — NGOs, state governments, and research institutions in India

🔷 **Corporate Sponsors** — Companies with gender equity commitments and ESG reporting requirements

🔷 **Community Partners** — Women in Web3 organisations and women's rights NGOs

> Interested in partnering? Email **contact@shetoken.org**

---

## Roadmap

| Phase | Timeline | Key Milestone |
|---|---|---|
| Foundation | Months 1–3 | Whitepaper, WEI formula, shetoken.org live |
| Build | Months 4–6 | Smart contract dev, NGO outreach, institutional pitches |
| Testnet | Months 7–9 | Ethereum testnet, Chainlink oracle, DAO governance |
| Mainnet | Months 10–12 | Public token sale, Uniswap V3, CoinGecko listing |
| Country Tokens | Year 2 | $SHE-IND, $SHE-NGA, $SHE-USA + 10 more |
| State Tokens | Year 3 | $SHE-WB, $SHE-KL, $SHE-MH, NGO portal |
| Scale | Year 4+ | UN Women partnership, 50+ country tokens |

---

## Contributing

We welcome contributions from developers, data scientists, gender researchers, and NGO partners.

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## License

MIT License — see [LICENSE](LICENSE) for details.

All WEI data and methodology is open-source and freely auditable.

---

## Contact & Community

| Channel | Link |
|---|---|
| 🌐 Website | [shetoken.org](https://shetoken.org) |
| 📧 Email | contact@shetoken.org |
| 🐦 Twitter | [@ShetokenDAO](https://twitter.com/ShetokenDAO) |
| 💻 GitHub | [github.com/shetoken](https://github.com/shetoken) |
| 💬 Discord | discord.gg/shetoken |

---

*© 2026 SHE Foundation. All rights reserved.*

*SHE — When the world gets better for women, SHE goes up.*
