import MetalCorner from './MetalCorner';

interface BookCoverProps {
  isOpen: boolean;
  onOpen: () => void;
  onClose: () => void;
}

export default function BookCover({ isOpen, onOpen, onClose }: BookCoverProps) {
  return (
    <div 
      className="leaf" 
      style={{ 
        transform: `rotateY(${isOpen ? -180 : 0}deg) translateZ(15px)`,
        zIndex: 100
      }}
    >
      {/* 外封面 */}
      <div className="face face-front tex-leather cursor-pointer group" onClick={onOpen}>
        <MetalCorner pos="tr" />
        <MetalCorner pos="br" />
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="border border-[#111] p-6 w-[80%] h-[85%] flex items-center justify-center">
            <h1 
              className="text-3xl opacity-40 text-black text-center font-handwriting"
              style={{ textShadow: '-1px -1px 1px rgba(255,255,255,0.1), 1px 1px 3px rgba(0,0,0,0.9)' }}
            >
              T. M. Riddle
            </h1>
          </div>
        </div>
        {!isOpen && (
          <div className="absolute bottom-12 w-full flex justify-center opacity-0 group-hover:opacity-60 transition-opacity">
            <span className="font-chinese-handwriting text-[#8a733e] text-sm">点击开启</span>
          </div>
        )}
      </div>
      
      {/* 内封面 */}
      <div className="face face-back tex-paper cursor-pointer" onClick={onClose}>
        <div className="spine-joint-left" />
        <div className="absolute inset-0 bg-black/10" />
        <div className="absolute inset-10 border border-black/5" />
        
        {/* 魔法装饰内容 */}
        <div className="absolute inset-0 flex flex-col items-center justify-center p-12 text-black/30 pointer-events-none">
          <div className="text-4xl mb-8 tracking-widest">☽ ✦ ☾</div>
          <div className="font-handwriting text-3xl mb-6 opacity-60 italic">
            Memories Preserved
          </div>
          <div className="text-2xl mb-8">⚡ ✧</div>
          <div className="font-handwriting text-lg opacity-40 mb-3">
            Diary Owner
          </div>
          <div className="font-handwriting text-2xl opacity-50 mb-8">
            Tom Marvolo Riddle
          </div>
          <div className="font-handwriting text-base opacity-30">
            Est. 1943
          </div>
        </div>
      </div>
    </div>
  );
}
