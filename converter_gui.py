#!/usr/bin/env python3
"""Potree Converter - simple cross-platform GUI (Windows / macOS / Linux).

Pick a point-cloud file, pick where to save the result, click Convert.
It just drives the same `docker run` the .bat / .command launchers use.

Run with:  python converter_gui.py   (double-clickable if Python is installed)
Needs only the Python standard library + Docker Desktop / Docker Engine.
"""
import os
import queue
import shutil
import subprocess
import sys
import tempfile
import threading
import tkinter as tk
from tkinter import filedialog, ttk

IMAGE = "ghcr.io/flaxandteal/potree-converter:latest"
SUPPORTED = [("Point clouds", "*.e57 *.las *.laz *.ply *.xyz *.pcd *.pts *.bpf"),
             ("All files", "*.*")]


def build_context():
    """Directory to hand `docker build` — must contain Dockerfile + convert.sh.

    When frozen by PyInstaller, __file__ lives in a temp dir and the bundled
    data is unpacked to sys._MEIPASS, so copy just the two build files into a
    clean dir (avoids shipping the whole runtime as the build context).
    """
    if getattr(sys, "frozen", False):
        d = tempfile.mkdtemp(prefix="potree-build-")
        for f in ("Dockerfile", "convert.sh"):
            shutil.copy(os.path.join(sys._MEIPASS, f), d)
        return d
    return os.path.dirname(os.path.abspath(__file__))


class App:
    def __init__(self, root):
        self.root = root
        self.infile = tk.StringVar()
        self.outdir = tk.StringVar()
        self.q = queue.Queue()
        root.title("Potree Converter")

        frm = ttk.Frame(root, padding=12)
        frm.grid(sticky="nsew")
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        frm.columnconfigure(1, weight=1)

        ttk.Label(frm, text="Point-cloud file:").grid(row=0, column=0, sticky="w")
        ttk.Entry(frm, textvariable=self.infile).grid(row=0, column=1, sticky="ew", padx=6)
        ttk.Button(frm, text="Choose…", command=self.pick_file).grid(row=0, column=2)

        ttk.Label(frm, text="Save results in:").grid(row=1, column=0, sticky="w", pady=(8, 0))
        ttk.Entry(frm, textvariable=self.outdir).grid(row=1, column=1, sticky="ew", padx=6, pady=(8, 0))
        ttk.Button(frm, text="Choose…", command=self.pick_outdir).grid(row=1, column=2, pady=(8, 0))

        self.btn = ttk.Button(frm, text="Convert", command=self.start)
        self.btn.grid(row=2, column=0, columnspan=3, pady=10, sticky="ew")

        self.log = tk.Text(frm, height=16, width=80, wrap="word", state="disabled")
        self.log.grid(row=3, column=0, columnspan=3, sticky="nsew")
        frm.rowconfigure(3, weight=1)
        sb = ttk.Scrollbar(frm, command=self.log.yview)
        sb.grid(row=3, column=3, sticky="ns")
        self.log["yscrollcommand"] = sb.set

    def pick_file(self):
        f = filedialog.askopenfilename(title="Choose a point-cloud file", filetypes=SUPPORTED)
        if f:
            self.infile.set(f)
            if not self.outdir.get():
                self.outdir.set(os.path.dirname(f))  # default: next to the input

    def pick_outdir(self):
        d = filedialog.askdirectory(title="Choose where to save the result")
        if d:
            self.outdir.set(d)

    def write(self, text):
        self.log["state"] = "normal"
        self.log.insert("end", text)
        self.log.see("end")
        self.log["state"] = "disabled"

    def start(self):
        infile, outdir = self.infile.get(), self.outdir.get()
        if not infile or not os.path.isfile(infile):
            self.write("Please choose a valid input file.\n")
            return
        if not outdir:
            outdir = os.path.dirname(infile)
            self.outdir.set(outdir)
        if not shutil.which("docker"):
            self.write("ERROR: Docker not found. Install Docker Desktop and make sure "
                       "it is running.\nhttps://www.docker.com/products/docker-desktop/\n")
            return
        self.btn["state"] = "disabled"
        self.log["state"] = "normal"
        self.log.delete("1.0", "end")
        self.log["state"] = "disabled"
        threading.Thread(target=self.run, args=(infile, outdir), daemon=True).start()
        self.root.after(100, self.drain)

    def run(self, infile, outdir):
        try:
            indir = os.path.dirname(os.path.abspath(infile))
            fname = os.path.basename(infile)
            base = os.path.splitext(fname)[0]

            # Fetch the image on first use (pull; build from source only if that fails).
            if subprocess.run(["docker", "image", "inspect", IMAGE],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode != 0:
                self.q.put("First run: downloading the converter. This is a few hundred "
                           "MB and only happens once…\n\n")
                if self._stream(["docker", "pull", IMAGE]) != 0:
                    self.q.put("\nDownload failed - building it locally instead. This "
                               "compiles from source and takes several minutes…\n\n")
                    if self._stream(["docker", "build", "-t", IMAGE, build_context()]) != 0:
                        self.q.put("\n*** Could not get the converter image. See the errors "
                                   "above.\n")
                        return

            cmd = ["docker", "run", "--rm"]
            if os.name != "nt":  # keep output files owned by the user on macOS/Linux
                cmd += ["--user", f"{os.getuid()}:{os.getgid()}"]
            cmd += ["-v", f"{indir}:/in", "-v", f"{os.path.abspath(outdir)}:/out",
                    IMAGE, f"/in/{fname}", "-o", f"/out/{base}_potree"]
            self.q.put(f"=== Converting {fname} ===\n")
            rc = self._stream(cmd)
            if rc == 0:
                self.q.put(f"\nDone: {os.path.join(outdir, base + '_potree')}\n")
            else:
                self.q.put(f"\n*** Conversion FAILED (exit {rc}). See messages above.\n")
        except Exception as e:  # noqa: BLE001 - surface anything to the user
            self.q.put(f"\nERROR: {e}\n")
        finally:
            self.q.put(None)  # sentinel: re-enable the button

    def _stream(self, cmd):
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                             text=True, bufsize=1)
        for line in p.stdout:
            self.q.put(line)
        return p.wait()

    def drain(self):
        try:
            while True:
                item = self.q.get_nowait()
                if item is None:
                    self.btn["state"] = "normal"
                    return
                self.write(item)
        except queue.Empty:
            pass
        self.root.after(100, self.drain)


if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
