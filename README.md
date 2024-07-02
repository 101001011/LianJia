# 链家爬虫

## 功能介绍

可以一键爬取某城市链家在售的二手房信息, 包括**标题**, **地址**, **户型**, **面积**, **朝向**, **楼层**, **建造时间**, **楼型**, **总价**, **每平米单价**, **图片**和**原链接**. 

详见 `AppData/information` 文件夹中的 `.csv` 文件和 `.json` 文件.

## 依赖

本项目由 `Python` 实现, 需要导入的包有 `time`, `random`, `os`, `json`, `csv`, `re`, `requests`, `lxml.etree`.

当然, 你也可以选择直接运行项目中的 `.exe` 文件, 无需安装任何依赖.

## 使用方法

1. 运行 `main.py` 或 `app.exe`.
2. 输入城市(中文名称).
3. 输入两个以空格分隔的正整数 $l, r(1 \leqslant l \leqslant r \leqslant 100)$, 表示爬取链家上该城市从第 $l$ 页到第 $r$ 页的所有在售二手房信息.
4. 稍事等待, 信息会自动存入 `AppData/information` 文件夹中的 `城市名_l-r.json` 和 `城市名_l-r.csv` 文件. 图片文件会被存入 `AppData/image` 文件夹.

## 参数解释

- `title`: 页面标题
- `location`: 房屋地址
- `details.configuration`: 户型
- `details.area`: 面积
- `details.towards`: 朝向
- `details.decorate`: 装修程度
- `details.storey`: 楼层高度
- `details.categorie`: 楼型
- `price.total_price`: 总价
- `price.unit_price`: 每平米单价

## 其它信息

- $\rm Author: CCA$
- $\rm Contact~Method:$ `c-c-a@qq.com`
- $\rm Date: 2024/6/12$
- $\rm Open~Source~License: GPL$
- $\rm Version: v3.2$
