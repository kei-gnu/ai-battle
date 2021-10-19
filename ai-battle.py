import copy
import random
import itertools
import time
import numpy as np
from numpy.core.fromnumeric import put
from numpy.lib.function_base import append

start = time.time()

# 地形情報
WALL = 0
GRASS = 1
SAND = 2
ROCK = 3
# 地形による防御力
SAND_ABILITY = 0
GRASS_ABILITY = 5
ROCK_ABILITY = 30

# コマの種類
CASTLE = 0
SOLDIER = 1
ARCHER = 2
KNIGHT = 3

# コマの番号
# PLAYER1
PLAYER1_CASTLE_ID = 0
PLAYER1_SOLDIER1_ID = 1
PLAYER1_SOLDIER2_ID = 2
PLAYER1_SOLDIER3_ID = 3
PLAYER1_SOLDIER4_ID = 4
PLAYER1_ARCHER1_ID = 5
PLAYER1_ARCHER2_ID = 6
PLAYER1_KNIGHT_ID = 7
# PLAYER2
PLAYER2_CASTLE_ID = 8
PLAYER2_SOLDIER1_ID = 9
PLAYER2_SOLDIER2_ID = 10
PLAYER2_SOLDIER3_ID = 11
PLAYER2_SOLDIER4_ID = 12
PLAYER2_ARCHER1_ID = 13
PLAYER2_ARCHER2_ID = 14
PLAYER2_KNIGHT_ID = 15

# PLAYER_ID
PLAYER1 = 1
PLAYER2 = 2

# CASTLE's States
CASTLE_HP = 150
CASTLE_ATTACK = 90
CASTLE_DEFENCE = 30
# 移動力
CASTLE_MOVE = 1

# Knight's States
KNIGHT_HP = 100
KNIGHT_ATTACK = 65
KNIGHT_DEFENCE = 40
# 移動力
KNIGHT_MOVE = 8
KNIGHT_GRASS = 3
KNIGHT_SAND = 1
KNIGHT_ROCK = 4

# SOLDIER's States
SOLDIER_HP = 80
SOLDIER_ATTACK = 50
SOLDIER_DEFENCE = 40
# 移動力
SOLDIER_MOVE = 5
SOLDIER_GRASS = 1
SOLDIER_SAND = 1
SOLDIER_ROCK = 2

# ARCHER's States
ARCHER_HP = 50
ARCHER_ATTACK = 50
ARCHER_DEFENCE = 40
# 移動力
ARCHER_MOVE = 5
ARCHER_GRASS = 2
ARCHER_SAND = 1
ARCHER_ROCK = 4

# コマの生存情報
DEAD = 0
ALIVE = 1

# 移動済みかどうか
NOT_MOVED = 0
MOVED = 1
# 最大移動コスト
MAX_DISTANCE = 99

# HP比較の値
COMPARISON_HP = 1000
# 移動のループ回数
MAX_NUMBER_OF_MOVES = 100
NUMBER_OF_GAMES = 100

# 終了するとき
GAME_FINISHED = 0
GAME_NOT_FINISHED = 1

# PLAYER1_PIECES_WIN = 3
# PLAYER2_PIECES_WIN = 4
# PLAYER1_CASTLE_WIN = 5
# PLAYER2_CASTLE_WIN = 6

PLAYER1_CASTLE_DESTROYER_WIN = 3
PLAYER2_CASTLE_DESTROYER_WIN = 4
PLAYER1_ARMY_DESTROYER_WIN = 5
PLAYER2_ARMY_DESTROYER_WIN = 6

ARMY_DESTROYER_AI = 10
CASTLE_DESTROYER_AI = 11

piece_dict = {PLAYER1_CASTLE_ID:["C", "CASTLE", "Player1 Castle"], PLAYER1_SOLDIER1_ID:["S", "SOLDIER", "Player1 Soldier1"], PLAYER1_SOLDIER2_ID: ["S", "SOLDIER","Player1 Soldier2"], PLAYER1_SOLDIER3_ID:["S", "SOLDIER", "Player1 Soldie3"],
            PLAYER1_SOLDIER4_ID:["S", "SOLDIER", "Player1 Soldier4"], PLAYER1_ARCHER1_ID:["A", "ARCHER", "Player1 Archer1"], PLAYER1_ARCHER2_ID:["A", "ARCHER", "Player1 Archer2"], PLAYER1_KNIGHT_ID:["K", "KNIGHT", "Player1 Knight"],
            PLAYER2_CASTLE_ID:["c", "CASTLE", "Player2 Castle"], PLAYER2_SOLDIER1_ID:["s", "SOLDIER", "Player2 Soldier1"], PLAYER2_SOLDIER2_ID:["s", "SOLDIER", "Player2 Soldier2"], PLAYER2_SOLDIER3_ID:["s", "SOLDIER", "Player2 Soldier3"],
            PLAYER2_SOLDIER4_ID:["s", "SOLDIER", "Player2 Soldier4"], PLAYER2_ARCHER1_ID:["a", "ARCHER", "Player2 Archer1"], PLAYER2_ARCHER2_ID:["a", "ARCHER", "Player2 Archer2"], PLAYER2_KNIGHT_ID:["k", "KNIGHT", "Player2 Knight"]}

