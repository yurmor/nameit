from nltk.corpus import names as nltknames
from nltk.corpus import stopwords
import re
import igraph
from igraph import Graph, EdgeSeq
from collections import Counter

domains = ['http', 'www', '@'] #'edu', 'org', 'net', 'com', 
nmbrs = '1234567890'
nonnamessmbls = ':;~!#$%^&*=<>?/\|.,'

nltk_names = [name.lower() for name in nltknames.words()]

with open('names/top_notnames.txt') as f:
    top_not_names = f.readlines()
top_not_names = [nm.strip().lower() for nm in top_not_names]

last_names = []
with open('names/asian.txt') as f:
    asiannames = f.readlines()
last_names = [nm.strip().lower() for nm in asiannames]

with open('names/white.txt') as f:
    whitenames = f.readlines()
    
last_names.extend([nm.strip().lower() for nm in whitenames])

#---------------------------------------------------------------------------------

# Men 3/4

def filter_names(names, filter_list = []):
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
            return names

    names = namesin
    
    parenthesiswords = re.findall('\(.*?\)',names)
    
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
    
    if len(names)<5 and len(names)>1:
        #print(rsltname)
        rsltname = [nm for nm in names if nm.lower() not in filter_list]
        result = ' '.join([nm for nm in rsltname if not(bool(re.search(r'[\d]', nm))) ])
        #result = ' '.join(names)
    else:
        result = ''

    return result

def dubl_rmv(inputlist, nstr=3):
    """
    Return shortest dublicates from the input list, 
    i.e. if there are element 'Abcd' and 'Abcd efg' in the list, it will return 'Abcd' only
    consider only strings that are more than nstr=3 character
    and strings that contain more than one word 
    
    """
    inputlist = list(set(inputlist))
    removelist = []
    n = len(inputlist)
    for i in range(n):
        for j in range(i,n):
            if i==j:
                continue
            else:
                x = inputlist[i]
                y = inputlist[j]
                if len(x)>nstr and len(x.split())>1:                    
                    if x in y:
                        removelist.append(y)
                    elif y in x:
                        removelist.append(x)
    
    resultlist = [x for x in inputlist if x not in removelist]
    return resultlist



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

def process_images(soup, filter_list = []):
    rslt = []
    
    for curimg in soup.find_all("img"):
        if 'alt' in curimg.attrs:
            rslt.append(curimg['alt'])
        if 'title' in curimg.attrs:
            rslt.append(curimg['title'])
        #rslt.extend([vals.strip() for vals in text.split('\n') if canbename(vals.strip(), filter_list = filter_list) ] )
    return list(set(rslt))

def process_tables(soup, filter_list = []):
    rslt = []
    for table in soup.find_all("table"):
        for table_row in table.find_all('tr'):
            cells = table_row.find_all('td')
            if len(cells) > 0:
                for cell in cells:
                    text = cell.text.replace('\xa0', ' ').strip() 
                    rslt.extend([vals.strip() for vals in text.split('\n') if canbename(vals.strip(), filter_list = filter_list) ] )
    return list(set(rslt))

def process_tables_rows(soup, possible_names, not_names ):
    #assume table has same number of columns in each row
    #zero column in the row is okay
    table_data = []
    table_names = []
    if len(soup.find_all("table"))==0:
        return []
    
    for table in soup.find_all("table"):
        for table_row in table.find_all('tr'):
            #print('-'*50)
            #print(clean_wspaces(table_row.get_text()))
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
    nm1 = colmn_list[0][2]
    nm2 = colmn_list[1][2]
    table_names = [' '.join( [ colmn_list[0][2][i], colmn_list[1][2][i] ] ) for i in range(len(colmn_list[0][2]))]

    return table_names

