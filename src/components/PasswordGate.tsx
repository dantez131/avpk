import { useState } from 'react';
import { X } from 'lucide-react';

interface PasswordGateProps {
  onSuccess: () => void;
  onClose?: () => void;
  isModal?: boolean;
  correctPassword?: string;
  title?: string;
}

export default function PasswordGate({
  onSuccess,
  onClose,
  isModal = false,
  correctPassword = '7300',
  title = 'Введите пароль',
}: PasswordGateProps) {
  const [password, setPassword] = useState('');
  const [error, setError] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (password === correctPassword) {
      onSuccess();
    } else {
      setError(true);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setPassword(e.target.value);
    setError(false);
  };

  if (isModal && onClose) {
    return (
      <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
        <div className="bg-white/10 backdrop-blur-md rounded-xl p-3 shadow-2xl border border-white/20 max-w-sm w-full relative">
          <button
            onClick={onClose}
            className="absolute top-2 right-2 text-white/60 hover:text-white transition-colors"
          >
            <X size={16} />
          </button>

          <h1 className="text-sm font-bold text-white text-center mb-2 drop-shadow-lg">
            {title}
          </h1>

          <form onSubmit={handleSubmit} className="flex flex-col gap-2">
            <input
              type="password"
              inputMode="numeric"
              pattern="[0-9]*"
              value={password}
              onChange={handleChange}
              placeholder="Inserisci il codice"
              className="px-3 py-2 bg-white/20 border-2 border-white/30 rounded-lg text-white text-center text-base font-bold placeholder-white/50 focus:outline-none focus:border-yellow-400 transition-all"
              autoFocus
            />

            <button
              type="submit"
              className="px-4 py-2 bg-gradient-to-r from-yellow-400 to-yellow-500 hover:from-yellow-500 hover:to-yellow-600 text-black text-sm font-bold rounded-lg shadow-lg transform transition-all hover:scale-105 active:scale-95"
            >
              Inviare
            </button>

            {error && (
              <p className="text-red-400 text-center text-xs font-medium animate-shake">
                La password non è corretta
              </p>
            )}
          </form>
        </div>

        <style>{`
          @keyframes shake {
            0%, 100% { transform: translateX(0); }
            10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
            20%, 40%, 60%, 80% { transform: translateX(5px); }
          }

          .animate-shake {
            animation: shake 0.5s ease-in-out;
          }
        `}</style>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-black via-red-950 to-black flex items-center justify-center overflow-hidden relative">
      <div
        className="absolute inset-0 opacity-40"
        style={{
          backgroundImage:
            'radial-gradient(circle at 20% 50%, rgba(220, 20, 60, 0.3) 0%, transparent 50%)',
        }}
      ></div>

      <div className="relative z-10 flex flex-col items-center gap-6 px-4">
        <div className="bg-white/10 backdrop-blur-md rounded-xl p-3 shadow-2xl border border-white/20 max-w-sm w-full">
          <h1 className="text-sm font-bold text-white text-center mb-2 drop-shadow-lg">
            {title}
          </h1>

          <form onSubmit={handleSubmit} className="flex flex-col gap-2">
            <input
              type="password"
              inputMode="numeric"
              pattern="[0-9]*"
              value={password}
              onChange={handleChange}
              placeholder="Inserisci la tua password"
              className="px-3 py-2 bg-white/20 border-2 border-white/30 rounded-lg text-white text-center text-base font-bold placeholder-white/50 focus:outline-none focus:border-yellow-400 transition-all"
              autoFocus
            />

            <button
              type="submit"
              className="px-4 py-2 bg-gradient-to-r from-yellow-400 to-yellow-500 hover:from-yellow-500 hover:to-yellow-600 text-black text-sm font-bold rounded-lg shadow-lg transform transition-all hover:scale-105 active:scale-95"
            >
              Inviare
            </button>

            {error && (
              <p className="text-red-400 text-center text-xs font-medium animate-shake">
                La password non è corretta
              </p>
            )}
          </form>
        </div>
      </div>

      <style>{`
        @keyframes shake {
          0%, 100% { transform: translateX(0); }
          10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
          20%, 40%, 60%, 80% { transform: translateX(5px); }
        }

        .animate-shake {
          animation: shake 0.5s ease-in-out;
        }
      `}</style>
    </div>
  );
}
