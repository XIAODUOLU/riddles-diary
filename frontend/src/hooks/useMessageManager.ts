import { useState, useCallback } from 'react';
import { Message } from '../types';
import { ANIMATION_TIMING } from '../constants/diary';
import { generateReplyText } from '../utils/replyGenerator';
import { parseAnswerSegments } from '../utils/textParser';

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
   * 生成并显示汤姆的回复（支持分段输出）
   */
  const generateTomReply = useCallback(async (userText: string, onComplete?: () => void) => {
    const reply = await generateReplyText(userText);
    
    // 解析 <Answer> 标签分段
    const segments = parseAnswerSegments(reply);
    
    // 如果只有一个段落，直接显示
    if (segments.length === 1) {
      triggerTomTyping(segments[0], Date.now(), onComplete);
      return;
    }
    
    // 多段落：依次显示每个段落，每个段落显示后消失，然后显示下一个
    const displaySegment = (index: number) => {
      if (index >= segments.length) {
        // 所有段落都显示完毕
        if (onComplete) onComplete();
        return;
      }
      
      // 显示当前段落，完成后显示下一个
      triggerTomTyping(segments[index], Date.now() + index, () => {
        displaySegment(index + 1);
      });
    };
    
    // 开始显示第一个段落
    displaySegment(0);
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
