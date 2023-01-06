import random
import numpy as np

# Reglene er som i vanlig sjakk, bortsett fra at en passant ikke finnes, og det er ikke sjakk/sjakkmatt - dvs. at
# målet er å ta kongen, ikke å sette sjakkmatt. Dette endrer ikke egentlig spillet, i og med at når noen angriper
# kongen, vil man naturligvis flytte den som om man var i sjakk uansett.

# Styrke på rundt 800 ELO, men dette har jeg kommet frem til ved å la den spille partier mot chess.com sin computer
# på forskjellige ratinger, så mot en menneskelig spiller er den kanskje noe lavere ratet.

# Ved dybde 4, altså da maskinen ser 4 trekk inn i fremtiden, er det en beregningstid på mellom 1-3 minutter.
# Ved dybde 3 er det en beregningstid på mellom 10-30 sekunder. Men naturligvis med svekket dømmekraft.
# Ved dybde 2 og 1 går det fort, men naturlig nok med svært ukompetent spill.
# Kan ikke si noe om beregningstid på dybde over 4, da jeg ikke har latt den holde på lenge nok til å fullføre et trekk
# ved så høy dybde. Betydelig høyere enn 3 minutter.

# Følgende to variabler brukes bare når maskinen spiller mot seg selv
gameended = False
results = [0,0,0]


CHECKMATE = 100000000
DEPTH = 4


# Følgende rabalder må til for å ha rokering
whitekinghasmoved = False
whitekingrookhasmoved = False
whitequeenrookhasmoved = False
whitecastled = False
blackkinghasmoved = True
blackkingrookhasmoved = False
blackqueenrookhasmoved = False
blackcastled = False


# Vekter for det nevrale nettverket om maskinen spiller som hvit. Vektene ble funnet ved å la maskinen spille mot seg selv, og la den tapende part
# endre vektene tilfeldig, for så å spille mot vinneren på nytt - en høyst rudimentær algoritme grunnet i min grunne
# maskinlæringsforståelse på den tiden denne koden ble skrevet, rundt høsten 2020.
w_weights = np.array([
    [ 6,1,7,-3,-9,1],
    [1002, 17, 31, 84, 46, 24],
    [-996,-3,-33,-86,-31,-37],
    [17, 13, 12, 14,5,0],
    [-14,-3,-11,-1,-14,-20],
    [17, 12, 15,3,4,8],
    [-5,-9,-6,-20,-17,8]
])

w_weights2 = np.array([
    [-3,-10, 7,-6,-7,-7],
    [993, 0,46,94,46,31],
    [995, 9,42,96,40,24],
    [ 17, 7,15,16, 5,15],
    [ 18,17,10, 7, 4,18],
    [2, 5,13, 3, 3,18],
    [ 12,12,16, 6,10,16],
])


# Vekter for det nevrale nettverket om maskinen spiller som hvit. Disse kan fint være lik hvits vekter, her har jeg
# bare prøvd å egendefinere dem.

b_weights = np.array([
    [20, -20, 20, -20, -20, 20],
    [1000, 30, 50, 120, 54, 70],
    [-1000, -30, -50, -120, -54, -70],
    [10, 10, 10, 10, 10, 10],
    [-10, -10, -10, -10, -10, -10],
    [10, 10, 10, 10, 10, 10],
    [-10, -10, -10, -10, -10, -10]
])

b_weights2 = np.array([
    [10, 10, 20, 20, 15, 15],
    [1000, 20, 40, 100, 40, 60],
    [1000, 20, 40, 100, 40, 60],
    [10, 10, 10, 10, 10, 10],
    [10, 10, 10, 10, 10, 10],
    [10, 10, 10, 10, 10, 10],
    [10, 10, 10, 10, 10, 10]
])

# To funksjoner som utgjør det nevrale nettverket. Ingen bias.
def inputlayer(input, weights):
    z = np.array(np.zeros(6))
    i = 0
    while i < len(z):
        z[i] = np.dot(input[i], weights[i])

        i += 1
    return z

def outputlayer(input):
    return np.dot(input[0], input[1])


# Funksjon som finner verdien av en gitt posisjon
def findstatevalue(x1, x2, w1, w2):
    node1 = inputlayer(x1, w1)
    node2 = inputlayer(x2, w2)
    res = outputlayer([node1, node2])

    return res


# Funksjoner for computerens trekk som hvit eller svart.

