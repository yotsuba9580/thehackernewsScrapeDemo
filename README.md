# Web Scraper for The Hacker News

This project provides a Python-based web scraper to extract articles from The Hacker News website.

## Requirements

- Python 3.7 or higher

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yotsuba9580/thehackernewsScrapeDemo.git
    cd thehackernewsScrapeDemo
    ```

2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Set up a proxy if required (e.g., via Clash or any proxy service).

## Usage

1. **Run the Scraper**:
    ```bash
    python scraper.py
    ```

2. **Output**:
    - Articles will be saved to `articles.csv` in the current directory.
    - The scraper will also save the last processed date to `last_processed_date.txt` for resuming scraping later.

3. **Resuming Scraping**:
    - The scraper automatically resumes from the last processed date if `last_processed_date.txt` exists. To restart from the beginning, delete this file.

## How It Works

1. **Fetching Pages**:
    - Uses `requests` to fetch HTML content from The Hacker News, with retries and delay to avoid rate limits.

2. **Parsing HTML**:
    - Extracts article titles, URLs, and dates using `lxml` and XPath expressions.
  
## Example Output

Example of a row in `articles.csv`:

| Title                                | Date       | URL                                                         |
|--------------------------------------|------------|-------------------------------------------------------------|
| Rockstar2FA Collapse Fuels Expansion of FlowerStorm Phishing-as-a-Service | Dec 23, 2024 | [https://thehackernews.com/2024/12/cisa-cloud-security.html](https://thehackernews.com/2024/12/rockstar2fa-collapse-fuels-expansion-of.html) |

---

## Customization

- **Ad Titles**:
  - Update the `ad_titles` list in `scraper.py` to add or remove titles considered as ads.

- **Proxies**:
  - Configure the `proxies` dictionary in `scraper.py` to use your preferred proxy service.



## Project Structure

```plaintext
thehackernewsScrapeDemo/
├── hackerNewsScrape.py         # Main scraper script
├── requirements.txt            # Dependencies
├── articles.csv                # Output file (generated)
├── last_processed_date.txt     # Stores last processed date (generated)
└── README.md                   # Project documentation
```

## Data Source

This project is designed to scrape articles from [The Hacker News](https://thehackernews.com/), a popular cybersecurity news website. The scraper targets publicly available information such as article titles, URLs, and publication dates.

---

### Disclaimer

- This project is for **educational and research purposes only**. Please ensure your usage complies with [The Hacker News Terms of Service](https://thehackernews.com/).
- The copyright and ownership of all content belong to **The Hacker News** and its respective authors. This tool is not affiliated with or endorsed by The Hacker News.

