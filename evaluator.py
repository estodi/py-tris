from lib import *
from params.eval import *

# 盤面自体の評価関数
def EvalMainBoard (mainBoard) -> float:
    # 凸凹具合を見る
    # 前の列との差分をみて，その差分の合計を凸凹具合とする

    # 各列において，上から順に見ていって，一番最初にブロックがある部分のrowIdxを格納する
    topRowIdx = []
    for colIdx in range(BOARD_WIDTH):
        isFound = False
        for rowIdx in range(BOARD_HEIGHT):
            if mainBoard[rowIdx][colIdx] is not MINO.NONE:
                topRowIdx.append(rowIdx)
                isFound = True
                break
        if not isFound:
            topRowIdx.append(BOARD_HEIGHT)
    roughness = 0
    for i in range(len(topRowIdx) - 1):
        roughness += abs(topRowIdx[i] - topRowIdx[i+1])

    # ブロックの下にある空白をカウントする
    blankUnderBlock = 0
    for colIdx in range(BOARD_WIDTH):
        for rowIdx in range(topRowIdx[colIdx], BOARD_HEIGHT):
            if mainBoard[rowIdx][colIdx] is MINO.NONE:
                blankUnderBlock += 1
    
    # 盤面の高さを見る
    height = 0
    for i in range(BOARD_HEIGHT):
        isFound = False
        for j in range(BOARD_WIDTH):
            if mainBoard[BOARD_HEIGHT - 1 - i][j] is not MINO.NONE:
                isFound = True
                break
        if not isFound:
            height = i
            break
    
    
    return roughness * EVAL_ROUGHNESS + blankUnderBlock * EVAL_BLANK_UNDER_BLOCK + height * EVAL_HEIGHT

# Tスピンの判定
def IsTSpin (joinedMainBoard, directedMino:DirectedMino, moveList:List[MOVE]) -> bool:
    """
    T-Spinの判定条件
    ①ミノ固定時にTミノの4隅が3つ以上埋まっていること
    ②最後の動作が回転であること
    """

    # 前提条件：directedMinoがTミノであること
    if directedMino.mino is not MINO.T:
        return False

    # ①の判定
    count = 0
    pos = directedMino.pos
    if pos[0] - 1 < 0 or pos[1] - 1 < 0 or joinedMainBoard[pos[1]-1][pos[0]-1] is not MINO.NONE: # 左上
        count += 1
    if pos[0] - 1 < 0 or pos[1] + 1 >= BOARD_HEIGHT or joinedMainBoard[pos[1]+1][pos[0]-1] is not MINO.NONE: # 左下
        count += 1
    if pos[0] + 1 >= BOARD_WIDTH or pos[1] + 1 >= BOARD_HEIGHT or joinedMainBoard[pos[1]+1][pos[0]+1] is not MINO.NONE: # 右下
        count += 1
    if pos[0] + 1 >= BOARD_WIDTH or pos[1] - 1 < 0 or joinedMainBoard[pos[1]-1][pos[0]+1] is not MINO.NONE: # 右上
        count += 1
    if count <= 2:
        return False

    # ②の判定
    if moveList[-1] is MOVE.DROP:
        if len(moveList) < 2: # DROPしかないので最後が回転ではない
            return False
        if moveList[-2] is not MOVE.L_ROT and moveList[-2] is not MOVE.R_ROT: # L_ROTでもR_ROTでもない場合は最後が回転ではない
            return False
        if MOVE.DOWN not in moveList: # ただのROT→DROPというようなmoveListを除く
            return False
    else:
        Error("Invalid MoveList from IsTSpin.")

    return True

