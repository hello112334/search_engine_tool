"""
Example

URL例: 
1. ●●課@(詳細ページURL) -> BEST
2. 支援制度詳細が必要
3. 一覧がPDFの場合は、一つ手前PDFを案内
4. 一覧で連絡先の記載があるのみの場合は一覧のURL
"""

# import requests
import pandas as pd
import difflib
from duckduckgo_search import DDGS
import time

similarity_limit = 0.3

def duckduckgo_search(query, url, target_flg, exception_flg):
    """
    DuckDuckGo APIを利用して検索を行う
    query:param query: 検索クエリ
    url:param url: 検索対象のURL
    target_url_list: 検索対象のURLリスト
    exception_url_list: 除外するURLリスト

    return: 検索結果のリスト
    """
    results = []  # 検索結果を格納するリスト

    # API/Server制限に注意
    time.sleep(1)

    with DDGS() as ddgs:
        search_results = [r for r in ddgs.text(query, max_results=5)]
    
    # for result in search_results:
    #     # 検索対象のURLを含む場合は抽出
    #     if url and url in result["href"]:
    #         results.append(result)
    #         break

    #     # 除外リストのURLを含む場合はスキップ
    #     if exception_flg:
    #         if any(item in result["href"] for item in exception_url_list['url']):
    #             continue

    #     # 対象リストに含まれるURLの場合のみ抽出
    #     if target_flg:
    #         if any(item in result["href"] for item in target_url_list['url']):
    #             results.append(result)

    # print(f"[INFO][QUERY] {query}")
    return search_results

def get_valid_webpage_link(search_results, query):
    """
    検索結果の中から最初にヒットしたリンクを返す
    search_results: 検索結果のリスト
    query: 検索クエリ
    """
    if search_results:
        first_item = search_results[0]

        return first_item.get("href")
    else:
        print(f"[INFO] -- NG")
        return "-"

def get_most_similar_link(search_results):
    """
    検索結果の中から類似度が最も高いリンクを返す
    :param search_results: 検索結果のリスト
    :param query: 検索クエリ
    :param similarity_limit: 類似度の閾値
    :return: 最も類似度が高いリンクまたは「-」
    """
    similarity_list = []

    for item in search_results:
        title = item.get("title", "")
        link = item.get("href", "")
        body = item.get("body", "")
        
        # 類似度計算
        # similarity = difflib.SequenceMatcher(None, similarity_keyword, title).ratio()
        similarity = calculate_similarity(similarity_keyword, title)

        if not link.endswith(('.pdf', '.xls', '.xlsx', '.doc', '.docx')):
            similarity_list.append((similarity, link))
    
    # 類似度の高い順にソート
    similarity_list.sort(reverse=True, key=lambda x: x[0])

    if similarity_list:
        print(f"[INFO][QUERY] {similarity_list[0]}")
        return similarity_list[0]

    return (0, "-")

def calculate_similarity(similarity_keyword, title):
    words = similarity_keyword.split()
    count = 0
    for word in words:
        # 各単語に対する最高の類似度を見つける
        max_ratio = max(difflib.SequenceMatcher(None, word, part).ratio() for part in title.split())
        # if max_ratio >= 0.2:
        count += max_ratio
    similarity = count / len(words)
    return similarity

