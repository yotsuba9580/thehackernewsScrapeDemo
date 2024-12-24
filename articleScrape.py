import os
import csv
import requests
from lxml import html
import random

# 设置代理和请求头
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

# 文件夹设置
PIC_FOLDER = "pic"
os.makedirs(PIC_FOLDER, exist_ok=True)


# 下载图片
def download_image(img_url, folder, filename):
    try:
        response = session.get(img_url, stream=True, timeout=10)
        response.raise_for_status()
        with open(os.path.join(folder, filename), "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"Image saved: {filename}")
    except Exception as e:
        print(f"Failed to download image: {img_url}, Error: {e}")


# 解析文章内容
def parse_article(article_url, title):
    try:
        response = session.get(article_url, timeout=10)
        response.raise_for_status()

        tree = html.fromstring(response.content)

        # 获取文章内容
        content_div = tree.xpath('/html/body/main/div/div/div[1]/div/div/div/div/div/div[5]')[0]
        paragraphs = content_div.xpath(
            './/p[not(ancestor::div[contains(@class, "dog_two clear")]) and not(ancestor::div[contains(@class, "cf note-b")])]')
        content = "\n".join([p.text_content().strip() for p in paragraphs])

        # 获取图片
        images = content_div.xpath('.//div[contains(@class, "saparator")]/a/@href')
        for idx, img_url in enumerate(images):
            img_filename = f"{title}_{idx + 1}.jpg"
            download_image(img_url, PIC_FOLDER, img_filename)

        return content

    except Exception as e:
        print(f"Failed to parse article: {article_url}, Error: {e}")
        return ""


# 从 CSV 读取 URL，解析内容，并写入新 CSV
def scrape_articles_to_csv(input_csv_file, output_csv_file):
    try:
        with open(input_csv_file, mode='r', encoding='utf-8') as infile, \
                open(output_csv_file, mode='w', encoding='utf-8', newline='') as outfile:

            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames + ['article']  # 添加新的列名
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)

            # 写入表头
            writer.writeheader()

            for row in reader:
                title = row['title'].strip().replace(" ", "_")  # 替换空格为下划线
                url = row['url'].strip()

                print(f"Processing article: {title}, URL: {url}")
                article_content = parse_article(url, title)

                # 将文章内容写入新列
                row['article'] = article_content
                writer.writerow(row)

                print(f"Article content added for: {title}")

    except Exception as e:
        print(f"Failed to process CSV file: {input_csv_file}, Error: {e}")


# 主函数
if __name__ == "__main__":
    csv_file = "articles.csv"  # 替换为你的 CSV 文件路径
    csv_output_file = "articles_with_content.csv"  # 输出 CSV 文件路径
    scrape_articles_to_csv(csv_file, csv_output_file)