# Tスピン-miniであるかどうかの判定
# Tスピンであることは前提として判定を省略する
def IsTSpinMini (joinedMainBoard, directedMino:DirectedMino, moveList:List[MOVE]) -> bool:
    """
    T-Spin Miniの判定条件
    ①T-Spinの条件を満たしていること
    ②ミノ固定時のTミノの4隅のうち，凸側の1つが空いていること
    ③SRSにおける回転補正の4番目(回転中心移動が(±1, ±2))でないこと
    """

    # ②の判定
    pos = directedMino.pos
    if directedMino.direction is DIRECTION.N:
        if (
            (pos[0] - 1 < 0 or pos[1] - 1 < 0 or joinedMainBoard[pos[1]-1][pos[0]-1] is not MINO.NONE) and # 左上が空いていない
            (pos[0] + 1 >= BOARD_WIDTH or pos[1] - 1 < 0 or joinedMainBoard[pos[1]-1][pos[0]+1] is not MINO.NONE) # 右上が空いていない
        ):
            return False
    elif directedMino.direction is DIRECTION.E:
        if (
            (pos[0] + 1 >= BOARD_WIDTH or pos[1] + 1 >= BOARD_HEIGHT or joinedMainBoard[pos[1]+1][pos[0]+1] is not MINO.NONE) and # 右下が空いていない
            (pos[0] + 1 >= BOARD_WIDTH or pos[1] - 1 < 0 or joinedMainBoard[pos[1]-1][pos[0]+1] is not MINO.NONE) # 右上が空いていない
        ):
            return False
    elif directedMino.direction is DIRECTION.S:
        if (
            (pos[0] + 1 >= BOARD_WIDTH or pos[1] + 1 >= BOARD_HEIGHT or joinedMainBoard[pos[1]+1][pos[0]+1] is not MINO.NONE) and # 右下が空いていない
            (pos[0] - 1 < 0 or pos[1] + 1 >= BOARD_HEIGHT or joinedMainBoard[pos[1]+1][pos[0]-1] is not MINO.NONE) # 左下が空いていない
        ):
            return False
    else:
        if (
            (pos[0] - 1 < 0 or pos[1] - 1 < 0 or joinedMainBoard[pos[1]-1][pos[0]-1] is not MINO.NONE) and # 左上が空いていない
            (pos[0] - 1 < 0 or pos[1] + 1 >= BOARD_HEIGHT or joinedMainBoard[pos[1]+1][pos[0]-1] is not MINO.NONE) # 左下が空いていない
        ):
            return False
    
    # ③の判定
    lastRotate = moveList[-2] # DROPの前の最後の回転を取得
    reversedLastRotate = MOVE.R_ROT if lastRotate is MOVE.L_ROT else MOVE.L_ROT
    # joinedMainBoardからdirectedMinoの部分のブロックを消去
    occupiedPositions = GetOccupiedPositions(directedMino)
    deletedMainBoard = copy.deepcopy(joinedMainBoard)
    for pos in occupiedPositions:
        deletedMainBoard[pos[1]][pos[0]] = MINO.NONE
    # 回転補正が4番目であるならMiniではない
    if GetRotateNum(directedMino, reversedLastRotate, deletedMainBoard) == 4:
        return False
    
    return True

# 経路・ライン数の評価関数
def EvalPath (moveList:List[MOVE], clearedRowCount:int, joinedMainBoard, directedMino:DirectedMino) -> float:
    t_spin = 0
    if IsTSpin(joinedMainBoard, directedMino, moveList):
        if IsTSpinMini(joinedMainBoard, directedMino, moveList):
            if clearedRowCount == 1:
                t_spin = EVAL_T_SPIN_MINI_SINGLE
            elif clearedRowCount == 2:
                t_spin = EVAL_T_SPIN_MINI_DOUBLE
        else:
            if clearedRowCount == 1:
                t_spin = EVAL_T_SPIN_SINGLE
            elif clearedRowCount == 2:
                t_spin = EVAL_T_SPIN_DOUBLE
            elif clearedRowCount == 3:
                t_spin = EVAL_T_SPIN_TRIPLE
    
    return t_spin + EVAL_LINE_CLEAR[clearedRowCount]
