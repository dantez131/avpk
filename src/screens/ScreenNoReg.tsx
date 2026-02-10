import FlyingPlane from '../components/FlyingPlane';
import FallingPixels from '../components/FallingPixels';

export default function ScreenNoReg() {
  const generateMultiplier = () => {

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

      <div className="relative z-10 flex-1 flex flex-col items-center justify-center px-4">
        <div className="flex flex-col items-center justify-center gap-6">
          <div className="bg-white/10 backdrop-blur-md rounded-xl p-4 shadow-2xl border border-white/20 w-full max-w-sm">
            <div className="text-center">
              <p className="text-white/90 text-sm font-light leading-tight">
                Bot not connected: Complete new account registration
              </p>
            </div>
          </div>

          <button
            onClick={generateMultiplier}
            className="px-8 py-2 bg-gradient-to-r from-yellow-400 to-yellow-500 hover:from-yellow-500 hover:to-yellow-600 text-black text-lg font-bold rounded-2xl shadow-2xl transform transition-all hover:scale-105 active:scale-95"
          >
            GET COEFFICIENT
          </button>
        </div>
      </div>

      <div className="z-20 flex flex-col items-center gap-2 px-2 pb-3">
        <div className="bg-white/10 backdrop-blur-md rounded-xl p-2 shadow-2xl border border-white/20 w-full max-w-sm">
          <p className="text-center text-white/70 text-xs font-light">
            Need help? Write to me -{' '}
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
