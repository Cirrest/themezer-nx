#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""校验汉化版 themezer-nx NRO 的完整性（结构 / 汉化文案 / API 参数 / 元数据）。

用法:
    python tools/verify_nro.py [汉化版.nro] [原始英文版.nro]

不传参数时默认检查 themezer-nx/themezer-nx.nro。
第二个参数（原始英文版）可选，提供后会额外做"原版不含中文串"的对照。

退出码: 0 = 全部通过; 1 = 存在失败项。
"""
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BUILT = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 \
    else os.path.join(REPO_ROOT, "themezer-nx", "themezer-nx.nro")
ORIG = os.path.abspath(sys.argv[2]) if len(sys.argv) > 2 else None

# 必须存在的中文文案（抽样覆盖全部界面模块）
MUST_HAVE_CN = [
    "主题包", "主界面", "锁屏", "全部应用", "设置", "玩家选择", "用户页面", "新闻", "开机画面",
    "热门", "创建时间", "更新时间", "下载量", "收藏量", "降序", "升序",
    "安装并保存", "仅安装", "仅下载", "返回", "确定", "知道了", "好的", "显示详情",
    "类型", "安装队列", "搜索与筛选", "排序方式", "顺序", "应用", "清除",
    "加载中...", "这里空空如也...", "长按", "取消",
    "你想做什么？", "浏览", "按 Quick ID 安装", "退出",
    "警告！", "下载错误", "请求出错", "连接错误！", "浏览数据加载失败",
    "正在查询 Quick ID...", "按 B 取消", "下载已取消！", "下载失败！",
    "正在下载主题...", "正在下载开机画面...", "主题已排队！", "开机画面已排队！", "已加入安装队列！",
    "输入 Quick ID（可在 themezer.net 上找到）", "未找到 Quick ID", "Quick ID 查询失败",
    "输入搜索词，最多 100 个字符", "搜索：", "移除已排队项目？",
    "确定要移除「%s」的已排队安装吗？", "选择「%s」主题", "这将替换 %d 个已排队的安装。是否继续？",
    "正在排队安装...", "下载完成", "下载未完成", "安装已排队", "安装未完成", "无内容可排队",
    "该主题包中的所有主题均已下载完成。", "下载已取消", "安装已取消",
    "作者：", "创建：", "更新：", "菜单：", "Hekate 开机画面", "Switch 主题",
    "退出 Themezer-NX", "已加入安装队列。退出应用即可应用主题。",
    "替换已排队的安装？", "未知",
]

# 必须已被替换掉的旧英文文案
MUST_BE_GONE = [
    "Install & Save", "Install Only", "Download Only", "Queued Installs",
    "Nothing to see here", "Show Details", "Connection Error", "Browse Load Failed",
    "Loading browse data failed", "Loading...", "Are you sure you want to remove",
    "Choose %s Theme", "Exit Themezer-NX", "Warning!", "Alright", "Got it!",
    "Splash Queued!", "Theme Queued!", "Install Queued!", "Download Error",
    "Error during request", "Search & Filters", "Sort By", "Input search terms",
    "Input Quick ID", "No result found for Quick ID", "Quick ID Not Found",
    "The themezer server returned", "Remove Queued Item?", "Replace Queued Installs",
    "The NXThemes Installer could not be found", "Hold", "to cancel",
    "Download Cancelled", "Download Complete", "Download Incomplete",
    "Install Cancelled", "Install Incomplete", "Installs Queued", "Nothing Queued",
    "Queueing Installs", "Downloading Themes", "Downloading Theme", "Downloading Splash",
    "This pack does not contain", "All themes in this pack", "theme downloads were cancelled",
    "This will replace", "theme%s failed", "install%s queued",
]

# 必须保留的 API 参数（翻译会破坏联网功能）
MUST_KEEP_API = ["ResidentMenu", "Entrance", "Flaunch", "MyPage", "Notification",
                 "lookupByQuickId", "api.themezer.net/graphql"]

fails = []


def check(cond, label):
    print(("  [通过] " if cond else "  [失败] ") + label)
    if not cond:
        fails.append(label)


if not os.path.exists(BUILT):
    print(f"找不到文件: {BUILT}")
    sys.exit(1)

built = open(BUILT, "rb").read()
orig = open(ORIG, "rb").read() if ORIG and os.path.exists(ORIG) else None

print(f"检查文件: {BUILT}（{len(built):,} 字节）\n")

print("[1] NRO 结构")
check(built[0x10:0x14] == b"NRO0", "NRO0 魔数位于 0x10")
if orig:
    check(built[:0x40] == orig[:0x40], "NRO 头部前 0x40 字节与原版一致")

print("[2] 汉化文案")
missing = [s for s in MUST_HAVE_CN if s.encode("utf-8") not in built]
check(not missing, f"{len(MUST_HAVE_CN)} 条中文文案全部存在" + (f"（缺失: {missing[:5]}）" if missing else ""))

print("[3] 旧英文文案清除")
left = [s for s in MUST_BE_GONE if s.encode("utf-8") in built]
check(not left, f"{len(MUST_BE_GONE)} 条旧英文文案全部清除" + (f"（残留: {left[:5]}）" if left else ""))

print("[4] API 参数保留")
api_missing = [s for s in MUST_KEEP_API if s.encode("utf-8") not in built]
check(not api_missing, "GraphQL/API 参数完整" + (f"（缺失: {api_missing}）" if api_missing else ""))

print("[5] 插件名与作者")
check(b"Themezer-NX" in built, "名称 Themezer-NX 保留")
check(b"Such Meme, Many Skill" in built, "作者 Such Meme, Many Skill 保留")

if orig:
    print("[6] 原版对照")
    cn_in_orig = sum(1 for s in MUST_HAVE_CN if s.encode("utf-8") in orig)
    check(cn_in_orig == 0, f"原始英文版不含本次新增的中文文案（命中 {cn_in_orig} 条）")

print()
if fails:
    print(f"结果: {len(fails)} 项未通过")
    sys.exit(1)
print("结果: 全部通过")