move_cost = [[MAX_DISTANCE, MAX_DISTANCE, MAX_DISTANCE, MAX_DISTANCE], [SOLDIER, SOLDIER_GRASS, SOLDIER_SAND, SOLDIER_ROCK], [ARCHER, ARCHER_GRASS, ARCHER_SAND, ARCHER_ROCK], [KNIGHT, KNIGHT_GRASS, KNIGHT_SAND, KNIGHT_ROCK]]
# move_cost = [[SOLDIER, SOLDIER_GRASS, SOLDIER_SAND, SOLDIER_ROCK], [ARCHER, ARCHER_GRASS, ARCHER_SAND, ARCHER_ROCK], [KNIGHT, KNIGHT_GRASS, KNIGHT_SAND, KNIGHT_ROCK]]

# 城、歩兵、アーチャー、ないと

piece_commpatibility = {CASTLE:[0, 0, -15, 0], KNIGHT: [0, 25, -25, 0], SOLDIER: [0, 0, 50, -25], ARCHER: [15, -50, 0, 25]}
terrain_power = {SAND: 0, GRASS: 5, ROCK: 30}

# ピースの情報を保存するClass
class Piece:
    def __init__(self, piece_id, piece_type, starty, startx, now_y, now_x, dead_or_alive, move_finished, hit_point, attack, defence, mov_pow, destinations=None):
        self.piece_id = piece_id    # 各コマを区別するためのID番号
        self.piece_type = piece_type    # 駒の種類 Str型？ → int
        self.startx, self.starty = startx, starty    # マップ上のコマの初期場所
        self.now_x, self.now_y = now_x, now_y     # マップ上の現在の場所
        self.dead_or_alive = dead_or_alive    # コマが生きているか死んでいるかの状態
        self.move_finished = move_finished    # 既にコマが移動済みかどうか
        self.hit_point = hit_point    # コマのHP値
        self.attack = attack    # コマの攻撃力
        self.defence = defence   # コマの防御力
        self.mov_pow = mov_pow    # コマの移動力
        self.destinations = destinations    # コマの移動可能な場所
        
# 最初の位置のピースを迷路に代入
def startyx_piece_map(no_piece_map, piece_info_list):
    for piece in piece_info_list:
        piece_name = piece_dict[piece.piece_id][0]
        # 迷路を更新
        no_piece_map[piece.starty][piece.startx] = piece_name
    return no_piece_map

# MAX_DISTANCEの場所を代入
def max_distance_sub(pinfo, piece):
    # 敵方の駒を迂回させるため、マップ移動最大値を詰め込む
    if piece.piece_id < PLAYER2_CASTLE_ID:
        for enemy_piece in pinfo:
            if (enemy_piece.piece_id >= PLAYER2_CASTLE_ID) and (enemy_piece.dead_or_alive == ALIVE):
                piece.destinations[enemy_piece.now_y][enemy_piece.now_x] = MAX_DISTANCE
    else:
        for enemy_piece in pinfo:
            if (enemy_piece.piece_id < PLAYER2_CASTLE_ID) and (enemy_piece.dead_or_alive == ALIVE):
                piece.destinations[enemy_piece.now_y][enemy_piece.now_x] = MAX_DISTANCE

# MAX_DISTANCEを削除する関数
def remove_max_distance(destinations):
    for row_num, column_num in itertools.product(range(map_row), range(map_col)):
        if destinations[row_num][column_num] == MAX_DISTANCE:
            destinations[row_num][column_num] = 0

# 再帰的な関数
def get_destinations_for_piece(y, x, cur_pow, piece_type, destinations):
    destinations[y][x] = cur_pow
    move = [[-1, 0], [1, 0], [0, 1], [0, -1]]
    # 上下左右展開
    for dis_move in move:
            # map の情報を取得し、if文で確認する
        if (0 <= y+dis_move[0] < len(destinations)) and (0 <= x+dis_move[1] < len(destinations)) and (terrain_map[y+dis_move[0]][x+dis_move[1]] != WALL):
            now_y, now_x = y+dis_move[0], x+dis_move[1]    # 次の迷路の場所
            # mapの地形を判断
            dest_power = cur_pow - move_cost[piece_type][terrain_map[y + dis_move[0]][x + dis_move[1]]]
            if destinations[now_y][now_x] < dest_power:    # 次に移動候補が現在の場所より値が大きいとき
                get_destinations_for_piece(now_y, now_x, dest_power, piece_type, destinations)

