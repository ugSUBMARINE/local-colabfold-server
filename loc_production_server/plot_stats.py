from __future__ import annotations
import numpy as np
import matplotlib.pyplot as plt
import argparse


def plot_server_usage(
    usage_data_hour: list[int],
    usage_data_month: list[int],
    months: list[str],
    storage_path: str,
):
    if len(usage_data_hour) != 24:
        raise ValueError("Hourly usage data must contain 24 values (one for each hour)")

    if len(usage_data_month) != len(months):
        raise ValueError("Monthly usage data and months must have the same length")

    _ = plt.figure(figsize=(5, 8), layout="tight")

    # Plot 1: Spider plot for hourly data
    angles = np.linspace(0, 2 * np.pi, 24, endpoint=False)
    values = np.concatenate((usage_data_hour, [usage_data_hour[0]]))
    angles = np.concatenate((angles, [angles[0]]))

    ax1 = plt.subplot(211, projection="polar")
    ax1.plot(angles, values, color="forestgreen", linewidth=3)
    ax1.fill(angles, values, alpha=0.5, color="firebrick")

    ax1.set_theta_offset(np.pi / 2)
    ax1.set_theta_direction(-1)
    ax1.set_xticks(np.linspace(0, 2 * np.pi, 24, endpoint=False))
    ax1.set_xticklabels([f"{i:02d}:00" for i in range(24)])
    ax1.set_title("Server Usage Over 24 Hours")

    # Plot 2: Line plot for monthly data
    ax2 = plt.subplot(212)
    ax2.plot(
        months,
        usage_data_month,
        marker="o",
        linestyle="-",
        color="royalblue",
        linewidth=2,
    )
    ax2.set_xlabel("Months")
    ax2.set_ylabel("Predictions")
    ax2.set_title("Monthly Server Usage")
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    plt.xticks(rotation=45)

    plt.tight_layout()
    plt.savefig(storage_path, dpi=150, transparent=True)


def get_stats(log_file: str, storage_path: str):
    dates = []
    clock = []
    with open(log_file, "r") as dfile:
        for i in dfile:
            if len(i) > 1:
                i_interest = i.split("~~")[1].split("-")
                dates.append("-".join(i_interest[0:2][::-1]))
                clock.append(int(i_interest[3]) + round(int(i_interest[4]) / 60))
    date, n_date = np.unique(dates, return_counts=True)
    date_dict = dict(zip(date, n_date))
    date = sorted(date, key=lambda x: (x.split("-")[1], x.split("-")[0]))
    n_date = [date_dict[i] for i in date]

    hours, n_hours = np.unique(clock, return_counts=True)
    target_hours = dict(zip(list(range(24)), [np.int64(0) for i in range(24)]))
    for h, nh in zip(hours, n_hours):
        target_hours[h] = nh
    usage24 = [target_hours[i] for i in range(24)]
    return usage24, n_date, date, storage_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", type=str, help="path to log file")
    parser.add_argument(
        "-o", "--output", type=str, help="path where the files should be stored"
    )
    args = parser.parse_args()

    plot_server_usage(*get_stats(args.input, args.output))
