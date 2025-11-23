"""
Multi-Agent Research System using LangGraph
This is the cutting-edge approach for complex LLM workflows (2024-2025)

Agents:
1. Router: Determines which specialized agent to use
2. Research Agent: Retrieves relevant news and context
3. Analysis Agent: Analyzes financial data and metrics
4. Synthesis Agent: Combines insights into coherent response
"""
import logging
from typing import TypedDict, Annotated, Sequence, Literal
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolExecutor
import operator
from ..utils.config import config
from ..retrieval.hybrid_retriever import HybridRetriever, RetrievalResult
from ..tools.market_tools import MARKET_TOOLS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    """State shared across all agents"""
    messages: Annotated[Sequence[BaseMessage], operator.add]
    query: str
    ticker: str | None
    retrieved_context: list[RetrievalResult]
    market_data: dict
    analysis: str
    final_response: str
    next_agent: str


class EquityResearchSystem:
    """
    Modern multi-agent system for equity research
    Uses LangGraph for orchestration (2024-2025 cutting edge)
    """

    def __init__(self, retriever: HybridRetriever):
        self.retriever = retriever

        # Initialize LLM based on config
        if config.llm.provider == "openai":
            self.llm = ChatOpenAI(
                model=config.llm.model,
                temperature=config.llm.temperature,
                streaming=config.llm.streaming,
                openai_api_key=config.api_keys.openai,
            )
        else:
            self.llm = ChatAnthropic(
                model=config.llm.model,
                temperature=config.llm.temperature,
                anthropic_api_key=config.api_keys.anthropic,
            )

        # LLM with tools for market data
        self.tool_executor = ToolExecutor(MARKET_TOOLS)
        self.llm_with_tools = self.llm.bind_tools(MARKET_TOOLS)

        # Build the agent graph
        self.graph = self._build_graph()

        logger.info(f"Equity Research System initialized with {config.llm.provider}")

    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph workflow
        This is the modern approach to agent orchestration
        """
        workflow = StateGraph(AgentState)

        # Add nodes (agents)
        workflow.add_node("router", self._router_agent)
        workflow.add_node("research", self._research_agent)
        workflow.add_node("analysis", self._analysis_agent)
        workflow.add_node("synthesis", self._synthesis_agent)

        # Define the flow
        workflow.set_entry_point("router")

        workflow.add_conditional_edges(
            "router",
            lambda state: state["next_agent"],
            {
                "research": "research",
                "analysis": "analysis",
                "synthesis": "synthesis",
            }
        )

        workflow.add_edge("research", "analysis")
        workflow.add_edge("analysis", "synthesis")
        workflow.add_edge("synthesis", END)

        return workflow.compile()

    def _router_agent(self, state: AgentState) -> AgentState:
        """
        Router agent: Determines the workflow path
        """
        query = state["query"]

        # Simple routing logic (can be made more sophisticated with LLM classification)
        if any(word in query.lower() for word in ["news", "article", "recent", "latest"]):
            state["next_agent"] = "research"
        elif any(word in query.lower() for word in ["price", "value", "compare", "financial"]):
            state["next_agent"] = "analysis"
        else:
            state["next_agent"] = "research"  # Default to research

        logger.info(f"Router: Directing to {state['next_agent']} agent")
        return state

    def _research_agent(self, state: AgentState) -> AgentState:
        """
        Research Agent: Retrieves relevant news and context using hybrid search
        """
        query = state["query"]

        # Retrieve relevant context
        results = self.retriever.retrieve(query, top_k=config.rag.top_k)
        state["retrieved_context"] = results

        # Create context message
        context_msg = self._format_context(results)

        state["messages"].append(
            AIMessage(content=f"Research Agent: Retrieved {len(results)} relevant sources")
        )

        logger.info(f"Research Agent: Retrieved {len(results)} sources")
        return state

    def _analysis_agent(self, state: AgentState) -> AgentState:
        """
        Analysis Agent: Analyzes market data and fundamentals
        Uses tool calling to get real-time data
        """
        query = state["query"]
        ticker = state.get("ticker")

        # If ticker mentioned, get market data
        if ticker:
            try:
                from ..tools.market_tools import get_stock_price, get_company_info

                price_data = get_stock_price.invoke({"ticker": ticker})
                company_info = get_company_info.invoke({"ticker": ticker})

                state["market_data"] = {
                    "price": price_data,
                    "company": company_info,
                }

                state["messages"].append(
                    AIMessage(
                        content=f"Analysis Agent: Retrieved market data for {ticker}"
                    )
                )
            except Exception as e:
                logger.error(f"Error in analysis agent: {e}")
                state["market_data"] = {}
        else:
            state["market_data"] = {}

        logger.info("Analysis Agent: Market analysis complete")
        return state

    def _synthesis_agent(self, state: AgentState) -> AgentState:
        """
        Synthesis Agent: Combines research and analysis into final response
        This is where the magic happens!
        """
        query = state["query"]
        context = state.get("retrieved_context", [])
        market_data = state.get("market_data", {})

        # Build comprehensive prompt
        system_prompt = """You are an expert equity research analyst.
