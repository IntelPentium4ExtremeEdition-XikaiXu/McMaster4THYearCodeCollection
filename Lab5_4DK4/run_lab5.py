#!/usr/bin/env python3
"""Run the Lab 5 cross-layer experiments and write plots plus CSV tables."""

import csv
import statistics
import subprocess
import sys
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src" / "cross_layer.c"
EXE = ROOT / "src" / "cross_layer"
OUT = ROOT / "results"

# Same family of seeds as Lab 4. The third value drives reservation coin flips.
SEEDS = [
    ("400440917", "400460804", "230411341234134134"),
    ("400460804", "230411341234134134", "400440917"),
    ("230411341234134134", "400440917", "400460804"),
]

TEND = "20000"
PALETTE = ["#1f4e79", "#c45911", "#2e7d32", "#6a1b9a", "#00838f", "#ad1457", "#455a64", "#ef6c00"]
MARKERS = ["o", "s", "D", "^", "v", "P", "X", "h"]


def build():
    subprocess.check_call(
        ["gcc", "-O2", "-Wall", "-Wextra", "-std=c11", "-o", str(EXE), str(SRC)]
    )


def parse_result(text):
    result = None
    for line in text.splitlines():
        if line.startswith("RESULT"):
            result = {}
            for tok in line.split()[1:]:
                k, v = tok.split("=")
                result[k] = float(v) if "." in v or "e" in v.lower() else int(v)
    if result is None:
        raise RuntimeError("no RESULT\n" + text)
    return result


def run_job(job):
    cmd = [str(EXE)]
    for key, val in job["args"]:
        cmd.extend([key, str(val)])
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(
            "failed " + " ".join(cmd) + "\n" + proc.stderr + proc.stdout[-500:]
        )
    row = dict(job["meta"])
    row.update(parse_result(proc.stdout))
    row["t_sys"] = max(row["tc0"], row["tc1"])
    return row


def submit(pool, jobs, rows):
    futs = [pool.submit(run_job, job) for job in jobs]
    for fut in as_completed(futs):
        rows.append(fut.result())
    return rows


def job(meta, extra, seed):
    args = [
        ("--ws", meta["ws"]),
        ("--wr", meta["wr"]),
        ("--pd", meta["pd"]),
        ("--pa", meta["pa"]),
        ("--timeout", meta["timeout"]),
        ("--n", meta["n"]),
        ("--tend", meta["tend"]),
        ("--mac", meta["mac"]),
        ("--timer", meta["timer"]),
        ("--p", meta.get("p", 0.5)),
        ("--seed-data", seed[0]),
        ("--seed-ack", seed[1]),
        ("--seed-mac", seed[2]),
        ("--trace", 0),
    ]
    args.extend(extra)
    return {"meta": meta, "args": args}


def seeds_for(meta):
    random = meta["mac"] == "aloha" or float(meta["pd"]) > 0 or float(meta["pa"]) > 0
    return SEEDS if random else SEEDS[:1]


def base_meta(**kwargs):
    meta = {
        "pd": 0,
        "pa": 0,
        "timeout": 15,
        "n": 0,
        "tend": TEND,
        "timer": "tx",
        "p": 0.5,
        "wr": 1,
    }
    meta.update(kwargs)
    return meta


def expand(metas):
    jobs = []
    for meta in metas:
        for seed in seeds_for(meta):
            item = dict(meta)
            item["seed"] = seed[0]
            jobs.append(job(item, [], seed))
    return jobs


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    keys = []
    seen = set()
    for row in rows:
        for k in row:
            if k not in seen:
                seen.add(k)
                keys.append(k)
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)


def group_mean(rows, key_fields, y_fields):
    buckets = defaultdict(list)
    for row in rows:
        buckets[tuple(row[k] for k in key_fields)].append(row)
    out = []
    for key, items in buckets.items():
        rec = {k: key[i] for i, k in enumerate(key_fields)}
        rec["nseed"] = len(items)
        for y in y_fields:
            vals = [float(it[y]) for it in items]
            rec[y] = statistics.fmean(vals)
            rec[y + "_std"] = statistics.pstdev(vals) if len(vals) > 1 else 0.0
        out.append(rec)
    return out


def style_ax(ax, xlabel, ylabel, title):
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=8)


def save(fig, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=140)
    plt.close(fig)


def series_label(mac, timer=None, proto=None):
    mac_name = "scheduled" if mac == "sched" else "slotted ALOHA"
    parts = []
    if proto:
        parts.append(proto)
    parts.append(mac_name)
    if timer:
        parts.append("timer@" + timer)
    return ", ".join(parts)


