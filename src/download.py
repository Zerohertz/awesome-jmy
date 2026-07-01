import os
import time

import requests

URL = "https://work.mma.go.kr/caisBYIS/search/downloadBYJJEopCheExcel.do"
DATA = {"eopjong_gbcd": "2", "al_eopjong_gbcd": "", "eopjong_gbcd_list": ""}
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/125.0.0.0 Safari/537.36"
    ),
    "Referer": "https://work.mma.go.kr/caisBYIS/search/byjjeopche.do",
}
# 정상 응답은 OLE2 Compound File(.xls) 형식으로 시작한다.
XLS_MAGIC = b"\xd0\xcf"


def download_data(file_name, retries=3, timeout=30):
    # 한국 외 네트워크(예: GitHub Actions)에서 실행 시 KR 프록시를 지정하면
    # work.mma.go.kr 의 IP 차단을 우회할 수 있다. (예: MMA_PROXY=http://host:port)
    proxy = os.environ.get("MMA_PROXY")
    proxies = {"http": proxy, "https": proxy} if proxy else None

    last_exc = None
    for attempt in range(1, retries + 1):
        try:
            response = requests.post(
                URL, data=DATA, headers=HEADERS, timeout=timeout, proxies=proxies
            )
            response.raise_for_status()
            content = response.content
            if content[:2] != XLS_MAGIC:
                raise ValueError(
                    f"Unexpected response (not an .xls file): {len(content)} bytes "
                    f"starting with {content[:16]!r}"
                )
            with open(file_name, "wb") as file:
                file.write(content)
            return file_name
        except (requests.RequestException, ValueError) as exc:
            last_exc = exc
            if attempt < retries:
                time.sleep(2**attempt)

    raise RuntimeError(
        f"Failed to download from {URL} after {retries} attempts. "
        "work.mma.go.kr blocks non-KR / datacenter IPs, so this must run from a "
        "Korean network (self-hosted runner, KR VPS, or via MMA_PROXY). "
        f"Last error: {last_exc}"
    ) from last_exc


if __name__ == "__main__":
    from datetime import datetime

    os.makedirs("data", exist_ok=True)
    ymd = datetime.now().strftime("%Y%m%d")
    out = os.path.join("data", f"병역지정업체검색_{ymd}.xls")
    download_data(out)
    print(f"Downloaded: {out}")
