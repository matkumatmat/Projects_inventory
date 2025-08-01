# --- backend/app/models/__init__.py ---

# Impor semua model dari setiap file agar mudah diakses dari 'app.models'
from .user import *
from .product import *
from .outbound import *
from .shipment import *
from .warehouse import *
from .consignment import *
from .tender import *
from .tender_item import *
