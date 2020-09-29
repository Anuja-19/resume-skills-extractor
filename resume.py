#installing required libraries
pip install pdfminer.six
pip install pandas
pip install spacy

#import required libraries
import io
import pandas
import spacy
import nltk
nltk.download()
import os
#importing stop words
import nltk
nltk.download('stopwords')


stop_words = set(nltk.corpus.stopwords.words('english'))


#getting the resumes dataset ready
directory = "/Resumes_Dataset"
count=0

for file in os.listdir(directory):
  #os.rename(directory+"/"+file,directory+"/"+str(count)+".pdf")
  count+=1
print(count)


#converting pdf to text
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as fh:
        for page in PDFPage.get_pages(fh, caching=True, check_extractable=True):
            resource_manager_obj = PDFResourceManager()
            fake_file_handle = io.StringIO()
            
            converter_object = TextConverter(
                                resource_manager_obj, 
                                fake_file_handle, 
                                codec='utf-8', 
                                laparams=LAParams()
                        )

            page_interpreter_object = PDFPageInterpreter(
                                resource_manager_obj, 
                                converter_object
                            )

            page_interpreter_object.process_page(page)
            
            text = fake_file_handle.getvalue()
            yield text

            # close open handles
            converter.close()
            fake_file_handle.close()

resumes_text = {}
pdfNo=-1
for file in os.listdir(directory):
  if(file.endswith(".pdf")):
    file = directory+"/"+str(file)
    pdfNo+=1
    temp=""
    for page in extract_text_from_pdf(file):
      temp += ' ' + page
    resumes_text[pdfNo]  =temp

nltk.download('punkt')

# removing duplicates
i=0
resumes_text_final={}
for key,value in resumes_text.items():
  if(value not in resumes_text_final):
    resumes_text_final[key]=value
    i+=1

#tokenizing sentences from resumes
sentence_wise_resumes ={}
from nltk import sent_tokenize
for key,value  in resumes_text_final.items():
  item_sent = sent_tokenize(value)
  sentence_wise_resumes[key] = item_sent

#tokenizing words from resumes
from nltk.tokenize import word_tokenize
tokenized_words={}
for key,value  in resumes_text_final.items():
  item_word = word_tokenize(value)
  nopunc = [word for word in item_word if word.isalpha() and word not in stop_words]
  tokenized_words[key] = nopunc

#getting non technical skills dataset
import json
skills_path = "/cleaned_related_skills.json"
with open(skills_path) as s:
  skills = json.load(s)


skills_list = []
for skill_name in skills:
   skills_list.append(skill_name["name"])
   skills_list.append(skill_name["related_1"])
   skills_list.append(skill_name["related_2"])
   skills_list.append(skill_name["related_3"])
  


#getting technical datasets
import csv
tech_skills= pd.read_csv('/techskill.csv')



#extracting technical skills


import pandas as pd
import spacy

# using pre-trained model from spacy
model = spacy.load('en_core_web_sm')
def extract_skills(resume_text):
    nlp_text = model(resume_text)
    doc = nlp(resume_text)
    nouns = doc.noun_chunks
    tokens = [token.text for token in nlp_text if not token.is_stop]    
    skillset_individual = []
    
    for token in tokens:
        if token.lower() in list(tech_skills):
            skillset_individual.append(token)
    
    for token in nouns:
        token = token.text.lower().strip()
        if token in skills_list:
            skillset_individual.append(token)
    
    return [i.capitalize() for i in set([i.lower() for i in skillset_individual])]

extracted_skills={}
for key,value in resumes_text_final.items():
  extracted_skills[key] = extract_skills(value)




#extracting non technical skills

import pandas as pd
import spacy

# using pre-trained model from spacy
model = spacy.load('en_core_web_sm')
def extract_non_tech_skills(resume_text):
    nlp_text = model(resume_text)
    doc = nlp(resume_text)
    nouns = doc.noun_chunks
    tokens = [token.text for token in nlp_text if not token.is_stop]    
    skillset_individual = []
    
    for token in tokens:
        if token.lower() in skills_list:
            skillset_individual.append(token)
    
    for token in nouns:
        token = token.text.lower().strip()
        if token in skills_list:
            skillset_individual.append(token)
    
    return [i.capitalize() for i in set([i.lower() for i in skillset_individual])]

extracted_non_tech_skills={}
for key,value in resumes_text_final.items():
  extracted_non_tech_skills[key] = extract_non_tech_skills(value)


# getting hot tech skills
from collections import Counter 

list_of_tech_skills=[]
for key,value in extracted_skills.items():
  list_of_tech_skills.append(value) 
  
#getting hot non-tech skills
list_of_non_tech_skills=[]
for key,value in extracted_non_tech_skills.items():
  list_of_non_tech_skills.append(value) 



single_list_of_tech_skills=[]
for l in list_of_tech_skills:
  for item in l :
    if(item not in stop_words):
      single_list_of_tech_skills.append(item)


cnter = Counter(single_list_of_tech_skills)
most_common_tech_skills = cnter.most_common(10)



single_list_of_non_tech_skills=[]
for l in list_of_non_tech_skills:
  for item in l :
    if(item not in stop_words):
      single_list_of_non_tech_skills.append(item)


cnter = Counter(single_list_of_non_tech_skills)
most_common_non_tech_skills = cnter.most_common(10)



import pandas

df= pd.DataFrame(most_common_tech_skills)

#getting skills of each resume which are trending

hot_tech_skills_of_each ={}
for key,value in extracted_skills.items():
  temp = []
  for skill in value:
    if (skill in list(df[0])):
     temp.append(skill)
     #print(temp)
  hot_tech_skills_of_each[key] = temp


#rating skills of each student

word_freq ={}
for key,value in tokenized_words.items():
  temp =[]
  temp_counter =Counter()
  for l in value:
    if(l in extracted_skills[key]):
      temp.append(l)
    temp_counter = Counter(temp)
  word_freq[key]=temp_counter.most_common(3)






common_skills_dataframe = pd.DataFrame(most_common_non_tech_skills)


#plotting tech skills vs count
import plotly.graph_objs as go
import plotly.offline as p


graph_data = [go.Bar(
   x = list(common_skills_dataframe[0]),
   y = list(common_skills_dataframe[1])
)]
fig = go.Figure(data=graph_data)
p.iplot(fig)

#plotting non tech skills vs count
graph_data = [go.Bar(
   x = list(df[0]),
   y = list(df[1])
)]
fig = go.Figure(data=graph_data)
p.iplot(fig)