Your task is to provide comprehensive, accurate, and well-sourced insights about stocks and markets.

Guidelines:
1. Base your analysis on the provided news context and market data
2. Always cite your sources with [Source: X]
3. Provide balanced perspectives (bullish and bearish factors)
4. Include specific metrics and data points
5. If information is missing, clearly state that
6. Be precise with numbers and dates
7. Structure your response clearly with sections

Remember: You are helping professional investors make informed decisions."""

        # Format context
        context_text = self._format_context_for_llm(context)

        # Format market data
        market_text = self._format_market_data(market_data)

        # Create the synthesis prompt
        user_prompt = f"""Question: {query}

## Relevant News Context:
{context_text}

## Market Data:
{market_text}

Please provide a comprehensive analysis that:
1. Directly answers the question
2. Incorporates insights from the news articles
3. Includes relevant market data and metrics
4. Cites all sources
5. Provides actionable insights

Analysis:"""

        # Generate response
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ]

        response = self.llm.invoke(messages)

        state["final_response"] = response.content
        state["messages"].append(AIMessage(content=response.content))

        logger.info("Synthesis Agent: Final response generated")
        return state

    def _format_context(self, results: list[RetrievalResult]) -> str:
        """Format retrieval results for display"""
        if not results:
            return "No relevant context found."

        formatted = []
        for idx, result in enumerate(results, 1):
            formatted.append(
                f"{idx}. [{result.source}] {result.ticker} - Score: {result.score:.3f}\n"
                f"   {result.content[:200]}...\n"
                f"   URL: {result.url}\n"
            )

        return "\n".join(formatted)

    def _format_context_for_llm(self, results: list[RetrievalResult]) -> str:
        """Format context for LLM consumption"""
        if not results:
            return "No relevant news articles found."

        formatted = []
        for idx, result in enumerate(results, 1):
            formatted.append(
                f"[Source {idx}: {result.source} - {result.published_at[:10]}]\n"
                f"{result.content}\n"
                f"URL: {result.url}\n"
            )

        return "\n---\n".join(formatted)

    def _format_market_data(self, market_data: dict) -> str:
        """Format market data for LLM"""
        if not market_data:
            return "No real-time market data available."

        formatted = []

        if "price" in market_data:
            price = market_data["price"]
            formatted.append(f"Current Price: ${price.get('current_price', 'N/A')}")
            formatted.append(f"Previous Close: ${price.get('previous_close', 'N/A')}")
            formatted.append(f"Market Cap: ${price.get('market_cap', 'N/A'):,}")
            formatted.append(f"P/E Ratio: {price.get('pe_ratio', 'N/A')}")

        if "company" in market_data:
            company = market_data["company"]
            formatted.append(f"\nCompany: {company.get('name', 'N/A')}")
            formatted.append(f"Sector: {company.get('sector', 'N/A')}")
            formatted.append(f"Industry: {company.get('industry', 'N/A')}")

        return "\n".join(formatted)

    def research(self, query: str, ticker: str = None) -> dict:
        """
        Main entry point for equity research
        """
        initial_state = AgentState(
            messages=[HumanMessage(content=query)],
            query=query,
            ticker=ticker,
            retrieved_context=[],
            market_data={},
            analysis="",
            final_response="",
            next_agent="",
        )

        # Run the agent graph
        final_state = self.graph.invoke(initial_state)

        return {
            "response": final_state["final_response"],
            "sources": final_state["retrieved_context"],
            "market_data": final_state["market_data"],
            "messages": final_state["messages"],
        }

    async def research_stream(self, query: str, ticker: str = None):
        """
        Streaming version for real-time responses
        """
        initial_state = AgentState(
            messages=[HumanMessage(content=query)],
            query=query,
            ticker=ticker,
            retrieved_context=[],
            market_data={},
            analysis="",
            final_response="",
            next_agent="",
        )

        # Stream the graph execution
        async for state in self.graph.astream(initial_state):
            yield state
