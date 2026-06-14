import logging
import traceback
from datetime import datetime, date
from math import ceil
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, Path, Request, Query
from sqlalchemy import func, extract, case
from sqlalchemy.orm import Session
from starlette import status
from pydantic import BaseModel, Field
from models import Expense, User
from database import SessionLocal
from .auth import get_current_user
from starlette.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates2")
router= APIRouter(
    prefix="/expenses",
    tags=["expenses"]
)

class CreateExpenseRequest(BaseModel):
    amount: int
    category: str
    description: str
    date: str
    mode: str
    etype: str
    notes: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency=Annotated[Session,Depends(get_db)]
user_dependency=Annotated[dict,Depends(get_current_user)]

def redirect_to_login():
    redirect_response = RedirectResponse(url="login.html", status_code=status.HTTP_302_FOUND)
    redirect_response.delete_cookie("access_token")
    return redirect_response




@router.get("/",status_code=status.HTTP_200_OK)
async def render_expenses_page(request: Request,db: db_dependency,user:user_dependency):
    try:
        # cookie = request.cookies.get("access_token")
        # if not cookie:
        #     raise HTTPException(status_code=401, detail="Authentication Failed")
        # user = await get_current_user(cookie)
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
        user1=db.query(User).filter(User.id == user.get("user_id")).first()
        return templates.TemplateResponse("dashboard.html", {"request": request,"user": user1})
    except Exception as err:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server Error")

@router.get("/expenses",status_code=status.HTTP_200_OK)
async def expenses_data(
    db: db_dependency,
    user:user_dependency,
    category: Optional[str] = Query(None, description="Filter by category (or 'all')"),
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    page: int = Query(1, ge=1),           # default page 1
    per_page: int = Query(5, ge=1, le=100)  # max 100 items per page
):
    try:
        # cookie = request.cookies.get("access_token")
        # if not cookie:
        #     raise HTTPException(status_code=401, detail="Authentication Failed")
        # user = await get_current_user(cookie)
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
        user_id = user.get("user_id")
        total = db.query(Expense).filter(Expense.user_id == user_id).count()
        offset = (page - 1) * per_page
        expenses = db.query(Expense)\
            .filter(Expense.user_id == user_id)
        # Pagination metadata
        if category and category!= "":
            expenses=expenses.filter(Expense.category == category)
        if start_date:
            expenses=expenses.filter(Expense.date >= start_date)
        if end_date:
            expenses=expenses.filter(Expense.date <= end_date)
        expenses = expenses.order_by(Expense.date.desc(), Expense.id.desc()) \
            .offset(offset) \
            .limit(per_page) \
            .all()
        total_pages = ceil(total / per_page)
        return  {
            "expenses": expenses,
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server Error")

@router.get("/chart-data", status_code=status.HTTP_200_OK)
async def expenses_chart_data(
        db: db_dependency,
        user:user_dependency,
        category: Optional[str] = Query(None, description="Filter by category (or 'all')"),
        start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
        end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)")
    ):
    try:
        # cookie = request.cookies.get("access_token")
        # if not cookie:
        #     raise HTTPException(status_code=401, detail="Authentication Failed")
        # user= await get_current_user(cookie)

        if user is None:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
        exp_summary=db.query(Expense.category,func.sum(Expense.amount).label("total")
        ).filter(Expense.user_id == user.get("user_id"))
        if category and category!= "":
            exp_summary=exp_summary.filter(Expense.category == category)
        if start_date:
            exp_summary=exp_summary.filter(Expense.date >= start_date)
        if end_date:
            exp_summary=exp_summary.filter(Expense.date <= end_date)
        exp_summary=exp_summary.group_by(Expense.category).order_by(func.sum(Expense.amount).desc()).all()
        summary = [{"category": cat, "total": float(total)} for cat, total in exp_summary]
        return {"chart_data": summary}
    except:
        raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Server Error")
