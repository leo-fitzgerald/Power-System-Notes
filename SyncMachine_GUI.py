# Leo Fitzgerald
# Synchronous Machine Three Phase Short Circuit Fault Response
# Combined calculation engine and Tkinter GUI
# 15th September 2024 (original), updated with GUI and corrected formulae
#
# Derived from lecture notes by Dr. Brian Johnston
# at University of Idaho Power Systems

import math
import numpy as np
import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk


# --------------- Calculation functions ---------------

def calc_Iass(Eass, Xdss, X_tran):
    """Calculate subtransient current phasor: E'' / j(Xd'' + X_tran)."""
    return Eass / (complex(0, Xdss) + complex(0, X_tran))


def calc_Ias(Eas, Xds, X_tran):
    """Calculate transient current phasor: E' / j(Xd' + X_tran)."""
    return Eas / (complex(0, Xds) + complex(0, X_tran))


def calc_Iss(Ea, Xd, X_tran):
    """Calculate steady-state current phasor: E / j(Xd + X_tran)."""
    return Ea / (complex(0, Xd) + complex(0, X_tran))


def calc_Idcoffsetmax(Eass, Xdss, X_tran):
    """Calculate maximum DC offset current magnitude."""
    return math.sqrt(2) * (Eass / (Xdss + X_tran))


def Iss_time(t, Ea, Xd, X_tran, omega):
    """Steady-state AC short-circuit current vs time."""
    Iss = calc_Iss(Ea, Xd, X_tran)
    return math.sqrt(2) * abs(Iss) * np.cos(omega * t)


def Itransient(t, Eas, Xds, X_tran, omega, Tds):
    """Transient AC short-circuit current component vs time."""
    Ias = calc_Ias(Eas, Xds, X_tran)
    return np.exp(-t / Tds) * math.sqrt(2) * abs(Ias) * np.cos(omega * t)


def Isubtransient(t, Eass, Xdss, X_tran, omega, Tdss):
    """Subtransient AC short-circuit current component vs time."""
    Iass = calc_Iass(Eass, Xdss, X_tran)
    return np.exp(-t / Tdss) * math.sqrt(2) * abs(Iass) * np.cos(omega * t)


def fullsymresponse(t, E, Xd, Xds, Xdss, X_tran, Tds, Tdss, omega):
    """Total symmetrical (AC) short-circuit current.

    Formula (standard textbook form):
        i_sym(t) = sqrt(2) * E * [ 1/(Xd  + X_tran)
            + (1/(Xd' + X_tran) - 1/(Xd  + X_tran)) * exp(-t/Td')
            + (1/(Xd''+ X_tran) - 1/(Xd' + X_tran)) * exp(-t/Td'')
        ] * cos(omega * t)

    At t=0 the envelope equals sqrt(2)*E/(Xd''+X_tran)  (subtransient).
    As t -> inf the envelope decays to sqrt(2)*E/(Xd+X_tran)  (steady-state).
    """
    envelope = (
        1.0 / (Xd + X_tran)
        + (1.0 / (Xds + X_tran) - 1.0 / (Xd + X_tran)) * np.exp(-t / Tds)
        + (1.0 / (Xdss + X_tran) - 1.0 / (Xds + X_tran)) * np.exp(-t / Tdss)
    )
    return math.sqrt(2) * E * envelope * np.cos(omega * t)


# --------------- GUI Application ---------------

