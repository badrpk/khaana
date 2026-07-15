# Khaana — competitive parity

**Target:** Foodpanda / Uber Eats (core customer + kitchen APIs)

| Competitor capability | Khaana |
|----------------------|--------|
| Vendor discovery + geo | `GET /vendors?lat=&lng=&city=&cuisine=` |
| Menu | `GET /vendors/{id}/menu` |
| Search dishes | `GET /search?q=` |
| Cart | `POST /cart/add`, `GET /cart` |
| Coupons | `GET /coupons`, checkout `coupon` |
| Checkout + payments | COD / card / JazzCash / EasyPaisa / wallet |
| Order tracking | `GET /orders/{id}/track` + advance states |
| Reviews | `POST /reviews` |
| Capabilities probe | `GET /capabilities` |

Run: `python3 src/app.py` → http://127.0.0.1:8765
