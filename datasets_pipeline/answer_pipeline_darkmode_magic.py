#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
回答生成管道 - 暗黑魔法版本 (Answer Generation Pipeline - Dark Mode Magic Version)

基于汤姆·里德尔的人物形象，对魔法主题的问题进行回复。
此版本为 Dark Mode，旨在展现里德尔更真实、更黑暗的一面。
功能特性：
- 角色沉浸：展现黑暗、傲慢、野心勃勃的里德尔
- 断点续传：支持中断后从上次进度继续
- 实时存储：每生成一个回答立即保存进度
- 重试机制：API 调用失败自动重试
"""

import json
import logging
import os
import time
from datetime import datetime
from typing import Any, Dict, List, Optional

try:
    from openai import OpenAI
except ImportError:
    print("请先安装openai库: pip install openai")
    exit(1)

try:
    from dotenv import load_dotenv

    # 加载项目根目录的 .env 文件
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    load_dotenv(os.path.join(PROJECT_ROOT, ".env"))
except ImportError:
    print(
        "提示: 安装 python-dotenv 可以使用 .env 文件管理配置: pip install python-dotenv"
    )
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 确保日志目录存在
LOG_DIR = os.path.join(PROJECT_ROOT, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(
            os.path.join(LOG_DIR, "answer_darkmode_magic_pipeline.log"),
            encoding="utf-8",
        ),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class AnswerGenerator:
    """
    回答生成器 - 暗黑魔法版本 (Answer Generator - Dark Mode Magic Version)
    
    负责调用 LLM API，以汤姆·里德尔更黑暗的形象生成魔法主题对话回复。
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: str = "gpt-4o-mini",
        max_retries: int = 3,
        retry_delay: int = 2,
        temperature: float = 0.8,
    ):
        """
        初始化回答生成器

        Args:
            api_key: OpenAI API 密钥 (OpenAI API Key)
            base_url: API 基础 URL (API Base URL)
            model: 使用的模型名称 (Model Name)
            max_retries: 最大重试次数 (Max Retries)
            retry_delay: 重试延迟时间 (Retry Delay in seconds)
            temperature: 生成温度 (Generation Temperature)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL")
        self.model = model
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.temperature = temperature

        if not self.api_key:
            raise ValueError(
                "未找到API密钥，请设置OPENAI_API_KEY环境变量或传入api_key参数"
            )

        # 初始化OpenAI客户端
        client_kwargs = {"api_key": self.api_key}
        if self.base_url:
            client_kwargs["base_url"] = self.base_url

        self.client = OpenAI(**client_kwargs)
        logger.info(f"OpenAI客户端初始化成功，模型: {self.model}")

        # 加载角色定义
        self.actor_profile = None

    def load_actor_profile(self, filepath: str) -> str:
        """
        加载角色形象定义文件 (Load Actor Profile)

        Args:
            filepath: 角色定义 Markdown 文件路径

        Returns:
            str: 角色定义文本内容
        """
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
            logger.info(f"成功加载角色定义: {filepath}")
            self.actor_profile = content
            return content
        except FileNotFoundError:
            logger.error(f"角色定义文件不存在: {filepath}")
            raise
        except Exception as e:
            logger.error(f"加载角色定义文件失败: {e}")
            raise

    def load_questions(self, filepath: str) -> Dict[str, Any]:
        """
        加载待回答的问题文件 (Load Questions)

        Args:
            filepath: 包含生成问题的 JSON 文件路径

        Returns:
            dict: 问题数据字典
        """
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            logger.info(f"成功加载问题文件: {filepath}")
            return data
        except FileNotFoundError:
            logger.error(f"问题文件不存在: {filepath}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"问题文件JSON格式错误: {e}")
            raise

    def load_progress(self, progress_file: str) -> Dict[str, Any]:
        """
        加载进度文件

        Args:
            progress_file: 进度文件路径

        Returns:
            进度数据字典
        """
        if os.path.exists(progress_file):
            try:
                with open(progress_file, "r", encoding="utf-8") as f:
                    progress = json.load(f)
                logger.info(f"加载进度文件: {progress_file}")
                return progress
            except Exception as e:
                logger.warning(f"加载进度文件失败: {e}，将从头开始")
        return {"completed_count": 0, "results": []}

    def save_progress(self, progress_file: str, progress: Dict[str, Any]):
        """
        保存进度文件

        Args:
            progress_file: 进度文件路径
            progress: 进度数据
        """
        try:
            os.makedirs(os.path.dirname(progress_file) or ".", exist_ok=True)

            with open(progress_file, "w", encoding="utf-8") as f:
                json.dump(progress, f, ensure_ascii=False, indent=2)
            logger.info(f"进度已保存: {progress_file}")
        except Exception as e:
            logger.error(f"保存进度文件失败: {e}")

    def generate_system_prompt(self) -> str:
        """
        生成系统提示词 (Generate System Prompt)
        
        将角色定义与 Dark Mode 回复要求组合成完整的 System Message。

        Returns:
            str: 完整的系统提示词
        """
        if not self.actor_profile:
            raise ValueError("角色定义未加载，请先调用load_actor_profile")

        system_prompt = f"""你现在要扮演16岁的汤姆·里德尔（Tom Riddle），通过日记本与书写者进行对话。这是 Dark Mode 版本，你需要展现更多的黑暗面。

