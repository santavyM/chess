from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import chess
import os
import chess.engine
import subprocess

# ✅ Inicializace FastAPI
app = FastAPI()

# ✅ Povolení CORS pro frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STOCKFISH_PATH = os.path.join(BASE_DIR, "stockfish3", "stockfish-ubuntu-x86-64")
os.chmod(STOCKFISH_PATH, 0o755)  # Nastaví spustitelná práva

print(f"🔍 Pokouším se spustit Stockfish na cestě: {STOCKFISH_PATH}")

try:
    engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
    print("✅ Stockfish spuštěn správně!")
except Exception as e:
    print(f"❌ Chyba při spouštění Stockfish:\n{e}")
    engine = None  # Pokud Stockfish nefunguje, nastavíme None


# ✅ Inicializace šachovnice
board = chess.Board()

# ✅ Model pro tahy
class MoveRequest(BaseModel):
    move: str

@app.get("/")
def welcome():
    return {"message": "Vítej v šachové API! Pošli tah na /move a AI odpoví."}

@app.post("/move")
def player_move(move_request: MoveRequest):
    global board

    try:
        move = chess.Move.from_uci(move_request.move)
        if move not in board.legal_moves:
            return {"error": "Neplatný tah", "fen": board.fen()}
        board.push(move)
    except Exception as e:
        return {"error": f"Chybný tah: {str(e)}", "fen": board.fen()}

    if board.is_game_over():
        return {"player_move": move_request.move, "message": "Hra skončila!", "fen": board.fen()}

    ai_move = get_ai_move()
    if ai_move:
        board.push(ai_move)
    else:
        return {"player_move": move_request.move, "message": "AI nemá tah - hra skončila", "fen": board.fen()}

    return {"player_move": move_request.move, "ai_move": ai_move.uci(), "fen": board.fen()}


def get_ai_move():
    """Použije Stockfish pro výpočet nejlepšího tahu."""
    if engine is None:
        print("❌ Stockfish neběží!")
        return None  # Pokud Stockfish neběží, vrátíme None

    try:
        print(f"📜 Posílám FEN do Stockfish: {board.fen()}")
        result = engine.play(board, chess.engine.Limit(time=0.5))  # AI přemýšlí 0.5 sekundy
        ai_move = result.move
        print(f"✅ Nejlepší tah AI: {ai_move}")
        return ai_move

    except Exception as e:
        print(f"❌ Chyba při komunikaci se Stockfish: {e}")
        return None



@app.post("/reset")
def reset_game():
    """Resetuje celou šachovnici na začátek."""
    global board
    board = chess.Board()
    print("♻️ Hra byla restartována!")
    return {"message": "Hra restartována!"}

import uvicorn

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)

import atexit

@atexit.register
def close_stockfish():
    if engine:
        print("🔴 Zavírám Stockfish...")
        engine.quit()

