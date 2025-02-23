import pygame as pg
import copy
import math

pg.init()
screen = pg.display.set_mode((400, 400))
clock = pg.time.Clock()

# CONSTANTES
width = 40      # largeur d'une case
height = 40     # hauteur d'une case
white = (255, 255, 255)
black = (0, 0, 0)
l, L = 10, 10   # dimensions en nombre de cases
size = 40       # taille d'une case en pixels

# --- Code de damier  ---
def damier(w, h, color, size, l, L):
    for x in range(l):
        if x % 2 == 0:
            for y in range(L//2):
                x2 = x * size
                y2 = y * size * 2
                rect = pg.Rect(x2, y2, w, h)
                pg.draw.rect(screen, color, rect)
        else:
            for y in range(L//2):
                x2 = x * size
                y2 = y * size * 2 + size
                rect = pg.Rect(x2, y2, w, h)
                pg.draw.rect(screen, color, rect)

# --- Initialisation du plateau de jeu ---
# Représentation : plateau[r][c]
# 0 : case vide
# 1 : pièce "blanche" (joueur humain), 3 : dame blanche (king)
# 2 : pièce "noire" (IA), 4 : dame noire (king)
def init_board():
    board = [[0 for _ in range(10)] for _ in range(10)]
    # Placement des pièces noires sur les 4 premières lignes (sur les cases "sombres": (r+c) pair)
    for r in range(4):
        for c in range(10):
            if (r + c) % 2 == 0:
                board[r][c] = 2
    # Placement des pièces blanches sur les 4 dernières lignes
    for r in range(6, 10):
        for c in range(10):
            if (r + c) % 2 == 0:
                board[r][c] = 1
    return board

# --- Affichage des pièces ---
def draw_pieces(board):
    for r in range(10):
        for c in range(10):
            piece = board[r][c]
            if piece != 0:
                center = (c * size + size // 2, r * size + size // 2)
                # Couleur et dessin (les dames sont dessinées avec une teinte différente)
                if piece == 1:
                    color_piece = (255, 0, 0)      # rouge pour le joueur humain
                elif piece == 3:
                    color_piece = (255, 100, 100)  # dame blanche
                elif piece == 2:
                    color_piece = (0, 0, 255)      # bleu pour l'IA
                elif piece == 4:
                    color_piece = (100, 100, 255)  # dame noire
                pg.draw.circle(screen, color_piece, center, size // 2 - 5)

# --- Affichage complet du plateau ---
def draw_board(board):
    screen.fill(white)
    damier(width, height, black, size, l, L)
    draw_pieces(board)

# --- Récupérer les mouvements possibles d'une pièce ---
# Chaque mouvement est représenté par un tuple (ligne_depart, col_depart, ligne_arrivée, col_arrivée, [liste_des_cases_sautées])
def get_piece_moves(board, r, c, piece, captured=None, start=None):
    if captured is None:
        captured = []
    if start is None:
        start = (r, c)
    moves = []
    # Définition des directions en fonction du type de pièce
    if piece == 1:  # pièce blanche (non dame) : avance vers le haut
        directions = [(-1, -1), (-1, 1)]
    elif piece == 2:  # pièce noire (non dame) : avance vers le bas
        directions = [(1, -1), (1, 1)]
    else:  # dames (king) : peuvent aller dans toutes les directions
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
    
    capture_found = False
    # Recherche de mouvements de prise
    for d in directions:
        mid_r = r + d[0]
        mid_c = c + d[1]
        end_r = r + 2 * d[0]
        end_c = c + 2 * d[1]
        if 0 <= mid_r < 10 and 0 <= mid_c < 10 and 0 <= end_r < 10 and 0 <= end_c < 10:
            # Définir l'adversaire
            if piece in (1, 3):
                opponents = (2, 4)
            else:
                opponents = (1, 3)
            if board[mid_r][mid_c] in opponents and board[end_r][end_c] == 0 and (mid_r, mid_c) not in captured:
                capture_found = True
                temp_board = copy.deepcopy(board)
                temp_board[r][c] = 0
                temp_board[mid_r][mid_c] = 0
                temp_board[end_r][end_c] = piece
                new_captured = captured + [(mid_r, mid_c)]
                subsequent_moves = get_piece_moves(temp_board, end_r, end_c, piece, new_captured, start)
                if subsequent_moves:
                    for move in subsequent_moves:
                        moves.append(move)
                else:
                    moves.append((start[0], start[1], end_r, end_c, new_captured))
    # Si une prise est possible, on ne propose pas de déplacement simple
    if capture_found:
        return moves
    # Sinon, recherche de mouvements simples (uniquement si on n'est pas en chaîne de prises)
    if not captured:
        for d in directions:
            new_r = r + d[0]
            new_c = c + d[1]
            if 0 <= new_r < 10 and 0 <= new_c < 10 and board[new_r][new_c] == 0:
                moves.append((start[0], start[1], new_r, new_c, []))
    return moves

# --- Récupérer tous les mouvements possibles pour un joueur ---
def get_all_moves(board, player):
    moves = []
    for r in range(10):
        for c in range(10):
            if player == 'white' and board[r][c] in (1, 3):
                piece_moves = get_piece_moves(board, r, c, board[r][c])
                moves.extend(piece_moves)
            elif player == 'black' and board[r][c] in (2, 4):
                piece_moves = get_piece_moves(board, r, c, board[r][c])
                moves.extend(piece_moves)
    # Si une prise est possible, on ne garde que ces mouvements
    capture_moves = [m for m in moves if m[4]]
    if capture_moves:
        return capture_moves
    return moves

# --- Appliquer un mouvement sur le plateau ---
def apply_move(board, move):
    new_board = copy.deepcopy(board)
    r_start, c_start, r_end, c_end, captured = move
    piece = new_board[r_start][c_start]
    new_board[r_start][c_start] = 0
    for (cr, cc) in captured:
        new_board[cr][cc] = 0
    # Promotion en dame si la pièce atteint l'extrémité adverse
    if piece == 1 and r_end == 0:
        piece = 3
    if piece == 2 and r_end == 9:
        piece = 4
    new_board[r_end][c_end] = piece
    return new_board

# --- Fonction d'évaluation du plateau ---
def evaluate_board(board):
    score = 0
    for r in range(10):
        for c in range(10):
            if board[r][c] == 1:
                score -= 1
            elif board[r][c] == 3:
                score -= 1.5
            elif board[r][c] == 2:
                score += 1
            elif board[r][c] == 4:
                score += 1.5
    return score

# --- Algorithme Minimax (profondeur limitée) ---
def minimax(board, depth, maximizingPlayer):
    if depth == 0:
        return evaluate_board(board), None
    if maximizingPlayer:
        maxEval = -math.inf
        best_move = None
        moves = get_all_moves(board, 'black')
        if not moves:
            return evaluate_board(board), None
        for move in moves:
            new_board = apply_move(board, move)
            eval, _ = minimax(new_board, depth - 1, False)
            if eval > maxEval:
                maxEval = eval
                best_move = move
        return maxEval, best_move
    else:
        minEval = math.inf
        best_move = None
        moves = get_all_moves(board, 'white')
        if not moves:
            return evaluate_board(board), None
        for move in moves:
            new_board = apply_move(board, move)
            eval, _ = minimax(new_board, depth - 1, True)
            if eval < minEval:
                minEval = eval
                best_move = move
        return minEval, best_move

# --- Boucle principale du jeu ---
def main():
    board = init_board()
    running = True
    turn = 'white'  # le joueur humain joue les pièces blanches
    selected = None
    valid_moves = []
    
    while running:
        clock.tick(30)
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_q:
                    running = False
            elif event.type == pg.MOUSEBUTTONDOWN:
                if turn == 'white':
                    pos = pg.mouse.get_pos()
                    col = pos[0] // size
                    row = pos[1] // size
                    # Si une pièce est déjà sélectionnée, on vérifie le mouvement
                    if selected:
                        move_found = None
                        for move in valid_moves:
                            if move[2] == row and move[3] == col:
                                move_found = move
                                break
                        if move_found:
                            board = apply_move(board, move_found)
                            turn = 'black'
                            selected = None
                            valid_moves = []
                        else:
                            # Nouvelle sélection si on clique sur une autre pièce blanche
                            if board[row][col] in (1, 3):
                                selected = (row, col)
                                valid_moves = get_piece_moves(board, row, col, board[row][col])
                    else:
                        if board[row][col] in (1, 3):
                            selected = (row, col)
                            valid_moves = get_piece_moves(board, row, col, board[row][col])
        
        # Tour de l'IA (joue les pièces noires)
        if turn == 'black':
            pg.time.delay(500)  # petit délai pour simuler la réflexion
            _, move = minimax(board, 3, True)
            if move:
                board = apply_move(board, move)
            turn = 'white'
        
        draw_board(board)
        # Mise en surbrillance de la pièce sélectionnée et des déplacements possibles
        if selected:
            r, c = selected
            rect = pg.Rect(c * size, r * size, size, size)
            pg.draw.rect(screen, (0, 255, 0), rect, 3)
            for move in valid_moves:
                dest_rect = pg.Rect(move[3] * size, move[2] * size, size, size)
                pg.draw.rect(screen, (255, 255, 0), dest_rect, 3)
        
        pg.display.flip()
    
    pg.quit()

if __name__ == "__main__":
    main()

