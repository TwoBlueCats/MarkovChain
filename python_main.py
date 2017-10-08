# -*- coding: utf-8 -*-
import telebot
import random
import sys
import json
import os
from copy import deepcopy
from chain_word import Chain_word

TOKEN = "358621240:AAF9_Jhl56-lrvR75q7Np7PLjFYVmKKpH9Q"
tester_TOKEN = "286496122:AAGED92TDcccXHGJmgyz5oJcCcZ4TI-vTrM"
bot = telebot.TeleBot(tester_TOKEN)
AdminID = 186898465


class ChainText:
    def str_to_tuple(self, a):
        tmp = a[1:-1].split(',')
        return tuple([x.strip().strip("'") for x in tmp])

    def __init__(self, code, file_name="model.txt"):
        self.__model_ = dict()
        self.__context_count_ = dict()

        # print("code =", type(code), code[0], code[1], code[2], code[3])
        self.__n = int(code[0])
        self.lines = int(code[1])
        model_t = deepcopy(code[2])
        context_count_t = deepcopy(code[3])

        for x, y in model_t.items():
            self.__model_[self.str_to_tuple(x)] = deepcopy(y)

        for x, y in context_count_t.items():
            self.__context_count_[self.str_to_tuple(x)] = deepcopy(y)

        self.__file_name = file_name

    def learn(self, line):
        if len(line) == 0:
            return

        self.lines += 1
        context = ['.'] * self.__n
        for w in line:
            context_t = tuple(deepcopy(context))
            self.__model_[context_t] = self.__model_.get(context_t, dict())
            self.__model_[context_t][w] = self.__model_[context_t].get(w, 0) + 1
            self.__context_count_[context_t] = self.__context_count_.get(context_t, 0) + 1
            context += [w]
            context = context[1:]

        # print('line =', line)

        with open(self.__file_name, "w") as f:
            json.dump(self.to_json(), f, indent=4)
        with open("model.json", "w") as f:
            json.dump(self.to_json(), f, indent=4)

    def __add__(self, line):
        if not isinstance(line, list):
            return NotImplemented
        else:
            self.learn(line)
            return self

    def __iadd__(self, line):
        if not isinstance(line, list):
            return NotImplemented
        else:
            self.learn(line)
        return self

    def __radd__(self, line):
        if not isinstance(line, list):
            return NotImplemented
        else:
            self.learn(line)
        return self

    def generate(self, ln, first=[]):
        result = first
        context = ['.'] * (self.__n - len(first))
        context += first

        for i in range(ln):
            context_t = tuple(deepcopy(context))
            context_size = self.__context_count_.get(context_t, 0)
            if context_size == 0:
                return len(result), result

            next_word_index = random.randint(0, context_size)
            for word_and_weight in self.__model_[context_t]:
                word = word_and_weight
                weight = self.__model_[context_t][word]
                if next_word_index <= weight:
                    result += [word]
                    context += [word]
                    context = context[1:]
                    break
                else:
                    next_word_index -= weight
        return len(result), result

    def to_json(self):
        a = [self.__n, self.lines, {}, {}]

        for x, y in self.__model_.items():
            a[2][str(x)] = deepcopy(y)
        for x, y in self.__context_count_.items():
            a[3][str(x)] = deepcopy(y)

            # print("to json = ", a, end="\n\n")
        return a

    def __str__(self):
        return '[' + str(self.__n) + ',' + str(self.lines) + ',' + str(self.__model_) + ',' + str(
            self.__context_count_) + ']'


ch = ChainText([2, 0, {}, {}])
try:
    fl = open("model.txt", "r")
    ch = ChainText(json.load(fl))
    fl.close()
except Exception as err:
    # print(str(err))
    ch = ChainText([2, 0, {}, {}])
    try:
        with open("data.txt", 'r', encoding='utf-8') as my_file:
            text = my_file.read()
            with open("tmp.txt", 'a', encoding='utf-8') as fl:
                print(text, end="", file=fl)
            for ln in text.split('\n'):
                ch += ln.split()

    except Exception as err:
        print(err, file=sys.stderr)


@bot.message_handler(commands=['help', 'start'])
def help_message(message):
    bot.send_message(message.chat.id,
                     "Привет, напиши /gen <number>, чтобы сгенерировать текст, состоящий из этого числа слов")


@bot.message_handler(commands=['generate'])
def generate_message(message):
    global ch
    try:
        d = message.text.split()
        try:
            text_len = int(d[1])
            first_words = d[2:]
            print(type(first_words))
        except:
            bot.send_message(message.chat.id, "Не соответствует формату запроса: /generate <number> <words>")
            return

        cnt = 1000
        while cnt >= 0:
            ans = ch.generate(text_len if text_len else 10000000, first_words)
            if ans[0] == text_len or text_len == 0:
                bot.send_message(message.chat.id, " ".join(ans[1]))
                break
            cnt -= 1
        else:
            bot.send_message(message.chat.id, "Sorry.... Я не могу сгенерировать текст такой длинны")
    except Exception as err:
        bot.send_message(AdminID, "error : " + str(err))
        bot.send_message(message.chat.id, "Internal error")


@bot.message_handler(commands=['gen'])
def gen_message(message):
    global ch
    try:
        d = message.text.split()
        text_len = 0
        try:
            text_len = int(d[1])
        except:
            text_len = 0
        cnt = 1000
        while cnt >= 0:
            ans = ch.generate(text_len if text_len else 10000000)
            if ans[0] == text_len or text_len == 0:
                bot.send_message(message.chat.id, " ".join(ans[1]))
                break
            cnt -= 1
        else:
            bot.send_message(message.chat.id, "Sorry.... Я не могу сгенерировать текст такой длинны")
    except Exception as err:
        bot.send_message(AdminID, "error : " + str(err))
        bot.send_message(message.chat.id, "Internal error")


@bot.message_handler(commands=['end'])
def end_of_bot(message):
    print("end")
    if message.chat.id == AdminID:
        bot.send_message(message.chat.id, "End")
        bot.stop_polling()


@bot.message_handler()
def add_message(message):
    global ch
    if message.text[0] == '/':
        return
    # print(type(message), message.from_user.id, message.chat.id)
    if message.from_user.id == message.chat.id:
        bot.send_message(message.chat.id, "Я принимаю сообщения только из групп")
    else:
        with open("data.txt", 'a', encoding='utf-8') as f:
            print(message.text, file=f, end="")
        try:
            for line in message.text.split('\n'):
                ch += line.split()
            with open("data.txt", 'a', encoding='utf-8') as f:
                print("\n", file=f, end="")
        except Exception as err2:
            with open("data.txt", 'a', encoding='utf-8') as f:
                print(" error\n", file=f, end="")
            print("in adding new message", str(err2))


# print("learn starts")
# fl = open("some_text.txt", "rt", encoding="utf-8")
# for line in fl.readlines()[:10]:
# ch += line.split()
# fl.close()
# print("learn is end")

bot.send_message(AdminID, "Start")
errors = 0
while True:
    try:
        bot.polling()
        break
    except Exception as err:
        with open("errors.txt", "a", encoding='utf-8') as fl:
            print(str(err), file=fl)
        errors += 1

print(errors)

# bot.send_message(AdminID, "Ends")

# text_len = int(input("Text len\n"))
# cnt = 0
# while True:
# print(cnt)
# cnt += 1
# ans = ch.generate(text_len)
# if ans[0] == text_len - 1:
# print(ans[1], '\n\n\n')
# break
