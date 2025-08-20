# coupons/discount_type/interface/discount_type_routes.py
from flask import Blueprint, jsonify
from coupons.discount_type.infraestructure.model.discount_type_model import DiscountTypeModel

discount_type_bp = Blueprint("discount_type_api", __name__, url_prefix="/api/discount-types")

def _canon(name: str) -> str:
    s = (name or "").strip().lower()
    if s in ("percentage", "porcentaje"):
        return "PERCENTAGE"
    if s in ("amount", "monto"):
        return "AMOUNT"
    return s.upper()

@discount_type_bp.get("")
def list_discount_types():
    rows = list(DiscountTypeModel.select())
    # En tu tabla tienes 'percentage' y 'amount' → se devuelven tal cual
    return jsonify([{"id": r.id, "name": r.name} for r in rows]), 200
