from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, or_
from sqlalchemy.orm import Session
from datetime import date, datetime, time

from app.database.connection import get_db
from app.models.account import Account
from app.models.transaction import Transaction, TransactionType
from app.models.user import User
from app.models.category import Category
from app.schemas.transaction import TransactionCreate, TransactionResponse, TransactionUpdate
from app.security.dependencies import get_current_user


router = APIRouter(
    prefix="/transactions",
    tags=["Transactions"],
)

# Create a new transaction
@router.post(
    "/",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_transaction(
    transaction_data: TransactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if transaction_data.type == TransactionType.TRANSFER:
        if transaction_data.category_id is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="TRANSFER transactions cannot have a category",
            )
        
    elif transaction_data.category_id is not None:
        category = db.scalar(
            select(Category).where(
                Category.id == transaction_data.category_id,
                Category.is_active.is_(True),
            )
        )

        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found",
            )

        if transaction_data.type != category.type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Transaction type does not match category type",
            )


    if transaction_data.type not in (
        TransactionType.INCOME,
        TransactionType.EXPENSE,
        TransactionType.TRANSFER,
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid transaction type. Must be INCOME, EXPENSE, or TRANSFER",
        )

    if transaction_data.type == TransactionType.INCOME:
        if transaction_data.destination_account_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="INCOME requires a destination account",
            )

        account = db.scalar(
            select(Account).where(
                Account.id == transaction_data.destination_account_id,
                Account.user_id == current_user.id,
                Account.is_active.is_(True),
            )
        )

        if account is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Destination account not found",
            )

        account.balance += transaction_data.amount 

    elif transaction_data.type == TransactionType.TRANSFER:
        if transaction_data.source_account_id is None or transaction_data.destination_account_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="TRANSFER requires both source and destination accounts",
            )

        if transaction_data.source_account_id == transaction_data.destination_account_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Source and destination accounts cannot be the same",
            )

        source_account = db.scalar(
            select(Account).where(
                Account.id == transaction_data.source_account_id,
                Account.user_id == current_user.id,
                Account.is_active.is_(True),
            )
        )

        destination_account = db.scalar(
            select(Account).where(
                Account.id == transaction_data.destination_account_id,
                Account.user_id == current_user.id,
                Account.is_active.is_(True),
            )
        )

        if source_account is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Source account not found",
            )

        if destination_account is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Destination account not found",
            )

        if source_account.balance < transaction_data.amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient funds in source account",
            )

        source_account.balance -= transaction_data.amount
        destination_account.balance += transaction_data.amount

    else:
        if transaction_data.source_account_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="EXPENSE requires a source account",
            )

        account = db.scalar(
            select(Account).where(
                Account.id == transaction_data.source_account_id,
                Account.user_id == current_user.id,
                Account.is_active.is_(True),
            )
        )

        if account is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Source account not found",
            )

        if account.balance < transaction_data.amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient funds",
            )

        account.balance -= transaction_data.amount

    transaction = Transaction(
        user_id=current_user.id,
        category_id=transaction_data.category_id,
        source_account_id=transaction_data.source_account_id,
        destination_account_id=transaction_data.destination_account_id,
        type=transaction_data.type,
        amount=transaction_data.amount,
        description=transaction_data.description,
        transaction_date=transaction_data.transaction_date,
    )

    try:
        db.add(transaction)
        db.commit()
        db.refresh(transaction)

    except Exception:
        db.rollback()
        raise

    return transaction

# Get all transactions for the current user
@router.get("/", response_model=list[TransactionResponse])
def get_transactions(
    type: TransactionType | None = Query(default=None),
    account_id: int | None = Query(default=None),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = select(Transaction).where(
        Transaction.user_id == current_user.id
    )

    if type is not None:
        query = query.where(
            Transaction.type == type
        )

    if account_id is not None:
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
        query = query.where(
            or_(
                Transaction.source_account_id == account_id,
                Transaction.destination_account_id == account_id,
            )
        )

    if start_date is not None and end_date is not None and start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_date cannot be after end_date",
        )

    if start_date is not None:
        start_datetime = datetime.combine(start_date, time.min)
        query = query.where(
            Transaction.transaction_date >= start_datetime
        )

    if end_date is not None:
        end_datetime = datetime.combine(end_date, time.max)
        query = query.where(
            Transaction.transaction_date <= end_datetime
        )

    transactions = db.scalars(query).all()

    return transactions

# Get a specific transaction by ID
@router.get("/{transaction_id}", response_model=TransactionResponse)
def get_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    transaction = db.scalar(
        select(Transaction).where(
            Transaction.id == transaction_id,
            Transaction.user_id == current_user.id,
        )
    )

    if transaction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )

    return transaction

