import requests


def download_data(file_name):
    url = "https://work.mma.go.kr/caisBYIS/search/downloadBYJJEopCheExcel.do"
    data = {"eopjong_gbcd": "2", "al_eopjong_gbcd": "", "eopjong_gbcd_list": ""}
    response = requests.post(url, data=data)
    with open(file_name, "wb") as file:
        file.write(response.content)
