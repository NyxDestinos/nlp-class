import sys
import os
import re
import pprint

def process_file(name, f):
    """
    TODO
    This function takes in a filename along with the file object (actually
    a StringIO object at submission time) and
    scans its contents against regex patterns. It returns a list of
    (filename, type, value) tuples where type is either an 'e' or a 'p'
    for e-mail or phone, and value is the formatted phone number or e-mail.
    The canonical formats are:
         (name, 'p', '###-###-#####')
         (name, 'e', 'someone@something')
    If the numbers you submit are formatted differently they will not
    match the gold answers

    NOTE: ***don't change this interface***, as it will be called directly by
    the submit script

    NOTE: You shouldn't need to worry about this, but just so you know, the
    'f' parameter below will be of type StringIO at submission time. So, make
    sure you check the StringIO interface if you do anything really tricky,
    though StringIO should support most everything.
    """
    # You should change most or all of this for the function to work.
    res = []
    for line in f:
        #res.append(('attapol', 'e', 'first@email.stanford.edu'))
        mail_line = re.sub(r'[-]|&[a-zA-Z]*;| [(]followed by\s*\"*|\s*domain[,]\s*name\s*|http://[a-zA-Z.-]+[.][a-zA-Z.-]+|<address>Apache.+</address>', '', line)
        mail_line = re.sub('&#x40;', '@', mail_line)
        mail_line = re.sub(';', '.', mail_line)
        mail_line = re.sub('WHERE| at ', '@', mail_line)
        mail_line = re.sub(r'DOM| dot |\sdt\s', '.', mail_line)
        
        #E1: simple pattern 
        result_temp = re.findall(r'\s*[a-zA-Z.-]+\s*@\s*[a-zA-Z.-]+\s*[.]\s*(?:edu|com|EDU)', mail_line)
        for i in result_temp:
            i = re.sub(r'\s*', '', i)
            res.append((name, 'e', i))

        #E2: (extra case) pattern with <script> obfuscate
        result_temp = re.findall('obfuscate[(].+[)]', mail_line)
        for i in result_temp:
            _all = re.findall('[\'].+[\']', i)
            for j in range(len(_all)):
                _all[j]= re.sub('\'', '', _all[j])
            if len(_all) != 0:
                _all = _all[0].split(',')
                _domain = re.sub('\'', '', re.findall('\'.+[.]edu\'', i)[0])
                _name = [x for x in _all if x != _domain][0]
                _result = _name +'@' + _domain
                res.append((name, 'e', _result))

        #E3 pattern with xxx @ xxxxx edu
        result_temp = re.findall(r'[a-zA-Z]+@[a-zA-Z]+\s+[a-zA-Z]+\s+(?:edu|com|EDU)', mail_line)
        for i in result_temp:
            i = re.sub(r'\s+', '.', i)
            res.append((name, 'e', i))

        #P1: pattern with (field) xxx-xxxx
        result_temp = re.findall(r'[(][0-9]{3}[)]\s*[0-9]{3}-[0-9]{4}', line)
        for i in result_temp:
            i = re.sub('[(]', '', i)
            i = re.sub(r'[)]\s*', '-', i)
            res.append((name, 'p', i))
        
        #P2: pattern with xxx-xxx-xxxx
        result_temp = re.findall(r'\s*[0-9]{3}\s*-\s*[0-9]{3}\s*-\s*[0-9]{4}', line)
        for i in result_temp:
            i = re.sub(r'\s*', '', i)
            res.append((name, 'p', i))

        #P3: pattern with xxx xxx xxxx
        result_temp = re.findall(r'[0-9]{3}\s[0-9]{3}\s[0-9]{4}', line)
        for i in result_temp:
            i = re.sub(r'\s', '-', i)
            res.append((name, 'p', i))

        #P4: pattern with +xx xxx(-)xxx(-)xxxx
        result_temp = re.findall(r'[+][0-9]*\s[0-9]{3}\s[-]*[0-9]{3}\s*[-]*[0-9]{4}', line)
        for i in result_temp:
            i = re.sub(r'[+][0-9]*\s', '', i)
            i = re.sub(r'\s', '-', i)
            res.append((name, 'p', i))

    return res


def process_dir(data_path):
    """
    You should not need to edit this function, nor should you alter
    its interface as it will be called directly by the submit script
    """
    # get candidates
    guess_list = []
    for fname in os.listdir(data_path):
        if fname[0] == '.':
            continue
        path = os.path.join(data_path, fname)
        f = open(path, 'r', encoding='latin-1')
        f_guesses = process_file(fname, f)
        guess_list.extend(f_guesses)
    return guess_list


def get_gold(gold_path):
    """
    You should not need to edit this function.
    Given a path to a tsv file of gold e-mails and phone numbers
    this function returns a list of tuples of the canonical form:
    (filename, type, value)
    """
    # get gold answers
    gold_list = []
    f_gold = open(gold_path, 'r', encoding='utf8')
    for line in f_gold:
        gold_list.append(tuple(line.strip().split('\t')))
    return gold_list


def score(guess_list, gold_list):
    """
    You should not need to edit this function.
    Given a list of guessed contacts and gold contacts, this function
    computes the intersection and set differences, to compute the true
    positives, false positives and false negatives.  Importantly, it
    converts all of the values to lower case before comparing
    """
    guess_list = [
        (fname, _type, value.lower())
        for (fname, _type, value)
        in guess_list
    ]
    gold_list = [
        (fname, _type, value.lower())
        for (fname, _type, value)
        in gold_list
    ]
    guess_set = set(guess_list)
    gold_set = set(gold_list)

    tp = guess_set.intersection(gold_set)
    fp = guess_set - gold_set
    fn = gold_set - guess_set

    pp = pprint.PrettyPrinter()
    # print 'Guesses (%d): ' % len(guess_set)
    # pp.pprint(guess_set)
    # print 'Gold (%d): ' % len(gold_set)
    # pp.pprint(gold_set)
    print('True Positives (%d): ' % len(tp))
    pp.pprint(tp)
    print('False Positives (%d): ' % len(fp))
    pp.pprint(fp)
    print('False Negatives (%d): ' % len(fn))
    pp.pprint(fn)
    print('Summary: tp=%d, fp=%d, fn=%d' % (len(tp), len(fp), len(fn)))


def main(data_path, gold_path):
    """
    You should not need to edit this function.
    It takes in the string path to the data directory and the
    gold file
    """
    guess_list = process_dir(data_path)
    gold_list = get_gold(gold_path)
    score(guess_list, gold_list)

"""
commandline interface takes a directory name and gold file.
It then processes each file within that directory and extracts any
matching e-mails or phone numbers and compares them to the gold file
"""
if __name__ == '__main__':
    if (len(sys.argv) != 3):
        print('usage:\tSpamLord.py <data_dir> <gold_file>')
        sys.exit(0)
    main(sys.argv[1], sys.argv[2])
