#!/usr/bin/env python3
"""Run the Lab 4 ARQ experiments described by experiments/lab.ini and draw the figures."""

import configparser
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
PIPE_MS = 11.0  # tx 1 ms + propagation 5 ms each way

CLI = {
    "ws": "--ws",
    "wr": "--wr",
    "pd": "--pd",
    "pa": "--pa",
    "timeout_ms": "--timeout",
    "n": "--n",
    "deliver_limit": "--limit",
}

MARKERS = ["o", "s", "D", "^", "v", "P", "X", "h"]
COLORS = ["C0", "C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9"]


def parser():
    cfg = configparser.ConfigParser(interpolation=None)
    cfg.optionxform = str
    return cfg


def build_exe():
    src = ROOT / "ARQSimBackEnd" / "ARQBackEnd.c"
    exe = ROOT / "ARQSimBackEnd" / "arq_sim"
    subprocess.check_call(
        ["gcc", "-O2", "-Wall", "-Wextra", "-std=c11", "-o", str(exe), str(src)]
    )
    return exe


def load_ini(path):
    cfg = parser()
    if not cfg.read(path):
        raise SystemExit(f"cannot read {path}")
    return cfg


def split_csv(text):
    return [p.strip() for p in text.split(",") if p.strip()]


def sections(cfg, prefix):
    found = []
    for name in cfg.sections():
        if name == prefix or name.startswith(prefix + "."):
            found.append(name)
    return found


def run_process(exe, args):
    proc = subprocess.run([str(exe), *args], capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(
            "command failed:\n"
            + " ".join([str(exe), *args])
            + "\n"
            + proc.stderr
            + proc.stdout
        )
    header = ""
    events = []
    result = None
    for line in proc.stdout.splitlines():
        if line.startswith("TRACE_HEADER"):
            header = line
        elif line.startswith("TRACE "):
            _, t, name, seq = line.split()
            events.append((float(t), name, int(seq)))
        elif line.startswith("RESULT"):
            _, eff, att, time_ms, delivered, tx = line.split()
            result = {
                "efficiency": float(eff),
                "attempts": float(att),
                "completion": float(time_ms),
                "delivered": int(delivered),
                "tx": int(tx),
            }
    if result is None:
        raise RuntimeError("no RESULT line from " + " ".join(args))
    return header, events, result


def job_args(params, seed_data, seed_ack, trace):
    args = []
    for key, flag in CLI.items():
        args.extend([flag, str(params[key])])
    args.extend(["--seed-data", seed_data, "--seed-ack", seed_ack, "--trace", "1" if trace else "0"])
    return args


def parse_seeds(text):
    pairs = []
    for item in split_csv(text):
        data, ack = item.split(":")
        pairs.append((data.strip(), ack.strip()))
    if not pairs:
        raise SystemExit(f"no seeds in '{text}'")
    return pairs


def base_params(cfg):
    fixed = cfg["fixed"]
    params = {
        "ws": fixed.get("ws", "1"),
        "wr": fixed.get("wr", "1"),
        "pd": fixed.get("pd", "0"),
        "pa": fixed.get("pa", "0"),
        "timeout_ms": fixed.get("timeout_ms", "15"),
        "n": fixed.get("n", "0"),
        "deliver_limit": fixed.get("deliver_limit", "100000"),
    }
    return params


def series_params(base, section):
    params = dict(base)
    for key in CLI:
        if key in section and key != "label":
            params[key] = section[key]
    return params


def sw_eta(pd, pa, tout):
    p = (1.0 - pd) * (1.0 - pa)
    if p <= 1e-12:
        return 0.0
    return 1.0 / (PIPE_MS + tout * (1.0 - p) / p)


def execute_jobs(exe, jobs, workers):
    results = []
    if not jobs:
        return results
    with ProcessPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(run_process, exe, job["args"]): job for job in jobs}
        done = 0
        total = len(futures)
        for fut in as_completed(futures):
            job = futures[fut]
            header, events, result = fut.result()
            done += 1
            if done % 50 == 0 or done == total:
                print(f"  {done}/{total}", flush=True)
            results.append({**job, **result, "header": header, "events": events})
    return results