class SyncMachineGUI:
    """Tkinter GUI for synchronous machine short-circuit analysis."""

    # Default generator parameter values
    DEFAULTS = {
        "S_rated": 20.0,
        "VLL": 13.8,
        "Xdss": 0.145,
        "Xds": 0.240,
        "Xd": 1.100,
        "freq": 50.0,
        "X_tran": 0.0,
        "V_term": 1.0,
        "Tdss": 0.035,
        "Tds": 1.0,
        "Ta": 0.2,
    }

    # Labels and units for each parameter
    PARAM_INFO = {
        "S_rated": ("Rated Power (MVA)", "MVA"),
        "VLL": ("Line-Line Voltage", "kV"),
        "Xdss": ("Subtransient Reactance  Xd''", "pu"),
        "Xds": ("Transient Reactance  Xd'", "pu"),
        "Xd": ("Synchronous Reactance  Xd", "pu"),
        "freq": ("System Frequency", "Hz"),
        "X_tran": ("External Reactance  X_tran", "pu"),
        "V_term": ("Terminal Voltage", "pu"),
        "Tdss": ("Subtransient Time Const  Td''", "sec"),
        "Tds": ("Transient Time Const  Td'", "sec"),
        "Ta": ("Armature Time Const  Ta", "sec"),
    }

    PARAM_ORDER = [
        "S_rated", "VLL", "freq", "V_term",
        "Xdss", "Xds", "Xd", "X_tran",
        "Tdss", "Tds", "Ta",
    ]

    def __init__(self, root):
        self.root = root
        self.root.title("Synchronous Machine \u2013 Three-Phase Short Circuit")
        self.root.minsize(1100, 750)

        self.entries = {}
        self._build_ui()

    # ---- UI construction ----

    def _build_ui(self):
        # Main horizontal paned window: left = controls, right = plot
        pane = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        pane.pack(fill=tk.BOTH, expand=True)

        # --- Left panel: parameters ---
        left = ttk.Frame(pane, padding=10)
        pane.add(left, weight=0)

        title = ttk.Label(left, text="Generator Parameters",
                          font=("TkDefaultFont", 13, "bold"))
        title.pack(anchor=tk.W, pady=(0, 8))

        param_frame = ttk.Frame(left)
        param_frame.pack(fill=tk.X)

        for idx, key in enumerate(self.PARAM_ORDER):
            label_text, unit = self.PARAM_INFO[key]
            lbl = ttk.Label(param_frame, text=label_text)
            lbl.grid(row=idx, column=0, sticky=tk.W, pady=3, padx=(0, 6))

            var = tk.StringVar(value=str(self.DEFAULTS[key]))
            entry = ttk.Entry(param_frame, textvariable=var, width=12,
                              justify=tk.RIGHT)
            entry.grid(row=idx, column=1, pady=3, padx=(0, 4))
            self.entries[key] = var

            unit_lbl = ttk.Label(param_frame, text=unit, foreground="gray")
            unit_lbl.grid(row=idx, column=2, sticky=tk.W, pady=3)

        # Buttons
        btn_frame = ttk.Frame(left)
        btn_frame.pack(fill=tk.X, pady=(16, 0))

        plot_btn = ttk.Button(btn_frame, text="Plot", command=self._on_plot)
        plot_btn.pack(side=tk.LEFT, padx=(0, 8))

        reset_btn = ttk.Button(btn_frame, text="Reset Defaults",
                               command=self._reset_defaults)
        reset_btn.pack(side=tk.LEFT)

        # Computed values display
        self.info_var = tk.StringVar(value="")
        info_lbl = ttk.Label(left, textvariable=self.info_var,
                             font=("TkDefaultFont", 9), foreground="gray30",
                             justify=tk.LEFT)
        info_lbl.pack(anchor=tk.W, pady=(14, 0))

        # --- Right panel: matplotlib figure ---
        right = ttk.Frame(pane, padding=4)
        pane.add(right, weight=1)

        self.fig = Figure(figsize=(9, 8), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=right)
        toolbar = NavigationToolbar2Tk(self.canvas, right)
        toolbar.update()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Draw initial plot with default values
        self._on_plot()

    # ---- Actions ----

    def _read_params(self):
        """Read and validate all parameter entries. Returns dict or None."""
        params = {}
        for key in self.PARAM_ORDER:
            raw = self.entries[key].get().strip()
            try:
                val = float(raw)
            except ValueError:
                messagebox.showerror(
                    "Invalid Input",
                    f"'{raw}' is not a valid number for "
                    f"{self.PARAM_INFO[key][0]}.")
                return None
            if key in ("S_rated", "VLL", "freq") and val <= 0:
                messagebox.showerror(
                    "Invalid Input",
                    f"{self.PARAM_INFO[key][0]} must be positive.")
                return None
            if key in ("Xdss", "Xds", "Xd") and val <= 0:
                messagebox.showerror(
                    "Invalid Input",
                    f"{self.PARAM_INFO[key][0]} must be > 0.")
                return None
            if key in ("Tdss", "Tds", "Ta") and val <= 0:
                messagebox.showerror(
                    "Invalid Input",
                    f"{self.PARAM_INFO[key][0]} must be > 0.")
                return None
            params[key] = val
        return params

    def _on_plot(self):
        """Validate inputs, run calculations, and update the plot."""
        params = self._read_params()
        if params is None:
            return

        omega = 2 * math.pi * params["freq"]
        V_term = params["V_term"]
        Xdss = params["Xdss"]
        Xds = params["Xds"]
        Xd = params["Xd"]
        X_tran = params["X_tran"]
        Tdss = params["Tdss"]
        Tds = params["Tds"]
        Ta = params["Ta"]
        S_rated = params["S_rated"]
        VLL = params["VLL"]

        # EMF values (all equal to terminal voltage for this model)
        E = V_term

        # Derived quantities
        X2 = Xdss
        L2 = (X2 / omega) * ((VLL ** 2) / S_rated)
        Ra = L2 / Ta

        # Base current
        Ibase = (S_rated * 1e6) / (math.sqrt(3) * VLL * 1e3)

        # Time vector
        t = np.arange(0, 2, 0.00001)

        # Compute individual current components (per-unit)
        iss = Iss_time(t, E, Xd, X_tran, omega)
        itrans = Itransient(t, E, Xds, X_tran, omega, Tds)
        isubtrans = Isubtransient(t, E, Xdss, X_tran, omega, Tdss)

        # Total symmetrical (AC) response
        isym = fullsymresponse(t, E, Xd, Xds, Xdss, X_tran, Tds, Tdss, omega)

        # Update info label with computed magnitudes
        Iss_mag = abs(calc_Iss(E, Xd, X_tran))
        Ias_mag = abs(calc_Ias(E, Xds, X_tran))
        Iass_mag = abs(calc_Iass(E, Xdss, X_tran))
        Idc_max = calc_Idcoffsetmax(E, Xdss, X_tran)
        self.info_var.set(
            f"Ibase  = {Ibase:,.1f} A\n"
            f"Ra     = {Ra:.6f} pu\n"
            f"\n"
            f"|Iss|   = {Iss_mag:.4f} pu  ({Iss_mag * Ibase:,.1f} A)\n"
            f"|Ias'|  = {Ias_mag:.4f} pu  ({Ias_mag * Ibase:,.1f} A)\n"
            f"|Iass''| = {Iass_mag:.4f} pu  ({Iass_mag * Ibase:,.1f} A)\n"
            f"Idc_max = {Idc_max:.4f} pu  ({Idc_max * Ibase:,.1f} A)"
        )

        # ---- Draw plots ----
        self.fig.clear()

        # 1) All individual components overlaid
        ax1 = self.fig.add_subplot(5, 1, 1)
        ax1.plot(t, iss, label="Iss (steady-state)")
        ax1.plot(t, itrans, label="Itransient")
        ax1.plot(t, isubtrans, label="Isubtransient")
        ax1.legend(loc="upper right", fontsize=8)
        ax1.set_xlim(0, 0.8)
        ax1.set_ylabel("Current (pu)")
        ax1.set_title("Individual Components", fontsize=10)

        # 2) Isubtransient
        ax2 = self.fig.add_subplot(5, 1, 2)
        ax2.plot(t, isubtrans, color="green")
        ax2.set_xlim(0, 0.8)
        ax2.set_ylabel("Current (pu)")
        ax2.set_title("Isubtransient", fontsize=10)

        # 3) Itransient
        ax3 = self.fig.add_subplot(5, 1, 3)
        ax3.plot(t, itrans, color="orange")
        ax3.set_xlim(0, 0.8)
        ax3.set_ylabel("Current (pu)")
        ax3.set_title("Itransient", fontsize=10)

        # 4) Iss (steady-state)
        ax4 = self.fig.add_subplot(5, 1, 4)
        ax4.plot(t, iss, color="blue")
        ax4.set_xlim(0, 0.8)
        ax4.set_ylabel("Current (pu)")
        ax4.set_title("Iss (steady-state)", fontsize=10)

        # 5) Total symmetrical response
        ax5 = self.fig.add_subplot(5, 1, 5)
        ax5.plot(t, isym, color="red")
        ax5.set_xlim(0, 0.8)
        ax5.set_xlabel("Time (s)")
        ax5.set_ylabel("Current (pu)")
        ax5.set_title("Total Symmetrical Response", fontsize=10)

        self.fig.tight_layout()
        self.canvas.draw()

    def _reset_defaults(self):
        """Reset all entries to default values."""
        for key, val in self.DEFAULTS.items():
            self.entries[key].set(str(val))


# --------------- Main ---------------

if __name__ == "__main__":
    root = tk.Tk()
    app = SyncMachineGUI(root)
    root.mainloop()