# 移動範囲の探索処理
def get_destinations_for_move(pinfo, f=None):
    # 生きているかどうか, 移動済みじゃないかどうか、CASTLEじゃないかどうかを確認
    for piece in pinfo:
        empty_list = [[0] * len(m) for m in terrain_map]   # からのリストを作成

        if (piece.dead_or_alive == ALIVE) and (piece.move_finished == NOT_MOVED) and (piece.piece_type != CASTLE):
            piece.destinations = empty_list    # destinationsのリストを初期化
            # 敵の場所、Castle、壁をMAX_DISTANCEに初期化
            max_distance_sub(pinfo, piece)
            # 再帰的な関数
            get_destinations_for_piece(piece.now_y, piece.now_x, piece.mov_pow, piece.piece_type, piece.destinations)
            # 99(MAX_DISTANCE)を削除する
            remove_max_distance(piece.destinations)
            
            
# moveを更新
def update_not_moved(moved_piece_info, player):
    for moved_piece in moved_piece_info:
        if moved_piece.move_finished == MOVED:
            moved_piece.move_finished = NOT_MOVED

def check_player(player, pinfo, number_of_moves):
    if player == PLAYER1:
        player = PLAYER2
        update_not_moved(pinfo, player)
        return player, number_of_moves
    else:
        player = PLAYER1
        number_of_moves += 1
        update_not_moved(pinfo, player)
        return player, number_of_moves

# MAX_NUMBER_OF_MOVES回ピースが移動する関数
def piece_max_number_of_moves(pinfo, piece_map):
    
    start_player1 = ARMY_DESTROYER_AI
    start_player2 = CASTLE_DESTROYER_AI
    # start_player1 = CASTLE_DESTROYER_AI
    # start_player2 = ARMY_DESTROYER_AI
    start_player1_wins = 0
    start_player2_wins = 0
    draws = 0
    file_write_name = "Game_Map_Output.txt"
    number_of_move = 1
    # game_finished = 0
    game_finished = GAME_NOT_FINISHED
    # ファイル書き出しスタート
    f = open(file_write_name, "w")   # 新規書き込み
    total = 0
    # 移動開始処理スタート
    while total != NUMBER_OF_GAMES:
        turn_player = PLAYER1
        total += 1
        number_of_move = 1
        # game_finished = 0
        game_finished = GAME_NOT_FINISHED
        print(f"toltal:  start_player1:{check_ai[start_player1]}, start_player2{check_ai[start_player2]}", file=f)
        file_print_map(piece_map, f"Starting game number {total}...", f)
        print_map(piece_map, f"Starting game number {total}...")
        # not_name_print_map(piece_map)
        while (number_of_move != MAX_NUMBER_OF_MOVES) and (game_finished == GAME_NOT_FINISHED):
            # print(f"start_player1:{check_ai[start_player1]}, start_player2{check_ai[start_player2]}", file=f)

            get_destinations_for_move(pinfo)
            check_ai_game(turn_player, pinfo, piece_map, start_player1, start_player2, number_of_move, f)
            
            game_finished =  check_game_finished(pinfo)
            # 勝利条件を満たしている場合ループ終了
            # if (game_finished == PLAYER1_ARMY_DESTROYER_WIN) or (game_finished == PLAYER2_ARMY_DESTROYER_WIN) or (game_finished == PLAYER1_CASTLE_DESTROYER_WIN) or (game_finished == PLAYER2_CASTLE_DESTROYER_WIN):
            #     game_finished = GAME_FINISHED
            
            print_map(piece_map, "Current position:")
            file_print_map(piece_map, "Current position:", f)
            print_pinfo(pinfo)  
            file_print_pinfo(pinfo, f)
            print(f"Player{turn_player} move {number_of_move} finished", file=f)
            print(f"Player{turn_player} move {number_of_move} finished")

            if turn_player == PLAYER1:
                turn_player = PLAYER2
                # update_not_moved(pinfo, turn_player)
                for piece in pinfo:
                    if piece.piece_id >= PLAYER2_CASTLE_ID:
                        piece.move_finished = NOT_MOVED
            else:
                turn_player == PLAYER2
                turn_player = PLAYER1
                number_of_move += 1
                # update_not_moved(pinfo)
                for piece in pinfo:
                    if piece.piece_id < PLAYER2_CASTLE_ID:
                        piece.move_finished = NOT_MOVED
            # turn_player, number_of_move = check_player(turn_player, number_of_move)
            
        if number_of_move == MAX_NUMBER_OF_MOVES:
            print("Game ended in a draw.", file=f)
            print("Game ended in a draw.")
            draws += 1
        # print(game_finished)
        if game_finished == PLAYER1_ARMY_DESTROYER_WIN:
            print("Game over: al pieces of player2 are dead", file=f)
            print("Game over: al pieces of player2 are dead")
            print("Army Destroyer AI wins.", file=f)
            # print("Player1 wins.")
            start_player1_wins += 1
        if game_finished == PLAYER2_ARMY_DESTROYER_WIN:
            print("Game over: all pieces of player1 are dead", file=f)
            print("Game over: all pieces of player1 are dead")
            print("Army Destroyer AI wins.", file=f)
            # print("Player2 wins.")
            start_player1_wins += 1
        if game_finished == PLAYER1_CASTLE_DESTROYER_WIN:
            print("Game over: player2 castle destroyed", file=f)
            print("Game over: player2 castle destroyed")
            print("Castle Destroyer AI wins.", file=f)
            # print("Player1 wins.")
            start_player2_wins += 1
        if game_finished == PLAYER2_CASTLE_DESTROYER_WIN:
            print("Game over: player1 castle destroyed", file=f)
            print("Game over: player1 castle destroyed")
            print("Castle Destroyer AI wins.", file=f)
            print("Player2 wins.")
            start_player2_wins += 1
        # ゲームの結果を出力
        print(f"Game number {total} finished", file=f)
        print(f"Game number {total} finished")
        print(f"Current score: Army Destroyer AI - Castle Destroyer AI {start_player1_wins} - {start_player2_wins} (Draws: {draws})", file=f)
        print(f"Current score: Army Destroyer AI - Castle Destroyer AI {start_player1_wins} - {start_player2_wins} (Draws: {draws})")
        # piece_map = backup_start_piece_map
        pinfo = create_pinfo(piece_info_string)
        # not_name_print_map(not_piece_map)
        # print("終わりのpinfoの更新:", file=f)
        # file_print_pinfo(pinfo, f)
        no_piece_map = copy.deepcopy(terrain_map)
        piece_map = startyx_piece_map(no_piece_map, pinfo)
        # file_print_map(piece_map, "更新したpiece_map情報:", f)
        # print(pinfo[PLAYER2_CASTLE_ID].dead_or_alive, file=f)
        number_of_move = 1
        game_finished = GAME_NOT_FINISHED
        
        if start_player1 == ARMY_DESTROYER_AI:
            start_player1 = CASTLE_DESTROYER_AI
            start_player2 = ARMY_DESTROYER_AI
        elif start_player1 == CASTLE_DESTROYER_AI:
            start_player1 = ARMY_DESTROYER_AI
            start_player2 = CASTLE_DESTROYER_AI
        
    f.close()
    # file_read = open(file_write_name)
    # print(file_read.read())
    # file_read.close()
