import json
import os
from datetime import datetime

import pandas as pd
import requests
from src import download_data, vis_data


def _send_discord_message(content):
    data = {"content": content}
    headers = {"Content-Type": "application/json"}
    response = requests.post(
        os.environ.get("WEBHOOK"), data=json.dumps(data), headers=headers
    )
    return response


if __name__ == "__main__":
    try:
        # ----- NOTE: [Data Download & Load] ----- #
        now = datetime.now()
        ymd = now.strftime("%Y%m%d")
        file_name = f"병역지정업체검색_{ymd}.xls"
        download_data(file_name)
        data = pd.read_excel(file_name)

        # ----- NOTE: [전체 전문연구요원] ----- #
        vd = vis_data(file_name, data, 0)
        vd.time_tsv()
        vd.pie_hist("연구분야", 3)
        vd.pie_hist("지방청", 3)
        vd.pie_hist("업종", 3)
        vd.pie_hist("위치", 2)
        vd.rank_vis("복무인원")
        vd.rank_vis("편입인원")
        vd.rank_readme()
        vd.plot_time()

        # ----- NOTE: [석사 전문연구요원] ----- #
        vd = vis_data(file_name, data, 1)
        vd.pie_hist("연구분야", 3)
        vd.pie_hist("지방청", 3)
        vd.pie_hist("위치", 2)
        vd.rank_vis("복무인원")
        vd.rank_vis("편입인원")
        vd.rank_readme()

        # ----- NOTE: [박사 전문연구요원] ----- #
        vd = vis_data(file_name, data, 2)
        vd.pie_hist("연구분야", 3)
        vd.pie_hist("지방청", 3)
        vd.pie_hist("위치", 2)
        vd.rank_vis("복무인원")
        vd.rank_vis("편입인원")
        vd.rank_readme()

    except Exception as e:
        print(e)
        _send_discord_message(
            ":warning:" * 10
            + "ERROR!!!"
            + ":warning:" * 10
            + "\n"
            + "Awesome JMY\n"
            + "```\n"
            + str(e)
            + "\n```",
        )
