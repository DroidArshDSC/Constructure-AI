from fastapi import APIRouter
from app.core.eval_runner import EvalRunner

router = APIRouter()

@router.get("/")
async def run_evaluation():
    runner = EvalRunner()
    return runner.run_all()