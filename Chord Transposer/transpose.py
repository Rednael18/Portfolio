from posixpath import split
import sys


# Get the chords which are to be transposed
chords = open(sys.argv[1], encoding="UTF-8")


# Basic chords w/variations
basechords = ["A", "B", "C", "D", "E", "F", "G", "H", "Ab", "Bb", "Cb", "Db", "Eb" "Fb", "Gb", "Hb", "A#", "B#", "C#", "D#", "E#", "F#", "G#", "H#"]
appendixes = ["m", "maj", "+", "dim", "aug", "sus"]
moreappendixes = ["4", "6", "7", "9", "11", "13"]
suses = ["sus2", "sus4", "sus6", "add2", "add4", "add6", "add9", "add11", "-5", "-7", "-9", "-11"]
bases = ["/A", "/B", "/C", "/D", "/E", "/F", "/G", "H", "/A#", "/B#", "/C#", "/D#", "/E#", "/F#", "/G#", "H#", "/Ab", "/Bb", "/Cb", "/Db", "/Eb", "/Fb", "/Gb", "Hb"]

# Following two for-loops create all possible chords from the variations above,
# and add them to a list newchordcheck
chordcheck = []
for chord in basechords:
    chordcheck.append(chord)
    for app in appendixes:
        chordcheck.append(chord + app)
        for app2 in moreappendixes:
            chordcheck.append(chord + app + app2)
            for sus in suses:
                chordcheck.append(chord + app + app2 + sus)
        for sus in suses:
            chordcheck.append(chord + app + sus)
    for app in moreappendixes:
        chordcheck.append(chord + app)
        for sus in suses:
            chordcheck.append(chord + app + sus)
    for sus in suses:
        chordcheck.append(chord + sus)

newchordcheck = []
for chord in chordcheck:
    newchordcheck.append(chord)
    for base in bases:
        newchordcheck.append(chord + base)
        

# Dictionaries for both chord naming conventions
transpose_no = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "H",]
transpose_eng = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B",]

newchords = []
iseng = True


# Retrieve how many semitones the chords are to be transposed
amount = int(sys.argv[2])

# Transpose the chords
for line in chords.readlines():
    line_split = line.split(" ")
    while "" in line_split:
        line_split.remove("")
    line_split = [a.strip() for a in line_split]
    ischordline = True
    total = len(line_split)
    prop = 0
    for element in line_split:
        if element not in newchordcheck:
            ischordline = False
            prop += 1
    if ischordline or prop/total < 0.5:
        # If more than 50% of the line is chords, it is assumed to be a chord line
        # If however, there are non-chord elements in the line, a warning is raised
        # about the parts of the line which are not recognized as chords
        if 0 < prop/total < 0.5:
            print("WARNING: Unknown chord in line: ", f"[{''.join(line)}]")
        passchordchar = False
        for chord in line:
            if passchordchar:
                passchordchar = False
                continue
            if chord == "H":
                iseng = False
            if iseng:
                newchordline = []
                if line.index(chord) + 1 < len(line):
                    if line[line.index(chord) + 1] == "#":
                        chord = chord + "#"
                        passchordchar = True
                if chord in transpose_eng:
                    ind = transpose_eng.index(chord)
                    newchordline.append(transpose_eng[(ind + amount)%len(transpose_eng)])
                else:
                    newchordline.append(chord)
                newchords.append("".join(newchordline))
            else:
                newchordline = []
                if line.index(chord) + 1 < len(line):
                    if line[line.index(chord) + 1] == "#":
                        chord = chord + "#"
                        passchordchar = True
                if chord in transpose_no:
                    ind = transpose_no.index(chord)
                    newchordline.append(transpose_no[(ind + amount)%len(transpose_no)])
                else:
                    newchordline.append(chord)
                newchords.append("".join(newchordline))
    else:
        newchords.append(line)
        

#for line in newchords:
    #line.replace("##", "")

# Write transposed chords to file
f = open("newchords.txt", "w")
f.writelines(newchords)


