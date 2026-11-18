"""CyberSafe V3 Pygame-CE client. Backend owns branches, scoring and session state."""
import asyncio
import os
from pathlib import Path
import pygame
from api_client import CyberSafeAPI, APIError

WIDTH, HEIGHT = 1120, 740
BG = (10, 16, 30); PANEL = (20, 31, 52); CARD = (29, 45, 72)
CYAN = (34, 211, 238); BLUE = (59, 130, 246); GREEN = (16, 185, 129)
RED = (244, 63, 94); AMBER = (245, 158, 11); WHITE = (245, 248, 255); MUTED = (154, 169, 190)

class CyberSafeV3:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("CyberSafe – Game Client V3")
        self.clock = pygame.time.Clock()
        # Bundled Unicode fonts keep Vietnamese accents working on desktop and Pygbag.
        font_dir = Path(__file__).resolve().parent / "assets" / "fonts"
        regular_font = font_dir / "font_regular.ttf"
        bold_font = font_dir / "font_bold.ttf"
        self.font = pygame.font.Font(str(regular_font), 22)
        self.small = pygame.font.Font(str(regular_font), 17)
        self.title = pygame.font.Font(str(bold_font), 34)
        self.button_font = pygame.font.Font(str(bold_font), 16)
        self.api = CyberSafeAPI()
        self.state = "AUTH"
        self.auth_mode = "login"
        self.fields = ["", "", ""]  # email, password, display name
        self.focus = 0
        self.user = None; self.campaigns = []; self.session = None
        self.dashboard_data = {}; self.history_data = []; self.errors_data = []; self.leaderboard_data = []
        self.selected_campaign = None; self.result_data = None
        self.message = "Đăng nhập hoặc tạo tài khoản để bắt đầu"
        self.busy = False; self.scroll = 0

    def text(self, value, x, y, color=WHITE, font=None):
        img = (font or self.font).render(str(value), True, color)
        self.screen.blit(img, (x, y))

    def wrap(self, value, x, y, width, color=WHITE, font=None, line_gap=5, max_lines=8):
        font = font or self.font
        words = str(value or "").split()
        line = ""; lines = []
        for word in words:
            trial = (line + " " + word).strip()
            if font.size(trial)[0] > width and line:
                lines.append(line); line = word
            else: line = trial
        if line: lines.append(line)
        for i, item in enumerate(lines[:max_lines]):
            self.text(item, x, y + i * (font.get_height() + line_gap), color, font)
        return y + min(len(lines), max_lines) * (font.get_height() + line_gap)

    def button(self, label, rect, color=BLUE, disabled=False):
        pygame.draw.rect(self.screen, (36, 48, 68) if disabled else CARD, rect, border_radius=10)
        pygame.draw.rect(self.screen, MUTED if disabled else color, rect, 2, border_radius=10)
        img = self.button_font.render(label, True, MUTED if disabled else WHITE)
        self.screen.blit(img, img.get_rect(center=rect.center))

    def input_box(self, label, value, rect, active=False, secret=False):
        self.text(label, rect.x, rect.y - 27, MUTED, self.small)
        pygame.draw.rect(self.screen, BG, rect, border_radius=8)
        pygame.draw.rect(self.screen, CYAN if active else MUTED, rect, 2, border_radius=8)
        shown = "•" * len(value) if secret else value
        self.text(shown[-48:], rect.x + 12, rect.y + 11, WHITE, self.small)

    def base(self, heading, subtitle=""):
        self.screen.fill(BG)
        for x in range(0, self.screen.get_width(), 48): pygame.draw.line(self.screen, (17, 27, 45), (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, 48): pygame.draw.line(self.screen, (17, 27, 45), (0, y), (WIDTH, y))
        self.text("CYBERSAFE  /  SECURITY AWARENESS", 34, 22, CYAN, self.small)
        self.text(heading, 34, 62, WHITE, self.title)
        if subtitle: self.text(subtitle, 36, 110, MUTED, self.small)
        if self.user: self.text(self.user.get("display_name", "Player"), WIDTH - 250, 28, CYAN, self.small)
        pygame.draw.line(self.screen, (48, 65, 90), (34, 145), (WIDTH - 34, 145), 1)

    async def set_home(self):
        self.campaigns = await self.api.campaigns()
        self.dashboard_data = await self.api.dashboard()
        self.state = "HOME"

    async def auth_submit(self):
        if self.busy: return
        self.busy = True; self.message = "Đang xác thực..."
        try:
            if self.auth_mode == "login": self.user = await self.api.login(self.fields[0].strip(), self.fields[1])
            else: self.user = await self.api.register(self.fields[0].strip(), self.fields[1], self.fields[2].strip())
            await self.set_home()
        except APIError as exc:
            self.message = str(exc)
            if exc.status == 401:
                self.user = None
                self.state = "AUTH"
        finally: self.busy = False

    async def open_campaign(self, campaign):
        if self.busy: return
        self.busy = True; self.selected_campaign = campaign
        try:
            self.session = await self.api.start_session(campaign["id"])
            self.state = "GAME" if self.session["status"] == "PLAYING" else "FEEDBACK"
            if self.session["status"] == "COMPLETED": await self.finish_game()
        except APIError as exc:
            self.message = str(exc)
            if exc.status == 401:
                self.user = None
                self.state = "AUTH"
        finally: self.busy = False

    async def choose(self, choice_id, scenario_id):
        if self.busy: return
        self.busy = True
        try:
            self.session = await self.api.choose(self.session["id"], scenario_id, choice_id)
            self.state = "FEEDBACK"
        except APIError as exc:
            self.message = str(exc)
            if exc.status == 401:
                self.user = None
                self.state = "AUTH"
        finally: self.busy = False

    async def continue_game(self):
        if self.busy: return
        self.busy = True
        try:
            self.session = await self.api.continue_session(self.session["id"])
            if self.session["status"] == "COMPLETED": await self.finish_game()
            else: self.state = "GAME"
        except APIError as exc:
            self.message = str(exc)
            if exc.status == 401:
                self.user = None
                self.state = "AUTH"
        finally: self.busy = False

    async def finish_game(self):
        self.result_data = await self.api.result(self.session["id"])
        self.state = "RESULT"

    async def load_section(self, state):
        try:
            if state == "DASHBOARD": self.dashboard_data = await self.api.dashboard()
            elif state == "HISTORY": self.history_data = await self.api.history()
            elif state == "ERRORS": self.errors_data = await self.api.errors()
            elif state == "LEADERBOARD":
                if not self.campaigns: self.campaigns = await self.api.campaigns()
                if self.campaigns: self.leaderboard_data = await self.api.leaderboard(self.campaigns[0]["id"])
            self.state = state
        except APIError as exc:
            self.message = str(exc)
            if exc.status == 401:
                self.user = None
                self.state = "AUTH"

    def draw_auth(self):
        self.base("ĐĂNG NHẬP CYBERSAFE", "Pygame-CE client · xác thực qua FastAPI V3")
        box = pygame.Rect(310, 180, 500, 470); pygame.draw.rect(self.screen, PANEL, box, border_radius=18)
        self.text("ĐĂNG NHẬP" if self.auth_mode == "login" else "TẠO TÀI KHOẢN", 355, 205, CYAN, self.title)
        self.input_box("Email", self.fields[0], pygame.Rect(355, 285, 410, 42), self.focus == 0)
        self.input_box("Mật khẩu (tối thiểu 8 ký tự khi đăng ký)", self.fields[1], pygame.Rect(355, 365, 410, 42), self.focus == 1, True)
        if self.auth_mode == "register": self.input_box("Tên hiển thị", self.fields[2], pygame.Rect(355, 445, 410, 42), self.focus == 2)
        self.button("ĐĂNG NHẬP" if self.auth_mode == "login" else "ĐĂNG KÝ", pygame.Rect(355, 535 if self.auth_mode == "login" else 590, 180, 48), GREEN, self.busy)
        self.button("ĐĂNG KÝ" if self.auth_mode == "login" else "ĐĂNG NHẬP", pygame.Rect(550, 535 if self.auth_mode == "login" else 590, 200, 48), BLUE)
        self.wrap(self.message, 355, 610 if self.auth_mode == "login" else 655, 410, AMBER, self.small, max_lines=2)

    def draw_home(self):
        d = self.dashboard_data or {}
        self.base("TRUNG TÂM ĐIỀU HÀNH", "Chọn một khu vực để tiếp tục hành trình an toàn thông tin")
        stats = [("Chiến dịch hoàn tất", d.get("campaigns_completed", 0)), ("Phiên hoàn tất", d.get("sessions_completed", 0)), ("Đang thực hiện", d.get("sessions_in_progress", 0)), ("SafetyScore TB", f"{d.get('average_safety_score', 0)}%")]
        for i, (label, value) in enumerate(stats):
            r = pygame.Rect(34 + i * 270, 175, 250, 95); pygame.draw.rect(self.screen, PANEL, r, border_radius=12)
            self.text(value, r.x + 18, r.y + 15, CYAN, self.title); self.text(label, r.x + 18, r.y + 60, MUTED, self.small)
        items = [("CHIẾN DỊCH", "CAMPAIGNS"), ("DASHBOARD", "DASHBOARD"), ("LỊCH SỬ", "HISTORY"), ("SỔ TAY LỖI", "ERRORS"), ("BẢNG XẾP HẠNG", "LEADERBOARD")]
        for i, (label, _) in enumerate(items): self.button(label, pygame.Rect(34 + (i % 3) * 350, 320 + (i // 3) * 100, 320, 68), CYAN if i == 0 else BLUE)
        self.button("ĐĂNG XUẤT", pygame.Rect(850, 625, 220, 48), RED)

    def draw_campaigns(self):
        self.base("CHỌN CHIẾN DỊCH", "Các chiến dịch được tải trực tiếp từ backend")
        for i, c in enumerate(self.campaigns[:4]):
            y = 180 + i * 118; r = pygame.Rect(45, y, WIDTH - 90, 94); pygame.draw.rect(self.screen, PANEL, r, border_radius=12)
            self.text(c["title"], r.x + 20, y + 12, CYAN, self.font)
            self.wrap(c.get("description", ""), r.x + 20, y + 44, 760, MUTED, self.small, max_lines=2)
            self.button("TIẾP TỤC" if c.get("active_session_id") else "BẮT ĐẦU", pygame.Rect(875, y + 23, 180, 48), GREEN, self.busy)
        self.button("QUAY LẠI", pygame.Rect(45, 650, 170, 42), BLUE)

    def draw_game(self):
        s = self.session or {}; sc = s.get("current_scenario") or {}
        self.base("TÌNH HUỐNG ĐANG DIỄN RA", f"Quyết định {s.get('decision_count', 0) + 1} · trạng thái {s.get('status', '')}")
        pygame.draw.rect(self.screen, PANEL, pygame.Rect(45, 170, WIDTH - 90, 180), border_radius=14)
        self.text(sc.get("title", "Tình huống"), 70, 190, CYAN, self.title)
        self.wrap(sc.get("body", ""), 70, 245, WIDTH - 150, WHITE, self.font, max_lines=5)
        self.text("Chọn phương án xử lý:", 50, 375, AMBER, self.font)
        for i, choice in enumerate(sc.get("choices", [])[:4]):
            y = 420 + i * 65
            r = pygame.Rect(50, y, WIDTH - 100, 54); pygame.draw.rect(self.screen, CARD, r, border_radius=9); pygame.draw.rect(self.screen, BLUE, r, 1, border_radius=9)
            self.wrap(f"{choice.get('code', '')}. {choice.get('text', '')}", r.x + 15, r.y + 12, r.width - 30, WHITE, self.small, max_lines=2)
        self.button("TẠM DỪNG / VỀ TRUNG TÂM", pygame.Rect(850, 98, 220, 36), BLUE)

    def draw_feedback(self):
        fb = (self.session or {}).get("feedback") or {}
        self.base("PHÂN TÍCH HẬU QUẢ", "Phản hồi được lưu ở backend và có thể khôi phục sau khi tải lại")
        pygame.draw.rect(self.screen, PANEL, pygame.Rect(75, 180, WIDTH - 150, 380), border_radius=16)
        self.text("HẬU QUẢ LỰA CHỌN", 110, 210, AMBER, self.title)
        self.wrap(fb.get("consequence", ""), 110, 275, WIDTH - 220, WHITE, self.font, max_lines=4)
        self.text("GIẢI THÍCH", 110, 385, CYAN, self.font)
        self.wrap(fb.get("explanation", ""), 110, 430, WIDTH - 220, MUTED, self.font, max_lines=4)
        self.text(f"Safety +{fb.get('safety_points', 0)}  |  Risk +{fb.get('risk_points', 0)}", 110, 525, GREEN if fb.get('safety_points', 0) else RED)
        self.button("TIẾP TỤC", pygame.Rect(420, 600, 280, 55), GREEN, self.busy)

    def draw_result(self):
        r = self.result_data or {}; self.base("CHIẾN DỊCH HOÀN TẤT", "Kết quả do backend tính toán")
        vals = [("SafetyScore", f"{r.get('safety_score', 0)}%"), ("RiskScore", f"{r.get('risk_score', 0)}%"), ("Xếp loại", r.get("rank", "—")), ("Số quyết định", r.get("decision_count", 0))]
        for i, (k, v) in enumerate(vals):
            x = 100 + (i % 2) * 480; y = 220 + (i // 2) * 150
            pygame.draw.rect(self.screen, PANEL, pygame.Rect(x, y, 420, 110), border_radius=12)
            self.text(k, x + 22, y + 18, MUTED); self.text(v, x + 22, y + 55, CYAN, self.title)
        self.button("VỀ TRUNG TÂM", pygame.Rect(420, 570, 280, 55), GREEN)

    def draw_list(self, title, rows, kind):
        self.base(title, "Dữ liệu cá nhân được truy vấn theo tài khoản đang đăng nhập")
        y = 175
        for row in rows[:9]:
            pygame.draw.rect(self.screen, PANEL, pygame.Rect(55, y, WIDTH - 110, 48), border_radius=8)
            if kind == "history": label = f"{row.get('campaign')} · {row.get('status')} · {row.get('decision_count')} quyết định · Safety {row.get('safety_score')}%"
            elif kind == "errors": label = f"{row.get('error_category')} · {row.get('count')} lần"
            else: label = f"{row.get('display_name')} · Safety {row.get('safety_score')}% · Risk {row.get('risk_score')}%"
            self.text(label[:100], 75, y + 13, WHITE, self.small); y += 58
        self.button("QUAY LẠI", pygame.Rect(55, 650, 170, 42), BLUE)

    def draw(self):
        if self.state == "AUTH": self.draw_auth()
        elif self.state == "HOME": self.draw_home()
        elif self.state == "CAMPAIGNS": self.draw_campaigns()
        elif self.state == "GAME": self.draw_game()
        elif self.state == "FEEDBACK": self.draw_feedback()
        elif self.state == "RESULT": self.draw_result()
        elif self.state == "DASHBOARD":
            self.base("DASHBOARD CÁ NHÂN")
            d=self.dashboard_data or {}; self.wrap(str(d), 60, 185, WIDTH-120, WHITE, self.font, max_lines=12)
            self.button("QUAY LẠI", pygame.Rect(55,650,170,42), BLUE)
        elif self.state == "HISTORY": self.draw_list("LỊCH SỬ CHƠI", self.history_data, "history")
        elif self.state == "ERRORS": self.draw_list("SỔ TAY LỖI", self.errors_data, "errors")
        elif self.state == "LEADERBOARD": self.draw_list("BẢNG XẾP HẠNG", self.leaderboard_data, "leaderboard")
        if self.message and self.state != "AUTH": self.wrap(self.message, 300, 690, 500, AMBER, self.small, max_lines=1)

    async def click(self, pos):
        x,y=pos
        if self.state == "AUTH":
            if 285 <= y <= 335: self.focus=0
            elif 365 <= y <= 415: self.focus=1
            elif self.auth_mode == "register" and 445 <= y <= 495: self.focus=2
            elif (535 <= y <= 585 and self.auth_mode == "login") or (590 <= y <= 640 and self.auth_mode == "register"):
                if x < 555: await self.auth_submit()
                else: self.auth_mode = "register" if self.auth_mode == "login" else "login"; self.message = ""
        elif self.state == "HOME":
            if 320 <= y <= 388:
                if x < 354: self.state = "CAMPAIGNS"
                elif x < 704: await self.load_section("DASHBOARD")
                else: await self.load_section("HISTORY")
            elif 420 <= y <= 488:
                if x < 354: await self.load_section("ERRORS")
                elif x < 704: await self.load_section("LEADERBOARD")
            elif y >= 625 and x >= 850:
                self.api.token=None; self.api._save_browser_token(); self.user=None; self.state="AUTH"; self.fields=["","",""]
        elif self.state == "CAMPAIGNS":
            if y >= 650: self.state="HOME"
            else:
                idx=(y-180)//118
                if 0 <= idx < len(self.campaigns): await self.open_campaign(self.campaigns[idx])
        elif self.state == "GAME":
            if y <= 140 and x >= 840: self.state="HOME"
            else:
                sc=self.session.get("current_scenario") or {}; idx=(y-420)//65; choices=sc.get("choices",[])
                if 0 <= idx < len(choices): await self.choose(choices[idx]["id"], sc["id"])
        elif self.state == "FEEDBACK":
            if y >= 580: await self.continue_game()
        elif self.state == "RESULT":
            if y >= 560: await self.set_home()
        elif self.state in ("DASHBOARD","HISTORY","ERRORS","LEADERBOARD"):
            if y >= 640: self.state="HOME"

    async def restore_auth(self):
        if not self.api.token:
            return
        try:
            self.user = await self.api.me()
            await self.set_home()
        except APIError as exc:
            self.api.token = None
            self.api._save_browser_token()
            self.message = str(exc)

    async def run(self):
        await self.restore_auth()
        running=True
        while running:
            self.draw()
            for event in pygame.event.get():
                if event.type == pygame.QUIT: running=False
                elif event.type == pygame.VIDEORESIZE:
                    self.screen=pygame.display.set_mode(event.size, pygame.RESIZABLE)
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    await self.click(event.pos)
                elif event.type == pygame.KEYDOWN and self.state == "AUTH":
                    if event.key == pygame.K_TAB: self.focus=(self.focus+1)%(3 if self.auth_mode=="register" else 2)
                    elif event.key == pygame.K_RETURN: await self.auth_submit()
                    elif event.key == pygame.K_BACKSPACE: self.fields[self.focus]=self.fields[self.focus][:-1]
                    elif event.unicode.isprintable() and len(self.fields[self.focus])<120: self.fields[self.focus]+=event.unicode
            pygame.display.flip(); self.clock.tick(30); await asyncio.sleep(0)
        await self.api.close(); pygame.quit()

if __name__ == "__main__":
    asyncio.run(CyberSafeV3().run())
