import { useState, useEffect, useRef } from 'react';
import { Message } from '../types';
import MetalCorner from './MetalCorner';
import '../styles/diary.css';

export default function TomRiddleDiary() {
  const [page, setPage] = useState(0); // 0 = 闭合, 1 = 翻开
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState("");
  const [isLocked, setIsLocked] = useState(false); // 锁定输入，等待汤姆回复
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const hasOpened = useRef(false);

  // 初始交互：汤姆的问候
  useEffect(() => {
    if (page === 1 && !hasOpened.current) {
      hasOpened.current = true;
      setIsLocked(true);
      setTimeout(() => {
        triggerTomTyping("给我写点什么...", Date.now(), () => {
          setIsLocked(false);
          setTimeout(() => inputRef.current?.focus(), 100);
        });
      }, 1500);
    }
  }, [page]);

  const triggerTomTyping = (text: string, id: number, onComplete?: () => void) => {
    setMessages(prev => [...prev, { id, text, sender: 'tom', status: 'typing', displayedText: '' }]);
    
    let i = 0;
    const interval = setInterval(() => {
      i++;
      setMessages(prev => prev.map(m => m.id === id ? { ...m, displayedText: text.slice(0, i) } : m));
      
      if (i >= text.length) {
        clearInterval(interval);
        setTimeout(() => {
          // 开始渗入纸张消失的过程
          setMessages(prev => prev.map(m => m.id === id ? { ...m, status: 'fading' } : m));
          setTimeout(() => {
            setMessages(prev => prev.map(m => m.id === id ? { ...m, status: 'gone' } : m));
            if (onComplete) onComplete();
          }, 3000); // 延长的吸收动画
        }, 2000); 
      }
    }, 80);
  };

  const generateTomReply = (userText: string) => {
    let reply = "我可以给你展示一些东西...";
    const lower = userText.toLowerCase();
    
    if (lower.includes("hello") || lower.includes("hi") || lower.includes("你好")) {
      reply = "你好... 我是汤姆·里德尔。";
    } else if (lower.includes("who") || lower.includes("谁")) {
      reply = "我是一段记忆，在日记里保存了五十年。";
    } else if (lower.includes("chamber") || lower.includes("secret") || lower.includes("密室")) {
      reply = "密室以前就被打开过。";
    } else if (lower.includes("voldemort") || lower.includes("dark lord") || lower.includes("伏地魔") || lower.includes("黑魔王")) {
      reply = "伏地魔是我的过去、现在和未来。";
    } else if (lower.includes("harry") || lower.includes("potter") || lower.includes("哈利") || lower.includes("波特")) {
      reply = "哈利·波特... 我们终于见面了。";
    } else if (lower.includes("magic") || lower.includes("魔法")) {
      reply = "我可以教你超越梦想的魔法。";
    } else if (lower.includes("help") || lower.includes("帮助")) {
      reply = "如果你愿意，我可以帮你。";
    } else if (lower.includes("dumbledore") || lower.includes("邓布利多")) {
      reply = "邓布利多... 一个愚蠢的老头。";
    } else if (lower.includes("horcrux") || lower.includes("魂器")) {
      reply = "你正踏入危险的领域。";
    }

    triggerTomTyping(reply, Date.now(), () => {
      setIsLocked(false);
      setTimeout(() => inputRef.current?.focus(), 100);
    });
  };

  const handleUserSubmit = (text: string) => {
    if (isLocked) return;
    setIsLocked(true);
    inputRef.current?.blur();

    const id = Date.now();
    setMessages(prev => [...prev, { id, text, sender: 'user', status: 'visible' }]);
    setInputValue("");

    setTimeout(() => {
      setMessages(prev => prev.map(m => m.id === id ? { ...m, status: 'fading' } : m));
      setTimeout(() => {
        setMessages(prev => prev.map(m => m.id === id ? { ...m, status: 'gone' } : m));
        generateTomReply(text);
      }, 2500); 
    }, 1500);
  };

  return (
    <div className="diary-environment">
      
      {/* 关闭按钮 */}
      <div 
        className={`fixed top-6 right-6 z-50 transition-all duration-1000 ${page === 1 ? 'opacity-100 translate-y-0 cursor-pointer' : 'opacity-0 -translate-y-4 pointer-events-none'}`}
        onClick={() => setPage(0)}
      >
        <div className="text-[#8a733e] hover:text-[#e2d1b5] text-sm tracking-[0.3em] uppercase flex items-center gap-3">
          <span>合上日记</span>
          <span className="text-xl">✕</span>
        </div>
      </div>

      <div className={`book ${page === 1 ? 'open' : ''}`}>
        <div className="book-shadow" />

        {/* --- 右侧堆叠（未翻动的书页和封底） --- */}
        
        {/* 封底层 */}
        <div className="leaf" style={{ transform: `translateZ(0px)` }}>
          <div className="face face-front tex-paper paper-edge" />
          <div className="face face-back tex-leather">
            <MetalCorner pos="tl" />
            <MetalCorner pos="bl" />
          </div>
        </div>

        {/* 右侧厚度模拟页 */}
        {[...Array(3)].map((_, i) => (
          <div key={`r-${i}`} className="leaf" style={{ transform: `translateZ(${(i + 1) * 1.5}px)` }}>
            <div className="face face-front tex-paper paper-edge" />
          </div>
        ))}

        {/* 交互主页 (右页) */}
        <div className="leaf" style={{ transform: `translateZ(6px)` }}>
          <div className="face face-front tex-paper paper-edge" onClick={() => !isLocked && inputRef.current?.focus()}>
            <div className="spine-joint-right" />
            <div className={`magic-glow ${messages.some(m => m.sender === 'tom' && m.status !== 'gone') ? 'opacity-100' : 'opacity-0'}`} />
            
            <div className="absolute inset-0 p-10 pt-16 overflow-hidden flex flex-col justify-start">
              {messages.filter(m => m.status !== 'gone').map(m => (
                <div 
                  key={m.id} 
                  className={`font-handwriting ink-text mb-5 w-full ${m.status === 'fading' ? 'ink-fading' : ''} ${m.sender === 'tom' ? 'text-center italic' : 'text-left pl-5 border-l border-black/5'}`}
                >
                  {m.sender === 'tom' ? m.displayedText : m.text}
                </div>
              ))}

              <div className="font-handwriting ink-text text-left pl-5 border-l border-black/10 flex flex-wrap relative z-10 min-h-[2.5rem]">
                {inputValue}
                {!isLocked && <span className="animate-pulse ml-1 opacity-60">|</span>}
              </div>

              <textarea
                ref={inputRef}
                className="absolute inset-0 w-full h-full opacity-0 cursor-text resize-none p-12 focus:outline-none z-20"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    if (inputValue.trim() && !isLocked) handleUserSubmit(inputValue);
                  }
                }}
                spellCheck={false}
                disabled={page === 0 || isLocked}
              />
            </div>
          </div>
        </div>

        {/* --- 左侧堆叠（翻转后的书页和封面） --- */}

        {/* 左侧厚度模拟页 - 翻开后在最下层 */}
        {[...Array(3)].map((_, i) => (
          <div key={`l-${i}`} className="leaf" 
               style={{ 
                 transform: `rotateY(${page === 1 ? -176 - i : 0}deg) translateZ(${(i + 7) * 1.5}px)`,
                 zIndex: 10 + i 
               }}>
            <div className="face face-front tex-paper paper-edge" />
            <div className="face face-back tex-paper">
               <div className="spine-joint-left" />
            </div>
          </div>
        ))}

        {/* 封面层 (最顶层) */}
        <div className={`leaf`} 
             style={{ 
               transform: `rotateY(${page === 1 ? -180 : 0}deg) translateZ(15px)`,
               zIndex: 100
             }}>
          
          {/* 外封面 */}
          <div className="face face-front tex-leather cursor-pointer group" onClick={() => setPage(1)}>
            <MetalCorner pos="tr" />
            <MetalCorner pos="br" />
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="border border-[#111] p-6 w-[80%] h-[85%] flex items-center justify-center">
                <h1 
                  className="text-2xl tracking-[0.4em] uppercase opacity-40 text-black text-center"
                  style={{ textShadow: '-1px -1px 1px rgba(255,255,255,0.1), 1px 1px 3px rgba(0,0,0,0.9)' }}
                >
                  T. M. Riddle
                </h1>
              </div>
            </div>
            {page === 0 && (
              <div className="absolute bottom-12 w-full flex justify-center opacity-0 group-hover:opacity-60 transition-opacity">
                <span className="text-[#8a733e] text-xs tracking-[0.5em] uppercase">点击开启</span>
              </div>
            )}
          </div>
          
          {/* 内封面 */}
          <div className="face face-back tex-paper cursor-pointer" onClick={() => setPage(0)}>
             <div className="spine-joint-left" />
             <div className="absolute inset-0 bg-black/10" />
             <div className="absolute inset-10 border border-black/5" />
          </div>

        </div>
      </div>
    </div>
  );
}
