"""
GeoCoord Transformer
Geodetic ↔ ECEF ↔ ENU Coordinate System Transformer
Author: Dr. Mosab Hawarey | @DrHawarey | github.com/mhawarey
"""

import tkinter as tk
from tkinter import ttk, messagebox
import math

# ── Ellipsoid definitions ──────────────────────────────────────────────────────
ELLIPSOIDS = {
    "WGS84": {
        "a": 6378137.0,
        "f": 1 / 298.257223563,
        "full": "WGS84 (World Geodetic System 1984)"
    },
    "GRS80": {
        "a": 6378137.0,
        "f": 1 / 298.257222101,
        "full": "GRS80 (Geodetic Reference System 1980)"
    },
    "Bessel": {
        "a": 6377397.155,
        "f": 1 / 299.1528128,
        "full": "Bessel 1841"
    },
    "Clarke": {
        "a": 6378206.4,
        "f": 1 / 294.9786982,
        "full": "Clarke 1866"
    },
}

def get_ellipsoid_params(name):
    e = ELLIPSOIDS[name]
    a = e["a"]
    f = e["f"]
    b = a * (1 - f)
    e2 = 2 * f - f ** 2          # first eccentricity squared
    ep2 = e2 / (1 - e2)          # second eccentricity squared
    return a, b, e2, ep2

# ── Math core ──────────────────────────────────────────────────────────────────

def geodetic_to_ecef(lat_deg, lon_deg, h, ellipsoid):
    a, b, e2, _ = get_ellipsoid_params(ellipsoid)
    lat = math.radians(lat_deg)
    lon = math.radians(lon_deg)
    N = a / math.sqrt(1 - e2 * math.sin(lat) ** 2)  # prime vertical radius
    X = (N + h) * math.cos(lat) * math.cos(lon)
    Y = (N + h) * math.cos(lat) * math.sin(lon)
    Z = (N * (1 - e2) + h) * math.sin(lat)
    return X, Y, Z

def ecef_to_geodetic(X, Y, Z, ellipsoid):
    """Bowring iterative method."""
    a, b, e2, ep2 = get_ellipsoid_params(ellipsoid)
    p = math.sqrt(X ** 2 + Y ** 2)
    lon = math.atan2(Y, X)
    # Initial estimate
    lat = math.atan2(Z, p * (1 - e2))
    for _ in range(10):
        N = a / math.sqrt(1 - e2 * math.sin(lat) ** 2)
        lat_new = math.atan2(Z + e2 * N * math.sin(lat), p)
        if abs(lat_new - lat) < 1e-12:
            break
        lat = lat_new
    lat = lat_new
    N = a / math.sqrt(1 - e2 * math.sin(lat) ** 2)
    if abs(math.cos(lat)) > 1e-10:
        h = p / math.cos(lat) - N
    else:
        h = abs(Z) / math.sin(lat) - N * (1 - e2)
    return math.degrees(lat), math.degrees(lon), h

def ecef_to_enu(X, Y, Z, lat0_deg, lon0_deg, h0, ellipsoid):
    X0, Y0, Z0 = geodetic_to_ecef(lat0_deg, lon0_deg, h0, ellipsoid)
    lat0 = math.radians(lat0_deg)
    lon0 = math.radians(lon0_deg)
    dX, dY, dZ = X - X0, Y - Y0, Z - Z0
    e = -math.sin(lon0) * dX + math.cos(lon0) * dY
    n = (-math.sin(lat0) * math.cos(lon0) * dX
         - math.sin(lat0) * math.sin(lon0) * dY
         + math.cos(lat0) * dZ)
    u = (math.cos(lat0) * math.cos(lon0) * dX
         + math.cos(lat0) * math.sin(lon0) * dY
         + math.sin(lat0) * dZ)
    return e, n, u

def enu_to_ecef(e, n, u, lat0_deg, lon0_deg, h0, ellipsoid):
    X0, Y0, Z0 = geodetic_to_ecef(lat0_deg, lon0_deg, h0, ellipsoid)
    lat0 = math.radians(lat0_deg)
    lon0 = math.radians(lon0_deg)
    X = (-math.sin(lon0) * e
         - math.sin(lat0) * math.cos(lon0) * n
         + math.cos(lat0) * math.cos(lon0) * u + X0)
    Y = (math.cos(lon0) * e
         - math.sin(lat0) * math.sin(lon0) * n
         + math.cos(lat0) * math.sin(lon0) * u + Y0)
    Z = math.cos(lat0) * n + math.sin(lat0) * u + Z0
    return X, Y, Z