c_player = {PLAYER1: "PLAYER1", PLAYER2:"player2"}
check_ai = {CASTLE_DESTROYER_AI: "CASTLE_DESTROYER_AI", ARMY_DESTROYER_AI: "ARM_DESTROYER_AI"}
shows_alive = {DEAD:"DEAD", ALIVE:"ALIVE"}
shows_move = {MOVED:"動いてしまっている", NOT_MOVED:"まだ動いていない"}
def check_ai_game(player, pinfo, piece_map, ai1, ai2, number, f):
    if(player == PLAYER1) and (ai1 == CASTLE_DESTROYER_AI) or (player == PLAYER2) and (ai2 == CASTLE_DESTROYER_AI):
        # print(f'player{c_player[player]}, 動作AI1: {check_ai[ai1]}, AI2: {check_ai[ai2]}', file=f)
        move_pieces_castle_destroyer(pinfo, player, piece_map, number, f)    # シャッフルしたpieceを取得
    
    if (player == PLAYER1) and (ai1 == ARMY_DESTROYER_AI) or (player == PLAYER2) and (ai2 == ARMY_DESTROYER_AI):
        # print(f'player{c_player[player]}, 動作AI1: {check_ai[ai1]}, AI2: {check_ai[ai2]}', file=f)

        move_pieces_army_destroyer(pinfo, player, piece_map, number, f)

