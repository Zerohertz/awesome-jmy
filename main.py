from glob import glob

import pandas as pd
from src import download_data, vis_data

if __name__ == "__main__":
    try:
        # ----- NOTE: [Data Download & Load] ----- #
        dd = download_data()
        dd.main()
        file_name = glob("*.xls")[0]
        data = pd.read_excel(file_name)

        # ----- NOTE: [전체 전문연구요원] ----- #
        vd = vis_data(file_name, data, 0)
        vd.time_tsv()
        vd.pie_hist("연구분야", 3)
        vd.pie_hist("지방청", 3)
        vd.pie_hist("업종", 3)
        vd.pie_hist("위치", 2)
        vd.rank_vis("현역 복무인원")
        vd.rank_vis("현역 편입인원")
        vd.rank_readme()
        vd.plot_time()

        # ----- NOTE: [석사 전문연구요원] ----- #
        vd = vis_data(file_name, data, 1)
        vd.pie_hist("연구분야", 3)
        vd.pie_hist("지방청", 3)
        vd.pie_hist("위치", 2)
        vd.rank_vis("현역 복무인원")
        vd.rank_vis("현역 편입인원")
        vd.rank_readme()

        # ----- NOTE: [박사 전문연구요원] ----- #
        vd = vis_data(file_name, data, 2)
        vd.pie_hist("연구분야", 3)
        vd.pie_hist("지방청", 3)
        vd.pie_hist("위치", 2)
        vd.rank_vis("현역 복무인원")
        vd.rank_vis("현역 편입인원")
        vd.rank_readme()

    except Exception as e:
        dd._send_discord_message(
            ":warning:" * 10
            + "ERROR!!!"
            + ":warning:" * 10
            + "\n"
            + "Awesome JMY\n"
            + "```\n"
            + str(e)
            + "\n```",
        )
