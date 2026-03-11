import { API_CONFIG, SYSTEM_PROMPT } from '../config/api';

interface ChatMessage {
  role: 'system' | 'user' | 'assistant';
  content: string;
}

interface ChatCompletionResponse {
  choices: Array<{
    message: {
      content: string;
    };
  }>;
}

/**
 * 调用 OpenAI 兼容的 API 生成回复
 */
export async function generateAIReply(userMessage: string): Promise<string> {
  try {
    const messages: ChatMessage[] = [
      { role: 'system', content: SYSTEM_PROMPT },
      { role: 'user', content: userMessage },
    ];

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), API_CONFIG.TIMEOUT);

    const response = await fetch(`${API_CONFIG.BASE_URL}/chat/completions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(API_CONFIG.API_KEY && { 'Authorization': `Bearer ${API_CONFIG.API_KEY}` }),
      },
      body: JSON.stringify({
        model: API_CONFIG.MODEL,
        messages,
        max_tokens: API_CONFIG.MAX_TOKENS,
        stream: false,
      }),
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      throw new Error(`API request failed: ${response.status} ${response.statusText}`);
    }

    const data: ChatCompletionResponse = await response.json();
    const reply = data.choices[0]?.message?.content?.trim();

    if (!reply) {
      throw new Error('Empty response from API');
    }

    return reply;
  } catch (error) {
    console.error('AI API Error:', error);
    
    // 如果API调用失败，返回一个默认的神秘回复
    if (error instanceof Error && error.name === 'AbortError') {
      return '时间的流逝让我的记忆变得模糊...';
    }
    
    return '日记本的魔法似乎受到了干扰...';
  }
}
