import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))

from easychat.wework import *
import logging
import json
logging.basicConfig(level=logging.DEBUG)

load_config("../../config.yaml")

bots = get_bots()
b_str = json.dumps(bots, indent=4, ensure_ascii=False)
print(b_str)