# 終了条件が満たしているかどうかの確認
def check_game_finished(pinfo):
    # 城が倒されたかどうかを確認
    if (pinfo[PLAYER1_CASTLE_ID].dead_or_alive == DEAD):
        # print("Game over: player1 castle destroyed。")
        # result_file.write("Game over: player1 castle destroyed\n")
        return PLAYER2_CASTLE_DESTROYER_WIN
    if pinfo[PLAYER2_CASTLE_ID].dead_or_alive == DEAD:
        # print("Game over: player2 castle destroyed")
        # result_file.write("Game over: player2 castle destroyed\n")
        return PLAYER1_CASTLE_DESTROYER_WIN
    # 各プレイヤーに城以外に生きている駒が残っているかどうかの確認
    for piece in pinfo:
        if piece.piece_id > PLAYER1_CASTLE_ID and piece.piece_id < PLAYER2_CASTLE_ID and piece.dead_or_alive == ALIVE:
            break
    else:
        # print("Game over: all pieces of player1 are dead")
        # result_file.write("Game over: all pieces of player1 are dead\n")
        return PLAYER2_ARMY_DESTROYER_WIN
    for piece in pinfo:
        if piece.piece_id > PLAYER2_CASTLE_ID and piece.dead_or_alive == ALIVE:
            break
    else:
        # print("Game over: all pieces of player2 are dead")
        # result_file.write("Game over: all pieces of player2 are dead\n")
        return PLAYER1_ARMY_DESTROYER_WIN
    return GAME_NOT_FINISHED


# シャッフル
def move_pieces_army_destroyer(pinfo, player_id, piece_map, number, f):
    # f = open("aspiration.txt", "a")
    aspiration_map = create_aspiration_map_army_destroyer(pinfo, player_id, f)
    # file_print_map(best_info, "army_aspiration_map", f)
    # if number == 99:
    #     file_print_map(aspiration_map, "army_aspiration_map:", f)
    for piece in pinfo:
        if piece.dead_or_alive == ALIVE and piece.move_finished == NOT_MOVED and piece.piece_type != CASTLE:
            # if number == 99:
            #     file_print_map(aspiration_map, "army_aspiration_map:", f)
            #     file_print_map(piece.destinations, f"{piece_dict[piece.piece_id][2]}'s army破壊の移動範囲マップ:", f)
            find_piece_destination(piece, pinfo, aspiration_map, piece_map, number, f)

def create_aspiration_map_army_destroyer(pinfo, player, f):
    # start = time.time()
    best_dest_info = [[MAX_DISTANCE for i_ in range(map_row)] for j_ in range(map_col)]
            # 移動できる場所を確認したら敵の情報enemyを展開
            
    for enemy_piece in pinfo:    # 敵のリストを展開
        # if (player == PLAYER1 and enemy_piece.piece_id >= PLAYER2_CASTLE_ID) or (player == PLAYER2 
        #     and enemy_piece.piece_id < PLAYER2_CASTLE_ID):
        #     print(f"敵の名前: {piece_dict[enemy_piece.piece_id][2]}, 生きているか: {shows_alive[enemy_piece.dead_or_alive]}", file=f)

        if (player == PLAYER1 and enemy_piece.piece_id >= PLAYER2_CASTLE_ID) or (player == PLAYER2 
            and enemy_piece.piece_id < PLAYER2_CASTLE_ID):
            # 敵のピースがCASTLEじゃないかつ、生きているかどうかを確認
            if enemy_piece.piece_type != CASTLE and enemy_piece.dead_or_alive == ALIVE:
                for y, x in itertools.product(range(map_row), range(map_col)):
                    man_dis = abs(enemy_piece.now_y - y) + abs(enemy_piece.now_x - x)
                    if man_dis < best_dest_info[y][x]:    # 現在のマンハッタン距離より値は低い場合
                        best_dest_info[y][x] = man_dis    # 低い値に更新
    # elapsed_time = time.time() - start 
    # print("elapsed_time:{0}".format(elapsed_time) + "sec")
    return best_dest_info

# シャッフル
def move_pieces_castle_destroyer(pinfo, player_id, piece_map, number,  f):
    # シャッフルしたピースを展開
    for piece in pinfo:
        if piece.dead_or_alive == ALIVE and piece.move_finished == NOT_MOVED and piece.piece_type != CASTLE:
        # 有利度マップ作成
            f_a = open("aspiration_2.txt", "a")
            aspiration = create_aspiration_map_castle_destroyer(piece, pinfo, player_id, f_a)
            
            f_a.close()
            # if number == 99:
            #     file_print_map(aspiration, f"{piece_dict[piece.piece_id][2]}'s aspiration_map:", f)
            #     file_print_map(piece.destinations, f"{piece_dict[piece.piece_id][2]}'s 移動範囲のマップ:", f)
            # 移動する
            find_piece_destination(piece, pinfo, aspiration, piece_map, number, f)

# 有利度マップ作成
def create_aspiration_map_castle_destroyer(piece, pinfo, player, f):
    start = time.time()
    best_dest_info = [[MAX_DISTANCE for i_ in range(map_row)] for j_ in range(map_col)]
    if player == PLAYER1:
        target_id = PLAYER2_CASTLE_ID
    else:
        player == PLAYER2
        target_id = PLAYER1_CASTLE_ID
    # f_a = open("aspiration.txt", "a")
    check_distance(pinfo[target_id].now_y, pinfo[target_id].now_x, 0, piece, best_dest_info, f)
    # f_a.close()
    return best_dest_info