def plot_xy(path, curves, xlabel, ylabel, title, theory=None):
    fig, ax = plt.subplots(figsize=(7.4, 4.8))
    if theory is not None:
        xs, ys, label = theory
        ax.plot(xs, ys, color="0.45", lw=1.2, label=label)
    for i, curve in enumerate(curves):
        curve["color"] = PALETTE[i % len(PALETTE)]
        curve["marker"] = MARKERS[i % len(MARKERS)]
        ax.errorbar(
            curve["x"],
            curve["y"],
            yerr=curve.get("yerr"),
            marker=curve.get("marker", "o"),
            color=curve.get("color"),
            ls=curve.get("ls", "-"),
            capsize=3,
            label=curve["label"],
        )
    style_ax(ax, xlabel, ylabel, title)
    save(fig, path)


def traces():
    dest = OUT / "traces"
    dest.mkdir(parents=True, exist_ok=True)
    cases = [
        ("sw_sched", ["--ws", "1", "--wr", "1", "--n", "3", "--mac", "sched", "--timeout", "15", "--pd", "0", "--pa", "0"]),
        ("gbn_sched", ["--ws", "4", "--wr", "1", "--n", "6", "--mac", "sched", "--timeout", "15", "--pd", "0", "--pa", "0"]),
        ("gbn_drop", ["--ws", "4", "--wr", "1", "--n", "4", "--mac", "sched", "--timeout", "15", "--pd", "0.5", "--pa", "0"]),
        ("aloha_sw", ["--ws", "1", "--wr", "1", "--n", "2", "--mac", "aloha", "--p", "0.5", "--timeout", "15", "--pd", "0", "--pa", "0", "--seed-mac", "400440917"]),
    ]
    for name, args in cases:
        cmd = [str(EXE), "--timer", "tx", "--trace", "1", "--tend", "20000", *args]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        (dest / f"{name}.log").write_text(proc.stdout)
        if proc.returncode != 0:
            raise RuntimeError(name + "\n" + proc.stderr)


def exp_ws(pool):
    metas = []
    for mac in ("sched", "aloha"):
        for ws in (1, 2, 3, 4, 5, 6, 8, 11, 16, 24):
            metas.append(base_meta(exp="ws", proto="GBN" if ws > 1 else "S&W", mac=mac, ws=ws, wr=1))
            if ws > 1:
                metas.append(base_meta(exp="ws", proto="SR", mac=mac, ws=ws, wr=ws))
    rows = submit(pool, expand(metas), [])
    return rows


def exp_tout(pool):
    metas = []
    touts = (8, 11, 12, 15, 20, 25, 30, 40, 50, 60, 80)
    for tout in touts:
        for timer in ("tx", "ready"):
            for mac in ("sched", "aloha"):
                metas.append(base_meta(
                    exp="tout", case="pd0", proto="GBN", mac=mac, timer=timer,
                    ws=16, wr=1, timeout=tout, pd=0,
                ))
            metas.append(base_meta(
                exp="tout", case="pd0", proto="S&W", mac="sched", timer=timer,
                ws=1, wr=1, timeout=tout, pd=0,
            ))
        for mac in ("sched", "aloha"):
            metas.append(base_meta(
                exp="tout", case="pd0.1", proto="GBN", mac=mac, timer="tx",
                ws=16, wr=1, timeout=tout, pd=0.1,
            ))
            metas.append(base_meta(
                exp="tout", case="pd0.1", proto="SR", mac=mac, timer="tx",
                ws=16, wr=16, timeout=tout, pd=0.1,
            ))
    # Keep the error sweep on a slightly coarser timeout grid by filtering later.
    rows = submit(pool, expand(metas), [])
    return rows


def exp_pd(pool):
    metas = []
    for pd in (0, 0.02, 0.05, 0.1, 0.15, 0.2, 0.3, 0.5):
        for mac in ("sched", "aloha"):
            metas.append(base_meta(exp="pd", proto="S&W", mac=mac, ws=1, wr=1, pd=pd))
            metas.append(base_meta(exp="pd", proto="GBN", mac=mac, ws=16, wr=1, pd=pd))
            metas.append(base_meta(exp="pd", proto="SR", mac=mac, ws=16, wr=16, pd=pd))
    return submit(pool, expand(metas), [])


def exp_finite(pool):
    metas = []
    for pd in (0, 0.05):
        for mac in ("sched", "aloha"):
            for ws in (1, 2, 4, 8, 11, 16, 24):
                metas.append(base_meta(
                    exp="finite", proto="GBN" if ws > 1 else "S&W", mac=mac,
                    ws=ws, wr=1, pd=pd, n=100, tend=1e7,
                ))
                if ws > 1:
                    metas.append(base_meta(
                        exp="finite", proto="SR", mac=mac,
                        ws=ws, wr=ws, pd=pd, n=100, tend=1e7,
                    ))
    return submit(pool, expand(metas), [])


