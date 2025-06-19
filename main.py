import json
import time
from typing import List, Dict, Tuple, Set
from collections import defaultdict
import pickle
import os

class BrailleAutocorrect:
    def __init__(self, dictionary_file: str = None):
        self.qwerty_to_dot = {
            'D': 1, 'W': 2, 'Q': 3, 'K': 4, 'O': 5, 'P': 6
        }
        
        self.braille_patterns = {
            frozenset([1]): 'A',
            frozenset([1, 2]): 'B',
            frozenset([1, 4]): 'C',
            frozenset([1, 4, 5]): 'D',
            frozenset([1, 5]): 'E',
            frozenset([1, 2, 4]): 'F',
            frozenset([1, 2, 4, 5]): 'G',
            frozenset([1, 2, 5]): 'H',
            frozenset([2, 4]): 'I',
            frozenset([2, 4, 5]): 'J',
            frozenset([1, 3]): 'K',
            frozenset([1, 2, 3]): 'L',
            frozenset([1, 3, 4]): 'M',
            frozenset([1, 3, 4, 5]): 'N',
            frozenset([1, 3, 5]): 'O',
            frozenset([1, 2, 3, 4]): 'P',
            frozenset([1, 2, 3, 4, 5]): 'Q',
            frozenset([1, 2, 3, 5]): 'R',
            frozenset([2, 3, 4]): 'S',
            frozenset([2, 3, 4, 5]): 'T',
            frozenset([1, 3, 6]): 'U',
            frozenset([1, 2, 3, 6]): 'V',
            frozenset([2, 4, 5, 6]): 'W',
            frozenset([1, 3, 4, 6]): 'X',
            frozenset([1, 3, 4, 5, 6]): 'Y',
            frozenset([1, 3, 5, 6]): 'Z',
            frozenset([]): ' '
        }
        
        self.letter_to_braille = {v: k for k, v in self.braille_patterns.items()}
        
        self.dictionary = set()
        self.trie = {}
        self.word_frequencies = defaultdict(int)
        
        self.user_corrections = defaultdict(list)
        self.correction_cache = {}
        
        if dictionary_file and os.path.exists(dictionary_file):
            self.load_dictionary(dictionary_file)
        else:
            self._initialize_default_dictionary()
    
    def _initialize_default_dictionary(self):
        basic_words = [
            "THE", "AND", "FOR", "ARE", "BUT", "NOT", "YOU", "ALL", "CAN", "HER", "WAS", "ONE",
            "OUR", "OUT", "DAY", "HAD", "HAS", "HIS", "HOW", "ITS", "NEW", "NOW", "OLD", "SEE",
            "TWO", "WHO", "BOY", "DID", "GET", "HIM", "OWN", "SAY", "SHE", "TOO", "USE", "WAY",
            "WORK", "MAKE", "TAKE", "COME", "GIVE", "GOOD", "LONG", "MANY", "OVER", "SUCH", "TIME",
            "VERY", "WELL", "YEAR", "BACK", "CALL", "CAME", "EACH", "FIND", "HAND", "HIGH", "KEEP",
            "KIND", "LAST", "LEFT", "LIFE", "LIVE", "LOOK", "MADE", "MOVE", "MUCH", "NAME", "NEED",
            "NEXT", "OPEN", "PART", "PLAY", "RIGHT", "SAID", "SAME", "SEEM", "SHOW", "SIDE", "TELL",
            "TURN", "WANT", "WAYS", "WEEK", "WENT", "WERE", "WHAT", "WHEN", "WITH", "WORD", "WORLD",
            "WRITE", "WOULD", "YEARS", "YOUNG", "ABOUT", "AFTER", "AGAIN", "ALONG", "BEING", "COULD",
            "EVERY", "FIRST", "FOUND", "GREAT", "GROUP", "HOUSE", "LARGE", "LIGHT", "MIGHT", "NEVER",
            "OTHER", "PLACE", "POINT", "SMALL", "SOUND", "STILL", "THINK", "THOSE", "THREE", "WATER",
            "WHERE", "WHILE", "WORDS", "WRITE", "HELLO", "WORLD", "BRAILLE", "COMPUTER", "KEYBOARD"
        ]
        
        for word in basic_words:
            self.add_word_to_dictionary(word)
    
    def qwerty_to_braille_pattern(self, qwerty_input: str) -> frozenset:
        
        dots = set()
        for char in qwerty_input.upper():
            if char in self.qwerty_to_dot:
                dots.add(self.qwerty_to_dot[char])
        return frozenset(dots)
    
    def braille_pattern_to_letter(self, pattern: frozenset) -> str:
        return self.braille_patterns.get(pattern, '?')
    
    def word_to_braille_patterns(self, word: str) -> List[frozenset]:
        patterns = []
        for char in word.upper():
            if char in self.letter_to_braille:
                patterns.append(self.letter_to_braille[char])
            else:
                patterns.append(frozenset())
        return patterns
    
    def braille_patterns_to_word(self, patterns: List[frozenset]) -> str:
        word = ""
        for pattern in patterns:
            word += self.braille_pattern_to_letter(pattern)
        return word
    
    def add_word_to_dictionary(self, word: str):
        word = word.upper().strip()
        if not word:
            return
            
        self.dictionary.add(word)
        self.word_frequencies[word] += 1
        
        patterns = self.word_to_braille_patterns(word)
        current = self.trie
        
        for pattern in patterns:
            pattern_key = tuple(sorted(pattern))
            if pattern_key not in current:
                current[pattern_key] = {}
            current = current[pattern_key]
        
        current['_word'] = word
        current['_frequency'] = self.word_frequencies[word]
    
    def load_dictionary(self, file_path: str):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                words = json.load(f)
                if isinstance(words, list):
                    for word in words:
                        self.add_word_to_dictionary(word)
                elif isinstance(words, dict):
                    for word, freq in words.items():
                        self.word_frequencies[word] = freq
                        self.add_word_to_dictionary(word)
        except Exception as e:
            print(f"Error loading dictionary: {e}")
            self._initialize_default_dictionary()
    
    def save_dictionary(self, file_path: str):
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(dict(self.word_frequencies), f, indent=2)
        except Exception as e:
            print(f"Error saving dictionary: {e}")
    
    def levenshtein_distance(self, s1: List[frozenset], s2: List[frozenset]) -> int:
        if len(s1) < len(s2):
            return self.levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    def pattern_similarity(self, p1: frozenset, p2: frozenset) -> float:
        if p1 == p2:
            return 1.0
        
        intersection = len(p1 & p2)
        union = len(p1 | p2)
        
        if union == 0:
            return 1.0
        
        return intersection / union
    
    def fuzzy_search_trie(self, input_patterns: List[frozenset], max_distance: int = 2) -> List[Tuple[str, int, float]]:
        
        results = []
        
        def search_recursive(node, word_patterns, input_idx, current_distance, path):
            if input_idx >= len(input_patterns):
                if '_word' in node:
                    confidence = 1.0 / (1.0 + current_distance)
                    results.append((node['_word'], current_distance, confidence))
                return
            
            if current_distance > max_distance:
                return
            
            current_input = input_patterns[input_idx]
            
            for pattern_key in node:
                if isinstance(pattern_key, str) and pattern_key.startswith('_'):
                    continue
                
                pattern = frozenset(pattern_key)
                
                if pattern == current_input:
                    search_recursive(node[pattern_key], word_patterns + [pattern], 
                                   input_idx + 1, current_distance, path + [pattern])
                
                elif current_distance < max_distance:
                    similarity = self.pattern_similarity(pattern, current_input)
                    if similarity > 0.3:
                        distance_increase = 1 if similarity < 0.8 else 0
                        search_recursive(node[pattern_key], word_patterns + [pattern],
                                       input_idx + 1, current_distance + distance_increase, 
                                       path + [pattern])
            
            if current_distance < max_distance:
                search_recursive(node, word_patterns, input_idx + 1, 
                               current_distance + 1, path)
            
            if current_distance < max_distance:
                for pattern_key in node:
                    if isinstance(pattern_key, str) and pattern_key.startswith('_'):

                        continue
                    pattern = frozenset(pattern_key)
                    search_recursive(node[pattern_key], word_patterns + [pattern],
                                   input_idx, current_distance + 1, path + [pattern])
        
        search_recursive(self.trie, [], 0, 0, [])
        return results
    
    def get_suggestions(self, qwerty_input: str, max_suggestions: int = 5) -> List[Tuple[str, float]]:
        
        cache_key = qwerty_input.strip().upper()
        if cache_key in self.correction_cache:
            return self.correction_cache[cache_key]
        
        qwerty_chars = qwerty_input.strip().split()
        if not qwerty_chars:
            return []
        
        input_patterns = []
        for char_combo in qwerty_chars:
            pattern = self.qwerty_to_braille_pattern(char_combo)
            input_patterns.append(pattern)
        
        word_attempt = self.braille_patterns_to_word(input_patterns)
        if word_attempt in self.dictionary:
            result = [(word_attempt, 1.0)]
            self.correction_cache[cache_key] = result
            return result
        
        candidates = self.fuzzy_search_trie(input_patterns, max_distance=3)
        
        scored_candidates = []
        for word, distance, confidence in candidates:
            frequency_score = self.word_frequencies.get(word, 1)
            final_score = confidence * (1 + 0.1 * min(frequency_score, 10))
            scored_candidates.append((word, final_score))
        
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        result = scored_candidates[:max_suggestions]
        
        self.correction_cache[cache_key] = result
        
        return result
    
    def learn_correction(self, original_input: str, corrected_word: str):
        """Learn from user corrections to improve future suggestions."""
        original_input = original_input.strip().upper()
        corrected_word = corrected_word.strip().upper()
        
        self.user_corrections[original_input].append(corrected_word)
        
        self.word_frequencies[corrected_word] += 5
        
        if corrected_word not in self.dictionary:
            self.add_word_to_dictionary(corrected_word)
        
        if original_input in self.correction_cache:
            del self.correction_cache[original_input]
    
    def save_learning_data(self, file_path: str):
        data = {
            'user_corrections': dict(self.user_corrections),
            'word_frequencies': dict(self.word_frequencies)
        }
        with open(file_path, 'wb') as f:
            pickle.dump(data, f)
    
    def load_learning_data(self, file_path: str):
        try:
            with open(file_path, 'rb') as f:
                data = pickle.load(f)
                self.user_corrections = defaultdict(list, data.get('user_corrections', {}))
                self.word_frequencies.update(data.get('word_frequencies', {}))
        except Exception as e:
            print(f"Error loading learning data: {e}")
    
    def get_statistics(self) -> Dict:
        return {
            'dictionary_size': len(self.dictionary),
            'cache_size': len(self.correction_cache),
            'learned_corrections': len(self.user_corrections),
            'total_word_frequency': sum(self.word_frequencies.values())
        }


