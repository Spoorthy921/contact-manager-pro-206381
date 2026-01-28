from __future__ import annotations

import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from ..auth import get_current_user
from ..db import get_db
from ..models import Contact, User
from .. import schemas

router = APIRouter()


def _contact_owned_or_404(db: Session, *, contact_id: uuid.UUID, user_id: uuid.UUID) -> Contact:
    contact = db.scalar(select(Contact).where(Contact.id == contact_id, Contact.user_id == user_id))
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


@router.get(
    "",
    response_model=List[schemas.ContactOut],
    summary="List contacts",
    description="List all contacts for the authenticated user. Supports simple search via `q`.",
    operation_id="contacts_list",
)
def list_contacts(
    q: Optional[str] = Query(None, description="Search query across name/phone/email/address."),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> List[schemas.ContactOut]:
    """List or search contacts for current user."""
    stmt = select(Contact).where(Contact.user_id == current_user.id)

    if q:
        like = f"%{q.strip()}%"
        stmt = stmt.where(
            or_(
                Contact.name.ilike(like),
                Contact.phone.ilike(like),
                Contact.email.ilike(like),
                Contact.address.ilike(like),
            )
        )

    stmt = stmt.order_by(Contact.name.asc())
    return list(db.scalars(stmt).all())


@router.post(
    "",
    response_model=schemas.ContactOut,
    summary="Create contact",
    description="Create a contact for the authenticated user.",
    operation_id="contacts_create",
)
def create_contact(
    payload: schemas.ContactCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> schemas.ContactOut:
    """Create a contact."""
    contact = Contact(
        user_id=current_user.id,
        name=payload.name.strip(),
        phone=payload.phone,
        email=str(payload.email) if payload.email else None,
        address=payload.address,
    )
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


@router.get(
    "/{contact_id}",
    response_model=schemas.ContactOut,
    summary="Get contact",
    description="Get a single contact by id (must belong to the authenticated user).",
    operation_id="contacts_get",
)
def get_contact(
    contact_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> schemas.ContactOut:
    """Get a contact."""
    return _contact_owned_or_404(db, contact_id=contact_id, user_id=current_user.id)


@router.put(
    "/{contact_id}",
    response_model=schemas.ContactOut,
    summary="Update contact",
    description="Update a contact (must belong to the authenticated user).",
    operation_id="contacts_update",
)
def update_contact(
    contact_id: uuid.UUID,
    payload: schemas.ContactUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> schemas.ContactOut:
    """Update a contact."""
    contact = _contact_owned_or_404(db, contact_id=contact_id, user_id=current_user.id)

    if payload.name is not None:
        contact.name = payload.name.strip()
    if payload.phone is not None:
        contact.phone = payload.phone
    if payload.email is not None:
        contact.email = str(payload.email)
    if payload.address is not None:
        contact.address = payload.address

    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


@router.delete(
    "/{contact_id}",
    status_code=204,
    summary="Delete contact",
    description="Delete a contact (must belong to the authenticated user).",
    operation_id="contacts_delete",
)
def delete_contact(
    contact_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Delete a contact."""
    contact = _contact_owned_or_404(db, contact_id=contact_id, user_id=current_user.id)
    db.delete(contact)
    db.commit()
    return None
