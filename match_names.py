import re
import csv
import sys
import unicodedata
import numpy as np


# Define file names
in_file  = 'names.csv'
out_file = 'names_matched.csv'

# Name columns
src_col = 'source'
tgt_col = 'target'

# Define CSV format
delim_char = ';'
quote_char = '"' 
encoding   = 'utf8'

# Include matches object or not
include_match = True

# Define replacements
# Note: using lower case
replace = [
    ['\\bb\.?v\.?\\b', ''],
    ['\\bn\.?v\.?\\b', ''],    
    ['\\bv\.?o\.?f\.?\\b', ''],
]

# Punctuation
punctuation = ['.', ';', ':', '!', '?', '/', '\\', ',', '#', '@', '$', '&', ')', '(', '"', '\'', '-']


def clean_names(val):    
    """
    Clean up names. Convert to lower case, perform specified replacements, remove punctuation and accented characters.
    
    Args:
        val:    String containing name to clean
    
    Returns:
        Cleansed name as string
    """
    # Convert to lower case
    val = val.lower()
    
    # Combine initials (max 4)
    val = combine_initials(val)
 
    # Substitutions in source and target
    for repl in replace:
        val = re.sub(repl[0], repl[1], val)
    
    # Clean punctuation
    val = ''.join([c if c not in punctuation else ' ' for c in val])
    
    # Replace accented characters
    val = strip_accents(val)
    
    # Strip trailing white-space
    val = val.strip()
    
    return val


def combine_initials(val):  
    """
    Combines uo to 4 initials in a string, for example, "j. k. rowling" or "j k rowling" becomes "jk rowling".
    
    Args:
        val:    String with initials
        
    Returns:
        String with initials combined
    """
    m = re.search('([a-z](?:\.|\\b))\s?([a-z](?:\.|\\b))\s?([a-z](?:\.|\\b))?\s?([a-z](?:\.|\\b))?', val)
    if m:
        initials = ''.join(i.strip('. ') if i else '' for i in m.groups())
        
        # Replace separate initials in source
        val = val.replace(m.group(0), initials + ' ')
    
    return val
 
 
def strip_accents(val):
    """
    Replaces accented characters from a string with their regular counterparts.
    
    Args:
        val:    String with accented characters
        
    Returns:
        String with accented characters replaced
    """
    # Check for string type
    if not (type(val) == str or type(val) == unicode):
        return val
    
    # Return string without accented characters
    return ''.join(c for c in unicodedata.normalize('NFD', val) if unicodedata.category(c) != 'Mn')

    
def edit_distance(s1, s2):
    """
    Compute edit distance between two strings
    
    Args:
        s1:     String to compare
        s2:     String to compare
    
    Returns:
        Edit distance as integer
    """
    m = len(s1) + 1
    n = len(s2) + 1

    tbl = {}
    for i in range(m): tbl[i, 0] = i
    for j in range(n): tbl[0, j] = j
    for i in range(1, m):
        for j in range(1, n):
            cost = 0 if s1[i - 1] == s2[j-1] else 1
            tbl[i,j] = min(tbl[i, j - 1] + 1, tbl[i - 1, j] + 1, tbl[i - 1, j - 1] + cost)

    return tbl[i, j]

    
def string_comp(src, tgt):
    """
    Calculate similarities between names
    
    Args:
        src:    Source account name to compare
        tgt:    Target account name to compare against
    
    Returns:
        Match score as percentage, dict of tokens and their match scores
    """
    # Check whether both strings are empty or None
    if src in [None, ''] and tgt in [None, '']:
        return (0, [])
    
    # Split into word entities
    src = src.split()
    tgt = tgt.split()
    
    # Match all entities, weigh by length
    mtx = np.zeros((len(src), len(tgt)))
    for i, stoken in enumerate(src):
        for j, ttoken in enumerate(tgt):
            # Compute match score
            dist = edit_distance(stoken, ttoken)
            
            # Compute ratio and store in matrix
            nchars = max(len(stoken), len(ttoken))
            mtx[i, j] = 1 - dist / nchars

    # Find best matching pairs between source and target tokens
    matches = []
    while mtx.shape[0] > 0 and mtx.shape[1] > 0:
        # Find maximum match
        max_score = np.max(mtx)
        st, tt = np.where(mtx == max_score)
       
        # Take first pair on ties
        st = st[0]
        tt = tt[0]
       
        # Add to matches
        matches.append({'source': src[st], 'target': tgt[tt], 'score': max_score})
        
        # Remove matched tokens
        mtx = np.delete(mtx, st, 0)
        src.pop(st)
        
        mtx = np.delete(mtx, tt, 1)
        tgt.pop(tt) 
    
    # Add unmatched tokens with score 0
    matches.extend([{'source': t,  'target': '', 'score': 0.0} for t in src])
    matches.extend([{'source': '', 'target': t,  'score': 0.0} for t in tgt])
    
    # Compute overall match score
    score = 0
    nchars = 0
    for match in matches:
        nchars += len(match['source'])
        score  += match['score'] * len(match['source'])
 
    # Return score as percentage
    if nchars > 0:
        score = int(round((score / nchars) * 100))
    
    return (score, matches)
 
 
def main():
    """
    Main program logic
    """
    # Read CSV
    with open(in_file, 'r', encoding=encoding) as in_fh:
        # Create DictReader
        in_csv = csv.DictReader(in_fh, delimiter=delim_char, quotechar=quote_char)
    
        # Get field names
        fields = in_csv.fieldnames
        fields.append('match_score')
        if include_match:
            fields.append('matches')
        
        # Open output file and create DictWriter
        with open(out_file, 'w', newline='', encoding=encoding) as out_fh:
            out_csv = csv.DictWriter(out_fh, fieldnames=fields, delimiter=delim_char, quotechar=quote_char)
            
            # Write header
            out_csv.writeheader()
            
            # Process rows
            for row in in_csv:
                # Perform cleansing on names
                src = clean_names(row[src_col])
                tgt = clean_names(row[tgt_col])
                
                # Compute matching score
                if include_match:
                    row['match_score'], row['matches'] = string_comp(src, tgt)
                else:
                    row['match_score'], matches = string_comp(src, tgt)
                
                # Write to output file
                out_csv.writerow(row)
            

# Execute main
if __name__ == '__main__':
    main()