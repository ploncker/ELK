__author__ = 'ashmaro1'
#http://stackoverflow.com/questions/15737806/extract-text-using-pdfminer-and-pypdf2-merges-columns

from pdfminer.pdfdocument import PDFDocument, PDFNoOutlines
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LTPage, LTChar, LTAnno, LTTextBox, LTTextLine


class PDFPageDetailedAggregator(PDFPageAggregator):
    def __init__(self, rsrcmgr, pageno=1, laparams=None):
        PDFPageAggregator.__init__(self, rsrcmgr, pageno=pageno, laparams=laparams)
        self.rows = []
        self.page_number = 0
    def receive_layout(self, ltpage):
        def render(item, page_number):
            if isinstance(item, LTPage) or isinstance(item, LTTextBox):
                for child in item:
                    render(child, page_number)
            elif isinstance(item, LTTextLine):
                child_str = ''
                for child in item:
                    if isinstance(child, (LTChar, LTAnno)):
                        child_str += child.get_text()
                child_str = ' '.join(child_str.split()).strip()
                if child_str:
                    row = (page_number, item.bbox[0], item.bbox[1], item.bbox[2], item.bbox[3], child_str) # bbox == (x1, y1, x2, y2)
                    self.rows.append(row)
                for child in item:
                    render(child, page_number)
            return
        render(ltpage, self.page_number)
        self.page_number += 1
        self.rows = sorted(self.rows, key = lambda x: (x[0], -x[2]))
        self.result = ltpage

from pprint import pprint
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.layout import LAParams
import pandas as pd
import glob
import timeit
#import collections


def readpdf(pdfFile):
    fp = open(pdfFile, 'rb')
    parser = PDFParser(fp)
    doc = PDFDocument(parser)
    #doc.initialize('password') # leave empty for no password

    rsrcmgr = PDFResourceManager()
    laparams = LAParams()
    laparams.char_margin = float('1.1') #too small and it splits the description, too big and Quantity-Unit-Part number are not separated: 1.1 seems to work
    laparams.line_margin = float('0.8')
    device = PDFPageDetailedAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)

    for page in PDFPage.create_pages(doc):
        interpreter.process_page(page)
        # receive the LTPage object for this page
        device.get_result()

    #print(device.rows)
    df = pd.DataFrame(device.rows, columns=['Page', 'x', 'y', 'c1','c2','String'])
    return df


def format(df):
    # create text rows from 'y' coordinate data

    PO_Number =df['String'][df['c1']>810].values.tolist()
    Vendor = [','.join(df['String'][(df["x"] > 31) & (df["x"] <32)].values.tolist()[1:])]
    Invoice_to = [','.join(df['String'][(df["x"] > 552) & (df["x"] <553)].values.tolist()[1:])]

    df['c2'] = df['c2'].astype('int')
    result = df.sort(['c1','c2'], ascending=True, axis=0)
    lines = result.groupby(['Page','c2'])

    #expand each row
    row_dict = lines.groups
    od = sorted(row_dict.keys(), key=lambda row: row[1],reverse=True) #sort by row
    od = sorted(od, key=lambda row: row[0]) #sort by page number
    ndict = [(i, row_dict[i]) for i in od]
    mylist = [df.iloc[item,0:] for key, item in ndict if len(item)>4]


    col=['PO_Number', 'Vendor', 'Invoice_to', 'Line item','Quantity', 'Unit', 'Part_Number', 'Description', 'Due_Date', 'Inventory','Unit_Price', 'GST', 'Line value']
    df2=pd.DataFrame(columns=col)
    items=[]
    for item in mylist:
        if len(item['String'].values.tolist())==10:
            if item['String'].values.tolist()[0] != 'Line':
                #print 'its a header'
            #else:
                row = item['String'].values.tolist()
                items.append(row)
        elif len(item['String'].values.tolist())<10:
            row=[]
            if 143 not in item["x"].astype(int).values.tolist():
                # no Part Number
                #print 'we got here'
                row = item['String'].values.tolist()
                row.insert(3,'--')
            if 268 not in item["x"].astype(int).values.tolist():
                # no description
                #print 'we got here'
                row = item['String'].values.tolist()
                row.insert(4,'--')
            if 699 not in item["c1"].astype(int).values.tolist():
                # no Unit Price or Line Value
                if len(row)==0:
                    row = item['String'].values.tolist()
                row.insert(7,0)
                row.insert(9,0)
            items.append(row)

    for i in range(0,len(items),1):
        row=items[i]
        row.insert(0,Invoice_to)
        row.insert(0,Vendor)
        row.insert(0,PO_Number)
        if len(row)==len(col):
            df2.loc[i] = row
        else:
            print "--------------conversion failed-----------------------------------"
            print "--------------conversion failed-----------------------------------"
            print "--------------conversion failed-----------------------------------"
            print "--------------conversion failed-----------------------------------"
            print "--------------conversion failed-----------------------------------"
            print "--------------conversion failed-----------------------------------"

    return df2

if __name__ == '__main__':

    source = r'C:/Users/ashmaro1/Documents/_Projects/Glencore/'
    #source = r'S:/Bhavani/Aaron'
    dest = r'C:/Users/ashmaro1/Documents/GitHub/Text-Analysis/PDFnOCR/output/suppChain/test/'
    #pdf = 'POxca-000052-R201631.pdf'
    #pdf = 'POxca-000078-AN168840.pdf'
    #pdf = 'POxca-000078-AN168846.pdf'
    #pdf = 'POxca-000078-AN168968.pdf'
    #pdf = 'POxca-000510-BX425914.pdf'

    # input = source+pdf
    # df=readpdf(input)
    # df2=format(df)
    # print df2
    # output = dest+pdf
    # df2.to_csv(output)

    start_time = timeit.default_timer()
    pdffiles = glob.glob(r'C:\Users\ashmaro1\Documents\_Projects\Glencore\*.pdf')
    for input in pdffiles:
        df=readpdf(input)
        df2=format(df)
        #print df2
        pdf=input[47:]
        csv=pdf[:-3]+'csv'
        output = dest+csv
        print pdf
        df2.to_csv(output)
    elapsed = timeit.default_timer() - start_time
    print("--- %s seconds ---" % elapsed )