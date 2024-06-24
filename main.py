from datetime import datetime

from src import DataLoader, download_data

if __name__ == "__main__":
    # ----- NOTE: [Data Download & Load] ----- #
    now = datetime.now()
    ymd = now.strftime("%Y%m%d")
    file_name = f"병역지정업체검색_{ymd}.xls"
    download_data(file_name)

    # ----- NOTE: [전체 전문연구요원] ----- #
    dataloader = DataLoader(file_name, 0)
    dataloader.time_tsv()
    dataloader.bar("연구분야")
    dataloader.bar("지방청")
    dataloader.bar("업종")
    dataloader.bar("위치")
    dataloader.rank_vis("복무인원")
    dataloader.rank_vis("편입인원")
    dataloader.rank_readme()
    dataloader.plot_time()

    # ----- NOTE: [석사 전문연구요원] ----- #
    dataloader = DataLoader(file_name, 1)
    dataloader.bar("연구분야")
    dataloader.bar("지방청")
    dataloader.bar("위치")
    dataloader.rank_vis("복무인원")
    dataloader.rank_vis("편입인원")
    dataloader.rank_readme()

    # ----- NOTE: [박사 전문연구요원] ----- #
    dataloader = DataLoader(file_name, 2)
    dataloader.bar("연구분야")
    dataloader.bar("지방청")
    dataloader.bar("위치")
    dataloader.rank_vis("복무인원")
    dataloader.rank_vis("편입인원")
    dataloader.rank_readme()
