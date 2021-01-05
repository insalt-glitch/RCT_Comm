""" Programm zur Auswertung der output-Dateien von Aufgabe 7.1.3/4
"""

def read_file_lines(file):
    """ Gibt eine Liste mit den Zeilen der Datei aus
    """
    ret = []
    with open(file) as f:
        for line in f:
            ret.append(line)
    return ret

def split_lines(lines, seperator, pos=0, start=0, end=None):
    """Splits the idividual lines and returns the specified part.
    """
    sections = [x.split(seperator)[pos][start:] for x in lines]
    #if we should cut the end
    if end is not None:
        sections = [sec[:end] for sec in sections]
    #return the sections
    return sections

def make_table(file):
    """Create a list of tuples from a the text file.
    """
    #get lines by parsing the file
    lines = read_file_lines(file)
    # get data_ids
    data_ids = split_lines(lines, ',')
    data_ids = [int(x, base=16) for x in data_ids]
    # get the type for each id
    types = split_lines(lines, '|', 1, start=3, end=-1)
    # get the description
    descriptions = split_lines(lines, '|', 2, end=-1)
    return list(zip(data_ids, types, descriptions))
