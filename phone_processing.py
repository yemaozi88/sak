"""Module to convert phonemes."""

def multi_character_tokenize(line, multi_character_tokens):
	"""Tries to match one of the tokens in multi_character_tokens at each position of line, starting at position 0,
	if so tokenizes and eats that token. Otherwise tokenizes a single character"""
	while line != '':
		for token in multi_character_tokens:
			if line.startswith(token) and len(token) > 0:
				yield token
				line = line[len(token):]
				break
		else:
			yield line[:1]
			line = line[1:]


def split_word(word, phoneset):
	"""
	split a line by given phoneset.
	
	Args:
		word (str): a word written in given phoneset.
		#multi_character_phones (list): the list of multicharacter phones which is considered as one phone. this can be obtained with phoneset definition such as fame_ipa.py. 
		phoneset (list): the list of phones.

	Returns:
		(word_seperated) (list): the word splitted in given phoneset. 

	"""
	multi_character_phones = extract_multi_character_phones(phoneset)
	return [phone 
		 for phone in multi_character_tokenize(word.strip(), multi_character_phones)
		 ]


def convert_phoneset(word_list, translation_key):
	"""
	Args:
		word_list (str): a list of phones written in given phoneset.
		translation_key (dict): 
	"""
	return [translation_key.get(phone, phone) for phone in word_list]


def phone_reduction(phones, reduction_key):
	multi_character_tokenize(wo.strip(), multi_character_phones)
	return [reduction_key.get(i, i) for i in phones
				  if not i in phones_to_be_removed]


def extract_multi_character_phones(phoneset):
	""" 
	Args:
		phoneset (list): 
	"""
	multi_character_phones = [i for i in phoneset if len(i) > 1]
	multi_character_phones.sort(key=len, reverse=True)
	return multi_character_phones