def AImove_white(validmoves):
    global nextMove
    global nextbest
    global nextbestscore
    nextbest = None
    nextMove = None
    nextbestscore = 10000000
    random.shuffle(validmoves)
    actscore = negamax_black(DEPTH, validmoves, -CHECKMATE, CHECKMATE, -1 if gs.whiteturn else 1)

    # Denne kodebiten sier at hvis det nest beste trekket er innenfor så bra som det beste trekket, kan den ta det
    # trekket i stedet. Sjansen for at dette inntreffer er høyere jo tidligere i spillet det er. Dette har jeg for at
    # maskinen ikke bare spiller den samme åpningen hver gang.
    rnd = random.randint(0, 10)
    if len(gs.movelog) < 2:
        mult = 0
        skew = 20000
    elif len(gs.movelog) < 5:
        if actscore < 0:
            mult = 1.3
        else:
            mult = 0.5
        skew = 1000
    else:
        if actscore < 0:
            mult = 1.2
        else:
            mult = 0.8
        skew = 800
    if (nextbestscore >= mult * actscore - skew) and (nextbest != None) and (rnd >= 6):
        nextMove = nextbest
        print("Chose next best move")


    print("")
    gs.makeMove(nextMove)
    gs.commit(nextMove)
    gs.show()

def AImove_black(validmoves):
    global nextMove
    global nextbest
    global nextbestscore
    nextbest = None
    nextMove = None
    nextbestscore = 10000000
    random.shuffle(validmoves)
    actscore = negamax_black(DEPTH, validmoves, -CHECKMATE, CHECKMATE, 1 if gs.whiteturn else -1)

    rnd = random.randint(0, 10)
    if len(gs.movelog) < 2:
        mult = 0
        skew = 20000
    elif len(gs.movelog) < 5:
        if actscore < 0:
            mult = 1.3
        else:
            mult = 0.5
        skew = 1000
    else:
        if actscore < 0:
            mult = 1.2
        else:
            mult = 0.8
        skew = 800
    if (nextbestscore >= mult * actscore - skew) and (nextbest != None) and (rnd >= 6):
        nextMove = nextbest
        print("Chose next best move")
    print("")
    gs.makeMove(nextMove)
    gs.commit(nextMove)
    gs.show()


# Negamax-funksjonene er tatt fra stackoverflow. Tror de bruker alfa-beta-pruning.
def negamax_white(depth, validmoves, alpha, beta, turnmultiplier):
    global nextMove
    if depth == 0:
        return turnmultiplier * findstatevalue(gs.getinput(), gs.getinput(), w_weights, w_weights2)

    maxscore = CHECKMATE
    if len(validmoves) == 0:
        return turnmultiplier * findstatevalue(gs.getinput(), gs.getinput(), w_weights, w_weights2)
    for move in validmoves:
        gs.makeMove(move)
        nextMoves = gs.getPossibleMoves()
        score = -negamax_white(depth - 1, nextMoves, -beta, -alpha, -turnmultiplier)
        if score < maxscore:
            maxscore = score
            if depth == DEPTH:
                nextMove = move
        gs.undoMove()
        if maxscore < alpha:
            alpha = maxscore
        if alpha <= beta:
            break
    return maxscore

def negamax_black(depth, validmoves, alpha, beta, turnmultiplier):
    global nextMove
    global nextbest
    global nextbestscore
    if depth == 0:
        return turnmultiplier * findstatevalue(gs.getinput(), gs.getinput(), b_weights, b_weights2)

    maxscore = -CHECKMATE
    if len(validmoves) == 0:
        return turnmultiplier * findstatevalue(gs.getinput(), gs.getinput(), w_weights, w_weights2)
    for move in validmoves:
        gs.makeMove(move)
        nextMoves = gs.getPossibleMoves()
        score = -negamax_black(depth - 1, nextMoves, -beta, -alpha, -turnmultiplier)
        if score > maxscore:
            if depth == DEPTH:
                if move != nextMove:
                    nextbest = nextMove
                    nextbestscore = maxscore
            maxscore = score
            if depth == DEPTH:
                print(f"Changed to {str(move)} with score {str(score)}")
                nextMove = move
        gs.undoMove()
        if maxscore > alpha:
            alpha = maxscore
        if alpha >= beta:
            break
    return maxscore



