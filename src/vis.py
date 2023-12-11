import os
import warnings
from glob import glob

import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from matplotlib.ticker import MaxNLocator

warnings.filterwarnings("ignore")


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
        self.data["복무인원"] = self.data["보충역 복무인원"] + self.data["현역 복무인원"]
        self.data["편입인원"] = self.data["보충역 편입인원"] + self.data["현역 편입인원"]
        self.ranked_data_org = self.data.sort_values(
            by=["복무인원", "업체명"], ascending=[False, True]
        ).loc[
            :,
            [
                "업체명",
                "보충역 배정인원",
                "보충역 편입인원",
                "보충역 복무인원",
                "현역 배정인원",
                "현역 편입인원",
                "현역 복무인원",
            ],
        ]
        self.ranked_data_new = self.data.sort_values(
            by=["편입인원", "업체명"], ascending=[False, True]
        ).loc[
            :,
            [
                "업체명",
                "보충역 배정인원",
                "보충역 편입인원",
                "보충역 복무인원",
                "현역 배정인원",
                "현역 편입인원",
                "현역 복무인원",
            ],
        ]
        plt.rcParams["font.size"] = 15
        plt.rcParams["font.family"] = "Do Hyeon"
        self.color_hist = {
            "보충역 편입인원": "#6060ff",
            "보충역 복무인원": "#c0c0f0",
            "현역 편입인원": "#ff6060",
            "현역 복무인원": "#f0c0c0",
        }
        self.color_plot = {
            "보충역 편입인원": "#c0c0f0",
            "보충역 복무인원": "#6060ff",
            "현역 편입인원": "#f0c0c0",
            "현역 복무인원": "#ff6060",
        }

    def time_tsv(self):
        print("WRITE TIME SERIES TSV")
        with open(f"prop/time.tsv", "a") as f:
            for name, _, a, b, _, c, d in self.ranked_data_org.values:
                f.writelines(f"{self.time}\t{name}\t{a}\t{b}\t{c}\t{d}\n")

    def pie_hist(self, tar, threshold=3):
        print("PLOT PIE & HIST:\t", tar)
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

    def rank_vis(self, by="복무인원", top=30):
        print("PLOT RANK:\t", by)
        plt.figure(figsize=(10, int(0.6 * top)))
        plt.grid(zorder=0)
        if by == "복무인원":
            bars_l = plt.barh(
                self.ranked_data_org["업체명"][:top][::-1],
                self.ranked_data_org["현역 복무인원"][:top][::-1],
                color=self.color_hist["현역 복무인원"],
                zorder=2,
                label="현역 복무인원",
            )
            plt.barh(
                self.ranked_data_org["업체명"][:top][::-1],
                self.ranked_data_org["현역 편입인원"][:top][::-1],
                color=self.color_hist["현역 편입인원"],
                zorder=2,
                label="현역 편입인원",
            )
            bars_r = plt.barh(
                self.ranked_data_org["업체명"][:top][::-1],
                self.ranked_data_org["보충역 복무인원"][:top][::-1],
                color=self.color_hist["보충역 복무인원"],
                zorder=2,
                left=self.ranked_data_org["현역 복무인원"][:top][::-1],
                label="보충역 복무인원",
            )
            plt.barh(
                self.ranked_data_org["업체명"][:top][::-1],
                self.ranked_data_org["보충역 편입인원"][:top][::-1],
                color=self.color_hist["보충역 편입인원"],
                zorder=2,
                left=self.ranked_data_org["현역 복무인원"][:top][::-1],
                label="보충역 편입인원",
            )
        elif by == "편입인원":
            bars_l = plt.barh(
                self.ranked_data_new["업체명"][:top][::-1],
                self.ranked_data_new["현역 편입인원"][:top][::-1],
                color=self.color_hist["현역 편입인원"],
                zorder=2,
                label="현역 편입인원",
            )
            bars_r = plt.barh(
                self.ranked_data_new["업체명"][:top][::-1],
                self.ranked_data_new["보충역 편입인원"][:top][::-1],
                color=self.color_hist["보충역 편입인원"],
                zorder=2,
                left=self.ranked_data_new["현역 편입인원"][:top][::-1],
                label="보충역 편입인원",
            )
        plt.legend(loc='lower right')
        MAX = bars_l[-1].get_width() + bars_r[-1].get_width()
        for l, r in zip(bars_l, bars_r):
            width_l = l.get_width()
            width_r = r.get_width()
            plt.text(
                width_l + width_r + MAX * 0.01,
                l.get_y() + l.get_height() / 4,
                f"{width_l + width_r}명",
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

    def rank_readme(self, top=0):
        print("WRITE README.md")
        with open(f"{self.dir}/README.md", "w") as f:
            if top == 0:
                f.writelines(
                    f"<div align=center> <h1> 🧑‍💻 전문연구요원 복무인원 순위 🧑‍💻 </h1> </div>\n\n<div align=center>\n\n|업체명|보충역 배정인원|보충역 편입인원|보충역 복무인원|현역 배정인원|현역 편입인원|현역 복무인원|\n|:-:|:-:|:-:|:-:|:-:|:-:|:-:|\n"
                )
                for name, a1, a2, a3, b1, b2, b3 in self.ranked_data_org.values:
                    f.writelines(
                        f"|[{name}](https://github.com/Zerohertz/awesome-jmy/blob/main/prop/time/{name.replace('(', '').replace(')', '').replace('/', '').replace(' ', '')}.png)|{a1}|{a2}|{a3}|{b1}|{b2}|{b3}|\n"
                    )
            else:
                f.writelines(
                    f"<div align=center> <h1> 🧑‍💻 전문연구요원 복무인원 순위 TOP {top} 🧑‍💻 </h1> </div>\n\n<div align=center>\n\n|업체명|보충역 배정인원|보충역 편입인원|보충역 복무인원|현역 배정인원|현역 편입인원|현역 복무인원|\n|:-:|:-:|:-:|:-:|:-:|:-:|:-:|\n"
                )
                for name, a1, a2, a3, b1, b2, b3 in self.ranked_data_org.values:
                    f.writelines(
                        f"|[{name}](https://github.com/Zerohertz/awesome-jmy/blob/main/prop/time/{name.replace('(', '').replace(')', '').replace('/', '').replace(' ', '')}.png)|{a1}|{a2}|{a3}|{b1}|{b2}|{b3}|\n"
                    )
            f.writelines("\n</div>")

    def plot_time(self):
        os.makedirs(f"prop/time", exist_ok=True)
        time_data = pd.read_csv(
            f"prop/time.tsv", sep="\t", header=None, encoding="utf-8"
        )
        for name in time_data.iloc[:, 1].unique():
            print("PLOT TIME SERIES:\t", name)
            self._plot(time_data, name)
            plt.savefig(
                f"prop/time/{name.replace('(', '').replace(')', '').replace('/', '').replace(' ', '')}.png",
                dpi=100,
                bbox_inches="tight",
            )
            plt.close("all")

    def _plot(self, data, name):
        tmp = data[data.iloc[:, 1] == name]
        x, y1, y2, y3, y4 = (
            pd.to_datetime(tmp.iloc[:, 0], format="%Y%m%d"),
            tmp.iloc[:, 2],
            tmp.iloc[:, 3],
            tmp.iloc[:, 4],
            tmp.iloc[:, 5],
        )
        _, ax = plt.subplots(figsize=(20, 10))
        plt.grid()
        plt.xlabel("Time")
        plt.ylabel("인원 [명]")
        plt.plot(
            x,
            y4,
            color=self.color_plot["현역 복무인원"],
            linestyle="-.",
            linewidth=2,
            marker="v",
            markersize=12,
            label="현역 복무인원",
        )
        plt.plot(
            x,
            y3,
            color=self.color_plot["현역 편입인원"],
            linestyle="--",
            linewidth=2,
            marker="o",
            markersize=12,
            label="현역 편입인원",
        )
        plt.plot(
            x,
            y2,
            color=self.color_plot["보충역 복무인원"],
            linestyle="-.",
            linewidth=2,
            marker="v",
            markersize=12,
            label="보충역 복무인원",
        )
        plt.plot(
            x,
            y1,
            color=self.color_plot["보충역 편입인원"],
            linestyle="--",
            linewidth=2,
            marker="o",
            markersize=12,
            label="보충역 편입인원",
        )
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        try:
            m1 = self.data[self.data["업체명"] == name]["보충역 배정인원"].iloc[0]
            m2 = self.data[self.data["업체명"] == name]["현역 배정인원"].iloc[0]
            plt.title(f"{name}\n(보충역 배정인원: {m1}명, 현역 배정인원: {m2}명)")
        except:
            plt.title(f"{name}\n(배정인원: X)")
        plt.legend(loc='lower right')


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