YS = ["S0", "S1", "Seff", "occ", "att0", "att1", "ad0", "ad1", "t_sys", "del0", "del1"]


def curves_from(means, xkey, ykey, selector, label_fn):
    chosen = [r for r in means if selector(r)]
    groups = defaultdict(list)
    for r in chosen:
        groups[label_fn(r)].append(r)
    curves = []
    for label, items in groups.items():
        items = sorted(items, key=lambda r: float(r[xkey]))
        sample = items[0]
        curves.append({
            "label": label,
            "x": [float(r[xkey]) for r in items],
            "y": [float(r[ykey]) for r in items],
            "yerr": [float(r[ykey + "_std"]) for r in items],
            "ls": "--" if sample.get("timer") == "ready" else "-",
        })
    return curves


def plot_all(ws, tout, pd_rows, finite):
    ws_m = group_mean(ws, ["proto", "mac", "ws"], YS)
    tout_m = group_mean(tout, ["case", "proto", "mac", "timer", "timeout", "ws"], YS)
    pd_m = group_mean(pd_rows, ["proto", "mac", "pd", "ws"], YS)
    fin_m = group_mean(finite, ["proto", "mac", "pd", "ws"], YS)

    write_csv(OUT / "ws" / "means.csv", ws_m)
    write_csv(OUT / "tout" / "means.csv", tout_m)
    write_csv(OUT / "pd" / "means.csv", pd_m)
    write_csv(OUT / "finite" / "means.csv", fin_m)

    xs = sorted({int(r["ws"]) for r in ws_m if r["proto"] in ("GBN", "S&W") and r["mac"] == "sched"})
    theory = (xs, [min(0.5, w / 21.0) for w in xs], r"scheduled analysis  min(0.5, $W_s$/21)")

    def ws_curves(ykey, protos):
        return curves_from(
            ws_m, "ws", ykey,
            lambda r: r["proto"] in protos,
            lambda r: series_label(r["mac"], proto=r["proto"]),
        )

    plot_xy(
        OUT / "ws" / "throughput_vs_Ws.png",
        ws_curves("S0", ("S&W", "GBN", "SR")),
        "Send window Ws (frames)",
        "Normalized throughput of link 0",
        "pd = pa = 0, Tout = 15 ms, timer starts at transmission",
        theory=theory,
    )
    plot_xy(
        OUT / "ws" / "efficiency_vs_Ws.png",
        ws_curves("Seff", ("S&W", "GBN", "SR")),
        "Send window Ws (frames)",
        "Shared-channel efficiency S0 + S1",
        "pd = pa = 0, Tout = 15 ms, timer starts at transmission",
    )
    plot_xy(
        OUT / "ws" / "access_delay_vs_Ws.png",
        ws_curves("ad0", ("S&W", "GBN")),
        "Send window Ws (frames)",
        "Mean access delay of link 0 (ms)",
        "Time from a frame becoming eligible until its data transmission",
    )

    def tout_curves(case, ykey, timer_filter=None):
        return curves_from(
            tout_m, "timeout", ykey,
            lambda r: r["case"] == case and (timer_filter is None or r["timer"] == timer_filter),
            lambda r: series_label(r["mac"], r["timer"], r["proto"] + ("" if r["proto"] == "S&W" else " Ws=16")),
        )

    plot_xy(
        OUT / "tout" / "efficiency_vs_Tout_pd0.png",
        tout_curves("pd0", "Seff"),
        "Retransmission timeout Tout (ms)",
        "Shared-channel efficiency S0 + S1",
        "No channel errors. Solid: timer at tx. Dashed: timer at eligibility.",
    )
    plot_xy(
        OUT / "tout" / "attempts_vs_Tout_pd0.png",
        tout_curves("pd0", "att0"),
        "Retransmission timeout Tout (ms)",
        "Transmissions per ACKed frame (link 0)",
        "No channel errors. Values above 1 are timeouts that fired too early.",
    )
    plot_xy(
        OUT / "tout" / "efficiency_vs_Tout_pd0.1.png",
        tout_curves("pd0.1", "Seff", "tx"),
        "Retransmission timeout Tout (ms)",
        "Shared-channel efficiency S0 + S1",
        "pd = 0.1, pa = 0, timer starts at transmission, Ws = 16",
    )

    plot_xy(
        OUT / "pd" / "efficiency_vs_pd.png",
        curves_from(pd_m, "pd", "Seff", lambda r: True, lambda r: series_label(r["mac"], proto=r["proto"])),
        "Data-frame error probability pd",
        "Shared-channel efficiency S0 + S1",
        "pa = 0, Tout = 15 ms, timer at tx, GBN/SR Ws = 16",
    )
    plot_xy(
        OUT / "pd" / "attempts_vs_pd.png",
        curves_from(pd_m, "pd", "att0", lambda r: True, lambda r: series_label(r["mac"], proto=r["proto"])),
        "Data-frame error probability pd",
        "Transmissions per ACKed frame (link 0)",
        "pa = 0, Tout = 15 ms, timer at tx, GBN/SR Ws = 16",
    )
    plot_xy(
        OUT / "pd" / "occupancy_vs_pd.png",
        curves_from(pd_m, "pd", "occ", lambda r: r["mac"] == "sched", lambda r: series_label(r["mac"], proto=r["proto"])),
        "Data-frame error probability pd",
        "Forward-channel busy fraction",
        "Scheduled minislots. Busy fraction counts retransmissions; efficiency does not.",
    )

    for pd, tag in ((0, "pd0"), (0.05, "pd0.05")):
        plot_xy(
            OUT / "finite" / f"completion_vs_Ws_{tag}.png",
            curves_from(
                fin_m, "ws", "t_sys",
                lambda r, pd=pd: float(r["pd"]) == pd,
                lambda r: series_label(r["mac"], proto=r["proto"]),
            ),
            "Send window Ws (frames)",
            "System completion time (ms)",
            f"Each link sends N = 100 frames, pd = {pd:g}, pa = 0, Tout = 15 ms",
        )

    return ws_m, tout_m, pd_m, fin_m


