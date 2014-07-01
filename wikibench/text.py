import os
import os.path

lexicon = {}
numeric_tags = {}

for line in open(os.path.join('datasets', 'lexicon.txt')):
    args = line.strip().split(' ')
    lexicon[args[0]] = args[1:]

    for tag in args[1:]:
        if tag not in numeric_tags:
            numeric_tags[tag] = len(numeric_tags)


def tag_words(words):
    tags = set()
    for word in words:
        for tag in lexicon.get(word.lower(), []):
            tags.add(tag)
    return tags


def tag_words_numerics(words):
    return set(map(lambda x: numeric_tags[x], tag_words(words)))


def tag_words_numerics_binary(words):
    binary = []
    num_tags = tag_words_numerics(words)

    for i in range(len(numeric_tags)):
        if i in num_tags:
            binary.append(1)
        else:
            binary.append(0)

    return binary