def name_probablity(namelist, flist_a, flist_b ):
    nnames = 0
    nnotnames = 0
    
    for x in namelist:
        #remove ',.'
        x.replace('.', ' ').replace(',', ' ')
        x = x.strip()
        #split x for words
        #and filter out one letter words
        xwords = x.split()
        xwords = [w for w in xwords if len(x)>1]
        if len(xwords)==0:
            nnotnames+=1
        elif len(xwords)>1:
            nnotnames+=1
        else:
            if xwords[0].lower() in flist_a:
                nnames+=1
            elif xwords[0].lower() in flist_b:
                nnotnames+=1
    return 1.*nnames/len(namelist), 1.*nnotnames/len(namelist)

def nameparts(namelist, first_names, last_names):
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
        
        #print(i, '-------------', initials)
        #print(x)
        xparts = [nm for nm in x.split() if nm.strip() not in initials]
        #print(xparts)
        #if it contains only one element, this is the last name, first initial is the first name
        if len(xparts)==0:
            raise ValueError('Name must contain at least one part ... ' + 'current name = ' + str(x))
            break
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
        
        #combine name again to one string woth
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
    #if one of them == 1
    #if any(p1_fst, p1_lst, p2_fst, p2_lst)!=:
    #if p1_fst==1 and p1_lst!=1:
    #print(p1_fst, p1_lst, p2_fst, p2_lst)
    if (p1_fst + p2_lst)/2 >= (p1_lst + p2_fst)/2: #need a special case when prob are the same
        #then first position is the first name, last position is the last name
        for nm in namelist:
            nmparts = remove_pq(nm).strip().split()
            if len(nmparts)>1:
                rslt_list.append((nm, nmparts[0], nmparts[-1]))
            else:
                rslt_list.append((nm, ' ', nmparts[-1]))
    elif (p1_fst + p2_lst)/2 < (p1_lst + p2_fst)/2:
        for nm in namelist:
            nmparts = remove_pq(nm).strip().split()
            if len(nmparts)>1:
                rslt_list.append((nm, nmparts[-1], nmparts[0]))
            else:
                rslt_list.append((nm, ' ', nmparts[0]))
    return rslt_list
            


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
            if wrd.lower() not in (last_names+nltk_names):
                notnames_list.append(wrd)
        
        #if noccur/nrows
    return notnames_list, cnt

def process_atags(soup):
    txtdict = get_text_dict(soup, 'a', 'href')
    page_refs = list(txtdict.keys())
    tree, graph = tree_grow_graph_links(page_refs)
    graph_with_path = routepath(graph, txtdict)

    #------------------------------------------------
    grlistall = graph_to_groups(graph_with_path)
    grlistall = [x for g in grlistall for x in g.values()]
    
    return clean_name_groups(grlistall)


def process_tables(soup, filter_list = []):
    rslt = []
    for table in soup.find_all("table"):
        for table_row in table.find_all('tr'):
            cells = table_row.find_all('td')
            if len(cells) > 0:
                for cell in cells:
                    text = cell.text.replace('\xa0', ' ').strip() 
                    rslt.extend([vals.strip() for vals in text.split('\n') if canbename(vals.strip(), filter_list = filter_list) ] )
    return list(set(rslt))

def process_htags(soup):
        #for gg in soup.find_all('a'):
    #    gg.replace_with(' ')

    alltags = ['h%d'%(i+1) for i in range(6)]

    rslt_dict = {}
    for tag in alltags:
        cur_text = []
        for gg in soup.find_all(tag):
            cur_text.append( clean_wspaces(gg.get_text()) )
        rslt_dict[tag] = cur_text

    rslt_list = [x for x in rslt_dict.values()]
    return rslt_list

def graph_to_groups(graph_with_path):
    #iterate over the vertives of the graph and find indexes vertices with children
    parent_inds = []
    for v in graph_with_path.vs[:]:
        ind = v.index
        if len(graph_with_path.vs[ind].neighbors())!=1:
            parent_inds.append(ind)


    grlistall = []

    #itereate over vertices with children

    for pind in parent_inds:
        #and collect names of all neighbors
        cur_group = []
        for neighbor in graph_with_path.vs[pind].neighbors():
            cur_group.append(neighbor['name'])
        #get only unique values

        cur_group = list(set(cur_group))


        grlistall.append({graph_with_path.vs[pind]['name']:cur_group})
    return grlistall


