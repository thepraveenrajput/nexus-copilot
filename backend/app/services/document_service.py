from sqlalchemy.orm import Session

from app.models.document import Document


def get_document_by_filename(
    db: Session,
    filename: str,
):
    return (
        db.query(Document)
        .filter(Document.filename == filename)
        .first()
    )