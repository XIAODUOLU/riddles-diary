import MetalCorner from './MetalCorner';

interface BookPagesProps {
  thicknessCount: number;
  depthStart: number;
}

/**
 * 封底组件
 */
export function BackCover() {
  return (
    <div className="leaf" style={{ transform: `translateZ(0px)` }}>
      <div className="face face-front tex-paper paper-edge" />
      <div className="face face-back tex-leather">
        <MetalCorner pos="tl" />
        <MetalCorner pos="bl" />
      </div>
    </div>
  );
}

/**
 * 厚度模拟页组件
 */
export function ThicknessPages({ thicknessCount, depthStart }: BookPagesProps) {
  return (
    <>
      {[...Array(thicknessCount)].map((_, i) => (
        <div 
          key={`thickness-${i}`} 
          className="leaf" 
          style={{ transform: `translateZ(${(i + 1) * depthStart}px)` }}
        >
          <div className="face face-front tex-paper paper-edge" />
        </div>
      ))}
    </>
  );
}
