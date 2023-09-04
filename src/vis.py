import os
from glob import glob

import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt


class vis_data:
    def __init__(self, file_name, data, degree):
        self.time = file_name[-12:-4]
        self.data = data
        """
        NOTE: "벤처기업부설연구소", "중견기업부설연구소", "중소기업부설연구소"를 제외한 모든 업종은 박사 전문연구요원으로 간주
        과기원
        과기원부설연구소
        국가기관 등 연구소
        기초연구연구기관
        대기업부설연구소
        대학원연구기관
        방산연구기관
        벤처기업부설연구소
        자연계대학부설연구기관
        정부출연연구소
        중견기업부설연구소
        중소기업부설연구소
        지역혁신센터연구소
        특정연구소
        """
        os.makedirs("prop", exist_ok=True)
        DIR_NAME = ["ALL", "MS", "PhD"]
        self.degree = DIR_NAME[degree]
        self.dir = os.path.join("prop", DIR_NAME[degree])
        os.makedirs(self.dir, exist_ok=True)
        if degree == 1:
            self.data = self.data[
                (self.data["업종"] == "벤처기업부설연구소")
                | (self.data["업종"] == "중견기업부설연구소")
                | (self.data["업종"] == "중소기업부설연구소")
            ]
        elif degree == 2:
            self.data = self.data[
                ~(
                    (self.data["업종"] == "벤처기업부설연구소")
                    | (self.data["업종"] == "중견기업부설연구소")
                    | (self.data["업종"] == "중소기업부설연구소")
                )
            ]
        self.data["위치"] = (
            self.data["주소"]
            .str.replace("서울특별시 ", "서울특별시")
            .str.replace("경기도 ", "경기도")
            .str.split(" ")
            .str[0]
            .str.replace("서울특별시", "서울특별시 ")
            .str.replace("경기도", "경기도 ")
        )
        self.ranked_data_org = self.data.sort_values(
            by=["현역 복무인원", "현역 편입인원", "업체명"], ascending=[False, False, True]
        ).iloc[:, [1, 14, 15, 16]]
        self.ranked_data_new = self.data.sort_values(
            by=["현역 편입인원", "현역 복무인원", "업체명"], ascending=[False, False, True]
        ).iloc[:, [1, 14, 15, 16]]
        plt.rcParams["font.size"] = 15
        plt.rcParams["font.family"] = "Do Hyeon"

    def time_tsv(self):
        with open(f"{self.dir}/time.tsv", "a") as f:
            for name, _, a, b in self.ranked_data_org.values:
                f.writelines(f"{self.time}\t{name}\t{a}\t{b}\n")

    def pie_hist(self, tar, threshold=3):
        field_counts = self.data[tar].value_counts()
        large_parts = field_counts[field_counts / len(self.data) * 100 >= threshold]
        small_parts = field_counts[field_counts / len(self.data) * 100 < threshold]
        large_parts_labels = [
            f"{i} ({v})" for i, v in zip(large_parts.index, large_parts.values)
        ]
        plt.figure(figsize=(30, 10))
        plt.subplot(1, 2, 1)
        colors = sns.color_palette("coolwarm", n_colors=len(large_parts))[::-1]
        plt.pie(
            large_parts,
            labels=large_parts_labels,
            autopct="%1.1f%%",
            startangle=90,
            radius=1,
            colors=colors,
        )
        plt.title(f"{threshold}% 이상 {tar} 분포", fontsize=25)
        plt.subplot(1, 2, 2)
        plt.grid(zorder=0)
        small_parts = small_parts[:15]
        colors = sns.color_palette("Spectral", n_colors=len(small_parts))
        bars = plt.bar(
            small_parts.index,
            small_parts.values,
            color=colors[: len(small_parts)],
            zorder=2,
        )
        for bar in bars:
            height = bar.get_height()
            percentage = (height / len(self.data)) * 100
            plt.text(
                bar.get_x() + bar.get_width() / 2,
                height,
                f"{percentage:.1f}%",
                ha="center",
                va="bottom",
            )
        plt.xlabel(tar)
        plt.ylabel("빈도")
        plt.xticks(small_parts.index, rotation=45)
        plt.title(f"{threshold}% 미만 {tar} 분포", fontsize=25)
        plt.savefig(f"{self.dir}/{tar}.png", dpi=300, bbox_inches="tight")

    def rank_vis(self, by="현역 복무인원", top=30):
        plt.figure(figsize=(10, int(0.6 * top)))
        plt.grid(zorder=0)
        colors = sns.color_palette("coolwarm", n_colors=top)
        if by == "현역 복무인원":
            bars = plt.barh(
                self.ranked_data_org["업체명"][:top][::-1],
                self.ranked_data_org[by][:top][::-1],
                color=colors,
                zorder=2,
            )
        elif by == "현역 편입인원":
            bars = plt.barh(
                self.ranked_data_new["업체명"][:top][::-1],
                self.ranked_data_new[by][:top][::-1],
                color=colors,
                zorder=2,
            )
        MAX = bars[-1].get_width()
        for bar in bars:
            width = bar.get_width()
            plt.text(
                width + MAX * 0.01,
                bar.get_y() + bar.get_height() / 4,
                f"{width}명",
                ha="left",
                va="bottom",
            )
        plt.xlabel(by)
        plt.ylabel("업체명")
        plt.xlim([0, MAX * 1.1])
        plt.title(f"{by} TOP {top}", fontsize=25)
        plt.savefig(
            f"{self.dir}/TOP_{top}_{by.replace(' ', '_')}.png",
            dpi=300,
            bbox_inches="tight",
        )

    def rank_readme(self, top=300):
        with open(f"{self.dir}/README.md", "w") as f:
            f.writelines(
                f"<div align=center> <h1> :technologist: 전문연구요원 TOP {top} :technologist: </h1> </div>\n\n<div align=center>\n\n|업체명|현역 배정인원|현역 편입인원|현역 복무인원|\n|:-:|:-:|:-:|:-:|\n"
            )
            for name, a, b, c in self.ranked_data_org.values[:top]:
                f.writelines(f"|{name}|{a}|{b}|{c}|\n")
            f.writelines("\n</div>")

    # def plot_time(self, M=100, w=10):
    #     time_data = pd.read_csv(
    #         f"{self.dir}/time.tsv", sep="\t", header=None, encoding="utf-8"
    #     )


if __name__ == "__main__":
    # ----- NOTE: [Data Load] ----- #
    file_name = sorted(glob("data/*.xls"))[-1]
    data = pd.read_excel(file_name)

    # ----- NOTE: [전체 전문연구요원] ----- #
    vd = vis_data(file_name, data, 0)
    vd.pie_hist("연구분야", 3)
    vd.pie_hist("지방청", 3)
    vd.pie_hist("업종", 3)
    vd.pie_hist("위치", 2)
    vd.rank_vis("현역 복무인원")
    vd.rank_vis("현역 편입인원")
    vd.rank_readme()

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
