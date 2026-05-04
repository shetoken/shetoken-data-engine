# Contributing to SHEtoken

Thank you for your interest in contributing to SHEtoken. This is an open-source project and we welcome contributions from developers, data scientists, gender researchers, NGO partners, and community members.

---

## Ways to Contribute

### 1. Data Contributions
Help improve the accuracy and coverage of the WEI index.

- **Suggest new data sources** — Open an issue with label `data-source`
- **Report data errors** — Open an issue with label `data-error`
- **Challenge a WEI score** — Open an issue with label `wei-challenge` (see methodology.md for full process)
- **Add country or state data** — Submit a pull request to the `data/` folder

### 2. Code Contributions
Help build the technical infrastructure.

- **WEI calculation scripts** (`wei-index/`)
- **Smart contract development** (`smart-contracts/`)
- **Dashboard improvements** (`dashboard/`)
- **API development** (`api/`)
- **Tests and validation** (`tests/`)

### 3. Documentation Contributions
Help make SHEtoken more accessible.

- Fix typos or unclear explanations
- Translate documentation into other languages
- Add examples and use cases
- Improve the methodology explanation

### 4. Community Contributions
Help grow the SHEtoken ecosystem.

- Share SHEtoken with NGOs and government bodies who should register
- Translate materials into Hindi, Bengali, Tamil, or other languages
- Write blog posts or research papers about the WEI methodology
- Organise community discussions via Discord

---

## Getting Started

### Fork and Clone

```bash
git clone https://github.com/YOUR_USERNAME/shetoken
cd shetoken
```

### Install Dependencies

```bash
# Python dependencies
pip install -r requirements.txt

# Node.js dependencies (for smart contracts)
npm install
```

### Run the WEI Calculator

```bash
python wei-index/formula.py
```

### Run Tests

```bash
python -m pytest tests/
```

---

## Pull Request Guidelines

1. **Fork** the repository and create a new branch
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** — keep commits focused and descriptive

3. **Test your changes** before submitting
   ```bash
   python -m pytest tests/
   ```

4. **Submit a Pull Request** with:
   - Clear title describing what you changed
   - Description of why the change is needed
   - Any relevant data sources or references
   - Screenshot or output if applicable

5. **Be patient** — all PRs are reviewed by the core team and may require DAO governance approval for significant methodology changes

---

## Issue Labels

| Label | Use When |
|---|---|
| `data-source` | Suggesting a new data source for the WEI |
| `data-error` | Reporting incorrect data in a WEI score |
| `wei-challenge` | Formally challenging a published WEI score |
| `bug` | Something is broken in the code |
| `enhancement` | Suggesting a new feature |
| `documentation` | Improving docs or methodology explanation |
| `gov-registration` | Government body wanting to register |
| `ngo-registration` | NGO wanting to register a program |
| `ngo-verification` | Community review of NGO data submission |
| `good-first-issue` | Good for new contributors |
| `help-wanted` | Extra attention needed |

---

## WEI Score Challenge Process

Anyone can formally challenge a published WEI score. To do so:

1. Open a GitHub Issue with label `wei-challenge`
2. Include:
   - Country or state being challenged
   - Specific indicator(s) in dispute
   - Your alternative data source (with methodology documentation)
   - Quantitative impact on the WEI score
3. The Advisory Council reviews the challenge
4. A DAO governance vote is held if the challenge has merit
5. Simple majority (51%) required to accept and revise the score
6. Challenges must be submitted within **30 days** of draft WEI publication

---

## Code of Conduct

SHEtoken is a project dedicated to women's empowerment. We expect all contributors to:

- Be respectful and inclusive in all communications
- Engage with data and methodology in good faith
- Declare any conflicts of interest (e.g. if you represent a government whose score you are challenging)
- Prioritise accuracy and transparency over political considerations
- Follow our [Code of Conduct](CODE_OF_CONDUCT.md)

---

## Governance

Significant changes to the WEI methodology require DAO governance approval:

| Change Type | Threshold Required |
|---|---|
| Formula weights | 66% supermajority |
| New data source | 51% simple majority |
| New country or state | 51% simple majority |
| Smart contract changes | 75% supermajority + 60-day timelock |

Minor changes (documentation, bug fixes, typos) do not require governance approval.

---

## Translations Needed

We are actively seeking translations of our key documents into:

- Hindi (`hi`)
- Bengali (`bn`)
- Tamil (`ta`)
- Telugu (`te`)
- Swahili (`sw`)
- French (`fr`)
- Spanish (`es`)
- Arabic (`ar`)

To contribute a translation, create a new folder `docs/translations/[language-code]/` and submit a PR.

---

## Recognition

All contributors are listed in our [CONTRIBUTORS.md](CONTRIBUTORS.md) file. Significant contributors may be eligible for token allocations from the Ecosystem & Partnerships fund — subject to DAO governance approval.

---

## Questions?

📧 **contact@shetoken.org**
💬 **Discord:** discord.gg/shetoken
💻 **GitHub Issues:** [github.com/shetoken/issues](https://github.com/shetoken/issues)

---

*Thank you for helping build the world's first women's empowerment index token.*

*© 2026 SHE Foundation. Licensed under MIT.*
