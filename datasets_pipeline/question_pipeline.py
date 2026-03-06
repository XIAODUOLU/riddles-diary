#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
问题生成管道 (Question Generation Pipeline)

基于对话类别配置文件，使用 OpenAI API 生成类似的话语样本
功能特性：
- 断点续传：支持中断后继续执行
- 重试机制：API 调用失败自动重试
- 实时存储：每完成一个类别立即保存进度
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
    # 获取项目根目录（脚本所在目录的父目录）
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    load_dotenv(os.path.join(PROJECT_ROOT, ".env"))
except ImportError:
    print(
        "提示: 安装 python-dotenv 可以使用 .env 文件管理配置: pip install python-dotenv"
    )
    PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 确保日志目录存在（在项目根目录下）
LOG_DIR = os.path.join(PROJECT_ROOT, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(
            os.path.join(LOG_DIR, "question_pipeline.log"), encoding="utf-8"
        ),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class QuestionGenerator:
    """
    问题生成器 (Question Generator)
    
    负责根据对话类别配置生成训练用的问题样本
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: str = "gpt-4o-mini",
        max_retries: int = 3,
        retry_delay: int = 2,
        samples_per_batch: int = 10,
        batches_per_class: int = 3,
        temperature: float = 0.7,
    ):
        """
        初始化问题生成器

        Args:
            api_key: OpenAI API 密钥（默认从环境变量 OPENAI_API_KEY 读取）
            base_url: API 基础 URL（默认从环境变量 OPENAI_BASE_URL 读取）
            model: 使用的模型名称（默认 gpt-4o-mini）
            max_retries: API 调用最大重试次数
            retry_delay: 重试延迟时间（秒）
            samples_per_batch: 每批次生成的样本数量
            batches_per_class: 每个类别生成的批次数
            temperature: 生成温度（0-1，越低越确定，越高越随机）
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL")
        self.model = model
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.samples_per_batch = samples_per_batch
        self.batches_per_class = batches_per_class
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

    def load_dialog_classes(self, filepath: str) -> List[Dict[str, Any]]:
        """
        加载对话类别配置文件
        
        配置文件包含各类对话的描述和示例

        Args:
            filepath: JSON 配置文件路径

        Returns:
            list: 对话类别列表，每个元素包含 class, description, examples
        """
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            logger.info(f"成功加载配置文件: {filepath}，共{len(data)}个类别")
            return data
        except FileNotFoundError:
            logger.error(f"配置文件不存在: {filepath}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"配置文件JSON格式错误: {e}")
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
        return {"completed_classes": [], "results": []}

    def save_progress(self, progress_file: str, progress: Dict[str, Any]):
        """
        保存进度文件

        Args:
            progress_file: 进度文件路径
            progress: 进度数据
        """
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(progress_file) or ".", exist_ok=True)

            with open(progress_file, "w", encoding="utf-8") as f:
                json.dump(progress, f, ensure_ascii=False, indent=2)
            logger.info(f"进度已保存: {progress_file}")
        except Exception as e:
            logger.error(f"保存进度文件失败: {e}")

    def generate_prompt(self, class_info: Dict[str, Any]) -> str:
        """
        生成 API 调用的提示词
        
        根据类别信息构造完整的生成指令

        Args:
            class_info: 类别信息字典（包含 class, description, examples）

        Returns:
            str: 完整的提示词字符串
        """
        class_name = class_info.get("class", "")
        description = class_info.get("description", "")
        examples = class_info.get("examples", [])

        prompt = f"""你是一个专业的对话生成助手。请根据以下信息生成{self.samples_per_batch}句类似的话语。

类别名称: {class_name}
类别描述: {description}

示例:
"""
        for i, example in enumerate(examples, 1):
            prompt += f"{i}. {example}\n"

        prompt += f"""
要求:
1. 生成{self.samples_per_batch}句与示例风格、语气、主题相似的话语
2. 保持与类别描述一致的特征
3. 每句话应该独立完整，具有实际使用价值
4. 避免简单重复示例的内容，要有创新性
5. 直接输出{self.samples_per_batch}句话，每句话一行，不要编号，不要其他说明

请开始生成:"""

        return prompt

    def call_api_with_retry(self, prompt: str) -> Optional[str]:
        """
        调用 OpenAI API 并支持自动重试
        
        使用指数退避策略进行重试

        Args:
            prompt: 提示词

        Returns:
            str: API 返回的生成文本
            None: 所有重试均失败
        """
        for attempt in range(self.max_retries):
            try:
                logger.info(f"调用API (尝试 {attempt + 1}/{self.max_retries})")

                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": "你是一个专业的对话生成助手，擅长根据示例生成类似风格的文本。",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    temperature=self.temperature,
                    max_tokens=2000,
                )

                content = response.choices[0].message.content
                logger.info("API调用成功")
                return content

            except Exception as e:
                logger.warning(
                    f"API调用失败 (尝试 {attempt + 1}/{self.max_retries}): {e}"
                )

                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (2**attempt)  # 指数退避
                    logger.info(f"等待{wait_time}秒后重试...")
                    time.sleep(wait_time)
                else:
                    logger.error(f"API调用失败，已达到最大重试次数")
                    return None

    def parse_response(self, response: str) -> List[str]:
        """
        解析 API 响应，提取生成的句子
        
        自动移除可能的编号前缀

        Args:
            response: API 响应文本

        Returns:
            list: 清理后的句子列表
        """
        if not response:
            return []

        lines = response.strip().split("\n")
        sentences = []

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 移除可能的编号
            if line and line[0].isdigit():
                # 移除开头的数字和标点
                parts = line.split(".", 1)
                if len(parts) > 1:
                    line = parts[1].strip()
                else:
                    parts = line.split("、", 1)
                    if len(parts) > 1:
                        line = parts[1].strip()

            if line:
                sentences.append(line)

        return sentences

    def generate_for_class(
        self, class_info: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        为单个类别生成样本（多批次生成）
        
        每个类别会生成多个批次以增加样本多样性

        Args:
            class_info: 类别信息字典

        Returns:
            dict: 生成结果（包含类别名、样本列表、统计信息等）
            None: 生成失败
        """
        class_name = class_info.get("class", "")
        logger.info(f"开始生成类别: {class_name} (共{self.batches_per_class}批次)")

        all_sentences = []

        # 多批次生成
        for batch_idx in range(self.batches_per_class):
            logger.info(f"  批次 {batch_idx + 1}/{self.batches_per_class}")

            prompt = self.generate_prompt(class_info)
            response = self.call_api_with_retry(prompt)

            if response is None:
                logger.warning(f"类别 {class_name} 批次 {batch_idx + 1} 生成失败，跳过")
                continue

            sentences = self.parse_response(response)
            all_sentences.extend(sentences)

            logger.info(f"  批次 {batch_idx + 1} 生成了 {len(sentences)} 句")

            # 批次间稍作延迟
            if batch_idx < self.batches_per_class - 1:
                time.sleep(0.5)

        if not all_sentences:
            logger.error(f"类别 {class_name} 所有批次都生成失败")
            return None

        expected_total = self.samples_per_batch * self.batches_per_class
        if len(all_sentences) < expected_total:
            logger.warning(
                f"类别 {class_name} 生成数量不足: {len(all_sentences)}/{expected_total}"
            )

        result = {
            "class": class_name,
            "description": class_info.get("description", ""),
            "original_examples": class_info.get("examples", []),
            "generated_samples": all_sentences,
            "generated_count": len(all_sentences),
            "batches": self.batches_per_class,
            "timestamp": datetime.now().isoformat(),
        }

        logger.info(f"类别 {class_name} 生成完成，共{len(all_sentences)}句")
        return result

    def run(
        self,
        input_file: str = None,
        output_file: str = None,
        progress_file: str = None,
    ):
        """
        运行问题生成管道（主流程）
        
        支持断点续传，可随时中断并在下次运行时继续

        Args:
            input_file: 输入配置文件路径（默认 datasets/custom/dialoag_classes.json）
            output_file: 输出结果文件路径（默认 datasets/custom/generated_questions.json）
            progress_file: 进度文件路径（默认 logs/question_pipeline_progress.json）
        """
        # 设置默认路径
        if input_file is None:
            input_file = os.path.join(
                PROJECT_ROOT, "datasets/custom/dialoag_classes.json"
            )
        if output_file is None:
            output_file = os.path.join(
                PROJECT_ROOT, "datasets/custom/generated_questions.json"
            )
        if progress_file is None:
            progress_file = os.path.join(
                PROJECT_ROOT, "logs/question_pipeline_progress.json"
            )

        logger.info("=" * 60)
        logger.info("问题生成管道启动")
        logger.info(f"输入文件: {input_file}")
        logger.info(f"输出文件: {output_file}")
        logger.info(f"进度文件: {progress_file}")
        logger.info("=" * 60)

        # 加载配置
        dialog_classes = self.load_dialog_classes(input_file)

        # 加载进度
        progress = self.load_progress(progress_file)
        completed_classes = set(progress.get("completed_classes", []))
        results = progress.get("results", [])

        # 确保输出目录存在
        os.makedirs(os.path.dirname(output_file) or ".", exist_ok=True)

        # 统计信息
        total_classes = len(dialog_classes)
        completed_count = len(completed_classes)

        logger.info(f"总类别数: {total_classes}")
        logger.info(f"已完成: {completed_count}")
        logger.info(f"待处理: {total_classes - completed_count}")

        # 处理每个类别
        for idx, class_info in enumerate(dialog_classes, 1):
            class_name = class_info.get("class", "")

            # 跳过已完成的类别
            if class_name in completed_classes:
                logger.info(f"[{idx}/{total_classes}] 跳过已完成的类别: {class_name}")
                continue

            logger.info(f"[{idx}/{total_classes}] 处理类别: {class_name}")

            # 生成样本
            result = self.generate_for_class(class_info)

            if result:
                # 添加到结果列表
                results.append(result)
                completed_classes.add(class_name)

                # 立即保存进度
                progress["completed_classes"] = list(completed_classes)
                progress["results"] = results
                self.save_progress(progress_file, progress)

                # 同时保存最终结果文件
                self.save_final_results(output_file, results)

                logger.info(f"进度: {len(completed_classes)}/{total_classes}")
            else:
                logger.error(f"类别 {class_name} 处理失败，将在下次运行时重试")

            # 避免请求过快
            time.sleep(1)

        # 最终统计
        logger.info("=" * 60)
        logger.info("生成完成!")
        logger.info(f"成功生成: {len(completed_classes)}/{total_classes} 个类别")
        logger.info(f"总样本数: {sum(r['generated_count'] for r in results)}")
        logger.info(f"结果文件: {output_file}")
        logger.info("=" * 60)

    def save_final_results(self, output_file: str, results: List[Dict[str, Any]]):
        """
        保存最终结果文件
        
        包含元数据和所有生成的问题样本

        Args:
            output_file: 输出文件路径
            results: 结果列表
        """
        try:
            output_data = {
                "metadata": {
                    "total_classes": len(results),
                    "total_samples": sum(r["generated_count"] for r in results),
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
    主函数 - 启动问题生成管道
    
    配置参数从环境变量读取，支持 .env 文件
    """
    # 从环境变量读取配置参数
    config = {
        "api_key": os.getenv("OPENAI_API_KEY"),
        "base_url": os.getenv("OPENAI_BASE_URL"),
        "model": os.getenv("MODEL", "gpt-4o-mini"),
        "max_retries": int(os.getenv("MAX_RETRIES", "3")),
        "retry_delay": int(os.getenv("RETRY_DELAY", "2")),
        "samples_per_batch": int(os.getenv("SAMPLES_PER_BATCH", "10")),
        "batches_per_class": int(os.getenv("BATCHES_PER_CLASS", "3")),
        "temperature": float(os.getenv("TEMPERATURE", "0.7")),
    }

    # 文件路径（相对于项目根目录）
    input_file = os.path.join(PROJECT_ROOT, "datasets/custom/dialoag_classes.json")
    output_file = os.path.join(PROJECT_ROOT, "datasets/custom/generated_questions.json")
    progress_file = os.path.join(PROJECT_ROOT, "logs/question_pipeline_progress.json")

    try:
        # 创建生成器
        generator = QuestionGenerator(**config)

        # 运行管道
        generator.run(
            input_file=input_file, output_file=output_file, progress_file=progress_file
        )

    except KeyboardInterrupt:
        logger.info("\n用户中断，进度已保存，可以稍后继续运行")
    except Exception as e:
        logger.error(f"程序异常: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
