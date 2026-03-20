from textual.app import App, ComposeResult
from textual.containers import Grid, Container
from textual.widgets import Header, Footer, Static, Label
import platform
import psutil
import shutil
import subprocess

def get_processor_name():
    if platform.system() == "Darwin":
        try:
            return subprocess.check_output(["sysctl", "-n", "machdep.cpu.brand_string"]).strip().decode("utf-8")
        except Exception:
            return platform.processor()
    elif platform.system() == "Windows":
        return platform.processor()
    else:
        try:
            with open("/proc/cpuinfo", "r") as f:
                for line in f:
                    if "model name" in line:
                        return line.split(":")[1].strip()
        except Exception:
            pass
        return platform.processor()

def get_os_info():
    if platform.system() == "Darwin":
        try:
            prod_ver = subprocess.check_output(["sw_vers", "-productVersion"]).strip().decode("utf-8")
            build_ver = subprocess.check_output(["sw_vers", "-buildVersion"]).strip().decode("utf-8")
            major_ver = int(prod_ver.split('.')[0])
            names = {
                15: "Sequoia",
                14: "Sonoma",
                13: "Ventura",
                12: "Monterey",
                11: "Big Sur"
            }
            name = names.get(major_ver, "")
            return f"macOS {name}".strip(), f"{prod_ver} ({build_ver})"
        except Exception:
            pass
    uname = platform.uname()
    return uname.system, f"{uname.release} ({uname.version})"

class SysPanel(Container):
    pass

class SysDiagApp(App):
    CSS = """
    Screen {
        background: #0A0F1A;
        color: #00FFCC;
    }
    
    Header {
        background: #011627;
        color: #00FFCC;
        border-bottom: heavy #00FFCC;
    }
    
    Footer {
        background: #011627;
        color: #00FFCC;
        border-top: heavy #00FFCC;
    }

    Grid {
        grid-size: 2;
        grid-gutter: 1 2;
        padding: 1 2;
    }

    SysPanel {
        border: heavy #00FFCC;
        padding: 1 2;
        background: #050A10;
        border-title-color: #FFFFFF;
        border-title-style: bold;
    }

    Label {
        padding-top: 1;
    }

    #control_instructions {
        width: 100%;
        content-align: center middle;
        padding: 1;
        background: #050A10;
        color: #FF3366;
        text-style: bold;
        border: heavy #FF3366;
        margin: 1 2;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit Dashboard"),
        ("ctrl+c", "quit", "Force Quit")
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True, icon="⚡")
        with Grid():
            with SysPanel(id="os_panel"):
                yield Label(id="os_info")
                yield Label(id="os_version")
                yield Label(id="arch_info")

            with SysPanel(id="cpu_panel"):
                yield Label(id="cpu_name")
                yield Label(id="cpu_cores")
                yield Label(id="cpu_usage")

            with SysPanel(id="ram_panel"):
                yield Label(id="ram_total")
                yield Label(id="ram_avail")
                yield Label(id="ram_usage")

            with SysPanel(id="disk_panel"):
                yield Label(id="disk_total")
                yield Label(id="disk_free")
                yield Label(id="disk_usage")
        
        yield Label("🛑 SYSTEM CONTROLS: Press Q to safely Terminate Link or [Ctrl+C] to Force Sever.", id="control_instructions")
        yield Footer()

    def on_mount(self) -> None:
        self.title = "NEURAL DIAGNOSTIC DASHBOARD"
        
        self.query_one("#os_panel", SysPanel).border_title = "SYSTEM IDENTIFICATION"
        self.query_one("#cpu_panel", SysPanel).border_title = "COMPUTE CORE"
        self.query_one("#ram_panel", SysPanel).border_title = "VOLATILE MEMORY"
        self.query_one("#disk_panel", SysPanel).border_title = "PERSISTENT STORAGE"

        self.update_system_info()
        self.set_interval(1.0, self.update_dynamic_info)

    def update_system_info(self) -> None:
        # Static info
        uname = platform.uname()
        os_name, os_ver = get_os_info()
        self.query_one("#os_info", Label).update(f"[bold white]OS:[/bold white] [cyan]{os_name}[/cyan]")
        self.query_one("#os_version", Label).update(f"[bold white]Version:[/bold white] [cyan]{os_ver}[/cyan]")
        self.query_one("#arch_info", Label).update(f"[bold white]Architecture:[/bold white] [cyan]{uname.machine}[/cyan]")
        
        self.query_one("#cpu_name", Label).update(f"[bold white]Processor:[/bold white] [cyan]{get_processor_name()}[/cyan]")
        core_count = psutil.cpu_count(logical=False) or "Unknown"
        thread_count = psutil.cpu_count(logical=True) or "Unknown"
        self.query_one("#cpu_cores", Label).update(f"[bold white]Cores:[/bold white] [cyan]{core_count} Physical / {thread_count} Logical[/cyan]")
        
        svmem = psutil.virtual_memory()
        self.query_one("#ram_total", Label).update(f"[bold white]Total RAM:[/bold white] [cyan]{svmem.total / (1024 ** 3):.2f} GB[/cyan]")
        
        total, used, free = shutil.disk_usage("/")
        self.query_one("#disk_total", Label).update(f"[bold white]Total Storage:[/bold white] [cyan]{total / (1024 ** 3):.2f} GB[/cyan]")

    def update_dynamic_info(self) -> None:
        # Dynamic info
        cpu_percent = psutil.cpu_percent()
        bars = int(cpu_percent / 5)
        bar_str = "█" * bars + "░" * (20 - bars)
        
        # Color coding the bars
        color = "green" if cpu_percent < 50 else ("yellow" if cpu_percent < 85 else "red")
        
        self.query_one("#cpu_usage", Label).update(f"[bold white]Utilization:[/bold white] {cpu_percent}%\n\n[{color}]{bar_str}[/{color}]")

        svmem = psutil.virtual_memory()
        self.query_one("#ram_avail", Label).update(f"[bold white]Available RAM:[/bold white] [cyan]{svmem.available / (1024 ** 3):.2f} GB[/cyan]")
        mem_bars = int(svmem.percent / 5)
        mem_bar_str = "█" * mem_bars + "░" * (20 - mem_bars)
        mem_color = "green" if svmem.percent < 50 else ("yellow" if svmem.percent < 85 else "red")
        
        self.query_one("#ram_usage", Label).update(f"[bold white]RAM Utilization:[/bold white] {svmem.percent}%\n\n[{mem_color}]{mem_bar_str}[/{mem_color}]")
        
        total, used, free = shutil.disk_usage("/")
        self.query_one("#disk_free", Label).update(f"[bold white]Free Storage:[/bold white] [cyan]{free / (1024 ** 3):.2f} GB[/cyan]")
        disk_pct = (used / total) * 100
        disk_bars = int(disk_pct / 5)
        disk_bar_str = "█" * disk_bars + "░" * (20 - disk_bars)
        disk_color = "green" if disk_pct < 50 else ("yellow" if disk_pct < 85 else "red")
        
        self.query_one("#disk_usage", Label).update(f"[bold white]Storage Utilization:[/bold white] {disk_pct:.2f}%\n\n[{disk_color}]{disk_bar_str}[/{disk_color}]")

if __name__ == "__main__":
    SysDiagApp().run()
