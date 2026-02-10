import { useEffect, useState } from 'react';

interface Pixel {
  id: number;
  left: number;
  animationDuration: number;
  delay: number;
  size: number;
}

export default function FallingPixels() {
  const [pixels, setPixels] = useState<Pixel[]>([]);

  useEffect(() => {
    const pixelArray: Pixel[] = Array.from({ length: 30 }, (_, i) => ({
      id: i,
      left: Math.random() * 100,
      animationDuration: 3 + Math.random() * 4,
      delay: Math.random() * 5,
      size: 2 + Math.random() * 2,
    }));
    setPixels(pixelArray);
  }, []);

  return (
    <div className="fixed inset-0 pointer-events-none overflow-hidden">
      {pixels.map((pixel) => (
        <div
          key={pixel.id}
          className="absolute bg-white/30"
          style={{
            left: `${pixel.left}%`,
            width: `${pixel.size}px`,
            height: `${pixel.size}px`,
            animation: `fall ${pixel.animationDuration}s linear ${pixel.delay}s infinite`,
          }}
        />
      ))}
      <style>{`
        @keyframes fall {
          0% {
            transform: translateY(-10vh) rotate(0deg);
            opacity: 0;
          }
          10% {
            opacity: 1;
          }
          90% {
            opacity: 1;
          }
          100% {
            transform: translateY(110vh) rotate(360deg);
            opacity: 0;
          }
        }
      `}</style>
    </div>
  );
}
