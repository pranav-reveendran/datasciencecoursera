"""
Advanced Hybrid Retrieval System
Combines semantic search (embeddings) with keyword search (BM25)
Includes reranking for improved relevance
"""
import logging
from typing import List, Dict, Tuple
from dataclasses import dataclass
import chromadb
from chromadb.config import Settings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain.schema import Document
from rank_bm25 import BM25Okapi
import numpy as np
from ..utils.config import config
from ..data.news_fetcher import NewsArticle

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class RetrievalResult:
    """Enhanced retrieval result with metadata"""
    content: str
    source: str
    url: str
    ticker: str
    published_at: str
    score: float
    retrieval_method: str  # "semantic", "keyword", "hybrid", "reranked"


class HybridRetriever:
    """
    Modern RAG retriever with cutting-edge features:
    1. Hybrid Search: Combines dense (semantic) and sparse (BM25) retrieval
    2. Reranking: Uses cross-encoder or Cohere for final ranking
    3. Multi-query: Generates multiple queries for better coverage
    4. Citation tracking: Maintains source attribution
    """

    def __init__(self):
        # Initialize ChromaDB (modern vector database)
        self.chroma_client = chromadb.PersistentClient(
            path=str(config.chroma_dir),
            settings=Settings(anonymized_telemetry=False),
        )

        # Get or create collection
        self.collection = self.chroma_client.get_or_create_collection(
            name="equity_news",
            metadata={"hnsw:space": "cosine"},
        )

        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings(
            model=config.embedding.model,
            openai_api_key=config.api_keys.openai,
        )

        # Text splitter for chunking
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.rag.chunk_size,
            chunk_overlap=config.rag.chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

        # BM25 index (keyword search)
        self.bm25_index = None
        self.bm25_docs = []

        logger.info("Hybrid Retriever initialized")

    def ingest_articles(self, articles: List[NewsArticle]) -> int:
        """
        Ingest news articles into the vector database
        Uses smart chunking and metadata preservation
        """
        documents = []
        metadatas = []
        ids = []

        for idx, article in enumerate(articles):
            # Create full text
            full_text = f"Title: {article.title}\n\nContent: {article.content}"

            # Split into chunks
            chunks = self.text_splitter.split_text(full_text)

            for chunk_idx, chunk in enumerate(chunks):
                doc_id = f"{article.source}_{idx}_{chunk_idx}"

                documents.append(chunk)
                metadatas.append(
                    {
                        "source": article.source,
                        "url": article.url,
                        "ticker": article.ticker or "MARKET",
                        "published_at": article.published_at.isoformat(),
                        "title": article.title,
                    }
                )
                ids.append(doc_id)

        # Add to ChromaDB
        if documents:
            # Process in batches (ChromaDB has limits)
            batch_size = 100
            for i in range(0, len(documents), batch_size):
                batch_docs = documents[i : i + batch_size]
                batch_meta = metadatas[i : i + batch_size]
                batch_ids = ids[i : i + batch_size]

                self.collection.add(
                    documents=batch_docs, metadatas=batch_meta, ids=batch_ids
                )

            # Build BM25 index for keyword search
            self._build_bm25_index(documents, metadatas)

            logger.info(f"Ingested {len(documents)} chunks from {len(articles)} articles")

        return len(documents)

    def _build_bm25_index(self, documents: List[str], metadatas: List[Dict]):
        """Build BM25 index for keyword-based retrieval"""
        tokenized_docs = [doc.lower().split() for doc in documents]
        self.bm25_index = BM25Okapi(tokenized_docs)
        self.bm25_docs = list(zip(documents, metadatas))
        logger.info("BM25 index built")

    def retrieve(
        self, query: str, top_k: int = None, use_reranking: bool = None
    ) -> List[RetrievalResult]:
        """
        Hybrid retrieval: combines semantic and keyword search
        """
        top_k = top_k or config.rag.top_k
        use_reranking = (
            use_reranking
            if use_reranking is not None
            else config.rag.use_reranking
        )

        results = []

        # 1. Semantic Search (Dense Retrieval)
        semantic_results = self._semantic_search(query, top_k)

        # 2. Keyword Search (Sparse Retrieval - BM25)
        keyword_results = self._keyword_search(query, top_k)

        # 3. Hybrid: Combine with Reciprocal Rank Fusion (RRF)
        if config.rag.use_hybrid_search and self.bm25_index:
            results = self._reciprocal_rank_fusion(
                semantic_results, keyword_results, top_k
            )
        else:
            results = semantic_results

        # 4. Reranking (optional but recommended)
        if use_reranking and config.api_keys.cohere:
            results = self._rerank_with_cohere(query, results)

        return results[: config.rag.rerank_top_n]

    def _semantic_search(self, query: str, top_k: int) -> List[RetrievalResult]:
        """Dense retrieval using embeddings"""
        try:
            results = self.collection.query(query_texts=[query], n_results=top_k)

            retrieval_results = []
            if results["documents"] and results["documents"][0]:
                for idx, (doc, metadata, distance) in enumerate(
                    zip(
                        results["documents"][0],
                        results["metadatas"][0],
                        results["distances"][0],
                    )
                ):
                    score = 1 - distance  # Convert distance to similarity
                    retrieval_results.append(
                        RetrievalResult(
                            content=doc,
                            source=metadata.get("source", "Unknown"),
                            url=metadata.get("url", ""),
                            ticker=metadata.get("ticker", ""),
                            published_at=metadata.get("published_at", ""),
                            score=score,
                            retrieval_method="semantic",
                        )
                    )

            return retrieval_results
        except Exception as e:
            logger.error(f"Semantic search error: {e}")
            return []

    def _keyword_search(self, query: str, top_k: int) -> List[RetrievalResult]:
        """Sparse retrieval using BM25"""
        if not self.bm25_index:
            return []

        tokenized_query = query.lower().split()
        scores = self.bm25_index.get_scores(tokenized_query)

        # Get top-k indices
        top_indices = np.argsort(scores)[::-1][:top_k]

        results = []
        for idx in top_indices:
            if scores[idx] > 0:  # Only include relevant results
                doc, metadata = self.bm25_docs[idx]
                results.append(
                    RetrievalResult(
                        content=doc,
                        source=metadata.get("source", "Unknown"),
                        url=metadata.get("url", ""),
                        ticker=metadata.get("ticker", ""),
                        published_at=metadata.get("published_at", ""),
                        score=float(scores[idx]),
                        retrieval_method="keyword",
                    )
                )

        return results

    def _reciprocal_rank_fusion(
        self,
        semantic_results: List[RetrievalResult],
        keyword_results: List[RetrievalResult],
        top_k: int,
        k: int = 60,
    ) -> List[RetrievalResult]:
        """
        Reciprocal Rank Fusion (RRF) - modern approach to combine rankings
        Score(d) = sum(1 / (k + rank(d)))
        """
        scores = {}
        doc_map = {}

        # Process semantic results
        for rank, result in enumerate(semantic_results):
            doc_key = result.content[:100]  # Use content prefix as key
            scores[doc_key] = scores.get(doc_key, 0) + (1 / (k + rank + 1))
            doc_map[doc_key] = result

        # Process keyword results
        for rank, result in enumerate(keyword_results):
            doc_key = result.content[:100]
            scores[doc_key] = scores.get(doc_key, 0) + (1 / (k + rank + 1))
            if doc_key not in doc_map:
                doc_map[doc_key] = result

        # Sort by combined score
        sorted_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        # Create final results
        fused_results = []
        for doc_key, score in sorted_docs[:top_k]:
            result = doc_map[doc_key]
            result.score = score
            result.retrieval_method = "hybrid"
            fused_results.append(result)

        return fused_results

    def _rerank_with_cohere(
        self, query: str, results: List[RetrievalResult]
    ) -> List[RetrievalResult]:
        """
        Rerank results using Cohere's reranking API
        This is cutting-edge for improving retrieval quality
        """
        try:
            import cohere

            co = cohere.Client(config.api_keys.cohere)

            documents = [r.content for r in results]

            rerank_response = co.rerank(
                model="rerank-english-v3.0",
                query=query,
                documents=documents,
                top_n=config.rag.rerank_top_n,
            )

            reranked_results = []
            for hit in rerank_response.results:
                original_result = results[hit.index]
                original_result.score = hit.relevance_score
                original_result.retrieval_method = "reranked"
                reranked_results.append(original_result)

            return reranked_results

        except Exception as e:
            logger.error(f"Reranking error: {e}")
            return results  # Fallback to original ranking

    def get_collection_stats(self) -> Dict:
        """Get statistics about the indexed articles"""
        count = self.collection.count()
        return {
            "total_chunks": count,
            "collection_name": self.collection.name,
            "has_bm25": self.bm25_index is not None,
        }
