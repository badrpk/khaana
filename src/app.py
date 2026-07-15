from __future__ import annotations
"""Khaana — multi-vendor food marketplace API.
Parity target: Foodpanda / Uber Eats core customer + kitchen APIs.
"""
import sys
from pathlib import Path as _P
sys.path.insert(0, str(_P(__file__).resolve().parent))

import math
from http_util import JsonAPI, serve, uid, iso, now

VENDORS = [
    {"id": "v1", "name": "Karachi Biryani House", "city": "Karachi", "lat": 24.8607, "lng": 67.0011,
     "cuisines": ["biryani", "pakistani"], "rating": 4.7, "rating_count": 1820, "delivery_fee_pkr": 80,
     "min_order_pkr": 400, "eta_min": 35, "open": True, "hours": "11:00-23:00"},
    {"id": "v2", "name": "Lahore Grill", "city": "Lahore", "lat": 31.5204, "lng": 74.3587,
     "cuisines": ["bbq", "pakistani"], "rating": 4.5, "rating_count": 940, "delivery_fee_pkr": 70,
     "min_order_pkr": 350, "eta_min": 40, "open": True, "hours": "12:00-00:00"},
    {"id": "v3", "name": "Islamabad Healthy Bowls", "city": "Islamabad", "lat": 33.6844, "lng": 73.0479,
     "cuisines": ["healthy", "salads"], "rating": 4.6, "rating_count": 410, "delivery_fee_pkr": 90,
     "min_order_pkr": 500, "eta_min": 30, "open": True, "hours": "10:00-22:00"},
    {"id": "v4", "name": "Pizza Peak", "city": "Karachi", "lat": 24.87, "lng": 67.05,
     "cuisines": ["pizza", "italian"], "rating": 4.3, "rating_count": 2200, "delivery_fee_pkr": 99,
     "min_order_pkr": 600, "eta_min": 45, "open": True, "hours": "12:00-02:00"},
]
MENU = {
    "v1": [
        {"id": "m1", "name": "Chicken Biryani", "price_pkr": 450, "category": "mains", "veg": False, "prep_min": 20},
        {"id": "m2", "name": "Raita", "price_pkr": 80, "category": "sides", "veg": True, "prep_min": 5},
        {"id": "m5", "name": "Beef Pulao", "price_pkr": 520, "category": "mains", "veg": False, "prep_min": 25},
    ],
    "v2": [
        {"id": "m3", "name": "Seekh Kebab", "price_pkr": 600, "category": "mains", "veg": False, "prep_min": 25},
        {"id": "m4", "name": "Naan", "price_pkr": 50, "category": "bread", "veg": True, "prep_min": 8},
    ],
    "v3": [
        {"id": "m6", "name": "Quinoa Bowl", "price_pkr": 750, "category": "mains", "veg": True, "prep_min": 15},
    ],
    "v4": [
        {"id": "m7", "name": "Margherita 12\"", "price_pkr": 990, "category": "pizza", "veg": True, "prep_min": 22},
        {"id": "m8", "name": "Pepperoni 12\"", "price_pkr": 1290, "category": "pizza", "veg": False, "prep_min": 22},
    ],
}
COUPONS = {
    "WELCOME100": {"type": "flat", "value": 100, "min_subtotal": 500},
    "SAVE10": {"type": "percent", "value": 10, "min_subtotal": 800},
}
CARTS: dict[str, list] = {}
ORDERS: dict[str, dict] = {}
REVIEWS: list[dict] = []
TRACK_STATES = ["placed", "confirmed", "preparing", "out_for_delivery", "delivered", "cancelled"]

