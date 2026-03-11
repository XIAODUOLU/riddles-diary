interface AccioButtonProps {
  onClick: () => void;
}

export default function AccioButton({ onClick }: AccioButtonProps) {
  return (
    <div className="fixed inset-0 flex items-center justify-center z-50 pointer-events-none" style={{ paddingTop: '64vh', paddingLeft: "1vw" }}>
      <button
        onClick={onClick}
        className="pointer-events-auto group relative px-8 py-4 bg-black/20 backdrop-blur-sm border-2 border-[#8a733e]/40 rounded-lg hover:border-[#e2d1b5]/60 transition-all duration-300 hover:scale-105 hover:shadow-[0_0_30px_rgba(138,115,62,0.3)]"
      >
        <div className="font-handwriting text-3xl text-[#8a733e] group-hover:text-[#e2d1b5] transition-colors duration-300 tracking-wide">
          Accio Horcrux!
        </div>
        <div className="absolute -top-2 -right-2 text-2xl animate-pulse">✨</div>
        <div className="absolute -bottom-2 -left-2 text-2xl animate-pulse delay-300">⚡</div>
      </button>
    </div>
  );
}
