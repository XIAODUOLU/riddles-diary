import { RefObject } from 'react';
import { Message } from '../types';

interface InteractivePageProps {
  messages: Message[];
  inputValue: string;
  isLocked: boolean;
  inputRef: RefObject<HTMLTextAreaElement>;
  onInputChange: (value: string) => void;
  onSubmit: (text: string) => void;
  onFocus: () => void;
}

export default function InteractivePage({
  messages,
  inputValue,
  isLocked,
  inputRef,
  onInputChange,
  onSubmit,
  onFocus,
}: InteractivePageProps) {
  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (inputValue.trim() && !isLocked) {
        onSubmit(inputValue);
      }
    }
  };

  return (
    <div className="face face-front tex-paper paper-edge" onClick={onFocus}>
      <div className="spine-joint-right" />
      <div className={`magic-glow ${messages.some(m => m.sender === 'tom' && m.status !== 'gone') ? 'opacity-100' : 'opacity-0'}`} />
      
      <div className="absolute inset-0 p-10 flex flex-col justify-center items-center">
        {/* 消息容器 - 支持滚动但隐藏滚动条 */}
        <div className="w-full max-w-[85%] flex-1 overflow-y-auto overflow-x-hidden scrollbar-hide flex flex-col justify-center">
          <div className="flex flex-col items-center min-h-full justify-center">
            {/* 消息列表 */}
            {messages.filter(m => m.status !== 'gone').map(m => (
              <div
                key={m.id}
                className={`font-chinese-handwriting ink-text mb-5 w-full ${
                  m.status === 'fading' ? 'ink-fading' : ''
                } ${
                  m.sender === 'tom' ? 'text-center italic' : 'text-left pl-5'
                }`}
              >
                {m.sender === 'tom' ? m.displayedText : m.text}
              </div>
            ))}

            {/* 输入区域 */}
            <div className="font-chinese-handwriting ink-text text-left pl-5 w-full min-h-[2.5rem] relative">
              <span className="whitespace-pre-wrap break-words">{inputValue}</span>
              {!isLocked && inputValue === "" && <span className="animate-pulse opacity-60">|</span>}
              {!isLocked && inputValue !== "" && <span className="animate-pulse ml-1 opacity-60">|</span>}
            </div>
          </div>
        </div>

        {/* 隐藏的文本输入框 */}
        <textarea
          ref={inputRef}
          className="absolute inset-0 w-full h-full opacity-0 cursor-text resize-none p-12 focus:outline-none z-20"
          value={inputValue}
          onChange={(e) => onInputChange(e.target.value)}
          onKeyDown={handleKeyDown}
          spellCheck={false}
          disabled={isLocked}
        />
      </div>
    </div>
  );
}
