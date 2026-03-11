import { API_CONFIG } from '../config/api';

/**
 * 解析包含分段标识符的文本，提取所有段落
 * 格式：每行以标识符开头（如 <Answer>）
 * @param text 原始文本
 * @returns 段落数组
 */
export function parseAnswerSegments(text: string): string[] {
  const marker = API_CONFIG.SEGMENT_MARKER;
  
  // 按行分割文本
  const lines = text.split('\n');
  const segments: string[] = [];

  for (const line of lines) {
    const trimmedLine = line.trim();
    // 检查是否以标识符开头
    if (trimmedLine.startsWith(marker)) {
      // 移除标识符，保留后面的内容
      const content = trimmedLine.substring(marker.length).trim();
      if (content) {
        segments.push(content);
      }
    }
  }

  // 如果没有找到标识符，返回整个文本作为单个段落
  if (segments.length === 0) {
    return [text.trim()];
  }

  return segments;
}
