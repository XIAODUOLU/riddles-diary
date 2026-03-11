import { useState, useEffect, useRef } from 'react';
import CloseButton from './CloseButton';
import BookCover from './BookCover';
import InteractivePage from './InteractivePage';
import { BackCover, ThicknessPages } from './BookPages';
import { useMessageManager } from '../hooks/useMessageManager';
import { ANIMATION_TIMING, BOOK_DIMENSIONS, INITIAL_GREETING } from '../constants/diary';
import '../styles/diary.css';

export default function TomRiddleDiary() {
  const [page, setPage] = useState(0); // 0 = 闭合, 1 = 翻开
  const [inputValue, setInputValue] = useState("");
  const [isLocked, setIsLocked] = useState(false);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const hasOpened = useRef(false);

  const { messages, triggerTomTyping, handleUserSubmit } = useMessageManager();

  // 初始交互：汤姆的问候
  useEffect(() => {
    if (page === 1 && !hasOpened.current) {
      hasOpened.current = true;
      setIsLocked(true);
      setTimeout(() => {
        triggerTomTyping(INITIAL_GREETING, Date.now(), () => {
          setIsLocked(false);
          setTimeout(() => inputRef.current?.focus(), ANIMATION_TIMING.FOCUS_DELAY);
        });
      }, ANIMATION_TIMING.INITIAL_GREETING_DELAY);
    }
  }, [page, triggerTomTyping]);

  const handleOpen = () => setPage(1);
  const handleClose = () => setPage(0);

  const handleSubmit = (text: string) => {
    if (isLocked) return;
    setIsLocked(true);
    inputRef.current?.blur();
    setInputValue("");

    handleUserSubmit(text, () => {
      setIsLocked(false);
      setTimeout(() => inputRef.current?.focus(), ANIMATION_TIMING.FOCUS_DELAY);
    });
  };

  const handleFocus = () => {
    if (!isLocked) {
      inputRef.current?.focus();
    }
  };

  return (
    <div className="diary-environment">
      <CloseButton isVisible={page === 1} onClick={handleClose} />

      <div className={`book ${page === 1 ? 'open' : ''}`}>
        <div className="book-shadow" />

        {/* 右侧堆叠（未翻动的书页和封底） */}
        <BackCover />
        <ThicknessPages 
          thicknessCount={BOOK_DIMENSIONS.DEPTH_LAYERS.THICKNESS_COUNT}
          depthStart={BOOK_DIMENSIONS.DEPTH_LAYERS.THICKNESS_START}
        />

        {/* 交互主页 (右页) */}
        <div className="leaf" style={{ transform: `translateZ(${BOOK_DIMENSIONS.DEPTH_LAYERS.MAIN_PAGE}px)` }}>
          <InteractivePage
            messages={messages}
            inputValue={inputValue}
            isLocked={isLocked || page === 0}
            inputRef={inputRef}
            onInputChange={setInputValue}
            onSubmit={handleSubmit}
            onFocus={handleFocus}
          />
        </div>

        {/* 封面层 (最顶层) */}
        <BookCover 
          isOpen={page === 1}
          onOpen={handleOpen}
          onClose={handleClose}
        />
      </div>
    </div>
  );
}
