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


# -- Imports --------------------------------------------------------------------------

from random import randrange
from .morph import analyze
from .responder import RandomResponder, PatternResponder, TemplateResponder, MarkovResponder
from .responder import KeywordResponder, SpecialResponder, UserRandomResponder
from .dictionary import Dictionary
from typing import Union, Iterable
from pathlib import Path
from traceback import print_exc

# -------------------------------------------------------------------------- Imports --

# -- MocaBot --------------------------------------------------------------------------


class MocaBot(object):
    """
    人工無脳コアクラス。

    プロパティ:
    name -- 人工無脳コアの名前
    responder_name -- 現在の応答クラスの名前
    """

    def __init__(self, name: str):
        self.__dictionary = Dictionary(name)

        self.__responders = {
            'random': RandomResponder('Random', self.__dictionary),
            'pattern': PatternResponder('Pattern', self.__dictionary),
            'template': TemplateResponder('Template', self.__dictionary),
            'markov': MarkovResponder('Markov', self.__dictionary),
            'special': SpecialResponder('special', self.__dictionary),
            'keyword': KeywordResponder('keyword', self.__dictionary),
            'user_random': UserRandomResponder('user_random', self.__dictionary)
        }

        self.__name = name
        self.__responder = self.__responders['pattern']

    def dialogue(self, message: str, study: bool = False) -> str:
        """
        ユーザーからの入力を受け取り、Responderに処理させた結果を返す。
        呼び出されるたびにランダムでResponderを切り替える。
        入力をDictionaryに学習させる。
        studyパラメータまたはauto_study設定がオンになっている場合のみ学習する。
        """
        parts = analyze(message)
        limit = 3
        while True:
            chance = randrange(0, 100)
            if limit <= 0:
                self.__responder = self.__responders['random']
            elif chance in range(0, 9):
                self.__responder = self.__responders['random']
            elif chance in range(10, 40):
                self.__responder = self.__responders['template']
            elif chance in range(41, 70):
                self.__responder = self.__responders['pattern']
            else:
                self.__responder = self.__responders['markov']
            response = self.__responder.response(message, parts)
            if response:
                break
            else:
                limit -= 1
        return response

    def save(self):
        """Dictionaryへの保存を行う。"""
        self.__dictionary.save()

    def study(self, message: Union[str, Iterable[str]]):
        """メッセージを学習する。"""
        if isinstance(message, str):
            self.__dictionary.study(message, analyze(message))
        else:
            for item in message:
                self.__dictionary.study(item, analyze(item))

    def study_from_file(self,
                        filename: Union[Path, str],
                        print_log: bool = False) -> bool:
        try:
            with open(str(filename), mode='r', encoding='utf-8') as file:
                count = 0
                for line in file:
                    for message in line.split():
                        if len(message) < 3:
                            pass
                        elif message.startswith('#'):
                            pass
                        elif message.startswith('@'):
                            pass
                        elif message.startswith('http'):
                            pass
                        elif message[0] in '0123456789':
                            pass
                        else:
                            parts = analyze(message)
                            self.__dictionary.study(message, parts)
                            count += 1
                            if print_log:
                                print(message)
            self.save()
            if print_log:
                print(f'{count}件のテキストを学習しました。')
            return True
        except Exception:
            print_exc()

    @property
    def name(self) -> str:
        """人工無脳インスタンスの名前"""
        return self.__name

    @property
    def responder_name(self) -> str:
        """保持しているResponderの名前"""
        return self.__responder.name

# -------------------------------------------------------------------------- MocaBot --