class Gamestate():
    def __init__(self):
        # Dersom man har lyst til å begynne fra en gitt posisjon, eller programmet kræsjet midt i spillet og man vil komme raskt tilbake til
        # der man var, kan man manuelt skrive inn utgangsposisjonen her.
        self.board = [
        ["br", "bn", "bb", "bq", "bk", "bb", "bn", "br"],
        ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
        ["  ", "  ", "  ", "  ", "  ", "  ", "  ", "  "],
        ["  ", "  ", "  ", "  ", "  ", "  ", "  ", "  "],
        ["  ", "  ", "  ", "  ", "  ", "  ", "  ", "  "],
        ["  ", "  ", "  ", "  ", "  ", "  ", "  ", "  "],
        ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
        ["wr", "wn", "wb", "wq", "wk", "wb", "wn", "wr"],
    ]
        self.whiteturn = True
        self.movelog = []


    def show(self):
        # Printer brettet i terminalen
        for line in self.board:
            for square in line:
                print(square, end=" ")
            print("")

    def findpiece(self, name):
        # Finner posisjonen til en brikke på brettet
        r = 0
        c = None
        for rank in gs.board:
            if name in rank:
                c = rank.index(name)
                break
            r += 1
        if c == None:
            return 0, 0
        return r, c

    def getinput(self):

        # Denne funksjonen henter inputen som det nevrale nettverket bruker til å bestemme hvor god en posisjon er.


        inp = np.zeros([7, 6])
        wrow, wc = self.findpiece("wk")
        brow, bc = self.findpiece("bk")

        # -------Utvikling---------------------------
        # Straffer computeren for å ikke ha utviklet sine offiserer

        whitedevelop = 0
        for piece in self.board[7]:
            if piece == "wn" or piece == "wb":
                whitedevelop += 3
            if piece == "wq":
                whitedevelop -= 4
        inp[0][4] = whitedevelop

        blackdevelop = 0
        for piece in self.board[0]:
            if piece == "bn" or piece == "bb":
                blackdevelop += 3
            if piece == "bq":
                blackdevelop -= 4
        inp[0][5] = blackdevelop
        #--------Kan rokere--------------------------
        # Computeren ser i utgangspunktet ikke langt nok inn i fremtiden til å skjønne poenget med rokering. Altså
        # er denne linjen her for å oppmuntre den til å rokere.
        if (whitekinghasmoved == False and (whitekingrookhasmoved == False or whitequeenrookhasmoved == False)):
            inp[0][0] = 1
        elif whitecastled:
            inp[0][0] = 3
        else:
            inp[0][0] = 0
        if (blackkinghasmoved == False and (blackkingrookhasmoved == False or blackqueenrookhasmoved == False)):
            inp[0][1] = 1
        elif whitecastled:
            inp[0][1] = 3
        else:
            inp[0][1] = 0

        #--------Antall brikker for hvit----------------
        wk = 0
        wp = 0
        wn = 0
        wq = 0
        wb = 0
        wr = 0
        for rank in gs.board:
            wk += rank.count("wk")
            wp += rank.count("wp")
            wn += rank.count("wn")
            wq += rank.count("wq")
            wb += rank.count("wb")
            wr += rank.count("wr")
        inp[1][0] = wk
        inp[1][1] = wp
        inp[1][2] = wn
        inp[1][3] = wq
        inp[1][4] = wb
        inp[1][5] = wr
        # --------Antall brikker for sort----------------
        bk = 0
        bp = 0
        bn = 0
        bq = 0
        bb = 0
        br = 0
        for rank in gs.board:
            bk += rank.count("bk")
            bp += rank.count("bp")
            bn += rank.count("bn")
            bq += rank.count("bq")
            bb += rank.count("bb")
            br += rank.count("br")
        inp[2][0] = bk
        inp[2][1] = bp
        inp[2][2] = bn
        inp[2][3] = bq
        inp[2][4] = bb
        inp[2][5] = br

        #-----------Kongens sikkerhet-----------------
        # Vanskelig å definere konkret. Er her simpelthen at dersom tårn eller dronning fortsatt er på brettet,
        # er det tryggere i hjørnene.

        if bq > 0 or br > 1:
            dangerwhite = 1
        else:
            dangerwhite = 0
        d8r, d8c = 0, 4
        safespacewhite = abs(2 * (d8r - wrow)) + abs(d8c - wc)
        inp[0][2] = dangerwhite * (safespacewhite)

        if wq > 0 or wr > 1:
            dangerblack = 1
        else:
            dangerblack = 0
        d1r, d1c = 7, 4
        safespaceblack = abs(2 * (d1r - brow)) + abs(d1c - bc)
        inp[0][3] = dangerblack * (safespaceblack)

        #--------------Hvit brettkontroll-------------
        inp[3][0] = gs.getControlledSquares("wk")
        inp[3][1] = gs.getControlledSquares("wp")
        inp[3][2] = gs.getControlledSquares("wn")
        inp[3][3] = gs.getControlledSquares("wq")
        inp[3][4] = gs.getControlledSquares("wb")
        inp[3][5] = gs.getControlledSquares("wr")

        #--------------Sort brettkontroll--------------

        inp[4][0] = gs.getControlledSquares("bk")
        inp[4][1] = gs.getControlledSquares("bp")
        inp[4][2] = gs.getControlledSquares("bn")
        inp[4][3] = gs.getControlledSquares("bq")
        inp[4][4] = gs.getControlledSquares("bb")
        inp[4][5] = gs.getControlledSquares("br")

        #-------Antall brikker hvit angriper/passer-----

        inp[5][0] = gs.getKingAttacks("w")
        inp[5][1] = gs.getPawnAttacks("w")
        inp[5][2] = gs.getKnightAttacks("w")
        inp[5][3] = gs.getQueenAttacks("w")
        inp[5][4] = gs.getBishopAttacks("w")
        inp[5][5] = gs.getRookAttacks("w")

        # -------Antall brikker svart angriper/passer-----

        inp[6][0] = gs.getKingAttacks("b")
        inp[6][1] = gs.getPawnAttacks("b")
        inp[6][2] = gs.getKnightAttacks("b")
        inp[6][3] = gs.getQueenAttacks("b")
        inp[6][4] = gs.getBishopAttacks("b")
        inp[6][5] = gs.getRookAttacks("b")











        return inp

    def makeMove(self, move):
        # Gjør trekket på brettet. Brukes både i beregning av mulige fremtidige posisjoner og til å faktisk ta trekk.

        self.board[move.origrow][move.origcol] = "  "
        if move.attacker == "wp" and move.tarrow == 0:
            self.board[move.tarrow][move.tarcol] = "wq"
        elif move.attacker == "bp" and move.tarrow == 7:
            self.board[move.tarrow][move.tarcol] = "bq"
        else:
            self.board[move.tarrow][move.tarcol] = move.attacker
        self.movelog.append(move)
        self.whiteturn = not self.whiteturn


        if (move.attacker == "wk") and (move.tarrow == 7 and move.tarcol == 6) and (move.origrow == 7 and move.origcol == 4):
            self.board[7][7] = "  "
            self.board[7][5] = "wr"
            whitecastled = True
        if (move.attacker == "wk") and (move.tarrow == 7 and move.tarcol == 2) and (move.origrow == 7 and move.origcol == 4):
            self.board[7][0] = "  "
            self.board[7][3] = "wr"
            whitecastled = True
        if (move.attacker == "bk") and (move.tarrow == 0 and move.tarcol == 6) and (move.origrow == 0 and move.origcol == 4):
            self.board[0][7] = "  "
            self.board[0][5] = "br"
            blackcastled = True
        if (move.attacker == "bk") and (move.tarrow == 0 and move.tarcol == 2) and (move.origrow == 0 and move.origcol == 4):
            self.board[0][0] = "  "
            self.board[0][3] = "br"
            blackcastled = True

    def commit(self, move):
        # Commit er funksjonen som gjør alle permanente endringer, og inntreffer ikke når maskinen gjør beregninger.
        # Hvis denne inndelingen ikke var til stede, ville maskinen trodd for eksempel at den allerede hadde rokert fordi
        # i en av linjene den kalkulerte rokerte den.

        global whitekinghasmoved
        global whitekingrookhasmoved
        global whitequeenrookhasmoved
        global blackkinghasmoved
        global blackkingrookhasmoved
        global blackqueenrookhasmoved

        if move.victim == "wk":
            endgame("b")
        if move.victim == "bk":
            endgame("w")

        if move.attacker == "wk":
            whitekinghasmoved = True
        if move.attacker == "bk":
            blackkinghasmoved = True
        if (move.tarrow == 7 and move.tarcol == 7) or (move.origrow == 7 and move.origcol == 7):
            whitekingrookhasmoved = True
        if (move.tarrow == 7 and move.tarcol == 0) or (move.origrow == 7 and move.origcol == 0):
            whitequeenrookhasmoved = True
        if (move.tarrow == 0 and move.tarcol == 0) or (move.origrow == 0 and move.origcol == 0):
            blackqueenrookhasmoved = True
        if (move.tarrow == 0 and move.tarcol == 7) or (move.origrow == 0 and move.origcol == 7):
            blackkingrookhasmoved = True


        # Denne kodebiten bestemmer om en posisjon har vært på brettet tre ganger på rad. Isåfall avsluttes spillet, med remis.
        if len(gs.movelog) > 20:
            if (str(gs.movelog[-1]) == str(gs.movelog[-5]) and str(gs.movelog[-5]) == str(gs.movelog[-9])) and ((str((gs.movelog[-2]) == str(gs.movelog[-6])) and (str(gs.movelog[-6]) == str(gs.movelog[-10])))):
                endgame("n")
            if len(gs.movelog) > 180:
                endgame("n")

    def undoMove(self):
        # Brukes både i kalkulasjoner, for å resette brettet for å beregne nye mulige linjer, eller av spilleren under et
        # parti, dersom hen vil gå tilbake et trekk.

        if len(self.movelog) != 0:
            move = self.movelog.pop()
            self.board[move.origrow][move.origcol] = move.attacker
            self.board[move.tarrow][move.tarcol] = move.victim
            if (move.attacker == "wk") and (move.tarrow == 7 and move.tarcol == 6) and (move.origrow == 7 and move.origcol == 4):
                self.board[7][5] = "  "
                self.board[7][7] = "wr"
            if (move.attacker == "wk") and (move.tarrow == 7 and move.tarcol == 2) and (move.origrow == 7 and move.origcol == 4):
                self.board[7][3] = "  "
                self.board[7][0] = "wr"
            if (move.attacker == "bk") and (move.tarrow == 0 and move.tarcol == 6) and (move.origrow == 0 and move.origcol == 4):
                self.board[0][5] = "  "
                self.board[0][7] = "br"
            if (move.attacker == "bk") and (move.tarrow == 0 and move.tarcol == 2) and (move.origrow == 0 and move.origcol == 4):
                self.board[0][3] = "  "
                self.board[0][0] = "br"
            self.whiteturn = not self.whiteturn

    def getPossibleMoves(self):

        # Returnerer en liste med alle lovlige trekk.

        moves = []
        wk = 0
        bk = 0
        for rank in self.board:
            wk += rank.count("wk")
            bk += rank.count("bk")

        if (self.whiteturn and wk == 0) or (self.whiteturn == False and bk == 0):
            return moves
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn == "w" and self.whiteturn == True) or (turn == "b" and self.whiteturn == False):
                    piece = self.board[r][c][1]
                    color = self.board[r][c][0]
                    if piece == "p":
                        self.getPawnMoves(r, c, moves, color)
                    elif piece == "k":
                        self.getKingMoves(r, c, moves, color)
                        self.getCastling(r, c, moves, color)
                    elif piece == "q":
                        self.getQueenMoves(r, c, moves, color)
                    elif piece == "r":
                        self.getRookMoves(r, c, moves, color)
                    elif piece == "n":
                        self.getKnightMoves(r, c, moves, color)
                    elif piece == "b":
                        self.getBishopMoves(r, c, moves, color)
        return moves

    def getControlledSquares(self, piece):
        # Finner alle kontrollerte felter på brettet av den gitte brikken; brukes i getinput.

        madeshift = False
        if (piece[0] == "w" and gs.whiteturn == False) or (piece[0] == "b" and gs.whiteturn == True):
            gs.whiteturn = not gs.whiteturn
            madeshift = True

        pm = gs.getPossibleMoves()


        num = 0
        for move in pm:
            if move.attacker == piece:
                num += 1

        if madeshift == True:
            gs.whiteturn = not gs.whiteturn


        return num

    # Alle følgende funksjoner finner simpelthen mulige trekk for den oppgitte brikken, og er tatt fra en
    # tutorial jeg fant på youtube.

    def getPawnMoves(self, r, c, moves, color):
        if self.whiteturn and color == "w":
            if r-1 >= 0:
                if self.board[r-1][c] == "  ":
                    moves.append(Move((r,c), (r - 1,c), self.board))
                    if r == 6 and self.board[r - 2][c] == "  ":
                        moves.append(Move((r, c), (r - 2, c), self.board))
            if c-1 >= 0:
                if self.board[r-1][c-1][0] == "b":
                    moves.append(Move((r, c), (r-1, c-1), self.board))
            if c+1 <= 7:
                if self.board[r-1][c+1][0] == "b":
                    moves.append(Move((r, c), (r-1, c+1), self.board))
        elif(self.whiteturn == False and color == "b"):
            if r + 1 <= 7:
                if self.board[r+1][c] == "  ":
                    moves.append(Move((r,c), (r + 1,c), self.board))
                    if r == 1 and self.board[r + 2][c] == "  ":
                        moves.append(Move((r, c), (r + 2, c), self.board))
            if c-1 >= 0:
                if self.board[r+1][c-1][0] == "w":
                    moves.append(Move((r, c), (r+1, c-1), self.board))
            if c+1 <= 7:
                if self.board[r+1][c+1][0] == "w":
                    moves.append(Move((r, c), (r+1, c+1), self.board))

    def getKingMoves(self, r, c, moves, color):
        kingmoves = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
        allyColor = "w" if color == "w" else "b"
        for i in range(8):
            endRow = r + kingmoves[i][0]
            endCol = c + kingmoves[i][1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    moves.append(Move((r, c), (endRow, endCol), self.board))

    def getQueenMoves(self, r, c, moves, color):
        self.getRookMoves(r,c,moves,color)
        self.getBishopMoves(r,c,moves,color)

    def getRookMoves(self, r, c, moves, color):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemyColor = "b" if color == "w" else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0]*i
                endCol = c + d[1]*i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "  ":
                        moves.append(Move((r,c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:
                        moves.append(Move((r,c), (endRow, endCol), self.board))
                        break
                    else:
                        break
                else:
                    break

    def getKnightMoves(self, r, c, moves, color):
        knightmoves = ((-2,-1),(-2,1),(-1,-2),(-1,2),(1,-2),(1,2),(2,-1),(2,1))
        allyColor = "w" if color == "w" else "b"
        for m in knightmoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    moves.append(Move((r,c), (endRow, endCol), self.board))

    def getBishopMoves(self, r, c, moves, color):
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemyColor = "b" if color == "w" else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "  ":
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:
                        break
                else:
                    break

    def getCastling(self, r, c, moves, color):
        global whitekinghasmoved
        global whitekingrookhasmoved
        global whitequeenrookhasmoved
        global blackkinghasmoved
        global blackkingrookhasmoved
        global blackqueenrookhasmoved

        if(c == 4):
            if (self.whiteturn) and (whitekinghasmoved == False) and (whitekingrookhasmoved == False) and (color == "w") and (self.board[r][c+1] == "  " and self.board[r][c+2] == "  "):
                moves.append(Move((r,c), (r, c+2), self.board))
            elif (self.whiteturn) and (whitekinghasmoved == False) and (whitequeenrookhasmoved == False) and (color == "w") and (self.board[r][c-1] == "  " and self.board[r][c-2] == "  " and self.board[r][c-3] == "  "):
                moves.append(Move((r,c), (r, c-2), self.board))
            elif (self.whiteturn == False) and (blackkinghasmoved == False) and (blackkingrookhasmoved == False) and (color == "b") and (self.board[r][c+1] == "  " and self.board[r][c+2] == "  "):
                moves.append(Move((r,c), (r, c+2), self.board))
            elif (self.whiteturn == False) and (blackkinghasmoved == False) and (blackqueenrookhasmoved == False) and (color == "b") and (self.board[r][c-1] == "  " and self.board[r][c-2] == "  " and self.board[r][c-3] == "  "):
                moves.append(Move((r,c), (r, c-2), self.board))

    # Samme som funksjonene over, bare at de returnerer hvor mange brikker de sikter på.

    def getPawnAttacks(self, color):
        totalattacks = 0


        for row in gs.board:
            for column in row:
                if column[0] == color and column[1] == "p":
                    r = gs.board.index(row)
                    c = row.index(column)
                    if color == "w":
                        if c - 1 >= 0 and r - 1 >= 0:
                            if self.board[r - 1][c - 1][0] != "  ":
                                totalattacks += 1
                        if c + 1 <= 7 and r - 1 >= 0:
                            if self.board[r - 1][c + 1][0] != "  ":
                                totalattacks += 1
                    elif color == "b":

                        if c - 1 >= 0 and r + 1 <= 7:
                            if self.board[r + 1][c - 1][0] != "  ":
                                totalattacks += 1
                        if c + 1 <= 7 and r + 1 <= 7:
                            if self.board[r + 1][c + 1][0] != "  ":
                                totalattacks += 1


        return totalattacks

    def getKingAttacks(self, color):
        totalattacks = 0

        for row in gs.board:
            for column in row:
                if column[0] == color and column[1] == "k":
                    r = gs.board.index(row)
                    c = row.index(column)
                    kingmoves = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, -11))
                    for i in range(8):
                        endRow = r + kingmoves[i][0]
                        endCol = c + kingmoves[i][1]
                        if 0 <= endRow < 8 and 0 <= endCol < 8:
                            endPiece = self.board[endRow][endCol]
                            if endPiece[0] != "  ":
                                totalattacks += 1
        return totalattacks

    def getQueenAttacks(self, color):
        at1 = self.getRookAttacks(color, piece="q")
        at2 = self.getBishopAttacks(color, piece="q")

        return int(at1 + at2)

    def getRookAttacks(self, color, piece="r"):
        totalattacks = 0

        for row in gs.board:
            for column in row:
                if column[0] == color and column[1] == piece:
                    r = gs.board.index(row)
                    c = row.index(column)
                    directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
                    for d in directions:
                        for i in range(1, 8):
                            endRow = r + d[0] * i
                            endCol = c + d[1] * i
                            if 0 <= endRow < 8 and 0 <= endCol < 8:
                                endPiece = self.board[endRow][endCol]
                                if endPiece == "  ":
                                    continue
                                elif endPiece[0] != "  ":
                                    totalattacks += 1
                                    break
                                else:
                                    break
                            else:
                                break

        return totalattacks

    def getKnightAttacks(self, color):
        totalattacks = 0

        for row in gs.board:
            for column in row:
                if column[0] == color and column[1] == "n":
                    r = gs.board.index(row)
                    c = row.index(column)
                    knightmoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
                    for m in knightmoves:
                        endRow = r + m[0]
                        endCol = c + m[1]
                        if 0 <= endRow < 8 and 0 <= endCol < 8:
                            endPiece = self.board[endRow][endCol]
                            if endPiece[0] != "  ":
                                totalattacks += 1

        return totalattacks

    def getBishopAttacks(self, color, piece="b"):
        totalattacks = 0

        for row in gs.board:
            for column in row:
                if column[0] == color and column[1] == piece:
                    r = gs.board.index(row)
                    c = row.index(column)
                    directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
                    for d in directions:
                        for i in range(1, 8):
                            endRow = r + d[0] * i
                            endCol = c + d[1] * i
                            if 0 <= endRow < 8 and 0 <= endCol < 8:
                                endPiece = self.board[endRow][endCol]
                                if endPiece == "  ":
                                    continue
                                elif endPiece[0] != "  ":
                                    totalattacks += 1
                                    break
                                else:
                                    break
                            else:
                                break

        return totalattacks


# Brukes for å konvertere fra leselige koordinater til maskinvennlige koordinater.
ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
               "5": 3, "6": 2, "7": 1, "8": 0}
filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
               "e": 4, "f": 5, "g": 6, "h": 7}


# Move er klassen som utgjør trekk på brettet.
class Move():

    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                   "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                   "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, origin, target, board):
        self.origrow = origin[0]
        self.origcol = origin[1]
        self.tarrow = target[0]
        self.tarcol = target[1]
        self.attacker = board[self.origrow][self.origcol]
        self.victim = board[self.tarrow][self.tarcol]
        self.moveID = self.origrow * 1000 + self.origcol * 100 + self.tarrow * 10 + self.tarcol

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def __str__(self):
        return str(self.getChessNotation())

    def getChessNotation(self):
        return self.getRankFile(self.origrow, self.origcol), self.getRankFile(self.tarrow, self.tarcol)

    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]


# Når en spiller har vunnet, eller det er remis, spiller denne funksjonen av.
def endgame(color):
    if color == "b":
        print("Black Won")
        print("")
        print("White weights:")
        print(w_weights, w_weights2, end="\n")
        print("Black weights:")
        print(b_weights, b_weights2, end="\n")
        results[2] += 1
    elif color == "w":
        print("White won")
        print("")
        print("White weights:")
        print(w_weights, w_weights2, end="\n")
        print("Black weights:")
        print(b_weights, b_weights2, end="\n")
        results[1] += 1
    elif color == "n":
        print("Draw")
        print("")
        print("White weights:")
        print(w_weights, w_weights2, end="\n")
        print("Black weights:")
        print(b_weights, b_weights2, end="\n")
        results[0] += 1
    global gameended
    gameended = True
    global winner
    winner = color


