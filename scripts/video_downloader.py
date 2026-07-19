"""
通用视频下载脚本 — 适合从你自己的网站批量下载视频。

用法：
  python scripts/video_downloader.py                           # 读取 config 下载
  python scripts/video_downloader.py --url "https://你的网站/video/123"  # 下载单个
  python scripts/video_downloader.py --list urls.txt            # 批量下载

搭好网站后，修改下面的 CONFIG 即可使用。
"""
import argparse, os, re, sys, time
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

# ============================================================
# CONFIG — 网站搭建好后修改这里
# ============================================================

CONFIG = {
    # 你的网站域名（可多个）
    "allowed_domains": ["your-website.com", "localhost"],

    # 视频页面 URL 模式（正则），用于匹配视频详情页
    "video_page_pattern": r"/video/[\w-]+",

    # CSS 选择器 — 从页面中提取视频链接
    "video_selector": "video source, video, .video-player source, [data-video-url]",

    # 属性名 — 优先取哪个属性里的 URL
    "video_attrs": ["src", "data-src", "data-video-url", "data-url"],

    # 下载保存路径
    "download_dir": "./downloads",

    # 请求头
    "headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Referer": "https://your-website.com/",
    },

    # 请求间隔（秒），避免给服务器压力
    "delay": 1,

    # 认证（如需要登录）
    "auth": None,  # 或 {"username": "xxx", "password": "xxx"}
    "cookies": {},  # 或 {"session_id": "xxx"}

    # 如果视频是 m3u8 流，使用 ffmpeg 下载
    "use_ffmpeg_for_m3u8": True,
}


# ============================================================
# 核心逻辑
# ============================================================

def create_session():
    """创建带配置的 requests session。"""
    s = requests.Session()
    s.headers.update(CONFIG["headers"])
    if CONFIG["auth"]:
        s.auth = (CONFIG["auth"]["username"], CONFIG["auth"]["password"])
    for k, v in CONFIG["cookies"].items():
        s.cookies.set(k, v)
    return s


