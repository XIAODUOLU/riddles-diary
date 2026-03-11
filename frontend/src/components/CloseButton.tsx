interface CloseButtonProps {
  isVisible: boolean;
  onClick: () => void;
}

export default function CloseButton({ isVisible, onClick }: CloseButtonProps) {
  return (
    <div 
      className={`fixed top-6 right-6 z-50 transition-all duration-1000 ${
        isVisible ? 'opacity-100 translate-y-0 cursor-pointer' : 'opacity-0 -translate-y-4 pointer-events-none'
      }`}
      onClick={onClick}
    >
      <div className="font-chinese-handwriting text-[#8a733e] hover:text-[#e2d1b5] text-base flex items-center gap-3">
        <span>合上日记</span>
        <span className="text-xl">✕</span>
      </div>
    </div>
  );
}
