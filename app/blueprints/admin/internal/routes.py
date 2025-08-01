# app/blueprints/admin/internal_routes.py
# Fokus: Alur internal gudang (manajemen rak & alokasi)

from flask import Blueprint, request, jsonify

# --- Impor service & skema yang relevan ---
from app.blueprints.warehouse.services import WarehouseService
from app.blueprints.allocations.services import AllocationService
from app.blueprints.warehouse.schemas import RackSchema
from app.blueprints.allocations.schemas import AllocationSchema

# --- Inisialisasi Blueprint ---
# Kita bisa bikin blueprint baru atau nambahin ke admin_bp yang sudah ada.
# Untuk modularitas, kita bikin baru.
internal_bp = Blueprint('internal_bp', __name__, url_prefix='/api/admin/internal')


# ===================================================================
# A. ENDPOINTS UNTUK MANAJEMEN GUDANG & RAK
# ===================================================================

@internal_bp.route('/racks', methods=['POST'])
# @admin_required
def create_rack_route():
    """Endpoint untuk membuat rak baru di dalam gudang."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body tidak boleh kosong"}), 400
    
    try:
        new_rack = WarehouseService.create_rack(data)
        schema = RackSchema()
        return jsonify(schema.dump(new_rack)), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        print(f"Internal Server Error: {e}")
        return jsonify({"error": "Gagal membuat rak baru"}), 500


# ===================================================================
# B. ENDPOINTS UNTUK ALOKASI STOK
# ===================================================================

@internal_bp.route('/reallocate', methods=['POST'])
# @admin_required
def reallocate_stock_route():
    """
    Endpoint untuk melakukan re-alokasi stok, 
    misalnya dari 'reguler' ke 'tender'.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body tidak boleh kosong"}), 400
        
    try:
        new_allocation = AllocationService.reallocate_stock(data)
        schema = AllocationSchema()
        return jsonify(schema.dump(new_allocation)), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        print(f"Internal Server Error: {e}")
        return jsonify({"error": "Gagal melakukan re-alokasi"}), 500

