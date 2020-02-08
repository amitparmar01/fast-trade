import zipfile
import os
import csv
import json
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()
# flake8: noqa
# this is a mess


def load_ohlcv_file(pair):
    csv_filename = f"{pair}.csv.zip"
    csv_base = f"{pair}.csv"
    # csv_path = os.path.join(os.getenv("CSV_PATH"), csv_filename)
    remove_csv = False
    if not os.path.isfile(csv_path):
        # check for a zip
        if os.path.isfile("{}.zip".format(csv_path)):
            with zipfile.ZipFile("{}.zip".format(csv_path), "r") as zip_file:
                zip_file.extractall(csv_base)
            remove_csv = True
    return


def create_run_summary_file(log_path, strategy, run_start, run_stop):
    run_sum = {
        "total_time": str(run_stop - run_start),
        "start": run_start.strftime("%m/%d/%Y %H:%M:%S"),
        "stop": run_stop.strftime("%m/%d/%Y %H:%M:%S"),
        "strategy": strategy,
        "pairs": pairs,
    }

    run_sum_path = os.path.join(log_path, "RunSummary.json")
    with open(run_sum_path, "w+") as new_run_log:
        new_run_log.write(json.dumps(run_sum, indent=2))


def create_status_file(pair, run_start, pairs):
    csv_filename = "{}.csv".format(pair)
    time_elapsed = datetime.datetime.utcnow() - run_start

    status = {
        "current_pair": pair,
        "current_location": pairs.index(pair) + 1,
        "total_pairs": len(pairs),
        "time_elapsed": str(time_elapsed),
    }

    status_path = os.path.join(log_path, "status.json")
    with open(status_path, "w+") as status_file:
        status_file.write(json.dumps(status))


def create_log_dir():
    run_dir_name = "run_{}".format(run_start.strftime("%m_%d_%Y_%H_%M_%S"))
    log_path = os.path.join(log_path, run_dir_name)
    if not os.path.isdir(log_path):
        os.mkdir(log_path)
    return True


def save_log_file(df, pair, log_path):
    strat_name = strategy.get("name").replace(" ", "")
    log_filename = "{}_log.csv".format(pair)

    strat_filename = "{}_strat.json".format(strat_name)

    with open(os.path.join(log_path, strat_filename), "w+") as strat_file:
        strat_file.write(json.dumps(strategy, indent=3))

    new_logpath = os.path.join(log_path, log_filename)

    # summary["log_file"] = new_logpath + ".zip"

    with open(new_logpath, "w") as new_logfile:
        file_writer = csv.writer(
            new_logfile, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL
        )
        file_writer.writerows(log)

    with zipfile.ZipFile(f"{new_logpath}.zip", "w") as log_zip:
        log_zip.write(
            new_logpath, compress_type=zipfile.ZIP_DEFLATED, arcname=log_filename,
        )

    os.remove(new_logpath)


def build_log_dataframe(log, symbol):
    load_dotenv()
    csv_path = os.getenv("CSV_PATH")
    csv_filename = f"{csv_path}{symbol}.csv"
    csv_zipfilename = f"{csv_path}{symbol}.csv.zip"
    # print("zipfilename: ",csv_filename)
    if os.path.isfile(csv_zipfilename):
        with zipfile.ZipFile(csv_zipfilename, "r") as zip_ref:
            zip_ref.extractall(f"{symbol}.csv")

    # print(csv_filename)


def read_logfile(log_filepath):
    arc_name = log_filepath.split("/")[-1].split(".zip")[0]

    unzipped_path = "/".join(log_filepath.split("/")[:-1])
    unzipped_file = f"{unzipped_path}/{arc_name}"
    if not os.path.isfile(unzipped_file):
        with zipfile.ZipFile(log_filepath, "r") as zip_ref:
            zip_ref.extractall(unzipped_path)

    with open(unzipped_file, "r") as opened_file:
        log = csv.reader(opened_file, delimiter=",")
        logs = list(log)

    return logs


def process_run_path(run_obj):
    # get the log file
    # buid the real path
    for log_obj in run_obj:
        for pair in log_obj["pairs"]:
            pair_obj = log_obj["pairs"][pair]
            log_filepath = f"{log_obj['base_path']}{pair_obj['log']}"
            # call the analysis function
            print(log_filepath)


def get_log_files(log_path):
    run_paths = []
    for run in os.listdir(log_path):
        base_path = f"{log_path}{run}/"
        log_obj = {
            "base_path": base_path,
            "RunSummary": None,
            "strat": None,
            "pairs": {},
        }
        if os.path.isdir(base_path):
            # this is each file in the base path
            for run_file in os.listdir(base_path):
                if run_file == "RunSummary.json":
                    log_obj["RunSummary"] = run_file
                if "_strat" in run_file:
                    log_obj["strat"] = run_file

                # symbol specific stuff
                symbol = run_file.split("_log")[0]
                if "_log" in run_file:
                    if log_obj["pairs"].get(symbol):
                        log_obj["pairs"][symbol]["log"] = run_file
                    else:
                        log_obj["pairs"][symbol] = {}
                        log_obj["pairs"][symbol]["log"] = run_file

                if "_sum" in run_file:
                    symbol = run_file.split("_sum")[0]
                    if log_obj["pairs"].get(symbol):
                        log_obj["pairs"][symbol]["sum"] = run_file
                    else:

                        log_obj["pairs"][symbol] = {}
                        log_obj["pairs"][symbol]["sum"] = run_file
            run_paths.append(log_obj)

    return run_paths


if __name__ == "__main__":
    # log_filepath = "./fast_trade/logs/run_01_17_2020_21_51_35/ZRXETH_log.csv"
    # log_path = "/Users/jedmeier/Projects/fast_trade/fast_trade/logs/"
    # res = anaylze(log_filepath)

    # res = get_log_files(log_path)
    # print(json.dumps(res, indent=2))
    # run_paths = [
    #     {
    #     "base_path": "/Users/jedmeier/Projects/fast_trade/fast_trade/logs/run_01_20_2020_22_21_27/",
    #     "RunSummary": "RunSummary.json",
    #     "strat": "example_strat.json",
    #     "pairs": {
    #     "ADABNB": {
    #         "sum": "ADABNB_sum.json",
    #         "log": "ADABNB_log.csv.zip"
    #     }
    #     }
    #     }
    # ]
    # res = process_run_path(run_paths)
    # log_file_path = "/Users/jedmeier/Projects/fast_trade/fast_trade/logs/run_01_20_2020_22_21_27/ADABNB_log.csv.zip" # noqa
    # res = read_logfile(log_file_path)

    res = build_log_dataframe("lol", "BTCUSDT")