# Denne funksjonen er bare relevant om man trener opp det nevrale nettverket; den klargjør brettet for en ny runde med
# spilling mot seg selv. Justerer også vektene alt etter hvem som vinner.
def reset(color):
    global w_weights
    global w_weights2
    global b_weights
    global b_weights2
    global gameended
    gameended = False
    gs.board = [
        ["br", "bn", "bb", "bq", "bk", "bb", "bn", "br"],
        ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
        ["  ", "  ", "  ", "  ", "  ", "  ", "  ", "  "],
        ["  ", "  ", "  ", "  ", "  ", "  ", "  ", "  "],
        ["  ", "  ", "  ", "  ", "  ", "  ", "  ", "  "],
        ["  ", "  ", "  ", "  ", "  ", "  ", "  ", "  "],
        ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
        ["wr", "wn", "wb", "wq", "wk", "wb", "wn", "wr"],
    ]
    gs.whiteturn = True
    gs.movelog = []

    smallchange = [
        np.array(np.random.randint(-10, 10, 6)),
        np.array(np.random.randint(-10, 10, 6)),
        np.array(np.random.randint(-10, 10, 6)),
        np.array(np.random.randint(-10, 10, 6)),
        np.array(np.random.randint(-10, 10, 6)),
        np.array(np.random.randint(-10, 10, 6)),
        np.array(np.random.randint(-10, 10, 6))
    ]
    smallchange = np.array(smallchange)

    smallchange2 = [
        np.array(np.random.randint(-10, 10, 6)),
        np.array(np.random.randint(-10, 10, 6)),
        np.array(np.random.randint(-10, 10, 6)),
        np.array(np.random.randint(-10, 10, 6)),
        np.array(np.random.randint(-10, 10, 6)),
        np.array(np.random.randint(-10, 10, 6)),
        np.array(np.random.randint(-10, 10, 6))

    ]
    smallchange2 = np.array(smallchange2)




    if color == "b":
        w_weights, w_weights2 = b_weights, b_weights2
        variation = np.random.randint(0,10)
        if variation < 7:
            b_weights, b_weights2 = b_weights + smallchange, b_weights2 + smallchange2
        else:
            b_weights = np.array([
                np.array(np.random.randint(-50, 50, 6)),
                np.array(np.random.randint(-50, 50, 6)),
                np.array(np.random.randint(-50, 50, 6)),
                np.array(np.random.randint(-50, 50, 6)),
                np.array(np.random.randint(-50, 50, 6)),
                np.array(np.random.randint(-50, 50, 6)),
                np.array(np.random.randint(-50, 50, 6))
            ])

            b_weights2 = np.array([
                np.array(np.random.randint(-50, 50, 6)),
                np.array(np.random.randint(-50, 50, 6)),
                np.array(np.random.randint(-50, 50, 6)),
                np.array(np.random.randint(-50, 50, 6)),
                np.array(np.random.randint(-50, 50, 6)),
                np.array(np.random.randint(-50, 50, 6)),
                np.array(np.random.randint(-50, 50, 6))
            ])


    elif color == "w":
        w_weights, w_weights2 = w_weights, w_weights2
        variation = np.random.randint(0, 10)
        if variation < 7:
            b_weights, b_weights2 = w_weights + smallchange, w_weights2 + smallchange2
        else:
            b_weights = np.array([
                np.array(np.random.randint(-50, 50, 6)),
                np.array(np.random.randint(-50, 50, 6)),
                np.array(np.random.randint(-50, 50, 6)),
                np.array(np.random.randint(-50, 50, 6)),
                np.array(np.random.randint(-50, 50, 6)),
                np.array(np.random.randint(-50, 50, 6)),
                np.array(np.random.randint(-50, 50, 6))
            ])

            b_weights2 = np.array([
                np.array(np.random.randint(-50, 50, 6)),
                np.array(np.random.randint(-50, 50, 6)),
                np.array(np.random.randint(-50, 50, 6)),
                np.array(np.random.randint(-50, 50, 6)),
                np.array(np.random.randint(-50, 50, 6)),
                np.array(np.random.randint(-50, 50, 6)),
                np.array(np.random.randint(-50, 50, 6))
            ])


    elif color == "n":
        w_weights, w_weights2 = w_weights + smallchange, w_weights2 + smallchange2
        variation = np.random.randint(0, 10)
        if variation < 2:
            b_weights, b_weights2= w_weights + smallchange, w_weights2 + smallchange2
        else:

            b_weights = np.array([
                np.array(np.random.randint(-50, 50, 6)),
                np.array(np.random.randint(-50, 50, 6)),
                np.array(np.random.randint(-50, 50, 6)),
                np.array(np.random.randint(-50, 50, 6)),
                np.array(np.random.randint(-50, 50, 6)),
                np.array(np.random.randint(-50, 50, 6)),
                np.array(np.random.randint(-50, 50, 6))

            ])

            b_weights2 = np.array([
                np.array(np.random.randint(-50, 50, 6)),
                np.array(np.random.randint(-50, 50, 6)),
                np.array(np.random.randint(-50, 50, 6)),
                np.array(np.random.randint(-50, 50, 6)),
                np.array(np.random.randint(-50, 50, 6)),
                np.array(np.random.randint(-50, 50, 6)),
                np.array(np.random.randint(-50, 50, 6))

            ])

