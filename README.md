# Khaana 🍛

**Multi-vendor food marketplace API** for Pakistan — discovery, menus, cart, orders.

Distinct from **Laiba Badar** (single food brand + delivery app).

## Download & run

```bash
git clone https://github.com/badrpk/khaana.git
cd khaana
python3 src/app.py
```

## API

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health |
| GET | `/vendors` | List kitchens |
| GET | `/vendors/{id}/menu` | Menu |
| GET | `/cart?user=` | Cart |
| POST | `/cart/add` | `{user, vendor_id, item_id, qty}` |
| POST | `/order` | `{user}` place order |

## Contribute

Public — [CONTRIBUTING.md](CONTRIBUTING.md) · [COMMUNITY.md](COMMUNITY.md)
