
"""CyberSafe V3 Pygame client with separate Player and Admin workspaces."""

import asyncio
from pathlib import Path

import pygame

try:
    from .api_client import CyberSafeAPI, APIError
except ImportError:
    from api_client import CyberSafeAPI, APIError


WIDTH, HEIGHT = 1120, 740

BG = (8, 13, 25)
PANEL = (17, 27, 45)
PANEL_ALT = (21, 35, 56)
CARD = (25, 42, 67)
BORDER = (42, 62, 88)
CYAN = (75, 222, 226)
BLUE = (83, 145, 255)
GREEN = (75, 216, 157)
RED = (245, 105, 125)
AMBER = (255, 195, 95)
WHITE = (239, 246, 255)
MUTED = (150, 169, 192)
DARK = (5, 11, 20)


class CyberSafeV3:
    def __init__(self):
        pygame.init()

        self.window = pygame.display.set_mode(
            (WIDTH, HEIGHT),
            pygame.RESIZABLE,
        )
        self.screen = pygame.Surface((WIDTH, HEIGHT))

        pygame.display.set_caption(
            "CyberSafe | Security Awareness"
        )

        self.clock = pygame.time.Clock()

        font_dir = Path(__file__).parent / "assets" / "fonts"
        regular_path = font_dir / "font_regular.ttf"
        bold_path = font_dir / "font_bold.ttf"

        self.font = pygame.font.Font(str(regular_path), 20)
        self.body_font = pygame.font.Font(str(regular_path), 16)
        self.small_font = pygame.font.Font(str(regular_path), 13)
        self.title_font = pygame.font.Font(str(bold_path), 31)
        self.heading_font = pygame.font.Font(str(bold_path), 21)
        self.button_font = pygame.font.Font(str(bold_path), 13)
        self.stat_font = pygame.font.Font(str(bold_path), 27)

        self.api = CyberSafeAPI()

        self.state = "AUTH"
        self.auth_mode = "login"

        self.fields = {
            "email": "",
            "password": "",
            "display_name": "",
        }

        self.focus = "email"
        self.user = None

        self.message = (
            "Đăng nhập hoặc tạo tài khoản để bắt đầu."
        )

        self.busy = False

        # Player data
        self.campaigns = []
        self.dashboard_data = {}
        self.history_data = []
        self.errors_data = []
        self.leaderboard_data = []

        self.session = None
        self.selected_campaign = None
        self.result_data = None

        # Admin data
        self.admin_overview_data = {}
        self.admin_users_data = []
        self.admin_users_total = 0

        self.admin_query = ""
        self.admin_search_value = ""

        self.admin_user_offset = 0
        self.admin_page_offset = 0
        self.admin_visible_rows = 6

        # UI state
        self.hitboxes = {}
        self.mouse_pos = (0, 0)
        self.scroll = 0

    # ------------------------------------------------------------------
    # Common drawing helpers
    # ------------------------------------------------------------------

    def add_hitbox(self, key, rect):
        self.hitboxes[key] = pygame.Rect(rect)

    def text(
        self,
        value,
        x,
        y,
        color=WHITE,
        font=None,
        max_width=None,
    ):
        font = font or self.font
        value = str(value if value is not None else "")

        if max_width is not None and max_width > 0:
            while value and font.size(value)[0] > max_width:
                value = (
                    value[:-2] + "…"
                    if len(value) > 2
                    else value[:-1]
                )

        image = font.render(value, True, color)
        self.screen.blit(image, (int(x), int(y)))

        return image.get_width()

    def wrap(
        self,
        value,
        x,
        y,
        width,
        color=WHITE,
        font=None,
        gap=5,
        max_lines=4,
    ):
        font = font or self.body_font
        value = str(value or "").replace("\n", " ")

        words = value.split()
        lines = []
        line = ""

        for word in words:
            trial = f"{line} {word}".strip()

            if line and font.size(trial)[0] > width:
                lines.append(line)
                line = word
            else:
                line = trial

        if line:
            lines.append(line)

        shown = lines[:max_lines]

        if len(lines) > max_lines and shown:
            last = shown[-1]

            while last and font.size(last + "…")[0] > width:
                last = last[:-1]

            shown[-1] = last.rstrip() + "…"

        line_height = font.get_linesize() + gap

        for index, item in enumerate(shown):
            self.text(
                item,
                x,
                y + index * line_height,
                color,
                font,
                width,
            )

        return y + len(shown) * line_height

    def panel(
        self,
        rect,
        fill=PANEL,
        outline=BORDER,
        radius=14,
    ):
        rect = pygame.Rect(rect)

        pygame.draw.rect(
            self.screen,
            fill,
            rect,
            border_radius=radius,
        )

        pygame.draw.rect(
            self.screen,
            outline,
            rect,
            1,
            border_radius=radius,
        )

    def button(
        self,
        key,
        label,
        rect,
        color=BLUE,
        disabled=False,
    ):
        rect = pygame.Rect(rect)
        self.add_hitbox(key, rect)

        hovered = rect.collidepoint(self.mouse_pos)

        fill = (
            (34, 54, 82)
            if disabled
            else (31, 57, 88)
            if hovered
            else CARD
        )

        border = MUTED if disabled else color

        pygame.draw.rect(
            self.screen,
            fill,
            rect,
            border_radius=9,
        )

        pygame.draw.rect(
            self.screen,
            border,
            rect,
            1 if disabled else 2,
            border_radius=9,
        )

        font = self.button_font

        if font.size(label)[0] > rect.width - 16:
            font = self.small_font

        image = font.render(
            label,
            True,
            MUTED if disabled else WHITE,
        )

        self.screen.blit(
            image,
            image.get_rect(center=rect.center),
        )

    def input_box(
        self,
        key,
        label,
        value,
        rect,
        secret=False,
        placeholder="",
    ):
        rect = pygame.Rect(rect)
        self.add_hitbox(key, rect)

        active = self.focus == key

        self.text(
            label,
            rect.x,
            rect.y - 22,
            MUTED,
            self.small_font,
        )

        pygame.draw.rect(
            self.screen,
            DARK,
            rect,
            border_radius=8,
        )

        pygame.draw.rect(
            self.screen,
            CYAN if active else BORDER,
            rect,
            2,
            border_radius=8,
        )

        if secret and value:
            shown = "•" * len(value)
        else:
            shown = value[-42:] if value else placeholder

        self.text(
            shown,
            rect.x + 12,
            rect.y + 11,
            WHITE if value else MUTED,
            self.body_font,
            rect.width - 24,
        )

    def draw_background(self):
        self.screen.fill(BG)

        for x in range(0, WIDTH, 48):
            pygame.draw.line(
                self.screen,
                (15, 25, 41),
                (x, 0),
                (x, HEIGHT),
                1,
            )

        for y in range(0, HEIGHT, 48):
            pygame.draw.line(
                self.screen,
                (15, 25, 41),
                (0, y),
                (WIDTH, y),
                1,
            )

    def base(self, heading, subtitle=""):
        self.draw_background()

        self.text(
            "CYBERSAFE",
            34,
            22,
            CYAN,
            self.heading_font,
        )

        self.text(
            "SECURITY AWARENESS PLATFORM",
            151,
            28,
            MUTED,
            self.small_font,
        )

        if self.user:
            display_name = (
                self.user.get("display_name")
                or self.user.get("email")
                or "User"
            )

            role = self.user.get("role", "Player")

            self.text(
                display_name,
                780,
                24,
                WHITE,
                self.small_font,
                155,
            )

            self.text(
                role.upper(),
                940,
                24,
                CYAN if role == "Admin" else MUTED,
                self.small_font,
                55,
            )

            self.button(
                "logout",
                "ĐĂNG XUẤT",
                (1000, 17, 86, 31),
                RED,
            )

        self.text(
            heading,
            34,
            62,
            WHITE,
            self.title_font,
            790,
        )

        if subtitle:
            self.text(
                subtitle,
                36,
                105,
                MUTED,
                self.small_font,
                900,
            )

        pygame.draw.line(
            self.screen,
            BORDER,
            (34, 139),
            (1086, 139),
            1,
        )

    def stat_card(
        self,
        rect,
        label,
        value,
        accent=CYAN,
        foot=None,
    ):
        self.panel(rect)

        x, y, _, _ = rect

        self.text(
            value,
            x + 16,
            y + 13,
            accent,
            self.stat_font,
            rect[2] - 30,
        )

        self.text(
            label,
            x + 17,
            y + 53,
            MUTED,
            self.small_font,
            rect[2] - 30,
        )

        if foot:
            self.text(
                foot,
                x + 17,
                y + 72,
                MUTED,
                self.small_font,
                rect[2] - 30,
            )

    def progress_bar(self, rect, ratio, color=CYAN):
        rect = pygame.Rect(rect)

        pygame.draw.rect(
            self.screen,
            (35, 49, 70),
            rect,
            border_radius=5,
        )

        ratio = max(
            0.0,
            min(1.0, float(ratio or 0)),
        )

        fill_width = int(rect.width * ratio)

        if fill_width > 0:
            pygame.draw.rect(
                self.screen,
                color,
                (rect.x, rect.y, fill_width, rect.height),
                border_radius=5,
            )

    def draw_message(self):
        if not self.message:
            return

        rect = pygame.Rect(34, 684, 1052, 34)

        self.panel(
            rect,
            fill=(47, 34, 30),
            outline=(117, 80, 47),
            radius=8,
        )

        self.text(
            self.message,
            48,
            693,
            AMBER,
            self.small_font,
            1020,
        )

    def present(self):
        window_width, window_height = self.window.get_size()

        scale = min(
            window_width / WIDTH,
            window_height / HEIGHT,
        )

        draw_width = max(1, int(WIDTH * scale))
        draw_height = max(1, int(HEIGHT * scale))

        scaled = pygame.transform.smoothscale(
            self.screen,
            (draw_width, draw_height),
        )

        self.window.fill(BG)

        offset_x = (window_width - draw_width) // 2
        offset_y = (window_height - draw_height) // 2

        self.window.blit(
            scaled,
            (offset_x, offset_y),
        )

        pygame.display.flip()

    def screen_to_canvas(self, position):
        window_width, window_height = self.window.get_size()

        scale = min(
            window_width / WIDTH,
            window_height / HEIGHT,
        )

        draw_width = WIDTH * scale
        draw_height = HEIGHT * scale

        offset_x = (window_width - draw_width) / 2
        offset_y = (window_height - draw_height) / 2

        x = (position[0] - offset_x) / scale
        y = (position[1] - offset_y) / scale

        return int(x), int(y)

    def expire_session(
        self,
        message="Phiên đăng nhập đã hết hạn. Vui lòng đăng nhập lại.",
    ):
        self.api.clear_token()
        self.user = None
        self.state = "AUTH"
        self.auth_mode = "login"
        self.focus = "email"
        self.message = message

    def handle_error(self, exc):
        self.message = (
            str(exc)
            or "Đã xảy ra lỗi không xác định."
        )

        if (
            isinstance(exc, APIError)
            and exc.status == 401
            and self.user
        ):
            self.expire_session()

    # ------------------------------------------------------------------
    # Authentication and routing by role
    # ------------------------------------------------------------------

    async def auth_submit(self):
        if self.busy:
            return

        email = self.fields["email"].strip()
        password = self.fields["password"]
        display_name = self.fields["display_name"].strip()

        if not email or not password:
            self.message = (
                "Vui lòng nhập đầy đủ email và mật khẩu."
            )
            return

        if self.auth_mode == "register" and not display_name:
            self.message = (
                "Vui lòng nhập tên hiển thị."
            )
            return

        self.busy = True
        self.message = "Đang xác thực tài khoản..."

        try:
            if self.auth_mode == "login":
                self.user = await self.api.login(
                    email,
                    password,
                )
            else:
                self.user = await self.api.register(
                    email,
                    password,
                    display_name,
                )

            # Route Admin and Player to different workspaces.
            await self.set_home()

        except Exception as exc:
            self.user = None
            self.handle_error(exc)

        finally:
            self.busy = False

    async def set_home(self):
        self.message = ""
        self.focus = None

        if self.user and self.user.get("role") == "Admin":
            self.state = "ADMIN"
            await self.load_admin_data()
        else:
            self.state = "HOME"
            await self.load_player_home()

    async def load_player_home(self):
        self.campaigns = []
        self.dashboard_data = {}

        try:
            self.campaigns = await self.api.campaigns()

        except Exception as exc:
            self.handle_error(exc)

            if self.state == "AUTH":
                return

        try:
            self.dashboard_data = await self.api.dashboard()

        except Exception as exc:
            self.handle_error(exc)

        if self.state != "AUTH":
            self.state = "HOME"

    async def restore_auth(self):
        if not self.api.token:
            return

        try:
            self.user = await self.api.me()
            await self.set_home()

        except Exception as exc:
            if isinstance(exc, APIError) and exc.status == 401:
                self.expire_session()
            else:
                self.state = "AUTH"
                self.handle_error(exc)

    def logout(self):
        self.api.clear_token()

        self.user = None
        self.state = "AUTH"
        self.auth_mode = "login"

        self.fields = {
            "email": "",
            "password": "",
            "display_name": "",
        }

        self.focus = "email"
        self.message = "Đã đăng xuất khỏi CyberSafe."

        self.admin_query = ""
        self.admin_search_value = ""

    # ------------------------------------------------------------------
    # Admin data and actions
    # ------------------------------------------------------------------

    async def load_admin_data(self):
        if (
            not self.user
            or self.user.get("role") != "Admin"
        ):
            self.state = "HOME"
            return

        self.state = "ADMIN"
        self.busy = True

        try:
            self.admin_overview_data = (
                await self.api.admin_overview()
            )

            await self.load_admin_users(
                show_message=False,
            )

            self.message = ""

        except Exception as exc:
            self.handle_error(exc)

        finally:
            self.busy = False

    async def load_admin_users(self, show_message=True):
        if (
            not self.user
            or self.user.get("role") != "Admin"
        ):
            return

        data = await self.api.admin_users(
            query=self.admin_query,
            offset=0,
            limit=100,
        )

        self.admin_users_total = int(
            data.get("total", 0)
        )

        self.admin_users_data = (
            data.get("items", []) or []
        )

        self.admin_page_offset = 0
        self.admin_user_offset = 0

        if show_message:
            self.message = (
                f"Đã tải {len(self.admin_users_data)} tài khoản."
            )

    async def search_admin_users(self):
        if self.busy:
            return

        self.busy = True
        self.admin_query = self.admin_search_value.strip()

        try:
            await self.load_admin_users(
                show_message=False,
            )

            if self.admin_query:
                self.message = (
                    "Tìm thấy "
                    f"{self.admin_users_total} tài khoản phù hợp."
                )
            else:
                self.message = (
                    f"Tổng cộng {self.admin_users_total} tài khoản."
                )

        except Exception as exc:
            self.handle_error(exc)

        finally:
            self.busy = False

    async def change_admin_page(self, direction):
        if self.busy:
            return

        next_local = (
            self.admin_user_offset
            + direction * self.admin_visible_rows
        )

        if (
            direction > 0
            and next_local >= len(self.admin_users_data)
        ):
            next_page = (
                self.admin_page_offset
                + len(self.admin_users_data)
            )

            if next_page < self.admin_users_total:
                self.busy = True

                try:
                    data = await self.api.admin_users(
                        query=self.admin_query,
                        offset=next_page,
                        limit=100,
                    )

                    self.admin_users_data = (
                        data.get("items", []) or []
                    )

                    self.admin_page_offset = next_page
                    self.admin_user_offset = 0

                except Exception as exc:
                    self.handle_error(exc)

                finally:
                    self.busy = False

            return

        if direction < 0 and next_local < 0:
            if self.admin_page_offset <= 0:
                self.admin_user_offset = 0
                return

            previous_page = max(
                0,
                self.admin_page_offset - 100,
            )

            self.busy = True

            try:
                data = await self.api.admin_users(
                    query=self.admin_query,
                    offset=previous_page,
                    limit=100,
                )

                self.admin_users_data = (
                    data.get("items", []) or []
                )

                self.admin_page_offset = previous_page

                self.admin_user_offset = max(
                    0,
                    len(self.admin_users_data)
                    - self.admin_visible_rows,
                )

            except Exception as exc:
                self.handle_error(exc)

            finally:
                self.busy = False

            return

        self.admin_user_offset = max(
            0,
            min(
                next_local,
                max(
                    0,
                    len(self.admin_users_data)
                    - self.admin_visible_rows,
                ),
            ),
        )

    async def toggle_admin_user(self, user):
        if self.busy or user.get("role") == "Admin":
            return

        next_status = not bool(
            user.get("is_active")
        )

        self.busy = True

        try:
            await self.api.admin_set_user_status(
                user["id"],
                next_status,
            )

            await self.load_admin_data()

            self.message = (
                "Đã kích hoạt tài khoản."
                if next_status
                else "Đã vô hiệu hóa tài khoản."
            )

        except Exception as exc:
            self.handle_error(exc)

        finally:
            self.busy = False

    # ------------------------------------------------------------------
    # Player data and game actions
    # ------------------------------------------------------------------

    async def load_section(self, section):
        if self.busy:
            return

        self.busy = True

        try:
            if section == "DASHBOARD":
                self.dashboard_data = (
                    await self.api.dashboard()
                )

            elif section == "HISTORY":
                self.history_data = (
                    await self.api.history()
                )

            elif section == "ERRORS":
                self.errors_data = (
                    await self.api.errors()
                )

            elif section == "LEADERBOARD":
                if not self.campaigns:
                    self.campaigns = (
                        await self.api.campaigns()
                    )

                self.leaderboard_data = []

                if self.campaigns:
                    self.leaderboard_data = (
                        await self.api.leaderboard(
                            self.campaigns[0]["id"]
                        )
                    )

            self.state = section
            self.message = ""

        except Exception as exc:
            self.handle_error(exc)

        finally:
            self.busy = False

    async def open_campaign(self, campaign):
        if self.busy:
            return

        self.busy = True
        self.selected_campaign = campaign

        try:
            self.session = await self.api.start_session(
                campaign["id"]
            )

            status = self.session.get("status")

            if status == "COMPLETED":
                await self.finish_game()

            elif status == "FEEDBACK":
                self.state = "FEEDBACK"

            else:
                self.state = "GAME"

            self.message = ""

        except Exception as exc:
            self.handle_error(exc)

        finally:
            self.busy = False

    async def choose(self, choice_id, scenario_id):
        if self.busy or not self.session:
            return

        self.busy = True

        try:
            self.session = await self.api.choose(
                self.session["id"],
                scenario_id,
                choice_id,
            )

            self.state = "FEEDBACK"
            self.message = ""

        except Exception as exc:
            self.handle_error(exc)

        finally:
            self.busy = False

    async def continue_game(self):
        if self.busy or not self.session:
            return

        self.busy = True

        try:
            self.session = (
                await self.api.continue_session(
                    self.session["id"]
                )
            )

            if self.session.get("status") == "COMPLETED":
                await self.finish_game()

            elif self.session.get("status") == "FEEDBACK":
                self.state = "FEEDBACK"

            else:
                self.state = "GAME"

            self.message = ""

        except Exception as exc:
            self.handle_error(exc)

        finally:
            self.busy = False

    async def finish_game(self):
        if not self.session:
            return

        self.result_data = await self.api.result(
            self.session["id"]
        )

        self.state = "RESULT"
        self.message = ""

    # ------------------------------------------------------------------
    # Authentication screen
    # ------------------------------------------------------------------

    def draw_auth(self):
        self.base(
            "ĐĂNG NHẬP CYBERSAFE",
            "Đăng nhập để tiếp tục hành trình rèn luyện an toàn thông tin.",
        )

        self.panel(
            (295, 165, 530, 515),
            fill=PANEL_ALT,
            radius=18,
        )

        self.text(
            "CHÀO MỪNG TRỞ LẠI",
            345,
            195,
            CYAN,
            self.heading_font,
        )

        self.text(
            "Đăng nhập bằng tài khoản Player hoặc Admin.",
            347,
            229,
            MUTED,
            self.small_font,
        )

        self.input_box(
            "email",
            "EMAIL",
            self.fields["email"],
            (347, 305, 426, 46),
            placeholder="name@example.com",
        )

        self.input_box(
            "password",
            "MẬT KHẨU",
            self.fields["password"],
            (347, 395, 426, 46),
            secret=True,
            placeholder="Nhập mật khẩu",
        )

        if self.auth_mode == "register":
            self.input_box(
                "display_name",
                "TÊN HIỂN THỊ",
                self.fields["display_name"],
                (347, 485, 426, 46),
                placeholder="Tên của bạn",
            )

            primary_y = 555
            switch_y = 610
            message_y = 652

        else:
            primary_y = 485
            switch_y = 545
            message_y = 600

        self.button(
            "auth_submit",
            (
                "ĐANG XÁC THỰC..."
                if self.busy
                else (
                    "ĐĂNG NHẬP HỆ THỐNG"
                    if self.auth_mode == "login"
                    else "TẠO TÀI KHOẢN"
                )
            ),
            (347, primary_y, 426, 48),
            GREEN,
            self.busy,
        )

        self.button(
            "auth_switch",
            (
                "Chưa có tài khoản? Đăng ký"
                if self.auth_mode == "login"
                else "Đã có tài khoản? Đăng nhập"
            ),
            (347, switch_y, 426, 38),
            BLUE,
        )

        if self.message:
            self.wrap(
                self.message,
                347,
                message_y,
                426,
                AMBER,
                self.small_font,
                max_lines=2,
            )

    # ------------------------------------------------------------------
    # Player screens
    # ------------------------------------------------------------------

    def draw_home(self):
        data = self.dashboard_data or {}

        self.base(
            "PLAYER COMMAND CENTER",
            "Tổng quan tiến trình và các khu vực rèn luyện của bạn.",
        )

        stats = [
            (
                "CHIẾN DỊCH HOÀN TẤT",
                data.get("campaigns_completed", 0),
                CYAN,
            ),
            (
                "PHIÊN ĐÃ HOÀN TẤT",
                data.get("sessions_completed", 0),
                GREEN,
            ),
            (
                "ĐANG THỰC HIỆN",
                data.get("sessions_in_progress", 0),
                AMBER,
            ),
            (
                "SAFETY SCORE TB",
                f"{data.get('average_safety_score', 0)}%",
                BLUE,
            ),
        ]

        for index, (label, value, accent) in enumerate(stats):
            self.stat_card(
                (34 + index * 267, 164, 250, 91),
                label,
                value,
                accent,
            )

        self.text(
            "KHU VỰC CHỨC NĂNG",
            36,
            287,
            CYAN,
            self.small_font,
        )

        cards = [
            (
                "player_campaigns",
                "CHIẾN DỊCH",
                "Bắt đầu hoặc tiếp tục tình huống",
                (34, 315, 330, 112),
                CYAN,
            ),
            (
                "player_dashboard",
                "DASHBOARD",
                "Điểm số và nhóm lỗi cá nhân",
                (395, 315, 330, 112),
                BLUE,
            ),
            (
                "player_history",
                "LỊCH SỬ CHƠI",
                "Các phiên rèn luyện trước đây",
                (756, 315, 330, 112),
                GREEN,
            ),
            (
                "player_errors",
                "SỔ TAY LỖI",
                "Những lỗi cần chú ý và cải thiện",
                (214, 455, 330, 112),
                AMBER,
            ),
            (
                "player_leaderboard",
                "BẢNG XẾP HẠNG",
                "So sánh kết quả với người chơi",
                (576, 455, 330, 112),
                BLUE,
            ),
        ]

        for key, title, subtitle, rect, accent in cards:
            self.panel(rect)

            self.text(
                title,
                rect[0] + 18,
                rect[1] + 22,
                accent,
                self.heading_font,
            )

            self.wrap(
                subtitle,
                rect[0] + 18,
                rect[1] + 58,
                rect[2] - 36,
                MUTED,
                self.small_font,
                max_lines=2,
            )

            self.add_hitbox(key, rect)

        self.text(
            (
                f"Tài khoản: {self.user.get('email', '')}"
                if self.user
                else ""
            ),
            36,
            615,
            MUTED,
            self.small_font,
            800,
        )

    def draw_campaigns(self):
        self.base(
            "CHỌN CHIẾN DỊCH",
            "Dữ liệu chiến dịch được tải trực tiếp từ máy chủ.",
        )

        visible = self.campaigns[:4]

        if not visible:
            self.panel((45, 180, 1030, 160))

            self.text(
                "Chưa có chiến dịch khả dụng.",
                75,
                220,
                MUTED,
                self.font,
            )

        for index, campaign in enumerate(visible):
            y = 170 + index * 116
            rect = (45, y, 1030, 98)

            self.panel(rect)

            self.text(
                campaign.get(
                    "code",
                    f"MISSION {index + 1}",
                ),
                68,
                y + 15,
                CYAN,
                self.small_font,
            )

            self.text(
                campaign.get("title", "Chiến dịch"),
                68,
                y + 36,
                WHITE,
                self.heading_font,
                630,
            )

            self.wrap(
                campaign.get("description", ""),
                68,
                y + 66,
                690,
                MUTED,
                self.small_font,
                max_lines=1,
            )

            label = (
                "TIẾP TỤC"
                if campaign.get("active_session_id")
                else "BẮT ĐẦU"
            )

            self.button(
                f"campaign_{index}",
                label,
                (870, y + 27, 165, 44),
                GREEN,
                self.busy,
            )

        self.button(
            "back_home",
            "← QUAY LẠI",
            (45, 650, 160, 40),
            BLUE,
        )

    def draw_personal_dashboard(self):
        data = self.dashboard_data or {}

        self.base(
            "DASHBOARD CÁ NHÂN",
            "Các chỉ số được tính từ lịch sử phiên chơi của tài khoản hiện tại.",
        )

        stats = [
            (
                "CHIẾN DỊCH HOÀN TẤT",
                data.get("campaigns_completed", 0),
                CYAN,
            ),
            (
                "PHIÊN ĐÃ HOÀN TẤT",
                data.get("sessions_completed", 0),
                GREEN,
            ),
            (
                "ĐANG THỰC HIỆN",
                data.get("sessions_in_progress", 0),
                AMBER,
            ),
            (
                "SAFETY SCORE TB",
                f"{data.get('average_safety_score', 0)}%",
                BLUE,
            ),
            (
                "SAFETY SCORE CAO NHẤT",
                f"{data.get('best_safety_score', 0)}%",
                GREEN,
            ),
        ]

        for index, (label, value, accent) in enumerate(stats[:4]):
            self.stat_card(
                (34 + index * 267, 170, 250, 91),
                label,
                value,
                accent,
            )

        self.stat_card(
            (34, 278, 250, 91),
            stats[4][0],
            stats[4][1],
            stats[4][2],
        )

        self.text(
            "NHÓM LỖI ĐÃ GHI NHẬN",
            34,
            410,
            CYAN,
            self.heading_font,
        )

        groups = data.get("error_groups", []) or []

        if not groups:
            self.panel((34, 450, 1052, 120))

            self.text(
                "Chưa ghi nhận lỗi rủi ro. Hãy tiếp tục duy trì thói quen tốt!",
                58,
                495,
                GREEN,
                self.body_font,
            )

        else:
            for index, group in enumerate(groups[:4]):
                y = 450 + index * 42

                self.panel(
                    (34, y, 1052, 34),
                    fill=PANEL,
                )

                self.text(
                    group.get("category", "Không xác định"),
                    52,
                    y + 9,
                    WHITE,
                    self.small_font,
                    840,
                )

                self.text(
                    f"{group.get('count', 0)} lần",
                    960,
                    y + 9,
                    AMBER,
                    self.small_font,
                )

        self.button(
            "back_home",
            "← QUAY LẠI",
            (34, 635, 160, 40),
            BLUE,
        )

    def draw_player_list(self, title, rows, kind):
        self.base(
            title,
            "Thông tin được truy vấn theo tài khoản đang đăng nhập.",
        )

        if not rows:
            self.panel((45, 175, 1030, 135))

            empty = "Chưa có dữ liệu để hiển thị."

            if kind == "errors":
                empty = "Chưa ghi nhận nhóm lỗi nào."

            self.text(
                empty,
                75,
                220,
                MUTED,
                self.body_font,
            )

        for index, row in enumerate(rows[:8]):
            y = 170 + index * 58

            self.panel(
                (45, y, 1030, 49),
                fill=PANEL,
            )

            if kind == "history":
                label = (
                    f"{row.get('campaign', 'Chiến dịch')}  ·  "
                    f"{row.get('status', '')}  ·  "
                    f"{row.get('decision_count', 0)} quyết định  ·  "
                    f"Safety {row.get('safety_score', 0)}%"
                )

            elif kind == "errors":
                label = (
                    f"{row.get('error_category', 'Không xác định')}  ·  "
                    f"{row.get('count', 0)} lần"
                )

            else:
                label = (
                    f"{row.get('display_name', 'Người chơi')}  ·  "
                    f"Safety {row.get('safety_score', 0)}%  ·  "
                    f"Risk {row.get('risk_score', 0)}%"
                )

            self.text(
                label,
                66,
                y + 15,
                WHITE,
                self.small_font,
                970,
            )

        self.button(
            "back_home",
            "← QUAY LẠI",
            (45, 650, 160, 40),
            BLUE,
        )

    def draw_game(self):
        session = self.session or {}

        scenario = (
            session.get("current_scenario") or {}
        )

        campaign_title = (
            self.selected_campaign.get("title", "Chiến dịch")
            if self.selected_campaign
            else "Chiến dịch"
        )

        self.base(
            "TÌNH HUỐNG ĐANG DIỄN RA",
            (
                f"{campaign_title}"
                f"  ·  Quyết định "
                f"{session.get('decision_count', 0) + 1}"
            ),
        )

        self.panel(
            (45, 165, 1030, 190),
            fill=PANEL_ALT,
        )

        self.text(
            scenario.get("title", "Tình huống"),
            72,
            192,
            CYAN,
            self.title_font,
            950,
        )

        self.wrap(
            scenario.get("body", ""),
            72,
            245,
            970,
            WHITE,
            self.body_font,
            max_lines=5,
        )

        self.text(
            "CHỌN PHƯƠNG ÁN XỬ LÝ",
            48,
            382,
            AMBER,
            self.small_font,
        )

        choices = scenario.get("choices", []) or []

        for index, choice in enumerate(choices[:4]):
            y = 410 + index * 61
            rect = (48, y, 1024, 51)

            self.panel(
                rect,
                fill=CARD,
                outline=BORDER,
                radius=9,
            )

            self.text(
                choice.get("code", chr(65 + index)),
                65,
                y + 16,
                CYAN,
                self.heading_font,
            )

            self.wrap(
                choice.get("text", ""),
                112,
                y + 14,
                920,
                WHITE,
                self.small_font,
                max_lines=2,
            )

            self.add_hitbox(
                f"choice_{index}",
                rect,
            )

        self.button(
            "pause_game",
            "VỀ TRUNG TÂM",
            (900, 96, 175, 34),
            BLUE,
        )

    def draw_feedback(self):
        feedback = (
            (self.session or {}).get("feedback") or {}
        )

        self.base(
            "PHÂN TÍCH HẬU QUẢ",
            "Đọc kỹ phản hồi trước khi chuyển sang tình huống tiếp theo.",
        )

        self.panel(
            (70, 170, 980, 405),
            fill=PANEL_ALT,
        )

        self.text(
            "HẬU QUẢ LỰA CHỌN",
            105,
            200,
            AMBER,
            self.heading_font,
        )

        self.wrap(
            feedback.get(
                "consequence",
                "Chưa có nội dung phản hồi.",
            ),
            105,
            245,
            905,
            WHITE,
            self.font,
            gap=8,
            max_lines=5,
        )

        self.text(
            "GIẢI THÍCH / BÀI HỌC",
            105,
            365,
            CYAN,
            self.heading_font,
        )

        self.wrap(
            feedback.get("explanation", ""),
            105,
            408,
            905,
            MUTED,
            self.body_font,
            gap=7,
            max_lines=5,
        )

        safety = feedback.get("safety_points", 0)
        risk = feedback.get("risk_points", 0)

        self.text(
            f"SAFETY +{safety}",
            108,
            525,
            GREEN,
            self.heading_font,
        )

        self.text(
            f"RISK +{risk}",
            310,
            525,
            RED,
            self.heading_font,
        )

        self.button(
            "continue_game",
            "TIẾP TỤC →",
            (420, 605, 280, 52),
            GREEN,
            self.busy,
        )

    def draw_result(self):
        result = self.result_data or {}

        self.base(
            "CHIẾN DỊCH HOÀN TẤT",
            "Kết quả cuối cùng do backend tính toán.",
        )

        values = [
            (
                "SAFETY SCORE",
                f"{result.get('safety_score', 0)}%",
                CYAN,
            ),
            (
                "RISK SCORE",
                f"{result.get('risk_score', 0)}%",
                RED,
            ),
            (
                "XẾP LOẠI",
                result.get("rank", "—"),
                GREEN,
            ),
            (
                "SỐ QUYẾT ĐỊNH",
                result.get("decision_count", 0),
                AMBER,
            ),
        ]

        for index, (label, value, accent) in enumerate(values):
            x = 125 + (index % 2) * 455
            y = 205 + (index // 2) * 145

            self.stat_card(
                (x, y, 390, 112),
                label,
                value,
                accent,
            )

        self.button(
            "result_home",
            "VỀ TRUNG TÂM",
            (420, 535, 280, 54),
            GREEN,
        )

    # ------------------------------------------------------------------
    # Admin screen
    # ------------------------------------------------------------------

    def draw_admin(self):
        overview = self.admin_overview_data or {}

        self.base(
            "ADMIN CONTROL ROOM",
            "Quản trị tài khoản, theo dõi hiệu quả chiến dịch và nhóm lỗi phổ biến.",
        )

        stats = [
            (
                "TỔNG TÀI KHOẢN",
                overview.get("users_total", 0),
                CYAN,
            ),
            (
                "ĐANG HOẠT ĐỘNG",
                overview.get("users_active", 0),
                GREEN,
            ),
            (
                "TỔNG PHIÊN CHƠI",
                overview.get("sessions_total", 0),
                BLUE,
            ),
            (
                "TỶ LỆ HOÀN THÀNH",
                f"{overview.get('completion_rate', 0)}%",
                AMBER,
            ),
        ]

        for index, (label, value, accent) in enumerate(stats):
            self.stat_card(
                (34 + index * 267, 158, 250, 88),
                label,
                value,
                accent,
            )

        self.text(
            "QUẢN LÝ NGƯỜI DÙNG",
            36,
            270,
            WHITE,
            self.heading_font,
        )

        self.text(
            f"{self.admin_users_total} tài khoản",
            36,
            298,
            MUTED,
            self.small_font,
        )

        self.input_box(
            "admin_search",
            "TÌM THEO TÊN HOẶC EMAIL",
            self.admin_search_value,
            (430, 273, 300, 40),
            placeholder="Nhập từ khóa...",
        )

        self.button(
            "admin_search_button",
            "TÌM KIẾM",
            (742, 273, 94, 40),
            BLUE,
            self.busy,
        )

        self.button(
            "admin_refresh",
            "TẢI LẠI",
            (845, 273, 90, 40),
            GREEN,
            self.busy,
        )

        # User table
        self.panel(
            (34, 325, 720, 337),
            fill=PANEL,
        )

        self.text(
            "TÊN HIỂN THỊ",
            49,
            340,
            MUTED,
            self.small_font,
        )

        self.text(
            "EMAIL",
            236,
            340,
            MUTED,
            self.small_font,
        )

        self.text(
            "VAI TRÒ",
            457,
            340,
            MUTED,
            self.small_font,
        )

        self.text(
            "TRẠNG THÁI",
            535,
            340,
            MUTED,
            self.small_font,
        )

        pygame.draw.line(
            self.screen,
            BORDER,
            (48, 360),
            (739, 360),
            1,
        )

        start = self.admin_user_offset

        visible = self.admin_users_data[
            start:start + self.admin_visible_rows
        ]

        for index, user in enumerate(visible):
            y = 368 + index * 39

            if index % 2 == 0:
                pygame.draw.rect(
                    self.screen,
                    (20, 33, 53),
                    (45, y - 3, 698, 36),
                    border_radius=5,
                )

            name = (
                user.get("display_name")
                or "Chưa đặt tên"
            )

            email = user.get("email") or "—"
            role = user.get("role") or "Player"
            active = bool(user.get("is_active"))

            self.text(
                name,
                53,
                y + 7,
                WHITE,
                self.small_font,
                170,
            )

            self.text(
                email,
                236,
                y + 7,
                MUTED,
                self.small_font,
                210,
            )

            self.text(
                role,
                457,
                y + 7,
                CYAN if role == "Admin" else MUTED,
                self.small_font,
                70,
            )

            self.text(
                "Hoạt động" if active else "Đã khóa",
                535,
                y + 7,
                GREEN if active else RED,
                self.small_font,
                85,
            )

            if role != "Admin":
                action_label = (
                    "KHÓA"
                    if active
                    else "MỞ KHÓA"
                )

                action_color = (
                    RED
                    if active
                    else GREEN
                )

                self.button(
                    f"admin_toggle_{user.get('id')}",
                    action_label,
                    (642, y - 1, 91, 31),
                    action_color,
                    self.busy,
                )

            else:
                self.text(
                    "—",
                    682,
                    y + 7,
                    MUTED,
                    self.small_font,
                )

        if not visible:
            self.text(
                "Không tìm thấy tài khoản phù hợp.",
                55,
                390,
                MUTED,
                self.body_font,
            )

        total = self.admin_users_total

        shown_from = (
            self.admin_page_offset + start + 1
            if total
            else 0
        )

        shown_to = min(
            self.admin_page_offset + start + len(visible),
            total,
        )

        self.text(
            f"Đang hiển thị {shown_from}-{shown_to} / {total}",
            50,
            625,
            MUTED,
            self.small_font,
        )

        can_go_prev = (
            start > 0
            or self.admin_page_offset > 0
        )

        can_go_next = (
            start + self.admin_visible_rows
            < len(self.admin_users_data)
            or self.admin_page_offset
            + len(self.admin_users_data)
            < total
        )

        self.button(
            "admin_prev",
            "←",
            (580, 617, 48, 32),
            BLUE,
            disabled=(not can_go_prev or self.busy),
        )

        self.button(
            "admin_next",
            "→",
            (688, 617, 48, 32),
            BLUE,
            disabled=(not can_go_next or self.busy),
        )

        # Campaign and common-error insights
        self.panel(
            (775, 325, 311, 337),
            fill=PANEL,
        )

        self.text(
            "HIỆU QUẢ CHIẾN DỊCH",
            795,
            340,
            CYAN,
            self.small_font,
        )

        campaigns = overview.get("campaigns", []) or []

        if not campaigns:
            self.text(
                "Chưa có dữ liệu chiến dịch.",
                795,
                370,
                MUTED,
                self.small_font,
            )

        for index, campaign in enumerate(campaigns[:4]):
            y = 370 + index * 43

            sessions = int(
                campaign.get("sessions", 0) or 0
            )

            completed = int(
                campaign.get("completed", 0) or 0
            )

            ratio = (
                completed / sessions
                if sessions
                else 0
            )

            self.text(
                campaign.get("campaign", "Chiến dịch"),
                795,
                y,
                WHITE,
                self.small_font,
                205,
            )

            self.text(
                f"{completed}/{sessions}",
                1015,
                y,
                MUTED,
                self.small_font,
                55,
            )

            self.progress_bar(
                (795, y + 20, 270, 6),
                ratio,
                CYAN,
            )

        divider_y = 545

        pygame.draw.line(
            self.screen,
            BORDER,
            (795, divider_y),
            (1067, divider_y),
            1,
        )

        self.text(
            "NHÓM LỖI PHỔ BIẾN",
            795,
            560,
            AMBER,
            self.small_font,
        )

        common_errors = (
            overview.get("common_errors", []) or []
        )

        if not common_errors:
            self.text(
                "Chưa ghi nhận lỗi.",
                795,
                588,
                MUTED,
                self.small_font,
            )

        for index, item in enumerate(common_errors[:3]):
            y = 588 + index * 22

            self.text(
                item.get("category", "Không xác định"),
                795,
                y,
                WHITE,
                self.small_font,
                215,
            )

            self.text(
                str(item.get("count", 0)),
                1035,
                y,
                AMBER,
                self.small_font,
                30,
            )

    # ------------------------------------------------------------------
    # Dispatch and input handling
    # ------------------------------------------------------------------

    def draw(self):
        self.hitboxes = {}

        if self.state == "AUTH":
            self.draw_auth()

        elif self.state == "ADMIN":
            self.draw_admin()

        elif self.state == "HOME":
            self.draw_home()

        elif self.state == "CAMPAIGNS":
            self.draw_campaigns()

        elif self.state == "DASHBOARD":
            self.draw_personal_dashboard()

        elif self.state == "HISTORY":
            self.draw_player_list(
                "LỊCH SỬ CHƠI",
                self.history_data,
                "history",
            )

        elif self.state == "ERRORS":
            self.draw_player_list(
                "SỔ TAY LỖI",
                self.errors_data,
                "errors",
            )

        elif self.state == "LEADERBOARD":
            self.draw_player_list(
                "BẢNG XẾP HẠNG",
                self.leaderboard_data,
                "leaderboard",
            )

        elif self.state == "GAME":
            self.draw_game()

        elif self.state == "FEEDBACK":
            self.draw_feedback()

        elif self.state == "RESULT":
            self.draw_result()

        else:
            self.state = "AUTH"
            self.draw_auth()

        if self.state != "AUTH":
            self.draw_message()

    def hit(self, key, position):
        rect = self.hitboxes.get(key)
        return bool(
            rect and rect.collidepoint(position)
        )

    async def click(self, position):
        if (
            self.state != "AUTH"
            and self.hit("logout", position)
        ):
            self.logout()
            return

        # AUTH screen
        if self.state == "AUTH":
            for field_name in (
                "email",
                "password",
                "display_name",
            ):
                if self.hit(field_name, position):
                    self.focus = field_name
                    return

            if self.hit("auth_submit", position):asyncio.create_task(self.auth_submit())
            return

            if self.hit("auth_switch", position):
                self.auth_mode = (
                    "register"
                    if self.auth_mode == "login"
                    else "login"
                )

                self.focus = "email"
                self.message = ""
                return

        # ADMIN screen
        elif self.state == "ADMIN":
            if self.hit("admin_search", position):
                self.focus = "admin_search"
                return

            if self.hit("admin_search_button", position):
                self.focus = None
                await self.search_admin_users()
                return

            if self.hit("admin_refresh", position):
                self.focus = None
                await self.load_admin_data()
                return

            if self.hit("admin_prev", position):
                await self.change_admin_page(-1)
                return

            if self.hit("admin_next", position):
                await self.change_admin_page(1)
                return

            for user in self.admin_users_data:
                key = f"admin_toggle_{user.get('id')}"

                if self.hit(key, position):
                    await self.toggle_admin_user(user)
                    return

            self.focus = None

        # PLAYER home
        elif self.state == "HOME":
            if self.hit("player_campaigns", position):
                self.state = "CAMPAIGNS"

            elif self.hit("player_dashboard", position):
                await self.load_section("DASHBOARD")

            elif self.hit("player_history", position):
                await self.load_section("HISTORY")

            elif self.hit("player_errors", position):
                await self.load_section("ERRORS")

            elif self.hit("player_leaderboard", position):
                await self.load_section("LEADERBOARD")

        # Campaign list
        elif self.state == "CAMPAIGNS":
            if self.hit("back_home", position):
                self.state = "HOME"
                return

            for index, campaign in enumerate(
                self.campaigns[:4]
            ):
                if self.hit(
                    f"campaign_{index}",
                    position,
                ):
                    await self.open_campaign(campaign)
                    return

        # Player sub-pages
        elif self.state in (
            "DASHBOARD",
            "HISTORY",
            "ERRORS",
            "LEADERBOARD",
        ):
            if self.hit("back_home", position):
                self.state = "HOME"

        # Game
        elif self.state == "GAME":
            if self.hit("pause_game", position):
                self.state = "HOME"
                return

            scenario = (
                (self.session or {}).get("current_scenario")
                or {}
            )

            choices = scenario.get("choices", []) or []

            for index, choice in enumerate(choices[:4]):
                if self.hit(
                    f"choice_{index}",
                    position,
                ):
                    await self.choose(
                        choice["id"],
                        scenario["id"],
                    )
                    return

        # Feedback
        elif self.state == "FEEDBACK":
            if self.hit("continue_game", position):
                await self.continue_game()

        # Result
        elif self.state == "RESULT":
            if self.hit("result_home", position):
                await self.set_home()

    async def handle_text_input(self, event):
        if event.key == pygame.K_TAB:
            if self.state == "AUTH":
                fields = [
                    "email",
                    "password",
                ]

                if self.auth_mode == "register":
                    fields.append("display_name")

                current = (
                    fields.index(self.focus)
                    if self.focus in fields
                    else -1
                )

                self.focus = fields[
                    (current + 1) % len(fields)
                ]

            elif self.state == "ADMIN":
                self.focus = (
                    "admin_search"
                    if self.focus != "admin_search"
                    else None
                )

            return

        if (
            self.state == "AUTH"
            and self.focus in self.fields
        ):
            if event.key == pygame.K_RETURN:
                if (
                    self.auth_mode == "login"
                    or self.focus == "display_name"
                ):
                    await self.auth_submit()
                else:
                    self.focus = "password"

                return

            if event.key == pygame.K_BACKSPACE:
                self.fields[self.focus] = (
                    self.fields[self.focus][:-1]
                )
                return

            if (
                event.unicode
                and event.unicode.isprintable()
            ):
                current = self.fields[self.focus]

                max_length = (
                    120
                    if self.focus != "display_name"
                    else 80
                )

                if len(current) < max_length:
                    self.fields[self.focus] += event.unicode

        elif (
            self.state == "ADMIN"
            and self.focus == "admin_search"
        ):
            if event.key == pygame.K_RETURN:
                await self.search_admin_users()

            elif event.key == pygame.K_BACKSPACE:
                self.admin_search_value = (
                    self.admin_search_value[:-1]
                )

            elif (
                event.unicode
                and event.unicode.isprintable()
            ):
                if len(self.admin_search_value) < 100:
                    self.admin_search_value += event.unicode

    async def run(self):
        await self.restore_auth()

        running = True

        try:
            while running:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False

                    elif event.type == pygame.VIDEORESIZE:
                        self.window = pygame.display.set_mode(
                            event.size,
                            pygame.RESIZABLE,
                        )

                    elif event.type == pygame.MOUSEMOTION:
                        self.mouse_pos = (
                            self.screen_to_canvas(event.pos)
                        )

                    elif (
                        event.type == pygame.MOUSEBUTTONDOWN
                        and event.button == 1
                    ):
                        self.mouse_pos = (
                            self.screen_to_canvas(event.pos)
                        )

                        await self.click(self.mouse_pos)

                    elif event.type == pygame.MOUSEWHEEL:
                        if self.state == "ADMIN":
                            max_offset = max(
                                0,
                                len(self.admin_users_data)
                                - self.admin_visible_rows,
                            )

                            self.admin_user_offset = max(
                                0,
                                min(
                                    max_offset,
                                    self.admin_user_offset - event.y,
                                ),
                            )

                    elif event.type == pygame.KEYDOWN:
                        await self.handle_text_input(event)

                self.draw()
                self.present()

                self.clock.tick(30)
                await asyncio.sleep(0)

        finally:
            await self.api.close()
            pygame.quit()


if __name__ == "__main__":
    asyncio.run(
        CyberSafeV3().run()
    )
