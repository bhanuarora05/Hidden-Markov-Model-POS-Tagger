import sys
import json
import math

output_file="hmmoutput.txt"
model_file="hmmmodel.txt"

if __name__=="__main__":
	input_file = sys.argv[1]
	fin = open(model_file,'r')
	jsonObj = json.loads(fin.read())
	fin.close()
	emissionList = jsonObj['vocab']
	tagList = jsonObj['tags']
	OpenEndedTags = [(index,posTag) for index,posTag in enumerate(list(tagList.keys()))]
	OpenEndedTags = sorted(OpenEndedTags,key=lambda tup: tagList[tup[1]],reverse=True)
	OpenEndedTags = OpenEndedTags[:int(((3*5)/100)*len(OpenEndedTags))]
	tagList = list(tagList.keys())
	tranProbability = jsonObj['transition']
	initialProbability = jsonObj['initial']
	finalProbability = jsonObj['final']
	emissionProbability = jsonObj['emission']
	fin = open(input_file,'r')
	fout = open(output_file,'w')
	for data in fin:
		data = data.strip()
		value = {}
		retrace = {}
		for i in range(0,len(tagList)):
			value[i]={}
			retrace[i]={}
		observation = data.split()[0]
		if observation in emissionList:
			for i,posTag in enumerate(tagList):
				hashstring = observation+'/'+posTag
				if hashstring not in emissionProbability:
					continue
				else:
					value[i][0] = math.log(emissionProbability[hashstring])
					value[i][0] += math.log(initialProbability[posTag])
					retrace[i][0] = -1
		else:
			for i,posTag in OpenEndedTags:
				value[i][0] = math.log(initialProbability[posTag])
				retrace[i][0] = -1
		for step,observation in list(enumerate(data.split()))[1:]:
			if observation in emissionList:
				for i,posTag in enumerate(tagList):
					hashstring = observation+'/'+posTag
					if hashstring not in emissionProbability:
						continue
					else:
						temp = [(math.log(tranProbability[posTag+'/'+tagList[j]])+value[j][step-1]+math.log(emissionProbability[hashstring]),j) for j in range(0,len(tagList)) if (step-1) in value[j]]
						value[i][step],retrace[i][step] = max(temp)
			else:
				for i,posTag in OpenEndedTags:
					temp = [(math.log(tranProbability[posTag+'/'+tagList[j]])+value[j][step-1],j) for j in range(0,len(tagList)) if (step-1) in value[j]]
					value[i][step],retrace[i][step] = max(temp)

		temp = [(math.log(finalProbability[tagList[j]])+value[j][step],j) for j in range(0,len(tagList)) if (step) in value[j]]
		ptr = max(temp)[1]
		arr = []
		for step,observation in reversed(list(enumerate(data.split()))):
			arr = [observation,'/',tagList[ptr],' ']+arr
			ptr = retrace[ptr][step]
		fout.write(''.join(arr)+"\n")
	fout.close()
	fin.close()