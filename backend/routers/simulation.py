"""
Real-time Simulation API with WebSocket support
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query, HTTPException, status
from typing import List
import asyncio

from simulation import ChurnSimulator
from auth import get_current_user, get_user_from_token, User
from database import SessionLocal
from logger import logger
from service_container import get_churn_service

router = APIRouter(tags=["Simulation"])


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")


manager = ConnectionManager()
service = get_churn_service()
simulator = ChurnSimulator()


def _authenticate_websocket_token(token: str) -> User:
    db = SessionLocal()
    try:
        user = get_user_from_token(db, token)
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Inactive user")
        return user
    finally:
        db.close()


@router.websocket("/ws/simulation")
async def websocket_simulation(
    websocket: WebSocket,
    interval: float = Query(default=2.0, ge=0.5, le=10.0),
):
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=1008, reason="Missing token")
        return

    try:
        current_user = _authenticate_websocket_token(token)
    except HTTPException:
        await websocket.close(code=1008, reason="Invalid token")
        return

    await manager.connect(websocket)

    try:
        while True:
            customer = simulator.generate_customer()
            customer_id = customer.pop("customer_id")
            profile = customer.pop("_profile")

            try:
                prediction = service.predict(customer)

                result = {
                    "type": "prediction",
                    "customer_id": customer_id,
                    "profile": profile,
                    "customer_data": {
                        "tenure": customer["tenure"],
                        "contract": customer["Contract"],
                        "payment": customer["PaymentMethod"],
                        "internet": customer["InternetService"],
                        "monthly_charges": customer["MonthlyCharges"],
                    },
                    "prediction": {
                        "churn_probability": prediction["churn_risk_score"],
                        "risk_level": prediction["summary"],
                        "prediction": prediction["prediction"],
                        "confidence": prediction["confidence"],
                        "risk_factors_count": len(prediction["risk_factors"]),
                        "top_risk": prediction["risk_factors"][0]["factor"] if prediction["risk_factors"] else None,
                    },
                }

                await websocket.send_json(result)
                logger.info(
                    f"Simulation by {current_user.username}: {customer_id} -> "
                    f"{prediction['summary']} ({prediction['churn_risk_score']:.2%})"
                )

            except Exception as e:
                logger.error(f"Prediction error in simulation: {e}")
                await websocket.send_json({"type": "error", "message": str(e)})

            await asyncio.sleep(interval)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


@router.get("/simulation/batch")
async def get_simulation_batch(
    count: int = Query(default=10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
):
    results = []

    for _ in range(count):
        customer = simulator.generate_customer()
        customer_id = customer.pop("customer_id")
        profile = customer.pop("_profile")

        try:
            prediction = service.predict(customer)
            results.append(
                {
                    "customer_id": customer_id,
                    "profile": profile,
                    "tenure": customer["tenure"],
                    "contract": customer["Contract"],
                    "payment": customer["PaymentMethod"],
                    "monthly_charges": customer["MonthlyCharges"],
                    "churn_probability": prediction["churn_risk_score"],
                    "risk_level": prediction["summary"],
                    "prediction": prediction["prediction"],
                }
            )
        except Exception as e:
            logger.error(f"Batch prediction error: {e}")

    if results:
        probs = [r["churn_probability"] for r in results]
        high_risk = sum(1 for r in results if r["churn_probability"] > 0.5)

        summary = {
            "total": len(results),
            "high_risk_count": high_risk,
            "high_risk_pct": round(high_risk / len(results) * 100, 1),
            "avg_churn_probability": round(sum(probs) / len(probs), 4),
            "max_churn_probability": round(max(probs), 4),
            "min_churn_probability": round(min(probs), 4),
        }
    else:
        summary = {}

    return {"summary": summary, "customers": results}


@router.get("/simulation/stats")
async def get_simulation_stats(current_user: User = Depends(get_current_user)):
    return {
        "active_connections": len(manager.active_connections),
        "simulator_customer_count": simulator.customer_id - 1000,
        "service_model_version": service.model_version,
    }