def clean_name_groups(name_group_list):
    name_fraction_thr = 0.1
    limit_n = 0

    grlist = []
    schoolauthors = []
    #iterate over groups in name_group_list and for every element check if it canbename()
    #if so, append to grlist list
    for gr in name_group_list:
        try:
            grlist.append([it for it in gr if canbename(it)])
        except:
            print("Something strange happened ... ")

    name_group_list.sort(key=lambda x: len(x) )
    grlist.sort(key=lambda x: len(x) )
    
    
    grlist = [g for g in grlist if len(g)>limit_n]
    name_group_list = [g for g in name_group_list if len(g)>limit_n]
            
    
    for curnames in grlist:
        curnames = clean_wspaces(curnames)            
        namesonly = get_names(curnames, nltk_names+last_names)
        
        names_fraction = float(len(namesonly))/len(curnames)
        if len(curnames)==1:
            if names_fraction==1:
                schoolauthors.extend(curnames)
        else:
            if names_fraction>=name_fraction_thr:
                schoolauthors.extend(curnames)
    return schoolauthors
#-----------------------------------------------------------------------------------
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

def get_names(namelist, allnames, n=0):
    #function returns all the elements of namelist that are present in allnames
    realnameslist = []
    for curname in namelist: 
        nameparts = [x.strip(',.-') for x in curname.split() if len(x.strip(',.-'))>n]
        for nmpart in nameparts:
            if nmpart.lower() in allnames:
                realnameslist.append(curname)
                break
    return realnameslist

#Find all stag tags, get text inside and if there is attribute sattr, append this pair to dictionary
def get_text_dict(soup, stag, sattr):
    name_list_items = soup.find_all(stag)
    txtdict = {}
    for i in range(len(name_list_items)):
        #curtxt = name_list_items[i].get_text()
        possiblename = name_list_items[i].get_text().replace('\n', ' ').replace('\r', '').strip()
        sidval =' no '
        if possiblename=='':
            continue
        #if len(possiblename.split())==1:
        #    continue
        if sattr in name_list_items[i].attrs.keys():
            if type(name_list_items[i][sattr])==str:
                sidval = name_list_items[i][sattr].replace('\n', ' ').replace('\r', '').strip()
            elif type(name_list_items[i][sattr])==list:
                sidval = [x.replace('\n', ' ').replace('\r', '').strip() for x in name_list_items[i][sattr]]
                sidval = sum_str_list(sidval, sep='/')
            else:
                raise ValueError('Type of the name_list_items[i][sattr] is neither str nor list ... ')
                
            if sidval in txtdict.keys():
                #txtdict[sidval].append(possiblename)
                txtdict[sidval+'_1'] = possiblename
            else:
                txtdict[sidval] = possiblename
                #txtdict[sidval] = [possiblename]
        #else:
            #print('This tag does not have href attribute ... ')
            #print(i, '++++')
            #print(name_list_items[i])
            #print(i, sidval, ' --- ',possiblename)
        
    return txtdict

#iterate over all graph vertices
def routepath(graphitem, textd):
    for v in graphitem.vs[:]:    
        ind = v.index
        cur_path = graphitem.get_shortest_paths(v=0, to=ind)[0][1:]
        cur_full_path = ''

        for p in cur_path:
            cur_full_path = cur_full_path + sum_str_list(graphitem.vs[p]['id'], sep='/') + '/'

        cur_full_path = cur_full_path[:-1] #remove last / symbol

        #if current vertice is the last element, e.g. has no children
        # assign to 'name' attribute full path for this element
        if len(graphitem.vs[ind].neighbors())==1:
            try:
                textd[cur_full_path]
                graphitem.vs[ind]['name'] = textd[cur_full_path]
            except:
                print("Error - -----------------------------------------------------")
                print(cur_full_path)
                print(graphitem.get_shortest_paths(v=0, to=ind))
                print(cur_path)

                for p in cur_path:
                    print(graphitem.vs[p]['id'])

        else:
            #print('xx --', cur_full_path)
            graphitem.vs[ind]['name'] = graphitem.vs[ind]['id']
    return graphitem


