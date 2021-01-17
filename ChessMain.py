import ChessEngine
import pygame as p
import math
import random


WIDTH = HEIGHT = 512
dim = 8 
sqsize = HEIGHT // dim
maxfps = 30
images = {} 

def loadImages():
    pieces = ["wP","wR","wN","wB","wQ","wK","bP","bR","bN","bB","bQ","bK"]
    for piece in pieces:
        images[piece] = p.transform.scale(p.image.load("images/" + piece +".png"),(sqsize,sqsize))
        
def main():
    p.init()
    screen = p.display.set_mode((WIDTH,HEIGHT))
    clock = p.time.Clock()
    gs = ChessEngine.GameState()
    validMoves = gs.get_valid_moves()
    moveMade = False
    loadImages()
    running = True
    
    sqSelected = ()
    playerClicks = []
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
                
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos()
                col = location[0]//sqsize
                row = location[1]//sqsize
                if sqSelected == (row,col):
                    sqSelected = ()
                    playerClicks = []
                else:
                    sqSelected = (row,col)
                    playerClicks.append(sqSelected)
                    
                if len(playerClicks) == 2:
                    move = ChessEngine.Move(playerClicks[0],playerClicks[1], gs.board)
                    print(move.get_chess_not())
                    for i in range(len(validMoves)):
                        if move == validMoves[i]:
                            gs.makeMove(validMoves[i])
                            moveMade = True
                            sqSelected = ()
                            playerClicks = []
                    if not moveMade:
                        playerClicks = [sqSelected]
            
                    
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    gs.undoMove()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = True
        drawGameState(screen, gs)
        clock.tick(maxfps)
        p.display.flip()
                    
        if moveMade:
            print(gs.white_to_move, "is white")
            validMoves = gs.get_valid_moves()
            moveMade = False
            move_made = False
        if gs.check_mate:
            print("Black wins by check_mate") if gs.white_to_move else print("White wins by check_mate")
            running = False
        
        if gs.stale_mate:
            print("Draw by stale_mate")
            running = False

        # if not gs.white_to_move and len(validMoves) != 0 and not moveMade:
        #     gs.makeMove(move)
        #     moveMade = True
            

def drawGameState(screen, gs):
    drawBoard(screen)
    drawPieces(screen, gs.board)

def drawBoard(screen):
    colours = [p.Color("white"),p.Color("pink")]
    for r in range(dim):
        for c in range(dim):
            colour = colours[((r + c) % 2)]
            p.draw.rect(screen, colour, p.Rect(c*sqsize, r*sqsize, sqsize, sqsize))
            
            

def drawPieces(screen,board):
    for r in range(dim):
        for c in range(dim):
            piece = board[r][c]
            if piece != "--":
                screen.blit(images[piece], p.Rect(c*sqsize, r*sqsize, sqsize, sqsize))



if __name__ == "__main__":
    main()
