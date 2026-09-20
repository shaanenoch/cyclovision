from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import List, Dict, Any
from backend.services.dataset_service import process_uploaded_dataset, get_all_datasets, run_analysis_on_dataset_id

router = APIRouter()

@router.post("/datasets/upload")
async def upload_dataset(
    file: UploadFile = File(...),
    purpose: str = Form("Live/New Cyclone Observation")
):
    """
    Accepts .csv, .json, .nc, .png, .jpg, .jpeg, .tif without code modification.
    """
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    contents = await file.read()
    result = process_uploaded_dataset(
        file_bytes=contents,
        original_filename=file.filename,
        purpose=purpose
    )
    return result

@router.get("/datasets")
def list_datasets():
    return get_all_datasets()

@router.post("/datasets/{dataset_id}/analyze")
def run_dataset_analysis(dataset_id: str):
    try:
        return run_analysis_on_dataset_id(dataset_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