# 
def check_distance(y, x, dis, piece, aspmap, f):
    try:
        aspmap[y][x] = dis
    except IndexError as e:
        print(e, file=f)
        print(y, x, file=f)
    move = [[-1, 0], [1, 0], [0, 1], [0, -1]]
    # print_map(aspmap, piece_dict[piece.piece_id][2])
    for dis_move in move:
        if (0 <= y+dis_move[0] < map_row ) and (0 <= x+dis_move[1] < map_col) and (terrain_map[y+dis_move[0]][x+dis_move[1]] != WALL):
            new_dis = dis + move_cost[piece.piece_type][terrain_map[y + dis_move[0]][x + dis_move[1]]]
            if aspmap[y + dis_move[0]][x + dis_move[1]] > new_dis:
                check_distance(y + dis_move[0], x + dis_move[1], new_dis, piece, aspmap, f)

# 各コマの移動先をランダムで決定する関数
def find_piece_destination(piece, pinfo, aspiration, piece_map, number, f):
    if (piece.dead_or_alive == ALIVE) and (piece.move_finished == NOT_MOVED):
        possible_list = []
        # for best_move in aspiration:
        for y, x in itertools.product(range(map_row), range(map_col)):
            # print(aspiration)
            if piece.destinations[y][x] != 0:
            # 移動先に駒がないことを確認
                for other_piece in pinfo:
                    if (other_piece.dead_or_alive == ALIVE and 
                        other_piece.piece_id != piece.piece_id and 
                        other_piece.now_y == y and other_piece.now_x == x):
                        break
                else:
                    possible_list.append([y, x])
        
        best_dest = [piece.now_y, piece.now_x]
        best_dest_value = MAX_DISTANCE
        for dest in possible_list:
            # 可能な移動先に移動希望が一番良い場所を探す
            # if aspiration[dest[0]][dest[1]] < best_dest_value:
            if aspiration[dest[0]][dest[1]] < aspiration[best_dest[0]][best_dest[1]]:
                if aspiration[best_dest[0]][best_dest[1]] == best_dest_value:
                    r_c = random.choice([True, False])
                    if r_c == True:
                        best_dest[0] = dest[0]
                        best_dest[1] = dest[1]
                        best_dest_value = aspiration[dest[0]][dest[1]]
                else:
                    best_dest[0] = dest[0]
                    best_dest[1] = dest[1]
                    best_dest_value = aspiration[dest[0]][dest[1]]
        # if number =:
        #     print("来たことを喜べ!", file=f)
        #     print(f"best_dest[0]: {best_dest[0]}, best_dest[1]: {best_dest[1]}", file=f)
        # print('変更する')
        piece_map[piece.now_y][piece.now_x] = terrain_map[piece.now_y][piece.now_x]    # ピースの現在の場所を元の地形数値に戻す
        # 駒を移動
        piece.now_y = best_dest[0]
        piece.now_x = best_dest[1]
        piece_map[piece.now_y][piece.now_x] = piece_dict[piece.piece_id][0]    # ピースが移動する場所に文字を代入
        # 駒の移動先を削除
        # 駒は移動済み
        piece.move_finished = MOVED
        resolve_battle(piece, pinfo, piece_map,  f)

# 敵のピースがいるかどうかを確認
def resolve_battle(piece, pinfo, piece_map, f):
    combat_candidate_hp = None
    destinations_check = [[-1, 0], [1, 0], [0, 1], [0, -1]]
    now_enemy_hp = COMPARISON_HP
    for enemy_piece in pinfo:
        if ((piece.piece_id < PLAYER2_CASTLE_ID and enemy_piece.piece_id >= PLAYER2_CASTLE_ID) or
            (piece.piece_id >= PLAYER2_CASTLE_ID and enemy_piece.piece_id < PLAYER2_CASTLE_ID)):
            for dest_c in destinations_check:
                if (piece.now_y+dest_c[0] == enemy_piece.now_y) and (piece.now_x+dest_c[1] == enemy_piece.now_x):
                    if enemy_piece.hit_point < now_enemy_hp:
                        combat_candidate_hp = enemy_piece
                        now_enemy_hp = enemy_piece.hit_point
    if combat_candidate_hp !=None:
        fight_battle(piece, combat_candidate_hp, piece_map, f)

