#! /usr/bin/python3
# Simple Summarizer
# Copyright (C) 2010-2012 Tristan Havelick
# Author: Tristan Havelick <tristan@havelick.com>
# URL: <https://github.com/thavelick/summarize/>
# For license information, see LICENSE.TXT

"""
A summarizer based on the algorithm found in Classifier4J by Nick Lothan.
In order to summarize a document this algorithm first determines the
frequencies of the words in the document.  It then splits the document
into a series of sentences.  Then it creates a summary by including the
first sentence that includes each of the most frequent words.  Finally
summary's sentences are reordered to reflect that of those in the original
document.
"""

##//////////////////////////////////////////////////////
##  Simple Summarizer
##//////////////////////////////////////////////////////

from nltk.probability import FreqDist
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
import nltk.data
import operator


class SimpleSummarizer:

	# def reorder_sentences( self, output_sentences, input ):
	# 	output_sentences.sort( lambda s1, s2: input.find(s1) - input.find(s2) )
	# 	return output_sentences
	
	def get_summarized(self, input, num_sentences ):
		# TODO: allow the caller to specify the tokenizer they want
		# TODO: allow the user to specify the sentence tokenizer they want
		
		tokenizer = RegexpTokenizer('\w+')
		# get the frequency of each word in the input
		base_words = [word.lower()
			for word in tokenizer.tokenize(input)]
		words = [word  for word in base_words if word not in stopwords.words() ]
		
		tf = {}
		for word in words:
			if word in tf:
				tf[word]+=1
			else:
				tf[word]=1
		# word_frequencies = FreqDist(words)
		
		# now create a set of the most frequent words		
		sorted_tf = sorted(tf.items(), key=operator.itemgetter(1), reverse=True)
		most_frequent_words = [ sorted_tf[i][0] for i in range( min(100 , len(sorted_tf) ) ) ]
		# print (most_frequent_words)

		# break the input up into sentences.  working_sentences is used
		# for the analysis, but actual_sentences is used in the results
		# so capitalization will be correct.		
		sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
		actual_sentences = sent_detector.tokenize(input)
		working_sentences = [sentence.lower()
			for sentence in actual_sentences]

		# iterate over the most frequent words, and add the first sentence
		# that inclues each word to the result.
		output_sentences = []
		for word in most_frequent_words:
			for i in range(0, len(working_sentences)):
				if (word in working_sentences[i] and actual_sentences[i] not in output_sentences):
					output_sentences.append(actual_sentences[i])
					break
				if len(output_sentences) >= num_sentences: break
			if len(output_sentences) >= num_sentences: break

		# sort the output sentences back to their original order		
		output = []
		for sentence in actual_sentences:
			if sentence in output_sentences:
				# print (sentence)
				output.append(sentence)
		
		return output
	
	def summarize(self, input, num_sentences):
		return " ".join(self.get_summarized(input, num_sentences))

ss = SimpleSummarizer()
f = open('text','r')
ss.summarize( f.read(), 5)