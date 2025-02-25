# /api/v1/tickers => not sure: 12k possible tickers...maybe we just return the 6 ones? eg. just the main categories.

# GET /api/v1/tickers/{ticker_code} => details everything about the ticker, eg. its name, description, statistical params... AND TYPE: eg. default (built-in) or custom defined
# => fetches the data from database and computes the other parameters.
# => note: for the custom ones, will need to return data from the user defined ones.
#
#
#
#
# POST /api/v1/tickers => allows a user to define a new custom ticker... must not overwrite a default, and has to be 4 chars and so on.... start with letter J or above basically, and last letter needs to be A-C (but middle 2 can be numbers/symbols? maybe not --- but they will have no bearing, and the stats params will need to be provided)
#
# CONSIDER A ROUTER GET /tickers/me (lists all the custom defined tickers for the current user)
#
# PATCH /api/v1/tickers/{ticker_code} => allows a user to update an existing custom defined ticker (cannot overwrite an existing default one.)
#
#

import re
import uuid
from typing import Any, List
from src.dependencies import SessionDep, CurrentUser, get_current_active_superuser

from fastapi import APIRouter, Depends, HTTPException, status, Path

from src.ticker.utils import compute_user_defined_ticker_derived_details
from src.ticker.built_in_tickers import get_built_in_category_context, compute_built_in_ticker_derived_details
from src.ticker.schemas import TickerDetails, UserDefinedTickerCreate
from src.ticker import service


router = APIRouter()


@router.get(
    "/{ticker_code}",
    response_model=TickerDetails
)
def get_ticker_details(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    ticker_code: str = Path(
        ...,
        regex="^[A-Z]{3}[A-C]$",
        description="Ticker code must be 4 characters: first 3 uppercase letters and 4th letter A, B, or C"
    )
) -> Any:
    """Given a default or custom ticker, retrieves details."""
    category_key = ticker_code[0]
    built_in_category_context = get_built_in_category_context(category_key)

    if built_in_category_context is not None:
        return compute_built_in_ticker_derived_details(ticker_code, built_in_category_context)

    user_defined_ticker = service.get_by_user(session=session, ticker_code=ticker_code, user_id=current_user.id)
    if not user_defined_ticker:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticker not found."
        )

    return compute_user_defined_ticker_derived_details(ticker_code, user_defined_ticker)



@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=TickerDetails,
)
def create_user_defined_ticker(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    body: UserDefinedTickerCreate,
) -> Any:
    """Create a new user-defined ticker."""
    if not re.match(r"^[G-Z]{3}[A-C]$", body.ticker_code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ticker code must match pattern '^[G-Z]{3}[A-C]$'."
        )

    existing_ticker = service.get_by_user(session=session, ticker_code=body.ticker_code, user_id=current_user.id)
    if existing_ticker:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Existing ticker with the same code already exists."
        )

    new_ticker = service.create(
        session=session,
        user_id=current_user.id,
        ticker_data=body,
    )
    return new_ticker


@router.get(
    "/",
    response_model=List[TickerDetails],
    status_code=status.HTTP_200_OK,
)
def get_user_defined_tickers(
    *,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """
    Retrieve all user-defined tickers for the authenticated user.
    """
    tickers = service.get_all_by_user(session=session, user_id=current_user.id)
    if tickers is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No tickers found for the current user."
        )
    return tickers