def mean_rows(raw, xkey):
    groups = defaultdict(list)
    for row in raw:
        groups[(row["case"], row["series"], row["x"])].append(row)
    means = []
    for (case, series, x), rows in groups.items():
        eff = [r["efficiency"] for r in rows]
        att = [r["attempts"] for r in rows]
        comp = [r["completion"] for r in rows]

        def avg(vals):
            return sum(vals) / len(vals)

        means.append(
            {
                "case": case,
                "series": series,
                "label": rows[0]["label"],
                "order": rows[0]["order"],
                "x": x,
                "xkey": xkey,
                "efficiency": avg(eff),
                "attempts": avg(att),
                "completion": avg(comp),
                "std_efficiency": statistics.pstdev(eff) if len(eff) > 1 else 0.0,
                "std_attempts": statistics.pstdev(att) if len(att) > 1 else 0.0,
                "std_completion": statistics.pstdev(comp) if len(comp) > 1 else 0.0,
                "nseeds": len(rows),
                "pinned": rows[0]["pinned"],
            }
        )
    means.sort(key=lambda r: (r["case"], r["order"], float(r["x"])))
    return means


def write_csv(path, rows, fields):
    with path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def plot_sweep(plot_cfg, means, xvalues, xkey, fixed_for_theory, out_path, title):
    ykey = plot_cfg["y"]
    stdkey = {"efficiency": "std_efficiency", "attempts": "std_attempts", "completion": "std_completion"}[ykey]
    fig, ax = plt.subplots(figsize=(8.2, 5.2))
    cases = []
    for row in means:
        if row["case"] not in cases:
            cases.append(row["case"])
    # One figure is already restricted to a single case by the caller.
    series_order = []
    for row in means:
        if row["series"] not in series_order:
            series_order.append(row["series"])
    xs_num = [float(x) for x in xvalues]
    for i, series in enumerate(series_order):
        rows = [r for r in means if r["series"] == series]
        color = COLORS[i % len(COLORS)]
        marker = MARKERS[i % len(MARKERS)]
        label = rows[0]["label"]
        if rows[0]["pinned"]:
            y = rows[0][ykey]
            ax.axhline(y, color=color, linestyle="--", linewidth=1.2, label=label)
            continue
        rows.sort(key=lambda r: float(r["x"]))
        xs = [float(r["x"]) for r in rows]
        ys = [r[ykey] for r in rows]
        yerr = [r[stdkey] for r in rows]
        show_err = any(e > 0 for e in yerr)
        ax.errorbar(
            xs,
            ys,
            yerr=yerr if show_err else None,
            color=color,
            marker=marker,
            linestyle="-",
            linewidth=1.1,
            markersize=5.5,
            capsize=3,
            label=label,
        )
    theory = plot_cfg.get("theory", "")
    if theory == "pipe" and ykey == "efficiency" and xkey == "ws":
        ax.plot(
            xs_num,
            [min(1.0, x / PIPE_MS) for x in xs_num],
            color="0.35",
            linestyle=":",
            linewidth=1.4,
            label="Analysis min(1, Ws/11)",
        )
    if theory == "sw" and ykey == "efficiency" and xkey in ("pd", "pa"):
        tout = float(fixed_for_theory["timeout_ms"])
        pd0 = float(fixed_for_theory["pd"])
        pa0 = float(fixed_for_theory["pa"])
        curve = []
        for x in xs_num:
            pd = x if xkey == "pd" else pd0
            pa = x if xkey == "pa" else pa0
            curve.append(sw_eta(pd, pa, tout))
        ax.plot(xs_num, curve, color="0.25", linestyle=":", linewidth=1.4, label="S&W analysis")
    ax.set_xlabel(plot_cfg.get("xlabel", xkey))
    ax.set_ylabel(plot_cfg.get("ylabel", ykey))
    ax.set_title(title)
    ax.grid(True, alpha=0.35, which="both")
    if plot_cfg.get("yscale") == "log":
        ax.set_yscale("log")
    else:
        ax.set_ylim(bottom=0)
        if ykey == "efficiency":
            ax.set_ylim(0, 1.05)
    ncol = 2 if len(series_order) > 5 else 1
    ax.legend(fontsize=8, ncol=ncol)
    fig.tight_layout()
    fig.savefig(out_path, dpi=140)
    plt.close(fig)


