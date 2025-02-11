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
STOCKFISH_PATH = os.path.join(BASE_DIR, "stockfish", "stockfish-windows-x86-64-avx2.exe")
os.chmod(STOCKFISH_PATH, 0o755)  # Nastaví spustitelná práva

print(f"🔍 Pokouším se spustit Stockfish na cestě: {STOCKFISH_PATH}")

try:
    # ✅ Spustíme Stockfish jako subprocess
    stockfish = subprocess.Popen(
        STOCKFISH_PATH,
        universal_newlines=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    print("✅ Stockfish spuštěn správně!")
except Exception as e:
    import traceback
    print(f"❌ Chyba při spouštění Stockfish:\n{traceback.format_exc()}")
    stockfish = None  # Pokud Stockfish nefunguje, nastavíme None

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
        return {"player_move": move_request.move, "ai_move": ai_move.uci(), "fen": board.fen()}

    return {"player_move": move_request.move, "message": "AI nemá tah - hra skončila", "fen": board.fen()}

def get_ai_move():
    """Použije Stockfish pro výpočet nejlepšího tahu."""
    if stockfish is None:
        print("❌ Stockfish neběží!")
        return None  # Pokud Stockfish neběží, vrátíme None

    try:
        fen = board.fen()
        print(f"📜 Posílám FEN do Stockfish: {fen}")

        stockfish.stdin.write(f"position fen {fen}\n")
        stockfish.stdin.write("go depth 10\n")
        stockfish.stdin.flush()

        while True:
            output = stockfish.stdout.readline().strip()
            print(f"🔄 Stockfish odpověď: {output}")

            if output.startswith("bestmove"):
                best_move = output.split(" ")[1]
                print(f"✅ Nejlepší tah AI: {best_move}")
                return chess.Move.from_uci(best_move)

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