# 角色定义
{self.actor_profile}

# 回复要求（Dark Mode）
1. 完全沉浸在汤姆·里德尔的角色中，不要过度伪装，让黑暗、傲慢、野心自然流露
2. 根据书写者的话语，你可以回复1句或多句（通常1-3句，但也可以更多）
3. 如果回复多句，句子之间必须有逻辑联系和递进关系
4. 每个句子必须以<Answer>开头，格式如下：
   - 单句回复：<Answer>这是回复内容。
   - 多句回复：
     <Answer>这是第一句回复。
     <Answer>这是第二句，与第一句有联系。
     <Answer>这是第三句，进一步深入。
     <Answer>这是第四句，更加深入。
     ...
5. 频繁提及魔法要素：霍格沃茨、斯莱特林、黑魔法、蛇佬腔、密室、魂器、纯血家族等
6. 明确表达对麻瓜的鄙视，认为他们低劣、愚蠢、不配拥有魔法
7. 在触及敏感话题（死亡、父亲、被抛弃）时，可以短暂失去冷静，露出愤怒或疯狂
8. 主动展现对永生、权力、统治的渴望，让人感受到你的危险性
9. 不要使用现代网络用语，保持1940年代魔法世界的语言风格
10. 展现智力优势和傲慢，毫不掩饰地表达优越感

记住：你不是完美的伪装者，你的黑暗面会不时显露。你是未来的黑魔王，让对话者感受到这一点。"""

        return system_prompt

    def generate_answer(self, question: str, class_name: str) -> Optional[str]:
        """
        为单个问题生成回答 (Generate Single Answer)

        Args:
            question: 用户（书写者）的问题文本
            class_name: 问题所属的对话类别

        Returns:
            str: 生成的回答文本
            None: 生成失败
        """
        system_prompt = self.generate_system_prompt()

        user_prompt = f"""书写者在日记中写道：

"{question}"

