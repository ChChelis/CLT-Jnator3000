import csv
import ctypes
from datetime import datetime
from pathlib import Path
import sys
import tkinter as tk
from tkinter import filedialog, font, messagebox
import unicodedata


APP_NAME = "CLT-Jnator 3000"
ASSET_DIR = "assets"
FONT_AWESOME_FILE = "fa-solid-900.ttf"
FONT_AWESOME_FAMILY = "Font Awesome 6 Free Solid"
ACCENT = "#5a5ff0"
ACCENT_DARK = "#3f43bf"
ACCENT_LIGHT = "#eceeff"
ACCENT_SOFT = "#f6f7ff"
CARD_BG = "#f7f8ff"
TEXT_DARK = "#24264a"
TEXT_MUTED = "#767abb"


def resource_path(relative_path):
    base_path = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return base_path / relative_path


def load_private_font():
    font_path = resource_path(Path(ASSET_DIR) / FONT_AWESOME_FILE)
    if not font_path.exists():
        return

    # FR_PRIVATE keeps the bundled icon font available only to this process.
    ctypes.windll.gdi32.AddFontResourceExW(str(font_path), 0x10, 0)


class RoundIconButton(tk.Canvas):
    def __init__(self, parent, icon, command, icon_font, tooltip, **kwargs):
        super().__init__(
            parent,
            width=66,
            height=66,
            highlightthickness=0,
            bd=0,
            bg=kwargs.get("bg", parent.cget("bg")),
        )
        self.command = command
        self.tooltip = tooltip
        self.icon_font = icon_font
        self.icon = icon
        self.state = "normal"
        self.normal_fill = kwargs.get("normal_fill", ACCENT)
        self.hover_fill = kwargs.get("hover_fill", ACCENT_DARK)
        self.disabled_fill = kwargs.get("disabled_fill", "#dfe1f2")
        self.normal_text = kwargs.get("normal_text", "#ffffff")
        self.disabled_text = kwargs.get("disabled_text", "#9ca0c9")
        self.shadow = self.create_oval(9, 12, 61, 64, fill="#4c50cc", outline="")
        self.oval = self.create_oval(7, 7, 59, 59, fill=self.normal_fill, outline="")
        self.glyph = self.create_text(
            33,
            33,
            text=self.icon,
            font=self.icon_font,
            fill=self.normal_text,
        )

        self.bind("<Button-1>", self.on_click)
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def config(self, **kwargs):
        if "state" in kwargs:
            self.state = kwargs.pop("state")
            self.redraw()
        if kwargs:
            super().config(**kwargs)

    configure = config

    def on_click(self, _event):
        if self.state == "disabled":
            return
        self.command()

    def on_enter(self, _event):
        if self.state != "disabled":
            self.itemconfig(self.oval, fill=self.hover_fill)

    def on_leave(self, _event):
        self.redraw()

    def redraw(self):
        if self.state == "disabled":
            self.itemconfig(self.shadow, fill="#c7cae8")
            self.itemconfig(self.oval, fill=self.disabled_fill, outline="#c6c6c6")
            self.itemconfig(self.glyph, fill=self.disabled_text)
            return

        self.itemconfig(self.shadow, fill="#4c50cc")
        self.itemconfig(self.oval, fill=self.normal_fill, outline="#a8a8a8")
        self.itemconfig(self.glyph, fill=self.normal_text)


