"""
example

"""

# import requests
import pandas as pd
import difflib
from duckduckgo_search import DDGS
import time

similarity_limit = 0.35

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
        search_results = [r for r in ddgs.text(query, max_results=10)]

    for result in search_results:

        # 検索対象のURLを含む場合は抽出
        if url and url in result["href"]:
            results.append(result)
            break

        # 除外リストのURLを含む場合はスキップ
        if exception_flg:
            if any(item in result["href"] for item in exception_url_list['url']):
                continue

        # 対象リストに含まれるURLの場合のみ抽出
        if target_flg:
            if any(item in result["href"] for item in target_url_list['url']):
                results.append(result)

    return results

def get_valid_webpage_link(search_results, query):
    """
    検索結果の中から最初にヒットしたリンクを返す
    search_results: 検索結果のリスト
    query: 検索クエリ
    """
    if search_results:
        first_item = search_results[0]
        title = first_item.get("title", "")

        # 類似度のチェック
        # similarity = difflib.SequenceMatcher(None, query, title).ratio()
        # if similarity < similarity_limit:
        #     print(f"[INFO] -- NG {similarity} {first_item.get('href')}")
        #     return "-"

        return first_item.get("href")
    else:
        print(f"[INFO] -- NG")
        return "-"

def get_most_similar_link(search_results, query):
    """
    検索結果の中から類似度が最も高いリンクを返す
    search_results: 検索結果のリスト
    query: 検索クエリ
    """
    similarity_list = []

    if search_results:
        for item in search_results:
            title = item.get("title", "")
            link = item.get("href", "")

            # 類似度の計算
            similarity = difflib.SequenceMatcher(None, query, title).ratio()

            # 特定のファイル形式のリンクを除外
            if not link.endswith(('.pdf', '.xls', '.xlsx', '.doc', '.docx')):
                similarity_list.append((similarity, link))

        # 類似度に基づいてソート
        similarity_list.sort(reverse=True, key=lambda x: x[0])

        if similarity_list:
            # 類似度の値
            print(f"[INFO] Similarity: {similarity_list[0][0]}")
            if similarity_list[0][0] < similarity_limit:
                print(f"[INFO] -- NG {similarity_list[0][1]}")
                return "-"
            # 最も類似度が高いリンクを返す
            return similarity_list[0][1]
    
    print(f"[INFO] -- NG")
    return "-"


if __name__ == "__main__":
    # 既存のCSVファイルを読み込む
    city_list = pd.read_csv("list.csv", encoding="shift-jis")
    org_support = pd.read_csv("support_organizations.csv", encoding="shift-jis")

    df_results = pd.read_csv("google_search_results.csv", encoding="shift-jis")
    # google_search_results.csv: 最初から検索を行う
    # google_search_results_updated.csv: 既に検索を行った結果を読み込む場合

    # 対象のURLリストを読み込む
    target_url_list = pd.read_csv("target_url_list.csv", encoding="shift-jis")

    # 除外するURLリストを読み込む
    exception_url_list = pd.read_csv("exception_url_list.csv", encoding="shift-jis")

    # 検索が必要な項目を更新
    for index1, row1 in city_list.iterrows():
        print(f"[INFO] {row1['city']} {row1['town']}")

        for index2, row2 in org_support.iterrows():
            org = f"{row2['department']} {row2['support']}"

            if pd.isna(df_results.at[index1, org]) or df_results.at[index1, org] == "-":
                query = f"{row2['support']} " # 検索クエリを作成 {row['city']} {'能登半島地震'}

                try:
                    # 1 回目の検索
                    search_results = duckduckgo_search(query, row1['portal'], False, False)
                    # link = get_most_similar_link(search_results, query) # 類似度の高いリンクを取得
                    link = get_valid_webpage_link(search_results, query) # 最初にヒットしたリンクを取得
                    
                    # 2 回目の検索
                    if link == "-":
                        # print(f"[INFO] ------- Not found. Retrying...")
                        new_query = f"{row1['city']} {row1['town']} {org}"
                        search_results = duckduckgo_search(new_query, row1['portal'], False, False)
                        # link = get_most_similar_link(search_results, new_query) 
                        link = get_valid_webpage_link(search_results, query)
                    
                    # 3 回目の検索
                    if link == "-":
                        # print(f"[INFO] ------- Not found. Retrying...")
                        new_query = f"{row1['city']} {row1['town']} {org} {'能登半島地震'}"
                        search_results = duckduckgo_search(new_query, row1['portal'], False, False)
                        # link = get_most_similar_link(search_results, new_query) 
                        link = get_valid_webpage_link(search_results, query)

                    # 4 回目の検索
                    if link == "-":
                        # print(f"[INFO] ------- Not found. Retrying...")
                        new_query = f"{row1['city']} {row1['town']} {row2['support']}"
                        search_results = duckduckgo_search(new_query, "", False, True)
                        # link = get_most_similar_link(search_results, new_query) 
                        link = get_valid_webpage_link(search_results, query)
                    
                    # 5 回目の検索
                    if link == "-":
                        # print(f"[INFO] ------- Not found. Retrying...")
                        new_query = f"{row1['city']} {row1['town']} {row2['department']}"
                        search_results = duckduckgo_search(new_query, "", False, True)
                        # link = get_most_similar_link(search_results, new_query) 
                        link = get_valid_webpage_link(search_results, query)
                    
                    df_results.at[index1, org] = link
                    print(f"[INFO] Updated: {query} -> {link}")
                    # time.sleep(1)  # API/Server制限に注意
                    
                    # 更新されたDataFrameをCSVに保存
                    df_results.to_csv("google_search_results_updated.csv", index=False, encoding="shift-jis")

                except Exception as e:
                    print(f"[ERROR] {e}")

    print(f"[INFO] 更新が完了しました。")