def main():
    print("Braille Autocorrect System")
    
    autocorrect = BrailleAutocorrect()
    
    test_cases = [
        ("D", "A"),
        ("DW", "B"),
        ("DK", "C"),
        ("D W Q", "THE"),
        ("DW DKO", "Suggestions for 'B' + complex pattern"),
        ("DWQK", "Complex single character"),
    ]
    
    print("Testing Braille Pattern Recognition:")
    
    for qwerty_input, expected in test_cases:
        suggestions = autocorrect.get_suggestions(qwerty_input, max_suggestions=3)
        print(f"Input: '{qwerty_input}'")
        print(f"Expected: {expected}")
        print(f"Suggestions: {suggestions}")
        print()
    
    print("Interactive Mode (type 'quit' to exit):")
    print("Enter QWERTY Braille input (space-separated for multiple characters):")
    print("Example: 'D' for A, 'DW' for B, 'D DW Q' for multiple characters")
    print()
    
    while True:
        try:
            user_input = input("Braille Input: ").strip()
            if user_input.lower() == 'quit':
                break
            
            if not user_input:
                continue
            
            start_time = time.time()
            suggestions = autocorrect.get_suggestions(user_input, max_suggestions=5)
            end_time = time.time()
            
            print(f"Suggestions (processed in {(end_time - start_time)*1000:.2f}ms):")
            for i, (word, confidence) in enumerate(suggestions, 1):
                print(f"  {i}. {word} (confidence: {confidence:.3f})")
            
            if suggestions:
                correct = input("Was suggestion correct? (y/n/word): ").strip()
                if correct.lower() not in ['y', 'yes', '']:
                    if correct.lower() not in ['n', 'no']:
                        autocorrect.learn_correction(user_input, correct)
                        print(f"Learned: '{user_input}' -> '{correct}'")
            
            print()
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")
    
    stats = autocorrect.get_statistics()
    print("\nSystem Statistics:")
    for key, value in stats.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()