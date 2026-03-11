import { CornerPosition } from '../types';

interface MetalCornerProps {
  pos: CornerPosition;
}

const MetalCorner = ({ pos }: MetalCornerProps) => {
  const positions = {
    'tl': 'top-0 left-0 rounded-br-xl',
    'tr': 'top-0 right-0 rounded-bl-xl',
    'bl': 'bottom-0 left-0 rounded-tr-xl',
    'br': 'bottom-0 right-0 rounded-tl-xl',
  };

  return (
    <div className={`absolute w-10 h-10 bg-gradient-to-br from-[#8a733e] via-[#5a4822] to-[#2a200a] border border-[#1a1405] shadow-sm opacity-90 ${positions[pos]}`}>
      <div className="absolute inset-1 border border-[#3a2d15] rounded-sm opacity-50" />
      <div className="absolute top-1/2 left-1/2 w-1.5 h-1.5 bg-[#1a1405] rounded-full transform -translate-x-1/2 -translate-y-1/2" />
    </div>
  );
};

export default MetalCorner;
