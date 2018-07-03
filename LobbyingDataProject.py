#Healthcare Lobbying Data Extraction Algorithm:
#An application of data mining techniques to explore congressional lobbying records 
#for patterns in pediatric special interest expenditures prior to the Affordable Care Act

#Authors: Elizabeth Harrison, Caitlin Dreisbach, Nada Basit, Jessica Keim-Malpass


#%%
import os #Import os package
import xml.etree.ElementTree as ET #Import ElementTree as ET
import pandas as pd #Import pandas package as pd
from collections import defaultdict #Import defaultdict from collections package
import unittest #Import unittest to bring in import
import matplotlib.pyplot as plt #Import matplotlib for plotting
import matplotlib
matplotlib.style.use('ggplot')
from pprint import pprint #Use this for "pretty print"

#%%
os.chdir('/Users/eihoman/Desktop/US Senate Data') #Set working directory to the master folder with all needed subfolders

#%%
folder = '2009_4/' #Assign folder of interest to variable "folder"

#%%
files = os.listdir(folder) #Use os.listdir function to extract all files from the folder

#%%  
master_dict = defaultdict(list) #Use defaultfict function to create an open dictionary to store key:value pairs in

#%%
for filename in files: #Use a for loop to open each file as "f" and parse with element tree
    if filename.endswith(".xml"): #Make sure files are all xml files
        tree = ET.parse(os.path.join(folder, filename)) #Use element tree to parse the file, assign this output to tree
        root = tree.getroot() #Get the "root" of the tree (in this case, "filings")
        filings = root.getchildren() #Get the "children" of the root (everything under "filings") and put these into a new variable, filings
        for filing in filings: #Use a for loop to extract data about each item in "filings" (which has direct data AND children with their own data)
            filing_tag, filing_data = filing.tag, filing.attrib #Assign variable names to each element's tags and attributes (keys & values)
            #Ensure that the data refers to events from the year 2009 only (since events can be filed later than they occur)
            if filing_data['Year'] != "2009": continue #Loop straight back to the start of the for loop if NOT referring to 2009 data 
            filing_id = filing_data['ID'] #Extract the ID attribute from each element in "filings"
            filing_data['Filing_ID'] = filing_id #Reassign this attribute the name "Filing_ID"
            del filing_data['ID'] #Delete the original (so as to avoid confusion and so as not to overwrite the ID's of later elements)
            master_dict[filing_tag].append(filing_data) #Append the key:value ("tag":"data") pairs to the master dictionary
            for child in filing.getchildren(): #Use a nested for loop to extract similar data from the children of "filings"
                if child.attrib: #This line ensures that the following only happens if the child has direct data (and not "grandchildren" of "filings")
                    child_tag, child_data = child.tag, child.attrib #Repeat what was done before and append data to the master dictionary...
                    child_data['Filing_ID'] = filing_id
                    master_dict[child_tag].append(child_data)
                for gc in child.getchildren(): #Do another nested loop for the "grandchildren" of the root/"filings"
                    if gc.attrib:
                        gc_tag, gc_data = gc.tag, gc.attrib
                        gc_data['Filing_ID'] = filing_id
                        master_dict[gc_tag].append(gc_data) 

#%%
len(master_dict) #Output: 8 -- this is the number of keys/"tags" in the dictionary

#%%

#This test confirms whether the loop has run correctly and that items have been placed in the dictionary
class DictTestCase(unittest.TestCase): #Name the test case to the master dictionary, brings in unittest

    def test__len(self): #Define test function
        self.assertTrue(len(master_dict)>0) #Look to see that at least one key:value pair has made it into the dictionary
        
if __name__ == '__main__': #executes the test in its entirety
    unittest.main() #Output: ran 1 test, OK

#%%
master_dict['Filing'][100] #Example of the key:value output in the direct data extracted from "Filings"
#Output: {'Amount': '20000','Filing_ID': '4EDDE173-D9DA-45DE-B921-16A2CA6D44A0','Period': '3rd Quarter (July 1 - Sep 30)'...'Year': '2009'}

#%%
master_dict['Issue'][100] #Example of the key:value output extracted from the grandchild "Issue"
#Output: {'Code': 'HEALTH ISSUES','Filing_ID': 'AE8D423C-F947-4587-AD93-4B07AD5B5E2A','SpecificIssue': "Monitor legislation...(H.R. 3200)...}

#%%
df_dict = {} #Open a dictionary, to be used for a group of dataframes

for tag_type, tag_data in master_dict.items(): #Use a for loop to extract each key:value pair from the master dictionary
#Place each value into a dataframe under the column corresponding to its key/tag...
    df_dict[tag_type] = pd.DataFrame(tag_data).convert_objects(convert_numeric=True) #Also convert all strings to float/int as necessary