def canbename(name, explain = False, filter_list = []):
    
    
    for dmn in domains:
        if dmn in name:
            if explain:
                print(name, ' is not name because ', dmn, ' in input string')
            return False
        
    words = name.strip(' ').split()
    words = [x for x in words if x not in nonnamessmbls + nmbrs + '-']
    words = [x for x in words if not(bool(re.search(r'[\d]', x))) ]
    words = [x.strip(nonnamessmbls + nmbrs) for x in words]
    
    filter_list = [fit.lower() for fit in filter_list]
    words = [x for x in words if not x.lower() in filter_list]
    
    #print(words)
    
    if len(words)<=1:
        if explain:
            print(name, ' is not name because len(words) = ', len(words), ' <= 1')
        return False
    
    elif len(words)>=5:
        if explain:
            print(name, 'is not name because len(words) = ', len(words), ' >=5')
        return False
    
    result = True
    
    for w in words:
        w = w.lower()
        if w in stopwords.words('english') and len(w)>1:
            result = False
            if explain:
                print(name, 'is not name because ', w,' present in stopwords')
            break
        if w in nonnamessmbls:
            result = False
            if explain:
                print(name, 'is not name because ', w, ' present in nonnamessmbls ', nonnamessmbls)
            break
        if w in top_not_names:
            result = False
            if explain:
                print(name, 'is not name because ', w, ' present in top_not_names' )
            break
    
    return result
    
#_________---------------------------------------------------------------------------------------------


def lcs(s1, s2):
    """
    Returns largest common substring of two strings s1, s2
    """
    m = [[0] * (1 + len(s2)) for i in range(1 + len(s1))]
    longest, x_longest = 0, 0
    for x in range(1, 1 + len(s1)):
        for y in range(1, 1 + len(s2)):
            if s1[x - 1] == s2[y - 1]:
                m[x][y] = m[x - 1][y - 1] + 1
                if m[x][y] > longest:
                    longest = m[x][y]
                    x_longest = x
            else:
                m[x][y] = 0
    return s1[x_longest - longest: x_longest]

def nsame(lst, s):
    """
    how many of the lst items starts with s
    """
    N = len(s)
    
    if type(s)==str:
        ns=0
        for item in lst:
            if item.startswith(s):
                ns+=1
    elif type(s)==list:
        ns=0
        for item in lst:
            if N>len(item):
                continue
            else:
                if item[:N] == s:
                    ns+=1
    else:
        raise ValueError("Received unsopurted type of the input variable... ")
    return ns

def largestgroup(lst):
    #return largest sublist with the same beginning
    #find the length of the longest string
    nmax = 0
    for s in lst:
        nmax = max(len(s), nmax)
    for i in range(nmax):
        nsame(lst, )

def groupme(inputlist, nb=4):
    #inputlist.sort()
    group = {}

    for it in inputlist:
        #iterate over the input list
        nlast = 0
        last_common = ''
        
        for i in range(nb, len(it) +1): #why 3???
        #for i in range(1, len(it) +1): 
            #how many elements of the input list have the same common beginning it[:i]
            n = nsame(inputlist, it[:i])
            if n >= nlast:
                #new largest common beginning
                last_common = it[:i]
            nlast = max(n, nlast)
            if n==0:
                break

        if last_common in group:
        #if 'id' in group:
            group[last_common].append(it[len(last_common):])
            #group['id'] = last_common #.append(it[len(last_common):])
        else:
            if nlast==1:
                group[last_common] = [False]
            else:
                #print('inputlist = ', inputlist)
                #print('it = ',it)

                group[last_common] = [it[len(last_common):]]
        #print(it, last_common, nlast)
    rslt = []
    for parent_id in group.keys():
        rslt.append({'id':parent_id, 'children':group[parent_id]})
        
    return rslt

def get_child(tree, path):
    cur_node = tree
    if len(path)==1 and path[0]==cur_node['id']:
        return cur_node['children']

    for p in path:
        children = cur_node['children']
        for child in children:
            if p==child['id']:
                cur_node = child
                break
    return cur_node['children']

