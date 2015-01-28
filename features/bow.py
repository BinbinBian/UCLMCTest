import sys
sys.path.insert(0, '../')
from UCLMCTest.classes import storyparser, Question, answers
import nltk
import numpy as np

STOPWORDS = nltk.corpus.stopwords.words('english')


def bow(s1, s2):
    set1 = {l for w, l, p in s1 if l not in STOPWORDS} \
        | {w for w, l, p in s1 if w not in STOPWORDS}
    set2 = {l for w, l, p in s2 if l not in STOPWORDS} \
        | {w for w, l, p in s2 if w not in STOPWORDS}
    return set1 & set2

def previous_bow(s1, s2):
    sim = []
    for w1, l1, p1 in s1:
        if w1 in STOPWORDS or l1 in STOPWORDS:
            continue
        for w2, l2, p2 in s2:
            if w2 in STOPWORDS or l2 in STOPWORDS:
                continue
            elif l2 == l1:
                sim.append((w1, l1, p1))
                break
    return sim


def score(story, question_n, answer_n):
    question = story.questions[question_n]
    answer = question.answers[answer_n]
    qa_pair = question.qsentence.parse.lemma + answer.parse.lemma
    similarities = [bow(qa_pair, s.parse.lemma) for s in story.sentences]
    return (max([len(s) for s in similarities]), similarities)

def XVector(stories, norm=None):
    X = []
    for story in stories:
        for q, question in enumerate(story.questions):
            qa_scores = [score(story, q, a)[0] for a, _ in enumerate(question.answers)]

            if (norm == "question"):
                qa_scores = np.array(qa_scores)
                qa_scores = (qa_scores / np.linalg.norm(qa_scores)).tolist()
            X = X + qa_scores

    if (norm == "all"):
        X = np.array(X)
        X = (X / np.linalg.norm(X)).tolist()

    return X


def baseline(stories, solutions, mode=None, debug=False):
    scored, total = 0, 0
    for story, solution in zip(stories, solutions):
        for q, question in enumerate(story.questions):
            if question.mode != mode:
                continue
            max_index, max_score = -1, (-1, None)
            for a, _ in enumerate(question.answers):
                current_score = score(story, q, a)
                if current_score[0] > max_score[0]:
                    max_index = a
                    max_score = current_score

            best_answer = chr(max_index + 0x41)
            correct = best_answer == solution[q]
            if correct:
                scored += 1

            total += 1
            if (debug):
                print "Correct:%i\nQuestion matched:\n%s\nWords count: %i\nWords matched:\n%s\n\n" % (correct, question, current_score[0], current_score[1])

    return {
        "total": total,
        "scored": scored,
        "accuracy": (scored * 1.0 / total) * 100
    }

if __name__ == "__main__":
    testset = "mc160.dev"
    stories = storyparser(testset)
    solutions = answers(testset)
    scores(stories, norm="all")
    print baseline(stories, solutions, mode=Question.SINGLE, debug=False)