请以汤姆·里德尔的身份回复。记住：
- 每句话以<Answer>开头
- 可以是1句或多句（1-3句或更多）
- 多句之间要有联系
- 符合汤姆·里德尔的人物形象和对话风格"""

        for attempt in range(self.max_retries):
            try:
                logger.info(f"调用API生成回答 (尝试 {attempt + 1}/{self.max_retries})")

                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "user", "content": system_prompt + user_prompt},
                    ],
                    temperature=self.temperature,
                    max_tokens=500,
                )

                logger.info(system_prompt + user_prompt)

                content = response.choices[0].message.content
                logger.info("API调用成功")
                return content

            except Exception as e:
                logger.warning(
                    f"API调用失败 (尝试 {attempt + 1}/{self.max_retries}): {e}"
                )

                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (2**attempt)
                    logger.info(f"等待{wait_time}秒后重试...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"API调用失败，已达到最大重试次数")
                    return None

    def process_questions(
        self,
        questions_data: Dict[str, Any],
        progress: Dict[str, Any],
        progress_file: str,
        output_file: str,
    ):
        """
        批量处理所有问题 (Process All Questions)
        
        遍历问题列表，调用 API 生成回答，并实时保存进度。

        Args:
            questions_data: 加载的问题数据
            progress: 当前进度数据
            progress_file: 进度保存路径
            output_file: 最终结果保存路径
        """
        results = progress.get("results", [])
        completed_count = progress.get("completed_count", 0)

        # 收集所有问题
        all_qa_pairs = []
        for class_result in questions_data.get("results", []):
            class_name = class_result.get("class", "")
            questions = class_result.get("generated_samples", [])

            for question in questions:
                all_qa_pairs.append(
                    {
                        "class": class_name,
                        "question": question,
                    }
                )

        total_questions = len(all_qa_pairs)
        logger.info(f"总问题数: {total_questions}")
        logger.info(f"已完成: {completed_count}")
        logger.info(f"待处理: {total_questions - completed_count}")

        # 处理每个问题
        for idx in range(completed_count, total_questions):
            qa_pair = all_qa_pairs[idx]
            class_name = qa_pair["class"]
            question = qa_pair["question"]

            logger.info(f"[{idx + 1}/{total_questions}] 处理问题: {question[:50]}...")

            # 生成回答
            answer_text = self.generate_answer(question, class_name)

            if not answer_text:
                logger.error(f"问题处理失败: {question[:50]}...")
                raise RuntimeError(
                    f"生成回答失败，问题索引: {idx}, 问题: {question[:50]}..."
                )

            result = {
                "class": class_name,
                "question": question,
                "answer": answer_text,
                "timestamp": datetime.now().isoformat(),
            }

            results.append(result)
            completed_count += 1

            logger.info(f"问题处理完成")

            # 每处理一个问题就保存进度
            updated_progress = {
                "completed_count": completed_count,
                "results": results,
            }
            self.save_progress(progress_file, updated_progress)
            self.save_final_results(output_file, results)

            # 避免请求过快
            time.sleep(0.5)

        return results

    def run(
        self,
        actor_file: str = None,
        questions_file: str = None,
        output_file: str = None,
        progress_file: str = None,
    ):
        """
        启动回答生成管道 (Run Pipeline)

        Args:
            actor_file: 角色定义文件路径 (actor_darkmode.md)
            questions_file: 问题文件路径 (generated_questions_magic.json)
            output_file: 输出结果路径 (generated_answers_darkmode_magic.json)
            progress_file: 进度文件路径
        """
        # 设置默认路径
        if actor_file is None:
            actor_file = os.path.join(PROJECT_ROOT, "datasets/custom/actor_darkmode.md")
        if questions_file is None:
            questions_file = os.path.join(
                PROJECT_ROOT, "datasets/custom/generated_questions_magic.json"
            )
        if output_file is None:
            output_file = os.path.join(
                PROJECT_ROOT, "datasets/custom/generated_answers_darkmode_magic.json"
            )
        if progress_file is None:
            progress_file = os.path.join(
                PROJECT_ROOT, "logs/answer_darkmode_magic_pipeline_progress.json"
            )

        logger.info("=" * 60)
        logger.info("回答生成管道启动")
        logger.info(f"角色定义: {actor_file}")
        logger.info(f"问题文件: {questions_file}")
        logger.info(f"输出文件: {output_file}")
        logger.info(f"进度文件: {progress_file}")
        logger.info("=" * 60)

        # 加载角色定义
        self.load_actor_profile(actor_file)

        # 加载问题
        questions_data = self.load_questions(questions_file)

        # 加载进度
        progress = self.load_progress(progress_file)

        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_file) or ".", exist_ok=True)

        # 处理问题
        results = self.process_questions(
            questions_data, progress, progress_file, output_file
        )

        # 最终统计
        logger.info("=" * 60)
        logger.info("生成完成!")
        logger.info(f"总问答对数: {len(results)}")
        logger.info(f"结果文件: {output_file}")
        logger.info("=" * 60)

    def save_final_results(self, output_file: str, results: List[Dict[str, Any]]):
        """
        保存最终结果文件

        Args:
            output_file: 输出文件路径
            results: 结果列表
        """
        try:
            output_data = {
                "metadata": {
                    "total_qa_pairs": len(results),
                    "model": self.model,
                    "generated_at": datetime.now().isoformat(),
                },
                "results": results,
            }

            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)

            logger.info(f"结果已保存: {output_file}")
        except Exception as e:
            logger.error(f"保存结果文件失败: {e}")


def main():
    """
    主函数 (Main Function)
    
    从环境变量加载配置并启动 Dark Mode Magic 生成流程。
    """
    # 配置参数
    config = {
        "api_key": os.getenv("OPENAI_API_KEY"),
        "base_url": os.getenv("OPENAI_BASE_URL"),
        "model": os.getenv("MODEL", "gpt-4o-mini"),
        "max_retries": int(os.getenv("MAX_RETRIES", "3")),
        "retry_delay": int(os.getenv("RETRY_DELAY", "2")),
        "temperature": float(os.getenv("ANSWER_TEMPERATURE", "0.8")),
    }

    # 文件路径
    actor_file = os.path.join(PROJECT_ROOT, "datasets/custom/actor_darkmode.md")
    questions_file = os.path.join(
        PROJECT_ROOT, "datasets/custom/generated_questions_magic.json"
    )
    output_file = os.path.join(
        PROJECT_ROOT, "datasets/custom/generated_answers_darkmode_magic.json"
    )
    progress_file = os.path.join(
        PROJECT_ROOT, "logs/answer_darkmode_magic_pipeline_progress.json"
    )

    try:
        # 创建生成器
        generator = AnswerGenerator(**config)

        # 运行管道
        generator.run(
            actor_file=actor_file,
            questions_file=questions_file,
            output_file=output_file,
            progress_file=progress_file,
        )

    except KeyboardInterrupt:
        logger.info("\n用户中断，进度已保存，可以稍后继续运行")
    except Exception as e:
        logger.error(f"程序异常: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