def set_child(tree, path, value):
    cur_node = tree
    n = len(path)
    if n==1 and path[0]==cur_node['id']:
        cur_node['children']  = value
        return tree.copy()

    for i, p in enumerate(path):
        children = cur_node['children']
        for child in children:
            if p==child['id']:
                cur_node = child
                if i==n-1:
                    child['children']  = value
                break
    return tree.copy()
    
def tree_grow_iterative(tree, nb=4):
    """
    fix the problem with longer required common beginning 
    """
    nodelist = [[tree['id']]]
    jj = 0
    while len(nodelist)>0 and jj<100:
        cur_node = nodelist[-1]
        
        children = get_child(tree, cur_node)

        #print(tree)
        #print(cur_node)
        #return(-1)
        if len(children)>1:
            g = groupme(children, nb=nb)
            
            if len(g)>1:
                tree = set_child(tree, cur_node, g)
                for subg in g:
                    if subg['children'] and subg['id']!='':
                        new_node = list(cur_node)
                        new_node.append(str(subg['id']))
                        nodelist.append(new_node)
            
        jj+=1
        nodelist.remove(cur_node)
        
    return tree

def tree_grow_graph(tree, nb=4):
    gr = Graph()
    gr.add_vertices(1)
    gr.vs[0]['id'] = tree['id']
    
    nodelist = [[tree['id']]]
    jj = 0
    
    parentid = len(gr.vs) - 1
    
    while len(nodelist)>0 and jj<100:
        cur_node = nodelist[-1]
        children = get_child(tree, cur_node)
        #parentid = len(gr.vs) - 1
        parentid = gr.vs.find(id=cur_node[-1]).index
        
        
        #print("cur_node[-1] = ", cur_node[-1])
        #print('cur_node = ', cur_node)
        if len(children)>1:
            g = groupme(children, nb=nb)
                
            if len(g)>1:
                tree = set_child(tree, cur_node, g)
                

                for subg in g:
                    if subg['children'] and subg['id']!='':
                        new_node = list(cur_node)
                        new_node.append(str(subg['id']))
                        nodelist.append(new_node)
                        
                        gr.add_vertices(1)
                        cur_id = len(gr.vs) -1
                        #print('---', subg['id'])
                        gr.add_edges([(parentid, cur_id)])
                        gr.vs[cur_id]['id'] = subg['id']
            else:
                
                
                for child in g[0]['children']:
                    gr.add_vertices(1)
                    cur_id = len(gr.vs) -1
                    
                    gr.add_edges([(parentid, cur_id)])
                    gr.vs[cur_id]['id'] = child
                    #print('+++',g[0], child, parentid)
                
        jj+=1
        nodelist.remove(cur_node)
        
    return tree, gr

#------------------------------------------------------------------------------------------------------

def group_links(inputlist):
    #print('=================================================================')
    #print('---', inputlist)
    #inlist_sqncd = [item.strip('/ ').split('/') for item in inputlist]
    inlist_sqncd = inputlist
    group = {}
    uniq_starts = [item[0] if item is not '' else '/' for item in inlist_sqncd ]
    uniq_starts = list(set(uniq_starts))
    uniq_starts.sort()
    
    for start in uniq_starts:
        group[start] = []
        for it in inlist_sqncd:
            #iterate over the input list
            if len(it)==0:
                continue
            if it[0]==start:
                if len(it)==1:
                    group[start].append('')
                else:
                    group[start].append(it[1:])
        
    rslt = []
    for parent_id in group.keys():
        rslt.append({'id':parent_id, 'children':group[parent_id]})
    return rslt