class TimerApp:
    def __init__(self, root):
        self.root = root
        self.root.title(APP_NAME)
        self.root.geometry("680x660")
        self.root.minsize(560, 520)
        self.root.configure(bg=ACCENT_DARK)

        self.tasks = []
        self.current_task = None
        self.task_counter = 0
        self.update_job = None
        self.selected_task_id = None
        self.updating_list = False
        self.dirty = False
        self.has_saved = False
        self.last_saved_path = None
        self.context_menu_open = False

        self.time_font = font.Font(family="Segoe UI", size=38, weight="bold")
        self.button_font = font.Font(family="Segoe UI", size=12)
        self.text_font = font.Font(family="Segoe UI", size=10)
        self.section_font = font.Font(family="Segoe UI", size=11, weight="bold")
        self.icon_font = font.Font(family=FONT_AWESOME_FAMILY, size=18)

        self.menu_bar = tk.Menu(root)
        self.file_menu = tk.Menu(self.menu_bar, tearoff=False)
        self.file_menu.add_command(label="Salvar como", command=self.save_as)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Sair", command=self.exit_without_saving)
        self.menu_bar.add_cascade(label="Arquivo", menu=self.file_menu)
        self.root.config(menu=self.menu_bar)

        self.background = tk.Canvas(root, highlightthickness=0, bd=0)
        self.background.pack(expand=True, fill="both")
        self.background.bind("<Configure>", self.draw_background)

        self.frame = tk.Frame(self.background, padx=30, pady=26, bg=CARD_BG)
        self.frame_window = self.background.create_window(
            0,
            0,
            window=self.frame,
            anchor="nw",
        )

        self.task_label = tk.Label(
            self.frame,
            text="Nenhuma tarefa",
            font=self.section_font,
            bg=CARD_BG,
            fg=TEXT_MUTED,
        )
        self.task_label.pack()

        self.time_label = tk.Label(
            self.frame,
            text="00:00:00",
            font=self.time_font,
            bg=CARD_BG,
            fg=ACCENT_DARK,
        )
        self.time_label.pack(pady=(4, 12))

        self.button_frame = tk.Frame(self.frame, bg=CARD_BG)
        self.button_frame.pack(pady=(0, 16))

        self.start_button = RoundIconButton(
            self.button_frame,
            icon="\uf04b",
            icon_font=self.icon_font,
            tooltip="Iniciar",
            command=self.start_new_task,
            bg=CARD_BG,
            normal_fill=ACCENT,
            hover_fill=ACCENT_DARK,
            normal_text=ACCENT_LIGHT,
        )
        self.start_button.pack(side="left", padx=(0, 12))

        self.stop_button = RoundIconButton(
            self.button_frame,
            icon="\uf04d",
            icon_font=self.icon_font,
            tooltip="Parar",
            command=self.stop_current_task,
            bg=CARD_BG,
            normal_fill="#eef0ff",
            hover_fill="#dfe2ff",
            normal_text=ACCENT_DARK,
        )
        self.stop_button.config(state="disabled")
        self.stop_button.pack(side="left")

        self.task_list = tk.Listbox(
            self.frame,
            font=self.text_font,
            height=7,
            activestyle="none",
            bg=ACCENT_SOFT,
            fg=TEXT_DARK,
            selectbackground=ACCENT,
            selectforeground="#ffffff",
            relief="flat",
            highlightthickness=1,
            highlightbackground="#d9dcff",
            highlightcolor=ACCENT,
        )
        self.task_list.pack(expand=True, fill="both")
        self.task_list.bind("<<ListboxSelect>>", self.on_task_selected)
        self.task_list.bind("<Button-3>", self.show_task_context_menu)

        self.task_context_menu = tk.Menu(self.root, tearoff=False)
        self.task_context_menu.add_command(
            label="Continuar",
            command=self.continue_selected_task,
        )
        self.task_context_menu.add_separator()
        self.task_context_menu.add_command(
            label="Renomear",
            command=self.rename_selected_task,
        )
        self.task_context_menu.bind("<Unmap>", self.on_context_menu_closed)

        self.parts_label = tk.Label(
            self.frame,
            text="Partes da tarefa selecionada",
            font=self.section_font,
            anchor="w",
            bg=CARD_BG,
            fg=TEXT_MUTED,
        )
        self.parts_label.pack(fill="x", pady=(12, 4))

        self.parts_list = tk.Listbox(
            self.frame,
            font=self.text_font,
            height=5,
            activestyle="none",
            bg=ACCENT_SOFT,
            fg=TEXT_DARK,
            selectbackground=ACCENT,
            selectforeground="#ffffff",
            relief="flat",
            highlightthickness=1,
            highlightbackground="#d9dcff",
            highlightcolor=ACCENT,
        )
        self.parts_list.pack(fill="both")

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def draw_background(self, event):
        self.background.delete("background")
        width = max(event.width, 1)
        height = max(event.height, 1)

        for y in range(height):
            ratio = y / height
            color = self.blend_hex("#969cff", "#4d48df", ratio)
            self.background.create_line(0, y, width, y, fill=color, tags="background")

        card_margin_x = max(28, int(width * 0.07))
        card_margin_y = max(28, int(height * 0.08))
        card_x1 = card_margin_x
        card_y1 = card_margin_y
        card_x2 = width - card_margin_x
        card_y2 = height - card_margin_y
        outer_radius = 34
        shadow_offset = 12

        self.create_round_rect(
            card_x1 + shadow_offset,
            card_y1 + shadow_offset,
            card_x2 + shadow_offset,
            card_y2 + shadow_offset,
            outer_radius,
            fill="#3533a8",
            outline="",
            tags="background",
        )
        self.create_round_rect(
            card_x1,
            card_y1,
            card_x2,
            card_y2,
            outer_radius,
            fill=CARD_BG,
            outline="#ffffff",
            width=2,
            tags="background",
        )

        inner_pad = 22
        self.background.coords(self.frame_window, card_x1 + inner_pad, card_y1 + inner_pad)
        self.background.itemconfig(
            self.frame_window,
            width=max(320, card_x2 - card_x1 - inner_pad * 2),
            height=max(280, card_y2 - card_y1 - inner_pad * 2),
        )
        self.background.tag_lower("background")

    def create_round_rect(self, x1, y1, x2, y2, radius, **kwargs):
        radius = min(radius, abs(x2 - x1) / 2, abs(y2 - y1) / 2)
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1,
        ]
        return self.background.create_polygon(points, smooth=True, splinesteps=24, **kwargs)

    @staticmethod
    def blend_hex(start, end, ratio):
        ratio = max(0.0, min(1.0, ratio))
        start_rgb = tuple(int(start[index:index + 2], 16) for index in (1, 3, 5))
        end_rgb = tuple(int(end[index:index + 2], 16) for index in (1, 3, 5))
        mixed = tuple(
            int(start_channel + (end_channel - start_channel) * ratio)
            for start_channel, end_channel in zip(start_rgb, end_rgb)
        )
        return "#{:02x}{:02x}{:02x}".format(*mixed)

    def start_new_task(self):
        if self.current_task is not None:
            self.stop_current_task()

        self.task_counter += 1
        task = {
            "id": self.task_counter,
            "name": f"Tarefa {self.task_counter}",
            "parts": [self.new_part()],
            "running": True,
        }
        self.tasks.append(task)
        self.current_task = task
        self.selected_task_id = task["id"]
        self.mark_dirty()

        self.select_task(task)
        self.schedule_update()

    def continue_selected_task(self):
        task = self.find_task(self.selected_task_id)
        if task is None or task["running"]:
            return

        if self.current_task is not None:
            self.stop_current_task()

        task["parts"].append(self.new_part())
        task["running"] = True
        self.current_task = task
        self.mark_dirty()

        self.select_task(task)
        self.schedule_update()

    def stop_current_task(self):
        if self.current_task is None:
            return

        self.cancel_update()
        open_part = self.get_open_part(self.current_task)
        if open_part is not None:
            finished_at = datetime.now()
            note = self.ask_stop_note(self.current_task, open_part, finished_at)
            open_part["end"] = finished_at
            open_part["note"] = note

        self.current_task["running"] = False
        self.current_task = None
        self.mark_dirty()
        self.refresh_view()

    def new_part(self):
        return {
            "start": datetime.now(),
            "end": None,
            "note": "",
        }

    def get_open_part(self, task):
        for part in reversed(task["parts"]):
            if part["end"] is None:
                return part
        return None

    def get_task_elapsed(self, task):
        elapsed = 0.0
        now = datetime.now()

        for part in task["parts"]:
            end = part["end"] or now
            elapsed += (end - part["start"]).total_seconds()

        return elapsed

    def schedule_update(self):
        self.refresh_view()
        self.update_job = self.root.after(200, self.schedule_update)

    def cancel_update(self):
        if self.update_job is not None:
            self.root.after_cancel(self.update_job)
            self.update_job = None

    def refresh_view(self):
        if self.context_menu_open:
            if self.current_task is None:
                self.task_label.config(text="Nenhuma tarefa em andamento")
                self.time_label.config(text="00:00:00")
            else:
                self.task_label.config(text=self.current_task["name"])
                self.time_label.config(text=self.format_duration(self.get_task_elapsed(self.current_task)))
            return

        selected_index = self.get_selected_index()
        self.updating_list = True
        self.task_list.delete(0, tk.END)

        for task in self.tasks:
            status = "rodando" if task["running"] else "parada"
            elapsed = self.format_duration(self.get_task_elapsed(task))
            first_start = self.format_timestamp(task["parts"][0]["start"])
            self.task_list.insert(
                tk.END,
                f'{task["name"]} - {elapsed} - inicio {first_start} ({status})',
            )

        if selected_index is not None and selected_index < len(self.tasks):
            self.task_list.selection_set(selected_index)
            self.task_list.activate(selected_index)
        self.updating_list = False

        selected_task = self.find_task(self.selected_task_id)
        self.refresh_parts(selected_task)
        self.refresh_buttons(selected_task)

        if self.current_task is None:
            self.task_label.config(text="Nenhuma tarefa em andamento")
            self.time_label.config(text="00:00:00")
            return

        self.task_label.config(text=self.current_task["name"])
        self.time_label.config(text=self.format_duration(self.get_task_elapsed(self.current_task)))

    def refresh_parts(self, task):
        self.parts_list.delete(0, tk.END)
        if task is None:
            return

        for index, part in enumerate(task["parts"], start=1):
            start = self.format_timestamp(part["start"])
            end = self.format_timestamp(part["end"]) if part["end"] is not None else "em andamento"
            note_status = "com texto" if part["note"] else "sem texto"
            self.parts_list.insert(tk.END, f"Parte {index}: {start} -> {end} ({note_status})")

    def ask_stop_note(self, task, part, finished_at):
        dialog = tk.Toplevel(self.root)
        dialog.title("Registrar atividade")
        dialog.geometry("460x300")
        dialog.minsize(420, 280)
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.protocol("WM_DELETE_WINDOW", lambda: None)

        content = tk.Frame(dialog, padx=18, pady=16)
        content.pack(expand=True, fill="both")

        title = tk.Label(
            content,
            text=f'Encerrando "{task["name"]}"',
            font=self.text_font,
            anchor="w",
        )
        title.pack(fill="x")

        period = tk.Label(
            content,
            text=(
                f"{self.format_timestamp(part['start'])} -> "
                f"{self.format_timestamp(finished_at)}"
            ),
            font=self.text_font,
            anchor="w",
        )
        period.pack(fill="x", pady=(4, 10))

        text_box = tk.Text(content, height=7, wrap="word", font=self.text_font)
        text_box.pack(expand=True, fill="both")
        text_box.focus_set()

        footer = tk.Frame(content)
        footer.pack(fill="x", pady=(10, 0))

        counter_var = tk.StringVar(value="0/50 caracteres")
        counter_label = tk.Label(footer, textvariable=counter_var, font=self.text_font)
        counter_label.pack(side="left")

        override_minimum_var = tk.BooleanVar(value=False)
        override_check = tk.Checkbutton(
            content,
            text="Permitir confirmar com menos de 50 caracteres",
            variable=override_minimum_var,
            command=lambda: refresh_confirm_state(),
            font=self.text_font,
        )
        override_check.pack(anchor="w", pady=(8, 0))

        note_var = tk.StringVar(value="")
        confirm_button = tk.Button(
            footer,
            text="Confirmar",
            font=self.text_font,
            state="disabled",
            command=lambda: confirm(),
        )
        confirm_button.pack(side="right")

        def typed_text():
            return text_box.get("1.0", "end-1c").strip()

        def refresh_confirm_state(_event=None):
            text = typed_text()
            counter_var.set(f"{len(text)}/50 caracteres")
            can_confirm = len(text) >= 50 or override_minimum_var.get()
            state = "normal" if can_confirm else "disabled"
            confirm_button.config(state=state)

        def confirm():
            text = typed_text()
            if len(text) < 50 and not override_minimum_var.get():
                return False
            note_var.set(text)
            dialog.destroy()
            return True

        def confirm_with_enter(_event=None):
            confirm()
            return "break"

        text_box.bind("<KeyRelease>", refresh_confirm_state)
        text_box.bind("<Return>", confirm_with_enter)
        dialog.bind("<Return>", confirm_with_enter)
        dialog.bind("<Escape>", lambda _event: "break")
        dialog.wait_window()
        return note_var.get()

    def refresh_buttons(self, selected_task):
        if self.current_task is None:
            self.stop_button.config(state="disabled")
        else:
            self.stop_button.config(state="normal")

    def select_task(self, task):
        index = self.tasks.index(task)
        self.task_list.selection_clear(0, tk.END)
        self.task_list.selection_set(index)
        self.task_list.activate(index)
        self.load_selected_task(task)
        self.refresh_view()

    def on_task_selected(self, _event):
        if self.updating_list:
            return

        index = self.get_selected_index()
        if index is None:
            return
        self.load_selected_task(self.tasks[index])
        self.refresh_view()

    def load_selected_task(self, task):
        self.selected_task_id = task["id"]

    def show_task_context_menu(self, event):
        index = self.task_list.nearest(event.y)
        if index < 0 or index >= len(self.tasks) or self.task_list.bbox(index) is None:
            return

        self.task_list.selection_clear(0, tk.END)
        self.task_list.selection_set(index)
        self.task_list.activate(index)
        task = self.tasks[index]
        self.load_selected_task(task)
        self.refresh_parts(task)
        self.refresh_buttons(task)
        self.task_context_menu.entryconfig(
            "Continuar",
            state="normal" if not task["running"] else "disabled",
        )
        self.context_menu_open = True

        try:
            self.task_context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.task_context_menu.grab_release()

    def on_context_menu_closed(self, _event=None):
        self.context_menu_open = False
        self.refresh_view()

    def rename_selected_task(self, _event=None):
        task = self.find_task(self.selected_task_id)
        if task is None:
            return

        new_name = self.ask_task_name(task)
        if new_name:
            task["name"] = new_name
            self.mark_dirty()
            self.refresh_view()

    def ask_task_name(self, task):
        dialog = tk.Toplevel(self.root)
        dialog.title("Renomear tarefa")
        dialog.geometry("360x130")
        dialog.minsize(320, 120)
        dialog.transient(self.root)
        dialog.grab_set()

        content = tk.Frame(dialog, padx=16, pady=14)
        content.pack(expand=True, fill="both")

        name_var = tk.StringVar(value=task["name"])
        name_entry = tk.Entry(content, textvariable=name_var, font=self.text_font)
        name_entry.pack(fill="x")
        name_entry.focus_set()
        name_entry.selection_range(0, tk.END)

        footer = tk.Frame(content)
        footer.pack(fill="x", pady=(14, 0))

        result_var = tk.StringVar(value="")

        def confirm(_event=None):
            value = name_var.get().strip()
            if not value:
                return
            result_var.set(value)
            dialog.destroy()

        def cancel():
            dialog.destroy()

        cancel_button = tk.Button(
            footer,
            text="Cancelar",
            font=self.text_font,
            command=cancel,
        )
        cancel_button.pack(side="right")

        confirm_button = tk.Button(
            footer,
            text="OK",
            font=self.text_font,
            command=confirm,
        )
        confirm_button.pack(side="right", padx=(0, 8))

        dialog.bind("<Return>", confirm)
        name_entry.bind("<Return>", confirm)
        dialog.bind("<Escape>", lambda _event: cancel())
        dialog.wait_window()
        return result_var.get()

    def find_task(self, task_id):
        for task in self.tasks:
            if task["id"] == task_id:
                return task
        return None

    def get_selected_index(self):
        selected = self.task_list.curselection()
        if not selected:
            return None
        return selected[0]

    def on_close(self):
        if self.current_task is not None:
            self.stop_current_task()

        if self.needs_save():
            save_path = self.ask_export_path()
            if save_path is None:
                return

            self.export_tasks(save_path)
            self.mark_saved(save_path)
        self.cancel_update()
        self.root.destroy()

    def exit_without_saving(self):
        confirmed = messagebox.askyesno(
            "Sair sem salvar",
            "Sair sem salvar? Alteracoes nao salvas serao perdidas.",
            icon="warning",
            parent=self.root,
        )
        if not confirmed:
            return

        self.cancel_update()
        self.root.destroy()

    def save_as(self):
        save_path = self.ask_export_path()
        if save_path is None:
            return

        self.export_tasks(save_path)
        self.mark_saved(save_path)
        messagebox.showinfo(
            "Arquivo salvo",
            f"Relatorio salvo em:\n{save_path}",
            parent=self.root,
        )

    def mark_dirty(self):
        self.dirty = True

    def mark_saved(self, path):
        self.dirty = False
        self.has_saved = True
        self.last_saved_path = path

    def needs_save(self):
        return self.dirty or not self.has_saved

    def ask_export_path(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = filedialog.asksaveasfilename(
            parent=self.root,
            title="Salvar relatório de tarefas",
            initialfile=f"relatorio_tarefas_{timestamp}.csv",
            defaultextension=".csv",
            filetypes=[
                ("CSV", "*.csv"),
                ("Texto Markdown", "*.txt"),
                ("Markdown", "*.md"),
            ],
        )
        if not filename:
            return None

        path = Path(filename)
        if path.suffix.lower() not in {".csv", ".txt", ".md"}:
            path = path.with_suffix(".csv")
        return path

    def export_tasks(self, path):
        if path.suffix.lower() == ".csv":
            self.export_csv(path)
            return
        self.export_markdown(path)

    def export_csv(self, path):
        headers = [
            "Tarefa",
            "Subtarefa",
            "Inicio geral",
            "Fim geral",
            "Inicio parte",
            "Fim parte",
            "Duracao",
            "Descricao",
        ]

        with path.open("w", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(headers)

            for task in self.tasks:
                writer.writerow([
                    task["name"],
                    "",
                    self.format_timestamp(self.get_task_start(task)),
                    self.format_timestamp(self.get_task_end(task)),
                    "",
                    "",
                    self.format_duration(self.get_task_elapsed(task)),
                    "",
                ])

                for index, part in enumerate(task["parts"], start=1):
                    writer.writerow([
                        "",
                        f"Parte {index}",
                        "",
                        "",
                        self.format_timestamp(part["start"]),
                        self.format_timestamp(part["end"]),
                        self.format_duration(self.get_part_elapsed(part)),
                        part["note"],
                    ])

            writer.writerow([])
            writer.writerow([])
            writer.writerow([])
            writer.writerow(["Resumo de horas"])
            writer.writerow([
                "Inicio",
                "Almoco",
                "Retorno Almoco",
                "Fim",
            ])
            writer.writerow(self.get_csv_time_summary())

    def export_markdown(self, path):
        generated_at = self.format_timestamp(datetime.now())
        lines = [
            "# Relatorio de Tarefas",
            "",
            f"Gerado em: `{generated_at}`",
            "",
            "## Resumo",
            "",
            "| Tarefa | Inicio geral | Fim geral | Duracao | Partes |",
            "| --- | --- | --- | --- | ---: |",
        ]

        for task in self.tasks:
            lines.append(
                "| "
                f"{self.escape_markdown_table(task['name'])} | "
                f"`{self.format_timestamp(self.get_task_start(task))}` | "
                f"`{self.format_timestamp(self.get_task_end(task))}` | "
                f"`{self.format_duration(self.get_task_elapsed(task))}` | "
                f"{len(task['parts'])} |"
            )

        if not self.tasks:
            lines.append("| Nenhuma tarefa registrada |  |  | `00:00:00` | 0 |")

        lines.extend(["", "## Detalhes", ""])

        for task in self.tasks:
            lines.extend([
                f"### {task['name']}",
                "",
                f"- Inicio geral: `{self.format_timestamp(self.get_task_start(task))}`",
                f"- Fim geral: `{self.format_timestamp(self.get_task_end(task))}`",
                f"- Duracao total: `{self.format_duration(self.get_task_elapsed(task))}`",
                "",
                "| Parte | Inicio | Fim | Duracao | Descricao |",
                "| ---: | --- | --- | --- | --- |",
            ])

            for index, part in enumerate(task["parts"], start=1):
                note = self.markdown_single_line(part["note"])
                lines.append(
                    "| "
                    f"{index} | "
                    f"`{self.format_timestamp(part['start'])}` | "
                    f"`{self.format_timestamp(part['end'])}` | "
                    f"`{self.format_duration(self.get_part_elapsed(part))}` | "
                    f"{note} |"
                )

            lines.append("")

        path.write_text("\n".join(lines), encoding="utf-8")

    def get_task_start(self, task):
        return task["parts"][0]["start"]

    def get_task_end(self, task):
        return task["parts"][-1]["end"] or datetime.now()

    def get_part_elapsed(self, part):
        end = part["end"] or datetime.now()
        return (end - part["start"]).total_seconds()

    def get_csv_time_summary(self):
        first_file_record = self.get_first_file_record()
        lunch_task = self.get_first_lunch_task()
        lunch_start = self.get_task_start(lunch_task) if lunch_task is not None else None
        lunch_end = self.get_task_end(lunch_task) if lunch_task is not None else None
        last_file_record = self.get_last_file_record()

        return [
            self.format_hour_minute(first_file_record),
            self.format_hour_minute(lunch_start),
            self.format_hour_minute(lunch_end),
            self.format_hour_minute(last_file_record),
        ]

    def get_first_file_record(self):
        starts = [part["start"] for task in self.tasks for part in task["parts"]]
        return min(starts) if starts else None

    def get_last_file_record(self):
        ends = [
            part["end"] or datetime.now()
            for task in self.tasks
            for part in task["parts"]
        ]
        return max(ends) if ends else None

    def get_first_lunch_task(self):
        for task in self.tasks:
            if self.is_lunch_name(task["name"]):
                return task
        return None

    def is_lunch_name(self, value):
        normalized = self.normalize_task_name(value)
        if "almoco" in normalized:
            return True

        common_typos = {
            "almoco",
            "almco",
            "almooco",
            "almoso",
            "almotso",
            "almorco",
            "amoco",
            "aloco",
            "almoca",
        }
        candidates = [normalized] + self.normalize_task_name_parts(value)
        return any(
            self.levenshtein_distance(candidate, typo) <= 1
            for candidate in candidates
            for typo in common_typos
        )

    @staticmethod
    def normalize_task_name(value):
        without_accents = unicodedata.normalize("NFKD", str(value))
        ascii_text = without_accents.encode("ascii", "ignore").decode("ascii")
        return "".join(character for character in ascii_text.lower() if character.isalpha())

    @staticmethod
    def normalize_task_name_parts(value):
        without_accents = unicodedata.normalize("NFKD", str(value))
        ascii_text = without_accents.encode("ascii", "ignore").decode("ascii")
        parts = []
        current = []

        for character in ascii_text.lower():
            if character.isalpha():
                current.append(character)
            elif current:
                parts.append("".join(current))
                current = []

        if current:
            parts.append("".join(current))

        return parts

    @staticmethod
    def levenshtein_distance(left, right):
        if left == right:
            return 0
        if not left:
            return len(right)
        if not right:
            return len(left)

        previous = list(range(len(right) + 1))
        for left_index, left_character in enumerate(left, start=1):
            current = [left_index]
            for right_index, right_character in enumerate(right, start=1):
                insert_cost = current[right_index - 1] + 1
                delete_cost = previous[right_index] + 1
                replace_cost = previous[right_index - 1] + (left_character != right_character)
                current.append(min(insert_cost, delete_cost, replace_cost))
            previous = current
        return previous[-1]

    @staticmethod
    def escape_markdown_table(value):
        return str(value).replace("\\", "\\\\").replace("|", "\\|").replace("\n", " ")

    def markdown_single_line(self, value):
        return self.escape_markdown_table(value).replace("\r", " ").strip()

    @staticmethod
    def format_duration(total_seconds):
        total_seconds = int(total_seconds)
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    @staticmethod
    def format_timestamp(value):
        return value.strftime("%Y%m%d_%H:%M:%S")

    @staticmethod
    def format_hour_minute(value):
        if value is None:
            return ""

        minute = value.minute
        hour = value.hour
        if value.second > 30:
            minute += 1
            if minute == 60:
                minute = 0
                hour = (hour + 1) % 24

        return f"{hour:02d}:{minute:02d}"


def main():
    load_private_font()
    root = tk.Tk()
    TimerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
