from lib.classes import *
from lib.helpers.joinMino import JoinDirectedMinoToBoard

COLOR_CODES = {
    MINO.T : fg(5),
    MINO.O : fg(3),
    MINO.Z : fg(1),
    MINO.I : fg(6),
    MINO.L : fg(136),
    MINO.S : fg(2),
    MINO.J : fg(4),
    MINO.JAMA : fg(15),
    MINO.NONE : fg(0),
}

# 盤面の色の情報をもらって、それを色付けしながら出力
def PrintBoardWithColor(board:Board, reset=False, elapsedTime=None, displayAll=False):
    # 表示する行を制限するかどうかを定める
    if displayAll:
        displayedRange = range(BOARD_HEIGHT)
        resetHeight = BOARD_HEIGHT
    else:
        displayedRange = range(DISPLAYED_BOARD_HEIGHT, BOARD_HEIGHT)
        resetHeight = BOARD_HEIGHT - DISPLAYED_BOARD_HEIGHT
    

    # リセットがTrueであればボードの高さ分戻る
    if reset:
        print("\033[{}A".format(resetHeight), end="", flush=True)
    
    # 盤面の状況を出力
    alreadyDisplayedLineCount = 0
    for i in displayedRange:
        if alreadyDisplayedLineCount < SHAPE_HEIGHT: # HOLDミノを表示させる行
            mino = board.holdMino
            for j in range(SHAPE_WIDTH):
                if SHAPE[mino][alreadyDisplayedLineCount][j] == 1:
                    print("{}■{}".format(COLOR_CODES[mino], attr('reset')), end="", flush=True)
                else:
                    print("{}■{}".format(COLOR_CODES[MINO.NONE], attr('reset')), end="", flush=True)
            print("", attr('reset'), end="", flush=True)
        else:
            print("     ", end="", flush=True)

        row = board.mainBoard[i]
        for j in range(BOARD_WIDTH):
            color = row[j]
            print('{}■{}'.format(COLOR_CODES[color], attr('reset')), end="", flush=True)
        
        if 0 <= alreadyDisplayedLineCount < len(board.followingMinos) * (SHAPE_HEIGHT + 1): # NEXTミノを表示させる行
            if alreadyDisplayedLineCount % (SHAPE_HEIGHT + 1) != SHAPE_HEIGHT: # 空白の行ではない
                mino = board.followingMinos[alreadyDisplayedLineCount // (SHAPE_HEIGHT + 1)]
                print(" ", end="", flush=True)
                for j in range(SHAPE_WIDTH):
                    if SHAPE[mino][alreadyDisplayedLineCount % (SHAPE_HEIGHT + 1)][j] == 1:
                        print("{}■{}".format(COLOR_CODES[mino], attr('reset')), end="", flush=True)
                    else:
                        print("{}■{}".format(COLOR_CODES[MINO.NONE], attr('reset')), end="", flush=True)
                print("", flush=True)
            else: # 空白の行
                print("", flush=True)
        elif elapsedTime is not None and alreadyDisplayedLineCount == BOARD_HEIGHT - 1: # 最後の行に経過時間を掲載する
            print("  elapsed time for one loop: {}(s)".format(round(elapsedTime, 5)), flush=True)
        else:
            print("", flush=True)
        
        alreadyDisplayedLineCount += 1

# directedMinoをboardに反映した状態で出力させる
def PrintBoardWithColorWithDirectedMino(board:Board, directedMino:DirectedMino, reset=False, elapsedTime=None):
    joinedBoard = JoinDirectedMinoToBoard(directedMino, board)
    
    # 出力
    PrintBoardWithColor(joinedBoard, reset, elapsedTime)
