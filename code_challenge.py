import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from loguru import logger
import time


class Scraper:
    def __init__(self):
        self.all_jobs: List[Dict[str, Any]] = []

    def fetch_page(self, url: str, headers: Dict[str, str]) -> BeautifulSoup:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")

    def extract_job_data(self, job) -> Dict[str, Any]:
        title = job.find("h2", itemprop="title").text.strip()
        name = job.find("h3", itemprop="name").text.strip()
        tags = [
            tag.text.strip() for tag in job.find("td", class_="tags").find_all("h3")
        ]
        job_path = job.find("a", itemprop="url", href=True)["href"]
        return {
            "title": title,
            "name": name,
            "tags": tags,
            "url": f"https://remoteok.com{job_path}",
        }

    def scrape(self, keywords: List[str], offset_range: int):
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0"
            )
        }
        try:
            start_time = time.time()
            for keyword in keywords:
                for offset in range(offset_range):
                    url = (
                        f"https://remoteok.com/remote-{keyword}-jobs?offset={offset*20}"
                    )
                    soup = self.fetch_page(url, headers)
                    jobs = soup.find_all("tr", attrs={"data-offset": True})
                    if not jobs:
                        break
                    for job in jobs:
                        job_data = self.extract_job_data(job)
                        self.all_jobs.append(job_data)
            total_latency = time.time() - start_time
            logger.info(f"Total latency: {total_latency:.2f} seconds")
        except requests.RequestException as e:
            total_latency = time.time() - start_time
            logger.error(f"요청 에러 발생: {e} / Total latency: {total_latency:.2f} seconds")
        except Exception as e:
            total_latency = time.time() - start_time
            logger.error(f"에러 발생: {e} / Total latency: {total_latency:.2f} seconds")


if __name__ == "__main__":
    scraper = Scraper()
    scraper.scrape(["golang", "python"], 4)
    print(len(scraper.all_jobs))