#%%
df_dict['Filing'].dtypes #Look to see what types of values there are in the Filings dataframe within the dataframe dictionary
#Output:AffiliatedOrgsURL      object
#Amount                       float64
#Filing_ID                     object
#Period                        object
#Received                      object
#RegistrationEffectiveDate     object
#TerminationEffectiveDate      object
#Type                          object
#Year                           int64


#%%
df_dict['Issue'].info() #Get info about the Issue dataframe in the dataframe dictionary (for reference)
#Output: 
#RangeIndex: 40598 entries, 0 to 40597
#Data columns (total 3 columns):
#Code             40598 non-null object
#Filing_ID        40598 non-null object
#SpecificIssue    40598 non-null object

#%%
df_dict['GovernmentEntity'].iloc[0:3] #Example of the header of the dataframe "GovernmentEntity"
#Output:
#                              Filing_ID             GovEntityName
#0  DC28EF14-DDEF-417A-B961-F5B825615868  HOUSE OF REPRESENTATIVES
#1  DC28EF14-DDEF-417A-B961-F5B825615868                    SENATE
#2  6702411E-F8C1-47F3-8E61-422C414F835E  HOUSE OF REPRESENTATIVES

#%%
df_issue_amount = pd.merge(df_dict['Filing'],df_dict['Issue']) #Merge the Filings and Issue dataframes to look at amounts spent on certain issues
#Note: this is merged automatically by Filing_ID, which is the only column these dataframes have in common


#%%
ser_issue_code_amount = df_issue_amount.groupby('Code').count() #Use groupby() and count() to evaluate the previously merged dataframe
ser_issue_code_amount #Return the resulting panda series
#Output: (first few rows and last few columns)
#                                      ...   Year  SpecificIssue  
#Code                                                             
#ACCOUNTING                                    52             52  
#ADVERTISING                                  100            100  
#AEROSPACE                                    121            121  
#...

#%%
ser_code_amount = df_issue_amount.groupby('Code')['Amount'].sum() #Sum the amounts spent in 2009 (filed in the 4th quarter), sorted by each "code"/issue 
ser_code_amount #Return the resulting panda series
#Output:
#Code                                         [ Amount ($)]
#ACCOUNTING                                     53290923.0 
#ADVERTISING                                    60717697.0
#AEROSPACE                                      35195738.0
#AGRICULTURE                                    98909622.0

#%%
type(ser_code_amount)
#Output: pandas.core.series.Series (confirms that these are panda series)

#%% #Use this

pprint(ser_code_amount.index.tolist()) #Print out the index list from the series above (in order to select which ones to subset...)

#%%
#Create a list of indexes that fit into the larger category of medical/research fields
medical = [
 'ALCOHOL AND DRUG ABUSE',
 'FAMILY ISSUES/ABORTION/ADOPTION',
 'HEALTH ISSUES',
 'MEDICAL/DISEASE RESEARCH/CLINICAL LABS',
 'MEDICARE/MEDICAID',
 'PHARMACY',
 'SCIENCE/TECHNOLOGY',
 ]

medical_code_amount = ser_code_amount.loc[medical] #Call the list as a loc for the series created above

medical_code_amount #return the resulting subset of the series

#%%
medical_code_amount.plot.bar() #Create a bar plot to display the results of the amounts filed under each medical/reaserch/healthcare code
#NOTE: the y values represent dollars in 100-millions
plt.figure() #Set a new figure so that tables/plots don't overlap

#%%
type(master_dict['Issue']) #Output = list

#%%
type(master_dict['Issue'][0]) #Output = dict (thus, master_dict['Issue'] is itself a list of dictionaries)

#%%
##Queries within the specific issues
def searching(list_of_dicts): #Define the searching function
    searchterms = input("What terms would you like to search the dataset for? ") #Allow user to search any term
    search_results = []    #Open an empty list
    for i in list_of_dicts: #Use a for loop to search through each value of each item in the dictionary
        for x in i.values():    
            if searchterms in x:
                search_results.append(i) #Append any matching results to the search_results list
    return search_results #Return the finalized list

#%%
master_issues = master_dict['Issue'] #Assign the "Issue" list of dictionaries from master_dict to a new variable name, master_issues

#%%
searching(master_issues) #Apply the searching function to master_issues (test the function manually)

