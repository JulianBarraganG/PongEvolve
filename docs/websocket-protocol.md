# PongEvolve — Client/Server Wire Protocol (v0.1)

The contract the frontend and backend build against. Server-authoritative,
realtime, over a WebSocket. Status tags: **[live]** implemented, **[planned]**
agreed but not built, **[later]** deliberately deferred.

## Invariants (don't break these)

1. **Server owns the truth.** The sim runs server-side; the client sends *intent*
   (a direction), never positions. Required for anti-cheat + the server-side RL agent.
2. **Sim rate is fixed**, decoupled from send rate. Physics must not depend on
   machine speed. `SIM_HZ = 60`. (`SNAPSHOT_HZ` may be lower later; today = `SIM_HZ`.)
3. **Every snapshot carries a monotonic `tick`** — the ordering hook smoothing needs.
4. **Every input carries a monotonic `input_seq`**, echoed back — the hook
   client-prediction/reconciliation needs.

Get these right now; the latency layer (§ Later) bolts on without a rewrite.

## Transport & units

- One **WebSocket** per game: `GET /ws/{gameid}`. JSON text frames; every message
  has a `type` field. **[live]**
- All values in **game units** (board = `GAME_WIDTH × GAME_HEIGHT` = `120 × 90`),
  never pixels. Origin top-left, `x` right, `y` down. Client scales to pixels.
- Optional REST warm-up `POST /game → {gameid}` to mint an id. **[later]**

## Server → Client

### `state` — one per tick **[live]**
```json
{
  "type": "state",
  "tick": 189,
  "ball":  { "x": 60.0, "y": 52.0 },
  "agent_pos": 45.0,
  "human_pos": 45.0,
  "score": { "agent": 0, "human": 0 },
  "game_over": false
}
```
- Paddles are named by **role** (`agent_pos`, `human_pos`), each a `y` position — never
  positional `p1/p2`, so wire order can't be gotten wrong. Score likewise a named map.
- **Position-only ball.** No velocity: the server sends every tick, so the client
  has no gaps to fill. `vx/vy` return only with extrapolation (§ Later).
- `game_over: true` marks the terminal snapshot; the server then closes the socket.

### `game_created` — once on connect **[planned]**
Static setup the client needs up front: `gameid`, the relevant `config` (board dims,
paddle/ball sizes from `config/constants.json`), and which side this client is.

## Client → Server

### `input` — on change, sequenced **[planned]**
```json
{ "type": "input", "input_seq": 88, "dir": -1 }
```
`dir ∈ {-1, 0, 1}` (up/none/down) → `Pong.move_paddle(human=True, dir)`. Server
applies it and echoes the last-applied seq (add `ack_input_seq` to `state` then).

### `leave` — graceful disconnect **[later]**

## Serializer boundary

`pong/game.py` stays pure (no JSON). One adapter, `serialize()` in `app/main.py`,
maps the live `Pong` → the `GameState` model in `pong/game_state.py` (the single
source of truth for the wire shape). Cast numpy scalars to Python `float`/`int` or
`json` can't serialize them.

## Open decisions / known bugs

- **Side mapping unresolved.** Frontend renders `machinePaddle` left / `humanPaddle`
  right; `game.py` puts `human` at `paddle_offset` (left). Pick one canonical mapping
  and make both ends obey. Role-named fields mean this is now purely a *render* choice.
- **Bug `game.py`: agent x uses `game_height`** (90) instead of `game_width` (120),
  so the agent paddle sits at x≈86 on a 120-wide board, not at the edge. Fix.

## Later (deferred by design — the invariants above enable each)

- Client-side prediction of the human paddle + server reconciliation.
- Ball extrapolation (re-adds `vx/vy`) / entity interpolation of the agent paddle.
- The real RL agent (today: a stub that tracks the ball / moves blindly).
- Multiple concurrent games, per-connection cleanup, persistence, auth, `wss`.

**Don't build smoothing against imagined latency.** Ship the loop, measure real
jitter (localhost ≈ 0), add only what the numbers demand.

## Build order

1. ✅ WebSocket echo — pipe proven.
2. ✅ Server tick loop → `state` snapshots; agent stubbed.
3. ▶ Frontend renders from `state` (drop the fake state); resolve the side mapping.
4. Input handling — human paddle moves (introduces send/receive concurrency).
5. Work through the deferred list as real needs appear.
</content>