def summary(ws_m, tout_m, pd_m, fin_m):
    lines = ["Lab 5 summary (means across seeds)", ""]

    def pick(rows, **want):
        for r in rows:
            if all(str(r[k]) == str(v) or r[k] == v for k, v in want.items()):
                return r
        return None

    lines.append("[ws sched GBN/S&W, link 0 throughput, analysis Ws/21 capped at 0.5]")
    for r in sorted(ws_m, key=lambda z: (z["mac"], z["proto"], int(z["ws"]))):
        if r["mac"] != "sched" or r["proto"] == "SR":
            continue
        pred = min(0.5, int(r["ws"]) / 21.0)
        lines.append(
            f"  Ws={int(r['ws']):2d}  S0={r['S0']:.4f}  pred={pred:.4f}  "
            f"Seff={r['Seff']:.4f}  ad={r['ad0']:.2f} ms"
        )
    lines.append("")
    lines.append("[aloha vs sched at Ws=16 pd=0]")
    for mac in ("sched", "aloha"):
        r = pick(ws_m, proto="GBN", mac=mac, ws=16)
        lines.append(f"  {mac:5s} S0={r['S0']:.4f} S1={r['S1']:.4f} Seff={r['Seff']:.4f} ad={r['ad0']:.2f}")
    lines.append("")
    lines.append("[timeout pd=0 GBN Ws=16 Seff]")
    for timer in ("tx", "ready"):
        for mac in ("sched", "aloha"):
            chunk = [
                r for r in tout_m
                if r["case"] == "pd0" and r["proto"] == "GBN" and r["timer"] == timer and r["mac"] == mac
            ]
            chunk.sort(key=lambda r: float(r["timeout"]))
            txt = " ".join(f"{int(r['timeout'])}:{r['Seff']:.3f}" for r in chunk)
            lines.append(f"  {mac} timer@{timer}  {txt}")
    lines.append("")
    lines.append("[pd sweep Seff sched]")
    for proto in ("S&W", "GBN", "SR"):
        chunk = [r for r in pd_m if r["proto"] == proto and r["mac"] == "sched"]
        chunk.sort(key=lambda r: float(r["pd"]))
        txt = " ".join(f"{float(r['pd']):.2f}:{r['Seff']:.3f}" for r in chunk)
        lines.append(f"  {proto} {txt}")
    lines.append("")
    lines.append("[finite N=100 sched pd=0 completion]")
    chunk = [r for r in fin_m if r["mac"] == "sched" and float(r["pd"]) == 0 and r["proto"] in ("S&W", "GBN")]
    for r in sorted(chunk, key=lambda z: int(z["ws"])):
        lines.append(f"  {r['proto']} Ws={int(r['ws']):2d}  Tsys={r['t_sys']:.1f} ms")
    text = "\n".join(lines) + "\n"
    (OUT / "summary.txt").write_text(text)
    print(text)


def main():
    build()
    traces()
    workers = min(8, __import__("os").cpu_count() or 2)
    with ProcessPoolExecutor(max_workers=workers) as pool:
        ws = exp_ws(pool)
        tout = exp_tout(pool)
        pd_rows = exp_pd(pool)
        finite = exp_finite(pool)
    write_csv(OUT / "ws" / "raw.csv", ws)
    write_csv(OUT / "tout" / "raw.csv", tout)
    write_csv(OUT / "pd" / "raw.csv", pd_rows)
    write_csv(OUT / "finite" / "raw.csv", finite)
    summary(*plot_all(ws, tout, pd_rows, finite))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)