#%%
#Create a unit test to test the function 
class TestSearchingCase(unittest.TestCase): #Call unittest.TestCase and establish the testing class

    def test__searching_1(self): #Define test function
        dict1 = {"one":"Liz","two":"Cait"} #Create a small dictioanry
        dict2 = {"lastone":"Homan","lasttwo":"Dresibach"} #Create another small dictionary
        list_dicts = [dict1,dict2] #Bring the two dictionaries together into a list of dictionaries
        print("\nPlease search for Cait") #Prompt the user to search for Cait, specifically
        result = searching(list_dicts) #Assign the result of the search to the variable "result"
        self.assertEqual(result, [{'two': 'Cait', 'one': 'Liz'}]) #Assert that the result is equal to the dictionary with the term searched
        
if __name__ == '__main__': #Execute the test in its entirety
    unittest.main() #Output: Ran 2 tests in 3.316s, OK

#%%
list2 = master_dict['Issue'] #Set variable "list2" to the Issue list of dictionaries in master_dict
peds_issues = [] #Open an empty list 
for i in list2: #Use a very similar set-up to query the dataset regarding any dictionaries under the Issue list that refer to pediatrics
    for x in i.values():    
        if "pediatric" in x:
            peds_issues.append(i) #Append the list created above
print("All done!") #Output: All Done (will print at the end of the completed for-loop)

#%%
df_peds = pd.DataFrame(peds_issues) #Create a dataframe out of the appended list
df_peds 
#Output: 34 results (header shown below)
#                             Code                             Filing_ID  \
#0                   HEALTH ISSUES  7CD8EBA2-8C7C-4654-8C1C-1A0ADFF3117E   
#1                   HEALTH ISSUES  0FE56B2B-A970-40DE-88F3-E8DB2B30135F   
#2              SCIENCE/TECHNOLOGY  7E6A337E-AB43-4914-B99D-493FE56BD517   
#3           BUDGET/APPROPRIATIONS  BD8F771D-DB49-422B-A13C-3FE2CA4287AC   
# ...

#%%
df_peds_amount = pd.merge(df_issue_amount,df_peds) #Merge the dataframe just created with the issue_amount dataframe

#%%
df_peds_amount.items  #Check the items in the new dataframe to see whether this worked correctly (it did)

#%%
ser_peds_amount_sum = df_peds_amount.groupby('Code')['Amount'].sum() #Sum the amounts spent by Code in the pediatric dataset
ser_peds_amount_sum
#Output: 
#Code (within pediatric search)  [Amount ($)]
#BUDGET/APPROPRIATIONS             187797.0
#DISASTER PLANNING/EMERGENCIES      30000.0
#EDUCATION                         600000.0
#HEALTH ISSUES                    2061383.0
#MEDICARE/MEDICAID                 340000.0
#SCIENCE/TECHNOLOGY                320000.0
#Name: Amount, dtype: float64

#NOTE: $3,539,180 total amount spent on issues related to pediatrics in 2009 and filed in the 4th quarter of that year

#%%
ser_peds_code_count = df_peds_amount.groupby('Code')["SpecificIssue"].count() #Count the number of times each code comes up in the dataframe
ser_peds_code_count #Return the resulting series (note, "SpecificIssue" was chosen arbitrarily so that only one series resulted from the count)
#Code
#BUDGET/APPROPRIATIONS             8
#DISASTER PLANNING/EMERGENCIES     1
#EDUCATION                         1
#HEALTH ISSUES                    19
#MEDICARE/MEDICAID                 5
#SCIENCE/TECHNOLOGY                1

#%%
ser_peds_code_count.plot.pie(figsize=(7,7)) #Create a pie plot to display how frequently pediatric issues were filed under certain codes
plt.figure() #Set a new figure so that tables/plots don't overlap

#%%

list3 = master_dict['Issue'] #Repeat query in a very similar way as before, but this time for "maternal" issues...
maternal_issues = []
for i in list3:
    for x in i.values():    
        if "maternal" in x:
            maternal_issues.append(i)
print("All done!")

#%%
df_maternal = pd.DataFrame(maternal_issues) #Put maternal issues list into a new dataframe
df_maternal

#%%
df_maternal_amount = pd.merge(df_issue_amount,df_maternal) #Merge the maternal dataframe with the issue_amount dataframe

#%%
ser_maternal_amount_sum = df_maternal_amount.groupby('Code')['Amount'].sum() #Sum the amounts filed in 2009/Q4 for maternal issues under specific codes
ser_maternal_amount_sum
#Output: 
#BUDGET/APPROPRIATIONS              40000.0
#FAMILY ISSUES/ABORTION/ADOPTION    35000.0
#FOREIGN RELATIONS                      NaN
#HEALTH ISSUES                      20000.0
#TOBACCO                            10000.0

#NOTE: $105,000 total amount spent on issues specified to be related to maternal [health] in 2009 and filed in the 4th quarter of that year