def extract_video_url(page_url: str, session: requests.Session) -> str | None:
    """从视频页面提取视频文件 URL。"""
    resp = session.get(page_url, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")

    # 方法 1：CSS 选择器
    for selector in CONFIG["video_selector"].split(", "):
        el = soup.select_one(selector.strip())
        if el:
            for attr in CONFIG["video_attrs"]:
                url = el.get(attr, "")
                if url and url.startswith(("http", "//", "/")):
                    return urljoin(page_url, url)

    # 方法 2：从 script / JSON 中提取
    for script in soup.find_all("script"):
        text = script.string or ""
        for pattern in [
            r'"videoUrl"\s*:\s*"([^"]+)"',
            r'"src"\s*:\s*"([^"]+\.mp4[^"]*)"',
            r'https?://[^"\']+\.(?:mp4|m3u8|webm|mkv)[^"\']*',
        ]:
            m = re.search(pattern, text)
            if m:
                return m.group(1) if m.lastindex else m.group(0)

    # 方法 3：meta 标签
    for meta in soup.find_all("meta"):
        if meta.get("property") in ("og:video", "og:video:url", "og:video:secure_url"):
            url = meta.get("content", "")
            if url:
                return url

    # 方法 4：iframe / embed
    iframe = soup.select_one("iframe[src*='video'], iframe[src*='player']")
    if iframe:
        src = iframe.get("src", "")
        if src:
            return urljoin(page_url, src)

    return None


def download_file(url: str, filepath: Path, session: requests.Session) -> bool:
    """流式下载文件，显示进度。"""
    filepath.parent.mkdir(parents=True, exist_ok=True)

    # 如果已存在，跳过
    if filepath.exists():
        print(f"  [SKIP] 已存在: {filepath.name}")
        return True

    resp = session.get(url, stream=True, timeout=300)
    resp.raise_for_status()
    total = int(resp.headers.get("content-length", 0))

    print(f"  下载: {filepath.name} ({total / 1024 / 1024:.1f} MB)" if total else f"  下载: {filepath.name}")

    downloaded = 0
    with open(filepath, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)
            downloaded += len(chunk)
            if total:
                pct = downloaded / total * 100
                print(f"\r  {downloaded / 1024 / 1024:.1f} / {total / 1024 / 1024:.1f} MB ({pct:.0f}%)", end="", flush=True)
    if total:
        print()
    return True


def download_m3u8(m3u8_url: str, filepath: Path, session: requests.Session) -> bool:
    """下载 m3u8 流（需要 ffmpeg）。"""
    import subprocess
    filepath = filepath.with_suffix(".mp4")
    if filepath.exists():
        print(f"  [SKIP] 已存在: {filepath.name}")
        return True

    print(f"  下载 m3u8: {filepath.name}")
    cmd = [
        "ffmpeg", "-y", "-loglevel", "error",
        "-headers", f"Referer: {CONFIG['headers']['Referer']}",
        "-i", m3u8_url, "-c", "copy", str(filepath),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  [FAIL] ffmpeg: {result.stderr[:200]}")
        return False
    print(f"  完成: {filepath.name}")
    return True


def download_video(page_url: str, session: requests.Session) -> bool:
    """下载单个视频页面。"""
    print(f"\n[页面] {page_url}")
    try:
        video_url = extract_video_url(page_url, session)
    except Exception as e:
        print(f"  [ERR] 页面加载失败: {e}")
        return False

    if not video_url:
        print(f"  [FAIL] 未找到视频链接，请调整 video_selector 或 video_attrs")
        return False

    print(f"  [OK] 视频链接: {video_url}")

    # 生成文件名
    slug = re.sub(r"[^\w\-]", "_", page_url.split("/")[-1][:80]) or "video"
    ext = ".mp4"
    if ".m3u8" in video_url:
        ext = ".m3u8"
    elif ".webm" in video_url:
        ext = ".webm"
    elif ".mkv" in video_url:
        ext = ".mkv"
    filepath = Path(CONFIG["download_dir"]) / f"{slug}{ext}"

    try:
        if video_url.endswith(".m3u8") and CONFIG["use_ffmpeg_for_m3u8"]:
            return download_m3u8(video_url, filepath, session)
        else:
            return download_file(video_url, filepath, session)
    except Exception as e:
        print(f"  [ERR] 下载失败: {e}")
        return False


def crawl_list(list_url: str, session: requests.Session) -> list[str]:
    """从列表页爬取所有视频页面链接。"""
    print(f"\n爬取列表: {list_url}")
    resp = session.get(list_url, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")

    urls = set()
    base = f"{urlparse(list_url).scheme}://{urlparse(list_url).netloc}"
    pattern = re.compile(CONFIG["video_page_pattern"])

    for a in soup.find_all("a", href=True):
        href = a["href"]
        full = urljoin(base, href)
        if pattern.search(href) or pattern.search(full):
            parsed = urlparse(full)
            domain = parsed.netloc.split(":")[0]
            if any(d in domain for d in CONFIG["allowed_domains"]):
                urls.add(full)

    print(f"  找到 {len(urls)} 个视频页面")
    return sorted(urls)


# ============================================================
# CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="通用视频下载脚本")
    parser.add_argument("--url", help="下载单个视频页面")
    parser.add_argument("--list", help="从包含 URL 列表的文本文件批量下载")
    parser.add_argument("--crawl", help="爬取列表页，自动发现所有视频并下载")
    parser.add_argument("--dir", help=f"下载目录（默认 {CONFIG['download_dir']}）")
    args = parser.parse_args()

    if args.dir:
        CONFIG["download_dir"] = args.dir

    session = create_session()

    if args.url:
        download_video(args.url, session)

    elif args.list:
        with open(args.list, encoding="utf-8") as f:
            urls = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        print(f"共 {len(urls)} 个 URL")
        ok = 0
        for url in urls:
            if download_video(url, session):
                ok += 1
            time.sleep(CONFIG["delay"])
        print(f"\n完成: {ok}/{len(urls)} 成功")

    elif args.crawl:
        urls = crawl_list(args.crawl, session)
        ok = 0
        for url in urls:
            if download_video(url, session):
                ok += 1
            time.sleep(CONFIG["delay"])
        print(f"\n完成: {ok}/{len(urls)} 成功")

    else:
        parser.print_help()
        print("\n示例:")
        print("  python scripts/video_downloader.py --url 'https://你的网站/video/123'")
        print("  python scripts/video_downloader.py --crawl 'https://你的网站/videos/'")
        print("  python scripts/video_downloader.py --list urls.txt")


if __name__ == "__main__":
    main()
