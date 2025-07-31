# app/blueprints/admin/stock_view_routes.py
# Fokus: Menyediakan data stok dari berbagai sudut pandang untuk frontend.

from flask import Blueprint, request, jsonify

# Impor semua service yang dibutuhkan untuk reporting
from ...products.services import ProductService
from ...warehouse.services import WarehouseService
from ...allocations.services import AllocationService
# Asumsi kita akan buat fungsi get_stock_by_batch di ProductService
# from ...services.product_services import ProductService 

# Inisialisasi Blueprint baru khusus untuk melihat stok
stock_view_bp = Blueprint('stock_view_bp', __name__, url_prefix='/api/admin/stock-view')


@stock_view_bp.route('/by-product/<string:erp_id>', methods=['GET'])
# @admin_required
def get_stock_by_product_route(erp_id):
    """Sudut Pandang 1: Total stok berdasarkan ID Produk (ERP)."""
    try:
        stock_data = ProductService.get_stock_by_product(erp_id)
        return jsonify(stock_data), 200
    except Exception as e:
        return jsonify({"error": "Gagal mengambil data stok produk"}), 500

@stock_view_bp.route('/by-warehouse/<int:warehouse_id>', methods=['GET'])
# @admin_required
def get_stock_by_warehouse_route(warehouse_id):
    """Sudut Pandang 2: Rincian stok berdasarkan Gudang."""
    try:
        stock_data = WarehouseService.get_stock_by_warehouse(warehouse_id)
        return jsonify(stock_data), 200
    except Exception as e:
        return jsonify({"error": "Gagal mengambil data stok gudang"}), 500

@stock_view_bp.route('/by-allocation/<string:allocation_code>', methods=['GET'])
# @admin_required
def get_stock_by_allocation_route(allocation_code):
    """Sudut Pandang 3: Rincian stok berdasarkan Kode Alokasi/Kontrak."""
    try:
        stock_data = AllocationService.get_stock_by_allocation(allocation_code)
        return jsonify(stock_data), 200
    except Exception as e:
        return jsonify({"error": "Gagal mengambil data alokasi"}), 500

@stock_view_bp.route('/by-batch/<int:batch_id>', methods=['GET'])
# @admin_required
def get_stock_by_batch_route(batch_id):
    """Sudut Pandang 4: Rincian stok berdasarkan ID Batch."""
    try:
        # Kita panggil fungsi yang ada di service produk (yang di-upgrade)
        # Ini akan memberikan rincian alokasi & lokasi untuk satu batch spesifik.
        stock_data = ProductService.get_batch_stock_summary(batch_id)
        return jsonify(stock_data), 200
    except Exception as e:
        return jsonify({"error": "Gagal mengambil data stok batch"}), 500
