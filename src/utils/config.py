"""
Configuration management for the Equity News Research Tool
"""
import os
from pathlib import Path
from typing import Literal
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class LLMConfig(BaseModel):
    """LLM provider configuration"""
    provider: Literal["openai", "anthropic"] = Field(
        default=os.getenv("DEFAULT_LLM_PROVIDER", "openai")
    )
    model: str = Field(default=os.getenv("DEFAULT_MODEL", "gpt-4-turbo-preview"))
    temperature: float = Field(default=float(os.getenv("TEMPERATURE", "0.1")))
    streaming: bool = True


class EmbeddingConfig(BaseModel):
    """Embedding model configuration"""
    model: str = Field(default=os.getenv("EMBEDDING_MODEL", "text-embedding-3-large"))
    provider: Literal["openai", "local"] = "openai"


class RAGConfig(BaseModel):
    """RAG pipeline configuration"""
    top_k: int = Field(default=int(os.getenv("TOP_K_RETRIEVAL", "10")))
    rerank_top_n: int = Field(default=int(os.getenv("RERANK_TOP_N", "5")))
    chunk_size: int = Field(default=int(os.getenv("CHUNK_SIZE", "1000")))
    chunk_overlap: int = Field(default=int(os.getenv("CHUNK_OVERLAP", "200")))
    use_hybrid_search: bool = True
    use_reranking: bool = True


class NewsConfig(BaseModel):
    """News ingestion configuration"""
    max_articles: int = Field(default=int(os.getenv("MAX_NEWS_ARTICLES", "100")))
    lookback_days: int = Field(default=int(os.getenv("NEWS_LOOKBACK_DAYS", "30")))
    sources: list[str] = Field(
        default=[
            "reuters",
            "bloomberg",
            "financial-times",
            "the-wall-street-journal",
            "cnbc",
        ]
    )


class APIKeys(BaseModel):
    """API keys configuration"""
    openai: str = Field(default=os.getenv("OPENAI_API_KEY", ""))
    anthropic: str = Field(default=os.getenv("ANTHROPIC_API_KEY", ""))
    cohere: str = Field(default=os.getenv("COHERE_API_KEY", ""))
    news_api: str = Field(default=os.getenv("NEWS_API_KEY", ""))
    alpha_vantage: str = Field(default=os.getenv("ALPHA_VANTAGE_API_KEY", ""))


class AppConfig(BaseModel):
    """Main application configuration"""
    llm: LLMConfig = Field(default_factory=LLMConfig)
    embedding: EmbeddingConfig = Field(default_factory=EmbeddingConfig)
    rag: RAGConfig = Field(default_factory=RAGConfig)
    news: NewsConfig = Field(default_factory=NewsConfig)
    api_keys: APIKeys = Field(default_factory=APIKeys)

    # Paths
    base_dir: Path = Field(default=Path(__file__).parent.parent.parent)
    data_dir: Path = Field(default=Path(__file__).parent.parent.parent / "data")
    chroma_dir: Path = Field(
        default=Path(os.getenv("CHROMA_PERSIST_DIRECTORY", "./data/chroma_db"))
    )


# Global config instance
config = AppConfig()
