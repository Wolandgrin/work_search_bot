import logging

from mcp.server.fastmcp import FastMCP

from core.aggregator import search_jobs

logger = logging.getLogger(__name__)

mcp = FastMCP("freelance-search")


@mcp.tool()
async def search_freelance_jobs(
    query: str,
    sources: list[str] | None = None,
    limit_per_source: int = 30,
    keywords: list[str] | None = None,
) -> list[dict]:
    """Search freelance/remote job boards and permanent job vacancies.

    query: free-text search term, e.g. "python automation qa"
    sources: subset of ["remotive", "remoteok", "weworkremotely", "flru",
        "guru", "freelancehunt", "jobscz", "nofluffjobs", "justjoin"], default all
    limit_per_source: max results fetched per source before filtering
    keywords: optional keyword filter applied to title/description/tags
    """
    jobs = await search_jobs(
        query=query,
        sources=sources,
        limit_per_source=limit_per_source,
        keywords=keywords,
    )
    return [job.model_dump(mode="json") for job in jobs]


if __name__ == "__main__":
    mcp.run()
