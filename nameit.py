from collections import Counter
import re

non_name_smbls = r':;~!#$%^&*=<>?/\|.,' #list of symbols that shoud not be present in a name
nmbrs = '1234567890'
punct_marks = """,.:;!?"'""" # regular punctuation  marks can be found in a sentence

def count_freq_words(alltxt, n = 4):
    """Count frequent words in alltxt and returns words with occurance > n """
    if type(alltxt)==list:
        words = alltxt
    else:
        words = [x.strip().strip(non_name_smbls) for nm in alltxt.split() for x in nm.translate({ord(c): None for c in nmbrs + non_name_smbls + '-'}).split()]
        words = [w for w in words if len(w)>1]
    cnt = Counter(words)
    notnames_list = []
    mostcommon_cntr = cnt.most_common()
    for cnted_word in mostcommon_cntr:
        wrd, noccur = cnted_word
        if noccur>n:
            notnames_list.append(wrd)
    return notnames_list, cnt

def filter_names(names, filter_list = []):
    """Function filters possible name string leaving only relevant words"""

    #todo: clean up this part, too complicated and messy  

    if len(names.strip().split()) <= 1:
        return ''
    #check names with ` (apostrofe)
    #if names contains only lastname and one or two initials return it
    namesin = names

    regex_initials = r'\s[A-Za-z][\s\.\,]|\s[A-Za-z]$|^[A-Za-z][\s\.\,]'
    rsltname = [nm for nm in names.split() if nm.lower() not in filter_list]
    names = ' '.join([nm for nm in rsltname if not(bool(re.search(r'[\d]', nm))) ])
    #result = ' '.join(names)
        
    initials = re.findall(regex_initials, names)
    possiblelastname = re.sub(regex_initials, ' ', names).strip()    
    #print(possiblelastname)
    if (len(initials)==1 or len(initials)==2) and len(possiblelastname.split())==1:
        if not(bool(re.search(r'[\d]', possiblelastname))):
            if len(names.strip().split())<=1:
                names=''
            return names

    names = namesin
    parenthesiswords = re.findall(r'\(.*?\)',names)
    
    for pthsword in parenthesiswords:
        names = names.replace(pthsword, ' ')
    
    filter_list.extend(parenthesiswords)
    filter_list = [fit.lower() for fit in filter_list]
    
    names = names.strip().split()
    #print(names)
    names = [nm for nm in names if nm.lower() not in filter_list]
    
    names = ' '.join(names)
    names = names.replace(',', ' ')
    names = names.replace('.', ' ')
    names = names.strip().split()
    
    names = [nm.strip(non_name_smbls) for nm in names]
    names = [nm.strip(non_name_smbls+'-') for nm in names if len(nm) > 1]

    names = [nm for nm in names if not(bool(re.search(r'[\d]', nm))) or bool(re.search(r'[\W]', nm.replace('-', ''))) ]
    names = [nm for nm in names if nm.lower() not in filter_list]
    
    names = [nm for nm in names if ((not nm.islower() and not nm.isupper()) or len(nm) == 1)]
    names = [nm if not (nm.endswith("’s") or nm.endswith("'s"))else nm[:-2] for nm in names]

    # todo: here count only words that are not included in name_prefixes
    if len(names)<=6 and len(names)>1:
        #print(rsltname)
        rsltname = [nm for nm in names if nm.lower() not in filter_list]
        result = ' '.join([nm for nm in rsltname if not(bool(re.search(r'[\d]', nm))) ])
        #result = ' '.join(names)
    else:
        result = ''
    if len(result.strip().split())<=1:
        result=''
    return result

def clean_wspaces(inputnames):
    """
    function removes extra white spaces from the element of the input list
    e.g. removes leading and trailing spaces, and extra spaces between words 
    leaving only one space between evry two words
    inputnames can be either string or a list of strings
    """

    if type(inputnames)==str:
        inputwasstring = True
        inputnames = [inputnames]
    else:
        inputwasstring = False

    for i in range(len(inputnames)):
        nameparts = [word.strip() for word in inputnames[i].strip().split()]        
        inputnames[i] = ''.join([word+' ' for word in nameparts]).strip()
        
    if inputwasstring: inputnames = inputnames[0]

    return inputnames

def remove_pq(s):
    """
    reomves text in quotes and parethesis from the input string
    """ 
    fltrlist = re.findall(r'"([A-Za-z0-9_\./\\-]*)"',s)
    fltrlist.extend(re.findall(r'\(([A-Za-z0-9_\./\\-]*)\)',s))
    fltrlist.extend(re.findall(r"([A-Za-z0-9_\./\\-]*)'",s))
    if len(fltrlist)==1:
        return s
    fltrlist = [f for f in fltrlist if f!='']
    #print(fltrlist)
    for fl in fltrlist: 
        s = s.replace(fl, '')
    s = s.split()
    s = ' '.join([x for x in s if bool(re.search(r'[A-Za-z]',x))])
    return s

