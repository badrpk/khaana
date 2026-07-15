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


## v3 payments & gaps

See [GAP_ANALYSIS.md](GAP_ANALYSIS.md). Multi-rail: Stripe, JazzCash, EasyPaisa, UPaisa, Coinbase, Binance, Monero, COD, bank.

```bash
python3 src/app.py
# GET /pricing  GET /gap-analysis  POST /checkout with payment_method=stripe|jazzcash|...
```