# Update a specific transaction by ID
@router.patch("/{transaction_id}", response_model=TransactionResponse)
def update_transaction(
    transaction_id: int,
    transaction_data: TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Fetch the transaction to be updated
    transaction = db.scalar(
        select(Transaction).where(
            Transaction.id == transaction_id,
            Transaction.user_id == current_user.id,
        )
    )

    if transaction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )

    # Determine the new values for the transaction fields, using the provided data or keeping the existing values if not provided
    new_type = (
        transaction_data.type 
        if transaction_data.type is not None 
        else transaction.type
    )

    new_category_id = (
        transaction_data.category_id 
        if "category_id" in transaction_data.model_fields_set 
        else transaction.category_id
    )

    new_amount = (
        transaction_data.amount 
        if transaction_data.amount is not None 
        else transaction.amount
    )

    new_source_account_id = (
        transaction_data.source_account_id
        if "source_account_id" in transaction_data.model_fields_set
        else transaction.source_account_id
    )

    new_destination_account_id = (
        transaction_data.destination_account_id
        if "destination_account_id" in transaction_data.model_fields_set
        else transaction.destination_account_id
    )

    # Validate the new category and account IDs based on the new transaction type
    if new_type == TransactionType.TRANSFER:
        if new_category_id is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="TRANSFER transactions cannot have a category",
            )

    elif new_category_id is not None:
        category = db.scalar(
            select(Category).where(
                Category.id == new_category_id,
                Category.is_active.is_(True),
            )
        )

        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found",
            )

        if category.type != new_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Transaction type does not match category type",
            )
    if new_type == TransactionType.INCOME:
        if new_destination_account_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="INCOME requires a destination account",
            )

    elif new_type == TransactionType.EXPENSE:
        if new_source_account_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="EXPENSE requires a source account",
            )

    elif new_type == TransactionType.TRANSFER:
        if new_source_account_id is None or new_destination_account_id is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="TRANSFER requires both source and destination accounts",
            )

        if new_source_account_id == new_destination_account_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Source and destination accounts cannot be the same",
            )

    # Adjust the balances of the involved accounts based on the old and new transaction details
    source_account = None
    destination_account = None

    if new_source_account_id is not None:
        source_account = db.scalar(
            select(Account).where(
                Account.id == new_source_account_id,
                Account.user_id == current_user.id,
                Account.is_active.is_(True),
            )
        )
        if source_account is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Source account not found",
            )

    if new_destination_account_id is not None:
        destination_account = db.scalar(
            select(Account).where(
                Account.id == new_destination_account_id,
                Account.user_id == current_user.id,
                Account.is_active.is_(True),
            )
        )
        if destination_account is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Destination account not found",
            )

    old_source_account = None
    old_destination_account = None

    if transaction.source_account_id is not None:
        old_source_account = db.scalar(
            select(Account).where(
                Account.id == transaction.source_account_id,
                Account.user_id == current_user.id,
            )
        )

        if old_source_account is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Source account not found",
            )

    if transaction.destination_account_id is not None:
        old_destination_account = db.scalar(
            select(Account).where(
                Account.id == transaction.destination_account_id,
                Account.user_id == current_user.id,
            )
        )

        if old_destination_account is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Destination account not found",
            )

    if transaction.type == TransactionType.INCOME:
        if old_destination_account is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Destination account not found",
            )

        old_destination_account.balance -= transaction.amount

    elif transaction.type == TransactionType.EXPENSE:
        if old_source_account is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Source account not found",
            )

        old_source_account.balance += transaction.amount

    elif transaction.type == TransactionType.TRANSFER:
        if old_source_account is None or old_destination_account is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Source or destination account not found",
            )

        old_source_account.balance += transaction.amount
        old_destination_account.balance -= transaction.amount

    transaction.type = new_type
    transaction.amount = new_amount
    transaction.source_account_id = new_source_account_id
    transaction.destination_account_id = new_destination_account_id

    if "category_id" in transaction_data.model_fields_set:
        transaction.category_id = transaction_data.category_id

    if transaction_data.description is not None:
        transaction.description = transaction_data.description

    if transaction_data.transaction_date is not None:
        transaction.transaction_date = transaction_data.transaction_date

    if new_type == TransactionType.INCOME:
        if destination_account is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Destination account not found",
            )

        destination_account.balance += new_amount

    elif new_type == TransactionType.EXPENSE:
        if source_account is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Source account not found",
            )

        if source_account.balance < new_amount:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient funds",
            )

        source_account.balance -= new_amount

    elif new_type == TransactionType.TRANSFER:
        if source_account is None or destination_account is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Source or destination account not found",
            )

        if source_account.balance < new_amount:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient funds",
            )

        source_account.balance -= new_amount
        destination_account.balance += new_amount    

    try:
        db.commit()
        db.refresh(transaction)
    except Exception:
        db.rollback()
        raise

    return transaction

# Delete a specific transaction by ID
@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    transaction = db.scalar(
        select(Transaction).where(
            Transaction.id == transaction_id,
            Transaction.user_id == current_user.id,
        )
    )

    if transaction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )

    source_account = None
    destination_account = None

    if transaction.source_account_id is not None:
        source_account = db.scalar(
            select(Account).where(
                Account.id == transaction.source_account_id,
                Account.user_id == current_user.id,
            )
        )

        if source_account is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Source account not found",
            )

    if transaction.destination_account_id is not None:
        destination_account = db.scalar(
            select(Account).where(
                Account.id == transaction.destination_account_id,
                Account.user_id == current_user.id,
            )
        )

        if destination_account is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Destination account not found",
            )

    if transaction.type == TransactionType.INCOME:
        if destination_account is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Destination account not found",
            )

        destination_account.balance -= transaction.amount

    elif transaction.type == TransactionType.EXPENSE:
        if source_account is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Source account not found",
            )

        source_account.balance += transaction.amount

    elif transaction.type == TransactionType.TRANSFER:
        if source_account is None or destination_account is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Source or destination account not found",
            )

        source_account.balance += transaction.amount
        destination_account.balance -= transaction.amount

    db.delete(transaction)

    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    return