def fight_battle(attack_piece, defence_piece, piece_map, f):
    print(f"Starting battle between {piece_dict[attack_piece.piece_id][2]} at {(attack_piece.now_y, attack_piece.now_x)} and {piece_dict[defence_piece.piece_id][2]} at {(defence_piece.now_y, defence_piece.now_x)}" , file=f)
    # print(f"Starting battle between {piece_dict[attack_piece.piece_id][2]} at {(attack_piece.now_y, attack_piece.now_x)} and {piece_dict[defence_piece.piece_id][2]} at {(defence_piece.now_y, defence_piece.now_x)}")
    result_hp = int(update_battle_hp(attack_piece, defence_piece))
    defence_piece.hit_point -= result_hp
    print(f"Attacked piece hp after attack: {defence_piece.hit_point}", file=f)
    if defence_piece.hit_point < 0:
        print(f"Attackied piece dead in battle: {piece_dict[defence_piece.piece_id][2]}", file=f)
        # print(f"Attack][defence_piece.now_x] = terrain_map[defence_piece.now_y][defence_piece.now_x]
        defence_piece.dead_or_alive = DEAD
        # print("敵は死んでいる")
        piece_map[defence_piece.now_y][defence_piece.now_x] = terrain_map[defence_piece.now_y][defence_piece.now_x]
        defence_piece.now_y, defence_piece.now_x = MAX_DISTANCE, MAX_DISTANCE
        
    else:
        print(f"Counter attack between {piece_dict[defence_piece.piece_id][2]} at {(defence_piece.now_y, defence_piece.now_x)} and {piece_dict[attack_piece.piece_id][2]} at {(attack_piece.now_y, attack_piece.now_x)}", file=f)
        # print(f"Counter attack between {piece_dict[defence_piece.piece_id][2]} at {(defence_piece.now_y, defence_piece.now_x)} and {piece_dict[attack_piece.piece_id][2]} at {(attack_piece.now_y, attack_piece.now_x)}")
        counter_hp = int(update_battle_hp(defence_piece, attack_piece))
        attack_piece.hit_point -= counter_hp
        print(f"Attacking piece hp after attack: {attack_piece.hit_point}", file=f)
        # print(f"Attacking piece hp after attack: {attack_piece.hit_point}")
        if attack_piece.hit_point < 0:
            print(f"Attacking piece dead in battle: {piece_dict[attack_piece.piece_id][2]}", file=f)
            # print(f"Attacking piece dead in battle: {piece_dict[attack_piece.piece_id][2]}")
            attack_piece.dead_or_alive = DEAD
            piece_map[attack_piece.now_y][attack_piece.now_x] = terrain_map[attack_piece.now_y][attack_piece.now_x]
            attack_piece.now_y, attack_piece.now_x = MAX_DISTANCE, MAX_DISTANCE
        
# HPを計算
def update_battle_hp(attack_piece, defence_piece):
    attack_power = attack_piece.attack + ((attack_piece.attack * piece_commpatibility[attack_piece.piece_type][defence_piece.piece_type]) / 100)
    defence_power = defence_piece.defence + ((defence_piece.defence * terrain_power[terrain_map[defence_piece.now_y][defence_piece.now_x]]) / 100)
    defence_hp = attack_power - defence_power
    if defence_hp < 0:
        defence_hp = 0
    return defence_hp

# ファイル書き出し用関数
def file_print_pinfo(pinfo, f_pinfo):
    for piece in pinfo:
        if piece.dead_or_alive == ALIVE:
            print(f"{piece_dict[piece.piece_id][2]} info: y = {piece.now_y}, x = {piece.now_x}, HP = {piece.hit_point}, att = {piece.attack}, def = {piece.defence}, mvp = {piece.mov_pow}", file=f_pinfo)

# 現在のpieceの情報を表示
def print_pinfo(pinfo):
    for piece in pinfo:
        if piece.dead_or_alive == ALIVE:
            print(f"{piece_dict[piece.piece_id][2]} info: y = {piece.now_y}, x = {piece.now_x}, HP = {piece.hit_point}, att = {piece.attack}, def = {piece.defence}, mvp = {piece.mov_pow}")

def read_file(file):
    fileobj = open(file)
    map_info = fileobj.read()
    fileobj.close()
    return map_info

def create_map_info(map):
    map_row = []
    map_info = []
    for map_char in map:
        if map_char == '\n':
            map_info.append(map_row)
            map_row = []
        elif map_char == 'R':
            map_row.append(ROCK)
        elif map_char == 'S':
            map_row.append(SAND)
        elif map_char == 'G':
            map_row.append(GRASS)
        elif map_char == 'W':
            map_row.append(WALL)
    return map_info