def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, bs4.element.Comment):
        return False
    return True

def contains(sentence, word_list):
    """
    Check whether or not input string sentence contains any of the words from the word_list
    """
    #todo: include word stemming here
    
    if type(word_list)==list:
        word_list = [w.lower().strip() for w in word_list]
    elif type(word_list)==str:
        word_list = [word_list.lower().strip()]
    else:
        raise ValueError('Type '+type(word_list)+' is not supported for the input variable word_list ... ')
    
    #remove regular punctuation marks that can be found in a sentence
    punct_marks = """,.:;!?"'"""
    sentence = sentence.translate(dict.fromkeys(map(ord, punct_marks), ' ')) 
    words = sentence.strip().split()
    words = [w.strip('-') for w in words]
    
    for wrd in words:
        if len(wrd)<=1:
            continue

        if wrd[1]=='-':
            wrd = wrd[2:]

        if wrd.lower() in word_list:
            result=True
            break
    else:
        result = False

    return result

def name_probablity(namelist, flist_a, flist_b ):
    """ Add description """
    if len(namelist)==0:
        raise ValueError('Input list can not be empty ... ')

    numb_a = 0
    numb_b = 0
    
    for x in namelist:
        x.replace('.', ' ').replace(',', ' ')
        x = x.strip()
        #split x for words
        #and filter out one letter words
        xwords = x.split()
        xwords = [w for w in xwords if len(x)>1]
        if len(xwords)==0:
            numb_b+=1
        elif len(xwords)>1:
            numb_b+=1
        else:
            if xwords[0].lower() in flist_a:
                numb_a+=1
            elif xwords[0].lower() in flist_b:
                numb_b+=1
    
    return 1.*numb_a/len(namelist), 1.*numb_b/len(namelist)

def nameparts(namelist, first_names, last_names, prefixes = []):
    """
    Based on first_names, last_names lists split every element in namelist on first and last names
    Every element of the namelist is a full name in a fomat 'Lastname Firstname' or 'Firstname Lastname'
       can also contain second names or initials
    """
    n1_fstnm = 0
    n1_lstnm = 0
    
    n2_fstnm = 0
    n2_lstnm = 0
    nnames = len(namelist)
    names_assigned = []
    rslt_list = []
    for i, x in enumerate(namelist):
        x = remove_pq(x)
        
        # process names with Initials and last names only
        initials = re.findall(r'\s[A-Za-z][\s\.\,]|[A-Z]$|^[A-Za-z][\s\.\,]', x)
        initials = [f.strip() for f in initials]
        #name without initials

        xparts = [nm for nm in x.split() if nm.strip().lower() not in initials+prefixes]

        #if it contains only one element, this is the last name, first initial is the first name
        if len(xparts)==0:
            raise ValueError('Name must contain at least one part ... ' + 'current name = ' + str(x))

        elif len(xparts)==1:
            #nnames = nnames - 1 #decrease number of nnames by 1 since this name has different than expected parten
            
            cur_last_name = xparts[0].strip().strip(',.')
            
            if len(initials)>=1:
                cur_first_name = initials[0]
            else:
                cur_first_name = ''
                
            names_assigned.append(i)
            rslt_list.append((namelist[i], cur_first_name, cur_last_name))
            #done with this name
            continue
        
        #at this point our name should contain two or more words
        if xparts[0].lower() in first_names:
            n1_fstnm += 1
        elif xparts[0].lower() in last_names:
            n1_lstnm += 1
        
        if xparts[-1].lower() in first_names:
            n2_fstnm += 1
        elif xparts[-1].lower() in last_names:
            n2_lstnm += 1
        #namelist[i] = ' '.join(xparts)
    
    #reomve those names that we have already processed
    namelist = [namelist[i] for i in range(len(namelist)) if i not in names_assigned ]
    
    #at this point we have 4 probabilities to decide at what position we have last name
    p1_fst, p1_lst, p2_fst, p2_lst = 1.*n1_fstnm/nnames, 1.*n1_lstnm/nnames, 1.*n2_fstnm/nnames, 1.*n2_lstnm/nnames
    if (p1_fst + p2_lst)/2 >= (p1_lst + p2_fst)/2: #need a special case when prob are the same
        #then first position is the first name, last position is the last name
        for nm in namelist:
            #next two lines looks redundant, see if it is possible to combine it with the loop above
            nmparts = remove_pq(nm).strip().split()
            nmparts = [nm for nm in nmparts if nm.strip().lower() not in initials+prefixes]
            if len(nmparts)>1:
                rslt_list.append((nm, nmparts[0], nmparts[-1]))
            else:
                rslt_list.append((nm, ' ', nmparts[-1]))
    elif (p1_fst + p2_lst)/2 < (p1_lst + p2_fst)/2:
        for nm in namelist:
            nmparts = remove_pq(nm).strip().split()
            nmparts = [nm for nm in nmparts if nm.strip().lower() not in initials+prefixes]
            if len(nmparts)>1:
                rslt_list.append((nm, nmparts[-1], nmparts[0]))
            else:
                rslt_list.append((nm, ' ', nmparts[0]))
    return rslt_list

