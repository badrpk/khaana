# Khaana gap analysis vs Foodpanda / Uber Eats

| Competitor feature | Before v2 | v3 |
|--------------------|-----------|-----|
| Geo vendor discovery | yes | yes |
| Coupons / checkout | yes | yes |
| Scheduled orders | missing | **added** |
| Favorites | missing | **added** |
| Reorder | missing | **added** |
| Driver tip | missing | **added** |
| Pro free-delivery plan | missing | **pricing + checkout flag** |
| Stripe card | partial labels only | **PaymentIntent + multi-rail** |
| JazzCash / EasyPaisa / crypto | labels | **invoice rails** |
| Undercut pricing | no | **delivery Rs40 vs ~120; menu undercut** |

Payments: `GET /pricing`, `/payments/rails`, `POST /payments/create`, checkout `payment_method`.
