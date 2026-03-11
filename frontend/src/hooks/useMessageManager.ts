import { useState, useCallback } from 'react';
import { Message } from '../types';
import { ANIMATION_TIMING } from '../constants/diary';
import { generateReplyText } from '../utils/replyGenerator';

export function useMessageManager() {
  const [messages, setMessages] = useState<Message[]>([]);

  /**
   * 触发汤姆的打字动画
   */
  const triggerTomTyping = useCallback((text: string, id: number, onComplete?: () => void) => {
    setMessages(prev => [...prev, { 
      id, 
      text, 
      sender: 'tom', 
      status: 'typing', 
      displayedText: '' 
    }]);
    
    let i = 0;
    const interval = setInterval(() => {
      i++;
      setMessages(prev => prev.map(m => 
        m.id === id ? { ...m, displayedText: text.slice(0, i) } : m
      ));
      
      if (i >= text.length) {
        clearInterval(interval);
        setTimeout(() => {
          setMessages(prev => prev.map(m => 
            m.id === id ? { ...m, status: 'fading' } : m
          ));
          setTimeout(() => {
            setMessages(prev => prev.map(m => 
              m.id === id ? { ...m, status: 'gone' } : m
            ));
            if (onComplete) onComplete();
          }, ANIMATION_TIMING.FADE_DURATION);
        }, ANIMATION_TIMING.DISPLAY_DURATION); 
      }
    }, ANIMATION_TIMING.TYPING_SPEED);
  }, []);

  /**
   * 生成并显示汤姆的回复
   */
  const generateTomReply = useCallback((userText: string, onComplete?: () => void) => {
    const reply = generateReplyText(userText);
    triggerTomTyping(reply, Date.now(), onComplete);
  }, [triggerTomTyping]);

  /**
   * 处理用户消息提交
   */
  const handleUserSubmit = useCallback((text: string, onComplete?: () => void) => {
    const id = Date.now();
    setMessages(prev => [...prev, { 
      id, 
      text, 
      sender: 'user', 
      status: 'visible' 
    }]);

    setTimeout(() => {
      setMessages(prev => prev.map(m => 
        m.id === id ? { ...m, status: 'fading' } : m
      ));
      setTimeout(() => {
        setMessages(prev => prev.map(m => 
          m.id === id ? { ...m, status: 'gone' } : m
        ));
        generateTomReply(text, onComplete);
      }, ANIMATION_TIMING.USER_FADE_DURATION); 
    }, ANIMATION_TIMING.USER_FADE_DELAY);
  }, [generateTomReply]);

  return {
    messages,
    triggerTomTyping,
    handleUserSubmit,
  };
}