class Nameit():
    """A class for extracting names from an arbitray html pages """
    
    def __init__(self, soup):
        """Initialize object with soup  - object of the Beutifulsoup class containing html page"""
        self.soup = soup
        
        # replace <br> tags with a space, can be importnat when dealing with tables
        for tg in self.soup.find_all('br'):
            tg.replace_with(' ')

        #load first, last names, frequent english words, etc.
        self.__load_names_data()
        
    def update_names(self, tables=False):
        # todo: this finction needs attention, clean it and provide more description of what's going on and why
        
        #get all text from the visible fields
        self.visible_texts = self.get_alltext(tables = tables)

        not_names = []
        known_names = []
        other_words = []

        for txt in self.visible_texts:   
            txt = txt.translate(dict.fromkeys(map(ord, punct_marks), ' ')) 
            words = txt.lower().strip().split()
            words = [w.strip('-') for w in words]
            
            for w in words:
                if len(w) <=1:
                    continue
                elif w[1]=='-':
                    w = w[2:]

                if w in self.name_prefixes:
                    continue
                elif w in (self.last_names + self.first_names):
                    known_names.append(w)
                    
                elif w in self.common_words:
                    not_names.append(w)
                else:
                    other_words.append(w)
                    
        freq_not_names, cntr = count_freq_words(not_names, n=1)
        freq_known_names, cntr2 = count_freq_words(known_names, n=0)
        freq_other_words, cntr3 = count_freq_words(other_words, n=4)

        # names that can be bothe names and regular words
        questionable_names = []
        for wrd in freq_known_names:
            if wrd.lower() in self.common_words:
                questionable_names.append(wrd.lower())
        
        # list of names that appear too often on the page
        too_often_names = []
        for wfreq in cntr2.most_common():
            if (len(known_names)>100 and wfreq[1]>0.05*len(known_names)) or (len(known_names)<=100 and wfreq[1]>=5):
                too_often_names.append(wfreq[0])
                freq_known_names = list(filter(lambda x: x != wfreq[0], freq_known_names))

        finalnames = []
        questionable_names_list = []

        for it in self.visible_texts:
            if contains(it, freq_not_names + too_often_names + freq_other_words + self.stopwords):
                continue
            if contains(it, questionable_names):
                questionable_names_list.append(filter_names(it))
                continue
            nm = filter_names(it)
            
            if nm!='':
                finalnames.append(nm)

        self.names = list(set(finalnames))
        self.possible_names = list(set(questionable_names_list))
        self.names_all = self.names + self.possible_names
        return self.names_all
    
    def assign_first_last_names(self):
        """Go through the list of possible names and assign first and last name for every name"""
        self.first_last_names = nameparts(self.names_all, self.first_names, self.last_names, prefixes=self.name_prefixes)
        return self.first_last_names
    
    def __load_names_data(self):
        """Loads names data such as popular first and last names, stop words and frequent english words"""

        # possible name prefixes 
        self.name_prefixes = ['dr', 'prof', 'jr', 'ph.d', 'ph.d.', 'phd', 'de', 'von', 'm.d', 'md', 'sir', 'mr', 'ms', 'mrs']

        # load list of most common words (some of them can be last names as wellm like bill, will, brown, etc. )
        # list obtained from https://www.wordfrequency.info/
        with open('names_data/most_common_words.txt') as f:
            most_common_words = f.readlines()
        self.common_words = [nm.strip().lower() for nm in most_common_words if len(nm.strip())>1 ]

        # load list of common first names, obtained from nltk names corpus
        with open('names_data/first_names_list.txt') as f:
            self.first_names = f.readlines()
        self.first_names = [nm.strip().lower() for nm in self.first_names if len(nm.strip())>1 ]
        
        # load list of common last names, obtained from https://names.mongabay.com/ 
        with open('names_data/last_names_list.txt') as f:
            self.last_names = f.readlines()
        self.last_names = [nm.strip().lower() for nm in self.last_names if len(nm.strip())>1 ]

        # load list of english stop words, obtained from nltk corpus stopwords
        with open('names_data/stop_words.txt') as f:
            self.stopwords = f.readlines()
        self.stopwords = [nm.strip().lower() for nm in self.stopwords if len(nm.strip())>1 ]
        # keep only stopwords with more than one letter
        self.stopwords = [sw for sw in self.stopwords if len(sw)>1]

        # filter first and last names from possible stopwords presented in there

        sw_innames = []
        for sw in self.stopwords:
            if sw in self.first_names:
                sw_innames.append(sw)
            elif sw in self.last_names:
                sw_innames.append(sw)
        for sw in sw_innames:
            self.first_names = list(filter(lambda x: x != sw, self.first_names))
            self.last_names = list(filter(lambda x: x != sw, self.last_names))
            
        #self.common_words = [x for x in self.common_words if x.lower() not in self.last_names+self.first_names]
        
    def get_alltext(self, soup=None, tables = False):
        """Obtain all visible text from the BeautifulSoup object soup"""
        soup = self.soup or soup
        
        # texts = soup.findAll(text=True)
        # visible_texts = filter(tag_visible, texts)
        # visible_texts = [t.strip() for t in visible_texts]
        # visible_texts = [t for t in visible_texts if t!='']
        visible_texts = []
        visible_texts.extend(self.process_a_tags())
        visible_texts.extend(self.process_h_tags())
        visible_texts.extend(self.process_img_tags())
        
        if tables:
            visible_texts.extend(self.process_tr_tags())
            visible_texts.extend(self.process_tables_rows( self.last_names + self.first_names, self.common_words ))

        return visible_texts
        
    def process_a_tags(self):
        cur_text = []
        for gg in self.soup.find_all('a'):
            cur_text.append( clean_wspaces(gg.get_text()) )
        return cur_text
    def process_h_tags(self):
        """Find all h1-h6 tags on the page and return text in those tags grouped in a dictionary by tag name"""

        #generate array of htags from h1 to h6
        all_h_tags = ['h%d'%(i+1) for i in range(6)]

        #dictionary to store results {'htag':[list of strings from htag tags]}
        rslt_dict = {}
        for tag in all_h_tags:
            cur_text = []
            #find all tag tags on  the page
            for gg in self.soup.find_all(tag):
                cur_text.append( clean_wspaces(gg.get_text()) )
            rslt_dict[tag] = cur_text

        rslt_list = [y for x in rslt_dict.values() for y in x]
        return rslt_list

    def process_tr_tags(self):
        rslt = []
        for table in self.soup.find_all("table"):
            for table_row in table.find_all('tr'):
                cells = table_row.find_all('td')
                if len(cells) > 0:
                    for cell in cells:
                        text = cell.text.replace('\xa0', ' ').strip() 
                        rslt.extend([vals.strip() for vals in text.split('\n') ] )
        return list(set(rslt))

    def process_img_tags(self):
        rslt_dict = {'alt':[], 'title':[]}
        
        for curimg in self.soup.find_all("img"):
            if 'alt' in curimg.attrs:
                rslt_dict['alt'].append(curimg['alt'])
            if 'title' in curimg.attrs:
                rslt_dict['title'].append(curimg['title'])
        rslt_list = [y for x in rslt_dict.values() for y in x]
        return rslt_list

    def process_tables_rows(self, possible_names, not_names ):
        #assume table has same number of columns in each row
        #zero column in the row is okay
        
        table_data = []
        table_names = []
        if len(soup.find_all("table"))==0:
            return []
        
        for table in soup.find_all("table"):
            for table_row in table.find_all('tr'):
                cells = table_row.find_all('td')
                cur_rowtxt = []
                if len(cells) > 0:
                    for cell in cells:
                        text = cell.text.replace('\xa0', ' ').strip() 
                        cur_rowtxt.append(clean_wspaces(text))
                    table_data.append(cur_rowtxt)
                    #print(cur_rowtxt)
                    #print(len(cells), len(cur_rowtxt))
        #print(table_data)
        
        nr = len(table_data)
        if len(table_data)==0:
            return []

        nc = len(table_data[0])
        print(nr, nc)
        colmn_list = []
        for i in  range(nc):
            try:
                cur_col = [table_data[s][i] for s in range(nr)]
            except:
                break
            #pprint(cur_col)

            pa , pb = name_probablity(cur_col, possible_names, not_names ) #nltk_names+last_names, top_not_names + notnames_list
            colmn_list.append([pa,pb, cur_col])
        if len(colmn_list)<=1:
            return []
        colmn_list.sort(key= lambda x: x[0], reverse=True)
        #nm1 = colmn_list[0][2]
        #nm2 = colmn_list[1][2]
        table_names = [' '.join( [ colmn_list[0][2][i], colmn_list[1][2][i] ] ) for i in range(len(colmn_list[0][2]))]

        return table_names