if __name__ == "__main__":
    # 既存のCSVファイルを読み込む
    city_list = pd.read_csv("list.csv", encoding="shift-jis")
    org_support = pd.read_csv("support_organizations.csv", encoding="shift-jis")

    df_results = pd.read_csv("search_results_updated.csv", encoding="shift-jis")
    # search_results.csv: 最初から検索を行う
    # search_results_updated.csv: 既に検索を行った結果を読み込む場合

    # 対象のURLリストを読み込む
    target_url_list = pd.read_csv("target_url_list.csv", encoding="shift-jis")

    # 除外するURLリストを読み込む
    exception_url_list = pd.read_csv("exception_url_list.csv", encoding="shift-jis")

    # 検索が必要な項目を更新
    for index1, row1 in city_list.iterrows():
        print(f"[INFO] {row1['city']} {row1['town']}")

        for index2, row2 in org_support.iterrows():
            # 検索結果を格納するカラム(CSV欄)名
            org = f"{row2['department']} {row2['support']}"

            # 検索クエリを作成参考 {'能登半島地震'}
            keyword1 = '能登半島地震'
            keyword2 = '地震'
            keyword3 = '令和６年'

            # 類似度キーワード
            similarity_keyword = f"{row1['town']} {row2['department']} {row2['support']} {keyword1}"

            if pd.isna(df_results.at[index1, org]) or df_results.at[index1, org] == "-":

                try:
                    # 検索結果を格納するリスト
                    linkList = []

                    link = (0, "-")
                    # 市内で検索を3回実行
                    if link[0] <= similarity_limit:
                        query = f"{row1['portal']} {row2['department']} {row2['support']} {keyword2}"
                        search_results = duckduckgo_search(query, "", False, False)
                        link = get_most_similar_link(search_results) 
                        linkList.append(link)

                        query = f"{row1['portal']} {row2['department']} {row2['support']} {keyword1}"
                        search_results = duckduckgo_search(query, "", False, False)
                        link = get_most_similar_link(search_results) 
                        linkList.append(link)

                        query = f"{row1['portal']} {row2['support']}"
                        search_results = duckduckgo_search(query, "", False, False)
                        link = get_most_similar_link(search_results) 
                        linkList.append(link)

                        # query = f"{row1['portal']} {row2['support']}"
                        # search_results = duckduckgo_search(query, "", False, False)
                        # link = get_most_similar_link(search_results) 
                        # linkList.append(link)
                        # print(f"[INFO] {link}")

                    # if link[0] <= similarity_limit:
                    #     query = f"{row1['portal']} {row2['department']} {row2['support']} {keyword2}"
                    #     search_results = duckduckgo_search(query, row1['portal'], False, False)
                    #     link = get_most_similar_link(search_results) 
                    #     linkList.append(link)
                    #     print(f"[INFO] {link}")

                    # if link[0] <= similarity_limit:
                    #     query = f"{row1['portal']} {row2['department']}"
                    #     search_results = duckduckgo_search(query, row1['portal'], False, False)
                    #     link = get_most_similar_link(search_results) 
                    #     linkList.append(link)
                    #     print(f"[INFO] {link}")

                    # 県内で検索を実行 city_portal
                    # if link[0] <= similarity_limit:
                    #     query = f"{row1['city_portal']} {row2['support']} {keyword1}"
                    #     search_results = duckduckgo_search(query, "", False, False)
                    #     link = get_most_similar_link(search_results) 
                    #     linkList.append(link)
                    #     print(f"[INFO] {link}")

                    # 全サイト検索を実行
                    # if link[0] <= similarity_limit:
                    #     query = f"{row1['city']} {row1['town']} {row2['department']}{row2['support']} {keyword1}"
                    #     search_results = duckduckgo_search(query, "", False, False)
                    #     link = get_most_similar_link(search_results) 
                    #     linkList.append(link)
                    #     print(f"[INFO] {link}")

                    # if link[0] <= similarity_limit:
                    #     query = f"{row1['city']} {row1['town']} {row2['support']} {row2['department']} {keyword1}"
                    #     search_results = duckduckgo_search(query, "", False, False)
                    #     link = get_most_similar_link(search_results) 
                    #     linkList.append(link)
                    #     print(f"[INFO] {link}")
                    
                    linkList.sort(reverse=True, key=lambda x: x[0])
                    if linkList[0][0] < similarity_limit:
                        # 県内で検索を実行
                        query = f"{row1['city_portal']} {row1['town']} {row2['support']}"
                        search_results = duckduckgo_search(query, "", False, False)
                        link = get_most_similar_link(search_results) 
                        linkList.append(link)
                        linkList.sort(reverse=True, key=lambda x: x[0])

                    if linkList[0][0] < similarity_limit:
                        # 全サイトで検索を実行
                        query = f"{row1['city']} {row1['town']} {row2['department']} {row2['support']}"
                        search_results = duckduckgo_search(query, "", False, False)
                        link = get_most_similar_link(search_results) 
                        linkList.append(link)
                        linkList.sort(reverse=True, key=lambda x: x[0])

                    df_results.at[index1, org] = linkList[0][1]
 
                    print(f"[INFO] Updated: {org} -> {'{0:.2}'.format(linkList[0][0])} {linkList[0][1]}")
                    
                    # 更新されたDataFrameをCSVに保存
                    df_results.to_csv("search_results_updated.csv", index=False, encoding="shift-jis")

                    print(f"[INFO] {'-'*20}")

                except Exception as e:
                    print(f"[ERROR] {e}")

    print(f"[INFO] 更新が完了しました。")