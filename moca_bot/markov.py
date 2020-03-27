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

from random import choice
from collections import defaultdict
from copy import copy
from dill import load, dump
from typing import List, Optional, Union, Tuple
from pathlib import Path

# -------------------------------------------------------------------------- Imports --

# -- Markov --------------------------------------------------------------------------


class Markov(object):
    """マルコフ連鎖による文章の学習・生成を行う。

    クラス定数:
    ENDMARK -- 文章の終わりを表す記号
    CHAIN_MAX -- 連鎖を行う最大値
    """
    ENDMARK = '%END%'
    CHAIN_MAX = 30

    def __init__(self):
        """インスタンス変数の初期化。
        self.__dic -- マルコフ辞書。 __dic['prefix1']['prefix2'] == ['suffixes']
        self.__starts -- 文章が始まる単語の数。 __starts['prefix'] == count
        """
        self.__dic = defaultdict(lambda: defaultdict(lambda: []))
        self.__starts = defaultdict(lambda: 0)

    def add_sentence(self, parts: List[Tuple[str, str]]) -> None:
        """形態素解析結果partsを分解し、学習を行う。"""
        # 実装を簡単にするため、3単語以上で構成された文章のみ学習する
        if len(parts) > 3:
            # 呼び出し元の値を変更しないように`copy`する
            parts_copy = copy(parts)
    
            # prefix1, prefix2 には文章の先頭の2単語が入る
            prefix1, prefix2 = parts_copy.pop(0)[0], parts_copy.pop(0)[0]
    
            # 文章の開始点を記録する
            # 文章生成時に「どの単語から文章を作るか」の参考にするため
            self.__add_start(prefix1)
    
            # `prefix`と`suffix`をスライドさせながら`__add_suffix`で学習させる
            # すべての単語を登録したら、最後にENDMARKを追加する
            for suffix, _ in parts_copy:
                self.__add_suffix(prefix1, prefix2, suffix)
                prefix1, prefix2 = prefix2, suffix
            self.__add_suffix(prefix1, prefix2, Markov.ENDMARK)

    def generate(self, keyword: str) -> Optional[str]:
        """keywordをprefix1とし、そこから始まる文章を生成して返す。"""
        # 辞書が空である場合はNoneを返す
        if not self.__dic:
            return None
        else:
            # keywordがprefix1として登録されていない場合、__startsからランダムに選択する
            prefix1 = keyword if self.__dic[keyword] else choice(list(self.__starts.keys()))

            # prefix1をもとにprefix2をランダムに選択する
            prefix2 = choice(list(self.__dic[prefix1].keys()))

            # 文章の始めの単語2つをwordsに設定する
            words = [prefix1, prefix2]

            # 最大CHAIN_MAX回のループを回し、単語を選択してwordsを拡張していく
            # ランダムに選択したsuffixがENDMARKであれば終了し、単語であればwordsに追加する
            # その後prefix1, prefix2をスライドさせて始めに戻る
            for _ in range(Markov.CHAIN_MAX):
                suffix = choice(self.__dic[prefix1][prefix2])
                if suffix == Markov.ENDMARK:
                    break
                words.append(suffix)
                prefix1, prefix2 = prefix2, suffix

            return ''.join(words)

    def load(self, filename: Union[Path, str]):
        """ファイルfilenameから辞書データを読み込む。"""
        with open(str(filename), 'rb') as file:
            self.__dic, self.__starts = load(file)

    def save(self, filename: Union[Path, str]):
        """ファイルfilenameへ辞書データを書き込む。"""
        with open(str(filename), 'wb') as file:
            dump((self.__dic, self.__starts), file)

    def __add_suffix(self, prefix1, prefix2, suffix):
        self.__dic[prefix1][prefix2].append(suffix)

    def __add_start(self, prefix1):
        self.__starts[prefix1] += 1

# -------------------------------------------------------------------------- Markov --