logger = logging.getLogger(__name__)
@router.get("/summary", status_code=status.HTTP_200_OK)
async def expenses_summary(db: db_dependency,user: user_dependency):
    try:
        # cookie = request.cookies.get("access_token")
        # if not cookie:
        #     raise HTTPException(status_code=401, detail="Authentication Failed")
        # user= await get_current_user(cookie)
        if user is None:
            raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
        user_id = user.get("user_id")
        now = datetime.now()
        # This month and Last month
        this_month = now.month
        this_year = now.year
        last_month = this_month - 1
        last_year = this_year if last_month > 0 else this_year - 1

        if last_month == 0:
            last_month = 12
        this_month_condition = (extract('month', Expense.date) == this_month) & \
                               (extract('year', Expense.date) == this_year)

        last_month_condition = (extract('month', Expense.date) == last_month) & \
                               (extract('year', Expense.date) == last_year)

        result = db.query(
            func.sum(
                case((this_month_condition, Expense.amount), else_=0)
            ).label("this_month_total"),

            func.sum(
                case((last_month_condition, Expense.amount), else_=0)
            ).label("last_month_total"),

            func.count(
                case((this_month_condition, Expense.id), else_=None)
            ).label("this_month_count"),
            func.count(
                case((last_month_condition, Expense.id), else_=None)
            ).label("last_month_count")
        ).filter(Expense.user_id == user_id).first()
        print("aaa")
        # Get Highest Spending Category This Month
        highest_cat = db.query(
            Expense.category,
            func.sum(Expense.amount).label("total")
        ).filter(
            Expense.user_id == user_id,
            extract('month', Expense.date) == this_month,
            extract('year', Expense.date) == this_year
        ).group_by(Expense.category) \
            .order_by(func.sum(Expense.amount).desc()) \
            .first()

        last_month_total = float(result.last_month_total or 0)
        this_month_total = float(result.this_month_total or 0)
        highest_category = highest_cat.category if highest_cat else None
        highest_amount = float(highest_cat.total) if highest_cat else 0

        percentage = round((highest_amount / this_month_total * 100), 2) if this_month_total > 0 else 0
        incr_percentage=round((this_month_total / last_month_total * 100), 2) if last_month_total > 0 else 0

        return {
            "this_month_total": this_month_total,
            "last_month_total": last_month_total,
            "this_month_count": int(result.this_month_count or 0),
            "highest_category": highest_category,
            "highest_amount": highest_amount,
            "highest_percentage": percentage,
            "month_avg":round(this_month_total/now.day),
            "incr_percentage":incr_percentage,
            "count_change":int(result.this_month_count-result.last_month_count or 0)
        }
    except Exception as e:
        error_msg = str(e)
        error_trace = traceback.format_exc()

        print("🔥 DB ERROR:", error_msg)  # ← See in terminal
        logger.error("Monthly Summary Error: %s", error_msg)
        print(error_trace)  # ← Full traceback

        return {
            "error": "Database query failed",
            "detail": error_msg,
            "trace": error_trace.split("\n")[-5:]  # last few lines
        }
        print("bbb")
        #return redirect_to_login()


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_expense(expense: CreateExpenseRequest, db:db_dependency, user: user_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    expense=Expense(
        user_id= user.get("user_id"),
        amount=expense.amount,
        category=expense.category,
        description=expense.description,
        date=expense.date,
        mode=expense.mode,
        etype=expense.etype,
        notes=expense.notes
    )
    db.add(expense)
    db.commit()

@router.get("/{expense_id}", status_code=status.HTTP_200_OK)
async def render_edit_expense( expense_id:int, db:db_dependency,user: user_dependency):
    try:
        # cookie = request.cookies.get("access_token")
        # if cookie is None:
        #     raise HTTPException(status_code=401, detail="Authentication Failed")
        # user= await get_current_user(cookie)

        if user is None:
            raise HTTPException(status_code=401, detail="Authentication Failed")
        expense=db.query(Expense).filter(Expense.id==expense_id).filter(Expense.user_id == user.get("user_id")).first()
        if expense is None:
            raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="No expense found")
        return expense
        # return templates.TemplateResponse("edit-expense.html",{"request":request,"expense":expense,"user":user})
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Server Error")


@router.put("/{expense_id}", status_code=status.HTTP_202_ACCEPTED)
async def update_expense(expense: CreateExpenseRequest, db:db_dependency, user: user_dependency, expense_id: int=Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    expense_model=db.query(Expense).filter(Expense.id == expense_id).filter(Expense.user_id == user.get("user_id")).first()
    if expense_model is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    expense_model.amount=expense.amount
    expense_model.category=expense.category
    expense_model.description=expense.description
    expense_model.date=expense.date
    expense_model.mode=expense.mode
    expense_model.etype=expense.etype
    expense_model.notes=expense.notes
    db.add(expense_model)
    db.commit()

@router.delete("/{expense_id}", status_code=status.HTTP_202_ACCEPTED)
async def delete_expense(db:db_dependency, user: user_dependency, expense_id: int=Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    expense=db.query(Expense).filter(Expense.user_id == user.get("user_id")).filter(Expense.id == expense_id).first()
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    db.delete(expense)
    db.commit()
