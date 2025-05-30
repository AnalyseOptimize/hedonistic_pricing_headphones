# Hedonistic pricing using multilinear regression (LAD, FGLS, Quantile)

Hedonic Pricing is an economic model used to estimate the value of a good or service by breaking it down into its constituent characteristics or attributes. The core idea is that the price of a product is determined by the sum of the values of its individual features rather than the product as a whole.

We explore the market of headphones in Russia and particulary pricing in [DrHead](https://doctorhead.ru/?srsltid=AfmBOopl28H6e8TpSRQw0Lzxjcbgs_KbcvEXK7U9t45iYY8_P2YJQNLI) store, which has a special segment of professional headsets. 

Our project consists of:
- Deep data analysis using econometrics
- Evaluating models and it's robustness
- Interpretation via average marginal effects and quantile coefficients
- Developing our own model of gaussian mixture (without realisation)

In `data` you can find 
- `dataset_for_regression.csv` - final dataset which was used in model estimation. All preprocessing stages you can find in our main `.ipynb`.
- `processed_df.csv` - clean dataset without missing data and irrelevant features.
- `parsed_data.csv` - raw data from DrHead website.
- `doctorhead_report.html` - extensive EDA on raw parsed data.
