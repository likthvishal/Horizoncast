# Public datasets for testing the HorizonCast UI

Use these files on **Datasets → Upload** (`/datasets`). The uploader accepts **CSV** (and Parquet) up to **500 MB**; CSV preview reads the first chunk of the file. For the **fullest** match to a panel-style pipeline (`date`, `store_id`, `item_id`, `sales`), prefer long-format files or reshape wide competition files (see notes below).

---

## Instant smoke test (tiny file, seconds to download)

| Dataset | Why use it | Download |
|--------|------------|----------|
| **Monthly retail sales** (`date`, `sales`) | Few dozen rows — ideal to confirm preview + upload end-to-end | [Raw CSV](https://raw.githubusercontent.com/urgedata/pythondata/master/examples/retail_sales.csv) · [Repository: urgedata/pythondata](https://github.com/urgedata/pythondata/blob/master/examples/retail_sales.csv) |

---

## Store-level weekly sales (good retail shape, still manageable)

| Dataset | Why use it | Download |
|--------|------------|----------|
| **Walmart store sales (GitHub sample)** | Rows with `Store`, `Date`, `Weekly_Sales` plus exogenous fields — closer to real planning | [Walmart_Store_sales.csv](https://github.com/parvathy-nsarma/Walmart-Data/blob/main/Walmart_Store_sales.csv) · [Repository: parvathy-nsarma/Walmart-Data](https://github.com/parvathy-nsarma/Walmart-Data) — use GitHub **Raw** for a direct URL |
| **Kaggle — Walmart Recruiting: Store Sales Forecasting** | Original competition data (45 stores, departments, markdowns, etc.) | [Kaggle competition](https://www.kaggle.com/competitions/walmart-recruiting-store-sales-forecasting) — requires a free Kaggle account |

---

## Same domain as HorizonCast benchmarks: hierarchical retail (M5)

| Dataset | Why use it | Download |
|--------|------------|----------|
| **M5 Forecasting – Accuracy (Kaggle)** | Walmart-style hierarchical daily sales; aligns with M5 papers and this repo | [Kaggle: M5 Forecasting - Accuracy](https://www.kaggle.com/competitions/m5-forecasting-accuracy) — files such as `sales_train_validation.csv` / `sales_train_evaluation.csv`, `calendar.csv`, `sell_prices.csv` |
| **M5 via sktime (Zenodo-backed)** | Fetch in Python instead of the Kaggle UI | [sktime `M5Dataset` API reference](https://www.sktime.net/en/stable/api_reference/auto_generated/sktime.datasets.forecasting.m5_competition.M5Dataset.html) |

**UI note:** M5 `sales_train_*.csv` is **wide** (columns `d_1`, `d_2`, … per day). The UI still shows headers and a preview row. For a **long** panel (`date`, `store_id`, `item_id`, `sales`), melt the day columns and join `calendar.csv` in a notebook or ETL job.

---

## Tabular “many products × weeks” (wide format, good for ML pipelines)

| Dataset | Why use it | Download |
|--------|------------|----------|
| **UCI — Sales Transactions Dataset Weekly** | ~811 products × 52 weeks (+ normalized columns) | [UCI ML Repository](https://archive.ics.uci.edu/dataset/396/sales+transactions+dataset+weekly) — primary file `Sales_Transactions_Dataset_Weekly.csv` |

---

## Hierarchical daily grocery (research / hierarchy experiments)

| Dataset | Why use it | Download |
|--------|------------|----------|
| **UCI — Hierarchical Sales Data** | Italian grocery: daily SKU-level quantities, promotion flags, natural hierarchy | [UCI ML Repository](https://archive.ics.uci.edu/dataset/611/hierarchical+sales+data) |

---

## Real-world benchmark (monthly, multi-location)

| Dataset | Why use it | Download |
|--------|------------|----------|
| **4TU — Real-world sales forecasting benchmark (extended)** | Monthly aggregates, multiple CSVs, README; real retail context | [4TU.ResearchData dataset](https://data.4tu.nl/datasets/539debdb-a325-412d-b024-593f70cba15b) |

---

## Transactional retail (aggregate to daily demand yourself)

| Dataset | Why use it | Download |
|--------|------------|----------|
| **UCI — Online Retail II** | Invoice-level lines; aggregate by day + `StockCode` (or description) to build a demand panel | [UCI ML Repository](https://archive.ics.uci.edu/dataset/502/online+retail+ii) — files are XLSX |

---

## Optional extras (from the same research pass)

| Dataset | Why use it | Download |
|--------|------------|----------|
| **GitHub — Kaggle M5 mirror / examples** | Alternative host or starter notebooks around M5 | [KunalArora/kaggle-m5-forecasting](https://github.com/KunalArora/kaggle-m5-forecasting) |
| **GitHub — M5 competition notes** | Context and file descriptions for M5 | [rruss2/M5_competition](https://github.com/rruss2/M5_competition) |
| **E-commerce sales sample repo** | Another CSV/XLSX option for forecasting experiments | [johnmars-prog/E-commerce-Sales-Data](https://github.com/johnmars-prog/E-commerce-Sales-Data) |

---

## Suggested order for testing this project

1. **[Retail sales sample (raw CSV)](https://raw.githubusercontent.com/urgedata/pythondata/master/examples/retail_sales.csv)** — fastest “does upload + preview work?”
2. **[Walmart_Store_sales.csv](https://github.com/parvathy-nsarma/Walmart-Data/blob/main/Walmart_Store_sales.csv)** — richer columns, still easy to open locally.
3. **[M5 on Kaggle](https://www.kaggle.com/competitions/m5-forecasting-accuracy)** — stress size and real hierarchy (reshape if you need long format).

---

## License and terms

Each source has its own **license and citation requirements**. Before redistributing or publishing results, read the **dataset / competition / repository README** for that source. Kaggle datasets typically require **accepting competition rules** in the browser before download.

---

## Related project docs

- End-user problem narrative: `example_usecase.md` (repository root)
- API and deployment: `docs/API.md`, `docs/SELF_HOSTED.md`
