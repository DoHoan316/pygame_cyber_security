import asyncio
import sys
import os
import math
import random
import pygame

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

from data.scenarios import SCENARIOS
from services.api_service import GameBridgeService

# Cấu hình cửa sổ rộng rãi, dễ đọc
WIDTH, HEIGHT = 1120, 740
FPS = 60

# Bảng màu hiện đại (Cyber Defense UI)
BG_DARK = (11, 17, 32)
BG_PANEL = (22, 33, 56)
BG_CARD = (30, 44, 72)
BG_CARD_HOVER = (44, 65, 105)
ACCENT_CYAN = (34, 211, 238)
ACCENT_BLUE = (59, 130, 246)
ACCENT_GREEN = (16, 185, 129)
ACCENT_RED = (244, 63, 94)
ACCENT_AMBER = (245, 158, 11)
TEXT_LIGHT = (248, 250, 252)
TEXT_MUTED = (148, 163, 184)
BORDER_SUBTLE = (51, 65, 85)

class CyberSecurityGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Chiến Dịch An Ninh Mạng - Mô Phỏng Tình Huống Thực Tế")
        self.clock = pygame.time.Clock()

        # Load Font Tiếng Việt UTF-8 từ assets/fonts (đảm bảo hiển thị dấu chuẩn cả trên Windows & Web)
        reg_font_path = os.path.join(BASE_DIR, "assets", "fonts", "font_regular.ttf")
        bold_font_path = os.path.join(BASE_DIR, "assets", "fonts", "font_bold.ttf")

        if os.path.exists(bold_font_path) and os.path.exists(reg_font_path):
            self.font_hero = pygame.font.Font(bold_font_path, 30)
            self.font_title = pygame.font.Font(bold_font_path, 22)
            self.font_sub = pygame.font.Font(bold_font_path, 17)
            self.font_body = pygame.font.Font(reg_font_path, 16)
            self.font_small = pygame.font.Font(reg_font_path, 14)
        else:
            self.font_hero = pygame.font.SysFont("segoeui", 30, bold=True)
            self.font_title = pygame.font.SysFont("segoeui", 22, bold=True)
            self.font_sub = pygame.font.SysFont("segoeui", 17, bold=True)
            self.font_body = pygame.font.SysFont("segoeui", 16)
            self.font_small = pygame.font.SysFont("segoeui", 14)

        self.bridge = GameBridgeService()

        # Trạng thái màn hình: LOGIN -> MENU -> PLAYING -> FEEDBACK -> SUMMARY
        self.state = "LOGIN"
        self.username_input = ""
        self.password_input = ""
        self.active_field = "username"
        self.status_msg = "Nhập tên người chơi và bấm ĐĂNG NHẬP để bắt đầu"

        # Dữ liệu chơi & hiệu ứng động
        self.play_mode = "ALL"  # "ALL" (30 câu) hoặc "QUICK" (10 câu ngẫu nhiên)
        self.active_scenarios = SCENARIOS[:]
        self.current_scen_idx = 0
        self.last_choice_result = None
        self.leaderboard_data = []
        self.streak_count = 0
        self.correct_count = 0

        # Hiệu ứng nền chuyển động nhẹ (Cyber Grid & Particles)
        self.tick_time = 0.0
        self.particles = [
            [random.randint(0, WIDTH), random.randint(0, HEIGHT), random.uniform(0.3, 1.0), random.randint(1, 3)]
            for _ in range(38)
        ]
        self.floating_popups = []  # Hiệu ứng +100 điểm bay lên

    def add_floating_popup(self, text, x, y, color):
        self.floating_popups.append({"text": text, "x": x, "y": y, "color": color, "alpha": 255, "life": 60})

    def draw_animated_background(self):
        self.screen.fill(BG_DARK)
        # Vẽ lưới công nghệ mờ
        grid_spacing = 48
        offset = int((self.tick_time * 15) % grid_spacing)
        for x in range(0, WIDTH, grid_spacing):
            pygame.draw.line(self.screen, (18, 28, 50), (x, 0), (x, HEIGHT), 1)
        for y in range(offset - grid_spacing, HEIGHT, grid_spacing):
            pygame.draw.line(self.screen, (18, 28, 50), (0, y), (WIDTH, y), 1)

        # Vẽ hạt ánh sáng trôi nổi
        for p in self.particles:
            p[1] -= p[2]
            if p[1] < 0:
                p[1] = HEIGHT
                p[0] = random.randint(0, WIDTH)
            pygame.draw.circle(self.screen, (34, 211, 238), (int(p[0]), int(p[1])), p[3])

    def draw_text_wrapped(self, text, font, color, rect, line_spacing=6):
        words = text.split(" ")
        lines = []
        current_line = ""
        for word in words:
            test_line = current_line + word + " "
            if font.size(test_line)[0] <= rect.width:
                current_line = test_line
            else:
                lines.append(current_line.strip())
                current_line = word + " "
        if current_line:
            lines.append(current_line.strip())

        y = rect.top
        for line in lines:
            if y + font.get_height() > rect.bottom + 8:
                break
            img = font.render(line, True, color)
            self.screen.blit(img, (rect.left, y))
            y += font.get_height() + line_spacing

    def draw_card_button(self, rect, text, badge=None, border_color=ACCENT_BLUE, bg_normal=BG_CARD):
        mouse_pos = pygame.mouse.get_pos()
        is_hover = rect.collidepoint(mouse_pos)
        fill = BG_CARD_HOVER if is_hover else bg_normal
        active_border = ACCENT_CYAN if is_hover else border_color

        # Đổ bóng nhẹ
        shadow_rect = rect.move(0, 4)
        pygame.draw.rect(self.screen, (6, 10, 20), shadow_rect, border_radius=12)

        pygame.draw.rect(self.screen, fill, rect, border_radius=12)
        pygame.draw.rect(self.screen, active_border, rect, width=2, border_radius=12)

        left_pad = 18
        if badge:
            badge_rect = pygame.Rect(rect.left + 14, rect.top + (rect.height - 34) // 2, 34, 34)
            pygame.draw.rect(self.screen, active_border, badge_rect, border_radius=8)
            b_img = self.font_sub.render(badge, True, BG_DARK)
            self.screen.blit(b_img, (badge_rect.centerx - b_img.get_width() // 2, badge_rect.centery - b_img.get_height() // 2))
            left_pad = 60

        text_rect = pygame.Rect(rect.left + left_pad, rect.top + 12, rect.width - left_pad - 16, rect.height - 20)
        self.draw_text_wrapped(text, self.font_body, TEXT_LIGHT, text_rect, line_spacing=4)
        return is_hover

    def handle_login_events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_TAB:
                self.active_field = "password" if self.active_field == "username" else "username"
            elif event.key == pygame.K_RETURN:
                self.trigger_login()
            elif event.key == pygame.K_BACKSPACE:
                if self.active_field == "username":
                    self.username_input = self.username_input[:-1]
                else:
                    self.password_input = self.password_input[:-1]
            else:
                if len(event.unicode) == 1 and event.unicode.isprintable():
                    if self.active_field == "username" and len(self.username_input) < 22:
                        self.username_input += event.unicode
                    elif self.active_field == "password" and len(self.password_input) < 22:
                        self.password_input += event.unicode

    def trigger_login(self):
        if self.username_input.strip():
            ok, msg = self.bridge.login(self.username_input.strip(), self.password_input.strip())
            self.status_msg = msg
            if ok:
                self.leaderboard_data = self.bridge.get_leaderboard()
                self.state = "MENU"

    def draw_login(self):
        # Huy hiệu khiên bảo mật ở trên
        shield_center = (WIDTH // 2, 105)
        pulse = int(4 * math.sin(self.tick_time * 4))
        pygame.draw.circle(self.screen, (20, 45, 75), shield_center, 46 + pulse)
        pygame.draw.circle(self.screen, ACCENT_CYAN, shield_center, 42, 2)
        icon_txt = self.font_title.render("CS", True, ACCENT_CYAN)
        self.screen.blit(icon_txt, (shield_center[0] - icon_txt.get_width() // 2, shield_center[1] - icon_txt.get_height() // 2))

        title = self.font_hero.render("CHIẾN DỊCH AN NINH MẠNG", True, TEXT_LIGHT)
        subtitle = self.font_body.render("Hệ thống mô phỏng phản xạ & tình huống An Toàn Thông Tin (30 Cấp Độ)", True, ACCENT_CYAN)
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 165))
        self.screen.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, 208))

        box = pygame.Rect(WIDTH // 2 - 250, 255, 500, 380)
        pygame.draw.rect(self.screen, BG_PANEL, box, border_radius=16)
        pygame.draw.rect(self.screen, BORDER_SUBTLE, box, 2, border_radius=16)

        # Ô Tên đăng nhập
        self.screen.blit(self.font_sub.render("Tên đăng nhập (Click vào ô hoặc bấm TAB):", True, TEXT_LIGHT), (box.left + 35, box.top + 30))
        u_rect = pygame.Rect(box.left + 35, box.top + 62, 430, 44)
        u_border = ACCENT_CYAN if self.active_field == "username" else BORDER_SUBTLE
        pygame.draw.rect(self.screen, BG_DARK, u_rect, border_radius=8)
        pygame.draw.rect(self.screen, u_border, u_rect, 2, border_radius=8)
        self.screen.blit(self.font_body.render(self.username_input, True, TEXT_LIGHT), (u_rect.left + 14, u_rect.top + 10))

        # Ô Mật khẩu
        self.screen.blit(self.font_sub.render("Mật khẩu:", True, TEXT_LIGHT), (box.left + 35, box.top + 125))
        p_rect = pygame.Rect(box.left + 35, box.top + 157, 430, 44)
        p_border = ACCENT_CYAN if self.active_field == "password" else BORDER_SUBTLE
        pygame.draw.rect(self.screen, BG_DARK, p_rect, border_radius=8)
        pygame.draw.rect(self.screen, p_border, p_rect, 2, border_radius=8)
        self.screen.blit(self.font_body.render("•" * len(self.password_input), True, TEXT_LIGHT), (p_rect.left + 14, p_rect.top + 10))

        # Nút Đăng nhập bấm chuột trực tiếp
        login_btn = pygame.Rect(box.left + 35, box.top + 230, 430, 52)
        self.draw_card_button(login_btn, "ĐĂNG NHẬP / TẠO TÀI KHOẢN NGAY", border_color=ACCENT_GREEN, bg_normal=(20, 65, 55))

        st = self.font_small.render(self.status_msg, True, ACCENT_AMBER)
        self.screen.blit(st, (box.centerx - st.get_width() // 2, box.top + 305))
        note = self.font_small.render("Hỗ trợ cả chế độ Online (FastAPI) và Offline tự động", True, TEXT_MUTED)
        self.screen.blit(note, (box.centerx - note.get_width() // 2, box.top + 332))

        return u_rect, p_rect, login_btn

    def draw_menu(self):
        user = self.bridge.current_user
        is_online = self.bridge.USE_REMOTE_SERVER
        badge_color = ACCENT_GREEN if is_online else ACCENT_AMBER
        mode_text = "ONLINE (FastAPI + SQLite)" if is_online else "OFFLINE (Cầu nối cục bộ)"

        # Thanh Header
        top_panel = pygame.Rect(40, 25, WIDTH - 80, 90)
        pygame.draw.rect(self.screen, BG_PANEL, top_panel, border_radius=14)
        pygame.draw.rect(self.screen, BORDER_SUBTLE, top_panel, 2, border_radius=14)

        self.screen.blit(self.font_title.render(f"Xin chào, {user['username']}", True, TEXT_LIGHT), (65, 40))
        self.screen.blit(self.font_body.render(f"Cấp bậc: {user['rank']}   |   Tổng điểm tích lũy: {user['total_score']} điểm", True, ACCENT_CYAN), (65, 75))

        # Trạng thái kết nối góc phải
        status_pill = pygame.Rect(WIDTH - 340, 48, 275, 42)
        pygame.draw.rect(self.screen, BG_DARK, status_pill, border_radius=20)
        pygame.draw.rect(self.screen, badge_color, status_pill, 2, border_radius=20)
        st_img = self.font_small.render(mode_text, True, badge_color)
        self.screen.blit(st_img, (status_pill.centerx - st_img.get_width() // 2, status_pill.centery - st_img.get_height() // 2))

        # Cột trái: Chế độ chơi + Bộ sưu tập lỗi
        btn_full = pygame.Rect(40, 140, 540, 72)
        self.draw_card_button(btn_full, "CHIẾN DỊCH TOÀN DIỆN (Đầy đủ 30 tình huống đa dạng)", badge="30", border_color=ACCENT_GREEN, bg_normal=(18, 60, 52))

        btn_quick = pygame.Rect(40, 228, 540, 72)
        self.draw_card_button(btn_quick, "LUYỆN TẬP NHANH (10 tình huống ngẫu nhiên)", badge="10", border_color=ACCENT_CYAN)

        # Khung Bộ Sưu Tập Lỗi Đã Học
        mistake_box = pygame.Rect(40, 320, 540, 380)
        pygame.draw.rect(self.screen, BG_PANEL, mistake_box, border_radius=14)
        pygame.draw.rect(self.screen, ACCENT_AMBER, mistake_box, 2, border_radius=14)
        self.screen.blit(self.font_sub.render("SỔ TAY LỖ HỔNG & LỖI BẢO MẬT ĐÃ GẶP:", True, ACCENT_AMBER), (62, 338))

        if not user["mistakes"]:
            self.screen.blit(self.font_body.render("• Bạn chưa mắc lỗi bảo mật nào. Tiếp tục phát huy nhé!", True, TEXT_MUTED), (62, 380))
        else:
            for idx, m in enumerate(user["mistakes"][-7:]):
                item_rect = pygame.Rect(60, 378 + idx * 42, 500, 34)
                pygame.draw.rect(self.screen, (45, 25, 38), item_rect, border_radius=6)
                self.screen.blit(self.font_small.render(f"⚠ {m}", True, (253, 164, 175)), (72, 386 + idx * 42))

        # Cột phải: Bảng xếp hạng
        lb_box = pygame.Rect(610, 140, 470, 560)
        pygame.draw.rect(self.screen, BG_PANEL, lb_box, border_radius=14)
        pygame.draw.rect(self.screen, ACCENT_BLUE, lb_box, 2, border_radius=14)
        self.screen.blit(self.font_sub.render("BẢNG XẾP HẠNG CHIẾN BINH AN NINH", True, ACCENT_CYAN), (635, 160))

        for i, entry in enumerate(self.leaderboard_data[:10]):
            row_rect = pygame.Rect(630, 205 + i * 47, 430, 38)
            is_me = entry["username"] == user["username"]
            row_bg = (35, 58, 95) if is_me else BG_DARK
            pygame.draw.rect(self.screen, row_bg, row_rect, border_radius=8)
            if is_me:
                pygame.draw.rect(self.screen, ACCENT_AMBER, row_rect, 1, border_radius=8)

            rank_color = ACCENT_AMBER if i == 0 else (ACCENT_CYAN if is_me else TEXT_LIGHT)
            line = f"#{i+1}  {entry['username']}  •  {entry['total_score']}đ ({entry['rank']})"
            self.screen.blit(self.font_small.render(line, True, rank_color), (645, row_rect.top + 10))

        return btn_full, btn_quick

    def draw_playing(self):
        scen = self.active_scenarios[self.current_scen_idx]
        user = self.bridge.current_user
        total_q = len(self.active_scenarios)

        # Thanh tiến trình phía trên
        progress_ratio = (self.current_scen_idx + 1) / total_q
        bar_bg = pygame.Rect(40, 24, WIDTH - 80, 12)
        pygame.draw.rect(self.screen, BG_PANEL, bar_bg, border_radius=6)
        pygame.draw.rect(self.screen, ACCENT_CYAN, (40, 24, int((WIDTH - 80) * progress_ratio), 12), border_radius=6)

        # Thông tin chỉ số
        info_txt = (
            f"Tiến độ: {self.current_scen_idx + 1}/{total_q}   |   "
            f"Chủ đề: {scen['category']}   |   "
            f"Trụ cột: {scen['cia_pillar']}   |   "
            f"Điểm: {user['total_score']}   |   Chuỗi đúng: {self.streak_count}🔥"
        )
        self.screen.blit(self.font_small.render(info_txt, True, ACCENT_AMBER), (40, 46))

        # Tiêu đề câu hỏi & Khung mô tả tình huống
        title_img = self.font_title.render(scen["title"], True, TEXT_LIGHT)
        self.screen.blit(title_img, (40, 78))

        desc_box = pygame.Rect(40, 118, WIDTH - 80, 125)
        pygame.draw.rect(self.screen, BG_PANEL, desc_box, border_radius=14)
        pygame.draw.rect(self.screen, ACCENT_BLUE, desc_box, 2, border_radius=14)
        self.draw_text_wrapped(scen["description"], self.font_body, TEXT_LIGHT, pygame.Rect(62, 134, WIDTH - 124, 98), line_spacing=6)

        # 4 Nút đáp án A, B, C, D rõ ràng, khoảng cách thoáng
        labels = ["A", "B", "C", "D"]
        choice_rects = []
        for i, choice in enumerate(scen["choices"]):
            btn_rect = pygame.Rect(40, 265 + i * 102, WIDTH - 80, 88)
            # Bỏ tiền tố "A. " nếu đã hiển thị badge A/B/C/D cho gọn
            clean_text = choice["text"][3:] if len(choice["text"]) > 3 and choice["text"][1] == "." else choice["text"]
            self.draw_card_button(btn_rect, clean_text, badge=labels[i], border_color=BORDER_SUBTLE)
            choice_rects.append((btn_rect, choice))

        # Nút thoát nhanh về Menu góc dưới
        quit_btn = pygame.Rect(WIDTH - 210, HEIGHT - 48, 170, 34)
        self.draw_card_button(quit_btn, "Về Dashboard", border_color=TEXT_MUTED, bg_normal=BG_PANEL)

        return choice_rects, quit_btn

    def draw_feedback(self):
        res = self.last_choice_result
        is_good = res["score_delta"] > 0
        main_color = ACCENT_GREEN if is_good else ACCENT_RED
        card_tint = (16, 48, 44) if is_good else (54, 22, 34)

        box = pygame.Rect(110, 120, WIDTH - 220, 420)
        pygame.draw.rect(self.screen, card_tint, box, border_radius=18)
        pygame.draw.rect(self.screen, main_color, box, 3, border_radius=18)

        status_label = "PHÂN TÍCH CHÍNH XÁC!" if is_good else "CẢNH BÁO RỦI RO BẢO MẬT!"
        self.screen.blit(self.font_hero.render(status_label, True, main_color), (150, 150))

        score_str = f"Mức độ rủi ro: {res['risk']}    |    Điểm số: {res['score_delta']:+d} điểm"
        self.screen.blit(self.font_sub.render(score_str, True, ACCENT_AMBER), (150, 205))

        pygame.draw.line(self.screen, main_color, (150, 242), (WIDTH - 150, 242), 1)

        self.screen.blit(self.font_sub.render("Giải thích chuyên môn:", True, ACCENT_CYAN), (150, 262))
        self.draw_text_wrapped(res["feedback"], self.font_body, TEXT_LIGHT, pygame.Rect(150, 296, WIDTH - 300, 140), line_spacing=8)

        if res.get("mistake_tag"):
            tag_rect = pygame.Rect(150, 445, WIDTH - 300, 44)
            pygame.draw.rect(self.screen, BG_DARK, tag_rect, border_radius=8)
            self.screen.blit(self.font_small.render(f"Đã ghi vào Sổ tay lỗ hổng: {res['mistake_tag']}", True, (253, 164, 175)), (165, 458))

        next_btn = pygame.Rect(WIDTH // 2 - 180, 575, 360, 60)
        self.draw_card_button(next_btn, "TIẾP TỤC TÌNH HUỐNG TIẾP THEO  >>", border_color=ACCENT_CYAN, bg_normal=BG_PANEL)
        return next_btn

    def draw_summary(self):
        user = self.bridge.current_user
        total_q = len(self.active_scenarios)
        accuracy = int((self.correct_count / total_q) * 100) if total_q else 0

        box = pygame.Rect(130, 100, WIDTH - 260, 460)
        pygame.draw.rect(self.screen, BG_PANEL, box, border_radius=18)
        pygame.draw.rect(self.screen, ACCENT_GREEN, box, 3, border_radius=18)

        self.screen.blit(self.font_hero.render("HOÀN THÀNH CHIẾN DỊCH HUẤN LUYỆN!", True, ACCENT_GREEN), (175, 135))
        self.screen.blit(self.font_title.render(f"Tỷ lệ xử lý an toàn: {self.correct_count}/{total_q} tình huống ({accuracy}%)", True, TEXT_LIGHT), (175, 195))
        self.screen.blit(self.font_title.render(f"Tổng điểm hiện tại: {user['total_score']} điểm", True, ACCENT_AMBER), (175, 240))
        self.screen.blit(self.font_title.render(f"Cấp bậc đạt được: {user['rank']}", True, ACCENT_CYAN), (175, 285))

        summary_msg = (
            "Toàn bộ kết quả và danh sách lỗ hổng đã gặp đã được đồng bộ tự động qua "
            "GameBridgeService. Bạn có thể quay lại Dashboard để xem Bảng xếp hạng hoặc luyện tập lại."
        )
        self.draw_text_wrapped(summary_msg, self.font_body, TEXT_MUTED, pygame.Rect(175, 345, WIDTH - 350, 120), line_spacing=6)

        menu_btn = pygame.Rect(WIDTH // 2 - 190, 595, 380, 60)
        self.draw_card_button(menu_btn, "QUAY VỀ DASHBOARD CHÍNH", border_color=ACCENT_CYAN)
        return menu_btn

    def update_and_draw_popups(self):
        for pop in self.floating_popups[:]:
            pop["y"] -= 1.2
            pop["life"] -= 1
            if pop["life"] <= 0:
                self.floating_popups.remove(pop)
            else:
                img = self.font_title.render(pop["text"], True, pop["color"])
                self.screen.blit(img, (pop["x"], int(pop["y"])))

    async def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            self.tick_time += dt
            self.draw_animated_background()

            u_rect = p_rect = login_btn = None
            btn_full = btn_quick = None
            choice_rects = []
            quit_btn = None
            next_btn = None
            menu_btn = None

            if self.state == "LOGIN":
                u_rect, p_rect, login_btn = self.draw_login()
            elif self.state == "MENU":
                btn_full, btn_quick = self.draw_menu()
            elif self.state == "PLAYING":
                choice_rects, quit_btn = self.draw_playing()
            elif self.state == "FEEDBACK":
                next_btn = self.draw_feedback()
            elif self.state == "SUMMARY":
                menu_btn = self.draw_summary()

            self.update_and_draw_popups()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                if self.state == "LOGIN":
                    self.handle_login_events(event)
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        if u_rect and u_rect.collidepoint(event.pos):
                            self.active_field = "username"
                        elif p_rect and p_rect.collidepoint(event.pos):
                            self.active_field = "password"
                        elif login_btn and login_btn.collidepoint(event.pos):
                            self.trigger_login()

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    pos = event.pos
                    if self.state == "MENU":
                        if btn_full and btn_full.collidepoint(pos):
                            self.active_scenarios = SCENARIOS[:]
                            self.current_scen_idx = 0
                            self.streak_count = 0
                            self.correct_count = 0
                            self.state = "PLAYING"
                        elif btn_quick and btn_quick.collidepoint(pos):
                            self.active_scenarios = random.sample(SCENARIOS, min(10, len(SCENARIOS)))
                            self.current_scen_idx = 0
                            self.streak_count = 0
                            self.correct_count = 0
                            self.state = "PLAYING"

                    elif self.state == "PLAYING":
                        if quit_btn and quit_btn.collidepoint(pos):
                            self.leaderboard_data = self.bridge.get_leaderboard()
                            self.state = "MENU"
                        else:
                            for rect, choice in choice_rects:
                                if rect.collidepoint(pos):
                                    scen = self.active_scenarios[self.current_scen_idx]
                                    self.last_choice_result = choice
                                    if choice["score_delta"] > 0:
                                        self.streak_count += 1
                                        self.correct_count += 1
                                        self.add_floating_popup(f"+{choice['score_delta']} ĐIỂM!", pos[0], pos[1] - 20, ACCENT_GREEN)
                                    else:
                                        self.streak_count = 0
                                        self.add_floating_popup(f"{choice['score_delta']} ĐIỂM!", pos[0], pos[1] - 20, ACCENT_RED)

                                    self.bridge.submit_scenario_result(
                                        scenario_id=scen["id"],
                                        score_delta=choice["score_delta"],
                                        risk=choice["risk"],
                                        mistake_tag=choice["mistake_tag"]
                                    )
                                    self.state = "FEEDBACK"
                                    break

                    elif self.state == "FEEDBACK" and next_btn and next_btn.collidepoint(pos):
                        self.current_scen_idx += 1
                        if self.current_scen_idx < len(self.active_scenarios):
                            self.state = "PLAYING"
                        else:
                            self.leaderboard_data = self.bridge.get_leaderboard()
                            self.state = "SUMMARY"

                    elif self.state == "SUMMARY" and menu_btn and menu_btn.collidepoint(pos):
                        self.state = "MENU"

            pygame.display.flip()
            await asyncio.sleep(0)

        pygame.quit()

if __name__ == "__main__":
    game = CyberSecurityGame()
    asyncio.run(game.run())
