"use client";

import { useState, useEffect } from "react";
import constants from '../../../config/constants.json';


export default function Home() {
  const [gameStarted, setGameStarted] = useState(false);
  const [scaleFactor, setScaleFactor] = useState(1);

  //setting initial starting position. These values shouldn't be hardcoded here. 
  //TODO get them from constants.json
  const [gameState, setGameState] = useState({
  ball: { x: 33, y: 25 },
  agentPaddle: { y: 19 },
  humanPaddle: { y: 19 },
  score: { agent: 0, human: 0 },
});


  const startGame = () => {
    setGameStarted(true);

    // TEMPORARY fake state — placeholder so the render doesn't crash before the
    // socket delivers real data. DELETE THIS once you render from `state` below.
    
    // ====================================================================
    // THIS IS WHERE THE GAME STATE COMES IN.
    // The backend runs the authoritative Pong sim and pushes one snapshot
    // per tick over this WebSocket. Full contract: docs/websocket-protocol.md
    //
    // Each message (JSON) looks like:
    //   {
    //     "type": "state",
    //     "tick": 189,                       // sim step counter (monotonic)
    //     "ball":  { "x": 60.0, "y": 52.0 }, // game units, NOT pixels
    //     "agent_pos": 45.0,                 // agent paddle y  (left  side)
    //     "human_pos": 45.0,                 // human paddle y  (right side)
    //     "score": { "agent": 0, "human": 0 },
    //     "game_over": false
    //   }
    //
    // Coordinates are in game units (board = constants.GAME_WIDTH x
    // GAME_HEIGHT). Multiply by scaleFactor to get pixels, same as the
    // existing render code does.
    //
    // TODO (frontend): replace the fake state above with this. Roughly:
    //   ws.onmessage = (e) => {
    //     const s = JSON.parse(e.data);
    //     setGameState({
    //       ball: s.ball,
    //       agentPaddle: { y: s.agent_pos },   // map agent -> left paddle
    //       humanPaddle:   { y: s.human_pos },   // map human -> right paddle
    //       score: { agent: s.score.agent, human: s.score.human },
    //     });
    //     if (s.game_over) { /* show win/lose screen */ }
    //   };
    // (Send human paddle input back with: ws.send(JSON.stringify({
    //   type: "input", input_seq: n, dir: -1|0|1 })) — not wired yet.)
    // ====================================================================
    const ws = new WebSocket("ws://localhost:8000/ws/test");
    ws.onmessage = (e) => {
      const s = JSON.parse(e.data);
      if (s.type !== "state") return;
      setGameState({
        ball: s.ball,
        agentPaddle: { y: s.agent_pos },
        humanPaddle: { y: s.human_pos },
        score: { agent: s.score.agent, human: s.score.human },
      });
      if (s.game_over) { /* TODO win/lose screen */ }
    };
    ws.onerror = (e) => console.log("ws error:", e);
  };
  

  useEffect(() => {
    const calculateScale = () => {
      const availableWidth = window.innerWidth-constants.UI_HORIZONTAL_PADDING; // Account for UI elements
      const availableHeight = window.innerHeight -constants.UI_VERTICAL_PADDING; // Account for UI elements

      const widthScale = Math.floor(availableWidth / constants.GAME_WIDTH);
      const heightScale = Math.floor(availableHeight / constants.GAME_HEIGHT);
      
      // Use the smaller scale, but ensure at least 1x
      setScaleFactor(Math.max(Math.min(widthScale, heightScale), 1));
      
       };

    calculateScale();
    window.addEventListener('resize', calculateScale);
    
    return () => window.removeEventListener('resize', calculateScale);
  }, [constants.GAME_WIDTH, constants.GAME_HEIGHT]);

  // Calculate actual pixel dimensions
  const displayWidth = constants.GAME_WIDTH * scaleFactor;
  const displayHeight = constants.GAME_HEIGHT * scaleFactor;

   return (
    <div
      className={`flex min-h-screen ${!gameStarted ? 'items-center justify-center' : ''}`}
      style={{ backgroundColor: constants.PAGE_BACKGROUND_COLOR }}
    >
      <main
        className={`flex min-h-screen w-full flex-col items-center px-16 ${!gameStarted ? 'justify-center' : 'justify-start pt-8'}`}
        style={{ backgroundColor: constants.PAGE_BACKGROUND_COLOR }}
      > 
        {!gameStarted ? (
          // Welcome Screen (disappears when button is clicked)
          <div className="flex flex-col items-center gap-8 text-center">
            <h1 className={`text-6xl font-bold tracking-wider font-mono`}
            style={{color: constants.TEXT_COLOR}}>
              Welcome to the pong game
            </h1>
            <button 
              onClick={startGame}
              className={`px-12 py-4 font-bold text-2xl rounded-lg mt-8 transition-all duration-200 font-mono`}
              style={{backgroundColor: constants.TEXT_COLOR, color: constants.PAGE_BACKGROUND_COLOR}}
            >
              PLAY
            </button>
          </div>
        ) : (
         // Game Screen
          <div className="flex flex-col items-center justify-center w-full">
            {/* Score at the top */}
            <div className="py-4 text-center w-full">
              <h2 
              className={`text-6xl font-bold font-mono`}
              style={{color: constants.TEXT_COLOR}}>
                {gameState.score.agent} : {gameState.score.human}
              </h2>
            </div>
            
           {/* Game view using constants.GAME_WIDTH and constants.GAME_HEIGHT */}
<div 
  className={`relative`} 
  style={{ 
    width: `${displayWidth}px`, 
    height: `${displayHeight}px`, 
    imageRendering: 'pixelated',
    backgroundColor: constants.GAME_BACKGROUND_COLOR,
  }}
>

{/* Center line - dashed */}
  {Array.from({ length: constants.GAME_HEIGHT}).map((_, i) => (
    i % 2 === 0 && (
      <div
        key={i}
        className={`absolute`}
        style={{
          left: `${(constants.GAME_WIDTH / 2) * scaleFactor - scaleFactor/2}px`,
          top: `${i * scaleFactor}px`,
          width: `${scaleFactor}px`,
          height: `${scaleFactor}px`,
          backgroundColor: constants.TEXT_COLOR,
        }}
      />
    )
  ))}

   {/* Left paddle */}
  <div
    className={`absolute`}
    style={{
      left: `${constants.PADDLE_OFFSET * scaleFactor}px`,
      top: `${gameState.humanPaddle.y * scaleFactor}px`,
      width: `${constants.PADDLE_WIDTH * scaleFactor}px`,
      height: `${constants.PADDLE_HEIGHT * scaleFactor}px`,
      backgroundColor: constants.TEXT_COLOR,
    }}
  />
  
  {/* Right paddle */}
  <div
    className={`absolute`}
    style={{
      right: `${constants.PADDLE_OFFSET * scaleFactor}px`,
      top: `${gameState.agentPaddle.y * scaleFactor}px`,
      width: `${constants.PADDLE_WIDTH * scaleFactor}px`,
      height: `${constants.PADDLE_HEIGHT * scaleFactor}px`,
      backgroundColor: constants.TEXT_COLOR,
    }}
  />
  
  {/* Ball */}
  <div
    className={`absolute`}
    style={{
      left: `${gameState.ball.x * scaleFactor - scaleFactor/2}px`,
      top: `${gameState.ball.y * scaleFactor}px`,
      width: `${constants.BALL_SIZE * scaleFactor}px`,
      height: `${constants.BALL_SIZE * scaleFactor}px`,
      backgroundColor: constants.TEXT_COLOR,
    }}
  />
</div>          </div>
        )}
      </main>
    </div>
  );
}
