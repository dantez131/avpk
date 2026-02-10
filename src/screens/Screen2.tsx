import { useState } from 'react';
import FlyingPlane from '../components/FlyingPlane';
import FallingPixels from '../components/FallingPixels';

interface Screen2Props {
  onPrecisionUpgradeClick: () => void;
}

export default function Screen2({ onPrecisionUpgradeClick }: Screen2Props) {
  const [multiplier, setMultiplier] = useState<number | null>(null);
  const [history, setHistory] = useState<number[]>([]);
  const [animationKey, setAnimationKey] = useState(0);

  const generateMultiplier = () => {
    const random = 1.01 + Math.random() * (12.01 - 1.01);
    const newMultiplier = Number(random.toFixed(2));
    setMultiplier(newMultiplier);
    setAnimationKey((prev) => prev + 1);
    setHistory((prev) => [newMultiplier, ...prev.slice(0, 19)]);
  };

  return (
    <div className="h-screen bg-gradient-to-br from-black via-red-950 to-black flex flex-col overflow-hidden relative">
      <div
        className="absolute inset-0 opacity-40"
        style={{
          backgroundImage:
            'radial-gradient(circle at 20% 50%, rgba(220, 20, 60, 0.3) 0%, transparent 50%)',
        }}
      ></div>

      <FlyingPlane />
      <FallingPixels />

      {history.length > 0 && (
        <div className="absolute top-2 left-0 right-0 z-20 flex justify-center px-2">
          <div className="text-center">
            <p className="text-xs font-light text-white/70 mb-1 tracking-wide">
               
            </p>
            <div className="flex flex-wrap gap-1 justify-center max-w-sm">
              {history.map((value, idx) => (
                <span key={idx} className="text-xs text-white/60 font-light">
                  {value.toFixed(2)}x{idx < history.length - 1 ? ',' : ''}
                </span>
              ))}
            </div>
          </div>
        </div>
      )}

      <div className="relative z-10 flex-1 flex flex-col items-center justify-center px-4">
        <div className="flex flex-col items-center justify-center">
          {multiplier && (
            <div key={animationKey} className="animate-scale-in">
              <div className="text-6xl font-bold text-white drop-shadow-2xl">
                {multiplier.toFixed(2)}x
              </div>
            </div>
          )}

          <button
            onClick={generateMultiplier}
            className="mt-8 px-8 py-2 bg-gradient-to-r from-yellow-400 to-yellow-500 hover:from-yellow-500 hover:to-yellow-600 text-black text-lg font-bold rounded-2xl shadow-2xl transform transition-all hover:scale-105 active:scale-95"
          >
            MOSTRA COEFFICIENTE
          </button>
        </div>
      </div>

      <div className="z-20 flex flex-col items-center gap-2 px-2 pb-3">
        <div className="bg-white/10 backdrop-blur-md rounded-xl p-2 shadow-2xl border border-white/20 w-full max-w-sm">
          <div className="text-center">
            <p className="text-white/90 text-xs font-light leading-tight mb-2">
              Il bot è connesso e pronto a funzionare. Sincronizzazione attuale dei coefficienti - 45%. Per una sincronizzazione al 100%, immettere una password aggiuntiva
            </p>
            <button
              onClick={onPrecisionUpgradeClick}
              className="w-full px-3 py-1 bg-gradient-to-r from-blue-400 to-blue-500 hover:from-blue-500 hover:to-blue-600 text-black font-bold rounded-lg shadow-lg transform transition-all hover:scale-105 active:scale-95 text-xs"
            >
              Aumenta la precisione al 100%
            </button>
          </div>
        </div>

        <div className="bg-white/10 backdrop-blur-md rounded-xl p-2 shadow-2xl border border-white/20 w-full max-w-sm">
          <p className="text-center text-white/70 text-xs font-light">
            Se hai qualche domanda -{' '}
            <a
              href="https://t.me/Dante_Valdes?text=Ciao!%20Ho%20una%20domanda%20sul%20bot"
              target="_blank"
              rel="noopener noreferrer"
              className="text-yellow-400 hover:text-yellow-500 transition-colors"
            >
              @Dante_Valdes
            </a>
          </p>
        </div>
      </div>

      <style>{`
        @keyframes scale-in {
          0% {
            transform: scale(0.7);
            opacity: 0;
          }
          50% {
            transform: scale(1.1);
          }
          100% {
            transform: scale(1);
            opacity: 1;
          }
        }

        .animate-scale-in {
          animation: scale-in 0.5s ease-out;
        }
      `}</style>
    </div>
  );
}
