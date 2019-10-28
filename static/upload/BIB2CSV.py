
import json
import csv
import os
import pandas as pd


class BIB2CSV:
    def __init__(self, CSVName, BIBName,JsonName):
        self.CSVName = CSVName
        self.BIBName = BIBName
        self.JsoName = JsonName
        self.BIBData = {}

    def make_dict(self):
        with open(self.BIBName, 'r', encoding="utf8") as BIBFilePointer:
            line1 = ''
            longline = False
            for line in BIBFilePointer:
                line = line.strip()
                if line == '':
                    continue
                    
                if '@' not in line and not line.endswith('},') and not line.endswith('},}') and not line.startswith('}'):
                    line1 += line
                    longline = True
                    continue
                if longline:
                    longline = False
                    line = line1 + line
                    line1 = ''
                if line.startswith('@'):
                    EntryKey = line[line.index('{') + 1:]
                    EntryKey = EntryKey.replace(',', '{')
                    entry_type = line[line.index('@')+1:line.index('{')]
                    self.BIBData[EntryKey] = {}
                    self.BIBData[EntryKey]['EntryType'] = entry_type
                else:
                    try:
                        field_name = line[:line.index('=')].strip()
                        field_value = line[line.index('{') + 1:line.index('}')].strip()
                        self.BIBData[EntryKey][field_name] = field_value
                    except:
                        print('The entry number ' + EntryKey + 'is not written according to Bib standard')

        BIBFilePointer.close()
        # Save it to json file for future use
        with open(self.JsoName, 'w') as jo:
            json.dump(self.BIBData, jo, indent=2)
            jo.close()

    def CreateCSV(self):
        # pdb.set_trace()

        BIBKeys = [Key for Key in self.BIBData]
        CSVHeader = ['ItemKey']
        for HeaderItem in self.BIBData[BIBKeys[1]]:
            CSVHeader.append(HeaderItem)


        with open('CSVTemp.csv', 'w', encoding='utf-8', newline='') as CSVFilePointer:
            CSVWriterPointer = csv.writer(CSVFilePointer)
            for BibKey in self.BIBData:
                CSVLineContent = []
                # This loop take an item from the CSV and put its value in the CSV line
                for HeaderItem in CSVHeader:
                    if HeaderItem == "ItemKey":
                        CSVLineContent.append(BibKey)
                        continue
                    if HeaderItem in self.BIBData[BibKey]:
                        CSVLineContent.append(self.BIBData[BibKey][HeaderItem])
                    else:
                        CSVLineContent.append('')

                # This loop search for a new head item an add it to the CSV head
                for HeaderItem in self.BIBData[BibKey]:
                    if HeaderItem not in CSVHeader:
                        CSVHeader.append(HeaderItem)
                        CSVLineContent.append(self.BIBData[BibKey][HeaderItem])

                CSVWriterPointer.writerow(CSVLineContent)

        # print(CSVFilePointer.closed)

        with open('CSVTemp.csv') as CSVFilePointer:
            CSVReaderPointer = csv.reader(CSVFilePointer)
            with open(self.CSVName, 'w+', newline='') as CSVFilePointer2:
                CSVWriterPointer = csv.writer(CSVFilePointer2)
                CSVWriterPointer.writerow(CSVHeader)
                for Row in CSVReaderPointer:
                    CSVWriterPointer.writerow(Row)
        os.remove('CSVTemp.csv')



def main():
    BIBName = '/var/www/sasr/static/upload/1.bib'
    CSVName ='/var/www/sasr/static/upload/CSVFile.csv'
    JsonName = '/var/www/sasr/static/upload/1.json'
    BibConverter = BIB2CSV(CSVName, BIBName, JsonName)
    BibConverter.make_dict()
    BibConverter.CreateCSV()


if __name__ == '__main__':
    main()
