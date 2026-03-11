import { TOM_REPLIES } from '../constants/diary';

/**
 * 根据用户输入生成汤姆的回复
 */
export function generateReplyText(userText: string): string {
  const lower = userText.toLowerCase();
  
  if (lower.includes("hello") || lower.includes("hi") || lower.includes("你好")) {
    return TOM_REPLIES.GREETING;
  }
  
  if (lower.includes("who") || lower.includes("谁")) {
    return TOM_REPLIES.WHO;
  }
  
  if (lower.includes("chamber") || lower.includes("secret") || lower.includes("密室")) {
    return TOM_REPLIES.CHAMBER;
  }
  
  if (lower.includes("voldemort") || lower.includes("dark lord") || lower.includes("伏地魔") || lower.includes("黑魔王")) {
    return TOM_REPLIES.VOLDEMORT;
  }
  
  if (lower.includes("harry") || lower.includes("potter") || lower.includes("哈利") || lower.includes("波特")) {
    return TOM_REPLIES.HARRY;
  }
  
  if (lower.includes("magic") || lower.includes("魔法")) {
    return TOM_REPLIES.MAGIC;
  }
  
  if (lower.includes("help") || lower.includes("帮助")) {
    return TOM_REPLIES.HELP;
  }
  
  if (lower.includes("dumbledore") || lower.includes("邓布利多")) {
    return TOM_REPLIES.DUMBLEDORE;
  }
  
  if (lower.includes("horcrux") || lower.includes("魂器")) {
    return TOM_REPLIES.HORCRUX;
  }
  
  return TOM_REPLIES.DEFAULT;
}
