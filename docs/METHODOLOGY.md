# Methodology

## Why this instead of another Kaggle dataset

I wanted to build something where the data didn't come pre-cleaned. SEC EDGAR is a real, live, public database — nobody hands you a CSV. You have to pull raw filings, figure out where the section you want actually starts, and deal with the fact that every company's lawyers format things slightly differently. That last part turned out to be a bigger problem than I expected, and I think the story of solving it is more interesting than the final numbers.

## Company selection

35 US retailers, 2019–2023 10-Ks. I picked retail specifically because that period has real disruption in it — COVID supply chain chaos, inflation, and a couple of companies (Bed Bath & Beyond, and to a lesser extent GameStop with the meme-stock episode) that give the dataset some genuine variation instead of five flat years of boilerplate.

## Getting the actual risk section out of a filing

This is the part that took the longest, and it's worth explaining honestly rather than pretending it went smoothly.

My first approach was to download the raw filings and use regex to find "Item 1A. Risk Factors" and grab everything up to "Item 1B." Sounds simple. It wasn't, for a few reasons:

- The phrase "Item 1A" shows up multiple times in every filing — once in the table of contents, once at the real header, and often again inside the section itself as a self-reference ("as discussed in Item 1A above"), plus sometimes in totally unrelated cross-references elsewhere in the document.
- Companies punctuate the header differently. Some use a period, some a dash, some an em-dash, some a comma. A few filings had literal typos — a stray space in the middle of the word "Risk" or "Factors," probably an artifact of how the original document was generated.
- The raw file isn't just the 10-K. It's the 10-K bundled together with every exhibit, certification, and attachment the company filed alongside it — sometimes over a hundred separate documents in one file. Searching the whole thing meant picking up false matches from totally unrelated exhibits.

I went through several rounds of fixes — isolating just the actual 10-K document before searching, rejecting candidates that looked like cross-references, picking the match with the largest gap before the next section header — and got it working for about 95% of filings. But when I did a manual spot-check (reading the first 150 characters of every single company's most recent filing instead of just trusting the success count), I found the automated logic was still picking the wrong text for over a third of companies. The success count was measuring "did we extract *something*," not "did we extract the *right* something," and those aren't the same thing.

At that point I stopped patching my own regex and switched to `edgartools`, a library built specifically for parsing SEC filings. It got every company right on the first real test, including several my own code had gotten wrong. In hindsight I should have looked for a purpose-built tool earlier — this is a well-known, solved problem, and reinventing it by hand was a worse use of time than it felt like in the moment. I'm leaving this in the writeup because I think knowing when to stop building something yourself is as relevant a skill as building it.

## Defining the change metrics

For each company, comparing consecutive years' risk sections:

- **Word count change (%)** — simple, interpretable, turned out to matter more than the fancier metric below
- **Text similarity** — TF-IDF cosine similarity between consecutive years' text, converted to a "change score" (1 − similarity)

## Getting volatility data

Used `yfinance` to pull daily prices for each company starting from its actual filing date, then computed annualized realized volatility over the following 60 trading days.

Four companies (Nordstrom, Gap, Walgreens, Bed Bath & Beyond) came back empty across every single year, even for basic date ranges that should have worked. All four were later delisted, taken private, or went bankrupt, and it looks like Yahoo Finance's data doesn't retain history for tickers that no longer trade — a documented limitation, not something specific to this project. I tried Stooq as a fallback and it didn't have the data either. These four were dropped from the volatility analysis specifically; their risk-language data is still used elsewhere.

## Controlling for the market

First pass, correlation between risk-language change and volatility was close to zero. Looking at the scatter plot, it was obvious why — a handful of points had very low text change but extremely high volatility, and they all clustered around March–April 2020. That's not a company-specific signal, that's the whole market panicking at once.

So I pulled S&P 500 volatility over the same windows and computed excess volatility (company minus market) for each filing. That's the number that actually isolates whatever a company did on its own, separate from what the market did to everyone.

## Results

| Metric | Raw volatility | Excess volatility (market-adjusted) |
|---|---|---|
| Correlation with text change score | 0.03 | 0.08 |
| Correlation with \|word count change\| | 0.13 | **0.20** |

Regression on word count change vs. excess volatility: r = 0.20, R² = 0.04, p = 0.026, n = 123.

That p-value means the relationship is unlikely to be random noise. The R² means it's still explaining a small slice of what actually happens to a stock's volatility — most of that is driven by things this dataset doesn't capture (earnings, guidance, sector-wide news, general sentiment).

## Bed Bath & Beyond, as a concrete example

| Year | Risk section length (characters) | Word count change |
|---|---|---|
| 2019 | 19,029 | — |
| 2020 | 29,134 | +55% |
| 2021 | 35,985 | +26% |
| 2022 | 50,585 | +39% |
| 2023 | 27,534 | -44% |

The section grew every year while the business was struggling, then shrank sharply right before the 2023 bankruptcy filing. My read on this: as things got worse, they had more to disclose in more detail. By the time collapse was close, the risks weren't hypothetical anymore — the language likely shifted from long, hedged, exploratory disclosure to something shorter and more direct (the kind of "substantial doubt about our ability to continue as a going concern" language that shows up in distressed filings). It's one company, so I wouldn't generalize from it alone, but it's a genuinely interesting data point that the aggregate stats don't show on their own.

## What I'd do differently with more time

- Longer window — five years isn't much for this kind of question, and a longer history would help confirm whether the pattern holds outside this specific, unusually turbulent period
- A better fallback for delisted companies' price history, so the volatility analysis doesn't lose exactly the companies most likely to be interesting (financial distress correlates with both disclosure changes and delisting, so dropping them probably biases the sample somewhat)
- Testing other sections of the filing (MD&A in particular) to see if risk language specifically matters, or if any section rewrite correlates similarly

## Honest limits

- R² of 0.04 is a real but small effect. This is not a trading signal on its own.
- The sample lost 4 of 35 companies for the volatility analysis, all of them companies that had financial trouble later — this probably understates the relationship somewhat, since distressed companies are likely to have both bigger disclosure changes and bigger stock moves.
- Five years, one sector. I wouldn't assume this generalizes to other industries or a calmer time period without checking.
