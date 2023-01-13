import math
import english_words
import time


# Create dictionary of letters and their positions on the keyboard
keyboard = {'q': (0, 0), 'w': (0, 1), 'e': (0, 2), 'r': (0, 3), 't': (0, 4), 
'y': (0, 5), 'u': (0, 6), 'i': (0, 7), 'o': (0, 8), 'p': (0, 9), 'å': (0, 10), 
'a': (1, 0), 's': (1, 1), 'd': (1, 2), 'f': (1, 3), 'g': (1, 4), 'h': (1, 5), 
'j': (1, 6), 'k': (1, 7), 'l': (1, 8), 'ø': (1, 9), 'æ': (1, 10), "'": (1, 11), 
'z': (2, 0), 'x': (2, 1), 'c': (2, 2), 'v': (2, 3), 'b': (2, 4), 'n': (2, 5), 
'm': (2, 6), '&': (100, 100)}

# Get all english words
words = english_words.english_words_lower_alpha_set

def similarity_score(s1, s2, iterated=False):
    s1 = s1.lower()
    s2 = s2.lower()
    score = 1
    # If the two words are equal, then the similarity score is 1
    if s1 == s2:
        return score
    # Get the similarity score of the two words if one letter is removed
    if iterated == False:
        if len(s1) - 1 == len(s2):
            newscore = 0
            for i in range(len(s1)):
                newscore = max(newscore, similarity_score(s1[:i] + s1[i + 1:], s2, iterated=True))
            newscore = newscore - 0.8/len(s2)**1.6
            return newscore
        # Get the similarity score of the two words if one letter is added
        if len(s1) + 1 == len(s2):
            newscore = 0
            for i in range(len(s2)):
                newscore = max(newscore, similarity_score(s1, s2[:i] + s2[i + 1:], iterated=True))
            newscore = newscore - 0.8/len(s1)**1.6
            return newscore
        # Get the similarity score of the two words if one letter is replaced
        if len(s1) == len(s2):
            newscore = 0
            j = 0
            for i in range(len(s1)):
                oldscore = newscore
                newscore = max(newscore, similarity_score(s1[:i] + s2[i] + s1[i + 1:], s2, iterated=True))
                if newscore > oldscore:
                    j = i
            distance = math.sqrt((keyboard[s1[j]][0] - keyboard[s2[j]][0])**2 
                                + (keyboard[s1[j]][1] - keyboard[s2[j]][1])**2)
            newscore = newscore - 0.8*distance/len(s1)**1.6
            return newscore
    # If the two words are not of equal length, then the similarity score is penalized accordingly
    if len(s1) != len(s2):
        score -= 1*(1 - abs(len(s1) - len(s2))/max(len(s1), len(s2))**1.5)
    # The score is further penalized according to how few letters are in the same position
    for i in range(min(len(s1), len(s2))):
        if s1[i] != s2[i]:
            # The score is penalized far less, however, if two letters next to each other are simply swapped
            if i + 1 < min(len(s1), len(s2)) and (s1[i + 1] == s2[i] and s1[i] == s2[i + 1]):
                score -= 0.01/min(len(s1), len(s2))
                score +=0.6/min(len(s1), len(s2))
            else:
                # Penalize differently based on how close the letters are on the keyboard
                if s1[i] in keyboard and s2[i] in keyboard:
                    distance = math.sqrt((keyboard[s1[i]][0] - keyboard[s2[i]][0])**2 
                                        + (keyboard[s1[i]][1] - keyboard[s2[i]][1])**2)
                    score -= 0.6*distance/min(len(s1), len(s2))
    
                    
    return score

def autocorrect_word(word):
    """
    Finds the most similar english word to input, as calculated through the 
    similarity_score function
    """
    if word in words:
        return word
    mostsim = None
    simscore = 0
    for engword in words:
        score = similarity_score(engword, word)
        if score > simscore:
            mostsim = engword
            simscore = score
    return mostsim

def autocorrect(sentence):
    """Autocorrects a sentence using the autocorrect_word function"""
    corrected_sentence = ""
    for word in sentence.split(" "):
        corrected_sentence = corrected_sentence + autocorrect_word(word) + " "
    return corrected_sentence


# Example

print(autocorrect("tihs is an exaple entence"))

