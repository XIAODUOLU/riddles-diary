export interface Message {
  id: number;
  text: string;
  sender: 'user' | 'tom';
  status: 'visible' | 'typing' | 'fading' | 'gone';
  displayedText?: string;
}

export type CornerPosition = 'tl' | 'tr' | 'bl' | 'br';
