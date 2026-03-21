from fastapi import APIRouter, Query, HTTPException
from app.services.vector_space import search_service

router = APIRouter(tags=["Search"])

@router.get("/search")
async def search(
    q: str = Query(..., description="Query string"),
    type: str = Query("keyword", enum=["keyword", "phrase"], description="Search type (keyword or phrase)")
):
    """
    Search endpoint:
    - Filters document IDs by keyword presence or phrase order.
    - Calculates rankings (Cosine Similarity + TF-IDF) only for matched documents.
    """
    try:
        results = search_service.search(q, query_type=type)
        return {
            "query": q,
            "type": type,
            "total": len(results),
            "results": results
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reindex")
async def reindex():
    """
    Updates the index to a Positional Index using the current dataset and VnCoreNLP.
    """
    try:
        search_service.build_index()
        return {"message": "Indexing completed successfully."}
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