def haversine_km(lat1, lng1, lat2, lng2):
    R = 6371
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dl = math.radians(lng2 - lng1)
    a = math.sin(dphi/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2 * R * math.asin(math.sqrt(a))

def item_price(vid, iid):
    for it in MENU.get(vid, []):
        if it["id"] == iid:
            return it
    return None

class H(JsonAPI):
    def do_GET(self):
        path, q = self.parse()
        if path in ("/", "/health"):
            return self._send(200, {
                "ok": True, "service": "khaana", "version": "2.0.0",
                "parity_target": "Foodpanda / Uber Eats core APIs",
                "routes": ["/vendors", "/vendors/{id}/menu", "/search", "/cart", "/orders",
                           "/orders/{id}", "/orders/{id}/track", "/coupons", "/reviews", "/capabilities"]
            })
        if path == "/capabilities":
            return self._send(200, {"ok": True, "features": [
                "geo_search", "cuisine_filter", "ratings", "eta", "cart", "coupons",
                "checkout", "order_tracking", "reviews", "payment_methods", "vendor_hours"
            ], "competitor": "Foodpanda"})
        if path == "/vendors":
            city = (q.get("city") or [None])[0]
            cuisine = (q.get("cuisine") or [None])[0]
            open_only = (q.get("open") or ["1"])[0] == "1"
            lat = float((q.get("lat") or ["0"])[0] or 0)
            lng = float((q.get("lng") or ["0"])[0] or 0)
            rows = []
            for v in VENDORS:
                if city and v["city"].lower() != city.lower():
                    continue
                if cuisine and cuisine.lower() not in [c.lower() for c in v["cuisines"]]:
                    continue
                if open_only and not v["open"]:
                    continue
                row = dict(v)
                if lat and lng:
                    d = haversine_km(lat, lng, v["lat"], v["lng"])
                    row["distance_km"] = round(d, 2)
                    row["eta_min"] = int(v["eta_min"] + d * 2)
                rows.append(row)
            rows.sort(key=lambda r: (-r["rating"], r.get("distance_km", 999)))
            return self._send(200, {"ok": True, "count": len(rows), "vendors": rows})
        if path.startswith("/vendors/") and path.endswith("/menu"):
            vid = path.split("/")[2]
            return self._send(200, {"ok": True, "vendor_id": vid, "menu": MENU.get(vid, [])})
        if path == "/search":
            term = ((q.get("q") or [""])[0] or "").lower()
            hits = []
            for vid, items in MENU.items():
                v = next((x for x in VENDORS if x["id"] == vid), None)
                for it in items:
                    if term in it["name"].lower() or term in (v or {}).get("name", "").lower():
                        hits.append({"vendor": v, "item": it})
            return self._send(200, {"ok": True, "q": term, "results": hits})
        if path == "/cart":
            user = (q.get("user") or ["guest"])[0]
            items = CARTS.get(user, [])
            sub = 0
            detailed = []
            for line in items:
                it = item_price(line["vendor_id"], line["item_id"])
                if not it:
                    continue
                line_total = it["price_pkr"] * line["qty"]
                sub += line_total
                detailed.append({**line, "name": it["name"], "unit_price": it["price_pkr"], "line_total": line_total})
            return self._send(200, {"ok": True, "user": user, "items": detailed, "subtotal_pkr": sub})
        if path == "/coupons":
            return self._send(200, {"ok": True, "coupons": list(COUPONS.keys())})
        if path == "/orders":
            user = (q.get("user") or [None])[0]
            rows = list(ORDERS.values())
            if user:
                rows = [o for o in rows if o["user"] == user]
            return self._send(200, {"ok": True, "orders": rows})
        if path.startswith("/orders/") and path.endswith("/track"):
            oid = path.split("/")[2]
            o = ORDERS.get(oid)
            if not o:
                return self._send(404, {"ok": False, "error": "order_not_found"})
            return self._send(200, {"ok": True, "order_id": oid, "status": o["status"],
                                    "timeline": o["timeline"], "eta_min": o.get("eta_min"),
                                    "rider": o.get("rider")})
        if path.startswith("/orders/"):
            oid = path.split("/")[2]
            o = ORDERS.get(oid)
            if not o:
                return self._send(404, {"ok": False, "error": "order_not_found"})
            return self._send(200, {"ok": True, "order": o})
        if path == "/reviews":
            vid = (q.get("vendor_id") or [None])[0]
            rows = REVIEWS if not vid else [r for r in REVIEWS if r["vendor_id"] == vid]
            return self._send(200, {"ok": True, "reviews": rows})
        self._send(404, {"ok": False, "error": "not_found"})

    def do_POST(self):
        path, q = self.parse()
        body = self._read_json()
        if body.get("_error"):
            return self._send(400, {"ok": False, "error": "invalid_json"})
        if path == "/cart/add":
            user = str(body.get("user") or "guest")
            vid, iid = body.get("vendor_id"), body.get("item_id")
            if not item_price(vid, iid):
                return self._send(400, {"ok": False, "error": "unknown_item"})
            qty = max(1, int(body.get("qty") or 1))
            CARTS.setdefault(user, []).append({"vendor_id": vid, "item_id": iid, "qty": qty})
            return self._send(200, {"ok": True, "cart": CARTS[user]})
        if path == "/cart/clear":
            user = str(body.get("user") or "guest")
            CARTS[user] = []
            return self._send(200, {"ok": True, "cart": []})
        if path == "/order" or path == "/checkout":
            user = str(body.get("user") or "guest")
            items = CARTS.get(user, [])
            if not items:
                return self._send(400, {"ok": False, "error": "cart_empty"})
            sub = 0
            lines = []
            max_eta = 30
            for line in items:
                it = item_price(line["vendor_id"], line["item_id"])
                if not it:
                    continue
                lt = it["price_pkr"] * line["qty"]
                sub += lt
                lines.append({**line, "name": it["name"], "line_total": lt})
                max_eta = max(max_eta, it.get("prep_min", 15) + 20)
            fee = 80
            discount = 0
            code = (body.get("coupon") or "").upper()
            if code in COUPONS:
                c = COUPONS[code]
                if sub >= c["min_subtotal"]:
                    discount = c["value"] if c["type"] == "flat" else int(sub * c["value"] / 100)
            total = max(0, sub + fee - discount)
            pay = body.get("payment_method") or "cod"
            if pay not in ("cod", "card", "jazzcash", "easypaisa", "wallet"):
                return self._send(400, {"ok": False, "error": "invalid_payment_method",
                                        "allowed": ["cod", "card", "jazzcash", "easypaisa", "wallet"]})
            oid = uid("ord")
            order = {
                "id": oid, "user": user, "items": lines, "subtotal_pkr": sub,
                "delivery_fee_pkr": fee, "discount_pkr": discount, "coupon": code or None,
                "total_pkr": total, "payment_method": pay, "payment_status": "pending" if pay != "cod" else "cod",
                "status": "placed", "address": body.get("address") or "Karachi, PK",
                "phone": body.get("phone") or "", "eta_min": max_eta,
                "timeline": [{"status": "placed", "at": iso()}],
                "rider": None, "created_at": iso(),
            }
            ORDERS[oid] = order
            CARTS[user] = []
            return self._send(201, {"ok": True, "order": order})
        if path.startswith("/orders/") and path.endswith("/advance"):
            # kitchen/rider simulate next tracking state
            oid = path.split("/")[2]
            o = ORDERS.get(oid)
            if not o:
                return self._send(404, {"ok": False, "error": "order_not_found"})
            i = TRACK_STATES.index(o["status"]) if o["status"] in TRACK_STATES else 0
            if i < len(TRACK_STATES) - 2:  # not past delivered
                o["status"] = TRACK_STATES[i + 1]
                o["timeline"].append({"status": o["status"], "at": iso()})
                if o["status"] == "out_for_delivery":
                    o["rider"] = {"name": "Ali R.", "phone": "+923001112233", "vehicle": "bike"}
            return self._send(200, {"ok": True, "order": o})
        if path == "/reviews":
            rec = {
                "id": uid("rev"), "vendor_id": body.get("vendor_id"), "user": body.get("user") or "guest",
                "rating": float(body.get("rating") or 5), "text": body.get("text") or "", "at": iso(),
            }
            REVIEWS.append(rec)
            return self._send(201, {"ok": True, "review": rec})
        self._send(404, {"ok": False, "error": "not_found"})

def main():
    serve(H, port=int(__import__("os").environ.get("PORT", "8765")), name="Khaana v2 (Foodpanda parity)")

if __name__ == "__main__":
    main()
