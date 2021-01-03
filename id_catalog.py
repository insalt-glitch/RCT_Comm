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

def split_lines(lines, seperator, pos=0):
    """ Liest die Sekunden aus der output-Datei aus
    """
    return [x.split(seperator)[pos] for x in lines]

def get_process_diffs(times_list):
    """ Berechnet für jeden Prozess die Differenz der beiden Zeiten
    """
    return [abs(times_list[i]-times_list[i+1]) for i in range(0, len(times_list), 2)]