def plot_timeline(events, title, out_path):
    styles = {
        "TX": ("o", "C0", "TX"),
        "RETX": ("x", "C3", "RETX"),
        "RECV": ("s", "C2", "RECV"),
        "DROP": ("v", "C1", "DROP"),
        "ACK_OK": ("^", "C0", "ACK ok"),
        "ACK_LOST": ("P", "C5", "ACK lost"),
        "TIMEOUT": ("D", "C4", "TIMEOUT"),
    }
    fig, ax = plt.subplots(figsize=(9.5, 4.8))
    for name, (marker, color, label) in styles.items():
        pts = [(t, seq) for t, ev, seq in events if ev == name]
        if not pts:
            continue
        ax.scatter(
            [p[0] for p in pts],
            [p[1] for p in pts],
            marker=marker,
            color=color,
            s=28,
            label=label,
            zorder=3,
        )
    ax.set_xlabel("Time (ms)")
    ax.set_ylabel("Sequence number")
    ax.set_title(title)
    ax.grid(True, alpha=0.35)
    ax.legend(fontsize=8, ncol=4, loc="upper left")
    fig.tight_layout()
    fig.savefig(out_path, dpi=140)
    plt.close(fig)


def run_trace(cfg, exe):
    exp = cfg["experiment"]
    outdir = ROOT / "results" / exp.get("outdir", exp.get("id", "trace"))
    outdir.mkdir(parents=True, exist_ok=True)
    base = base_params(cfg)
    notes = []
    for name in sections(cfg, "trace"):
        sec = cfg[name]
        params = series_params(base, sec)
        for key in ("ws", "wr", "pd", "pa", "n", "timeout_ms"):
            if key in sec:
                params[key] = sec[key]
        seed_data = sec.get("seed_data", cfg["fixed"].get("seed_data", "400440917"))
        seed_ack = sec.get("seed_ack", cfg["fixed"].get("seed_ack", "400460804"))
        header, events, result = run_process(exe, job_args(params, seed_data, seed_ack, True))
        stem = name.split(".", 1)[1]
        log_path = outdir / f"{stem}.log"
        lines = [header] + [f"TRACE {t:.6f} {ev} {seq}" for t, ev, seq in events]
        lines.append(
            "RESULT {efficiency:.10f} {attempts:.10f} {completion:.6f} {delivered} {tx}".format(**result)
        )
        log_path.write_text("\n".join(lines) + "\n")
        fig_path = outdir / f"{stem}.png"
        plot_timeline(events, sec.get("label", stem), fig_path)
        names = {ev for _, ev, _ in events}
        warn = []
        if float(params["pd"]) > 0 and "DROP" not in names:
            warn.append("no DROP")
        if float(params["pa"]) > 0 and "ACK_LOST" not in names:
            warn.append("no ACK_LOST")
        flag = ("  WARNING " + ", ".join(warn)) if warn else ""
        print(f"  {stem}: {len(events)} events -> {fig_path.name}{flag}")
        notes.append(f"{stem}: completion={result['completion']:.3f} ms, attempts={result['attempts']:.3f}{flag}")
    return notes


