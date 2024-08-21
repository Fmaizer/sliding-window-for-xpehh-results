#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd  
import numpy as np  
from tqdm import tqdm
import argparse

def normalize_and_window_statistics_xpehh(input,window, step, chr):
    """
    由于selscan的norm窗口统计不能滑窗统计，这里写一个连同标准化和滑窗统
    计一起做了，这里舍弃了原来norm的第7、8列的百分位数的统计。输出结果
    解读如下：
    chr: 染色体
    win_start:  窗口起始
    win_end: 窗口结束
    nSNPs: 窗口里的snp数量
    ratio_gt2: 大于标准化后normxpehh阈值2的标记占整个窗口的比例
    ratio_lt2: 小于于标准化后normxpehh阈值-2的标记占整个窗口的比例
    mean_normxpehh: 窗口内normxpehh均值
    median_normxpehh: 窗口内normxpehh中位数
    max_normxpehh: 窗口内normxpehh最大值
    min_normxpehh: 窗口内normxpehh最小值
    """
    # 读取数据
    data = pd.read_csv(input, sep="\t")  
  
    # 删除包含NA的行
    data = data.dropna() 

    # 对原来的xpehh列进行标准化，并对显著的SNP进行标记（大于2记为1，小于-2记为-1，其余为0）
    data["normxpehh"] = (data["xpehh"] - data["xpehh"].mean()) / data["xpehh"].std()
    data["crit"] = data["normxpehh"].apply(lambda x: 1 if x > 2 else (-1 if x < -2 else 0))
    # print(data)

    # 初始化列表来收集结果行的字典
    result_list = []  

    # 滑动窗口计算normxpehh在各个窗口的各个统计值
    for start in tqdm(range(1, data["pos"].max(), step)):  
        end = start + window -1  
        window_data = data[(data["pos"] >= start) & (data["pos"] <= end)]  

        if not window_data.empty:  
            result_dict = {  
                "chr": chr,  
                "win_start": start,  
                "win_end": end,  
                "nSNPs": window_data["pos"].count(),  
                "ratio_gt2": np.mean(window_data["normxpehh"] > 2),   # 利用计算布尔值的均值，就相当于计算比例了
                "ratio_lt2": np.mean(window_data["normxpehh"] < -2),  
                "mean_normxpehh": window_data["normxpehh"].mean(),  
                "median_normxpehh": window_data["normxpehh"].median(),  
                "max_normxpehh": window_data["normxpehh"].max(),  
                "min_normxpehh": window_data["normxpehh"].min()  
            }  
            result_list.append(result_dict)  

    # 使用列表推导式和 pd.DataFrame 构造器一次性创建 DataFrame  
    result = pd.DataFrame(result_list)  

    # 输出结果  
    # print(result)  
    data.to_csv(f"{input}.norm",sep="\t", index=False)
    result.to_csv(f"{input}.norm.{int(window/1000)}kb.windows", sep="\t", index=False)
    


def main():
    # 创建解析步骤
    parser = argparse.ArgumentParser(description="For normalizing and window statistics of XPEHH results")
    parser.add_argument("--input", required=True, help="Input file (required, xpehh result)")
    parser.add_argument("--window", type=int, default=20000, help="window size (default 20000)")
    parser.add_argument("--step", type=int, default=10000, help="step size (default 10000)")
    parser.add_argument("--chr", required=True,help="Chromosome number (required, e.g., 10/chr10)")
    # 解析参数
    args = parser.parse_args()

    # 打印命令
    print(f'Running command: \npython {__file__} --input {args.input} --window {args.window} --step {args.step} --chr {args.chr}')
    
    input = args.input
    window = args.window
    step = args.step
    chr = args.chr 

    # 运行程序
    normalize_and_window_statistics_xpehh(input,window,step,chr)



if __name__ == "__main__":
    main()