def getRowCol(move):
    if (len(move) == 4):
        try:
            return [
                [ranksToRows[move[1]], filesToCols[move[0]]],
                [ranksToRows[move[3]], filesToCols[move[2]]]
            ]
        except:
            print("Not convertible to move")
            return None
    else:
        print("A move has exactly 4 characters")
        return None










# Selve UI-en
inp = ""
gs = Gamestate()

who = input("I play as (w/b): ")


if who == "w":
    while inp != "quit":
        madevalidmove = False
        print("")
        inp = input("Make a move: ")
        # Skriv undo for å ta tilbake det siste trekket. Skriv moves for å se alle mulige lovlige trekk. Skriv input for å se
        # input fra nåværende posisjon.
        if inp != "undo":
            if inp == "moves":
                for move in gs.getPossibleMoves():
                    print(move)
                continue
            if inp == "input":
                print(gs.getinput())
                continue
            m = getRowCol(inp)

            # Alle trekk må oppgis på koordinatform, som i "e2e4" eller "g1f3".
            if m is not None:
                print("")
                newmove = Move(m[0], m[1], gs.board)
                print(str(newmove))
                possmoves = gs.getPossibleMoves()
                for i in range(len(possmoves)):
                    if newmove == possmoves[i]:
                        gs.makeMove(newmove)
                        gs.show()
                        madevalidmove = True
                if madevalidmove == True:
                    print("")
                    print("")
                    AImove_black(gs.getPossibleMoves())
                    print("")
                else:
                    print("Not a legal move")




        else:
            gs.undoMove()
            print("")
            gs.show()

else:
    print("")
    print("")
    AImove_white(gs.getPossibleMoves())
    print("")
    print("")
    while inp != "quit":
        hasmadevalidmove = False
        inp = input("Make a move: ")
        if inp != "undo":
            if inp == "moves":
                for move in gs.getPossibleMoves():
                    print(move)
                continue
            if inp == "input":
                print(gs.getinput())
                continue
            m = getRowCol(inp)
            if m is not None:
                print("")
                newmove = Move(m[0], m[1], gs.board)
                print(str(newmove))
                possmoves = gs.getPossibleMoves()
                for i in range(len(possmoves)):
                    if newmove == possmoves[i]:
                        gs.makeMove(newmove)
                        gs.show()
                        madevalidmove = True
                if madevalidmove == True:
                    print("")
                    print("")
                    AImove_black(gs.getPossibleMoves())
                    print("")
                else:
                    print("Not a legal move")




        else:
            gs.undoMove()
            print("")
            gs.show()


# Når spillet avsluttes, får man hele spilleloggen.

for log in gs.movelog:
    print(log)