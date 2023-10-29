import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from easychat.wework import *
import logging
import json
import argparse
logging.basicConfig(level=logging.DEBUG)

load_config("../../config.yaml")

def main():
    parser = argparse.ArgumentParser(description="获取微信临时素材")
    parser.add_argument("media_id", help="微信的media_id")
    parser.add_argument("--filepath", default=None, help="文件保存路径（可选）")

    args = parser.parse_args()

    filename, type_, content = get_media(args.media_id, args.filepath)

    if args.filepath:
        print(f"文件已保存到：{filename}")
    else:
        print(content)

if __name__ == "__main__":
    main()