def tree_grow_graph_links(inl):
    
    #inls = [item.strip('/ ').split('/') for item in inl]
    inls = []
    
    for item in inl:
        inls.append(split2symb(item, '/'))
        
    tree = {'id':'all', 'children': inls}
    
    gr = Graph()
    gr.add_vertices(1)
    gr.vs[0]['id'] = tree['id']
    
    nodelist = [[tree['id']]]
    jj = 0
    
    parentid = len(gr.vs) - 1
    
    node_dict = {'all':(len(gr.vs) - 1)}
    #print(node_dict)
    while len(nodelist)>0 and jj<1000:
        cur_node = nodelist[-1]
        children = get_child(tree, cur_node)
        #parentid = len(gr.vs) - 1
        #parentid = gr.vs.find(id=cur_node[-1]).index
        #print(sum_str_list(cur_node[:-1], sep='/'))
        #if len(cur_node)>1:
        
        parentid = node_dict[sum_str_list(cur_node, sep='/')]
        #print(cur_node)
        #print(sum_str_list(cur_node, sep='/'))
        #print(parentid)
        
        #print('cur_node[-1] = ', cur_node[-1])
        #print('gr.vs.find(id=cur_node[-1]) = ', gr.vs.find(id=cur_node[-1]))
        #print('cur_node = ', cur_node)
        #print(gr.get_shortest_paths(v=0, to=ind)[0])
        if len(children)>1:
            #print('chchch --- ', parentid, children)
            g = group_links(children)
            
            if len(g)>0: #for some works only with 1
                #print('+++++++++++++++++++++')
               
                tree = set_child(tree, cur_node, g)
                

                for subg in g:
                    if subg['children'] and subg['id']!='':
                        new_node = list(cur_node)
                        new_node.append(str(subg['id']))
                        nodelist.append(new_node)
                        
                        gr.add_vertices(1)
                        cur_id = len(gr.vs) -1
                        
                        node_dict[sum_str_list(new_node, sep='/')] = cur_id
                        
                        #print('---', subg['id'])
                        gr.add_edges([(parentid, cur_id)])
                        gr.vs[cur_id]['id'] = subg['id']
                        
                        #print('oo --', new_node,parentid, cur_id, cur_node, subg['id'], subg['children'])
                    #else:
                    #    print('*********', subg)
            else:
                for child in g[0]['children']:
                    gr.add_vertices(1)
                    cur_id = len(gr.vs) -1
                    
                    gr.add_edges([(parentid, cur_id)])
                    gr.vs[cur_id]['id'] = child
                    #print('xx --',parentid, cur_id, cur_node, g[0]['id'],child)
                    #print('+++',g[0], child, parentid)
        else:
            #print('--------', children, cur_node)
            if children!=['']:
                tree = set_child(tree, cur_node, {'id':children[0], 'children':['']})
                gr.add_vertices(1)
                cur_id = len(gr.vs) -1
                gr.add_edges([(parentid, cur_id)])
                gr.vs[cur_id]['id'] = children[0]
                #print('ww ++', parentid, cur_id, cur_node, children[0])
            
                
        jj+=1
        nodelist.remove(cur_node)
    #print(node_dict)
    return tree, gr

# ['all', '..', '_tour-of-san-diego'] 7 106 ['all', '..'] _tour-of-san-diego [['san-diego.html'], ['la-jolla-research.html']] 

def sum_str_list(inlist, sep = ''):
    if len(inlist)==0:
        return inlist
    elif len(inlist)==1:
        if inlist[0].strip(' /')=='':
            return inlist[0]
        else:
            #return '/'+inlist[0]
            return inlist[0]
    elif type(inlist)==str:
        return inlist
    else:
        sn = ''
        for el in inlist:
            if el=='':
                continue
            else:
                sn = sn + sep + el
        return sn[1:]

def split2symb(s, symb):
    if s=='':
        return s
    if 2*symb in s:
        rslt = s.strip(' '+symb).split(symb)
        indc = [i for i,x in enumerate(rslt) if x==''] 
        for i in indc:
            rslt[i-1] = rslt[i-1]+'/'
        while '' in rslt:
            rslt.remove('')
        if s[:2]=='//':
            rslt[0] = '/'+rslt[0]
    else:
        rslt = s.strip(' '+symb).split(symb)
        
    if s[0]=='/':
        rslt[0] = '/'+rslt[0]
    if s[-1]=='/' and len(s)>1:
        rslt[-1] = rslt[-1] + '/'
            
    return rslt


