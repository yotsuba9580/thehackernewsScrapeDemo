import os
import time
import requests
import csv
from lxml import html
import random
from datetime import datetime

from requests import RequestException

# 广告文章标题列表
ad_titles = [
    "Data Governance in DevOps: Ensuring Compliance in the AI Era",
    "What CISOs Really Think About AI (and What They're Doing About It)"
]

# 设置代理
proxies = {
    "http": "http://127.0.0.1:7890",
    "https": "http://127.0.0.1:7890"
}

# 随机选择 User-Agent 和其他请求头
def get_random_headers():
    user_agents = [
        # 示例User-Agent列表，可以根据需要添加更多
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/89.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/91.0.864.59",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.113 Safari/537.36"
    ]

    headers = {
        'User-Agent': random.choice(user_agents),
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'DNT': '1',  # Do Not Track
        'Referer': 'https://thehackernews.com/',
        'Origin': 'https://thehackernews.com/'
    }

    return headers

# 设置请求头，模拟浏览器请求
headers = get_random_headers()

# 创建会话，自动处理 Cookies
session = requests.Session()
session.headers.update(headers)
session.proxies = proxies

# 获取页面内容
def fetch_page(url, retries=3):
    for attempt in range(retries):
        try:
            response = session.get(url, timeout=10)
            response.raise_for_status()  # 检查请求是否成功
            return response.content
        except RequestException as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < retries - 1:
                wait_time = random.randint(3, 6)
                print(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                raise e  # 如果所有尝试都失败，抛出异常

# 将上一页的标题保存在一个集合中, 以防止重复
last_page_titles = set()
# 记录上次的 URL ,避免死循环
last_url = None

# 解析页面并提取文章信息
def parse_articles(page_content):
    tree = html.fromstring(page_content)  # 解析 HTML 页面，树形结构，便于使用 XPath 提取数据

    # 提取文章条目的容器
    article_elements = tree.xpath('//div[@class="body-post clear"]')

    articles = []
    for article in article_elements:
        title = article.xpath('.//h2[@class="home-title"]/text()')[0].strip()
        url = article.xpath('.//a[@class="story-link"]/@href')[0]
        date = article.xpath('.//span[@class="h-datetime"]/text()')[0].strip()

        if title not in last_page_titles:
            articles.append({'title': title, 'url': url, 'date': date})

    return articles

# 保存当前处理的日期
def save_last_processed_date(date, filename="last_processed_date.txt"):
    with open(filename, mode='w', encoding='utf-8') as file:
        file.write(date)

# 读取最后处理的日期
def load_last_processed_date(filename="last_processed_date.txt"):
    try:
        with open(filename, mode='r', encoding='utf-8') as file:
            return file.read().strip()
    except FileNotFoundError:
        return None  # 如果文件不存在，返回 None

# 过滤广告文章并返回有效文章
def filter_articles(articles):
    filtered_articles = [article for article in articles if article['title'] not in ad_titles]
    return filtered_articles


# 获取下一页的 URL
def get_next_page_url(updated_max_date):
    return f"https://thehackernews.com/search?updated-max={updated_max_date}T23:59:59%2B05:30&max-results=20&by-date=true"


# 将文章数据保存到 CSV 文件中
def save_articles_to_csv(articles, filename="articles.csv"):
    # 检查文件是否存在，如果不存在，则写入表头
    file_exists = os.path.exists(filename)

    # 以追加模式打开文件
    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=["title", "date", "url"])

        # 如果文件不存在，写入表头
        if not file_exists:
            writer.writeheader()  # 写入表头

        # 写入文章数据
        writer.writerows(articles)

# 主循环，抓取所有文章的 URL
def scrape_all_articles(start_url):
    global last_page_titles
    global last_url
    page_url = start_url
    try_counter = 0

    # 读取最后处理的日期
    last_processed_date = load_last_processed_date()
    if last_processed_date:
        page_url = f"https://thehackernews.com/search?updated-max={last_processed_date}T23:59:59%2B05:30&max-results=20&by-date=true"

    while page_url:
        try_counter += 1
        print(f"Fetching page: {page_url}")
        # 获取页面内容
        response_content = fetch_page(page_url)

        if response_content is None:
            print("Failed to fetch page")

        # 解析页面内容，提取文章信息
        articles = parse_articles(response_content)
        # 如果当前页面没有提取到任何文章，报错
        if not articles:
            print("Error: No articles found, the page content is the same as the previous one.")
            raise ValueError("No new articles found. This indicates duplicate content!")
        print(f"Found {len(articles)} articles on this page")

        # 过滤广告文章
        filtered_articles = filter_articles(articles)

        # 更新上一页的标题集
        last_page_titles = {article['title'] for article in filtered_articles}

        # 如果没有有效文章，则结束循环
        if not filtered_articles:
            break

        # 保存到 CSV
        save_articles_to_csv(filtered_articles)

        # 获取下一页的 URL，使用最后一篇文章的日期作为 updated-max
        updated_max_date = filtered_articles[-1]['date']
        date_obj = datetime.strptime(updated_max_date, "%b %d, %Y")
        formatted_date = date_obj.strftime("%Y-%m-%d")
        save_last_processed_date(formatted_date)  # 保存最后处理的日期

        # 获取下一页的 URL，使用最后一篇文章的日期作为 updated-max
        page_url = get_next_page_url(formatted_date)

        if last_url and page_url == last_url:
            print(
                f"Error: The current page URL is the same as the previous one. This indicates that the content is identical.")
            raise ValueError("The current page is identical to the previous one!")

        # 为防止请求过快，加入延时
        wait_time = random.randint(3, 6)
        # print(f"Waiting for {wait_time} seconds before next request...")
        time.sleep(wait_time)

        # 先试试看
        if try_counter >= 5:
            break

    print("All articles scraped successfully!")


# 启动爬虫，开始抓取
start_url = "https://thehackernews.com/"
scrape_all_articles(start_url)