def run_sweep(cfg, exe, workers):
    exp = cfg["experiment"]
    outdir = ROOT / "results" / exp.get("outdir", exp.get("id", "sweep"))
    outdir.mkdir(parents=True, exist_ok=True)
    prefix = exp.get("prefix", "")
    xsec = cfg["x"]
    xkey = xsec["key"]
    xvalues = split_csv(xsec["values"])
    fixed = base_params(cfg)
    default_seeds = parse_seeds(cfg["fixed"]["seeds"])
    case_names = sections(cfg, "case")
    if not case_names:
        case_names = [None]
    series_names = sections(cfg, "series")
    jobs = []
    for case_name in case_names:
        case = cfg[case_name] if case_name else {}
        case_tag = case.get("tag", "")
        seeds = parse_seeds(case["seeds"]) if "seeds" in case else default_seeds
        for s_index, sname in enumerate(series_names):
            sec = cfg[sname]
            params0 = series_params(fixed, sec)
            for key, value in case.items():
                if key in CLI:
                    params0[key] = value
            pinned = xkey in sec
            xs = [params0[xkey]] if pinned else xvalues
            for x in xs:
                params = dict(params0)
                params[xkey] = x
                for seed_data, seed_ack in seeds:
                    jobs.append(
                        {
                            "args": job_args(params, seed_data, seed_ack, False),
                            "case": case_tag,
                            "series": sname.split(".", 1)[-1],
                            "label": sec.get("label", sname),
                            "order": s_index,
                            "x": x,
                            "pinned": pinned,
                            "seed_data": seed_data,
                            "seed_ack": seed_ack,
                        }
                    )
    print(f"  {len(jobs)} runs", flush=True)
    raw = execute_jobs(exe, jobs, workers)
    # Drop bulky unused fields before writing csv.
    for row in raw:
        row.pop("args", None)
        row.pop("events", None)
        row.pop("header", None)
    raw_fields = [
        "case", "series", "label", "x", "pinned", "seed_data", "seed_ack",
        "efficiency", "attempts", "completion", "delivered", "tx",
    ]
    tag = f"{prefix}_" if prefix else ""
    write_csv(outdir / f"{tag}raw.csv", raw, raw_fields)
    means = mean_rows(raw, xkey)
    mean_fields = [
        "case", "series", "label", "x", "xkey", "efficiency", "attempts", "completion",
        "std_efficiency", "std_attempts", "std_completion", "nseeds", "pinned",
    ]
    write_csv(outdir / f"{tag}means.csv", means, mean_fields)
    plot_names = sections(cfg, "plot")
    notes = []
    for case_name in case_names:
        case = cfg[case_name] if case_name else {}
        case_tag = case.get("tag", "")
        subset = [r for r in means if r["case"] == case_tag]
        theory_params = dict(fixed)
        for key, value in case.items():
            if key in CLI:
                theory_params[key] = value
        for pname in plot_names:
            plot_cfg = cfg[pname]
            if case.get("title") and plot_cfg.get("title"):
                title = case["title"] + " — " + plot_cfg["title"]
            else:
                title = case.get("title") or plot_cfg.get("title") or exp.get("title", "")
            outfile = plot_cfg["outfile"]
            if case_tag:
                outfile = f"{case_tag}_{outfile}"
            out_path = outdir / outfile
            plot_sweep(plot_cfg, subset, xvalues, xkey, theory_params, out_path, title)
            print(f"  wrote {out_path.relative_to(ROOT)}")
            notes.append(str(out_path.relative_to(ROOT)))
    return notes, means


def theory_check(lines, means_by_id):
    rows = means_by_id.get("Q2", [])
    if not rows:
        return
    lines.append("Q2 check against min(1, Ws/11):")
    for row in rows:
        if row["series"] != "GBN":
            continue
        ws = float(row["x"])
        expect = min(1.0, ws / PIPE_MS)
        err = row["efficiency"] - expect
        if ws in (1, 5, 11, 16, 32):
            lines.append(
                f"  GBN Ws={ws:.0f}: sim={row['efficiency']:.4f}  analysis={expect:.4f}  delta={err:+.4f}"
            )


def main(argv):
    workers = 4
    exe = build_exe()
    master = load_ini(ROOT / "experiments" / "lab.ini")
    if argv:
        ini_paths = [Path(a) if Path(a).is_absolute() else ROOT / a for a in argv]
    else:
        ini_paths = [ROOT / master["questions"][k] for k in master["questions"]]
    summary = [
        "Lab 4 ARQ results",
        f"backend = {master['backend']['exe']}",
        "Seeds: 400440917, 400460804, 230411341234134134",
        "Error-free pipe: efficiency = min(1, Ws/11), S&W = 1/11.",
        "",
    ]
    means_by_id = {}
    for path in ini_paths:
        cfg = load_ini(path)
        exp = cfg["experiment"]
        print(f"== {exp.get('id', path.name)} ==")
        mode = exp.get("mode", "sweep")
        if mode == "trace":
            notes = run_trace(cfg, exe)
        else:
            notes, means = run_sweep(cfg, exe, workers)
            means_by_id[exp.get("id", path.stem)] = means
        summary.append(f"[{exp.get('id', path.name)}]")
        summary.extend(f"  {n}" for n in notes)
        summary.append("")
    theory_check(summary, means_by_id)
    out = ROOT / "results" / "summary.txt"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(summary) + "\n")
    print(f"wrote {out}")


if __name__ == "__main__":
    main(sys.argv[1:])
