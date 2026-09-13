# Does Risk Disclosure Language Predict Stock Volatility?

I wanted to know if the way a company writes about risk in its 10-K actually says anything about what happens to its stock afterward. Short answer: a little, but not enough to trade on.

## The idea

Every public company has to file a 10-K once a year, and buried in it is a section called "Risk Factors" where they're legally required to list what could go wrong. Most years it's copy-pasted with small edits. Sometimes it changes a lot. I wanted to test whether a big change in that language, new risks appearing, old language getting rewritten, the section growing or shrinking, actually predicts whether the stock gets more volatile in the months after the filing comes out.

I pulled real 10-K filings for 35 US retailers (Walmart, Target, Costco, Etsy, GameStop, Bed Bath & Beyond, and 29 others) covering 2019 through 2023, on purpose, that window has COVID, inflation, and a couple of actual bankruptcies in it, so there's real variation to work with instead of five years of nothing happening.

## What I found

Not much, honestly, until I controlled for the market. Raw correlation between risk-language change and volatility was basically zero (0.03). Made sense once I looked closer, 2020 volatility was high for almost everyone because the whole market was volatile, not because of anything specific companies wrote.

Once I subtracted out market-wide volatility and looked at each company's *excess* volatility, a real relationship showed up: word count change in the risk section correlates with excess volatility at r = 0.20 (p = 0.026, so it's not noise). It only explains about 4% of the variation though, so it's a real signal, just a small one. Companies in the top 10% for how much their risk section grew or shrank showed roughly 10 points higher excess volatility than companies that barely touched theirs.

Bed Bath & Beyond's numbers tell a good story on their own, their risk section grew every year from 2019 to 2022 as things got worse, then shrank by 44% right before they filed for bankruptcy in 2023. Worth a look if you want a concrete example instead of the aggregate stats.

## How it's built

- `notebooks/` — the actual analysis, step by step
- `src/` — reusable code (mostly extraction helpers)
- `app/dashboard.py` — a Streamlit app you can click through
- `docs/METHODOLOGY.md` — the long version, including a couple of dead ends I hit and how I got past them

## Running it

```bash
git clone https://github.com/Akeem-Akinyemi/sec-risk-volatility-project.git
cd sec-risk-volatility-project
pip install -r requirements.txt
streamlit run app/dashboard.py
```

## What this used

Python, SEC EDGAR (via edgartools), yfinance, pandas, scikit-learn, scipy, Streamlit, Plotly.

## A couple of honest caveats

Four companies (Nordstrom, Gap, Walgreens, Bed Bath & Beyond) got dropped from the volatility side of the analysis, they were later delisted, taken private, or went bankrupt, and I couldn't find historical pricing for them through the free data sources I tried. Their risk-language data is still in there, just not matched to a stock outcome.

Also worth saying plainly: R² of 0.04 means this alone isn't a trading strategy. It's a real, statistically significant pattern, not a strong one.
