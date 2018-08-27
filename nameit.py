import nltk
from nltk.corpus import names as nltknames
from nltk.corpus import stopwords

from collections import Counter
import re
import bs4

nonnamessmbls = r':;~!#$%^&*=<>?/\|.,'
nmbrs = '1234567890'



def count_freq_words(alltxt, n = 4):
    if type(alltxt)==list:
        words = alltxt
    else:
        words = [x.strip().strip(nonnamessmbls) for nm in alltxt.split() for x in nm.translate({ord(c): None for c in nmbrs + nonnamessmbls + '-'}).split()]
        words = [w for w in words if len(w)>1]
        

    cnt = Counter(words)
    nwords = len(words)
    #print(nwords)
    #print(cnt.most_common(10))
    notnames_list = []
    mostcommon_cntr = cnt.most_common()
    for cnted_word in mostcommon_cntr:
        wrd, noccur = cnted_word
        if noccur>n:
            notnames_list.append(wrd)
        
        #if noccur/nrows
    return notnames_list, cnt

def filter_names(names, filter_list = []):
    #clean up this part 
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
    
    names = [nm.strip(nonnamessmbls) for nm in names]
    names = [nm.strip(nonnamessmbls+'-') for nm in names if len(nm) > 1]

    names = [nm for nm in names if not(bool(re.search(r'[\d]', nm))) or bool(re.search(r'[\W]', nm.replace('-', ''))) ]
    names = [nm for nm in names if nm.lower() not in filter_list]
    
    names = [nm for nm in names if ((not nm.islower() and not nm.isupper()) or len(nm) == 1)]
    names = [nm if not (nm.endswith("’s") or nm.endswith("'s"))else nm[:-2] for nm in names]

    # todo: here count only words that not included in name_prefixes
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
    e.g. removes leading and triling spaces, and extra spaces between words 
    leaving only one space between words
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

class Nameit():
    """A class for extracting names from an arbitray html pages """
    
    def __init__(self, soup):
        """Initialize object with soup  - object of the Beutifulsoup class containing html page"""
        self.soup = soup
        self.__load_names_data()


        #get all text from the visible fields
        self.visible_texts = self.get_alltext()
        #keep only text that does not contains known names
        self.not_names = [txt for txt in self.visible_texts if not(contains(txt, self.last_names + self.first_names))]
        
        self._n_limit = 3 # minimum number of word occurance to assume that this is not a name, provided that this word was not found in the list of last and first names
        #make a list of most popular words
        self.freq_not_names, cntr = count_freq_words(' '.join(self.not_names), n=self._n_limit)
        self.freq_not_names = [nm for nm in self.freq_not_names if nm.lower not in self.name_prefixes and len(nm.strip())>1]
        
    def update_names(self):
        possible_names = []
        possible_names.extend(self.process_a_tags())
        possible_names.extend(self.process_h_tags())
        possible_names.extend(self.process_img_tags())
        
        self.texts_from_tags = possible_names

        #first iterate over the possible_names and find names that are present in self.last_names and self.first_names
        #all names from self.first_names+ self.last_names except those that are frquent on the page

        # 1. possible names from the tags 2. frequent words in the text 3. list of names and lastnames 4. list of common words

        all_names = [x for x in  self.first_names+ self.last_names if x not in self.freq_not_names]
        self.name_list = [nm for nm in possible_names if contains(nm, all_names)]
        possible_names = [it for it in  possible_names if it not in self.name_list]
        possible_names = [it for it in possible_names if not(contains(it, self.freq_not_names + self.common_words)) ]
        
        self.name_list = self.name_list + possible_names

        #self.possible_names = [x for x in self.possible_names if len(x.split())>1 ]
        self.name_list = list(set([it for it in [filter_names(x) for x in self.name_list] if it!='']))

        return self.name_list
    def first_last_names(self):
        """Go through the list of possible names and assign first and last name for every name"""
        return True
    @property
    def n_limit(self):
        return self._n_limit
    
    @n_limit.setter
    def n_limit(self, value):
        if value==self._n_limit:
            return True
        
        self._n_limit = value
        #update list of most common not words based on a new limit 
        self.freq_not_names, cntr = count_freq_words(' '.join(self.not_names), n=self._n_limit)
        #update final results as well

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
        
    def get_alltext(self, soup=None):
        """Obtain all visible text from the BeautifulSoup object soup"""
        # soup = self.soup or soup
        # texts = soup.findAll(text=True)
        # visible_texts = filter(tag_visible, texts)
        # visible_texts = [t.strip() for t in visible_texts]
        # visible_texts = [t for t in visible_texts if t!='']
        possible_names = []
        possible_names.extend(self.process_a_tags())
        possible_names.extend(self.process_h_tags())
        possible_names.extend(self.process_img_tags())
        
        return visible_texts

    def clean_page(self):
        """Removes unnecessary symbols form the page """
        
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

    #def process_tr_tags(self):

    def process_img_tags(self):
        rslt_dict = {'alt':[], 'title':[]}
        
        for curimg in self.soup.find_all("img"):
            if 'alt' in curimg.attrs:
                rslt_dict['alt'].append(curimg['alt'])
            if 'title' in curimg.attrs:
                rslt_dict['title'].append(curimg['title'])
        rslt_list = [y for x in rslt_dict.values() for y in x]
        return rslt_list