def create_pinfo(pinfor):
    piece_info = []
    p1_soldier_id = 0
    p1_archer_id = 0
    p2_soldier_id = 0
    p2_archer_id = 0
    for cur_piece in pinfor:
        piece_list = cur_piece.split(" ")
        y, x = int(piece_list[1]), int(piece_list[2])
        if piece_list[0] == 'C':
            piece_info.append(Piece(PLAYER1_CASTLE_ID , CASTLE, y, x, y, x, ALIVE, NOT_MOVED, CASTLE_HP, CASTLE_ATTACK, CASTLE_DEFENCE, CASTLE_MOVE))
        elif piece_list[0] == 'S':
            piece_info.append(Piece(PLAYER1_SOLDIER1_ID + p1_soldier_id , SOLDIER, y, x, y, x, ALIVE, NOT_MOVED, SOLDIER_HP, SOLDIER_ATTACK, SOLDIER_DEFENCE, SOLDIER_MOVE))
            p1_soldier_id += 1
        elif piece_list[0] == 'A':
            piece_info.append(Piece(PLAYER1_ARCHER1_ID + p1_archer_id , ARCHER, y, x, y, x, ALIVE, NOT_MOVED, ARCHER_HP, ARCHER_ATTACK, ARCHER_DEFENCE, ARCHER_MOVE))
            p1_archer_id += 1
        elif piece_list[0] == 'K':   
            piece_info.append(Piece(PLAYER1_KNIGHT_ID, KNIGHT, y, x, y, x, ALIVE, NOT_MOVED, KNIGHT_HP, KNIGHT_ATTACK, KNIGHT_DEFENCE, KNIGHT_MOVE))
        # プレイヤー2
        if piece_list[0] == 'c':
            piece_info.append(Piece(PLAYER2_CASTLE_ID , CASTLE, y, x, y, x, ALIVE, MOVED, CASTLE_HP, CASTLE_ATTACK, CASTLE_DEFENCE, CASTLE_MOVE))
        elif piece_list[0] == 's':
            piece_info.append(Piece(PLAYER2_SOLDIER1_ID + p2_soldier_id , SOLDIER, y, x, y, x, ALIVE, MOVED, SOLDIER_HP, SOLDIER_ATTACK, SOLDIER_DEFENCE, SOLDIER_MOVE))
            p2_soldier_id += 1
        elif piece_list[0] == 'a':
            piece_info.append(Piece(PLAYER2_ARCHER1_ID + p2_archer_id , ARCHER, y, x, y, x, ALIVE, MOVED, ARCHER_HP, ARCHER_ATTACK, ARCHER_DEFENCE, ARCHER_MOVE))
            p2_archer_id += 1
        elif piece_list[0] == 'k':   
            piece_info.append(Piece(PLAYER2_KNIGHT_ID, KNIGHT, y, x, y, x, ALIVE, MOVED, KNIGHT_HP, KNIGHT_ATTACK, KNIGHT_DEFENCE, KNIGHT_MOVE))
    return piece_info
    
# ファイル書き出し用関数
def file_not_name_print_map(map, f_map):
    output_row = ""
    for row in map:
        for entry in row:
            output_row += ("{:>3}".format(entry))
        print(output_row, file=f_map)
        output_row = ""

def not_name_print_map(map):
    output_row = ""
    for row in map:
        for entry in row:
            output_row += ("{:>3}".format(entry))
        print(output_row)
        output_row = ""

def print_map(map, print_name):
    print(print_name)
    output_row = ""
    for row in map:
        for entry in row:
            output_row += ("{:>3}".format(entry))
        print(output_row)
        output_row = ""
        
def file_print_map(map, print_name, f):
    print(print_name, file=f)
    output_row = ""
    for row in map:
        for entry in row:
            output_row += ("{:>3}".format(entry))
        print(output_row, file=f)
        output_row = ""


file = "Test_Game_Map.txt"
map_string = read_file(file)   # file read finction read
map_string_list = map_string.split("#")    # #で分割する
map_info_string = map_string_list[0]
piece_info_string = map_string_list[1].split("\n")[1:]
# 迷路の情報を取得
terrain_map = create_map_info(map_info_string)
# 最初の位置のピースを迷路に代入する用のマップ
not_piece_map = copy.deepcopy(terrain_map)
map_row, map_col = np.array(not_piece_map, dtype=int).shape
print(map_row, map_col)
# コマの情報を作成
piece_info = create_pinfo(piece_info_string)
start_pinfo = copy.deepcopy(piece_info)
print_map(not_piece_map, "コピーする前")
print(piece_info[PLAYER1_CASTLE_ID].piece_id)
# 最初の位置のピースを代入
now_piece_map = startyx_piece_map(not_piece_map, piece_info)
backup_start_piece_map = copy.deepcopy(now_piece_map)
# 移動開始
piece_max_number_of_moves(piece_info, now_piece_map)
elapsed_time = time.time() - start 
print("elapsed_time:{0}".format(elapsed_time) + "sec")
