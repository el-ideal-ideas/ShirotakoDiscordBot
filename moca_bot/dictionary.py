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

from typing import List, Tuple
from collections import defaultdict
from .markov import Markov
from .morph import is_keyword
from json import dump, load
from pathlib import Path

# -------------------------------------------------------------------------- Imports --

# -- Dictionary --------------------------------------------------------------------------


class Dictionary(object):
    """思考エンジンの辞書クラス。

    プロパティ:
    __name -- 辞書の名前
    __random -- ランダム辞書
    __pattern -- パターン辞書
    __template -- テンプレート辞書
    __markov -- マルコフ辞書
    __special -- 固定返事
    __keyword -- キーワード辞書
    __user_random -- ユーザー定義ランダム辞書
    """

    def __init__(self, name: str):
        """ファイルから辞書の読み込みを行う。"""
        self.__name = name
        self.__random = self.__load_random()
        self.__pattern = self.__load_pattern()
        self.__template = self.__load_template()
        self.__markov = self.__load_markov()
        self.__special = self.__load_special()
        self.__keyword = self.__load_keyword()
        self.__user_random = self.__load_user_random()

    def study(self, message: str, parts: List[Tuple[str, str]]) -> None:
        """ランダム辞書、パターン辞書、テンプレート辞書をメモリに保存する。"""
        self.study_random(message)
        self.study_pattern(message, parts)
        self.study_template(parts)
        self.study_markov(parts)

    def study_markov(self, parts: List[Tuple[str, str]]) -> None:
        """形態素のリストpartsを受け取り、マルコフ辞書に学習させる。"""
        self.__markov.add_sentence(parts)

    def study_template(self, parts: List[Tuple[str, str]]) -> None:
        """
        形態素のリストpartsを受け取り、
        名詞のみ'%noun%'に変更した文字列templateをself.__templateに追加する。
        名詞が存在しなかった場合、または同じtemplateが存在する場合は何もしない。
        """
        template = ''
        count = 0
        for word, part in parts:
            if is_keyword(part):
                word = '%noun%'
                count += 1
            template += word

        if count > 0 and template not in self.__template[count]:
            self.__template[count].append(template)

    def study_random(self, message: str) -> None:
        """
        ユーザーの発言をランダム辞書に保存する。
        すでに同じ発言があった場合は何もしない。
        """
        if message not in self.__random:
            self.__random.append(message)

    def study_pattern(self, message: str, parts: List[Tuple[str, str]]) -> None:
        """ユーザーの発言を形態素partsに基づいてパターン辞書に保存する。"""
        for word, part in parts:
            if is_keyword(part):  # 品詞が名詞でなければ学習しない
                # 単語の重複チェック
                # 同じ単語で登録されていれば、パターンを追加する
                # 無ければ新しいパターンを作成する
                duplicated = self.__find_duplicated_pattern(word)
                if duplicated and message not in duplicated['phrases']:
                    duplicated['phrases'].append(message)
                else:
                    self.__pattern.append({'pattern': word, 'phrases': [message]})

    def save(self) -> None:
        """メモリ上の辞書をファイルに保存する。"""
        self.__save_random()
        self.__save_pattern()
        self.__save_template()
        self.__markov.save(Path(__file__).parent.parent.joinpath('data').joinpath(self.__name).joinpath('markov.dat'))
        self.__save_special()
        self.__save_keyword()
        self.__save_user_random()

    def __save_template(self):
        """テンプレート辞書を保存する。"""
        filename = str(Path(__file__).parent.parent.joinpath('data').joinpath(self.__name).joinpath('template.txt'))
        with open(filename, mode='w', encoding='utf-8') as file:
            for count, templates in self.__template.items():
                for template in templates:
                    file.write('{}\t{}\n'.format(count, template))

    def __save_pattern(self):
        """パターン辞書を保存する。"""
        filename = str(Path(__file__).parent.parent.joinpath('data').joinpath(self.__name).joinpath('pattern.txt'))
        with open(filename, mode='w', encoding='utf-8') as file:
            for pattern in self.__pattern:
                file.write(Dictionary.pattern2line(pattern))
                file.write('\n')

    def __save_random(self):
        """ランダム辞書を保存する。"""
        filename = str(Path(__file__).parent.parent.joinpath('data').joinpath(self.__name).joinpath('random.txt'))
        with open(filename, mode='w', encoding='utf-8') as file:
            file.write('\n'.join(self.random))

    def __save_special(self):
        """固定返事を保存する。"""
        filename = str(Path(__file__).parent.parent.joinpath('data').joinpath(self.__name).joinpath('special.json'))
        with open(filename, mode='w', encoding='utf-8') as file:
            dump(self.__special,
                 file,
                 ensure_ascii=False,
                 indent=4,
                 sort_keys=False,
                 separators=(',', ': '))

    def __save_keyword(self):
        """キーワードを保存する。"""
        filename = str(Path(__file__).parent.parent.joinpath('data').joinpath(self.__name).joinpath('keyword.json'))
        with open(filename, mode='w', encoding='utf-8') as file:
            dump(self.__keyword,
                 file,
                 ensure_ascii=False,
                 indent=4,
                 sort_keys=False,
                 separators=(',', ': '))

    def __save_user_random(self):
        """ユーザー定義ランダム辞書を保存する。"""
        filename = str(Path(__file__).parent.parent.joinpath('data').joinpath(self.__name).joinpath('user_random.json'))
        with open(filename, mode='w', encoding='utf-8') as file:
            dump(self.__user_random,
                 file,
                 ensure_ascii=False,
                 indent=4,
                 sort_keys=False,
                 separators=(',', ': '))

    def __find_duplicated_pattern(self, word: str):
        """パターン辞書に名詞wordがあればパターンハッシュを、無ければNoneを返す。"""
        return next((pattern for pattern in self.__pattern if pattern['pattern'] == word), None)

    def __load_random(self):
        """
        ランダム辞書を読み込み、リストを返す。
        空である場合、[el]#moca_null#を追加する。
        """
        filename = str(Path(__file__).parent.parent.joinpath('data').joinpath(self.__name).joinpath('random.txt'))
        try:
            with open(filename, mode='r', encoding='utf-8') as file:
                lines = file.read().splitlines()
                return [message for message in lines if message != ''] if len(lines) > 0 else ['[el]#moca_null#']
        except FileNotFoundError:
            return ['[el]#moca_null#']

    def __load_pattern(self):
        """パターン辞書を読み込み、パターンハッシュのリストを返す。"""
        filename = str(Path(__file__).parent.parent.joinpath('data').joinpath(self.__name).joinpath('pattern.txt'))
        try:
            with open(filename, mode='r', encoding='utf-8') as file:
                return [Dictionary.line2pattern(line) for line in file.read().splitlines() if line != '']
        except FileNotFoundError:
            return []

    def __load_template(self):
        """テンプレート辞書を読み込み、ハッシュを返す。"""
        filename = str(Path(__file__).parent.parent.joinpath('data').joinpath(self.__name).joinpath('template.txt'))
        templates = defaultdict(lambda: [])
        try:
            with open(filename, mode='r', encoding='utf-8') as file:
                for line in file.read().splitlines():
                    count, template = line.split('\t')
                    if count and template:
                        count = int(count)
                        templates[count].append(template)
                return templates
        except FileNotFoundError:
            return templates

    def __load_special(self):
        """固定返事を読み込んで辞書を返す。"""
        filename = str(Path(__file__).parent.parent.joinpath('data').joinpath(self.__name).joinpath('special.json'))
        try:
            with open(filename, mode='r', encoding='utf-8') as file:
                return load(file)
        except FileNotFoundError:
            return {}

    def __load_keyword(self):
        """キーワードを読み込んで辞書を返す。"""
        filename = str(Path(__file__).parent.parent.joinpath('data').joinpath(self.__name).joinpath('keyword.json'))
        try:
            with open(filename, mode='r', encoding='utf-8') as file:
                return load(file)
        except FileNotFoundError:
            return {}

    def __load_user_random(self):
        """ユーザー定義ランダム辞書を読み込んでリストを返す。"""
        filename = str(Path(__file__).parent.parent.joinpath('data').joinpath(self.__name).joinpath('user_random.json'))
        try:
            with open(filename, mode='r', encoding='utf-8') as file:
                return load(file)
        except FileNotFoundError:
            return []

    def __load_markov(self):
        """Markovオブジェクトを生成し、filenameから読み込みを行う。"""
        markov = Markov()
        filename = Path(__file__).parent.parent.joinpath('data').joinpath(self.__name).joinpath('markov.dat')
        if filename.is_file():
            markov.load(filename)
        return markov

    @staticmethod
    def pattern2line(pattern: dict):
        """
        パターンのハッシュを文字列に変換する。
        >>> pattern = {'pattern': 'Pattern', 'phrases': ['phrases', 'list']}
        >>> Dictionary.pattern2line(pattern)
        'Pattern\\tphrases|list'
        """
        return '{}\t{}'.format(pattern['pattern'], '|'.join(pattern['phrases']))

    @staticmethod
    def line2pattern(line: str):
        """
        文字列lineを\tで分割し、{'pattern': [0], 'phrases': [1]}の形式で返す。
        [1]はさらに`|`で分割し、文字列のリストとする。
        >>> line = 'Pattern\\tphrases|list'
        >>> Dictionary.line2pattern(line)
        {'pattern': 'Pattern', 'phrases': ['phrases', 'list']}
        """
        pattern, phrases = line.split('\t')
        if pattern and phrases:
            return {'pattern': pattern, 'phrases': phrases.split('|')}

    @property
    def random(self):
        """ランダム辞書"""
        return self.__random

    @property
    def pattern(self):
        """パターン辞書"""
        return self.__pattern

    @property
    def template(self):
        """テンプレート辞書"""
        return self.__template

    @property
    def markov(self):
        """マルコフ辞書"""
        return self.__markov

    @property
    def special(self):
        """固定返事"""
        return self.__special

    @property
    def keyword(self):
        """キーワード"""
        return self.__keyword

    @property
    def user_random(self):
        """ユーザー定義ランダム"""
        return self.__user_random

# -------------------------------------------------------------------------- Dictionary --
