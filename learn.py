import sys
import json
import collections

model_file="hmmmodel.txt"

if __name__=="__main__":
	train_file = sys.argv[1]
	emissionCollection = set()
	tagCounter = collections.Counter()
	tranProbability = collections.Counter()
	initialProbability = collections.Counter()
	finalProbability = collections.Counter()
	emissionProbability = collections.Counter()
	tagWordSet = collections.defaultdict(set)
	fin = open(train_file,'r')
	for data in fin:
		data = data.strip()
		lastTag = None
		for sample in data.split():
			emissionProbability[sample]+=1
			sample = sample.rsplit('/',1)
			emission = sample[0]
			posTag = sample[1]
			tagCounter[posTag]+=1
			tagWordSet[posTag].add(emission)
			if lastTag==None:
				initialProbability[posTag]+=1
			else: 
				tranProbability[posTag+'/'+lastTag]+=1
			lastTag = posTag
			emissionCollection.add(emission)
		finalProbability[lastTag]+=1
	countOfSequences = sum(initialProbability.values())
	for posTag in tagCounter:
		initialProbability[posTag]+=1
		finalProbability[posTag]+=1
	for sample in emissionProbability:
		emissionProbability[sample]=emissionProbability[sample]/float(tagCounter[sample.rsplit('/',1)[1]])
	for lastTag,posTag in [(x,y) for x in tagCounter for y in tagCounter]:
		tranProbability[posTag+'/'+lastTag]+=1
	countOfTags = len(tagCounter)
	for hashstring in initialProbability:
		initialProbability[hashstring]=initialProbability[hashstring]/float(countOfTags+countOfSequences)
	for hashstring in finalProbability:
		finalProbability[hashstring]=finalProbability[hashstring]/float(countOfTags+1+tagCounter[hashstring])
	for hashstring in tranProbability:
		tranProbability[hashstring]=tranProbability[hashstring]/float(countOfTags+1+tagCounter[hashstring.rsplit('/',1)[1]])
	for posTag in tagWordSet:
		tagCounter[posTag] = len(tagWordSet[posTag])
	fin.close()
	fout = open(model_file,'w')
	fout.write(json.dumps({"emission":dict(emissionProbability),"vocab":list(emissionCollection),"tags":dict(tagCounter),"transition":dict(tranProbability),"initial":dict(initialProbability),"final":dict(finalProbability)},indent=4))
	fout.close()