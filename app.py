import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import streamlit as st

# ユーザーエージェント設定
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}

# スクレイピングを実行する関数
def fetch_search_results(url, headers):
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            results = []
            for item in soup.select("li.b_algo h2 a"):
                title = item.text.strip()
                link = item['href']
                if title and link:
                    results.append({"title": title, "link": link})
            return results
        else:
            st.error(f"Failed to retrieve search results. HTTP Status Code: {response.status_code}")
            return []
    except Exception as e:
        st.error(f"An error occurred during fetch: {e}")
        return []

# Streamlitアプリケーション
st.title("Web Scraping Tool")

# ユーザー入力
url = st.text_input("Enter the start URL:")
filename = st.text_input("Enter the desired file name (without .xlsx):", value="bing_results")

if st.button("Start Scraping"):
    if url and filename:
        all_results = []
        seen_urls = set()
        page = 0
        has_results = True

        with st.spinner("Scraping in progress..."):
            while has_results:
                random_param = random.randint(1, 100000)
                page_url = f"{url}&first={page * 10}&rnd={random_param}"

                st.write(f"Fetching page {page + 1}: {page_url}")
                results = fetch_search_results(page_url, headers)
                if not results:
                    has_results = False
                    break

                unique_results = [result for result in results if result['link'] not in seen_urls]
                if not unique_results:
                    has_results = False
                    break

                all_results.extend(unique_results)
                seen_urls.update([result['link'] for result in unique_results])

                st.write(f"Page {page + 1}: {len(unique_results)} unique results found.")

                page += 1
                time.sleep(random.uniform(2, 5))

        if all_results:
            df = pd.DataFrame(all_results)
            output_file = f"{filename}.xlsx"
            df.to_excel(output_file, index=False)
            st.success(f"Scraping completed! {len(all_results)} results saved to {output_file}.")

            with open(output_file, "rb") as file:
                btn = st.download_button(
                    label="Download Excel File",
                    data=file,
                    file_name=output_file,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        else:
            st.warning("No results found.")
    else:
        st.error("Please provide both URL and file name.")
