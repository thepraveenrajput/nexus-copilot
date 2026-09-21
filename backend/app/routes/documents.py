from pathlib import Path

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.db.qdrant import qdrant_client
from app.db.qdrant_documents import delete_document_chunks

from app.models.document import Document

from app.services.ingest_document import ingest_document

from app.core.dependencies import get_current_user


router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)


UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# UPLOAD DOCUMENT

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # VALIDATE FILE TYPE

    if not file.filename:
        return {
            "message": "Filename is required."
        }

    allowed_extensions = {
        ".pdf",
        ".docx",
    }

    safe_filename = Path(file.filename).name

    file_extension = Path(
        safe_filename
    ).suffix.lower()

    if file_extension not in allowed_extensions:
        return {
            "message": "Unsupported file type",
            "filename": safe_filename,
        }

    # USER-SPECIFIC STORAGE DIRECTORY

    user_upload_dir = (
        UPLOAD_DIR / str(current_user.id)
    )

    user_upload_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    # HANDLE EXISTING DOCUMENT

    existing_document = (
        db.query(Document)
        .filter(
            Document.filename == safe_filename,
            Document.uploaded_by == current_user.id,
        )
        .first()
    )

    if existing_document:

        # Remove old vectors
        delete_document_chunks(
            qdrant_client=qdrant_client,
            document_id=existing_document.id,
        )

        # Remove old physical file
        old_file_path = (
            UPLOAD_DIR
            / str(current_user.id)
            / f"{existing_document.id}_{existing_document.filename}"
        )

        if old_file_path.exists():
            old_file_path.unlink()

        # Remove old DB record
        db.delete(existing_document)
        db.commit()

    # CREATE DOCUMENT RECORD FIRST

    document = Document(
        filename=safe_filename,
        file_type=file_extension,
        uploaded_by=current_user.id,
        status="processing",
        qdrant_collection="nexus_documents",
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    # PHYSICAL FILE PATH

    file_path = (
        user_upload_dir
        / f"{document.id}_{safe_filename}"
    )

    # SAVE FILE

    try:
        file_content = await file.read()

        if not file_content:
            db.delete(document)
            db.commit()

            return {
                "message": "Uploaded file is empty.",
                "filename": safe_filename,
            }

        with open(file_path, "wb") as buffer:
            buffer.write(file_content)

    except Exception as e:

        document.status = "failed"
        db.commit()

        return {
            "message": "Failed to save uploaded file.",
            "filename": safe_filename,
            "error": str(e),
        }

    # INGEST DOCUMENT

    try:

        chunk_count = ingest_document(
            file_path=str(file_path),
            document_id=document.id,
            user_id=current_user.id,
        )

        document.status = "indexed"

        db.commit()
        db.refresh(document)

    except Exception as e:

        # ----------------------------------------------
        # CLEAN PARTIAL QDRANT DATA
        # ----------------------------------------------

        try:
            delete_document_chunks(
                qdrant_client=qdrant_client,
                document_id=document.id,
            )

        except Exception as cleanup_error:
            print(
                "Qdrant cleanup failed:",
                cleanup_error,
            )

        # ----------------------------------------------
        # CLEAN PHYSICAL FILE
        # ----------------------------------------------

        try:
            if file_path.exists():
                file_path.unlink()
        except Exception as cleanup_error:
            print(
                "File cleanup failed:",
                cleanup_error,
            )

        # ----------------------------------------------
        # MARK DOCUMENT FAILED
        # ----------------------------------------------

        document.status = "failed"

        db.commit()
        db.refresh(document)

        return {
            "message": "Document processing failed",
            "document_id": document.id,
            "filename": document.filename,
            "status": document.status,
            "error": str(e),
        }

    # SUCCESS

    return {
        "message": (
            "Document uploaded and indexed successfully"
        ),
        "document_id": document.id,
        "filename": document.filename,
        "file_type": document.file_type,
        "status": document.status,
        "chunks": chunk_count,
    }


# LIST DOCUMENTS

@router.get("")
def list_documents(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    documents = (
        db.query(Document)
        .filter(
            Document.uploaded_by == current_user.id
        )
        .order_by(Document.created_at.desc())
        .all()
    )

    return [
        {
            "id": document.id,
            "filename": document.filename,
            "file_type": document.file_type,
            "status": document.status,
            "qdrant_collection": (
                document.qdrant_collection
            ),
            "created_at": document.created_at,
        }
        for document in documents
    ]


# DELETE DOCUMENT

@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    document = (
        db.query(Document)
        .filter(
            Document.id == document_id,
            Document.uploaded_by == current_user.id,
        )
        .first()
    )

    if not document:
        return {
            "message": "Document not found",
            "document_id": document_id,
        }

    # DELETE QDRANT VECTORS

    delete_document_chunks(
        qdrant_client=qdrant_client,
        document_id=document.id,
    )

    # DELETE PHYSICAL FILE

    file_path = (
        UPLOAD_DIR
        / str(current_user.id)
        / f"{document.id}_{document.filename}"
    )

    if file_path.exists():
        file_path.unlink()

    # DELETE DATABASE RECORD

    db.delete(document)
    db.commit()

    return {
        "message": "Document deleted successfully",
        "document_id": document_id,
    }