def geodetic_to_enu(lat_deg, lon_deg, h, lat0_deg, lon0_deg, h0, ellipsoid):
    X, Y, Z = geodetic_to_ecef(lat_deg, lon_deg, h, ellipsoid)
    return ecef_to_enu(X, Y, Z, lat0_deg, lon0_deg, h0, ellipsoid)

def enu_to_geodetic(e, n, u, lat0_deg, lon0_deg, h0, ellipsoid):
    X, Y, Z = enu_to_ecef(e, n, u, lat0_deg, lon0_deg, h0, ellipsoid)
    return ecef_to_geodetic(X, Y, Z, ellipsoid)

# ── Formatting helpers ─────────────────────────────────────────────────────────

def dd_to_dms(dd):
    sign = -1 if dd < 0 else 1
    dd = abs(dd)
    d = int(dd)
    m = int((dd - d) * 60)
    s = ((dd - d) * 60 - m) * 60
    return sign * d, m, s

def fmt_deg(val, axis='lat'):
    d, m, s = dd_to_dms(val)
    if axis == 'lat':
        hem = 'N' if val >= 0 else 'S'
    else:
        hem = 'E' if val >= 0 else 'W'
    return f"{abs(d)}° {m:02d}' {s:07.4f}\" {hem}   ({val:.8f}°)"

def fmt_m(val):
    return f"{val:.4f} m"

def fmt_enu(val):
    return f"{val:.4f} m"

# ── GUI ────────────────────────────────────────────────────────────────────────

DARK_BG    = "#0d1117"
PANEL_BG   = "#161b22"
BORDER     = "#30363d"
ACCENT     = "#00e5ff"
ACCENT2    = "#ff6b35"
ACCENT3    = "#7fff6e"
TEXT       = "#e6edf3"
MUTED      = "#8b949e"
INPUT_BG   = "#0d1117"
RESULT_BG  = "#0a1628"
FONT_MONO  = ("Courier New", 10)
FONT_LABEL = ("Segoe UI", 9)
FONT_HEAD  = ("Segoe UI", 11, "bold")
FONT_TITLE = ("Segoe UI", 16, "bold")
FONT_SMALL = ("Courier New", 8)

class GeoCoordApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("GeoCoord Transformer — Dr. Mosab Hawarey")
        self.configure(bg=DARK_BG)
        self.resizable(True, True)
        self.minsize(820, 680)

        self._build_styles()
        self._build_ui()
        self.after(100, lambda: self.geometry("980x780"))

    def _build_styles(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TNotebook", background=DARK_BG, borderwidth=0)
        style.configure("TNotebook.Tab",
                        background=PANEL_BG, foreground=MUTED,
                        font=("Segoe UI", 9), padding=[14, 6],
                        borderwidth=0)
        style.map("TNotebook.Tab",
                  background=[("selected", DARK_BG)],
                  foreground=[("selected", ACCENT)])
        style.configure("TFrame", background=DARK_BG)
        style.configure("TLabel", background=DARK_BG, foreground=TEXT,
                        font=FONT_LABEL)
        style.configure("TCombobox",
                        fieldbackground=INPUT_BG, background=INPUT_BG,
                        foreground=TEXT, selectbackground=INPUT_BG,
                        selectforeground=ACCENT, font=FONT_MONO)
        style.map("TCombobox",
                  fieldbackground=[("readonly", INPUT_BG)],
                  foreground=[("readonly", TEXT)])

    def _build_ui(self):
        # ── Header ──
        hdr = tk.Frame(self, bg=DARK_BG, pady=14)
        hdr.pack(fill="x", padx=20)

        tk.Label(hdr, text="GeoCoord Transformer",
                 bg=DARK_BG, fg=TEXT,
                 font=FONT_TITLE).pack(side="left")

        tk.Label(hdr,
                 text="  //  Geodetic ↔ ECEF ↔ ENU",
                 bg=DARK_BG, fg=MUTED,
                 font=("Segoe UI", 10)).pack(side="left", pady=4)

        # Ellipsoid selector (top-right)
        ef = tk.Frame(hdr, bg=DARK_BG)
        ef.pack(side="right")
        tk.Label(ef, text="ELLIPSOID", bg=DARK_BG, fg=MUTED,
                 font=("Courier New", 8)).pack(anchor="e")
        self.ellipsoid_var = tk.StringVar(value="WGS84")
        cb = ttk.Combobox(ef, textvariable=self.ellipsoid_var,
                          values=list(ELLIPSOIDS.keys()),
                          state="readonly", width=10,
                          font=FONT_MONO)
        cb.pack()
        cb.bind("<<ComboboxSelected>>", lambda e: self._update_ellipsoid_info())

        self.ellipsoid_info = tk.Label(ef, text="", bg=DARK_BG, fg=MUTED,
                                       font=("Courier New", 7))
        self.ellipsoid_info.pack(anchor="e")
        self._update_ellipsoid_info()

        # Separator
        tk.Frame(self, bg=BORDER, height=1).pack(fill="x", padx=20)

        # ── Notebook tabs ──
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=20, pady=14)

        self.tab_geo_ecef  = self._make_tab(nb, "Geodetic → ECEF",  self._build_geo_ecef)
        self.tab_ecef_geo  = self._make_tab(nb, "ECEF → Geodetic",  self._build_ecef_geo)
        self.tab_geo_enu   = self._make_tab(nb, "Geodetic → ENU",   self._build_geo_enu)
        self.tab_enu_geo   = self._make_tab(nb, "ENU → Geodetic",   self._build_enu_geo)
        self.tab_ecef_enu  = self._make_tab(nb, "ECEF → ENU",       self._build_ecef_enu)
        self.tab_enu_ecef  = self._make_tab(nb, "ENU → ECEF",       self._build_enu_ecef)

        # ── Credit bar ──
        bar = tk.Frame(self, bg="#0a0e1a", pady=5)
        bar.pack(fill="x", side="bottom")
        tk.Frame(bar, bg=BORDER, height=1).pack(fill="x")
        credit = tk.Label(bar,
            text="© Dr. Mosab Hawarey  |  @DrHawarey  |  github.com/mhawarey  |  GeoCoord Transformer v1.0",
            bg="#0a0e1a", fg=MUTED, font=("Courier New", 8))
        credit.pack(pady=4)

    def _make_tab(self, nb, label, builder):
        frame = ttk.Frame(nb)
        nb.add(frame, text=f"  {label}  ")
        builder(frame)
        return frame

    def _update_ellipsoid_info(self):
        name = self.ellipsoid_var.get()
        e = ELLIPSOIDS[name]
        a, b, e2, _ = get_ellipsoid_params(name)
        self.ellipsoid_info.config(
            text=f"a={e['a']:,.3f} m   f=1/{1/e['f']:.6f}"
        )

    # ── Widget helpers ─────────────────────────────────────────────────────────

    def _section(self, parent, title, color=ACCENT):
        f = tk.Frame(parent, bg=DARK_BG)
        f.pack(fill="x", padx=16, pady=(12, 4))
        tk.Label(f, text=f"  {title}  ",
                 bg=color, fg=DARK_BG,
                 font=("Courier New", 8, "bold"),
                 padx=6, pady=2).pack(side="left")
        tk.Frame(f, bg=BORDER, height=1).pack(side="left", fill="x", expand=True, padx=8)
        return f

    def _row(self, parent, label, default="", hint=""):
        row = tk.Frame(parent, bg=PANEL_BG)
        row.pack(fill="x", padx=16, pady=2)
        tk.Label(row, text=label, bg=PANEL_BG, fg=MUTED,
                 font=("Courier New", 9), width=22, anchor="w").pack(side="left", padx=(8,4))
        var = tk.StringVar(value=default)
        ent = tk.Entry(row, textvariable=var,
                       bg=INPUT_BG, fg=TEXT, insertbackground=ACCENT,
                       relief="flat", font=FONT_MONO,
                       highlightthickness=1,
                       highlightbackground=BORDER,
                       highlightcolor=ACCENT, width=26)
        ent.pack(side="left", ipady=4, padx=4)
        if hint:
            tk.Label(row, text=hint, bg=PANEL_BG, fg=MUTED,
                     font=("Courier New", 8)).pack(side="left", padx=4)
        return var

    def _result_box(self, parent, rows=6):
        rb = tk.Frame(parent, bg=PANEL_BG,
                      highlightthickness=1, highlightbackground=BORDER)
        rb.pack(fill="x", padx=16, pady=6)
        txt = tk.Text(rb, height=rows, bg=RESULT_BG, fg=ACCENT,
                      font=("Courier New", 10),
                      relief="flat", padx=12, pady=8,
                      insertbackground=ACCENT,
                      state="disabled", wrap="none")
        txt.pack(fill="x")
        return txt

    def _btn(self, parent, label, cmd):
        tk.Button(parent, text=label, command=cmd,
                  bg=ACCENT, fg=DARK_BG,
                  font=("Segoe UI", 10, "bold"),
                  relief="flat", padx=24, pady=6,
                  activebackground="#00b8cc",
                  activeforeground=DARK_BG,
                  cursor="hand2").pack(pady=10)

    def _show(self, txt_widget, content):
        txt_widget.config(state="normal")
        txt_widget.delete("1.0", "end")
        txt_widget.insert("end", content)
        txt_widget.config(state="disabled")

    def _get_ellipsoid(self):
        return self.ellipsoid_var.get()

    # ── Tab 1: Geodetic → ECEF ─────────────────────────────────────────────────
    def _build_geo_ecef(self, f):
        self._section(f, "INPUT — Geodetic (φ, λ, h)", ACCENT)
        p = tk.Frame(f, bg=PANEL_BG,
                     highlightthickness=1, highlightbackground=BORDER)
        p.pack(fill="x", padx=16, pady=4)
        self.g2e_lat = self._row(p, "Latitude φ  (°)",   "37.3861",  "decimal degrees, N+")
        self.g2e_lon = self._row(p, "Longitude λ (°)",  "-122.0839", "decimal degrees, E+")
        self.g2e_h   = self._row(p, "Ellipsoidal h (m)", "0.0",      "metres above ellipsoid")
        self._btn(f, "  Convert →  ", self._do_geo_ecef)
        self._section(f, "RESULT — ECEF (X, Y, Z)", ACCENT2)
        self.res_geo_ecef = self._result_box(f, 6)

    def _do_geo_ecef(self):
        try:
            lat = float(self.g2e_lat.get())
            lon = float(self.g2e_lon.get())
            h   = float(self.g2e_h.get())
            ell = self._get_ellipsoid()
            X, Y, Z = geodetic_to_ecef(lat, lon, h, ell)
            a, b, e2, _ = get_ellipsoid_params(ell)
            N = a / math.sqrt(1 - e2 * math.sin(math.radians(lat))**2)
            out = (
                f"Ellipsoid  : {ELLIPSOIDS[ell]['full']}\n"
                f"─────────────────────────────────────────\n"
                f"X          : {X:+.4f} m\n"
                f"Y          : {Y:+.4f} m\n"
                f"Z          : {Z:+.4f} m\n"
                f"─────────────────────────────────────────\n"
                f"Radius |r| : {math.sqrt(X**2+Y**2+Z**2):.4f} m\n"
                f"N (ν)      : {N:.4f} m   (prime vertical radius)\n"
            )
            self._show(self.res_geo_ecef, out)
        except ValueError as ex:
            messagebox.showerror("Input Error", str(ex))

    # ── Tab 2: ECEF → Geodetic ─────────────────────────────────────────────────
    def _build_ecef_geo(self, f):
        self._section(f, "INPUT — ECEF (X, Y, Z)", ACCENT)
        p = tk.Frame(f, bg=PANEL_BG,
                     highlightthickness=1, highlightbackground=BORDER)
        p.pack(fill="x", padx=16, pady=4)
        self.e2g_X = self._row(p, "X (m)", "-2694044.9706", "metres")
        self.e2g_Y = self._row(p, "Y (m)", "-4266843.3528", "metres")
        self.e2g_Z = self._row(p, "Z (m)",  "3887339.9725", "metres")
        self._btn(f, "  Convert →  ", self._do_ecef_geo)
        self._section(f, "RESULT — Geodetic (φ, λ, h)", ACCENT2)
        self.res_ecef_geo = self._result_box(f, 8)

    def _do_ecef_geo(self):
        try:
            X = float(self.e2g_X.get())
            Y = float(self.e2g_Y.get())
            Z = float(self.e2g_Z.get())
            ell = self._get_ellipsoid()
            lat, lon, h = ecef_to_geodetic(X, Y, Z, ell)
            d_lat, m_lat, s_lat = dd_to_dms(lat)
            d_lon, m_lon, s_lon = dd_to_dms(lon)
            out = (
                f"Ellipsoid  : {ELLIPSOIDS[ell]['full']}\n"
                f"─────────────────────────────────────────\n"
                f"Latitude φ : {fmt_deg(lat, 'lat')}\n"
                f"             {abs(d_lat)}° {m_lat:02d}' {s_lat:07.4f}\" {'N' if lat>=0 else 'S'}\n"
                f"Longitude λ: {fmt_deg(lon, 'lon')}\n"
                f"             {abs(d_lon)}° {m_lon:02d}' {s_lon:07.4f}\" {'E' if lon>=0 else 'W'}\n"
                f"Height h   : {h:.4f} m\n"
                f"─────────────────────────────────────────\n"
                f"Method     : Bowring iterative (10 iterations)\n"
            )
            self._show(self.res_ecef_geo, out)
        except ValueError as ex:
            messagebox.showerror("Input Error", str(ex))

    # ── Tab 3: Geodetic → ENU ──────────────────────────────────────────────────
    def _build_geo_enu(self, f):
        self._section(f, "INPUT — Point (Geodetic)", ACCENT)
        p = tk.Frame(f, bg=PANEL_BG,
                     highlightthickness=1, highlightbackground=BORDER)
        p.pack(fill="x", padx=16, pady=4)
        self.g2n_lat = self._row(p, "Latitude φ  (°)",   "37.3861",  "decimal degrees")
        self.g2n_lon = self._row(p, "Longitude λ (°)",  "-122.0839", "decimal degrees")
        self.g2n_h   = self._row(p, "Height h (m)",       "100.0",   "ellipsoidal height")

        self._section(f, "ORIGIN — Local ENU Reference", ACCENT3)
        o = tk.Frame(f, bg=PANEL_BG,
                     highlightthickness=1, highlightbackground=BORDER)
        o.pack(fill="x", padx=16, pady=4)
        self.g2n_lat0 = self._row(o, "Origin Lat φ₀ (°)",  "37.3500",  "decimal degrees")
        self.g2n_lon0 = self._row(o, "Origin Lon λ₀ (°)", "-122.0500", "decimal degrees")
        self.g2n_h0   = self._row(o, "Origin h₀ (m)",       "0.0",     "ellipsoidal height")

        self._btn(f, "  Convert →  ", self._do_geo_enu)
        self._section(f, "RESULT — ENU (East, North, Up)", ACCENT2)
        self.res_geo_enu = self._result_box(f, 7)

    def _do_geo_enu(self):
        try:
            lat  = float(self.g2n_lat.get());  lon  = float(self.g2n_lon.get());  h  = float(self.g2n_h.get())
            lat0 = float(self.g2n_lat0.get()); lon0 = float(self.g2n_lon0.get()); h0 = float(self.g2n_h0.get())
            ell = self._get_ellipsoid()
            e, n, u = geodetic_to_enu(lat, lon, h, lat0, lon0, h0, ell)
            dist_2d = math.sqrt(e**2 + n**2)
            dist_3d = math.sqrt(e**2 + n**2 + u**2)
            az = math.degrees(math.atan2(e, n)) % 360
            out = (
                f"Ellipsoid  : {ELLIPSOIDS[ell]['full']}\n"
                f"─────────────────────────────────────────\n"
                f"East   (E) : {e:+.4f} m\n"
                f"North  (N) : {n:+.4f} m\n"
                f"Up     (U) : {u:+.4f} m\n"
                f"─────────────────────────────────────────\n"
                f"2D distance: {dist_2d:.4f} m\n"
                f"3D distance: {dist_3d:.4f} m\n"
                f"Azimuth    : {az:.4f}°\n"
            )
            self._show(self.res_geo_enu, out)
        except ValueError as ex:
            messagebox.showerror("Input Error", str(ex))

    # ── Tab 4: ENU → Geodetic ──────────────────────────────────────────────────
    def _build_enu_geo(self, f):
        self._section(f, "INPUT — ENU Coordinates", ACCENT)
        p = tk.Frame(f, bg=PANEL_BG,
                     highlightthickness=1, highlightbackground=BORDER)
        p.pack(fill="x", padx=16, pady=4)
        self.n2g_e = self._row(p, "East  E (m)",  "3983.1", "metres")
        self.n2g_n = self._row(p, "North N (m)",  "4027.5", "metres")
        self.n2g_u = self._row(p, "Up    U (m)",   "100.0", "metres")

        self._section(f, "ORIGIN — Local ENU Reference", ACCENT3)
        o = tk.Frame(f, bg=PANEL_BG,
                     highlightthickness=1, highlightbackground=BORDER)
        o.pack(fill="x", padx=16, pady=4)
        self.n2g_lat0 = self._row(o, "Origin Lat φ₀ (°)",  "37.3500",  "decimal degrees")
        self.n2g_lon0 = self._row(o, "Origin Lon λ₀ (°)", "-122.0500", "decimal degrees")
        self.n2g_h0   = self._row(o, "Origin h₀ (m)",       "0.0",     "ellipsoidal height")

        self._btn(f, "  Convert →  ", self._do_enu_geo)
        self._section(f, "RESULT — Geodetic (φ, λ, h)", ACCENT2)
        self.res_enu_geo = self._result_box(f, 7)

    def _do_enu_geo(self):
        try:
            e  = float(self.n2g_e.get());   n  = float(self.n2g_n.get());  u  = float(self.n2g_u.get())
            lat0 = float(self.n2g_lat0.get()); lon0 = float(self.n2g_lon0.get()); h0 = float(self.n2g_h0.get())
            ell = self._get_ellipsoid()
            lat, lon, h = enu_to_geodetic(e, n, u, lat0, lon0, h0, ell)
            out = (
                f"Ellipsoid  : {ELLIPSOIDS[ell]['full']}\n"
                f"─────────────────────────────────────────\n"
                f"Latitude φ : {fmt_deg(lat, 'lat')}\n"
                f"Longitude λ: {fmt_deg(lon, 'lon')}\n"
                f"Height h   : {h:.4f} m\n"
                f"─────────────────────────────────────────\n"
                f"ECEF check :\n"
                f"  X = {geodetic_to_ecef(lat,lon,h,ell)[0]:+.4f} m\n"
                f"  Y = {geodetic_to_ecef(lat,lon,h,ell)[1]:+.4f} m\n"
                f"  Z = {geodetic_to_ecef(lat,lon,h,ell)[2]:+.4f} m\n"
            )
            self._show(self.res_enu_geo, out)
        except ValueError as ex:
            messagebox.showerror("Input Error", str(ex))

    # ── Tab 5: ECEF → ENU ─────────────────────────────────────────────────────
    def _build_ecef_enu(self, f):
        self._section(f, "INPUT — ECEF Point", ACCENT)
        p = tk.Frame(f, bg=PANEL_BG,
                     highlightthickness=1, highlightbackground=BORDER)
        p.pack(fill="x", padx=16, pady=4)
        self.e2n_X = self._row(p, "X (m)", "-2694044.9706", "metres")
        self.e2n_Y = self._row(p, "Y (m)", "-4266843.3528", "metres")
        self.e2n_Z = self._row(p, "Z (m)",  "3887339.9725", "metres")

        self._section(f, "ORIGIN — Local ENU Reference (Geodetic)", ACCENT3)
        o = tk.Frame(f, bg=PANEL_BG,
                     highlightthickness=1, highlightbackground=BORDER)
        o.pack(fill="x", padx=16, pady=4)
        self.e2n_lat0 = self._row(o, "Origin Lat φ₀ (°)",  "37.3500",  "decimal degrees")
        self.e2n_lon0 = self._row(o, "Origin Lon λ₀ (°)", "-122.0500", "decimal degrees")
        self.e2n_h0   = self._row(o, "Origin h₀ (m)",       "0.0",     "ellipsoidal height")

        self._btn(f, "  Convert →  ", self._do_ecef_enu)
        self._section(f, "RESULT — ENU (East, North, Up)", ACCENT2)
        self.res_ecef_enu = self._result_box(f, 6)

    def _do_ecef_enu(self):
        try:
            X = float(self.e2n_X.get()); Y = float(self.e2n_Y.get()); Z = float(self.e2n_Z.get())
            lat0 = float(self.e2n_lat0.get()); lon0 = float(self.e2n_lon0.get()); h0 = float(self.e2n_h0.get())
            ell = self._get_ellipsoid()
            e, n, u = ecef_to_enu(X, Y, Z, lat0, lon0, h0, ell)
            dist_3d = math.sqrt(e**2 + n**2 + u**2)
            az = math.degrees(math.atan2(e, n)) % 360
            out = (
                f"Ellipsoid  : {ELLIPSOIDS[ell]['full']}\n"
                f"─────────────────────────────────────────\n"
                f"East   (E) : {e:+.4f} m\n"
                f"North  (N) : {n:+.4f} m\n"
                f"Up     (U) : {u:+.4f} m\n"
                f"─────────────────────────────────────────\n"
                f"3D distance: {dist_3d:.4f} m\n"
                f"Azimuth    : {az:.4f}°\n"
            )
            self._show(self.res_ecef_enu, out)
        except ValueError as ex:
            messagebox.showerror("Input Error", str(ex))

    # ── Tab 6: ENU → ECEF ─────────────────────────────────────────────────────
    def _build_enu_ecef(self, f):
        self._section(f, "INPUT — ENU Coordinates", ACCENT)
        p = tk.Frame(f, bg=PANEL_BG,
                     highlightthickness=1, highlightbackground=BORDER)
        p.pack(fill="x", padx=16, pady=4)
        self.n2e_e = self._row(p, "East  E (m)",  "3983.1", "metres")
        self.n2e_n = self._row(p, "North N (m)",  "4027.5", "metres")
        self.n2e_u = self._row(p, "Up    U (m)",   "100.0", "metres")

        self._section(f, "ORIGIN — Local ENU Reference (Geodetic)", ACCENT3)
        o = tk.Frame(f, bg=PANEL_BG,
                     highlightthickness=1, highlightbackground=BORDER)
        o.pack(fill="x", padx=16, pady=4)
        self.n2e_lat0 = self._row(o, "Origin Lat φ₀ (°)",  "37.3500",  "decimal degrees")
        self.n2e_lon0 = self._row(o, "Origin Lon λ₀ (°)", "-122.0500", "decimal degrees")
        self.n2e_h0   = self._row(o, "Origin h₀ (m)",       "0.0",     "ellipsoidal height")

        self._btn(f, "  Convert →  ", self._do_enu_ecef)
        self._section(f, "RESULT — ECEF (X, Y, Z)", ACCENT2)
        self.res_enu_ecef = self._result_box(f, 6)

    def _do_enu_ecef(self):
        try:
            e  = float(self.n2e_e.get()); n  = float(self.n2e_n.get()); u  = float(self.n2e_u.get())
            lat0 = float(self.n2e_lat0.get()); lon0 = float(self.n2e_lon0.get()); h0 = float(self.n2e_h0.get())
            ell = self._get_ellipsoid()
            X, Y, Z = enu_to_ecef(e, n, u, lat0, lon0, h0, ell)
            out = (
                f"Ellipsoid  : {ELLIPSOIDS[ell]['full']}\n"
                f"─────────────────────────────────────────\n"
                f"X          : {X:+.4f} m\n"
                f"Y          : {Y:+.4f} m\n"
                f"Z          : {Z:+.4f} m\n"
                f"─────────────────────────────────────────\n"
                f"Radius |r| : {math.sqrt(X**2+Y**2+Z**2):.4f} m\n"
            )
            self._show(self.res_enu_ecef, out)
        except ValueError as ex:
            messagebox.showerror("Input Error", str(ex))


if __name__ == "__main__":
    app = GeoCoordApp()
    app.mainloop()
