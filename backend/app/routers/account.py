from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.database.connection import get_db
from app.models.account import Account
from app.models.user import User
from app.schemas.account import AccountCreate, AccountResponse, AccountUpdate
from app.security.dependencies import get_current_user


router = APIRouter(
    prefix="/accounts",
    tags=["Accounts"],
)

# Create a new account
@router.post(
    "/",
    response_model=AccountResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_account(
    account_data: AccountCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    account = Account(
        user_id=current_user.id,
        name=account_data.name,
        type=account_data.type,
    )

    db.add(account)
    db.commit()
    db.refresh(account)

    return account

# Get all accounts for the current user
@router.get(
    "/",
    response_model=list[AccountResponse],
)
def get_accounts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    accounts = db.scalars(
        select(Account).where(
            Account.user_id == current_user.id,
            Account.is_active.is_(True),
        )
    ).all()

    return accounts

# Get a specific account by ID
@router.get(
    "/{account_id}",
    response_model=AccountResponse,
)
def get_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    account = db.scalar(
        select(Account).where(
            Account.id == account_id,
            Account.user_id == current_user.id,
            Account.is_active.is_(True),
        )
    )

    if account is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found",
        ) 

    return account

# Update a specific account by ID
@router.patch(
    "/{account_id}",
    response_model=AccountResponse,
)
def update_account(
    account_id: int,
    account_data: AccountUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    account = db.scalar(
        select(Account).where(
            Account.id == account_id,
            Account.user_id == current_user.id,
            Account.is_active.is_(True),
        )
    )

    if account is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found",
        )

    update_data = account_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(account, key, value)

    db.commit()
    db.refresh(account)

    return account

# Deactivate a specific account by ID
@router.delete(
    "/{account_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_account(
    account_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    account = db.scalar(
        select(Account).where(
            Account.id == account_id,
            Account.user_id == current_user.id,
            Account.is_active.is_(True),
        )
    )

    if account is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found",
        )

    account.is_active = False
    db.commit()