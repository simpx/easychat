#!/usr/bin/env python
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
    parser = argparse.ArgumentParser(description="media tool")
    subparsers = parser.add_subparsers(dest='command')

    # get命令
    get_parser = subparsers.add_parser('get', help='获取微信临时素材')
    get_parser.add_argument('media_id', help='要获取的媒体文件ID')
    get_parser.add_argument('directory', nargs='?', default=None, help='保存文件的目录')

    # put命令
    put_parser = subparsers.add_parser('put', help='上传文件到微信')
    put_parser.add_argument('filepath', help='要上传的文件的路径')

    args = parser.parse_args()

    if args.command == "get":
        filepath, media_type, content = get_media(args.media_id, args.directory, access_token)
        if args.directory:
            print(f"文件已保存到：{filepath}")
        else:
            print(f"文件内容：\n{content}")

    elif args.command == "put":
        media_id, media_type = put_media(args.filepath)
        print(f"上传成功！Media ID: {media_id}, Type: {media_type}")
    else:
        parser.print_help()
        sys.exit(0)

if __name__ == "__main__":
    main()

