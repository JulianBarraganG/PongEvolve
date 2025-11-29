"use client";

import { useState, useEffect } from "react";
import constants from '../../../config/constants.json';


export default function Home() {
  const [gameStarted, setGameStarted] = useState(false);
  const [scaleFactor, setScaleFactor] = useState(1);
  const [gameState, setGameState] = useState({});


  const startGame = () => {
    setGameStarted(true);
    //Call the backend API to get start position of the ball and paddles 
    //Let's simulate this for now
    //These numbers are just for testing
    const setGameStateWithStartPosition = () => {
      setGameState({
        ...gameState,
        ball: {
          x: 33,
          y: 25,
        },
        machinePaddle: {
          y: 19,
        },
        humanPaddle: {
          y: 19,
        },
        score: {
          machine: 0,
          human: 0,
        },
      });
    };
    setGameStateWithStartPosition();
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
                {gameState.score.machine} : {gameState.score.human}
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
      top: `${gameState.machinePaddle.y * scaleFactor}px`,
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
      top: `${gameState.humanPaddle.y * scaleFactor}px`,
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
