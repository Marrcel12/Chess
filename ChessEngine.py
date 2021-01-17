import math

class GameState():
    def __init__(self):

        self.board = [
            ["bR","bN","bB","bQ","bK","bB","bN","bR"],
            ["bP","bP","bP","bP","bP","bP","bP","bP"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["--","--","--","--","--","--","--","--"],
            ["wP","wP","wP","wP","wP","wP","wP","wP"],
            ["wR","wN","wB","wQ","wK","wB","wN","wR"]]
        self.move_functions = {'P': self.get_pawn_moves, 'R': self.get_rook_moves, 'N': self.get_knight_moves,
                              'B': self.get_bishop_moves, 'Q': self.get_queen_moves, 'K': self.get_king_moves}
        
        
        self.white_to_move = True
        self.move_log = []
        self.w_king_loc = (7,4)
        self.b_king_loc = (0,4)
        
        self.check_mate = False
        self.stale_mate = False
        
        self.enpassant_possible = ()
        
        self.current_castling_right = castle_rights(True, True, True, True)
        self.castle_rights_log = [castle_rights(self.current_castling_right.wks, self.current_castling_right.bks,
                                             self.current_castling_right.wqs, self.current_castling_right.bqs)]
        
        
    def makeMove(self, move):
        self.board[move.start_row][move.start_col] = '--'
        self.board[move.end_row][move.end_col] = move.piece_moved
        self.move_log.append(move)
        self.white_to_move = not self.white_to_move
        if move.piece_moved == 'wK':
            self.w_king_loc = (move.end_row, move.end_col)
        elif move.piece_moved == 'bK':
            self.b_king_loc = (move.end_row, move.end_col)

        # promotion
        if move.is_pawn_promotion:
            self.board[move.end_row][move.end_col] = move.piece_moved[0] + 'Q'

        # enpassant
        if move.is_enpassant_move:
            self.board[move.start_row][move.end_col] = '--'
        if move.piece_moved[1] == 'P' and abs(move.start_row - move.end_row) == 2:
            self.enpassant_possible = ((move.start_row + move.end_row) // 2, move.start_col)
        else:
            self.enpassant_possible = ()

        if move.is_castle_move:
            if move.end_col - move.start_col == 2:
                self.board[move.end_row][move.end_col-1] = self.board[move.end_row][move.end_col+1]
                self.board[move.end_row][move.end_col+1] = '--'
            else:
                self.board[move.end_row][move.end_col+1] = self.board[move.end_row][move.end_col-2]
                self.board[move.end_row][move.end_col-2] = '--'

        self.update_castle_rights(move)
        self.castle_rights_log.append(castle_rights(self.current_castling_right.wks, self.current_castling_right.bks,
                                             self.current_castling_right.wqs, self.current_castling_right.bqs))

        
                

    def undoMove(self):
        if len(self.move_log) != 0:
            move = self.move_log.pop()
            self.board[move.start_row][move.start_col] = move.piece_moved
            self.board[move.end_row][move.end_col] = move.piece_captured
            # changing turn
            self.white_to_move = not self.white_to_move
            if move.piece_moved == 'wK':
                self.w_king_loc = (move.start_row, move.start_col)
            elif move.piece_moved == 'bK':
                self.b_king_loc = (move.start_row, move.start_col)

            # undoing enpassant move
            if move.is_enpassant_move:
                self.board[move.end_row][move.end_col] = '--'
                self.board[move.start_row][move.end_col] = move.piece_captured
                self.enpassant_possible = (move.end_row, move.end_col)
            # undo a 2 square pawn advance
            if move.piece_moved[1] == 'P' and abs(move.start_row - move.end_row) == 2:
                self.enpassant_possible = ()
                
            # undoing castle move
            if move.is_castle_move:
                if move.end_col - move.start_col == 2:
                    self.board[move.end_row][move.end_col+1] = self.board[move.end_row][move.end_col-1]
                    self.board[move.end_row][move.end_col-1] = '--'
                else:
                    self.board[move.end_row][move.end_col-2] = self.board[move.end_row][move.end_col+1]
                    self.board[move.end_row][move.end_col+1] = '--'
            
            # undoing castling rights
            self.castle_rights_log.pop()
            self.current_castling_right = self.castle_rights_log[-1]
            


    def update_castle_rights(self, move):
        if move.piece_moved == 'wK':
            self.current_castling_right.wks = False
            self.current_castling_right.wqs = False
        elif move.piece_moved == 'bK':
            self.current_castling_right.bks = False
            self.current_castling_right.bqs = False
        elif move.piece_moved == 'wR':
            if move.start_row == 7:
                if move.start_col == 0:
                    self.current_castling_right.wqs = False
                elif move.start_col == 7:
                    self.current_castling_right.wks = False

        elif move.piece_moved == 'bR':
            if move.start_row == 0:
                if move.start_col == 0:
                    self.current_castling_right.bqs = False
                elif move.start_col == 7:
                    self.current_castling_right.bks = False
                

                

    def get_valid_moves(self):
        tempenpassant_possible = self.enpassant_possible
        tempcastle_rights = castle_rights(self.current_castling_right.wks, self.current_castling_right.bks,
                                        self.current_castling_right.wqs, self.current_castling_right.bqs)
        # gets all move
        moves = self.get_all_moves()
        if self.white_to_move:
            self.getCastleMoves(self.w_king_loc[0], self.w_king_loc[1], moves)
        else:
            self.getCastleMoves(self.b_king_loc[0], self.b_king_loc[1], moves)
        for i in range(len(moves)-1,-1,-1):
            self.makeMove(moves[i])
            self.white_to_move = not self.white_to_move
            if self.inCheck():
                moves.remove(moves[i])
            self.white_to_move = not self.white_to_move
            self.undoMove()
        if len(moves) == 0:
            # sees if in check or stale_mate
            if self.inCheck():
                self.check_mate = True
            else:
                self.stale_mate = True
        
        # all the valid moves
        self.enpassant_possible = tempenpassant_possible
        self.current_castling_right = tempcastle_rights
        return moves

    def inCheck(self):
        # checks which turn
        if self.white_to_move:
            # returns a bool and checks if the whiite king is under attack
            return self.squareUnderAttack(self.w_king_loc[0], self.w_king_loc[1])
        else:
            # then checks black king
            return self.squareUnderAttack(self.b_king_loc[0], self.b_king_loc[1])

    def squareUnderAttack(self, r, c):
        # sees opponent moves by changing turn gets all there moves and changes back turn
        self.white_to_move = not self.white_to_move
        oppMoves = self.get_all_moves()
        self.white_to_move = not self.white_to_move
        # checks all moves and sees if the end square is the square entered in the function
        for move in oppMoves:
            if move.end_row == r and move.end_col == c:
                return True
        return False 


    def get_all_moves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                # checking piece colour
                turn = self.board[r][c][0]
                if (turn == 'w' and self.white_to_move) or (turn == 'b' and not self.white_to_move):
                    # using dictionary to reduce if statements
                    piece = self.board[r][c][1]
                    self.move_functions[piece](r, c, moves)
        return moves




                     
    def get_pawn_moves(self, r, c, moves):
        if self.white_to_move:
            if self.board[r-1][c] == '--':
                moves.append(Move((r, c), (r-1, c), self.board))
                if r == 6 and self.board[r-2][c] == '--':
                    moves.append(Move((r, c), (r-2, c), self.board))
            # captures to the left        
            if c - 1 >= 0: 
                if self.board[r-1][c-1][0] == 'b':
                    moves.append(Move((r, c), (r-1, c-1), self.board))
                elif (r-1, c-1) == self.enpassant_possible:
                    moves.append(Move((r, c), (r-1, c-1), self.board, is_enpassant_move = True))
            # captures to the right
            if c + 1 <= 7: 
                if self.board[r-1][c+1][0] == 'b':
                    moves.append(Move((r, c), (r-1, c+1), self.board))
                elif (r-1, c+1) == self.enpassant_possible:
                    moves.append(Move((r, c), (r-1, c+1), self.board, is_enpassant_move = True))

        else:
            if self.board[r + 1][c] == '--':
                moves.append(Move((r, c), (r + 1, c), self.board))
                if r == 1 and self.board[r + 2][c] == '--':
                    moves.append(Move((r, c), (r+2, c), self.board))
            # captures to the left
            if c - 1 >= 0:
                if self.board[r + 1][c - 1][0] == 'w':
                    moves.append(Move((r, c), (r + 1, c-1), self.board))
                elif (r + 1, c - 1) == self.enpassant_possible:
                    moves.append(Move((r, c), (r + 1, c - 1), self.board, is_enpassant_move = True))
            # captures to the right
            if c + 1 <= 7:
                if self.board[r + 1][c + 1][0] == 'w':
                    moves.append(Move((r, c), (r+1, c+1), self.board))
                elif (r + 1, c + 1) == self.enpassant_possible:
                    moves.append(Move((r, c), (r + 1, c + 1), self.board, is_enpassant_move = True))
        
    def get_rook_moves(self, r, c, moves):
        directions = ((-1,0), (0,-1), (1,0), (0,1))
        opp_color = 'b' if self.white_to_move else 'w'
        for d in directions:
            for i in range(1,8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    endPiece = self.board[end_row][end_col]
                    if endPiece == '--':
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                    elif endPiece[0] == opp_color:
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                        break
                    else:
                        break
                else:
                    break
            
    def get_bishop_moves(self, r, c, moves):
        directions = ((-1,-1), (1,-1), (1,1), (-1,1))
        opp_color = 'b' if self.white_to_move else 'w'
        for d in directions:
            for i in range(1,8):
                end_row = r + d[0] * i
                end_col = c + d[1] * i
                if 0 <= end_row < 8 and 0 <= end_col < 8:
                    endPiece = self.board[end_row][end_col]
                    if endPiece == '--':
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                    elif endPiece[0] == opp_color:
                        moves.append(Move((r, c), (end_row, end_col), self.board))
                        break
                    else:
                        break
                # breaks if it off the board
                else:
                    break
                
    def get_queen_moves(self, r, c, moves):
        self.get_rook_moves(r, c, moves)
        self.get_bishop_moves(r, c, moves)

    def get_knight_moves(self, r, c, moves):
        # knight moves
        knightMoves = ((-2,-1), (-2,1), (-1,-2), (-1,2), (1,-2), (1,2), (2,-1), (2,1))
        # gets ally colour
        allyColour = 'w' if self.white_to_move else 'b'
        for m in knightMoves:
            end_row = r + m[0]
            end_col = c + m[1]
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                endPiece = self.board[end_row][end_col]
                if endPiece[0] != allyColour:
                    moves.append(Move((r, c), (end_row, end_col), self.board))

    def get_king_moves(self, r, c, moves):
        directions = ((-1,-1), (1,-1), (1,1), (-1,1), (-1,0), (0,-1), (1,0), (0,1))
        allyColour = 'w' if self.white_to_move else 'b'
        for d in directions:
            end_row = r + d[0]
            end_col = c + d[1]
            # checks if off the board
            if 0 <= end_row < 8 and 0 <= end_col < 8:
                endPiece = self.board[end_row][end_col]
                if endPiece[0] != allyColour:
                    moves.append(Move((r, c), (end_row, end_col), self.board))

    

    def getCastleMoves(self, r, c, moves):
        if self.squareUnderAttack(r, c):
            return
        if (self.white_to_move and self.current_castling_right.wks) or (not self.white_to_move and self.current_castling_right.bks):
            self.getKingsideCastleMoves(r, c, moves)
        if (self.white_to_move and self.current_castling_right.wqs) or (not self.white_to_move and self.current_castling_right.bqs):
            self.getQueensideCastleMoves(r, c, moves)

    def getKingsideCastleMoves(self, r, c, moves):
        if self.board[r][c + 1] == '--' and self.board[r][c + 2] == '--':
            if not self.squareUnderAttack(r, c + 1) and not self.squareUnderAttack(r, c + 2):
                moves.append(Move((r, c), (r, c + 2), self.board, is_castle_move = True))

    def getQueensideCastleMoves(self, r, c, moves):
        if self.board[r][c - 1] == '--' and self.board[r][c - 2] == '--' and self.board[r][c - 3] == '--':
            if not self.squareUnderAttack(r, c - 1) and not self.squareUnderAttack(r, c - 2):
                moves.append(Move((r, c), (r, c - 2), self.board, is_castle_move = True))        


class castle_rights():

    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs
    

class Move():
    ranks_to_rows = {"1":7,"2":6,"3":5,"4":4,
                   "5":3,"6":2,"7":1,"8":0}
    rows_to_ranks = {v: k for k, v in ranks_to_rows.items()}

    filesToCols = {"a":0,"b":1,"c":2,"d":3,
                   "e":4,"f":5,"g":6,"h":7}
    cols_to_files = {v: k for k, v in filesToCols.items()}

    
    def __init__(self, startSq, endSq, board, is_enpassant_move = False, is_castle_move = False):
        # start location
        self.start_row = startSq[0]
        self.start_col = startSq[1]
        # end location
        self.end_row = endSq[0]
        self.end_col = endSq[1]
        # piece moved
        self.piece_moved = board[self.start_row][self.start_col]
        self.piece_captured = board[self.end_row][self.end_col]
        # pawn prom
        self.is_pawn_promotion = ((self.piece_moved == 'wP' and self.end_row == 0) or (self.piece_moved == 'bP' and self.end_row == 7))
        
        self.is_enpassant_move = is_enpassant_move
        
        if self.is_enpassant_move:
            self.piece_captured = 'wP' if self.piece_moved == 'bP' else 'bP'

        self.is_castle_move = is_castle_move

        self.move_id = self.start_row * 1000 + self.start_col * 100 + self.end_row * 10 + self.end_col
    # new equality function
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.move_id == other.move_id
    
    #print out the move in chess notation (e2e4)
    def get_chess_not(self):
        return self.get_rank_file(self.start_row, self.start_col) + self.get_rank_file(self.end_row, self.end_col)
    def get_rank_file(self, r, c):
        return self.cols_to_files[c] + self.rows_to_ranks[r]













    
