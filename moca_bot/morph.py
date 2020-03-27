# Ω*
#               ■          ■■■■■  
#               ■         ■■   ■■ 
#               ■        ■■     ■ 
#               ■        ■■       
#     ■■■■■     ■        ■■■      
#    ■■   ■■    ■         ■■■     
#   ■■     ■■   ■          ■■■■   
#   ■■     ■■   ■            ■■■■ 
#   ■■■■■■■■■   ■              ■■■
#   ■■          ■               ■■
#   ■■          ■               ■■
#   ■■     ■    ■        ■■     ■■
#    ■■   ■■    ■   ■■■  ■■■   ■■ 
#     ■■■■■     ■   ■■■    ■■■■■


"""
Moca System
モカシステム
茉客系统

Copyright (c) 2020.1.17 [el.ideal-ideas]

This software is released under the MIT License. see LICENSE.txt.

https://www.el-ideal-ideas.com
"""

# -- Imports --------------------------------------------------------------------------

from typing import Tuple, List
from re import match
from janome.tokenizer import Tokenizer

# -------------------------------------------------------------------------- Imports --

# -- Init --------------------------------------------------------------------------

TOKENIZER = Tokenizer()

# -------------------------------------------------------------------------- Init --

# -- Public Functions --------------------------------------------------------------------------


def analyze(message: str) -> List[Tuple[str, str]]:
    """メッセージを形態素解析し、[(surface, parts)]の形にして返す。"""
    return [(token.surface, token.part_of_speech) for token in TOKENIZER.tokenize(message)]


def is_keyword(part: str) -> bool:
    """品詞partが学習すべきキーワードであるかどうかを真偽値で返す。"""
    return bool(match(r'名詞,(一般|代名詞|固有名詞|サ変接続|形容動詞語幹)', part))

# -------------------------------------------------------------------------- Public Functions --
